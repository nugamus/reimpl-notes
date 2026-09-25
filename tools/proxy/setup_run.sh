#!/usr/bin/env bash
# Build (or refresh) the run folder the proxies trace in. Idempotent.
#   bash tools/proxy/setup_run.sh [run-dir]        # default /c/MonetRun
# Copies the 02_PR binaries and Data/ (never modifies Original Game Files/, rule 7), adds
# dgVoodoo2 configured for windowed play, installs the tracing proxies, and patches the
# copied exe (tools/proxy/patch_exe.py). Launch with tools/proxy/run.ps1.
set -euo pipefail
repo="$(cd "$(dirname "$0")/../.." && pwd)"
run=${1:-/c/MonetRun}
src="$repo/Original Game Files"
dg="$repo/third_party/dgVoodoo2_87_3"

mkdir -p "$run"
if [ ! -f "$run/x3d_orig.dll" ]; then
    cp -r "$src/INSTALL/02_PR/." "$run/"
    mv "$run/x3d.dll" "$run/x3d_orig.dll"
    mv "$run/h3d.dll" "$run/h3d_orig.dll"
fi
[ -f "$run/Data/App.bin" ] || cp -r "$src/Data" "$run/Data"
attrib -R "$(cygpath -w "$run")\\*" //S //D >/dev/null   # CD copies arrive read-only

# dgVoodoo2: 32-bit DirectDraw/D3D DLLs next to the exe, plus its config.
cp "$dg/MS/x86/DDraw.dll" "$dg/MS/x86/D3DImm.dll" "$dg/dgVoodooCpl.exe" "$run/"
cp "$dg/dgVoodoo.conf" "$run/dgVoodoo.conf"
set_key() { sed -i -E "s/^($1 +=).*/\\1 $2/" "$run/dgVoodoo.conf"; }
set_key FullScreenMode false        # a window, never fullscreen
set_key ScalingMode stretched_ar
set_key DesktopBitDepth 16          # the game's windowed mode needs a 16-bit primary surface
set_key FPSLimit 60                 # windowed rendering is otherwise uncapped (~200+ fps)
set_key dgVoodooWatermark false
set_key Resolution unforced
set_key CaptureMouse false          # do not trap the mouse in the window

# Tracing proxies (build them first: see tools/proxy/README.md, Build).
cp "$repo/build/proxy/Release/x3d.dll" "$repo/build/proxy/Release/h3d.dll" "$run/"
python "$repo/tools/proxy/patch_exe.py" --run "$(cygpath -w "$run")"
echo "run folder ready: $run"
