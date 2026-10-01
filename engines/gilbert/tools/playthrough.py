"""The playthrough of games/gilbert/playthrough/: the walkthrough of games/gilbert/docs/flow.md
in words, from the game's own names.

    python engines/gilbert/tools/playthrough.py             # writes games/gilbert/playthrough/part*.md
    python engines/gilbert/tools/playthrough.py --selftest  # every action resolves to names

Nothing here is new knowledge: each step is one walkthrough action, its objects named by the
tooltips the player sees (Danish), its dialogue choices by their text, its rooms by English
names of the database's internal Swedish titles, and its areas by where their cells lie in
the room's control map. The README beside the parts is written by hand.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent / "parsers"))
import ctrlmap  # noqa: E402
import gamedat  # noqa: E402

DATA = REPO / "games/gilbert/discs/cd/Program/Data"
FLOW = REPO / "games/gilbert/docs/flow.md"
OUT = REPO / "games/gilbert/playthrough"

# English names of the rooms (the database's titles are internal Swedish names).
ROOMS = {
    100: "the beach", 150: "the pier", 151: "the crash site", 170: "the beach path",
    200: "the laboratory, upper floor", 250: "the laboratory, lower floor",
    254: "outside the laboratory", 270: "the path to the laboratory",
    300: "the desert: oil refinery", 350: "the desert: camel", 351: "the desert: bedouin's tent",
    352: "the desert: strawberry field", 370: "the desert path",
    400: "the mine entrance", 461: "the mine elevator", 462: "the lava man's hall",
    463: "the mine, before the elevator",
    500: "the forest", 550: "the clearing (the food lady's house)",
    552: "the rainforest: plane wreck", 553: "the rainforest", 554: "the rainforest",
    555: "the rainforest: hollow tree", 556: "the pine forest", 557: "the pine forest",
    558: "the pine forest", 600: "the glacier: ice-cream kiosk", 650: "the glacier: lookout",
}
for _n in range(1, 11):
    ROOMS[450 + _n] = f"mine room {_n}"

# The parts: (file, title, first step), in walkthrough order.
PARTS = [
    ("part1.md", "The beach and the laboratory", 1),
    ("part2.md", "The desert, the forest and the food lady", 100),
    ("part3.md", "The mine, the lava man and the ice queen", 192),
    ("part4.md", "Artists, balloons and the flying kiosk", 319),
    ("part5.md", "Bees, lipstick, zinc and the wok", 433),
    ("part6.md", "The crystal, the last eggshells and the ending", 523),
]


def load():
    db = gamedat.parse((DATA / "game/default.dat").read_bytes())
    states, cuas = {}, {}
    objs = [o for w in db["walkmaps_36c"] for c in w["cuas_1c"] for o in c["objs_20"]]
    objs += list(db["inventory_2f1d4"])
    for o in objs:
        for s in o["states_14"]:
            states.setdefault(o["id_0c"] * 100 + s["state_04"], s)
    for w in db["walkmaps_36c"]:
        for c in w["cuas_1c"]:
            cuas[c["id_08"]] = c["name_0c"]
    dialogs = {d["id_20"]: d for d in db["dialogs_2f244"]}
    return states, cuas, dialogs


def name(states, code: int) -> str:
    s = states.get(code)
    if not s:
        raise KeyError(f"object {code}")
    text = s["text_24"].strip()
    return f"«{text}»" if text else f"the spot the game calls \"{s['name_08'].strip()}\" (no description)"


_maps = {}


def where(room: int, area: int) -> str:
    """Where area n's cells lie in the room: thirds of its width and height."""
    if room not in _maps:
        _maps[room] = ctrlmap.parse((DATA / f"maps/{room}/ctrl{room}.map").read_bytes())[0]
    m = _maps[room]
    cells = [(i % m["w"], i // m["w"]) for i, v in enumerate(m["cells"]) if v == area + 1]
    if not cells:
        raise KeyError(f"room {room} area {area}")
    x = sum(c[0] for c in cells) / len(cells) / max(m["w"] - 1, 1)
    y = sum(c[1] for c in cells) / len(cells) / max(m["h"] - 1, 1)
    edge = min(x, 1 - x, y, 1 - y) < 0.06
    h = "left" if x < 1 / 3 else ("right" if x > 2 / 3 else "")
    v = "top" if y < 1 / 3 else ("bottom" if y > 2 / 3 else "")
    spot = " ".join(p for p in (v, h) if p) or "middle"
    return f"{spot} edge" if edge and spot != "middle" else spot


def walkthrough():
    lines = FLOW.read_text(encoding="utf-8").splitlines()
    start = lines.index("```") + 1
    end = lines.index("```", start)
    steps, section = [], ""
    for l in lines[start:end]:
        l = l.strip()
        if l.startswith("#"):
            section = l.lstrip("# ").strip()
        elif l:
            steps.append((section, l))
    return steps


def say(states, cuas, dialogs, action: str, nxt: str | None) -> str:
    a = action.split()
    if a[0] == "room":
        room, area = int(a[1]), int(a[3])
        spot = where(room, area)
        n = nxt.split() if nxt else []
        if n and n[0] == "room" and int(n[1]) != room:
            return f"Walk to {ROOMS[int(n[1])]} (area {area}, {spot} of the room)."
        if n and n[0] == "cua":
            return f"Walk up to close-up {n[1]} \"{cuas[int(n[1])]}\" (area {area}, {spot} of the room)."
        return f"Walk into area {area} ({spot} of the room)."
    if a[0] == "map":
        sym = 99900 + int(a[1]) - 9900
        return f"Open the map (Kort) and click {name(states, sym * 100)}."
    if a[0] == "back":
        return "Leave the close-up (the back arrow, bottom right)."
    if a[0] == "wait":
        return f"Wait about {int(a[1]) // 1000 or 1} s while it happens."
    if a[0] == "dialog":
        d = dialogs[int(a[1])]
        k = int(a[3])
        text = d["choices_04"][k]["text_08"].strip().replace("\n", " ")
        return f"Choose «{text}» (choice {k + 1})."
    if a[0] == "cua":
        if a[2] == "click":
            return f"Click {name(states, int(a[3]))}."
        if a[2] == "take":
            return f"Take {name(states, int(a[3]))} (drag it into the inventory)."
        if a[2] == "use":
            return f"Drag {name(states, int(a[3]))} onto {name(states, int(a[5]))}."
    raise ValueError(f"unknown action {action!r}")


def generate() -> dict[str, str]:
    states, cuas, dialogs = load()
    steps = walkthrough()
    files = {}
    for p, (fname, title, first) in enumerate(PARTS):
        last = PARTS[p + 1][2] - 1 if p + 1 < len(PARTS) else len(steps)
        nav = ["[Index](README.md)"]
        if p > 0:
            nav.append(f"Previous: [{PARTS[p - 1][1]}]({PARTS[p - 1][0]})")
        if p + 1 < len(PARTS):
            nav.append(f"Next: [{PARTS[p + 1][1]}]({PARTS[p + 1][0]})")
        out = [f"# Part {p + 1}: {title}", "", " · ".join(nav), "",
               f"Steps {first}–{last} of the [walkthrough](../docs/flow.md#walkthrough). "
               "Generated by `engines/gilbert/tools/playthrough.py`; edit flow.md or the tool, "
               "not this file. Each step ends with its walkthrough action for scripted runs.", ""]
        section = None
        for i in range(first - 1, last):
            sec, action = steps[i]
            if sec != section:
                section = sec
                out += ["", f"## {sec[0].upper() + sec[1:]}", ""]
            nxt = steps[i + 1][1] if i + 1 < len(steps) else None
            out.append(f"{i + 1}. {say(states, cuas, dialogs, action, nxt)} `{action}`")
        files[fname] = "\n".join(out) + "\n"
    return files


def selftest() -> None:
    files = generate()
    steps = walkthrough()
    assert len(steps) == 582, len(steps)
    body = "".join(files.values())
    for i in range(1, len(steps) + 1):
        assert f"\n{i}. " in body, i
    assert where(151, 11) and where(100, 25)
    print(f"selftest ok: {len(steps)} steps in {len(files)} parts")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        for f, text in generate().items():
            (OUT / f).write_text(text, encoding="utf-8", newline="\n")
            print(f"wrote {OUT / f}")
