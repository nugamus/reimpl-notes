"""PostToolUse hook: one line per tool call in logs/tool-usage.tsv (time, session, tool, a
short detail), so `python tools/usage.py` can show what sessions actually spend their
calls on. Fast and silent; never blocks."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

LOG = Path(__file__).resolve().parents[2] / "logs" / "tool-usage.tsv"


def detail(tool: str, args: dict) -> str:
    if tool == "Bash":
        cmd = args.get("command", "").strip().split()
        words = [w for w in cmd[:6] if not w.startswith("-")]
        return " ".join(words[:3])[:80]
    for key in ("file_path", "path", "pattern", "url", "subagent_type", "skill", "program"):
        if args.get(key):
            return str(args[key])[-80:]
    return ""


def main() -> None:
    try:
        event = json.load(sys.stdin)
        tool = event.get("tool_name", "")
        line = "\t".join([time.strftime("%Y-%m-%d %H:%M:%S"), event.get("session_id", "")[:8], tool,
                          detail(tool, event.get("tool_input", {})).replace("\t", " ").replace("\n", " ")])
        LOG.parent.mkdir(exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass  # telemetry must never break a session


if __name__ == "__main__":
    main()
