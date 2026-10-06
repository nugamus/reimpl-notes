"""Map Grumpa's whole scene graph and game flow from the `.abi` corpus (E-0108/E-0116).

Pure Python over `games/grumpa/discs/cab/Scenes/Scene_*.abi`. Imports the validated record
walker `parsers/abi.py` (do not modify it): every record's byte layout is `abi`'s, this script
only *captures* the fields `abi` skips — the type-0x11 views (camera eye) and the type-0x19
triggers (click polygon + command list) — so it cannot drift from the parser.

Navigation model (E-0116): a trigger's command list (CC vector, 5-int commands
`(when, targetId, opcode, arg1, arg2)` each with an EC condition sublist) drives reserved
manager actors. `targetId==185, opcode==31` → go to scene `arg1`; `targetId==186, opcode==16`
→ change to view `arg1` within the scene. A command is *conditional* when it carries EC guards.

Backgrounds on disc are `<scene>_<view>_IS.jpg` (+ `_IZ.fxi` depth) under `Bitmaps/`, where
`<scene>` is the Scene_<NNN> number without leading zeros and `<view>` is the 186/op16 index.

    python engines/grumpa/tools/scenegraph.py            # write games/grumpa/docs/scene-flow.md
    python engines/grumpa/tools/scenegraph.py --selftest
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "parsers"))
import abi  # the validated walker (Cur, TYPES, the shared element readers)

REPO = Path(__file__).resolve().parents[3]
CORPUS = REPO / "games/grumpa/discs/cab"
OUT = REPO / "games/grumpa/docs/scene-flow.md"

NAV_MGR, VIEW_MGR = 185, 186
NAV_OP, VIEW_OP = 31, 16


def _floats(b: bytes) -> tuple:
    return struct.unpack_from("<%df" % (len(b) // 4), b, 0)


def _cc_capture(c: abi.Cur) -> dict:
    """One CC = command: 5 base ints + EC condition list. Mirrors abi.cc byte-for-byte."""
    base = struct.unpack_from("<5i", c.raw(20), 0)      # when, targetId, opcode, arg1, arg2
    conds = []
    for _ in range(abi._count(c, "EC-in-CC")):
        conds.append(struct.unpack_from("<5i", c.raw(20), 0))
    return {"when": base[0], "target": base[1], "op": base[2],
            "arg1": base[3], "arg2": base[4], "conds": conds}


def _cc_vec_capture(c: abi.Cur) -> list:
    return [_cc_capture(c) for _ in range(abi._count(c, "CC"))]


def x11_view(c: abi.Cur) -> dict:
    """Type 0x11 view (abi.t_11 layout), capturing the camera eye."""
    c.raw(12); abi.ec_vec(c); c.raw(8); abi.cc_vec(c); abi.cc_vec(c)
    cam_id = c.u32()
    block = _floats(c.raw(0x68))          # 26 floats; eye = [13..15] (scene.md E-0105)
    return {"cam_id": cam_id, "eye": (block[13], block[14], block[15])}


def x19_trigger(c: abi.Cur) -> dict:
    """Type 0x19 trigger (abi.t_19 layout), capturing the click polygon and command list."""
    c.raw(12); abi.ec_vec(c); c.raw(32)
    c.raw(76)
    abi.sub_456d70(c)
    abi.ec_vec(c)
    cmds = _cc_vec_capture(c)                               # +0x128 command list (E-0113)
    k = struct.unpack_from("<i", c.raw(4), 0)[0]           # polygon point count
    poly = []
    if k > 0:
        fl = _floats(c.raw(8 * k))
        poly = [(fl[2 * i], fl[2 * i + 1]) for i in range(k)]
    c.raw(16); c.raw(4)
    mode = c.u32()
    if mode == 2:
        for _ in range(abi._count(c, "bubble")):
            c.raw(8)
            if c.u32() != 0:
                abi.pstr(c)
    return {"poly": poly, "cmds": cmds}


def walk_scene(d: bytes) -> dict:
    """Walk one scene .abi, returning {views:{id:view}, triggers:{id:trig}, types:Counter}.
    Record layout and byte consumption are abi's; only 0x11/0x19 bodies are captured here."""
    from collections import Counter
    c = abi.Cur(d)
    views, triggers, types = {}, {}, Counter()
    while len(d) - c.o >= 8:
        t = c.u32(); rid = c.u32()
        types[t] += 1
        if t == 0x11:
            views[rid] = x11_view(c)
        elif t == 0x19:
            triggers[rid] = x19_trigger(c)
        else:
            fn = abi.TYPES.get(t)
            if fn is None:
                raise abi.ParseError(f"unmodeled type {t:#x} id {rid} at {c.o - 8:#x}")
            fn(c)
    return {"views": views, "triggers": triggers, "types": types, "tail": len(d) - c.o}


def scene_num(path: Path) -> int:
    return int(path.stem.split("_")[1])


def exits_of(trig: dict) -> list:
    """Nav commands (185/op31 -> dest) and view-switches (186/op16 -> view) in a trigger."""
    navs, vws = [], []
    for cmd in trig["cmds"]:
        guarded = bool(cmd["conds"]) or cmd["when"] != -1
        if cmd["target"] == NAV_MGR and cmd["op"] == NAV_OP:
            navs.append((cmd["arg1"], guarded))
        elif cmd["target"] == VIEW_MGR and cmd["op"] == VIEW_OP:
            vws.append((cmd["arg1"], guarded))
    return navs, vws


def build(root: Path) -> dict:
    scenes = {}
    for f in sorted(root.glob("Scenes/Scene_*.abi")):
        n = scene_num(f)
        s = walk_scene(f.read_bytes())
        s["num"] = n
        s["backgrounds"] = sorted(
            int(m.group(1))
            for p in root.glob(f"Bitmaps/{n}_*_IS.jpg")
            for m in [re.match(rf"{n}_(\d+)_IS\.jpg$", p.name)] if m)
        scenes[n] = s
    return scenes


def ipoly(poly: list) -> str:
    return "".join(f"({int(round(x))},{int(round(y))})" for x, y in poly) or "(none)"


def analyse(scenes: dict) -> dict:
    graph = {n: [] for n in scenes}                       # scene -> [(dest, trigId, guarded)]
    for n, s in scenes.items():
        for tid, trig in sorted(s["triggers"].items()):
            for dest, guarded in exits_of(trig)[0]:
                graph[n].append((dest, tid, guarded))
    start = 1 if 1 in scenes else min(scenes)
    # reachability from start over nav edges (dest need not be a loaded scene file)
    seen, stack = set(), [start]
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        for dest, _, _ in graph.get(n, []):
            if dest in scenes and dest not in seen:
                stack.append(dest)
    reachable = {n for n in scenes if n in seen}
    unreachable = sorted(set(scenes) - reachable)
    dead_ends = sorted(n for n in scenes if not graph[n])
    # tutorial chain: follow the first unconditional nav from start
    chain, cur, guard = [start], start, 0
    while guard < 50:
        guard += 1
        nxt = next((d for d, _, g in graph.get(cur, []) if not g and d in scenes and d not in chain), None)
        if nxt is None:
            break
        chain.append(nxt); cur = nxt
    # nav targets that have no scene file
    missing = sorted({d for n in scenes for d, _, _ in graph[n] if d not in scenes})
    return {"graph": graph, "start": start, "reachable": reachable,
            "unreachable": unreachable, "dead_ends": dead_ends, "chain": chain,
            "missing": missing}


def write_md(scenes: dict, a: dict, parse_report: str) -> None:
    g = a["graph"]
    nav_count = sum(len(v) for v in g.values())
    L = []
    L.append("# Grumpa scene graph and game flow\n")
    L.append("Generated by `engines/grumpa/tools/scenegraph.py` from "
             "`games/grumpa/discs/cab/Scenes/Scene_*.abi` (navigation model E-0116; "
             "trigger polygons E-0108; command lists E-0109). Regenerate after a parser change.\n")
    L.append("## Summary\n")
    L.append(f"- Scene files: **{len(scenes)}** `Scene_*.abi`.")
    L.append(f"- Navigation edges (trigger command `185/op31 -> dest`): **{nav_count}**.")
    L.append(f"- Start scene: **{a['start']}** (`Scene_{a['start']:03d}`).")
    L.append(f"- Reachable from start (over nav edges): **{len(a['reachable'])}/{len(scenes)}**.")
    L.append(f"- Tutorial chain (first unconditional nav each hop): "
             f"{' -> '.join(str(x) for x in a['chain'])}.")
    if a["unreachable"]:
        L.append(f"- Unreachable scene files: {', '.join(str(x) for x in a['unreachable'])}.")
    else:
        L.append("- Unreachable scene files: none.")
    if a["dead_ends"]:
        L.append(f"- Scenes with no nav exit (dead ends): "
                 f"{', '.join(str(x) for x in a['dead_ends'])}.")
    if a["missing"]:
        L.append(f"- Nav targets with no `Scene_*.abi` on disc: "
                 f"{', '.join(str(x) for x in a['missing'])}.")
    L.append(f"\n{parse_report}\n")

    L.append("## Exit table\n")
    L.append("Per scene, every trigger carrying a go-to-scene (`185/op31`) and/or a "
             "view-switch (`186/op16`) command. `cond?` = the command has an EC guard or a "
             "non-immediate `when` (conditional). Polygon points are integer screen (800x600).\n")
    L.append("| scene | trigger | polygon | -> scene | view-switch | cond? |")
    L.append("|---|---|---|---|---|---|")
    for n in sorted(scenes):
        s = scenes[n]
        rows = 0
        for tid, trig in sorted(s["triggers"].items()):
            navs, vws = exits_of(trig)
            if not navs and not vws:
                continue
            rows += 1
            dest = ", ".join(str(d) for d, _ in navs) or "-"
            vw = ", ".join(str(v) for v, _ in vws) or "-"
            cond = "yes" if any(g for _, g in navs + vws) else "no"
            L.append(f"| {n} | {tid} | {ipoly(trig['poly'])} | {dest} | {vw} | {cond} |")
        if rows == 0:
            L.append(f"| {n} | *(no scene/view exit)* | | | | |")

    L.append("\n## Views and backgrounds per scene\n")
    L.append("Type-0x11 view records (with camera eye from the view block, E-0105) and the "
             "`<scene>_<view>_IS.jpg` backgrounds present on disc.\n")
    L.append("| scene | views (0x11 ids) | camera eyes | bg views on disc | triggers |")
    L.append("|---|---|---|---|---|")
    for n in sorted(scenes):
        s = scenes[n]
        vids = ", ".join(str(i) for i in sorted(s["views"])) or "-"
        eyes = "; ".join(f"({v['eye'][0]:.0f},{v['eye'][1]:.0f},{v['eye'][2]:.0f})"
                         for _, v in sorted(s["views"].items())) or "-"
        bgs = ", ".join(str(b) for b in s["backgrounds"]) or "-"
        L.append(f"| {n} | {vids} | {eyes} | {bgs} | {len(s['triggers'])} |")

    L.append("\n## Connectivity (adjacency)\n")
    L.append("Each scene and the scenes its triggers navigate to (`*` = conditional).\n")
    for n in sorted(scenes):
        edges = g[n]
        if not edges:
            L.append(f"- **{n}** -> (none)")
            continue
        parts = ", ".join(f"{d}{'*' if guard else ''}(t{tid})" for d, tid, guard in edges)
        L.append(f"- **{n}** -> {parts}")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")


def validate_all(root: Path) -> str:
    """Re-run abi over every .abi (Scenes + Actors) and report X/Y, bytes consumed."""
    from collections import Counter
    files = sorted(set(root.glob("Scenes/*.abi")) | set(root.glob("Actors/*.abi")))
    bad = char = nrec = tail = 0
    types: Counter = Counter()
    fails = []
    for f in files:
        d = f.read_bytes()
        if len(d) >= 4 and struct.unpack_from("<I", d, 0)[0] == 0x03:
            char += 1
            continue
        try:
            r = abi.parse(d)
            types.update(r["types"]); nrec += len(r["records"]); tail += r["tail"]
        except (abi.ParseError, struct.error) as e:
            bad += 1; fails.append(f"{f.name}: {e}")
    done = len(files) - bad - char
    lines = ["## Parser coverage\n",
             f"- `abi.py`: **{done}/{len(files) - char}** scene/item `.abi` parsed, "
             f"every byte consumed ({nrec} records, {tail} trailing padding bytes).",
             f"- {char} `CFXCharacter` type-0x03 database files skipped as expected (Q-0006)."]
    if fails:
        lines.append("- FAILURES: " + "; ".join(fails))
    else:
        lines.append("- No failures.")
    return "\n".join(lines)


def selftest() -> None:
    # a CC command with one EC guard round-trips through _cc_vec_capture
    cc = struct.pack("<5i", -1, 185, 31, 211, 0) + struct.pack("<i", 1) + struct.pack("<5i", 269, 0, 0, 0, 0)
    c = abi.Cur(struct.pack("<i", 1) + cc)
    cmds = _cc_vec_capture(c)
    assert c.o == len(c.d), c.o
    assert cmds[0]["target"] == 185 and cmds[0]["op"] == 31 and cmds[0]["arg1"] == 211, cmds
    assert cmds[0]["conds"] == [(269, 0, 0, 0, 0)], cmds
    navs, vws = exits_of({"cmds": cmds})
    assert navs == [(211, True)], navs            # guarded: has an EC condition
    # an immediate unconditional view-switch
    cmd2 = {"when": -1, "target": 186, "op": 16, "arg1": 2, "arg2": 0, "conds": []}
    assert exits_of({"cmds": [cmd2]})[1] == [(2, False)]
    # the real start scene: Scene_001 navigates to 211 (tutorial chain head)
    s1 = CORPUS / "Scenes/Scene_001.abi"
    if s1.exists():
        sc = walk_scene(s1.read_bytes())
        dests = {d for tr in sc["triggers"].values() for d, _ in exits_of(tr)[0]}
        assert 211 in dests, f"Scene_001 should navigate to 211, got {dests}"
    print("selftest ok")


def write_graph(scenes: dict) -> Path:
    """The scene graph in the engine-independent format tools/route.py reads
    (engines/<engine>/notes/graph.json): nodes are scenes; an edge is a trigger whose command
    list goes to another scene, with the harness input that fires it (grumpa_vm syntax:
    click the polygon's centre, then let the fade run) and whether conditions guard it."""
    import json
    edges = []
    for n, s in sorted(scenes.items()):
        for tid, trig in sorted(s["triggers"].items()):
            navs, _ = exits_of(trig)
            if not navs or not trig["poly"]:
                continue
            cx = round(sum(p[0] for p in trig["poly"]) / len(trig["poly"]))
            cy = round(sum(p[1] for p in trig["poly"]) / len(trig["poly"]))
            for dest, guarded in navs:
                edges.append({"from": str(n), "to": str(dest), "guarded": guarded,
                              "action": f"trigger {tid} at ({cx}, {cy})",
                              "input": f"click {cx} {cy};ticks 80"})
    out = REPO / "engines/grumpa/notes/graph.json"
    out.write_text(json.dumps({"engine": "grumpa", "start": "1",
                               "nodes": [str(n) for n in sorted(scenes)], "edges": edges},
                              indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=str(CORPUS))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--graph", action="store_true", help="write notes/graph.json for tools/route.py")
    args = ap.parse_args()
    if args.selftest:
        selftest()
    elif args.graph:
        out = write_graph(build(Path(args.root)))
        print(f"wrote {out}")
    else:
        root = Path(args.root)
        scenes = build(root)
        a = analyse(scenes)
        write_md(scenes, a, validate_all(root))
        print(f"wrote {OUT}")
        print(f"scenes={len(scenes)} reachable={len(a['reachable'])} "
              f"start={a['start']} chain={'->'.join(str(x) for x in a['chain'])}")
        if a["unreachable"]:
            print("unreachable:", a["unreachable"])
        if a["dead_ends"]:
            print("dead ends:", a["dead_ends"])
