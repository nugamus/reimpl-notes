"""Dump Grumpa's game logic, one block per scene, for the walkthrough (games/grumpa/docs/walkthrough.md).

Walks every `Scenes/Scene_*.abi` with the validated `parsers/abi.py` (its byte layout, unchanged)
and captures what it skips: each record's names (the `pstr` strings: sprite frames, mesh, wav),
its state slots, the trigger gate words, and every command list (CC vectors, in order). Adds the
`.scn` scene links (exits, entries), the characters of `Actors/Characters.abi` and the globals
of `Actors/global.atx`. Commands print as `when:target.op(a1,a2) if cond`, a target or
condition id labelled by its record (`g269 Snake Dead`, `i120 IO_rope`, `c10 grumpa`).

    python engines/grumpa/tools/logic.py > engines/grumpa/notes/logic.txt
    python engines/grumpa/tools/logic.py 61           # one scene
    python engines/grumpa/tools/logic.py --selftest
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
import scn  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
import events  # noqa: E402  (parse_global)

CORPUS = abi.CORPUS
KIND = {0x03: "char", 0x05: "item", 0x07: "x07", 0x0d: "sprite", 0x11: "light", 0x18: "sound",
        0x2a: "sound", 0x19: "trig", 0x1a: "mesh", 0x1d: "x1d", 0x1e: "x1e", 0x20: "x20",
        0x21: "script", 0x22: "counter", 0x25: "counter", 0x23: "timer", 0x26: "timer",
        0x24: "flag", 0x27: "flag"}
OPS = {(185, 31): "GOTO", (185, 30): "VIEW", (600, 6): "OPENWALL", (600, 5): "CLOSEWALL"}

_cur: dict = {}
_orig_pstr = abi.pstr


def _pstr(c: abi.Cur) -> None:
    o = c.o
    _orig_pstr(c)
    n = struct.unpack_from("<i", c.d, o)[0]
    if n > 1 and "names" in _cur:
        _cur["names"].append(c.d[o + 4:o + 4 + n].rstrip(b"\0").decode("latin-1"))


def _cc(c: abi.Cur) -> None:
    base = struct.unpack_from("<5i", c.raw(20), 0)
    conds = [struct.unpack_from("<5i", c.raw(20), 0) for _ in range(abi._count(c, "EC-in-CC"))]
    _cur["lists"][-1].append((base, conds))


def _cc_vec(c: abi.Cur) -> None:
    _cur["lists"].append([])
    for _ in range(abi._count(c, "CC")):
        _cc(c)


def _ec_vec(c: abi.Cur) -> None:
    n = abi._count(c, "EC")
    ecs = [struct.unpack_from("<5i", c.raw(20), 0) for _ in range(n)]
    if _cur["nec"] == 0:
        _cur["state"] = [e[0] for e in ecs]
        if _cur["type"] == 0x19:     # +0x170 once, +0x174 view, +0x178 click, +0x17c prox, +0x180 conds
            _cur["gate"] = struct.unpack_from("<8i", c.d, c.o)
    elif _cur["type"] == 0x19 and _cur["nec"] == 1:
        _cur["conds"] = ecs          # +0x194: the trigger's own conditions
    _cur["nec"] += 1


abi.pstr, abi.cc, abi.cc_vec, abi.ec_vec = _pstr, _cc, _cc_vec, _ec_vec


def _t19(c: abi.Cur) -> None:
    """abi.t_19's layout, capturing the click polygon (screen) and the proximity sphere."""
    _cur["active"] = struct.unpack_from("<3i", c.raw(12), 0)[1]
    abi.ec_vec(c); c.raw(32); c.raw(76)
    abi.sub_456d70(c); abi.ec_vec(c); abi.cc_vec(c)
    k = struct.unpack_from("<i", c.raw(4), 0)[0]
    pts = struct.unpack_from("<%df" % (2 * k), c.raw(8 * k), 0) if k > 0 else ()
    _cur["poly"] = list(zip(pts[0::2], pts[1::2]))
    _cur["sphere"] = struct.unpack_from("<4f", c.raw(16), 0)
    c.raw(4)
    if c.u32() == 2:
        for _ in range(abi._count(c, "bubble")):
            c.raw(8)
            if c.u32() != 0:
                abi.pstr(c)


abi.TYPES[0x19] = _t19


def walk(d: bytes) -> list[dict]:
    c = abi.Cur(d)
    out = []
    while len(d) - c.o >= 8:
        t, rid = c.u32(), c.u32()
        _cur.clear()
        _cur.update(type=t, id=rid, nec=0, state=[], lists=[], names=[], gate=None, conds=[])
        abi.TYPES[t](c)
        out.append(dict(_cur))
    return out


def labels(root: Path) -> dict[int, str]:
    lab = {3: "player", 4: "actor4", 8: "hud", 90: "inv", 180: "amb", 185: "fade", 186: "proxy"}
    for r in walk((root / "Actors/Items.abi").read_bytes()):
        lab[r["id"]] = "i%d %s" % (r["id"], (r["names"] or ["?"])[0].replace(".ANB", "").replace(".anb", ""))
    for r in walk((root / "Actors/Characters.abi").read_bytes()):
        nm = (r["names"] or ["?"])[0].rsplit(".", 1)[0]
        lab[r["id"]] = "c%d %s" % (r["id"], nm)
    for b in atx.parse((root / "Actors/global.atx").read_text(encoding="latin-1")):
        hdr = b.get("name") or b.get("title") or ""
        g = events.parse_global(b)
        lab[g["id"]] = "g%d %s" % (g["id"], hdr)
    return lab


def fmt_cond(e, lab) -> str:
    i, slot, val, mode, link = e
    s = "%s[%d]%s%d" % (lab.get(i, str(i)), slot, ["==", ">", "<", "!="][mode] if 0 <= mode < 4 else "?%d" % mode, val)
    return s + (" |" if link == 1 else "")


def fmt_cmd(base, conds, lab) -> str:
    w, t, op, a1, a2 = base
    tn = "ALL" if t == -1 else lab.get(t, str(t))
    s = "%s%s.%s(%d,%d)" % ("" if w == -1 else "@%d " % w, tn, OPS.get((t, op), op), a1, a2)
    if conds:
        s += " if " + " & ".join(fmt_cond(e, lab) for e in conds)
    return s


def dump_records(recs, lab, out, prefix="") -> None:
    for r in recs:
        k = KIND.get(r["type"], hex(r["type"]))
        head = "%s%s %d %s" % (prefix, k, r["id"], " ".join(r["names"][:2]))
        if r["state"] and r["state"] != [0]:
            head += " state=%s" % r["state"]
        if r["gate"]:
            g = r["gate"]
            head += "%s view=%d %s%s%s" % ("" if r["active"] else " OFF", g[1], "click" if g[2] == 1 else "walkin",
                                         " prox" if g[3] == 1 else "", " once" if g[0] == 1 else "")
            if r.get("poly"):
                xs, ys = zip(*r["poly"])
                head += " at(%d,%d)" % (round(sum(xs) / len(xs)), round(sum(ys) / len(ys)))
            head += " sph(%.0f,%.0f,%.0f r%.0f)" % r["sphere"]
            if r["conds"] and g[4] == 1:
                head += " IF " + " & ".join(fmt_cond(e, lab) for e in r["conds"])
        out.append(head)
        for n, lst in enumerate(r["lists"]):
            for base, conds in lst:
                out.append("    L%d %s" % (n, fmt_cmd(base, conds, lab)))


def scene_block(root: Path, num: int, lab: dict) -> list[str]:
    out = ["== Scene %d" % num]
    sp = root / ("Scenes/Scene_%03d.scn" % num)
    if sp.exists():
        r = scn.parse(sp.read_bytes())
        links = r.get(0x14, {})
        if links.get("exits"):
            out.append("  exits: " + ", ".join("->%d@(%.0f,%.0f,%.0f r%.0f)" % (e[4], *e[:4]) for e in links["exits"]))
        special = Counter(t for t in r[0x08]["unk_face"] if t > 4)
        if special:                  # floor types: 12/13 water, 15 platform, 19..21 closed walls
            out.append("  floor types: " + ", ".join("%d x%d" % kv for kv in sorted(special.items())))
        if links.get("entries"):
            out.append("  entries from: " + ", ".join(str(e[6]) for e in links["entries"]))
    recs = walk((root / ("Scenes/Scene_%03d.abi" % num)).read_bytes())
    local = {r["id"]: "%s%d %s" % (KIND.get(r["type"], "?")[0:2], r["id"], (r["names"] or [""])[0][:24])
             for r in recs}
    dump_records(recs, {**lab, **local}, out, "  ")
    return out


def scene_nums(root: Path) -> list[int]:
    return sorted(int(re.search(r"(\d+)", f.stem).group(1)) for f in root.glob("Scenes/Scene_*.abi")
                  if struct.unpack_from("<I", f.read_bytes(), 0)[0] != 0x03)


def selftest() -> None:
    body = (struct.pack("<II", 0x24, 700) + struct.pack("<3i", 700, 1, 0)
            + struct.pack("<i", 1) + struct.pack("<5i", 5, 0, 0, 0, 0) + struct.pack("<i", 1)
            + struct.pack("<i", 1) + struct.pack("<5i", 3, 185, 31, 12, 0)
            + struct.pack("<i", 1) + struct.pack("<5i", 269, 0, 1, 0, 0))
    r = walk(body)[0]
    assert r["state"] == [5] and r["lists"] == [[((3, 185, 31, 12, 0), [(269, 0, 1, 0, 0)])]], r
    assert fmt_cmd(*r["lists"][0][0], {269: "g269", 185: "fade"}) == "@3 fade.GOTO(12,0) if g269[0]==1"
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes", nargs="*", type=int)
    ap.add_argument("--root", type=Path, default=CORPUS)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        sys.exit(0)
    lab = labels(a.root)
    lines = []
    if not a.scenes:
        lines.append("== Characters (Actors/Characters.abi)")
        dump_records(walk((a.root / "Actors/Characters.abi").read_bytes()), lab, lines, "  ")
        lines.append("== Globals (Actors/global.atx)")
        for b in atx.parse((a.root / "Actors/global.atx").read_text(encoding="latin-1")):
            g = events.parse_global(b)
            lines.append("  %s state=%s" % (lab[g["id"]], g["state"]))
            lines += ["    L0 " + fmt_cmd(base, conds, lab) for base, conds in g["cmds"]]
    for n in a.scenes or scene_nums(a.root):
        lines += scene_block(a.root, n, lab)
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(lines))
