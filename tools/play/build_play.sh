#!/bin/bash
# Builds the latest committed engine (branch monet) in its own worktree and installs it,
# with its DLLs and data files, in C:\MonetPlay for playing like a normal user.
# Runs inside MSYS2 UCRT64 (play.bat starts it). Development builds in C:\scummvm are
# never touched, so a running game does not lock them and half-done work never ships.
set -e
git() { "/c/Program Files/Git/cmd/git.exe" "$@"; } # MSYS2 has no git: Git for Windows
SRC=/c/scummvm-play
OUT=/c/MonetPlay
if [ ! -d "$SRC" ]; then
	git -C /c/scummvm worktree add --detach "$SRC" monet
	(cd "$SRC" && ./configure --disable-all-engines --enable-engine=x3d --enable-optimizations)
fi
git -C "$SRC" checkout -q --detach monet
echo "Engine at: $(git -C "$SRC" log --oneline -1)"
make -C "$SRC" -j16 | grep -E "error|LINK" || true
[ -f "$SRC/scummvm.exe" ] || { echo "Build failed"; exit 1; }
mkdir -p "$OUT/saves"
cp "$SRC/scummvm.exe" "$OUT/"
ldd "$SRC/scummvm.exe" | awk '$3 ~ /ucrt64/ {print $3}' | xargs -I{} cp {} "$OUT/"
cp "$SRC"/gui/themes/*.dat "$SRC"/gui/themes/*.zip "$SRC"/dists/engine-data/fonts.dat "$OUT/"
if [ ! -f "$OUT/scummvm.ini" ]; then
	cat > "$OUT/scummvm.ini" <<INI
[scummvm]
themepath=C:/MonetPlay
extrapath=C:/MonetPlay
savepath=C:/MonetPlay/saves
INI
fi
