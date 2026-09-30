"""Validate Grumpa's `.fxi` surface images (E-0008, E-0009).

`.fxi` is the game's own surface format, loaded by `FUN_00418de0` (the `fxi` case of the
generic loader `FUN_004189d0`, which switches on the extension `tga`/`raw`/`fxi`/`pcx`/
`jpg`; strings and code in the decrypted `Grumpa.exe`, E-0003). The surface is 16-bit
(`FUN_00418910(this, w, h, 0x10)`), either raw or block-compressed:

    u8   version         1
    u8   flag            0 = raw pixels, non-zero = block-compressed
    u16  width           800 in the whole corpus
    u16  height          600
    u32  field0          usually 0 (colour key?)
    u32  field1
    u32  field2

    flag == 0:  width*height*2 bytes of raw 16-bit pixels.

    flag != 0:  (width/8)*(height/8) control bytes, one per 8x8 block, row-major; then,
                for each block in that order, two sub-blocks — the control byte's low
                nibble then its high nibble — each a mode:
                    0  solid        1 byte
                    1  two colours   8-byte 1bpp mask + 2 x u16 colours   (10 bytes)
                    2  four colours 16-byte 2bpp mask + 4 x u16 colours   (20 bytes)
                    3  raw          64 bytes (an 8x4 half-block of u16 pixels)
                Every byte of the file is one of: header, control map, or sub-block data.

This validator proves the container: header + control map + the exact per-mode byte counts
account for every byte of all 316 files. The per-mode pixel maths (how the masks and
colours fill the 8x8 block) is `FUN_00418de0`'s inner writes, specced separately before the
renderer (Q-0004).

    python engines/grumpa/tools/parsers/fxi.py --selftest
    python engines/grumpa/tools/parsers/fxi.py [root]        # default: the cab corpus
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/grumpa/discs/cab"

HEADER = 18  # u8 version, u8 flag, u16 w, u16 h, u32 x3
MODE_BYTES = {0: 1, 1: 10, 2: 20, 3: 64}


class ParseError(Exception):
    pass


def parse(d: bytes) -> dict:
    """{version, flag, width, height, blocks:[(lo,hi)]|None}. Raises unless every byte is
    consumed, so a clean parse == the whole file fit the format."""
    if len(d) < HEADER:
        raise ParseError("shorter than the header")
    version, flag, width, height = struct.unpack_from("<BBHH", d, 0)
    off = HEADER
    if flag == 0:
        need = width * height * 2
        if off + need != len(d):
            raise ParseError(f"raw: {off + need} expected, {len(d)} on disk")
        return {"version": version, "flag": flag, "width": width, "height": height, "blocks": None}
    bw, bh = width >> 3, height >> 3
    ctrl = d[off:off + bw * bh]
    if len(ctrl) != bw * bh:
        raise ParseError("control map truncated")
    off += bw * bh
    blocks = []
    for c in ctrl:
        lo, hi = c & 0xF, c >> 4
        if lo > 3 or hi > 3:
            raise ParseError(f"block mode {lo}/{hi} out of range")
        off += MODE_BYTES[lo] + MODE_BYTES[hi]
        blocks.append((lo, hi))
    if off != len(d):
        raise ParseError(f"{off} consumed, {len(d)} on disk")
    return {"version": version, "flag": flag, "width": width, "height": height, "blocks": blocks}


def validate(root: Path) -> int:
    files = sorted(root.rglob("*.fxi"))
    if not files:
        sys.exit(f"no .fxi under {root}")
    bad = 0
    dims: Counter = Counter()
    flags: Counter = Counter()
    modes: Counter = Counter()
    for f in files:
        try:
            r = parse(f.read_bytes())
        except ParseError as e:
            bad += 1
            print(f"FAIL {f.relative_to(root)}: {e}")
            continue
        dims[(r["width"], r["height"])] += 1
        flags[r["flag"]] += 1
        for lo, hi in r["blocks"] or []:
            modes[lo] += 1
            modes[hi] += 1
    print(f"{len(files) - bad}/{len(files)} .fxi parsed, every byte consumed")
    print("  sizes: " + ", ".join(f"{w}x{h}:{n}" for (w, h), n in dims.most_common()))
    print("  flags: " + ", ".join(f"{k}:{v}" for k, v in sorted(flags.items())))
    print("  block modes: " + ", ".join(f"{k}:{v}" for k, v in sorted(modes.items())))
    return bad


def selftest() -> None:
    hdr = struct.pack("<BBHH", 1, 0, 2, 2) + b"\0" * 12
    assert parse(hdr + b"\0" * 8)["blocks"] is None  # 2x2 raw = 8 bytes
    # one 8x8 block, low nibble mode 0 (1 B), high nibble mode 3 (64 B)
    comp = struct.pack("<BBHH", 1, 1, 8, 8) + b"\0" * 12 + bytes([0x30]) + b"\0" * (1 + 64)
    r = parse(comp)
    assert r["flag"] == 1 and r["blocks"] == [(0, 3)], r
    for bad in (hdr + b"\0" * 7, comp + b"\0", struct.pack("<BBHH", 1, 1, 8, 8) + b"\0" * 12 + bytes([0x40])):
        try:
            parse(bad)
            raise AssertionError("should have failed")
        except ParseError:
            pass
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=str(CORPUS))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    else:
        sys.exit(1 if validate(Path(a.root)) else 0)
