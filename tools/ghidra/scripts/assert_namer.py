"""Recover the original source-file layout of a binary from its assert strings.

Both EXEs are MSVC 6 debug builds, so every `MessageToUser` / assert site pushes the
literal source path and the literal line number. That is ground truth about which
compiled function came from which `.cpp` and roughly where in it — no guessing, no
decompilation.

Observed call shape (MissionMonet.exe, three sites referencing
`D:\\MissionD\\Source\\XScene.cpp` at 0x00441788):

    PUSH 0x46          ; line number
    PUSH 0x441788      ; -> "D:\\MissionD\\Source\\XScene.cpp"
    PUSH 0x3ed         ; message id
    MOV  ECX,EAX
    CALL 0x0042a200    ; MessageToUser

so the line number is the immediately preceding PUSH-immediate. Anything that does not
match that shape is recorded with a null line rather than guessed at.

Two modes, one file.

Scan one program (writes JSON, mutates the Ghidra database):

    /c/ghidra/support/analyzeHeadless.bat ghidra_projects Monet \\
        -process MissionMonet.exe -noanalysis \\
        -scriptPath tools/ghidra/scripts -postScript assert_namer.py engines/x3d/notes/_assert_scan

Merge every scanned program into the notes (plain CPython, no Ghidra):

    python tools/ghidra/scripts/assert_namer.py --merge engines/x3d/notes/_assert_scan

Self-check:

    python tools/ghidra/scripts/assert_namer.py --selftest
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# A source path as MSVC 6 bakes it into __FILE__: either absolute with a drive letter, or
# relative with at least one directory component. Deliberately generic — the 4X
# Technologies DLLs are a different vendor and need not use D:\MissionD\Source\.
SRC_RE = re.compile(
    r"^(?:[A-Za-z]:\\)?(?:[^\\/:*?\"<>|\r\n]+\\)+[^\\/:*?\"<>|\r\n]+\.(?:cpp|cxx|cc|c|hpp|h)$",
    re.IGNORECASE,
)

# Line numbers outside this range are not line numbers; MSVC pushes plenty of other
# immediates around a call site.
MAX_LINE = 200_000

CSV_COLUMNS = [
    "address",
    "program",
    "source_file",
    "min_line",
    "max_line",
    "assert_count",
    "size",
    "xref_count",
    "current_name",
]


# --------------------------------------------------------------------------- scan mode


def _stem(source_path: str) -> str:
    """`D:\\MissionD\\Source\\FrameWork Sources\\LSound.cpp` -> `LSound`."""
    leaf = source_path.replace("/", "\\").rsplit("\\", 1)[-1]
    return leaf.rsplit(".", 1)[0]


def _ns_name(stem: str) -> str:
    """Ghidra namespaces reject most punctuation; source stems are already close."""
    name = re.sub(r"[^A-Za-z0-9_]", "_", stem)
    return name if name and not name[0].isdigit() else "_" + name


def _push_scalar(ins) -> "int | None":
    """Value of a `PUSH <imm>`, else None."""
    if ins is None or ins.getMnemonicString().upper() != "PUSH":
        return None
    try:
        scalar = ins.getScalar(0)
    except Exception:
        return None
    return None if scalar is None else scalar.getUnsignedValue()


def scan(program, out_dir: Path) -> dict:
    """Walk the assert strings of one program, tag what they prove, return the record."""
    from ghidra.program.model.symbol import SourceType

    listing = program.getListing()
    ref_mgr = program.getReferenceManager()
    symbols = program.getSymbolTable()
    prog_name = program.getName()

    strings_found = []
    # function entry address -> {source_file: [line or None, ...]}
    per_func = defaultdict(lambda: defaultdict(list))
    func_objs = {}

    for data in listing.getDefinedData(True):
        if not data.hasStringValue():
            continue
        value = data.getValue()
        if value is None:
            continue
        text = str(value)
        if not SRC_RE.match(text):
            continue
        str_addr = data.getAddress()
        refs = list(ref_mgr.getReferencesTo(str_addr))
        strings_found.append(
            {"address": str(str_addr), "value": text, "xref_count": len(refs)}
        )
        for ref in refs:
            from_addr = ref.getFromAddress()
            func = listing.getFunctionContaining(from_addr)
            if func is None:
                continue
            entry = str(func.getEntryPoint())
            func_objs[entry] = func
            ins = listing.getInstructionAt(from_addr)
            line = _push_scalar(ins.getPrevious()) if ins is not None else None
            if line is not None and not (1 <= line <= MAX_LINE):
                line = None
            per_func[entry][text].append(line)

    single, multi = [], []
    for entry, by_file in sorted(per_func.items()):
        func = func_objs[entry]
        size = func.getBody().getNumAddresses()
        xrefs = ref_mgr.getReferenceCountTo(func.getEntryPoint())
        current_name = func.getName()
        assert_count = sum(len(v) for v in by_file.values())

        if len(by_file) > 1:
            # Shared helper or an inlined callee: attributing it to one .cpp would be a
            # guess, so comment it and leave the name and namespace alone.
            note = "; ".join(
                "%s:%s" % (f, sorted(x for x in lines if x is not None))
                for f, lines in sorted(by_file.items())
            )
            func.setComment("SRC (multiple): " + note)
            multi.append(
                {
                    "address": entry,
                    "program": prog_name,
                    "source_file": "; ".join(sorted(by_file)),
                    "min_line": None,
                    "max_line": None,
                    "assert_count": assert_count,
                    "size": size,
                    "xref_count": xrefs,
                    "current_name": current_name,
                    "files": {
                        f: sorted(x for x in l if x is not None)
                        for f, l in by_file.items()
                    },
                }
            )
            continue

        source_file, lines = next(iter(by_file.items()))
        known = sorted(x for x in lines if x is not None)
        stem = _stem(source_file)

        func.setComment(
            "SRC: "
            + "; ".join(
                "%s:%s" % (source_file, "?" if x is None else x) for x in lines
            )
        )

        ns_name = _ns_name(stem)
        try:
            ns = symbols.getNamespace(ns_name, None)
            if ns is None:
                ns = symbols.createNameSpace(None, ns_name, SourceType.ANALYSIS)
            func.getSymbol().setNamespace(ns)
        except Exception as exc:  # namespace collides with an existing symbol
            print("  namespace %s failed for %s: %s" % (ns_name, entry, exc))

        if current_name.startswith("FUN_") and known:
            new_name = "%s_%d" % (stem, known[0])
            try:
                func.setName(new_name, SourceType.ANALYSIS)
            except Exception:
                try:
                    func.setName("%s_%s" % (new_name, entry), SourceType.ANALYSIS)
                except Exception as exc:
                    print("  rename failed for %s: %s" % (entry, exc))

        single.append(
            {
                "address": entry,
                "program": prog_name,
                "source_file": source_file,
                "min_line": known[0] if known else None,
                "max_line": known[-1] if known else None,
                "assert_count": assert_count,
                "size": size,
                "xref_count": xrefs,
                "current_name": func.getName(),
            }
        )

    record = {
        "program": prog_name,
        "strings": sorted(strings_found, key=lambda s: s["value"]),
        "single": single,
        "multi": multi,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / (prog_name + ".json")).write_text(
        json.dumps(record, indent=2), encoding="utf-8"
    )
    print(
        "%s: %d source-path strings, %d single-file functions, %d multi-file functions"
        % (prog_name, len(strings_found), len(single), len(multi))
    )
    return record


# -------------------------------------------------------------------------- merge mode


def _sort_key(row: dict):
    return (row["min_line"] if row["min_line"] is not None else 1 << 30, row["address"])


def merge(scan_dir: Path, notes_dir: Path) -> dict:
    records = [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(scan_dir.glob("*.json"))
    ]
    single = [r for rec in records for r in rec["single"]]
    multi = [r for rec in records for r in rec["multi"]]

    notes_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(notes_dir / "function-map.csv", single)
    _write_csv(notes_dir / "function-map-multi.csv", multi)
    (notes_dir / "module-map.md").write_text(
        _render_module_map(records, single, multi), encoding="utf-8"
    )
    return {"records": len(records), "single": len(single), "multi": len(multi)}


def _write_csv(path: Path, rows: list) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in sorted(
            rows, key=lambda r: (r["program"], r["source_file"], _sort_key(r))
        ):
            writer.writerow(row)


def _render_module_map(records: list, single: list, multi: list) -> str:
    out: list = []
    w = out.append

    w("# Module map")
    w("")
    w(
        "Reconstructed from the assert strings of an MSVC 6 debug build: each function "
        "below references exactly one source path, and the line number is the immediate "
        "pushed just before the path pointer. Generated by "
        "`tools/ghidra/scripts/assert_namer.py`; regenerate rather than hand-edit."
    )
    w("")
    w("A `?` line number means the assert site did not match the expected push shape.")
    w("")

    w("## Coverage")
    w("")
    w("| Program | Source-path strings | Attributed functions | Multi-file functions |")
    w("|---|---:|---:|---:|")
    for rec in sorted(records, key=lambda r: r["program"]):
        w(
            "| `%s` | %d | %d | %d |"
            % (rec["program"], len(rec["strings"]), len(rec["single"]), len(rec["multi"]))
        )
    w("")

    by_file = defaultdict(list)
    for row in single:
        by_file[(row["program"], row["source_file"])].append(row)

    w("## Source files by attributed code size")
    w("")
    w("| Program | Source file | Functions | Bytes | Line span |")
    w("|---|---|---:|---:|---|")
    for (prog, src), rows in sorted(
        by_file.items(), key=lambda kv: -sum(r["size"] for r in kv[1])
    ):
        lines = [r["min_line"] for r in rows if r["min_line"] is not None]
        lines += [r["max_line"] for r in rows if r["max_line"] is not None]
        span = "%d-%d" % (min(lines), max(lines)) if lines else "?"
        w(
            "| `%s` | `%s` | %d | %s | %s |"
            % (prog, src, len(rows), format(sum(r["size"] for r in rows), ","), span)
        )
    w("")

    for (prog, src), rows in sorted(by_file.items()):
        w("## `%s` — `%s`" % (src, prog))
        w("")
        w("%d function(s), %s bytes." % (len(rows), format(sum(r["size"] for r in rows), ",")))
        w("")
        w("| Line | Address | Name | Bytes | Asserts | Xrefs |")
        w("|---:|---|---|---:|---:|---:|")
        for row in sorted(rows, key=_sort_key):
            lo, hi = row["min_line"], row["max_line"]
            line = "?" if lo is None else (str(lo) if lo == hi else "%d-%d" % (lo, hi))
            w(
                "| %s | `0x%s` | `%s` | %s | %d | %d |"
                % (
                    line,
                    row["address"],
                    row["current_name"],
                    format(row["size"], ","),
                    row["assert_count"],
                    row["xref_count"],
                )
            )
        w("")

    if multi:
        w("## Functions referencing more than one source file")
        w("")
        w(
            "Inlined callees or shared helpers. Not attributed to a single `.cpp`, not "
            "renamed, not put in a namespace."
        )
        w("")
        w("| Program | Address | Name | Bytes | Source files |")
        w("|---|---|---|---:|---|")
        for row in sorted(multi, key=lambda r: (r["program"], r["address"])):
            files = ", ".join("`%s`" % f for f in sorted(row.get("files", {})))
            w(
                "| `%s` | `0x%s` | `%s` | %s | %s |"
                % (
                    row["program"],
                    row["address"],
                    row["current_name"],
                    format(row["size"], ","),
                    files,
                )
            )
        w("")

    return "\n".join(out) + "\n"


# ------------------------------------------------------------------------------ checks


def selftest() -> int:
    assert SRC_RE.match(r"D:\MissionD\Source\XScene.cpp")
    assert SRC_RE.match(r"FrameWork Sources\MessageToUser.h")
    assert SRC_RE.match(r"D:\MissionD\Source\FrameWork Sources\LSoundManager.cpp")
    assert not SRC_RE.match("XScene.cpp"), "bare filename is not a path"
    assert not SRC_RE.match(r"Data\U01.X3D"), "not a source extension"
    assert not SRC_RE.match("D:\\MissionD\\Source\\"), "directory is not a file"

    assert _stem(r"D:\MissionD\Source\FrameWork Sources\LSound.cpp") == "LSound"
    assert _stem(r"FrameWork Sources\MessageToUser.h") == "MessageToUser"
    assert _ns_name("MessageToUser") == "MessageToUser"
    assert _ns_name("U04_03") == "U04_03"
    assert _ns_name("3dstuff") == "_3dstuff"

    import tempfile

    rec = {
        "program": "MissionMonet.exe",
        "strings": [
            {"address": "441788", "value": r"D:\M\Source\XScene.cpp", "xref_count": 2}
        ],
        "single": [
            {
                "address": "0041acf0",
                "program": "MissionMonet.exe",
                "source_file": r"D:\M\Source\XScene.cpp",
                "min_line": 124,
                "max_line": 124,
                "assert_count": 1,
                "size": 200,
                "xref_count": 3,
                "current_name": "XScene_124",
            },
            {
                "address": "0041a970",
                "program": "MissionMonet.exe",
                "source_file": r"D:\M\Source\XScene.cpp",
                "min_line": None,
                "max_line": None,
                "assert_count": 1,
                "size": 88,
                "xref_count": 1,
                "current_name": "FUN_0041a970",
            },
        ],
        "multi": [
            {
                "address": "0042a200",
                "program": "MissionMonet.exe",
                "source_file": "a.cpp; b.cpp",
                "min_line": None,
                "max_line": None,
                "assert_count": 2,
                "size": 40,
                "xref_count": 9,
                "current_name": "FUN_0042a200",
                "files": {"a.cpp": [1], "b.cpp": [2]},
            }
        ],
    }
    with tempfile.TemporaryDirectory() as tmp:
        scan_dir = Path(tmp) / "scan"
        notes = Path(tmp) / "notes"
        scan_dir.mkdir()
        (scan_dir / "MissionMonet.exe.json").write_text(
            json.dumps(rec), encoding="utf-8"
        )
        stats = merge(scan_dir, notes)
        assert stats == {"records": 1, "single": 2, "multi": 1}, stats
        rows = list(csv.DictReader((notes / "function-map.csv").open(encoding="utf-8")))
        assert [r["address"] for r in rows] == [
            "0041acf0",
            "0041a970",
        ], "known line numbers must sort before unknown"
        assert list(rows[0]) == CSV_COLUMNS
        md = (notes / "module-map.md").read_text(encoding="utf-8")
        assert "XScene.cpp" in md and "| ? |" in md and "more than one source file" in md
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
            "merged %d program(s): %d attributed, %d multi-file -> %s"
            % (stats["records"], stats["single"], stats["multi"], notes)
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
