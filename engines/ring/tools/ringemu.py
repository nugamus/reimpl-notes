"""Extract the zone set-up calls of RING.EXE (DVD) by running each set-up function in an
x86 emulator (Unicorn) with every call it makes stubbed: the calls are recorded with their
arguments as the code computed them, so loops (`sprintf("...%04d.bmp", i + 1)` then
`ObjAddPre` / `ObjPreAddImgToPuz(object, i, ...)`) come out unrolled, and arguments the
static extractor (tools/ghidra/scripts/ring_calls.py) left as "?" are known. E-0094.

Writes engines/ring/notes/calls/<zone>_setup.jsonl in ring_calls.py's format (rows of
fn, at, callee, addr, args, purge; strings as {"str": ...}, floats as their bit patterns),
replacing it. The callee set and each callee's stack purge come from the existing files
(the static extraction), so no other code of the game runs.

    python engines/ring/tools/ringemu.py             # rewrites the eight .jsonl files
    python engines/ring/tools/ringemu.py --selftest  # checks against the static extraction
"""

from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

import pefile
from unicorn import UC_ARCH_X86, UC_HOOK_CODE, UC_MODE_32, Uc, UcError
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EIP, UC_X86_REG_ESP

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zonedecl import API, CALLS, REPO  # noqa: E402

EXE = REPO / "build/ring-import/RING_DVD.EXE"
ZONES = ["sy", "ni", "rh", "fo", "ro", "wa", "as", "n2"]
SPRINTF = 0x46F069  # cdecl sprintf (MSVC CRT)
APP = 0x10000000    # a fake aApplication; set-ups only pass it to the stubs
STACK_TOP = 0x0FF00000
RET_MAGIC = 0x0BADF00D


def load(uc: Uc, pe: pefile.PE) -> None:
    base = pe.OPTIONAL_HEADER.ImageBase
    size = (pe.OPTIONAL_HEADER.SizeOfImage + 0xFFF) & ~0xFFF
    uc.mem_map(base, size)
    uc.mem_write(base, pe.get_memory_mapped_image()[:size])
    uc.mem_map(STACK_TOP - 0x100000, 0x100000)
    uc.mem_map(APP, 0x10000)
    uc.mem_map(RET_MAGIC & ~0xFFF, 0x1000)


def c_string(uc: Uc, ptr: int) -> str | None:
    try:
        data = bytes(uc.mem_read(ptr, 256))
    except UcError:
        return None
    end = data.find(b"\0")
    if end < 0:
        return None
    return data[:end].decode("latin-1")


def c_format(uc: Uc, fmt: str, args: list[int]) -> str:
    """The `%d` / `%s` / `%0Nd` subset the set-ups use."""
    out, i = [], 0
    for m in re.finditer(r"%(0?\d*)([dsx%])|[^%]+", fmt):
        if not m.group(0).startswith("%"):
            out.append(m.group(0))
        elif m.group(2) == "%":
            out.append("%")
        else:
            v = args[i]
            i += 1
            if m.group(2) == "s":
                out.append(c_string(uc, v) or "")
            else:
                if v >= 0x80000000:
                    v -= 1 << 32
                out.append(("%" + m.group(1) + m.group(2)) % v)
    return "".join(out)


def static_rows(zone: str) -> list[dict]:
    return [json.loads(line) for line in (CALLS / f"{zone}_setup.jsonl").open()]


def emulate(pe: pefile.PE, fn_addr: int, fn_name: str, callees: dict[int, tuple[str, int]]) -> list[dict]:
    uc = Uc(UC_ARCH_X86, UC_MODE_32)
    load(uc, pe)
    rows: list[dict] = []

    def stack(n: int) -> list[int]:
        esp = uc.reg_read(UC_X86_REG_ESP)
        raw = bytes(uc.mem_read(esp, 4 * (n + 1)))
        return list(struct.unpack(f"<{n + 1}I", raw))

    def hook(uc: Uc, address: int, size: int, user) -> None:
        if address not in callees and address != SPRINTF:
            return
        name, purge = callees.get(address, ("FUN_0046f069", 0))
        key = f"{address:08x}"
        if address == SPRINTF:
            ret, buf, fmt_ptr, *rest = stack(10)
            fmt = c_string(uc, fmt_ptr) or ""
            text = c_format(uc, fmt, rest)
            uc.mem_write(buf, text.encode("latin-1") + b"\0")
            uc.reg_write(UC_X86_REG_EAX, len(text))
            uc.reg_write(UC_X86_REG_ESP, uc.reg_read(UC_X86_REG_ESP) + 4)  # cdecl: the caller pops
            uc.reg_write(UC_X86_REG_EIP, ret)
            return
        sig = API[key][1] if key in API else "i" * (purge // 4)
        ret, *args = stack(len(sig))
        out: list = []
        for v, t in zip(args, sig):
            if t == "s":
                s = c_string(uc, v)
                out.append({"str": s} if s is not None else v)
            elif t == "b":
                out.append(v & 0xFF)
            else:
                out.append(v)  # unsigned, as the static extraction writes them
        rows.append({"fn": fn_name, "at": f"{ret - 5:08x}", "callee": name, "addr": key, "args": out, "purge": purge})
        uc.reg_write(UC_X86_REG_EAX, 1)
        uc.reg_write(UC_X86_REG_ESP, uc.reg_read(UC_X86_REG_ESP) + 4 + purge)
        uc.reg_write(UC_X86_REG_EIP, ret)

    uc.hook_add(UC_HOOK_CODE, hook)
    esp = STACK_TOP - 0x1000
    uc.mem_write(esp, struct.pack("<I", RET_MAGIC))
    uc.reg_write(UC_X86_REG_ESP, esp)
    uc.reg_write(UC_X86_REG_ECX, APP)
    uc.emu_start(fn_addr, RET_MAGIC, count=50_000_000)
    return rows


def extract(zone: str, pe: pefile.PE) -> list[dict]:
    static = static_rows(zone)
    callees = {int(r["addr"], 16): (r["callee"], r["purge"]) for r in static if r["addr"] != f"{SPRINTF:08x}"}
    fn_name = static[0]["fn"]
    return emulate(pe, int(fn_name.split("_")[1], 16), fn_name, callees)


def main() -> None:
    pe = pefile.PE(str(EXE))
    for zone in ZONES:
        rows = extract(zone, pe)
        with (CALLS / f"{zone}_setup.jsonl").open("w", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print(f"{zone}: {len(rows)} calls")


def selftest() -> None:
    """Every call the static extraction resolved fully appears with the same arguments, in
    order, among the emulated calls; loops only add calls."""
    pe = pefile.PE(str(EXE))
    for zone in ZONES:
        static = [r for r in static_rows(zone) if r["addr"] != f"{SPRINTF:08x}"]
        emu = extract(zone, pe)
        i = 0
        for r in static:
            if "?" in json.dumps(r["args"]):
                continue
            while i < len(emu) and not (emu[i]["at"] == r["at"] and emu[i]["args"] == r["args"]):
                i += 1
            assert i < len(emu), (zone, r)
        print(f"{zone}: {len(static)} static, {len(emu)} emulated calls; static ones all found in order")
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
