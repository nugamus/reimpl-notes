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
        lib.ring_dpcm.restype = ctypes.c_int
        lib.ring_dpcm.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_int,
                                  ctypes.c_int, ctypes.POINTER(ctypes.c_int16),
                                  ctypes.POINTER(ctypes.c_int16), ctypes.POINTER(ctypes.c_uint32)]
        lib.ring_hbr.restype = ctypes.c_int
        lib.ring_hbr.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_uint32,
                                 ctypes.c_char_p, ctypes.c_size_t,
                                 ctypes.POINTER(ctypes.c_uint16), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint16),
                                 ctypes.POINTER(ctypes.c_uint16), ctypes.c_int,
                                 ctypes.POINTER(ctypes.c_uint16), ctypes.c_size_t]
        u8p, u16p, u32p = (ctypes.POINTER(t) for t in (ctypes.c_uint8, ctypes.c_uint16,
                                                       ctypes.c_uint32))
        ip = ctypes.POINTER(ctypes.c_int)
        lib.ring_unr_tiles.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_size_t,
                                       ctypes.c_int, ctypes.c_int, u8p, u32p]
        lib.ring_unr1_frame.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int,
                                        ctypes.c_int, u8p, u32p, ctypes.c_int, ctypes.c_int, u32p]
        lib.ring_unr2_frame.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int,
                                        ctypes.c_int, u8p, u32p, ctypes.c_int, ctypes.c_int,
                                        ctypes.c_int, u16p, u16p, u32p, ip]
        _lib = lib
    return _lib


def decode(buf: bytes, vbits: int, ibits: int, pos: int, end: int, max_codes: int):
    lib = _load()
    cap = min(max_codes, max(0, end - pos) // 2 + 1)
    out = (ctypes.c_uint16 * cap)()
    endpos = ctypes.c_uint32()
    n = lib.ring_decode(buf, len(buf), vbits, ibits, pos, end, out, cap, ctypes.byref(endpos))
    return out[:n], endpos.value


def py_dpcm(buf: bytes, pos: int, vbits: int, nsamples: int, state: list[int]):
    """Mono sound DPCM (0x47bc20): returns (samples, end bit); updates state [sample, delta]."""
    sample, delta = state
    pos += 3
    out = []
    for _ in range(nsamples):
        o = pos >> 3
        w = int.from_bytes(buf[o:o + 4].ljust(4, b"\0"), "big")
        sh = 31 - (pos & 7)
        if not (w >> sh) & 1:
            d = ((w << (32 - sh)) & 0xFFFFFFFF) >> (32 - vbits)
            if d > 0x1FF:
                d = 0x200 - d
            delta = ((d * 0x40 + 0x8000) & 0xFFFF) - 0x8000
            pos += vbits + 1
        else:
            pos += 1
        sample = ((sample + delta + 0x8000) & 0xFFFF) - 0x8000
        out.append(sample)
    state[:] = [sample, delta]
    return out, pos


def dpcm(buf: bytes, pos: int, vbits: int, nsamples: int, state: list[int]):
    lib = _load()
    out = (ctypes.c_int16 * nsamples)()
    st = (ctypes.c_int16 * 2)(*state)
    endpos = ctypes.c_uint32()
    lib.ring_dpcm(buf, len(buf), pos, vbits, nsamples, out, st, ctypes.byref(endpos))
    state[:] = [st[0], st[1]]
    return list(out), endpos.value


HBR_ERRORS = {-1: "output overflow", -2: "tile index out of range", -3: "run list overrun",
              -4: "ring reference to an unset code", -5: "back-buffer segment out of range"}


def hbr(buf: bytes, pos: int, end: int, runs: bytes, tiles, ntiles: int, ring, back, segs,
        cap: int):
    """One HBR video stream (0x42ce30). ring: ctypes u32[128] carried between calls.
    Returns (pixels as ctypes array, count) or raises ValueError with the error."""
    lib = _load()
    out = (ctypes.c_uint16 * cap)()
    t = (ctypes.c_uint16 * max(1, len(tiles)))(*tiles)
    s = (ctypes.c_uint16 * max(1, len(segs)))(*segs)
    b = back if back is not None else (ctypes.c_uint16 * 1)()
    n = lib.ring_hbr(buf, len(buf), pos, end, runs, len(runs), t, ntiles, ring, b, s,
                     len(segs), out, cap)
    if n < 0:
        raise ValueError(HBR_ERRORS[n])
    return out, n


UNR_ERRORS = {-1: "bits past the buffer", -2: "tile index out of range",
              -3: "copy from before the picture", -4: "vector the first row cannot use",
              -5: "unsupported layout"}


class Unr:
    """State of one UNR video (RING_ISO.EXE 0x42c680 / LEGEND.EXE 0x423630): the tile
    table, the picture (u32 per pixel, kept between frames) and v2's neighbour list."""

    def __init__(self, version: int, width: int, height: int, interlaced: bool):
        self.lib = _load()
        self.version, self.w, self.h, self.interlaced = version, width, height, interlaced
        self.tiles = (ctypes.c_uint8 * (4096 * 16))()
        self.out = (ctypes.c_uint32 * (width * height))()
        self.map = (ctypes.c_uint16 * (width * height // 2 + 64))()  # as the original's
        self.list = (ctypes.c_uint16 * 4)()
        self.limit = 0

    def load_tiles(self, buf: bytes, ntiles: int) -> int:
        """Decode a tile table of ntiles tiles; returns the bits used (counting the 16 raw
        bytes)."""
        end = ctypes.c_uint32()
        r = self.lib.ring_unr_tiles(self.version, buf, len(buf), ntiles, self.interlaced,
                                    self.tiles, ctypes.byref(end))
        if r < 0:
            raise ValueError("tiles: " + UNR_ERRORS[r])
        self.limit = ntiles
        return end.value

    def frame(self, buf: bytes, ntiles: int) -> tuple[int, int]:
        """Decode one picture into self.out; returns (bits used, v2's count of left-over
        neighbour list reads)."""
        end, n = ctypes.c_uint32(), ctypes.c_int()
        if self.version == 1:
            if not self.interlaced:
                raise ValueError("v1 without interlace: no file uses it")
            r = self.lib.ring_unr1_frame(buf, len(buf), ntiles, self.limit, self.tiles,
                                         self.out, self.w, self.h, ctypes.byref(end))
        else:
            r = self.lib.ring_unr2_frame(buf, len(buf), ntiles, self.limit, self.tiles,
                                         self.out, self.w, self.h, self.interlaced, self.map,
                                         self.list, ctypes.byref(end), ctypes.byref(n))
        if r < 0:
            raise ValueError("frame: " + UNR_ERRORS[r])
        return end.value, n.value


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
    for start in (0, 5):
        a, b = [0, 0], [0, 0]
        assert py_dpcm(blob, start, 10, 256, a) == dpcm(blob, start, 10, 256, b) and a == b
    print("selftest ok")


if __name__ == "__main__" and "--selftest" in sys.argv:
    selftest()
