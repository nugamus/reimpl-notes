"""Validate Grumpa's `.scn` scene files (E-0500).

`LoadScene` (`FUN_0040cb30`, decrypted `Grumpa.exe`) builds `Scenes\\Scene_%03d.scn` and
reads it with the same `CFXActorFactory::CreateFromABIFile` (`FUN_0040cef0`) as the `.abi`:
a flat record stream to EOF, `record = u32 type, u32 id, <Serialize(mode 1)>`. The reader
seeks back 4 bytes after the id, so each `Serialize` re-reads the id as its `+0x108`
(the abi.py grammar starts after the id; here the id is consumed by the record header).
Three classes occur, each once per file, ids 600/601/602:

    0x08 walk mesh  (Serialize FUN_00432880):
         u16 nv, u16 nf, nv * vertex(8 f32: x y z, 5 unk), nf * (3 u16 vertex index),
         nf * u16 unk; FUN_00432c60 then builds the face adjacency (shared edges)
    0x14 scene links "CFXToScene" (Serialize FUN_00447cd0):
         u32 np, np * u32 parameter (State, Scene_ID), u32 n, n * exit, u32 m, m * entry
           exit  (FUN_0045a370 over FUN_0044c750): f32 x y z, f32 radius, u32 scene
           entry (FUN_0045a2a0 over FUN_00401c00): f32 x y z, f32 rx ry rz, u32 scene
    0x09 view list  (Serialize FUN_0045a750):
         u32 n, n * (pstr colour `.jpg`, pstr depth `.fxi`), n * 64 B, n * 64 B (4x4 f32)

    python engines/grumpa/tools/parsers/scn.py --selftest
    python engines/grumpa/tools/parsers/scn.py [root]        # default: the cab corpus
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from abi import CORPUS, Cur, ParseError, _count  # noqa: E402


def _str(c: Cur) -> str:           # u32 len (with the NUL) + bytes
    return c.raw(_count(c, "string")).rstrip(b"\0").decode("latin-1")


def t_08(c: Cur) -> dict:
    nv, nf = struct.unpack("<HH", c.raw(4))
    verts = [struct.unpack("<8f", c.raw(32)) for _ in range(nv)]
    faces = [struct.unpack("<3H", c.raw(6)) for _ in range(nf)]
    unk = struct.unpack(f"<{nf}H", c.raw(2 * nf))
    for f in faces:
        if max(f) >= nv:
            raise ParseError(f"face index {max(f)} >= {nv} vertices")
    return {"verts": verts, "faces": faces, "unk_face": unk}


def t_14(c: Cur) -> dict:
    params = [c.u32() for _ in range(_count(c, "param"))]
    exits = [struct.unpack("<4fI", c.raw(20)) for _ in range(_count(c, "exit"))]
    entries = [struct.unpack("<6fI", c.raw(28)) for _ in range(_count(c, "entry"))]
    return {"params": params, "exits": exits, "entries": entries}


def t_09(c: Cur) -> dict:
    n = _count(c, "view")
    names = [(_str(c), _str(c)) for _ in range(n)]
    m1 = [struct.unpack("<16f", c.raw(64)) for _ in range(n)]
    m2 = [struct.unpack("<16f", c.raw(64)) for _ in range(n)]
    return {"views": names, "unk_m1": m1, "unk_m2": m2}


TYPES = {0x08: t_08, 0x14: t_14, 0x09: t_09}


def parse(d: bytes) -> dict:
    """{type: body} for the three records; raises unless every byte is consumed."""
    c = Cur(d)
    out = {}
    while not c.eof():
        t, rid = c.u32(), c.u32()
        fn = TYPES.get(t)
        if fn is None:
            raise ParseError(f"unexpected type {t:#x} id {rid} at {c.o - 8:#x}")
        if t in out:
            raise ParseError(f"type {t:#x} twice")
        out[t] = fn(c)
        out[t]["id"] = rid
    if set(out) != set(TYPES):
        raise ParseError(f"types {sorted(out)}")
    return out


def validate(root: Path) -> int:
    files = sorted(root.glob("Scenes/*.scn"))
    if not files:
        sys.exit(f"no .scn under {root}")
    bad = 0
    st: Counter = Counter()
    for f in files:
        try:
            r = parse(f.read_bytes())
            st["verts"] += len(r[8]["verts"])
            st["faces"] += len(r[8]["faces"])
            st["exits"] += len(r[0x14]["exits"])
            st["entries"] += len(r[0x14]["entries"])
            st["views"] += len(r[9]["views"])
        except (ParseError, struct.error, UnicodeDecodeError) as e:
            bad += 1
            print(f"FAIL {f.name}: {e}")
    print(f"{len(files) - bad}/{len(files)} .scn parsed, every byte consumed; "
          + ", ".join(f"{k} {v}" for k, v in st.items()))
    return bad


def selftest() -> None:
    d = (struct.pack("<IIHH", 8, 600, 3, 1) + struct.pack("<8f", *range(8)) * 3
         + struct.pack("<3H", 0, 1, 2) + struct.pack("<H", 7)
         + struct.pack("<II", 0x14, 601) + struct.pack("<III", 2, 0, 0)
         + struct.pack("<I", 1) + struct.pack("<4fI", 1, 2, 3, 4, 5)
         + struct.pack("<I", 0)
         + struct.pack("<III", 9, 602, 1) + struct.pack("<I", 4) + b"a.j\0"
         + struct.pack("<I", 4) + b"a.f\0" + b"\0" * 128)
    r = parse(d)
    assert r[8]["faces"] == [(0, 1, 2)] and r[8]["unk_face"] == (7,)
    assert r[0x14]["exits"] == [(1.0, 2.0, 3.0, 4.0, 5)] and r[0x14]["entries"] == []
    assert r[9]["views"] == [("a.j", "a.f")]
    for bad in (d[:-1], d + b"\0" * 8):
        try:
            parse(bad); raise AssertionError("should fail")
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
