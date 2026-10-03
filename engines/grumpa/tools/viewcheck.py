"""Check the scene-view model (docs/spec/scene.md, E-0301, E-0302) against the corpus.

    python engines/grumpa/tools/viewcheck.py mesh <scene> <mesh.anb> <view>
        project a mesh through the view's .scn matrices: screen bbox, and its z/w*65535
        minus the view's _IZ.fxi depth under each vertex (near 0 = it sits on the surface)
    python engines/grumpa/tools/viewcheck.py sprites <scene>
        each placed 0x0d sprite: view, layer, colour key, and its mean difference to every
        view's background at its position (an opaque sprite matches its own view's)
    python engines/grumpa/tools/viewcheck.py --selftest
"""
from __future__ import annotations

import re
import statistics
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "parsers"))
import abi  # noqa: E402
import anb  # noqa: E402
import fxi  # noqa: E402

CAB = HERE.parents[2] / "games/grumpa/discs/cab"


def views(scn: bytes):
    """The CFXView record (u32 9, u32 id, u32 n, n*(pstr jpg, pstr fxi), n view, n proj
    matrices); it ends the file in every scene. Returns [(jpg, fxi, view16, proj16)]."""
    for m in re.finditer(rb"\x09\x00\x00\x00", scn):
        o = m.start()
        if o + 12 > len(scn):
            continue
        n = struct.unpack_from("<I", scn, o + 8)[0]
        if not 1 <= n <= 5:
            continue
        p, names = o + 12, []
        try:
            for _ in range(2 * n):
                ln = struct.unpack_from("<I", scn, p)[0]
                if not 0 < ln <= 64:
                    raise ValueError
                names.append(scn[p + 4:p + 4 + ln].rstrip(b"\0").decode("latin1"))
                p += 4 + ln
        except (ValueError, struct.error):
            continue
        if p + n * 128 != len(scn):
            continue
        mats = [struct.unpack_from("<16f", scn, p + 64 * i) for i in range(2 * n)]
        return [(names[2 * k], names[2 * k + 1], mats[k], mats[n + k]) for k in range(n)]
    return None


def xf(v, m):
    return [v[0] * m[j] + v[1] * m[4 + j] + v[2] * m[8 + j] + v[3] * m[12 + j] for j in range(4)]


def mesh_check(scene: str, mesh: str, k: int):
    jpg, zname, vm, pm = views((CAB / f"Scenes/Scene_{scene}.scn").read_bytes())[k]
    w, h, z = fxi.decode((CAB / "Bitmaps" / zname).read_bytes())
    m = anb.parse((CAB / "Meshes" / mesh).read_bytes())
    pts, diff = [], []
    for s in m["sections"]:
        for v in s["verts"]:
            c = xf(xf((*v, 1.0), vm), pm)
            if c[3] <= 0 or c[2] < 0:
                continue
            sx, sy, zz = (c[0] / c[3] + 1) * 400, (1 - c[1] / c[3]) * 300, c[2] / c[3]
            pts.append((sx, sy))
            if 0 <= sx < w and 0 <= sy < h:
                diff.append(int(zz * 65535) - z[int(sy) * w + int(sx)])
    return jpg, pts, diff


def sprite_records(scene: str):
    d = (CAB / f"Scenes/Scene_{scene}.abi").read_bytes()
    c, out = abi.Cur(d), []
    while len(d) - c.o >= 8:
        t, i = struct.unpack_from("<II", d, c.o)
        c.o += 8
        if t == 0x0d:
            st = c.o
            c.raw(12); abi.ec_vec(c)
            f = struct.unpack_from("<10i", d, c.o)
            c.raw(40); abi.cc_vec(c); abi.sub_456d70(c)
            pos = struct.unpack_from("<2i", d, c.o) if f[9] == 1 else None
            c.o = st
            abi.t_0d(c)
            tail = d[c.o - 64:c.o]
            name = next(tail[64 - k:].decode("latin1") for k in range(1, 60)
                        if struct.unpack_from("<I", tail, 60 - k)[0] == k)
            out.append(dict(id=i, name=name, layer=f[0], fps=f[2], anim=f[3], view=f[4],
                            keyed=f[5], key=f[6], pos=pos))
        else:
            abi.TYPES[t](c)
    return out


def sprite_check(scene: str):
    from PIL import Image, ImageChops, ImageStat
    vs = views((CAB / f"Scenes/Scene_{scene}.scn").read_bytes())
    bgs = [Image.open(CAB / "Bitmaps" / v[0]).convert("RGB") for v in vs]
    rows = []
    for s in sprite_records(scene):
        if s["pos"] is None or not (CAB / "Bitmaps" / s["name"]).exists():
            continue
        sp = Image.open(CAB / "Bitmaps" / s["name"]).convert("RGB")
        x, y = s["pos"]
        err = [round(sum(ImageStat.Stat(ImageChops.difference(
            bg.crop((x, y, x + sp.width, y + sp.height)), sp)).mean) / 3, 1) for bg in bgs]
        rows.append((s, err))
    return rows


def selftest():
    vs = views((CAB / "Scenes/Scene_004.scn").read_bytes())
    assert [v[0] for v in vs] == ["4_1_IS.jpg", "4_2_IS.jpg", "4_3_IS.jpg", "4_4_IS.jpg"]
    n = sum(1 for p in sorted((CAB / "Scenes").glob("*.scn")) if views(p.read_bytes()))
    assert n == 110, n
    _, pts, diff = mesh_check("061", "boulder B_at ground.ANB", 0)
    assert abs(statistics.median(diff)) < 2000, statistics.median(diff)
    for s, err in sprite_check("004"):
        if not s["keyed"] and s["view"] >= 0:  # opaque, view-bound: matches its own view
            assert min(range(len(err)), key=err.__getitem__) == s["view"], (s, err)
    print(f"viewcheck selftest ok: {n}/110 .scn views, boulder median dz {statistics.median(diff)}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--selftest"]:
        selftest()
    elif a[:1] == ["mesh"]:
        jpg, pts, diff = mesh_check(a[1], a[2], int(a[3]))
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        print(jpg, "bbox x %.0f..%.0f y %.0f..%.0f" % (min(xs), max(xs), min(ys), max(ys)))
        if diff:
            print("z16 - fxi: median", statistics.median(diff), "min", min(diff), "max", max(diff))
    elif a[:1] == ["sprites"]:
        for s, err in sprite_check(a[1]):
            print(s["id"], s["name"], "view", s["view"], "layer", s["layer"], "keyed", s["keyed"],
                  "key %#x" % (s["key"] & 0xffffffff), s["pos"], "diff/bg", err)
    else:
        print(__doc__)
