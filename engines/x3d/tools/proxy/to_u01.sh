#!/usr/bin/env bash
# Start the original in C:\MonetRun and drive it to U01's free-roam hand-over, skipping
# what can be skipped (~2.5 min; Monet's U00 tutorial alone takes ~70 s). Needs the h3d
# proxy in background mode (run.ps1 sets it), which lets posted Enter reach the skips.
#   bash engines/x3d/tools/proxy/to_u01.sh
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
ps() { powershell -ExecutionPolicy Bypass -File "$(cygpath -w "$here/$1")" "${@:2}"; }

rm -rf /c/MonetRun/Save/*
ps run.ps1
sleep 12
ps send.ps1 -Text Name -Enter            # players screen
sleep 5
ps send.ps1 -Key 0x1B -HoldMs 70000      # held through the tutorial until the menu opens
ps send.ps1 -ClickX 376 -ClickY 37       # New game
sleep 8
ps send.ps1 -Key 0x0D -HoldMs 1500       # skip the prologue
sleep 5
for _ in $(seq 1 20); do                 # cut U01's voice lines and camera waits
    ps send.ps1 -Key 0x0D -HoldMs 600 >/dev/null
    sleep 2
done
ps camera.ps1                            # expect -466.36,-452.495,30.48,4.7,1.5708
