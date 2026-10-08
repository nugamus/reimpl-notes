# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///
"""Scenario runs: scripted, bounded playtests with screenshot checks.

A scenario (`engines/<engine>/tests/<name>.toml`, committed) starts the engine in an exact
state, drives it with the engine's dev-harness keys, and names the screenshots it takes.
The runner builds a throwaway config from the engine's dev ini, runs the dev worktree's
exe (C:\\scummvm-dev\\<engine>) with a timeout, then compares each screenshot with its
reference in `engines/<engine>/tests/golden/<name>/` (gitignored: game imagery). A failure
leaves `<snap>-compare.png` (reference | now | changed pixels in red) in
`engines/<engine>/tests/out/<name>/` to look at.

    uv run tools/scenario.py grumpa                 # every Grumpa scenario
    uv run tools/scenario.py grumpa hut --update    # (re)record the references
    uv run tools/scenario.py --selftest

Scenario keys:
    description = "what it shows"
    snaps = ["hut.png"]            # files the run writes into {out}
    timeout = 60                   # seconds
    max_diff = 0.002               # allowed fraction of changed pixels per snap
    save = "C:/MonetPlay/saves/monet.003"   # optional: copied into the run's save folder
    saves_from = "chapter1"        # optional: start with the saves another scenario exported
    export_saves = true            # optional: keep this run's saves for later scenarios
    args = ["-d2", "--debugflags=script"]   # optional: extra ScummVM arguments (logging)
    [keys]                         # game-domain keys; {out} is the snap folder

Every run's output is kept in `engines/<engine>/tests/out/<name>/run.log` (coverage.py and
grep read it). Options: `--asan` runs the AddressSanitizer + UBSan build (tools/build-asan.sh) instead
and fails on any memory error or undefined behaviour it reports, with the first report in
the summary; `--coverage` turns on the engines' `coverage` debug channel for
tools/runcoverage.py; `--path DIR` replaces the game folder (the fuzzer uses it).
    grumpa_vm = "1;ticks 50;snap {out}/hut.png"
"""

from __future__ import annotations

import configparser
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEV = Path(os.environ.get("DEVROOT", "C:/scummvm-dev"))  # DEVROOT: a parallel agent's tree
OPTS = {"asan": False, "path": None, "coverage": False}
TOLERANCE = 16  # per-channel difference that counts as a changed pixel


def load_ini(path: Path) -> configparser.ConfigParser:
    ini = configparser.ConfigParser(interpolation=None, strict=False, comment_prefixes=("#",))
    ini.optionxform = str
    ini.read(path, encoding="utf-8")
    return ini


def compare(golden: Path, actual: Path, out: Path, max_diff: float) -> tuple[bool, float]:
    from PIL import Image, ImageChops

    a, b = Image.open(golden).convert("RGB"), Image.open(actual).convert("RGB")
    if a.size != b.size:
        changed = 1.0
        mask = Image.new("L", b.size, 255)
    else:
        bands = ImageChops.difference(a, b).split()
        mask = Image.eval(ImageChops.lighter(ImageChops.lighter(bands[0], bands[1]), bands[2]),
                          lambda v: 255 if v > TOLERANCE else 0)
        changed = mask.histogram()[255] / (mask.size[0] * mask.size[1])
    ok = changed <= max_diff
    if not ok:
        w, h = b.size
        sheet = Image.new("RGB", (w * 3, h))
        sheet.paste(a.resize(b.size), (0, 0))
        sheet.paste(b, (w, 0))
        red = Image.new("RGB", b.size, (255, 0, 0))
        sheet.paste(Image.composite(red, b.point(lambda v: v // 3), mask.resize(b.size)), (w * 2, 0))
        out.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(out)
    return ok, changed


def run(engine: str, path: Path, update: bool) -> bool:
    sc = tomllib.loads(path.read_text(encoding="utf-8"))
    name = path.stem
    dev_ini = load_ini(REPO / "engines" / engine / "tools" / "scummvm.ini")
    domain = sc.get("domain") or next(s for s in dev_ini.sections() if s != "scummvm")
    exe = (Path("C:/scummvm-asan") if OPTS["asan"] else DEV) / engine / "scummvm.exe"
    if not exe.exists():
        print(f"{engine}/{name}: no {exe} (bash tools/build{'-asan' if OPTS['asan'] else ''}.sh {engine})")
        return False

    with tempfile.TemporaryDirectory(prefix=f"scenario-{engine}-") as tmp:
        tmp = Path(tmp)
        out, saves = tmp / "out", tmp / "saves"
        out.mkdir()
        saves.mkdir()
        if sc.get("save"):
            shutil.copy(sc["save"], saves)
        if sc.get("saves_from"):
            for f in (REPO / "engines" / engine / "tests" / "saves" / sc["saves_from"]).glob("*"):
                shutil.copy(f, saves)
        ini = dev_ini
        if not ini.has_section("scummvm"):
            ini.add_section("scummvm")
        ini["scummvm"].update({"savepath": saves.as_posix(), "enable_unsupported_game_warning": "false",
                               "gfx_mode": sc.get("gfx_mode", "surfacesdl")})
        for k, v in sc.get("keys", {}).items():
            ini[domain][k] = str(v).replace("{out}", out.as_posix())
        if OPTS["path"]:
            ini[domain]["path"] = str(OPTS["path"])
        cfg = tmp / "scummvm.ini"
        with cfg.open("w", encoding="utf-8") as f:
            ini.write(f, space_around_delimiters=False)

        dlls = "C:\\msys64\\clang64\\bin;" if OPTS["asan"] else "C:\\msys64\\ucrt64\\bin;"
        env = dict(os.environ, SDL_WINDOW_NO_ACTIVATION_WHEN_SHOWN="1", PATH=dlls + os.environ.get("PATH", ""),
                   ASAN_OPTIONS="detect_leaks=0:print_summary=1", UBSAN_OPTIONS="print_stacktrace=1")
        start = time.time()
        # A renamed copy, so killing it on a timeout can never hit the user's scummvm.exe.
        runner = tmp / f"scummvm-scenario-{engine}.exe"
        shutil.copy(exe, runner)
        logdir = REPO / "engines" / engine / "tests" / "out" / name
        logdir.mkdir(parents=True, exist_ok=True)
        cov = ["-d1", "--debugflags=coverage"] if OPTS["coverage"] else []
        cmd = [str(runner), f"--config={cfg}", *cov, *sc.get("args", []), domain]
        timeout = sc.get("timeout", 60)
        if OPTS["asan"]:
            timeout *= 4
        try:
            proc = subprocess.run(cmd, env=env, cwd=tmp, timeout=timeout, capture_output=True, text=True,
                                  errors="replace")
            status = f"exit {proc.returncode}"
            (logdir / "run.log").write_text(proc.stdout + proc.stderr, encoding="utf-8")
        except subprocess.TimeoutExpired as e:
            status = "timed out"
            # Keep what the run printed before it was killed: where it got stuck
            text = lambda b: b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")
            (logdir / "run.log").write_text(text(e.stdout) + text(e.stderr), encoding="utf-8")
        took = time.time() - start
        if not OPTS["asan"] and not OPTS["coverage"] and status == "exit 0":  # timings of normal runs only
            with (REPO / "logs" / "perf.tsv").open("a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M')}\t{engine}\t{name}\t{took:.2f}\n")
        if sc.get("export_saves"):
            kept = REPO / "engines" / engine / "tests" / "saves" / name
            shutil.rmtree(kept, ignore_errors=True)
            shutil.copytree(saves, kept)

        results, ok = [], True
        for snap in sc.get("snaps", []):
            actual, golden = out / snap, REPO / "engines" / engine / "tests" / "golden" / name / snap
            if not actual.exists():
                results.append(f"{snap} missing")
                ok = False
            elif update or not golden.exists():
                golden.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(actual, golden)
                results.append(f"{snap} recorded")
            else:
                cmp_png = REPO / "engines" / engine / "tests" / "out" / name / (Path(snap).stem + "-compare.png")
                good, changed = compare(golden, actual, cmp_png, sc.get("max_diff", 0.002))
                results.append(f"{snap} {'ok' if good else 'CHANGED'} {changed:.2%}" + ("" if good else f" -> {cmp_png}"))
                ok &= good
        if OPTS["asan"]:
            log = (logdir / "run.log").read_text(encoding="utf-8", errors="replace") if (logdir / "run.log").exists() else ""
            found = [l for l in log.splitlines() if "ERROR: AddressSanitizer:" in l or "runtime error:" in l]
            results.append(f"sanitizers: {len(found)} reports" + (f", first: {found[0].strip()[:160]}" if found else ""))
            ok &= not found
        print(f"{'PASS' if ok else 'FAIL'} {engine}/{name} ({status}, {took:.0f}s): " + "; ".join(results))
        return ok


def selftest() -> None:
    from PIL import Image

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        a = Image.new("RGB", (100, 100), (10, 10, 10))
        b = a.copy()
        b.putpixel((5, 5), (200, 10, 10))
        a.save(tmp / "a.png")
        b.save(tmp / "b.png")
        assert compare(tmp / "a.png", tmp / "a.png", tmp / "c.png", 0.0) == (True, 0.0)
        ok, changed = compare(tmp / "a.png", tmp / "b.png", tmp / "c.png", 0.0)
        assert not ok and abs(changed - 0.0001) < 1e-9 and (tmp / "c.png").exists()
        assert compare(tmp / "a.png", tmp / "b.png", tmp / "d.png", 0.001)[0]
    print("scenario selftest ok")


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        selftest()
        return 0
    update = "--update" in argv
    OPTS["asan"] = "--asan" in argv
    OPTS["coverage"] = "--coverage" in argv
    if "--path" in argv:
        OPTS["path"] = argv[argv.index("--path") + 1]
        argv = argv[:argv.index("--path")] + argv[argv.index("--path") + 2:]
    args = [a for a in argv if a not in ("--update", "--asan", "--coverage")]
    if not args:
        print(__doc__)
        return 2
    engine, names = args[0], args[1:]
    tests = REPO / "engines" / engine / "tests"
    paths = [tests / f"{n}.toml" for n in names] if names else sorted(
        p for p in tests.glob("*.toml") if not p.name.startswith(("save_", "_")))  # templates and temporaries
    if not paths:
        print(f"{engine}: no scenarios in {tests}")
        return 0
    results = [run(engine, p, update) for p in paths]
    print(f"{engine}: {sum(results)}/{len(results)} scenarios pass")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
