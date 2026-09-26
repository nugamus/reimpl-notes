"""Windows raster font files (`.fon`, and the DVD's `ARXRIN.GRE`/`.HEB`/`.SLO`): an NE
executable whose resources are one FONTDIR (0x8007) and FNT 2.0 fonts (0x8008). Spec:
engines/ring/docs/formats/README.md "Fonts", E-0043.

Each font resource is accounted for byte by byte: the 118-byte header, the character table
(last - first + 2 entries of width u16, offset u16), every glyph's bitmap (ceil(width / 8)
columns of pixel-height bytes, at its offset), the face name at dfFace; the only bytes left
over must be zero. Bytes after dfSize are the resource's alignment padding (zero, or 0xFF in
the DVD's ARXRIN.SLO) and are not part of the font. The NE file itself is walked
through its header, segment-less resource table and resource name strings.

    python engines/ring/tools/parsers/fon.py            # corpus
    python engines/ring/tools/parsers/fon.py --selftest
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ParseError, main_for  # noqa: E402

RT_FONTDIR, RT_FONT = 0x8007, 0x8008
HEADER = 0x76


def parse_fnt(res: bytes) -> dict:
    if len(res) < HEADER:
        raise ParseError("font resource shorter than its header", 0)
    version, size = struct.unpack_from("<HI", res, 0)
    if version != 0x200:
        raise ParseError(f"FNT version {version:#x}", 0)
    if size > len(res):
        raise ParseError(f"dfSize {size} beyond resource {len(res)}", 2)
    ftype, points = struct.unpack_from("<HH", res, 0x42)
    if ftype & 1:
        raise ParseError("vector font", 0x42)
    ascent = struct.unpack_from("<H", res, 0x4a)[0]
    italic, underline, strike = res[0x50:0x53]
    weight, charset = struct.unpack_from("<HB", res, 0x53)
    pix_width, pix_height = struct.unpack_from("<HH", res, 0x56)
    first, last, default, brk = res[0x5f:0x63]
    face_off, bits_ptr, bits_off = struct.unpack_from("<III", res, 0x69)
    if pix_width:
        raise ParseError("fixed-pitch font", 0x56)
    count = last - first + 2
    table_end = HEADER + 4 * count
    used = bytearray(size)
    used[:table_end] = b"\1" * table_end
    widths = []
    for i in range(count):
        width, off = struct.unpack_from("<HH", res, HEADER + 4 * i)
        n = (width + 7) // 8 * pix_height
        if off < table_end or off + n > size:
            raise ParseError(f"glyph {first + i} bitmap {off:#x}+{n} outside the resource", HEADER + 4 * i)
        used[off:off + n] = b"\1" * n
        widths.append(width)
    end = res.index(b"\0", face_off)
    face = res[face_off:end].decode("latin-1")
    used[face_off:end + 1] = b"\1" * (end + 1 - face_off)
    gaps = [i for i in range(size) if not used[i] and res[i]]
    if gaps:
        raise ParseError(f"{len(gaps)} unaccounted non-zero bytes", gaps[0])
    return {"face": face, "points": points, "height": pix_height, "ascent": ascent,
            "weight": weight, "charset": charset, "italic": italic, "underline": underline,
            "strike": strike, "chars": (first, last), "default": first + default,
            "break": first + brk, "widths": widths, "padding": bytes(set(res[size:])), "bits_offset": bits_off, "bits_ptr": bits_ptr}


def parse(data: bytes) -> dict:
    if data[:2] != b"MZ":
        raise ParseError("no MZ header", 0)
    ne = struct.unpack_from("<I", data, 0x3c)[0]
    if data[ne:ne + 2] != b"NE":
        raise ParseError("not an NE executable", ne)
    rsrc = ne + struct.unpack_from("<H", data, ne + 0x24)[0]
    names = ne + struct.unpack_from("<H", data, ne + 0x26)[0]  # resident name table
    shift = struct.unpack_from("<H", data, rsrc)[0]
    pos, fonts, dirs, other = rsrc + 2, [], 0, []
    while True:
        rtype, n = struct.unpack_from("<HH", data, pos)
        pos += 8
        if rtype == 0:
            break
        for _ in range(n):
            off, length, _flags, rid = struct.unpack_from("<HHHH", data, pos)
            pos += 12
            off, length = off << shift, length << shift
            if off + length > len(data):
                raise ParseError(f"resource {rid:#x} beyond the file", pos - 12)
            if rtype == RT_FONT:
                try:
                    fonts.append(parse_fnt(data[off:off + length]))
                except ParseError as e:
                    raise ParseError(f"font {rid:#x}: {e}", off) from None
            elif rtype == RT_FONTDIR:
                dirs += 1
            else:
                other.append(rtype)
    if pos > names:
        raise ParseError("resource table runs into the name table", pos)
    if not fonts or dirs != 1:
        raise ParseError(f"{len(fonts)} fonts, {dirs} font directories", rsrc)
    return {"fonts": fonts, "other_resources": other}


def selftest() -> None:
    # One 2-character font: 'A' 3 px wide, the sentinel 0 wide, 2 rows, face "T".
    count = 3
    table = HEADER + 4 * count
    bits = table
    face = bits + 2
    res = bytearray(face + 2)
    struct.pack_into("<HI", res, 0, 0x200, len(res))
    struct.pack_into("<HH", res, 0x42, 0, 8)
    struct.pack_into("<HH", res, 0x56, 0, 2)
    res[0x5f:0x63] = bytes([65, 66, 0, 0])
    struct.pack_into("<I", res, 0x69, face)
    struct.pack_into("<HHHHHH", res, HEADER, 3, bits, 0, bits, 0, bits)
    res[bits:bits + 2] = b"\xe0\xa0"
    res[face] = ord("T")
    out = parse_fnt(bytes(res))
    assert out["face"] == "T" and out["widths"] == [3, 0, 0] and out["height"] == 2
    bad = bytearray(res)
    bad[0x40] = 1  # inside the copyright field: accounted as header, allowed
    parse_fnt(bytes(bad))
    bad = bytearray(res) + b"\0\0"
    struct.pack_into("<I", bad, 2, len(bad))
    bad[-1] = 9  # an unaccounted byte
    try:
        parse_fnt(bytes(bad))
    except ParseError:
        pass
    else:
        raise AssertionError("accepted an unaccounted byte")


if __name__ == "__main__":
    raise SystemExit(main_for(parse, "Windows raster font (.fon) validator",
                              [".fon", ".gre", ".heb", ".slo"], selftest=selftest))
