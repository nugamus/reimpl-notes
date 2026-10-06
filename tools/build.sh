#!/bin/bash
# tools/build.sh <engine> [make args]: builds the engine's dev worktree C:\scummvm-dev\<engine>
# (branch <engine>-dev) with ccache, configuring it the first time. Prints only errors and
# warnings, then one status line, so a build costs a few lines of context. The full log is
# C:\scummvm-dev\<engine>\build.log.
# From Git Bash: bash tools/build.sh grumpa
set -o pipefail
git() { "/c/Program Files/Git/cmd/git.exe" "$@"; } # MSYS2 has no git: Git for Windows
ENGINE=${1:?usage: build.sh <engine> [make args]}
shift
if [ "$MSYSTEM" != UCRT64 ]; then # Git Bash (MINGW64): re-run inside MSYS2 UCRT64
	exec /c/msys64/usr/bin/env MSYSTEM=UCRT64 CHERE_INVOKING=1 DEVROOT="$DEVROOT" /c/msys64/usr/bin/bash -lc \
		"bash '$(cygpath -u "$0")' $ENGINE $*"
fi
SRC=${DEVROOT:-/c/scummvm-dev}/$ENGINE # DEVROOT: a parallel agent's tree
[ -d "$SRC" ] || { echo "no worktree $SRC (git -C /c/scummvm worktree add $SRC $ENGINE-dev)"; exit 1; }
cd "$SRC" || exit 1
FLAGS="--disable-all-engines --enable-engine=$ENGINE --enable-optimizations --enable-eventrecorder"
if ! grep -q "^SAVED_CONFIGFLAGS *:= $FLAGS\$" config.mk 2>/dev/null; then
	./configure $FLAGS > configure.log 2>&1 || { tail -20 configure.log; exit 1; }
fi
start=$(date +%s)
make -j"$(nproc)" CXX="ccache g++" "$@" > build.log 2>&1
status=$?
# Every error; warnings only from the engine itself (upstream code has its own).
{ grep -E "error:|Error [0-9]" build.log; grep -E "^engines/$ENGINE/.*warning:" build.log; } | sort -u | head -40
echo "$ENGINE: $( [ $status -eq 0 ] && echo OK || echo FAILED ) in $(( $(date +%s) - start ))s, $(git log --oneline -1) -> $SRC/scummvm.exe"
exit $status
