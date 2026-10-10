#!/bin/bash
# tools/publish.sh <engine>: copies every commit on <engine>-dev that the clean branch <engine>
# lacks (except DEV: and BRIDGE: commits) onto <engine>, pushes <engine> to the fork, copies the commits onto
# the fork's (linear) master, then rebases <engine>-dev on it so the dev branch is again "clean branch +
# the DEV commit".
# Refuses commits without an Assisted-by trailer (ScummVM AI-GUIDELINES.md).
set -e
ENGINE=${1:?usage: publish.sh <engine>}
REPO=${REPO:-/c/scummvm}       # overridable for testing
REMOTE=${REMOTE:-fork}
DEVWT=${DEVROOT:-/c/scummvm-dev}/$ENGINE
g() { git -C "$REPO" "$@"; }

picks=""
for c in $(g cherry "$ENGINE" "$ENGINE-dev" | awk '$1 == "+" {print $2}'); do
	subject=$(g log -1 --format=%s "$c")
	case "$subject" in DEV:* | BRIDGE:*) continue ;; esac
	g log -1 --format=%B "$c" | grep -q '^Assisted-by: ' || { echo "no Assisted-by: $subject"; exit 1; }
	picks="$picks $c"
done
[ -n "$picks" ] || { echo "$ENGINE: nothing new to publish"; exit 0; }

tmp=C:/tmp/publish-$ENGINE-$$
g worktree add -q "$tmp" "$ENGINE"
before=$(git -C "$tmp" rev-parse HEAD)
if ! git -C "$tmp" cherry-pick $picks > /dev/null; then
	echo "Conflict publishing to $ENGINE: resolve in $tmp, git cherry-pick --continue, push, then"
	echo "git -C $REPO worktree remove $tmp"
	exit 1
fi
published=$(git -C "$tmp" rev-list --reverse "$before..HEAD")
git -C "$tmp" push -q "$REMOTE" "$ENGINE"
g worktree remove "$tmp"
g log --oneline "$ENGINE" -$(echo $picks | wc -w)

# The fork's master is linear: the same commits are copied onto it.
REPO=$REPO REMOTE=$REMOTE bash "$(dirname "$0")/linear-master.sh" append $published ||
	echo "$ENGINE itself is published; finish master as linear-master.sh says."

# The dev branch: drop the now-published copies, keep the DEV commit on top.
if git -C "$DEVWT" diff --quiet && git -C "$DEVWT" diff --cached --quiet; then
	git -C "$DEVWT" -c advice.skippedCherryPicks=false rebase -q "$ENGINE" && echo "$ENGINE-dev rebased: $(git -C "$DEVWT" log --oneline -1)"
else
	echo "$DEVWT has uncommitted changes: rebase $ENGINE-dev on $ENGINE yourself later"
fi
