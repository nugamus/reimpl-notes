"""`.C3D` parser and corpus validator.

Derived from `X3d_Load_Sdk_c3d` (`x3d.dll` `0x1000124e`) and the loader it dispatches to,
`FUN_100148e0` (`x3d.dll` `0x100148e0`). Same skeleton as the `.O3D`/`.A3D`/`.L3D`
loaders — read a 32-byte signature, dispatch to a per-format reader, then either succeed
or fail loudly.

Per-camera layout comes from the read sequence inside `FUN_100148e0`:

    thunk_FUN_1000bb50(cursor, dst+0x0c, 0x20)         # 32-byte name
    thunk_FUN_1000bb20(cursor, dst+0x2c)               # f32
    thunk_FUN_1000bb20(cursor, dst+0x30)               # f32
    thunk_FUN_1000bb20(cursor, dst+0x34)               # f32
    thunk_FUN_1000bb20(cursor, dst+0x3c)               # f32
    thunk_FUN_1000bb20(cursor, dst+0x40)               # f32
    thunk_FUN_1000bb20(cursor, dst+0x44)               # f32
    thunk_FUN_1000bb20(cursor, dst+0x54)               # f32
    thunk_FUN_1000bb20(cursor, dst+0x58)               # f32
    thunk_FUN_1000bb20(cursor, dst+0x4c)               # f32
    thunk_FUN_1000bb20(cursor, dst+0x50)               # f32

The struct offsets are non-monotonic in file order (0x54/0x58 come before 0x4c/0x50)
because `bb20` only advances the reader; the destination offset is a fixed camera-object
slot, not the next byte position. The parser tracks reader order, not struct order.

The 10 f32s are stored under the same key for every camera; their meaning is opaque to
this point (see OPEN-QUESTIONS.md for likely groupings — three camera slots at +0x2c,
+0x3c, +0x4c are the best guesses for position, target, and up).

Per CLAUDE.md rule 2 the validator must consume every byte of every `.C3D` file with no
out-of-range indices. `parse` insists on `expect_eof()` at the end.

    python engines/x3d/tools/parsers/c3d.py                 # validate the corpus
    python engines/x3d/tools/parsers/c3d.py --selftest
    python engines/x3d/tools/parsers/c3d.py --file <path>  # one file, structural summary
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
    b"(c) 1998 4X Tech. 0.95 (C)": "0.95",
    b"(c) 1998 4X Tech. 1.00 (C)": "1.00",
}

# Reading order is the file order — bb20 advances the cursor. Struct offsets are kept
# here so a future struct-savvy reader can map file index -> camera field. Order in the
# tuple matches the call sequence inside FUN_100148e0.
_FLOAT_STRUCT_OFFSETS = (0x2C, 0x30, 0x34, 0x3C, 0x40, 0x44, 0x54, 0x58, 0x4C, 0x50)


def _parse_signature(r: Reader) -> str:
    raw = r.bytes(SIG_LEN)
    end = raw.find(b"\0")
    if end < 0:
        raise ParseError("signature has no NUL terminator", r.pos - SIG_LEN)
    text = raw[:end]
    if text not in SIGNATURES:
        raise ParseError(f"unknown signature {text!r}", r.pos - SIG_LEN)
    return SIGNATURES[text]


def _parse_camera(r: Reader) -> dict:
    return {
        "name": r.fixed_str(32),
        # 10 f32s in file order; meaning opaque (see Q-0014).
        "params": [r.f32() for _ in range(10)],
    }


def parse(data: bytes) -> dict:
    r = Reader(data)
    version = _parse_signature(r)
    count = r.u32()
    cameras = [_parse_camera(r) for _ in range(count)]
    r.expect_eof()
    return {"version": version, "count": count, "cameras": cameras}


def _selftest() -> None:
    sig = b"(c) 1998 4X Tech. 0.95 (C)\0".ljust(32, b"\0")

    def make_camera(name: bytes) -> bytes:
        # values exact in IEEE-754 float32 (powers of two, simple fractions)
        return name.ljust(32, b"\0") + struct.pack(
            "<10f", 1.0, 2.0, 4.0, 8.0, 16.0, 0.5, 0.25, 0.125, 32.0, 64.0
        )

    blob = sig + struct.pack("<I", 2) + make_camera(b"Cam01") + make_camera(b"Cam02")
    doc = parse(blob)
    assert doc["version"] == "0.95"
    assert doc["count"] == 2
    assert doc["cameras"][0]["name"] == "Cam01"
    assert doc["cameras"][0]["params"] == [
        1.0, 2.0, 4.0, 8.0, 16.0, 0.5, 0.25, 0.125, 32.0, 64.0
    ]
    assert doc["cameras"][1]["name"] == "Cam02"

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
        parse(b"(c) 1998 4X Tech. 0.95 (O)\0".ljust(32, b"\0") + struct.pack("<I", 0))
    except ParseError as exc:
        assert "signature" in exc.message or "unknown" in exc.message
    else:
        raise AssertionError("wrong signature accepted")

    # 1.00 signature parses with no cameras
    blob10 = b"(c) 1998 4X Tech. 1.00 (C)\0".ljust(32, b"\0") + struct.pack("<I", 0)
    doc10 = parse(blob10)
    assert doc10["version"] == "1.00"
    assert doc10["cameras"] == []

    print("selftest ok")


def _dump(path: Path) -> None:
    doc = parse(path.read_bytes())
    print(
        f"{path.name}: version {doc['version']}, {doc['count']} camera(s),"
        f" {path.stat().st_size} bytes"
    )
    for i, cam in enumerate(doc["cameras"]):
        print(f"  [{i}] {cam['name']:>16}  params={cam['params']}")


def main(argv: list) -> int:
    if "--selftest" in argv:
        _selftest()
        return 0

    args = corpus_argparser(".C3D validator").parse_args(argv)

    if args.file:
        _dump(args.file)
        return 0

    root = args.root or default_root()
    files = find_files(root, "*.C3D")
    if not files:
        print(f"no .c3d files under {root}", file=sys.stderr)
        return 2

    ok = 0
    failures: list[tuple[Path, str]] = []
    versions: dict[str, int] = {}
    totals = {"cameras": 0, "bytes": 0}

    for path in files:
        data = path.read_bytes()
        try:
            doc = parse(data)
        except ParseError as exc:
            failures.append((path, f"{exc.message} at 0x{exc.offset:08x}"))
            continue
        ok += 1
        versions[doc["version"]] = versions.get(doc["version"], 0) + 1
        totals["cameras"] += doc["count"]
        totals["bytes"] += len(data)

    print(f"corpus: {root}")
    print(f"files: {len(files)}  passed: {ok}  failed: {len(failures)}")
    print(f"  versions:  {versions}")
    print(f"  cameras:   {totals['cameras']}")
    print(f"  bytes:     {totals['bytes']}")
    for path, err in failures[:25]:
        print(f"  FAIL {path}  {err}")
    if len(failures) > 25:
        print(f"  ... and {len(failures) - 25} more failures")

    print("100% of corpus parsed" if ok == len(files) else "SPEC INCOMPLETE")
    return 0 if ok == len(files) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))