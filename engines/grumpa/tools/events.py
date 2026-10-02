"""Corpus statistics for Grumpa's event VM (docs/spec/events.md, E-0200..).

Walks every `Scenes/Scene_*.abi` with the validated record walker `parsers/abi.py` (its byte
layout, unchanged) and captures what `abi` skips: each record's state vector (the header's EC
vector, `actor+0x11c`), and every command (CC: `when, target, opcode, arg1, arg2` + EC
conditions `id, slot, value, mode, link`) on every actor type. `Actors/global.atx` adds the
global counters / timers / flags (types 37/38/39) in their text form.

    python engines/grumpa/tools/events.py              # print the statistics cited in EVIDENCE
    python engines/grumpa/tools/events.py --selftest
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "parsers"))
import abi  # noqa: E402
import atx  # noqa: E402

CORPUS = abi.CORPUS

_cur: dict = {}          # the record being walked: {"type", "id", "nec", "state", "cmds"}


def _cc(c: abi.Cur) -> None:
    base = struct.unpack_from("<5i", c.raw(20), 0)
    n = abi._count(c, "EC-in-CC")
    conds = [struct.unpack_from("<5i", c.raw(20), 0) for _ in range(n)]
    _cur["cmds"].append((base, conds))


def _ec_vec(c: abi.Cur) -> None:
    n = abi._count(c, "EC")
    ecs = [struct.unpack_from("<5i", c.raw(20), 0) for _ in range(n)]
    if _cur["nec"] == 0:              # the first EC vector of a record = its state slots
        _cur["state"] = [e[0] for e in ecs]
        if _cur["type"] == 0x19:      # +0x170 +0x174 +0x178 +0x17c +0x180 +0x188 +0x14c +0x150
            _cur["gate"] = struct.unpack_from("<8i", c.d, c.o)
    _cur["nec"] += 1


abi.cc = _cc                          # cc_vec / t_* resolve these at call time
abi.ec_vec = _ec_vec


def walk(d: bytes) -> list[dict]:
    """[{type, id, state, cmds:[(base5, [cond5])]}] for one .abi."""
    c = abi.Cur(d)
    out = []
    while len(d) - c.o >= 8:
        t, rid = c.u32(), c.u32()
        _cur.clear()
        _cur.update(type=t, id=rid, nec=0, state=[], cmds=[], gate=None)
        abi.TYPES[t](c)
        out.append(dict(_cur))
    return out


def scenes(root: Path) -> dict[int, list[dict]]:
    res = {}
    for f in sorted(root.glob("Scenes/Scene_*.abi")):
        d = f.read_bytes()
        if struct.unpack_from("<I", d, 0)[0] == 0x03:
            continue                  # Characters.abi-style database
        res[int(re.search(r"(\d+)", f.stem).group(1))] = walk(d)
    return res


def report(root: Path) -> None:
    sc = scenes(root)
    nums = set(sc)
    ids_type = {}
    for recs in sc.values():
        for r in recs:
            ids_type[r["id"]] = r["type"]
    g = atx.parse((root / "Actors/global.atx").read_text(encoding="latin-1"))
    for b in g:
        ids_type.setdefault(int(b["fields"][0] if isinstance(b["fields"][0], str)
                                else b["fields"][0][0]), int(b["type"]))
    when = Counter()
    modes = Counter()
    links = Counter()
    cond_ids = Counter()
    ops = Counter()
    ncmd = ncond_cmd = 0
    when_self = when_other = when_bad = 0
    stateful = Counter()
    for num, recs in sc.items():
        for r in recs:
            if r["state"]:
                stateful[len(r["state"])] += 1
            for base, conds in r["cmds"]:
                ncmd += 1
                w = base[0]
                if w == -1:
                    when["-1"] += 1
                elif w == num:
                    when_self += 1
                elif w in nums:
                    when_other += 1
                else:
                    when_bad += 1
                ops[(ids_type.get(base[1], "?") if base[1] >= 0 else "all", base[2])] += 1
                if conds:
                    ncond_cmd += 1
                for e in conds:
                    modes[e[3]] += 1
                    links[e[4]] += 1
                    cond_ids["global(<600)" if e[0] < 600 else "scene(>=600)"] += 1
    print(f"{len(sc)} scene .abi, {sum(len(r) for r in sc.values())} records, {ncmd} commands")
    print(f"  when: -1 = {when['-1']}, = own scene {when_self}, = another scene {when_other}, "
          f"not a scene {when_bad}")
    print(f"  commands with conditions: {ncond_cmd}; condition modes {dict(sorted(modes.items()))}; "
          f"link field {dict(sorted(links.items()))}; ids {dict(cond_ids)}")
    print(f"  records with state slots (by slot count): {dict(sorted(stateful.items()))}")
    print("  top (target type, opcode): " + ", ".join(
        f"{t if isinstance(t, str) else hex(t)}/{o}:{n}" for (t, o), n in ops.most_common(40)))
    # view indices: a trigger's view gate (+0x174) and 185/op30 targets vs the scene's backgrounds
    over = checked = 0
    for num, recs in sc.items():
        nbg = len(list(root.glob(f"Bitmaps/{num}_*_IS.jpg")))
        views = [r["gate"][1] for r in recs if r["type"] == 0x19]
        views += [b[3] for r in recs for b, _ in r["cmds"] if b[1] == 185 and b[2] == 30]
        views = [v for v in views if v >= 0]
        if views:
            checked += 1
            over += max(views) + 1 > nbg
    print(f"  scenes using view indices: {checked}; view index + 1 > background count in {over}")
    # global.atx: counters 37, timers 38, flags 39 in their text layout
    ok = 0
    for b in g:
        try:
            parse_global(b)
            ok += 1
        except (ValueError, IndexError):
            pass
    print(f"  global.atx: {ok}/{len(g)} blocks consume every token in the 37/38/39 layout")


def _tokens(b: dict) -> list[int]:
    out = []
    for f in b["fields"]:
        out += [int(x) for x in (f if isinstance(f, list) else str(f).split())]
    return out


def parse_global(b: dict) -> dict:
    """A global.atx counter (37), timer (38) or flag (39): id, active, visible, n state values,
    the class fields (37: max, fire; 38: limit, +0x130, +0x134; 39: fire), then the commands
    (when, target, opcode, arg1, arg2, n, n * 5-int condition). Raises unless every token is used."""
    t = _tokens(b)
    p = 0

    def take(k=1):
        nonlocal p
        if p + k > len(t):
            raise IndexError("short block")
        v = t[p:p + k]
        p += k
        return v

    rid, active, visible, n = take(4)
    state = take(n)
    extra = take({37: 2, 38: 3, 39: 1}[int(b["type"])])
    cmds = []
    for _ in range(take()[0]):
        base = take(5)
        cmds.append((base, [take(5) for _ in range(take()[0])]))
    if p != len(t):
        raise ValueError(f"{len(t) - p} tokens left")
    return dict(id=rid, active=active, visible=visible, state=state, extra=extra, cmds=cmds)


def selftest() -> None:
    # one 0x24 flag record: header (id, active, visible), state [5], +300, one CC with a guard
    body = (struct.pack("<II", 0x24, 700) + struct.pack("<3i", 700, 1, 0)
            + struct.pack("<i", 1) + struct.pack("<5i", 5, 0, 0, 0, 0)
            + struct.pack("<i", 1)
            + struct.pack("<i", 1) + struct.pack("<5i", 3, 701, 2, 0, 0)
            + struct.pack("<i", 1) + struct.pack("<5i", 269, 0, 1, 0, 0))
    recs = walk(body)
    assert len(recs) == 1 and recs[0]["state"] == [5], recs
    assert recs[0]["cmds"] == [((3, 701, 2, 0, 0), [(269, 0, 1, 0, 0)])], recs
    flag = parse_global({"type": "39", "fields": "261 0 0 1 0 1 1 -1 221 66 0 0 0".split()})
    assert flag["state"] == [0] and flag["extra"] == [1], flag
    assert flag["cmds"] == [([-1, 221, 66, 0, 0], [])], flag
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", type=Path, default=CORPUS)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    selftest() if a.selftest else report(a.root)
