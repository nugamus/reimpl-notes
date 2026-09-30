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
                for each block in that order, two planes — the control byte's low nibble
                codes the high byte of every pixel in the block, its high nibble codes the
                low byte (`pixel16 = high << 8 | low`). Each plane is 8x8 bytes in one of
                four modes:
                    0  solid       1 byte, the value of all 64
                    1  1bpp         8-byte mask (bit 1<<col of row byte) + 2 values (10 B)
                    2  2bpp        16-byte mask (2 bits/pixel) + 4 values           (20 B)
                    3  raw         64 bytes, the plane directly
                Every byte of the file is header, control map, or plane data.

`decode()` returns the 16-bit values; `validate` proves the container and decode over all
316 files. From `FUN_00418de0` in the decrypted `Grumpa.exe` (E-0009); the split into a
high-byte and a low-byte plane, each coded on its own 8x8 redundancy, is the whole codec.

All 316 corpus `.fxi` are Z-depth buffers (names `*_IZ`/`*_Z*`), one per pre-rendered
background: the 16-bit value is a depth, and `CFXZBuffer::CreateFromFile` loads it for
compositing the 3D actors into the 2D scene. The same format also serves colour surfaces
(`CFXSurface`, which reads the 16 bits as RGB555, `(p>>7)&0xf8` etc.); `to_rgb` below is a
555 preview, only meaningful for a colour `.fxi`.

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


def _plane(d: bytes, off: int, mode: int, out: list, shift: int) -> int:
    """Decode one 8x8 byte plane starting at `off`, writing each byte into `out[i]` at
    `<< shift` (8 for the high plane, 0 for the low). Returns the new offset."""
    if mode == 0:
        v = d[off]
        for i in range(64):
            out[i] |= v << shift
        return off + 1
    if mode == 1:
        mask, v0, v1 = d[off:off + 8], d[off + 8], d[off + 9]
        for row in range(8):
            for col in range(8):
                out[row * 8 + col] |= (v1 if mask[row] & (1 << col) else v0) << shift
        return off + 10
    if mode == 2:
        mask, vals = d[off:off + 16], d[off + 16:off + 20]
        for row in range(8):
            b0, b1 = mask[row * 2], mask[row * 2 + 1]
            for col in range(8):
                src = b0 if col < 4 else b1
                idx = (src >> ((col & 3) * 2)) & 3
                out[row * 8 + col] |= vals[idx] << shift
        return off + 20
    plane = d[off:off + 64]  # mode 3, raw
    for i in range(64):
        out[i] |= plane[i] << shift
    return off + 64


def decode(d: bytes) -> tuple[int, int, list[int]]:
    """(width, height, row-major list of 16-bit pixels)."""
    r = parse(d)
    w, h = r["width"], r["height"]
    px = [0] * (w * h)
    if r["flag"] == 0:
        for i in range(w * h):
            px[i] = d[HEADER + i * 2] | d[HEADER + i * 2 + 1] << 8
        return w, h, px
    off = HEADER + (w >> 3) * (h >> 3)
    bw = w >> 3
    for bi, (lo, hi) in enumerate(r["blocks"]):
        blk = [0] * 64
        off = _plane(d, off, lo, blk, 8)   # low nibble -> high byte
        off = _plane(d, off, hi, blk, 0)   # high nibble -> low byte
        bx, by = (bi % bw) * 8, (bi // bw) * 8
        for row in range(8):
            base = (by + row) * w + bx
            src = row * 8
            px[base:base + 8] = blk[src:src + 8]
    return w, h, px


def to_rgb(px: list[int]) -> bytes:
    """RGB565 -> 24-bit RGB bytes (the surface format, DAT check 0xf800 = 565, E-0009)."""
    out = bytearray(len(px) * 3)
    for i, p in enumerate(px):
        r5, g6, b5 = p >> 11, (p >> 5) & 0x3F, p & 0x1F
        out[i * 3] = r5 << 3 | r5 >> 2
        out[i * 3 + 1] = g6 << 2 | g6 >> 4
        out[i * 3 + 2] = b5 << 3 | b5 >> 2
    return bytes(out)


def write_png(path: Path, w: int, h: int, rgb: bytes) -> None:
    import struct as _s
    import zlib

    def chunk(tag, data):
        return _s.pack(">I", len(data)) + tag + data + _s.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * w * 3:(y + 1) * w * 3]
    path.write_bytes(b"\x89PNG\r\n\x1a\n"
                     + chunk(b"IHDR", _s.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
                     + chunk(b"IEND", b""))


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
            d = f.read_bytes()
            r = parse(d)
            w, h, px = decode(d)  # decode too, so a bad plane offset would raise here
            assert len(px) == w * h
        except (ParseError, IndexError, AssertionError) as e:
            bad += 1
            print(f"FAIL {f.relative_to(root)}: {e}")
            continue
        dims[(r["width"], r["height"])] += 1
        flags[r["flag"]] += 1
        for lo, hi in r["blocks"] or []:
            modes[lo] += 1
            modes[hi] += 1
    print(f"{len(files) - bad}/{len(files)} .fxi parsed and decoded, every byte consumed")
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
    # pixel maths: high plane solid 0xAB (low nibble 0), low plane a 1bpp checker (high nibble 1)
    mask = bytes([0x55, 0xAA] * 4)  # rows alternate 0x55/0xAA -> a checkerboard of bit(1<<col)
    blk = struct.pack("<BBHH", 1, 1, 8, 8) + b"\0" * 12 + bytes([0x10]) + bytes([0xAB]) + mask + bytes([0x11, 0x22])
    w, h, px = decode(blk)
    assert (w, h) == (8, 8)
    # pixel(0,0): row0 mask 0x55 bit0 set -> low value v1=0x22; high plane 0xAB -> 0xAB22
    assert px[0] == 0xAB22, hex(px[0])
    # pixel(1,0): row0 bit1 clear -> low v0=0x11 -> 0xAB11
    assert px[1] == 0xAB11, hex(px[1])
    # raw round-trip
    raw = struct.pack("<BBHH", 1, 0, 2, 1) + b"\0" * 12 + struct.pack("<HH", 0x1234, 0x5678)
    assert decode(raw) == (2, 1, [0x1234, 0x5678])
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=str(CORPUS))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--png", metavar="FILE.fxi", help="decode one file to FILE.png beside it")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.png:
        src = Path(a.png)
        w, h, px = decode(src.read_bytes())
        out = src.with_suffix(".png")
        write_png(out, w, h, to_rgb(px))
        print(f"{src.name}: {w}x{h} -> {out}")
    else:
        sys.exit(1 if validate(Path(a.root)) else 0)
