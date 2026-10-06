#!/bin/bash
# tools/linear-master.sh rebuild | append <commit>...
# The fork's master is linear: origin/master, then master's own commits (README, CI), then
# a copy of every engine commit in author-date order. No merge commits; master is never
# merged anywhere, the engine branches are what pull requests come from.
#   rebuild           recreate master from scratch (after an upstream sync)
#   append <c>...     copy these commits (just published to an engine branch) onto master
# The engine list in game.rst, the one file the engines share, resolves itself
# (resolve_engine_list.py); any other conflict stops with the worktree left for you.
set -e
REPO=${REPO:-/c/scummvm}
REMOTE=${REMOTE:-fork}
ENGINES=${ENGINES:-x3d peintre ring gilbert grumpa}
HERE=$(cd "$(dirname "$0")" && pwd)
g() { git -C "$REPO" "$@"; }
OWN_PATHS="README.md .github/workflows/engines.yml"

pick() { # cherry-pick one commit into $tmp, resolving the engine list
	local c=$1
	git -C "$tmp" cherry-pick --allow-empty --keep-redundant-commits "$c" > /dev/null 2>&1 && return
	local rst=doc/docportal/settings/game.rst
	local left
	left=$(git -C "$tmp" diff --name-only --diff-filter=U)
	# Nothing left: rerere already replayed a recorded resolution.
	if [ -z "$left" ] || { [ "$left" = "$rst" ] && python "$HERE/resolve_engine_list.py" "$tmp/$rst" && git -C "$tmp" add "$rst"; }; then
		GIT_EDITOR=true git -C "$tmp" cherry-pick --continue > "$tmp.log" 2>&1 && return
		cat "$tmp.log"
	fi
	echo "master: conflict copying $(g log --oneline -1 "$c"). Resolve in $tmp, then"
	echo "git cherry-pick --continue and rerun (or push $tmp HEAD to $REMOTE master)."
	exit 1
}

g fetch -q origin 2>/dev/null || true # absent in tests
g fetch -q "$REMOTE"
tmp=C:/tmp/linear-master-$$
case "$1" in
rebuild)
	g worktree add -q --detach "$tmp" origin/master
	# master's own commits: those on master touching only its own files.
	for c in $(g rev-list --reverse --no-merges "$REMOTE/master" ^origin/master -- $OWN_PATHS); do
		[ -z "$(g diff-tree --no-commit-id --name-only -r "$c" | grep -vxF -e README.md -e .github/workflows/engines.yml)" ] &&
			pick "$c"
	done
	# Every engine commit: each branch in its own order, the branches interleaved by date.
	for e in $ENGINES; do g log --reverse --no-merges --format="$e %at %H" "origin/master..$e"; done |
		python "$HERE/interleave.py" | tr -d '\r' > "$tmp.list"
	while read -r c; do pick "$c"; done < "$tmp.list"
	rm -f "$tmp.list"
	git -C "$tmp" push -q --force-with-lease "$REMOTE" HEAD:master
	;;
append)
	shift
	g worktree add -q --detach "$tmp" "$REMOTE/master"
	for c in "$@"; do pick "$c"; done
	git -C "$tmp" push -q "$REMOTE" HEAD:master
	;;
*)
	echo "usage: linear-master.sh rebuild | append <commit>..."
	exit 2
	;;
esac
echo "master: $(git -C "$tmp" log --oneline -1), $(git -C "$tmp" rev-list --count origin/master..HEAD) commits over upstream"
g worktree remove --force "$tmp"
