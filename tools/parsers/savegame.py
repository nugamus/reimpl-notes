"""Save files (`<exe dir>/Save/`): parser and validator. Spec: docs/engine-spec/save.md.

Every save file is the `.BIN` chunk container (binchunk.py, E-0025); this module parses
each chunk payload and insists that it is consumed exactly (E-0180..E-0184):

    Save/Info.bin              #CURRENT#   u16 current player
    Save/InfoPara.bin          #FILTER#    u32 texture filter (0 point, else bilinear)
    Save/User_<i>/Info.bin     #USERINFO#  char name[64], u16 unit reached
    Save/User_<i>/Gamesave.<n> #GAME# first, then the scene's chunks, then #PORTEF#

Samples are not corpus data: they come from runs of the original (`traces/save/`,
gitignored), so the default root is that folder.

    python tools/parsers/savegame.py                 # validate traces/save
    python tools/parsers/savegame.py --root C:/MonetRun/Save
    python tools/parsers/savegame.py --file <path> --dump
    python tools/parsers/savegame.py --selftest
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

import binchunk
from common import ParseError, Reader, corpus_argparser, run_corpus


def _game(r):
    return {"name": r.fixed_str(64), "unit": r.u16(), "scene": r.fixed_str(20)}


def _scene(r):
    return {"ambient": (r.u8(), r.u8(), r.u8()), "unk_pad": r.u8()}


def _cursor(r):
    return {"image": r.fixed_str(30), "mode": r.u32(), "pending": r.u32()}


def _actions(r):
    exhausted, runs = r.array("I", 256), r.array("I", 256)
    r.check(r.remaining % 256 == 0, "condition blocks are not 256 bytes each")
    conds = [r.fixed_str(256) for _ in range(r.remaining // 256)]
    return {"exhausted": exhausted, "runs": runs, "conditions": conds}


def _camera(r):
    return {"pos": r.array("f", 3), "unk_w": r.u32(), "yaw": r.f32(), "pitch": r.f32(),
            "sphere_radius": r.f32(), "sphere_z": r.f32(), "can_move": r.u32(),
            "can_turn": r.u32(), "collide": r.u32(), "eye_height": r.f32()}


def _objects(r):
    count = r.u32()
    return [{"name": r.fixed_str(40), "type": r.u32(), "cursor": r.u32(), "visible": r.u32(),
             "frame": r.f32(), "paused": r.u32(), "fps": r.u32(), "loop": r.u32()}
            for _ in range(count)]


def _animations(r):
    nodes = []
    while r.remaining:
        node = {"name": r.fixed_str(64), "count": r.u16(), "active": r.u16(), "slots": []}
        for _ in range(node["count"]):
            node["slots"].append({
                "slot": r.index(r.u16(), 16, "slot"), "path": r.fixed_str(260),
                "name": r.fixed_str(64), "enabled": r.u32(), "paused": r.u32(),
                "loop": r.u32(), "pingpong": r.u32(), "backward": r.u32(), "frame": r.f32(),
                "fps": r.f32(), "first": r.u32(), "last": r.u32(),
                "unk_1cc": r.u32(), "unk_1d0": r.u32()})
        nodes.append(node)
    return nodes


def _gauge(r):
    return {"name": r.fixed_str(30), "visible": r.u32(), "duration_ms": r.u32(),
            "elapsed_ms": r.u32()}


def _portef(r):
    last = r.i32()
    r.check(last >= -1, f"last index {last}")
    return [r.fixed_str(30) for _ in range(last + 1)]


def _u32s(n):
    return lambda r: r.array("I", n)


PAYLOADS = {
    "#GAME#": _game, "#SCENE#": _scene, "#CURSOR#": _cursor, "#ACTIONS#": _actions,
    "#CAMERA#": _camera, "#OBJECTS#": _objects, "#ANIMATIONS#": _animations,
    "#JAUGE#": _gauge, "#PORTEF#": _portef,
    "#TRAIN_CHANGED#": _u32s(2), "#TIMEVENDEUSE#": _u32s(4), "#PARAMS#": _u32s(3),
    "#PLANCHE#": _u32s(1),
    "#CURRENT#": lambda r: r.u16(), "#FILTER#": lambda r: r.u32(),
    "#USERINFO#": lambda r: {"name": r.fixed_str(64), "unit": r.u16()},
}

# Which chunk sets a file may hold: players file, settings, player info, game save.
SHAPES = [{"#CURRENT#"}, {"#FILTER#"}, {"#USERINFO#"}]
GAME_REQUIRED = {"#GAME#", "#SCENE#", "#CURSOR#", "#ACTIONS#", "#CAMERA#", "#PORTEF#"}


def parse(data: bytes) -> dict[str, object]:
    chunks = binchunk.parse(data)
    names = set(chunks)
    if names not in SHAPES:
        missing = GAME_REQUIRED - names
        if missing:
            raise ParseError(f"not a save file: chunks {sorted(names)}", 0)
        # GAME is written first: the save lists read the name from offset 0 (E-0183).
        if not data.startswith(chunks["#GAME#"]):
            raise ParseError("#GAME# is not at offset 0", 0)
    out = {}
    for name, payload in chunks.items():
        if name not in PAYLOADS:
            raise ParseError(f"unknown chunk {name}", 0)
        r = Reader(payload, name=name)
        out[name] = PAYLOADS[name](r)
        r.expect_eof()
    return out


def _chunked(chunks: list[tuple[str, bytes]]) -> bytes:
    body, table, pos = b"", b"", 0
    for name, payload in chunks:
        table += struct.pack("<20sII", name.encode(), pos, len(payload))
        body += payload
        pos += len(payload)
    return body + table + struct.pack("<I", len(chunks))


def _selftest() -> None:
    game = b"Mine\0".ljust(64, b"\xcd") + struct.pack("<H", 1) + b"U01.X3D\0".ljust(20, b"Z")
    slot = (struct.pack("<H", 1) + b"C:\\Data\\U01/Anim/x.A3D\0".ljust(260, b"\xcd")
            + b"GiveCard\0".ljust(64, b"\xcd") + struct.pack("<5I2f4I", 1, 0, 0, 0, 0,
                                                            25.0, 15.0, 1, 25, 0, 0))
    base = [
        ("#GAME#", game), ("#SCENE#", b"\xff\xff\xff\xcd"),
        ("#CURSOR#", b"\xcd" * 30 + struct.pack("<2I", 0, 0)),
        ("#ACTIONS#", bytes(2048) + b"TRUE".ljust(256, b"\0")),
        ("#CAMERA#", struct.pack("<3fI4f3If", 1, 2, 3, 0, 4.7, 1.5, 20, 37, 0, 0, 1, 60)),
        ("#OBJECTS#", struct.pack("<I", 1) + b"*U01_01".ljust(40, b"\0")
         + struct.pack("<3If3I", 6, 3, 1, 1.0, 0, 15, 1)),
        ("#ANIMATIONS#", b"*U01_02".ljust(64, b"\0") + struct.pack("<2H", 1, 1) + slot),
        ("#PORTEF#", struct.pack("<i", 0) + b"U02_01P".ljust(30, b"\0")),
    ]
    got = parse(_chunked(base))
    assert got["#GAME#"] == {"name": "Mine", "unit": 1, "scene": "U01.X3D"}
    assert got["#ANIMATIONS#"][0]["slots"][0]["frame"] == 25.0
    assert got["#PORTEF#"] == ["U02_01P"]
    assert parse(_chunked([("#CURRENT#", b"\1\0")])) == {"#CURRENT#": 1}
    bad = [
        base[1:] + base[:1],                                    # GAME not first
        base[:-1] + [("#PORTEF#", struct.pack("<i", 1) + bytes(30))],  # one item short
        base[:1] + [("#SCENE#", b"\xff\xff\xff")] + base[2:],   # short payload
        base + [("#BOGUS#", b"")],                              # unknown chunk
        base[:2],                                               # incomplete save
    ]
    for chunks in bad:
        try:
            parse(_chunked(chunks))
        except ParseError:
            continue
        raise AssertionError(f"accepted {[n for n, _ in chunks]}")
    print("selftest ok")


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        _selftest()
        return 0
    ap = corpus_argparser("Save file validator")
    ap.add_argument("--dump", action="store_true")
    args = ap.parse_args(argv)
    if args.file:
        out = parse(args.file.read_bytes())
        if args.dump:
            for name, value in out.items():
                print(name, value)
        print(f"ok {args.file}")
        return 0
    root = args.root or Path(__file__).resolve().parents[2] / "traces" / "save"
    ok = True
    for pattern in ("Gamesave.*", "*.bin"):
        ok &= run_corpus(parse, pattern, root, args.verbose).complete
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
