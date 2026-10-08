"""Feed an engine corrupted game files and see whether it crashes.

A shipped engine meets damaged discs and bad rips; ScummVM wants it to refuse them with a
warning, not crash. This builds a throwaway copy of the game folder (hard links, so it costs
no space and the originals are never touched), replaces one file with a mutated copy
(random byte flips, a truncation, or a chunk of 0xFF), and runs a scenario on it with
`--path`. A crash (an exit code other than 0, a hang until the timeout, or a sanitizer
report with --asan) is a finding: the mutated file is kept in build/fuzz/ to reproduce it.

    python tools/fuzz.py grumpa hut "Scenes/Scene_001.abi" --runs 20
    python tools/fuzz.py grumpa hut "Bitmaps/1_*.jpg" --runs 10 --asan
    python tools/fuzz.py --selftest

The file pattern is relative to the game folder (the dev ini's path). Only files the
scenario actually loads are worth fuzzing.
"""

from __future__ import annotations

import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import scenario  # noqa: E402


def mutate(data: bytes, rng: random.Random) -> tuple[bytes, str]:
    if not data:
        return data, "empty"
    kind = rng.choice(["flip", "flip", "truncate", "fill"])
    b = bytearray(data)
    if kind == "flip":
        for _ in range(rng.randint(1, 8)):
            b[rng.randrange(len(b))] ^= 1 << rng.randrange(8)
        return bytes(b), "flip"
    if kind == "truncate":
        cut = rng.randrange(len(b))
        return bytes(b[:cut]), f"truncate@{cut}"
    at = rng.randrange(len(b))
    n = min(len(b) - at, rng.randint(4, 64))
    b[at:at + n] = b"\xff" * n
    return bytes(b), f"fill@{at}+{n}"


def link_tree(src: Path, dst: Path) -> None:
    for root, dirs, files in os.walk(src):
        rel = Path(root).relative_to(src)
        (dst / rel).mkdir(parents=True, exist_ok=True)
        for f in files:
            os.link(Path(root) / f, dst / rel / f)


def main(engine: str, name: str, pattern: str, runs: int, asan: bool) -> int:
    ini = scenario.load_ini(REPO / "engines" / engine / "tools" / "scummvm.ini")
    import tomllib
    sc = tomllib.loads((REPO / "engines" / engine / "tests" / f"{name}.toml").read_text(encoding="utf-8"))
    domain = sc.get("domain") or next(s for s in ini.sections() if s != "scummvm")
    game = Path(ini[domain]["path"])
    targets = sorted(game.glob(pattern))
    if not targets:
        print(f"no files match {pattern} under {game}")
        return 2
    work = REPO / "build" / "fuzz" / engine
    shutil.rmtree(work / "game", ignore_errors=True)
    link_tree(game, work / "game")
    rng = random.Random(1234)
    found = 0
    for i in range(runs):
        target = rng.choice(targets)
        rel = target.relative_to(game)
        copy = work / "game" / rel
        copy.unlink()  # break the hard link before writing
        data, how = mutate(target.read_bytes(), rng)
        copy.write_bytes(data)
        out = subprocess.run(["uv", "run", str(REPO / "tools" / "scenario.py"), engine, name, "--path",
                              str(work / "game")] + (["--asan"] if asan else []),
                             capture_output=True, text=True)
        line = next((l for l in out.stdout.splitlines() if l.startswith(("PASS", "FAIL"))), out.stdout.strip()[:200])
        crashed = "timed out" in line or ("(exit " in line and "(exit 0," not in line) or (asan and "sanitizers: 0" not in line)
        if crashed:
            found += 1
            keep = work / "findings" / f"{i:03d}_{how}_{rel.name}"
            keep.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(copy, keep)
            print(f"CRASH run {i}: {rel} ({how}) -> {keep.relative_to(REPO)}: {line[:160]}")
        copy.unlink()
        os.link(target, copy)  # restore the original
    print(f"{engine}/{name}: {runs} runs over {len(targets)} file(s), {found} crash(es)")
    return 1 if found else 0


def selftest() -> None:
    rng = random.Random(1)
    data = bytes(range(256)) * 4
    kinds = set()
    for _ in range(50):
        out, how = mutate(data, rng)
        kinds.add(how.split("@")[0])
        assert out != data or how.startswith("truncate@1024")
    assert {"flip", "truncate", "fill"} <= kinds, kinds
    print("fuzz selftest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
        sys.exit(0)
    asan = "--asan" in a
    a = [x for x in a if x != "--asan"]
    runs = 10
    if "--runs" in a:
        runs = int(a[a.index("--runs") + 1])
        a = a[:a.index("--runs")] + a[a.index("--runs") + 2:]
    if len(a) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(a[0], a[1], a[2], runs, asan))
