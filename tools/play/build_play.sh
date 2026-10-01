#!/bin/bash
# Builds the latest committed engines (branch monet) in their own worktree and installs them,
# with their DLLs and data files, in a play folder (argument, default C:\MonetPlay) for
# playing like a normal user. Runs inside MSYS2 UCRT64 (_play.bat starts it). Development
# builds in C:\scummvm are never touched, so a running game does not lock them and half-done
# work never ships.
# One worktree builds every played engine, without debug symbols, so a commit is compiled
# once for all play folders, and nothing is built or copied when monet has not moved.
set -e
git() { "/c/Program Files/Git/cmd/git.exe" "$@"; } # MSYS2 has no git: Git for Windows
SRC=/c/scummvm-play
OUT=${1:-/c/MonetPlay}
WIN_OUT=$(cygpath -m "$OUT")
FLAGS="--disable-all-engines --enable-engine=x3d,peintre,gilbert,grumpa --enable-optimizations --disable-debug"
COMMIT=$(git -C /c/scummvm rev-parse monet)
if [ ! -d "$SRC" ]; then
	git -C /c/scummvm worktree add --detach "$SRC" monet
fi
if [ "$(cat "$SRC/.play-built" 2>/dev/null)" != "$COMMIT" ]; then
	git -C "$SRC" checkout -q --detach monet
	echo "Building: $(git -C "$SRC" log --oneline -1)"
	# Configure when unconfigured (fresh, or an interrupted create) or configured otherwise.
	grep -q "^SAVED_CONFIGFLAGS *:= $FLAGS\$" "$SRC/config.mk" 2>/dev/null ||
		(cd "$SRC" && ./configure $FLAGS)
	make -C "$SRC" -j16
	echo "$COMMIT" > "$SRC/.play-built"
fi
if [ "$(cat "$OUT/.play-built" 2>/dev/null)" != "$COMMIT" ]; then
	echo "Installing in $WIN_OUT"
	mkdir -p "$OUT/saves"
	cp "$SRC/scummvm.exe" "$OUT/"
	ldd "$SRC/scummvm.exe" | awk '$3 ~ /ucrt64/ {print $3}' | xargs -I{} cp {} "$OUT/"
	cp "$SRC"/gui/themes/*.dat "$SRC"/gui/themes/*.zip "$SRC"/dists/engine-data/fonts.dat "$OUT/"
	echo "$COMMIT" > "$OUT/.play-built"
fi
if [ ! -f "$OUT/scummvm.ini" ]; then
	cat > "$OUT/scummvm.ini" <<INI
[scummvm]
themepath=$WIN_OUT
extrapath=$WIN_OUT
savepath=$WIN_OUT/saves
INI
fi
# The engines are in development: no "unsupported game" dialog before each start.
grep -q enable_unsupported_game_warning "$OUT/scummvm.ini" ||
	sed -i '/^\[scummvm\]/a enable_unsupported_game_warning=false' "$OUT/scummvm.ini"
