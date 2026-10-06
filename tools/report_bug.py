"""One-click bug report from a play folder (desktop shortcut "Report a game bug").

Run right after seeing a bug while playing. It asks which game (or takes it as an argument),
then gathers from that game's play folder (C:\\<Game>Play) the newest screenshot (ScummVM's
screenshot key, Alt+S, saves into the play folder's screenshots), the newest save, the
newest event recording (if you played with Record), and scummvm.log, into
`bugs/<date>-<game>/` (gitignored: these hold game imagery and saves), then opens a new
GitHub issue in the browser with the form filled in and the folder's path in it. Attach
nothing there; agents read the folder.

    python tools/report_bug.py                 # asks for the game
    python tools/report_bug.py grumpa "Grumpa walks through the table"
    python tools/report_bug.py --selftest
"""

from __future__ import annotations

import shutil
import sys
import time
import urllib.parse
import webbrowser
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
def play_folders() -> dict[str, tuple[str, str]]:
    """engine -> (game title, play folder), read from tools/play/play-*.bat, so a new game's
    play launcher is all it takes."""
    import re
    out = {}
    for bat in sorted((REPO / "tools" / "play").glob("play-*.bat")):
        text = bat.read_text(encoding="utf-8", errors="replace")
        call = re.search(r'_play\.bat"\s+(\w+)\s+(\S+)', text)
        title = re.search(r"rem Play (.+?) in ScummVM", text)
        if call:
            out[call.group(1)] = (title.group(1) if title else call.group(1), call.group(2))
    return out


PLAY = play_folders()
FORM_GAME = {e: f"{t} ({e})" for e, (t, _) in PLAY.items()}  # matches the issue form's options


def newest(folder: Path, patterns: list[str]) -> Path | None:
    files = [f for p in patterns for f in folder.rglob(p) if f.is_file()]
    return max(files, key=lambda f: f.stat().st_mtime) if files else None


def gather(engine: str, what: str, play: Path, out_root: Path) -> tuple[Path, list[str]]:
    name, _ = PLAY[engine]
    out = out_root / f"{time.strftime('%Y-%m-%d-%H%M')}-{engine}"
    out.mkdir(parents=True, exist_ok=True)
    found = []
    for label, pats in [("screenshot", ["scummvm-*.png", "*.png"]), ("save", ["saves/*"]),
                        ("recording", ["*.rec", "saves/*.rec"]), ("log", ["scummvm.log"])]:
        f = newest(play, pats)
        if f:
            shutil.copy2(f, out / f.name)
            found.append(f"{label}: {f.name}")
    (out / "README.txt").write_text(f"{name}: {what}\nfrom {play}\n" + "\n".join(found) + "\n", encoding="utf-8")
    return out, found


def issue_url(engine: str, what: str, folder: Path, found: list[str]) -> str:
    body_where = f"Bug folder on the dev PC: `{folder}`\n\n" + "\n".join(f"- {f}" for f in found)
    q = {"template": "bug.yml", "title": f"{PLAY[engine][0]}: {what}", "labels": f"bug,{engine}",
         "engine": FORM_GAME[engine], "what": what, "where": body_where, "save": str(folder)}
    return "https://github.com/nugamus/reimpl-notes/issues/new?" + urllib.parse.urlencode(q)


def main(argv: list[str]) -> int:
    engine = argv[0] if argv else ""
    while engine not in PLAY:
        engine = input(f"Which game? ({', '.join(f'{k} = {v[0]}' for k, v in PLAY.items())}): ").strip().lower()
    what = " ".join(argv[1:]) or input("What went wrong, in one line: ").strip() or "bug"
    folder, found = gather(engine, what, Path(PLAY[engine][1]), REPO / "bugs")
    print(f"Saved to {folder}:\n  " + "\n  ".join(found or ["nothing found in the play folder"]))
    webbrowser.open(issue_url(engine, what, folder, found))
    return 0


def selftest() -> None:
    import tempfile

    tmp = Path(tempfile.mkdtemp())
    play = tmp / "play"
    (play / "saves").mkdir(parents=True)
    (play / "scummvm-grumpa-00001.png").write_bytes(b"png")
    (play / "saves" / "grumpa.001").write_bytes(b"save")
    (play / "scummvm.log").write_text("log")
    out, found = gather("grumpa", "test", play, tmp / "bugs")
    assert sorted(p.name for p in out.iterdir()) == ["README.txt", "grumpa.001", "scummvm-grumpa-00001.png", "scummvm.log"]
    url = issue_url("grumpa", "walks through the table", out, found)
    assert "template=bug.yml" in url and "labels=bug%2Cgrumpa" in url
    shutil.rmtree(tmp)
    print("report_bug selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        sys.exit(main(sys.argv[1:]))
