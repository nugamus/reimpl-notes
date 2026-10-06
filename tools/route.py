"""How do I get from one place in the game to another? Answered from the game's own data,
so scenarios start where they should without anyone wandering (rule 7).

Reads `engines/<engine>/notes/graph.json`, written by the engine's own extractor from the
corpus (Grumpa: `engines/grumpa/tools/scenegraph.py --graph`). The format, the same for
every engine:

    {"engine": "...", "start": "<node>", "nodes": ["<node>", ...],
     "edges": [{"from": "<node>", "to": "<node>", "action": "what fires it",
                "input": "<harness input that fires it>", "guarded": true|false}, ...]}

Prints the shortest route (fewest edges; unguarded edges only, unless --guarded) and the
harness inputs joined, ready to paste after the teleport in a scenario's keys. Guarded
edges have conditions (an item, a flag) the route must satisfy first; prefer a save or the
teleport to the scene before it.

    python tools/route.py grumpa 1 211
    python tools/route.py grumpa 1 61 --guarded
    python tools/route.py grumpa --reachable          # what the start reaches, and what not
    python tools/route.py --selftest
"""

from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def shortest(graph: dict, src: str, dst: str, guarded: bool) -> list[dict] | None:
    adj: dict[str, list[dict]] = {}
    for e in graph["edges"]:
        if guarded or not e.get("guarded"):
            adj.setdefault(e["from"], []).append(e)
    prev: dict[str, dict | None] = {src: None}
    q = deque([src])
    while q:
        n = q.popleft()
        if n == dst:
            path = []
            while prev[n] is not None:
                path.append(prev[n])
                n = prev[n]["from"]
            return path[::-1]
        for e in adj.get(n, []):
            if e["to"] not in prev:
                prev[e["to"]] = e
                q.append(e["to"])
    return None


def reachable(graph: dict, src: str, guarded: bool) -> set[str]:
    seen, q = {src}, deque([src])
    while q:
        n = q.popleft()
        for e in graph["edges"]:
            if e["from"] == n and (guarded or not e.get("guarded")) and e["to"] not in seen:
                seen.add(e["to"])
                q.append(e["to"])
    return seen


def main(argv: list[str]) -> int:
    guarded = "--guarded" in argv
    args = [a for a in argv if not a.startswith("--")]
    graph_file = REPO / "engines" / args[0] / "notes" / "graph.json"
    if not graph_file.exists():
        print(f"no {graph_file.relative_to(REPO)}: write the engine's graph extractor first")
        return 1
    graph = json.loads(graph_file.read_text(encoding="utf-8"))
    if "--reachable" in argv:
        r = reachable(graph, graph["start"], guarded)
        rest = sorted(set(graph["nodes"]) - r, key=lambda s: (len(s), s))
        print(f"from {graph['start']}: {len(r)} of {len(graph['nodes'])} reachable"
              f"{' (guarded edges included)' if guarded else ' without conditions'}; not: {' '.join(rest[:60])}")
        return 0
    src, dst = args[1], args[2]
    path = shortest(graph, src, dst, guarded)
    if path is None:
        print(f"no route {src} -> {dst}" + ("" if guarded else " without conditions (try --guarded)"))
        return 1
    for e in path:
        print(f"{e['from']} -> {e['to']}: {e['action']}{'  [guarded]' if e.get('guarded') else ''}")
    print("inputs: " + ";".join(e["input"] for e in path if e.get("input")))
    return 0


def selftest() -> None:
    g = {"start": "1", "nodes": ["1", "2", "3", "4"], "edges": [
        {"from": "1", "to": "2", "action": "a", "input": "click 1 1"},
        {"from": "2", "to": "3", "action": "b", "input": "click 2 2", "guarded": True},
        {"from": "1", "to": "4", "action": "c", "input": "click 3 3"},
        {"from": "4", "to": "3", "action": "d", "input": "click 4 4"}]}
    assert [e["action"] for e in shortest(g, "1", "3", False)] == ["c", "d"]
    assert len(shortest(g, "1", "3", True)) == 2
    assert reachable(g, "1", False) == {"1", "2", "3", "4"}
    assert shortest(g, "3", "1", True) is None
    print("route selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif len(sys.argv) >= 3:
        sys.exit(main(sys.argv[1:]))
    else:
        print(__doc__)
        sys.exit(2)
