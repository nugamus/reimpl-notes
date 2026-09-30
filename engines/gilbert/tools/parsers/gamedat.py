"""`default.dat` game database (and saved games): an MFC 6 CArchive written by ge.dll, engine `gilbert`.

    Header (the game object's Load 0x100031f0 / Save 0x100034e0), then 17 CObLists of
    serialised objects (CObList::Serialize 0x1001565f: count, then ReadObject per element).
    See engines/gilbert/docs/formats/README.md, section "default.dat".

    python engines/gilbert/tools/parsers/gamedat.py            # validate the corpus
    python engines/gilbert/tools/parsers/gamedat.py FILE...    # dump the objects
    python engines/gilbert/tools/parsers/gamedat.py --selftest
"""

from __future__ import annotations

import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
DATA = REPO / "games/gilbert/discs/cd/Program/Data"

# Each class's Serialize, in archive order: ("u32" | "s32" | "str" | "rect" | "list", field name + the
# member offset the Serialize function uses). "rect" = 16 raw bytes, four s32.
CLASSES = {
    "CWalkmap": [("list", "cuas_1c"), ("u32", "id_04"), ("str", "title_08"), ("rect", "radar_rect_0c")],
    "CCUA": [("list", "objs_20"), ("u32", "id_08"), ("str", "name_0c"), ("u32", "first_event_10"),
             ("u32", "event_14"), ("u32", "end_event_18"), ("u32", "first_visit_1c")],
    "CObj": [("list", "states_14"), ("u32", "cua_id_08"), ("u32", "id_0c"), ("u32", "visible_10"),
             ("u32", "state_30")],
    "CObjState": [("u32", "state_04"), ("str", "name_08"), ("u32", "walkmap_anim_0c"),
                  ("u32", "cua_anim_10"), ("u32", "click_event_14"), ("u32", "take_event_18"),
                  ("u32", "unk_1c"), ("u32", "pickable_20"), ("str", "text_24")],
    "CAnim": [("u32", "time_04"), ("u32", "id_08"), ("u32", "next_0c"), ("str", "name_10"),
              ("u32", "duration_14"), ("u32", "unk_18"), ("u32", "unk_1c"), ("u32", "unk_20"),
              ("u32", "z_24"), ("u32", "unk_28"), ("u32", "end_event_2c")],
    "CUseObj": [("u32", "obj_04"), ("u32", "target_08"), ("u32", "event_0c")],
    "CEvent": [("u32", "id_04"), ("u32", "type_08"), ("u32", "cond_0c"), ("u32", "var_10"),
               ("s32", "value_14")]
              + [("u32", n) for n in ("jump_18", "walkmap_1c", "cua_20", "obj_24", "book_28", "topic_2c",
                                     "topic2_30", "dialog_34", "sound_38", "sound_3c")]
              + [("str", "sound_40"), ("u32", "sound_44"), ("u32", "unk_48"), ("str", "video_4c"),
                 ("u32", "x_50"), ("u32", "y_54"), ("u32", "unk_58"), ("str", "comment_5c")],
    "CDialogs": [("list", "choices_04"), ("u32", "id_20"), ("str", "title_24"), ("str", "text_28")],
    "CDialogChoice": [("u32", "unk_04"), ("str", "text_08"), ("u32", "event_0c")],
    "CTopic": [("u32", "id_04"), ("str", "title_08"), ("str", "text_0c"), ("u32", "shown_10"),
               ("s32", "index_14")],
    "CText": [("u32", "id_04"), ("str", "text_08")],
}

# The game object's lists in file order, named after their member offset in the 0x2fa40-byte
# game object, and the one class the text loaders put in each.
LISTS = [("walkmaps_36c", "CWalkmap"), ("inventory_2f1d4", "CObj"), ("useobjs_2f20c", "CUseObj"),
         ("events_2f228", "CEvent"), ("dialogs_2f244", "CDialogs"), ("texts_2f264", "CText")]
NVARS, NBOOKS = 200, 10


class Obj(dict):
    """One deserialised object: its class name in .cls, its fields as items."""

    def __init__(self, cls: str):
        super().__init__()
        self.cls = cls


class Reader:
    def __init__(self, data: bytes):
        self.d, self.p = data, 0
        self.loaded: list = [None]  # MFC load array: index 0 = NULL, then classes and objects in order
        self.refs = 0

    def take(self, n: int) -> bytes:
        if self.p + n > len(self.d):
            raise ValueError(f"read past the end at {self.p:#x}")
        b = self.d[self.p:self.p + n]
        self.p += n
        return b

    def u8(self) -> int:
        return self.take(1)[0]

    def u16(self) -> int:
        return struct.unpack("<H", self.take(2))[0]

    def u32(self) -> int:
        return struct.unpack("<I", self.take(4))[0]

    def s32(self) -> int:
        return struct.unpack("<i", self.take(4))[0]

    def string(self) -> str:  # CString >> (0x1001ade2 / 0x1001ad8b)
        n = self.u8()
        if n == 0xFF:
            n = self.u16()
            if n == 0xFFFE:
                raise ValueError(f"Unicode CString at {self.p:#x}")
            if n == 0xFFFF:
                n = self.u32()
        return self.take(n).decode("cp1252")

    def count(self) -> int:  # CArchive::ReadCount 0x1001b3ba
        n = self.u16()
        return self.u32() if n == 0xFFFF else n

    def obj(self):  # CArchive::ReadObject 0x1001a90c / ReadClass 0x1001ab44
        at = self.p
        tag = self.u16()
        big = self.u32() if tag == 0x7FFF else ((tag & 0x8000) << 16) | (tag & 0x7FFF)
        if tag == 0xFFFF:
            schema, n = self.u16(), self.u16()
            name = self.take(n).decode("ascii")
            if name not in CLASSES or schema != 1:
                raise ValueError(f"class {name!r} schema {schema} at {at:#x}")
            self.loaded.append(name)
        elif big & 0x80000000:
            i = big & 0x7FFFFFFF
            if not 0 < i < len(self.loaded) or not isinstance(self.loaded[i], str):
                raise ValueError(f"bad class index {i} at {at:#x}")
            name = self.loaded[i]
        else:  # reference to an object already loaded (0 = NULL)
            if big >= len(self.loaded) or isinstance(self.loaded[big], str):
                raise ValueError(f"bad object index {big} at {at:#x}")
            self.refs += 1
            return self.loaded[big]
        o = Obj(name)
        self.loaded.append(o)
        for kind, field in CLASSES[name]:
            o[field] = (self.u32() if kind == "u32" else self.s32() if kind == "s32"
                        else self.string() if kind == "str" else self.oblist() if kind == "list"
                        else struct.unpack("<4i", self.take(16)))
        return o

    def oblist(self) -> list:  # CObList::Serialize 0x1001565f
        return [self.obj() for _ in range(self.count())]


def parse(data: bytes) -> dict:
    r = Reader(data)
    g = {"walkmap_first": r.u32(), "start_x_08": r.u32(), "start_y_0c": r.u32(), "unk_10": r.u32()}
    if r.u32() != NVARS:
        raise ValueError("variable count is not 200")
    g["vars_4c"] = [r.s32() for _ in range(NVARS)]
    g["walkmap_04"] = r.u32()
    for name, _ in LISTS:
        g[name] = r.oblist()
    if r.u32() != NBOOKS:
        raise ValueError("book count is not 10")
    g["books_2f280"] = [r.oblist() for _ in range(NBOOKS)]
    g["anims_2fa24"] = r.oblist()
    if r.p != len(data):
        raise ValueError(f"{len(data) - r.p} trailing bytes at {r.p:#x}")
    g["_refs"], g["_loaded"] = r.refs, r.loaded
    return g


def walk(o: dict, path: str, out: list) -> list:
    """(where, object) for every object, depth first."""
    for k, v in o.items():
        if not isinstance(v, list) or k.startswith("_"):
            continue
        for x in v:
            for y in (x if isinstance(x, list) else [x]):
                if isinstance(y, Obj):
                    out.append((f"{path}{k}", y))
                    walk(y, f"{y.cls}.", out)
    return out


def validate() -> int:
    files = sorted((DATA / "game").glob("*.dat"))
    bad = 0
    for f in files:
        try:
            g = parse(f.read_bytes())
            objs = walk(g, "", [])
            wrong = [(w, o.cls) for w, o in objs if w in dict(LISTS) and o.cls != dict(LISTS)[w]]
            if wrong:
                raise ValueError(f"unexpected class in a list: {wrong[:3]}")
        except (ValueError, UnicodeDecodeError) as e:
            bad += 1
            print(f"FAIL {f.name}: {e}")
            continue
        print(f"{f.name}: {len(objs)} objects, {sum(isinstance(o, str) for o in g['_loaded'])} classes, "
              f"{g['_refs']} object references; header walkmap {g['walkmap_first']}/{g['walkmap_04']} "
              f"start {g['start_x_08']},{g['start_y_0c']} unk_10 {g['unk_10']}, "
              f"nonzero variables {sum(1 for v in g['vars_4c'] if v)}")
        for k, v in sorted(Counter(f"{w}: {o.cls}" for w, o in objs).items()):
            print(f"  {v:5}  {k}")
        print("  topics per book: " + " ".join(str(len(b)) for b in g["books_2f280"]))
        ev = [o for w, o in objs if o.cls == "CEvent"]
        print(f"  {len({e['id_04'] for e in ev})} event IDs; records per type: "
              + " ".join(f"{t}:{n}" for t, n in sorted(Counter(e["type_08"] for e in ev).items())))
        print("  type 18 conditions: " + " ".join(
            f"{t}:{n}" for t, n in sorted(Counter(e["cond_0c"] for e in ev if e["type_08"] == 18).items())))
    print(f"{len(files) - bad}/{len(files)} parsed, every byte consumed")
    return 1 if bad else 0


def dump(path: Path) -> None:
    g = parse(path.read_bytes())
    print({k: g[k] for k in ("walkmap_first", "start_x_08", "start_y_0c", "unk_10", "walkmap_04")})
    print("vars_4c", {i: v for i, v in enumerate(g["vars_4c"]) if v})
    for where, o in walk(g, "", []):
        print(f"{where}: {o.cls} " + " ".join(f"{k}=<{len(v)}>" if isinstance(v, list) else f"{k}={v!r}"
                                          for k, v in o.items()))


def selftest() -> None:
    def s(t: bytes) -> bytes:
        return bytes([len(t)]) + t
    w = struct.pack
    body = w("<5I", 7, 320, 258, 0, NVARS) + w("<200I", *range(NVARS)) + w("<I", 7)
    # walkmaps: one CWalkmap (class 1, object 2) holding one CCUA (class 3, object 4) with no
    # objects, then a reference back to the walkmap (object index 2)
    body += w("<HHHH", 2, 0xFFFF, 1, 8) + b"CWalkmap" + w("<HHHH", 1, 0xFFFF, 1, 4) + b"CCUA"
    body += w("<HI", 0, 5) + s(b"cua") + w("<4I", 1, 2, 3, 4)
    body += w("<I", 7) + s(b"walk") + w("<4i", 1, 2, 3, -4) + w("<H", 2)
    body += w("<H", 0) * 5 + w("<I", NBOOKS) + w("<H", 0) * NBOOKS
    # anims: two CAnim, the second through a class reference (0x8005) and a long name
    anim = w("<3I", 0, 10, 10) + b"%s" + w("<7I", *range(7))
    body += w("<HHHH", 2, 0xFFFF, 1, 5) + b"CAnim" + anim.replace(b"%s", s(b"hej"))
    body += w("<H", 0x8005) + anim.replace(b"%s", b"\xff" + w("<H", 300) + b"d\xe5g" * 100)
    g = parse(body)
    wm = g["walkmaps_36c"][0]
    assert g["walkmaps_36c"][1] is wm and wm["title_08"] == "walk" and wm["radar_rect_0c"] == (1, 2, 3, -4)
    assert wm["cuas_1c"][0]["name_0c"] == "cua" and g["_refs"] == 1 and g["vars_4c"][199] == 199
    assert [a["name_10"][:3] for a in g["anims_2fa24"]] == ["hej", "dåg"]
    for bad in (body + b"\0", body[:-1]):
        try:
            parse(bad)
            raise AssertionError("bad length accepted")
        except ValueError:
            pass
    print("selftest ok")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--selftest"]:
        selftest()
    elif args:
        sys.stdout.reconfigure(encoding="utf-8")
        for a in args:
            dump(Path(a))
    else:
        sys.exit(validate())
