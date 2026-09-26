"""Rename functions: arguments `addr=Class::name` (or `addr=name`) and set a comment with
the evidence id, e.g. `0x406080=aApplication::VarDefByte@E-0031`. Not read-only: saved.

    ... -process RING_DVD.EXE -noanalysis -scriptPath tools/ghidra/scripts \\
        -postScript rename.py 0x406080=aApplication::VarDefByte@E-0031
"""

from __future__ import annotations

from ghidra.program.model.symbol import SourceType  # type: ignore

fm = currentProgram.getFunctionManager()  # noqa: F821 (Ghidra script global)
st = currentProgram.getSymbolTable()  # noqa: F821
space = currentProgram.getAddressFactory().getDefaultAddressSpace()  # noqa: F821
for arg in getScriptArgs():  # noqa: F821
    addr, _, rest = arg.partition("=")
    name, _, ev = rest.partition("@")
    f = fm.getFunctionAt(space.getAddress(int(addr, 16)))
    if f is None:
        print(f"{addr}: no function")
        continue
    ns = None
    if "::" in name:
        cls, name = name.rsplit("::", 1)
        ns = st.getNamespace(cls, None) or st.createClass(None, cls, SourceType.USER_DEFINED)
    f.setName(name, SourceType.USER_DEFINED)
    if ns is not None:
        f.getSymbol().setNamespace(ns)
    if ev:
        f.setComment((f.getComment() + "\n" if f.getComment() else "") + f"named: {ev}")
    print(f"{addr}: {f.getName(True)}")
