"""Dump every function of a program as JSON lines for cross-edition matching: entry, size,
and in instruction order its call targets (thunks resolved), strings referenced outside code, scalar
operands >= 0x100 that are not addresses in the program, and the subset of those pushed or
moved (`args`: call arguments, not switch-case compares, which compilers lay out differently). Used by
engines/ring/tools/handlers.py (E-0304).

    python -m pyghidra.ghidra_launch --install-dir 'C:\ghidra' \
        ghidra.app.util.headless.AnalyzeHeadless build/ghidra-ring-editions Ring \
        -process RING_ISO.EXE -noanalysis -readOnly \
        -scriptPath tools/ghidra/scripts -postScript ring_features.py build/ring-features/RING_ISO.jsonl
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def cstring(mem, addr, limit=200):
    out = bytearray()
    try:
        for i in range(limit):
            b = mem.getByte(addr.add(i)) & 0xFF
            if b == 0:
                break
            if b < 0x20 and b not in (9, 10, 13):
                return None
            out.append(b)
        else:
            return None
    except Exception:
        return None
    return out.decode("latin1") if out else None


def dump(program, out: Path) -> None:
    from ghidra.program.model.scalar import Scalar
    fm = program.getFunctionManager()
    listing = program.getListing()
    mem = program.getMemory()
    rows = []
    for f in fm.getFunctions(True):
        if f.isThunk():
            continue
        calls, strings, scalars, args = [], [], [], []
        for ins in listing.getInstructions(f.getBody(), True):
            for ref in ins.getReferencesFrom():
                to = ref.getToAddress()
                if not to.isMemoryAddress():
                    continue
                if ref.getReferenceType().isCall():
                    c = fm.getFunctionAt(to)
                    if c is not None and c.isThunk():
                        c = c.getThunkedFunction(True)
                    calls.append(c.getName() if c is not None and c.isExternal() else str(to))
                elif ref.getReferenceType().isData() and not mem.getBlock(to).isExecute():  # not jump tables
                    s = cstring(mem, to)
                    if s is not None:
                        strings.append(s)
            for i in range(ins.getNumOperands()):
                for o in ins.getOpObjects(i):
                    if isinstance(o, Scalar):
                        v = o.getUnsignedValue() & 0xFFFFFFFF
                        if v >= 0x100 and not mem.contains(program.getAddressFactory().getDefaultAddressSpace().getAddress(v)):
                            scalars.append(v)
                            if ins.getMnemonicString().upper() in ("PUSH", "MOV"):
                                args.append(v)
        rows.append(json.dumps({"entry": str(f.getEntryPoint()), "name": f.getName(),
                                "size": f.getBody().getNumAddresses(), "calls": calls,
                                "strings": strings, "scalars": scalars, "args": args}))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"{program.getName()}: {len(rows)} functions -> {out}")


try:
    currentProgram  # noqa: F821
except NameError:
    if __name__ == "__main__":
        print(__doc__)
        sys.exit(2)
else:
    dump(currentProgram, Path(list(getScriptArgs())[0]))  # noqa: F821
