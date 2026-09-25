"""Lip-sync `.BIN` (`Sound/*.bin`, `#INDEX#` chunk) parser and corpus validator.

Loader: `FUN_00421960` (MissionMonet.exe) opens `%sSound/%s.bin` (`0x00441f5c`), finds the
`INDEX` chunk, reads a `u32 count` and, if count >= 1, `count * 8` bytes (E-0122):

    u32 count
    record[count]   u32 time_ms, u16 shape, u16 unk_pad

`time_ms` rises through the file (first is 0 in the corpus); `shape` is a mouth-shape slot
1..8 (sound.md). `unk_pad` is 0xCDCD in every record (writer garbage, never read as a
field). The chunk ends at the container table (binchunk.py).

    python tools/parsers/lip.py                 # validate the corpus
    python tools/parsers/lip.py --selftest
    python tools/parsers/lip.py --file <path>   # dump one file
"""

from __future__ import annotations

import struct
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import binchunk  # noqa: E402
from common import ParseError, Reader, corpus_argparser, default_root  # noqa: E402


def parse_index(payload: bytes) -> list[tuple[int, int, int]]:
    r = Reader(payload)
    count = r.u32()
    r.check(len(payload) == 4 + 8 * count, f"{count} records do not fill the chunk", 0)
    recs = [(r.u32(), r.u16(), r.u16()) for _ in range(count)]
    r.expect_eof()
    for i, (t, shape, _) in enumerate(recs):
        r.check(1 <= shape <= 8, f"record {i}: shape {shape} outside 1..8", 4 + 8 * i)
        r.check(i == 0 or t >= recs[i - 1][0], f"record {i}: time goes backwards", 4 + 8 * i)
    return recs


def parse(data: bytes) -> list[tuple[int, int, int]]:
    chunks = binchunk.parse(data)
    if set(chunks) != {"#INDEX#"}:
        raise ParseError(f"expected only #INDEX#, got {sorted(chunks)}", 0)
    return parse_index(chunks["#INDEX#"])


def _selftest() -> None:
    payload = struct.pack("<I", 2) + struct.pack("<IHH", 0, 1, 0xCDCD) + struct.pack("<IHH", 92, 3, 0xCDCD)
    blob = payload + struct.pack("<20sII", b"#INDEX#", 0, len(payload)) + struct.pack("<I", 1)
    assert parse(blob) == [(0, 1, 0xCDCD), (92, 3, 0xCDCD)]
    bad_shape = struct.pack("<I", 1) + struct.pack("<IHH", 0, 9, 0)
    backwards = struct.pack("<I", 2) + struct.pack("<IHH", 5, 1, 0) + struct.pack("<IHH", 4, 1, 0)
    for b in (payload + b"\0", bad_shape, backwards):
        try:
            parse_index(b)
        except ParseError:
            continue
        raise AssertionError("accepted bad input")
    print("selftest ok")


def _wav_ms(bin_path: Path) -> float | None:
    for p in bin_path.parent.iterdir():
        if p.stem.lower() == bin_path.stem.lower() and p.suffix.lower() == ".wav":
            with wave.open(str(p)) as w:
                return w.getnframes() * 1000 / w.getframerate()
    return None


def main(argv: list) -> int:
    if "--selftest" in argv:
        _selftest()
        return 0
    args = corpus_argparser("lip-sync .BIN validator").parse_args(argv)
    if args.file:
        for t, shape, _ in parse(args.file.read_bytes()):
            print(f"{t:7d} ms  shape {shape}")
        return 0
    root = args.root or default_root()
    files = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() == ".bin"
                   and p.parent.name.lower() in ("sound", "nonuse"))
    ok = records = 0
    shapes: dict[int, int] = {}
    no_wav, past_end, pads = [], 0, set()
    for path in files:
        try:
            recs = parse(path.read_bytes())
        except ParseError as exc:
            print(f"  FAIL {path}  {exc}")
            continue
        ok += 1
        records += len(recs)
        for t, shape, pad in recs:
            shapes[shape] = shapes.get(shape, 0) + 1
            pads.add(pad)
        ms = _wav_ms(path)
        if ms is None:
            no_wav.append(path.name)
        elif recs and recs[-1][0] > ms:
            past_end += 1
        if args.verbose:
            print(f"  ok   {path.relative_to(root)}  {len(recs)} records, last {recs[-1][0]} ms, wav {ms and round(ms)} ms")
    print(f"files: {len(files)}  passed: {ok}  records: {records}")
    print(f"shapes: {dict(sorted(shapes.items()))}  pad values: {sorted(hex(p) for p in pads)}")
    print(f"without a .wav of the same name: {no_wav}  last time past the .wav's end: {past_end}")
    print("100% of corpus parsed" if files and ok == len(files) else "SPEC INCOMPLETE")
    return 0 if files and ok == len(files) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
