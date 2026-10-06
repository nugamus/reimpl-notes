"""Can the docs be trusted, and does the engine implement what the specs say?

Checks, per engine:
  ids        every E-xxxx and Q-xxxx cited (specs, formats, CLAUDE.md, engine code) exists in
             EVIDENCE.md / OPEN-QUESTIONS.md, and no id is defined twice;
  links      relative markdown links in the engine's docs point at files that exist;
  trace      spec sections (## / ### headings in docs/spec/) whose evidence ids never appear
             in the engine's code (possibly not implemented yet), and code citing ids that
             no spec mentions. Engine comments cite evidence as `E-0123`, which is the link.

    python tools/doclint.py grumpa
    python tools/doclint.py --all
    python tools/doclint.py --selftest
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ENGINES = [l.split()[0] for l in (REPO / "tools" / "engines.txt").read_text().splitlines()
           if l.strip() and not l.startswith("#")]
EID = re.compile(r"\b([EQ])-(\d{4})\b")


def defined(text: str, kind: str) -> Counter:
    # A definition is the id followed by its dash ("### Q-0008 — ..."). Follow-ups re-head it
    # with a word ("Q-0008 RESOLVED ...", "UPDATE", "narrowed": supersede, don't edit), and the
    # format template ("<one-line claim>") is not an entry; neither counts as a duplicate.
    return Counter(m.group(1) for m in re.finditer(rf"^#+\s*{kind}-(\d{{4}})\b(?=\s*[—–:]|\s*-\s|\s*$)(?!.*<one-line)", text, re.M))


def cited(text: str) -> set[tuple[str, str]]:
    return {(m.group(1), m.group(2)) for m in EID.finditer(text)}


def sections(text: str) -> list[tuple[str, set[str]]]:
    """(heading, E-ids under it) for each ## / ### section."""
    out, head, buf = [], None, []
    for line in text.splitlines() + ["## end"]:
        m = re.match(r"^#{2,3}\s+(.+)", line)
        if m:
            if head:
                out.append((head, {n for k, n in cited("\n".join(buf)) if k == "E"}))
            head, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    return out


def check(engine: str) -> int:
    root = REPO / "engines" / engine
    docs = root / "docs"
    ev = (docs / "EVIDENCE.md").read_text(encoding="utf-8") if (docs / "EVIDENCE.md").exists() else ""
    oq = (docs / "OPEN-QUESTIONS.md").read_text(encoding="utf-8") if (docs / "OPEN-QUESTIONS.md").exists() else ""
    e_def, q_def = defined(ev, "E"), defined(oq, "Q")
    texts = {p: p.read_text(encoding="utf-8", errors="replace") for p in docs.rglob("*.md")}
    if (root / "CLAUDE.md").exists():
        texts[root / "CLAUDE.md"] = (root / "CLAUDE.md").read_text(encoding="utf-8")
    code_root = Path(f"C:/scummvm-dev/{engine}/engines/{engine}")
    code = {p: p.read_text(encoding="utf-8", errors="replace")
            for p in code_root.rglob("*") if p.suffix in (".cpp", ".h")} if code_root.exists() else {}
    problems = []
    for kind, d in (("E", e_def), ("Q", q_def)):
        for n, c in d.items():
            if c > 1:
                problems.append(f"{kind}-{n} defined {c} times")
    missing = Counter()
    for p, t in list(texts.items()) + list(code.items()):
        if p.name in ("EVIDENCE.md", "OPEN-QUESTIONS.md"):
            continue
        for k, n in cited(t):
            if n not in (e_def if k == "E" else q_def):
                missing[f"{k}-{n}"] += 1
    if missing:
        problems.append(f"{len(missing)} ids cited but not defined: " + " ".join(sorted(missing)[:15]))
    broken = []
    for p, t in texts.items():
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", t):
            if "://" in target or target.startswith("mailto:") or not re.fullmatch(r"[\w./-]*[./][\w./-]*", target):
                continue  # a URL, or not a path at all (code like `a[i](*(this+0x1b4)`)
            if not (p.parent / target).exists() and not (REPO / target).exists():
                broken.append(f"{p.relative_to(REPO).as_posix()} -> {target}")
    if broken:
        problems.append(f"{len(broken)} broken links, e.g. " + "; ".join(broken[:3]))
    code_ids = {n for t in code.values() for k, n in cited(t) if k == "E"}
    unimplemented, spec_ids = [], set()
    for p in sorted((docs / "spec").glob("*.md")) if (docs / "spec").exists() else []:
        for head, ids in sections(texts[p]):
            spec_ids |= ids
            if ids and not ids & code_ids:
                unimplemented.append(f"{p.stem}: {head}")
    # Format facts live in docs/formats/ (and game logic in games/<game>/docs), not docs/spec.
    for p, t in texts.items():
        if "formats" in p.parts:
            spec_ids |= {n for k, n in cited(t) if k == "E"}
    for p in (docs / "formats").glob("*.ksy") if (docs / "formats").exists() else []:
        spec_ids |= {n for k, n in cited(p.read_text(encoding="utf-8", errors="replace")) if k == "E"}
    orphan = sorted(code_ids - spec_ids)
    print(f"## {engine}: {len(e_def)} evidence, {len(q_def)} questions, {len(code)} code files")
    for pr in problems:
        print(f"  FIX  {pr}")
    print(f"  trace: {len(unimplemented)} spec sections whose evidence no code cites"
          + "".join(f"\n      {u[:110]}" for u in unimplemented[:8]) + ("\n      ..." if len(unimplemented) > 8 else ""))
    print(f"  trace: {len(orphan)} evidence ids cited in code but in no spec section"
          + (f": {' '.join('E-' + o for o in orphan[:12])}" if orphan else ""))
    return len(problems)


def selftest() -> None:
    t = ("### E-0001 — <one-line claim>\n### E-0001 — x\n### E-0001 — y\n### E-0002 — z\n"
         "### E-0002 UPDATE (date) — more\n### E-0003\n")
    assert defined(t, "E") == Counter({"0001": 2, "0002": 1, "0003": 1}), defined(t, "E")
    assert cited("see E-0100 and Q-0003, not E-12") == {("E", "0100"), ("Q", "0003")}
    s = sections("## Fades\nE-0700 E-0701\n### Score\nnone\n## Ambience\nE-0705")
    assert s == [("Fades", {"0700", "0701"}), ("Score", set()), ("Ambience", {"0705"})], s
    print("doclint selftest ok")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
    elif a == ["--all"]:
        sys.exit(1 if sum(check(e) for e in ENGINES) else 0)
    elif len(a) == 1:
        sys.exit(1 if check(a[0]) else 0)
    else:
        print(__doc__)
        sys.exit(2)
