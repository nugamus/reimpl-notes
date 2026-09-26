"""`.cnm` / `.ci2` video containers (and the `CNM UNR` images inside Prophet's `.at3`).
Spec: engines/ring/docs/formats/cnm.ksy, E-0024. Container level only: frame payloads are
walked by their size fields; the video codec is not decoded yet (README status).

Two variants, told apart by the magic:

"CNM HBR\\0" — Ring DVD and CD version, read by `aImageFileCin` / `aCin` / `aCinMov::Play`
(RING_DVD.EXE 0x42a6b0 header, 0x415990 Play, 0x42ccf0 SControl, 0x42cbf0 TControl,
0x4158c0 SkipSound):
    0x00 magic, 0x08 u8 channels, 0x09 u8 bits, 0x0a u32 rate, 0x0e u32 frame_count,
    0x12 u32 unk_timing, 0x16 u8 unk, 0x17 u32 width, 0x1b u32 height, 0x1f u16 unk,
    zeros to 0x40
    chunks: u8 type;  'A' 'B' 'Z' sound: u32 size + size bytes
                      'S' image: 20-byte header (u32 size, ...) + size bytes
                      'T' tiles: 13-byte header (u32 size, u32, u16, u16, u8 n) + size + 2n+2

"CNM UNR\\0" — Ring ISO version, Prophet `.ci2` and `.at3` images, read by
`aImageFileCinema::ReadHeader` (LEGEND.EXE 0x421c30), SControl 0x422fc0, TControl
0x423170, SkipFrame 0x422f20, `aCinMov::Play` 0x4a51c0:
    0x00 magic, 0x08 u32 frame_count, 0x0c u32 unk_timing, 0x10 u8, 0x11 u32 width,
    0x15 u32 height, 0x19 u8 (32), 0x1a u8, 0x1b u8 tracks (0..3), 0x1c u32 table_count,
    0x20 u32 frame_count again, 0x24 u32 unk_table_size, 0x28 u32 unk_flag, zeros to 0xc0
    tracks x 16 bytes (u8 channels, u8 bits, u32 rate, 10 zero bytes)
    table_count x { u32 video_offset, u32 audio_offset }   (all zero when unk_flag = 1)
    chunks: 'A' 'B' 'Z': u32 size + bytes; 'S' 'U': 0x2f-byte header (u32 size, ...) +
            size bytes; 'T': 8-byte header (u32 size, u16, u16) + size bytes

The image chunks ('S' + 'U') number frame_count. Exceptions (TRAILING, DAMAGED) are
listed with their reasons.

    python engines/ring/tools/parsers/cnm.py            # corpus
    python engines/ring/tools/parsers/cnm.py --selftest
"""

from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ParseError, Reader, main_for  # noqa: E402

HBR, UNR = b"CNM HBR\0", b"CNM UNR\0"

# Bytes after the last image the engine plays (frame_count reached), E-0024.
TRAILING = {"809d0ba3e79231fc6ea0294e4bf1a4ba": "1672.CNM / RHS05N01_S05N02.cnm: a 300th "
            "image chunk, cut short by the end of the file, after the 299 of frame_count"}
# Unreadable in the corpus, E-0024, Q-0005.
DAMAGED = {"c1827c4f23651692a8b5cf21f999afe7": "damaged in the corpus: ISO disc 4 fo/Pla/fos03n02_s05n01.cnm, frame 132 video chunk at 0x6d4d29 is not a chunk "
           "(the table's other 212 frames are)"}


def chunks(r: Reader, header_sizes: dict[str, int], frames: int, image_types: str,
           allow_trailing: bool) -> dict:
    counts: dict[str, int] = {}
    starts = []
    images = 0
    while not r.eof():
        if images == frames and allow_trailing:
            return {"counts": counts, "starts": starts, "unk_trailing": r.remaining}
        at = r.pos
        t = chr(r.u8())
        if t not in header_sizes:
            raise ParseError(f"unknown chunk type {t!r}", at)
        hs = header_sizes[t]
        size = struct.unpack_from("<I", r.data, r.pos)[0] if r.remaining >= 4 else -1
        r.skip(hs)
        extra = 0
        if t == "T" and hs == 13:  # HBR: 2n + 2 more bytes, n = last header byte
            extra = 2 * r.data[r.pos - 1] + 2
        r.skip(size + extra)
        counts[t] = counts.get(t, 0) + 1
        starts.append(at)
        images += t in image_types
    r.check(images == frames, f"{images} image chunks for frame_count {frames}")
    return {"counts": counts, "starts": starts}


def parse(data: bytes) -> dict:
    r = Reader(data)
    magic = r.bytes(8)
    trailing = hashlib.md5(data).hexdigest() in TRAILING
    if magic == HBR:
        ch, bits, rate, frames, timing = r.u8(), r.u8(), r.u32(), r.u32(), r.u32()
        unk16, width, height, unk1f = r.u8(), r.u32(), r.u32(), r.u16()
        r.check(r.bytes(0x40 - r.pos) == bytes(0x40 - 0x21), "header tail not zero")
        body = chunks(r, {"A": 4, "B": 4, "Z": 4, "S": 20, "T": 13}, frames, "S", trailing)
        return {"variant": "HBR", "frames": frames, "width": width, "height": height,
                "audio": (ch, bits, rate), "unk_timing": timing, "unk": (unk16, unk1f), **body}
    r.check(magic == UNR, f"bad magic {magic!r}", 0)
    frames, timing, b10, width, height = r.u32(), r.u32(), r.u8(), r.u32(), r.u32()
    b19, b1a, tracks = r.u8(), r.u8(), r.u8()
    count, frames2, table_size, flag = r.u32(), r.u32(), r.u32(), r.u32()
    r.check(tracks <= 3 and frames2 == frames and count == frames, "header counts", 0x1b)
    r.check(r.bytes(0xc0 - r.pos) == bytes(0xc0 - 0x2c), "header tail not zero")
    audio = []
    for _ in range(tracks):
        c, b, rt = r.u8(), r.u8(), r.u32()
        r.check(r.bytes(10) == bytes(10), "track tail not zero")
        audio.append((c, b, rt))
    table = [(r.u32(), r.u32()) for _ in range(count)]
    body = chunks(r, {"A": 4, "B": 4, "Z": 4, "S": 0x2f, "U": 0x2f, "T": 8}, frames, "SU",
                  trailing)
    starts = set(body["starts"])
    if flag:
        r.check(all(v == a == 0 for v, a in table), "table not zero with unk_flag set")
    else:
        bad = [(v, a) for v, a in table if v not in starts or (a and a not in starts)]
        r.check(not bad, f"table entries off the chunk chain: {bad[:3]}")
    return {"variant": "UNR", "frames": frames, "width": width, "height": height,
            "audio": audio, "unk_timing": timing, "unk": (b10, b19, b1a, table_size, flag),
            **body}


def selftest() -> None:
    hdr = HBR + struct.pack("<BBIIIBIIH", 1, 16, 22050, 1, 1250, 0, 2, 2, 16) + bytes(0x1f)
    body = b"Z" + struct.pack("<I", 2) + b"ab" + b"S" + struct.pack("<I", 3) + bytes(16) + b"xyz"
    out = parse(hdr + body)
    assert out["frames"] == 1 and out["counts"] == {"Z": 1, "S": 1}
    try:
        parse(hdr + body + b"S")
    except ParseError:
        pass
    else:
        raise AssertionError("stray byte accepted")


if __name__ == "__main__":
    raise SystemExit(main_for(parse, "CNM/CI2 container validator", [".cnm", ".ci2"],
                              [".bmp", ".tga"], archives=(".at3",), selftest=selftest,
                              not_this_type=DAMAGED))
