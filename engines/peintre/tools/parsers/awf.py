"""AWF bitmap fonts (Data/FONTS/*.AWF).

Layout (engines/peintre/docs/formats/README.md, awf.ksy; E-0105):

    38-byte header, kept by the engine as the font record:
      u32 unk_0, u32 unk_data_ptr     0 in the files; the loader stores the data pointer
                                      at +4
      u32 glyphs_ofs, glyph_table_ofs, widths_ofs, spacing_a_ofs, spacing_b_ofs
                                      offsets into the data (made pointers on load);
                                      the last three are 0 in a fixed-width font
      u8 first_char, u8 count, u8 baseline, u8 unk_1f
      u16 flags (bit 0 = proportional), u16 fixed_width, u16 height
    data (the rest of the file):
      u32 glyph_table[count]          glyph offsets from glyphs_ofs
      glyph bitmaps                   height rows of ceil(w / 8) bytes, MSB = leftmost,
                                      1 = ink; w = widths[i] or fixed_width
      u8 widths[count], u8 spacing_a[count], s8 spacing_b[count]   (proportional only)
    advance: fixed_width, or widths[i] + spacing_a[i] + spacing_b[i]

    python engines/peintre/tools/parsers/awf.py            # validate the corpus
    python engines/peintre/tools/parsers/awf.py --selftest
    python engines/peintre/tools/parsers/awf.py --png OUT.png FILE.AWF
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/mission-sunlight/discs/cd/Data/FONTS"
HEADER = struct.Struct("<7I4B3H")


class FormatError(Exception):
    pass


def read(blob: bytes) -> dict:
    """Header fields plus glyphs [(char, width, advance, rows of bools)]."""
    if len(blob) < HEADER.size:
        raise FormatError("shorter than the header")
    (u0, uptr, g_ofs, t_ofs, w_ofs, a_ofs, b_ofs, first, count, baseline, u1f,
     flags, fixed_w, height) = HEADER.unpack_from(blob)
    data = blob[HEADER.size:]
    if (u0, uptr, t_ofs, flags & ~1) != (0, 0, 0, 0):
        raise FormatError(f"header {(u0, uptr, t_ofs, flags)}")
    prop = flags & 1
    if g_ofs != 4 * count:
        raise FormatError(f"glyphs at {g_ofs}, table of {count} entries")
    table = struct.unpack_from(f"<{count}I", data)
    if prop:
        if (w_ofs, a_ofs, b_ofs, len(data)) != tuple(w_ofs + i * count for i in range(4)):
            raise FormatError("width/spacing tables are not the last 3 * count bytes")
        widths = data[w_ofs:a_ofs]
        spa = data[a_ofs:b_ofs]
        spb = struct.unpack_from(f"<{count}b", data, b_ofs)
        end_glyphs = w_ofs
    else:
        if (w_ofs, a_ofs, b_ofs) != (0, 0, 0):
            raise FormatError("fixed-width font with width tables")
        widths, spa, spb = [fixed_w] * count, [0] * count, [0] * count
        end_glyphs = len(data)
    pos = g_ofs
    glyphs = []
    for i in range(count):
        if g_ofs + table[i] != pos:
            raise FormatError(f"glyph {i} at {table[i]}, expected {pos - g_ofs}")
        bpr = (widths[i] + 7) >> 3
        rows = []
        for _ in range(height):
            bits = int.from_bytes(data[pos:pos + bpr], "big")
            rows.append([bool(bits >> (bpr * 8 - 1 - x) & 1) for x in range(widths[i])])
            pos += bpr
        adv = widths[i] + spa[i] + spb[i] if prop else fixed_w
        glyphs.append((first + i, widths[i], adv, rows))
    if pos != end_glyphs:
        raise FormatError(f"glyphs end at {pos}, next table at {end_glyphs}")
    return dict(first=first, count=count, baseline=baseline, unk_1f=u1f,
                proportional=bool(prop), fixed_width=fixed_w, height=height, glyphs=glyphs)


def validate() -> int:
    files = sorted(CORPUS.glob("*.[Aa][Ww][Ff]"))
    ok = 0
    for f in files:
        try:
            r = read(f.read_bytes())
        except FormatError as e:
            print(f"FAIL {f.name}: {e}")
            continue
        ok += 1
        print(f"  {f.name}: chars {r['first']}..{r['first'] + r['count'] - 1}, height "
              f"{r['height']}, baseline {r['baseline']}, "
              f"{'proportional' if r['proportional'] else 'fixed ' + str(r['fixed_width'])}")
    print(f"AWF: {ok}/{len(files)} files valid, every byte consumed")
    return 0 if ok == len(files) else 1


def to_png(path: Path, out: str) -> None:
    from PIL import Image
    r = read(path.read_bytes())
    gl = r["glyphs"]
    im = Image.new("1", (sum(max(g[2], g[1]) + 1 for g in gl), r["height"]), 1)
    x0 = 0
    for _, w, adv, rows in gl:
        for y, row in enumerate(rows):
            for x, ink in enumerate(row):
                if ink:
                    im.putpixel((x0 + x, y), 0)
        x0 += max(adv, w) + 1
    im.save(out)


def selftest() -> None:
    # proportional font, 1 glyph '!' 3 px wide, 2 rows: 101, 010
    count, height = 1, 2
    data = struct.pack("<I", 0) + bytes([0b10100000, 0b01000000]) + bytes([3, 1]) + b"\xff"
    hdr = HEADER.pack(0, 0, 4, 0, 6, 7, 8, 33, count, 2, 0, 1, 0, height)
    r = read(hdr + data)
    assert r["glyphs"] == [(33, 3, 3, [[True, False, True], [False, True, False]])], r
    try:
        read(hdr + data + b"\0")
    except FormatError:
        pass
    else:
        raise AssertionError("trailing byte accepted")
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--png", nargs=2, metavar=("OUT", "AWF"))
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.png:
        to_png(Path(a.png[1]), a.png[0])
    else:
        sys.exit(validate())
