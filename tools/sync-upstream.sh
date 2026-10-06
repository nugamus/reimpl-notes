#!/bin/bash
# tools/sync-upstream.sh [engine...]: moves the fork onto ScummVM's latest master.
#  1. each clean branch <engine> is rebased on origin/master and force-pushed (with lease);
#  2. each <engine>-dev is rebased on its new clean branch (DEV commit stays on top);
#  3. the fork's master is rebuilt linear (linear-master.sh rebuild);
#  4. every rebased engine is built with tools/build.sh.
# Stops at the first conflict and says where to resolve it. Default: all engines.
set -e
REPO=/c/scummvm
REMOTE=fork
ALL="x3d peintre ring gilbert grumpa"
ENGINES=${*:-$ALL}
HERE=$(cd "$(dirname "$0")" && pwd)
g() { git -C "$REPO" "$@"; }

g fetch -q origin
g fetch -q "$REMOTE"
echo "upstream: $(g log --oneline -1 origin/master)"

for e in $ENGINES; do
	behind=$(g rev-list --count "$e..origin/master")
	[ "$behind" -gt 0 ] || { echo "$e: up to date"; continue; }
	tmp=C:/tmp/sync-$e-$$
	g worktree add -q "$tmp" "$e"
	if ! git -C "$tmp" -c rerere.enabled=true rebase -q origin/master; then
		echo "$e: conflict rebasing on upstream. Resolve in $tmp (git rebase --continue), push with"
		echo "git -C $tmp push --force-with-lease $REMOTE $e, remove the worktree, and rerun."
		exit 1
	fi
	git -C "$tmp" push -q --force-with-lease "$REMOTE" "$e"
	g worktree remove "$tmp"
	echo "$e: rebased over $behind upstream commits"
	wt=/c/scummvm-dev/$e
	if git -C "$wt" diff --quiet && git -C "$wt" diff --cached --quiet; then
		git -C "$wt" -c rerere.enabled=true rebase -q --onto "$e" "$e@{1}" "$e-dev" ||
			{ echo "$e-dev: conflict, resolve in $wt"; exit 1; }
	else
		echo "$e-dev: uncommitted changes in $wt, rebase it onto $e yourself"
	fi
done

bash "$HERE/linear-master.sh" rebuild

for e in $ENGINES; do bash "$HERE/build.sh" "$e" | tail -3; done
