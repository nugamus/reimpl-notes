"""TGP full-screen and panorama images (Data/GFX/*.TGP).

Layout (engines/peintre/docs/formats/README.md, tgp.ksy; E-0100, E-0101):

    u32 width, u32 height           pixels
    then one of two bodies, picked by the caller (not by the file):

    chunked (Tgp_Load 0x40d9c0, 24 files, panoramas up to 1500 px):
        u32 count
        count x { u32 packed_size; u32 unpacked_size; packed_size bytes HLZ }
        chunks unpack back to back into width * height * 2 bytes

    single (Tgp_Load2 0x414779, 110 files, 640x480 only):
        u32 unk_hdr_size (0x24)  char magic[8] "LZWCRYO\\0"  u32 unk[2] (0)
        u32 unk_a (256)  u32 unk_b (1)  u32 unpacked_size  u32 packed_size
        packed_size bytes HLZ
        the engine seeks to 8, reads 0x24 bytes, uses only packed_size and
        unpacks into the 640x480 screen

Pixels: RGB565 little-endian, row-major, top row first (0x40b266 turns them into
RGB555 on 555 surfaces). HLZ: Cryo's LZ (0x430700), identical to ScummVM's
Image::HLZDecoder::decodeFrameInPlace: a u32 LE bit register read MSB first;
1 = literal byte; 01 = long match (u16: count = v & 7, offset = (v >> 3) - 0x2000,
count 0 -> next byte, 0 = end); 00 = short match (2 bits count, byte offset - 0x100);
match length = count + 2. The stream ends exactly at the end of its chunk.

    python engines/peintre/tools/parsers/tgp.py            # validate the corpus
    python engines/peintre/tools/parsers/tgp.py --selftest
    python engines/peintre/tools/parsers/tgp.py --png OUT.png FILE.TGP
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/mission-sunlight/discs/cd/Data/GFX"
MAGIC = b"LZWCRYO\0"


class FormatError(Exception):
    pass


def hlz(src: bytes) -> bytes:
    """Unpack one HLZ stream; it must end exactly at the end of `src`."""
    out = bytearray()
    i, end = 0, len(src)
    reg = bits = 0

    def bit() -> int:
        nonlocal reg, bits, i
        if bits == 0:
            if i + 4 > end:
                raise FormatError("bit register past the end")
            reg = int.from_bytes(src[i:i + 4], "little")
            i += 4
            bits = 32
        bits -= 1
        return (reg >> bits) & 1

    while True:
        if bit():
            if i >= end:
                raise FormatError("literal past the end")
            out.append(src[i])
            i += 1
            continue
        if bit():
            if i + 2 > end:
                raise FormatError("long match past the end")
            v = src[i] | src[i + 1] << 8
            i += 2
            count, dist = v & 7, 0x2000 - (v >> 3)
            if count == 0:
                if i >= end:
                    raise FormatError("count byte past the end")
                count = src[i]
                i += 1
                if count == 0:
                    break
        else:
            count = bit() << 1
            count |= bit()
            if i >= end:
                raise FormatError("short match past the end")
            dist = 0x100 - src[i]
            i += 1
        count += 2
        if dist > len(out):
            raise FormatError(f"match distance {dist} outside output ({len(out)})")
        if dist >= count:
            s = len(out) - dist
            out += out[s:s + count]
        else:
            for _ in range(count):
                out.append(out[-dist])
    if i != end:
        raise FormatError(f"{end - i} bytes after the end marker")
    return bytes(out)


def read(path: Path):
    """(width, height, kind, pixels RGB565 bytes), validating every byte."""
    b = path.read_bytes()
    w, h = struct.unpack_from("<II", b)
    if b[12:20] == MAGIC:
        hs, u0, u1, ua, ub, usize, psize = struct.unpack_from("<I8x6I", b, 8)
        if (w, h, hs, u0, u1, ua, ub) != (640, 480, 0x24, 0, 0, 256, 1):
            raise FormatError(f"single header {(w, h, hs, u0, u1, ua, ub)}")
        if 0x2C + psize != len(b):
            raise FormatError("packed size does not reach EOF")
        px = hlz(b[0x2C:])
        if len(px) != usize or usize != w * h * 2:
            raise FormatError(f"unpacked {len(px)}, header {usize}")
        return w, h, "single", px
    (count,) = struct.unpack_from("<I", b, 8)
    pos, px = 12, bytearray()
    for _ in range(count):
        psize, usize = struct.unpack_from("<II", b, pos)
        pos += 8
        chunk = hlz(b[pos:pos + psize])
        if len(chunk) != usize:
            raise FormatError(f"chunk unpacked {len(chunk)}, header {usize}")
        px += chunk
        pos += psize
    if pos != len(b):
        raise FormatError(f"{len(b) - pos} bytes after the last chunk")
    if len(px) != w * h * 2:
        raise FormatError(f"chunks give {len(px)} bytes for {w}x{h}")
    return w, h, "chunked", bytes(px)


def _check(f: Path):
    try:
        w, h, kind, _ = read(f)
        return f.name, None, (kind, w, h)
    except FormatError as e:
        return f.name, str(e), None


def validate() -> int:
    files = sorted(p for p in CORPUS.iterdir() if p.suffix.lower() == ".tgp")
    with Pool() as pool:
        res = pool.map(_check, files)
    kinds = Counter()
    ok = 0
    for name, err, info in res:
        if err:
            print(f"FAIL {name}: {err}")
        else:
            ok += 1
            kinds[info[0]] += 1
    print(f"TGP: {ok}/{len(files)} files valid, every byte consumed; {dict(kinds)}")
    return 0 if ok == len(files) else 1


def to_png(w: int, h: int, px: bytes, out: str) -> None:
    from PIL import Image
    rgb = bytearray()
    for (v,) in struct.iter_unpack("<H", px):
        rgb += bytes(((v >> 11) * 255 // 31, (v >> 5 & 63) * 255 // 63, (v & 31) * 255 // 31))
    Image.frombytes("RGB", (w, h), bytes(rgb)).save(out)


def selftest() -> None:
    # register 1,1,1 (literals a b c), 00 + count 01 + byte 0xFD (distance 3,
    # length 3), 01 + u16 0 + byte 0 (end): bits 111 00 01 01 -> 0xE2800000
    s = struct.pack("<I", 0b11100010100000000000000000000000) + b"abc" + bytes([0xFD]) + bytes(3)
    assert hlz(s) == b"abcabc", hlz(s)
    try:
        hlz(s + b"\0")
    except FormatError:
        pass
    else:
        raise AssertionError("trailing byte accepted")
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--png", nargs=2, metavar=("OUT", "TGP"))
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.png:
        w, h, _, px = read(Path(a.png[1]))
        to_png(w, h, px, a.png[0])
    else:
        sys.exit(validate())
