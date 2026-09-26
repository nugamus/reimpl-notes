"""The Ring engine's packed bit stream (RING_DVD.EXE 0x4308e0, E-0017), in Python and
through the C build of the same loop (ringdec.c -> build/ringdec.dll, compiled here on
first use with MSYS2's gcc).

    decode(buf, vbits, ibits, start_bit, end_bit, max_codes) -> (codes, end_bit_reached)

Decoding stops at end_bit or after max_codes codes, whichever comes first.

    python engines/ring/tools/parsers/bitstream.py --selftest
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DLL = HERE.parents[3] / "build" / "ringdec.dll"
GCC = Path(r"C:\msys64\ucrt64\bin\gcc.exe")


def py_decode(buf: bytes, vbits: int, ibits: int, pos: int, end: int, max_codes: int):
    value, stamp = [0] * 64, [0] * 64
    repl = last = 0
    out: list[int] = []
    n = len(buf)
    while pos < end and len(out) < max_codes:
        o = pos >> 3
        w = int.from_bytes(buf[o:o + 4].ljust(4, b"\0"), "big") if o < n else 0
        sh = 31 - (pos & 7)
        if not (w >> sh) & 1:
            v = ((w << (32 - sh)) & 0xFFFFFFFF) >> (32 - vbits)
            out.append(v)
            last = repl
            value[repl] = v
            pos += vbits + 1
        elif not (w >> (sh - 1)) & 1:
            i = ((w << (33 - sh)) & 0xFFFFFFFF) >> (32 - ibits)
            last = i
            out.append(value[i])
            pos += ibits + 2
            stamp[i] = pos
            if i == repl:
                repl = min(range(64), key=lambda k: (stamp[k], k))
        else:
            pos += 2
            out.append(out[-1] if out else 0)
            stamp[last] = pos
            if repl == last:
                repl = min(range(64), key=lambda k: (stamp[k], k))
    return out, pos


_lib = None


def _load():
    global _lib
    if _lib is None:
        src = HERE / "ringdec.c"
        if not DLL.exists() or DLL.stat().st_mtime < src.stat().st_mtime:
            DLL.parent.mkdir(parents=True, exist_ok=True)
            env = dict(os.environ, PATH=str(GCC.parent) + os.pathsep + os.environ["PATH"])
            subprocess.run([str(GCC), "-O2", "-shared", "-o", str(DLL), str(src)],
                           check=True, env=env)
        os.add_dll_directory(str(GCC.parent))
        lib = ctypes.CDLL(str(DLL))
        lib.ring_decode.restype = ctypes.c_int
        lib.ring_decode.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_uint32, ctypes.c_uint32,
                                    ctypes.POINTER(ctypes.c_uint16), ctypes.c_size_t,
                                    ctypes.POINTER(ctypes.c_uint32)]
        _lib = lib
    return _lib


def decode(buf: bytes, vbits: int, ibits: int, pos: int, end: int, max_codes: int):
    lib = _load()
    cap = min(max_codes, max(0, end - pos) // 2 + 1)
    out = (ctypes.c_uint16 * cap)()
    endpos = ctypes.c_uint32()
    n = lib.ring_decode(buf, len(buf), vbits, ibits, pos, end, out, cap, ctypes.byref(endpos))
    return out[:n], endpos.value


def selftest() -> None:
    # Hand-built stream: literal 0x1234 (16 bits), repeat, cache hit slot 0, literal 5.
    bits = "0" + format(0x1234, "016b") + "11" + "10" + "000000" + "0" + format(5, "016b")
    nbytes = (len(bits) + 7) // 8
    buf = int(bits.ljust(nbytes * 8, "0"), 2).to_bytes(nbytes, "big")
    want = [0x1234, 0x1234, 0x1234, 5]
    assert py_decode(buf, 16, 6, 0, len(bits), 99) == (want, len(bits))
    assert decode(buf, 16, 6, 0, len(bits), 99) == (want, len(bits))
    # A pseudo-random stream exercises the cache replacement in both versions alike.
    import random

    rnd = random.Random(1)
    blob = bytes(rnd.randrange(256) for _ in range(4000))
    for vb, ib in ((16, 6), (11, 6), (13, 6)):
        assert py_decode(blob, vb, ib, 3, 30000, 10**6) == decode(blob, vb, ib, 3, 30000, 10**6)
    print("selftest ok")


if __name__ == "__main__" and "--selftest" in sys.argv:
    selftest()
