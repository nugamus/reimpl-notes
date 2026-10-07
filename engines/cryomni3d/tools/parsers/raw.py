"""RAW puzzle masks of China (DATA/PUZZLES/HORLOGE/MASK.RAW, PUZZLE4/MASK.RAW).

Layout (E-0106): 640 * 480 bytes, no header, one byte per screen pixel, row by row from
the top. CHINE.EXE loads the whole file (0x413200) and looks up the byte under the mouse
as mask[y * 640 + x]:
  - PUZZLE4 (0x4189bc): value - 0xE7 is a zone 0..23 (0xE7..0xFE), 0xFF (24) = no zone;
  - HORLOGE (0x41c1d0): 0 = no zone, 1..54 a zone (the code tests < 0x37 and < 13).

    python engines/cryomni3d/tools/parsers/raw.py            # validate the corpus
    python engines/cryomni3d/tools/parsers/raw.py --selftest
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/china/discs/en-iso/cd1/CHINE"
W, H = 640, 480
# the values each puzzle's code can tell apart (E-0106)
RANGES = {"PUZZLE4": range(0xE7, 0x100), "HORLOGE": range(0, 0x37)}


class FormatError(Exception):
    pass


def read(blob: bytes, puzzle: str) -> set[int]:
    if len(blob) != W * H:
        raise FormatError(f"{len(blob)} bytes, not 640x480")
    vals = set(blob)
    if not vals <= set(RANGES[puzzle]):
        raise FormatError(f"values {sorted(vals - set(RANGES[puzzle]))} outside {RANGES[puzzle]}")
    return vals


def validate() -> int:
    files = sorted(p for p in CORPUS.rglob("*") if p.suffix.lower() == ".raw")
    ok = 0
    for f in files:
        try:
            vals = read(f.read_bytes(), f.parent.name.upper())
        except (FormatError, KeyError) as e:
            print(f"FAIL {f.relative_to(CORPUS)}: {e}")
            continue
        ok += 1
        print(f"  {f.parent.name}/{f.name}: {len(vals)} values {min(vals)}..{max(vals)}"
              f"{'' if len(vals) == max(vals) - min(vals) + 1 else ' (gaps)'}")
    print(f"RAW: {ok}/{len(files)} files valid, every byte consumed")
    return 0 if ok == len(files) else 1


def selftest() -> None:
    assert read(bytes([0xFF]) * (W * H), "PUZZLE4") == {0xFF}
    for bad, pz in ((bytes(W * H - 1), "HORLOGE"), (bytes([0x37]) * (W * H), "HORLOGE"),
                    (bytes(W * H), "PUZZLE4")):
        try:
            read(bad, pz)
        except FormatError:
            continue
        raise AssertionError("bad file accepted")
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    sys.exit(selftest() if a.selftest else validate())
