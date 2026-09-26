"""Subtitles (`.dia`) and lip/animation timing (`.dan`). Spec: engines/ring/docs/formats/
README.md "Dialog text", E-0025.

`.dia` — `aDialog::ReadLyrics` (RING_DVD.EXE 0x427090) reads the first 0x1000 bytes, cuts
them at each '\\n' (blanking the byte before it: the '\\r', or, in files with bare '\\n',
the line's last character), and hands every complete line to
`aDialog::ParseLyricLine` (0x427550): spaces, a decimal time, optionally
",digits:digits.digits", spaces, then the text; '#' splits the text in two parts. Bytes
after the last '\\n' are never parsed (in the corpus: none, or the text of a last line).

`.dan` — `aDialog::ReadDialogAnimation` (0x4271b0): fscanf "%d" must match once, then
"%d %d %d" repeatedly until it does not match three.

    python engines/ring/tools/parsers/dia.py            # corpus (.dia and .dan)
    python engines/ring/tools/parsers/dia.py --selftest
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ParseError, main_for  # noqa: E402

LINE = re.compile(rb"^[ \t\x0b\x0c]*(\d+)(?:,(\d+):[ \t]*\d*\.\d*)?[ \t\x0b\x0c]*(.*)$", re.S)
SPACE = b" \t\r\n\x0b\x0c"


def parse_dia(data: bytes) -> dict:
    buf = data[:0x1000]
    lines, pos, lost = [], 0, []
    while True:
        nl = buf.find(b"\n", pos)
        if nl < 0:
            break
        line = buf[pos:nl]
        if line and not line.endswith(b"\r"):
            lost.append(line[-1:])  # the engine blanks the byte before '\n' regardless
        line = line[:-1]
        m = LINE.match(line)
        if not m:
            raise ParseError(f"not a lyric line: {line[:40]!r}", pos)
        text = m.group(3).split(b"#", 1)
        lines.append((int(m.group(1)), text))
        pos = nl + 1
    return {"lines": lines, "ignored_tail": data[pos:], "beyond_4k": len(data) > 0x1000,
            "lost_last_bytes": lost}


def parse_dan(data: bytes) -> dict:
    tokens = data.split()
    for i, t in enumerate(tokens):
        if not re.fullmatch(rb"-?\d+", t):
            raise ParseError(f"token {i} {t[:20]!r} is not an integer", data.find(t))
    if len(tokens) % 3 != 1:
        raise ParseError(f"{len(tokens)} integers: not 1 + 3n", len(data))
    return {"first": int(tokens[0]), "triples": (len(tokens) - 1) // 3}


def parse(data: bytes) -> dict:
    # A .dan starts with an integer line and has only integers; .dia lines carry text.
    if re.fullmatch(rb"[\s\d-]*", data):
        return parse_dan(data)
    return parse_dia(data)


def selftest() -> None:
    out = parse_dia(b" 0  Hello#World\r\n 2280  Bye\r\n 14403  END\r\n")
    assert out["lines"][0] == (0, [b"Hello", b"World"]) and out["ignored_tail"] == b""
    assert parse_dia(b"5000   END")["lines"] == []           # no '\n': nothing parsed
    assert parse_dan(b"1\r\n1 30101 0\r\n0 28 0\r\n")["triples"] == 2
    for bad in (b"1\r\n1 2\r\n", b"x 1\n"):
        try:
            parse_dan(bad) if b"x" not in bad else parse_dia(bad)
        except ParseError:
            continue
        raise AssertionError(f"accepted {bad!r}")


if __name__ == "__main__":
    raise SystemExit(main_for(parse, "DIA/DAN validator", [".dia", ".dan"], selftest=selftest))
