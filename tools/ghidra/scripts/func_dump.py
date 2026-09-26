"""Dump every function of a program with what names it: strings, API calls, callees.

One TSV row per function, for naming offline (plain Python, testable) instead of in
Ghidra. Columns: address, name, size, callers, callees (addresses), apis (imported
functions called, direct or through the IAT), strings (every string the function's
instructions reference, `|`-separated, tabs and newlines escaped).

    python -m pyghidra.ghidra_launch --install-dir 'C:\\ghidra' \\
        ghidra.app.util.headless.AnalyzeHeadless ghidra_projects Peintre \\
        -process MISSION.EXE -noanalysis -readOnly \\
        -scriptPath tools/ghidra/scripts -postScript func_dump.py engines/peintre/notes/function-dump.tsv
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def cstring(mem, addr, limit=200):
    """The NUL-terminated printable string at addr, or None."""
    out = bytearray()
    try:
        for i in range(limit):
            b = mem.getByte(addr.add(i)) & 0xFF
            if b == 0:
                break
            if b < 0x20 and b not in (9, 10, 13) or b > 0x7E and b < 0xA0:
                return None
            out.append(b)
        else:
            return None
    except Exception:
        return None
    return out.decode("latin1") if len(out) >= 3 else None


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r").replace("|", "\\x7c")


def dump(program, out: Path) -> None:
    fm = program.getFunctionManager()
    listing = program.getListing()
    mem = program.getMemory()
    refs = program.getReferenceManager()
    rows = []
    for f in fm.getFunctions(True):
        strings, apis = [], set()
        for ins in listing.getInstructions(f.getBody(), True):
            for ref in ins.getReferencesFrom():
                to = ref.getToAddress()
                if not to.isMemoryAddress():
                    continue
                sym = program.getSymbolTable().getPrimarySymbol(to)
                if sym is not None and sym.isExternal():
                    apis.add(sym.getName())
                    continue
                if ref.getReferenceType().isCall():
                    continue
                if ref.getReferenceType().isData():
                    # IAT slot: data pointing at an external
                    for r2 in refs.getReferencesFrom(to):
                        s2 = program.getSymbolTable().getPrimarySymbol(r2.getToAddress())
                        if s2 is not None and s2.isExternal():
                            apis.add(s2.getName())
                    s = cstring(mem, to)
                    if s is not None and s not in strings:
                        strings.append(s)
        callees = set()
        for c in f.getCalledFunctions(None):
            if c.isThunk():  # incremental-link jump stubs: record what they reach
                c = c.getThunkedFunction(True)
            if c.isExternal():
                apis.add(c.getName())
            else:
                callees.add(str(c.getEntryPoint()))
        callees = sorted(callees)
        callers = {str(c.getEntryPoint()) for c in f.getCallingFunctions(None)}
        for t in f.getFunctionThunkAddresses(True) or []:
            thunk = fm.getFunctionAt(t)
            if thunk is not None:
                callers |= {str(c.getEntryPoint()) for c in thunk.getCallingFunctions(None)}
        callers = len(callers)
        if f.isThunk():
            continue
        rows.append("\t".join([
            str(f.getEntryPoint()), f.getName(True), str(f.getBody().getNumAddresses()),
            str(callers), ",".join(callees), ",".join(sorted(apis)),
            "|".join(esc(s) for s in strings),
        ]))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("address\tname\tsize\tcallers\tcallees\tapis\tstrings\n" + "\n".join(rows) + "\n",
                   encoding="utf-8")
    print(f"{program.getName()}: {len(rows)} functions -> {out}")


try:
    currentProgram  # noqa: F821
except NameError:
    if __name__ == "__main__":
        print(__doc__)
        sys.exit(2)
else:
    args = list(getScriptArgs())  # noqa: F821
    dump(currentProgram, Path(args[0]))  # noqa: F821
