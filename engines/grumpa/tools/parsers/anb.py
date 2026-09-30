"""Validate Grumpa's `.anb` meshes — geometry, UVs and vertex animation (E-0014).

`CFXAMeshEx` reads `<base>.anb` in `FUN_004157d0` (decrypted `Grumpa.exe`, E-0003). Layout:

    u32 frameCount F
    u32 sectionCount S
    per section (S):
        u32 vertCount A, u32 uvCount B, u32 faceCount C
        A * 24   vertices of frame 0: pos[3f] + normal[3f] (normal stored z,y,x)
        C * 6    face vertex-index triples (3 x u16, into the section's vertices)
        B * 8    texture coordinates (2 x f32)
        C * 6    face uv-index triples (3 x u16, into the section's uvs)
    trailing: K * (sum of A) * 24   further animation frames (vertices only)

The static mesh (frame 0 vertices, triangles, UVs) is the renderable geometry and parses
exactly. The trailing holds the animation: K = F-1 frames for most meshes, K = F for the
`X2Y` transition-animation clips (N2N idle, N2W normal->walk, W2R walk->run, ...); the
in-file discriminator is not yet pinned (Q-0007), so this validator accepts K in {F-1, F}
and still consumes every byte. One corpus file is malformed (a non-integer trailing).

    python engines/grumpa/tools/parsers/anb.py --selftest
    python engines/grumpa/tools/parsers/anb.py [root]        # default: the cab corpus
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/grumpa/discs/cab"


class ParseError(Exception):
    pass


def parse(d: bytes) -> dict:
    """{frames, sections:[{verts,normals,faces,uvs,face_uvs}], anim_frames}; raises unless
    every byte is consumed (with the trailing K in {F-1, F})."""
    if len(d) < 8:
        raise ParseError("shorter than the header")
    frames, nsec = struct.unpack_from("<II", d, 0)
    off = 8
    sections = []
    total_a = 0
    for _ in range(nsec):
        if off + 12 > len(d):
            raise ParseError("section header past end")
        a, b, c = struct.unpack_from("<III", d, off)
        off += 12
        verts, norms, faces, uvs, face_uvs = [], [], [], [], []
        for _ in range(a):
            x, y, z = struct.unpack_from("<3f", d, off)
            nz, ny, nx = struct.unpack_from("<3f", d, off + 12)
            verts.append((x, y, z))
            norms.append((nx, ny, nz))
            off += 24
        for _ in range(c):
            faces.append(struct.unpack_from("<3H", d, off))
            off += 6
        for _ in range(b):
            uvs.append(struct.unpack_from("<2f", d, off))
            off += 8
        for _ in range(c):
            face_uvs.append(struct.unpack_from("<3H", d, off))
            off += 6
        sections.append({"verts": verts, "normals": norms, "faces": faces, "uvs": uvs,
                         "face_uvs": face_uvs})
        total_a += a
    trailing = len(d) - off
    step = total_a * 24
    if step == 0:
        if trailing != 0:
            raise ParseError(f"no vertices but {trailing} trailing bytes")
        k = 0
    else:
        if trailing % step:
            raise ParseError(f"trailing {trailing} not a whole number of {step}-byte frames")
        k = trailing // step
        if k not in (max(frames - 1, 0), frames):
            raise ParseError(f"trailing has {k} frames, expected {frames - 1} or {frames}")
    return {"frames": frames, "sections": sections, "anim_frames": k, "total_verts": total_a}


def validate(root: Path) -> int:
    files = sorted(set(p.as_posix().lower() for p in root.rglob("*.anb")))
    files = [Path(p) for p in files]
    if not files:
        sys.exit(f"no .anb under {root}")
    bad = tris = verts = 0
    for f in files:
        try:
            r = parse(f.read_bytes())
        except (ParseError, struct.error) as e:
            bad += 1
            print(f"FAIL {f.name}: {e}")
            continue
        tris += sum(len(s["faces"]) for s in r["sections"])
        verts += r["total_verts"]
    print(f"{len(files) - bad}/{len(files)} .anb parsed, every byte consumed "
          f"({verts} base vertices, {tris} triangles)")
    return bad


def selftest() -> None:
    # F=1, S=1, A=2, B=1, C=1; K=0 (static).
    d = struct.pack("<II", 1, 1) + struct.pack("<III", 2, 1, 1)
    d += struct.pack("<6f", 1, 2, 3, 30, 20, 10) + struct.pack("<6f", 4, 5, 6, 60, 50, 40)  # 2 verts
    d += struct.pack("<3H", 0, 1, 0)          # 1 face (vertex indices)
    d += struct.pack("<2f", 0.5, 0.25)        # 1 uv
    d += struct.pack("<3H", 0, 0, 0)          # 1 face uv-index triple
    r = parse(d)
    assert r["frames"] == 1 and r["anim_frames"] == 0
    s = r["sections"][0]
    assert s["verts"][0] == (1, 2, 3) and s["normals"][0] == (10, 20, 30)
    assert s["faces"] == [(0, 1, 0)] and s["uvs"] == [(0.5, 0.25)]
    frame = b"\0" * (2 * 24)  # one animation frame = total_verts (2) * 24 bytes
    # F=3 with K=F-1=2 extra frames.
    assert parse(struct.pack("<II", 3, 1) + d[8:] + frame * 2)["anim_frames"] == 2
    # K=F variant (3 extra frames for F=3).
    assert parse(struct.pack("<II", 3, 1) + d[8:] + frame * 3)["anim_frames"] == 3
    for bad in (b"\0" * 4, d + b"\0"):  # short header / stray byte
        try:
            parse(bad)
            raise AssertionError("should have failed")
        except (ParseError, struct.error):
            pass
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=str(CORPUS))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    else:
        sys.exit(1 if validate(Path(a.root)) else 0)
