r"""China's save games (Data\Saved\_game<1..12>.sav, Data\Saved\<NAME>.sav).

Specced from CHINE.EXE only: the corpus has no saves (README "Save games", china_sav.ksy;
E-0208). Layout, all little-endian: 227 u32 game variables, 36 pairs of u32 object
fields, a 256-byte place name, two f32 view angles, then the minutes the player holds
(u32 count; per minute u32 length + that many bytes, no NUL). 1464 bytes (with the count) + minutes.

The variable and object tables are read from CHINE.EXE so a save can be shown by name:
    python engines/cryomni3d/tools/parsers/sav.py <file.sav>...
    python engines/cryomni3d/tools/parsers/sav.py --tables   # print both tables
    python engines/cryomni3d/tools/parsers/sav.py --selftest # synthetic save round trip
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "games/china/discs/en-iso/cd1/CHINE/CHINE.EXE"
NVARS, NOBJS, PLACE = 227, 36, 256
VARS_VA, VAR_STRIDE = 0x45EEC4, 12   # {char *name; u32 value; u32 id}; value is saved
OBJS_VA, OBJ_STRIDE = 0x45D5E4, 0x30  # {u32 unk_0; u32 unk_4; char *name; ...}
MAX_MINUTES, MINUTE_ID = 50, 14       # 50 slots of 15 bytes at 0x51e3c8


class FormatError(Exception):
    pass


def exe_reader(path: Path = EXE):
    d = path.read_bytes()
    pe = struct.unpack_from("<I", d, 0x3C)[0]
    n, opt = struct.unpack_from("<H", d, pe + 6)[0], struct.unpack_from("<H", d, pe + 20)[0]
    secs = [struct.unpack_from("<8sIIII", d, pe + 24 + opt + i * 40) for i in range(n)]

    def rd(va: int, size: int) -> bytes:
        for _, _, rva, rsize, raw in secs:
            if rva <= va - 0x400000 < rva + rsize:
                o = raw + va - 0x400000 - rva
                return d[o:o + size]
        return b"\0" * size  # bss

    def cstr(va: int) -> str:
        return rd(va, 64).split(b"\0")[0].decode("latin1") if va else ""

    return rd, cstr


def tables() -> tuple[list[str], list[str]]:
    rd, cstr = exe_reader()
    var_names = [cstr(struct.unpack_from("<I", rd(VARS_VA + i * VAR_STRIDE, 4))[0])
                 for i in range(NVARS)]
    obj_names = [cstr(struct.unpack_from("<I", rd(OBJS_VA + i * OBJ_STRIDE + 8, 4))[0])
                 for i in range(NOBJS - 1)] + ["(past the table)"]
    var_names[-1] = "(past the table)"
    return var_names, obj_names


def read(blob: bytes) -> dict:
    fixed = NVARS * 4 + NOBJS * 8 + PLACE + 8 + 4
    if len(blob) < fixed:
        raise FormatError(f"{len(blob)} bytes, at least {fixed} expected")
    p = 0
    variables = list(struct.unpack_from(f"<{NVARS}I", blob, p))
    p += NVARS * 4
    objects = [struct.unpack_from("<Ii", blob, p + i * 8) for i in range(NOBJS)]
    p += NOBJS * 8
    place = blob[p:p + PLACE].split(b"\0")[0].decode("latin1")
    p += PLACE
    view = struct.unpack_from("<2f", blob, p)
    p += 8
    (count,) = struct.unpack_from("<I", blob, p)
    p += 4
    if count > MAX_MINUTES:
        raise FormatError(f"{count} minutes, the game holds {MAX_MINUTES}")
    minutes = []
    for _ in range(count):
        if p + 4 > len(blob):
            raise FormatError("minute length past EOF")
        (n,) = struct.unpack_from("<I", blob, p)
        if n > MINUTE_ID or p + 4 + n > len(blob):
            raise FormatError(f"minute id of {n} bytes")
        minutes.append(blob[p + 4:p + 4 + n].decode("latin1"))
        p += 4 + n
    if p != len(blob):
        raise FormatError(f"{len(blob) - p} bytes after the minutes")
    return {"variables": variables, "objects": objects, "place": place, "view": view,
            "minutes": minutes}


def write(s: dict) -> bytes:
    out = struct.pack(f"<{NVARS}I", *s["variables"])
    out += b"".join(struct.pack("<Ii", *o) for o in s["objects"])
    out += s["place"].encode("latin1").ljust(PLACE, b"\0")
    out += struct.pack("<2fI", *s["view"], len(s["minutes"]))
    for m in s["minutes"]:
        out += struct.pack("<I", len(m)) + m.encode("latin1")
    return out


def selftest() -> None:
    s = {"variables": list(range(NVARS)), "objects": [(0, -1)] * NOBJS, "place": "PNE001",
         "view": (1.5, -0.25), "minutes": ["MIN001", "MINPN102"]}
    blob = write(s)
    assert len(blob) == 1464 + 4 + 6 + 4 + 8
    assert read(blob) == s
    try:
        read(blob + b"\0")
        raise AssertionError
    except FormatError:
        pass
    v, o = tables()
    assert v[0] == "MODE_VISITE" and v[1] == "CHAPITRE" and o[0] == "LISTE_BOITES", (v[:2], o[:1])
    assert o[34] == "CLE_JARRE", o[34]
    print("selftest ok")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tables", action="store_true")
    ap.add_argument("files", nargs="*", type=Path)
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    if a.tables:
        v, o = tables()
        for i, n in enumerate(v):
            print(f"var {i:3} {n}")
        for i, n in enumerate(o):
            print(f"obj {i:3} {n}")
        return 0
    ok = 0
    for f in a.files:
        try:
            r = read(f.read_bytes())
            print(f"ok   {f.name}: place {r['place']!r} view {r['view']} "
                  f"minutes {len(r['minutes'])}")
            ok += 1
        except FormatError as e:
            print(f"FAIL {f.name}: {e}")
    print(f"{ok}/{len(a.files)} saves parsed (the corpus has none)")
    return 0 if ok == len(a.files) else 1


if __name__ == "__main__":
    sys.exit(main())
