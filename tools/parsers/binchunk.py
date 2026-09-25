"""`.BIN` chunk container: parser and corpus validator.

Every `.BIN` in the corpus (App.bin, SCENE.BIN, INFOOBJ.BIN, INFOACT.BIN, Sound/*.bin,
...) is one container shape, read from the end:

    body            chunk payloads, back to back, starting at offset 0
    table[count]    28 bytes each: char name[20] ("#SCENE#", NUL-padded), u32 offset, u32 size
    u32 count       last 4 bytes of the file

Loader side: `FUN_00415420` (MissionMonet.exe) seeks `-4` from EOF for the count, then
`-(count*0x1c + 4)` for the table; `FUN_00415190` finds a chunk by name.

This validator proves the container layer only: the table is in range, names are `#..#`,
and the chunks tile the body exactly (no gaps, no overlap, nothing trailing). Chunk
payloads are opaque here; per-chunk parsers (infoobj.py for #OBJECTS#, ...) own those.

    python tools/parsers/binchunk.py            # validate the corpus
    python tools/parsers/binchunk.py --file <path>
"""

from __future__ import annotations

import struct
import sys

from common import ParseError, Reader, main_for

ENTRY = 28


def parse(data: bytes) -> dict[str, bytes]:
    r = Reader(data)
    r.check(len(data) >= 4, "file shorter than the count field", 0)
    r.seek(len(data) - 4)
    count = r.u32()
    table = len(data) - 4 - count * ENTRY
    r.check(0 < count and table >= 0, f"chunk count {count} does not fit the file", len(data) - 4)

    r.seek(table)
    entries = []
    for _ in range(count):
        at = r.pos
        name = r.fixed_str(20)
        offset, size = r.u32(), r.u32()
        r.check(len(name) > 2 and name[0] == name[-1] == "#", f"bad chunk name {name!r}", at)
        entries.append((offset, size, name, at))

    chunks, pos = {}, 0
    for offset, size, name, at in sorted(entries):
        r.check(offset == pos, f"chunk {name} at 0x{offset:x}, expected 0x{pos:x}", at)
        r.check(name not in chunks, f"duplicate chunk {name}", at)
        chunks[name] = data[offset : offset + size]
        pos = offset + size
    r.check(pos == table, f"chunks end at 0x{pos:x}, table starts at 0x{table:x}", pos)
    return chunks


def _selftest() -> None:
    def build(chunks: list[tuple[bytes, bytes]]) -> bytes:
        body, table, pos = b"", b"", 0
        for name, payload in chunks:
            table += struct.pack("<20sII", name, pos, len(payload))
            body += payload
            pos += len(payload)
        return body + table + struct.pack("<I", len(chunks))

    good = build([(b"#SCENE#", b"abcd"), (b"#CAMERA#", b"xy")])
    assert parse(good) == {"#SCENE#": b"abcd", "#CAMERA#": b"xy"}
    for bad in (good[:-1], b"\0" + good, build([(b"SCENE", b"a")]), struct.pack("<I", 0)):
        try:
            parse(bad)
        except ParseError:
            continue
        raise AssertionError(f"accepted bad input {bad!r}")
    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
        sys.exit(0)
    sys.exit(main_for(parse, "**/*.BIN", ".BIN chunk container validator"))
