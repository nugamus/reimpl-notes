"""A page to look at an engine's state: every scenario with its reference snaps, the latest
difference sheet if it changed, and frames of the original for the same moment when we have
them (`engines/<engine>/traces/original/<scenario>/*.png`, captured with snap.ps1, or
`traces/longplay/` frames named `<scenario>-*.png`). Writes build/review/<engine>.html
(local only, it shows game imagery) and opens it in the browser.

    python tools/review_page.py grumpa
    python tools/review_page.py --all
"""

from __future__ import annotations

import html
import sys
import tomllib
import webbrowser
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ENGINES = [l.split()[0] for l in (REPO / "tools" / "engines.txt").read_text().splitlines()
           if l.strip() and not l.startswith("#")]


def img(path: Path, caption: str) -> str:
    return (f'<figure><a href="{path.as_uri()}"><img src="{path.as_uri()}" loading="lazy"></a>'
            f"<figcaption>{html.escape(caption)}</figcaption></figure>")


def build(engine: str) -> Path:
    t = REPO / "engines" / engine / "tests"
    traces = REPO / "engines" / engine / "traces"
    parts = [f"<h1>{engine}: scenarios</h1>"]
    for sc in sorted(t.glob("*.toml")):
        if sc.name.startswith(("save_", "_")):
            continue
        meta = tomllib.loads(sc.read_text(encoding="utf-8"))
        figs = []
        for snap in meta.get("snaps", []):
            ref = t / "golden" / sc.stem / snap
            if ref.exists():
                figs.append(img(ref, f"reference {snap}"))
            cmp_png = t / "out" / sc.stem / (Path(snap).stem + "-compare.png")
            if cmp_png.exists() and (not ref.exists() or cmp_png.stat().st_mtime > ref.stat().st_mtime):
                figs.append(img(cmp_png, f"CHANGED {snap}: reference | now | changed pixels"))
        for orig in sorted((traces / "original" / sc.stem).glob("*.png")):
            figs.append(img(orig, f"original: {orig.name}"))
        for frame in sorted((traces / "longplay").glob(f"{sc.stem}-*.png")):
            figs.append(img(frame, f"original (playthrough): {frame.name}"))
        parts.append(f"<section><h2>{sc.stem}</h2><p>{html.escape(meta.get('description', ''))}</p>"
                     f"<div class=row>{''.join(figs) or '<p>no images yet: run the scenario</p>'}</div></section>")
    out = REPO / "build" / "review" / f"{engine}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("<!doctype html><meta charset=utf-8><title>" + engine + " review</title><style>"
                   "body{font-family:sans-serif;margin:2em;background:#111;color:#ddd}"
                   ".row{display:flex;flex-wrap:wrap;gap:12px}figure{margin:0}"
                   "img{max-width:420px;border:1px solid #444}figcaption{font-size:12px}"
                   "section{border-top:1px solid #333;padding:1em 0}</style>" + "".join(parts), encoding="utf-8")
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    for e in (ENGINES if a == ["--all"] else a):
        page = build(e)
        print(page)
        if a != ["--all"]:
            webbrowser.open(page.as_uri())
