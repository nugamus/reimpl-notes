# /// script
# requires-python = ">=3.11"
# dependencies = ["kaitaistruct>=0.11"]
# ///
"""Check the .ksy format specs against the corpus, so specs and parsers can't drift apart.

Compiles every `engines/<engine>/docs/formats/*.ksy` with the Kaitai Struct compiler
(third_party/kaitai, Java) into `build/ksy/<engine>/`, then parses the corpus files whose
extension the spec declares (`meta: file-extension`) with the generated parser and checks
each one is read to its last byte. One line per spec: compiled or not, files parsed,
failures (first few named).

    uv run tools/ksy_check.py ring              # one engine
    uv run tools/ksy_check.py ring bma --max 0  # one spec, every file (default --max 200)
    uv run tools/ksy_check.py --all
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KSC = REPO / "third_party" / "kaitai" / "kaitai-struct-compiler-0.11" / "bin" / "kaitai-struct-compiler.bat"
GAMES = {"x3d": ["monet"], "peintre": ["mission-sunlight"], "ring": ["ring"],
         "gilbert": ["gilbert"], "grumpa": ["grumpa"]}


def meta(ksy: Path) -> tuple[str, list[str]]:
    text = ksy.read_text(encoding="utf-8")
    ident = re.search(r"^\s*id:\s*(\S+)", text, re.M).group(1)
    m = re.search(r"file-extension:\s*(\[[^\]]*\]|\S+)", text)
    exts = re.findall(r"[\w.]+", m.group(1)) if m else []
    return ident, [e.lower().lstrip(".") for e in exts]


def compile_all(engine: str, specs: list[Path]) -> tuple[Path, str]:
    out = REPO / "build" / "ksy" / engine
    out.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([str(KSC), "-t", "python", "--outdir", str(out), *map(str, specs)],
                       capture_output=True, text=True, shell=False)
    return out, (r.stdout + r.stderr).strip()


def check(engine: str, only: str | None, max_files: int) -> int:
    specs = sorted((REPO / "engines" / engine / "docs" / "formats").glob("*.ksy"))
    if only:
        specs = [s for s in specs if s.stem == only]
    if not specs:
        print(f"{engine}: no .ksy specs")
        return 0
    out, log = compile_all(engine, specs)
    sys.path.insert(0, str(out))
    corpus = [REPO / "games" / g / "discs" for g in GAMES.get(engine, [])]
    bad = 0
    for ksy in specs:
        ident, exts = meta(ksy)
        mod_path = out / f"{ident}.py"
        if not mod_path.exists():
            lines = log.splitlines()
            at = next((i for i, l in enumerate(lines) if ksy.name in l), None)
            err = " ".join(l.strip() for l in lines[at:at + 2]) if at is not None else (lines[-1] if lines else "")
            print(f"FAIL {engine}/{ksy.stem}: does not compile: {err.split(ksy.name)[-1][:200]}")
            bad += 1
            continue
        spec = importlib.util.spec_from_file_location(ident, mod_path)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:  # generated code that imports a missing sibling, etc.
            print(f"FAIL {engine}/{ksy.stem}: generated parser does not load: {e}")
            bad += 1
            continue
        cls = getattr(mod, "".join(p.capitalize() for p in ident.split("_")))
        if not exts:
            print(f"ok   {engine}/{ksy.stem}: compiles (no file-extension in meta, corpus not checked)")
            continue
        files = [f for root in corpus if root.exists() for f in root.rglob("*")
                 if f.is_file() and f.suffix.lower().lstrip(".") in exts]
        if max_files:
            files = files[:max_files]
        fails, partial = [], 0
        container = "instances:" in ksy.read_text(encoding="utf-8")  # payload read by offset, not to the end
        for f in files:
            try:
                obj = cls.from_file(str(f))
                obj._read() if hasattr(obj, "_read") and not getattr(obj, "_m_read", True) else None
                if not obj._io.is_eof():
                    if container:
                        partial += 1
                    else:
                        fails.append(f"{f.name} (stops at {obj._io.pos()} of {f.stat().st_size})")
                obj._io.close()
            except Exception as e:
                fails.append(f"{f.name} ({type(e).__name__}: {str(e)[:60]})")
        status = "ok  " if not fails else "FAIL"
        bad += bool(fails)
        print(f"{status} {engine}/{ksy.stem}: {len(files) - len(fails)}/{len(files)} .{'/.'.join(exts)} files parse"
              + (" to the end" if not container else f" ({partial} read by offset, so not to the end)")
              + (f"; e.g. {'; '.join(fails[:3])}" if fails else ""))
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("engine", nargs="?")
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--max", type=int, default=200, help="files per spec, 0 = all")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    engines = list(GAMES) if a.all else [a.engine] if a.engine else []
    if not engines:
        print(__doc__)
        return 2
    return 1 if sum(check(e, a.spec, a.max) for e in engines) else 0


if __name__ == "__main__":
    sys.exit(main())
