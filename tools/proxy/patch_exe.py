"""Patch the run-folder copy of the game so it can run windowed on a 32-bit desktop.

Never point this at `Original Game Files/` (CLAUDE.md rule 7). It edits the copy in the run
folder (default C:\\MonetRun), checks the original bytes before writing, and is idempotent.

    python tools/proxy/patch_exe.py [--run C:\\MonetRun]

Patches:
  MissionMonet.exe 0x0041768c  je -> jmp. In windowed mode (0x004667a4 == 0) the game
      calls GetDeviceCaps(GetDC(hwnd), BITSPIXEL) (0x00417683) and shows message 951
      "Please set your screen to 16 bits colour mode." unless it is 16. dgVoodoo reports
      16 bpp to DirectDraw (DesktopBitDepth = 16) but cannot change the GDI answer.
  MissionMonet.exe 0x00416cdc  push 1 -> push 4. WinMain's windowed-path
      ShowWindow(hwnd, SW_SHOWNORMAL) (0x00416cdf) becomes SW_SHOWNOACTIVATE, so the
      window appears behind whatever you are using instead of taking focus.
  MissionD.exe 0x0042cd6b / 0x0042bbcf  the same two patches in the developer build
      (GetDeviceCaps at 0x0042cd62, windowed-path ShowWindow at 0x0042bbd8).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pefile

# (file, virtual address, original bytes, patched bytes, reason)
PATCHES = [
    ("MissionMonet.exe", 0x0041768C, b"\x74\x35", b"\xEB\x35", "skip 16-bit desktop check"),
    ("MissionMonet.exe", 0x00416CDC, b"\x6A\x01", b"\x6A\x04", "show game window without activating it"),
    # Same two sites in the developer build (unoptimised, so different code shape).
    ("MissionD.exe", 0x0042CD6B, b"\x74\x6B", b"\xEB\x6B", "skip 16-bit desktop check"),
    ("MissionD.exe", 0x0042BBCF, b"\x6A\x01", b"\x6A\x04", "show game window without activating it"),
]


def apply(run: Path) -> int:
    if "Original Game Files" in str(run.resolve()):
        raise SystemExit("refusing to patch the original game files")
    for name, va, old, new, why in PATCHES:
        path = run / name
        pe = pefile.PE(str(path), fast_load=True)
        off = pe.get_offset_from_rva(va - pe.OPTIONAL_HEADER.ImageBase)
        pe.close()
        data = bytearray(path.read_bytes())
        cur = bytes(data[off : off + len(old)])
        if cur == new:
            print(f"{name} 0x{va:08x} already patched ({why})")
            continue
        if cur != old:
            raise SystemExit(f"{name} 0x{va:08x}: expected {old.hex()}, found {cur.hex()}; wrong binary?")
        data[off : off + len(new)] = new
        path.write_bytes(bytes(data))
        print(f"{name} 0x{va:08x} {old.hex()} -> {new.hex()} ({why})")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, default=Path("C:/MonetRun"))
    sys.exit(apply(ap.parse_args().run))
