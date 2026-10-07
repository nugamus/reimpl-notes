# /// script
# dependencies = ["capstone"]
# ///
"""China (CHINE.EXE): dump every place script with its warp, zones and event calls.

China's places are code, not data (games/china/docs/places.md, E-0700..E-0704): each
place is a cdecl procedure `int proc(int msg)` in .text 0x421f00..0x436e20:
    msg 1 -> next procedure in the global list (0 ends it); the list starts at 0x436db0
    msg 2 -> the place name (char *)
    msg 3 -> entry: reset zones, load the warp, add zones; then falls into the event part
    other -> event part: run the generic zone handler 0x41f430, then the place's own
             reaction to the clicked zone (index in [0x48f27c])
This tool walks the list from Script_Start and prints, per procedure, the API calls of
the entry and event parts with their pushed arguments decoded (strings, rects, floats,
procedure names, variable and object names).

    uv run engines/cryomni3d/tools/china_places.py            # all places
    uv run engines/cryomni3d/tools/china_places.py jixw111    # one place
    uv run engines/cryomni3d/tools/china_places.py --selftest
"""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[3]
EXE = ROOT / "games/china/discs/en-iso/cd1/CHINE/CHINE.EXE"

LIST_HEAD = 0x436DB0
HOLE = (0x421E80, 0x436E20)
VARS = 0x45EEC4      # {char *name; int value; int id} x 220
OBJS = 0x45D5C0      # object idx -> 48-byte record, name at +4, state at +0x24
ZONE_INDEX = 0x48F27C

# script API (E-0701..E-0703); arg kinds: r=rect ptr, s=string, p=procedure, f=float,
# v=variable index, o=object index, i=int
API = {
    0x420330: ("zones_reset", ""),
    0x402D50: ("warp", "s"),
    0x403060: ("zone_goto", "ripidd"),        # type 0: proc, arg4, two doubles (angles)
    0x4030A0: ("zone_type2", "ripi"),
    0x403290: ("zone_take", "rip"),           # type 4: proc on click
    0x4032F0: ("zone_type6", "ri"),
    0x403100: ("zone_label", "ris"),          # type 7
    0x403210: ("zone_doc", "ris"),            # type 8
    0x4031B0: ("zone_type9", "ri"),
    0x403590: ("zone_enable", "i"),
    0x4035D0: ("zone_disable", "i"),
    0x402CF0: ("video_hns", "s"),
    0x402E20: ("image", "s"),
    0x403350: ("dialogue", "s"),
    0x403380: ("sync_video", "sss"),
    0x4033C0: ("var_set", "vi"),
    0x403580: ("var_get", "v"),
    0x4033E0: ("obj_is_destroyed", "o"),
    0x403400: ("obj_not_initial", "o"),
    0x403420: ("obj_is_cursor", "o"),
    0x403440: ("obj_to_inventory", "o"),
    0x403480: ("obj_to_cursor", "o"),
    0x4034F0: ("obj_destroy", "o"),
    0x4035F0: ("puzzle", "ii"),
    0x4037E0: ("sound_ambient", "s"),
    0x4039A0: ("sound_wait", "s"),
    0x4039F0: ("sound_stop", ""),
    0x403860: ("screen_effect", ""),
    0x403A10: ("set_angles", "ff"),
    0x411D80: ("minutes_add", "s"),
    0x41F190: ("goto", "p"),
    0x41F430: ("zone_default", ""),
}


class Exe:
    def __init__(self, data: bytes):
        self.d = data

    def off(self, va: int) -> int:
        if 0x401000 <= va < 0x450000:
            return va - 0x401000 + 0x400
        if 0x452000 <= va < 0x48C000:
            return va - 0x452000 + 0x50A00
        raise ValueError(hex(va))

    def u32(self, va: int) -> int:
        return struct.unpack_from("<I", self.d, self.off(va))[0]

    def cstr(self, va: int) -> str | None:
        try:
            o = self.off(va)
        except ValueError:
            return None
        m = re.match(rb"[\x20-\x7e]*\x00", self.d[o:o + 128])
        return m.group()[:-1].decode() if m else None


def proc_starts(exe: Exe) -> list[int]:
    out = []
    for a in range(HOLE[0], HOLE[1], 16):
        o = exe.off(a)
        if exe.d[o - 1] in (0x90, 0xC3) and exe.d[o:o + 4] == b"\x8b\x44\x24\x04":
            out.append(a)
    return out


def msg_value(insns, msg: int) -> int | None:
    for i, ins in enumerate(insns[:-2]):
        if ins.mnemonic == "cmp" and ins.op_str == f"eax, {msg}":
            nxt = insns[i + 2]
            if nxt.mnemonic == "mov" and nxt.op_str.startswith("eax, 0x"):
                return int(nxt.op_str[5:], 16)
            if nxt.mnemonic == "xor":
                return 0
    return None


class Dumper:
    def __init__(self, data: bytes):
        self.exe = Exe(data)
        self.md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        starts = proc_starts(self.exe)
        self.ends = dict(zip(starts, starts[1:] + [HOLE[1]]))
        self.names: dict[int, str] = {}

    def insns(self, a: int):
        o = self.exe.off(a)
        return list(self.md.disasm(self.exe.d[o:o + self.ends[a] - a], a))

    def name(self, a: int) -> str:
        if a not in self.names:
            v = msg_value(self.insns(a), 2) if a in self.ends else None
            self.names[a] = (self.exe.cstr(v) if v else None) or f"proc_{a:x}"
        return self.names[a]

    def walk(self) -> list[int]:
        seen, a = [], LIST_HEAD
        while a and a not in seen and a in self.ends:
            seen.append(a)
            a = msg_value(self.insns(a), 1) or 0
        return seen

    def var(self, i: int) -> str:
        p = self.exe.u32(VARS + 12 * i)
        return self.exe.cstr(p) or f"var{i}"

    def obj(self, i: int) -> str:
        try:
            return self.exe.cstr(self.exe.u32(OBJS + 48 * i + 4)) or f"obj{i}"
        except ValueError:
            return f"obj{i}"

    def arg(self, kind: str, v):
        if v is None:
            return "?"
        if kind == "r":
            return "[%d,%d,%d,%d]" % struct.unpack_from("<4I", self.exe.d, self.exe.off(v))
        if kind == "s":
            return repr(self.exe.cstr(v)) if v else "0"
        if kind == "p":
            return self.name(v) if v in self.ends else ("0" if v == 0 else hex(v))
        if kind == "f":
            return "%.3g" % struct.unpack("<f", struct.pack("<I", v))[0]
        if kind == "v":
            return self.var(v)
        if kind == "o":
            return self.obj(v)
        return str(v)

    @staticmethod
    def dbl(lo_hi) -> str:
        return "%.3g" % struct.unpack("<d", struct.pack("<II", *lo_hi))[0]

    def calls(self, insns):
        """Yield (address, text) for API calls, zone tests and variable tests."""
        pushes: list = []
        last_load = None
        for ins in insns:
            m, op = ins.mnemonic, ins.op_str
            if m == "push":
                pushes.append(int(op, 16) if op.startswith("0x") or op.isdigit() else None)
            elif m == "call" and op.startswith("0x"):
                tgt = int(op, 16)
                name, kinds = API.get(tgt, (f"call_{tgt:x}", ""))
                args = list(reversed(pushes))
                vals, i = [], 0
                for k in kinds:
                    if k == "d":
                        lo_hi = args[i:i + 2]
                        vals.append(self.dbl(lo_hi) if len(lo_hi) == 2 and None not in lo_hi else "?")
                        i += 2
                    else:
                        vals.append(self.arg(k, args[i] if i < len(args) else None))
                        i += 1
                txt = ", ".join(vals)
                yield ins.address, f"{name}({txt})"
                pushes = []
                last_load = name if name in ("var_get", "obj_is_destroyed", "obj_not_initial",
                                             "obj_is_cursor") else None
            elif m == "mov" and op.endswith(f"dword ptr [0x{ZONE_INDEX:x}]"):
                last_load = "zone"
            elif m == "cmp" and last_load == "zone" and re.match(r"e[a-d]x, (0x)?[0-9a-f]+$", op):
                yield ins.address, f"  zone == {int(op.split(', ')[1], 0)} ?"
            elif m == "test" and last_load == "zone" and op in ("eax, eax", "ecx, ecx", "edx, edx"):
                yield ins.address, "  zone == 0 ?"
            elif m == "ret":
                pushes = []

    def dump(self, a: int) -> str:
        ins = self.insns(a)
        nxt = msg_value(ins, 1)
        lines = [f"## {self.name(a)}  (0x{a:x}, next {self.name(nxt) if nxt else '-'})"]
        # entry part starts after `cmp eax, 3; jne X`; event part starts at X
        split = next((int(ins[i + 1].op_str, 16) for i, x in enumerate(ins[:-1])
                      if x.mnemonic == "cmp" and x.op_str == "eax, 3"), None)
        entry = [x for x in ins if split and x.address < split]
        event = [x for x in ins if split and x.address >= split] if split else ins
        lines.append("entry:")
        lines += [f"  {t}" for _, t in self.calls(entry)]
        lines.append("event:")
        lines += [f"  {t}" for _, t in self.calls(event)]
        return "\n".join(lines)


def selftest(dm: Dumper) -> None:
    order = dm.walk()
    assert order[0] == LIST_HEAD and dm.name(LIST_HEAD) == "Script_Start", dm.name(LIST_HEAD)
    assert len(order) == len(dm.ends) == 270, (len(order), len(dm.ends))
    out = dm.dump(0x423210)
    assert "warp('jixw111')" in out and "[290,1982,460,2047]" in out, out
    print("selftest ok: 270 procedures, list covers all of them")


def main(argv: list[str]) -> int:
    dm = Dumper(EXE.read_bytes())
    if "--selftest" in argv:
        selftest(dm)
        return 0
    order = dm.walk()
    want = {a.lower() for a in argv}
    for a in order:
        if not want or dm.name(a).lower() in want:
            print(dm.dump(a))
            print()
    missing = set(dm.ends) - set(order)
    print(f"# {len(order)} procedures in the list, {len(missing)} not in it", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
