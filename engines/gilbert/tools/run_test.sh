#!/bin/sh
# Runs the engine unattended and off-screen (no window on the desktop): SDL's offscreen video
# driver with the software renderer; snapshots come from the engine's own page (dev.cpp).
#   engines/gilbert/tools/run_test.sh "<dev_input>" [seconds] [extra debug flags] [extra ini line]
# Uses a copy of C:\scummvm\scummvm.exe (C:\tmp\scummvm-gilbert.exe), the dev ini with the
# logos skipped, saves in C:\tmp\gilsaves; the log goes to C:\tmp\gil-run.log.
set -e
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p /c/tmp/gilsaves
cp /c/scummvm/scummvm.exe /c/tmp/scummvm-gilbert.exe
sed -e 's#^gfx_mode=.*#gfx_mode=surfacesdl#' "$here/scummvm.ini" > /c/tmp/gil-test.ini
printf 'savepath=C:/tmp/gilsaves\n' | sed -i '/^\[scummvm\]/r /dev/stdin' /c/tmp/gil-test.ini
printf 'dev_skip_logos=true\ndev_input=%s\n' "$1" >> /c/tmp/gil-test.ini
if [ -n "$4" ]; then printf '%s\n' "$4" >> /c/tmp/gil-test.ini; fi
cd /c/tmp
SDL_VIDEODRIVER=offscreen PATH=/c/msys64/ucrt64/bin:$PATH timeout "${2:-120}" ./scummvm-gilbert.exe \
	-c 'C:\tmp\gil-test.ini' -d1 --debugflags=Script${3:+,$3} gilbert > /c/tmp/gil-run.log 2>&1 || true
grep -vE 'HardwareInput|^SDL|OpenGL|Antialiasing|^Checking' /c/tmp/gil-run.log | tail -n 40
