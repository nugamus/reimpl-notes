"""CRF fonts of China (DATA/FONTES/FONT01..11.CRF).

Layout (E-0105), the one upstream ScummVM engines/cryomni3d/fonts/cryofont.cpp reads for
Versailles; every value big-endian:

    char magic[8] "CRYOFONT"; u16 unk_08; u16 unk_0a; u16 unk_0c; s16 height;
    char comment[32]                          (48 bytes so far)
    glyphs for characters 0x20..0xFF, back to back, up to EOF:
      u16 h; u16 w; s16 off_x; s16 off_y; u16 advance; w*h bytes (0 or 255)

CHINE.EXE's loader (0x413420, MyFont.cpp) loads the whole file, starts the glyphs at 48 and
indexes them for characters 0x20.. while they lie inside the file. ScummVM reads 223
glyphs (0x20..0xFE) and leaves the last one (0xFF) unread.

    python engines/cryomni3d/tools/parsers/crf.py            # validate the corpus
    python engines/cryomni3d/tools/parsers/crf.py --selftest
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/china/discs/en-iso/cd1/CHINE"
HEADER = struct.Struct(">8sHHHh32s")
GLYPH = struct.Struct(">HHhhH")


class FormatError(Exception):
    pass


def read(blob: bytes) -> dict:
    if len(blob) < HEADER.size:
        raise FormatError("shorter than the header")
    magic, u08, u0a, u0c, height, comment = HEADER.unpack_from(blob)
    if magic != b"CRYOFONT":
        raise FormatError(f"magic {magic!r}")
    pos, glyphs, values = HEADER.size, [], Counter()
    while pos < len(blob):
        if pos + GLYPH.size > len(blob):
            raise FormatError(f"glyph {len(glyphs)} header past EOF")
        h, w, ox, oy, adv = GLYPH.unpack_from(blob, pos)
        bm = blob[pos + GLYPH.size: pos + GLYPH.size + w * h]
        if len(bm) != w * h:
            raise FormatError(f"glyph {len(glyphs)} bitmap past EOF")
        values.update(bm)
        glyphs.append((h, w, ox, oy, adv))
        pos += GLYPH.size + w * h
    if len(glyphs) != 0x100 - 0x20:
        raise FormatError(f"{len(glyphs)} glyphs, not 224")
    if set(values) - {0, 255}:
        raise FormatError(f"bitmap values {sorted(values)}")
    return dict(unk=(u08, u0a, u0c), height=height, comment=comment, glyphs=glyphs)


def validate() -> int:
    files = sorted(p for p in CORPUS.rglob("*") if p.suffix.lower() == ".crf")
    ok, unk, comments = 0, Counter(), Counter()
    for f in files:
        try:
            i = read(f.read_bytes())
        except FormatError as e:
            print(f"FAIL {f.relative_to(CORPUS)}: {e}")
            continue
        ok += 1
        unk[i["unk"][:2]] += 1
        comments[i["comment"]] += 1
        print(f"  {f.name}: unk_0c {i['unk'][2]}, height {i['height']}, "
              f"max advance {max(g[4] for g in i['glyphs'])}")
    print(f"CRF: {ok}/{len(files)} files valid, every byte consumed; 224 glyphs each; "
          f"unk_08/unk_0a {dict(unk)}; comments {dict(comments)}")
    return 0 if ok == len(files) else 1


def selftest() -> None:
    glyphs = b"".join(GLYPH.pack(1, 1, 0, 0, 1) + b"\xff" for _ in range(224))
    blob = HEADER.pack(b"CRYOFONT", 1, 1, 9, 12, b"?" * 32) + glyphs
    assert read(blob)["height"] == 12
    for bad in (blob[:-1], blob + b"\0", b"CRYOFONX" + blob[8:]):
        try:
            read(bad)
        except FormatError:
            continue
        raise AssertionError("bad file accepted")
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    sys.exit(selftest() if a.selftest else validate())
