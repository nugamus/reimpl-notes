#!/bin/bash
# SessionStart hook: the user's decisions waiting to be acted on (ENHANCEMENTS.md approvals,
# POSSIBLE-BUGS.md verdicts), then one line of open issues per engine, so no session starts
# without seeing them (github.com/nugamus/reimpl-notes/issues). Silent when gh is offline.
cd "$(dirname "$0")/../.." || exit 0
todo=$(awk '/^### /{h=substr($0,5)} /\*\*Decision:\*\* approved/{print "  implement " h} /\*\*Verdict:\*\* (bug|option)/{print "  act on verdict: " h}' ENHANCEMENTS.md POSSIBLE-BUGS.md 2>/dev/null)
[ -z "$todo" ] || { echo "The user decided (do these first):"; echo "$todo"; }
out=$(gh issue list -R nugamus/reimpl-notes --state open --limit 200 --search "-label:needs-decision" \
	--json number,title,labels --jq '.[] | "\(.labels | map(.name) | map(select(. == "x3d" or . == "peintre" or . == "ring" or . == "gilbert" or . == "grumpa")) | first // "other")\t#\(.number) \(.title)"' 2>/dev/null) || exit 0
[ -n "$out" ] || { echo "Open issues: none."; exit 0; }
echo "Open issues (fix these before new Next items; gh issue view <n> -R nugamus/reimpl-notes):"
echo "$out" | sort | awk -F'\t' '{ a[$1] = a[$1] (a[$1] ? "; " : "") $2 } END { for (e in a) print "  " e ": " a[e] }'
