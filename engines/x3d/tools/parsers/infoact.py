"""`INFOACT.BIN` (`#ACTIONS#` chunk) parser and corpus validator.

Loader: `FUN_0041da90` (MissionMonet.exe) finds `ACTIONS`, reads a `u32 count`, then
`count * 0x440` bytes, and builds one action per record (`FUN_0041e020`). Layout
(E-0071):

    +0x000 u32 id               slot in the action table (run counters, conditions)
    +0x004 char name[30]        action name ("TakeCard", "M01")
    +0x022 char condition[258]  flag expression, "TRUE" = always
    +0x124 i32 max_runs         disabled after this many runs; >= 100 never
    +0x128 u32 trigger          7 = use the held item on the hotspot, 8 = plain click
    +0x12c char item[32]        held item name for trigger 7
    +0x14c u32 hotspot_type     must equal the hotspot's type (INFOOBJ.BIN type)
    +0x150 char hotspot[32]     hotspot name (matched as a substring of the object name)
    +0x170 u32 target_type
    +0x174 char target[32]      object the steps act on
    +0x194 u32 step_count       <= 10
    +0x198 step[10]             u32 op + char arg[64]

The chunk ends at the container table (binchunk.py). Strings are NUL-terminated;
the bytes after the NUL are writer garbage (0xCD), kept but not interpreted.

    python engines/x3d/tools/parsers/infoact.py                 # validate the corpus
    python engines/x3d/tools/parsers/infoact.py --selftest
    python engines/x3d/tools/parsers/infoact.py --file <path>   # dump one file
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import binchunk  # noqa: E402
from common import ParseError, Reader, corpus_argparser, default_root, find_files  # noqa: E402

RECORD = 0x440
MAX_STEPS = 10


def _record(r: Reader) -> dict:
    start = r.pos
    rec = {
        "id": r.u32(),
        "name": r.fixed_str(30),
        "condition": r.fixed_str(258),
        "max_runs": r.i32(),
        "trigger": r.u32(),
        "item": r.fixed_str(32),
        "hotspot_type": r.u32(),
        "hotspot": r.fixed_str(32),
        "target_type": r.u32(),
        "target": r.fixed_str(32),
    }
    count = r.u32()
    r.check(count <= MAX_STEPS, f"step count {count} > {MAX_STEPS}", r.pos - 4)
    steps = [(r.u32(), r.fixed_str(64)) for _ in range(MAX_STEPS)]
    rec["steps"] = steps[:count]
    r.check(r.pos - start == RECORD, "record size", start)
    return rec


def parse_actions(payload: bytes) -> list[dict]:
    r = Reader(payload)
    count = r.u32()
    r.check(len(payload) == 4 + count * RECORD, f"{count} records do not fill the chunk", 0)
    return [_record(r) for _ in range(count)]


def parse(data: bytes) -> list[dict]:
    chunks = binchunk.parse(data)
    if set(chunks) != {"#ACTIONS#"}:
        raise ParseError(f"expected only #ACTIONS#, got {sorted(chunks)}", 0)
    return parse_actions(chunks["#ACTIONS#"])


def _selftest() -> None:
    def s(text: str, n: int) -> bytes:
        return (text.encode() + b"\0").ljust(n, b"\xcd")

    steps = struct.pack("<I", 10) + s("TakeCard", 64) + (struct.pack("<I", 0) + b"\xcd" * 64) * 9
    rec = (struct.pack("<I", 3) + s("TakeCard", 30) + s("TRUE", 258) + struct.pack("<iI", 100, 8)
           + s(" ", 32) + struct.pack("<I", 4) + s("U01_03", 32) + struct.pack("<I", 4)
           + s("U01_03", 32) + struct.pack("<I", 1) + steps)
    assert len(rec) == RECORD, hex(len(rec))
    payload = struct.pack("<I", 1) + rec
    blob = payload + struct.pack("<20sII", b"#ACTIONS#", 0, len(payload)) + struct.pack("<I", 1)
    (a,) = parse(blob)
    assert (a["id"], a["name"], a["condition"], a["trigger"], a["hotspot"]) == (
        3, "TakeCard", "TRUE", 8, "U01_03")
    assert a["steps"] == [(10, "TakeCard")]
    bad = rec[:0x194] + struct.pack("<I", 11) + rec[0x198:]
    for b in (struct.pack("<I", 2) + rec, struct.pack("<I", 1) + bad):
        try:
            parse_actions(b)
        except ParseError:
            continue
        raise AssertionError("accepted bad input")
    print("selftest ok")


def main(argv: list) -> int:
    if "--selftest" in argv:
        _selftest()
        return 0
    args = corpus_argparser("INFOACT.BIN validator").parse_args(argv)
    if args.file:
        for a in parse(args.file.read_bytes()):
            print(f"[{a['id']:3d}] {a['name']:<24} trig={a['trigger']} item={a['item']!r:<12}"
                  f" hs={a['hotspot_type']}:{a['hotspot']:<10} tgt={a['target_type']}:{a['target']:<10}"
                  f" max={a['max_runs']} if {a['condition']!r}")
            for op, arg in a["steps"]:
                print(f"        {op:3d} {arg}")
        return 0
    root = args.root or default_root()
    files = [p for p in find_files(root, "INFOACT.BIN") if p.name.upper() == "INFOACT.BIN"]
    ok, records = 0, 0
    for path in files:
        try:
            records += len(parse(path.read_bytes()))
            ok += 1
        except ParseError as exc:
            print(f"  FAIL {path}  {exc}")
    print(f"files: {len(files)}  passed: {ok}  records: {records}")
    print("100% of corpus parsed" if files and ok == len(files) else "SPEC INCOMPLETE")
    return 0 if files and ok == len(files) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
