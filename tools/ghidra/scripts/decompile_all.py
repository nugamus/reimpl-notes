"""Decompile every function of a program to disk, plus a grep-able index.

The point is to search before exploring: `grep -l` over the dump finds which functions read
a string, call an import or touch an offset, and INDEX.tsv lists every function with its
size, callers and the strings it references, all without one decompile in context. Rerun
after a naming session so the dump carries the new names.

    python -m pyghidra.ghidra_launch --install-dir C:\\ghidra \\
        ghidra.app.util.headless.AnalyzeHeadless ghidra_projects Grumpa/grumpa-import \\
        -process GRUMPA.EXE -noanalysis -readOnly \\
        -scriptPath tools/ghidra/scripts -postScript decompile_all.py engines/grumpa/notes/decomp/all

Output (gitignored with the rest of notes/decomp, never published, never pasted into
engine code, rule 3): `<address>_<name>.c` per function and `INDEX.tsv`
(address, name, bytes, callers, callees, strings).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def strings_of(program, func, limit: int = 4) -> list:
    listing, refs = program.getListing(), program.getReferenceManager()
    found = []
    for addr in func.getBody().getAddresses(True):
        for ref in refs.getReferencesFrom(addr):
            data = listing.getDataAt(ref.getToAddress())
            if data is not None and data.hasStringValue():
                s = str(data.getValue()).replace("\t", " ").replace("\n", "\\n")[:60]
                if s not in found:
                    found.append(s)
                    if len(found) >= limit:
                        return found
    return found


def run(program, args: list) -> None:
    from ghidra.app.decompiler import DecompInterface
    from ghidra.util.task import ConsoleTaskMonitor

    if not args:
        print("usage: decompile_all.py <outdir>")
        return
    out = Path(args[0]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    iface = DecompInterface()
    iface.openProgram(program)
    monitor = ConsoleTaskMonitor()
    rows, failed = [], 0
    try:
        for func in program.getFunctionManager().getFunctions(True):
            if func.isThunk() or func.isExternal():
                continue
            entry, name = str(func.getEntryPoint()), func.getName(True)
            callers = func.getCallingFunctions(None).size()
            callees = func.getCalledFunctions(None).size()
            result = iface.decompileFunction(func, 60, monitor)
            if not result.decompileCompleted():
                failed += 1
                continue
            safe = re.sub(r"[^A-Za-z0-9_.-]", "_", name)[:80]
            (out / ("%s_%s.c" % (entry, safe))).write_text(
                "/* %s!%s at 0x%s. Ghidra output, reference only (rule 3). */\n\n%s"
                % (program.getName(), name, entry, result.getDecompiledFunction().getC()),
                encoding="utf-8")
            rows.append("\t".join([entry, name, str(func.getBody().getNumAddresses()), str(callers),
                                   str(callees), " | ".join(strings_of(program, func))]))
    finally:
        iface.dispose()
    (out / "INDEX.tsv").write_text("address\tname\tbytes\tcallers\tcallees\tstrings\n" + "\n".join(rows) + "\n",
                                   encoding="utf-8")
    print("%s: %d functions -> %s (%d failed)" % (program.getName(), len(rows), out, failed))


try:  # injected by Ghidra; absent under plain CPython
    currentProgram  # noqa: F821
except NameError:
    if __name__ == "__main__":
        print(__doc__)
        sys.exit(2)
else:
    run(currentProgram, list(getScriptArgs()))  # noqa: F821
