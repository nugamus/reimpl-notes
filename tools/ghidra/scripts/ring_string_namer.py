"""Name Ring-engine functions from the method names in their error strings.

The Ring EXEs have no RTTI and no source paths (engines/ring E-0002), but their error
messages name the method that raises them:

    "aApplication::AddRot -> Node File does not exist -> "
    "PuzSetMovToRot -> Wrong Puzzle ID ->"
    "ObjSetAccOnOrOff(INT id, CHAR v) -> pa == NULL"

A function that references strings naming exactly one method is that method (or has it
inlined whole). The class comes from an `aClass::` prefix on any of its strings; a
function whose strings name no class keeps the bare method name.

Scan one program (renames FUN_* functions, comments every one, writes a CSV):

    python -m pyghidra.ghidra_launch --install-dir 'C:\\ghidra' \\
        ghidra.app.util.headless.AnalyzeHeadless ghidra_projects Ring \\
        -process RING_DVD.EXE -noanalysis \\
        -scriptPath tools/ghidra/scripts -postScript ring_string_namer.py engines/ring/notes/names

Self-check (plain CPython): python tools/ghidra/scripts/ring_string_namer.py --selftest
"""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

# "aClass::Method" anywhere at the start, optionally "(args)" after the method.
CLASS_RE = re.compile(r"^\s*(a[A-Z][A-Za-z0-9_]*)::~?([A-Za-z_][A-Za-z0-9_]*)")
# "Method -> ..." or "Method(args) -> ..." without a class.
BARE_RE = re.compile(r"^\s*([A-Z][A-Za-z0-9_]*)\s*(?:\([^)]*\))?\s*(?:I\s*)?->")


def parse(text: str) -> "tuple[str | None, str] | None":
    """(class or None, method) named by an error string, else None."""
    m = CLASS_RE.match(text)
    if m:
        return m.group(1), m.group(2)
    m = BARE_RE.match(text)
    if m:
        return None, m.group(1)
    return None


def strings_in(program):
    """(address, text) for every NUL-terminated printable run of 5+ bytes in initialised
    non-code blocks. Does not rely on Ghidra having defined the string."""
    mem = program.getMemory()
    for block in mem.getBlocks():
        if not block.isInitialized() or block.isExecute():
            continue
        import jpype

        size = int(block.getSize())
        jbuf = jpype.JArray(jpype.JByte)(size)
        block.getBytes(block.getStart(), jbuf)
        buf = bytes(b & 0xFF for b in jbuf)
        for m in re.finditer(rb"[\x20-\x7e]{5,}\x00", buf):
            yield block.getStart().add(m.start()), m.group()[:-1].decode("latin1")


def scan(program, out_dir: Path) -> None:
    from ghidra.program.model.symbol import SourceType

    listing = program.getListing()
    refs = program.getReferenceManager()
    symbols = program.getSymbolTable()
    per_func = defaultdict(set)  # entry -> {(class, method, text)}
    funcs = {}
    for addr, text in strings_in(program):
        named = parse(text)
        if named is None:
            continue
        for ref in refs.getReferencesTo(addr):
            f = listing.getFunctionContaining(ref.getFromAddress())
            if f is None:
                continue
            key = str(f.getEntryPoint())
            funcs[key] = f
            per_func[key].add((named[0], named[1], text))

    rows = []
    for key, hits in sorted(per_func.items()):
        f = funcs[key]
        methods = {m for _, m, _ in hits}
        classes = {c for c, _, _ in hits if c}
        texts = sorted(t for _, _, t in hits)
        verdict = "named"
        if len(methods) != 1 or len(classes) > 1:
            verdict = "ambiguous"
        f.setComment("RING-STR: " + " | ".join(texts))
        new = None
        if verdict == "named":
            method = next(iter(methods))
            cls = next(iter(classes)) if classes else None
            new = f"{cls}::{method}" if cls else method
            if f.getName().startswith("FUN_"):
                try:
                    if cls:
                        ns = symbols.getNamespace(cls, None) or symbols.createClass(
                            None, cls, SourceType.ANALYSIS)
                        f.getSymbol().setNamespace(ns)
                    f.setName(method, SourceType.ANALYSIS)
                except Exception as exc:  # duplicate name: keep the address in it
                    try:
                        f.setName(f"{method}_{key}", SourceType.ANALYSIS)
                    except Exception:
                        print(f"  rename failed at {key}: {exc}")
        rows.append({
            "address": key,
            "name": new or "",
            "verdict": verdict,
            "size": f.getBody().getNumAddresses(),
            "strings": " | ".join(texts),
        })

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{program.getName()}.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["address", "name", "verdict", "size", "strings"])
        w.writeheader()
        w.writerows(rows)
    named = sum(r["verdict"] == "named" for r in rows)
    print(f"{program.getName()}: {program.getFunctionManager().getFunctionCount()} functions, "
          f"{len(rows)} with method strings, {named} named, "
          f"{len(rows) - named} ambiguous -> {path}")


def selftest() -> None:
    assert parse("aApplication::AddRot -> Node File does not exist -> ") == ("aApplication", "AddRot")
    assert parse("PuzSetMovToRot -> Wrong Puzzle ID ->") == (None, "PuzSetMovToRot")
    assert parse("ObjSetAccOnOrOff(INT id, CHAR v) -> pa == NULL") == (None, "ObjSetAccOnOrOff")
    assert parse("aApplication::ObjPreSetAniCooOnPuz I -> Object ID is wrong ->") == (
        "aApplication", "ObjPreSetAniCooOnPuz")
    assert parse("aApplication::DisFad Mem Lock falied") == ("aApplication", "DisFad")
    assert parse("Microsoft Visual C++ Runtime Library") is None
    assert parse("InsertCD") is None
    print("selftest ok")


if "--selftest" in sys.argv:
    selftest()
else:
    args = getScriptArgs()  # noqa: F821 (Ghidra script global)
    scan(currentProgram, Path(args[0] if args else "engines/ring/notes/names"))  # noqa: F821
