"""Detection entries for ScummVM, computed the way its AdvancedDetector does (md5 of a
file's first 5000 bytes, plus the file size), for every edition or language folder we have.

Given one or more game folders (one per edition), it picks detection files that every
folder has, preferring files whose md5 tells the editions apart and small non-media files,
and prints an `AD_ENTRY<n>s(...)` per folder to paste into detection_tables.h, plus a
markdown table of the md5s for the engine's wiki page.

    python tools/detection_entry.py games/ring/discs/dvd-edition games/ring/discs/cd/disc1
    python tools/detection_entry.py games/grumpa/discs/cab --files Actors/Characters.abi,Actors/Items.abi
    python tools/detection_entry.py --selftest
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

MD5_BYTES = 5000
MEDIA = {".wav", ".mp3", ".ogg", ".avi", ".mpg", ".mpeg", ".mov", ".bik", ".smk", ".hnm",
         ".jpg", ".jpeg", ".png", ".bmp", ".tga", ".gif", ".dll", ".exe"}


def ad_md5(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.md5(f.read(MD5_BYTES)).hexdigest()


def files_of(root: Path) -> dict[str, Path]:
    return {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file()}


def pick(roots: list[Path], n: int = 2) -> list[str]:
    tables = [files_of(r) for r in roots]
    common = set(tables[0]).intersection(*tables[1:]) if tables else set()
    def score(rel: str) -> tuple:
        sums = {ad_md5(t[rel]) for t in tables}
        size = tables[0][rel].stat().st_size
        return (len(sums) < len(tables),                   # tells every edition apart first
                Path(rel).suffix.lower() in MEDIA,          # data files over media
                size < 1024 or size > 50_000_000,           # not tiny, not huge
                rel.count("/"), size)
    return sorted(common, key=score)[:n]


def entry(root: Path, rels: list[str]) -> str:
    parts = []
    for rel in rels:
        p = root / rel
        parts.append(f'"{rel}", "{ad_md5(p)}", {p.stat().st_size}')
    return f"AD_ENTRY{len(rels)}s({', '.join(parts)})"


def main(argv: list[str]) -> int:
    files = None
    if "--files" in argv:
        files = argv[argv.index("--files") + 1].split(",")
        argv = argv[:argv.index("--files")] + argv[argv.index("--files") + 2:]
    roots = [Path(a) for a in argv]
    if not roots or not all(r.is_dir() for r in roots):
        print(__doc__)
        return 2
    rels = files or pick(roots)
    if not rels:
        print("no file is common to all folders")
        return 1
    print("// detection_tables.h")
    for r in roots:
        print(f"// {r.as_posix()}\n{entry(r, rels)},")
    print("\n| Edition folder | File | md5 (first 5000 bytes) | Size |\n|---|---|---|---|")
    for r in roots:
        for rel in rels:
            p = r / rel
            print(f"| {r.as_posix()} | {rel} | {ad_md5(p)} | {p.stat().st_size} |")
    return 0


def selftest() -> None:
    import tempfile

    tmp = Path(tempfile.mkdtemp())
    for ed, content in (("en", b"A" * 6000), ("de", b"B" * 6000)):
        (tmp / ed / "data").mkdir(parents=True)
        (tmp / ed / "data" / "game.dat").write_bytes(content)
        (tmp / ed / "data" / "same.dat").write_bytes(b"S" * 2000)
        (tmp / ed / "intro.avi").write_bytes(b"V" * 5000)
    assert ad_md5(tmp / "en" / "data" / "game.dat") == hashlib.md5(b"A" * 5000).hexdigest()
    rels = pick([tmp / "en", tmp / "de"], 1)
    assert rels == ["data/game.dat"], rels                    # the one that tells editions apart
    assert entry(tmp / "en", rels) == f'AD_ENTRY1s("data/game.dat", "{hashlib.md5(b"A" * 5000).hexdigest()}", 6000)'
    print("detection_entry selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        sys.exit(main(sys.argv[1:]))
