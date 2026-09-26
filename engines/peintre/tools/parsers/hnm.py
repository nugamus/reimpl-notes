"""HNM6 movies (Data/MOVIES/*.HNM and the extensionless A13_052B).

Layout (engines/peintre/docs/formats/README.md, hnm.ksy; E-0200..E-0203):

    64-byte header:
      char tag[4] "HNM6"; u16 unk_04; u8 audio_flags; u8 bpp; u16 width; u16 height;
      u32 file_size; u32 frame_count; u32 unk_14; u16 unk_18; u16 unk_1a;
      u32 max_frame_size; char author[16]; char copyright[16]
    frame_count superchunks, back to back, then a zero u32 at EOF:
      u32 size | flags << 24 (size includes these 4 bytes)
      chunks: u32 size (with its 8-byte header), char type[2], u16 flags, data,
              padded to a multiple of 4 inside the superchunk
    chunk types: IX / IV video (the EXE's frame walker 0x40c5c2 takes only these two),
      AA = first audio chunk (a 32-byte CRYO_APC header, then IMA ADPCM),
      BB = following audio chunks (ADPCM only)

audio_flags: bit 0 sound, bits 5..6 rate / 11025, bit 7 stereo (0x40c9aa).
IX video payload: 28-byte header of seven s32/u32 (quality, then five offsets into the
payload ending with `end`, then unk_18 = end again), then the bit, motion, short-motion and JPEG-like streams
(ScummVM image/codecs/hnm.cpp).

    python engines/peintre/tools/parsers/hnm.py            # validate the corpus
    python engines/peintre/tools/parsers/hnm.py -v         # one line per file
    python engines/peintre/tools/parsers/hnm.py --selftest
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/mission-sunlight/discs/cd/Data/MOVIES"
HEADER = struct.Struct("<4sHBBHHIIIHHI16s16s")
APC_HEADER = struct.Struct("<8s4sIIiiI")  # magic, version, samples, rate, left, right, flags
IX_HEADER = struct.Struct("<i6I")  # quality, bit, motion, shortmo, jpeg, end, unk_18


class FormatError(Exception):
    pass


def corpus_files() -> list[Path]:
    return sorted(p for p in CORPUS.iterdir()
                  if p.suffix.lower() == ".hnm" or p.name == "A13_052B")


def read(blob: bytes) -> dict:
    """Walk one HNM6 file; returns its header fields and chunk statistics."""
    if len(blob) < HEADER.size:
        raise FormatError("shorter than the header")
    (tag, unk_04, aflags, bpp, w, h, fsize, frames, unk_14, unk_18, unk_1a, max_frame,
     author, copyright_) = HEADER.unpack_from(blob)
    if tag != b"HNM6":
        raise FormatError(f"tag {tag!r}")
    if fsize != len(blob):
        raise FormatError(f"file_size {fsize} != {len(blob)}")
    if frames < 1 or max_frame < 1:  # the EXE rejects max_frame_size < 1 (0x40ba64)
        raise FormatError("corrupted header")
    info = dict(audio_flags=aflags, bpp=bpp, width=w, height=h, frames=frames,
                max_frame_size=max_frame, unk=(unk_04, unk_14, unk_18, unk_1a),
                author=author, copyright=copyright_, chunks=Counter(), sc_flags=Counter(),
                chunk_flags=Counter(), keyframes=0, aa=None, bb_sizes=Counter(),
                max_superchunk=0, max_video=0, audio_frames=0)
    pos, n = HEADER.size, 0
    while n < frames:
        if pos + 4 > len(blob):
            raise FormatError(f"superchunk header past EOF at {pos:#x}")
        (word,) = struct.unpack_from("<I", blob, pos)
        size, scflags = word & 0xFFFFFF, word >> 24
        if size < 4 or pos + size > len(blob):
            raise FormatError(f"superchunk {n} size {size} at {pos:#x}")
        info["sc_flags"][scflags] += 1
        info["max_superchunk"] = max(info["max_superchunk"], size)
        end, p = pos + size, pos + 4
        audio = False
        while p < end:
            if p + 8 > end:
                raise FormatError(f"frame {n}: chunk header past superchunk")
            csize, ctype, cflags = struct.unpack_from("<I2sH", blob, p)
            padded = (csize + 3) & ~3
            if csize < 8 or p + padded > end:
                raise FormatError(f"frame {n}: chunk {ctype!r} size {csize}")
            data = blob[p + 8: p + csize]
            if any(blob[p + csize: p + padded]):
                raise FormatError(f"frame {n}: non-zero chunk padding")
            ctype = ctype.decode("latin1")
            info["chunks"][ctype] += 1
            info["chunk_flags"][(ctype, cflags)] += 1
            if ctype in ("IX", "IV"):
                check_video(data, max_frame, n)
                info["max_video"] = max(info["max_video"], len(data))
                if struct.unpack_from("<i", data)[0] < 0:  # quality < 0: key frame
                    info["keyframes"] += 1
                elif n == 0:
                    raise FormatError("frame 0 is not a key frame")
            elif ctype == "AA":
                if info["aa"] is not None or n != 0:
                    raise FormatError(f"frame {n}: second AA chunk")
                info["aa"] = check_apc_chunk(data, aflags)
                audio = True
            elif ctype == "BB":
                if info["aa"] is None:
                    raise FormatError(f"frame {n}: BB before AA")
                info["bb_sizes"][len(data)] += 1
                audio = True
            else:
                raise FormatError(f"frame {n}: unknown chunk {ctype!r}")
            p += padded
        if p != end:
            raise FormatError(f"frame {n}: chunks overrun the superchunk")
        info["audio_frames"] += audio
        pos, n = end, n + 1
    if blob[pos:] != bytes(4):  # a zero superchunk word ends the file
        raise FormatError(f"{len(blob) - pos} bytes after superchunk {n}, not one zero u32")
    if (aflags & 1) != (info["aa"] is not None):
        raise FormatError(f"audio_flags {aflags:#x} but AA chunk present={info['aa'] is not None}")
    return info


def check_video(data: bytes, max_frame: int, n: int) -> None:
    if len(data) < IX_HEADER.size:
        raise FormatError(f"frame {n}: video chunk shorter than its header")
    q, *offs, unk_18 = IX_HEADER.unpack_from(data)
    if unk_18 != offs[-1]:  # ScummVM reads 24 header bytes and never looks at these 4
        raise FormatError(f"frame {n}: video unk_18 {unk_18} != end {offs[-1]}")
    if offs[0] != IX_HEADER.size or offs != sorted(offs):
        raise FormatError(f"frame {n}: video stream offsets {offs}")
    if offs[-1] != len(data):  # ScummVM reads `end` bytes: every byte is a stream byte
        raise FormatError(f"frame {n}: video end {offs[-1]} != payload {len(data)}")
    if offs[-1] > max_frame:  # ScummVM's decoder buffer is max_frame_size bytes
        raise FormatError(f"frame {n}: video payload {offs[-1]} > max_frame_size {max_frame}")
    if q == 0 or abs(q) > 100:
        raise FormatError(f"frame {n}: quality {q}")


def check_apc_chunk(data: bytes, aflags: int) -> tuple:
    if len(data) < APC_HEADER.size:
        raise FormatError("AA chunk shorter than an APC header")
    magic, ver, samples, rate, left, right, flags = APC_HEADER.unpack_from(data)
    if magic != b"CRYO_APC" or ver != b"1.20":
        raise FormatError(f"AA header {magic!r} {ver!r}")
    if rate != ((aflags & 0x60) >> 4) * 11025 or (flags & 1) != aflags >> 7:
        raise FormatError(f"AA rate {rate} / stereo {flags & 1} vs audio_flags {aflags:#x}")
    return samples, rate, flags, len(data) - APC_HEADER.size


def validate(verbose: bool) -> int:
    files = corpus_files()
    ok = 0
    total = Counter()
    fl = Counter()
    notes = Counter()
    for f in files:
        try:
            i = read(f.read_bytes())
        except FormatError as e:
            print(f"FAIL {f.name}: {e}")
            continue
        ok += 1
        total.update(i["chunks"])
        fl[(i["audio_flags"], i["bpp"], i["width"], i["height"], i["unk"], i["author"],
            i["copyright"])] += 1
        for k in i["sc_flags"]:
            notes[f"superchunk flag byte {k:#x}"] += 1
        for k in i["chunk_flags"]:
            notes[f"chunk {k[0]} flags {k[1]:#x}"] += 1
        line = (f"{f.name:14} {i['frames']:5} frames, key {i['keyframes']:4}, "
                f"audio {i['audio_flags']:#04x}")
        if i["aa"]:
            samples, rate, apcflags, adpcm = i["aa"]
            bb = i["bb_sizes"]
            per = adpcm // 32
            # the first chunk holds 32 frames' sound; each BB one frame's (0x40c9aa)
            if adpcm % 32 or set(bb) != {per}:
                notes["BB size != AA ADPCM / 32"] += 1
            if i["audio_frames"] != i["frames"] - 32:
                notes["audio frames != frames - 32"] += 1
            chans = 2 if apcflags & 1 else 1
            spf = per * 2 // chans
            line += f" {rate} Hz {'stereo' if chans == 2 else 'mono'}, {spf} samples/frame " \
                    f"= {rate / spf:.3f} fps, AA samples {samples}, audio frames {i['audio_frames']}"
            notes[f"fps {rate / spf:.2f}"] += 1
        else:
            notes["no sound (80 ms timer)"] += 1
        if verbose:
            print(line)
    print(f"HNM: {ok}/{len(files)} files valid, every byte consumed; chunks {dict(total)}")
    for k, v in sorted(fl.items(), key=lambda kv: -kv[1]):
        print(f"  {v:3} x header audio {k[0]:#04x} bpp {k[1]} {k[2]}x{k[3]} unk {k[4]} {k[5]!r} {k[6]!r}")
    for k, v in sorted(notes.items()):
        print(f"  {v:3} files: {k}")
    return 0 if ok == len(files) else 1


def build(frames: list[list[tuple[bytes, bytes]]], aflags: int = 0) -> bytes:
    body = b""
    for chunks in frames:
        sc = b""
        for t, d in chunks:
            c = struct.pack("<I2sH", 8 + len(d), t, 0) + d
            sc += c + bytes(-len(c) % 4)
        body += struct.pack("<I", len(sc) + 4) + sc
    body += bytes(4)
    hdr = HEADER.pack(b"HNM6", 0, aflags, 16, 640, 480, HEADER.size + len(body), len(frames),
                      0, 0, 2, 64, b"x" * 16, b"y" * 16)
    return hdr + body


def selftest() -> None:
    ix = IX_HEADER.pack(-50, 28, 28, 30, 30, 31, 31) + b"abc"  # 3 stream bytes, odd length
    blob = build([[(b"IX", ix)], [(b"IX", IX_HEADER.pack(40, 28, 28, 28, 28, 28, 28))]])
    i = read(blob)
    assert i["chunks"] == {"IX": 2} and i["keyframes"] == 1 and i["frames"] == 2
    apc = APC_HEADER.pack(b"CRYO_APC", b"1.20", 128, 22050, 0, 0, 0) + bytes(64)
    i = read(build([[(b"AA", apc), (b"IX", ix)], [(b"BB", bytes(2)), (b"IX", ix)]], 0x21))
    assert i["aa"][1] == 22050 and i["bb_sizes"] == {2: 1}
    for bad in (blob[:-1], blob.replace(b"IX", b"IW", 1), build([[(b"BB", b"")]])):
        try:
            read(bad)
        except FormatError:
            continue
        raise AssertionError("bad file accepted")
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    else:
        sys.exit(validate(a.v))
