#!/bin/bash
# build_play.sh <engine> <play folder>: builds the latest commit of the engine's dev branch
# (<engine>-dev) in its own worktree and installs it, with its DLLs and data files, in the play
# folder for playing like a normal user. Runs inside MSYS2 UCRT64 (_play.bat starts it). Development
# builds in C:\scummvm are never touched, so a running game does not lock them and half-done
# work never ships.
# Each engine has its own worktree, built without debug symbols; nothing is built or copied
# when the branch has not moved.
set -e
git() { "/c/Program Files/Git/cmd/git.exe" "$@"; } # MSYS2 has no git: Git for Windows
ENGINE=$1
BRANCH=$ENGINE-dev
SRC=/c/scummvm-play-$ENGINE
OUT=$2
WIN_OUT=$(cygpath -m "$OUT")
FLAGS="--disable-all-engines --enable-engine=$ENGINE --enable-optimizations --disable-debug"
COMMIT=$(git -C /c/scummvm rev-parse "$BRANCH")
if [ ! -d "$SRC" ]; then
	git -C /c/scummvm worktree add --detach "$SRC" "$BRANCH"
fi
if [ "$(cat "$SRC/.play-built" 2>/dev/null)" != "$COMMIT" ]; then
	git -C "$SRC" checkout -q --detach "$BRANCH"
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
# The game to start: the first section with a gameid (none yet: the launcher opens).
awk '{sub(/\r$/, "")} /^\[/ {s = substr($0, 2, length($0) - 2)} /^gameid=/ {print s; exit}' \
	"$OUT/scummvm.ini" > "$OUT/.play-target"
