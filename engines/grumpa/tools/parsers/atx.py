"""Validate Grumpa's `.atx` actor/object text definitions (E-0005..).

An `.atx` file is a sequence of blocks read by `CFXActorFactory::CreateFromATXFile`
(named in the decrypted game, E-0003). Each block is:

    <type><name>        optional header: a decimal class code and an actor name
    {
        <field>         one field per line: one value, several whitespace-separated
                        values (a colour triple, an x/y/z position), or a file name
                        (which may contain spaces); an optional trailing comment, which
                        starts at the first `/` (no field value contains one)
        ...
    }

A block without a `<type><name>` header (an override of the block before it) is allowed.
The first field of a block is the actor id (e.g. FX_INVENTORY = 30). The type code is the
CFX class (5 = character, 3 = item, 4 = inventory, 37 = global counter, ...); the field
list depends on the class and is the game's business, so this validator checks the file's
*shape*, not the meaning of each field.

Done = every `.atx` in the corpus tokenises with no leftover bytes.

    python engines/grumpa/tools/parsers/atx.py --selftest
    python engines/grumpa/tools/parsers/atx.py [root]        # default: the cab corpus
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = REPO / "games/grumpa/discs/cab"

HEADER = re.compile(r"<(\d+)><([^>]*)>")


class ParseError(Exception):
    pass


def parse(text: str) -> list[dict]:
    """[{type, name, fields:[str]}]; type/name None for a headerless block. Raises on
    anything the grammar does not cover, so a clean parse means the whole file fit."""
    i, n = 0, len(text)
    blocks = []

    def skip_ws():
        nonlocal i
        while i < n and text[i] in " \t\r\n":
            i += 1

    while True:
        skip_ws()
        if i >= n:
            break
        typ = name = None
        m = HEADER.match(text, i)
        if m:
            typ, name = int(m.group(1)), m.group(2)
            i = m.end()
            skip_ws()
        if i >= n or text[i] != "{":
            raise ParseError(f"expected '{{' at offset {i}: {text[i:i + 20]!r}")
        i += 1
        fields = []
        while True:
            skip_ws()
            if i >= n:
                raise ParseError("unterminated block")
            if text[i] == "}":
                i += 1
                break
            eol = text.find("\n", i)
            eol = n if eol < 0 else eol
            line = text[i:eol]
            brace = line.find("}")
            if brace >= 0:  # `}` on the same line as the last field
                line, eol = line[:brace], i + brace
            value = line.split("/", 1)[0].strip()  # drop the `/`- or `//`-comment
            if not value:
                raise ParseError(f"empty field line at offset {i}: {line!r}")
            fields.append(value)
            i = eol
        blocks.append({"type": typ, "name": name, "fields": fields})
    return blocks


def validate(root: Path) -> int:
    files = sorted(root.rglob("*.atx"))
    if not files:
        sys.exit(f"no .atx under {root}")
    bad = 0
    types: dict[int, int] = {}
    for f in files:
        try:
            blocks = parse(f.read_text(encoding="latin1"))
        except ParseError as e:
            bad += 1
            print(f"FAIL {f.relative_to(root)}: {e}")
            continue
        for b in blocks:
            if b["type"] is not None:
                types[b["type"]] = types.get(b["type"], 0) + 1
    ok = len(files) - bad
    print(f"{ok}/{len(files)} .atx parsed; header types "
          + ", ".join(f"{t}:{c}" for t, c in sorted(types.items())))
    return bad


def selftest() -> None:
    sample = ("<5><hbrygd>\n{\n\t200\n\t0\n\tfoo.tga\n}\n"
              "{\n\t90\t\t// id\n\t1\t/ process\n\tbar_0000.tga  // seq\n}\n")
    b = parse(sample)
    assert len(b) == 2
    assert b[0] == {"type": 5, "name": "hbrygd", "fields": ["200", "0", "foo.tga"]}, b[0]
    assert b[1]["type"] is None and b[1]["fields"] == ["90", "1", "bar_0000.tga"], b[1]
    assert parse("<4><x>{\n1\n}") == [{"type": 4, "name": "x", "fields": ["1"]}]
    for bad in ("<4><x>\n1\n2", "<4><x>\n{\n1\n"):  # no brace / unterminated
        try:
            parse(bad)
            raise AssertionError(f"should have failed: {bad!r}")
        except ParseError:
            pass
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=str(CORPUS))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    else:
        sys.exit(1 if validate(Path(a.root)) else 0)
