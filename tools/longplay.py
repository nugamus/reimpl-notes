# /// script
# requires-python = ">=3.11"
# dependencies = ["yt-dlp", "imageio-ffmpeg"]
# ///
"""Frames from a recorded playthrough of the original, as a visual reference for a scene
without running the original at all.

Downloads the video once (yt-dlp, cached in build/longplay/), then extracts a frame at each
timestamp with ffmpeg into `engines/<engine>/traces/longplay/` (gitignored with the other
captures: it is the original's imagery, never committed). Look at the frames with Read and
compare them with a scenario snap of the same scene.

    uv run tools/longplay.py grumpa https://www.youtube.com/watch?v=XXXX 0:42 12:05 1:03:10
    uv run tools/longplay.py grumpa C:/videos/grumpa-longplay.mp4 5:00     # a local file
    uv run tools/longplay.py --selftest
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CACHE = REPO / "build" / "longplay"


def seconds(ts: str) -> float:
    parts = [float(p) for p in ts.split(":")]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def fetch(source: str) -> Path:
    if Path(source).exists():
        return Path(source)
    import yt_dlp

    CACHE.mkdir(parents=True, exist_ok=True)
    opts = {"outtmpl": str(CACHE / "%(id)s.%(ext)s"), "format": "bv*[height<=720][ext=mp4]/bv*[height<=720]/b",
            "quiet": True, "noprogress": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(source, download=True)
        return Path(ydl.prepare_filename(info))


def frames(engine: str, source: str, stamps: list[str]) -> list[Path]:
    import imageio_ffmpeg

    video = fetch(source)
    out = REPO / "engines" / engine / "traces" / "longplay"
    out.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    made = []
    for ts in stamps:
        dst = out / f"{video.stem}_{ts.replace(':', '-')}.png"
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-ss", str(seconds(ts)), "-i", str(video),
                        "-frames:v", "1", str(dst)], check=True)
        made.append(dst)
        print(dst.relative_to(REPO))
    return made


def selftest() -> None:
    import imageio_ffmpeg

    assert seconds("1:03:10") == 3790 and seconds("0:42") == 42 and seconds("90") == 90
    tmp = CACHE / "selftest.mp4"
    CACHE.mkdir(parents=True, exist_ok=True)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    "testsrc=duration=3:size=320x240:rate=10", str(tmp)], check=True)
    made = frames("_selftest", str(tmp), ["0:01", "0:02"])
    assert all(p.exists() and p.stat().st_size > 1000 for p in made)
    for p in made:
        p.unlink()
    (REPO / "engines" / "_selftest" / "traces" / "longplay").rmdir()
    (REPO / "engines" / "_selftest" / "traces").rmdir()
    (REPO / "engines" / "_selftest").rmdir()
    tmp.unlink()
    print("longplay selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif len(sys.argv) >= 4:
        frames(sys.argv[1], sys.argv[2], sys.argv[3:])
    else:
        print(__doc__)
        sys.exit(2)
