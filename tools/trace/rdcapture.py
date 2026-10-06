"""EXPERIMENTAL (issue #15: no capture yet; needs the game windowed and active first).
Exact frames from a running original, through RenderDoc (third_party/renderdoc).

Works for games that end up on Direct3D 11 or OpenGL, which includes every DirectDraw and
Direct3D 1..7 game run under dgVoodoo (it translates them to Direct3D 11), where apitrace
cannot capture frames. Starts the game under `renderdoccmd capture`, waits for each moment
you name (seconds from start), brings the game's window forward and presses RenderDoc's
capture key (F12), then closes the game and writes each captured frame as a PNG next to
its .rdc capture. Open a capture in `qrenderdoc.exe` to step through every draw call.

    python tools/trace/rdcapture.py C:/GrumpaNoCD/Grumpa.exe --at 20 35 --out engines/grumpa/traces/original/intro
    python tools/trace/rdcapture.py --selftest

Captures are the original's imagery: they stay local (traces/ images are gitignored).
"""

from __future__ import annotations

import argparse
import ctypes
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RD = REPO / "third_party" / "renderdoc" / "RenderDoc_1.46_64"
VK_F12 = 0x7B
user32 = ctypes.windll.user32 if sys.platform == "win32" else None


def windows_of(pid: int) -> list[int]:
    found = []
    proto = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def cb(hwnd, _):
        owner = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid and user32.IsWindowVisible(hwnd):
            found.append(hwnd)
        return True
    user32.EnumWindows(proto(cb), 0)
    return found


def press_f12(pid: int) -> bool:
    wins = windows_of(pid)
    if not wins:
        return False
    user32.SetForegroundWindow(wins[0])
    time.sleep(0.3)
    user32.keybd_event(VK_F12, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(VK_F12, 0, 2, 0)  # KEYEVENTF_KEYUP
    return True


def pid_of(exe_name: str) -> int | None:
    out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {exe_name}", "/FO", "CSV", "/NH"],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) > 1 and parts[0].lower() == exe_name.lower():
            return int(parts[1])
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("exe")
    ap.add_argument("--at", type=float, nargs="+", required=True, help="seconds after start to capture")
    ap.add_argument("--out", required=True, help="folder (and file prefix) for captures")
    a = ap.parse_args()
    exe = Path(a.exe)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    subprocess.Popen([str(RD / "renderdoccmd.exe"), "capture", "-d", str(exe.parent), "-c", str(out / exe.stem), str(exe)])
    start = time.time()
    pid = None
    for t in sorted(a.at):
        while time.time() - start < t:
            time.sleep(0.2)
        pid = pid or pid_of(exe.name)
        ok = pid is not None and press_f12(pid)
        print(f"{t:.0f}s: {'capture requested' if ok else 'no game window to capture'}")
        time.sleep(2)
    if pid:
        subprocess.run(["taskkill", "/PID", str(pid)], capture_output=True)  # close normally first
        time.sleep(5)
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
    shots = []
    for rdc in sorted(out.glob("*.rdc")):
        png = rdc.with_suffix(".png")
        subprocess.run([str(RD / "renderdoccmd.exe"), "thumb", "-o", str(png), str(rdc)], capture_output=True)
        if png.exists():
            shots.append(png)
    print(f"{len(shots)} frame(s): " + ", ".join(str(p) for p in shots) if shots else "no captures were written")
    return 0 if shots else 1


def selftest() -> None:
    assert (RD / "renderdoccmd.exe").exists() and (RD / "qrenderdoc.exe").exists()
    assert pid_of("definitely-not-running-xyz.exe") is None
    me = pid_of("python.exe") or pid_of("py.exe")
    assert me is None or isinstance(me, int)
    print("rdcapture selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        sys.exit(main())
