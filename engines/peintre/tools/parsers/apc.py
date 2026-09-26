"""CRYO_APC sounds (Data/SOUND/*.APC), streamed by the game's '!' sound path.

Layout (engines/peintre/docs/formats/README.md, apc.ksy; E-0207):

    char magic[8] "CRYO_APC"; char version[4] "1.20"
    u32 samples                     per channel
    u32 rate
    s32 left_start, right_start     initial predictors
    u32 flags                       bit 0 stereo
    IMA ADPCM, high nibble first (stereo: high = left, low = right),
    samples * channels / 2 bytes rounded down, plus one byte: the size the Cryo encoder
    (0x4662bd) allocates, pcm_bytes / 4 + 0x21 with the header; the last byte is zero
    or holds the final high nibble

    python engines/peintre/tools/parsers/apc.py            # validate the corpus
    python engines/peintre/tools/parsers/apc.py --selftest
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/mission-sunlight/discs/cd/Data/SOUND"
HEADER = struct.Struct("<8s4sIIiiI")


class FormatError(Exception):
    pass


def read(blob: bytes) -> dict:
    if len(blob) < HEADER.size:
        raise FormatError("shorter than the header")
    magic, ver, samples, rate, left, right, flags = HEADER.unpack_from(blob)
    if magic != b"CRYO_APC" or ver != b"1.20":  # 0x4667ad checks both
        raise FormatError(f"magic {magic!r} {ver!r}")
    if flags & ~1:
        raise FormatError(f"flags {flags:#x}")
    chans = 2 if flags & 1 else 1
    want = samples * 2 * chans // 4 + 1
    if len(blob) - HEADER.size != want:
        raise FormatError(f"{len(blob) - HEADER.size} ADPCM bytes, header wants {want}")
    if samples * chans % 2 == 0 and blob[-1]:
        raise FormatError("padding byte not zero")
    if samples * chans % 2 and blob[-1] & 0x0F:
        raise FormatError("unused low nibble of the last byte not zero")
    return dict(samples=samples, rate=rate, channels=chans, start=(left, right))


def validate() -> int:
    files = sorted(p for p in CORPUS.iterdir() if p.suffix.lower() == ".apc")
    ok = 0
    kinds = Counter()
    secs = 0.0
    for f in files:
        try:
            i = read(f.read_bytes())
        except FormatError as e:
            print(f"FAIL {f.name}: {e}")
            continue
        ok += 1
        kinds[(i["rate"], i["channels"], i["start"])] += 1
        secs += i["samples"] / i["rate"]
    print(f"APC: {ok}/{len(files)} files valid, every byte consumed; {secs / 60:.1f} min")
    for (rate, ch, start), v in kinds.items():
        print(f"  {v:3} x {rate} Hz, {ch} channel(s), start predictors {start}")
    return 0 if ok == len(files) else 1


def selftest() -> None:
    hdr = HEADER.pack(b"CRYO_APC", b"1.20", 5, 22050, 0, 0, 0)
    assert read(hdr + b"\x12\x34\x50")["samples"] == 5  # 5 nibbles, last low nibble 0
    for bad in (hdr + b"\x12\x34\x55", hdr + b"\x12\x34", hdr[:-1] + b"\x02" + b"\x12\x34\x50"):
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
    if a.selftest:
        selftest()
    else:
        sys.exit(validate())
