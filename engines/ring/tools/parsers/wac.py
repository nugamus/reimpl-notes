"""Packed sound: `.wac` (mono DPCM) and `.was` (stereo, packed bit stream). Spec:
engines/ring/docs/formats/wac.ksy, E-0021.

`.wac` — `aSecComSouMono` (RING_DVD.EXE vtable 0x47f0d4): DecompressHeader 0x47b250 reads
0x36 bytes, Decompress 0x47b3b0 reads each chunk (u16 size + the next size) and decodes it
with 0x47bc20 (10-bit deltas, bitstream.py `dpcm`), 256 samples (0x200 bytes) per chunk:

    u32 chunk_count
    u32 wav_size          44 + 512 * chunk_count: the unpacked WAV file's size
    u8[44] wav_header     the first 44 bytes of that WAV (RIFF, fmt: PCM mono 16-bit)
    chunk_count x { u16 size, size bytes: 3 unk bits, 256 codes, < 8 padding bits }

`.was` — `aSecComSou` (stereo; vtable 0x47f0a8): DecompressHeader 0x47aaf0 reads 0x3c
bytes, Decompress 0x47ac90 decodes each chunk with 0x430a80 (packed bit stream, 12-bit
literals shifted left by 4, 6-bit indices):

    u32 chunk_count
    u32 wav_size          44 + sum of chunk sizes
    u8[44] wav_header     (RIFF, fmt: PCM stereo 16-bit; 'fact' may follow fmt)
    chunk_count x { u32 packed_size, u32 unpacked_size, packed_size bytes }

Files damaged in the corpus (DAMAGED) are reported separately with where they break.

    python engines/ring/tools/parsers/wac.py            # corpus
    python engines/ring/tools/parsers/wac.py --selftest
"""

from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bitstream import decode, dpcm  # noqa: E402
from common import ParseError, Reader, main_for  # noqa: E402

DAMAGED_LIST = Path(__file__).with_name("wac_damaged.txt")


def wav_header(r: Reader, channels: int) -> dict:
    at = r.pos
    h = r.bytes(44)
    riff, _size, wave, fmt, fmt_len, tag, ch, rate, _bps, _align, bits = struct.unpack_from(
        "<4sI4s4sIHHIIHH", h)
    if not (riff == b"RIFF" and wave == b"WAVE" and fmt == b"fmt " and fmt_len == 16
            and tag == 1 and ch == channels and bits == 16):
        raise ParseError(f"not a PCM {channels}-channel 16-bit WAV header: {h[:36].hex()}", at)
    return {"rate": rate, "next_chunk": h[36:40]}


def parse_mono(data: bytes) -> dict:
    r = Reader(data)
    count, wav_size = r.u32(), r.u32()
    hdr = wav_header(r, 1)
    r.check(wav_size == 44 + 512 * count, f"wav_size {wav_size} != 44 + 512 * {count}", 4)
    state = [0, 0]
    unk = set()
    for i in range(count):
        size = r.u16()
        start = r.pos
        r.skip(size)
        unk.add(data[start] >> 5)
        _, end = dpcm(data, start * 8, 10, 256, state)
        if not 0 <= (start + size) * 8 - end < 8:
            raise ParseError(f"chunk {i}: 256 samples take {end - start * 8} bits of "
                             f"{size * 8}", start - 2)
    r.expect_eof()
    return {"channels": 1, "chunks": count, "unk_bits": sorted(unk), **hdr}


def parse_stereo(data: bytes) -> dict:
    r = Reader(data)
    count, wav_size = r.u32(), r.u32()
    hdr = wav_header(r, 2)
    total = 44
    for i in range(count):
        packed, unpacked = r.u32(), r.u32()
        start = r.pos
        r.skip(packed)
        codes, end = decode(data, 12, 6, start * 8, (start + packed) * 8, unpacked // 2 + 2)
        if not (unpacked % 2 == 0 and unpacked // 2 <= len(codes) <= unpacked // 2 + 1
                and end >= (start + packed) * 8):
            raise ParseError(f"chunk {i}: {len(codes)} codes for {unpacked} bytes", start)
        total += unpacked
    r.expect_eof()
    r.check(wav_size == total, f"wav_size {wav_size} != {total}", 4)
    return {"channels": 2, "chunks": count, **hdr}


def parse(data: bytes) -> dict:
    ch = struct.unpack_from("<H", data, 8 + 22)[0] if len(data) >= 52 else 0
    return parse_stereo(data) if ch == 2 else parse_mono(data)


def damaged() -> dict[str, str]:
    out = {}
    for line in DAMAGED_LIST.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            h, why = line.split(" ", 1)
            out[h] = "damaged in the corpus: " + why
    return out


def selftest() -> None:
    hdr = struct.pack("<4sI4s4sIHHIIHH4sI", b"RIFF", 36 + 512, b"WAVE", b"fmt ", 16, 1, 1,
                      22050, 44100, 2, 16, b"data", 512)
    chunk = bytes([0x1F]) + b"\xff" * 31 + b"\xf0"   # 3 bits, then 256 one-bit repeats
    mono = struct.pack("<II", 1, 44 + 512) + hdr + struct.pack("<H", len(chunk)) + chunk
    assert parse(mono)["chunks"] == 1
    try:
        parse(mono + b"\0")
    except ParseError:
        pass
    else:
        raise AssertionError("trailing byte accepted")


if __name__ == "__main__":
    raise SystemExit(main_for(parse, "WAC/WAS sound validator", [".wac", ".was"],
                              selftest=selftest, not_this_type=damaged()))
