"""What do sessions spend their tool calls on? Reads logs/tool-usage.tsv (the usage_log hook).

    python tools/usage.py               # all sessions: calls per tool, top commands and files
    python tools/usage.py --sessions    # one line per session: calls, Ghidra share, reads
    python tools/usage.py --selftest
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "logs" / "tool-usage.tsv"


def load(text: str) -> list[list[str]]:
    return [l.split("\t") for l in text.splitlines() if l.count("\t") >= 3]


def summary(rows: list[list[str]]) -> str:
    tools = Counter("ghidra (MCP)" if r[2].startswith("mcp__ghidra") else r[2] for r in rows)
    bash = Counter(r[3].split()[0] if r[3] else "" for r in rows if r[2] == "Bash")
    reads = Counter(r[3] for r in rows if r[2] == "Read")
    out = [f"{len(rows)} calls in {len({r[1] for r in rows})} sessions", "", "by tool:"]
    out += [f"  {n:6} {t}" for t, n in tools.most_common(12)]
    out += ["", "top shell commands:"] + [f"  {n:6} {c}" for c, n in bash.most_common(8)]
    out += ["", "most re-read files:"] + [f"  {n:6} {f}" for f, n in reads.most_common(8) if n > 1]
    return "\n".join(out)


def sessions(rows: list[list[str]]) -> str:
    by = defaultdict(list)
    for r in rows:
        by[r[1]].append(r)
    out = ["first call           session   calls  ghidra  reads  bash"]
    for s, rs in sorted(by.items(), key=lambda kv: kv[1][0][0]):
        g = sum(r[2].startswith("mcp__ghidra") for r in rs)
        out.append(f"{rs[0][0]}  {s:8}  {len(rs):5}  {g:6}  {sum(r[2] == 'Read' for r in rs):5}  "
                   f"{sum(r[2] == 'Bash' for r in rs):4}")
    return "\n".join(out)


def selftest() -> None:
    rows = load("t\ts1\tRead\ta.md\nt\ts1\tRead\ta.md\nt\ts2\tmcp__ghidra__decompile_function\t\nt\ts2\tBash\tgit status\n")
    s = summary(rows)
    assert "4 calls in 2 sessions" in s and "ghidra (MCP)" in s and "a.md" in s, s
    assert len(sessions(rows).splitlines()) == 3
    print("usage selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
        sys.exit(0)
    rows = load(LOG.read_text(encoding="utf-8")) if LOG.exists() else []
    print(sessions(rows) if sys.argv[1:] == ["--sessions"] else summary(rows))
