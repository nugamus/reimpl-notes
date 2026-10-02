"""Run Grumpa's own `.abi` Serialize on a file under Unicorn and log every read (E-0400).

The type 0x03 `CFXCharacter` Serialize (`FUN_00422f80`) decompiles with broken control flow
(Q-0006), so instead of reading it we run it: the decrypted dump (`build/grumpa/Grumpa.dump.exe`,
memory layout) is mapped as is, the record's object is built by its constructor (as
`CreateActor` `FUN_0040d2f0` does) and its Serialize (vtable[1], mode 1) is called on the file
bytes. Three functions are replaced:

    FUN_004026c0  archive read(dst, n)      -> copy n bytes from the file, log (offset, n, dst)
    FUN_0047b020  operator new(n)           -> bump allocator
    FUN_00468640  operator delete(p)        -> nothing

Every read is logged with the object offset it lands in (or `heap`) and the return address
of the call, which is the field's reader in the original code.

    python engines/grumpa/tools/abiemu.py <file.abi> [--log out.tsv]
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

from unicorn import (UC_ARCH_X86, UC_HOOK_CODE, UC_HOOK_MEM_UNMAPPED, UC_MODE_32, Uc,
                     UcError)
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EIP,
                               UC_X86_REG_ESP, UC_X86_REG_FS,
                               UC_X86_REG_DS, UC_X86_REG_ES, UC_X86_REG_SS,
                               UC_X86_REG_GDTR)

REPO = Path(__file__).resolve().parents[3]
DUMP = REPO / "build/grumpa/Grumpa.dump.exe"

BASE, IMG = 0x400000, 0xcb000
STACK_TOP = 0x00200000
HEAP = 0x10000000
TEB = 0x7ffd0000
GDT = 0x7ffc0000
ARCH = 0x00300000          # the fake istream
RET_MAGIC = 0x00310000
DEVICE = 0x00320000

READ, NEW, DELETE = 0x4026c0, 0x47b020, 0x468640
# type -> (object size, constructor, offset of the object in the allocation); CreateActor
CTORS = {0x03: (0x698, 0x41c9b0, 4)}
INJECT_CUT = {0x03: {0x41df6e: 1}}   # address -> args the cut call pops


class Emu:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.heap = HEAP
        self.log: list[tuple] = []
        self.obj = 0
        self.objsize = 0
        self.cut: dict[int, int] = {}
        self.entry_esp = 0
        uc = self.uc = Uc(UC_ARCH_X86, UC_MODE_32)
        uc.mem_map(BASE, IMG)
        uc.mem_write(BASE, DUMP.read_bytes()[:IMG])
        uc.mem_map(STACK_TOP - 0x100000, 0x100000)
        uc.mem_map(HEAP, 0x4000000)
        uc.mem_map(TEB, 0x1000)
        uc.mem_map(ARCH, 0x1000)
        uc.mem_map(RET_MAGIC, 0x1000)
        uc.mem_map(DEVICE, 0x1000)
        self._fs(TEB)
        uc.mem_write(TEB, struct.pack("<I", 0xffffffff))
        # istream: [vbptr] -> {0, 0x10}; the ios sub-object (state at +4, buf at +0x28) at +0x10
        uc.mem_write(ARCH, struct.pack("<II", ARCH + 0x80, 0))
        uc.mem_write(ARCH + 0x80, struct.pack("<II", 0, 0x10))
        uc.mem_write(ARCH + 0x10 + 0x28, struct.pack("<I", ARCH + 0x100))
        uc.hook_add(UC_HOOK_CODE, self._hook, begin=BASE, end=BASE + IMG)
        uc.hook_add(UC_HOOK_MEM_UNMAPPED, self._unmapped)

    def _fs(self, base: int) -> None:
        """A flat GDT with a data segment at `base` for FS (SEH frames use fs:[0])."""
        gdt = GDT
        self.uc.mem_map(gdt, 0x1000)

        def desc(b: int, limit: int, access: int) -> bytes:
            v = (limit & 0xffff) | ((b & 0xffffff) << 16) | (access << 40)
            v |= ((limit >> 16) & 0xf) << 48 | 0xc << 52 | ((b >> 24) & 0xff) << 56
            return struct.pack("<Q", v)
        self.uc.mem_write(gdt + 8, desc(0, 0xfffff, 0x9b) + desc(0, 0xfffff, 0x93)
                          + desc(base, 0xfffff, 0x93))
        self.uc.reg_write(UC_X86_REG_GDTR, (0, gdt, 0x1000, 0))
        for reg in (UC_X86_REG_DS, UC_X86_REG_ES, UC_X86_REG_SS):
            self.uc.reg_write(reg, 2 << 3)
        self.uc.reg_write(UC_X86_REG_FS, 3 << 3)

    def u32(self, a: int) -> int:
        return struct.unpack("<I", self.uc.mem_read(a, 4))[0]

    def _ret(self, value: int, pop: int) -> None:
        esp = self.uc.reg_read(UC_X86_REG_ESP)
        ra = self.u32(esp)
        self.uc.reg_write(UC_X86_REG_EAX, value)
        self.uc.reg_write(UC_X86_REG_ESP, esp + 4 + pop)
        self.uc.reg_write(UC_X86_REG_EIP, ra)

    def _hook(self, uc: Uc, addr: int, size: int, _user) -> None:
        if addr == READ:
            esp = uc.reg_read(UC_X86_REG_ESP)
            ra, dst, n = self.u32(esp), self.u32(esp + 4), self.u32(esp + 8)
            if self.pos + n > len(self.data):
                raise EOFError(f"read {n} at {self.pos:#x} past end (caller {ra:#x})")
            uc.mem_write(dst, self.data[self.pos:self.pos + n])
            rel = dst - self.obj if 0 <= dst - self.obj < self.objsize else None
            self.log.append((self.pos, n, rel, dst, ra))
            self.pos += n
            self._ret(uc.reg_read(UC_X86_REG_ECX), 8)
        elif addr == NEW:
            n = self.u32(uc.reg_read(UC_X86_REG_ESP) + 4)
            p = self.heap
            self.heap = (self.heap + n + 15) & ~15
            uc.mem_write(p, b"\xcd" * n)
            self._ret(p, 0)
        elif addr in self.cut:
            # leave the current top-level call here (see record())
            uc.reg_write(UC_X86_REG_ESP, self.entry_esp + 4 + 4 * self.cut[addr])
            uc.reg_write(UC_X86_REG_EIP, RET_MAGIC)
        elif addr == DELETE:
            self._ret(0, 0)

    def _unmapped(self, uc: Uc, access, addr, size, value, _user) -> bool:
        esp = uc.reg_read(UC_X86_REG_ESP)
        print(f"unmapped access {access} at {addr:#x} (eip {uc.reg_read(UC_X86_REG_EIP):#x}, "
              f"[esp] {self.u32(esp):#x})", file=sys.stderr)
        return False

    def call(self, fn: int, this: int, args: list[int]) -> int:
        esp = STACK_TOP - 0x1000
        frame = struct.pack("<I", RET_MAGIC) + b"".join(struct.pack("<I", a) for a in args)
        esp -= len(frame)
        self.uc.mem_write(esp, frame)
        self.uc.reg_write(UC_X86_REG_ESP, esp)
        self.entry_esp = esp
        self.uc.reg_write(UC_X86_REG_ECX, this)
        self.uc.emu_start(fn, RET_MAGIC)
        return self.uc.reg_read(UC_X86_REG_EAX)

    def record(self) -> tuple[int, int, int]:
        """Read one record (u32 type, then the body from the id on) as CreateFromABIFile does."""
        start = self.pos
        t, rid = struct.unpack_from("<II", self.data, self.pos)
        # CreateFromABIFile reads type and id, then seeks back 4 (0x40d087: seekoff(-4, cur)),
        # so the Serialize reads the id again into +0x108
        self.pos += 4
        size, ctor, off = CTORS[t]
        block = self.heap
        self.heap += (size + 15) & ~15
        self.uc.mem_write(block, b"\xcd" * size)
        self.obj, self.objsize = block + off, size - off
        self.call(ctor, self.obj, [])
        # CreateActor then injects the render device (vtable[2], E-0104), which sizes the
        # actor's vectors; then it builds DirectDraw surfaces from 0x41df6e on, which a
        # load does not need, so the call is cut there (type 3's CFXCharacter::SetDevice)
        self.cut = INJECT_CUT.get(t, {})
        self.call(self.u32(self.u32(self.obj) + 8), self.obj, [DEVICE])
        self.cut = {}
        vt = self.u32(self.obj)
        self.call(self.u32(vt + 4), self.obj, [ARCH, 1])
        return t, rid, self.pos - start


def run(e: Emu) -> Emu:
    while len(e.data) - e.pos >= 8:
        t = struct.unpack_from("<I", e.data, e.pos)[0]
        if t not in CTORS:
            break
        t, rid, n = e.record()
        print(f"record type {t:#x} id {rid} {n} bytes at {e.pos - n:#x}")
    return e


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("abi")
    ap.add_argument("--log")
    a = ap.parse_args()
    e = Emu(Path(a.abi).read_bytes())
    try:
        run(e)
    except (UcError, EOFError) as err:
        print(f"emulation stopped at file offset {e.pos:#x}: {err}", file=sys.stderr)
    print(f"consumed {e.pos}/{len(e.data)} bytes")
    if a.log:
        with open(a.log, "w") as f:
            f.write("file_off\tn\tobj_off\tdst\tcaller\n")
            for pos, n, rel, dst, ra in e.log:
                f.write(f"{pos:#x}\t{n}\t{'' if rel is None else hex(rel)}\t{dst:#x}\t{ra:#x}\n")


if __name__ == "__main__":
    main()
