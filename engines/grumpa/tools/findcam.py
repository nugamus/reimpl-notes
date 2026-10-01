"""Scan a running Grumpa process for the view/projection matrices (Q-0008).

With the no-CD Grumpa.exe running (SafeDisc-free) in a scene, the software-3D device holds
the per-view camera. This scans the process's committed memory for 4x4 float matrices that
look like a perspective projection (a diagonal of 1/tan(fov/2)-ish terms, a +-1 in the w
column, the rest ~0) and for orthonormal view matrices (rotation rows unit length), and
prints candidates with the derived FOV. Read-only (ReadProcessMemory).

    python engines/grumpa/tools/findcam.py
"""
from __future__ import annotations
import ctypes, ctypes.wintypes as wt, struct, sys, math
sys.path.insert(0, "engines/grumpa/tools"); import sddump
k32 = sddump.k32
k32.VirtualQueryEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", wt.DWORD), ("RegionSize", ctypes.c_size_t),
                ("State", wt.DWORD), ("Protect", wt.DWORD), ("Type", wt.DWORD)]

def regions(h):
    addr = 0
    mbi = MBI()
    while addr < 0x7fff0000:
        if not k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            break
        if mbi.State == 0x1000 and (mbi.Protect & 0xff) in (0x02, 0x04, 0x20, 0x40) and mbi.RegionSize < 0x4000000:
            yield mbi.BaseAddress or addr, mbi.RegionSize
        addr = (mbi.BaseAddress or addr) + mbi.RegionSize

def f(b, o):
    return struct.unpack_from("<f", b, o)[0]

def scan(h):
    hits = []
    for base, size in regions(h):
        try:
            data = sddump.read(h, base, size)
        except OSError:
            continue
        for o in range(0, len(data) - 64, 4):
            m = struct.unpack_from("<16f", data, o)
            # perspective projection: m[0],m[5] in [0.5,5], many near-zero, |m[11]| or |m[14]| ~1
            if not (0.5 < abs(m[0]) < 5 and 0.5 < abs(m[5]) < 5):
                continue
            zeros = sum(1 for i in (1, 2, 3, 4, 6, 7, 8, 9, 12, 13) if abs(m[i]) < 1e-4)
            wcol = abs(abs(m[11]) - 1) < 1e-3 or abs(abs(m[14]) - 1) < 1e-3
            if zeros >= 8 and wcol:
                aspect = 800.0 / 600.0
                fov = math.degrees(2 * math.atan(1.0 / m[5])) if m[5] else 0
                hits.append((base + o, m, fov))
    return hits

def main():
    pid = sddump.find_pid("Grumpa.exe")
    if not pid:
        sys.exit("Grumpa.exe not running")
    h = k32.OpenProcess(sddump.PROCESS_ALL_ACCESS, False, pid)
    hits = scan(h)
    print(f"{len(hits)} projection-matrix candidates:")
    for a, m, fov in hits[:20]:
        print(f"  @0x{a:08x} fovY~{fov:.1f} m00={m[0]:.3f} m11={m[5]:.3f} m22={m[10]:.4f} m23={m[11]:.1f} m32={m[14]:.3f} m33={m[15]:.1f}")

if __name__ == "__main__":
    main()
