#!/bin/bash
# SessionStart hook: what the user approved (do first), the open bugs per engine, and how
# many issues wait for the user's decision (agents leave those alone), so no session
# starts without seeing them. Issues: github.com/nugamus/reimpl-notes. Silent when offline.
R=nugamus/reimpl-notes
ENGINES='map(.name) | map(select(. == "x3d" or . == "peintre" or . == "ring" or . == "gilbert" or . == "grumpa")) | first // "other"'
list() { # <search> -> "engine<TAB>#n title" lines
	gh issue list -R "$R" --state open --limit 200 --search "$1" --json number,title,labels \
		--jq ".[] | \"\(.labels | $ENGINES)\t#\(.number) \(.title)\"" 2>/dev/null
}
show() { sort | awk -F'\t' '{ a[$1] = a[$1] (a[$1] ? "; " : "") $2 } END { for (e in a) print "  " e ": " a[e] }'; }

approved=$(list "label:approved") || exit 0
bugs=$(list "label:bug -label:approved -label:needs-decision")
waiting=$(gh issue list -R "$R" --state open --search "label:needs-decision" --json number --jq length 2>/dev/null)

[ -z "$approved" ] || { echo "Approved by the user (do these first; enhancements become game options):"; echo "$approved" | show; }
if [ -n "$bugs" ]; then
	echo "Open bugs (before new Next items; gh issue view <n> -R $R):"
	echo "$bugs" | show
fi
[ -z "$approved$bugs" ] && echo "Open bugs: none."
[ "${waiting:-0}" -gt 0 ] && echo "$waiting issue(s) wait for the user's decision (label needs-decision): leave them be."
exit 0
