"""What is this file, and does anyone already know its format? Run before reverse engineering.

On a file: Detect It Easy (compiler, packer, protection, installer for executables), TrID
(file type from ~18,000 signatures), the first bytes, entropy (above ~7.5 bits/byte means
compressed or encrypted), then the reference index (tools/ref.py) searched for what was
found, including whether ScummVM already has a decoder for it.

On a folder (a game's disc or install): one row per extension with count, size, TrID's
guess, magic bytes and entropy of a sample, and the best reference hit, as a markdown
table: the corpus triage for a new game.

    python tools/identify.py games/grumpa/discs/cab/Movies_Danish/grumpa_intro.mpg
    python tools/identify.py games/atlantis-2/discs/cd1 > engines/<engine>/notes/corpus-triage.md
    python tools/identify.py --selftest
"""

from __future__ import annotations

import math
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TP = REPO / "third_party"
DIEC = TP / "die" / "die" / "diec.exe"
TRID = TP / "trid" / "trid.exe"
TRID_DEFS = TP / "trid" / "triddefs.trd"
EXE_EXT = {".exe", ".dll", ".ocx", ".drv", ".sys", ".bpl", ".cpl", ".scr", ".ex_", ".dl_"}

sys.path.insert(0, str(REPO / "tools"))
import ref  # noqa: E402


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    return -sum(c / len(data) * math.log2(c / len(data)) for c in counts if c)


def head(path: Path, n: int = 16) -> str:
    data = path.read_bytes()[:n]
    return data.hex(" ") + "  " + "".join(chr(b) if 32 <= b < 127 else "." for b in data)


def trid(path: Path, top: int = 3) -> list[str]:
    try:
        out = subprocess.run([str(TRID), f"-d:{TRID_DEFS}", f"-n:{top}", str(path)], capture_output=True,
                             text=True, timeout=60).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [l.strip() for l in out.splitlines() if re.match(r"\s*\d+\.\d+%", l)]


def die(path: Path) -> list[str]:
    try:
        out = subprocess.run([str(DIEC), str(path)], capture_output=True, text=True, timeout=120).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [l.strip() for l in out.splitlines() if l.strip()]


def guess_terms(trid_lines: list[str], ext: str) -> str:
    for l in trid_lines:  # "100.0% (.MPG/MPEG) MPEG video (4000/1)" -> "MPEG video"
        m = re.match(r"\s*[\d.]+% \([^)]*\) (.+?) \(\d+/", l)
        if m:
            return m.group(1)
    return f"{ext.lstrip('.')} file format"


def one_file(path: Path) -> None:
    data = path.read_bytes()[: 1 << 20]
    print(f"# {path.name} ({path.stat().st_size:,} bytes)")
    print(f"first bytes: {head(path)}")
    print(f"entropy (first MB): {entropy(data):.2f} bits/byte")
    t = trid(path)
    print("TrID:", *(t or ["no match"]), sep="\n  ")
    if path.suffix.lower() in EXE_EXT or data[:2] == b"MZ":
        print("Detect It Easy:", *die(path), sep="\n  ")
    terms = guess_terms(t, path.suffix)
    print(f"ScummVM code for '{terms}' (reuse before writing a decoder):")
    for source, p, title, snip in ref.search(terms, 3, "scummvm-src") or [("", "", "nothing found", "")]:
        print(f"  {title} - {p}")
    print(f"reference hits for '{terms}':")
    for source, p, title, snip in ref.search(terms, 5):
        print(f"  [{source}] {title} - {p}")


def folder(root: Path) -> None:
    groups = defaultdict(list)
    for p in root.rglob("*"):
        if p.is_file():
            groups[p.suffix.lower() or "(none)"].append(p)
    print(f"# Corpus triage: {root}\n")
    print(f"{sum(len(v) for v in groups.values())} files, {len(groups)} extensions.\n")
    print("| ext | files | total | TrID (sample) | first bytes | entropy | best reference |")
    print("|---|---|---|---|---|---|---|")
    for ext, files in sorted(groups.items(), key=lambda kv: -sum(f.stat().st_size for f in kv[1])):
        sample = max(files, key=lambda f: f.stat().st_size)
        size = sum(f.stat().st_size for f in files)
        t = trid(sample, 1)
        terms = guess_terms(t, ext)
        hit = ref.search(terms, 1)
        hit_s = f"[{hit[0][0]}] {hit[0][2]}" if hit else ""
        trid_s = re.sub(r"\s*\(\d+/\d+(/\d+)?\)$", "", t[0]) if t else "?"
        print(f"| {ext} | {len(files)} | {size / 1e6:.1f} MB | {trid_s} | `{sample.read_bytes()[:8].hex(' ')}` | "
              f"{entropy(sample.read_bytes()[: 1 << 20]):.1f} | {hit_s} |")


def selftest() -> None:
    assert entropy(b"\x00" * 64) == 0.0 and abs(entropy(bytes(range(256))) - 8.0) < 1e-9
    assert guess_terms(["100.0% (.MPG/MPEG) MPEG video (4000/1)"], ".mpg") == "MPEG video"
    assert guess_terms([], ".abi") == "abi file format"
    print("identify selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif len(sys.argv) == 2 and Path(sys.argv[1]).is_dir():
        folder(Path(sys.argv[1]))
    elif len(sys.argv) == 2 and Path(sys.argv[1]).is_file():
        one_file(Path(sys.argv[1]))
    else:
        print(__doc__)
        sys.exit(2)
