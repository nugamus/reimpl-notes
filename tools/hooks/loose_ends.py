"""Stop hook: before a session ends, check nothing is left half-done.

Looks for uncommitted or unpushed work in this repo, uncommitted changes or unpublished
commits in the engines' dev worktrees, and a failed CI run on the fork's master. If it finds
any, it asks the agent once to finish (or to say why not) by blocking the stop; a second
stop goes through (stop_hook_active), so it can never loop. Paths the user keeps
uncommitted on purpose go in .claude/loose-ends-ignore, one per line.

    python tools/hooks/loose_ends.py --check     # print what it would say
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ENGINES = [l.split()[0] for l in (Path(__file__).resolve().parents[2] / "tools" / "engines.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
GIT = "git"


def run(*cmd: str, cwd: Path | None = None) -> str:
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def findings() -> list[str]:
    out = []
    ignore_file = REPO / ".claude" / "loose-ends-ignore"
    ignore = set(ignore_file.read_text().split()) if ignore_file.exists() else set()
    dirty = [l[3:] for l in run(GIT, "status", "--porcelain", cwd=REPO).splitlines() if l[3:] not in ignore]
    if dirty:
        out.append(f"reimpl-notes has uncommitted changes: {', '.join(dirty[:6])}")
    if run(GIT, "log", "--oneline", "origin/main..main", cwd=REPO).strip():
        out.append("reimpl-notes has commits not pushed to origin/main")
    for e in ENGINES:
        wt = Path(f"C:/scummvm-dev/{e}")
        if not wt.exists():
            continue
        if [l for l in run(GIT, "status", "--porcelain", "--untracked-files=no", cwd=wt).splitlines()]:
            out.append(f"{e}-dev has uncommitted changes in {wt}")
        new = [l for l in run(GIT, "cherry", e, f"{e}-dev", cwd=wt).splitlines() if l.startswith("+")]
        subjects = [run(GIT, "log", "-1", "--format=%s", l[2:], cwd=wt).strip() for l in new]
        unpublished = [s for s in subjects if not s.startswith(("DEV:", "BRIDGE:"))]
        if unpublished:
            out.append(f"{e}-dev has {len(unpublished)} commit(s) not published (bash tools/publish.sh {e})")
    ci = run("gh", "run", "list", "-R", "nugamus/scummvm", "-L", "1", "--json", "conclusion,headSha",
             "--jq", ".[0].conclusion")
    if ci.strip() == "failure":
        out.append("the last CI run on nugamus/scummvm master failed (gh run list -R nugamus/scummvm -L 3)")
    return out


def main() -> int:
    if sys.argv[1:] == ["--check"]:
        print("\n".join(findings()) or "nothing left open")
        return 0
    event = json.load(sys.stdin)
    if event.get("stop_hook_active"):
        return 0
    found = findings()
    if found:
        print("Before stopping, finish or explain: " + "; ".join(found) +
              ". If this is deliberate or you are waiting for the user, say so briefly and stop.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
