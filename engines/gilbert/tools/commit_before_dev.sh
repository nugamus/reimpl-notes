#!/bin/sh
# Commit what is staged in ../scummvm, then move the new commit below the DEV: commits at
# the tip of the branch (the development harnesses stay last, CLAUDE.md).
#   engines/gilbert/tools/commit_before_dev.sh <message-file>
# Stops (and leaves the cherry-pick for you) if a DEV commit does not apply on top.
set -e
cd /c/scummvm
git commit -q -F "$1"
n=0
while git log -1 --format=%s "HEAD~$((n + 1))" | grep -q '^DEV: '; do
	n=$((n + 1))
done
[ "$n" -eq 0 ] && { git log --oneline -1; exit 0; }
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
