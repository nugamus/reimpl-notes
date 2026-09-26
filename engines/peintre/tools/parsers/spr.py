"""SPR sprite banks (Data/SPRITES/*.SPR).

Layout (engines/peintre/docs/formats/README.md, spr.ksy; E-0102, E-0103):

    u32 head        bit 31 = raw frames, bit 30 = band frames (only read when bit 31
                    is clear), bits 0..29 = palette_end: offset of the bank
    palette         (palette_end - 4) / 3 RGB triples, 8 bits per channel (256 or none)
    bank            from palette_end to EOF; offsets below are relative to it
        u32 offsets[n]      n = offsets[0] / 4; frame i = offsets[i] .. offsets[i+1]
                            (the last frame ends at EOF)
        frames, each { u16 a; u16 b; data; 0..3 zero bytes to a multiple of 4 }

Frame data by bank kind (Sprite_Draw 0x409d76 picks the blitter):
    rle   (bits 00): a = width, b = height; b rows of RLE over palette indices, drawn
                     centred on (x - a/2, y - b/2)
    band  (bits 01): a = first screen row, b = rows; b rows of RLE, each across the
                     full 640-pixel screen from x = 0; a frame of a = b = 0 is empty
    raw8  (bit 1, palette): a = width, b = height; a*b palette indices, top-left at (x, y)
    raw16 (bit 1, no palette): a = width, b = height; a*b RGB565 u16, top-left at (x, y)
RLE row: byte c; c == 0x80 ends the row, c < 0x80 skips c pixels (transparent),
c > 0x80 is followed by c & 0x7F palette indices.

    python engines/peintre/tools/parsers/spr.py            # validate the corpus
    python engines/peintre/tools/parsers/spr.py --selftest
    python engines/peintre/tools/parsers/spr.py --png OUTDIR FILE.SPR
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/mission-sunlight/discs/cd/Data/SPRITES"
SCREEN_W, SCREEN_H = 640, 480


class FormatError(Exception):
    pass


def rle_rows(data: bytes, pos: int, rows: int, width: int):
    """Decode `rows` RLE rows into [[index or None] * width]; returns (rows, end)."""
    out = []
    for _ in range(rows):
        row = [None] * width
        x = 0
        while True:
            if pos >= len(data):
                raise FormatError("row past the end of the frame")
            c = data[pos]
            pos += 1
            if c == 0x80:
                break
            n = c & 0x7F
            if x + n > width:
                raise FormatError(f"row runs to {x + n}, width {width}")
            if c > 0x80:
                if pos + n > len(data):
                    raise FormatError("literal run past the end of the frame")
                row[x:x + n] = data[pos:pos + n]
                pos += n
            x += n
        out.append(row)
    return out, pos


def kind_of(head: int, has_palette: bool) -> str:
    if head >> 31:
        return "raw8" if has_palette else "raw16"
    return "band" if head >> 30 & 1 else "rle"


def read(path: Path):
    """(kind, palette [(r,g,b)], frames [(a, b, pixels)]); pixels are rows of palette
    indices (None = transparent) or, for raw16, rows of RGB565 values."""
    blob = path.read_bytes()
    (head,) = struct.unpack_from("<I", blob)
    pal_end = head & 0x3FFFFFFF
    if pal_end < 4 or (pal_end - 4) % 3 or pal_end % 4:
        raise FormatError(f"palette end {pal_end}")
    pal = [tuple(blob[i:i + 3]) for i in range(4, pal_end, 3)]
    kind = kind_of(head, bool(pal))
    bank = blob[pal_end:]
    (first,) = struct.unpack_from("<I", bank)
    if first % 4 or first == 0:
        raise FormatError(f"first offset {first}")
    n = first // 4
    offs = list(struct.unpack_from(f"<{n}I", bank)) + [len(bank)]
    frames = []
    for i in range(n):
        if offs[i + 1] < offs[i] + 4 or offs[i] % 4:
            raise FormatError(f"frame {i} offsets {offs[i]}..{offs[i + 1]}")
        fr = bank[offs[i]:offs[i + 1]]
        a, b = struct.unpack_from("<HH", fr)
        if kind == "raw16":
            end = 4 + a * b * 2
            px = [list(struct.unpack_from(f"<{a}H", fr, 4 + y * a * 2)) for y in range(b)]
        elif kind == "raw8":
            end = 4 + a * b
            px = [list(fr[4 + y * a:4 + (y + 1) * a]) for y in range(b)]
        elif kind == "rle":
            px, end = rle_rows(fr, 4, b, a)
        else:
            if a + b > SCREEN_H:
                raise FormatError(f"band rows {a}+{b} below the screen")
            px, end = rle_rows(fr, 4, b, SCREEN_W)
        pad = fr[end:]
        if len(pad) > 3 or any(pad) or len(fr) % 4:
            raise FormatError(f"frame {i}: {len(pad)} bytes after the data")
        frames.append((a, b, px))
    return kind, pal, frames


def validate() -> int:
    files = sorted(CORPUS.glob("*.[Ss][Pp][Rr]"))
    ok, kinds, nframes = 0, Counter(), Counter()
    for f in files:
        try:
            kind, pal, frames = read(f)
        except FormatError as e:
            print(f"FAIL {f.name}: {e}")
            continue
        ok += 1
        kinds[kind] += 1
        nframes[kind] += len(frames)
    print(f"SPR: {ok}/{len(files)} files valid, every byte consumed; files {dict(kinds)}; "
          f"frames {dict(nframes)}")
    return 0 if ok == len(files) else 1


def to_png(path: Path, outdir: Path) -> None:
    from PIL import Image
    kind, pal, frames = read(path)
    outdir.mkdir(parents=True, exist_ok=True)
    for i, (a, b, px) in enumerate(frames):
        if not px:
            continue
        im = Image.new("RGBA", (len(px[0]), len(px)))
        for y, row in enumerate(px):
            for x, v in enumerate(row):
                if v is None:
                    continue
                if kind == "raw16":
                    rgb = ((v >> 11) * 255 // 31, (v >> 5 & 63) * 255 // 63, (v & 31) * 255 // 31)
                else:
                    rgb = pal[v]
                im.putpixel((x, y), rgb + (255,))
        im.save(outdir / f"{path.stem}_{i:03d}.png")


def selftest() -> None:
    # 3-wide row: literal [7, 8], skip 1, end; second row: skip 3, end
    rows, end = rle_rows(bytes([0x82, 7, 8, 1, 0x80, 3, 0x80]), 0, 2, 3)
    assert rows == [[7, 8, None], [None] * 3] and end == 7
    try:
        rle_rows(bytes([0x84, 1, 2, 3, 4, 0x80]), 0, 1, 3)
    except FormatError:
        pass
    else:
        raise AssertionError("overlong row accepted")
    assert kind_of(0x40000304, True) == "band" and kind_of(0x80000004, False) == "raw16"
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--png", nargs=2, metavar=("OUTDIR", "SPR"))
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.png:
        to_png(Path(a.png[1]), Path(a.png[0]))
    else:
        sys.exit(validate())
