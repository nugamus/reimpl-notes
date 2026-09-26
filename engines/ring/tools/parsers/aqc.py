"""`.aqc` panorama node validator. Spec: engines/ring/docs/formats/aqc.ksy, E-0020.

Read by `aSecComAqi::DecompressNode` (RING_DVD.EXE 0x429be0) and
`aSecComAqi::DecompressChannel` (0x429dc0); names built by `aApplication::AddRot`
(0x404dc0, "%s%s\\%s\\%s\\%s.aqc"). Bit streams: README "Packed bit stream", index width
6; the "13-bit" decoder is 0x430600, the 16-bit one 0x430770.

    node:
      u32   index_size
      header (13 x u32, below)
      index stream     index_size bytes, 13-bit literals: one index per 4 pixels
      u32   table_size
      table stream     table_size bytes, 16-bit literals: the colour table
    sections until EOF:
      u32   count
      u32   unk_a, unk_b
      count x { u32 size, header, index stream of size bytes }

    header: width, height, bytes_per_pixel (2), unk_3, f32 unk_4 (360.0), f32 unk_5,
            f32 unk_6 (-60/60 or -75/75), x0, x1, y0, y1, data_size = (x1-x0)*(y1-y0)*2,
            stride = (x1-x0)*2

One Prophet file has 18,289 bytes after its tenth section that do not form a section
(TRAILING, Q-0003): the engine reads as many sections as the rotation has layers (set by
the game code, `this+0x48` in 0x4111d0), so bytes past them are never read.

The node's index stream covers the whole width x height (x0 = y0 = 0); a section entry
covers its rectangle. Every index is below the table's entry count (table values / 4).

    python engines/ring/tools/parsers/aqc.py            # corpus
    python engines/ring/tools/parsers/aqc.py --selftest
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bitstream import decode  # noqa: E402
from common import ParseError, Reader, main_for  # noqa: E402

# Files with bytes after their last well-formed section, kept as unk_trailing (Q-0003).
TRAILING = {"9a1d45d0a1d8c2157d2e5ddb1594e981": "A03S02N05R01.aqc (Prophet cd2): 18,289 bytes after 10 sections"}

HEADER = ("width", "height", "bytes_per_pixel", "unk_3", "unk_4", "unk_5", "unk_6",
          "x0", "x1", "y0", "y1", "data_size", "stride")


def header(r: Reader) -> dict:
    at = r.pos
    h = dict(zip(HEADER, struct.unpack("<3Ii3f6I", r.bytes(52))))
    w, hh = h["x1"] - h["x0"], h["y1"] - h["y0"]
    r.check(h["bytes_per_pixel"] == 2 and 0 < w and 0 < hh and h["x1"] <= h["width"]
            and h["y1"] <= h["height"] and h["data_size"] == w * hh * 2
            and h["stride"] == w * 2, f"inconsistent header {h}", at)
    return h


def stream(r: Reader, data: bytes, size: int, vbits: int, want: int, what: str) -> list[int]:
    start = r.pos
    r.skip(size)
    codes, end = decode(data, vbits, 6, start * 8, (start + size) * 8, want + 2)
    if not want <= len(codes) <= want + 1 or end < (start + size) * 8:
        raise ParseError(f"{what}: {len(codes)} codes for {want}", start)
    return codes[:want]


def parse(data: bytes) -> dict:
    import hashlib

    r = Reader(data)
    trailing_ok = hashlib.md5(data).hexdigest() in TRAILING
    index_size = r.u32()
    node = header(r)
    r.check(node["x0"] == node["y0"] == 0 and node["x1"] == node["width"]
            and node["y1"] == node["height"], "node does not cover the panorama")
    idx = stream(r, data, index_size, 13, node["data_size"] // 8, "node index")
    table_size = r.u32()
    t_start = r.pos
    r.skip(table_size)
    table, end = decode(data, 16, 6, t_start * 8, (t_start + table_size) * 8, 1 << 20)
    entries = len(table) // 4
    r.check(max(idx) < entries, f"node index {max(idx)} >= {entries} table entries", t_start)
    sections = []
    while not r.eof():
        if trailing_ok:
            try:
                probe = Reader(data, r.pos)
                probe.u32(), probe.u32(), probe.u32()
                probe.u32()
                header(probe)
            except ParseError:
                return {"node": node, "table_values": len(table), "sections": sections,
                        "unk_trailing": r.remaining}
        count, unk_a, unk_b = r.u32(), r.u32(), r.u32()
        rects = []
        for _ in range(count):
            size = r.u32()
            h = header(r)
            codes = stream(r, data, size, 13, h["data_size"] // 8, "section index")
            r.check(not codes or max(codes) < entries, "section index beyond the table")
            rects.append((h["x0"], h["y0"], h["x1"], h["y1"]))
        sections.append({"count": count, "unk_a": unk_a, "unk_b": unk_b, "rects": rects})
    return {"node": node, "table_values": len(table), "sections": sections}


def selftest() -> None:
    def bits(values, width):
        s = "".join("0" + format(v, f"0{width}b") for v in values)
        n = (len(s) + 7) // 8
        return int(s.ljust(n * 8, "0"), 2).to_bytes(n, "big")

    def hdr(w, h, x0, x1, y0, y1):
        return struct.pack("<3Ii3f6I", w, h, 2, 0, 360.0, -60.0, 60.0, x0, x1, y0, y1,
                           (x1 - x0) * (y1 - y0) * 2, (x1 - x0) * 2)

    idx, table = bits([1, 0], 13), bits(range(8), 16)   # 4x2 pixels, 2 table entries
    sec = bits([1], 13)
    blob = struct.pack("<I", len(idx)) + hdr(4, 2, 0, 4, 0, 2) + idx
    blob += struct.pack("<I", len(table)) + table
    blob += struct.pack("<3I", 1, 0, 0) + struct.pack("<I", len(sec)) + hdr(4, 2, 0, 2, 0, 2) + sec
    out = parse(blob)
    assert out["table_values"] == 8 and out["sections"][0]["rects"] == [(0, 0, 2, 2)]
    try:
        parse(blob + b"\0")
    except ParseError:
        pass
    else:
        raise AssertionError("trailing byte accepted")


if __name__ == "__main__":
    raise SystemExit(main_for(parse, "AQC panorama validator", [".aqc"], selftest=selftest))
