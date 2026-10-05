r"""Patch the run-folder copy of Mission Sunlight so it runs without an installation.

Never point this at games/mission-sunlight/discs. It edits the copy in
the run folder (default C:\SunlightRun\mission.exe), checks the original bytes before
writing, and is idempotent.

    python engines/peintre/tools/run/patch_exe.py [--run C:\SunlightRun]

Patches:
  mission.exe 0x00418448  push 0x80000002 -> push 0x80000001. Registry_Read (0x418416)
      opens HKLM\SOFTWARE\Cryo\Mission Sunlight with KEY_ALL_ACCESS (boot.md "Data
      root"), which needs an elevated installer. HKEY_CURRENT_USER instead lets
      setup_run.sh write the same keys for the current user.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pefile

# (file, virtual address, original bytes, patched bytes, reason)
PATCHES = [
    ("mission.exe", 0x00418448, bytes.fromhex("6802000080"), bytes.fromhex("6801000080"),
     "read the game's registry key from HKCU instead of HKLM"),
]


def apply(run: Path) -> int:
    if "discs" in str(run.resolve()).replace("\\", "/").split("/"):
        raise SystemExit("refusing to patch the original game files")
    for name, va, old, new, why in PATCHES:
        path = run / name
        pe = pefile.PE(str(path), fast_load=True)
        off = pe.get_offset_from_rva(va - pe.OPTIONAL_HEADER.ImageBase)
        pe.close()
        data = bytearray(path.read_bytes())
        cur = bytes(data[off: off + len(old)])
        if cur == new:
            print(f"{name} 0x{va:08x} already patched ({why})")
            continue
        if cur != old:
            raise SystemExit(f"{name} 0x{va:08x}: expected {old.hex()}, found {cur.hex()}; wrong binary?")
        data[off: off + len(new)] = new
        path.write_bytes(bytes(data))
        print(f"{name} 0x{va:08x} {old.hex()} -> {new.hex()} ({why})")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, default=Path("C:/SunlightRun"))
    sys.exit(apply(ap.parse_args().run))
