"""Spec check for docs/spec/render.md: the plane test and the screen winding agree.

For random cameras (eye near a scene vertex, random yaw, no pitch or roll) it projects
every poly of every .3DC the way render.md says (camera x right, y down, z forward;
sx = 320 + 480 x / z, sy = 240 + 480 y / z, truncated) and compares two culls the
original makes: the plane test of 0x44d980 (front when n . eye_local >= poly +0x30) and
the screen test of the drawers (drawn when the signed area is negative). They must
agree apart from integer snapping on nearly edge-on polys (E-0505).

    python engines/peintre/tools/winding_check.py
"""

from __future__ import annotations

import struct
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "parsers"))
import bfg  # noqa: E402


def i32(b: bytes, o: int) -> int:
    return struct.unpack_from("<i", b, o)[0]


def check_scene(b: bytes, rng, res: Counter, trials: int = 4) -> None:
    n = i32(b, 0)
    table = [i32(b, 4 + 4 * i) for i in range(n)]
    root = table[0]

    def tree(v):
        return root + v - 1

    world = {}  # node -> (rotation, position), parent * local

    def walk(nd, pr, pt):
        r = np.array(struct.unpack_from("<9i", b, nd + 0x28), float).reshape(3, 3) / 32768
        p = np.array(struct.unpack_from("<3i", b, nd + 0x1C), float)
        world[nd] = (pr @ r, pr @ p + pt)
        c = i32(b, nd + 0x14)
        while c:
            walk(tree(c), *world[nd])
            c = i32(b, tree(c) + 0x18)

    walk(root, np.eye(3), np.zeros(3))
    # a vertex moves with the node whose array holds it (shared vertices, E-0504)
    wpos = {}
    for nd in table:
        for k in range(i32(b, nd + 0x7C)):
            v = tree(i32(b, nd + 0x80)) + 40 * k
            wr, wt = world[nd]
            wpos[v] = wr @ np.array(struct.unpack_from("<3i", b, v + 4), float) + wt
    polys = []
    for nd in table:
        fg = i32(b, nd + 0xA4)
        while fg:
            g = tree(fg)
            for k in range(i32(b, g + 0x1C)):
                p = tree(i32(b, g + 0x20)) + i32(b, g + 0x2C) * k
                normal = np.array(struct.unpack_from("<3i", b, tree(i32(b, p + 0x2C))), float)
                if i32(b, p) & 8 or np.linalg.norm(normal) > 40000:
                    continue  # dynamic test / 63 garbage normals in the corpus
                polys.append((nd, normal, i32(b, p + 0x30),
                              [wpos[tree(i32(b, p + 8 + 12 * c))] for c in range(3)]))
            fg = i32(b, g)
    pts = np.array(list(wpos.values()))
    for _ in range(trials):
        eye = pts[rng.integers(len(pts))] + rng.uniform(-300, 300, 3)
        yaw = rng.uniform(0, 2 * np.pi)
        cam = np.array([[np.cos(yaw), 0, np.sin(yaw)], [0, 1, 0], [-np.sin(yaw), 0, np.cos(yaw)]])
        for nd, normal, d, verts in polys:
            wr, wt = world[nd]
            front = (normal @ (wr.T @ (eye - wt))) / 32768 - d >= 0
            c = [cam.T @ (w - eye) for w in verts]
            if min(v[2] for v in c) < 64:
                continue
            (x0, y0), (x1, y1), (x2, y2) = [(int(320 + 480 * v[0] / v[2]), int(240 + 480 * v[1] / v[2]))
                                            for v in c]
            area = (y2 - y1) * (x1 - x0) - (y1 - y0) * (x2 - x1)
            if abs(area) > 4:
                res["agree" if bool(front) == (area < 0) else "disagree"] += 1


def main() -> int:
    res, rng = Counter(), np.random.default_rng(1)
    for f in sorted(bfg.CORPUS.glob("*.BFG")):
        for name, _, data in bfg.read(f):
            if name.upper().endswith(".3DC"):
                check_scene(data[bfg.HEADER.size:], rng, res)
    total = res["agree"] + res["disagree"]
    print(f"plane test vs screen winding: {res['agree']}/{total} agree "
          f"({100 * res['agree'] / total:.1f}%)")
    return 0 if res["agree"] > 0.99 * total else 1


if __name__ == "__main__":
    sys.exit(main())
