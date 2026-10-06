# /// script
# requires-python = ">=3.11"
# dependencies = ["kaitaistruct>=0.11"]
# ///
"""Field-by-field difference between two files of a spec'd format, through its .ksy.

The save-file oracle: parse a save the original wrote and one our engine wrote at the same
point (or two original saves either side of an action) and see exactly which variables,
flags and inventory slots differ, instead of guessing from behaviour. Works for any format
with a .ksy (scenes, meshes, scripts), using the parser `tools/ksy_check.py` generates.

    uv run tools/structdiff.py x3d savegame A.bin B.bin --type anim_slot
    uv run tools/structdiff.py ring aqc a.aqc b.aqc
    uv run tools/structdiff.py --selftest

Prints one line per differing field path (`header.flags: 3 -> 7`, `objects[12].x: ...`), and
the count. Lists of different length show the length change and diff the common part.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KSC = REPO / "third_party" / "kaitai" / "kaitai-struct-compiler-0.11" / "bin" / "kaitai-struct-compiler.bat"


def load_class(engine: str, spec: str, type_name: str | None):
    ksy = REPO / "engines" / engine / "docs" / "formats" / f"{spec}.ksy"
    ident = re.search(r"^\s*id:\s*(\S+)", ksy.read_text(encoding="utf-8"), re.M).group(1)
    out = REPO / "build" / "ksy" / engine
    if not (out / f"{ident}.py").exists() or (out / f"{ident}.py").stat().st_mtime < ksy.stat().st_mtime:
        out.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(KSC), "-t", "python", "--outdir", str(out), str(ksy)], check=True, capture_output=True)
    sys.path.insert(0, str(out))
    s = importlib.util.spec_from_file_location(ident, out / f"{ident}.py")
    mod = importlib.util.module_from_spec(s)
    s.loader.exec_module(mod)
    cls = getattr(mod, camel(ident))
    return getattr(cls, camel(type_name)) if type_name else cls


def camel(name: str) -> str:
    return "".join(p.capitalize() for p in name.split("_"))


def fields(obj) -> dict:
    from kaitaistruct import KaitaiStruct

    if not isinstance(obj, KaitaiStruct):
        return obj
    return {k: v for k, v in vars(obj).items() if not k.startswith("_")}


def diff(a, b, path: str, out: list[str]) -> None:
    from kaitaistruct import KaitaiStruct

    if isinstance(a, KaitaiStruct) and isinstance(b, KaitaiStruct):
        fa, fb = fields(a), fields(b)
        for k in dict.fromkeys(list(fa) + list(fb)):
            diff(fa.get(k), fb.get(k), f"{path}.{k}" if path else k, out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: {len(a)} -> {len(b)} entries")
        for i, (x, y) in enumerate(zip(a, b)):
            diff(x, y, f"{path}[{i}]", out)
    elif a != b:
        show = lambda v: (v.hex(" ")[:48] + ("..." if len(v) > 16 else "")) if isinstance(v, bytes) else repr(v)
        out.append(f"{path}: {show(a)} -> {show(b)}")


def parse(cls, path: str):
    from kaitaistruct import KaitaiStream

    with open(path, "rb") as f:
        return cls(KaitaiStream(f))


def run(engine: str, spec: str, a: str, b: str, type_name: str | None) -> int:
    cls = load_class(engine, spec, type_name)
    out: list[str] = []
    diff(parse(cls, a), parse(cls, b), "", out)
    print("\n".join(out[:200]) + (f"\n... {len(out) - 200} more" if len(out) > 200 else ""))
    print(f"{len(out)} differing fields")
    return 0


def selftest() -> None:
    files = sorted((REPO / "games" / "ring" / "discs").rglob("*.aqc"))[:2]
    assert len(files) == 2, "needs two Ring .aqc files"
    cls = load_class("ring", "aqc", None)
    out: list[str] = []
    diff(parse(cls, str(files[0])), parse(cls, str(files[0])), "", out)
    assert out == [], out
    diff(parse(cls, str(files[0])), parse(cls, str(files[1])), "", out)
    assert out, "two different files should differ"
    print(f"structdiff selftest ok ({len(out)} fields differ between two .aqc files)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--selftest"]:
        selftest()
        sys.exit(0)
    t = None
    if "--type" in args:
        t = args[args.index("--type") + 1]
        args = args[:args.index("--type")] + args[args.index("--type") + 2:]
    if len(args) != 4:
        print(__doc__)
        sys.exit(2)
    sys.exit(run(*args, t))
