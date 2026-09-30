"""The walkthrough of games/gilbert/docs/flow.md as dev_input for a play-through run.

    python engines/gilbert/tools/walkthrough_input.py [step_ms] [--upto N] [--ui]
prints a dev_input string (dev.cpp's commands) for run_test.sh with dev_skip_films: a new
game, then every walkthrough action with a check of where the game is before it, a
`where` every 20 steps, and at the end a snapshot and `where`. With --ui the actions go
through the user interface (walking into areas, clicks and drags, the map), not straight
to the game rules. --selftest checks the translation.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FLOW = REPO / "games/gilbert/docs/flow.md"


def walkthrough() -> list[str]:
    lines = FLOW.read_text(encoding="utf-8").splitlines()
    start = lines.index("```") + 1
    end = lines.index("```", start)
    return [l.strip() for l in lines[start:end] if l.strip() and not l.strip().startswith("#")]


def translate(action: str, ui: bool = False) -> tuple[list[str], int]:
    """dev commands for one walkthrough action, and the extra time it needs in ms."""
    a = action.split()
    if ui:
        return translate_ui(a)
    if a[0] == "room":
        return [f"inroom {a[1]}", f"area {a[3]}"], 700
    if a[0] == "map":
        # Kort: the room's event walkmap * 100 + 99 opens close-up 999; the symbol whose click
        # event is a[1] is object 99900 + (event - 9900).
        return ["area 99", f"clickobj {(99900 + int(a[1]) - 9900) * 100}"], 900
    if a[0] == "back":
        return ["back"], 700
    if a[0] == "dialog":
        return [f"indialog {a[1]}", f"choice {a[3]}"], 300
    if a[0] == "wait":
        return [], int(a[1])
    if a[0] == "cua":
        check = f"incua {a[1]}"
        if a[2] == "click":
            return [check, f"clickobj {a[3]}"], 300
        if a[2] == "take":
            return [check, f"take {a[3]}"], 300
        if a[2] == "use":
            return [check, f"use {a[3]} {a[5]}"], 300
    raise ValueError(f"unknown action {action!r}")


def translate_ui(a: list[str]) -> tuple[list[str], int]:
    if a[0] == "room":
        return [f"inroom {a[1]}", f"uiarea {a[3]}"], 900
    if a[0] == "map":
        return [f"uimap {a[1]}"], 1500
    if a[0] == "back":
        return ["uiback"], 900
    if a[0] == "dialog":
        return [f"indialog {a[1]}", f"uichoice {a[3]}"], 500
    if a[0] == "wait":
        return [], int(a[1])
    if a[0] == "cua":
        check = f"incua {a[1]}"
        if a[2] == "click":
            return [check, f"uiclick {a[3]}"], 500
        if a[2] == "take":
            return [check, f"uitake {a[3]}"], 600
        if a[2] == "use":
            return [check, f"uiuse {a[3]} {a[5]}"], 700
    raise ValueError(f"unknown action {' '.join(a)!r}")


def dev_input(step_ms: int, upto: int | None, ui: bool = False) -> str:
    cmds = ["1500:click 461 120"]
    t = 4000
    for i, action in enumerate(walkthrough()[:upto]):
        dev, extra = translate(action, ui)
        for c in dev:
            cmds.append(f"{t}:{c}")
            t += 40
        t += step_ms + extra
        if i % 20 == 19:
            cmds.append(f"{t}:where")
    cmds += [f"{t + 1000}:where", f"{t + 1500}:snap C:/tmp/walk_end.png", f"{t + 2500}:quit"]
    return ";".join(cmds)


def selftest() -> None:
    assert translate("room 151 area 11") == (["inroom 151", "area 11"], 700)
    assert translate("map 9908")[0] == ["area 99", "clickobj 9990800"]
    assert translate("cua 103 use 1060100 on 1032101")[0] == ["incua 103", "use 1060100 1032101"]
    assert translate("dialog 50000 choice 4")[0] == ["indialog 50000", "choice 4"]
    steps = walkthrough()
    assert len(steps) == 582, len(steps)
    for s in steps:
        translate(s)
        translate(s, True)
    assert translate("room 151 area 11", True)[0] == ["inroom 151", "uiarea 11"]
    print("selftest ok")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--selftest"]:
        selftest()
    else:
        upto = int(args[args.index("--upto") + 1]) if "--upto" in args else None
        step = int(args[0]) if args and args[0].isdigit() else 300
        print(dev_input(step, upto, "--ui" in args))
