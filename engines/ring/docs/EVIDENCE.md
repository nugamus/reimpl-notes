# Evidence log (Ring engine, Arxel Tribe)

Every factual claim in `engines/ring/docs/` and `games/{ring,prophet-and-assassin}/docs/`
must have an entry here that names the thing that proved it. Claims without evidence are
bugs, not shortcuts.

Append only. Do not rewrite history; if a claim turns out to be wrong, add a new entry
that supersedes it and mark the old one `SUPERSEDED by E-nnnn`.

## Entry format

```
### E-0001 — <one-line claim>
- **Binary/file:** games/ring/discs/dvd-edition/RING.EXE | .../DATA/AS.AT2 | traces/<run>.log
- **Evidence:** Ghidra address (`0x004ab120`), trace line number, or corpus statistic
  ("all 57 .CNM files start with `CNM UNR\0`").
- **Reference:** optional: the matching place in Templier's engine
  (`reference/templier-scummvm-ring/engines/ring/<file>:<line>`). A reference alone is
  never proof: confirm it in the original binary or the data.
- **Method:** how it was obtained (decompiled `FUN_004ab120`; ran
  `engines/ring/tools/parsers/cnm.py` over the corpus; trace of a scenario).
- **Confidence:** proven | strong | tentative
```

An entry at `tentative` confidence must also have a matching line in `OPEN-QUESTIONS.md`.

## Entries
