"""Corpus harness for the Ring-engine format validators.

The byte reader is X3D's (`engines/x3d/tools/parsers/common.py`: bounds-checked reads,
`expect_eof()` as the "every byte consumed" assertion). What differs here is the corpus:
every edition of Ring and Prophet (engines/ring E-0001), and the members of every
`.at2`/`.at3` archive as well as loose files, because many types exist only inside archives.

Identical contents are parsed once; the report gives both counts.

    from common import Reader, ParseError, main_for
    raise SystemExit(main_for(parse, [".tga"], "TGA validator"))
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from pathlib import Path
from typing import Callable, Iterator

REPO = Path(__file__).resolve().parents[4]


def _x3d_common():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "x3d_common", REPO / "engines/x3d/tools/parsers/common.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["x3d_common"] = mod  # dataclasses in it look their module up
    spec.loader.exec_module(mod)
    return mod


ParseError = _x3d_common().ParseError
Reader = sys.modules["x3d_common"].Reader

ROOTS = {
    "ring/dvd": "games/ring/discs/dvd-edition",
    **{f"ring/cd{i}": f"games/ring/discs/cd-version/disc{i}" for i in range(1, 7)},
    **{f"ring/iso{i}": f"games/ring/discs/iso-version/disc{i}" for i in range(1, 5)},
    "prophet/cd1": "games/prophet-and-assassin/discs/cd1",
    "prophet/cd2": "games/prophet-and-assassin/discs/cd2",
}
ARCHIVE_EXTS = (".at2", ".at3")
SKIP_DIRS = {"directx", "crack"}  # redistributables; modified EXEs (never RE'd)


def loose_files(exts: tuple[str, ...]) -> Iterator[tuple[str, Path]]:
    for ed, rel in ROOTS.items():
        root = REPO / rel
        for p in sorted(root.rglob("*")):
            if p.is_file() and p.suffix.lower() in exts and not SKIP_DIRS & {
                x.lower() for x in p.relative_to(root).parts[:-1]}:
                yield f"{ed}:{p.relative_to(root).as_posix()}", p


def archive_members(data: bytes) -> list[tuple[str, int, int, int]]:
    """(name, offset, size, unpacked size) of each member; layout per at2.py."""
    count = struct.unpack_from("<I", data, 12)[0]
    out = []
    for i in range(count):
        o = 32 + 255 * i
        name = data[o:o + 243].split(b"\0", 1)[0].decode("cp1252")
        off, size, unpacked = struct.unpack_from("<III", data, o + 243)
        out.append((name, off, size, unpacked))
    return out


def corpus(loose: tuple[str, ...], members: tuple[str, ...] = (),
           archives: tuple[str, ...] = ARCHIVE_EXTS) -> Iterator[tuple[str, bytes]]:
    """(label, bytes) for every loose file with an extension in `loose` and every member
    with an extension in `members` of an archive with an extension in `archives`."""
    for label, p in loose_files(loose):
        yield label, p.read_bytes()
    if not members:
        return
    for label, p in loose_files(archives):
        data = p.read_bytes()
        for name, off, size, _ in archive_members(data):
            if Path(name).suffix.lower() in members:
                yield f"{label}{name}", data[off:off + size]


def run(parser: Callable[[bytes], object], loose: tuple[str, ...], members: tuple[str, ...] = (),
        archives: tuple[str, ...] = ARCHIVE_EXTS, not_this_type: dict[str, str] | None = None,
        limit: int = 25) -> bool:
    """Parse every distinct content once. `not_this_type` maps the MD5 of a file that only
    carries the extension (e.g. a misnamed text file) to the reason; those are counted and
    reported, not parsed."""
    not_this_type = not_this_type or {}
    seen: dict[str, str | None] = {}  # md5 -> error or None
    total = 0
    failures = []
    excluded = []
    for label, data in corpus(loose, members, archives):
        total += 1
        h = hashlib.md5(data).hexdigest()
        if h in not_this_type:
            excluded.append((label, not_this_type[h]))
            continue
        if h not in seen:
            try:
                parser(data)
                seen[h] = None
            except ParseError as exc:
                seen[h] = f"0x{exc.offset:08x}: {exc.message}"
            except Exception as exc:  # noqa: BLE001 - a spec bug is still a failure
                seen[h] = f"{type(exc).__name__}: {exc}"
        if seen[h]:
            failures.append((label, seen[h]))
    distinct = len(seen)
    bad = sum(1 for v in seen.values() if v)
    print(f"loose: {' '.join(loose) or '-'}  members: {' '.join(members) or '-'} "
          f"(of {' '.join(archives)})")
    print(f"files: {total}  not this type: {len(excluded)}  distinct parsed: {distinct}  "
          f"passed: {distinct - bad}  failed: {bad}")
    for label, why in excluded:
        print(f"  NOT THIS TYPE {label}: {why}")
    for label, err in failures[:limit]:
        print(f"  FAIL {label}  {err}")
    ok = total > 0 and bad == 0
    print("100% of corpus parsed" if ok else "SPEC INCOMPLETE")
    return ok


def main_for(parser: Callable[[bytes], object], description: str, loose: list[str],
             members: list[str] = (), archives: tuple[str, ...] = ARCHIVE_EXTS,
             selftest: Callable[[], None] | None = None,
             not_this_type: dict[str, str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("--file", type=Path, help="parse one file and print the result")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        if selftest is None:
            raise SystemExit("no selftest")
        selftest()
        print("selftest ok")
        return 0
    if args.file:
        print(parser(args.file.read_bytes()))
        return 0
    low = lambda xs: tuple(x.lower() for x in xs)  # noqa: E731
    return 0 if run(parser, low(loose), low(members), archives, not_this_type) else 1
