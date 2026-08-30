"""`.A3D` parser and corpus validator.

Same container family as `.O3D` — a 32-byte `(c) 1998 4X Tech. 0.95 (A)` signature, then
a sequential stream through the identical cursor primitives. Derived from
`X3d_Load_Sdk_a3d` (`x3d.dll` `0x10001091`), which dispatches to `FUN_10012ee0`.

An animation carries five keyframe tracks. Each opens with a count and a second u32, then
holds `count` frame ids followed by per-key data whose shape differs by track:

    track  count at  frame ids  per key            then
    A      +0x40     u32        5 f32              3 f32
    B      +0x54     u32        5 f32              3 f32
    C      +0x68     u32        5 f32              4 f32  (stride 0x10)
    D      +0xa0     u32        1 u32              -
    E      +0x7c     u32        5 f32              see below

Track E then reads one more count and, for every one of its keys, two `inner_count`-long
runs of vec3 plus ten trailing floats.

The loader's `if (ptr != 0)` guards around each track are null checks on the animation
object, not file flags — every read loop is bounded by the count itself, so a zero count
simply reads nothing.

    python tools/parsers/a3d.py                 # validate the corpus
    python tools/parsers/a3d.py --selftest
    python tools/parsers/a3d.py --dump <file>
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
    track = {"count": count, "unknown": r.u32(), "frames": r.u32s(count)}
    if extra_key_u32s:
        track["keys"] = [r.u32s(extra_key_u32s) for _ in range(count)]
    else:
        track["keys"] = [r.floats(5) for _ in range(count)]
        track["values"] = [r.floats(value_floats) for _ in range(count)]
    return track


def read_track_e(r: Reader) -> dict:
    count = r.u32()
    track = {"count": count, "unknown": r.u32(), "frames": r.u32s(count)}
    track["keys"] = [r.floats(5) for _ in range(count)]
    if count:
        inner = r.u32()
        track["inner_count"] = inner
        track["positions"] = [
            [r.floats(3) for _ in range(inner)] for _ in range(count)
        ]
        track["normals"] = [
            [r.floats(3) for _ in range(inner)] for _ in range(count)
        ]
        track["tail"] = r.floats(7)
    return track


def read_animation(r: Reader) -> dict:
    anim = {"name": r.name(), "parent": None}
    if r.u32():
        anim["parent"] = r.name()
    anim["pivot"] = r.floats(3)
    anim["unknown"] = r.u32s(3)
    anim["track_a"] = read_track(r, 3)
    anim["track_b"] = read_track(r, 3)
    anim["track_c"] = read_track(r, 4)
    # Track D holds two u32s per key (frame time at +0xa8, key info at +0xb0).
    anim["track_d"] = read_track(r, 0, extra_key_u32s=2)
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
        # track D: count, companion u32, frame ids, then two u32s per key (frame + info)
        + struct.pack("<I", 2)
        + struct.pack("<I", 0)
        + struct.pack("<2I", 0, 1)
        + struct.pack("<4I", 7, 8, 9, 10)
        # track E: one key, inner count 2; per-key = u32 + 5f + u32 + 2*(inner*3f) + 7f
        + struct.pack("<I", 1)
        + struct.pack("<I", 0)
        + struct.pack("<I", 0)
        + struct.pack("<5f", 1, 2, 3, 4, 5)
        + struct.pack("<I", 2)
        + struct.pack("<%df" % (2 * 3), *range(2 * 3))
        + struct.pack("<%df" % (2 * 3), *range(2 * 3))
        + struct.pack("<7f", *range(7))
    )
    blob = name32("(c) 1998 4X Tech. 0.95 (A)") + struct.pack("<I", 1) + anim

    doc = parse(blob)
    assert doc["consumed"] == len(blob), (doc["consumed"], len(blob))
    a = doc["animations"][0]
    assert a["name"] == "Anim" and a["parent"] == "Root"
    assert a["track_a"]["count"] == 2 and len(a["track_a"]["values"][0]) == 3
    assert len(a["track_c"]["values"][0]) == 4, "track C values are quaternions"
    assert a["track_d"]["keys"] == [(7, 8), (9, 10)]
    assert a["track_e"]["count"] == 1
    assert a["track_e"]["inner_count"] == 2
    assert tuple(a["track_e"]["frames"]) == (0,)
    assert len(a["track_e"]["tail"]) == 7

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
