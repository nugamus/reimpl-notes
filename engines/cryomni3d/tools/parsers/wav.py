"""RIFF WAVE sounds of China (every *.WAV under CHINE/: LOC/VOICES, SOUND, PUZZLES, SPRITES).

Layout (engines/cryomni3d/docs/formats/README.md, wav.ksy; E-0104): standard RIFF,
"WAVE", then chunks {char id[4]; u32 size; data; pad to even}; `fmt ` is 16 bytes (or 18
with cbSize 0), the `data` size a multiple of the block size. Same checks as Mission
Sunlight's validator (engines/peintre/tools/parsers/wav.py). Which CHINE.EXE routine reads
them and which fields it uses is not traced yet (Q-0101).

    python engines/cryomni3d/tools/parsers/wav.py            # validate the corpus
    python engines/cryomni3d/tools/parsers/wav.py --selftest
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/china/discs/en-iso/cd1/CHINE"
FMT = struct.Struct("<HHIIHH")  # tag, channels, rate, byte rate, block align, bits


class FormatError(Exception):
    pass


def read(blob: bytes) -> dict:
    if len(blob) < 12 or blob[:4] != b"RIFF" or blob[8:12] != b"WAVE":
        raise FormatError("not a RIFF WAVE file")
    (riff,) = struct.unpack_from("<I", blob, 4)
    if riff + 8 != len(blob):
        raise FormatError(f"RIFF size {riff} + 8 != {len(blob)}")
    pos, order, fmt, data = 12, [], None, None
    while pos < len(blob):
        if pos + 8 > len(blob):
            raise FormatError("chunk header past EOF")
        cid, size = struct.unpack_from("<4sI", blob, pos)
        end = pos + 8 + size + (size & 1)
        if pos + 8 + size > len(blob) or end > len(blob):
            raise FormatError(f"chunk {cid!r} past EOF")
        order.append(cid.decode("latin1"))
        if cid == b"fmt ":
            if size < 14:
                raise FormatError("fmt shorter than 14 bytes")
            fmt = FMT.unpack_from(blob, pos + 8) if size >= 16 else None
            if size > 16:
                (cb,) = struct.unpack_from("<H", blob, pos + 24)
                if size != 18 or cb != 0:
                    raise FormatError(f"fmt size {size}, cbSize {cb}")
        elif cid == b"data":
            data = size
        pos = end
    if fmt is None or data is None:
        raise FormatError("no fmt or data chunk")
    tag, ch, rate, brate, align, bits = fmt
    if align != ch * bits // 8 or brate != rate * align:
        raise FormatError(f"inconsistent fmt {fmt}")
    if data % align:
        raise FormatError(f"data size {data} not a multiple of {align}")
    return dict(fmt=fmt, order=tuple(order), data=data)


def validate() -> int:
    files = sorted(p for p in CORPUS.rglob("*") if p.suffix.lower() == ".wav")
    ok = 0
    fmts, orders = Counter(), Counter()
    for f in files:
        try:
            i = read(f.read_bytes())
        except FormatError as e:
            print(f"FAIL {f.relative_to(CORPUS)}: {e}")
            continue
        ok += 1
        fmts[i["fmt"]] += 1
        orders[i["order"]] += 1
    print(f"WAV: {ok}/{len(files)} files valid, every byte consumed")
    for (tag, ch, rate, _, _, bits), v in fmts.items():
        print(f"  {v:3} x tag {tag} ({'PCM' if tag == 1 else '?'}), {ch} ch, {rate} Hz, {bits} bit")
    for k, v in orders.items():
        print(f"  {v:3} x chunks {' '.join(k)}")
    return 0 if ok == len(files) else 1


def build(chunks: list[tuple[bytes, bytes]]) -> bytes:
    body = b"WAVE" + b"".join(struct.pack("<4sI", c, len(d)) + d + bytes(len(d) & 1)
                              for c, d in chunks)
    return b"RIFF" + struct.pack("<I", len(body)) + body


def selftest() -> None:
    fmt = FMT.pack(1, 1, 22050, 44100, 2, 16)
    assert read(build([(b"fmt ", fmt), (b"data", bytes(4)), (b"LIST", b"abc")]))["data"] == 4
    for bad in (build([(b"fmt ", fmt)]), build([(b"fmt ", fmt), (b"data", bytes(3))]),
                build([(b"fmt ", fmt), (b"data", bytes(4))])[:-1]):
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
