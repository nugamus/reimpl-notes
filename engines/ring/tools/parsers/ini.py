"""The game's text configuration files. Spec: engines/ring/docs/formats/README.md
"Configuration files", E-0026. Readers in RING_DVD.EXE (the other EXEs have the same):

    fl.ini     aApplication::Init 0x407b80: fscanf "%d" = n, then n x fscanf "%s %s"
               (key, value); keys it compares: KEYS
    aPre.ini   aPreFer::Load 0x428870: fscanf "%d %d %d %d" must match 4
    cd.ini     0x402280 (data\\cd.ini): fscanf "%d"
    aObj.ini   0x4213d0 (strings aApplication::AddObjectsFromFile): fscanf "%d\\n" = object
               id, then a fixed number of lines (10 in the DVD EXE) read up to '\\n'; the line
               starting with the language code gives the texts between its '#'s
    aMes.ini   aApplication::GetMultiLanMes 0x40e150 (path "%sames.ini"): fscanf "%s\\n"
               until the key, then lines up to '\\n'; the line starting with the language code
               gives "#title#text"
    *.aba      aFileList::Load 0x47a1d0 ("%sdata/Save/%s" with backslashes): u32 record count, then
               records (read by 0x479f10, not specced yet); the corpus has only count 0
Lines longer than 0xfd characters are cut by the readers; none in the corpus.

    python engines/ring/tools/parsers/ini.py            # corpus
    python engines/ring/tools/parsers/ini.py --selftest
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ParseError, main_for  # noqa: E402

KEYS = {"CDPATH:", "LANGUAGE:", "CHECKCD:", "SOUNDCHUNCK_BGRMUS:", "LOADFROM_BGRMUS:",
        "SOUNDCHUNCK_AMBMUS:", "LOADFROM_AMBMUS:", "SOUNDCHUNCK_AMBEFE:", "LOADFROM_AMBEFE:",
        "SOUNDCHUNCK_EFE:", "LOADFROM_EFE:", "SOUNDCHUNCK_DIA:", "LOADFROM_DIA:", "ART_BAG:",
        "ART_CURSOR:", "ART_SY:", "ART_AS:", "ART_NI:", "ART_N2:", "ART_RO:", "ART_RH:",
        "ART_WA:", "ART_FO:", "CHECKLOADSAVE:"}
# The readers compare the first 3 characters with the language code; "TA" (a typo for ITA
# in the CD/ISO aMes.ini) is a line no language matches.
LANG_LINE = re.compile(rb"^(\S{1,3})[ \t]+(#.*)$")


def ints(data: bytes, n: int) -> list[int]:
    tok = data.split()
    if len(tok) != n or not all(re.fullmatch(rb"-?\d+", t) for t in tok):
        raise ParseError(f"expected exactly {n} integers, got {tok[:8]}", 0)
    return [int(t) for t in tok]


def parse_fl(data: bytes) -> dict:
    tok = data.split()
    if not tok or not tok[0].isdigit():
        raise ParseError("no count", 0)
    n = int(tok[0])
    if len(tok) != 1 + 2 * n:
        raise ParseError(f"count {n} but {len(tok) - 1} tokens", 0)
    pairs = dict((tok[1 + 2 * i].decode(), tok[2 + 2 * i].decode()) for i in range(n))
    unknown = set(pairs) - KEYS
    if unknown:
        raise ParseError(f"keys not read by the EXE: {sorted(unknown)}", 0)
    return pairs


def lines_of(data: bytes) -> list[bytes]:
    out = data.split(b"\n")
    if out and out[-1] == b"":
        out.pop()
    for ln in out:
        if len(ln) > 0xfd:
            raise ParseError(f"line of {len(ln)} bytes", data.find(ln))
    return [ln.rstrip(b"\r") for ln in out]


def parse_multilang(data: bytes, key: bytes) -> dict:
    """aObj.ini (key = integer id) and aMes.ini (key = one token): key line, then a fixed
    number of language lines "LAN<ws>#...". Returns the per-file language count."""
    lines = lines_of(data)
    blocks, i = [], 0
    while i < len(lines):
        k = lines[i].strip()
        if not re.fullmatch(key, k):
            raise ParseError(f"line {i + 1}: expected a key, got {lines[i][:40]!r}", 0)
        j = i + 1
        langs = []
        while j < len(lines) and LANG_LINE.match(lines[j]):
            langs.append(LANG_LINE.match(lines[j]).group(1).decode())
            j += 1
        if not langs:
            raise ParseError(f"line {i + 1}: key without language lines", 0)
        blocks.append((k.decode("cp1252"), langs))
        i = j
    counts = {len(b[1]) for b in blocks}
    return {"keys": len(blocks), "langs_per_key": sorted(counts),
            "languages": blocks[0][1] if blocks else []}


def parse(data: bytes, name: str = "") -> dict:
    n = name.lower()
    if n.endswith(".aba"):
        from common import Reader

        r = Reader(data)
        count = r.u32()
        r.check(count == 0, "save list with records: record layout not specced yet", 0)
        r.expect_eof()
        return {"records": 0}
    if n.endswith("fl.ini"):
        return parse_fl(data)
    if n.endswith("apre.ini"):
        return {"values": ints(data, 4)}
    if n.endswith("cd.ini"):
        return {"disc": ints(data, 1)[0]}
    if n.endswith("aobj.ini"):
        return parse_multilang(data, rb"\d+")
    if n.endswith("ames.ini"):
        return parse_multilang(data, rb"\S+")
    raise ParseError(f"not a configuration file the EXE reads: {name}", 0)


def selftest() -> None:
    assert parse(b"2\r\nCDPATH: CDROM\r\nART_SY: 1\r\n", "fl.ini")["ART_SY:"] == "1"
    assert parse(b"100 100 -1 1", "aPre.ini")["values"] == [100, 100, -1, 1]
    out = parse(b"10000\nENG     #Brutality#\nGER\t#Brutalit\xe4t#\n", "aObj.ini")
    assert out["keys"] == 1 and out["languages"] == ["ENG", "GER"]
    for bad, name in ((b"3\r\nCDPATH: X\r\n", "fl.ini"), (b"1 2 3", "aPre.ini")):
        try:
            parse(bad, name)
        except ParseError:
            continue
        raise AssertionError(f"accepted {bad!r}")


if __name__ == "__main__":
    import common

    # The harness passes bytes only; the reader depends on the file name, so wrap it.
    names = {}
    orig = common.corpus

    def corpus(loose, members=(), archives=common.ARCHIVE_EXTS):
        for label, data in orig(loose, members, archives):
            names[id(data)] = label
            yield label, data

    common.corpus = corpus
    raise SystemExit(main_for(lambda d: parse(d, names.get(id(d), "")),
                              "configuration file validator", [".ini", ".aba"],
                              selftest=selftest))
