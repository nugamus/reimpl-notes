# Formats (CryOmni3D engine)

One row per recovered format: status here, the validator in
`engines/cryomni3d/tools/parsers/<fmt>.py` (with `--selftest`), the proof in `EVIDENCE.md`.
A format is done only when its validator passes 100% of that type in every game's reference
edition (`games/<game>/discs/<version>/`), every byte accounted for. Formats upstream
`cryomni3d` already reads (HLZ, HNM, WAM, the Versailles `.dat` files) still get a row and a
validator run over the other games, since their variants may differ.

| Format | Games | Files | Validator | Evidence | Status |
|---|---|---:|---|---|---|
