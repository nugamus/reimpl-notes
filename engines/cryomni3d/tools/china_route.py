# /// script
# requires-python = ">=3.11"
# dependencies = ["capstone"]
# ///
"""Shortest route between two China places, as the zones to click.

Reads the place statement trees (`china_places.py --json`, E-0710..E-0712). Edges are the
go/look/take zones with a target created by a place's entry part, numbered in creation
order as places-logic.md does (a zone created under a condition, and every zone after it,
has no fixed index and is printed as `?`). By default only zones enabled at creation are
used; `--any` also uses zones created disabled and gotos in a place's event code under
`if zone == n` (those depend on game state: read the place's logic), at a cost of 100
clicks each, so the route uses as few of them as it can.

    uv run engines/cryomni3d/tools/china_route.py pne140 cpc110
    uv run engines/cryomni3d/tools/china_route.py --any pne140 pne210
    uv run engines/cryomni3d/tools/china_route.py --selftest
"""

from __future__ import annotations

import json
import subprocess
import sys
import heapq
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGETED = {"zone_goto", "zone_type2", "zone_take"}  # go, look, take: args [rect, disabled, target, ...]
ZONE_ADD = TARGETED | {"zone_type6", "zone_type9", "zone_label", "zone_doc"}
KIND = {"zone_goto": "go", "zone_type2": "look", "zone_take": "take"}


def zone_of(cond) -> int | None:
    """The n of a condition `zone == n` (alone, or the first inside an `and`/`or`)."""
    if isinstance(cond, dict):
        if cond.get("cmp") == "==" and cond.get("lhs") == {"zone": True}:
            return cond["rhs"]
        for c in cond.get("and", []) + cond.get("or", []):
            n = zone_of(c)
            if n is not None:
                return n
    return None


def edges(place: dict) -> list[dict]:
    """Edges {to, zone, kind, off, code} out of one place."""
    out, idx = [], [0]

    def entry(stmts, nested):
        for s in stmts:
            if s.get("op") == "if":
                entry(s["then"], True)
                entry(s["else"], True)
            elif s.get("op") == "call" and s["fn"] in ZONE_ADD:
                if nested:
                    idx[0] = None
                i = idx[0]
                if s["fn"] in TARGETED and s["args"][2]:
                    out.append({"to": s["args"][2], "zone": i, "kind": KIND[s["fn"]],
                                "off": bool(s["args"][1]), "code": False})
                if i is not None:
                    idx[0] += 1

    def event(stmts, zone):
        for s in stmts:
            if s.get("op") == "if":
                z = zone_of(s["cond"])
                event(s["then"], z if z is not None else zone)
                event(s["else"], zone)
            elif s.get("op") == "call" and s["fn"] == "goto" and zone is not None:
                out.append({"to": s["args"][0], "zone": zone, "kind": "code", "off": False, "code": True})

    entry(place["entry"], False)
    event(place["event"], None)
    return out


def graph(places: list[dict], any_edge: bool) -> dict[str, list[dict]]:
    return {p["name"]: [e for e in edges(p) if any_edge or not (e["off"] or e["code"])] for p in places}


def route(g: dict[str, list[dict]], src: str, dst: str) -> list[tuple[str, dict]] | None:
    """Cheapest path (Dijkstra): a plain zone costs 1, a disabled zone or code goto 100."""
    best, prev, q = {src: 0}, {src: None}, [(0, src)]
    while q:
        cost, a = heapq.heappop(q)
        if a == dst:
            path = []
            while prev[a]:
                path.append(prev[a])
                a = prev[a][0]
            return path[::-1]
        if cost > best[a]:
            continue
        for e in g.get(a, []):
            c = cost + (100 if e["off"] or e["code"] else 1)
            if c < best.get(e["to"], 1 << 30):
                best[e["to"]], prev[e["to"]] = c, (a, e)
                heapq.heappush(q, (c, e["to"]))
    return None


def fmt(step: tuple[str, dict]) -> str:
    a, e = step
    z = "?" if e["zone"] is None else e["zone"]
    flag = " (code goto)" if e["code"] else " (off at entry)" if e["off"] else ""
    return f"{a} zone {z} {e['kind']} -> {e['to']}{flag}"


def selftest() -> None:
    go = lambda t, off=0: {"op": "call", "fn": "zone_goto", "args": [[0, 0, 1, 1], off, t, 0, -1.0, -1.0]}
    places = [
        {"name": "a", "entry": [go("b"), {"op": "call", "fn": "zone_type9", "args": [[0, 0, 1, 1], 1]}, go("c", 1)],
         "event": [{"op": "if", "cond": {"cmp": "==", "lhs": {"zone": True}, "rhs": 1},
                    "then": [{"op": "call", "fn": "goto", "args": ["d"]}], "else": []}]},
        {"name": "b", "entry": [{"op": "if", "cond": {}, "then": [go("x")], "else": []}, go("c")], "event": []},
        {"name": "c", "entry": [go("a")], "event": []},
        {"name": "d", "entry": [], "event": []},
    ]
    g = graph(places, False)
    assert [fmt(s) for s in route(g, "a", "c")] == ["a zone 0 go -> b", "b zone ? go -> c"]
    assert route(g, "a", "d") is None
    ga = graph(places, True)
    assert [fmt(s) for s in route(ga, "a", "c")] == ["a zone 0 go -> b", "b zone ? go -> c"]  # 2 beats 100
    assert [fmt(s) for s in route(ga, "a", "d")] == ["a zone 1 code -> d (code goto)"]
    places[0]["event"][0]["cond"] = {"or": [{"cmp": "==", "lhs": {"zone": True}, "rhs": 3}, {"cmp": "==", "lhs": {"zone": True}, "rhs": 4}]}
    places[1]["entry"].append(go("d", 1))
    ga = graph(places, True)  # a -> b -(off)-> d costs 101, the code goto 100
    assert [fmt(s) for s in route(ga, "a", "d")] == ["a zone 3 code -> d (code goto)"]
    assert route(g, "a", "a") == []
    print("china_route selftest ok")


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        selftest()
        return 0
    any_edge = "--any" in argv
    names = [a for a in argv if a != "--any"]
    if len(names) != 2:
        print(__doc__)
        return 2
    data = subprocess.run([sys.executable, str(HERE / "china_places.py"), "--json"],
                          capture_output=True, text=True, check=True).stdout
    path = route(graph(json.loads(data), any_edge), *names)
    if path is None:
        print(f"no route {names[0]} -> {names[1]}" + ("" if any_edge else " (try --any)"))
        return 1
    for s in path:
        print(fmt(s))
    print(f"# {len(path)} clicks")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
