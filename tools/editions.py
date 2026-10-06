"""Which editions and languages of a game does the engine recognise?

Runs the engine's own ScummVM detection (`scummvm --detect --recursive`, the dev build in
C:\\scummvm-dev\\<engine>) on every edition folder under the game's `discs/` (the game folders
come from tools/engines.txt), and prints one row per folder with what was detected: the
editions we own but don't support yet, and every language variant that works.

    python tools/editions.py ring
    python tools/editions.py --all
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GAMES = {l.split()[0]: l.split()[1:] for l in (REPO / "tools" / "engines.txt").read_text().splitlines()
         if l.strip() and not l.startswith("#")}


def detect(engine: str, folder: Path) -> list[str]:
    exe = Path(f"C:/scummvm-dev/{engine}/scummvm.exe")
    env = dict(os.environ, PATH="C:\\msys64\\ucrt64\\bin;" + os.environ.get("PATH", ""))
    out = subprocess.run([str(exe), "--detect", "--recursive", f"--path={folder}"], capture_output=True,
                         text=True, errors="replace", env=env, timeout=600).stdout
    found = []
    for line in out.splitlines():
        m = re.match(rf"^{engine}:\S+\s+(.+?)\s{{2,}}\S", line)
        if m:
            found.append(m.group(1).strip())
    return found


def check(engine: str) -> int:
    rows = []
    for game in GAMES.get(engine, []):
        discs = REPO / "games" / game / "discs"
        for edition in sorted(p for p in discs.iterdir() if p.is_dir()) if discs.exists() else []:
            rows.append((f"{game}/{edition.name}", detect(engine, edition)))
    print(f"## {engine}")
    for name, found in rows:
        if found:
            langs = sorted({re.sub(r".*/", "", f.rstrip(")")) for f in found})
            print(f"  ok   {name}: {len(found)} detected ({', '.join(langs)})")
        else:
            print(f"  --   {name}: not detected")
    return sum(not f for _, f in rows)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    engines = list(GAMES) if a == ["--all"] else a
    missing = sum(check(e) for e in engines)
    print(f"{missing} edition folder(s) not detected")
