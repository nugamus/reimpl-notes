"""Plain `.wav` files: RIFF WAVE, read by the engine through WINMM `mmio*` (imports,
E-0002). Spec: engines/ring/docs/formats/README.md "Plain WAV", E-0022.

    "RIFF" u32 size "WAVE", then chunks { char[4] id, u32 size, size bytes, pad to even }
    to the end of the RIFF size; a 'fmt ' chunk (PCM) and a 'data' chunk are required.

    python engines/ring/tools/parsers/wav.py            # corpus
    python engines/ring/tools/parsers/wav.py --selftest
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ParseError, Reader, main_for  # noqa: E402


def parse(data: bytes) -> dict:
    r = Reader(data)
    r.magic(b"RIFF")
    size = r.u32()
    r.magic(b"WAVE")
    r.check(size + 8 == len(data), f"RIFF size {size} + 8 != {len(data)}", 4)
    chunks, fmt = [], None
    while not r.eof():
        cid, csize = r.bytes(4), r.u32()
        body = r.bytes(csize)
        if csize % 2 and not r.eof():
            r.skip(1)
        if cid == b"fmt ":
            fmt = struct.unpack_from("<HHIIHH", body)
        chunks.append(cid.decode("latin1"))
    r.check(fmt is not None and fmt[0] == 1 and "data" in chunks, f"chunks {chunks}", 12)
    return {"channels": fmt[1], "rate": fmt[2], "bits": fmt[5], "chunks": chunks}


def selftest() -> None:
    fmt = struct.pack("<HHIIHH", 1, 1, 22050, 44100, 2, 16)
    body = b"WAVE" + b"fmt " + struct.pack("<I", 16) + fmt + b"data" + struct.pack("<I", 2) + b"\0\0"
    wav = b"RIFF" + struct.pack("<I", len(body)) + body
    assert parse(wav)["rate"] == 22050
    try:
        parse(wav + b"\0")
    except ParseError:
        pass
    else:
        raise AssertionError("trailing byte accepted")


if __name__ == "__main__":
    raise SystemExit(main_for(parse, "plain WAV validator", [".wav"], selftest=selftest))
