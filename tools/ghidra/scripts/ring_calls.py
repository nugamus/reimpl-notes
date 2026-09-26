"""List every call a function makes, with the constant arguments pushed for it.

For the Ring engine's zone set-up and event functions, which are long runs of engine API
calls (`AddPuz`, `PuzAddBgrImg`, …) with constant arguments. MSVC pushes arguments right
to left, so the pushes between the previous call and this one, read backwards, are the
arguments in order. Each argument is reported as its constant: an integer, a string when
the value points at a NUL-terminated string in a data block, or `?` when it was not a
constant push (a register or memory). The callee's argument count comes from its stack
purge (callee-cleaned `__thiscall`/`__stdcall`) when Ghidra knows it.

    python -m pyghidra.ghidra_launch --install-dir 'C:\\ghidra' \\
        ghidra.app.util.headless.AnalyzeHeadless ghidra_projects Ring \\
        -process RING_DVD.EXE -noanalysis -readOnly \\
        -scriptPath tools/ghidra/scripts -postScript ring_calls.py <out.jsonl> 0x4662a0 ...

Output: one JSON object per call: {"fn", "at", "callee", "addr", "args": [...],
"purge": n}.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def string_at(program, value: int) -> str | None:
    mem = program.getMemory()
    space = program.getAddressFactory().getDefaultAddressSpace()
    try:
        a = space.getAddress(value)
    except Exception:
        return None
    block = mem.getBlock(a)
    if block is None or block.isExecute() or not block.isInitialized():
        return None
    out = bytearray()
    for i in range(256):
        try:
            b = mem.getByte(a.add(i)) & 0xFF
        except Exception:
            return None
        if b == 0:
            break
        if b < 0x20 and b not in (9, 10, 13):
            return None
        out.append(b)
    else:
        return None
    return out.decode("cp1252") if out else ""


def operand_value(program, ins):
    """The constant a PUSH pushes, or None."""
    from ghidra.program.model.scalar import Scalar
    from ghidra.program.model.address import Address

    objs = ins.getOpObjects(0)
    if len(objs) == 1 and isinstance(objs[0], Scalar):
        return objs[0].getUnsignedValue() & 0xFFFFFFFF
    if len(objs) == 1 and isinstance(objs[0], Address):
        return objs[0].getOffset() & 0xFFFFFFFF
    return None


def describe(program, v):
    if v is None:
        return "?"
    s = string_at(program, v) if v >= 0x400000 else None
    return {"str": s} if s is not None else v


def calls_of(program, func):
    listing = program.getListing()
    fm = program.getFunctionManager()
    pending = []  # pushes since the last call, in execution order
    out = []
    for ins in listing.getInstructions(func.getBody(), True):
        m = ins.getMnemonicString()
        if m == "PUSH":
            pending.append(operand_value(program, ins))
        elif m == "CALL":
            target = None
            flows = ins.getFlows()
            if flows:
                target = fm.getFunctionAt(flows[0])
            purge = target.getStackPurgeSize() if target else -1
            n = purge // 4 if purge and purge > 0 else len(pending)
            args = list(reversed(pending))[:n] if n <= len(pending) else list(reversed(pending))
            out.append({
                "fn": func.getName(True), "at": str(ins.getAddress()),
                "callee": target.getName(True) if target else str(ins.getDefaultOperandRepresentation(0)),
                "addr": str(target.getEntryPoint()) if target else None,
                "args": [describe(program, a) for a in args], "purge": purge,
            })
            # pushes that were not this call's arguments stay for an outer call
            pending = pending[:len(pending) - n] if n <= len(pending) else []
        elif m in ("RET", "JMP") and not pending:
            pass
    return out


args = getScriptArgs()  # noqa: F821 (Ghidra script global)
out_path = Path(args[0])
fm = currentProgram.getFunctionManager()  # noqa: F821
space = currentProgram.getAddressFactory().getDefaultAddressSpace()  # noqa: F821
rows = []
for sel in args[1:]:
    f = fm.getFunctionContaining(space.getAddress(int(sel, 16)))
    if f is None:
        print(f"no function at {sel}")
        continue
    rows += calls_of(currentProgram, f)  # noqa: F821
out_path.parent.mkdir(parents=True, exist_ok=True)
with out_path.open("w", encoding="utf-8") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"{len(rows)} calls -> {out_path}")
