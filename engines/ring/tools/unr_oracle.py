"""Check the UNR decoder (parsers/ringdec.c) against the original code: every picture of
every distinct UNR file in the corpus is decoded both ways and compared byte for byte.
E-0357.

The original decoders run in Unicorn on the EXEs in build/ring-import/ (never committed):
v1 (Ring ISO) `RING_ISO.EXE` from 0x42c6d3, inside SControl 0x42c680 after the header
and payload reads: tile table, then the picture (0x436440 for interlaced 4-pixel tiles);
v2 (Prophet) `LEGEND.EXE` 0x424240 (tile table) and 0x423630 (DecompressSeq). Their
object is a block of zeroed memory with the fields the code reads: v1 `[obj]` -> a file
object whose +0x98 is the payload, the frame header at +0x10005, the interlace byte at
+0x10004, tiles at +4; v2 the file object at +0, the streamed flag +0x54088 = 1 (so the
payload pointer is the global 0x4d11b0), the frame header at +0x54051, the interlace byte
at +0x5404c, the map pointer at +0x10008, tiles at +8. The payload is followed by zeros.

    python engines/ring/tools/unr_oracle.py [--jobs N] [--every K]
    python engines/ring/tools/unr_oracle.py --selftest     # the first 40 pictures of 3 files
"""

from __future__ import annotations

import argparse
import hashlib
import multiprocessing as mp
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "parsers"))
import cnm  # noqa: E402
from bitstream import Unr  # noqa: E402
from common import REPO, corpus, loose_files  # noqa: E402

STOP = 0x10000000
OBJ, FILEO, BUF, OUT, MAP, STK = (0x20000000, 0x21000000, 0x22000000, 0x23000000,
                                  0x24000000, 0x25000000)


def _machine(exe: str):
    import pefile
    from unicorn import UC_ARCH_X86, UC_MODE_32, Uc

    pe = pefile.PE(str(REPO / "build/ring-import" / exe))
    img = pe.get_memory_mapped_image()
    uc = Uc(UC_ARCH_X86, UC_MODE_32)
    uc.mem_map(0x400000, (len(img) + 0xfff) & ~0xfff)
    uc.mem_write(0x400000, img)
    uc.mem_map(STOP, 0x1000)
    for a, s in ((OBJ, 0x60000), (FILEO, 0x1000), (BUF, 0x200000), (OUT, 0x200000),
                 (MAP, 0x100000), (STK, 0x100000)):
        uc.mem_map(a, s)
    return uc


class Original:
    def __init__(self, version: int, w: int, h: int, interlaced: int):
        self.v, self.size = version, w * h * 4
        self.uc = uc = _machine("RING_ISO.EXE" if version == 1 else "LEGEND.EXE")
        if version == 1:
            uc.mem_write(OBJ, struct.pack("<I", FILEO))
            uc.mem_write(FILEO + 0x98, struct.pack("<I", BUF))
            uc.mem_write(OBJ + 0x10004, bytes([interlaced]))
        else:
            uc.mem_write(OBJ, struct.pack("<I", FILEO))
            uc.mem_write(OBJ + 0x54088, struct.pack("<I", 1))
            uc.mem_write(0x4d11b0, struct.pack("<I", BUF))
            uc.mem_write(OBJ + 0x10008, struct.pack("<I", MAP))
            uc.mem_write(OBJ + 0x5404c, bytes([interlaced]))

    def _call(self, fn: int, args: tuple[int, ...]) -> None:
        from unicorn.x86_const import UC_X86_REG_ECX, UC_X86_REG_ESP

        esp = STK + 0x80000
        self.uc.mem_write(esp, struct.pack(f"<I{len(args)}I", STOP, *args))
        self.uc.reg_write(UC_X86_REG_ESP, esp)
        self.uc.reg_write(UC_X86_REG_ECX, OBJ)
        self.uc.emu_start(fn, STOP)

    def tiles(self, body: bytes, ntiles: int) -> None:  # v2 'T'
        self.uc.mem_write(BUF + 0x100000, body + bytes(4096))
        self._call(0x424240, (BUF + 0x100000, 16, ntiles))

    def picture(self, hdr: bytes, payload: bytes) -> bytes:
        from unicorn.x86_const import (UC_X86_REG_EBP, UC_X86_REG_EBX, UC_X86_REG_EDI,
                                       UC_X86_REG_ESP)

        uc = self.uc
        uc.mem_write(BUF, payload + bytes(4096))
        size, off, ntiles, tsize = struct.unpack_from("<IIHH", hdr)
        if self.v == 1:
            uc.mem_write(OBJ + 0x10005, hdr)
            ebp = STK + 0x80000  # SControl's frame as at 0x42c6d3
            uc.mem_write(ebp + 4, struct.pack("<III", STOP, OUT, 0x20))
            uc.mem_write(ebp - 0x10, struct.pack("<II", OBJ, OBJ + 4))
            uc.mem_write(ebp - 4, struct.pack("<I", tsize << 2))
            uc.reg_write(UC_X86_REG_EBP, ebp)
            uc.reg_write(UC_X86_REG_ESP, ebp - 0x14 - 12)
            uc.reg_write(UC_X86_REG_EBX, OBJ)
            uc.reg_write(UC_X86_REG_EDI, tsize << 2)
            uc.emu_start(0x42c6d3, STOP)
        else:
            uc.mem_write(OBJ + 0x54051, hdr)
            if off < size:
                self._call(0x424240, (BUF + off, tsize << 2, ntiles))
            self._call(0x423630, (OUT,))
        return bytes(uc.mem_read(OUT, self.size))


def check(data: bytes, every: int = 1, limit: int = 10**9) -> tuple[int, int]:
    """(pictures compared, mismatches) for one UNR file."""
    r = cnm.parse(data)
    version = 1 if struct.unpack_from("<I", data, 0xc)[0] == 1250 else 2
    w, h, il = r["width"], r["height"], data[0x1a]
    orig, mine = Original(version, w, h, il), Unr(version, w, h, bool(il))
    n = compared = bad = 0
    for at in r["starts"]:
        t = chr(data[at])
        if t == "T":
            size, ntiles = struct.unpack_from("<IH", data, at + 1)
            body = data[at + 9:at + 9 + size]
            orig.tiles(body, ntiles)
            mine.load_tiles(body, ntiles)
        elif t in "SU":
            hdr = data[at + 1:at + 0x30]
            size, off, ntiles = struct.unpack_from("<IIH", hdr)
            body = data[at + 0x30:at + 0x30 + size]
            if off < size:
                mine.load_tiles(body[off:], ntiles)
            mine.frame(body[:off], ntiles)
            # v2 pictures build on the previous one: the original runs every frame
            if n % every == 0 or version == 2:
                ref = orig.picture(hdr, body)
                if n % every == 0:
                    compared += 1
                    bad += ref != bytes(mine.out)
            n += 1
            if n >= limit:
                break
    return compared, bad


def _job(item):
    label, data, every = item
    try:
        return (label, *check(data, every), None)
    except Exception as exc:  # noqa: BLE001
        return label, 0, 0, repr(exc)


def _items(every: int):
    seen = set()
    for label, data in corpus((".cnm", ".ci2"), (".bmp", ".tga"), (".at3",)):
        h = hashlib.md5(data).hexdigest()
        if data[:8] == cnm.UNR and h not in seen and h not in cnm.DAMAGED:
            seen.add(h)
            yield label, data, every


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--jobs", type=int, default=max(1, mp.cpu_count() - 2))
    ap.add_argument("--every", type=int, default=1, help="compare every K-th picture")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        files = [p for _, p in loose_files((".cnm", ".ci2"))]
        picks = [next(p for p in files if "iso" in str(p)),
                 next(p for p in files if p.suffix.lower() == ".ci2")]
        member = next(d for label, d in corpus((), (".tga",), (".at3",)) if d[:8] == cnm.UNR)
        for data in [p.read_bytes() for p in picks] + [member]:
            compared, bad = check(data, limit=40)
            assert compared and not bad, (compared, bad)
        print("selftest ok")
        return 0
    files = pictures = bad_files = 0
    with mp.Pool(args.jobs) as pool:
        for label, compared, bad, err in pool.imap_unordered(_job, _items(args.every), 4):
            files += 1
            pictures += compared
            if bad or err:
                bad_files += 1
                print(f"  MISMATCH {label}: {bad} pictures {err or ''}", flush=True)
    print(f"files {files}  pictures compared {pictures}  files with mismatches {bad_files}")
    return 1 if bad_files else 0


if __name__ == "__main__":
    raise SystemExit(main())
