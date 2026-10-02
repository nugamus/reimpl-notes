"""Pair the DVD edition's renamed data files with the CD and ISO versions' names (E-0300).

The DVD stores videos, sounds and dialogues under numbers (`DATA/AS/PLA/1001.CNM`,
`DATA/NI/SOUND/1583.WAS`, `DATA/NI/DIA/ENG/1626.DAN`), the CD and ISO versions under
descriptive names (`ass00n01_s00n02.cnm`, `ni_bgr_main_hall.was`, `cin_rh1_01.dan`), the
same number for the same file in every language; and 18 pictures under shorter names
(`DATA/AS/IMAGE/ASV01.BMA` = `ass01n01_v01.bma`, `DATA/SY/VISUAL/UP_GUN.TGA` =
`larup_gun.tga`). Every file under `DATA/<zone>/<folder>/` is compared. Files
byte-identical between the DVD and the CD pair by MD5 (zone, folder and language the
same; a number paired in one language holds for all). Where several CD names hold the same
bytes, the one the ISO's code uses in the DVD name's place wins (notes/calls-iso/
string-pairs.tsv, from handlers.py, E-0304), else the one whose stem is the same-numbered
sound's or video's. A file the MD5 leaves unpaired pairs with the one unpaired file of the
same size in its folder. The ISO re-encoded the videos (E-0010): its names are checked
against the CD's. DVD names with no file on the CD/ISO discs take the name the ISO's code
uses in their place.

Writes engines/ring/notes/media-names.tsv, one row per (zone, folder, DVD file) whose name
differs: zone, folder (pla | sound | dia | image | visual), dvd name, cd/iso name (both
lower case, with extension), CD discs, ISO discs, how it paired: md5 | md5-code |
md5-stem | md5-dup (any of the names, same bytes) | size | code (no such file on the CD/ISO
discs; zone empty when no edition has the file, E-0097) | dvd-only | cd-only.

    python engines/ring/tools/namemap.py             # writes the table, prints a summary
    python engines/ring/tools/namemap.py --selftest
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MD5 = REPO / "engines/ring/notes/corpus-md5.tsv"
PAIRS = REPO / "engines/ring/notes/calls-iso/string-pairs.tsv"
OUT = REPO / "engines/ring/notes/media-names.tsv"


def media() -> dict[str, list[tuple]]:
    """edition ('dvd'|'cd'|'iso') -> [(zone, folder, lan, name, disc, md5, size)]"""
    out = defaultdict(list)
    for r in csv.DictReader(MD5.open(encoding="utf-8"), delimiter="\t"):
        parts = r["path"].lower().split("/")  # data/<zone>/<folder>[/<lan>]/<name>
        if not r["edition"].startswith("ring/") or parts[0] != "data" or len(parts) < 4:
            continue
        ed = r["edition"][5:]
        kind = ed.rstrip("0123456789")
        lan = parts[3] if len(parts) == 5 else ""
        out[kind].append((parts[1], parts[2], lan, parts[-1], ed[len(kind):], r["md5"], r["size"]))
    return out


def code_names() -> dict[str, set[str]]:
    """DVD string -> the strings the ISO's code has in its place."""
    out: dict[str, set[str]] = defaultdict(set)
    if PAIRS.exists():
        for r in csv.DictReader(PAIRS.open(encoding="utf-8"), delimiter="\t"):
            out[r["dvd"]].add(r["iso"])
    return out


def stem(name: str) -> str:
    return name.rsplit(".", 1)[0]


def build() -> list[tuple]:
    m = media()
    code = code_names()
    cd_by_md5 = defaultdict(set)
    for z, fo, lan, n, _, md5, _ in m["cd"]:
        cd_by_md5[(z, fo, lan, md5)].add(n)
    cands: dict[tuple, set[str]] = {}  # (zone, folder, dvd name) -> CD names of its content
    left = []
    for z, fo, lan, n, _, md5, size in m["dvd"]:
        c = cd_by_md5.get((z, fo, lan, md5))
        if c:
            cands[(z, fo, n)] = cands.get((z, fo, n), c) & c
            assert cands[(z, fo, n)], (z, fo, n, lan)  # one number, one name in every language
        else:
            left.append((z, fo, lan, n, size))
    stems = {(z, stem(n)): stem(min(c)) for (z, fo, n), c in cands.items() if len(c) == 1 and fo != "dia"}
    pairs = {}
    for (z, fo, n), c in cands.items():
        by_code = {x for x in c if x in code.get(n, ()) or stem(x) in code.get(stem(n), ())}
        by_stem = {x for x in c if stem(x) == stems.get((z, stem(n)))}
        if len(c) == 1 or n in c:
            pairs[(z, fo, n)] = (n if n in c else min(c), "md5")
        elif len(by_code) == 1:
            pairs[(z, fo, n)] = (min(by_code), "md5-code")
        elif len(by_stem) == 1:
            pairs[(z, fo, n)] = (min(by_stem), "md5-stem")
        else:
            pairs[(z, fo, n)] = (min(c), "md5-dup")
    paired_cd = {(z, fo, c) for (z, fo, _), cs in cands.items() for c in cs}
    for z, fo, lan, n, size in left:
        if (z, fo, n) in pairs:
            continue
        same = [c[3] for c in m["cd"] if c[:3] == (z, fo, lan) and c[6] == size and (z, fo, c[3]) not in paired_cd]
        same_dvd = [d for d in left if d[:3] == (z, fo, lan) and d[4] == size and (z, fo, d[3]) not in pairs]
        if len(same) == 1 and len(same_dvd) == 1:
            pairs[(z, fo, n)] = (same[0], "size")
            paired_cd.add((z, fo, same[0]))
    discs = {k: defaultdict(set) for k in ("cd", "iso")}
    for k in discs:
        for z, fo, _, n, d, _, _ in m[k]:
            discs[k][(z, fo, n)].add(d)
    rows = []
    for z, fo, n in sorted({(z, fo, n) for z, fo, _, n, *_ in m["dvd"]}):
        c, how = pairs.get((z, fo, n), ("", "dvd-only"))
        named = code.get(stem(n), set())
        if not c and len(named) == 1:
            c, how = min(named) + n[len(stem(n)):], "code"
        if c == n:
            continue
        rows.append((z, fo, n, c, ",".join(sorted(discs["cd"].get((z, fo, c), ()))),
                     ",".join(sorted(discs["iso"].get((z, fo, c), ()))), how))
    for (z, fo, c), d in sorted(discs["cd"].items()):
        if (z, fo, c) not in paired_cd:
            rows.append((z, fo, "", c, ",".join(sorted(d)), ",".join(sorted(discs["iso"].get((z, fo, c), ()))), "cd-only"))
    dvd_stems = {stem(n) for _, _, _, n, *_ in m["dvd"]}
    for n, named in sorted(code.items()):
        if n.isdigit() and n not in dvd_stems and len(named) == 1:  # rides on no disc, E-0097
            rows.append(("", "pla", n + ".cnm", min(named) + ".cnm", "", "", "code"))
    return sorted(rows)


def write(rows) -> None:
    with OUT.open("w", newline="\n", encoding="utf-8") as f:
        f.write("zone\tfolder\tdvd\tname\tcd_discs\tiso_discs\tpaired\n")
        for r in rows:
            f.write("\t".join(r) + "\n")


def summary(rows) -> dict[str, int]:
    s = defaultdict(int)
    for r in rows:
        s[f"{r[1]} {r[6]}"] += 1
        if r[3] and not r[5] and r[6] != "code":
            s[f"{r[1]} cd name not on iso"] += 1
    return dict(sorted(s.items()))


def selftest() -> None:
    rows = build()
    s = summary(rows)
    print(s)
    assert ("as", "pla", "1001.cnm", "ass00n01_s00n02.cnm", "1", "2", "md5") in rows
    assert ("wa", "pla", "1911.cnm", "was03n01_s03n02_var2.cnm", "6", "3", "size") in rows
    assert ("ni", "sound", "1583.was", "ni_bgr_main_hall.was", "6", "1", "md5") in rows
    assert ("ni", "dia", "1626.dan", "cin_rh1_01.dan", "2,3,4", "1", "md5") in rows
    assert ("as", "dia", "1061.dia", "as_drill02.dia", "2,3,4", "1", "md5-stem") in rows
    assert ("fo", "dia", "1323.dan", "fos00n03p01di02.dan", "3", "", "md5-stem") in rows  # French only
    assert s["pla md5"] == 441 and s["pla size"] == 1, s
    assert "pla cd-only" not in s and "pla cd name not on iso" not in s, s
    if PAIRS.exists():
        assert ("fo", "sound", "1359.wav", "fos06n02_sun.wav", "2,3,4,6", "1", "md5-code") in rows
        assert ("as", "pla", "1163.cnm", "introm_2.cnm", "", "", "code") in rows
        assert ("", "pla", "1723.cnm", "rhs02n01_s01n01.cnm", "", "", "code") in rows
        assert s["pla code"] == 9 + 13 and "pla dvd-only" not in s, s
        assert s["sound md5-dup"] == 1  # FO_PLA.WAV, which no code names
    names = [(r[0], r[1], r[2]) for r in rows if r[2]]
    assert len(names) == len(set(names))
    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        rows = build()
        write(rows)
        print(summary(rows), "->", OUT)
