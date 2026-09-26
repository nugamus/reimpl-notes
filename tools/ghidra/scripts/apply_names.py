"""Apply names from a CSV (columns `address`, `name`, optional `evidence`) to a program.

Only functions still called FUN_* or named earlier by this script are renamed (names
given by hand in Ghidra win). A
`Class::method` name puts the function in that class namespace. The evidence goes into
the function's plate comment.

    python -m pyghidra.ghidra_launch --install-dir 'C:\\ghidra' \\
        ghidra.app.util.headless.AnalyzeHeadless ghidra_projects Peintre \\
        -process MISSION.EXE -noanalysis \\
        -scriptPath tools/ghidra/scripts -postScript apply_names.py engines/peintre/notes/function-map.csv
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path


def apply(program, path: Path) -> None:
    from ghidra.program.model.symbol import SourceType

    fm = program.getFunctionManager()
    st = program.getSymbolTable()
    af = program.getAddressFactory()
    done = skipped = 0
    for row in csv.DictReader(path.open(encoding="utf-8")):
        name = (row.get("name") or "").strip()
        if not name:
            continue
        f = fm.getFunctionAt(af.getAddress(row["address"].replace("0x", "")))
        if f is None:
            print(f"  no function at {row['address']}")
            continue
        ours = (f.getComment() or "").startswith("Named from: ")  # a name this script gave
        if not f.getName().startswith("FUN_") and not ours and f.getName(True) != name:
            skipped += 1
            continue
        cls, _, method = name.rpartition("::")
        if cls:
            ns = st.getNamespace(cls, None) or st.createClass(None, cls, SourceType.USER_DEFINED)
            f.getSymbol().setNamespace(ns)
        f.setName(method, SourceType.USER_DEFINED)
        if row.get("evidence"):
            f.setComment("Named from: " + row["evidence"])
        done += 1
    print(f"{program.getName()}: {done} named, {skipped} kept their existing names")


try:
    currentProgram  # noqa: F821
except NameError:
    if __name__ == "__main__":
        print(__doc__)
        sys.exit(2)
else:
    apply(currentProgram, Path(list(getScriptArgs())[0]))  # noqa: F821
