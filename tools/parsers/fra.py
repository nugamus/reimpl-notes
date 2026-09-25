"""`.FRA` (2D frame) parser and corpus validator. Spec: docs/formats/fra.ksy, E-0100.

A frame file is the serialised object list of one 2D screen, read by `LFrameReader`
(`LFrameReader.cpp:97`, `0x0042d290`) and built by `LClassCreator` (`LClassCreator.cpp:128`,
`0x0042e4e0`):

    u32 object_count
    object_count x {
        u32 class_tag                 4 ASCII bytes, e.g. "TIB#"
        class body                    fixed size per class, read by its constructor
        properties until u32 0:  { u32 prop_tag ("RCS@" ...), prop body }
    }

Tags are MSVC multi-character constants ('#BIT' is stored "TIB#"); the bytes in the file are
used as the names here. Body sizes are the `FUN_0042d3c0` read lengths of each constructor
chain (E-0100). `nCC#` / `nIC#` (video frames) are registered in neither EXE; their size
is from the corpus only (5 + 2 files, all end exactly after it).

    python tools/parsers/fra.py                 # validate the corpus
    python tools/parsers/fra.py --selftest
    python tools/parsers/fra.py --file <path>   # dump one frame
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ParseError, Reader, main_for  # noqa: E402

# View base (#VIE, 0x4342f0): 9 x u32.
VIEW_FIELDS = ("id", "x", "y", "w", "h", "visible", "parent", "unk_7", "unk_8")


def _view(r: Reader) -> dict:
    return dict(zip(VIEW_FIELDS, r.array("i", 9)))


def _bitmap(r: Reader) -> dict:  # #BIT 0x423ea0: 0x2c bytes
    dx, dy = r.array("i", 2)
    return {"bmp_dx": dx, "bmp_dy": dy, "bitmap": r.fixed_str(32), "unk_blit": r.i32()}


def _scroll(r: Reader) -> dict:  # #SCR 0x4325d0: 0x6c bytes
    out = {"name_a": r.fixed_str(32)}
    out["unk_a"], out["unk_b"] = r.array("i", 2)
    out["name_b"] = r.fixed_str(32)
    out["name_c"] = r.fixed_str(32)
    out["unk_c"] = r.i32()
    return out


def _vol(r: Reader) -> dict:  # #Vol 0x434d30: 0x24 bytes
    return {"unk_a": r.i32(), "name": r.fixed_str(32)}


def _video(r: Reader) -> dict:  # nCC# / nIC#: not in either EXE, corpus layout
    return {"unk_a": r.i32(), "file": r.fixed_str(32)}


# class tag -> extra body readers after the view base, in constructor order
CLASSES = {
    b"EIV#": (),                     # view
    b"vop#": (),                     # inventory strip (PorteF id 200)
    b"bop#": (),                     # inventory scroll button
    b"idE#": (),                     # text edit
    b"dEU#": (),                     # user-name edit
    b"dES#": (),                     # save-name edit
    b"TIB#": (_bitmap,),
    b"POL#": (_bitmap, lambda r: dict(zip(("unk_a", "unk_b"), r.array("i", 2)))),
    b"RCS#": (_scroll,),
    b"AOL#": (_scroll,),             # load list
    b"VAS#": (_scroll,),             # save list
    b"cSU#": (_scroll,),             # user list
    b"loV#": (_vol,),
    b"BoV#": (_vol,),
    b"AoV#": (_vol,),
    b"nCC#": (_video,),
    b"nIC#": (_video,),
}

PROPS = {
    b"ucg@": lambda r: {"cursor": r.i32()},                       # 0x426ac0
    b"RUC@": lambda r: {"unk_a": r.i32()},                        # 0x42e8b0
    b"ARD@": lambda r: {"unk_a": r.i32()},                        # 0x42ea30
    b"ARF@": lambda r: {"frame": r.fixed_str(32)},                # 0x42d070
    b"RCS@": lambda r: {"command": r.fixed_str(32)},              # 0x4322f0
    b"LIH@": lambda r: {"bitmap": r.fixed_str(32), "dx": r.i32(), "dy": r.i32()},  # 0x42ec90
    b"GIH@": lambda r: {"bitmap": r.fixed_str(32), "dx": r.i32(), "dy": r.i32()},  # 0x42ef90
    b"INA@": lambda r: {"unk": r.bytes(0x38)},                    # 0x42d4f0
}


def parse(data: bytes) -> dict:
    r = Reader(data)
    objects = []
    for _ in range(r.u32()):
        at = r.pos
        tag = r.bytes(4)
        if tag not in CLASSES:
            raise ParseError(f"unknown class tag {tag!r}", at)
        obj = {"class": tag.decode(), **_view(r)}
        for body in CLASSES[tag]:
            obj.update(body(r))
        props = []
        while True:
            at = r.pos
            ptag = r.bytes(4)
            if ptag == b"\0\0\0\0":
                break
            if ptag not in PROPS:
                raise ParseError(f"unknown property tag {ptag!r}", at)
            props.append({"prop": ptag.decode(), **PROPS[ptag](r)})
        obj["props"] = props
        objects.append(obj)
    r.expect_eof()
    return {"objects": objects}


def _selftest() -> None:
    def view(i, parent=0):
        return struct.pack("<9i", i, 10, 20, 30, 40, 1, parent, 0, 0)

    def name(s):
        return s.encode().ljust(32, b"\0")

    blob = (
        struct.pack("<I", 2)
        + b"TIB#" + view(1) + struct.pack("<2i", 0, 0) + name("UserFond") + struct.pack("<i", 0x60)
        + b"ucg@" + struct.pack("<i", 0) + b"\0\0\0\0"
        + b"EIV#" + view(2, 1)
        + b"RCS@" + name("SelectUser") + b"LIH@" + name("UserOKH") + struct.pack("<2i", 0, 0)
        + b"\0\0\0\0"
    )
    doc = parse(blob)
    a, b = doc["objects"]
    assert a["class"] == "TIB#" and a["bitmap"] == "UserFond" and a["unk_blit"] == 0x60
    assert a["props"] == [{"prop": "ucg@", "cursor": 0}]
    assert b["parent"] == 1 and b["props"][0]["command"] == "SelectUser"
    assert b["props"][1]["bitmap"] == "UserOKH"
    for bad in (blob + b"\0", blob[:-1], blob.replace(b"EIV#", b"XXX#")):
        try:
            parse(bad)
        except ParseError:
            pass
        else:
            raise AssertionError("bad frame accepted")
    print("selftest ok")


def _dump(path: Path) -> None:
    for o in parse(path.read_bytes())["objects"]:
        extra = {k: v for k, v in o.items() if k not in VIEW_FIELDS + ("class", "props")}
        print(f"{o['class']} id={o['id']} rect=({o['x']},{o['y']},{o['w']},{o['h']})"
              f" vis={o['visible']} parent={o['parent']} u7={o['unk_7']} u8={o['unk_8']} {extra}")
        for p in o["props"]:
            print(f"    {p}")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
        sys.exit(0)
    if "--file" in sys.argv:
        _dump(Path(sys.argv[sys.argv.index("--file") + 1]))
        sys.exit(0)
    sys.exit(main_for(parse, "**/*.fra", ".FRA validator"))
