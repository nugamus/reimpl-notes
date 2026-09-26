"""`.at2` / `.at3` archive validator. Spec: engines/ring/docs/formats/at2.ksy, E-0016.

Read by `aArt::Init` (DVD 0x4194d0, Prophet 0x41e470) and `aArt::GetRec` (0x4198e0 /
0x41e880):

    char[8] magic            "AT_II\\0\\0\\0" (.at2, Ring) or "ATIII\\0\\0\\0" (.at3, Prophet)
    u32     dir_size         count * 255
    u32     count
    u32     record_size      255
    u32[3]  unk_zero         0 in every file
    count x { char[243] name, u32 offset, u32 size, u32 unpacked_size }
    member data              each member at its offset, size bytes; members are contiguous,
                             in directory order, from the end of the directory to EOF

The engine reads 0x20 header bytes, then 0xff bytes per record; `GetRec` seeks to offset
and reads size bytes. unpacked_size is the member's size after decompression (e.g. 921,654
for a 640x480x24 BMP), which the member's own format undoes (not the archive).

    python engines/ring/tools/parsers/at2.py            # every archive in every edition
    python engines/ring/tools/parsers/at2.py --selftest
    python engines/ring/tools/parsers/at2.py --file <path>
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ParseError, Reader, main_for  # noqa: E402

MAGICS = (b"AT_II\0\0\0", b"ATIII\0\0\0")
RECORD = 255


def parse(data: bytes) -> dict:
    r = Reader(data)
    magic = r.bytes(8)
    r.check(magic in MAGICS, f"bad magic {magic!r}", 0)
    dir_size, count, record_size = r.u32(), r.u32(), r.u32()
    r.check(record_size == RECORD, f"record size {record_size}", 16)
    r.check(dir_size == count * RECORD, f"dir size {dir_size} != {count} * 255", 8)
    r.check(r.array("I", 3) == (0, 0, 0), "unk_zero not zero", 20)
    members, names = [], set()
    for _ in range(count):
        name = r.bytes(243)
        text = name.split(b"\0", 1)[0].decode("cp1252")
        off, size, unpacked = r.u32(), r.u32(), r.u32()
        r.check(text and text.lower() not in names, f"empty or duplicate name {text!r}")
        names.add(text.lower())
        members.append((text, off, size, unpacked))
    # Member data: contiguous, in directory order, up to EOF.
    for text, off, size, _ in members:
        r.check(off == r.pos, f"{text}: offset {off} != expected {r.pos}")
        r.skip(size)
    r.expect_eof()
    return {"magic": magic[:5].decode(), "count": count, "members": members}


def selftest() -> None:
    body = b"abc" + b"de"
    recs = [(b"\\a.bmp", 32 + 2 * RECORD, 3, 10), (b"\\b.tga", 32 + 2 * RECORD + 3, 2, 2)]
    blob = b"AT_II\0\0\0" + struct.pack("<3I3I", 2 * RECORD, 2, RECORD, 0, 0, 0)
    for name, off, size, unp in recs:
        blob += name.ljust(243, b"\0") + struct.pack("<3I", off, size, unp)
    out = parse(blob + body)
    assert out["count"] == 2 and out["members"][1] == ("\\b.tga", 32 + 2 * RECORD + 3, 2, 2)
    for bad in (blob + body + b"x", blob + body[:-1], blob.replace(b"AT_II", b"AT_IX") + body):
        try:
            parse(bad)
        except ParseError:
            continue
        raise AssertionError("bad archive accepted")


if __name__ == "__main__":
    raise SystemExit(main_for(parse, "AT2/AT3 archive validator", [".at2", ".at3"],
                              selftest=selftest))
