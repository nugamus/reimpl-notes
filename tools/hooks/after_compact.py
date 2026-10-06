"""SessionStart hook for "compact": right after the conversation was compacted, put back what
the summary may have lost: uncommitted and unpublished work (from loose_ends.py) and where
the durable state lives, so the agent re-reads instead of reconstructing from memory.
(A PreCompact hook can only block compaction, not add to it; this runs just after.)"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loose_ends  # noqa: E402

note = [
    "The conversation was just compacted. Before continuing:",
    "1. Re-read the engine's CLAUDE.md (Status, Next) and the spec or issue you were working on;"
    " trust them over the summary where they differ.",
    "2. Anything you learned that is not yet in its home (EVIDENCE.md, a spec, notes/summaries.tsv,"
    " the engine's CLAUDE.md) goes there now, before more work.",
]
found = loose_ends.findings()
if found:
    note.append("3. Open work found on disk: " + "; ".join(found) + ".")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n".join(note)}}))
