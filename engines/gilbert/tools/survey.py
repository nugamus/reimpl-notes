"""Survey the Gilbert corpus (engine `gilbert`).

Read-only over games/gilbert/discs/cd. Writes into engines/gilbert/notes/:

  binaries.md         every PE file: MD5, size, PE timestamp, linker, Rich header,
                      sections, imports, exports, compiler guess. Program/REDIST/ and the
                      Acrobat installer only counted; 16-bit NE files listed as such.
  corpus-inventory.md layout, then extension x magic counts.
  corpus-md5.tsv      path, size, MD5 of every file.
  exe-strings.md      what names the programs' origin: banners, build paths, data paths,
                      and which DirectX / DirectShow interfaces they reference
                      (Gilbert.exe, ge.dll, gempeg.dll).

    python engines/gilbert/tools/survey.py
    python engines/gilbert/tools/survey.py --selftest
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import re
import uuid
from collections import Counter, defaultdict
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[3]
NOTES = REPO / "engines/gilbert/notes"
ROOT = REPO / "games/gilbert/discs/cd"
EXES = [ROOT / "Program" / n for n in ("Gilbert.exe", "ge.dll", "gempeg.dll")]
PE_EXTS = {".exe", ".dll"}
REDIST_DIRS = {"redist", "acrobat reader eng"}
# COM class and interface IDs the programs could create or QueryInterface for.
IIDS = {
    "CLSID_DirectDraw": "D7B70EE0-4340-11CF-B063-0020AFC2CD35",
    "IID_IDirectDraw": "6C14DB80-A733-11CE-A521-0020AF0BE560",
    "IID_IDirectDraw2": "B3A6F3E0-2B43-11CF-A2DE-00AA00B93356",
    "IID_IDirectDraw4": "9C59509A-39BD-11D1-8C4A-00C04FD930C5",
    "IID_IDirectDrawSurface4": "0B2B8630-AD35-11D0-8EA6-00609797EA5B",
    "IID_IDirect3D": "3BBA0080-2421-11CF-A31A-00AA00B93356",
    "IID_IDirectSound": "279AFA83-4981-11CE-A521-0020AF0BE560",
    "IID_IDirectSoundBuffer": "279AFA85-4981-11CE-A521-0020AF0BE560",
    "IID_IDirectInput": "89521360-AA8A-11CF-BFC7-444553540000",
    "CLSID_FilterGraph": "E436EBB3-524F-11CE-9F53-0020AF0BA770",
    "IID_IGraphBuilder": "56A868A9-0AD4-11CE-B03A-0020AF0BA770",
    "IID_IMediaControl": "56A868B1-0AD4-11CE-B03A-0020AF0BA770",
    "IID_IAMMultiMediaStream": "BEBE595C-9A6F-11D0-8FDE-00C04FD9189D",
}
BANNER_RE = re.compile(
    rb"[\x20-\x7e]*(?:Delphi|DelphiX|Borland|Fantasy|Pir |\.pdb|\.pas|\.cpp|Copyright|\(C\))[\x20-\x7e]*")
PATH_RE = re.compile(rb"[\x20-\x7e]*(?:\\[A-Za-z!]{2,}|\.wxi|\.map|\.dat|\.mpg|\.wav|\.dxw|\.wxs|\.ini|\.txt)[\x20-\x7e]*", re.I)


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def magic(head: bytes) -> str:
    """First four bytes as text when printable, else hex."""
    m = head[:4]
    if len(m) == 4 and all(32 <= b < 127 for b in m):
        return "'" + m.decode() + "'"
    return m.hex()


def rich(pe) -> str:
    rh = pe.parse_rich_header()
    if not rh:
        return "none"
    v = rh["values"]
    return ", ".join(f"id {v[i] >> 16} build {v[i] & 0xFFFF} x{v[i + 1]}" for i in range(0, len(v), 2))


def pe_info(path: Path) -> dict | None:
    blob = path.read_bytes()
    if blob[:2] != b"MZ":
        return None
    try:
        pe = pefile.PE(data=blob)
    except pefile.PEFormatError:
        return {"kind": "NE"}  # 16-bit InstallShield stubs
    fh, oh = pe.FILE_HEADER, pe.OPTIONAL_HEADER
    secs = [s.Name.rstrip(b"\0").decode("latin1") for s in pe.sections]
    ts = fh.TimeDateStamp
    imports = []
    for d in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
        names = [(i.name or f"#{i.ordinal}".encode()).decode() for i in d.imports]
        imports.append((d.dll.decode(), names))
    exports = []
    if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
        exports = [(s.name or f"#{s.ordinal}".encode()).decode() for s in pe.DIRECTORY_ENTRY_EXPORT.symbols]
    linker = f"{oh.MajorLinkerVersion}.{oh.MinorLinkerVersion}"
    # Delphi's linker writes CODE/DATA/BSS sections and the fixed stamp 0x2a425e19.
    compiler = "Borland Delphi" if "CODE" in secs else "Microsoft"
    return {
        "kind": "DLL" if fh.Characteristics & 0x2000 else "EXE",
        "timestamp": f"0x{ts:08x} "
        + datetime.datetime.fromtimestamp(ts, datetime.UTC).strftime("%Y-%m-%d %H:%M:%S"),
        "compiler": f"{compiler}, linker {linker}",
        "rich": rich(pe),
        "sections": secs,
        "imports": imports,
        "exports": exports,
        "base": f"0x{oh.ImageBase:08x}",
        "entry": f"0x{oh.ImageBase + oh.AddressOfEntryPoint:08x}",
    }


def is_redist(rel: Path) -> bool:
    return any(p.lower() in REDIST_DIRS for p in rel.parts[:-1])


def survey() -> None:
    rows = []  # (rel, size, md5, magic, path)
    for path in sorted(p for p in ROOT.rglob("*") if p.is_file()):
        rel = path.relative_to(ROOT)
        with path.open("rb") as fh:
            head = fh.read(16)
        rows.append((rel, path.stat().st_size, md5(path), magic(head), path))
    NOTES.mkdir(parents=True, exist_ok=True)
    with (NOTES / "corpus-md5.tsv").open("w", encoding="utf-8", newline="\n") as out:
        out.write("path\tsize\tmd5\n")
        for rel, size, h, _, _ in rows:
            out.write(f"{rel.as_posix()}\t{size}\t{h}\n")
    write_binaries(rows)
    write_inventory(rows)
    write_exe_strings()


def write_binaries(rows) -> None:
    lines = ["# Binaries (Gilbert CD)", "",
             "Generated by `engines/gilbert/tools/survey.py`. Every PE file outside `Program/REDIST/`",
             "and the Acrobat installer (only counted).", ""]
    redist = 0
    for rel, size, h, _, path in rows:
        if path.suffix.lower() not in PE_EXTS:
            continue
        if is_redist(rel):
            redist += 1
            continue
        info = pe_info(path)
        if info is None:
            continue
        if info["kind"] == "NE":
            lines += [f"## `{rel.as_posix()}`", "", f"- {size:,} B, MD5 `{h}`, 16-bit NE executable", ""]
            continue
        lines += [f"## `{rel.as_posix()}`", "",
                  f"- {size:,} B, MD5 `{h}`, {info['kind']}, PE timestamp {info['timestamp']} UTC",
                  f"- {info['compiler']}; Rich header: {info['rich']}",
                  f"- image base {info['base']}, entry {info['entry']}; sections {' '.join(info['sections'])}",
                  "- imports:"]
        for dll, names in info["imports"]:
            lines.append(f"  - {dll} ({len(names)}): {' '.join(names)}")
        if info["exports"]:
            lines.append(f"- exports ({len(info['exports'])}): {' '.join(info['exports'])}")
        lines.append("")
    lines += [f"Redistributable PE files skipped: {redist}", ""]
    (NOTES / "binaries.md").write_text("\n".join(lines), encoding="utf-8")


def write_inventory(rows) -> None:
    sel = [r for r in rows if not is_redist(r[0])]
    lines = ["# Corpus inventory (Gilbert CD)", "",
             "Generated by `engines/gilbert/tools/survey.py`. Regenerate rather than hand-edit.",
             "Magic = first four bytes, quoted when printable, else hex. `Program/REDIST/` and the",
             "Acrobat installer excluded from the extension table.", "",
             f"Root `games/gilbert/discs/cd`: {len(rows):,} files, "
             f"{sum(r[1] for r in rows):,} bytes ({len(rows) - len(sel)} redistributable).", "",
             "Layout (files per directory, redistributables collapsed):", ""]
    dirs = Counter()
    for r in rows:
        parts = r[0].parts[:-1]
        if is_redist(r[0]):
            parts = parts[:next(i for i, p in enumerate(parts) if p.lower() in REDIST_DIRS) + 1]
        dirs["/".join(parts) or "."] += 1
    for d, n in sorted(dirs.items()):
        lines.append(f"- `{d}/` {n}")
    lines += ["", "| Ext | Files | Bytes | Magics (count) | Directories |", "|---|---:|---:|---|---|"]
    by_ext = defaultdict(list)
    for r in sel:
        by_ext[r[0].suffix.lower() or "(none)"].append(r)
    for ext, rs in sorted(by_ext.items(), key=lambda kv: -len(kv[1])):
        mags = Counter(r[3] for r in rs)
        top = ", ".join(f"`{m}` {n}" for m, n in mags.most_common(6))
        if len(mags) > 6:
            top += f", … {len(mags)} distinct"
        ds = sorted({"/".join(r[0].parts[:-1]) or "." for r in rs})
        dtxt = ", ".join(ds) if len(ds) <= 4 else f"{', '.join(ds[:3])}, … {len(ds)} directories"
        lines.append(f"| `{ext}` | {len(rs):,} | {sum(r[1] for r in rs):,} | {top} | {dtxt} |")
    (NOTES / "corpus-inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_exe_strings() -> None:
    lines = ["# Origin strings of `Gilbert.exe`, `ge.dll`, `gempeg.dll`", "",
             "Generated by `engines/gilbert/tools/survey.py`: banners, build paths, data paths,",
             "and a search for DirectX / DirectShow interface IDs (little-endian GUIDs).", ""]
    for exe in EXES:
        lines += exe_strings(exe)
    (NOTES / "exe-strings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def exe_strings(exe: Path) -> list[str]:
    blob = exe.read_bytes()
    lines = [f"## `{exe.name}`", "", "### Banners and build paths", ""]
    for m in BANNER_RE.finditer(blob):
        if len(m.group()) >= 8:
            lines.append(f"- 0x{m.start():06x}: `{m.group().decode('latin1')}`")
    lines += ["", "### DirectX and DirectShow interface IDs", "", "| ID | File offset |", "|---|---|"]
    for name, g in IIDS.items():
        i = blob.find(uuid.UUID(g).bytes_le)
        lines.append(f"| {name} | {'absent' if i < 0 else f'0x{i:06x}'} |")
    lines += ["", "### Data paths and extensions", ""]
    for m in PATH_RE.finditer(blob):
        if len(m.group()) >= 5:
            lines.append(f"- 0x{m.start():06x}: `{m.group().decode('latin1')}`")
    lines.append("")
    return lines


def selftest() -> None:
    assert magic(b"ML01....") == "'ML01'"
    assert magic(b"\xff\x0a\x00W") == "ff0a0057"
    assert is_redist(Path("Program/REDIST/DSETUP.DLL")) and not is_redist(Path("Program/ge.dll"))
    assert uuid.UUID(IIDS["IID_IDirectDraw2"]).bytes_le[:4] == bytes.fromhex("e0f3a6b3")
    print("selftest ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
    else:
        survey()
