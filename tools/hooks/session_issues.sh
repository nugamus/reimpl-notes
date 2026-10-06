#!/bin/bash
# SessionStart hook: one line of open issues per engine, so no session starts without
# seeing the bug list (github.com/nugamus/reimpl-notes/issues). Silent when gh is offline.
out=$(gh issue list -R nugamus/reimpl-notes --state open --limit 200 \
	--json number,title,labels --jq '.[] | "\(.labels | map(.name) | map(select(. == "x3d" or . == "peintre" or . == "ring" or . == "gilbert" or . == "grumpa")) | first // "other")\t#\(.number) \(.title)"' 2>/dev/null) || exit 0
[ -n "$out" ] || { echo "Open issues: none."; exit 0; }
echo "Open issues (fix these before new Next items; gh issue view <n> -R nugamus/reimpl-notes):"
echo "$out" | sort | awk -F'\t' '{ a[$1] = a[$1] (a[$1] ? "; " : "") $2 } END { for (e in a) print "  " e ": " a[e] }'
