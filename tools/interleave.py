"""Interleave several branches' commit lists into one timeline without reordering any
branch: repeatedly take the branch whose next commit is oldest. Input on stdin, one
`<branch> <author-time> <sha>` line per commit, each branch's lines in its own order;
output the shas, one per line.

    python interleave.py --selftest
"""

from __future__ import annotations

import sys
from collections import OrderedDict


def interleave(lines: list[str]) -> list[str]:
    queues: "OrderedDict[str, list[tuple[int, str]]]" = OrderedDict()
    for line in lines:
        branch, at, sha = line.split()
        queues.setdefault(branch, []).append((int(at), sha))
    heads = {b: 0 for b in queues}
    out = []
    while True:
        live = [b for b in queues if heads[b] < len(queues[b])]
        if not live:
            return out
        b = min(live, key=lambda k: queues[k][heads[k]][0])
        out.append(queues[b][heads[b]][1])
        heads[b] += 1


def selftest() -> None:
    lines = ["a 10 a1", "a 30 a2", "a 20 a3", "b 15 b1", "b 25 b2"]
    assert interleave(lines) == ["a1", "b1", "b2", "a2", "a3"], interleave(lines)
    print("interleave selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        print("\n".join(interleave([l for l in sys.stdin.read().splitlines() if l.strip()])))
