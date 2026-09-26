"""`.A3D` parser and corpus validator.

Same container family as `.O3D` — a 32-byte `(c) 1998 4X Tech. 0.95 (A)` signature, then
a sequential stream through the identical cursor primitives. Derived from
`X3d_Load_Sdk_a3d` (`x3d.dll` `0x10001091`), which dispatches to `FUN_10012ee0`.

An animation has a header (pivot, frame count, first and last frame: E-0055) and five
keyframe tracks. Each opens with a count and a flags u32, then holds `count` frame
numbers followed by per-key data whose shape differs by track (loader error strings in
brackets):

    track        count at  per key
    translation  +0x40     5 f32 TCB/ease, then 3 f32 position
    scale        +0x54     5 f32 TCB/ease, then 3 f32 scale
    rotation     +0x68     5 f32 TCB/ease, then 4 f32 quaternion (w, x, y, z)
    hide         +0xa0     1 u32 ("Hide key info")
    morph        +0x7c     5 f32, then (once) an inner count, then per key: inner
                           positions, inner normals, a bounding sphere (4 f32) and a
                           bounding box (6 f32)

No corpus file has hide or morph keys, so those two layouts are the loader's only.

The loader's `if (ptr != 0)` guards around each track are null checks on the animation
object, not file flags — every read loop is bounded by the count itself, so a zero count
simply reads nothing.

    python engines/x3d/tools/parsers/a3d.py                 # validate the corpus
    python engines/x3d/tools/parsers/a3d.py --selftest
    python engines/x3d/tools/parsers/a3d.py --dump <file>
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import default_root  # noqa: E402
from o3d import ParseError, Reader  # noqa: E402

SIG_LEN = 32
SIGNATURES = {
    b"(c) 1998 4X Tech. 0.95 (A)": "0.95",
    b"(c) 1998 4X Tech. 1.00 (A)": "1.00",
}


def read_signature(r: Reader) -> str:
    raw = r.take(SIG_LEN)
    end = raw.find(b"\0")
    text = raw[: end if end >= 0 else SIG_LEN]
    if text not in SIGNATURES:
        raise ParseError("unknown signature %r" % text)
    return SIGNATURES[text]


def read_track(r: Reader, value_floats: int, extra_key_u32s: int = 0) -> dict:
    """A count, a companion u32, `count` frame ids, then per-key data."""
    count = r.u32()
    track = {"count": count, "flags": r.u32(), "frames": r.u32s(count)}
    if extra_key_u32s:
        track["keys"] = [r.u32s(extra_key_u32s) for _ in range(count)]
    else:
        track["keys"] = [r.floats(5) for _ in range(count)]
        track["values"] = [r.floats(value_floats) for _ in range(count)]
    return track


def read_track_e(r: Reader) -> dict:
    count = r.u32()
    track = {"count": count, "flags": r.u32(), "frames": r.u32s(count)}
    track["keys"] = [r.floats(5) for _ in range(count)]
    if count:
        inner = r.u32()
        track["inner_count"] = inner
        track["morphs"] = [
            {
                "positions": [r.floats(3) for _ in range(inner)],
                "normals": [r.floats(3) for _ in range(inner)],
                "sphere": r.floats(4),
                "box": r.floats(6),
            }
            for _ in range(count)
        ]
    return track


def read_animation(r: Reader) -> dict:
    anim = {"name": r.name(), "parent": None}
    if r.u32():
        anim["parent"] = r.name()
    anim["pivot"] = r.floats(3)
    anim["num_frames"], anim["first_frame"], anim["last_frame"] = r.u32s(3)
    anim["track_a"] = read_track(r, 3)
    anim["track_b"] = read_track(r, 3)
    anim["track_c"] = read_track(r, 4)
    # Hide: frame numbers at +0xa8, then one u32 per key at +0xb0.
    anim["track_d"] = read_track(r, 0, extra_key_u32s=1)
    anim["track_e"] = read_track_e(r)
    return anim


def parse(data: bytes) -> dict:
    r = Reader(data)
    version = read_signature(r)
    if version == "1.00":
        raise ParseError("version 1.00 is not implemented (no corpus sample)")
    animations = [read_animation(r) for _ in range(r.u32())]
    if not r.eof:
        raise ParseError("%d bytes left over at offset %d" % (len(data) - r.pos, r.pos))
    return {"version": version, "animations": animations, "consumed": r.pos}


TRACKS = ("track_a", "track_b", "track_c", "track_d", "track_e")


def validate(root: Path) -> int:
    files = sorted(root.rglob("*.[aA]3[dD]"))
    if not files:
        print("no .A3D files under %s" % root, file=sys.stderr)
        return 2

    ok = 0
    failures = []
    totals = {"animations": 0, "keys": 0, "bytes": 0}
    parented = 0

    for path in files:
        try:
            doc = parse(path.read_bytes())
        except ParseError as exc:
            failures.append((path, str(exc)))
            continue
        ok += 1
        totals["animations"] += len(doc["animations"])
        totals["bytes"] += doc["consumed"]
        for anim in doc["animations"]:
            parented += 1 if anim["parent"] else 0
            for name in TRACKS:
                totals["keys"] += anim[name]["count"]

    print("%d/%d files parsed, every byte consumed" % (ok, len(files)))
    print("  animations: %(animations)d" % totals)
    print("  keyframes:  %(keys)d" % totals)
    print("  bytes:      %(bytes)d" % totals)
    print("  parented:   %d" % parented)
    for path, exc in failures[:10]:
        print("  FAIL %s: %s" % (path.name, exc))
    if len(failures) > 10:
        print("  ... and %d more failures" % (len(failures) - 10))
    return 0 if ok == len(files) else 1


def selftest() -> int:
    def name32(s):
        return s.encode("ascii").ljust(32, b"\0")

    def track(n, value_floats):
        out = struct.pack("<I", n) + struct.pack("<I", 0)
        out += struct.pack("<%dI" % n, *range(n))
        for _ in range(n):
            out += struct.pack("<5f", 1, 2, 3, 4, 5)
        for _ in range(n):
            out += struct.pack("<%df" % value_floats, *range(value_floats))
        return out

    anim = (
        name32("Anim")
        + struct.pack("<I", 1)
        + name32("Root")
        + struct.pack("<3f", 0, 0, 0)
        + struct.pack("<3I", 0, 0, 0)
        + track(2, 3)
        + track(1, 3)
        + track(1, 4)
        # hide: count, flags, frame numbers, then one u32 per key
        + struct.pack("<I", 2)
        + struct.pack("<I", 0)
        + struct.pack("<2I", 0, 1)
        + struct.pack("<2I", 7, 8)
        # morph: count 2, flags, frames, 5f per key, inner count 2, then per key
        # 2 positions, 2 normals, sphere 4f, box 6f
        + struct.pack("<I", 2)
        + struct.pack("<I", 0)
        + struct.pack("<2I", 0, 5)
        + struct.pack("<10f", *range(10))
        + struct.pack("<I", 2)
        + (struct.pack("<12f", *range(12)) + struct.pack("<4f", 1, 2, 3, 4)
           + struct.pack("<6f", *range(6))) * 2
    )
    blob = name32("(c) 1998 4X Tech. 0.95 (A)") + struct.pack("<I", 1) + anim

    doc = parse(blob)
    assert doc["consumed"] == len(blob), (doc["consumed"], len(blob))
    a = doc["animations"][0]
    assert a["name"] == "Anim" and a["parent"] == "Root"
    assert a["track_a"]["count"] == 2 and len(a["track_a"]["values"][0]) == 3
    assert len(a["track_c"]["values"][0]) == 4, "track C values are quaternions"
    assert [tuple(k) for k in a["track_d"]["keys"]] == [(7,), (8,)]
    assert a["track_e"]["count"] == 2
    assert a["track_e"]["inner_count"] == 2
    assert tuple(a["track_e"]["frames"]) == (0, 5)
    assert a["track_e"]["morphs"][1]["sphere"] == (1.0, 2.0, 3.0, 4.0)
    assert len(a["track_e"]["morphs"][1]["box"]) == 6

    for mutate, why in (
        (lambda b: b + b"\0", "trailing byte accepted"),
        (lambda b: b[:-4], "truncated file accepted"),
    ):
        try:
            parse(mutate(blob))
        except ParseError:
            pass
        else:
            raise AssertionError(why)

    try:
        read_signature(Reader(name32("(c) 1998 4X Tech. 0.95 (O)")))
    except ParseError:
        pass
    else:
        raise AssertionError("an .O3D signature must not pass as .A3D")

    print("selftest ok")
    return 0


def main(argv: list) -> int:
    if "--selftest" in argv:
        return selftest()
    if "--dump" in argv:
        path = Path(argv[argv.index("--dump") + 1])
        doc = parse(path.read_bytes())
        print("%s: version %s, %d bytes" % (path.name, doc["version"], doc["consumed"]))
        for anim in doc["animations"]:
            counts = " ".join(
                "%s=%d" % (name[-1], anim[name]["count"]) for name in TRACKS
            )
            print("  %-32s parent=%-20s %s" % (anim["name"], anim["parent"], counts))
        return 0
    root = Path(argv[argv.index("--root") + 1]) if "--root" in argv else default_root()
    return validate(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
