# <Engine> (<Developer>): engine briefing

Loaded on top of the root CLAUDE.md whenever files under `engines/<engine>/` are read. Holds this
engine's ground truth, status and next steps; keep it current (rule 6) and keep the root file
free of engine detail.

### Ground truth

- **Disc:** where the images are (`games/<game>/images/`), what was extracted where
  (`games/<game>/discs/<version>/`), languages and editions (E-0001).
- **Programs:** each executable with compiler, libraries and protection (Detect It Easy),
  and which one is the game (E-0002). Decrypted or no-CD copies used for Ghidra and runs.
- **Engine name** `<engine>` (and why; tentative names get a Q-id).
- **Architecture:** how the game is built in a paragraph: rendering (2D, pre-rendered, 3D,
  resolution, colour depth), scripting, how scenes, objects and saves work, with E-ids.
- **Run folder:** `C:\<Game>Run` (what it holds, dgVoodoo or not, windowed).

### Status

- **Survey** (E-..): `notes/corpus-triage.md` from `tools/identify.py`; binaries.
- **Ghidra** (E-..): `ghidra_projects/<Project>.gpr`, programs, how named (docs/patterns/naming-code.md);
  `notes/decomp/all` dump and `tools/coverage.py <engine>` numbers.
- **Formats** (`docs/formats/README.md`): one line per format, validator counts (rule 2).
- **Specs** (`docs/spec/`): one line per area.
- **Engine `<engine>`** (`C:\scummvm-dev\<engine>`): what plays, and how it was verified
  (scenarios in `engines/<engine>/tests/`). Dev harness keys (DEV commit only).

### Next

1. The next slice, small enough to finish in a session.
