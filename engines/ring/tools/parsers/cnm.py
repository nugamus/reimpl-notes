"""`.cnm` / `.ci2` video containers (and the `CNM UNR` images inside Prophet's `.at3`).
Spec: engines/ring/docs/formats/cnm.ksy, E-0024. HBR frames are decoded in full
(decode_hbr, E-0028), UNR frames too (decode_unr, E-0350..).

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
    0x15 u32 height, 0x19 u8 (32), 0x1a u8 interlaced, 0x1b u8 tracks (0..3),
    0x1c u32 table_count, 0x20 u32 frame_count again, 0x24 u32 unk_table_size, 0x28 u32 unk_flag, zeros to 0xc0
    tracks x 16 bytes (u8 channels, u8 bits, u32 rate, 10 zero bytes)
    table_count x { u32 video_offset, u32 audio_offset }   (all zero when unk_flag = 1)
    chunks: 'A' 'B' 'Z': u32 size + bytes; 'S' 'U': 0x2f-byte header (u32 size, ...) +
            size bytes; 'T': 8-byte header (u32 size, u16, u16) + size bytes

The image chunks ('S' + 'U') number frame_count. Exceptions (TRAILING, DAMAGED) are
listed with their reasons. UNR has two codecs, chosen by the program, not the file: v1 in
the Ring ISO EXE, v2 in Prophet's; in the corpus unk_timing (+0x0c) tells them apart (1250 in
every Ring ISO file, 1500 or 2500 in every Prophet file).

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


def decode_hbr(data: bytes, starts: list[int], frames: int, width: int, height: int) -> dict:
    """Decode every 'T' and 'S' chunk of an HBR file (0x42ccf0 / 0x42cbf0 / 0x42ce30):
    'T' = u32 size, u32 runs_size, u16 ntiles, u16 tile_words (4), u8 n, then n+1 u16
    back-buffer segment lengths (in tiles), then size bytes: tiles, code stream, run list
    (the last runs_size bytes); its stream decodes into the back buffer. 'S' = u32 size,
    u32 runs_size, u16 ntiles, u16 tile_words, u32 width, u32 height, then size bytes laid
    out the same; its stream decodes into the frame. A stream may emit one tile more than
    it covers (its last nibble); a short frame leaves the rest of the picture as it was."""
    import ctypes

    from bitstream import hbr

    from collections import Counter

    sizes = Counter()
    ring = (ctypes.c_uint32 * 128)()
    back, segs, images = None, [], 0
    for at in starts:
        t = chr(data[at])
        if t not in "TS" or images == frames:
            continue
        if t == "T":
            size, runs, ntiles, words, n = struct.unpack_from("<IIHHB", data, at + 1)
            segs = list(struct.unpack_from(f"<{n + 1}H", data, at + 14))
            body = data[at + 16 + 2 * n:at + 16 + 2 * n + size]
            want = sum(segs) * 4
        else:
            size, runs, ntiles, words, w, h = struct.unpack_from("<IIHHII", data, at + 1)
            if (w, h) != (width, height) or back is None:
                raise ParseError(f"frame {w}x{h} or no tile chunk before it", at)
            body = data[at + 21:at + 21 + size]
            want = w * h
        if words != 4:
            raise ParseError(f"tile of {words} words", at)
        tiles = struct.unpack_from(f"<{ntiles * 4}H", body, 0)
        try:
            out, got = hbr(body, ntiles * 8, size - runs, body[size - runs:], tiles, ntiles,
                           ring, back if t == "S" else None, segs if t == "S" else [],
                           (0x8d000 if t == "S" else 1200000) // 2)
        except ValueError as exc:
            raise ParseError(f"{t} chunk: {exc}", at) from None
        # The engine's only size check: SControl > 0x8cfff bytes, TControl > 1,200,000.
        if got * 2 > (0x8cfff if t == "S" else 1200000):
            raise ParseError(f"{t} chunk decodes to {got} pixels", at)
        sizes[(t, "short" if got < want else "exact" if got == want else "over")] += 1
        if t == "T":
            back = out
        else:
            images += 1
    return {"decoded_frames": images, "decoded_sizes": dict(sizes)}


def decode_unr(data: bytes, starts: list[int], frames: int, width: int, height: int,
               version: int, interlaced: bool) -> dict:
    """Decode every UNR 'T', 'S' and 'U' chunk (README "UNR video codec"; RING_ISO.EXE
    0x42c680 v1, LEGEND.EXE 0x423630 v2). 'S'/'U' payload = index stream (first `offset`
    bytes), then, if offset < size, a tile table; 'T' payload = a tile table. Each stream
    must end in the last byte of its part (byte padding only)."""
    from bitstream import Unr

    u = Unr(version, width, height, interlaced)
    images, stale, have_tiles = 0, 0, False
    for at in starts:
        t = chr(data[at])
        if t not in "TSU" or images == frames:
            continue
        try:
            if t == "T":
                size, ntiles, tsize = struct.unpack_from("<IHH", data, at + 1)
                parts = [(data[at + 9:at + 9 + size], "tiles")]
            else:
                size, off, ntiles, tsize, w, h = struct.unpack_from("<IIHHII", data, at + 1)
                if (w, h) != (width, height):
                    raise ParseError(f"frame {w}x{h}", at)
                body = data[at + 0x30:at + 0x30 + size]
                parts = ([(body[off:], "tiles")] if off < size else []) + [(body[:off], "map")]
            if tsize != 4:
                raise ParseError(f"tiles of {tsize} pixels", at)
            for part, kind in parts:
                if kind == "tiles":
                    used = u.load_tiles(part, ntiles)
                    have_tiles = True
                else:
                    if not have_tiles:
                        raise ParseError("picture before any tile table", at)
                    used, n = u.frame(part, ntiles)
                    stale += n
                if not len(part) * 8 - 8 < used <= len(part) * 8:
                    raise ParseError(f"{t} {kind} stream ends at bit {used} of {len(part) * 8}", at)
        except ValueError as exc:
            raise ParseError(f"{t} chunk: {exc}", at) from None
        images += t in "SU"
    if stale:
        raise ParseError(f"{stale} neighbour choices past the list", 0)
    return {"decoded_frames": images}


def parse(data: bytes) -> dict:
    r = Reader(data)
    magic = r.bytes(8)
    trailing = hashlib.md5(data).hexdigest() in TRAILING
    if magic == HBR:
        ch, bits, rate, frames, timing = r.u8(), r.u8(), r.u32(), r.u32(), r.u32()
        unk16, width, height, unk1f = r.u8(), r.u32(), r.u32(), r.u16()
        r.check(r.bytes(0x40 - r.pos) == bytes(0x40 - 0x21), "header tail not zero")
        body = chunks(r, {"A": 4, "B": 4, "Z": 4, "S": 20, "T": 13}, frames, "S", trailing)
        body.update(decode_hbr(data, body["starts"], frames, width, height))
        return {"variant": "HBR", "frames": frames, "width": width, "height": height,
                "audio": (ch, bits, rate), "unk_timing": timing, "unk": (unk16, unk1f), **body}
    r.check(magic == UNR, f"bad magic {magic!r}", 0)
    frames, timing, b10, width, height = r.u32(), r.u32(), r.u8(), r.u32(), r.u32()
    b19, interlaced, tracks = r.u8(), r.u8(), r.u8()
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
    body.update(decode_unr(data, body["starts"], frames, width, height,
                           1 if timing == 1250 else 2, bool(interlaced)))
    return {"variant": "UNR", "frames": frames, "width": width, "height": height,
            "audio": audio, "unk_timing": timing, "interlaced": interlaced,
            "unk": (b10, b19, table_size, flag),
            **body}


def selftest() -> None:
    # 4x1 picture: a tile chunk (1 tile, 1 segment), then a frame that emits tile code 0.
    hdr = HBR + struct.pack("<BBIIIBIIH", 1, 16, 22050, 1, 1250, 0, 4, 1, 16) + bytes(0x1f)
    tile = struct.pack("<4H", 1, 2, 3, 4)
    tbody = tile + b"\0\0"                        # code 0 (12 bits) + pad nibble
    body = b"T" + struct.pack("<IIHHB", len(tbody), 0, 1, 4, 0) + struct.pack("<H", 1) + tbody
    body += b"Z" + struct.pack("<I", 2) + b"ab"
    body += b"S" + struct.pack("<IIHHII", len(tbody), 0, 1, 4, 4, 1) + tbody
    out = parse(hdr + body)
    assert out["frames"] == 1 and out["counts"] == {"T": 1, "Z": 1, "S": 1}, out
    try:
        parse(hdr + body + b"S")
    except ParseError:
        pass
    else:
        raise AssertionError("stray byte accepted")
    _selftest_unr()


def _bits(fields: list[tuple[int, int]], lsb_first: bool) -> bytes:
    """Pack (value, width) fields: v1 MSB first, v2 LSB first (value bits low to high)."""
    bits = []
    for v, n in fields:
        bits += [(v >> i) & 1 for i in (range(n) if lsb_first else reversed(range(n)))]
    bits += [0] * (-len(bits) % 8)
    if lsb_first:
        return bytes(sum(b << i for i, b in enumerate(bits[k:k + 8])) for k in range(0, len(bits), 8))
    return bytes(int("".join(map(str, bits[k:k + 8])), 2) for k in range(0, len(bits), 8))


def _unr_file(timing: int, interlaced: int, w: int, h: int, chunks: list[bytes]) -> bytes:
    head = UNR + struct.pack("<IIBIIBBBIIII", 1, timing, 0, w, h, 32, interlaced, 0, 1, 1, 0,
                             timing != 1250)
    head += bytes(0xc0 - len(head))
    table = struct.pack("<II", 0xc0 + 8 if timing == 1250 else 0, 0)
    return head + table + b"".join(chunks)


def _selftest_unr() -> None:
    from bitstream import Unr

    tile0 = bytes(range(1, 17))
    # v2, 32x2, plain: 'T' with 2 tiles (tile 1 = tile 0 with lane 0 raw 10, 20, 30, 40),
    # then 'S' without tiles: a group of 8 new indices 1 (000 + 2 bits), a group copied up.
    tiles = tile0 + _bits([(7, 3), (10, 8), (20, 8), (30, 8), (40, 8)] + [(0, 3)] * 3, True)
    stream = _bits([(0, 1)] + [(0, 3), (1, 2)] * 8 + [(1, 1)], True)
    t = b"T" + struct.pack("<IHH", len(tiles), 2, 4) + tiles
    sc = b"S" + struct.pack("<IIHHIIII", len(stream), len(stream), 2, 4, 32, 2, 0, 0) + bytes(19)
    assert parse(_unr_file(1500, 0, 32, 2, [t, sc + stream]))["decoded_frames"] == 1
    u = Unr(2, 32, 2, False)
    u.load_tiles(tiles, 2)
    u.frame(stream, 2)
    want = bytes([10, 2, 3, 4, 20, 6, 7, 8, 30, 10, 11, 12, 40, 14, 15, 16])
    assert bytes(u.out)[:16] == want and bytes(u.out)[-16:] == want, bytes(u.out)[:16]
    # v1, 4x3, interlaced: tile 1 = tile 0 + 1 in byte 0 (n = 0: 1-bit deltas, sign 0);
    # rows 0 and 2 get tiles 1 and 0 (0 + 10-bit index), row 1 their average.
    tiles = tile0 + _bits([(0, 3), (1, 1), (0, 1)] + [(0, 1)] * 15, False)
    stream = _bits([(0, 1), (1, 10), (0, 1), (0, 10)], False)
    body = stream + tiles
    sc = b"S" + struct.pack("<IIHHIIII", len(body), len(stream), 2, 4, 4, 3, 0, 0) + bytes(19)
    assert parse(_unr_file(1250, 1, 4, 3, [sc + body]))["decoded_frames"] == 1
    u = Unr(1, 4, 3, True)
    u.load_tiles(tiles, 2)
    u.frame(stream, 2)
    t0 = [v << 1 & 0xFFFFFFFF for v in struct.unpack("<4I", tile0)]  # interlaced: doubled
    t1 = [v << 1 & 0xFFFFFFFF for v in struct.unpack("<4I", bytes([2]) + tile0[1:])]
    got = struct.unpack("<12I", bytes(u.out))
    assert got == tuple(t1 + [(a >> 1) + (b >> 1) for a, b in zip(t0, t1)] + t0), got


if __name__ == "__main__":
    raise SystemExit(main_for(parse, "CNM/CI2 container validator", [".cnm", ".ci2"],
                              [".bmp", ".tga"], archives=(".at3",), selftest=selftest,
                              not_this_type=DAMAGED))
