# Formats (Ring engine)

One row per recovered format: status here, the Kaitai spec next to it (`<fmt>.ksy`), the
validator in `engines/ring/tools/parsers/<fmt>.py` (with `--selftest`), the proof in
`EVIDENCE.md`. A format is done only when its validator passes 100% of that type across
every version in `games/ring/discs/` and `games/prophet-and-assassin/discs/`, every byte
consumed.

| Format | Files | Validator | Spec | Evidence | Status |
|---|---:|---|---|---|---|
