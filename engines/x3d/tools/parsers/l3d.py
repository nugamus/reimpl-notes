"""`.L3D` parser and corpus validator.

Derived from `X3d_Load_Sdk_l3d` (`x3d.dll` `0x100012fd`) and the loader it dispatches to,
`FUN_10014d50` (`x3d.dll` `0x10014d50`). The skeleton of the dispatch is the same as the
`.O3D` and `.A3D` loaders — read a 32-byte signature, dispatch to a per-format reader, then
either succeed or fail loudly. The per-light layout comes from the read sequence inside
`FUN_10014d50`:

    thunk_FUN_1000bb50(cursor, dst, 0x20)  # 32-byte name
    thunk_FUN_1000bb20(cursor, dst)        # f32 x
    thunk_FUN_1000bb20(cursor, dst+4)      # f32 y
    thunk_FUN_1000bb20(cursor, dst+8)      # f32 z
    thunk_FUN_1000baf0(cursor, dst)        # u8 R
    thunk_FUN_1000baf0(cursor, dst+1)      # u8 G
    thunk_FUN_1000baf0(cursor, dst+2)      # u8 B
    thunk_FUN_1000bb20(cursor, dst)        # f32  (unknown)
    thunk_FUN_1000bb20(cursor, dst)        # f32  (unknown)
    thunk_FUN_1000bb20(cursor, dst)        # f32  (unknown)
    thunk_FUN_1000ba90(cursor, dst)        # u32  (unknown)
    thunk_FUN_1000ba90(cursor, dst)        # u32  (unknown)
    thunk_FUN_1000ba90(cursor, &flag)      # u32  is_spot
    [if is_spot: +5 f32 target xyz + angles]

The `if is_spot` block then reads another 5 f32s — three for the spot target xyz plus two
cone angles. None of the five corpus files carries a spot light, so that branch is parsed
but never cross-validated (no sample).

Per CLAUDE.md rule 2 the validator must consume every byte of every `.L3D` file with no
out-of-range indices. `parse` insists on `expect_eof()` at the end.

    python engines/x3d/tools/parsers/l3d.py                 # validate the corpus
    python engines/x3d/tools/parsers/l3d.py --selftest
    python engines/x3d/tools/parsers/l3d.py --file <path>  # one file, structural summary
"""

from __future__ import annotations

import struct
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

SIG_LEN = 32
# strcmp in the loader: only the bytes up to the NUL matter. Bytes 27..31 are uninitialised
# writer memory and vary between files, so compare only up to the first NUL.
SIGNATURES = {
    b"(c) 1998 4X Tech. 0.95 (L)": "0.95",
    b"(c) 1998 4X Tech. 1.00 (L)": "1.00",
}


def _parse_signature(r: Reader) -> str:
    raw = r.bytes(SIG_LEN)
    end = raw.find(b"\0")
    if end < 0:
        raise ParseError("signature has no NUL terminator", r.pos - SIG_LEN)
    text = raw[:end]
    if text not in SIGNATURES:
        raise ParseError(f"unknown signature {text!r}", r.pos - SIG_LEN)
    return SIGNATURES[text]


def _parse_light(r: Reader) -> dict:
    light = {
        "name": r.fixed_str(32),
        "position": r.array("f", 3),
        "color": [r.u8(), r.u8(), r.u8()],
        "extra_floats": [r.f32(), r.f32(), r.f32()],
        "extra_u32s": [r.u32(), r.u32()],
        "is_spot": r.u32(),
    }
    if light["is_spot"]:
        light["spot_target"] = r.array("f", 3)
        light["spot_angles"] = [r.f32(), r.f32()]
    return light


def parse(data: bytes) -> dict:
    r = Reader(data)
    version = _parse_signature(r)
    count = r.u32()
    lights = [_parse_light(r) for _ in range(count)]
    r.expect_eof()
    return {"version": version, "count": count, "lights": lights}


def _selftest() -> None:
    sig = b"(c) 1998 4X Tech. 0.95 (L)\0"
    sig = sig + b"\x78\xc4\xa1\x63\x00"  # padding to fill 32 bytes
    sig = sig.ljust(32, b"\0")

    # values exact in IEEE-754 float32 (powers of two, simple fractions)
    pf = (0.5, 0.25, 0.125)
    pt = (8.0, 4.0, 2.0)
    pa = (30.0, 45.0)

    def make_non_spot(name: bytes) -> bytes:
        return (
            name.ljust(32, b"\0")
            + struct.pack("<3f", 1.0, 2.0, 3.0)
            + bytes([10, 20, 30])
            + struct.pack("<3f", *pf)
            + struct.pack("<2I", 100, 200)
            + struct.pack("<I", 0)
        )

    def make_spot(name: bytes) -> bytes:
        return (
            name.ljust(32, b"\0")
            + struct.pack("<3f", 1.0, 2.0, 3.0)
            + bytes([10, 20, 30])
            + struct.pack("<3f", *pf)
            + struct.pack("<2I", 100, 200)
            + struct.pack("<I", 1)
            + struct.pack("<5f", *pt, *pa)
        )

    blob = sig + struct.pack("<I", 2) + make_non_spot(b"Omni") + make_spot(b"Spot")
    doc = parse(blob)
    assert doc["version"] == "0.95"
    assert doc["count"] == 2
    assert doc["lights"][0]["name"] == "Omni"
    assert doc["lights"][0]["position"] == (1.0, 2.0, 3.0)
    assert doc["lights"][0]["color"] == [10, 20, 30]
    assert doc["lights"][0]["extra_floats"] == [pf[0], pf[1], pf[2]]
    assert doc["lights"][0]["extra_u32s"] == [100, 200]
    assert doc["lights"][0]["is_spot"] == 0
    assert doc["lights"][1]["is_spot"] == 1
    assert doc["lights"][1]["spot_target"] == (pt[0], pt[1], pt[2])
    assert doc["lights"][1]["spot_angles"] == [pa[0], pa[1]]

    # trailing byte must fail, not be silently ignored
    try:
        parse(blob + b"\0")
    except ParseError as exc:
        assert "unconsumed" in exc.message
    else:
        raise AssertionError("trailing byte accepted")

    # truncation must fail
    try:
        parse(blob[:-4])
    except ParseError:
        pass
    else:
        raise AssertionError("truncated file accepted")

    # bad signature
    try:
        parse(b"(c) 1998 4X Tech. 0.95 (O)\0" + b"\x00" * 4 + struct.pack("<I", 0))
    except ParseError as exc:
        assert "signature" in exc.message or "unknown" in exc.message
    else:
        raise AssertionError("wrong signature accepted")

    # 1.00 signature parses
    blob10 = (
        b"(c) 1998 4X Tech. 1.00 (L)\0".ljust(32, b"\0")
        + struct.pack("<I", 0)
    )
    assert len(blob10) == 36
    doc10 = parse(blob10)
    assert doc10["version"] == "1.00"
    assert doc10["lights"] == []

    print("selftest ok")


def _dump(path: Path) -> None:
    doc = parse(path.read_bytes())
    print(
        f"{path.name}: version {doc['version']}, {doc['count']} light(s),"
        f" {path.stat().st_size} bytes"
    )
    for i, light in enumerate(doc["lights"]):
        spot = (
            "SPOT target="
            + repr(light["spot_target"])
            + " angles="
            + repr(light["spot_angles"])
            if light["is_spot"]
            else "omni"
        )
        print(
            f"  [{i}] {light['name']:>16}  pos={light['position']}"
            f"  rgb={tuple(light['color'])}  extra_f={light['extra_floats']}"
            f"  extra_u={light['extra_u32s']}  {spot}"
        )


def main(argv: list) -> int:
    if "--selftest" in argv:
        _selftest()
        return 0

    args = corpus_argparser(".L3D validator").parse_args(argv)

    if args.file:
        _dump(args.file)
        return 0

    root = args.root or default_root()
    files = find_files(root, "*.l3d")
    if not files:
        print(f"no .l3d files under {root}", file=sys.stderr)
        return 2

    ok = 0
    failures: list[tuple[Path, str]] = []
    versions: dict[str, int] = {}
    totals = {"lights": 0, "spot_lights": 0, "bytes": 0}

    for path in files:
        data = path.read_bytes()
        try:
            doc = parse(data)
        except ParseError as exc:
            failures.append((path, f"{exc.message} at 0x{exc.offset:08x}"))
            continue
        ok += 1
        versions[doc["version"]] = versions.get(doc["version"], 0) + 1
        totals["lights"] += doc["count"]
        totals["spot_lights"] += sum(1 for l in doc["lights"] if l["is_spot"])
        totals["bytes"] += len(data)

    print(f"corpus: {root}")
    print(f"files: {len(files)}  passed: {ok}  failed: {len(failures)}")
    print(f"  versions:  {versions}")
    print(f"  lights:    {totals['lights']}")
    print(f"  spot:      {totals['spot_lights']}")
    print(f"  bytes:     {totals['bytes']}")
    for path, err in failures[:25]:
        print(f"  FAIL {path}  {err}")
    if len(failures) > 25:
        print(f"  ... and {len(failures) - 25} more failures")

    print("100% of corpus parsed" if ok == len(files) else "SPEC INCOMPLETE")
    return 0 if ok == len(files) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
