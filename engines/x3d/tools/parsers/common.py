"""Binary parsing helpers for X3D format specs.

Two things this exists for, both from CLAUDE.md rule 2:

  * every read is bounds-checked, so a bad spec fails loudly at a known offset instead of
    silently returning garbage;
  * a parser is not done until it consumes every byte of every file in the corpus, so
    `Reader.expect_eof()` is a hard assertion, not a warning.

Usage:

    from common import Reader, ParseError, run_corpus

    def parse(data: bytes):
        r = Reader(data)
        magic = r.magic(b"4X3D")
        count = r.u32()
        items = [r.f32() for _ in range(count)]
        r.expect_eof()
        return {"magic": magic, "items": items}

    if __name__ == "__main__":
        raise SystemExit(main_for(parse, "**/*.O3D", "O3D validator"))
"""

from __future__ import annotations

import argparse
import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


class ParseError(Exception):
    """Raised at a known offset. Always carries where it happened."""

    def __init__(self, message: str, offset: int):
        super().__init__(f"{message} (at offset 0x{offset:08x} / {offset})")
        self.offset = offset
        self.message = message


class Reader:
    """Sequential little-endian reader over a bytes buffer.

    Every method raises ParseError rather than returning short data, and the offset in the
    message is the offset the failing read *started* at.
    """

    def __init__(self, data: bytes, offset: int = 0, name: str = "<buffer>"):
        self.data = data
        self.pos = offset
        self.name = name

    # --- position -------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.data)

    @property
    def remaining(self) -> int:
        return len(self.data) - self.pos

    def seek(self, offset: int) -> None:
        if not 0 <= offset <= len(self.data):
            raise ParseError(f"seek past end of {self.name} ({len(self.data)} bytes)", offset)
        self.pos = offset

    def skip(self, count: int) -> None:
        self._check(count)
        self.pos += count

    def eof(self) -> bool:
        return self.pos >= len(self.data)

    def expect_eof(self) -> None:
        """The 'must consume all bytes' assertion. Call it at the end of every parser."""
        if self.remaining:
            tail = self.data[self.pos : self.pos + 32]
            raise ParseError(
                f"{self.remaining} unconsumed byte(s), next 32: {tail.hex(' ')}", self.pos
            )

    def _check(self, count: int) -> None:
        if count < 0:
            raise ParseError(f"negative read size {count}", self.pos)
        if self.pos + count > len(self.data):
            raise ParseError(
                f"read of {count} byte(s) overruns {self.name}"
                f" ({self.remaining} remaining of {len(self.data)})",
                self.pos,
            )

    # --- primitives -----------------------------------------------------------

    def bytes(self, count: int) -> bytes:
        self._check(count)
        out = self.data[self.pos : self.pos + count]
        self.pos += count
        return out

    def _unpack(self, fmt: str, size: int):
        start = self.pos
        self._check(size)
        (value,) = struct.unpack_from(fmt, self.data, start)
        self.pos += size
        return value

    def u8(self) -> int:
        return self._unpack("<B", 1)

    def i8(self) -> int:
        return self._unpack("<b", 1)

    def u16(self) -> int:
        return self._unpack("<H", 2)

    def i16(self) -> int:
        return self._unpack("<h", 2)

    def u32(self) -> int:
        return self._unpack("<I", 4)

    def i32(self) -> int:
        return self._unpack("<i", 4)

    def f32(self) -> float:
        return self._unpack("<f", 4)

    def array(self, fmt: str, count: int) -> tuple:
        """Bulk read, e.g. array('f', 3) for a vec3. Much faster than a loop."""
        size = struct.calcsize("<" + fmt) * count
        start = self.pos
        self._check(size)
        out = struct.unpack_from(f"<{count}{fmt}", self.data, start)
        self.pos += size
        return out

    # --- strings --------------------------------------------------------------

    def magic(self, expected: bytes) -> bytes:
        start = self.pos
        got = self.bytes(len(expected))
        if got != expected:
            raise ParseError(f"expected magic {expected!r}, got {got!r}", start)
        return got

    def fixed_str(self, count: int, encoding: str = "cp1252") -> str:
        """Fixed-width, NUL-padded. The game is French, so cp1252 rather than ascii."""
        raw = self.bytes(count)
        return raw.split(b"\0", 1)[0].decode(encoding, errors="replace")

    def cstr(self, encoding: str = "cp1252") -> str:
        start = self.pos
        end = self.data.find(b"\0", self.pos)
        if end < 0:
            raise ParseError("unterminated C string", start)
        out = self.data[self.pos : end].decode(encoding, errors="replace")
        self.pos = end + 1
        return out

    # --- validation -----------------------------------------------------------

    def check(self, condition: bool, message: str, offset: int | None = None) -> None:
        if not condition:
            raise ParseError(message, self.pos if offset is None else offset)

    def index(self, value: int, limit: int, what: str) -> int:
        """Bounds-check an index read out of the file. Out-of-range indices are the most
        common sign a struct layout is wrong, so they must fail, never clamp."""
        if not 0 <= value < limit:
            raise ParseError(f"{what} index {value} out of range [0, {limit})", self.pos)
        return value


# --- corpus harness -----------------------------------------------------------


@dataclass
class FileResult:
    path: Path
    ok: bool
    size: int
    error: str = ""
    offset: int = -1


@dataclass
class CorpusResult:
    results: list[FileResult]

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.ok)

    @property
    def failed(self) -> list[FileResult]:
        return [r for r in self.results if not r.ok]

    @property
    def complete(self) -> bool:
        """CLAUDE.md rule 2: anything short of 100% means the spec is not done."""
        return self.total > 0 and not self.failed


def find_files(root: Path, pattern: str) -> list[Path]:
    """Glob the corpus, case-insensitively.

    The corpus mixes casing freely (U01.X3D, Info.bin, App.bin), and NTFS will happily
    hand back either, so match on the lowercased suffix rather than trusting the pattern.
    """
    suffix = "." + pattern.rsplit(".", 1)[-1].lower() if "." in pattern else None
    out = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.match(pattern) or (suffix and path.suffix.lower() == suffix):
            out.append(path)
    return sorted(out)


def run_corpus(
    parser: Callable[[bytes], object],
    pattern: str,
    root: Path | None = None,
    verbose: bool = False,
    max_failures_shown: int = 25,
) -> CorpusResult:
    """Run `parser` over every corpus file matching `pattern`; print a pass/fail report.

    Returns a CorpusResult; the caller decides the exit code, so this stays usable from a
    pre-commit hook and from a REPL.
    """
    root = Path(root) if root else default_root()
    results: list[FileResult] = []

    for path in find_files(root, pattern):
        data = path.read_bytes()
        try:
            parser(data)
        except ParseError as exc:
            results.append(FileResult(path, False, len(data), exc.message, exc.offset))
        except Exception as exc:  # noqa: BLE001 - a spec bug is still a failure to report
            results.append(FileResult(path, False, len(data), f"{type(exc).__name__}: {exc}", -1))
        else:
            results.append(FileResult(path, True, len(data)))

    out = CorpusResult(results)
    _report(out, pattern, root, verbose, max_failures_shown)
    return out


def _report(result: CorpusResult, pattern: str, root: Path, verbose: bool, limit: int) -> None:
    print(f"corpus: {root}")
    print(f"pattern: {pattern}")
    print(f"files: {result.total}  passed: {result.passed}  failed: {len(result.failed)}")

    if result.total == 0:
        print("NO FILES MATCHED - check the root and the pattern")
        return

    for r in result.failed[:limit]:
        where = f"0x{r.offset:08x}" if r.offset >= 0 else "unknown offset"
        print(f"  FAIL {r.path}  [{r.size} bytes]  {where}: {r.error}")
    if len(result.failed) > limit:
        print(f"  ... and {len(result.failed) - limit} more failures")

    if verbose:
        for r in result.results:
            if r.ok:
                print(f"  ok   {r.path}  [{r.size} bytes]")

    print("100% of corpus parsed" if result.complete else "SPEC INCOMPLETE")


def default_root() -> Path:
    """Data root, overridable with --root or MONET_DATA_ROOT.

    Repo-relative default so parsers run with no arguments; the extracted CD image is
    checked in next to the tools. Treat it as read-only (CLAUDE.md rule 7).
    """
    env = os.environ.get("MONET_DATA_ROOT")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[4] / "games/monet/discs/cd" / "Data"


def corpus_argparser(description: str) -> argparse.ArgumentParser:
    """Shared CLI for parser modules."""
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("--root", type=Path, default=None, help="data root (default: CD image)")
    ap.add_argument("-v", "--verbose", action="store_true", help="list passing files too")
    ap.add_argument("--file", type=Path, default=None, help="parse one file and stop")
    return ap


def main_for(parser: Callable[[bytes], object], pattern: str, description: str) -> int:
    """Boilerplate `if __name__ == '__main__'` body for a parser module."""
    args = corpus_argparser(description).parse_args()
    if args.file:
        parser(args.file.read_bytes())
        print(f"ok {args.file}")
        return 0
    return 0 if run_corpus(parser, pattern, args.root, args.verbose).complete else 1


# --- self-check ---------------------------------------------------------------


def _selftest() -> None:
    r = Reader(struct.pack("<4sIf", b"4X3D", 2, 1.5))
    assert r.magic(b"4X3D") == b"4X3D"
    assert r.u32() == 2
    assert abs(r.f32() - 1.5) < 1e-6
    r.expect_eof()

    # an overrun reports the offset the read started at, not where it ended
    r = Reader(b"\x01\x02\x03")
    r.u16()
    try:
        r.u32()
    except ParseError as exc:
        assert exc.offset == 2, exc.offset
    else:
        raise AssertionError("overrun not detected")

    # trailing bytes are a failure, not a warning
    r = Reader(b"\x00\x00\x00\x00\xff")
    r.u32()
    try:
        r.expect_eof()
    except ParseError as exc:
        assert exc.offset == 4 and "unconsumed" in exc.message
    else:
        raise AssertionError("trailing bytes not detected")

    for thunk in (
        lambda: Reader(b"XXXX").magic(b"4X3D"),
        lambda: Reader(b"").index(7, 3, "vertex"),
        lambda: Reader(b"abc").cstr(),
        lambda: Reader(b"ab").skip(5),
        lambda: Reader(b"ab").seek(9),
    ):
        try:
            thunk()
        except ParseError:
            pass
        else:
            raise AssertionError("expected ParseError")

    r = Reader(b"hello\0world\0")
    assert r.cstr() == "hello" and r.cstr() == "world"
    r.expect_eof()

    assert Reader(struct.pack("<3f", 1, 2, 3)).array("f", 3) == (1.0, 2.0, 3.0)
    assert Reader(b"name\0\0\0\0").fixed_str(8) == "name"

    # the harness collects failures rather than raising them
    res = CorpusResult([FileResult(Path("a"), True, 1), FileResult(Path("b"), False, 1)])
    assert res.total == 2 and res.passed == 1 and not res.complete
    assert not CorpusResult([]).complete

    print("common.py selftest ok")


if __name__ == "__main__":
    _selftest()
    sys.exit(0)
