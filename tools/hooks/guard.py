"""PreToolUse guard for agent sessions in this repo (wired in .claude/settings.json).

Blocks (exit 2, the reason goes back to the agent):
- git push/commit with --no-verify (the ScummVM pre-push hook keeps the harness private)
- any push to `origin` from the ScummVM clone or its worktrees (origin is upstream ScummVM)
- `git add -A`, `git add .`, `git add --renormalize` in this public repo (stage named paths)
- reading a big file whole: decompile dumps, logs and anything over 600 lines need
  offset/limit, or a grep first

    python tools/hooks/guard.py --selftest
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MAX_LINES = 600


def check(tool: str, args: dict, cwd: str) -> str | None:
    if tool == "Bash":
        cmd = args.get("command", "")
        if re.search(r"\bgit\b[^|;&]*\b(push|commit)\b[^|;&]*--no-verify", cmd):
            return "--no-verify is not allowed: the pre-push hook keeps DEV commits off GitHub."
        scummvm = "scummvm" in cmd.lower() or "scummvm" in cwd.lower()
        if scummvm and re.search(r"\bgit\b[^|;&]*\bpush\b[^|;&]*\borigin\b", cmd):
            return "origin is upstream ScummVM: push to `fork` (tools/publish.sh does it)."
        if re.search(r"\bgit\b[^|;&]*\badd\b[^|;&]*(\s-A\b|\s--all\b|\s\.(\s|$)|--renormalize)", cmd) and not scummvm:
            return "Stage named paths in this public repo (git add <paths>), never everything."
    elif tool == "Read" and not args.get("limit"):
        path = Path(args.get("file_path", ""))
        posix = path.as_posix()
        if "/notes/decomp/" in posix or path.suffix in (".log", ".tsv"):
            return f"{path.name}: grep it, or Read with offset/limit (decompile dumps and logs stay out of context)."
        try:
            with path.open("rb") as f:
                lines = sum(1 for _ in f)
        except OSError:
            return None
        if lines > MAX_LINES:
            return f"{path.name} has {lines} lines: grep for what you need, or Read with offset/limit."
    return None


def selftest() -> None:
    assert check("Bash", {"command": "git push --no-verify fork x"}, "")
    assert check("Bash", {"command": "git -C /c/scummvm push origin master"}, "")
    assert check("Bash", {"command": "git push fork grumpa"}, "C:/scummvm-dev/grumpa") is None
    assert check("Bash", {"command": "git add -A"}, "C:/x/Game Reimplementations")
    assert check("Bash", {"command": "git add --renormalize ."}, "C:/x/Game Reimplementations")
    assert check("Bash", {"command": "git add tools/build.sh"}, "C:/x/Game Reimplementations") is None
    assert check("Read", {"file_path": "C:/r/engines/ring/notes/decomp/all/x.c"}, "")
    assert check("Read", {"file_path": "C:/r/engines/ring/notes/decomp/all/x.c", "limit": 50}, "") is None
    assert check("Read", {"file_path": __file__}, "") is None
    print("guard selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
        sys.exit(0)
    event = json.load(sys.stdin)
    reason = check(event.get("tool_name", ""), event.get("tool_input", {}), event.get("cwd", ""))
    if reason:
        print(reason, file=sys.stderr)
        sys.exit(2)
