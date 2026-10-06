"""Resolve the one conflict our engine branches share: the `Engines:` link list in
doc/docportal/settings/game.rst. Each side adds its engine; the answer is the union,
alphabetical as upstream keeps it. Exit 1 if the file has any other conflict.

    python resolve_engine_list.py <repo>/doc/docportal/settings/game.rst
    python resolve_engine_list.py --selftest
"""

from __future__ import annotations

import re
import sys

HUNK = re.compile(r"<<<<<<< [^\n]*\n(.*?)(?:\|\|\|\|\|\|\| [^\n]*\n.*?)?=======\n(.*?)>>>>>>> [^\n]*\n", re.S)


def union(a: str, b: str) -> str:
    names = {n.strip() for n in a.split(":", 1)[1].split("|")} | {n.strip() for n in b.split(":", 1)[1].split("|")}
    return "Engines: " + " | ".join(sorted((n for n in names if n), key=str.lower)) + "\n"


def resolve(text: str) -> str | None:
    def fix(m: re.Match) -> str:
        ours, theirs = m.group(1), m.group(2)
        if ours.count("\n") != 1 or theirs.count("\n") != 1 or not (ours.startswith("Engines:") and theirs.startswith("Engines:")):
            raise ValueError("not the engine list")
        return union(ours, theirs)
    try:
        out = HUNK.sub(fix, text)
    except ValueError:
        return None
    return None if "<<<<<<<" in out else out


def selftest() -> None:
    t = "x\n<<<<<<< HEAD\nEngines: ADL_ | X3D_ | Xeen_\n=======\nEngines: ADL_ | Gilbert_ | Xeen_\n>>>>>>> abc\ny\n"
    assert resolve(t) == "x\nEngines: ADL_ | Gilbert_ | X3D_ | Xeen_\ny\n", resolve(t)
    assert resolve("<<<<<<< HEAD\nfoo\n=======\nbar\n>>>>>>> a\n") is None
    print("resolve_engine_list selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
        sys.exit(0)
    path = sys.argv[1]
    text = open(path, encoding="utf-8").read()
    out = resolve(text)
    if out is None:
        sys.exit(1)
    open(path, "w", encoding="utf-8", newline="\n").write(out)
