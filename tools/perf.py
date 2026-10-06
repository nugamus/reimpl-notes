"""Did a scenario get slower? Reads logs/perf.tsv (scenario.py appends every normal run's
wall time) and flags a scenario whose latest run is more than 40% slower than the median of
its previous ten runs (and at least half a second slower, so tiny runs don't flap). Scenarios
are deterministic, so a jump is the engine, not the game. The nightly run reports these.

    python tools/perf.py [engine]
    python tools/perf.py --selftest
"""

from __future__ import annotations

import statistics
import sys
from collections import defaultdict
from pathlib import Path

LOG = Path(__file__).resolve().parents[1] / "logs" / "perf.tsv"


def slower(rows: list[list[str]], engine: str | None) -> list[str]:
    runs = defaultdict(list)
    for r in rows:
        if len(r) == 4 and (engine is None or r[1] == engine):
            runs[(r[1], r[2])].append(float(r[3]))
    out = []
    for (e, name), ts in sorted(runs.items()):
        if len(ts) < 4:
            continue
        base = statistics.median(ts[-11:-1])
        if ts[-1] > base * 1.4 and ts[-1] - base > 0.5:
            out.append(f"SLOW {e}/{name}: {ts[-1]:.1f}s, median of the last runs {base:.1f}s")
    return out


def selftest() -> None:
    rows = [["t", "g", "a", "2.0"]] * 6 + [["t", "g", "a", "3.5"], ["t", "g", "b", "1.0"]]
    assert slower(rows, None) == ["SLOW g/a: 3.5s, median of the last runs 2.0s"], slower(rows, None)
    assert slower(rows[:6] + [["t", "g", "a", "2.4"]], None) == []
    print("perf selftest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
        sys.exit(0)
    rows = [l.split("\t") for l in LOG.read_text(encoding="utf-8").splitlines()] if LOG.exists() else []
    found = slower(rows, a[0] if a else None)
    print("\n".join(found) or "no scenario got slower")
    sys.exit(1 if found else 0)
