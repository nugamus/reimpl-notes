"""CVY movie masks (Data/MOVIES/*.CVY), one per HNM of the same name.

Layout (engines/peintre/docs/formats/README.md, cvy.ksy; E-0204, E-0205):

    u32 frame_count                 the HNM's frame_count (4 files differ, see README)
    u32 buffer_size                 the engine allocates this for one unpacked frame
    u32 offsets[frame_count]        from the end of this table
    frame_count HLZ streams, each padded to a multiple of 4 bytes (padding bytes
                                    hold leftover memory)

HLZ (Cryo LZ, EXE 0x430700 = ScummVM image/codecs/hlz.cpp): a u32 bit register read
MSB first; 1 = literal byte; 01 = u16 t: length (t & 7) + 2, distance (t >> 3) - 0x2000,
and t & 7 == 0 takes the length from the next byte (0 ends the stream); 00 = two bits
length + 2, byte distance - 0x100.

Unpacked frame = a run mask over the 640-pixel screen from the movie rectangle's
origin, painted by 0x46ff0d in the colour the caller passes (0x116A in 5-6-5, 0x08AA in
5-5-5), one u32 (two pixels) per unit:
    b > 0      skip b lines
    b == 0     repeat the previous mask line
    b & 0x80   a line of (b & 0x7F) runs, each one byte r: r & 0x80 = paint
               (r & 0x7F) + 1 u32, else skip r + 1 u32; a line's runs add up to 320
The engine stops when it has covered the rectangle's height; bytes after 480 lines
are zero padding it never reads.

    python engines/peintre/tools/parsers/cvy.py            # validate the corpus
    python engines/peintre/tools/parsers/cvy.py --selftest
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[4]
DATA = REPO / "games/mission-sunlight/discs/cd/Data"
CORPUS = DATA / "MOVIES"
MOVIE_TABLE = 0x4A7A08  # 68 x {char name[12]; u32 has_cvy; u32 x, y, w, h; u32 unk_20}
MOVIE_RECORD = struct.Struct("<12s5iI")
LINE_UNITS = 320  # u32 per 640-pixel line
SCREEN_LINES = 480


class FormatError(Exception):
    pass


def hlz(src: bytes, pos: int, end: int) -> tuple[bytes, int]:
    """Unpack one HLZ stream starting at pos; returns (data, position after the stream)."""
    out = bytearray()
    reg = bits = 0

    def need(n: int) -> None:
        if pos + n > end:
            raise FormatError("HLZ stream runs past its end")

    def bit() -> int:
        nonlocal reg, bits, pos
        if bits == 0:
            need(4)
            reg = struct.unpack_from("<I", src, pos)[0]
            pos += 4
            bits = 32
        bits -= 1
        return (reg >> bits) & 1

    while True:
        if bit():
            need(1)
            out.append(src[pos])
            pos += 1
            continue
        if bit():
            need(2)
            t = struct.unpack_from("<H", src, pos)[0]
            pos += 2
            count, dist = t & 7, (t >> 3) - 0x2000
            if count == 0:
                need(1)
                count = src[pos]
                pos += 1
                if count == 0:
                    return bytes(out), pos
        else:
            count = bit() << 1
            count |= bit()
            need(1)
            dist = src[pos] - 0x100
            pos += 1
        if -dist > len(out):
            raise FormatError("HLZ match before the start of the output")
        for _ in range(count + 2):
            out.append(out[dist])


def walk(mask: bytes) -> tuple[int, int, int]:
    """Walk a mask; returns (lines covered, last painted line + 1, padding bytes)."""
    p = lines = painted = 0
    prev = None
    while p < len(mask) and lines < SCREEN_LINES:
        b = mask[p]
        if 0 < b < 0x80:
            lines += b
            p += 1
            continue
        if b == 0:
            if prev is None:
                raise FormatError("line repeat before any line")
            q, p = prev, p + 1
        else:
            prev = q = p
            p += 1 + (b & 0x7F)
        n = mask[q] & 0x7F
        runs = mask[q + 1: q + 1 + n]
        if len(runs) != n:
            raise FormatError("line runs past the mask")
        if sum((r & 0x7F) + 1 for r in runs) != LINE_UNITS:
            raise FormatError(f"line {lines}: runs do not add up to {LINE_UNITS}")
        lines += 1
        painted = lines if any(r & 0x80 for r in runs) else painted
    if any(mask[p:]):
        raise FormatError(f"non-zero bytes after {lines} lines")
    return lines, painted, len(mask) - p


def read(blob: bytes):
    """(buffer_size, [unpacked masks]) of one CVY, validating every byte."""
    if len(blob) < 8:
        raise FormatError("shorter than the header")
    count, bufsize = struct.unpack_from("<II", blob)
    base = 8 + 4 * count
    if count < 1 or base > len(blob):
        raise FormatError(f"frame_count {count}")
    offs = struct.unpack_from(f"<{count}I", blob, 8)
    masks = []
    for i, off in enumerate(offs):
        end = base + offs[i + 1] if i + 1 < count else len(blob)
        if off % 4 or base + off > end:
            raise FormatError(f"frame {i}: offset {off}")
        data, pos = hlz(blob, base + off, end)
        if not 0 <= end - pos <= 3:  # alignment padding, leftover memory (unk)
            raise FormatError(f"frame {i}: {end - pos} bytes after the stream")
        if len(data) > bufsize:
            raise FormatError(f"frame {i}: unpacks to {len(data)} > buffer_size {bufsize}")
        masks.append(data)
    return bufsize, masks


def movie_table() -> dict[str, tuple]:
    """name -> (has_cvy, x, y, w, h) from the game's own table (0x4a7a08)."""
    pe = pefile.PE(str(DATA / "mission.___"), fast_load=True)
    raw = pe.get_data(MOVIE_TABLE - pe.OPTIONAL_HEADER.ImageBase, MOVIE_RECORD.size * 68)
    out = {}
    for i in range(68):
        name, *rec, _ = MOVIE_RECORD.unpack_from(raw, i * MOVIE_RECORD.size)
        out[name.split(b"\0")[0].decode().upper()] = tuple(rec)
    return out


def hnm_frames(stem: str) -> int | None:
    for p in CORPUS.iterdir():
        if p.suffix.lower() == ".hnm" and p.stem.upper() == stem:
            return struct.unpack_from("<I", p.read_bytes()[:20], 16)[0]
    return None


def validate() -> int:
    files = sorted(p for p in CORPUS.iterdir() if p.suffix.lower() == ".cvy")
    table = movie_table()
    ok = frames = 0
    notes = Counter()
    for f in files:
        stem = f.stem.upper()
        try:
            _, masks = read(f.read_bytes())
            rec = table.get(stem)
            hf = hnm_frames(stem)
            if hf != len(masks):
                # the engine reads mask n for HNM frame n (0x40c072): fewer masks would overrun
                if hf is None or (rec and rec[0] and len(masks) < hf):
                    raise FormatError(f"{len(masks)} frames, HNM has {hf}")
                notes[f"{f.name}: {len(masks)} frames, {stem}.HNM {hf}"] += 1
            for i, m in enumerate(masks):
                lines, painted, pad = walk(m)
                notes["empty frames" if not painted else "painted frames"] += 1
                if rec and lines < rec[4]:
                    raise FormatError(f"frame {i}: {lines} lines < rectangle height {rec[4]}")
                if rec and painted > rec[4]:
                    raise FormatError(f"frame {i}: paints line {painted} > height {rec[4]}")
        except FormatError as e:
            print(f"FAIL {f.name}: {e}")
            continue
        ok += 1
        frames += len(masks)
        notes["in the table, has_cvy = 1" if rec and rec[0] else
              "in the table, has_cvy = 0 (never opened)" if rec else "not in the table"] += 1
    have = {f.stem.upper() for f in files}
    unused = sorted(n for n, r in table.items() if r[0] and n not in have)
    print(f"CVY: {ok}/{len(files)} files valid, every byte consumed; {frames} frames")
    for k, v in sorted(notes.items()):
        print(f"  {v:5} {k}")
    print(f"  table entries with has_cvy = 1 and no CVY file: {unused or 'none'}")
    return 0 if ok == len(files) else 1


def selftest() -> None:
    # HLZ: 1 'a', 1 'b', 00 + 10 -> 4 bytes from distance 2, 01 + t = 0, byte 0 -> end
    bits = "1" "1" "00" "10" "01"
    reg = int(bits.ljust(32, "0"), 2)
    stream = struct.pack("<I", reg) + b"ab" + bytes([0x100 - 2]) + struct.pack("<H", 0) + b"\0"
    data, pos = hlz(stream, 0, len(stream))
    assert data == b"ababab" and pos == len(stream), (data, pos)
    line = bytes([0x82, 0x80 | 9, 0x7F, 0x7F, 0x36])
    try:
        walk(line)
    except FormatError:
        pass  # 2 runs adding up to 138, not 320
    else:
        raise AssertionError("short line accepted")
    # one line painting 10 u32, repeated once, then 478 lines skipped, 3 padding bytes
    line = bytes([0x84, 0x80 | 9, 0x7F, 0x7F, 0x35])
    assert walk(line + b"\0" + bytes([0x7F, 0x7F, 0x7F, 0x61]) + bytes(3)) == (480, 2, 3)
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    else:
        sys.exit(validate())
