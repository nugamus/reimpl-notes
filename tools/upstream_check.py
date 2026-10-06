"""How ready is an engine for a pull request to ScummVM? One table of the things reviewers
check (as written in ScummVM's HOWTO-Engines and coding conventions), run on the clean
branch `<engine>` (what a PR would contain), plus two audits that are frequent review
comments: GUI text not wrapped for translation, and keys read directly instead of through
the keymapper.

    python tools/upstream_check.py grumpa
    python tools/upstream_check.py --all
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ENGINES = [l.split()[0] for l in (Path(__file__).resolve().parents[1] / "tools" / "engines.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
REPO = "C:/scummvm"


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True).stdout


def files(engine: str) -> dict[str, str]:
    names = [n for n in git("ls-tree", "-r", "--name-only", engine, f"engines/{engine}").split() if n]
    return {n: git("show", f"{engine}:{n}") for n in names}


def check(engine: str) -> int:
    fs = files(engine)
    if not fs:
        print(f"{engine}: no clean branch")
        return 1
    code = {n: t for n, t in fs.items() if n.endswith((".cpp", ".h"))}
    allc = "\n".join(code.values())
    meta = "\n".join(t for n, t in code.items() if "metaengine" in n or "detection" in n)
    rst = git("show", f"{engine}:doc/docportal/settings/game.rst")
    uses_tr = "_(" in allc or "_s(" in allc
    rows = [
        ("configure.engine", f"engines/{engine}/configure.engine" in fs, "engine registration for configure"),
        ("credits.pl", f"engines/{engine}/credits.pl" in fs, "credits entry, merged into AUTHORS"),
        ("module.mk", f"engines/{engine}/module.mk" in fs, ""),
        ("detection tables with md5s", bool(re.search(r"AD_ENTRY\w*\(|ADGameFileDescription", meta)), ""),
        ("marked unstable/testing", "ADGF_UNSTABLE" in meta or "ADGF_TESTING" in meta,
         "new engines start as ADGF_UNSTABLE"),
        ("POTFILES (translatable strings)", f"engines/{engine}/POTFILES" in fs or not uses_tr,
         "list every file using _() / _s()"),
        ("saves through ScummVM", bool(re.search(r"saveGame(Stream|State)", allc)) and bool(re.search(r"loadGame(Stream|State)", allc)),
         "launcher and in-game save/load go through the MetaEngine, not only the original's own files"),
        ("saves: versioned", bool(re.search(r"(?i)save\w*version|kSavegameVersion|SAVEGAME_VERSION", allc)),
         "a version field, bumped on format changes, old versions still loading"),
        ("saves: thumbnails", "Graphics::saveThumbnail" in allc or "saveThumbnail" in allc or "getSavegameThumbnail" in allc, ""),
        ("keymapper", "initKeymaps" in allc, "controls listed in Global Options > Keymaps"),
        ("options documented in game.rst", engine.lower() in rst.lower() or not re.search(r"ExtraGuiOption", meta),
         "every extra GUI option in doc/docportal/settings/game.rst"),
        ("GPL header on every file", all("ScummVM - Graphic Adventure Engine" in t[:400] for t in code.values()), ""),
    ]
    width = max(len(r[0]) for r in rows)
    print(f"## {engine}")
    for name, ok, why in rows:
        print(f"  {'ok  ' if ok else 'TODO'} {name.ljust(width)}  {'' if ok else why}")
    # Audits: literal GUI text not wrapped for translation; raw key checks outside the keymapper.
    gui = [(n, i + 1, l.strip()) for n, t in code.items() for i, l in enumerate(t.splitlines())
           if re.search(r"(MessageDialog|GUIErrorMessage|U32String|setTooltip|ButtonWidget|StaticTextWidget)\s*\(\s*\"", l)]
    keys = [(n, i + 1, l.strip()) for n, t in code.items() for i, l in enumerate(t.splitlines())
            if re.search(r"kbd\.keycode\s*==\s*Common::KEYCODE_", l) and "dev.cpp" not in n]
    print(f"  GUI text not wrapped in _(): {len(gui)}" + "".join(f"\n      {n}:{i}: {l[:100]}" for n, i, l in gui[:5]))
    print(f"  keys read directly (not via the keymapper; fine for typing text): {len(keys)}"
          + "".join(f"\n      {n}:{i}: {l[:100]}" for n, i, l in keys[:5]))
    # Our own test tooling (not an upstream requirement, but how we keep the engine right).
    tests = Path(__file__).resolve().parents[1] / "engines" / engine / "tests"
    scenarios = len([p for p in tests.glob("*.toml") if not p.name.startswith(("save_", "_"))])
    dev_all = "\n".join(git("show", f"{engine}:{n}") for n in fs if n.endswith(".cpp"))
    print("  testing (ours):")
    for name, ok, why in [
        (f"scenarios ({scenarios})", scenarios >= 3, "at least boot, a scene, a save/load round trip (new-scenario skill)"),
        ("coverage debug channel", '"cov ' in dev_all, 'debugC(1, kDebugCoverage, "cov <kind> %d", ...) at the script/event dispatch'),
        ("coverage universe", (tests / "coverage.txt").exists(), "tests/coverage.txt: every opcode and room the spec defines"),
        ("debugger console", "registerCmd" in dev_all,
         "a GUI::Debugger console with goto/give/var/save/load commands (model: engines/x3d/console.cpp)"),
        ("save-compat templates", (tests / "save_make.toml").exists() and (tests / "save_load.toml").exists(),
         "tests/save_make.toml + save_load.toml for tools/savecompat.py (model: grumpa)"),
        ("route graph", (tests.parent / "notes" / "graph.json").exists(),
         "notes/graph.json from the game data for tools/route.py (model: grumpa scenegraph.py --graph)"),
    ]:
        print(f"    {'ok  ' if ok else 'TODO'} {name.ljust(width - 2)}  {'' if ok else why}")
    todo = sum(not r[1] for r in rows)
    print(f"  {todo} to do; the engine wiki page, a game-data md5 list for the wiki, and a forum/Discord heads-up are manual")
    return todo


if __name__ == "__main__":
    targets = ENGINES if sys.argv[1:] == ["--all"] else sys.argv[1:]
    if not targets:
        print(__doc__)
        sys.exit(2)
    sys.exit(1 if sum(check(e) for e in targets) else 0)
