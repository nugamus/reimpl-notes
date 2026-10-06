"""Run CFXCharacter's action function `FUN_0041fde0` under Unicorn and print the clip queue
it builds (E-0801), for every (action, current clip) pair.

The function is a large switch over the action and the clip playing (`+0x434`) that pushes
clip numbers onto the character's clip queue (a `std::deque<int>` at `+0x404`); its
decompile is long and the deque code is inlined, so instead of reading it we run it, like
`abiemu.py` runs Serialize. The character is Grumpa (id 10) built from
`Actors/Characters.abi` by `abiemu.Emu`; its clip table `+0x2dc` gets fake meshes whose
frame count `+0x118` is that of the real `.anb`.

    python engines/grumpa/tools/charemu.py [--id 10] [--selftest]
"""

from __future__ import annotations

import argparse
import math
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "parsers"))
import abiemu  # noqa: E402

ACTION = 0x41fde0
CLEAR = 0x426d40          # deque clear
CHARS = abiemu.REPO / "games/grumpa/discs/cab/Actors/Characters.abi"
MESHES = abiemu.REPO / "games/grumpa/discs/cab/Meshes"


def character(cid: int) -> tuple[abiemu.Emu, int, list[str]]:
    e = abiemu.Emu(CHARS.read_bytes())
    while True:
        rid = struct.unpack_from("<I", e.data, e.pos + 4)[0]
        start = e.log.__len__()
        e.record()
        if rid == cid:
            break
    obj = e.obj
    # the clip names: the pascal strings Serialize read (count +0x2e8, pointers +0x2f0..+0x2f4)
    names = []
    begin, end = e.u32(obj + 0x2f0), e.u32(obj + 0x2f4)  # count at +0x2e8
    for p in range(begin, end, 4):
        s = bytes(e.uc.mem_read(e.u32(p), 64)).split(b"\0")[0].decode("latin1")
        names.append(s)
    return e, obj, names


def setup_meshes(e: abiemu.Emu, obj: int, names: list[str]) -> dict[int, int]:
    """Clip number (the name's leading number, as LoadResources indexes it) -> frames."""
    table = e.heap
    e.heap += 0x100 * 4
    e.uc.mem_write(table, b"\0" * 0x400)
    frames = {}
    for n in names:
        k = int(n[:3])
        f = MESHES / n
        cand = [q for q in MESHES.iterdir() if q.name.lower() == n.lower()]
        fr = struct.unpack_from("<I", cand[0].read_bytes())[0] if cand else 1
        mesh = e.heap
        e.heap += 0x160
        e.uc.mem_write(mesh, b"\0" * 0x160)
        e.uc.mem_write(mesh + 0x118, struct.pack("<I", fr))
        e.uc.mem_write(table + 4 * k, struct.pack("<I", mesh))
        frames[k] = fr
    e.uc.mem_write(obj + 0x2dc, struct.pack("<I", table))
    return frames


def queue(e: abiemu.Emu, obj: int) -> list[int]:
    n = e.u32(obj + 0x430)
    # MSVC 6 deque iterators are (block first, block last, cur, node): begin at +0x408
    last, cur, node = e.u32(obj + 0x40c), e.u32(obj + 0x410), e.u32(obj + 0x414)
    out = []
    for _ in range(n):
        if cur == last:            # next block of the deque
            node += 4
            cur = e.u32(node)
            last = cur + 0x1000
        out.append(e.u32(cur))
        cur += 4
    return out


def act(e: abiemu.Emu, obj: int, clip: int, action: int, angle: float = 0.0) -> dict:
    e.call(CLEAR, obj + 0x404, [])
    for off, v in ((0x434, clip), (0x494, 0), (0x47c, 0), (0x4dc, 0), (0x4ac, 0)):
        e.uc.mem_write(obj + off, struct.pack("<i", v))
    e.uc.mem_write(obj + 0x164, struct.pack("<f", 0.0))
    e.uc.mem_write(obj + 0x4b8, struct.pack("<f", 0.0))
    e.call(ACTION, obj, [action & 0xffffffff, struct.unpack("<I", struct.pack("<f", angle))[0]])
    f = lambda o: struct.unpack("<f", e.uc.mem_read(obj + o, 4))[0]
    return {"queue": queue(e, obj), "clip": e.u32(obj + 0x434), "frame": e.u32(obj + 0x494),
            "turn_steps": e.u32(obj + 0x4ac), "turn_rate": f(0x4b8)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", type=int, default=10)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    e, obj, names = character(a.id)
    frames = setup_meshes(e, obj, names)
    if a.selftest:
        r = act(e, obj, 0, -1, 1.0)
        assert r["queue"] == [] and r["turn_steps"] == 10 and abs(r["turn_rate"] - 0.1) < 1e-6, r
        r = act(e, obj, 0, 0, 0.0)
        assert r["queue"] and r["queue"][-1] == 2, r      # idle + walk -> ... the walk loop
        print("selftest ok")
        return
    print("clips:", ", ".join(f"{k}={n}" for k, n in sorted((int(n[:3]), n) for n in names)))
    clips = sorted(frames)
    for action in list(range(-1, 6)) + list(range(0x12, 0x16)):
        for clip in clips:
            try:
                r = act(e, obj, clip, action, 0.5)
            except abiemu.UcError as err:
                print(f"action {action:3d} clip {clip:2d}: emulation error {err}")
                continue
            print(f"action {action:3d} clip {clip:2d}: queue {r['queue']} now clip {r['clip']} "
                  f"frame {r['frame']} turn {r['turn_steps']} x {r['turn_rate']:.3f}")


if __name__ == "__main__":
    main()
