"""One-line summaries of the original's functions, so none is ever decompiled twice.

Whoever understands a function (usually the re-analyst subagent) records it here; the line
then shows up in `tools/coverage.py`'s TRIAGE.tsv (kind `summarized`), in `ref.py` searches,
and in Ghidra as the function's plate comment and name (`apply_summaries.py`). Summaries are
our own words about behaviour (never decompiler output, rule 3), so the file is committed:
`engines/<engine>/notes/summaries.tsv` (program, address, name, summary, evidence).

    python tools/summary.py add grumpa GRUMPA_NOCD.EXE 0x4387d0 "Adds an item to the inventory: counters, no duplicates, first free slot" --name Inventory::add --evidence E-0501
    python tools/summary.py get grumpa 0x4387d0
    python tools/summary.py list grumpa [words]
    python tools/summary.py --selftest
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HEADER = "program\taddress\tname\tsummary\tevidence\n"


def path_of(engine: str) -> Path:
    return REPO / "engines" / engine / "notes" / "summaries.tsv"


def norm(addr: str) -> str:
    return f"{int(addr, 16):08x}"


def load(engine: str) -> dict[str, list[str]]:
    p = path_of(engine)
    rows = {}
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines()[1:]:
            f = line.split("\t")
            if len(f) >= 4:
                rows[f[1]] = (f + [""])[:5]
    return rows


def save(engine: str, rows: dict[str, list[str]]) -> None:
    p = path_of(engine)
    p.parent.mkdir(parents=True, exist_ok=True)
    body = "".join("\t".join(r) + "\n" for _, r in sorted(rows.items()))
    p.write_text(HEADER + body, encoding="utf-8", newline="\n")


def add(engine: str, program: str, addr: str, text: str, name: str = "", evidence: str = "") -> None:
    rows = load(engine)
    a = norm(addr)
    old = rows.get(a)
    clean = lambda s: s.replace("\t", " ").replace("\n", " ").strip()
    rows[a] = [program, a, clean(name or (old[2] if old else "")), clean(text), clean(evidence or (old[4] if old else ""))]
    save(engine, rows)
    print(f"{'updated' if old else 'added'} {engine} {program}!0x{a}: {rows[a][2] or '(no name)'}: {rows[a][3]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("add")
    a.add_argument("engine"); a.add_argument("program"); a.add_argument("address"); a.add_argument("summary")
    a.add_argument("--name", default=""); a.add_argument("--evidence", default="")
    g = sub.add_parser("get"); g.add_argument("engine"); g.add_argument("address")
    l = sub.add_parser("list"); l.add_argument("engine"); l.add_argument("words", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return 0
    if args.cmd == "add":
        add(args.engine, args.program, args.address, args.summary, args.name, args.evidence)
    elif args.cmd == "get":
        r = load(args.engine).get(norm(args.address))
        print("\t".join(r) if r else "no summary")
    elif args.cmd == "list":
        for r in load(args.engine).values():
            if all(w.lower() in "\t".join(r).lower() for w in args.words):
                print(f"{r[0]}!0x{r[1]} {r[2]}: {r[3]} {r[4]}")
    else:
        print(__doc__)
        return 2
    return 0


def selftest() -> None:
    global path_of
    import tempfile

    tmp = Path(tempfile.mkdtemp())
    real = path_of
    path_of = lambda e: tmp / f"{e}.tsv"
    try:
        add("t", "A.EXE", "0x401000", "Loads a scene", "Scene::load")
        add("t", "A.EXE", "401000", "Loads a scene and its views", evidence="E-0100")
        r = load("t")["00401000"]
        assert r == ["A.EXE", "00401000", "Scene::load", "Loads a scene and its views", "E-0100"], r
    finally:
        path_of = real
    print("summary selftest ok")


if __name__ == "__main__":
    sys.exit(main())
