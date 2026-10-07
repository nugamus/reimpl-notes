"""China's music (DATA/MUSIC/*.ZIK): headerless PCM.

Layout (engines/cryomni3d/docs/formats/README.md, zik.ksy; E-0206): no header at all;
the whole file is little-endian signed 16-bit stereo PCM at 22050 Hz (4 bytes a frame),
played from byte 0 and looped from byte 0 at the end. Music::update 0x412740 streams it
into a 512 KiB looping DirectSound buffer.

    python engines/cryomni3d/tools/parsers/zik.py            # validate the corpus
    python engines/cryomni3d/tools/parsers/zik.py --selftest
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/china/discs/en-iso/cd1/CHINE/DATA/MUSIC"
RATE, FRAME = 22050, 4


class FormatError(Exception):
    pass


def read(blob: bytes) -> dict:
    if not blob or len(blob) % FRAME:
        raise FormatError(f"size {len(blob)} is not a whole number of 4-byte frames")
    lead = len(blob) - len(blob.lstrip(b"\0"))
    return {"frames": len(blob) // FRAME, "seconds": round(len(blob) / FRAME / RATE, 2),
            "silent_lead_bytes": lead}


def selftest() -> None:
    assert read(b"\0\0\0\0\1\0\2\0") == {"frames": 2, "seconds": 0.0, "silent_lead_bytes": 4}
    try:
        read(b"\0\0\0")
        raise AssertionError
    except FormatError:
        pass
    print("selftest ok")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("folder", nargs="?", type=Path, default=CORPUS)
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    files = sorted(p for p in a.folder.iterdir() if p.suffix.upper() == ".ZIK")
    ok = 0
    for p in files:
        try:
            print(f"ok   {p.name}: {read(p.read_bytes())}")
            ok += 1
        except FormatError as e:
            print(f"FAIL {p.name}: {e}")
    print(f"{ok}/{len(files)} ZIK files parsed, every byte accounted for")
    return 0 if files and ok == len(files) else 1


if __name__ == "__main__":
    sys.exit(main())
