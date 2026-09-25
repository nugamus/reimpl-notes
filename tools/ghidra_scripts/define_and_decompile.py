"""Define a function at the given address (if missing) and decompile it.

Use when Ghidra's auto-analysis skipped a routine (e.g. because the prologue
isn't the standard 55 8B EC). Reads as `python -m pyghidra... -postScript
define_and_decompile.py notes/decomp 0x41d340 [more...]`.

Runs in non-readOnly mode so the new function persists.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import decompile_one as d1

HEX = re.compile(r"^(0x)?[0-9a-fA-F]{4,16}$")


def ensure_function(program, addr_str: str):
    from ghidra.program.model.symbol import SourceType  # type: ignore

    addr = program.getAddressFactory().getAddress(addr_str.replace("0x", ""))
    fn_mgr = program.getFunctionManager()
    fn = fn_mgr.getFunctionAt(addr) or fn_mgr.getFunctionContaining(addr)
    if fn is not None:
        return fn

    listing = program.getListing()
    next_defined = None
    for f in fn_mgr.getFunctions(True):
        entry = int(str(f.getEntryPoint()), 16)
        if entry > int(str(addr), 16):
            if next_defined is None or entry < int(str(next_defined), 16):
                next_defined = f.getEntryPoint()
    end = int(str(next_defined), 16) - 1 if next_defined else int(str(addr), 16) + 0x400
    end_addr = program.getAddressFactory().getAddress("0x%x" % end)

    body = program.getAddressFactory().getAddressSet(addr, end_addr)
    print("defining function at %s .. %s" % (addr, end_addr))

    # Public 4-arg form: name, entry, body, source
    name = "FUN_%s" % addr_str.replace("0x", "")
    fn = fn_mgr.createFunction(name, addr, body, SourceType.USER_DEFINED)
    return fn


def run(program, args):
    if len(args) < 2:
        print("usage: define_and_decompile.py <outdir> <hex-addr> [more...]")
        return
    out_dir = Path(args[0]).resolve()
    for sel in args[1:]:
        if not HEX.match(sel):
            print("skip %r (not a hex address)" % sel)
            continue
        fn = ensure_function(program, sel)
        if fn is None:
            print("could not define function at %s" % sel)
            continue
        info = d1.decompile(program, fn, out_dir)
        if "error" in info:
            print("decompile failed for %s: %s" % (sel, info["error"]))
            continue
        print(
            "%s @ %s, %d bytes, %d callees -> %s"
            % (info["name"], info["address"], info["size"], len(info["callees"]), info["path"])
        )
        for c in info["callees"]:
            print("    calls %s" % c)


try:  # injected by Ghidra; absent under plain CPython
    currentProgram  # noqa: F821
except NameError:
    if __name__ == "__main__":
        print(__doc__)
        sys.exit(2)
else:
    run(currentProgram, list(getScriptArgs()))  # noqa: F821
