"""Gilbert's game rules without graphics: replay a walkthrough against default.dat, engine `gilbert`.

    ge.dll's event interpreter, object lists, anims, inventory and dialogues as specced in
    engines/gilbert/docs/spec/logic.md; the player's moves as the EXE makes them (rooms.md,
    screens.md). The walkthrough is the fenced block under "## Walkthrough" in
    games/gilbert/docs/flow.md, one action per line:

      room R area N         walk into area N of room R (control-map cell value N + 1)
      map E                 the room's "Kort" button (area 99 -> CUA 999), then the symbol with click event E
      cua C click CODE      click the listed, not pickable object CODE (id * 100 + state) in close-up C
      cua C take CODE       drag the pickable object CODE to the inventory
      cua C use A on B      drag A (an inventory item or a pickable object of C) onto the listed object B
      dialog D choice K     choose K (0-based) in the open dialogue D
      back                  leave the close-up
      wait MS               let MS milliseconds pass in ticks of 15..17 ms (anims run, end events fire)

    python engines/gilbert/tools/simulate.py              # replay the walkthrough, check the end
    python engines/gilbert/tools/simulate.py -v           # ... printing every event run
    python engines/gilbert/tools/simulate.py --upto N     # replay N lines, then list what can be done
    python engines/gilbert/tools/simulate.py --selftest
"""

from __future__ import annotations

import functools
import re
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "parsers"))
import ctrlmap  # noqa: E402
import gamedat  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
DATA = REPO / "games/gilbert/discs/cd/Program/Data"
FLOW = REPO / "games/gilbert/docs/flow.md"
# Tick lengths for `wait`, cycled: timeGetTime steps of a 16 ms timer. A fixed 16 would stall
# every anim whose duration is a multiple of 16 (t == duration wraps without ending, logic.md).
TICKS = (16, 17, 15, 16, 16, 17, 16)


class Fail(Exception):
    pass


@functools.lru_cache(maxsize=None)
def reachable(room: int, start: tuple) -> frozenset:
    """Areas Gilbert can walk into from cell `start`: the control map's 0 cells joined to it,
    8-connected as the path finder steps (logic.md), and the areas next to them."""
    m = ctrlmap.parse((DATA / "maps" / str(room) / f"ctrl{room}.map").read_bytes())[0]
    w, h, cells = m["w"], m["h"], m["cells"]
    if not (0 <= start[0] < w and 0 <= start[1] < h):
        return frozenset(v - 1 for v in cells if v >= 2)
    seen, q, areas = {start}, deque([start]), set()
    v = cells[start[1] * w + start[0]]
    if v >= 2:
        areas.add(v - 1)
    while q:
        x, y = q.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (x + dx, y + dy)
                if n in seen or not (0 <= n[0] < w and 0 <= n[1] < h):
                    continue
                v = cells[n[1] * w + n[0]]
                if v == 0:
                    seen.add(n)
                    q.append(n)
                elif v >= 2:
                    areas.add(v - 1)
    return frozenset(areas)


class Game:
    def __init__(self, g: dict, verbose: bool = False):
        self.g, self.verbose = g, verbose
        self.vars = list(g["vars_4c"])
        self.walkmaps = g["walkmaps_36c"]
        self.inventory = list(g["inventory_2f1d4"])
        self.useobjs = g["useobjs_2f20c"]
        self.events: dict[int, list] = {}
        for e in g["events_2f228"]:
            self.events.setdefault(e["id_04"], []).append(e)
        self.dialogs = {}
        for d in g["dialogs_2f244"]:
            self.dialogs.setdefault(d["id_20"], d)
        self.anims = {}
        for a in g["anims_2fa24"]:
            self.anims.setdefault(a["id_08"], a)  # 40340 occurs twice: the first wins
        self.books = g["books_2f280"]
        self.objs = {}  # FindObj's index: every object at load time
        for w in self.walkmaps:
            for c in w["cuas_1c"]:
                for o in c["objs_20"]:
                    o["_owner"] = c
                    self.objs.setdefault(o["id_0c"], o)
        for o in self.inventory:
            o["_owner"] = None
            self.objs.setdefault(o["id_0c"], o)
        for o in self.objs.values():
            st = o["states_14"]
            o["_cur"] = next((s for s in st if s["state_04"] == o["state_30"]), st[0] if st else None)
            o["_deleted"] = False
            for s in st:
                s["_anim"] = None
        self.walkmap = self.cua = self.dialog = None
        self.wm_list: list = []
        self.cua_list: list = []
        self.shown_inv: list = []
        self.films: list[str] = []
        self.dangling: list[tuple[int, int]] = []
        self.event = 0
        self.depth = 0
        self.gpos = None  # Gilbert's cell after the last room load, for area reachability

    # ---- lookups
    def find_anim(self, aid):
        return self.anims.get(aid) if aid else None

    def find_obj(self, oid):
        o = self.objs.get(oid)
        if o is not None and o["_deleted"]:
            self.dangling.append((self.event, oid))  # the original follows a freed pointer here (Q-0401)
            return None
        return o

    def find_cua(self, cid):
        return next((c for w in self.walkmaps for c in w["cuas_1c"] if c["id_08"] == cid), None)

    def code(self, o):
        return o["id_0c"] * 100 + o["_cur"]["state_04"]

    def log(self, msg):
        if self.verbose:
            print("  " * self.depth + msg)

    # ---- object lists (logic.md "Walkmap and CUA objects")
    def clear_anims(self, lst, field):
        for o in lst:
            for s in o["states_14"]:
                if not s[field]:
                    continue
                a = self.find_anim(s[field])
                if a is None:
                    return
                s["_anim"] = a
                a["time_04"] = 0

    def sort(self, lst, field):
        rest, out = list(lst), []
        while rest:
            best, bz = 0, -1
            for i, o in enumerate(rest):
                a = self.find_anim(o["_cur"][field])
                z = a["z_24"] if a else 0
                if bz <= z:
                    best, bz = i, z
            out.append(rest.pop(best))
        return out

    def build_walkmap(self):
        lst = []
        for c in self.walkmap["cuas_1c"]:
            for o in c["objs_20"]:
                if o["visible_10"] and o["_cur"] and self.find_anim(o["_cur"]["walkmap_anim_0c"]) and len(lst) < 100:
                    lst.append(o)
                    o["_cur"]["_anim"] = self.find_anim(o["_cur"]["walkmap_anim_0c"])
        self.clear_anims(lst, "walkmap_anim_0c")
        self.wm_list = self.sort(lst, "walkmap_anim_0c")

    def build_cua(self, reset=False):
        if not self.cua:
            return
        lst = [o for o in self.cua["objs_20"]
               if o["visible_10"] and o["_cur"] and self.find_anim(o["_cur"]["cua_anim_10"])][:100]
        if reset:
            self.clear_anims(lst, "cua_anim_10")
        self.cua_list = self.sort(lst, "cua_anim_10")

    def update_inventory(self):
        self.shown_inv = [o for o in self.inventory if o["visible_10"]]

    def reset_state_anim(self, s):
        a = self.find_anim(s["cua_anim_10"])
        if a:
            s["_anim"] = a
            a["time_04"] = 0

    def set_state(self, o, n):
        s = next((s for s in o["states_14"] if s["state_04"] == n), None)
        if s is None:
            raise Fail(f"object {o['id_0c']} has no state {n} (Q-0400)")
        o["_cur"] = s

    # ---- places (logic.md "Moving between places")
    def goto_walkmap(self, wid, x, y):
        self.walkmap = next((w for w in self.walkmaps if w["id_04"] == wid), None)
        self.log(f"-> walkmap {wid} at {x},{y}")
        if self.walkmap:
            self.build_walkmap()
            self.gpos = (x // 16, y // 16)

    def goto_cua(self, cid):
        c = self.find_cua(cid)
        self.log(f"-> CUA {cid}")
        if c is None:
            self.cua = None
            return
        self.cua = c
        self.build_cua(reset=True)
        if c["first_visit_1c"]:
            c["first_visit_1c"] = 0
            self.do_event(c["first_event_10"])
        else:
            self.do_event(c["event_14"])

    def cua_end(self):
        if not self.cua:
            return
        end, self.cua, self.cua_list = self.cua["end_event_18"], None, []
        self.log("<- CUA end")
        if self.walkmap:
            self.build_walkmap()
        self.do_event(end)

    # ---- events (logic.md "Events")
    def do_event(self, eid):
        outer = self.event
        while eid:
            recs = self.events.get(eid, [])
            self.log(f"event {eid}" + ("" if recs else " (no records)"))
            self.depth += 1
            for e in recs:
                self.event = eid
                jump = self.run(e)
                if jump is not None:
                    break
            else:
                jump = None
            self.depth -= 1
            eid = jump
        self.event = outer

    def run(self, e):
        t, code = e["type_08"], e["obj_24"]
        oid, st = code // 100, code % 100
        if t == 1:
            o = self.find_obj(oid)
            if o is None:
                self.note(e, "remove: no such object")
            elif o["_owner"] is None:
                self.inventory.remove(o)
                o["_deleted"] = True
                self.update_inventory()
            elif o in o["_owner"]["objs_20"]:
                o["_owner"]["objs_20"].remove(o)
                o["_deleted"] = True
                self.build_cua()
        elif t == 2:
            o = self.find_obj(oid)
            if o:
                self.set_state(o, st)
                self.reset_state_anim(o["_cur"])
                self.build_cua()
        elif t == 3:
            if e["walkmap_1c"] and e["cua_20"]:
                self.goto_cua(e["cua_20"])
        elif t == 4:
            if self.cua:
                self.cua_end()
            self.goto_walkmap(e["walkmap_1c"], e["x_50"], e["y_54"])
        elif t in (5, 21, 22):
            self.topic(e)
        elif t == 6:
            self.log(f"sound {e['sound_40'] or (e['sound_38'], e['sound_3c'])}")
        elif t == 7:
            o = self.find_obj(oid)
            if o is None or o["_owner"] is None or o not in o["_owner"]["objs_20"]:
                self.note(e, "to inventory: object not in a close-up, nothing")
            else:
                o["_owner"]["objs_20"].remove(o)
                o["_owner"] = None
                self.inventory.append(o)
                self.set_state(o, st)
                o["visible_10"] = 1
                self.update_inventory()
                self.build_cua()
                self.log(f"inventory + {self.code(o)}")
        elif t == 8:
            o = self.find_obj(oid)
            if o and o["_owner"] is None:
                self.inventory.remove(o)
                o["_deleted"] = True
                self.update_inventory()
                self.log(f"inventory - {oid}")
            else:
                self.note(e, "from inventory: not in the inventory, nothing")
        elif t == 9:
            self.dialog = self.dialogs.get(e["dialog_34"])
            self.log(f"dialog {e['dialog_34']}")
        elif t == 10:
            if e["video_4c"]:
                self.films.append(e["video_4c"])
                self.log(f"film {e['video_4c']}")
        elif t in (12, 13):
            o = self.find_obj(oid)
            s = o and o["_cur"] and next((s for s in o["states_14"] if s["state_04"] == st), None)
            if s:
                s["pickable_20"] = 1 if t == 12 else 0
        elif t == 14:
            o = self.find_obj(oid)
            if o and o["_cur"]:
                self.set_state(o, o["_cur"]["state_04"] + 1)
                self.reset_state_anim(o["_cur"])
                self.build_cua()
        elif t in (15, 16):
            o = self.find_obj(oid)
            if o is None:
                return None
            if o["_cur"]:
                a = self.find_anim(o["_cur"]["cua_anim_10"])
                if a is None:
                    self.note(e, "show/hide: the state has no close-up anim, nothing")
                    return None
                o["_cur"]["_anim"] = a
                a["time_04"] = 0
            o["visible_10"] = 1 if t == 15 else 0
            if t == 15:
                self.reset_state_anim(o["_cur"])
            self.build_cua()
            self.update_inventory()
        elif t == 18:
            v, val, c = self.vars[e["var_10"]], e["value_14"], e["cond_0c"]
            ok = {0: v == val, 1: v != val, 2: v < val, 3: v > val, 4: True,
                  5: self.rand() <= val}.get(c, False)
            if ok:
                return e["jump_18"]
        elif t == 19:
            self.vars[e["var_10"]] = e["value_14"]
            self.log(f"v{e['var_10']} = {e['value_14']}")
        elif t == 20:
            self.vars[e["var_10"]] += e["value_14"]
            self.log(f"v{e['var_10']} += {e['value_14']} -> {self.vars[e['var_10']]}")
        return None

    def rand(self):
        return 0  # rand() % 101: the walkthrough must not depend on it (type 18 cond 5)

    def topic(self, e):
        book = self.books[e["book_28"]] if e["book_28"] < len(self.books) else []
        t = next((x for x in book if x["id_04"] == e["topic_2c"]), None)
        if t is None:
            return
        if e["type_08"] == 22:
            t2 = next((x for x in book if x["id_04"] == e["topic2_30"]), None)
            if t2 is None or not (t2["title_08"] or t2["text_0c"]):
                return
            t["title_08"] += t2["title_08"]
            t["text_0c"] += t2["text_0c"]
            t2["title_08"] = t2["text_0c"] = ""
        t["shown_10"] = 0 if e["type_08"] == 21 else 1

    def note(self, e, msg):
        self.log(f"({msg}: event {e['id_04']} obj {e['obj_24']})")

    # ---- time (logic.md "The tick")
    def tick(self, dt):
        lst = self.cua_list if self.cua else self.wm_list
        changed, ends = False, []
        for o in lst:
            s = o["_cur"]
            a = s["_anim"] if s else None
            if a is None or not a["duration_14"]:
                continue
            t = a["time_04"] + dt
            if t > a["duration_14"]:
                ends.append(a["end_event_2c"])
                a["time_04"] = t % a["duration_14"]
                n = self.find_anim(a["next_0c"])
                if n:
                    s["_anim"] = n
                s["_anim"]["time_04"] = 0
                changed = True
            else:
                a["time_04"] = t % a["duration_14"]
        if changed:
            for eid in ends:
                self.do_event(eid)

    # ---- the player's moves
    def listed(self, code):
        o = next((o for o in self.cua_list if self.code(o) == code), None)
        if o is None:
            raise Fail(f"{code} is not shown in CUA {self.cua['id_08']}: "
                       f"{sorted(self.code(o) for o in self.cua_list)}")
        return o

    def reachable_areas(self):
        return reachable(self.walkmap["id_04"], self.gpos)

    def act(self, line: str):
        a = line.split()
        if self.vars[198]:
            raise Fail("the game is over")
        if a[0] == "wait":
            left, i = int(a[1]), 0
            while left > 0:
                self.tick(TICKS[i % len(TICKS)])
                left -= TICKS[i % len(TICKS)]
                i += 1
            return
        if a[0] == "dialog":
            if not self.dialog or self.dialog["id_20"] != int(a[1]):
                raise Fail(f"dialogue {a[1]} is not open ({self.dialog and self.dialog['id_20']})")
            k, d = int(a[3]), self.dialog
            self.dialog = None
            if k >= len(d["choices_04"]):
                raise Fail(f"dialogue {a[1]} has no choice {k}")
            self.do_event(d["choices_04"][k]["event_0c"])
            return
        if self.dialog:
            raise Fail(f"dialogue {self.dialog['id_20']} is open")
        if a[0] in ("room", "map"):
            if self.cua:
                raise Fail(f"in CUA {self.cua['id_08']}, not in a room")
            if a[0] == "map":
                self.do_event(self.walkmap["id_04"] * 100 + 99)
                o = next((o for o in self.cua_list if o["_cur"]["click_event_14"] == int(a[1])), None)
                if o is None:
                    raise Fail(f"no map symbol runs event {a[1]}")
                self.do_event(int(a[1]))
                return
            r, n = int(a[1]), int(a[3])
            if self.walkmap["id_04"] != r:
                raise Fail(f"in room {self.walkmap['id_04']}, not {r}")
            if n not in self.reachable_areas():
                raise Fail(f"area {n} of room {r} is not reachable from cell {self.gpos}")
            self.do_event(r * 100 + n)
            return
        if a[0] == "back":
            if not self.cua:
                raise Fail("not in a close-up")
            self.cua_end()
            return
        if a[0] == "cua":
            if not self.cua or self.cua["id_08"] != int(a[1]):
                raise Fail(f"not in CUA {a[1]} ({self.cua and self.cua['id_08']})")
            if a[2] == "click":
                o = self.listed(int(a[3]))
                if o["_cur"]["pickable_20"]:
                    raise Fail(f"{a[3]} is pickable: a click does nothing")
                self.do_event(o["_cur"]["click_event_14"])
            elif a[2] == "take":
                o = self.listed(int(a[3]))
                if not o["_cur"]["pickable_20"]:
                    raise Fail(f"{a[3]} is not pickable")
                o["_owner"]["objs_20"].remove(o)
                o["_owner"] = None
                self.inventory.append(o)
                self.do_event(o["_cur"]["take_event_18"])
                self.build_cua()
                self.update_inventory()
            elif a[2] == "use":
                src, dst = int(a[3]), int(a[5])
                if not any(self.code(o) == src for o in self.shown_inv):
                    o = self.listed(src)
                    if not o["_cur"]["pickable_20"]:
                        raise Fail(f"{src} is neither in the inventory nor pickable")
                self.listed(dst)
                u = next((u for u in self.useobjs if u["obj_04"] == src and u["target_08"] == dst), None)
                if u is None:
                    raise Fail(f"no use of {src} on {dst}")
                self.do_event(u["event_0c"])
                self.build_cua()
                self.update_inventory()
            else:
                raise Fail(f"bad line {line!r}")
            return
        raise Fail(f"bad line {line!r}")

    def new_game(self):
        self.do_event(1)
        self.update_inventory()

    def options(self) -> list[str]:
        """What the player can do now (for writing walkthroughs)."""
        if self.dialog:
            return [f"dialog {self.dialog['id_20']} choice {k}  # {c['text_08']!r} -> {c['event_0c']}"
                    for k, c in enumerate(self.dialog["choices_04"])]
        if not self.cua:
            r = self.walkmap["id_04"]
            return [f"room {r} area {n}" for n in sorted(self.reachable_areas()) if r * 100 + n in self.events]
        c, out = self.cua["id_08"], ["back"]
        inv = [self.code(o) for o in self.shown_inv]
        for o in self.cua_list:
            s = o["_cur"]
            out.append(f"cua {c} {'take' if s['pickable_20'] else 'click'} {self.code(o)}  # {s['name_08']}")
        shown = {self.code(o) for o in self.cua_list}
        srcs = set(inv) | {self.code(o) for o in self.cua_list if o["_cur"]["pickable_20"]}
        for u in self.useobjs:
            if u["obj_04"] in srcs and u["target_08"] in shown:
                out.append(f"cua {c} use {u['obj_04']} on {u['target_08']}  # event {u['event_0c']}")
        return out


def walkthrough(text: str) -> list[tuple[int, str]]:
    m = re.search(r"^## Walkthrough\n.*?^```\n(.*?)^```", text, re.S | re.M)
    if not m:
        raise SystemExit("no walkthrough block in flow.md")
    start = text[:m.start(1)].count("\n") + 1
    return [(start + i, l.split("#")[0].strip()) for i, l in enumerate(m.group(1).splitlines())
            if l.split("#")[0].strip()]


def replay(lines, verbose=False, upto=None) -> Game:
    game = Game(gamedat.parse((DATA / "game/default.dat").read_bytes()), verbose)
    game.new_game()
    for i, (n, line) in enumerate(lines):
        if upto is not None and i >= upto:
            break
        if verbose:
            print(f"{n}: {line}")
        try:
            game.act(line)
        except Fail as e:
            raise SystemExit(f"flow.md line {n}: {line}: {e}")
    return game


def selftest() -> None:
    g = Game(gamedat.parse((DATA / "game/default.dat").read_bytes()))
    g.new_game()
    assert g.walkmap["id_04"] == 151 and g.films == ["intro.mpg"] and g.vars[60:65] == [1] * 5
    g.act("map 9909")  # the map (CUA 999, nine symbols), then the mine
    assert g.walkmap["id_04"] == 400 and g.cua is None
    lines = walkthrough(FLOW.read_text(encoding="utf-8"))
    end = replay(lines)
    assert end.vars[198] == 1 and end.films[-1] == "outro.mpg"
    print(f"selftest ok ({len(lines)} steps)")


def main(args) -> int:
    if args == ["--selftest"]:
        selftest()
        return 0
    sys.stdout.reconfigure(encoding="utf-8")
    lines = walkthrough(FLOW.read_text(encoding="utf-8"))
    upto = int(args[args.index("--upto") + 1]) if "--upto" in args else None
    game = replay(lines, "-v" in args, upto)
    if upto is not None:
        print(f"after {min(upto, len(lines))} lines: room {game.walkmap['id_04']}, "
              f"CUA {game.cua and game.cua['id_08']}, eggs v199={game.vars[199]}, v1={game.vars[1]}")
        print("inventory:", " ".join(f"{game.code(o)}" for o in game.shown_inv))
        print("\n".join(game.options()))
        return 0
    ok = game.vars[198] != 0
    print(f"{len(lines)} steps; films {' '.join(game.films)}; v198={game.vars[198]} v199={game.vars[199]} v1={game.vars[1]}")
    if game.dangling:
        print("events that name a deleted object:", " ".join(f"{e}:{o}" for e, o in game.dangling))
    print("end reached" if ok else "END NOT REACHED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
