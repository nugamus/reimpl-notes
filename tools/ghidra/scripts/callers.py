"""Print the callers (and the call sites) of functions, by name or hex address.

    python -m pyghidra.ghidra_launch --install-dir 'C:\\ghidra' \\
        ghidra.app.util.headless.AnalyzeHeadless ghidra_projects Ring \\
        -process RING_DVD.EXE -noanalysis -readOnly \\
        -scriptPath tools/ghidra/scripts -postScript callers.py 00429dc0 aArt::Init
"""

from __future__ import annotations


def find(program, sel: str):
    fm = program.getFunctionManager()
    try:
        addr = program.getAddressFactory().getDefaultAddressSpace().getAddress(int(sel, 16))
        f = fm.getFunctionContaining(addr)
        return [f] if f else []
    except ValueError:
        return [f for f in fm.getFunctions(True) if f.getName(True) == sel or f.getName() == sel]


for sel in getScriptArgs():  # noqa: F821 (Ghidra script global)
    for f in find(currentProgram, sel):  # noqa: F821
        print(f"== {f.getName(True)} @ {f.getEntryPoint()}")
        for ref in currentProgram.getReferenceManager().getReferencesTo(f.getEntryPoint()):  # noqa: F821
            caller = currentProgram.getListing().getFunctionContaining(ref.getFromAddress())  # noqa: F821
            print(f"   {ref.getFromAddress()} {ref.getReferenceType()} "
                  f"{caller.getName(True) + ' @ ' + str(caller.getEntryPoint()) if caller else '-'}")
