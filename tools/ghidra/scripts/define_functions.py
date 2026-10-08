"""Define functions from a list file (lines: `<hexaddr> [name]`), disassembling first.
Name given -> renamed to it. Run without -readOnly. Arg: list file."""
from __future__ import annotations

import sys
from pathlib import Path


def run(program, args):
    from ghidra.app.cmd.disassemble import DisassembleCommand
    from ghidra.app.cmd.function import CreateFunctionCmd
    from ghidra.program.model.symbol import SourceType

    af, fm = program.getAddressFactory(), program.getFunctionManager()
    made = named = fail = 0
    for line in Path(args[0]).read_text().splitlines():
        f = line.split()
        if not f:
            continue
        a = af.getAddress(f[0])
        fn = fm.getFunctionAt(a)
        if fn is None:
            DisassembleCommand(a, None, True).applyTo(program)
            if CreateFunctionCmd(a).applyTo(program):
                made += 1
            else:
                fail += 1
                print("FAIL", f[0])
                continue
            fn = fm.getFunctionAt(a)
        if len(f) > 1 and fn is not None:
            ns = program.getSymbolTable().getOrCreateNameSpace(
                program.getGlobalNamespace(), f[1].rsplit("::", 1)[0], SourceType.USER_DEFINED) if "::" in f[1] else None
            fn.setName(f[1].rsplit("::", 1)[-1], SourceType.USER_DEFINED)
            if ns is not None:
                fn.setParentNamespace(ns)
            named += 1
    print("DEFINED %d NAMED %d FAILED %d" % (made, named, fail))


run(currentProgram, list(getScriptArgs()))  # noqa: F821
