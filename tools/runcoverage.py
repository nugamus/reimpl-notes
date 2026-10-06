"""Which script opcodes, handlers, rooms ... did the scenarios actually exercise?

Convention: an engine prints `cov <kind> <id>` on its `coverage` debug channel wherever it
dispatches something worth counting, e.g. `debugC(1, kDebugCoverage, "cov opcode %d", op)`
in the script VM, `"cov room %d"` on entering a room, `"cov handler %s"` in an event table.
`uv run tools/scenario.py <engine> --coverage` runs every scenario with that channel on and
keeps the logs; this tool counts what ran. With `engines/<engine>/tests/coverage.txt` (the
universe, one `<kind> <id>` per line, written from the spec: every opcode the format
defines, every room in the game) it also lists what never ran, which is where untested
behaviour and bugs hide.

    python tools/runcoverage.py grumpa
    python tools/runcoverage.py --selftest
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
COV = re.compile(r"\bcov (\w+) (\S+)")


def gather(logs: list[str]) -> Counter:
    seen = Counter()
    for text in logs:
        for kind, ident in COV.findall(text):
            seen[(kind, ident)] += 1
    return seen


def report(seen: Counter, universe: list[tuple[str, str]]) -> str:
    kinds = defaultdict(set)
    for kind, ident in seen:
        kinds[kind].add(ident)
    lines = []
    for kind in sorted(set(kinds) | {k for k, _ in universe}):
        want = {i for k, i in universe if k == kind}
        got = kinds.get(kind, set())
        if want:
            missing = sorted(want - got, key=lambda s: (len(s), s))
            lines.append(f"{kind}: {len(got & want)}/{len(want)} exercised"
                         + (f"; never: {' '.join(missing[:40])}{' ...' if len(missing) > 40 else ''}" if missing else ""))
            extra = got - want
            if extra:
                lines.append(f"  {kind} seen but not in coverage.txt: {' '.join(sorted(extra)[:20])}")
        else:
            lines.append(f"{kind}: {len(got)} distinct seen (no universe in coverage.txt)")
    return "\n".join(lines) or "no `cov` lines in the logs: is the engine instrumented, and was --coverage used?"


def main(engine: str) -> int:
    logs = [p.read_text(encoding="utf-8", errors="replace")
            for p in (REPO / "engines" / engine / "tests" / "out").glob("*/run.log")]
    uni_file = REPO / "engines" / engine / "tests" / "coverage.txt"
    universe = []
    if uni_file.exists():
        for l in uni_file.read_text(encoding="utf-8").splitlines():
            parts = l.split()
            if len(parts) >= 2 and not l.startswith("#"):
                universe.append((parts[0], parts[1]))
    print(f"{engine}: {len(logs)} scenario logs")
    print(report(gather(logs), universe))
    return 0


def selftest() -> None:
    seen = gather(["x cov opcode 1\ncov opcode 1\ncov opcode 7\n", "cov room 12"])
    assert seen[("opcode", "1")] == 2 and seen[("room", "12")] == 1
    r = report(seen, [("opcode", "1"), ("opcode", "2"), ("opcode", "7")])
    assert "opcode: 2/3 exercised; never: 2" in r and "room: 1 distinct" in r, r
    print("runcoverage selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif len(sys.argv) == 2:
        sys.exit(main(sys.argv[1]))
    else:
        print(__doc__)
        sys.exit(2)
