#!/bin/bash
# tools/bridge-branch.sh [--push]: rebuilds the fork's agent-bridge branch = the fork's master +
# every BRIDGE: commit (scummvm-agent-bridge adapters) of each <engine>-dev, so others can build
# our engines with the adapters. BRIDGE: commits sit between the clean branch and the DEV
# commit on <engine>-dev; they never reach a clean branch or master (publish.sh skips them,
# the pre-push hook refuses them anywhere but agent-bridge). --push force-pushes the result.
set -e
REPO=${REPO:-/c/scummvm}
REMOTE=${REMOTE:-fork}
ENGINES=${ENGINES:-$(grep -v '^#' "$(dirname "$0")/engines.txt" | cut -d' ' -f1 | paste -sd' ' -)}
g() { git -C "$REPO" "$@"; }

g fetch -q "$REMOTE"
picks=""
for e in $ENGINES; do
	g rev-parse -q --verify "$e-dev" > /dev/null || continue
	picks="$picks $(g log --reverse --format='%H %s' "$e..$e-dev" | awk '$2 == "BRIDGE:" {print $1}')"
done
[ -n "${picks// /}" ] || { echo "no BRIDGE: commits"; exit 0; }

tmp=C:/tmp/bridge-branch-$$
g worktree add -q -B agent-bridge "$tmp" "$REMOTE/master"
if ! git -C "$tmp" cherry-pick $picks > /dev/null; then
	echo "agent-bridge: conflict. Resolve in $tmp (git cherry-pick --continue), then rerun with --push"
	exit 1
fi
git -C "$tmp" log --oneline "$REMOTE/master..HEAD"
[ "$1" = --push ] && git -C "$tmp" push -q --force "$REMOTE" agent-bridge && echo "pushed $REMOTE agent-bridge"
g worktree remove "$tmp"
