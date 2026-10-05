#!/usr/bin/env bash
# Build (or refresh) C:\SunlightRun, a runnable copy of Mission Sunlight for answering
# precise questions. Idempotent.
#   bash engines/peintre/tools/run/setup_run.sh [run-dir]
# - copies Data/ from the CD folder (never modifies games/mission-sunlight/discs) and
#   Data/mission.___ as mission.exe;
# - dgVoodoo2's DirectDraw (32-bit) next to the exe, windowed (the EXE's windowed flag
#   0x4b0054 is already 1);
# - patches the copy (patch_exe.py: registry key read from HKCU);
# - writes HKCU\Software\Cryo\Mission Sunlight: Path\Target and Path\CD = the run folder
#   with a trailing backslash, Language\LOC = 0, Install Level\IL = 3 (boot.md "Data root").
#   Remove with: reg delete "HKCU\Software\Cryo\Mission Sunlight" /f
set -euo pipefail
repo="$(cd "$(dirname "$0")/../../../.." && pwd)"
run=${1:-/c/SunlightRun}
src="$repo/games/mission-sunlight/discs/cd"
dg="$repo/third_party/dgVoodoo2_87_3"

mkdir -p "$run"
[ -d "$run/DATA" ] || cp -r "$src/Data" "$run/DATA"
cp "$src/Data/mission.___" "$run/mission.exe"
mkdir -p "$run/SAVE"
attrib -R "$(cygpath -w "$run")\*" //S //D >/dev/null

cp "$dg/MS/x86/DDraw.dll" "$dg/dgVoodooCpl.exe" "$run/"
cp "$dg/dgVoodoo.conf" "$run/dgVoodoo.conf"
set_key() { sed -i -E "s/^($1 +=).*/\1 $2/" "$run/dgVoodoo.conf"; }
set_key FullScreenMode false
set_key ScalingMode stretched_ar
set_key DesktopBitDepth 16
set_key FPSLimit 60
set_key dgVoodooWatermark false
set_key Resolution unforced
set_key CaptureMouse false

python "$repo/engines/peintre/tools/run/patch_exe.py" --run "$(cygpath -w "$run")"

win="$(cygpath -w "$run")\\"
key='HKCU\Software\Cryo\Mission Sunlight'
reg add "$key\Path" //v Target //t REG_SZ //d "$win" //f >/dev/null
reg add "$key\Path" //v CD //t REG_SZ //d "$win" //f >/dev/null
reg add "$key\Language" //v LOC //t REG_DWORD //d 0 //f >/dev/null
reg add "$key\Install Level" //v IL //t REG_DWORD //d 3 //f >/dev/null
echo "run folder ready: $run"
