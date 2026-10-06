"""Triage a decompile dump: which functions are the game's, and how much of it we understand.

Reads `engines/<engine>/notes/decomp/all/INDEX.tsv` (decompile_all.py) and the engine's
EVIDENCE.md, writes `TRIAGE.tsv` next to the index (address, name, kind, bytes, callers)
and prints one coverage line per program. Kinds:

  lib       recognised library code (Function ID names: CRT, STL, MFC)
  lib?      unnamed, but inside a 64 KB block that is mostly recognised library code
            (MSVC links the libraries as one block, after the game's own objects)
  specced   game code whose address is cited in EVIDENCE.md
  named     game code with a name we gave it (no evidence cited yet)
  unknown   game code nobody has looked at: where reverse engineering should go

    python tools/coverage.py grumpa
    python tools/coverage.py --selftest
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GAME_NAME = re.compile(r"^(FUN_|thunk_)")


def is_library_name(name: str) -> bool:
    # Function ID names are plain C/C++ library names; ours are Class::method or CFX*.
    return not GAME_NAME.match(name) and "::" not in name and not name.startswith("CFX")


def triage(rows: list[dict], cited: set[int]) -> list[dict]:
    blocks = defaultdict(lambda: [0, 0])
    for r in rows:
        b = blocks[r["addr"] >> 16]
        b[0] += 1
        b[1] += is_library_name(r["name"])
    lib_blocks = {k for k, (total, lib) in blocks.items() if lib * 2 > total}
    for r in rows:
        if is_library_name(r["name"]):
            r["kind"] = "lib"
        elif r["addr"] >> 16 in lib_blocks and GAME_NAME.match(r["name"]):
            r["kind"] = "lib?"
        elif r["addr"] in cited:
            r["kind"] = "specced"
        elif not GAME_NAME.match(r["name"]):
            r["kind"] = "named"
        else:
            r["kind"] = "unknown"
    return rows


def cited_addresses(engine: str) -> set[int]:
    ev = REPO / "engines" / engine / "docs" / "EVIDENCE.md"
    if not ev.exists():
        return set()
    return {int(m, 16) for m in re.findall(r"0x([0-9a-fA-F]{6,8})\b", ev.read_text(encoding="utf-8"))}


def main(engine: str) -> int:
    cited = cited_addresses(engine)
    dumps = sorted((REPO / "engines" / engine / "notes" / "decomp").glob("**/INDEX.tsv"))
    if not dumps:
        print(f"{engine}: no INDEX.tsv; run decompile_all.py first")
        return 1
    for index in dumps:
        rows = []
        for line in index.read_text(encoding="utf-8").split("\n")[1:]:
            f = line.split("\t")
            if len(f) < 4 or not re.fullmatch(r"[0-9a-fA-F]+", f[0]):
                continue  # blank, or a stray piece of an old dump's string column
            rows.append({"addr": int(f[0], 16), "name": f[1], "bytes": f[2], "callers": f[3]})
        rows = triage(rows, cited)
        out = index.with_name("TRIAGE.tsv")
        out.write_text("address\tname\tkind\tbytes\tcallers\n" + "".join(
            f"{r['addr']:08x}\t{r['name']}\t{r['kind']}\t{r['bytes']}\t{r['callers']}\n" for r in rows), encoding="utf-8")
        n = defaultdict(int)
        for r in rows:
            n[r["kind"]] += 1
        game = n["specced"] + n["named"] + n["unknown"]
        print(f"{engine} {index.parent.relative_to(REPO)}: {game} game functions, {n['specced']} specced, "
              f"{n['named']} named, {n['unknown']} unknown ({100 * (game - n['unknown']) // max(game, 1)}% looked at); "
              f"{n['lib'] + n['lib?']} library ({n['lib?']} by block) -> {out.name}")
    return 0


def selftest() -> None:
    rows = [{"addr": 0x480000 + i, "name": n} for i, n in enumerate(["_strlen", "_memcpy", "_atoi", "FUN_00480010"])]
    rows += [{"addr": 0x401000, "name": "FUN_00401000"}, {"addr": 0x401100, "name": "Scene::load"},
             {"addr": 0x401200, "name": "FUN_00401200"}]
    kinds = [r["kind"] for r in triage(rows, {0x401200})]
    assert kinds == ["lib", "lib", "lib", "lib?", "unknown", "named", "specced"], kinds
    print("coverage selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif len(sys.argv) == 2:
        sys.exit(main(sys.argv[1]))
    else:
        print(__doc__)
        sys.exit(2)
