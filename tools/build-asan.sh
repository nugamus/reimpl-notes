#!/bin/bash
# tools/build-asan.sh <engine>: builds the engine's dev worktree with AddressSanitizer and
# UndefinedBehaviorSanitizer (MSYS2 CLANG64) out of tree in C:\scummvm-asan\<engine>, so it
# never disturbs the normal build. `uv run tools/scenario.py <engine> --asan` then runs the
# scenarios on it and reports memory errors (overflows, use-after-free, uninitialised
# reads become crashes with a source line) found while they play. Dr. Memory, the usual
# tool for this, crashes on current Windows 11; ASan does not.
set -o pipefail
ENGINE=${1:?usage: build-asan.sh <engine>}
if [ "$MSYSTEM" != CLANG64 ]; then
	exec /c/msys64/usr/bin/env MSYSTEM=CLANG64 CHERE_INVOKING=1 /c/msys64/usr/bin/bash -lc \
		"bash '$(cygpath -u "$0")' $ENGINE"
fi
SRC=/c/scummvm-dev/$ENGINE
OUT=/c/scummvm-asan/$ENGINE
[ -d "$SRC" ] || { echo "no worktree $SRC"; exit 1; }
mkdir -p "$OUT" && cd "$OUT" || exit 1
# The engine and its subengines (cryomni3d: versailles, ...): --disable-all-engines drops them.
ENGINES=$(awk -F'"' -v e="$ENGINE" '$1 == "add_engine " e " " {print e, $4}' "$SRC/engines/$ENGINE/configure.engine" | tr -s ' ' ',' | sed 's/,$//')
[ -n "$ENGINES" ] || ENGINES=$ENGINE
FLAGS="--disable-all-engines --enable-engine=$ENGINES --enable-asan --enable-ubsan --enable-optimizations"
if ! grep -q "^SAVED_CONFIGFLAGS *:= $FLAGS\$" config.mk 2>/dev/null; then
	CXX=clang++ "$SRC/configure" $FLAGS > configure.log 2>&1 || { tail -20 configure.log; exit 1; }
fi
start=$(date +%s)
make -j"$(nproc)" > build.log 2>&1
status=$?
{ grep -E "error:|Error [0-9]" build.log; grep -E "engines/$ENGINE/.*warning:" build.log; } | sort -u | head -30
echo "$ENGINE (asan): $( [ $status -eq 0 ] && echo OK || echo FAILED ) in $(( $(date +%s) - start ))s -> $OUT/scummvm.exe"
exit $status
