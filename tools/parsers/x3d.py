r"""`.X3D` scene script parser and corpus validator.

Mirrors the reader in MissionMonet.exe (E-0036): `load::load_262` (`0x0041f8c0`,
`D:\MissionD\Source\load.cpp`) loops over the buffer:

  * skip ' ', '\t', '\r', '\n'                                   (`FUN_0041f1e0`)
  * ';' skips to the end of the line                              (`FUN_0041f220`)
  * otherwise a keyword, matched case-insensitively in this order (`FUN_0041f140`,
    table `0x00441d94`): scene= object= animation= camera= light= lod=
    Anything else aborts the load (assert load.cpp:0xea).
  * each keyword takes one double-quoted argument. A field is read up to '"', '\r' or
    ',' (`FUN_0041f260`, 255 chars max). `animation=` takes an optional ",<fps>"
    (default 30.0), `lod=` a mandatory ",<distance>".

Paths are relative to the scene's asset directory: `Data/<first 3 chars of the X3D
name>/`, except that U00 loads from `U04/` (E-0034). Scripts outside `Data/Uxx/` are
authoring leftovers and resolve against their own folder; a few of their references are
missing from the corpus, which is reported but not a failure. The validator checks that every
referenced file exists, case-insensitively, since the original runs on a case-insensitive
file system.

    python tools/parsers/x3d.py                 # validate the corpus
    python tools/parsers/x3d.py --selftest
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ParseError, corpus_argparser, default_root, find_files  # noqa: E402

KEYWORDS = ("scene=", "object=", "animation=", "camera=", "light=", "lod=")


def _field(data: bytes, pos: int) -> tuple[str, int]:
    """FUN_0041f260: read up to '"', '\r' or ','; the terminator must exist and not be CR."""
    start = pos
    if pos < len(data) and data[pos] != ord(","):
        while pos < len(data) and data[pos] not in b'"\r':
            pos += 1
            if pos - start > 0xff:
                raise ParseError("field longer than 255 chars", start)
            if pos < len(data) and data[pos] == ord(","):
                break
    if pos >= len(data) or data[pos] == ord("\r"):
        raise ParseError("unterminated field", start)
    return data[start:pos].decode("cp1252"), pos


def _expect(data: bytes, pos: int, ch: str) -> int:
    if pos >= len(data) or data[pos] != ord(ch):
        raise ParseError(f"expected {ch!r}", pos)
    return pos + 1


def parse(data: bytes) -> list[tuple]:
    """Returns the statements in order: (keyword, path[, number])."""
    out = []
    pos = 0
    while True:
        while pos < len(data) and data[pos] in b" \t\r\n":
            pos += 1
        if pos >= len(data):
            return out
        if data[pos] == ord(";"):
            while pos < len(data) and data[pos] != ord("\n"):
                pos += 1
            pos += 1
            continue
        for kw in KEYWORDS:
            if data[pos:pos + len(kw)].lower() == kw.encode():
                break
        else:
            raise ParseError("unknown keyword", pos)
        pos = _expect(data, pos + len(kw), '"')
        path, pos = _field(data, pos)
        number = None
        if kw == "animation=" and data[pos] == ord(","):
            number, pos = _field(data, pos + 1)
            number = float(number)
        elif kw == "lod=":
            pos = _expect(data, pos, ",")
            number, pos = _field(data, pos)
            number = float(number)
        pos = _expect(data, pos, '"')
        if kw == "lod=" and not any(s[0] == "object" for s in out):
            raise ParseError("lod= before any object=", pos)
        out.append((kw[:-1], path) if number is None else (kw[:-1], path, number))


def asset_dir(root: Path, x3d: Path) -> Path:
    """Scene scripts sit in Data/Uxx/. The rest (authoring leftovers in Anim/ folders,
    never loaded by the game) resolve against their own folder."""
    if x3d.parent.parent != root:
        return x3d.parent
    unit = x3d.name[:3].upper()
    return root / ("U04" if unit == "U00" else unit)


def _exists(base: Path, rel: str) -> bool:
    cur = base
    for part in rel.replace("\\", "/").split("/"):
        if not cur.is_dir():
            return False
        match = [p for p in cur.iterdir() if p.name.lower() == part.lower()]
        if not match:
            return False
        cur = match[0]
    return cur.is_file()


def _selftest() -> None:
    src = (b';SCRIPT\r\nOBject="static\\a.o3d"\r\nLod="static\\aLoD.o3d,800"\r\n'
           b';Camera="x.c3d"\r\nANIMATION="anim\\b.a3d,30"\r\nAnimation="c.a3d"\r\n'
           b'Light="Static\\LIGHTS.l3d"')
    assert parse(src) == [
        ("object", "static\\a.o3d"), ("lod", "static\\aLoD.o3d", 800.0),
        ("animation", "anim\\b.a3d", 30.0), ("animation", "c.a3d"),
        ("light", "Static\\LIGHTS.l3d")]
    for bad in (b'Mesh="a"', b'object="a', b'lod="a.o3d"', b'object="a"\r\nlod="b,1"x'):
        try:
            parse(bad)
        except ParseError:
            continue
        raise AssertionError(bad)
    print("selftest ok")


def main(argv: list) -> int:
    if "--selftest" in argv:
        _selftest()
        return 0
    args = corpus_argparser(".X3D validator").parse_args(argv)
    root = args.root or default_root()
    files = find_files(root, "**/*.X3D")
    failed = 0
    leftover_missing = 0
    counts: dict[str, int] = {}
    for f in files:
        try:
            stmts = parse(f.read_bytes())
            base = asset_dir(root, f)
            for s in stmts:
                counts[s[0]] = counts.get(s[0], 0) + 1
                if _exists(base, s[1]):
                    continue
                if f.parent.parent == root:
                    raise ParseError(f"missing file {s[1]}", 0)
                leftover_missing += 1
        except ParseError as exc:
            failed += 1
            print(f"  FAIL {f}: {exc}")
    print(f"files: {len(files)}  passed: {len(files) - failed}  failed: {failed}")
    print(f"missing references in non-scene scripts (not loaded by the game): {leftover_missing}")
    print("statements: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    print("100% of corpus parsed" if files and not failed else "SPEC INCOMPLETE")
    return 1 if failed or not files else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
