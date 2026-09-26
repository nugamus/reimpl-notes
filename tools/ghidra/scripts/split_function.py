"""Make each given address a function entry, splitting the function that swallowed it.

Auto-analysis sometimes grows one function over a neighbour that is only reached through a
vtable (Ring's sound classes, 0x47ac90 inside 0x47aaf0). For each address: if a function
contains it but starts elsewhere, that function is removed and both entries are re-created
from their flow. Not read-only: the change is saved.

    ... -process RING_DVD.EXE -noanalysis -scriptPath tools/ghidra/scripts \\
        -postScript split_function.py 0x47ac90 0x47b3b0
"""

from __future__ import annotations

from ghidra.app.cmd.function import CreateFunctionCmd  # type: ignore

fm = currentProgram.getFunctionManager()  # noqa: F821 (Ghidra script global)
space = currentProgram.getAddressFactory().getDefaultAddressSpace()  # noqa: F821
for arg in getScriptArgs():  # noqa: F821
    addr = space.getAddress(int(arg, 16))
    f = fm.getFunctionContaining(addr)
    if f is not None and f.getEntryPoint() == addr:
        print(f"{arg}: already an entry ({f.getName(True)})")
        continue
    entries = [addr]
    if f is not None:
        entries.insert(0, f.getEntryPoint())
        fm.removeFunction(f.getEntryPoint())
    for e in entries:
        ok = CreateFunctionCmd(e).applyTo(currentProgram)  # noqa: F821
        g = fm.getFunctionAt(e)
        print(f"{e}: {'created' if ok else 'FAILED'} "
              f"{g.getBody().getNumAddresses() if g else 0} bytes")
