"""Extract the zone set-up calls of RING.EXE by running each set-up function in an x86
emulator (Unicorn) with every call it makes stubbed: the calls are recorded with their
arguments as the code computed them, so loops (`sprintf("...%04d.bmp", i + 1)` then
`ObjAddPre` / `ObjPreAddImgToPuz(object, i, ...)`) come out unrolled. E-0094; the ISO and
CD editions E-0303.

A call is stubbed at the callee's first instruction: its stack purge is the callee's
`ret N` (Visual C++ `__thiscall`), else the caller's `add esp, N` / `pop ecx` after the call
(cdecl; Borland's member functions take `this` as the first stack argument and the caller
pops, sometimes a few instructions later). A cdecl call whose second argument is a format
string is `sprintf`, emulated.

DVD (`build/ring-import/RING_DVD.EXE`): writes engines/ring/notes/calls/<zone>_setup.jsonl
(rows of fn, at, callee, addr, args, purge; strings as {"str": ...}, floats as their bit
patterns, argument types per zonedecl.API).

ISO / CD (`RING_ISO.EXE`, `RING_CD.EXE`): the callees are named by aligning each zone's
calls with the DVD's (difflib on the arguments; each callee takes the DVD callee it is
matched with most often). Writes notes/calls-<edition>/<zone>_setup.jsonl in the DVD's
format, `addr` being the DVD callee's address (so zonedecl/zonetable read them) and
`exe_addr` the edition's own, and notes/calls-<edition>/diff-vs-dvd.md: the calls that
differ from the DVD's once its numbered media are renamed (notes/media-names.tsv).

    python engines/ring/tools/ringemu.py [--edition dvd|iso|cd]   # default dvd
    python engines/ring/tools/ringemu.py --selftest
"""

from __future__ import annotations

import csv
import difflib
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

import capstone
import pefile
from unicorn import UC_ARCH_X86, UC_HOOK_CODE, UC_MODE_32, Uc, UcError
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_ECX, UC_X86_REG_EIP, UC_X86_REG_ESP

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zonedecl import API, CALLS, REPO  # noqa: E402

ZONES = ["sy", "ni", "rh", "fo", "ro", "wa", "as", "n2"]
# Set-up functions, in ZONES order, as the zone set-up (DVD 0x431040, ISO 0x439780, CD
# 0x455270) calls them; convention 'vc' (Visual C++ thiscall) or 'bc' (Borland).
EDITIONS = {
    "dvd": ("RING_DVD.EXE", "vc", [0x4662A0, 0x45EB30, 0x455A50, 0x44F3E0, 0x458A90, 0x44AB00, 0x4635A0, 0x45B610]),
    "iso": ("RING_ISO.EXE", "vc", [0x46EAA0, 0x467330, 0x45E250, 0x457BE0, 0x461290, 0x453300, 0x46BDA0, 0x463E10]),
    "cd": ("RING_CD.EXE", "bc", [0x473B18, 0x469244, 0x463C20, 0x4559F0, 0x44A1E4, 0x441C10, 0x450530, 0x43BA24]),
}
APP = 0x10000000    # a fake aApplication; set-ups only pass it to the stubs
STACK_TOP = 0x0FF00000
RET_MAGIC = 0x0BADF00D
MD = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)


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


class Exe:
    def __init__(self, edition: str):
        name, self.conv, self.setups = EDITIONS[edition]
        self.pe = pefile.PE(str(REPO / "build/ring-import" / name))
        self.img = self.pe.get_memory_mapped_image()
        self.base = self.pe.OPTIONAL_HEADER.ImageBase
        self._purge: dict[int, int] = {}

    def code(self, addr: int, n: int) -> bytes:
        return self.img[addr - self.base:addr - self.base + n]

    def purge(self, addr: int) -> int:
        """The callee's `ret N` (the first `ret` of a linear sweep), 0 for cdecl."""
        if addr not in self._purge:
            p = 0
            for ins in MD.disasm(self.code(addr, 0x8000), addr):
                if ins.mnemonic == "ret":
                    p = int(ins.op_str, 0) if ins.op_str else 0
                    break
            self._purge[addr] = p
        return self._purge[addr]

    def caller_pops(self, ret: int) -> int:
        """The caller's `add esp, N` / `pop ecx` after the call (Borland may put other
        instructions first), before any other stack or control-flow instruction."""
        for ins in MD.disasm(self.code(ret, 64), ret):
            if ins.mnemonic == "add" and ins.op_str.startswith("esp, "):
                return int(ins.op_str[5:], 0) // 4
            if ins.mnemonic == "pop" and ins.op_str == "ecx":
                return 1
            if ins.mnemonic in ("push", "pop", "call", "ret") or ins.mnemonic.startswith("j") or "esp" in ins.op_str:
                return 0
        return 0


def emulate(exe: Exe, fn_addr: int) -> list[dict]:
    """Every call the function makes, in order: at, exe addr, raw stack args (`this`
    dropped), purge, and the args decoded as strings where they point at one."""
    uc = Uc(UC_ARCH_X86, UC_MODE_32)
    load(uc, exe.pe)
    rows: list[dict] = []
    pending = [False]

    def stack(n: int) -> list[int]:
        esp = uc.reg_read(UC_X86_REG_ESP)
        return list(struct.unpack(f"<{n + 1}I", bytes(uc.mem_read(esp, 4 * (n + 1)))))

    def hook(uc: Uc, address: int, size: int, user) -> None:
        if not pending[0]:
            b = bytes(uc.mem_read(address, 2))
            pending[0] = b[0] == 0xE8 or (b[0] == 0xFF and (b[1] >> 3) & 7 == 2)
            return
        pending[0] = False  # first instruction of a callee: stub it
        ret = stack(0)[0]
        purge = exe.purge(address)
        n = purge // 4 if purge else exe.caller_pops(ret)
        raw = stack(max(n, 12))[1:]
        fmt = c_string(uc, raw[1])
        if not purge and STACK_TOP - 0x100000 <= raw[0] < STACK_TOP and fmt and "%" in fmt:
            text = c_format(uc, fmt, raw[2:])  # sprintf
            uc.mem_write(raw[0], text.encode("latin-1") + b"\0")
            uc.reg_write(UC_X86_REG_EAX, len(text))
        else:
            args = raw[:n]
            if exe.conv == "bc" and args and args[0] == APP:
                args = args[1:]
            strs = [c_string(uc, a) if exe.base <= a < exe.base + len(exe.img) or
                    STACK_TOP - 0x100000 <= a < STACK_TOP else None for a in args]
            rows.append({"at": f"{ret - 5:08x}", "exe_addr": f"{address:08x}", "raw": args,
                         "strs": strs, "purge": purge})
            uc.reg_write(UC_X86_REG_EAX, 1)
        uc.reg_write(UC_X86_REG_ESP, uc.reg_read(UC_X86_REG_ESP) + 4 + purge)
        uc.reg_write(UC_X86_REG_EIP, ret)

    uc.hook_add(UC_HOOK_CODE, hook)
    esp = STACK_TOP - 0x1000
    uc.mem_write(esp, struct.pack("<II", RET_MAGIC, APP))  # Borland: `this` on the stack
    uc.reg_write(UC_X86_REG_ESP, esp)
    uc.reg_write(UC_X86_REG_ECX, APP)                       # Visual C++: `this` in ECX
    uc.emu_start(fn_addr, RET_MAGIC, count=50_000_000)
    return rows


def typed(r: dict, dvd_addr: str, callee: str, fn: str) -> dict:
    sig = API[dvd_addr][1] if dvd_addr in API else "i" * len(r["raw"])
    out: list = []
    for i, v in enumerate(r["raw"]):
        t = sig[i] if i < len(sig) else "i"
        if t == "s":
            out.append({"str": r["strs"][i]} if r["strs"][i] is not None else v)
        elif t == "b":
            out.append(v & 0xFF)
        else:
            out.append(v)
    return {"fn": fn, "at": r["at"], "callee": callee, "addr": dvd_addr, "args": out, "purge": r["purge"]}


def dvd_rows(zone: str) -> list[dict]:
    return [json.loads(line) for line in (CALLS / f"{zone}_setup.jsonl").open()]


def extract_dvd(exe: Exe, zone: str) -> list[dict]:
    fn = exe.setups[ZONES.index(zone)]
    names = {r["addr"]: r["callee"] for z in ZONES for r in dvd_rows(z)}
    return [typed(r, r["exe_addr"], names.get(r["exe_addr"], f"FUN_{r['exe_addr']}"), f"FUN_{fn:08x}")
            for r in emulate(exe, fn)]


def key(args: list, strs: list | None = None) -> tuple:
    """Arguments compared across editions: strings lower case, numbers as they are."""
    out = []
    for i, a in enumerate(args):
        if isinstance(a, dict):
            out.append((a["str"] or "").lower())
        elif strs is not None and strs[i] is not None and strs[i].isprintable() and strs[i]:
            out.append(strs[i].lower())
        else:
            out.append(a)
    return tuple(out)


def callee_map(exe: Exe, raw: dict[str, list[dict]]) -> dict[str, str]:
    """Edition callee address -> DVD callee address, by majority over aligned calls."""
    votes: dict[str, Counter] = defaultdict(Counter)
    for zone in ZONES:
        a = [key(r["args"]) for r in dvd_rows(zone)]
        b = [key(r["raw"], r["strs"]) for r in raw[zone]]
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        d = dvd_rows(zone)
        for op, i1, i2, j1, j2 in sm.get_opcodes():  # matched runs, and replaced runs of one length
            if op == "equal" or (op == "replace" and i2 - i1 == j2 - j1):
                for k in range(i2 - i1):
                    votes[raw[zone][j1 + k]["exe_addr"]][d[i1 + k]["addr"]] += 2 if op == "equal" else 1
    return {e: c.most_common(1)[0][0] for e, c in votes.items()}


def media_names() -> dict[str, str]:
    """DVD media name -> CD/ISO name (notes/media-names.tsv), with and without extension."""
    path = REPO / "engines/ring/notes/media-names.tsv"
    out: dict[str, str] = {}
    for r in csv.DictReader(path.open(encoding="utf-8"), delimiter="	"):
        if r["dvd"] and r["name"]:
            out[r["dvd"]] = r["name"]
            out.setdefault(r["dvd"].rsplit(".", 1)[0], r["name"].rsplit(".", 1)[0])
    return out


def renamed(args: list, videos: dict[str, str]) -> tuple:
    return key([{"str": videos.get(a["str"].lower(), a["str"])} if isinstance(a, dict) and a["str"] else a
                for a in args])


def show(r: dict) -> str:
    args = ", ".join(json.dumps(a["str"]) if isinstance(a, dict) else str(a) for a in r["args"])
    return f"`{r['at']}` {r['callee'].split('::')[-1]}({args})"


def extract_edition(edition: str) -> None:
    exe = Exe(edition)
    raw = {z: emulate(exe, exe.setups[i]) for i, z in enumerate(ZONES)}
    cmap = callee_map(exe, raw)
    names = {r["addr"]: r["callee"] for z in ZONES for r in dvd_rows(z)}
    out_dir = REPO / f"engines/ring/notes/calls-{edition}"
    out_dir.mkdir(exist_ok=True)
    videos = media_names()
    report = [f"# {edition.upper()} set-up calls against the DVD's (generated)", "",
              "Generated by `engines/ring/tools/ringemu.py --edition " + edition + "`. DVD media",
              "numbers renamed per `notes/media-names.tsv`; `-` DVD only, `+` this edition only.", ""]
    unmapped = sorted({r["exe_addr"] for z in ZONES for r in raw[z] if r["exe_addr"] not in cmap})
    if unmapped:
        report += ["Callees with no DVD counterpart: " + ", ".join(unmapped), ""]
    for i, zone in enumerate(ZONES):
        fn = f"FUN_{exe.setups[i]:08x}"
        rows = []
        for r in raw[zone]:
            dvd = cmap.get(r["exe_addr"])
            row = typed(r, dvd or r["exe_addr"], names.get(dvd, f"FUN_{r['exe_addr']}"), fn)
            row["exe_addr"] = r["exe_addr"]
            rows.append(row)
        with (out_dir / f"{zone}_setup.jsonl").open("w", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        d = dvd_rows(zone)
        a = [(r["addr"], renamed(r["args"], videos)) for r in d]
        b = [(r["addr"], renamed(r["args"], {})) for r in rows]
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
        report.append(f"## {zone.upper()}: {len(d)} DVD calls, {len(rows)} {edition.upper()} calls, "
                      f"{sum(max(i2 - i1, j2 - j1) for _, i1, i2, j1, j2 in ops)} differ")
        report.append("")
        for _, i1, i2, j1, j2 in ops:
            report += [f"- {show(d[k])}" for k in range(i1, i2)]
            report += [f"+ {show(rows[k])}" for k in range(j1, j2)]
            report.append("")
        print(f"{zone}: {len(rows)} calls")
    (out_dir / "diff-vs-dvd.md").write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    edition = sys.argv[sys.argv.index("--edition") + 1] if "--edition" in sys.argv else "dvd"
    if edition != "dvd":
        extract_edition(edition)
        return
    exe = Exe("dvd")
    for zone in ZONES:
        rows = extract_dvd(exe, zone)
        with (CALLS / f"{zone}_setup.jsonl").open("w", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        print(f"{zone}: {len(rows)} calls")


def selftest() -> None:
    """The DVD's extraction reproduces notes/calls/ exactly (callees, purges, arguments)."""
    exe = Exe("dvd")
    for zone in ZONES:
        old, new = dvd_rows(zone), extract_dvd(exe, zone)
        assert len(old) == len(new), (zone, len(old), len(new))
        for o, n in zip(old, new):
            assert o == n, (zone, o, n)
        print(f"{zone}: {len(new)} calls as in notes/calls/")
    # ISO: as many calls as the DVD in every zone, every callee matched; CD: SY lacks two
    # drag cursors' calls, AS has eight mode-switch calls, two callees are those helpers.
    expect = {"iso": ({}, set()), "cd": ({"sy": 285 - 3, "as": 373 + 8}, {"004190b4", "00453548"})}
    for edition, (counts, helpers) in expect.items():
        exe = Exe(edition)
        raw = {z: emulate(exe, exe.setups[i]) for i, z in enumerate(ZONES)}
        cmap = callee_map(exe, raw)
        for zone in ZONES:
            assert len(raw[zone]) == counts.get(zone, len(dvd_rows(zone))), (edition, zone, len(raw[zone]))
        assert {r["exe_addr"] for z in ZONES for r in raw[z]} - set(cmap) == helpers, edition
        print(f"{edition}: call counts and callee names as expected")
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
