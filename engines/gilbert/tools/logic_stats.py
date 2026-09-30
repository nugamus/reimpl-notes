"""Corpus statistics behind the ge.dll logic spec (engines/gilbert/docs/spec/logic.md).

    python engines/gilbert/tools/logic_stats.py

Reads default.dat, the control maps and the room picture collections; prints one line per
check. Every number cited from here in EVIDENCE.md (E-04xx) comes from this output.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "parsers"))
import ctrlmap  # noqa: E402
import gamedat  # noqa: E402
import wxi  # noqa: E402

MAPS = gamedat.DATA / "maps"


def items(path: Path) -> int | None:
    return len(wxi.parse(path.read_bytes())["items"]) if path.exists() else None


def main() -> None:
    g = gamedat.parse((gamedat.DATA / "game/default.dat").read_bytes())
    anims = {a["id_08"]: a for a in g["anims_2fa24"]}
    objs, owner_cua, owner_wm = {}, {}, {}
    for w in g["walkmaps_36c"]:
        for c in w["cuas_1c"]:
            for o in c["objs_20"]:
                objs[o["id_0c"]] = o
                owner_cua[o["id_0c"]], owner_wm[o["id_0c"]] = c, w
    states = lambda o: {s["state_04"]: s for s in o["states_14"]}  # noqa: E731
    ev = g["events_2f228"]
    ids = {e["id_04"] for e in ev}

    # anims
    zs = [a["z_24"] for a in anims.values()]
    print(f"anims: {len(anims)}, id 0 present: {0 in anims}, z {min(zs)}..{max(zs)}, "
          f"duration 0: {sum(a['duration_14'] == 0 for a in anims.values())}, "
          f"next == own id: {sum(a['next_0c'] == a['id_08'] for a in anims.values())}, "
          f"end events: {sum(a['end_event_2c'] != 0 for a in anims.values())}")
    use = defaultdict(list)
    for w in g["walkmaps_36c"]:
        for c in w["cuas_1c"]:
            for o in c["objs_20"]:
                for s in o["states_14"]:
                    if s["walkmap_anim_0c"]:
                        use[("w", w["id_04"], s["walkmap_anim_0c"])].append(o["id_0c"])
                    if s["cua_anim_10"]:
                        use[("c", c["id_08"], s["cua_anim_10"])].append(o["id_0c"])
    shared = [k for k, v in use.items() if len(set(v)) > 1]
    print(f"anim IDs used by more than one object of the same walkmap/CUA: {len(shared)}")

    # object counts per walkmap / CUA against the 100-entry arrays
    per_wm = [sum(len(c["objs_20"]) for c in w["cuas_1c"]) for w in g["walkmaps_36c"]]
    per_cua = [len(c["objs_20"]) for w in g["walkmaps_36c"] for c in w["cuas_1c"]]
    print(f"objects per walkmap max {max(per_wm)}, per CUA max {max(per_cua)}")

    # picture numbers against the room collections
    bad_c = bad_w = n_c = n_w = 0
    for w in g["walkmaps_36c"]:
        wid = w["id_04"]
        n_wo = items(MAPS / str(wid) / f"w{wid}o.wxi")
        for c in w["cuas_1c"]:
            n_cua = items(MAPS / str(wid) / f"cua{c['id_08']}.wxi")
            for o in c["objs_20"]:
                for s in o["states_14"]:
                    a = anims.get(s["cua_anim_10"])
                    if a and n_cua is not None:
                        n_c += 1
                        bad_c += not a["unk_28"] < n_cua
                    a = anims.get(s["walkmap_anim_0c"])
                    if a and n_wo is not None:
                        n_w += 1
                        bad_w += not a["unk_28"] < n_wo
    print(f"cua anim +0x28 < items of cua<id>.wxi: {n_c - bad_c}/{n_c}; "
          f"walkmap anim +0x28 < items of w<id>o.wxi: {n_w - bad_w}/{n_w}")
    inv = [s["unk_1c"] for o in objs.values() for s in o["states_14"]]
    print(f"state +0x1c range {min(inv)}..{max(inv)}")

    # event operands
    t = lambda n: [e for e in ev if e["type_08"] == n]  # noqa: E731
    for n in (2, 7, 12, 13):
        ok = sum(e["obj_24"] // 100 in objs and e["obj_24"] % 100 in states(objs[e["obj_24"] // 100])
                 for e in t(n))
        print(f"type {n}: object and state exist {ok}/{len(t(n))}")
    ok = sum(e["obj_24"] // 100 in objs and e["obj_24"] % 100 + 1 in states(objs[e["obj_24"] // 100])
             for e in t(14))
    print(f"type 14: state obj%100 + 1 exists {ok}/{len(t(14))}")
    for n in (15, 16):
        noanim = sum(e["obj_24"] // 100 in objs and
                     all(s["cua_anim_10"] not in anims for s in objs[e["obj_24"] // 100]["states_14"])
                     for e in t(n))
        print(f"type {n}: objects with no CUA anim in any state {noanim}/{len(t(n))}")
    cua_wm = {c["id_08"]: w["id_04"] for w in g["walkmaps_36c"] for c in w["cuas_1c"]}
    print(f"type 3: walkmap operand = the CUA's walkmap {sum(cua_wm.get(e['cua_20']) == e['walkmap_1c'] for e in t(3))}"
          f"/{len(t(3))}")
    print(f"type 4 +0x58: {sorted(Counter(e['unk_58'] for e in t(4)).items())}")
    named = [e for e in t(6) if e["sound_40"]]
    print(f"type 6: named {len(named)} (+0x44 kinds {sorted(Counter(e['sound_44'] for e in named).items())}, "
          f"+0x48 {sorted(Counter(e['unk_48'] for e in named).items())}); numbered "
          f"{sorted(Counter((e['sound_38'], e['sound_3c'], e['unk_48']) for e in t(6) if not e['sound_40']).items())}")
    self_jumps = sum(e["jump_18"] == e["id_04"] for e in t(18))
    print(f"type 18: jumps to their own ID {self_jumps}")

    # control maps: area cells and their events walkmap*100 + v - 1
    have = miss = 0
    missing = []
    values = Counter()
    for w in g["walkmaps_36c"]:
        f = MAPS / str(w["id_04"]) / f"ctrl{w['id_04']}.map"
        if not f.exists():
            continue
        m = ctrlmap.parse(f.read_bytes())[0]
        vs = set(m["cells"])
        values.update(vs)
        for v in sorted(x for x in vs if x >= 2):
            if w["id_04"] * 100 + v - 1 in ids:
                have += 1
            else:
                miss += 1
                missing.append((w["id_04"], v))
    print(f"control-map values >= 2 with an event walkmap*100 + v - 1: {have}/{have + miss}; "
          f"without: {missing}")
    print(f"rooms per cell value: {sorted(values.items())}")
    print(f"events walkmap*100 + 99: {sorted(i for i in ids if i % 100 == 99 and i // 100 in cua_wm.values())}")


if __name__ == "__main__":
    main()
