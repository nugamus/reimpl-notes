#!/bin/bash
# tools/nightly.sh: the unattended check of every engine (Windows Task Scheduler runs it at
# night, see the root CLAUDE.md). For each engine in tools/engines.txt: build the dev
# worktree, run all its scenarios, check its .ksy specs against the corpus, and lint for
# HARD findings. The report goes to logs/nightly-<date>.txt; an engine with failures new since
# the last night (NIGHTLY_NO_ISSUES=1 only records that baseline) gets one
# GitHub issue "Nightly: <engine> fails" (created, or commented on if already open), so the
# next session sees it in the hook's list. It never commits, pushes or syncs.
cd "$(dirname "$0")/.." || exit 1
log=logs/nightly-$(date +%Y-%m-%d).txt
mkdir -p logs
: > "$log"
for e in $(grep -v '^#' tools/engines.txt | cut -d' ' -f1); do
	out=$( {
		echo "== $e $(date +%H:%M)"
		bash tools/build.sh "$e" 2>&1 | tail -3 || echo "BUILD FAILED"
		uv run tools/scenario.py "$e" 2>&1 | grep -E '^(PASS|FAIL)|scenarios pass|no scenarios'
		uv run tools/ksy_check.py "$e" 2>&1 | grep -E '^(ok|FAIL)'
		bash tools/lint.sh "$e" 2>&1 | grep -E '^HARD|lint:'
	} 2>&1 )
	echo "$out" >> "$log"
	# Only what is new since the last night counts: known failures already have issues.
	last=logs/nightly-last-$e.txt
	now=$(echo "$out" | grep -E 'FAILED|^FAIL|^HARD' | sed -E 's/, [0-9]+s\)/)/' | sort)
	new=$(comm -13 <(sort "$last" 2>/dev/null) <(echo "$now") | grep .)
	echo "$now" > "$last"
	if [ -n "$new" ] && [ -z "$NIGHTLY_NO_ISSUES" ]; then
		body=$(printf 'The nightly run on %s found new failures (full report: `%s` on the dev machine):\n\n```\n%s\n```\n' \
			"$(date +%Y-%m-%d)" "$log" "$(echo "$new" | head -30)")
		n=$(gh issue list -R nugamus/reimpl-notes --state open --search "\"Nightly: $e fails\" in:title" --json number --jq '.[0].number' 2>/dev/null)
		if [ -n "$n" ]; then
			gh issue comment "$n" -R nugamus/reimpl-notes --body "$body" > /dev/null
		else
			gh issue create -R nugamus/reimpl-notes --label bug --label "$e" --title "Nightly: $e fails" --body "$body" > /dev/null
		fi
	fi
done
echo "nightly done: $log"
