"""SPR sprites of China (every *.SPR under CHINE/: INTERF, INVENT, PUZZLES, SPRITES).

Not Mission Sunlight's SPR bank: China's SPR is one picture in a TGA container whose
12-byte image ID holds a key colour and two more fields (E-0102):

    18-byte TGA header: id_length 12, colour map type 0, image type 2, colour map spec 0,
      x/y origin 0, u16 width, u16 height, depth 15, descriptor 0x20 (top row first)
    12-byte image ID: u32 key (a 555 colour, high half 0), s32 unk_16, s32 unk_1a
    width * height u16 pixels, X1R5G5B5 (bit 15 is 0 in every pixel); nothing after

CHINE.EXE's loader (0x41f760, used by every game source for *.spr) reads the 18-byte header,
then the three u32 of the ID (never using id_length), accepts depth 15 or 16 only, reads
width*height*2 pixel bytes and keeps key, unk_16 and unk_1a in the sprite; on a 565 screen
it converts the pixels and the key to 565.

    python engines/cryomni3d/tools/parsers/spr.py            # validate the corpus
    python engines/cryomni3d/tools/parsers/spr.py --selftest
    python engines/cryomni3d/tools/parsers/spr.py --png OUT.png FILE.SPR
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
ID = struct.Struct("<Iii")  # key, unk_16, unk_1a


class FormatError(Exception):
    pass


def read(blob: bytes) -> dict:
    if len(blob) < HEADER.size + ID.size:
        raise FormatError("shorter than the header")
    idl, cmt, typ, cms, cml, cmd, xo, yo, w, h, depth, desc = HEADER.unpack_from(blob)
    if (idl, cmt, typ, cms, cml, cmd, xo, yo, depth, desc) != (12, 0, 2, 0, 0, 0, 0, 0, 15, 0x20):
        raise FormatError(f"header {(idl, cmt, typ, cms, cml, cmd, xo, yo, depth, desc)}")
    key, unk_16, unk_1a = ID.unpack_from(blob, HEADER.size)
    if key >> 15:
        raise FormatError(f"key {key:#x}")
    start = HEADER.size + ID.size
    if len(blob) != start + w * h * 2:
        raise FormatError(f"{len(blob)} bytes, {w}x{h} needs {start + w * h * 2}")
    px = struct.unpack_from(f"<{w * h}H", blob, start)
    if any(v >> 15 for v in px):
        raise FormatError("bit 15 set")
    return dict(width=w, height=h, key=key, unk_16=unk_16, unk_1a=unk_1a,
                rows=[list(px[y * w:(y + 1) * w]) for y in range(h)])


def validate() -> int:
    files = sorted(p for p in CORPUS.rglob("*") if p.suffix.lower() == ".spr")
    ok, keyed, keys = 0, 0, Counter()
    lo, hi = [1 << 31] * 2, [-(1 << 31)] * 2
    for f in files:
        try:
            i = read(f.read_bytes())
        except FormatError as e:
            print(f"FAIL {f.relative_to(CORPUS)}: {e}")
            continue
        ok += 1
        keys[i["key"]] += 1
        keyed += any(i["key"] in r for r in i["rows"])
        for n, k in enumerate(("unk_16", "unk_1a")):
            lo[n], hi[n] = min(lo[n], i[k]), max(hi[n], i[k])
    print(f"SPR: {ok}/{len(files)} files valid, every byte consumed; {len(keys)} key colours "
          f"(most common {', '.join(f'{k:#06x} x{v}' for k, v in keys.most_common(3))}); "
          f"{keyed} files contain their key colour; unk_16 {lo[0]}..{hi[0]}, unk_1a {lo[1]}..{hi[1]}")
    return 0 if ok == len(files) else 1


def to_png(path: Path, out: str) -> None:
    from PIL import Image
    i = read(path.read_bytes())
    im = Image.new("RGBA", (i["width"], i["height"]))
    im.putdata([(0, 0, 0, 0) if v == i["key"] else
                ((v >> 10) * 255 // 31, (v >> 5 & 31) * 255 // 31, (v & 31) * 255 // 31, 255)
                for r in i["rows"] for v in r])
    im.save(out)


def build(w: int, h: int, key: int, px: list[int]) -> bytes:
    return (HEADER.pack(12, 0, 2, 0, 0, 0, 0, 0, w, h, 15, 0x20) + ID.pack(key, 196, 225)
            + struct.pack(f"<{len(px)}H", *px))


def selftest() -> None:
    blob = build(2, 1, 0x1F, [0x1F, 0x7C00])
    i = read(blob)
    assert i["rows"] == [[0x1F, 0x7C00]] and (i["unk_16"], i["unk_1a"]) == (196, 225)
    for bad in (blob[:-1], blob + b"\0\0", build(1, 1, 0, [0x8000]),
                blob[:16] + b"\x10" + blob[17:]):
        try:
            read(bad)
        except FormatError:
            continue
        raise AssertionError("bad file accepted")
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--png", nargs=2, metavar=("OUT", "SPR"))
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.png:
        to_png(Path(a.png[1]), a.png[0])
    else:
        sys.exit(validate())
