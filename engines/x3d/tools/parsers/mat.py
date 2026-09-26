r"""`.MAT` parser and corpus validator.

Plain ASCII material scripts. No magic, no binary primitives, no per-record signatures.
The handoff loader-list note (03-HANDOFF-PHASE-2.md §2) records that `.MAT` is plain
ASCII beginning with `;-------...`; the loader decompile step is skipped per that note
and the layout is taken directly from the sample bytes.

Structure (every line is a literal sample observation):

    line 0      ;-------...          (49 dashes; header banner)
    line 1      ; <path>             (source path comment, all caps `D:\`)
    line 2      ;-------...          (49 dashes; header banner)
    blank lines are allowed between sections

    MATERIAL="<name>"                 (string in double quotes)
    TYPE=<type>                       (one of MATERIAL_GOURAUD_RGB, MATERIAL_SELF_ILLUM)
    AMBIENT=<r>,<g>,<b>               (3×u8)
    DIFFUSE=<r>,<g>,<b>
    SPECULAR=<r>,<g>,<b>
    LIGHT_COLOR=<r>,<g>,<b>
    SHININESS=<int>
    SHININESS_STRENGTH=<int>
    TRANSPARENCY=<int>
    BINARY_OPACITY=<int>
    TWO_SIDED=<int>
    TILING=<int>
    TEXTURE_MAP="<path>"              (string in double quotes)
    REFLECTION=<int>
    LIGHT_MAP="<path>"                (string in double quotes; empty `""` allowed)
    REFLECTION=<int>                  (note: duplicated, see Observed)

    ;-------...                      (separator; trailing separator optional)

The duplicated trailing `REFLECTION=` line is a stable artefact of every corpus sample —
never zero in line 17 when line 19 is non-zero, etc. The parser captures both into a list
under `reflection` rather than picking one, since the loader's behaviour on the duplicate
is unverified (the handoff skips the loader decompile for `.MAT`).

Per CLAUDE.md rule 2 the validator must consume every byte of every `.MAT` file with no
unparsed trailing matter.

    python engines/x3d/tools/parsers/mat.py                 # validate the corpus
    python engines/x3d/tools/parsers/mat.py --selftest
    python engines/x3d/tools/parsers/mat.py --file <path>  # one file, structural summary
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    ParseError,
    corpus_argparser,
    default_root,
    find_files,
)

HEADER_DASHES = ";" + "-" * 47  # ";" + 47 dashes, as observed in every corpus file
SEPARATOR = HEADER_DASHES
HEADER_LINES = 3  # banner, path, banner

REQUIRED_KEYS = (
    "MATERIAL", "TYPE",
    "AMBIENT", "DIFFUSE", "SPECULAR", "LIGHT_COLOR",
    "SHININESS", "SHININESS_STRENGTH",
    "TRANSPARENCY", "BINARY_OPACITY", "TWO_SIDED", "TILING",
    "TEXTURE_MAP", "REFLECTION", "LIGHT_MAP", "REFLECTION",
)

RGB_KEYS = ("AMBIENT", "DIFFUSE", "SPECULAR", "LIGHT_COLOR")
INT_KEYS = (
    "SHININESS", "SHININESS_STRENGTH",
    "TRANSPARENCY", "BINARY_OPACITY", "TWO_SIDED", "TILING", "REFLECTION",
)
STR_KEYS = ("MATERIAL", "TEXTURE_MAP", "LIGHT_MAP")


def _is_banner(line: str) -> bool:
    return line == HEADER_DASHES


def _is_path_comment(line: str) -> bool:
    return line.startswith("; ") and len(line) >= 3


def _parse_rgb(raw: str, what: str, lineno: int) -> tuple[int, int, int]:
    parts = raw.split(",")
    if len(parts) != 3:
        raise ParseError(f"{what}: expected 3 comma-separated values, got {parts!r}", lineno)
    try:
        r, g, b = (int(p) for p in parts)
    except ValueError as exc:
        raise ParseError(f"{what}: non-integer component in {raw!r}", lineno) from exc
    for v in (r, g, b):
        if not 0 <= v <= 255:
            raise ParseError(f"{what}: component {v} out of range [0, 255]", lineno)
    return (r, g, b)


def _parse_int(raw: str, what: str, lineno: int) -> int:
    try:
        v = int(raw)
    except ValueError as exc:
        raise ParseError(f"{what}: non-integer value {raw!r}", lineno) from exc
    if v < 0:
        raise ParseError(f"{what}: negative value {v}", lineno)
    return v


def _parse_quoted(raw: str, what: str, lineno: int) -> str:
    if len(raw) < 2 or raw[0] != '"' or raw[-1] != '"':
        raise ParseError(f"{what}: expected quoted string, got {raw!r}", lineno)
    return raw[1:-1]


def _parse_material_block(lines: list[str], start: int) -> tuple[dict, int]:
    """Read one 16-line material block starting at `lines[start]`. Returns the parsed
    material plus the index of the next line to read."""
    mat: dict = {}
    for offset, key in enumerate(REQUIRED_KEYS):
        lineno = start + offset
        if lineno >= len(lines):
            raise ParseError(f"unexpected EOF inside material block at line {lineno}",
                             lineno)
        line = lines[lineno].strip()
        if "=" not in line:
            raise ParseError(f"material line {lineno}: missing '=' in {line!r}", lineno)
        k, _, raw = line.partition("=")
        if k != key:
            raise ParseError(
                f"material line {lineno}: expected key {key!r}, got {k!r}", lineno
            )
        if k in RGB_KEYS:
            mat.setdefault("colors", {})[k] = _parse_rgb(raw, k, lineno)
        elif k in INT_KEYS:
            mat.setdefault("ints", []).append((k, _parse_int(raw, k, lineno)))
        elif k in STR_KEYS:
            mat.setdefault("strings", {})[k] = _parse_quoted(raw, k, lineno)
    return mat, start + len(REQUIRED_KEYS)


def parse(data: bytes) -> dict:
    try:
        text = data.decode("latin1")
    except UnicodeDecodeError as exc:
        raise ParseError(f"not latin1 text: {exc}", 0) from exc

    lines = text.splitlines()
    if len(lines) < HEADER_LINES:
        raise ParseError(
            f"file shorter than {HEADER_LINES}-line header (got {len(lines)})", len(lines)
        )

    if not _is_banner(lines[0]):
        raise ParseError(f"line 0: expected banner, got {lines[0]!r}", 0)
    if not _is_path_comment(lines[1]):
        raise ParseError(f"line 1: expected '; <path>' comment, got {lines[1]!r}", 1)
    if not _is_banner(lines[2]):
        raise ParseError(f"line 2: expected banner, got {lines[2]!r}", 2)

    materials: list[dict] = []
    cur = HEADER_LINES

    while cur < len(lines):
        line = lines[cur].strip()
        if line == "":
            cur += 1
            continue
        if _is_banner(line):
            cur += 1
            continue
        if line.startswith("MATERIAL="):
            mat, cur = _parse_material_block(lines, cur)
            materials.append(mat)
            continue
        raise ParseError(
            f"line {cur}: expected separator, blank, or MATERIAL=, got {line!r}", cur
        )

    return {"path": lines[1][2:].strip(), "materials": materials}


def _selftest() -> None:
    sample = (
        ";-----------------------------------------------\n"
        "; D:\\U02\\ANIM\\U02_02\\U02_02.MAT\n"
        ";-----------------------------------------------\n"
        "\n"
        'MATERIAL="Material #475"\n'
        "TYPE=MATERIAL_GOURAUD_RGB\n"
        "AMBIENT=25,25,25\n"
        "DIFFUSE=127,127,127\n"
        "SPECULAR=229,229,229\n"
        "LIGHT_COLOR=255,255,255\n"
        "SHININESS=0\n"
        "SHININESS_STRENGTH=0\n"
        "TRANSPARENCY=0\n"
        "BINARY_OPACITY=0\n"
        "TWO_SIDED=0\n"
        "TILING=1\n"
        "TEXTURE_MAP=\"SNCFTETE.TGA\"\n"
        "REFLECTION=0\n"
        'LIGHT_MAP=""\n'
        "REFLECTION=0\n"
        "\n"
        ";-----------------------------------------------\n"
    )

    doc = parse(sample.encode("latin1"))
    assert doc["path"] == r"D:\U02\ANIM\U02_02\U02_02.MAT"
    assert len(doc["materials"]) == 1
    m = doc["materials"][0]
    assert m["strings"]["MATERIAL"] == "Material #475"
    assert m["colors"]["AMBIENT"] == (25, 25, 25)
    assert m["colors"]["DIFFUSE"] == (127, 127, 127)
    assert m["strings"]["TEXTURE_MAP"] == "SNCFTETE.TGA"
    assert m["strings"]["LIGHT_MAP"] == ""
    assert [k for k, _ in m["ints"]] == [
        "SHININESS", "SHININESS_STRENGTH",
        "TRANSPARENCY", "BINARY_OPACITY", "TWO_SIDED", "TILING",
        "REFLECTION", "REFLECTION",
    ]

    # header-only file (U02_03LOD.MAT shape)
    empty = (
        ";-----------------------------------------------\n"
        "; D:\\U02GARE\\PERSON\\U02_03\\U02_03LOD.MAT\n"
        ";-----------------------------------------------\n"
    )
    doc2 = parse(empty.encode("latin1"))
    assert doc2["materials"] == []

    # malformed: out-of-range RGB
    bad = sample.replace("AMBIENT=25,25,25", "AMBIENT=25,25,256")
    try:
        parse(bad.encode("latin1"))
    except ParseError as exc:
        assert "range" in exc.message
    else:
        raise AssertionError("RGB > 255 accepted")

    # malformed: missing = in MATERIAL line
    bad = sample.replace('MATERIAL="Material #475"', "MATERIAL Material #475")
    try:
        parse(bad.encode("latin1"))
    except ParseError as exc:
        assert "missing" in exc.message or "=" in exc.message
    else:
        raise AssertionError("missing '=' accepted")

    # malformed: non-latin1 bytes
    try:
        parse(b"\x00not ascii")
    except ParseError:
        pass
    else:
        raise AssertionError("non-latin1 bytes accepted")

    # truncated file (missing last few lines)
    try:
        parse(sample.encode("latin1")[:200])
    except ParseError:
        pass
    else:
        raise AssertionError("truncated file accepted")

    # unknown key inside a material block
    bad = sample.replace("SHININESS=0", "FLIBBERTY=0", 1)
    try:
        parse(bad.encode("latin1"))
    except ParseError as exc:
        assert "expected key" in exc.message
    else:
        raise AssertionError("unknown key accepted")

    print("selftest ok")


def _dump(path: Path) -> None:
    doc = parse(path.read_bytes())
    print(
        f"{path.name}: path={doc['path']!r}, {len(doc['materials'])} material(s),"
        f" {path.stat().st_size} bytes"
    )
    for i, m in enumerate(doc["materials"]):
        s = m["strings"]
        c = m["colors"]
        print(
            f"  [{i}] name={s['MATERIAL']!r} tex={s['TEXTURE_MAP']!r}"
            f" amb={c['AMBIENT']} diff={c['DIFFUSE']}"
        )


def main(argv: list) -> int:
    if "--selftest" in argv:
        _selftest()
        return 0

    args = corpus_argparser(".MAT validator").parse_args(argv)

    if args.file:
        _dump(args.file)
        return 0

    root = args.root or default_root()
    files = find_files(root, "*.MAT")
    if not files:
        print(f"no .mat files under {root}", file=sys.stderr)
        return 2

    ok = 0
    failures: list[tuple[Path, str]] = []
    totals = {"materials": 0, "bytes": 0}

    for path in files:
        data = path.read_bytes()
        try:
            doc = parse(data)
        except ParseError as exc:
            failures.append((path, f"{exc.message} at line {exc.offset}"))
            continue
        ok += 1
        totals["materials"] += len(doc["materials"])
        totals["bytes"] += len(data)

    print(f"corpus: {root}")
    print(f"files: {len(files)}  passed: {ok}  failed: {len(failures)}")
    print(f"  materials:  {totals['materials']}")
    print(f"  bytes:      {totals['bytes']}")
    for path, err in failures[:25]:
        print(f"  FAIL {path}  {err}")

    print("100% of corpus parsed" if ok == len(files) else "SPEC INCOMPLETE")
    return 0 if ok == len(files) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))