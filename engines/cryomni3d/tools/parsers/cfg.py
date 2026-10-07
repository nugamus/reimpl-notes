"""China's options file chine.cfg: four little-endian u32 (16 bytes).

Layout (engines/cryomni3d/docs/formats/README.md, china_cfg.ksy; E-0207): Options::load
0x405870 reads, Options::save 0x4059f0 writes, in this order: navigation speed 0..4
(very slow, slow, normal, rapid, very rapid), subtitles 0/1, music 0/1, save mode
(1 = automatic, 0 = manual).

    python engines/cryomni3d/tools/parsers/cfg.py            # validate the corpus
    python engines/cryomni3d/tools/parsers/cfg.py --selftest
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/china/discs/en-iso/cd1/CHINE/chine.cfg"
SPEEDS = ("very slow", "slow", "normal", "rapid", "very rapid")


class FormatError(Exception):
    pass


def read(blob: bytes) -> dict:
    if len(blob) != 16:
        raise FormatError(f"{len(blob)} bytes, expected 16")
    speed, subs, music, auto = struct.unpack("<4I", blob)
    if speed > 4 or subs > 1 or music > 1 or auto > 1:
        raise FormatError(f"value out of range {speed, subs, music, auto}")
    return {"speed": SPEEDS[speed], "subtitles": bool(subs), "music": bool(music),
            "save_mode": "automatic" if auto else "manual"}


def selftest() -> None:
    assert read(struct.pack("<4I", 2, 1, 1, 0)) == {
        "speed": "normal", "subtitles": True, "music": True, "save_mode": "manual"}
    for bad in (b"\0" * 15, struct.pack("<4I", 5, 0, 0, 0)):
        try:
            read(bad)
            raise AssertionError(bad)
        except FormatError:
            pass
    print("selftest ok")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("file", nargs="?", type=Path, default=CORPUS)
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    try:
        print(f"ok   {a.file.name}: {read(a.file.read_bytes())}")
    except FormatError as e:
        print(f"FAIL {a.file.name}: {e}")
        return 1
    print("1/1 cfg files parsed, every byte accounted for")
    return 0


if __name__ == "__main__":
    sys.exit(main())
