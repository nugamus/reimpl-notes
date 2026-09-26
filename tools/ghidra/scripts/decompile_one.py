"""Decompile one named function to disk, with its callee list.

CLAUDE.md rule 4: one function at a time, never bulk. The output lands in `engines/x3d/notes/decomp/`
so it can be read selectively instead of being dragged through context, and the callee
list is what drives the next hop.

    python -m pyghidra.ghidra_launch --install-dir C:\\ghidra \\
        ghidra.app.util.headless.AnalyzeHeadless ghidra_projects Monet \\
        -process x3d.dll -noanalysis -readOnly \\
        -scriptPath tools/ghidra/scripts -postScript decompile_one.py \\
        engines/x3d/notes/decomp X3d_Load_Sdk_o3d

Accepts a symbol name or a hex address, and more than one of either. `-readOnly` fits
here: decompiling changes nothing, and it leaves the project untouched.

Nothing produced here may be pasted into `engine/` (rule 3). It is reference for writing
a spec; the spec is what gets implemented.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HEX = re.compile(r"^(0x)?[0-9a-fA-F]{4,16}$")


def resolve(program, selector: str) -> list:
    """Functions matching a name or an address."""
    fn_mgr = program.getFunctionManager()

    if HEX.match(selector):
        addr = program.getAddressFactory().getAddress(selector.replace("0x", ""))
        if addr is not None:
            func = fn_mgr.getFunctionAt(addr) or fn_mgr.getFunctionContaining(addr)
            if func is not None:
                return [func]

    return [f for f in fn_mgr.getFunctions(True) if f.getName() == selector]


def decompile(program, func, out_dir: Path, timeout: int = 120) -> dict:
    from ghidra.app.decompiler import DecompInterface
    from ghidra.util.task import ConsoleTaskMonitor

    iface = DecompInterface()
    iface.openProgram(program)
    try:
        result = iface.decompileFunction(func, timeout, ConsoleTaskMonitor())
        if not result.decompileCompleted():
            return {"name": func.getName(), "error": result.getErrorMessage()}
        code = result.getDecompiledFunction().getC()
    finally:
        iface.dispose()

    entry = func.getEntryPoint()
    callees = sorted(
        "%s @ %s" % (c.getName(), c.getEntryPoint())
        for c in func.getCalledFunctions(None)
    )

    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", func.getName())
    path = out_dir / ("%s__%s.c" % (program.getName(), safe))
    header = [
        "/* %s!%s at 0x%s, %d bytes"
        % (program.getName(), func.getName(), entry, func.getBody().getNumAddresses()),
        " *",
        " * Ghidra decompiler output. Reference only — never paste into engine/",
        " * (CLAUDE.md rule 3). Regenerate with tools/ghidra/scripts/decompile_one.py.",
        " *",
        " * Calls:",
    ]
    header += [" *   %s" % c for c in callees] or [" *   (none)"]
    header.append(" */")
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(header) + "\n\n" + code, encoding="utf-8")

    return {
        "name": func.getName(),
        "address": str(entry),
        "size": func.getBody().getNumAddresses(),
        "callees": callees,
        "path": str(path),
    }


def run(program, args: list) -> None:
    if len(args) < 2:
        print("usage: decompile_one.py <outdir> <name-or-address> [more...]")
        return
    out_dir = Path(args[0]).resolve()
    for selector in args[1:]:
        funcs = resolve(program, selector)
        if not funcs:
            print("%s: no function matching %r" % (program.getName(), selector))
            continue
        for func in funcs:
            info = decompile(program, func, out_dir)
            if "error" in info:
                print("%s: decompile failed: %s" % (info["name"], info["error"]))
                continue
            print(
                "%s @ 0x%s, %d bytes, %d callees -> %s"
                % (
                    info["name"],
                    info["address"],
                    info["size"],
                    len(info["callees"]),
                    info["path"],
                )
            )
            for callee in info["callees"]:
                print("    calls %s" % callee)


try:  # injected by Ghidra; absent under plain CPython
    currentProgram  # noqa: F821
except NameError:
    if __name__ == "__main__":
        print(__doc__)
        sys.exit(2)
else:
    run(currentProgram, list(getScriptArgs()))  # noqa: F821
