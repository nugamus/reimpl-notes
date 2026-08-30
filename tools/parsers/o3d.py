"""`.O3D` parser and corpus validator.

Derived from the loader, not from guesswork. `X3d_Load_Sdk_o3d` (`x3d.dll` `0x10001302`)
opens the file and dispatches to `FUN_10011450` for materials and `FUN_10012920` for
objects, which in turn calls `FUN_10011ea0` per object. All three read through the same
stream primitives, so the file has no fixed-offset records at all — read order *is* the
layout:

    FUN_1000ba90(cursor, dst)      u32,  cursor += 4
    FUN_1000baf0(cursor, dst)      u8,   cursor += 1
    FUN_1000bb20(cursor, dst)      f32,  cursor += 4
    FUN_1000bb50(cursor, dst, n)   n bytes, cursor += n

That is why the fixed-stride readings in `notes/o3d-findings.md` failed: material and
object records vary in length depending on flags and counts inside them.

Validation is the whole point. A parse that stops early is a failure even when it raises
nothing, so `parse` insists the cursor lands exactly on end-of-file.

    python tools/parsers/o3d.py                 # validate the corpus, print counts
    python tools/parsers/o3d.py --selftest
    python tools/parsers/o3d.py --dump <file>   # one file, structure summary
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import default_root  # noqa: E402

SIG_LEN = 32
# Compared with strcmp in the loader, so only the bytes up to the NUL matter; the rest of
# the 32-byte field is uninitialised writer memory and varies between files.
SIGNATURES = {
    b"(c) 1998 4X Tech. 0.95 (O)": "0.95",
    b"(c) 1998 4X Tech. 1.00 (O)": "1.00",
}


class ParseError(Exception):
    pass


class Reader:
    """The loader's cursor, with the bounds checks it does not bother with."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def take(self, n: int) -> bytes:
        if n < 0 or self.pos + n > len(self.data):
            raise ParseError(
                "read of %d at offset %d runs past end of file (%d bytes)"
                % (n, self.pos, len(self.data))
            )
        out = self.data[self.pos : self.pos + n]
        self.pos += n
        return out

    def u32(self) -> int:
        return struct.unpack("<I", self.take(4))[0]

    def f32(self) -> float:
        return struct.unpack("<f", self.take(4))[0]

    def floats(self, n: int) -> tuple:
        return struct.unpack("<%df" % n, self.take(4 * n))

    def u32s(self, n: int) -> tuple:
        return struct.unpack("<%dI" % n, self.take(4 * n))

    def name(self, n: int = 32) -> str:
        raw = self.take(n)
        end = raw.find(b"\0")
        return raw[: end if end >= 0 else n].decode("latin1")

    @property
    def eof(self) -> bool:
        return self.pos == len(self.data)


def read_signature(r: Reader) -> str:
    raw = r.take(SIG_LEN)
    end = raw.find(b"\0")
    text = raw[: end if end >= 0 else SIG_LEN]
    if text not in SIGNATURES:
        raise ParseError("unknown signature %r" % text)
    return SIGNATURES[text]


def read_material(r: Reader) -> dict:
    """FUN_10011450, body of the per-material loop."""
    mat = {
        "name": r.name(),
        "flags": r.u32(),
        # Four RGB triples; the loader folds each through X3d_Rgb_To_16 into a 16-bit
        # colour stored alongside. Which is ambient/diffuse/specular is not proven.
        "colors": [tuple(r.take(3)) for _ in range(4)],
        "unknown": r.u32s(5),
        "texture_map": None,
        "light_map": None,
    }
    if r.u32():
        mat["texture_map"] = {"name": r.name(), "flags": r.u32()}
    if r.u32():
        mat["light_map"] = {"name": r.name(), "flags": r.u32()}
    return mat


def read_face(r: Reader) -> dict:
    """FUN_10011ea0, body of the per-face loop."""
    n = r.u32()
    face = {"vertex_count": n, "indices": r.u32s(n), "uv": None}
    if r.u32():
        face["uv"] = [(r.f32(), r.f32()) for _ in range(n)]
    face["material"] = r.u32()
    face["normal"] = r.floats(3)
    return face


def read_object(r: Reader) -> dict:
    """FUN_10011ea0."""
    obj = {"name": r.name(), "parent": None}
    if r.u32():
        obj["parent"] = r.name()

    # Two vertex counts with a selector between them. When the flag is set the loader
    # reads an extra u32 and a second count and uses that one; otherwise it uses the
    # first, and the second is never present.
    count_a = r.u32()
    flag = r.u32()
    obj["vertex_flag"] = flag
    if flag:
        obj["vertex_extra"] = r.u32()
        count = r.u32()
    else:
        count = count_a
    obj["vertex_count"] = count
    obj["positions"] = [r.floats(3) for _ in range(count)]
    obj["normals"] = [r.floats(3) for _ in range(count)]

    obj["faces"] = [read_face(r) for _ in range(r.u32())]

    # Ten floats the loader fans out into a cached bounding box.
    obj["bounds"] = r.floats(10)
    obj["lights"] = r.u32s(r.u32())
    obj["unknown"] = r.u32()
    obj["position"] = r.floats(3)
    obj["scale"] = r.floats(3)
    obj["rotation"] = r.floats(3)
    obj["matrix"] = r.floats(16)
    return obj


def parse(data: bytes) -> dict:
    r = Reader(data)
    version = read_signature(r)
    if version == "1.00":
        # FUN_10012920 reads a LOD block after each object, but only for 1.00. No such
        # file exists in the corpus, so that path is unexercised and fails loudly rather
        # than guessing.
        raise ParseError("version 1.00 LOD block is not implemented (no corpus sample)")

    materials = [read_material(r) for _ in range(r.u32())]
    objects = [read_object(r) for _ in range(r.u32())]

    if not r.eof:
        raise ParseError("%d bytes left over at offset %d" % (len(data) - r.pos, r.pos))
    return {
        "version": version,
        "materials": materials,
        "objects": objects,
        "consumed": r.pos,
    }


def effective_vertex_count(obj: dict, by_name: dict) -> int:
    """Vertices an object's faces index into, following shared geometry.

    An object whose `vertex_flag` is set carries its vertex array in a shared structure
    rather than its own, and the on-disk count is then 0. Every such object in the corpus
    (5,193 of them, without exception) names a parent, and its faces index the parent's
    vertices. Walk up until a real count appears.
    """
    seen = set()
    cur = obj
    while cur is not None and cur["vertex_count"] == 0 and cur["parent"]:
        if cur["name"] in seen:  # a cycle would otherwise hang the validator
            break
        seen.add(cur["name"])
        cur = by_name.get(cur["parent"])
    return cur["vertex_count"] if cur is not None else 0


def check_indices(doc: dict) -> list:
    """Out-of-range indices are a failure even when the byte count works out."""
    problems = []
    nmat = len(doc["materials"])
    by_name = {o["name"]: o for o in doc["objects"]}
    for obj in doc["objects"]:
        nvert = effective_vertex_count(obj, by_name)
        for i, face in enumerate(obj["faces"]):
            for idx in face["indices"]:
                if idx >= nvert:
                    problems.append(
                        "%s face %d: vertex index %d of %d"
                        % (obj["name"], i, idx, nvert)
                    )
            if face["material"] >= nmat:
                problems.append(
                    "%s face %d: material index %d of %d"
                    % (obj["name"], i, face["material"], nmat)
                )
    return problems


def validate(root: Path) -> int:
    files = sorted(root.rglob("*.[oO]3[dD]"))
    if not files:
        print("no .O3D files under %s" % root, file=sys.stderr)
        return 2

    ok = 0
    failures = []
    index_problems = []
    totals = {"materials": 0, "objects": 0, "faces": 0, "vertices": 0, "bytes": 0}
    versions = {}

    for path in files:
        data = path.read_bytes()
        try:
            doc = parse(data)
        except ParseError as exc:
            failures.append((path, str(exc)))
            continue
        problems = check_indices(doc)
        if problems:
            index_problems.append((path, problems))
            continue
        ok += 1
        versions[doc["version"]] = versions.get(doc["version"], 0) + 1
        totals["materials"] += len(doc["materials"])
        totals["objects"] += len(doc["objects"])
        totals["faces"] += sum(len(o["faces"]) for o in doc["objects"])
        totals["vertices"] += sum(o["vertex_count"] for o in doc["objects"])
        totals["bytes"] += doc["consumed"]

    print("%d/%d files parsed, every byte consumed" % (ok, len(files)))
    print("  versions:   %s" % versions)
    print("  materials:  %(materials)d" % totals)
    print("  objects:    %(objects)d" % totals)
    print("  faces:      %(faces)d" % totals)
    print("  vertices:   %(vertices)d" % totals)
    print("  bytes:      %(bytes)d" % totals)

    for path, exc in failures[:10]:
        print("  FAIL %s: %s" % (path.name, exc))
    if len(failures) > 10:
        print("  ... and %d more failures" % (len(failures) - 10))
    for path, problems in index_problems[:10]:
        print("  INDEX %s: %s" % (path.name, problems[0]))
    if len(index_problems) > 10:
        print("  ... and %d more with bad indices" % (len(index_problems) - 10))

    return 0 if ok == len(files) else 1


def selftest() -> int:
    def name32(s):
        return s.encode("ascii").ljust(32, b"\0")

    sig = name32("(c) 1998 4X Tech. 0.95 (O)")
    material = (
        name32("Mat")
        + struct.pack("<I", 2)
        + bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        + struct.pack("<5I", 0, 0, 0, 0, 0)
        + struct.pack("<I", 1)
        + name32("T.TGA")
        + struct.pack("<I", 0)
        + struct.pack("<I", 0)
    )
    face = (
        struct.pack("<I", 3)
        + struct.pack("<3I", 0, 1, 2)
        + struct.pack("<I", 1)
        + struct.pack("<6f", 0, 0, 1, 0, 0, 1)
        + struct.pack("<I", 0)
        + struct.pack("<3f", 0, 0, 1)
    )
    obj = (
        name32("Obj")
        + struct.pack("<I", 0)
        + struct.pack("<I", 3)
        + struct.pack("<I", 0)
        + struct.pack("<9f", *range(9))
        + struct.pack("<9f", *range(9))
        + struct.pack("<I", 1)
        + face
        + struct.pack("<10f", *range(10))
        + struct.pack("<I", 0)
        + struct.pack("<I", 7)
        + struct.pack("<9f", *range(9))
        + struct.pack("<16f", *range(16))
    )
    blob = sig + struct.pack("<I", 1) + material + struct.pack("<I", 1) + obj

    doc = parse(blob)
    assert doc["version"] == "0.95"
    assert doc["consumed"] == len(blob), (doc["consumed"], len(blob))
    assert len(doc["materials"]) == 1 and len(doc["objects"]) == 1
    assert doc["materials"][0]["name"] == "Mat"
    assert doc["materials"][0]["texture_map"]["name"] == "T.TGA"
    assert doc["materials"][0]["light_map"] is None
    assert doc["materials"][0]["colors"][0] == (1, 2, 3)
    assert doc["objects"][0]["vertex_count"] == 3
    assert doc["objects"][0]["faces"][0]["indices"] == (0, 1, 2)
    assert doc["objects"][0]["unknown"] == 7
    assert check_indices(doc) == []

    # A trailing byte must fail: silently ignoring it is the bug rule 2 targets.
    try:
        parse(blob + b"\0")
    except ParseError as exc:
        assert "left over" in str(exc), exc
    else:
        raise AssertionError("trailing byte accepted")

    # Truncation must fail too, rather than returning a short parse.
    try:
        parse(blob[:-4])
    except ParseError:
        pass
    else:
        raise AssertionError("truncated file accepted")

    # An out-of-range vertex index must be caught even though the length works out.
    bad = bytearray(blob)
    off = blob.index(struct.pack("<3I", 0, 1, 2))
    bad[off : off + 12] = struct.pack("<3I", 0, 1, 99)
    assert check_indices(parse(bytes(bad))), "bad vertex index not reported"

    assert read_signature(Reader(name32("(c) 1998 4X Tech. 1.00 (O)"))) == "1.00"
    try:
        read_signature(Reader(name32("nope")))
    except ParseError:
        pass
    else:
        raise AssertionError("unknown signature accepted")

    print("selftest ok")
    return 0


def main(argv: list) -> int:
    if "--selftest" in argv:
        return selftest()
    if "--dump" in argv:
        path = Path(argv[argv.index("--dump") + 1])
        doc = parse(path.read_bytes())
        print("%s: version %s, %d bytes" % (path.name, doc["version"], doc["consumed"]))
        for mat in doc["materials"]:
            print(
                "  material %-32s tex=%s light=%s"
                % (
                    mat["name"],
                    mat["texture_map"] and mat["texture_map"]["name"],
                    mat["light_map"] and mat["light_map"]["name"],
                )
            )
        for obj in doc["objects"]:
            print(
                "  object   %-32s parent=%-20s verts=%-6d faces=%d"
                % (obj["name"], obj["parent"], obj["vertex_count"], len(obj["faces"]))
            )
        return 0

    root = Path(argv[argv.index("--root") + 1]) if "--root" in argv else default_root()
    return validate(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
