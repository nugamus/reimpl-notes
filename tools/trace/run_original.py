# /// script
# requires-python = ">=3.11"
# dependencies = ["frida>=17"]
# ///
"""EXPERIMENTAL (issue #15: results differ between runs, background running not proven).
Run an original game in a normal window that keeps running in the background.

Old games make a borderless, always-on-top window the size of the screen (Grumpa: 2048x1280
on this PC, even under dgVoodoo's windowed mode) and pause when they lose focus. That gets
in the way of everything we do with a running original: snapshots, captures, traces, and
the user working next to it. This starts the game suspended under Frida and, before it
runs a single instruction:

  - the screen it asks for (GetSystemMetrics SM_CXSCREEN/SM_CYSCREEN) is the game's
    resolution (--size, default 800x600), so the window it builds is that size;
  - its windows are created framed and not always-on-top (CreateWindowEx), and later
    attempts to make them topmost or borderless are rewritten (SetWindowPos,
    SetWindowLong);
  - it never learns it lost focus: WM_ACTIVATEAPP / WM_ACTIVATE / WM_NCACTIVATE always
    say active, WM_KILLFOCUS is dropped, GetForegroundWindow/GetActiveWindow/GetFocus
    return its own window. So it keeps running behind other windows.

(DxWnd, in third_party/dxwnd, does the same and much more, but needs administrator rights.)

    uv run tools/trace/run_original.py C:/GrumpaNoCD/Grumpa.exe --size 800x600
    uv run tools/trace/run_original.py --selftest

Returns when the game exits.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

AGENT = r"""
const W = %W%, H = %H%;
const u32 = Process.getModuleByName('user32.dll');
let game = ptr(0);
const procs = new Set();
const WS_POPUP = 0x80000000, WS_OVERLAPPEDWINDOW = 0x00CF0000, WS_EX_TOPMOST = 0x8;

Interceptor.attach(u32.getExportByName('GetSystemMetrics'), {
  onEnter(a) { this.i = a[0].toInt32(); },
  onLeave(r) { if (this.i === 0) r.replace(ptr(W)); else if (this.i === 1) r.replace(ptr(H)); }
});

function hookProc(hwnd) {
  const getLong = new NativeFunction(u32.getExportByName('GetWindowLongA'), 'pointer', ['pointer', 'int']);
  const proc = getLong(hwnd, -4);
  if (procs.has(proc.toString())) return;
  procs.add(proc.toString());
  Interceptor.attach(proc, { onEnter(a) {
    const msg = a[1].toInt32() & 0xffff;
    if (msg === 0x1C || msg === 0x86) a[2] = ptr(1);                              // ACTIVATEAPP, NCACTIVATE
    else if (msg === 0x06 && (a[2].toInt32() & 0xffff) === 0) a[2] = ptr(1);      // ACTIVATE: inactive -> active
    else if (msg === 0x08) a[1] = ptr(0);                                         // KILLFOCUS -> NULL
  }});
  send('window ' + hwnd + ': procedure ' + proc + ' hooked');
}

['CreateWindowExA', 'CreateWindowExW'].forEach(n => Interceptor.attach(u32.getExportByName(n), {
  onEnter(a) {
    const parent = a[8];
    this.top = parent.isNull();
    if (!this.top) return;
    a[0] = ptr(a[0].toUInt32() & ~WS_EX_TOPMOST);
    a[3] = ptr((a[3].toUInt32() & ~WS_POPUP) | WS_OVERLAPPEDWINDOW);
    a[4] = ptr(60); a[5] = ptr(60);
  },
  onLeave(r) { if (this.top && !r.isNull()) { game = r; hookProc(r); } }
}));

Interceptor.attach(u32.getExportByName('SetWindowPos'), { onEnter(a) {
  if (!game.isNull() && a[0].equals(game) && a[1].toInt32() === -1) a[1] = ptr(-2);   // TOPMOST -> NOTOPMOST
}});
['SetWindowLongA', 'SetWindowLongW'].forEach(n => Interceptor.attach(u32.getExportByName(n), { onEnter(a) {
  if (game.isNull() || !a[0].equals(game)) return;
  const idx = a[1].toInt32();
  if (idx === -16) a[2] = ptr((a[2].toUInt32() & ~WS_POPUP) | WS_OVERLAPPEDWINDOW);
  else if (idx === -20) a[2] = ptr(a[2].toUInt32() & ~WS_EX_TOPMOST);
  else if (idx === -4) setTimeout(() => hookProc(game), 0);                         // a new procedure
}}));
['GetForegroundWindow', 'GetActiveWindow', 'GetFocus'].forEach(n => Interceptor.attach(u32.getExportByName(n), {
  onLeave(r) { if (!game.isNull()) r.replace(game); }
}));
send('hooks in place');
"""


def run(exe: Path, size: tuple[int, int]) -> int:
    import frida

    device = frida.get_local_device()
    pid = device.spawn([str(exe)], cwd=str(exe.parent))
    session = device.attach(pid)
    script = session.create_script(AGENT.replace("%W%", str(size[0])).replace("%H%", str(size[1])))
    script.on("message", lambda m, d: print(m.get("payload") or m.get("description")))
    script.load()
    device.resume(pid)
    ended = []
    session.on("detached", lambda *a: ended.append(1))
    try:
        while not ended:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("detached; the game keeps running")
    return 0


def selftest() -> None:
    assert "%W%" in AGENT and "GetSystemMetrics" in AGENT
    import frida  # noqa: F401  (installed)
    print("run_original selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("exe", nargs="?")
    ap.add_argument("--size", default="800x600")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        sys.exit(0)
    if not a.exe:
        print(__doc__)
        sys.exit(2)
    w, h = (int(v) for v in a.size.lower().split("x"))
    sys.exit(run(Path(a.exe), (w, h)))
