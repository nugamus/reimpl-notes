"""TGA pictures of China (every *.TGA under CHINE/: INTERF, INVENT, PUZZLES, SPRITES).

Plain Truevision TGA, two variants (E-0103):

    18-byte header: id_length 0, colour map type 0, image type 2 (true colour),
    colour map spec 0, x/y origin 0, u16 width, u16 height, depth 16 or 24,
    descriptor 0 or 1 (attribute bits; origin bit 5 never set: bottom row first)
    width * height pixels: depth 16 = u16 X1R5G5B5 (bit 15 is 0 in every pixel),
    depth 24 = B, G, R bytes
    optional 26-byte TGA 2.0 footer: u32 0 (extension), u32 0 (developer),
    "TRUEVISION-XFILE.\\0"

CHINE.EXE's loader (0x416510, MyTga.cpp) reads the 18-byte header, skips id_length
bytes, reads width*height*2 bytes for depth 16 or width*height*3 for depth 24 (converted
to the screen's 15/16-bit format), any other depth is "TGA load Failure."; it flips the
rows when descriptor bit 5 is clear and never reads the footer. Same layout as Mission
Sunlight's TGA (engines/peintre/docs/formats/tga.ksy), which had no 24-bit file.

    python engines/cryomni3d/tools/parsers/tga.py            # validate the corpus
    python engines/cryomni3d/tools/parsers/tga.py --selftest
    python engines/cryomni3d/tools/parsers/tga.py --png OUT.png FILE.TGA
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/china/discs/en-iso/cd1/CHINE"
HEADER = struct.Struct("<BBBHHBHHHHBB")
FOOTER = struct.pack("<II", 0, 0) + b"TRUEVISION-XFILE.\0"


class FormatError(Exception):
    pass


def read(blob: bytes):
    """(width, height, depth, rows top first as lists of RGB triples, has_footer)."""
    if len(blob) < HEADER.size:
        raise FormatError("shorter than the header")
    idl, cmt, typ, cms, cml, cmd, xo, yo, w, h, depth, desc = HEADER.unpack_from(blob)
    if (idl, cmt, typ, cms, cml, cmd, xo, yo) != (0, 0, 2, 0, 0, 0, 0, 0) or depth not in (16, 24):
        raise FormatError(f"header {(idl, cmt, typ, cms, cml, cmd, xo, yo, depth)}")
    if desc not in (0, 1):
        raise FormatError(f"descriptor {desc:#x}")
    bpp = depth // 8
    end = HEADER.size + w * h * bpp
    if end > len(blob):
        raise FormatError("pixels past EOF")
    tail = blob[end:]
    if tail not in (b"", FOOTER):
        raise FormatError(f"{len(tail)} bytes after the pixels are not the TGA footer")
    if depth == 16:
        px = struct.unpack_from(f"<{w * h}H", blob, HEADER.size)
        if any(v >> 15 for v in px):
            raise FormatError("bit 15 set")
        rgb = [((v >> 10) * 255 // 31, (v >> 5 & 31) * 255 // 31, (v & 31) * 255 // 31) for v in px]
    else:
        p = blob[HEADER.size:end]
        rgb = [(p[i + 2], p[i + 1], p[i]) for i in range(0, len(p), 3)]
    rows = [rgb[y * w:(y + 1) * w] for y in reversed(range(h))]
    return w, h, depth, rows, bool(tail)


def validate() -> int:
    files = sorted(p for p in CORPUS.rglob("*") if p.suffix.lower() == ".tga")
    ok, kinds = 0, Counter()
    for f in files:
        try:
            w, h, depth, rows, ft = read(f.read_bytes())
        except FormatError as e:
            print(f"FAIL {f.relative_to(CORPUS)}: {e}")
            continue
        ok += 1
        kinds[(depth, "footer" if ft else "no footer")] += 1
    print(f"TGA: {ok}/{len(files)} files valid, every byte consumed; "
          + ", ".join(f"{v} x {d}-bit {ft}" for (d, ft), v in sorted(kinds.items())))
    return 0 if ok == len(files) else 1


def to_png(path: Path, out: str) -> None:
    from PIL import Image
    w, h, _, rows, _ = read(path.read_bytes())
    im = Image.new("RGB", (w, h))
    im.putdata([v for r in rows for v in r])
    im.save(out)


def selftest() -> None:
    hdr = HEADER.pack(0, 0, 2, 0, 0, 0, 0, 0, 2, 2, 16, 1)
    blob = hdr + struct.pack("<4H", 0x7C00, 0x03E0, 0x001F, 0)
    rows = read(blob)[3]
    assert rows == [[(0, 0, 255), (0, 0, 0)], [(255, 0, 0), (0, 255, 0)]]  # bottom row first
    assert read(blob + FOOTER)[4]
    b24 = HEADER.pack(0, 0, 2, 0, 0, 0, 0, 0, 1, 1, 24, 0) + bytes([1, 2, 3])
    assert read(b24)[3] == [[(3, 2, 1)]]
    for bad in (blob + b"\0", hdr[:2] + b"\x0a" + hdr[3:] + blob[18:], b24[:-1]):
        try:
            read(bad)
        except FormatError:
            continue
        raise AssertionError("bad file accepted")
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--png", nargs=2, metavar=("OUT", "TGA"))
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.png:
        to_png(Path(a.png[1]), a.png[0])
    else:
        sys.exit(validate())
