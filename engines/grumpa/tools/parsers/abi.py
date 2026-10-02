"""Validate Grumpa's `.abi` scene-graph files (E-0100..).

`.abi` is a serialized `CFXActorFactory` tree. `CFXActorFactory::CreateFromABIFile`
(`FUN_0040cef0`, decrypted `Grumpa.exe`, E-0003) opens the file as a C++ ifstream and reads
records until end-of-stream:

    record = u32 type, u32 id, <Serialize(mode 1)>

`CreateActor` (`FUN_0040d2f0`) maps the type code to a `CFX*` class (34 codes); each class's
`Serialize` (vtable[1]) is called with mode 1 — the full-load path (`FUN_0040cef0` pushes 1 as
the mode; type 5's full-load is the `case 1` arm, which rules out mode 2). The grammar below
is each `Serialize`'s mode-1 read sequence of the raw-read primitive
`FUN_004026c0(archive, dest, n)` ("read n bytes"), counted child/command loops, pascal strings
(`FUN_00430c50` = u32 len + len bytes) and inline embedded sub-objects (their own Serialize).

Two element classes recur as vector members in almost every actor:

    EC  (serialize FUN_00409920, stride 0x118): 5 u32                       = 20 bytes
    CC  (serialize FUN_00409150, stride 0x128): 5 u32 + u32 n + n*EC        = 24 + 20n

Embedded sub-objects seen inline (serialized via vtable[1], no type/id prefix):

    SUB_456d70 (ctor 0x456cf0, size 0x140): 14 u32                          = 56 bytes
    SUB_401c00 (ctor 0x401bb0, size 0x120): 2 * 0xc                         = 24 bytes

Per-type field layouts come from each `Serialize` in the decrypted `Grumpa.exe` (E-0100..);
only field *order and size* matter here (offsets are the object's, not the file's). Two actors
branch on a value they just read: 0x19 reads a bubble array iff its +0x1ac field == 2, and
0x0d reads two extra u32 iff its +0x20c field == 1.

    python engines/grumpa/tools/parsers/abi.py --selftest
    python engines/grumpa/tools/parsers/abi.py [root]        # default: the cab corpus
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/grumpa/discs/cab"


class ParseError(Exception):
    pass


class Cur:
    """A cursor over the bytes with counting reads."""

    __slots__ = ("d", "o")

    def __init__(self, d: bytes, o: int = 0):
        self.d = d
        self.o = o

    def raw(self, n: int) -> bytes:
        if n < 0 or self.o + n > len(self.d):
            raise ParseError(f"read {n} at {self.o:#x} past end {len(self.d):#x}")
        b = self.d[self.o:self.o + n]
        self.o += n
        return b

    def u32(self) -> int:
        return struct.unpack_from("<I", self.raw(4), 0)[0]

    def eof(self) -> bool:
        return self.o >= len(self.d)


def _count(c: Cur, what: str) -> int:
    n = struct.unpack_from("<i", c.raw(4), 0)[0]
    if n < 0 or n > 0x100000:
        raise ParseError(f"implausible {what} count {n} at {c.o - 4:#x}")
    return n


# ---- shared element classes -------------------------------------------------

def ec(c: Cur) -> None:            # FUN_00409920, 20 bytes
    c.raw(20)


def cc(c: Cur) -> None:            # FUN_00409150
    c.raw(20)
    for _ in range(_count(c, "EC-in-CC")):
        ec(c)


def ec_vec(c: Cur) -> None:        # u32 n; n*EC
    for _ in range(_count(c, "EC")):
        ec(c)


def cc_vec(c: Cur) -> None:        # u32 n; n*CC
    for _ in range(_count(c, "CC")):
        cc(c)


def pstr(c: Cur) -> None:          # FUN_00430c50: u32 len; len bytes (only if len>0)
    n = struct.unpack_from("<i", c.raw(4), 0)[0]
    if n > 0:
        c.raw(n)


def sub_456d70(c: Cur) -> None:    # embedded CFX* (ctor 0x456cf0): 14 u32
    c.raw(56)


def sub_401c00(c: Cur) -> None:    # embedded CFX* (ctor 0x401bb0): 2*0xc
    c.raw(24)


def pair_vec(c: Cur) -> None:      # u32 n; n*(u32,u32)
    c.raw(8 * _count(c, "pair"))


# ---- per-type Serialize (mode 1) --------------------------------------------

def t_11(c: Cur) -> None:          # 0x11 view (FUN_0043d200)
    c.raw(12); ec_vec(c); c.raw(8); cc_vec(c); cc_vec(c); c.raw(4); c.raw(0x68)


def t_18(c: Cur) -> None:          # 0x18/0x2a CFXSound (FUN_004492d0)
    c.raw(12); ec_vec(c); c.raw(40); sub_456d70(c); pstr(c); cc_vec(c)


def t_19(c: Cur) -> None:          # 0x19 CFXTrigger/CFXSprite (FUN_00457ea0)
    c.raw(12); ec_vec(c); c.raw(32)        # +170..+150 (8 u32)
    c.raw(76)                               # 19 u32 block
    sub_456d70(c)
    ec_vec(c)                               # +0x194
    cc_vec(c)                               # +0x128
    k = struct.unpack_from("<i", c.raw(4), 0)[0]   # +iStack_380 path-point count
    if k > 0:
        c.raw(8 * k)
    c.raw(16)                               # 358,370,36c,368
    c.raw(4)                                # +0x1a0
    mode = c.u32()                          # +0x1ac
    if mode == 2:
        for _ in range(_count(c, "bubble")):
            c.raw(8)                        # +0x104,+0x108
            has = c.u32()                   # +0x10c name flag
            if has != 0:
                pstr(c)


def t_0d(c: Cur) -> None:          # 0x0d (FUN_0044ccb0)
    c.raw(12); ec_vec(c)
    c.raw(32)                               # 114,314,1e0,1e4,1c8,1f8,208,[48c]  (8 u32)
    c.raw(4)                                # +0x1d4
    gate = c.u32()                          # +0x20c
    cc_vec(c)                               # +0x150
    sub_456d70(c)                           # +0x128
    if gate == 1:
        c.raw(8)                            # +0x190,+0x194
    cc_vec(c)                               # +0x130
    cc_vec(c)                               # +0x140
    pstr(c)                                 # trailing filename


def t_1a(c: Cur) -> None:          # 0x1a (FUN_00452100)
    c.raw(12); ec_vec(c)
    c.raw(72)                               # 18 u32
    sub_456d70(c); sub_401c00(c); sub_401c00(c)
    pair_vec(c)                             # +0x25c: count*(u32,u32)
    for _ in range(8):                      # 8 CC vectors
        cc_vec(c)
    pstr(c); pstr(c)


def t_1d(c: Cur) -> None:          # 0x1d (FUN_0044a250)
    c.raw(12); ec_vec(c)
    c.raw(8)                                # +0x154,+0x158
    for _ in range(_count(c, "1d-elem")):   # +0x134 vector, stride 0x12c
        sub_401c00(c)                       # element Serialize (24)
        c.raw(4 * _count(c, "1d-sub"))      # trailing u32 run


def t_05(c: Cur) -> None:          # 0x05 CFXItem (FUN_0043c4f0)
    c.raw(16)                               # 108,10c,110,4d8
    pstr(c); pstr(c); pstr(c); pstr(c)      # ANB + 3 textures
    c.raw(40)                               # 288(4),28c(0xc),298(0xc),7d8,7ec,7f0
    pair_vec(c)                             # +0x7dc: count*(u32,u32)


def t_07(c: Cur) -> None:          # 0x07 (FUN_00429d40)
    c.raw(12); ec_vec(c)
    c.raw(4)                                # +0x114
    pstr(c)
    c.raw(4)                                # +0x13c
    c.raw(76)                               # 19 u32
    cc_vec(c)                               # +0x248


def t_20(c: Cur) -> None:          # 0x20 (FUN_00434550)
    c.raw(12); ec_vec(c)
    c.raw(80)                                # +0x130: 5 transform elements (0x10 each),
    #                                          the vector the ctor FUN_00434200 pre-sizes to 5


def t_21(c: Cur) -> None:          # 0x21 (FUN_0042e670)
    c.raw(12); ec_vec(c); c.raw(4); ec_vec(c); cc_vec(c)


def t_1e(c: Cur) -> None:          # 0x1e (FUN_0045b6f0)
    c.raw(12); ec_vec(c); c.raw(24)         # 6 u32 of the +0x12c sub-object


def t_22(c: Cur) -> None:          # 0x22/0x25 (FUN_00428b10)
    c.raw(12); ec_vec(c); c.raw(8); cc_vec(c)


def t_23(c: Cur) -> None:          # 0x23/0x26 (FUN_00417180)
    c.raw(12); ec_vec(c); c.raw(12); cc_vec(c)


def t_24(c: Cur) -> None:          # 0x24/0x27 (FUN_00431810)
    c.raw(12); ec_vec(c); c.raw(4); cc_vec(c)


def names(c: Cur) -> None:         # u32 n; n pascal strings
    for _ in range(_count(c, "name")):
        pstr(c)


def class_d(c: Cur) -> None:       # ClassD (FUN_00409cf0): EC-vec + CC-vec
    ec_vec(c); cc_vec(c)


def t_03(c: Cur) -> None:          # 0x03 CFXCharacter (FUN_00422f80, mode 1/2/8 arm 0x4231f0)
    # CreateFromABIFile seeks back over the id (0x40d087), so every Serialize reads it again
    # into +0x108; parse() has consumed it once already. Type 3 then reads only two more.
    c.raw(8)                                # +0x10c, +0x110
    c.raw(4 * _count(c, "03-u32"))          # +0x11c: 6 elements of 1 u32 (0x409107; scene
    #                                         actors have the same vector with n = 1)
    c.raw(4)                                # +0x444
    c.raw(24)                               # +0x16c vec3, +0x160 vec3
    c.raw(20)                               # +0x28c, +0x5fc, +0x290 floats; +0x48c, +0x490
    for _ in range(_count(c, "ClassD")):    # 0x423321 -> +0x660: guarded rules
        class_d(c)
    cc_vec(c)                               # 0x4234fa -> +0x640
    cc_vec(c)                               # 0x4236c9 -> +0x650
    for _ in range(_count(c, "03-msg")):    # 0x423898: messages (none in the corpus)
        pstr(c)                             #   text -> +0x674 (shown by opcode 0x44)
        cc_vec(c)                           #   commands -> +0x684
    cc_vec(c)                               # 0x423ac0 -> +0x630
    for _ in range(_count(c, "03-react")):  # 0x423c8f: reactions (AddReactCharacter)
        c.raw(4)                            #   other character's id
        cc_vec(c)                           #   commands
    c.raw(4)                                # +0x434
    names(c)                                # +0x2e8 .anb animations
    names(c)                                # +0x330 .wav sounds
    c.raw(4)                                # +0x440
    names(c)                                # +0x30c .tga textures
    for _ in range(_count(c, "03-attach")):  # +0x344: carried objects
        pstr(c); pstr(c)                    # .ANB mesh, .tga texture
        c.raw(12)                           # +0x36c[i], +0x37c[i], +0x38c[i]
    c.raw(12)                               # +0x128, +0x13c, +0x140
    pair_vec(c)                             # +0x12c: count*(u32,u32)


TYPES = {
    0x03: t_03,
    0x05: t_05,
    0x07: t_07,
    0x0d: t_0d,
    0x11: t_11,
    0x18: t_18, 0x2a: t_18,
    0x19: t_19,
    0x1a: t_1a,
    0x1d: t_1d,
    0x1e: t_1e,
    0x20: t_20,
    0x21: t_21,
    0x22: t_22, 0x25: t_22,
    0x23: t_23, 0x26: t_23,
    0x24: t_24, 0x27: t_24,
}


def parse(d: bytes) -> dict:
    """Walk the flat record stream; raise unless every byte is consumed (bar a <8-byte tail).
    `CreateFromABIFile` reads a u32 type, then a u32 id, then the body, looping until the
    stream hits EOF; a trailing chunk too short for a full type+id just ends the loop, so a
    0..7-byte tail is tolerated (and counted as consumed). Returns
    {records:[(type,id,size)], types:Counter, tail:int}."""
    c = Cur(d)
    recs = []
    types: Counter = Counter()
    while len(d) - c.o >= 8:
        start = c.o
        t = c.u32()
        rid = c.u32()
        fn = TYPES.get(t)
        if fn is None:
            raise ParseError(f"unmodeled type {t:#x} id {rid} at {start:#x} "
                             f"({len(d) - start} bytes left)")
        fn(c)
        recs.append((t, rid, c.o - start))
        types[t] += 1
    return {"records": recs, "types": types, "tail": len(d) - c.o}


def validate(root: Path) -> int:
    files = sorted(set(root.glob("Scenes/*.abi")) | set(root.glob("Actors/*.abi")))
    if not files:
        sys.exit(f"no .abi under {root}")
    bad = 0
    nrec = 0
    tail = 0
    char = 0
    types: Counter = Counter()
    for f in files:
        d = f.read_bytes()
        if len(d) >= 4 and struct.unpack_from("<I", d, 0)[0] == 0x03:
            char += 1
        try:
            r = parse(d)
            types.update(r["types"])
            nrec += len(r["records"])
            tail += r["tail"]
        except (ParseError, struct.error) as e:
            bad += 1
            print(f"FAIL {f.name}: {e}")
    print(f"{len(files) - bad}/{len(files)} .abi parsed ({char} CFXCharacter databases), "
          f"every byte consumed; "
          f"{nrec} records ({tail} trailing padding bytes total)")
    print("  record types: " + ", ".join(f"{t:#x}:{n}" for t, n in sorted(types.items())))
    return bad


def selftest() -> None:
    # EC=20, CC=24+20n
    cc_bytes = struct.pack("<20sI", b"", 1) + b"\0" * 20   # 5u32 + count 1 + 1 EC
    c = Cur(cc_bytes); cc(c); assert c.o == 44, c.o
    # a minimal 0x07 record
    body = (struct.pack("<II", 0x07, 3) + b"\0" * 12 + struct.pack("<i", 0)   # f3 + EC count 0
            + b"\0" * 4 + struct.pack("<i", 0) + b"\0" * 4 + b"\0" * 76        # 114, str len0, 13c, 19u32
            + struct.pack("<i", 0))                                           # CC count 0
    r = parse(body)
    assert r["records"] == [(0x07, 3, len(body))], r
    # a <8-byte tail is tolerated (the original's read-type-then-EOF)
    assert parse(body + b"\0\0\0\0")["tail"] == 4
    # a record whose body runs past the end must fail
    try:
        parse(body + struct.pack("<II", 0x07, 1)); raise AssertionError("should fail")
    except ParseError:
        pass
    # a minimal 0x03 CFXCharacter: header, 1 stat, all lists empty but one .anb name
    z = struct.pack("<i", 0)
    ch = (struct.pack("<IIII", 0x03, 10, 1, 1) + struct.pack("<iI", 1, 32)  # id, act, vis, n=1
          + bytes(4 + 24 + 20) + z * 6                     # fixed block; rules, 3 CC, msgs, CC, react
          + bytes(4) + struct.pack("<ii", 1, 4) + b"a.ab"  # [0x434]; one .anb name
          + z + bytes(4) + z + z + bytes(12) + z)          # wav, [0x440], tga, attach, tail, pairs
    r = parse(ch)
    assert r["records"] == [(0x03, 10, len(ch))], r
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
