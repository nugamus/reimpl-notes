"""TGA 2D overlays of the 3D scenes (Data/Graphs_2D/*.TGA).

Plain Truevision TGA, one variant only (E-0104):

    18-byte header: id_length 0, colour map type 0, image type 2 (true colour),
    colour map spec 0, x/y origin 0, u16 width, u16 height, depth 16,
    descriptor 0 or 1 (attribute bits; origin bit 5 never set: bottom row first)
    width * height u16 pixels, X1R5G5B5 (bit 15 is 0 in every pixel)
    optional 26-byte TGA 2.0 footer: u32 0 (extension), u32 0 (developer),
    "TRUEVISION-XFILE.\\0"

LoadTga (0x41ad98) reads width/height at 12 and width*height*2 bytes from 18,
ignoring every other field and the footer, flips the rows (0x41acfa) and turns
555 into 565 on 565 screens (0x41aae0). The keyed blitter 0x41b1d5 skips pixels
equal to pure green (0x03E0 in 555, 0x07C0 in 565).

    python engines/peintre/tools/parsers/tga.py            # validate the corpus
    python engines/peintre/tools/parsers/tga.py --selftest
    python engines/peintre/tools/parsers/tga.py --png OUT.png FILE.TGA
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/mission-sunlight/discs/cd/Data/Graphs_2D"
HEADER = struct.Struct("<BBBHHBHHHHBB")
FOOTER = struct.pack("<II", 0, 0) + b"TRUEVISION-XFILE.\0"
KEY_555 = 0x03E0


class FormatError(Exception):
    pass


def read(blob: bytes):
    """(width, height, rows top first as lists of 555 values, has_footer)."""
    if len(blob) < HEADER.size:
        raise FormatError("shorter than the header")
    idl, cmt, typ, cms, cml, cmd, xo, yo, w, h, depth, desc = HEADER.unpack_from(blob)
    if (idl, cmt, typ, cms, cml, cmd, xo, yo, depth) != (0, 0, 2, 0, 0, 0, 0, 0, 16):
        raise FormatError(f"header {(idl, cmt, typ, cms, cml, cmd, xo, yo, depth)}")
    if desc not in (0, 1):
        raise FormatError(f"descriptor {desc:#x}")
    end = HEADER.size + w * h * 2
    tail = blob[end:]
    if tail not in (b"", FOOTER):
        raise FormatError(f"{len(tail)} bytes after the pixels are not the TGA footer")
    px = struct.unpack_from(f"<{w * h}H", blob, HEADER.size)
    if any(v >> 15 for v in px):
        raise FormatError("bit 15 set")
    rows = [list(px[y * w:(y + 1) * w]) for y in reversed(range(h))]
    return w, h, rows, bool(tail)


def validate() -> int:
    files = sorted(p for p in CORPUS.iterdir() if p.suffix.lower() == ".tga")
    ok, footer, keyed = 0, 0, 0
    for f in files:
        try:
            w, h, rows, ft = read(f.read_bytes())
        except FormatError as e:
            print(f"FAIL {f.name}: {e}")
            continue
        ok += 1
        footer += ft
        keyed += any(KEY_555 in r for r in rows)
    print(f"TGA: {ok}/{len(files)} files valid, every byte consumed; {footer} with the "
          f"TGA 2.0 footer; {keyed} use the key colour 0x03E0")
    return 0 if ok == len(files) else 1


def to_png(path: Path, out: str) -> None:
    from PIL import Image
    w, h, rows, _ = read(path.read_bytes())
    im = Image.new("RGBA", (w, h))
    im.putdata([(0, 0, 0, 0) if v == KEY_555 else
                ((v >> 10) * 255 // 31, (v >> 5 & 31) * 255 // 31, (v & 31) * 255 // 31, 255)
                for r in rows for v in r])
    im.save(out)


def selftest() -> None:
    hdr = HEADER.pack(0, 0, 2, 0, 0, 0, 0, 0, 2, 2, 16, 1)
    blob = hdr + struct.pack("<4H", 1, 2, 3, 4)
    assert read(blob)[2] == [[3, 4], [1, 2]]  # bottom row first in the file
    assert read(blob + FOOTER)[3]
    for bad in (blob + b"\0", hdr[:2] + b"\x0a" + hdr[3:] + blob[18:]):
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
