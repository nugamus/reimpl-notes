"""BFG scene bundles (Data/Scenes_3D/*.BFG) and their packed entries.

Layout (engines/peintre/docs/formats/README.md, bfg.ksy; E-0013):

    u32 count                       used directory entries (<= 100)
    100 x { char name[28]; u32 offset; u32 size; }   offset from DATA_BASE; the engine
                                    reads only `count` slots and names up to their NUL:
                                    later bytes and unused slots hold leftover memory
    pad to DATA_BASE = 0xE18
    entries, back to back

Each entry is packed: byte 0 = method (1 stored, else LZ), bytes 1..3 unused, then the
payload. LZ: a u16 flag word (LSB first) per 16 items; flag 0 = one literal byte,
flag 1 = two bytes b0 b1, copy (b0 & 0x0F) + 1 bytes from distance
((b0 & 0xF0) << 4) + b1 back in the output. The stream ends exactly at the entry's end.

The unpacked entry starts with the 20-byte engine object header: u32 unk_handle,
u32 unk_size, u32 type, u32 unk_prev, u32 unk_next (the engine overwrites all but type
when it loads the entry; in the files they hold leftover memory).

    python engines/peintre/tools/parsers/bfg.py            # validate the corpus
    python engines/peintre/tools/parsers/bfg.py --selftest
    python engines/peintre/tools/parsers/bfg.py --extract OUTDIR FILE.BFG
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/mission-sunlight/discs/cd/Data/Scenes_3D"
DATA_BASE = 0xE18
MAX_ENTRIES = 100
ENTRY = struct.Struct("<28sII")
HEADER = struct.Struct("<5I")  # unk_handle, unk_size, type, unk_prev, unk_next
TYPE_BY_EXT = {".3dc": 1, ".3dm": 3, ".3da": 4, ".3di": 5}


class FormatError(Exception):
    pass


def unpack(entry: bytes) -> bytes:
    """Unpack one BFG entry (method byte, 3 unused bytes, payload)."""
    if len(entry) < 4:
        raise FormatError("entry shorter than its 4-byte header")
    if entry[0] == 1:
        return entry[4:]
    out = bytearray()
    i, end, count, flags = 4, len(entry), 0, 0
    while i != end:
        if count == 0:
            if i + 2 > end:
                raise FormatError("flag word past the end")
            flags = entry[i] | entry[i + 1] << 8
            i += 2
            count = 16
        if i >= end:
            raise FormatError("item past the end")
        if flags & 1 == 0:
            out.append(entry[i])
            i += 1
        else:
            if i + 2 > end:
                raise FormatError("match past the end")
            b0, b1 = entry[i], entry[i + 1]
            i += 2
            dist = ((b0 & 0xF0) << 4) + b1
            length = (b0 & 0x0F) + 1
            if dist == 0 or dist > len(out):
                raise FormatError(f"match distance {dist} outside output ({len(out)})")
            for _ in range(length):
                out.append(out[-dist])
        flags >>= 1
        count -= 1
    return bytes(out)


def pack_stored(data: bytes) -> bytes:
    return b"\x01\0\0\0" + data


def read(path: Path):
    """[(name, packed bytes, unpacked bytes)] of a BFG, validating every byte."""
    blob = path.read_bytes()
    if len(blob) < DATA_BASE:
        raise FormatError("shorter than the directory")
    (count,) = struct.unpack_from("<I", blob)
    if not 0 < count <= MAX_ENTRIES:
        raise FormatError(f"count {count}")
    ents = []
    for i in range(MAX_ENTRIES):
        raw = blob[4 + i * ENTRY.size: 4 + (i + 1) * ENTRY.size]
        if i >= count:  # unused slots: never read by the engine, may hold leftovers
            continue
        name, off, size = ENTRY.unpack(raw)
        n = name.split(b"\0")[0]  # bytes after the NUL are leftover memory (unk)
        ents.append((n.decode("latin1"), off, size))
    tail = blob[4 + MAX_ENTRIES * ENTRY.size: DATA_BASE]
    if any(tail):
        raise FormatError("directory padding not zero")
    pos = 0
    out = []
    for name, off, size in ents:
        if off != pos:
            raise FormatError(f"{name}: offset {off} expected {pos}")
        pos += size
        packed = blob[DATA_BASE + off: DATA_BASE + off + size]
        if len(packed) != size:
            raise FormatError(f"{name}: truncated")
        data = unpack(packed)
        if len(data) < HEADER.size:
            raise FormatError(f"{name}: no object header")
        typ = HEADER.unpack_from(data)[2]
        want = TYPE_BY_EXT.get(Path(name).suffix.lower())
        if want is None or typ != want:
            raise FormatError(f"{name}: type {typ}, extension wants {want}")
        out.append((name, packed, data))
    if DATA_BASE + pos != len(blob):
        raise FormatError(f"{len(blob) - DATA_BASE - pos} bytes after the last entry")
    return out


def validate() -> int:
    files = sorted(CORPUS.glob("*.BFG"))
    ok = 0
    ext = Counter()
    methods = Counter()
    for f in files:
        try:
            for name, packed, _ in read(f):
                ext[Path(name).suffix.upper()] += 1
                methods["stored" if packed[0] == 1 else "lz"] += 1
            ok += 1
        except FormatError as e:
            print(f"FAIL {f.name}: {e}")
    print(f"BFG: {ok}/{len(files)} files valid, every byte consumed; entries {dict(ext)}; "
          f"packing {dict(methods)}")
    return 0 if ok == len(files) else 1


def selftest() -> None:
    # literal a, b, c, then a match copying 3 bytes from distance 3
    stream = bytes([0, 0, 0, 0]) + bytes([0b1000, 0]) + b"abc" + bytes([0x02, 0x03])
    assert unpack(stream) == b"abcabc"
    assert unpack(pack_stored(b"xyz")) == b"xyz"
    # distance high nibble: b0 = 0x1F means distance 0x100 + b1, length 16
    data = bytes(range(256)) + b"\x00"
    lits = b"".join([bytes([0, 0])] + [bytes([b]) for b in data[:16]])
    try:
        unpack(bytes(4) + bytes([1, 0, 0x10, 5]))  # match before any output
    except FormatError:
        pass
    else:
        raise AssertionError("bad distance accepted")
    del lits
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--extract", nargs=2, metavar=("OUTDIR", "BFG"))
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.extract:
        out = Path(a.extract[0])
        out.mkdir(parents=True, exist_ok=True)
        for i, (name, _, data) in enumerate(read(Path(a.extract[1]))):
            (out / f"{i:03d}_{name}").write_bytes(data)
    else:
        sys.exit(validate())
