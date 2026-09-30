"""`ctrl<room>.map` control maps (wDx TDxMaps files, magic `ML01`), engine `gilbert`.

    "ML01", s32 high index (0: one map), then per map a 32-byte record and its data:
      +0x00 name, Delphi string[15] (length byte + 15 bytes, tail uninitialised)
      +0x10 u32 width in cells, +0x14 u32 height in cells (cells are 16x16 pixels)
      +0x18 u32 data size (= width * height * 10), +0x1c u32 unk_ptr (editor memory)
      data: width*height u32 cell values, row-major, then 6*width*height bytes unk_tail
    See engines/gilbert/docs/formats/README.md.

    python engines/gilbert/tools/parsers/ctrlmap.py            # validate the corpus
    python engines/gilbert/tools/parsers/ctrlmap.py FILE...    # draw the cell grid
    python engines/gilbert/tools/parsers/ctrlmap.py --selftest
"""

from __future__ import annotations

import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
DATA = REPO / "games/gilbert/discs/cd/Program/Data"


def parse(data: bytes) -> list[dict]:
    if data[:4] != b"ML01":
        raise ValueError("no ML01 magic")
    high = struct.unpack_from("<i", data, 4)[0]
    p, maps = 8, []
    for _ in range(high + 1):
        n = data[p]
        if n > 15:
            raise ValueError(f"name length {n}")
        name = data[p + 1:p + 1 + n].decode("latin1")
        w, h, size, unk_ptr = struct.unpack_from("<4I", data, p + 16)
        p += 32
        if size != w * h * 10 or p + size > len(data):
            raise ValueError(f"data size {size} for {w}x{h}")
        cells = struct.unpack_from(f"<{w * h}I", data, p)
        tail = data[p + 4 * w * h:p + size]
        p += size
        maps.append({"name": name, "w": w, "h": h, "cells": cells, "unk_ptr": unk_ptr, "unk_tail": tail})
    if p != len(data):
        raise ValueError(f"{len(data) - p} trailing bytes")
    return maps


def validate() -> int:
    files = sorted(DATA.rglob("*.map"))
    stats, bad = Counter(), 0
    for f in files:
        try:
            maps = parse(f.read_bytes())
        except (ValueError, struct.error, IndexError) as e:
            bad += 1
            print(f"FAIL {f.relative_to(DATA)}: {e}")
            continue
        stats[f"{len(maps)} map(s) per file"] += 1
        for m in maps:
            stats[f"name {m['name']!r}"] += 1
            stats["cell values " + ("<= 29" if max(m["cells"]) <= 29 else "> 29")] += 1
            nz = sum(1 for b in m["unk_tail"] if b)
            stats[f"unk_tail nonzero bytes: {nz}"] += 1
    print(f"{len(files) - bad}/{len(files)} parsed, every byte consumed")
    for k, v in sorted(stats.items()):
        print(f"  {v:4}  {k}")
    return 1 if bad else 0


def draw(path: Path) -> None:
    for m in parse(path.read_bytes()):
        print(f"{path.name}: {m['name']} {m['w']}x{m['h']}, values {sorted(Counter(m['cells']).items())}")
        for y in range(m["h"]):
            row = m["cells"][y * m["w"]:(y + 1) * m["w"]]
            print("".join(" " if v == 0 else "#" if v == 1 else chr(ord("a") + (v - 2) % 26) for v in row))


def selftest() -> None:
    w, h = 2, 1
    rec = b"\x03Map" + b"\xcc" * 12 + struct.pack("<4I", w, h, w * h * 10, 0x1234)
    data = b"ML01" + struct.pack("<i", 0) + rec + struct.pack("<2I", 0, 5) + b"\0" * 12
    m = parse(data)[0]
    assert (m["name"], m["w"], m["h"], m["cells"]) == ("Map", 2, 1, (0, 5))
    for bad in (data + b"\0", data[:-1]):
        try:
            parse(bad)
            raise AssertionError("bad length accepted")
        except (ValueError, struct.error):
            pass
    print("selftest ok")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--selftest"]:
        selftest()
    elif args:
        for a in args:
            draw(Path(a))
    else:
        sys.exit(validate())
