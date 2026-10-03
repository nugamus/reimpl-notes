"""Validate Grumpa's `.anb` meshes — geometry, UVs and vertex animation (E-0014, E-0600).

`CFXAMeshEx` reads `<base>.anb` in `FUN_004157d0` (decrypted `Grumpa.exe`, E-0003). Layout:

    u32 frameCount F
    u32 sectionCount S
    per section (S):
        u32 vertCount A, u32 uvCount B, u32 faceCount C
        A * 24   vertices of frame 0: pos[3f] + normal[3f] (x, y, z each)
        C * 6    face vertex-index triples (3 x u16, into the section's vertices)
        B * 8    texture coordinates (2 x f32)
        C * 6    face uv-index triples (3 x u16, into the section's uvs)
    (F-1) * (sum of A) * 24   frames 1..F-1: every section's vertices, frame after frame
    tail     bytes the loader never reads (E-0600)

The loader reads exactly F frames and closes the file. 521 files store one frame more
(a whole `(sum of A) * 24` block) and `012_D2D_Grumpa_In_Boat.ANB` 4,456 stray bytes: both
are the unread tail, reported apart (Q-0007 resolved).

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
    """{frames, sections:[{verts,normals,faces,uvs,face_uvs}], anim:[[(pos, normal)]],
    tail, tail_frame}; raises unless the F frames the loader reads are all there."""
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
            nx, ny, nz = struct.unpack_from("<3f", d, off + 12)
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
    step = total_a * 24
    anim = []
    for _ in range(max(frames - 1, 0)):
        if off + step > len(d):
            raise ParseError(f"frame {len(anim) + 1} of {frames} past end")
        anim.append([(struct.unpack_from("<3f", d, o), struct.unpack_from("<3f", d, o + 12))
                     for o in range(off, off + step, 24)])
        off += step
    tail = len(d) - off
    return {"frames": frames, "sections": sections, "anim": anim, "total_verts": total_a,
            "tail": tail, "tail_frame": step > 0 and tail == step}


def validate(root: Path) -> int:
    files = sorted(set(p.as_posix().lower() for p in root.rglob("*.anb")))
    files = [Path(p) for p in files]
    if not files:
        sys.exit(f"no .anb under {root}")
    bad = tris = verts = frames = 0
    extra = stray = stray_bytes = 0
    for f in files:
        try:
            r = parse(f.read_bytes())
        except (ParseError, struct.error) as e:
            bad += 1
            print(f"FAIL {f.name}: {e}")
            continue
        tris += sum(len(s["faces"]) for s in r["sections"])
        verts += r["total_verts"]
        frames += max(r["frames"], 1)
        if r["tail_frame"]:
            extra += 1
        elif r["tail"]:
            stray += 1
            stray_bytes += r["tail"]
            print(f"note {f.name}: {r['tail']} unread bytes")
    print(f"{len(files) - bad}/{len(files)} .anb parsed, every byte accounted for "
          f"({verts} base vertices, {tris} triangles, {frames} frames read); unread tail: "
          f"one stored frame more in {extra} files, {stray_bytes} stray bytes in {stray}")
    return bad


def selftest() -> None:
    # F=1, S=1, A=2, B=1, C=1; K=0 (static).
    d = struct.pack("<II", 1, 1) + struct.pack("<III", 2, 1, 1)
    d += struct.pack("<6f", 1, 2, 3, 30, 20, 10) + struct.pack("<6f", 4, 5, 6, 60, 50, 40)  # 2 verts
    d += struct.pack("<3H", 0, 1, 0)          # 1 face (vertex indices)
    d += struct.pack("<2f", 0.5, 0.25)        # 1 uv
    d += struct.pack("<3H", 0, 0, 0)          # 1 face uv-index triple
    r = parse(d)
    assert r["frames"] == 1 and r["anim"] == [] and r["tail"] == 0
    s = r["sections"][0]
    assert s["verts"][0] == (1, 2, 3) and s["normals"][0] == (30, 20, 10)
    assert s["faces"] == [(0, 1, 0)] and s["uvs"] == [(0.5, 0.25)]
    frame = struct.pack("<12f", *range(12))  # one frame = total_verts (2) * 24 bytes
    # F=3: frames 1 and 2 follow; the second vertex of frame 1 is at (6, 7, 8).
    r = parse(struct.pack("<II", 3, 1) + d[8:] + frame * 2)
    assert len(r["anim"]) == 2 and r["anim"][0][1][0] == (6, 7, 8) and r["tail"] == 0
    # one stored frame more: unread by the loader, reported as a frame-sized tail
    r = parse(struct.pack("<II", 3, 1) + d[8:] + frame * 3)
    assert len(r["anim"]) == 2 and r["tail_frame"]
    assert parse(d + b"\0")["tail"] == 1      # a stray byte is tail, not a frame
    for bad in (b"\0" * 4, struct.pack("<II", 3, 1) + d[8:] + frame):  # short / frame missing
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
