"""Match RING.EXE's functions between the DVD and the ISO or CD edition and list the zone
handlers whose strings, constant arguments or API calls differ (E-0304).

Input: per-function features dumped by tools/ghidra/scripts/ring_features.py into
build/ring-features/RING_<EDITION>.jsonl (call targets, strings, constants, in order).
Matching (DVD -> edition): functions with the same error-string name (notes/names/*.csv),
the set-up functions (ringemu.EDITIONS) and their callees (ringemu.callee_map), then
repeatedly the callees of matched functions (the two call lists aligned with difflib on the
callees already matched; gaps of equal length pair one to one), functions with the same
unique strings and constants, and the single unmatched callers of matched functions.

A handler is compared with its local helpers (callees with at most two callers, three
levels deep, not into the zone set-ups) on: strings (case-blind; the DVD's media numbers renamed per
notes/media-names.tsv), constants pushed or moved that can be ids or times (1000..999999,
not 1024 or 32767; switch-case compares are left out, the two compilers lay them out
differently), and the named API functions called (notes/names). The ISO is compared with
the DVD; the CD (Borland) with the ISO, through the DVD's matches.

Writes engines/ring/notes/calls-<edition>/handlers-vs-<base>.md (base dvd for iso, iso for
cd): the match counts and every handler of spec/events.md with its differences; for the ISO
also every other matched function whose strings or constants differ, and
notes/calls-iso/string-pairs.tsv: the DVD and ISO strings found at the same place in matched
functions (read by namemap.py).

    python engines/ring/tools/handlers.py --edition iso|cd
    python engines/ring/tools/handlers.py --selftest
"""

from __future__ import annotations

import csv
import difflib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ringemu  # noqa: E402
from zonedecl import REPO  # noqa: E402

FEATURES = REPO / "build/ring-features"
NAMES = REPO / "engines/ring/notes/names"
EXE = {"dvd": "RING_DVD", "iso": "RING_ISO", "cd": "RING_CD"}
ZONES = ["sy", "ni", "rh", "fo", "ro", "wa", "as", "n2"]
# Zone handlers per dispatcher, spec/events.md (DVD addresses), in ZONES order; None = default.
HANDLERS = {
    "object click": [0x431660, 0x445C80, 0x443990, 0x43DAC0, 0x43AFA0, 0x437D60, 0x4364A0, 0x4341E0],
    "button down": [None, 0x4472B0, None, 0x441860, 0x43B9A0, None, None, 0x434740],
    "click, flag bit 3": [None, None, None, 0x441860, None, 0x4392A0, None, None],
    "drag": [0x4331B0, 0x4477D0, None, 0x441890, 0x43BBF0, None, None, 0x4349B0],
    "inventory list click": [None, None, None, 0x441D50, None, None, None, None],
    "before a movability": [0x433530, 0x449080, 0x444B40, 0x4420B0, 0x43C290, 0x439F40, 0x436C10, 0x435390],
    "after a movability": [0x433570, 0x449320, 0x444BA0, 0x442580, 0x43C450, 0x43A050, 0x436D60, 0x435410],
    "timer": [None, 0x4497B0, 0x444D30, 0x442810, 0x43C500, None, 0x436DF0, 0x435470],
    "animation 0x40c910": [None, None, None, None, None, 0x43A6F0, None, None],
    "on an accessibility": [0x4335A0, 0x44A120, None, None, None, None, None, 0x435970],
    "on a movability": [0x433B80, 0x44A1B0, 0x44A1B0, 0x433B80, 0x433B80, 0x433B80, 0x433B80, 0x44A1B0],
    "on nothing": [0x433BC0, 0x442E30, 0x442E30, 0x442E30, 0x442E30, 0x442E30, 0x442E30, 0x442E30],
    "sound or dialog finished": [0x433CF0, 0x44A1C0, 0x444E60, 0x442E40, 0x43D4A0, 0x43A860, 0x437190, 0x435A00],
    "animation event": [None, 0x4499E0, 0x444DC0, 0x442B60, 0x43C5E0, 0x43A400, 0x437110, 0x4354B0],
    "key": [0x433D30, None, None, None, None, None, None, None],
}


def features(edition: str) -> dict[str, dict]:
    path = FEATURES / f"{EXE[edition]}.jsonl"
    return {(f := json.loads(line))["entry"]: f for line in path.open(encoding="utf-8")}


def names(edition: str) -> dict[str, str]:
    """name -> address, for names given to one function only."""
    rows = [r for r in csv.DictReader((NAMES / f"{EXE[edition]}.EXE.csv").open(encoding="utf-8")) if r["name"]]
    count = Counter(r["name"] for r in rows)
    return {r["name"]: r["address"] for r in rows if count[r["name"]] == 1}


def seed(edition: str) -> dict[str, str]:
    """DVD entry -> edition entry, from names and the set-ups."""
    d, e = names("dvd"), names(edition)
    m = {d[n]: e[n] for n in d if n in e}
    _, _, dvd_setups = ringemu.EDITIONS["dvd"]
    _, _, ed_setups = ringemu.EDITIONS[edition]
    m.update({f"{a:08x}": f"{b:08x}" for a, b in zip(dvd_setups, ed_setups)})
    exe = ringemu.Exe(edition)
    raw = {z: ringemu.emulate(exe, exe.setups[i]) for i, z in enumerate(ZONES)}
    m.update({dvd: ed for ed, dvd in ringemu.callee_map(exe, raw).items()})
    return m


def signature(f: dict) -> tuple:
    return tuple(sorted(s.lower() for s in f["strings"])), tuple(sorted(f["scalars"])), len(f["calls"])


def by_signature(m: dict[str, str], dvd: dict, ed: dict) -> bool:
    """Pair unmatched functions whose strings, constants and call count are the same and
    unique on both sides (only functions with at least one string or constant)."""
    taken = set(m.values())
    sa = Counter(signature(f) for k, f in dvd.items() if k not in m)
    sb = Counter(signature(f) for k, f in ed.items() if k not in taken)
    index = {signature(f): k for k, f in ed.items() if k not in taken}
    new = {k: index[sig] for k, f in dvd.items() if k not in m and (sig := signature(f)) in index
           and (sig[0] or sig[1]) and sa[sig] == 1 and sb[sig] == 1}
    m.update(new)
    return bool(new)


def by_callers(m: dict[str, str], dvd: dict, ed: dict) -> bool:
    """A matched pair whose functions each have exactly one unmatched caller pairs the callers."""
    def callers(fs: dict) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for k, f in fs.items():
            for c in set(f["calls"]):
                out.setdefault(c, []).append(k)
        return out
    ca, cb = callers(dvd), callers(ed)
    taken = set(m.values())
    new = {}
    for a, b in m.items():
        ua = [x for x in ca.get(a, []) if x not in m and x not in new]
        ub = [y for y in cb.get(b, []) if y not in taken and y not in new.values()]
        if len(ua) == 1 and len(ub) == 1:
            new[ua[0]] = ub[0]
    m.update(new)
    return bool(new)


def match(m: dict[str, str], dvd: dict, ed: dict) -> dict[str, str]:
    m = propagate(m, dvd, ed)
    while by_signature(m, dvd, ed) or by_callers(m, dvd, ed):
        m = propagate(m, dvd, ed)
    return m


def propagate(m: dict[str, str], dvd: dict, ed: dict) -> dict[str, str]:
    m = dict(m)
    taken = set(m.values())
    changed = True
    while changed:
        changed = False
        for a, b in list(m.items()):
            if a not in dvd or b not in ed:
                continue
            ca, cb = dvd[a]["calls"], ed[b]["calls"]
            inv = {v: k for k, v in m.items()}
            ta = [c if c in m or c not in dvd else ("a", i) for i, c in enumerate(ca)]  # imports by name
            tb = [inv.get(c, c if c not in ed else ("b", i)) for i, c in enumerate(cb)]
            sm = difflib.SequenceMatcher(None, ta, tb, autojunk=False)
            for op, i1, i2, j1, j2 in sm.get_opcodes():
                if op == "equal" or i2 - i1 != j2 - j1:
                    continue
                for x, y in zip(ca[i1:i2], cb[j1:j2]):
                    if x in dvd and y in ed and x not in m and y not in taken:
                        m[x], changed = y, True
                        taken.add(y)
    return m


def media_names() -> dict[str, str]:
    return ringemu.media_names()


def is_text(s: str) -> bool:
    """Not a pointer read as a string (3 bytes ending in the image's high byte 0x40..0x4b)."""
    return all(" " <= c <= "~" for c in s) and not (len(s) == 3 and "@" <= s[2] <= "K")


def norm_strings(strings: list[str], rename: dict[str, str]) -> Counter:
    return Counter(rename.get(s.lower(), s.lower()) for s in strings if is_text(s))


def ids(values: list[int]) -> Counter:
    return Counter(v for v in values if 1000 <= v < 1_000_000 and v not in (1024, 32767))


def closure(k: str, fs: dict, callers: Counter, api: dict[str, str], stop: set[str], depth: int = 3) -> dict:
    """A handler with its local helpers merged: strings, constant arguments, API calls (by
    name, through `api`: address -> name); the zone set-ups (`stop`) are not followed."""
    out = {"strings": [], "args": [], "api": []}
    seen, todo = set(), [(k, 0)]
    while todo:
        x, d = todo.pop()
        if x in seen or x not in fs:
            continue
        seen.add(x)
        out["strings"] += fs[x]["strings"]
        out["args"] += fs[x]["args"]
        out["api"] += [api[c] for c in fs[x]["calls"] if c in api]
        if d < depth:
            todo += [(c, d + 1) for c in fs[x]["calls"] if callers[c] <= 2 and c not in api and c not in stop]
    return out


def diff(a: Counter, b: Counter, what: str, la: str, lb: str, fmt=str) -> list[str]:
    if a == b:
        return []
    return [f"{what} {la} only: " + ", ".join(fmt(v) for v in sorted((a - b).elements())),
            f"{what} {lb} only: " + ", ".join(fmt(v) for v in sorted((b - a).elements()))]


def compare(f: dict, g: dict, rename: dict[str, str], la: str, lb: str) -> list[str]:
    return (diff(norm_strings(f["strings"], rename), norm_strings(g["strings"], {}), "strings", la, lb, json.dumps)
            + diff(ids(f["args"]), ids(g["args"]), "ids", la, lb)
            + (diff(Counter(f["api"]), Counter(g["api"]), "API calls", la, lb) if "api" in f else []))


class Edition:
    """An edition's features, its match from the DVD, callers and API names."""

    def __init__(self, edition: str, dvd_names: dict[str, str]):
        self.fs = features(edition)
        self.m = {k: k for k in features("dvd")} if edition == "dvd" else match(seed(edition), features("dvd"), self.fs)
        self.callers = Counter(c for f in self.fs.values() for c in set(f["calls"]))
        self.api = {self.m[a]: n for a, n in dvd_names.items() if a in self.m}
        setups = [f"{a:08x}" for a in ringemu.EDITIONS["dvd"][2]] + ["00431040"]  # + the zone set-up
        self.stop = {self.m[a] for a in setups if a in self.m}

    def handler(self, dvd_addr: str) -> dict | None:
        k = self.m.get(dvd_addr)
        return closure(k, self.fs, self.callers, self.api, self.stop) if k in self.fs else None


def report(edition: str) -> str:
    base = "dvd" if edition == "iso" else "iso"
    dvd_names = {a: n for n, a in names("dvd").items()}
    b, e = Edition(base, dvd_names), Edition(edition, dvd_names)
    rename = media_names() if base == "dvd" else {}
    lb, le = base.upper(), edition.upper()
    lines = [f"# {le} zone handlers against the {lb}'s (generated)", "",
             f"Generated by `engines/ring/tools/handlers.py --edition {edition}` (method in its "
             f"docstring). DVD functions matched: {len(b.m)} in the {lb} EXE, {len(e.m)} in the {le} "
             f"EXE (of {len(features('dvd'))}).", "", "## Zone handlers (spec/events.md)", ""]
    for event, addrs in HANDLERS.items():
        for zone, a in zip(ZONES, addrs):
            if a is None:
                continue
            k = f"{a:08x}"
            hb, he = b.handler(k), e.handler(k)
            d = compare(hb, he, rename, lb, le) if hb and he else ["not matched"]
            lines.append(f"- {event}, {zone.upper()}: DVD `{k}`, {lb} `{b.m.get(k)}`, {le} `{e.m.get(k)}`"
                         + (": same" if not d else ""))
            lines += [f"  - {x}" for x in d]
    if base == "dvd":
        lines += ["", "## Every other matched function whose strings or constants differ", ""]
        for k in sorted(e.m):
            f, g = b.fs.get(k), e.fs.get(e.m[k])
            if f and g:
                d = compare(f, g, rename, lb, le)
                if d:
                    lines.append(f"- DVD `{k}` {f['name']} = `{e.m[k]}`")
                    lines += [f"  - {x}" for x in d]
    return "\n".join(lines) + "\n"


def string_pairs() -> Counter:
    """(DVD string, ISO string) at the same place: in every matched function pair with as
    many strings on both sides, the strings that differ (case-blind), paired in order."""
    dvd_names = {a: n for n, a in names("dvd").items()}
    b, e = Edition("dvd", dvd_names), Edition("iso", dvd_names)
    pairs: Counter = Counter()
    for k, v in e.m.items():
        f, g = b.fs.get(k), e.fs.get(v)
        if not f or not g:
            continue
        sa = [x.lower() for x in f["strings"] if is_text(x)]
        sb = [x.lower() for x in g["strings"] if is_text(x)]
        if len(sa) == len(sb):
            pairs.update((x, y) for x, y in zip(sa, sb) if x != y)
    return pairs


def main() -> None:
    edition = sys.argv[sys.argv.index("--edition") + 1]
    out = REPO / f"engines/ring/notes/calls-{edition}/handlers-vs-{'dvd' if edition == 'iso' else 'iso'}.md"
    out.write_text(report(edition), encoding="utf-8", newline="\n")
    print(out)
    if edition == "iso":
        out = REPO / "engines/ring/notes/calls-iso/string-pairs.tsv"
        rows = sorted(string_pairs().items())
        out.write_text("dvd\tiso\tcount\n" + "".join(f"{x}\t{y}\t{c}\n" for (x, y), c in rows),
                       encoding="utf-8", newline="\n")
        print(out)


def selftest() -> None:
    """The DVD matched against itself pairs every function with itself and finds no difference."""
    dvd = features("dvd")
    m = propagate({k: k for k in list(dvd)[:50]}, dvd, dvd)
    assert all(k == v for k, v in m.items()), [k for k, v in m.items() if k != v][:5]
    assert not any(compare(dvd[k], dvd[k], {}, "a", "b") for k in dvd)
    iso = match(seed("iso"), dvd, features("iso"))
    assert iso["00431660"] and iso["004635a0"] == "0046bda0", iso.get("004635a0")
    print(f"selftest ok ({len(m)} self-matches, {len(iso)} ISO matches)")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
