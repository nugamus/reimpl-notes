# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Old saves must keep loading (a ScummVM requirement). Archive today's saves, and check that
every archived generation still loads with the current build.

Per engine, two scenario templates in `engines/<engine>/tests/`:
  save_make.toml   reaches a state and saves it (its keys use the harness's save command);
  save_load.toml   loads slot {slot} and snaps (`{slot}` is replaced).
They are templates, not regular scenarios (the runner skips names starting with `save_`).

    uv run tools/savecompat.py grumpa --capture     # archive saves from the current build
    uv run tools/savecompat.py grumpa               # load every archived generation
    uv run tools/savecompat.py --all

Archives live in `engines/<engine>/tests/saves/legacy/<date>-<commit>/` (gitignored: saves
carry thumbnails of game imagery). A generation passes when the load run exits normally,
takes its snap, and its log has no load error. Run --capture before every save-format
version bump, so the old format stays covered.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import scenario  # noqa: E402

ENGINES = [l.split()[0] for l in (REPO / "tools" / "engines.txt").read_text().splitlines()
           if l.strip() and not l.startswith("#")]
LOAD_ERROR = re.compile(r"(?i)(unsupported save|save.*version|failed to load|cannot load|corrupt)")


def tests(engine: str) -> Path:
    return REPO / "engines" / engine / "tests"


def capture(engine: str) -> int:
    make = tests(engine) / "save_make.toml"
    if not make.exists():
        print(f"{engine}: no tests/save_make.toml")
        return 1
    tmp = tests(engine) / "_savecompat_make.toml"
    tmp.write_text("export_saves = true\n" + make.read_text(encoding="utf-8"), encoding="utf-8")  # before [keys]
    try:
        scenario.run(engine, tmp, update=True)
    finally:
        tmp.unlink()
    made = tests(engine) / "saves" / "_savecompat_make"
    files = [f for f in made.glob("*") if f.is_file()] if made.exists() else []
    if not files:
        print(f"{engine}: the make scenario saved nothing")
        return 1
    commit = subprocess.run(["git", "-C", f"C:/scummvm-dev/{engine}", "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    dest = tests(engine) / "saves" / "legacy" / f"{time.strftime('%Y-%m-%d')}-{commit}"
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(made, dest)
    shutil.rmtree(made)
    # What the game looked like when it saved: loading must bring that back.
    shot = tests(engine) / "golden" / "_savecompat_make" / "saved.png"
    if shot.exists():
        shutil.copy(shot, dest / "saved.png")
    shutil.rmtree(shot.parent, ignore_errors=True)
    print(f"{engine}: archived {len(files)} save file(s) -> {dest.relative_to(REPO)}")
    return 0


def check(engine: str) -> int:
    load = tests(engine) / "save_load.toml"
    gens = sorted((tests(engine) / "saves" / "legacy").glob("*")) if (tests(engine) / "saves" / "legacy").exists() else []
    if not load.exists() or not gens:
        print(f"{engine}: {'no tests/save_load.toml' if not load.exists() else 'no archived saves (--capture)'}")
        return 0
    bad = 0
    template = load.read_text(encoding="utf-8")
    for gen in gens:
        slots = sorted({int(m.group(1)) for f in gen.glob("*") for m in [re.search(r"\.(\d+)$", f.name)] if m})
        for slot in slots or [1]:
            tmp = tests(engine) / "_savecompat_load.toml"
            tmp.write_text(f'saves_from = "legacy/{gen.name}"\n' + template.replace("{slot}", str(slot)),
                           encoding="utf-8")  # top-level keys go before [keys]
            # The loaded screen is compared with the screen at save time (when it was captured).
            golden = tests(engine) / "golden" / "_savecompat_load"
            shutil.rmtree(golden, ignore_errors=True)
            if (gen / "saved.png").exists():
                golden.mkdir(parents=True)
                shutil.copy(gen / "saved.png", golden / "loaded.png")
            try:
                ok = scenario.run(engine, tmp, update=False)
            finally:
                tmp.unlink()
            log = (tests(engine) / "out" / "_savecompat_load" / "run.log")
            err = LOAD_ERROR.search(log.read_text(encoding="utf-8", errors="replace")) if log.exists() else None
            if not ok or err:
                bad += 1
                print(f"FAIL {engine} {gen.name} slot {slot}" + (f": {err.group(0)}" if err else ""))
            else:
                print(f"ok   {engine} {gen.name} slot {slot} loads")
    shutil.rmtree(tests(engine) / "golden" / "_savecompat_load", ignore_errors=True)
    return bad


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    engines = ENGINES if "--all" in a else [x for x in a if not x.startswith("--")]
    fn = capture if "--capture" in a else check
    sys.exit(1 if sum(fn(e) for e in engines) else 0)
