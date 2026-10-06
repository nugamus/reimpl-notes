#!/bin/sh
# Commit what is staged in the current ScummVM worktree (e.g. C:\scummvm-dev\grumpa), then
# move the new commit below the DEV: commits at the tip of the branch (the development
# harness stays last). Run it from inside the worktree:
#   bash <notes>/tools/commit_before_dev.sh <message-file>
# Stops (and leaves the cherry-pick for you) if a DEV commit does not apply on top.
set -e
msg=$(realpath "$1")
cd "$(git rev-parse --show-toplevel)"
git commit -q -F "$msg"
n=0
while git log -1 --format=%s "HEAD~$((n + 1))" | grep -q '^DEV: '; do
	n=$((n + 1))
done
[ "$n" -eq 0 ] && { git log --oneline -1; exit 0; }
# The reorder resets the tree: never with someone's uncommitted work in it.
if ! git diff --quiet || ! git diff --cached --quiet; then
	echo "Uncommitted changes in $(pwd): the commit stays on top of the DEV commits."
	git log --oneline -1
	exit 1
fi
git branch -f commit-before-dev HEAD
git reset -q --hard "HEAD~$((n + 1))"
picks="commit-before-dev"
i=$n
while [ "$i" -ge 1 ]; do
	picks="$picks commit-before-dev~$i"
	i=$((i - 1))
done
git cherry-pick $picks > /dev/null
git branch -D commit-before-dev > /dev/null
git log --oneline -$((n + 2))
