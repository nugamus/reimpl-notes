"""Packed 16-bit image ("BMA"): loose `.bma` files and every `.bmp` member of Ring's `.at2`
archives. Spec: engines/ring/docs/formats/bma.ksy, E-0017.

Read by `aImageFileBma::Init` / `ReadImage` (RING_DVD.EXE 0x42ba40 / 0x42bbf0; header copy
0x42bb90); `aImage::Load` (0x413150) picks this loader for `.bmp` names read from an
archive and for `.bma` names:

    0x00 u32     seq_size        bytes of the index stream
    0x04 u16     core_count      entries in the colour table
    0x06 u16     pixels_per_entry  3 in every file
    0x08 u32     width
    0x0c u32     height
    0x10 u16[3]  last_pixels     written over the last 3 output pixels
    0x16 u8[54]  unk_bmp_header  a 24-bit Windows BMP header ('BM'); the loader skips it
    0x4c         index stream    seq_size bytes: bit stream (bitstream.py), literals of
                                 bit_length(core_count) bits, 6-bit cache indices
         u32     core_size
         ...     core stream     core_size bytes: bit stream of 16-bit values
    EOF

Decoded: the core stream gives core_count * 3 16-bit pixels (a table of 3-pixel entries),
the index stream gives width*height*2 // 3 // 2 indices; each index copies one entry
(3 pixels) to the output in order. Each stream may decode one extra code from its padding
bits (the engine decodes to the end of the stream into an oversized buffer).

    python engines/ring/tools/parsers/bma.py            # corpus
    python engines/ring/tools/parsers/bma.py --selftest
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bitstream import decode  # noqa: E402
from common import ParseError, Reader, main_for  # noqa: E402

# Named .bma but holding the text of a .dia subtitle file; no EXE names "bogus" (E-0017).
MISNAMED = {"00a8437538845c711bec93a2a840064e": "text of a .dia file (BOGUS*.BMA/BMP)"}


def parse(data: bytes, pixels: bool = False) -> dict:
    r = Reader(data)
    seq_size, core_count, per_entry = r.u32(), r.u16(), r.u16()
    width, height = r.u32(), r.u32()
    last = r.array("H", 3)
    bmp = r.bytes(54)
    r.check(per_entry == 3, f"pixels_per_entry {per_entry}", 6)
    r.check(0 < core_count and 0 < width and 0 < height, "empty image", 4)
    seq_start = r.pos
    r.skip(seq_size)
    core_size = r.u32()
    core_start = r.pos
    r.skip(core_size)
    r.expect_eof()

    need = width * height * 2 // per_entry // 2
    seq, seq_end = decode(data, core_count.bit_length(), 6, seq_start * 8,
                          (seq_start + seq_size) * 8, need + 2)
    core, core_end = decode(data, 16, 6, core_start * 8, (core_start + core_size) * 8,
                            core_count * per_entry + 2)
    for what, codes, want, end, limit in (("index", seq, need, seq_end, seq_start + seq_size),
                                          ("core", core, core_count * per_entry, core_end,
                                           core_start + core_size)):
        if not want <= len(codes) <= want + 1 or end < limit * 8:
            raise ParseError(f"{what} stream: {len(codes)} codes for {want}, "
                             f"stopped at bit {end} of {limit * 8}", limit)
    bad = [i for i in seq[:need] if i >= core_count]
    if bad:
        raise ParseError(f"index {bad[0]} >= core_count {core_count}", seq_start)
    out = {"width": width, "height": height, "core_count": core_count,
           "bmp_magic": bmp[:2], "last_pixels": last}
    if pixels:
        px = []
        for i in seq[:need]:
            px += core[3 * i:3 * i + 3]
        px += [0] * (width * height - len(px))
        px[-3:] = last
        out["pixels"] = px
    return out


def selftest() -> None:
    def stream(values, bits):
        s = "".join("0" + format(v, f"0{bits}b") for v in values)
        n = (len(s) + 7) // 8
        return int(s.ljust(n * 8, "0"), 2).to_bytes(n, "big")

    core = stream([1, 2, 3, 4, 5, 6], 16)          # two entries of 3 pixels
    seq = stream([1, 0], 2)                         # bit_length(2) == 2
    blob = struct.pack("<IHHII3H", len(seq), 2, 3, 3, 2, 7, 8, 9) + b"BM" + bytes(52)
    blob += seq + struct.pack("<I", len(core)) + core
    out = parse(blob, pixels=True)
    assert out["pixels"] == [4, 5, 6, 7, 8, 9], out["pixels"]
    try:
        parse(blob + b"\0")
    except ParseError:
        pass
    else:
        raise AssertionError("trailing byte accepted")


if __name__ == "__main__":
    raise SystemExit(main_for(parse, "packed image (BMA) validator", [".bma"], [".bmp"],
                              archives=(".at2",), selftest=selftest, not_this_type=MISNAMED))
