"""The 3D objects inside BFG bundles: .3DC scenes, .3DM textures, .3DA animations, .3DI boxes.

Each is a memory image written by the authoring tool: after the 20-byte object header
(bfg.py) comes a body whose pointers are stored as offsets that the loader relocates
(E-0013). This validator follows every pointer the loader relocates, checks strides and
counts, and requires the structures reached to cover every byte of the body exactly once.

    .3DC  body: u32 n; u32 node[n] (body-relative); u32 nmat; material[nmat] (44 B);
          then the node tree. Tree pointers are 1-based offsets from the first node
          (0 = none). node (0xDC B) -> vertices (40 B), uvs (8 B), vertex normals (16 B),
          face normals (16 B), face groups (0x34 B + polys of `stride` B),
          vertex groups (0x18 B + items of 100/0x70/0x58/0x3C B by group type).
    .3DM  body: 32 x 256 u32 shade table (RGB565 in the high 16 bits; low 16 bits zero),
          256 x 256 u8 texel indices (4 textures differ in length, ODD_TEXTURES, Q-0003).
    .3DA  body: u32 n; u32 track[n] (body-relative); track: u32 unk_0, u32 nrot, u32 npos,
          u32 rot (body-relative), u32 pos; rot key 20 B (u32 t, 4 x s32 Q15), pos key 16 B.
    .3DI  body: u32 nvert; u32 verts; u32 nface; u32 faces; u32 nitem; u32 items; u32 unk;
          pointers 1-based from the body; verts 12 B; faces 0x60 B; items 12 B.

    python engines/peintre/tools/parsers/obj3d.py            # validate every BFG entry
    python engines/peintre/tools/parsers/obj3d.py --selftest
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bfg  # noqa: E402

H = bfg.HEADER.size  # 20-byte object header
NODE = 0xDC
MATERIAL = 44
VERTEX = 40
UV = 8
NORMAL = 16
FACE_GROUP = 0x34
VERTEX_GROUP = 0x18
# Poly size per face-group type, from the relocation switch at 0x433b70.
POLY_38 = {-2, 1, 4, 0x11, 0x1B}
# Vertex-group item size per type, from the relocation switch at 0x433ff0.
VG_ITEM = {}
for size, types in {100: (0x16, 0x19, 0x1E, -0xC, -9, -7, -6, -4, 3, 9, 0x14, 0x1C, 0x1D),
                    0x70: (0x17, 0x1A),
                    0x58: (-0x16, -0x15, -0xF, -0xE, -0xD, -0xB, -10, -8, -5, -3, 2, 0x12,
                           0x15, 0x20, 0x21),
                    0x3C: (-2, 1, 4, 0x11, 0x1B)}.items():
    for t in types:
        VG_ITEM[t] = size
TEX_TABLE = 32 * 256 * 4
TEX_PIXELS = 256 * 256


class FormatError(Exception):
    pass


class Cover:
    """Byte coverage of a body: every byte claimed exactly once."""

    def __init__(self, size: int):
        self.size = size
        self.owner = [None] * size

    def claim(self, off: int, n: int, what: str) -> None:
        if off < 0 or off + n > self.size:
            raise FormatError(f"{what} at 0x{off:x}+0x{n:x} outside the body (0x{self.size:x})")
        for i in range(off, off + n):
            if self.owner[i] is not None:
                raise FormatError(f"{what} at 0x{off:x} overlaps {self.owner[i]}")
            self.owner[i] = what

    def check(self) -> None:
        gaps = [i for i, o in enumerate(self.owner) if o is None]
        if gaps:
            raise FormatError(f"{len(gaps)} bytes not reached, first at 0x{gaps[0]:x}")


def i32(b: bytes, off: int) -> int:
    return struct.unpack_from("<i", b, off)[0]


def parse_3dc(body: bytes, stats: Counter) -> dict:
    cov = Cover(len(body))
    n = i32(body, 0)
    cov.claim(0, 4 + 4 * n, "node table")
    table = [i32(body, 4 + 4 * i) for i in range(n)]
    nmat = i32(body, 4 + 4 * n)
    mat_off = 8 + 4 * n
    cov.claim(4 + 4 * n, 4 + MATERIAL * nmat, "materials")
    materials = []
    for i in range(nmat):
        rec = body[mat_off + MATERIAL * i: mat_off + MATERIAL * (i + 1)]
        materials.append((rec[:16].split(b"\0")[0].decode("latin1"),
                          rec[16:32].split(b"\0")[0].decode("latin1")))
    root = table[0]
    if root != mat_off + MATERIAL * nmat:
        raise FormatError("first node does not follow the materials")

    def tree(v: int) -> int:  # 1-based offset from the root node
        return root + v - 1

    nodes, stack = [], [root]
    while stack:
        nd = stack.pop()
        if nd in nodes:
            raise FormatError(f"node 0x{nd:x} reached twice")
        nodes.append(nd)
        cov.claim(nd, NODE, "node")
        for link in (0x14, 0x18):  # first child, next sibling
            if i32(body, nd + link):
                stack.append(tree(i32(body, nd + link)))
        (nv, pv, nuv, puv, nvn, pvn, nfn, pfn, n9c, pa0, fg, vg) = struct.unpack_from(
            "<12i", body, nd + 0x7C)
        if n9c or pa0:
            raise FormatError("node +0x9c/+0xa0 set")  # never in the corpus
        for count, ptr, size, what in ((nv, pv, VERTEX, "vertices"), (nuv, puv, UV, "uvs"),
                                       (nvn, pvn, NORMAL, "vertex normals"),
                                       (nfn, pfn, NORMAL, "face normals")):
            if count:
                cov.claim(tree(ptr), size * count, what)
        stats["vertices"] += nv
        while fg:
            g = tree(fg)
            cov.claim(g, FACE_GROUP, "face group")
            gtype, count, polys, stride = (i32(body, g + 4), i32(body, g + 0x1C),
                                           i32(body, g + 0x20), i32(body, g + 0x2C))
            want = 0x38 if gtype in POLY_38 else 0x44
            if stride != want:
                raise FormatError(f"face group type {gtype}: stride {stride}, loader uses {want}")
            if count:
                cov.claim(tree(polys), stride * count, "polys")
            stats[f"face group type {gtype}"] += 1
            stats["polys"] += count
            fg = i32(body, g)
        while vg:
            g = tree(vg)
            cov.claim(g, VERTEX_GROUP, "vertex group")
            gtype, count, items = i32(body, g + 4), i32(body, g + 8), i32(body, g + 0xC)
            if gtype not in VG_ITEM:
                raise FormatError(f"vertex group type {gtype}")
            if count:
                cov.claim(tree(items), VG_ITEM[gtype] * count, "vertex group items")
            stats[f"vertex group type {gtype}"] += 1
            vg = i32(body, g)
    if sorted(nodes) != sorted(table):
        raise FormatError("node table differs from the tree")
    cov.check()
    stats["nodes"] += len(nodes)
    stats["materials"] += nmat
    return {"nodes": len(nodes), "materials": materials}


# Textures whose pixel block is not 256 x 256 bytes (Q-0003): name -> pixel bytes.
ODD_TEXTURES = {"salon.3DM": TEX_PIXELS + 512, "plafond.3DM": TEX_PIXELS - 256,
                "plafond2.3DM": TEX_PIXELS - 256, "plafond3.3DM": TEX_PIXELS - 256}


def parse_3dm(body: bytes, stats: Counter, name: str = "") -> None:
    pixels = len(body) - TEX_TABLE
    if pixels != TEX_PIXELS:
        if ODD_TEXTURES.get(name) != pixels:
            raise FormatError(f"texture body {len(body)} bytes")
        stats[f"texture pixel block {pixels} B"] += 1
    table = struct.unpack_from(f"<{32 * 256}I", body)
    if any(v & 0xFFFF for v in table):
        raise FormatError("shade table low half not zero")


def parse_3da(body: bytes, stats: Counter) -> None:
    cov = Cover(len(body))
    n = i32(body, 0)
    cov.claim(0, 4 + 4 * n, "track table")
    for i in range(n):
        t = i32(body, 4 + 4 * i)
        cov.claim(t, 20, "track")
        _, nrot, npos, prot, ppos = struct.unpack_from("<5i", body, t)
        if nrot:
            cov.claim(prot, 20 * nrot, "rotation keys")
        if npos:
            cov.claim(ppos, 16 * npos, "position keys")
        stats["tracks"] += 1
        stats["rotation keys"] += nrot
        stats["position keys"] += npos
    cov.check()


def parse_3di(body: bytes, stats: Counter) -> None:
    cov = Cover(len(body))
    cov.claim(0, 0x1C, "box header")  # +0x18: unk, leftover memory
    nvert, pvert, nface, pface, nitem, pitem = struct.unpack_from("<6i", body)
    for count, ptr, size, what in ((nvert, pvert, 12, "box vertices"),
                                   (nface, pface, 0x60, "box faces"),
                                   (nitem, pitem, 12, "box items")):
        if count:
            cov.claim(ptr - 1, size * count, what)
    stats["box vertices"] += nvert
    stats["box faces"] += nface
    stats["box items"] += nitem
    cov.check()


PARSERS = {1: parse_3dc, 3: parse_3dm, 4: parse_3da, 5: parse_3di}


def validate() -> int:
    stats, ok, total, fails = Counter(), Counter(), Counter(), 0
    for f in sorted(bfg.CORPUS.glob("*.BFG")):
        for name, _, data in bfg.read(f):
            ext = Path(name).suffix.upper()
            total[ext] += 1
            typ = bfg.HEADER.unpack_from(data)[2]
            try:
                if typ == 3:
                    parse_3dm(data[H:], stats, name)
                else:
                    PARSERS[typ](data[H:], stats)
                ok[ext] += 1
            except FormatError as e:
                fails += 1
                if fails <= 20:
                    print(f"FAIL {f.name}:{name}: {e}")
    for ext in sorted(total):
        print(f"{ext}: {ok[ext]}/{total[ext]} valid, every byte reached exactly once")
    print("; ".join(f"{k} {v}" for k, v in sorted(stats.items())))
    return 0 if not fails else 1


def selftest() -> None:
    # a 3DA with one track, one rotation key and one position key
    track = struct.pack("<5i", 30, 1, 1, 28, 48)
    body = struct.pack("<ii", 1, 8) + track + struct.pack("<5i", 0, 0, 0, 0, 32768) \
        + struct.pack("<4i", 0, 1, 2, 3)
    s = Counter()
    parse_3da(body, s)
    assert s["tracks"] == 1 and s["position keys"] == 1
    try:
        parse_3da(body + b"\0", Counter())
    except FormatError:
        pass
    else:
        raise AssertionError("unreached byte accepted")
    c = Cover(4)
    c.claim(0, 2, "a")
    try:
        c.claim(1, 2, "b")
    except FormatError:
        pass
    else:
        raise AssertionError("overlap accepted")
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
    else:
        sys.exit(validate())
