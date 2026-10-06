"""Search everything we know before reverse engineering anything new.

One full-text index (SQLite FTS5, `build/ref.sqlite`, rebuilt in about a minute) over:
  - reference/: the ArchiveTeam file-formats wiki, MultimediaWiki, the ScummVM wiki, and
    Retro Reversing (about 14,000 pages);
  - every engine's and game's docs here: specs, formats (.md and .ksy), EVIDENCE,
    OPEN-QUESTIONS, CLAUDE.md, docs/patterns/;
  - ScummVM's own headers for what it already provides: video/, image/, audio/, graphics/,
    common/formats/, and the engines' detection and decoder headers.

    python tools/ref.py build                    # (re)index; also after adding docs
    python tools/ref.py "hnm video codec"        # top hits: path, title, snippet
    python tools/ref.py -n 20 -s scummvm smacker # more hits, only one source
    python tools/ref.py --selftest

Sources for -s: formats (ArchiveTeam), multimedia, scummvm-wiki, retro, ours, scummvm-src.
Results print the path; read the page in slices if it looks right.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DB = REPO / "build" / "ref.sqlite"
SCUMMVM = Path("C:/scummvm-dev/x3d")  # any dev worktree has the same upstream tree

SOURCES = [
    ("formats", REPO / "reference" / "archiveteam_formats", "**/*.md"),
    ("multimedia", REPO / "reference" / "multimedia_cx", "**/*.md"),
    ("scummvm-wiki", REPO / "reference" / "scummvm", "**/*.md"),
    ("retro", REPO / "reference" / "retroReversing", "**/*.md"),
    ("ours", REPO / "engines", "*/docs/**/*.md"),
    ("ours", REPO / "engines", "*/docs/**/*.ksy"),
    ("ours", REPO / "engines", "*/CLAUDE.md"),
    ("ours", REPO / "games", "*/docs/**/*.md"),
    ("ours", REPO / "docs", "**/*.md"),
    ("scummvm-src", SCUMMVM, "video/*.h"),
    ("scummvm-src", SCUMMVM, "image/**/*.h"),
    ("scummvm-src", SCUMMVM, "audio/**/*.h"),
    ("scummvm-src", SCUMMVM, "graphics/**/*.h"),
    ("scummvm-src", SCUMMVM, "common/formats/*.h"),
    ("scummvm-src", SCUMMVM, "common/compression/*.h"),
]


def title_of(path: Path, text: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else path.stem


def build() -> None:
    DB.parent.mkdir(exist_ok=True)
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.execute("CREATE VIRTUAL TABLE ref USING fts5(title, body, source UNINDEXED, path UNINDEXED, "
                "tokenize='porter unicode61')")
    n = 0
    for source, root, pattern in SOURCES:
        if not root.exists():
            continue
        for path in root.glob(pattern):
            if not path.is_file() or "/.git/" in path.as_posix():
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if re.search(r"^\d+\.\s+REDIRECT\b", text, re.M) and len(text) < 400:
                continue  # wiki redirect stubs
            rel = path.relative_to(REPO).as_posix() if path.is_relative_to(REPO) else path.as_posix()
            con.execute("INSERT INTO ref VALUES (?, ?, ?, ?)", (title_of(path, text), text, source, rel))
            n += 1
    con.commit()
    con.execute("INSERT INTO ref(ref) VALUES('optimize')")
    con.close()
    print(f"indexed {n} documents -> {DB.relative_to(REPO)}")


def to_match(query: str) -> str:
    # Plain words become an AND of prefix terms; quoted phrases and FTS syntax pass through.
    if any(c in query for c in '"*:()') or re.search(r"\b(AND|OR|NOT|NEAR)\b", query):
        return query
    return " ".join(f'"{w}"*' for w in re.findall(r"\w+", query))


def search(query: str, n: int = 8, source: str | None = None) -> list[tuple]:
    if not DB.exists():
        build()
    con = sqlite3.connect(DB)
    sql = ("SELECT source, path, title, snippet(ref, 1, '[', ']', ' ... ', 18) FROM ref WHERE ref MATCH ?"
           + (" AND source = ?" if source else "") + " ORDER BY bm25(ref, 8.0, 1.0) LIMIT ?")
    try:
        for match in (to_match(query), " ".join(f'"{w}"*' for w in re.findall(r"\w+", query))):
            try:
                return con.execute(sql, (match, source, n) if source else (match, n)).fetchall()
            except sqlite3.OperationalError:
                continue  # FTS syntax in the query: retry with its plain words
        return []
    finally:
        con.close()


def selftest() -> None:
    assert to_match("hnm video") == '"hnm"* "video"*'
    assert to_match('"exact phrase"') == '"exact phrase"'
    hits = search("smacker", 5)
    assert hits and any("mack" in (h[2] + h[3]).lower() for h in hits), hits
    print(f"ref selftest ok ({len(hits)} hits for smacker)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Search the reference index")
    ap.add_argument("query", nargs="*")
    ap.add_argument("-n", type=int, default=8)
    ap.add_argument("-s", "--source")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    if a.query == ["build"]:
        build()
        return 0
    if not a.query:
        print(__doc__)
        return 2
    hits = search(" ".join(a.query), a.n, a.source)
    if not hits:
        print("no hits")
    for source, path, title, snip in hits:
        snip = re.sub(r"\s+", " ", snip)
        print(f"[{source}] {title} - {path}\n    {snip}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
