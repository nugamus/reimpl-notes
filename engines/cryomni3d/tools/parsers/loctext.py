"""China's text files in DATA/LOC (DIAL, LABELS, LISTE, MINUTES, Fichetxt, CREDITS).

Grammar and reader behaviour: engines/cryomni3d/docs/formats/README.md, section "LOC
text files" (E-0200..E-0205). Bytes are Windows-1252, lines end in CR LF. Each file has
its own reader in CHINE.EXE; this validator follows each reader's rules and also checks
that every byte is part of a token, whitespace or a comment (strict grammar), so a file
the game would accept only by its loose scanning is still reported.

    python engines/cryomni3d/tools/parsers/loctext.py            # validate the corpus
    python engines/cryomni3d/tools/parsers/loctext.py --selftest
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
LOC = REPO / "games/china/discs/en-iso/cd1/CHINE/DATA/LOC"
WS = b" \t\r\n"


class FormatError(Exception):
    pass


def dec(b: bytes) -> str:
    return b.decode("cp1252", errors="replace")


class Cur:
    """A cursor over the file that accounts for every byte it passes."""

    def __init__(self, blob: bytes, comments: bool = False):
        self.b, self.p, self.comments = blob, 0, comments

    def eof(self) -> bool:
        return self.p >= len(self.b)

    def line(self) -> int:
        return self.b.count(b"\n", 0, self.p) + 1

    def err(self, msg: str) -> FormatError:
        return FormatError(f"line {self.line()}: {msg}")

    def ws(self) -> None:
        """Whitespace, and `/`-to-CR comments where the reader allows them."""
        while not self.eof():
            c = self.b[self.p]
            if c in WS:
                self.p += 1
            elif self.comments and c == 0x2F:  # '/': skipped up to the next CR
                e = self.b.find(b"\r", self.p)
                self.p = len(self.b) if e < 0 else e
            else:
                break

    def peek(self, s: bytes) -> bool:
        return self.b.startswith(s, self.p)

    def delim(self, open_: bytes, close: bytes, oneline: bool, forbid: bytes = b"") -> bytes:
        if not self.peek(open_):
            raise self.err(f"expected {open_!r}")
        s = self.p + len(open_)
        e = self.b.find(close, s)
        if e < 0:
            raise self.err(f"unterminated {open_!r}")
        body = self.b[s:e]
        if oneline and (b"\r" in body or b"\n" in body):
            raise self.err(f"line break inside {open_!r}..{close!r}")
        for f in forbid:
            if f in body:
                raise self.err(f"{chr(f)!r} inside {open_!r}..{close!r}")
        self.p = e + len(close)
        return body


# --- DIAL.TXT: Dial::parse 0x404190, Dial::resolveGotos 0x404150 (E-0200) -------------
def read_dial(blob: bytes) -> dict:
    c, blocks = Cur(blob, comments=True), []
    while True:
        c.ws()
        if c.eof():
            break
        ident = c.delim(b"#", b"#", True)
        c.ws()
        text = c.delim(b"<", b">", True)
        c.ws()
        if c.b[c.p:c.p + 4].lower() != b"goto":
            raise c.err("expected GOTO")
        c.p += 5  # the reader skips 'GOTO' and one more byte unseen
        if c.b[c.p - 1] not in b" ":
            raise c.err("GOTO not followed by a space")
        e = c.p
        while e < len(blob) and blob[e] not in b"\r\n":
            e += 1
        target = blob[c.p:e].lstrip(b" ")
        c.p = e
        blocks.append((ident.lower(), dec(text), target.lower()))
    if len(blocks) > 700:
        raise FormatError(f"{len(blocks)} blocks, the reader holds 700")
    ids = {b[0] for b in blocks}
    if len(ids) != len(blocks):
        raise FormatError("duplicate block id")
    bad = [t for _, _, t in blocks if t != b"fin" and t not in ids]
    if bad:
        raise FormatError(f"GOTO to unknown ids {bad[:5]}")
    return {"blocks": len(blocks), "fin": sum(t == b"fin" for _, _, t in blocks)}


# --- LABELS.TXT: Label::parse 0x410300 (E-0201) -----------------------------------------
def read_labels(blob: bytes) -> dict:
    c, labels = Cur(blob, comments=True), []
    while True:
        c.ws()
        if c.eof():
            break
        ident = c.delim(b"#", b"#", True)
        c.ws()
        text = c.delim(b"<", b">", False)
        labels.append((ident.lower(), dec(text)))
    if len(labels) > 450:
        raise FormatError(f"{len(labels)} labels, the reader holds 450")
    return {"labels": len(labels), "dups": len(labels) - len({k for k, _ in labels})}


# --- MINUTES.TXT: Minutes::load 0x4119f0, Minutes::parse 0x411900 (E-0202) --------------
def read_minutes(blob: bytes) -> dict:
    c, items = Cur(blob), []
    while True:
        c.ws()
        if c.eof():
            break
        ident = c.delim(b"#", b"#", True)
        c.ws()
        text = c.delim(b"<", b">", False, forbid=b"#")
        items.append((ident, dec(text)))
    if len(items) > 50:
        raise FormatError(f"{len(items)} minutes, the reader holds 50")
    return {"minutes": len(items)}


# --- LISTE.TXT: Interface::loadIndex 0x40b3e0 (E-0203) ----------------------------------
def read_liste(blob: bytes) -> dict:
    """Strict grammar: `##C` letter lines, `##name##` + `<title>` sections, `#id#` +
    `<text>` entries. Then the game's own scan (index_rows) gives the rows it builds."""
    c, kinds = Cur(blob), {"letter": 0, "section": 0, "entry": 0, "orphan": 0}
    while True:
        c.ws()
        if c.eof():
            break
        if c.peek(b"##"):
            e = c.b.find(b"\r", c.p)
            ln = c.b[c.p:e]
            if ln.endswith(b"##") and len(ln) > 4:
                c.p = e
                c.ws()
                c.delim(b"<", b">", True)
                kinds["section"] += 1
            elif len(ln) == 3:
                c.p = e
                kinds["letter"] += 1
            else:
                raise c.err(f"bad header {ln!r}")
        elif c.peek(b"<"):  # text with no #id#: the game's scan passes over it
            c.delim(b"<", b">", True, forbid=b"#")
            kinds["orphan"] += 1
        else:
            c.delim(b"#", b"#", True)
            c.ws()
            c.delim(b"<", b">", True, forbid=b"#")
            kinds["entry"] += 1
    rows = index_rows(blob)
    if sum(r[0] == "id" for r in rows) != kinds["entry"]:
        raise FormatError("game scan and grammar disagree on entries")
    return {**kinds, "rows": len(rows), "headers": sum(r[0] == "hdr" for r in rows)}


def zero_line_ends(blob: bytes) -> bytearray:
    """0x40a5b0: outside <...>, every CR and the byte after it become NUL."""
    b, inside = bytearray(blob) + b"\0\0", False
    for i in range(len(blob)):
        if b[i] == 0x3C:
            inside = True
        elif b[i] == 0x3E:
            inside = False
        elif b[i] == 0x0D and not inside:
            b[i] = b[i + 1] = 0
    return b


def index_rows(blob: bytes) -> list:
    """The rows 0x40b3e0 builds: ('hdr', '-C-') per group, ('id', 'id/text') per entry."""
    b, n, u, rows = zero_line_ends(blob), len(blob), 0, []
    while u < n:
        while u < n and b[u] != 0x23:
            u += 1
        while u < n and b[u] == 0x23:
            u += 1
        ch = b[u]
        while u < n and b[u] != 0x23:
            u += 1
        if b[u] == 0x23 and b[u + 1] == 0x23:
            continue  # a `##name##` line: no group
        rows.append(("hdr", "-" + (chr(ch) if ch else "") + "-"))
        while u < n:
            u += 1  # past '#'
            e = b.index(b"#", u)
            ident = bytes(b[u:e])
            u = b.index(b"<", e) + 1
            e = b.index(b">", u)
            rows.append(("id", dec(ident) + "/" + dec(bytes(b[u:e]))))
            while u < n and b[u] != 0x23:
                u += 1
            if b[u] == 0x23 and b[u + 1] == 0x23:
                break
    return rows


# --- Fichetxt.txt: Interface::loadDoc 0x40a5f0 (E-0204) ---------------------------------
def skip_to(c: Cur, want: bytes, errs: bytes, st: dict) -> None:
    """The reader scans to `want` and fails only on `errs`; other non-blank bytes on the
    way (a repeated `!089!` line in the corpus) are counted as skipped."""
    c.ws()
    while not c.eof() and not c.peek(want):
        if c.b[c.p] in errs:
            raise c.err(f"{chr(c.b[c.p])!r} before {want!r}")
        st["skipped"] += c.b[c.p] not in WS
        c.p += 1


def links(c: Cur, stop: bytes, st: dict) -> list:
    """Up to 10 `$link$`. The reader's scan for the next `$` passes over any byte but
    `stop` and `$`; such stray bytes (a comma in the corpus) are counted as skipped."""
    out = []
    while True:
        c.ws()
        while not c.eof() and c.b[c.p] not in stop + b"$" + WS:
            st["skipped"] += 1
            c.p += 1
            c.ws()
        if not c.peek(b"$"):
            return out
        out.append(c.delim(b"$", b"$", True))
        if len(out) > 10:
            raise c.err("more than 10 links")


def read_fiches(blob: bytes) -> dict:
    c = Cur(blob)
    st = {"themes": 0, "fiches": 0, "picture": 0, "table": 0, "rows": 0, "links": 0,
          "max_fiches": 0, "max_rows": 0, "skipped": 0}
    last_dollars = 0  # the reader's link-count check carries over (see README)
    while True:
        c.ws()
        if c.eof():
            break
        if not c.peek(b"##") or c.peek(b"###"):
            raise c.err("expected ##theme##")
        c.p += 1
        c.delim(b"#", b"##", True)
        c.ws()
        c.delim(b"<", b">", True)
        st["themes"] += 1
        nf = 0
        while True:
            c.ws()
            if c.peek(b"###"):
                c.p += 3
                break
            c.delim(b"#", b"#", True, forbid=b"<")
            c.ws()
            c.delim(b"<", b">", True, forbid=b"#")
            c.ws()
            tga = c.delim(b"!", b"!", True, forbid=b"<")
            nf += 1
            if tga:
                st["picture"] += 1
                skip_to(c, b"<", b">#", st)
                c.delim(b"<", b">", False, forbid=b"#")  # caption
                c.ws()
                text = c.delim(b"<", b">", False, forbid=b"<#")
                ls = links(c, b"#", st)
                last_dollars = text.count(b"$") // 2
                if last_dollars != len(ls):
                    raise c.err(f"{last_dollars} $..$ in text, {len(ls)} links")
            else:
                st["table"] += 1
                if last_dollars:
                    raise c.err("table fiche after a picture fiche with links")
                nr, ls = 0, []
                while True:
                    c.ws()
                    if not c.peek(b"<"):
                        break
                    c.delim(b"<", b">", False, forbid=b"#")
                    c.ws()
                    c.delim(b"<", b">", False, forbid=b"#")
                    ls += links(c, b"<#", st)
                    nr += 1
                if nr > 20:
                    raise c.err(f"{nr} rows, the table holds 20")
                st["rows"] += nr
                st["max_rows"] = max(st["max_rows"], nr)
            st["links"] += len(ls)
            c.ws()
            if not c.peek(b"##") or c.peek(b"###"):
                raise c.err("expected ## after a fiche")
            c.p += 2
        if nf > 50:
            raise c.err(f"{nf} fiches in a theme, the reader holds 50")
        st["fiches"] += nf
        st["max_fiches"] = max(st["max_fiches"], nf)
    return st


# --- CREDITS.TXT: credits::run 0x403b10 (E-0205) ----------------------------------------
def read_credits(blob: bytes) -> dict:
    if not blob.endswith(b"\r\n") or blob.count(b"\n") != blob.count(b"\r\n"):
        raise FormatError("lines must end in CR LF")
    if b"<" in blob or b">" in blob:
        raise FormatError("< or > would stop the line-end zeroing")
    lines = blob[:-2].split(b"\r\n")
    pages, cur, end = [], [], None
    for i, ln in enumerate(lines):
        if ln.startswith(b"##"):
            end = i
            break
        if ln[:1] == b"/" or ln[1:2] == b"/":
            if ln.strip(b"/"):
                raise FormatError(f"line {i + 1}: page break line carries text")
            pages.append(cur)
            cur = []
            continue
        if not cur and not ln and pages:
            continue  # blank lines after a page break are skipped with it
        cur.append(ln)
    pages.append(cur)
    if end is None:
        raise FormatError("no ## end line")
    if any(len(p) > 30 for p in pages):
        raise FormatError("a page has more than 30 lines")
    tail = lines[end + 1:]
    if any(t.strip() for t in tail):
        raise FormatError("text after ##")
    heads = sum(ln.startswith(b"#") for p in pages for ln in p)
    return {"pages": len(pages), "lines": sum(map(len, pages)), "headings": heads,
            "max_lines": max(map(len, pages))}


READERS = {
    "DIAL.TXT": read_dial, "LABELS.TXT": read_labels, "MINUTES.TXT": read_minutes,
    "LISTE.TXT": read_liste, "FICHETXT.TXT": read_fiches, "CREDITS.TXT": read_credits,
}


def encoding_note(blob: bytes) -> str:
    c1 = sorted({b for b in blob if 0x80 <= b < 0xA0})
    return f"hi={sum(b >= 0x80 for b in blob)}" + (f" C1={[hex(x) for x in c1]}" if c1 else "")


def selftest() -> None:
    d = read_dial(b"#A1#\r\n<Hi.>\r\nGOTO b1\r\n\r\n/ note\r\n#B1#\r\n<Yes.>\r\ngoto FIN\r\n")
    assert d == {"blocks": 2, "fin": 1}, d
    for bad in (b"#A#\r\n<x>\r\nGOTO Z\r\n", b"#A#\r\n<x\r\ny>\r\nGOTO FIN\r\n"):
        try:
            read_dial(bad)
            raise AssertionError(bad)
        except FormatError:
            pass
    assert read_labels(b"//c\r\n#a#\r\n<x\r\ny>\r\n")["labels"] == 1
    assert read_minutes(b"#M1#\r\n<a\r\nb>\r\n")["minutes"] == 1
    li = read_liste(b"##A\r\n#f 1#\r\n<Alpha>\r\n##Sec##\r\n<S>\r\n#f 2#\r\n<Beta>\r\n")
    assert li["rows"] == 4 and li["headers"] == 2, li
    assert index_rows(b"##A\r\n#f 1#\r\n<Alpha>\r\n")[1] == ("id", "f 1/Alpha")
    f = read_fiches(b"##T##\r\n<Theme>\r\n#f1#\r\n<A>\r\n!001!\r\n<cap>\r\n\r\n<x $y$ z>\r\n"
                    b"$f2$\r\n##\r\n###\r\n")
    assert f["fiches"] == 1 and f["links"] == 1, f
    cr = read_credits(b"#Head\r\nName\r\n//\r\n\r\nOther\r\n##\r\n")
    assert cr == {"pages": 2, "lines": 3, "headings": 1, "max_lines": 2}, cr
    print("selftest ok")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("folder", nargs="?", type=Path, default=LOC)
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    ok = total = 0
    for p in sorted(a.folder.iterdir()):
        r = READERS.get(p.name.upper())
        if not r:
            continue
        total += 1
        blob = p.read_bytes()
        try:
            res = r(blob)
            ok += 1
            print(f"ok   {p.name}: {res} {encoding_note(blob)}")
        except FormatError as e:
            print(f"FAIL {p.name}: {e}")
    print(f"{ok}/{total} LOC text files parsed, every byte accounted for")
    return 0 if ok == total == 6 else 1


if __name__ == "__main__":
    sys.exit(main())
