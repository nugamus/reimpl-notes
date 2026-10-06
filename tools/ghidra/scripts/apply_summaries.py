"""Push engines/<engine>/notes/summaries.tsv into the open program: each summarized function
gets its summary (and evidence id) as its plate comment, and its name when it still has a
generated one (FUN_...). Run headless without -readOnly, after backing up the project:

    python -m pyghidra.ghidra_launch --install-dir C:\\ghidra \\
        ghidra.app.util.headless.AnalyzeHeadless ghidra_projects Grumpa/grumpa-import \\
        -process GRUMPA_NOCD.EXE -noanalysis \\
        -scriptPath tools/ghidra/scripts -postScript apply_summaries.py engines/grumpa/notes/summaries.tsv

Only rows whose program column matches the open program are applied.
"""

from __future__ import annotations

import sys
from pathlib import Path


def run(program, args: list) -> None:
    from ghidra.program.model.symbol import SourceType

    rows = Path(args[0]).read_text(encoding="utf-8").splitlines()[1:]
    fm, af = program.getFunctionManager(), program.getAddressFactory()
    named = commented = missing = 0
    for line in rows:
        f = line.split("\t")
        if len(f) < 4 or f[0].lower() != program.getName().lower():
            continue
        func = fm.getFunctionAt(af.getAddress(f[1]))
        if func is None:
            missing += 1
            continue
        evidence = f" ({f[4]})" if len(f) > 4 and f[4] else ""
        func.setComment(f"{f[3]}{evidence}")
        commented += 1
        if f[2] and func.getName().startswith("FUN_"):
            name = f[2].split("::")[-1]
            func.setName(name, SourceType.USER_DEFINED)
            named += 1
    print("%s: %d comments, %d names applied, %d addresses without a function"
          % (program.getName(), commented, named, missing))


try:  # injected by Ghidra; absent under plain CPython
    currentProgram  # noqa: F821
except NameError:
    if __name__ == "__main__":
        print(__doc__)
        sys.exit(2)
else:
    run(currentProgram, list(getScriptArgs()))  # noqa: F821
