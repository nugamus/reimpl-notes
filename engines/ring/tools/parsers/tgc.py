"""Packed TGA ("TGC"): every `.tga` member of Ring's `.at2` archives. Spec:
engines/ring/docs/formats/tgc.ksy, E-0018.

Read by `aImageFileTgc::Init` (RING_DVD.EXE 0x42b230, strings name it; the function also
carries an `aFileIoBuf::Init` message), `ReadInfo` 0x42b540, `ReadImage` 0x42b600;
`aImage::Load` (0x413150) picks it for `.tga` names read from an archive and for `.tgc`:

    u32 chunk_count
    u32 unpacked_size
    chunk_count x { u32 packed_size, u32 chunk_unpacked_size,
                    packed_size bytes of bit stream (16-bit literals, 6-bit indices) }
    EOF

Each chunk decodes to chunk_unpacked_size bytes (plus at most one padding code), placed one
after the other; the sum is unpacked_size. The result is a TGA file: 18-byte header with
image type 2 (uncompressed true colour) and 32 bits per pixel (ReadInfo rejects anything
else), then width*height*4 bytes of BGRA rows, bottom-up (ReadImage fills rows from the
last up), optionally the 26-byte TGA 2.0 footer (two zero offsets and
"TRUEVISION-XFILE." and a NUL), which the engine does not read.

    python engines/ring/tools/parsers/tgc.py            # corpus
    python engines/ring/tools/parsers/tgc.py --selftest
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bitstream import decode  # noqa: E402
from common import ParseError, Reader, main_for  # noqa: E402


def unpack(data: bytes) -> bytes:
    r = Reader(data)
    count, unpacked = r.u32(), r.u32()
    r.check(count > 0, "no chunks", 0)
    out = bytearray()
    for _ in range(count):
        packed, want = r.u32(), r.u32()
        start = r.pos
        r.skip(packed)
        codes, end = decode(data, 16, 6, start * 8, (start + packed) * 8, want // 2 + 1)
        r.check(want % 2 == 0 and want // 2 <= len(codes) <= want // 2 + 1
                and end >= (start + packed) * 8,
                f"chunk: {len(codes)} codes for {want} bytes, stopped at bit {end}", start)
        out += struct.pack(f"<{want // 2}H", *codes[:want // 2])
    r.expect_eof()
    r.check(len(out) == unpacked, f"unpacked {len(out)} != {unpacked}", 4)
    return bytes(out)


def parse_tga32(tga: bytes) -> dict:
    """The unpacked TGA: 18-byte header, type 2, 32 bpp, pixels to the end."""
    r = Reader(tga)
    id_len, cmap_type, img_type = r.u8(), r.u8(), r.u8()
    cmap = r.bytes(5)
    x0, y0, w, h, bpp, desc = r.u16(), r.u16(), r.u16(), r.u16(), r.u8(), r.u8()
    r.check(img_type == 2 and bpp == 32 and cmap_type == 0 and id_len == 0,
            f"type {img_type} bpp {bpp} cmap {cmap_type} id {id_len}", 2)
    r.skip(w * h * 4)
    footer = False
    if r.remaining == 26:  # TGA 2.0 footer, not read by the engine
        ext_off, dev_off, sig = r.u32(), r.u32(), r.bytes(18)
        r.check(ext_off == dev_off == 0 and sig == b"TRUEVISION-XFILE.\0", "bad footer")
        footer = True
    r.expect_eof()
    return {"width": w, "height": h, "origin": (x0, y0), "descriptor": desc,
            "unk_cmap": cmap, "footer": footer}


def parse(data: bytes) -> dict:
    return parse_tga32(unpack(data))


def selftest() -> None:
    tga = struct.pack("<BBB5sHHHHBB", 0, 0, 2, bytes(5), 0, 0, 1, 1, 32, 8) + b"\x01\x02\x03\x04"
    vals = struct.unpack(f"<{len(tga) // 2}H", tga)
    s = "".join("0" + format(v, "016b") for v in vals)
    n = (len(s) + 7) // 8
    bits = int(s.ljust(n * 8, "0"), 2).to_bytes(n, "big")
    blob = struct.pack("<IIII", 1, len(tga), len(bits), len(tga)) + bits
    assert parse(blob)["width"] == 1
    try:
        parse(blob + b"\0")
    except ParseError:
        pass
    else:
        raise AssertionError("trailing byte accepted")


if __name__ == "__main__":
    raise SystemExit(main_for(parse, "packed TGA (TGC) validator", [".tgc"], [".tga"],
                              archives=(".at2",), selftest=selftest))
