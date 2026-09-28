"""Where can the viewer walk? Collision (movement.md "Collision" and "Floor") run over a
scene's box sets, flood-filled from a start point in steps of one tick's walk.

  python boxreach.py musee 1 [--start x,y,z] [--map out.txt]

Prints the reachable (x, z) bounds and an ASCII map (one cell = 100 units, '#' = a wall
face, '.' = reached, 'S' = start). Only the rules of the spec: no engine code.
"""
import argparse
import math
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "parsers"))
import bfg  # noqa: E402

R = 250
EYE = 700


def load_boxes(scene, names):
    entries = {n.upper(): d for n, _, d in bfg.read(bfg.CORPUS / f"{scene}.BFG")}
    faces = []
    for name in names:
        body = entries[name.upper()][bfg.HEADER.size:]
        nv, pv, nf, pf, ni, pi = struct.unpack_from("<6i", body)
        for k in range(nf):
            o = pf - 1 + 0x60 * k
            w = struct.unpack_from("<24i", body, o)
            v = [struct.unpack_from("<3i", body, w[i] - 1) for i in range(3)]
            n = struct.unpack_from("<3i", body, w[3] - 1)
            faces.append(dict(v=v, n=n, D=w[4], e=[(w[5 + 3 * j:8 + 3 * j], w[14 + j]) for j in range(3)],
                              lo=w[18:21], hi=w[21:24]))
    return faces


def t15(a, b):
    """(a * b) >> 15 rounded toward zero, as the original's integer dot products."""
    x = a * b
    return -((-x) >> 15) if x < 0 else x >> 15


def dot15(n, c):
    return t15(n[0], c[0]) + t15(n[1], c[1]) + t15(n[2], c[2])


def seg_closest(c, a, b):
    ab = [b[i] - a[i] for i in range(3)]
    L = sum(x * x for x in ab)
    t = 0 if L == 0 else max(0, min(1, sum((c[i] - a[i]) * ab[i] for i in range(3)) / L))
    return [a[i] + ab[i] * t for i in range(3)]


BUCKET = 1000


def near(faces, c):
    """The faces whose (x, z) box comes within R of c (a speed-up; same result)."""
    key = (c[0] // BUCKET, c[2] // BUCKET)
    hit = _index.get((id(faces), key))
    if hit is None:
        x0, z0 = key[0] * BUCKET - R - 200, key[1] * BUCKET - R - 200
        x1, z1 = x0 + BUCKET + 2 * R + 400, z0 + BUCKET + 2 * R + 400
        hit = [f for f in faces if not (f["hi"][0] < x0 or f["lo"][0] > x1 or f["hi"][2] < z0 or f["lo"][2] > z1)]
        _index[(id(faces), key)] = hit
    return hit


_index = {}


def collide(all_faces, c):
    faces = near(all_faces, c)
    F = [0, 0, 0]; N = [0, 0, 0]; E = [0, 0, 0]; nf = ne = 0
    for f in faces:
        if any(c[i] + R < f["lo"][i] or c[i] - R > f["hi"][i] for i in range(3)):
            continue
        n = f["n"]
        d = dot15(n, c) - f["D"]
        if not (-R < d < R) or d < 0:
            continue
        e = [dot15(en, c) - ed for en, ed in f["e"]]
        if min(e) < -R:
            continue
        mask = sum(1 << k for k in range(3) if e[k] < 0)
        v = f["v"]
        if mask == 7:
            continue  # the original reuses a stale point here
        if mask == 0:
            t = sum(n[i] * (c[i] - v[0][i]) for i in range(3)) / sum(x * x for x in n)
            q = [c[i] - n[i] * t for i in range(3)]
        elif mask in (1, 2, 4):
            k = {1: 0, 2: 1, 4: 2}[mask]
            q = seg_closest(c, v[k], v[(k + 1) % 3])
        else:
            q = list(v[{3: 1, 5: 0, 6: 2}[mask]])
        p = [int(x) for x in q]
        if mask == 0:
            F = [F[i] + p[i] for i in range(3)]; N = [N[i] + n[i] for i in range(3)]; nf += 1
        elif sum((p[i] - c[i]) ** 2 for i in range(3)) < R * R and nf == 0:
            E = [E[i] + p[i] for i in range(3)]; ne += 1
    if nf:
        c = [int(math.trunc(math.trunc(math.trunc(N[i] / nf) * R / 32768) + F[i] / nf)) for i in range(3)]
    elif ne:
        e = [E[i] / ne for i in range(3)]
        d = [math.trunc(c[i] - e[i]) for i in range(3)]
        L = math.sqrt(sum(x * x for x in d))
        if L:
            c = [int(math.trunc(math.trunc(d[i] * R / L) + e[i])) for i in range(3)]
    # Floor
    faces = near(all_faces, c)
    best = None
    for f in faces:
        if c[0] + R < f["lo"][0] or c[0] - R > f["hi"][0] or c[2] + R < f["lo"][2] or c[2] - R > f["hi"][2]:
            continue
        n = f["n"]
        if n[1] == 0:
            continue
        v = f["v"]
        s = [(v[(k + 1) % 3][0] - v[k][0]) * (c[2] - v[k][2]) - (v[(k + 1) % 3][2] - v[k][2]) * (c[0] - v[k][0])
             for k in range(3)]
        if not (min(s) >= 0 or max(s) <= 0):
            continue
        if dot15(n, c) - f["D"] < 0:
            continue
        yf = (f["D"] * 32768 - n[0] * c[0] - n[2] * c[2]) / n[1]
        if yf > c[1] and (best is None or yf < best):
            best = yf
    if best is not None:
        c[1] = int(best - EYE)
    else:
        c[1] += 10  # falling
    return c


def crosses(all_faces, a, b):
    """Bug fix (not in the original): did the centre go from a wall's front to behind it,
    through the triangle, this tick?"""
    for f in near(all_faces, b):
        n = f["n"]
        if abs(n[1]) > 16384:
            continue  # floors and slopes
        da = dot15(n, a) - f["D"]
        db = dot15(n, b) - f["D"]
        if not (da >= 0 > db):
            continue
        t = da / (da - db)
        q = [a[i] + (b[i] - a[i]) * t for i in range(3)]
        if min(dot15(en, [int(x) for x in q]) - ed for en, ed in f["e"]) >= 0:
            return True
    return False


FIX = True


def reach(faces, start, step=120, dirs=16, cell=60, limit=200000):
    seen = {}
    todo = [list(start)]
    while todo and len(seen) < limit:
        c = todo.pop()
        key = (c[0] // cell, c[2] // cell)
        if key in seen:
            continue
        seen[key] = tuple(c)
        for k in range(dirs):
            a = 2 * math.pi * k / dirs
            n = [c[0] + int(step * math.sin(a)), c[1], c[2] + int(step * math.cos(a))]
            n = collide(faces, n)
            if FIX and crosses(faces, c, n):
                n = list(c)
            if n[1] > 5000:  # fell out of the world
                continue
            if (n[0] // cell, n[2] // cell) not in seen:
                todo.append(n)
    return seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("sets", nargs="*", help="extra box set numbers (BOX<n>.3DI)")
    ap.add_argument("--start", default="-39,-209,361")
    ap.add_argument("--map")
    a = ap.parse_args()
    faces = load_boxes(a.scene, ["BOX.3DI"] + [f"BOX{s}.3DI" for s in a.sets])
    start = [int(x) for x in a.start.split(",")]
    seen = reach(faces, start)
    xs = [p[0] for p in seen.values()]; zs = [p[2] for p in seen.values()]
    print(f"{len(seen)} cells; x {min(xs)}..{max(xs)}, z {min(zs)}..{max(zs)}")
    if a.map:
        wx = [v[0] for f in faces for v in f["v"]]; wz = [v[2] for f in faces for v in f["v"]]
        x0, x1, z0, z1 = min(wx), max(wx), min(wz), max(wz)
        W, H = (x1 - x0) // 100 + 1, (z1 - z0) // 100 + 1
        grid = [[" "] * W for _ in range(H)]
        for f in faces:
            if f["n"][1] != 0 and abs(f["n"][1]) > 20000:
                continue  # floors and ceilings
            for k in range(3):
                a0, b0 = f["v"][k], f["v"][(k + 1) % 3]
                for t in range(21):
                    q = [a0[i] + (b0[i] - a0[i]) * (t / 20) for i in range(3)]
                    grid[int(q[2] - z0) // 100][int(q[0] - x0) // 100] = "#"
        for p in seen.values():
            gx, gz = (p[0] - x0) // 100, (p[2] - z0) // 100
            if 0 <= gx < W and 0 <= gz < H and grid[gz][gx] == " ":
                grid[gz][gx] = "."
        gx, gz = (start[0] - x0) // 100, (start[2] - z0) // 100
        grid[gz][gx] = "S"
        with open(a.map, "w") as out:
            out.write(f"x {x0}..{x1} left to right, z {z1}..{z0} top to bottom, 100 per cell\n")
            for row in reversed(grid):
                out.write("".join(row) + "\n")


if __name__ == "__main__":
    main()
