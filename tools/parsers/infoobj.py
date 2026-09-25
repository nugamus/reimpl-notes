"""`.INFOOBJ.BIN` parser and corpus validator.

Per-unit object-info container. Read by two loaders in `MissionMonet.exe`:

  * `FUN_0041d490` (`0x0041d490`) — opens INFOOBJ.BIN, dispatches to the OBJECTS sub-loader
  * `FUN_0041d6f0` (`0x0041d6f0`) — the OBJECTS sub-loader itself

The second loader is the one that pins the on-disk format. It does:

    FUN_00415190(this, "OBJECTS")   seek to OBJECTS tag
    FUN_004153a0(this, &count, 4)   u32 count
    FUN_004153a0(this, buf, count*0x44)   raw bytes, count entries of 68 bytes
    FUN_00415180(this)              close the section

`count` is `0` at the trailing `#OBJECTS#` terminator tag, so the loader returns early
without consuming anything. The real entries sit before that terminator, in a fixed
prefix with no leading section tag of its own. Every file in the corpus is laid out as:

    [u32 count][count * 68-byte entries][32-byte terminator]

The terminator is:

    [10 b "#OBJECTS#\0"][10 b 0xCD padding][u32=0][u32=offset_of_OBJECTS][u32=1]

The 32-byte 0xCD region inside each entry is real on-disk bytes, but every byte is
`0xCD` across all 9 files in the corpus — MSVC's uninitialised-heap pattern. The loader
overwrites entry-offset `+0x2C` (byte 44) at runtime with a pointer, so this slot is a
runtime field that the writer leaves untouched on disk. Documented as opaque per
CLAUDE.md rule 5; see OPEN-QUESTIONS.

Per CLAUDE.md rule 2 the validator must consume every byte of every INFOOBJ.BIN file
with no out-of-range indices. `parse` insists on `expect_eof()` at the end.

    python tools/parsers/infoobj.py                 # validate the corpus
    python tools/parsers/infoobj.py --selftest
    python tools/parsers/infoobj.py --file <path>   # one file, structural summary
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    ParseError,
    Reader,
    corpus_argparser,
    default_root,
    find_files,
)

NAME_LEN = 8                # fixed-width NUL-terminated object name (e.g. "*U04_03")
ENTRY_RESERVED_LEN = 32     # 32 bytes of 0xCD (MSVC uninit heap) — see notes
ENTRY_LEN = 68              # NAME_LEN + ENTRY_RESERVED_LEN + 28 = 8 + 32 + 28 = 68
FOOTER_TAG = b"#OBJECTS#\x00"
FOOTER_LEN = 32             # 10 (tag) + 10 (0xCD pad) + 4 + 4 + 4


def _parse_entry(r: Reader) -> dict:
    start = r.pos
    name = r.fixed_str(NAME_LEN)
    # 32 bytes of 0xCD across the whole corpus. Stash as raw bytes so the validator
    # proves they are present (and surfaces any future non-0xCD entry).
    reserved = r.bytes(ENTRY_RESERVED_LEN)
    field_a = r.u32()
    field_b = r.u32()
    field_c = r.u32()
    field_d = r.f32()
    field_e = r.u32()
    field_f = r.u32()
    field_g = r.u32()
    return {
        "name": name,
        "reserved": reserved,
        "field_a": field_a,
        "field_b": field_b,
        "field_c": field_c,
        "field_d": field_d,
        "field_e": field_e,
        "field_f": field_f,
        "field_g": field_g,
        "_offset": start,
    }


def _parse_footer(r: Reader) -> dict:
    tag = r.bytes(len(FOOTER_TAG))
    if tag != FOOTER_TAG:
        raise ParseError(f"expected terminator {FOOTER_TAG!r}, got {tag!r}", r.pos - len(FOOTER_TAG))
    pad = r.bytes(10)
    count = r.u32()
    obj_offset = r.u32()
    flag = r.u32()
    return {"terminator_count": count, "obj_offset": obj_offset, "flag": flag, "pad": pad}


def parse(data: bytes) -> dict:
    r = Reader(data)
    count = r.u32()
    entries = [_parse_entry(r) for _ in range(count)]
    footer = _parse_footer(r)
    r.expect_eof()
    return {"count": count, "entries": entries, "footer": footer}


def _selftest() -> None:
    # Build a synthetic file with 2 entries + correct footer.
    def make_entry(name: str, a: int, b: int, c: int, d: float, e: int, f: int, g: int) -> bytes:
        raw_name = name.encode("cp1252").ljust(NAME_LEN, b"\0")[:NAME_LEN]
        reserved = b"\xcd" * ENTRY_RESERVED_LEN
        # 7 fields × 4 bytes = 28 bytes
        tail = struct.pack(
            "<IIIfIII", a, b, c, d, e, f, g,
        )
        assert len(tail) == 28, len(tail)
        return raw_name + reserved + tail

    e1 = make_entry("*U01_01", 6, 3, 1, 1.0, 0, 15, 1)
    e2 = make_entry("*Ernest", 5, 0, 0, 1.0, 0, 15, 1)
    body = e1 + e2
    count = 2
    obj_offset = 4 + len(body)
    footer = FOOTER_TAG + b"\xcd" * 10 + struct.pack("<III", 0, obj_offset, 1)
    blob = struct.pack("<I", count) + body + footer

    doc = parse(blob)
    assert doc["count"] == 2
    assert doc["entries"][0]["name"] == "*U01_01"
    assert doc["entries"][0]["reserved"] == b"\xcd" * 32
    assert doc["entries"][0]["field_a"] == 6 and doc["entries"][0]["field_f"] == 15
    assert doc["entries"][1]["name"] == "*Ernest"
    assert doc["footer"]["terminator_count"] == 0
    assert doc["footer"]["obj_offset"] == obj_offset
    assert doc["footer"]["flag"] == 1

    # Trailing byte must fail
    try:
        parse(blob + b"\0")
    except ParseError as exc:
        assert "unconsumed" in exc.message
    else:
        raise AssertionError("trailing byte accepted")

    # Truncation must fail
    try:
        parse(blob[:-1])
    except ParseError:
        pass
    else:
        raise AssertionError("truncated file accepted")

    # Missing terminator must fail
    blob_no_term = struct.pack("<I", count) + body + b"\x00" * 32
    try:
        parse(blob_no_term)
    except ParseError as exc:
        assert "terminator" in exc.message
    else:
        raise AssertionError("missing terminator accepted")

    # count = 0 with just the footer is valid
    blob_empty = struct.pack("<I", 0) + FOOTER_TAG + b"\xcd" * 10 + struct.pack("<III", 0, 4, 1)
    doc_empty = parse(blob_empty)
    assert doc_empty["count"] == 0 and doc_empty["entries"] == []

    print("selftest ok")


def _dump(path: Path) -> None:
    doc = parse(path.read_bytes())
    print(
        f"{path.name}: {doc['count']} object(s), {path.stat().st_size} bytes,"
        f" terminator_count={doc['footer']['terminator_count']},"
        f" obj_offset={doc['footer']['obj_offset']},"
        f" flag={doc['footer']['flag']}"
    )
    for i, ent in enumerate(doc["entries"]):
        print(
            f"  [{i:2d}] {ent['name']:>10s}  a={ent['field_a']:2d} b={ent['field_b']:2d}"
            f" c={ent['field_c']:2d} d={ent['field_d']:5.1f}"
            f" e={ent['field_e']:2d} f={ent['field_f']:3d} g={ent['field_g']:2d}"
        )


def main(argv: list) -> int:
    if "--selftest" in argv:
        _selftest()
        return 0

    args = corpus_argparser("INFOOBJ.BIN validator").parse_args(argv)

    if args.file:
        _dump(args.file)
        return 0

    root = args.root or default_root()
    # find_files matches on suffix case-insensitively, so glob on the basename here
    # (the corpus uses INFOOBJ.BIN and Infoobj.bin mixed).
    files = [p for p in find_files(root, "INFOOBJ.BIN") if p.name.upper() == "INFOOBJ.BIN"]
    if not files:
        print(f"no INFOOBJ.BIN under {root}", file=sys.stderr)
        return 2

    ok = 0
    failures: list[tuple[Path, str]] = []
    totals = {"objects": 0, "bytes": 0}

    for path in files:
        data = path.read_bytes()
        try:
            doc = parse(data)
        except ParseError as exc:
            failures.append((path, f"{exc.message} at 0x{exc.offset:08x}"))
            continue
        ok += 1
        totals["objects"] += doc["count"]
        totals["bytes"] += len(data)

    print(f"corpus: {root}")
    print(f"files: {len(files)}  passed: {ok}  failed: {len(failures)}")
    print(f"  objects: {totals['objects']}")
    print(f"  bytes:   {totals['bytes']}")
    for path, err in failures[:25]:
        print(f"  FAIL {path}  {err}")
    if len(failures) > 25:
        print(f"  ... and {len(failures) - 25} more failures")

    print("100% of corpus parsed" if ok == len(files) else "SPEC INCOMPLETE")
    return 0 if ok == len(files) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
