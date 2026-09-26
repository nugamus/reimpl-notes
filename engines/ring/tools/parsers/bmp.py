"""Plain Windows BMP and TGA files on disk (not in archives). Spec:
engines/ring/docs/formats/README.md "Plain BMP / TGA", E-0019.

Loaded by `aImageFileBMP` (ReadHeader 0x42a8b0, ReadInfo 0x42a900, ReadImage 0x42aac0)
and `aImageFileTGA` (ReadInfo 0x42a190, ReadImage 0x42a220) when `aImage::Load` (0x413150)
reads from disk ('e'). Only the layouts found in the corpus are accepted:

    BMP: 14-byte file header 'BM', 40-byte BITMAPINFOHEADER, 24 bpp, no compression,
         rows padded to 4 bytes, bottom-up; after the pixels nothing or two zero
         bytes (the file-size field includes them)
    TGA: 18-byte header, type 2, 24 or 32 bpp, no id, no colour map, rows to the end,
         optional 26-byte TGA 2.0 footer

    python engines/ring/tools/parsers/bmp.py            # corpus (.bmp and .tga on disk)
    python engines/ring/tools/parsers/bmp.py --selftest
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bma import MISNAMED  # noqa: E402
from common import ParseError, Reader, main_for  # noqa: E402


def parse_bmp(data: bytes) -> dict:
    r = Reader(data)
    r.magic(b"BM")
    size, _res, off = r.u32(), r.u32(), r.u32()
    hdr = r.u32()
    r.check(hdr == 40, f"info header size {hdr}", 14)
    w, h, planes, bpp, comp = r.i32(), r.i32(), r.u16(), r.u16(), r.u32()
    img_size, xppm, yppm, used, important = r.array("I", 5)
    r.check(bpp == 24 and comp == 0 and planes == 1 and h > 0 and w > 0,
            f"{bpp} bpp, compression {comp}", 28)
    r.check(off == 54, f"pixel offset {off}", 10)
    r.skip((w * 3 + 3) // 4 * 4 * h)
    pad = 0
    if r.remaining == 2:  # some writers add two zero bytes; the size field counts them
        r.check(r.u16() == 0, "non-zero pad")
        pad = 2
    r.expect_eof()
    r.check(size == len(data), f"file size field {size} != {len(data)}", 2)
    return {"width": w, "height": h, "unk_image_size": img_size, "unk_ppm": (xppm, yppm),
            "pad": pad}


def parse_tga(data: bytes) -> dict:
    r = Reader(data)
    id_len, cmap_type, img_type = r.u8(), r.u8(), r.u8()
    r.skip(5)
    r.skip(4)
    w, h, bpp, desc = r.u16(), r.u16(), r.u8(), r.u8()
    r.check(img_type == 2 and bpp in (24, 32) and not cmap_type and not id_len,
            f"type {img_type} bpp {bpp}", 2)
    r.skip(w * h * bpp // 8)
    if r.remaining == 26:
        r.skip(8)
        r.check(r.bytes(18) == b"TRUEVISION-XFILE." + bytes(1), "bad footer")
    r.expect_eof()
    return {"width": w, "height": h, "bpp": bpp, "descriptor": desc}


def parse(data: bytes) -> dict:
    return parse_bmp(data) if data[:2] == b"BM" else parse_tga(data)


def selftest() -> None:
    bmp = b"BM" + struct.pack("<3I", 54 + 8, 0, 54) + struct.pack(
        "<IiiHHI5I", 40, 2, 1, 1, 24, 0, 0, 0, 0, 0, 0) + bytes(8)
    assert parse(bmp)["width"] == 2
    tga = struct.pack("<BBB5s4sHHBB", 0, 0, 2, bytes(5), bytes(4), 1, 1, 24, 0) + bytes(3)
    assert parse(tga)["bpp"] == 24
    for bad in (bmp + b"\0", tga + b"\0"):
        try:
            parse(bad)
        except ParseError:
            continue
        raise AssertionError("trailing byte accepted")


if __name__ == "__main__":
    raise SystemExit(main_for(parse, "plain BMP/TGA validator", [".bmp", ".tga"],
                              selftest=selftest, not_this_type=MISNAMED))
