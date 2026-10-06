"""Walk-mesh questions for the walkthrough and for scenarios (games/grumpa/docs/walkthrough.md).

Reads a scene's `.scn` (parsers/scn.py): the walk mesh (`CFXFloor`, faces joined by shared
edges, face type = view 0..4 or a special type, walking.md) and the scene links. Closed wall
types 19..21 (opened by floor opcode 6) are left out of the flood fill unless named open.

    python engines/grumpa/tools/walkplan.py reach [scene...]
        per entry: the exits its walk-mesh region touches, and which wall type opens more
    python engines/grumpa/tools/walkplan.py plan <scene> sx sy sz gx gy gz [open types...]
        grumpa_vm "hold x y;ticks n;where" commands that walk the player from s to g: the
        shortest face path, cut where the view (face type) changes (released for the fade
        to finish), each leg aimed at a point at most LOOKAHEAD units ahead in that leg's view
    python engines/grumpa/tools/walkplan.py route x y z <scene> <scene>...
        plans across scenes: from (x, y, z) in the first, then from each entry to the exit
    python engines/grumpa/tools/walkplan.py --selftest

The exit test uses a player sphere of PR units (a guess: Characters.abi radius, Q-0805 area);
the plan's tick counts assume SPEED units an update (measured from runs, rough), so put a
`where` after each leg and check it.
"""

from __future__ import annotations

import heapq
import math
import sys
from collections import defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "parsers"))
sys.path.insert(0, str(HERE))
import scn  # noqa: E402
import viewcheck as vc  # noqa: E402

SCENES = vc.CAB / "Scenes"
CLOSED = {19, 20, 21}
PR = 60.0       # player sphere radius for the exit test (rough)
SPEED = 2.0     # world units per update while walking (rough, from runs)
LOOKAHEAD = float(__import__("os").environ.get("LOOKAHEAD", 150))  # a leg aims at most this far ahead: the steering is by screen angle (E-0812)


def load(n: int):
    r = scn.parse((SCENES / ("Scene_%03d.scn" % n)).read_bytes())
    m = r[0x08]
    V = [v[:3] for v in m["verts"]]
    F, T = m["faces"], m["unk_face"]
    edge = defaultdict(list)
    for i, f in enumerate(F):
        for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
            edge[(min(a, b), max(a, b))].append(i)
    adj = defaultdict(set)
    for fs in edge.values():
        for i in fs:
            adj[i].update(j for j in fs if j != i)
    return V, F, T, adj, r[0x14]


def inside(V, f, x, z) -> bool:
    (ax, _, az), (bx, _, bz), (cx, _, cz) = (V[i] for i in f)
    d = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz)
    if abs(d) < 1e-9:
        return False
    u = ((bz - cz) * (x - cx) + (cx - bx) * (z - cz)) / d
    v = ((cz - az) * (x - cx) + (ax - cx) * (z - cz)) / d
    return u >= -1e-6 and v >= -1e-6 and u + v <= 1 + 1e-6


def face_at(V, F, x, y, z):
    best = None
    for i, f in enumerate(F):
        if inside(V, f, x, z):
            dy = abs(sum(V[k][1] for k in f) / 3 - y)
            if best is None or dy < best[0]:
                best = (dy, i)
    return best[1] if best else None


def flood(T, adj, start, closed):
    seen, q = {start}, deque([start])
    while q:
        i = q.popleft()
        for j in adj[i]:
            if j not in seen and T[j] not in closed:
                seen.add(j)
                q.append(j)
    return seen


def exits_hit(V, F, faces, exits) -> set:
    hit = set()
    for ex, ey, ez, r, s in exits:
        if any(math.dist((V[k][0], V[k][1] + PR, V[k][2]), (ex, ey, ez)) < r + PR
               for i in faces for k in F[i]):
            hit.add(s)
    return hit


def reach(n: int) -> list[str]:
    V, F, T, adj, links = load(n)
    exits = links["exits"]
    out = ["Scene %d: exits %s" % (n, sorted({e[4] for e in exits}))]
    for en in links["entries"]:
        x, y, z, *_, s = en
        fi = face_at(V, F, x, y, z)
        if fi is None:
            out.append("  from %d: entry off the mesh" % s)
            continue
        base = exits_hit(V, F, flood(T, adj, fi, CLOSED), exits)
        more = {}
        for t in sorted(set(T) & CLOSED):
            extra = exits_hit(V, F, flood(T, adj, fi, CLOSED - {t}), exits) - base
            if extra:
                more[t] = sorted(extra)
        out.append("  from %d: reaches %s%s" % (s, sorted(base), "; wall type opens %s" % more if more else ""))
    return out


def proj(scene: int, view: int, x, y, z):
    _, _, vm, pm = vc.views((SCENES / f"Scene_{scene:03d}.scn").read_bytes())[view]
    c = vc.xf(vc.xf((x, y, z, 1.0), vm), pm)
    return round((c[0] / c[3] + 1) * 400), round((1 - c[1] / c[3]) * 300)


def plan(scene: int, s, g, opened=(), stop_within: float = 0.0) -> str:
    V, F, T, adj, _ = load(scene)
    closed = CLOSED - set(opened)
    cen = [tuple(sum(V[k][i] for k in f) / 3 for i in range(3)) for f in F]
    a = face_at(V, F, *s)
    b = face_at(V, F, *g)
    if b is None:   # a goal off the mesh (a trigger sphere behind a gate): the nearest open face
        b = min((i for i in range(len(F)) if T[i] not in closed), key=lambda i: math.dist(cen[i], g))
    dist, prev, pq = {a: 0.0}, {}, [(0.0, a)]
    while pq:
        d, i = heapq.heappop(pq)
        if i == b:
            break
        if d > dist[i]:
            continue
        for j in adj[i]:
            nd = d + math.dist(cen[i], cen[j])
            if T[j] not in closed and nd < dist.get(j, 1e18):
                dist[j], prev[j] = nd, i
                heapq.heappush(pq, (nd, j))
    if b not in dist:
        raise SystemExit("no path on the open walk mesh")
    path = [b]
    while path[-1] != a:
        path.append(prev[path[-1]])
    path.reverse()
    pts = [s] + [cen[i] for i in path[1:-1]] + [g]
    if stop_within > 0:   # an exit: end at the first path point inside its sphere, so no leg
        k = next((i for i, q in enumerate(pts) if math.dist(q, g) < stop_within), len(pts) - 1)
        pts = pts[:max(k, 1) + 1]     # is left over to run in the next scene
        path = path[:len(pts)]
    views, v = [], T[a] if T[a] <= 4 else 0
    for i in path:
        v = T[i] if T[i] <= 4 else v
        views.append(v)
    cmds, cur, k, last = [], s, 0, views[0]
    while k < len(pts) - 1:
        vk = views[min(k, len(views) - 1)]
        if vk != last:
            cmds.append("release;ticks 60;where")   # the faded view change (185, 30) completes
            last = vk
        j, run = k + 1, math.dist(pts[k], pts[k + 1])
        while j < len(pts) - 1 and views[min(j, len(views) - 1)] == vk and run < LOOKAHEAD:
            run += math.dist(pts[j], pts[j + 1])
            j += 1
        sx, sy = proj(scene, vk, *pts[j])
        cmds.append("hold %d %d;ticks %d;where" % (max(1, min(799, sx)), max(1, min(599, sy)),
                                                   int(math.dist(cur, pts[j]) / SPEED) + 5))
        cur, k = pts[j], j
    if stop_within > 0:   # then straight at the exit's centre, with time to spare
        sx, sy = proj(scene, last, *g)
        cmds.append("hold %d %d;ticks %d;where" % (max(1, min(799, sx)), max(1, min(599, sy)),
                                                   int(math.dist(cur, g) / SPEED) + 60))
    cmds.append("release;ticks 10;where")
    return ";".join(cmds)


def route(scenes: list[int], start=None) -> str:
    """Walk through scenes[0] -> scenes[1] -> ...: in each scene from the entry of the scene
    left (or `start`) to the exit sphere leading to the next; `ticks 120` for the fade."""
    out = []
    for a, b in zip(scenes, scenes[1:]):
        links = load(a)[4]
        s = start
        if s is None:
            s = next(e[:3] for e in links["entries"] if e[6] == prev)
        ex = next(e for e in links["exits"] if e[4] == b)
        out.append(plan(a, s, ex[:3], stop_within=ex[3] * 0.8).replace("release;ticks 10;where", "release;ticks 120;where"))
        prev, start = a, None
    return ";".join(out)


def selftest() -> None:
    V = [(0, 0, 0), (10, 0, 0), (0, 0, 10), (10, 0, 10)]
    assert inside(V, (0, 1, 2), 2, 2) and not inside(V, (0, 1, 2), 9, 9)
    assert face_at(V, [(0, 1, 2), (1, 3, 2)], 9, 0, 9) == 1
    adj = {0: {1}, 1: {0}}
    assert flood([0, 19], adj, 0, CLOSED) == {0} and flood([0, 19], adj, 0, set()) == {0, 1}
    # corpus facts the walkthrough cites (E-1802): banana guard and roots walls gate exits
    assert any("wall type opens {19: [6]}" in l for l in reach(5))
    assert any("from 10: reaches [10]; wall type opens {19: [8, 309]}" in l for l in reach(7))
    print("selftest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--selftest"]:
        selftest()
    elif a[:1] == ["reach"]:
        nums = [int(x) for x in a[1:]] or sorted(int(p.stem[6:]) for p in SCENES.glob("Scene_*.scn"))
        for n in nums:
            print("\n".join(reach(n)))
    elif a[:1] == ["route"]:   # route <x> <y> <z> <scene> <scene>...: start in the first
        print(route([int(x) for x in a[4:]], tuple(map(float, a[1:4]))))
    elif a[:1] == ["plan"]:
        print(plan(int(a[1]), tuple(map(float, a[2:5])), tuple(map(float, a[5:8])), tuple(map(int, a[8:]))))
    else:
        print(__doc__)
