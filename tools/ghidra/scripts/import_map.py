"""Map engine-DLL imports to the source files that call them.

Answers "which `x3d.dll` export is used by which `.cpp`" without decompiling anything:
walk the import thunks, take their callers, and join those function addresses against the
assert attribution in `engines/x3d/notes/function-map.csv` (see `assert_namer.py`).

Scan one program:

    python -m pyghidra.ghidra_launch --install-dir C:\\ghidra \\
        ghidra.app.util.headless.AnalyzeHeadless ghidra_projects Monet \\
        -process MissionMonet.exe -noanalysis \\
        -scriptPath tools/ghidra/scripts -postScript import_map.py engines/x3d/notes/_assert_scan

Merge into `engines/x3d/notes/import-map.md`:

    python tools/ghidra/scripts/import_map.py --merge engines/x3d/notes/_assert_scan

Self-check:

    python tools/ghidra/scripts/import_map.py --selftest
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

# The DLLs whose call sites matter for reimplementation. Everything else (kernel32, the
# CRT, GDI) is noise here.
ENGINE_LIBS = {
    "x3d.dll",
    "h3d.dll",
    "x3dsdk.dll",
    "xd3d.dll",
    "xs3d.dll",
    "x3dmp5.dll",
    "x3dmp6.dll",
    "x3dmp6k.dll",
    "4xvideo.dll",
    "aviplay.dll",
    "flc.dll",
}


# --------------------------------------------------------------------------- scan mode


def scan(program, out_dir: Path) -> dict:
    listing = program.getListing()
    ref_mgr = program.getReferenceManager()
    fn_mgr = program.getFunctionManager()
    prog_name = program.getName()

    imports = []
    for ext in fn_mgr.getExternalFunctions():
        loc = ext.getExternalLocation()
        library = (loc.getLibraryName() or "").lower()
        if library not in ENGINE_LIBS:
            continue

        # An import is reachable through its EXTERNAL-space entry and through every thunk
        # Ghidra generated for it; call sites may reference either.
        targets = [ext.getEntryPoint()]
        try:
            targets.extend(list(ext.getFunctionThunkAddresses() or []))
        except Exception:
            pass

        callers = set()
        for target in targets:
            for ref in ref_mgr.getReferencesTo(target):
                caller = listing.getFunctionContaining(ref.getFromAddress())
                if caller is not None and not caller.isThunk():
                    callers.add(str(caller.getEntryPoint()))

        imports.append(
            {
                "library": library,
                "name": ext.getName(),
                "thunks": [str(a) for a in targets],
                "callers": sorted(callers),
            }
        )

    record = {
        "program": prog_name,
        "imports": sorted(imports, key=lambda i: (i["library"], i["name"])),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / (prog_name + ".imports.json")).write_text(
        json.dumps(record, indent=2), encoding="utf-8"
    )
    used = sum(1 for i in imports if i["callers"])
    print(
        "%s: %d engine-DLL imports, %d with an identified calling function"
        % (prog_name, len(imports), used)
    )
    return record


# -------------------------------------------------------------------------- merge mode


def _attribution(notes_dir: Path) -> dict:
    """(program, function address) -> source file, from the assert attribution."""
    path = notes_dir / "function-map.csv"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return {
            (row["program"], row["address"]): row["source_file"]
            for row in csv.DictReader(fh)
        }


def merge(scan_dir: Path, notes_dir: Path) -> dict:
    attributed = _attribution(notes_dir)
    records = [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(scan_dir.glob("*.imports.json"))
    ]
    text = _render(records, attributed)
    notes_dir.mkdir(parents=True, exist_ok=True)
    (notes_dir / "import-map.md").write_text(text, encoding="utf-8")
    return {"records": len(records), "imports": sum(len(r["imports"]) for r in records)}


def _render(records: list, attributed: dict) -> str:
    out: list = []
    w = out.append

    w("# Engine-DLL import map")
    w("")
    w(
        "Every import from an engine DLL, the functions that call it, and — where the "
        "assert strings attribute that caller — the source file it came from. Generated "
        "by `tools/ghidra/scripts/import_map.py`; regenerate rather than hand-edit."
    )
    w("")
    w(
        "A caller with no source file is a function no assert site names. That is a gap "
        "in the attribution, not evidence the call is unattributable."
    )
    w("")

    for rec in sorted(records, key=lambda r: r["program"]):
        prog = rec["program"]
        by_lib = defaultdict(list)
        for imp in rec["imports"]:
            by_lib[imp["library"]].append(imp)

        w("## `%s`" % prog)
        w("")
        w("| Library | Imports | With a known caller | With a known source file |")
        w("|---|---:|---:|---:|")
        for lib, imps in sorted(by_lib.items()):
            with_caller = sum(1 for i in imps if i["callers"])
            with_src = sum(
                1 for i in imps if any((prog, c) in attributed for c in i["callers"])
            )
            w("| `%s` | %d | %d | %d |" % (lib, len(imps), with_caller, with_src))
        w("")

        for lib, imps in sorted(by_lib.items()):
            w("### `%s` — `%s`" % (lib, prog))
            w("")
            w("| Export | Callers | Source files |")
            w("|---|---:|---|")
            for imp in sorted(imps, key=lambda i: i["name"]):
                srcs = sorted(
                    {
                        attributed[(prog, c)]
                        for c in imp["callers"]
                        if (prog, c) in attributed
                    }
                )
                w(
                    "| `%s` | %d | %s |"
                    % (
                        imp["name"],
                        len(imp["callers"]),
                        ", ".join("`%s`" % s for s in srcs) if srcs else "—",
                    )
                )
            w("")

    # Cross-program view: the same export reached from different source files in each
    # build is the interesting case, so keep it visible rather than buried per program.
    by_export = defaultdict(set)
    for rec in records:
        for imp in rec["imports"]:
            for c in imp["callers"]:
                src = attributed.get((rec["program"], c))
                if src:
                    by_export[(imp["library"], imp["name"])].add(src)
    if by_export:
        w("## Exports by source file, both programs pooled")
        w("")
        w("| Library | Export | Source files |")
        w("|---|---|---|")
        for (lib, name), srcs in sorted(by_export.items()):
            w(
                "| `%s` | `%s` | %s |"
                % (lib, name, ", ".join("`%s`" % s for s in sorted(srcs)))
            )
        w("")

    return "\n".join(out) + "\n"


# ------------------------------------------------------------------------------ checks


def selftest() -> int:
    import tempfile

    rec = {
        "program": "MissionMonet.exe",
        "imports": [
            {
                "library": "x3d.dll",
                "name": "X3d_Scene_Create_Light",
                "thunks": ["00401000"],
                "callers": ["0041a970", "00499999"],
            },
            {
                "library": "x3d.dll",
                "name": "X3d_Unused_Export",
                "thunks": ["00401004"],
                "callers": [],
            },
        ],
    }
    with tempfile.TemporaryDirectory() as tmp:
        scan_dir = Path(tmp) / "scan"
        notes = Path(tmp) / "notes"
        scan_dir.mkdir()
        notes.mkdir()
        (scan_dir / "MissionMonet.exe.imports.json").write_text(
            json.dumps(rec), encoding="utf-8"
        )
        with (notes / "function-map.csv").open("w", newline="", encoding="utf-8") as fh:
            wr = csv.writer(fh)
            wr.writerow(["address", "program", "source_file"])
            wr.writerow(["0041a970", "MissionMonet.exe", r"D:\M\Source\XScene.cpp"])
        stats = merge(scan_dir, notes)
        assert stats == {"records": 1, "imports": 2}, stats
        md = (notes / "import-map.md").read_text(encoding="utf-8")
        # 2 imports, 1 with a caller, 1 of those attributed to a source file.
        assert "| `x3d.dll` | 2 | 1 | 1 |" in md, md
        assert "`X3d_Scene_Create_Light` | 2 | `D:\\M\\Source\\XScene.cpp`" in md, md
        # An import with no caller must still be listed, with an em dash.
        assert "| `X3d_Unused_Export` | 0 | — |" in md, md
    print("selftest ok")
    return 0


def main(argv: list) -> int:
    if "--selftest" in argv:
        return selftest()
    if "--merge" in argv:
        i = argv.index("--merge")
        scan_dir = Path(argv[i + 1]) if len(argv) > i + 1 else Path("engines/x3d/notes/_assert_scan")
        notes = Path(__file__).resolve().parents[2] / "notes"
        stats = merge(scan_dir, notes)
        print(
            "merged %d program(s), %d engine-DLL imports -> %s"
            % (stats["records"], stats["imports"], notes / "import-map.md")
        )
        return 0
    print(__doc__)
    return 2


try:  # injected by Ghidra; absent under plain CPython
    currentProgram  # noqa: F821
except NameError:
    if __name__ == "__main__":
        sys.exit(main(sys.argv[1:]))
else:
    _args = getScriptArgs()  # noqa: F821
    _out = Path(_args[0]) if _args else Path("engines/x3d/notes/_assert_scan")
    scan(currentProgram, _out.resolve())  # noqa: F821
