"""HNM6 videos, stills and warps of China (every *.HNM / *.HNS under CHINE/).

Layout (engines/cryomni3d/docs/formats/README.md, hnm.ksy; E-0100, E-0101), the same as
Mission Sunlight's (engines/peintre/docs/formats/hnm.ksy) plus the warp variant:

    64-byte header:
      char tag[4] "HNM6"; u16 unk_04; u8 audio_flags; u8 bpp; u16 width; u16 height;
      u32 file_size; u32 frame_count; u32 unk_14; u16 unk_18; u16 unk_1a;
      u32 max_frame_size; char author[16]; char copyright[16]
    frame_count superchunks, back to back, then a zero u32 at EOF:
      u32 size | flags << 24 (size includes these 4 bytes)
      chunks: u32 size (with its 8-byte header), char type[2], u16 flags, data,
              padded to a multiple of 4 inside the superchunk
    chunk types: IX video (28-byte header: quality, five stream offsets, unk_18 = end),
      IW warp picture (24-byte header: quality > 0, five stream offsets; one frame only;
      decoded by ScummVM engines/cryomni3d/image/hnm.cpp in warp mode),
      AA first audio chunk (32-byte CRYO_APC header, then IMA ADPCM), BB later audio.

Warps (DATA/WARP): 2048x768, one IW frame, unk_1a = 1, and file_size = file length - 4
(the terminator is not counted); every other file counts it.

    python engines/cryomni3d/tools/parsers/hnm.py            # validate the corpus
    python engines/cryomni3d/tools/parsers/hnm.py -v         # one line per file
    python engines/cryomni3d/tools/parsers/hnm.py --selftest
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/china/discs/en-iso/cd1/CHINE"
HEADER = struct.Struct("<4sHBBHHIIIHHI16s16s")
APC_HEADER = struct.Struct("<8s4sIIiiI")  # magic, version, samples, rate, left, right, flags
IX_HEADER = struct.Struct("<i6I")  # quality, bit, motion, shortmo, jpeg, end, unk_18
IW_HEADER = struct.Struct("<i5I")  # quality, bit, motion, shortmo, jpeg, end


class FormatError(Exception):
    pass


def corpus_files() -> list[Path]:
    return sorted(p for p in CORPUS.rglob("*") if p.suffix.lower() in (".hnm", ".hns"))


def read(blob: bytes) -> dict:
    """Walk one HNM6 file; returns its header fields and chunk statistics."""
    if len(blob) < HEADER.size:
        raise FormatError("shorter than the header")
    (tag, unk_04, aflags, bpp, w, h, fsize, frames, unk_14, unk_18, unk_1a, max_frame,
     author, copyright_) = HEADER.unpack_from(blob)
    if tag != b"HNM6":
        raise FormatError(f"tag {tag!r}")
    if fsize not in (len(blob), len(blob) - 4):  # warps leave out the terminator (E-0101)
        raise FormatError(f"file_size {fsize} != {len(blob)}")
    if frames < 1 or max_frame < 1:
        raise FormatError("corrupted header")
    info = dict(audio_flags=aflags, bpp=bpp, width=w, height=h, frames=frames,
                max_frame_size=max_frame, unk=(unk_04, unk_14, unk_18, unk_1a),
                author=author, copyright=copyright_, chunks=Counter(), sc_flags=Counter(),
                chunk_flags=Counter(), keyframes=0, aa=None, bb_sizes=Counter(),
                max_superchunk=0, max_video=0, audio_frames=0,
                fsize_short=fsize == len(blob) - 4, quality=Counter())
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
            if ctype == "IW":
                if n != 0 or frames != 1:
                    raise FormatError(f"frame {n}: IW chunk outside a one-frame file")
                info["quality"][check_warp(data, max_frame)] += 1
                info["max_video"] = len(data)
            elif ctype in ("IX", "IV"):
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


def check_warp(data: bytes, max_frame: int) -> int:
    """IW payload: like IX but a 24-byte header (no unk_18); always a key picture."""
    if len(data) < IW_HEADER.size:
        raise FormatError("IW chunk shorter than its header")
    q, *offs = IW_HEADER.unpack_from(data)
    if offs[0] != IW_HEADER.size or offs != sorted(offs) or offs[-1] != len(data):
        raise FormatError(f"IW stream offsets {offs}, payload {len(data)}")
    if not 0 < q <= 100:  # ScummVM asserts quality > 0 in warp mode
        raise FormatError(f"IW quality {q}")
    if offs[-1] > max_frame:
        raise FormatError(f"IW payload {offs[-1]} > max_frame_size {max_frame}")
    return q


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
    per_folder: dict[str, Counter] = {}
    notes = Counter()
    for f in files:
        try:
            i = read(f.read_bytes())
        except FormatError as e:
            print(f"FAIL {f.relative_to(CORPUS)}: {e}")
            continue
        ok += 1
        total.update(i["chunks"])
        folder = f.parent.name if f.parent != CORPUS else "CHINE"
        fr = "1 frame" if i["frames"] == 1 else "frames>1"
        per_folder.setdefault(folder, Counter())[
            (i["width"], i["height"], fr, i["audio_flags"], i["bpp"], i["unk"],
             "+".join(sorted(i["chunks"])), "file_size=len-4" if i["fsize_short"] else "file_size=len",
             i["author"] + i["copyright"] == b"Pascal URRO  R&D-Copyright CRYO-")] += 1
        for k in i["sc_flags"]:
            notes[f"superchunk flag byte {k:#x}"] += 1
        for k in i["chunk_flags"]:
            notes[f"chunk {k[0]} flags {k[1]:#x}"] += 1
        for q in i["quality"]:
            notes[f"IW quality {q}"] += 1
        line = (f"{str(f.relative_to(CORPUS)):28} {i['frames']:5} frames, key {i['keyframes']:4}, "
                f"audio {i['audio_flags']:#04x}")
        if i["aa"]:
            samples, rate, apcflags, adpcm = i["aa"]
            bb = i["bb_sizes"]
            per = adpcm // 32
            # the first chunk holds 32 frames' sound; each BB one frame's
            if adpcm % 32 or set(bb) - {per}:
                notes["BB size != AA ADPCM / 32"] += 1  # none in the corpus
                line += f" BB sizes {dict(bb)} AA/32 {adpcm / 32}"
            notes[f"audio frames - frames = {i['audio_frames'] - i['frames']}"] += 1
            chans = 2 if apcflags & 1 else 1
            spf = per * 2 // chans
            line += f" {rate} Hz {'stereo' if chans == 2 else 'mono'}, {spf} samples/frame "                     f"= {rate / spf:.3f} fps, AA samples {samples}, audio frames {i['audio_frames']}"
            notes[f"fps {rate / spf:.2f}"] += 1
        if verbose:
            print(line)
    print(f"HNM: {ok}/{len(files)} files valid, every byte consumed; chunks {dict(total)}")
    for folder, c in sorted(per_folder.items()):
        for k, v in sorted(c.items(), key=lambda kv: -kv[1]):
            print(f"  {folder:8} {v:3} x {k[0]}x{k[1]} {k[2]} audio {k[3]:#04x} bpp {k[4]} "
                  f"unk {k[5]} chunks {k[6]} {k[7]} author/copyright std {k[8]}")
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
    iw = IW_HEADER.pack(85, 24, 24, 25, 25, 27) + b"abc"
    w = build([[(b"IW", iw)]])
    w = w[:12] + struct.pack("<I", len(w) - 4) + w[16:]  # warps leave out the terminator
    i = read(w)
    assert i["chunks"] == {"IW": 1} and i["fsize_short"] and i["quality"] == {85: 1}
    bad_iw = build([[(b"IW", IW_HEADER.pack(-85, 24, 24, 25, 25, 27) + b"abc")]])
    for bad in (blob[:-1], blob.replace(b"IX", b"IW", 1), build([[(b"BB", b"")]]), bad_iw):
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
