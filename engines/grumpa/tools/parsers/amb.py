"""Validate Grumpa's `.amb` meshes — the vertex/normal set (E-0013).

`CFXAMeshEx::CreateFromFile` (`FUN_00416a90`, decrypted `Grumpa.exe`, E-0003) opens
`<base>.amb` as a binary stream and reads:

    u32 count               number of vertices
    count x {
        float pos[3]        x, y, z            (12 bytes, read as one block)
        float normal[3]     z, y, x            (12 bytes, read as three reversed u32)
    }

So a `.amb` is `4 + count*24` bytes. The face topology, UVs and animation live in the
companion `.anb` (read afterwards by `FUN_004157d0`, Q-0007). A few `.amb` are 4-byte stubs
(a count with no data) that the game tolerates (the stream fails and the mesh stays empty).

    python engines/grumpa/tools/parsers/amb.py --selftest
    python engines/grumpa/tools/parsers/amb.py [root]        # default: the cab corpus
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
    """{count, vertices:[(x,y,z)], normals:[(x,y,z)]}; raises unless every byte is used."""
    if len(d) < 4:
        raise ParseError("shorter than the count")
    count = struct.unpack_from("<I", d, 0)[0]
    if len(d) == 4:
        return {"count": count, "stub": True, "vertices": [], "normals": []}
    if 4 + count * 24 != len(d):
        raise ParseError(f"{4 + count * 24} expected for count {count}, {len(d)} on disk")
    verts, norms = [], []
    off = 4
    for _ in range(count):
        x, y, z = struct.unpack_from("<3f", d, off)
        nz, ny, nx = struct.unpack_from("<3f", d, off + 12)  # normal stored z, y, x
        verts.append((x, y, z))
        norms.append((nx, ny, nz))
        off += 24
    return {"count": count, "stub": False, "vertices": verts, "normals": norms}


def validate(root: Path) -> int:
    files = sorted(root.rglob("*.amb"))
    if not files:
        sys.exit(f"no .amb under {root}")
    bad = stubs = total = 0
    for f in files:
        try:
            r = parse(f.read_bytes())
        except ParseError as e:
            bad += 1
            print(f"FAIL {f.relative_to(root)}: {e}")
            continue
        stubs += r["stub"]
        total += r["count"] if not r["stub"] else 0
    print(f"{len(files) - bad}/{len(files)} .amb parsed, every byte consumed "
          f"({stubs} empty stubs, {total} vertices total)")
    return bad


def selftest() -> None:
    d = struct.pack("<I", 2) + struct.pack("<6f", 1, 2, 3, 30, 20, 10) + struct.pack("<6f", 4, 5, 6, 60, 50, 40)
    r = parse(d)
    assert r["count"] == 2 and not r["stub"]
    assert r["vertices"][0] == (1, 2, 3) and r["normals"][0] == (10, 20, 30), r  # normal reversed
    assert r["vertices"][1] == (4, 5, 6) and r["normals"][1] == (40, 50, 60)
    assert parse(struct.pack("<I", 10))["stub"]  # 4-byte stub
    for bad in (b"\0\0", struct.pack("<I", 3) + b"\0" * 10):
        try:
            parse(bad)
            raise AssertionError("should have failed")
        except ParseError:
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
