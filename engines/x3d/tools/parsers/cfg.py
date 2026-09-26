"""`x3dcfg.cfg` parser and corpus validator. Spec: engines/x3d/docs/formats/cfg.ksy, E-0103.

No shipping binary reads these files: neither EXE nor any DLL contains the string `cfg`
except `MissionD.exe`'s unrelated `APP.CFG` (E-0103). They are left behind by the
authoring tools. Layout from the corpus alone:

    f32 unk_f[3]
    u32 unk_u[6]
    u32 path_count
    path_count x char[260]     MAX_PATH, NUL-padded ("D:\\MissionD\\Data\\U01\\maps")

    python engines/x3d/tools/parsers/cfg.py                 # validate the corpus
    python engines/x3d/tools/parsers/cfg.py --selftest
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ParseError, Reader, main_for  # noqa: E402

PATH_LEN = 260


def parse(data: bytes) -> dict:
    r = Reader(data)
    out = {"unk_f": r.array("f", 3), "unk_u": r.array("I", 6)}
    count = r.u32()
    out["paths"] = [r.fixed_str(PATH_LEN) for _ in range(count)]
    r.expect_eof()
    return out


def _selftest() -> None:
    path = b"D:\\MissionD\\Data\\U01\\maps".ljust(PATH_LEN, b"\0")
    blob = struct.pack("<3f6II", 0.4, 1.0, 1.0, 0, 0, 0, 0, 0, 1, 1) + path
    doc = parse(blob)
    assert doc["paths"] == ["D:\\MissionD\\Data\\U01\\maps"]
    assert doc["unk_f"][1] == 1.0 and doc["unk_u"][5] == 1
    for bad in (blob + b"\0", blob[:-1]):
        try:
            parse(bad)
        except ParseError:
            pass
        else:
            raise AssertionError("bad cfg accepted")
    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
        sys.exit(0)
    sys.exit(main_for(parse, "**/*.cfg", "x3dcfg.cfg validator"))
