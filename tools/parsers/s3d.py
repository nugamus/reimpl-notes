"""`.S3D` parser and corpus validator.

Super-container that sequences the four already-recovered per-format readers against a
shared file cursor. Derived from `X3d_Load_Sdk_s3d` (`x3d.dll` `0x100010e1`):

    thunk_FUN_100148e0(...)         cameras     (.C3D body, no signature)
    thunk_FUN_10014d50(...)         lights      (.L3D body, no signature)
    thunk_FUN_10011450(...)         materials   (.O3D body, no signature)
    thunk_FUN_10012920(...)         objects     (.O3D body, no signature)
    thunk_FUN_10012ee0(...)         animations  (.A3D body, no signature)

Each section starts with a u32 count, then that many records of the per-format shape.
No per-section signature — the cursor advances straight from one section into the next.
The signature and counts in the individual `.O3D`/`.A3D`/`.L3D`/`.C3D` files are
superfluous here because each section uses the same shape as the standalone format but
without its 32-byte prefix.

Per CLAUDE.md rule 2 the validator must consume every byte of every `.S3D` file with
no out-of-range indices. `parse` insists on `expect_eof()` at the end.

    python tools/parsers/s3d.py                 # validate the corpus
    python tools/parsers/s3d.py --selftest
    python tools/parsers/s3d.py --file <path>  # one file, structural summary
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    ParseError,
    Reader,
    corpus_argparser,
    default_root,
    find_files,
)
import o3d  # noqa: E402  (has its own Reader + record readers, reused as-is)
import a3d  # noqa: E402
import c3d  # noqa: E402
import l3d  # noqa: E402

SIG_LEN = 32
SIGNATURES = {
    b"(c) 1998 4X Tech. 0.95 (S)": "0.95",
    b"(c) 1998 4X Tech. 1.00 (S)": "1.00",
}


class _O3dReaderAdapter:
    """Expose `o3d.Reader`'s API on top of `common.Reader` so the file cursor is owned
    in one place. Every method forwards to the underlying common.Reader and updates its
    position. The only divergence from `o3d.Reader` is `.eof` — a method here vs a
    property in o3d — so callers using `r.eof` are flagged by tests rather than used."""

    __slots__ = ("_r",)

    def __init__(self, r: Reader) -> None:
        self._r = r

    def take(self, n: int) -> bytes:
        return self._r.bytes(n)

    def u32(self) -> int:
        return self._r.u32()

    def f32(self) -> float:
        return self._r.f32()

    def floats(self, n: int) -> tuple:
        return self._r.array("f", n)

    def u32s(self, n: int) -> tuple:
        return self._r.array("I", n)

    def name(self, n: int = 32) -> str:
        return self._r.fixed_str(n)

    @property
    def eof(self) -> bool:
        return self._r.eof()


def _parse_signature(r: Reader) -> str:
    raw = r.bytes(SIG_LEN)
    end = raw.find(b"\0")
    if end < 0:
        raise ParseError("signature has no NUL terminator", r.pos - SIG_LEN)
    text = raw[:end]
    if text not in SIGNATURES:
        raise ParseError(f"unknown signature {text!r}", r.pos - SIG_LEN)
    return SIGNATURES[text]


def _read_section(r: Reader, fn) -> list:
    count = r.u32()
    inner = _O3dReaderAdapter(r)
    return [fn(inner) for _ in range(count)]


def parse(data: bytes) -> dict:
    r = Reader(data)
    version = _parse_signature(r)
    cameras = _read_section(r, c3d._parse_camera)
    lights = _read_section(r, l3d._parse_light)
    materials = _read_section(r, o3d.read_material)
    objects = _read_section(r, o3d.read_object)
    animations = _read_section(r, a3d.read_animation)
    r.expect_eof()
    return {
        "version": version,
        "cameras": cameras,
        "lights": lights,
        "materials": materials,
        "objects": objects,
        "animations": animations,
    }


def _selftest() -> None:
    import struct

    sig = b"(c) 1998 4X Tech. 0.95 (S)\0".ljust(32, b"\0")

    def name32(s: bytes) -> bytes:
        return s.ljust(32, b"\0")

    # 0 cameras, 0 lights
    cam_light = struct.pack("<II", 0, 0)

    # 1 minimal material: name + flags=0 + 4 RGBs + 5 u32s + texture=0 + lightmap=0
    material = (
        name32(b"M")
        + struct.pack("<I", 0)
        + bytes(12)
        + struct.pack("<5I", 0, 0, 0, 0, 0)
        + struct.pack("<II", 0, 0)
    )

    # 1 minimal object: name, no parent, count_a=0/flag=0 → count=0 vertices, no faces,
    # bounds, 0 lights, unknown, position/scale/rotation (9f) and matrix (16f)
    obj = (
        name32(b"O")
        + struct.pack("<II", 0, 0)  # no parent; first count_a = 0
        + struct.pack("<I", 0)       # flag
        + struct.pack("<I", 0)       # face count
        + struct.pack("<10f", 0, 0, 0, 1, 1, 1, 0, 0, 0, 0)
        + struct.pack("<I", 0)       # light count
        + struct.pack("<I", 0)       # unknown
        + struct.pack("<3f", 0, 0, 0)
        + struct.pack("<3f", 1, 1, 1)
        + struct.pack("<3f", 0, 0, 0)
        + struct.pack("<16f", *range(16))
    )

    def track(n: int, vfloats: int) -> bytes:
        out = struct.pack("<II", n, 0) + struct.pack("<%dI" % n, *range(n))
        for _ in range(n):
            out += struct.pack("<5f", 1, 2, 3, 4, 5)
        for _ in range(n):
            out += struct.pack("<%df" % vfloats, *range(vfloats))
        return out

    track_d = (
        struct.pack("<II", 1, 0) + struct.pack("<I", 0) + struct.pack("<2I", 7, 8)
    )
    track_e = (
        struct.pack("<II", 1, 0)
        + struct.pack("<I", 0)
        + struct.pack("<5f", 1, 2, 3, 4, 5)
        + struct.pack("<I", 0)
        + struct.pack("<7f", 0, 0, 0, 0, 0, 0, 0)
    )

    anim = (
        name32(b"A")
        + struct.pack("<I", 0)        # no parent
        + struct.pack("<3f", 0, 0, 0) # pivot
        + struct.pack("<3I", 0, 0, 0) # unknown
        + track(1, 3)                 # track A
        + track(1, 3)                 # track B
        + track(1, 4)                 # track C
        + track_d                     # track D
        + track_e                     # track E
    )

    body = (
        sig
        + cam_light
        + struct.pack("<I", 1) + material
        + struct.pack("<I", 1) + obj
        + struct.pack("<I", 1) + anim
    )

    doc = parse(body)
    assert doc["version"] == "0.95"
    assert doc["cameras"] == [] and doc["lights"] == []
    assert len(doc["materials"]) == 1 and doc["materials"][0]["name"] == "M"
    assert len(doc["objects"]) == 1 and doc["objects"][0]["name"] == "O"
    assert len(doc["animations"]) == 1 and doc["animations"][0]["name"] == "A"
    assert doc["animations"][0]["track_a"]["values"][0] == (0.0, 1.0, 2.0)

    try:
        parse(body + b"\0")
    except ParseError as exc:
        assert "unconsumed" in exc.message
    else:
        raise AssertionError("trailing byte accepted")

    try:
        parse(body[:-4])
    except ParseError:
        pass
    else:
        raise AssertionError("truncated file accepted")

    try:
        parse(b"(c) 1998 4X Tech. 0.95 (O)\0".ljust(32, b"\0") + body[32:])
    except ParseError as exc:
        assert "signature" in exc.message or "unknown" in exc.message
    else:
        raise AssertionError("wrong signature accepted")

    blob10 = (
        b"(c) 1998 4X Tech. 1.00 (S)\0".ljust(32, b"\0")
        + struct.pack("<IIIII", 0, 0, 0, 0, 0)
    )
    doc10 = parse(blob10)
    assert doc10["version"] == "1.00"
    assert doc10["cameras"] == []

    print("selftest ok")


def _dump(path: Path) -> None:
    doc = parse(path.read_bytes())
    print(
        f"{path.name}: version {doc['version']}, {path.stat().st_size} bytes"
    )
    print(
        f"  cameras={len(doc['cameras'])}  lights={len(doc['lights'])}"
        f"  materials={len(doc['materials'])}  objects={len(doc['objects'])}"
        f"  animations={len(doc['animations'])}"
    )


def main(argv: list) -> int:
    if "--selftest" in argv:
        _selftest()
        return 0

    args = corpus_argparser(".S3D validator").parse_args(argv)

    if args.file:
        _dump(args.file)
        return 0

    root = args.root or default_root()
    files = find_files(root, "*.S3D")
    if not files:
        print(f"no .s3d files under {root}", file=sys.stderr)
        return 2

    ok = 0
    failures: list[tuple[Path, str]] = []
    versions: dict[str, int] = {}
    totals = {
        "cameras": 0, "lights": 0, "materials": 0, "objects": 0,
        "animations": 0, "bytes": 0,
    }

    for path in files:
        data = path.read_bytes()
        try:
            doc = parse(data)
        except ParseError as exc:
            failures.append((path, f"{exc.message} at 0x{exc.offset:08x}"))
            continue
        ok += 1
        versions[doc["version"]] = versions.get(doc["version"], 0) + 1
        totals["cameras"] += len(doc["cameras"])
        totals["lights"] += len(doc["lights"])
        totals["materials"] += len(doc["materials"])
        totals["objects"] += len(doc["objects"])
        totals["animations"] += len(doc["animations"])
        totals["bytes"] += len(data)

    print(f"corpus: {root}")
    print(f"files: {len(files)}  passed: {ok}  failed: {len(failures)}")
    print(f"  versions:    {versions}")
    print(f"  cameras:     {totals['cameras']}")
    print(f"  lights:      {totals['lights']}")
    print(f"  materials:   {totals['materials']}")
    print(f"  objects:     {totals['objects']}")
    print(f"  animations:  {totals['animations']}")
    print(f"  bytes:       {totals['bytes']}")
    for path, err in failures[:25]:
        print(f"  FAIL {path}  {err}")

    print("100% of corpus parsed" if ok == len(files) else "SPEC INCOMPLETE")
    return 0 if ok == len(files) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))