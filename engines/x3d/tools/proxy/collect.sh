#!/usr/bin/env bash
# Move the newest proxy traces from the run folder into engines/x3d/traces/ under a scenario name.
#   bash engines/x3d/tools/proxy/collect.sh 03-walk            # after quitting the game
# Writes engines/x3d/traces/03-walk-x3d.log, -h3d.log and -dbginfo.log (the game's own Save/DbgInfo.txt).
set -euo pipefail
name=${1:?usage: collect.sh <NN-scenario>}
run=${MONET_RUN:-/c/MonetRun}
out="$(cd "$(dirname "$0")/../.." && pwd)/traces"

for dll in x3d h3d; do
    newest=$(ls -t "$run"/monet-trace-$dll.dll-*.log 2>/dev/null | head -1 || true)
    [ -n "$newest" ] || { echo "no $dll trace in $run" >&2; exit 1; }
    mv "$newest" "$out/$name-$dll.log"
    tail -1 "$out/$name-$dll.log" | grep -q '^# [0-9]* calls' || echo "warning: $dll trace has no end marker (game killed or crashed?)"
done
[ -f "$run/Save/DbgInfo.txt" ] && cp "$run/Save/DbgInfo.txt" "$out/$name-dbginfo.log"
rm -f "$run"/monet-trace-*.log   # leftovers from aborted runs
ls -la "$out/$name"-*
echo "now add a row for $name to engines/x3d/traces/INDEX.md"
