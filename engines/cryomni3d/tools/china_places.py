# /// script
# dependencies = ["capstone"]
# ///
"""China (CHINE.EXE): dump every place procedure as structured pseudo-code.

China's places are code, not data (games/china/docs/places.md, E-0700..E-0704): each
place is a cdecl procedure `int proc(int msg)` in .text 0x421f00..0x436e20:
    msg 1 -> next procedure in the global list (0 ends it); the list starts at 0x436db0
    msg 2 -> the place name (char *)
    msg 3 -> entry: reset zones, load the warp, add zones; then falls into the event part
    other -> event part: run the generic zone handler 0x41f430, then the place's own
             reaction to the clicked zone (index in [0x48f27c])

The procedures are small, loop-free MSVC 5 code. This tool executes each one
symbolically (pushes, eax/esi, flags), turns it into a graph of statement and branch
nodes, folds chains of branches into `and`/`or` conditions and rebuilds if/else from
post-dominators (E-0710). Every call is kept: known API calls are decoded, others print
as `call 0x<addr>(args)`, instructions it does not model as `asm '<text>'`.

    uv run engines/cryomni3d/tools/china_places.py            # all places, text
    uv run engines/cryomni3d/tools/china_places.py jixw111    # one place
    uv run engines/cryomni3d/tools/china_places.py --json     # statement trees
    uv run engines/cryomni3d/tools/china_places.py --md       # games/china/docs/places-logic.md
    uv run engines/cryomni3d/tools/china_places.py --selftest
"""
from __future__ import annotations

import json
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

# script API (E-0701..E-0703, E-0508, E-0804); arg kinds: r=rect ptr, s=string,
# p=procedure, f=float, v=variable index, o=object index, i=int, d=double (2 pushes)
API = {
    0x420330: ("zones_reset", ""),
    0x402D50: ("warp", "s"),
    0x403060: ("zone_goto", "ripidd"),        # type 0: off, proc, arg, alpha, beta
    0x4030A0: ("zone_type2", "ripi"),         # look
    0x403290: ("zone_take", "rip"),           # type 4: proc on click
    0x4032F0: ("zone_type6", "ri"),           # use
    0x403100: ("zone_label", "ris"),          # type 7
    0x403210: ("zone_doc", "ris"),            # type 8
    0x4031B0: ("zone_type9", "ri"),           # talk
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
    0x416C90: ("time_ms", ""),                # E-0804
    0x40EFD0: ("interface_screen", "i"),      # E-0508
}
ZONE_ADDERS = {"zone_goto": "go", "zone_type2": "look", "zone_take": "take",
               "zone_type6": "use", "zone_label": "label", "zone_doc": "doc",
               "zone_type9": "talk"}
TESTS = {"obj_is_destroyed": "destroyed", "obj_not_initial": "not_initial",
         "obj_is_cursor": "held"}
INV = {"==": "!=", "!=": "==", "<": ">=", ">=": "<", ">": "<=", "<=": ">"}
JCC = {"je": "==", "jne": "!=", "jl": "<", "jge": ">=", "jg": ">", "jle": "<="}
EXIT = "exit"


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


def imm(s: str) -> int | None:
    try:
        v = int(s, 0)
    except ValueError:
        return None
    return v - (1 << 32) if v >= 1 << 31 else v


# --- conditions: ("cmp", op, lhs, rhs) | ("bit", lhs, mask, set) | ("and"|"or", a, b)

def negate(c):
    if c[0] == "cmp":
        return ("cmp", INV[c[1]], c[2], c[3])
    if c[0] == "bit":
        return ("bit", c[1], c[2], not c[3])
    return ("or" if c[0] == "and" else "and", negate(c[1]), negate(c[2]))


# --- symbolic execution -------------------------------------------------------------

class Node:
    def __init__(self, addr: int):
        self.addr = addr
        self.stmts: list = []      # ("call", name, addr, args) | ("store", addr, size, e)
        self.term = None           # ("goto", k) | ("br", cond, then, else) | ("ret", e) | ("end",)


class Proc:
    """One procedure as a graph of Nodes keyed by (address, live state)."""

    def __init__(self, dm: "Dumper", a: int, start: int, stop: int | None, eax):
        self.dm = dm
        self.stop = stop
        self.ins = dm.insns(a)
        self.at = {x.address: i for i, x in enumerate(self.ins)}
        self.targets = {int(x.op_str, 16) for x in self.ins
                        if x.mnemonic.startswith("j") and x.op_str.startswith("0x")}
        self.nodes: dict = {}
        self.asm = 0
        self.root = self.visit(start, (), eax, None)

    def eax_live(self, a: int, depth: int = 0) -> bool:
        i = self.at.get(a)
        while i is not None and i < len(self.ins):
            x = self.ins[i]
            m, op = x.mnemonic, x.op_str
            if m == "call":
                return False
            if m in ("mov", "lea") and op.startswith("eax, ") and "eax" not in op[5:]:
                return False
            if (m, op) in (("xor", "eax, eax"), ("or", "eax, 0xffffffff")):
                return False
            if m == "jmp" and depth < 4:
                return self.eax_live(int(op, 16), depth + 1)
            if m in ("ret", "jmp") or re.search(r"\b(eax|al)\b", op):
                return True
            i += 1
        return True

    def key(self, a, pushes, eax, esi):
        return (a, tuple(pushes), eax if self.eax_live(a) else None, esi)

    def visit(self, a, pushes, eax, esi):
        k = self.key(a, pushes, eax, esi)
        if k in self.nodes:
            return k
        n = self.nodes[k] = Node(a)
        self.run(n, list(pushes), k[2], esi)
        return k

    def run(self, n: Node, pushes: list, eax, esi):
        dm = self.dm
        flags = None             # (lhs, rhs, register) or ("bit", lhs, mask)
        pend = None              # last call result not consumed yet

        def use(v):
            nonlocal pend
            if pend is not None and v is pend:
                pend = None
            return v

        def flush():
            nonlocal pend
            if pend is not None:
                n.stmts.append(pend)
                pend = None

        i = self.at[n.addr]
        first = True
        while True:
            x = self.ins[i]
            a, m, op = x.address, x.mnemonic, x.op_str
            if a == self.stop:                 # entry part: falls into the event part
                flush()
                n.term = ("end",)
                return
            if not first and a in self.targets:
                flush()
                n.term = ("goto", self.visit(a, pushes, eax, esi))
                return
            first = False
            i += 1
            if m == "nop" or op in ("esi",) and m in ("push", "pop"):
                continue                       # padding; esi save/restore (fight)
            if m == "push":
                v = imm(op)
                pushes.append(("const", v) if v is not None
                              else use(eax) if op == "eax" else ("asm", op))
            elif m == "add" and op.startswith("esp, "):
                pass                           # cdecl cleanup; args were taken at the call
            elif m == "call":
                flush()
                tgt = imm(op)
                args = tuple(reversed(pushes))
                pushes = []
                name = API.get(tgt, (None,))[0] if tgt is not None else None
                eax = pend = ("call", name or f"0x{tgt:x}" if tgt is not None else op,
                              tgt, args)
            elif m == "mov" and op == "eax, dword ptr [esp + 4]":
                eax = ("msg",)
            elif m == "mov" and op == f"eax, dword ptr [0x{ZONE_INDEX:x}]":
                eax = ("zone",)
            elif m == "mov" and re.fullmatch(r"eax, dword ptr \[0x[0-9a-f]+\]", op):
                eax = ("mem", int(op[16:-1], 16))
            elif m == "mov" and op.startswith("eax, ") and imm(op[5:]) is not None:
                eax = ("const", imm(op[5:]))
            elif (m, op) in (("xor", "eax, eax"), ("or", "eax, 0xffffffff")):
                eax = ("const", 0 if m == "xor" else -1)
            elif m == "mov" and op == "esi, eax":
                v = use(eax)
                flush()
                n.stmts.append(("let", "esi", v))
                esi = ("reg", "esi")
            elif m == "sub" and op.startswith("esi, dword ptr [0x"):
                esi = ("sub", esi, ("mem", int(op[16:-1], 16)))
            elif m == "inc" and op == "eax":
                eax = ("add", use(eax), 1)
            elif m == "or" and op.startswith("al, "):
                eax = ("bitor", use(eax), imm(op[4:]))
            elif m == "lea" and op.startswith("eax, [esp + "):
                eax = ("stackaddr", imm(op[12:-1]))
            elif m == "sete" and op == "al":
                eax = ("cond", ("cmp", "==", flags[0], flags[1]))
            elif m == "mov" and re.fullmatch(r"(dword|byte) ptr \[0x[0-9a-f]+\], .*", op):
                dst, src = op.split(", ")
                v = use(eax) if src in ("eax", "al") else ("const", imm(src))
                flush()
                ma = int(dst[dst.index("[") + 1:-1], 16)
                n.stmts.append(("store", ma, 4 if dst.startswith("dword") else 1, v))
                if ma == ZONE_INDEX and src == "eax":
                    eax = ("zone",)            # `zone = -1; if (zone == 1 ...)`
            elif m == "cmp" and op.startswith(("eax, ", "esi, ")):
                reg = op[:3]
                flags = (use(eax) if reg == "eax" else esi, imm(op[5:]), reg)
            elif m == "cmp" and op.startswith(f"dword ptr [0x{ZONE_INDEX:x}], "):
                flags = (("zone",), imm(op.split(", ")[1]), None)
            elif m == "test" and op == "eax, eax":
                flags = (use(eax), 0, "eax")
            elif m == "test" and op.startswith("al, "):
                flags = ("bit", use(eax), imm(op[4:]))
            elif m in JCC:
                rel = JCC[m]
                if flags[0] == "bit":
                    taken = ("bit", flags[1], flags[2], rel == "!=")
                else:
                    taken = ("cmp", rel, flags[0], flags[1])
                flush()
                then = self.succ(a + x.size, pushes, eax, esi, negate(taken), flags)
                els = self.succ(int(op, 16), pushes, eax, esi, taken, flags)
                n.term = ("br", negate(taken), then, els)
                return
            elif m == "jmp":
                flush()
                n.term = ("goto", self.visit(int(op, 16), pushes, eax, esi))
                return
            elif m == "ret":
                flush()
                n.term = ("ret", eax)
                return
            else:
                flush()
                self.asm += 1
                n.stmts.append(("asm", f"{m} {op}"))

    def succ(self, a, pushes, eax, esi, cond, flags):
        # constant propagation: on the path where `reg == N` holds, reg is N
        if cond[0] == "cmp" and cond[1] == "==" and flags[0] != "bit" and flags[2] == "eax":
            eax = ("const", cond[3])
        return self.visit(a, pushes, eax, esi)


# --- structuring --------------------------------------------------------------------

def succs(n: Node):
    t = n.term
    return [t[1]] if t[0] == "goto" else [t[2], t[3]] if t[0] == "br" else [EXIT]


def collapse(nodes: dict, root) -> None:
    """Fold branch chains into and/or conditions (MSVC's short-circuit layout)."""
    changed = True
    while changed:
        changed = False
        live, todo = set(), [root]
        while todo:
            k = todo.pop()
            if k != EXIT and k not in live:
                live.add(k)
                todo += succs(nodes[k])
        preds: dict = {}
        for k in live:
            for s in succs(nodes[k]):
                preds.setdefault(s, set()).add(k)

        def pure(k):
            return k != EXIT and not nodes[k].stmts and nodes[k].term[0] == "br" \
                and preds[k] == {a}

        for a in sorted(live, key=lambda k: nodes[k].addr):
            n = nodes[a]
            if n.term[0] != "br":
                continue
            _, c, t, e = n.term
            if c[0] == "cmp" and c[2][:2] == ("call", "zone_default"):
                continue                       # kept apart: "default zone handling"
            if pure(t):
                _, c2, t2, e2 = nodes[t].term
                if e2 == e:
                    n.term = ("br", ("and", c, c2), t2, e)
                elif t2 == e:
                    n.term = ("br", ("and", c, negate(c2)), e2, e)
            if n.term[2:] == (t, e) and pure(e):
                _, c2, t2, e2 = nodes[e].term
                if t2 == t:
                    n.term = ("br", ("or", c, c2), t, e2)
                elif e2 == t:
                    n.term = ("br", ("or", c, negate(c2)), t, t2)
            if n.term[2:] != (t, e):
                changed = True
                break


def postdom(nodes: dict, root):
    order, seen = [], set()

    def dfs(k):
        if k == EXIT or k in seen:
            return
        seen.add(k)
        for s in succs(nodes[k]):
            dfs(s)
        order.append(k)

    dfs(root)
    # Early returns put no constraint on where an if ends (`if (c) { ...; return 0; }`):
    # only the main return (most jumped-to) leads to EXIT, the others count as
    # post-dominated by everything (None). A node whose paths all return early has
    # no join (EXIT). MSVC shares such tails between branches (`goto x; return 0;`
    # jumps into another branch's identical tail); they count as early returns too.
    npred: dict = {}
    for k in order:
        for s in succs(nodes[k]):
            npred[s] = npred.get(s, 0) + 1
    rets = [k for k in order if nodes[k].term[0] == "end"] or [
        k for k in order if nodes[k].term[0] == "ret"]
    main = max(rets, key=lambda k: (npred.get(k, 0), nodes[k].addr))
    pd: dict = {EXIT: {EXIT}}
    for k in order:            # post-order: successors first (the graph is acyclic)
        t = nodes[k].term
        if k != main and (t[0] in ("ret", "end") or t[0] == "goto" and pd[t[1]] is None
                          or t == ("goto", main)):
            pd[k] = None       # a straight tail ending in a return: like an early return
            continue
        ss = [pd[s] for s in succs(nodes[k]) if pd[s] is not None]
        pd[k] = {k} | set.intersection(*ss) if ss else None
    ipd = {k: EXIT if pd[k] is None else max(pd[k] - {k}, key=lambda j: len(pd[j]))
           for k in order}
    return ipd, order


class Structurer:
    def __init__(self, nodes, root):
        self.graph = {k: n.term for k, n in nodes.items()}     # before folding, for checks
        collapse(nodes, root)
        self.nodes = nodes
        self.ipd, _ = postdom(nodes, root)
        self.tree = self.emit(root, EXIT)

    def emit(self, k, stop) -> list:
        out = []
        while k != stop and k != EXIT:
            n = self.nodes[k]
            out += n.stmts
            t = n.term
            if t[0] == "goto":
                k = t[1]
                continue
            if t[0] == "ret":
                out.append(("return", t[1]))
                return out
            if t[0] == "end":
                return out
            _, c, th, el = t
            j = self.ipd[k]
            if el == j and self.bare_ret(j) and c[0] == "cmp" and c[2][:2] == ("call", "zone_default"):
                # the generic handler acted: the procedure returns; the rest stays flat
                out.append(("if", negate(c), [("return", self.nodes[j].term[1])], []))
                k = th
                continue
            if j == EXIT:
                # both sides end in their own return: one side becomes the if-body,
                # the code goes on with the other (prefer a bare return, else the
                # fall-through side, which is MSVC's then-part)
                if self.bare_ret(el) and not self.bare_ret(th):
                    c, th, el = negate(c), el, th
                out.append(("if", c, self.emit(th, EXIT), []))
                k = el
                continue
            a, b = self.emit(th, j), self.emit(el, j)
            if not a:
                c, a, b = negate(c), b, a
            elif b and self.nodes[el].addr < self.nodes[th].addr:
                c, a, b = negate(c), b, a
            if a:
                out.append(("if", c, a, b))
            k = j
        return out

    def bare_ret(self, k):
        return k != EXIT and not self.nodes[k].stmts and self.nodes[k].term[0] == "ret"


# --- rendering ----------------------------------------------------------------------

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

    def arg(self, kind: str, v: int):
        """JSON value of a constant argument of the given kind."""
        if kind == "r":
            return list(struct.unpack_from("<4i", self.exe.d, self.exe.off(v)))
        if kind == "s":
            return self.exe.cstr(v) if v else None
        if kind == "p":
            return self.name(v) if v in self.ends else (None if v == 0 else hex(v))
        if kind == "f":
            return round(struct.unpack("<f", struct.pack("<i", v))[0], 4)
        if kind == "v":
            return self.var(v)
        if kind == "o":
            return self.obj(v)
        return v

    # expressions -> JSON
    def ej(self, e):
        k = e[0]
        if k == "const":
            return e[1]
        if k == "call":
            _, name, tgt, args = e
            if name == "var_get" and args and args[0][0] == "const":
                return {"var": self.var(args[0][1])}
            return {"call": name, "addr": f"0x{tgt:x}" if tgt else None,
                    "args": self.args(name, args)}
        if k in ("zone", "msg"):
            return {k: True}
        if k == "mem":
            return {"mem": f"0x{e[1]:x}"}
        if k == "reg":
            return {"reg": e[1]}
        if k == "stackaddr":
            return {"stackaddr": e[1]}
        if k == "cond":
            return {"cond": self.cj(e[1])}
        if k == "asm":
            return {"asm": e[1]}
        op = {"add": "+", "bitor": "|", "sub": "-"}[k]
        rhs = self.ej(e[2]) if isinstance(e[2], tuple) else e[2]
        return {"op": op, "lhs": self.ej(e[1]), "rhs": rhs}

    def args(self, name, args):
        kinds = API.get(next((a for a, v in API.items() if v[0] == name), None),
                        (None, "i" * len(args)))[1]
        out, i = [], 0
        for k in kinds:
            if k == "d":
                lo_hi = args[i:i + 2]
                if len(lo_hi) == 2 and all(x[0] == "const" for x in lo_hi):
                    raw = struct.pack("<ii", lo_hi[0][1], lo_hi[1][1])
                    out.append(round(struct.unpack("<d", raw)[0], 4))
                else:
                    out += [self.ej(x) for x in lo_hi]
                i += 2
                continue
            if i < len(args):
                x = args[i]
                out.append(self.arg(k, x[1]) if x[0] == "const" else self.ej(x))
            i += 1
        out += [self.ej(x) for x in args[i:]]       # more pushes than the API takes
        return out

    def cj(self, c):
        if c[0] in ("and", "or"):
            flat = []
            for s in c[1:]:
                sj = self.cj(s)
                flat += sj[c[0]] if c[0] in sj else [sj]
            return {c[0]: flat}
        if c[0] == "bit":
            return {"bit": c[2], "lhs": self.ej(c[1]), "set": c[3]}
        return {"cmp": c[1], "lhs": self.ej(c[2]), "rhs": c[3]}

    def sj(self, s):
        k = s[0]
        if k == "call":
            _, name, tgt, args = s
            return {"op": "call", "fn": name, "addr": f"0x{tgt:x}" if tgt else None,
                    "args": self.args(name, args)}
        if k == "if":
            return {"op": "if", "cond": self.cj(s[1]), "then": [self.sj(x) for x in s[2]],
                    "else": [self.sj(x) for x in s[3]]}
        if k == "return":
            return {"op": "return", "value": self.ej(s[1]) if s[1] else None}
        if k == "store":
            return {"op": "store", "addr": f"0x{s[1]:x}", "size": s[2], "value": self.ej(s[3])}
        if k == "let":
            return {"op": "let", "reg": s[1], "value": self.ej(s[2])}
        return {"op": "asm", "text": s[1]}

    def proc(self, a: int) -> dict:
        """One procedure: {name, addr, next, entry, event} (or {body} if not that shape)."""
        ins = self.insns(a)
        nxt = msg_value(ins, 1)
        out = {"name": self.name(a), "addr": f"0x{a:x}",
               "next": self.name(nxt) if nxt else None, "asm": 0}

        def tree(start, stop, eax):
            p = Proc(self, a, start, stop, eax)
            t = [self.sj(s) for s in Structurer(p.nodes, p.root).tree]
            out["asm"] += p.asm
            return t

        # msg dispatch (E-0700): `cmp eax, 3; jne event` starts the entry part
        i = next((i for i, x in enumerate(ins[:-1])
                  if x.mnemonic == "cmp" and x.op_str == "eax, 3" and ins[i + 1].mnemonic == "jne"),
                 None)
        if i is None:
            out["body"] = tree(a, None, None)
            return out
        split = int(ins[i + 1].op_str, 16)
        out["entry"] = tree(ins[i + 2].address, split, ("const", 3))
        event = tree(split, None, ("msg",))
        if event and event[-1] == {"op": "return", "value": 0}:
            event = event[:-1]
        out["event"] = event
        return out


# text notation

def ex(e) -> str:
    if isinstance(e, float):
        return f"{e:g}"
    if e is None:
        return "-"
    if isinstance(e, int):
        return str(e)
    if isinstance(e, str):
        return e
    if "var" in e:
        return e["var"]
    if "call" in e:
        if e["call"] in TESTS:
            return f"{TESTS[e['call']]}({', '.join(map(ex, e['args']))})"
        fn = e["call"] if not e["call"].startswith("0x") else "call " + e["call"]
        return f"{fn}({', '.join(map(ex, e['args']))})"
    if "zone" in e:
        return "zone"
    if "msg" in e:
        return "msg"
    if "mem" in e:
        return f"[{e['mem']}]"
    if "reg" in e:
        return e["reg"]
    if "stackaddr" in e:
        return f"&[esp+{e['stackaddr']}]"
    if "cond" in e:
        return f"({cx(e['cond'])})"
    if "asm" in e:
        return f"asm '{e['asm']}'"
    return f"{ex(e['lhs'])} {e['op']} {ex(e['rhs'])}"


def cx(c, outer: str | None = None) -> str:
    for op in ("and", "or"):
        if op in c:
            s = f" {op} ".join(cx(x, op) for x in c[op])
            return f"({s})" if outer and outer != op else s
    if "bit" in c:
        s = f"{ex(c['lhs'])} & {c['bit']}"
        return s if c["set"] else f"not ({s})"
    lhs, op, rhs = c["lhs"], c["cmp"], c["rhs"]
    boolish = isinstance(lhs, dict) and ("var" in lhs or "call" in lhs)
    if rhs == 0 and op in ("==", "!=") and boolish:
        return ("not " if op == "==" else "") + ex(lhs)
    return f"{ex(lhs)} {op} {rhs}"


def q(v) -> str:
    return "-" if v is None else str(v)


def rect(r) -> str:
    return "[%s]" % ",".join(map(str, r)) if isinstance(r, list) else ex(r)


class Text:
    def __init__(self):
        self.zone = 0          # creation index of the next zone, None once unknown

    def stmt(self, s, depth: int) -> str:
        op = s["op"]
        if op == "return":
            return "return" if s["value"] in (0, None) else f"return {ex(s['value'])}"
        if op == "store":
            dst = "zone" if s["addr"] == f"0x{ZONE_INDEX:x}" else f"[{s['addr']}]"
            return f"{dst} = {ex(s['value'])}"
        if op == "let":
            return f"{s['reg']} = {ex(s['value'])}"
        if op == "asm":
            return f"asm '{s['text']}'"
        fn, a = s["fn"], s["args"]
        if fn in ZONE_ADDERS:
            if depth or self.zone is None:
                idx, self.zone = "?", None
            else:
                idx, self.zone = str(self.zone), self.zone + 1
            t = f"zone {idx}: {ZONE_ADDERS[fn]} {rect(a[0])}"
            if len(a) > 1 and a[1] != 0:
                t += " off" if a[1] == 1 else f" flag={ex(a[1])}"
            if fn in ("zone_label", "zone_doc"):
                t += f" '{q(a[2])}'"
            elif fn in ("zone_goto", "zone_type2", "zone_take"):
                t += f" -> {a[2] or '(code)'}" if len(a) > 2 else ""
                if fn != "zone_take" and len(a) > 3 and a[3]:
                    t += f" arg {ex(a[3])}"
                if fn == "zone_goto" and len(a) > 5 and not (isinstance(a[4], (int, float)) and a[4] < 0):
                    t += f" @ {ex(a[4])}, {ex(a[5])}"
            return t + "".join(f" +{ex(x)}" for x in a[{"zone_goto": 6, "zone_type2": 4,
                                                          "zone_take": 3, "zone_label": 3,
                                                          "zone_doc": 3}.get(fn, 2):])
        if fn == "zones_reset":
            self.zone = 0 if not depth else None
            return "zones reset"
        if fn == "zone_default":
            return "default zone handling"
        simple = {"warp": "warp", "video_hns": "video", "image": "image",
                  "dialogue": "voice", "minutes_add": "note", "goto": "goto",
                  "sound_ambient": "sound queue", "sound_wait": "sound play-wait",
                  "obj_to_inventory": "to inventory", "obj_to_cursor": "to cursor",
                  "obj_destroy": "destroy", "interface_screen": "interface screen"}
        if fn in simple and len(a) <= 1:
            return f"{simple[fn]} {ex(a[0]) if a else ''}".rstrip()
        if fn == "sync_video" and len(a) == 3:
            return f"dialogue {ex(a[0])} ({ex(a[1])}, {ex(a[2])})"
        if fn == "var_set" and len(a) == 2:
            return f"set {ex(a[0])} = {ex(a[1])}"
        if fn == "set_angles" and len(a) == 2:
            return f"view {ex(a[0])}, {ex(a[1])}"
        if fn == "puzzle":
            return f"puzzle({', '.join(map(ex, a))})"
        if fn in ("zone_enable", "zone_disable"):
            return f"{fn[5:]} zone {', '.join(map(ex, a))}"
        if fn in ("sound_stop", "screen_effect"):
            return fn.replace("_", " ")
        name = fn if not fn.startswith("0x") else "call " + fn
        return f"{name}({', '.join(map(ex, a))})"

    def block(self, stmts, depth: int) -> list[str]:
        pad = "  " * (depth + 1)
        lines: list[str] = []
        i = 0
        while i < len(stmts):
            s = stmts[i]
            # zone enable/disable runs: "enable zones 1, 2"
            if s["op"] == "call" and s["fn"] in ("zone_enable", "zone_disable"):
                j = i
                while j < len(stmts) and stmts[j]["op"] == "call" and stmts[j]["fn"] == s["fn"]:
                    j += 1
                ids = [ex(x["args"][0]) if x["args"] else "?" for x in stmts[i:j]]
                lines.append(f"{pad}{s['fn'][5:]} zone{'s' if j - i > 1 else ''} {', '.join(ids)}")
                i = j
                continue
            if s["op"] == "if":
                lines += self.cond_block(s, depth, "if")
            else:
                lines.append(pad + self.stmt(s, depth))
            i += 1
        return lines

    def cond_block(self, s, depth, kw) -> list[str]:
        pad = "  " * (depth + 1)
        c = s["cond"]
        if c == {"cmp": "!=", "lhs": {"call": "zone_default", "addr": "0x41f430", "args": []},
                 "rhs": 0} and s["then"] == [{"op": "return", "value": 0}] and not s["else"]:
            return [f"{pad}default zone handling (return if it acted)"]
        head = f"on zone {c['rhs']}" if kw == "if" and c.get("cmp") == "==" and \
            c.get("lhs") == {"zone": True} and not s["else"] else f"{kw} {cx(c)}"
        body = self.block(s["then"], depth + 1)
        if len(body) == 1 and not s["else"] and len(head) + len(body[0].strip()) < 100:
            out = [f"{pad}{head}: {body[0].strip()}"]
        else:
            out = [f"{pad}{head}:"] + body
        e = s["else"]
        if len(e) == 1 and e[0]["op"] == "if":
            out += self.cond_block(e[0], depth, "elif")
        elif e:
            out += [f"{pad}else:"] + self.block(e, depth + 1)
        return out


def text(p: dict) -> str:
    lines = [f"{p['name']}  ({p['addr']}, next {p['next'] or '-'})"]
    t = Text()
    for part in ("entry", "event", "body"):
        if part in p:
            lines.append(f"{part}:")
            lines += t.block(p[part], 0) or ["  (nothing)"]
    return "\n".join(lines)


def walk_json(v):
    if isinstance(v, dict):
        yield v
        for x in v.values():
            yield from walk_json(x)
    elif isinstance(v, list):
        for x in v:
            yield from walk_json(x)


def unknown_calls(p: dict) -> list[str]:
    return sorted({x.get("fn") or x.get("call") for x in walk_json(p)
                   if (x.get("op") == "call" and x["fn"].startswith("0x"))
                   or str(x.get("call", "")).startswith("0x")})


def stats(procs: list[dict]) -> dict:
    return {"procedures": len(procs),
            "not_entry_event_shape": sum("body" in p for p in procs),
            "asm_statements": sum(p["asm"] for p in procs),
            "with_unknown_calls": sum(bool(unknown_calls(p)) for p in procs),
            "unknown_calls": sorted({c for p in procs for c in unknown_calls(p)})}


def markdown(procs: list[dict]) -> str:
    st = stats(procs)
    head = f"""# China: the logic of every place procedure (generated)

Generated by `engines/cryomni3d/tools/china_places.py` from `CHINE.EXE` (E-0710..E-0712);
do not edit by hand. Regenerate with

    uv run engines/cryomni3d/tools/china_places.py --md > games/china/docs/places-logic.md

How to read it: `games/china/docs/places.md` explains places, zones and the API.
`entry:` runs once on arrival (msg 3) and then falls into `event:` (every frame).
`zone n:` lines add zones in creation order (the index `on zone n` refers to; `off` =
created disabled; `-> (code)` = no target, the place's code reacts; `@ a, b` = arrival
angles). `default zone handling` is the generic handler 0x41f430: when it acted (a zone
with a target was clicked) the procedure returns. `zone` is the clicked zone's index
(0x48f27c, -1 = none). Conditions use variable names (a bare name = non-zero, `not` =
zero), `held(o)` / `destroyed(o)` / `not_initial(o)` for object states, `puzzle(n, m)` for
a puzzle's result. Calls the dumper does not know print as `call 0x<addr>(args)`;
instructions it does not model print as `asm '<text>'`. Where the compiler shared one
tail of code between branches (or chose a call argument by a jump), the tail is printed
in each branch; a zone created under a condition prints as `zone ?` (as do the zones
after it, whose index then depends on the condition).

{st['procedures']} procedures, in list order; {st['procedures'] - st['with_unknown_calls']}
without unknown calls; unknown callees: {', '.join(st['unknown_calls']) or 'none'};
{st['asm_statements']} unmodelled instructions; {st['not_entry_event_shape']} procedures
not of the entry/event shape.
"""
    parts = [head]
    for p in procs:
        parts.append(f"## {p['name']}\n\n```\n{text(p)}\n```\n")
    return "\n".join(parts)


# --- check: the structured tree does what the instruction graph does ------------------

def leaves(c):
    if c[0] in ("and", "or"):
        yield from leaves(c[1])
        yield from leaves(c[2])
    else:
        yield c


def holds(c, val) -> bool:
    if c[0] == "and":
        return holds(c[1], val) and holds(c[2], val)
    if c[0] == "or":
        return holds(c[1], val) or holds(c[2], val)
    if c[0] == "bit":
        return bool(val[c[1]] & c[2]) == c[3]
    v, r = val[c[2]], c[3]
    return {"==": v == r, "!=": v != r, "<": v < r, ">=": v >= r, ">": v > r,
            "<=": v <= r}[c[1]]


def run_graph(nodes, graph, k, val) -> list:
    out = []
    while k != EXIT:
        out += nodes[k].stmts
        t = graph[k]
        if t[0] == "goto":
            k = t[1]
        elif t[0] == "br":
            k = t[2] if holds(t[1], val) else t[3]
        else:
            if t[0] == "ret":
                out.append(("return", t[1]))
            return out
    return out


def run_tree(tree, val, out) -> bool:
    for s in tree:
        if s[0] == "if":
            if run_tree(s[2] if holds(s[1], val) else s[3], val, out):
                return True
        else:
            out.append(s)
            if s[0] == "return":
                return True
    return False


def check_structure(dm: "Dumper", a: int, runs: int = 300) -> int:
    """Give every tested value random contents (0, 1, the compared constant +-1, bit
    masks) and compare the statements met by walking the instruction graph and the
    structured tree. Returns the number of runs."""
    import random
    rnd = random.Random(a)
    ins = dm.insns(a)
    i = next(i for i, x in enumerate(ins[:-1]) if x.op_str == "eax, 3" and x.mnemonic == "cmp")
    split = int(ins[i + 1].op_str, 16)
    n = 0
    for start, stop, eax in ((ins[i + 2].address, split, ("const", 3)), (split, None, ("msg",))):
        p = Proc(dm, a, start, stop, eax)
        st = Structurer(p.nodes, p.root)
        cands: dict = {}
        for t in st.graph.values():
            if t[0] == "br":
                for c in leaves(t[1]):
                    lhs, r = (c[1], c[2]) if c[0] == "bit" else (c[2], c[3])
                    cands.setdefault(lhs, {0, 1}).update({r, r - 1, r + 1, 15, -1})
        for _ in range(runs):
            val = {k: rnd.choice(sorted(v)) for k, v in cands.items()}
            want = run_graph(p.nodes, st.graph, p.root, val)
            got: list = []
            run_tree(st.tree, val, got)
            if stop is None and want[-1:] == [("return", ("const", 0))] and got[-1:] != want[-1:]:
                got.append(want[-1])
            assert got == want, (dm.name(a), val, want, got)
            n += 1
    return n


def selftest(dm: Dumper) -> None:
    order = dm.walk()
    assert order[0] == LIST_HEAD and dm.name(LIST_HEAD) == "Script_Start", dm.name(LIST_HEAD)
    assert len(order) == len(dm.ends) == 270, (len(order), len(dm.ends))
    out = text(dm.proc(0x423210))
    assert "warp jixw111" in out and "[290,1982,460,2047]" in out, out
    # pne140, the worked example of places.md (E-0705)
    p = dm.proc(0x431050)
    out = text(p)
    assert p["next"] == "pne130" and "body" not in p, p.keys()
    for want in (
        "  zone 0: go [277,974,439,1084] -> pne150",
        "  zone 1: talk [381,1483,512,1517] off",
        "  zone 3: go [244,1471,475,1612] off -> (code) @ 0, 0",
        "  zone 7: label [358,1702,454,1756] 'lion_pne'",
        "  warp pne140",
        "  if MODE_VISITE == 1: enable zone 3",
        "  default zone handling (return if it acted)",
        "  if (CHAPITRE == 1 and not XNED1011 and not GICD1011 and not GIDD1011) or "
        "(CHAPITRE == 9 and ENED3111 == 1 and not GICD3111 and not GIDD3111):",
        "    enable zones 1, 2",
        "  on zone 1:",
        "    if CHAPITRE == 1 and not XNED1011 and not GICD1011 and not GIDD1011:",
        "      dialogue GICD1011 (D140gia, D140ANJ)",
        "      set GICD1011 = 1",
        "      disable zones 1, 2",
        "      note MINAO311",
        "      dialogue GIDD3111 (D140gib, D140ANJ)",
        "  on zone 3:",
        "    view 1.58, 0",
        "    if MODE_VISITE == 1: goto pne210",
    ):
        assert want in out.split("\n"), (want, out)
    assert out.count("disable zones 1, 2") == 4, out
    procs = [dm.proc(a) for a in order]
    st = stats(procs)
    assert st["not_entry_event_shape"] == 0, st
    assert st["asm_statements"] == 0, st
    runs = sum(check_structure(dm, a) for a in order)
    print(f"selftest ok: 270 procedures, list covers all of them; pne140 matches the "
          f"worked example; structure = instruction graph in {runs} random runs; {st}")


def main(argv: list[str]) -> int:
    dm = Dumper(EXE.read_bytes())
    if "--selftest" in argv:
        selftest(dm)
        return 0
    order = dm.walk()
    want = {a.lower() for a in argv if not a.startswith("--")}
    procs = [dm.proc(a) for a in order if not want or dm.name(a).lower() in want]
    if "--json" in argv:
        json.dump(procs, sys.stdout, indent=1)
        print()
    elif "--md" in argv:
        sys.stdout.reconfigure(newline="\n")
        print(markdown(procs), end="")
    else:
        for p in procs:
            print(text(p))
            print()
    print(f"# {stats(procs)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
