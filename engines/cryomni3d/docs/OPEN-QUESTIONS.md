# Open questions (CryOmni3D engine)

Unknowns that block or limit something (rule 4). Unknown fields stay `unk_*` in parsers
and specs until a question here is answered.

Entry format:

```
### Q-0001 — <one-line question>
- **Context:** where it came up, with E-ids.
- **What we checked:** what was tried, so nobody repeats it.
- **Blocks:** what can't be done or is guessed until it is answered.
- **Status:** open | RESOLVED (date) — the answer and its E-id
```

### Q-0001 — Are Atlantis III and Egypt III Omni3D games?
- **Context:** ScummVM's wiki lists Atlantis III as "not using Omni3D technology"; Egypt III
  (The Egyptian Prophecy, Kheops Studio, 2004) is not on the page at all. Both are in our
  images (`games/atlantis-3`, `games/egypt-3`). Templier's fork names Atlantis III (E-0002)
  but has no code for it.
- **What we checked:** only the wiki and the fork.
- **Blocks:** whether they belong in this engine, a new engine, or neither.
- **Status:** open. Settle from the survey: compiler, libraries and data formats of their
  executables against the Omni3D games'.

### Q-0002 — How many Omni3D engine generations are there?
- **Context:** the games span 1996 (Versailles) to 2001 (Versailles II, Egypt II) and two
  studios' lines (Cryo's own, and the Kheops-made later titles). Upstream `cryomni3d` covers
  one game (E-0001).
- **What we checked:** nothing yet.
- **Blocks:** how much of upstream's shared code each game can reuse, and the order to
  implement the games in.
- **Status:** open. Compare the executables (shared library functions by hash in Ghidra)
  and the data formats per game.

### Q-0003 — What are Aztec's four 580 MB `Data/file/File.*` entries?
- **Context:** the English ISO of Aztec (`games/aztec/discs/en-iso/cd1`, E-0003) is a 645 MB
  volume, but its directory lists `Data/file/File.alw`, `.bmx`, `.cny`, `.doz` at about
  580 MB each, so extraction yields 2.8 GB; 7-Zip reports "Unexpected end of archive".
- **What we checked:** sizes only. Overlapping or out-of-volume extents are a known
  copy-protection trick, but which one (and whether the game reads these files) is not
  established.
- **Blocks:** nothing yet; corpus tools should skip these four files until answered.
- **Status:** open. Check the executable's protection (Detect It Easy) and whether its code
  opens `Data/file/`.

### Q-0600 — Does Versailles' original warp renderer use upstream's >>10 / >>15 row deltas?
- **Context:** China's renderer (E-0603) changes the per-pixel x and y steps down a
  16-row block by (delta >> 4) and (delta >> 9); upstream `Omni3DManager::getSurface` uses
  >> 10 and >> 15. Everything else in the grid and renderer matches.
- **Blocks:** whether China can use `getSurface` unchanged (a per-game shift) or upstream
  carries a slip that also affects Versailles.
- **Status:** open. Decompile Versailles' warp blitter and compare.

### Q-0601 — Who reads China's warp edge columns (0x534858, 0x534854)?
- **Context:** `Warp::setView` (0x441df0) stores the image x of the two ends of the top or
  bottom grid row (E-0602). No function in the decompile dump names them as readers.
- **Blocks:** nothing for display; maybe zone culling or sound panning.
- **Status:** open. Ghidra references to the two globals.

### Q-0500 — What is China's fourth option, `save`?
- **Context:** E-0501, E-0505, E-0506: `chine.cfg` field 4 and the options button
  labelled `save` toggle a flag that gates the emblem chooser on New game, Load and Save.
- **What we checked:** the flag's uses in the menu and dispatcher only.
- **Blocks:** naming the field; how the two save systems differ (emblem profiles vs. the
  plain `Fondlod`/`Fondsvg` screens).
- **Status:** open. Next: 0x410da0, 0x41e930, 0x41e090 and LABELS.TXT `#save#`.

### Q-0501 — China's warp angle units and limits
- **Context:** E-0503, E-0507, E-0509: start alpha 4.7; projection set-up 0x441c90(75.137,
  50.0); alpha wraps by a runtime period (0x533c98), beta is clamped to 0.9 x 0x5314c4.
- **What we checked:** the call sites only.
- **Blocks:** the starting direction in degrees and the pitch limits.
- **Status:** open. Next: decompile 0x441c90 and 0x441df0.

### Q-0502 — Extension of China's `Loc\` still-image fallback
- **Context:** E-0510: the last try is `<L>:\Chine\Data\Loc\<stem>` with no extension
  added in 0x402e20; `Load` exists as `DATA/LOC/LOAD.HNM`.
- **What we checked:** 0x402e20 and 0x41fdb0.
- **Blocks:** nothing practical (load `<stem>.hnm`).
- **Status:** open. Next: 0x416d60's path handling.

### Q-0503 — China's scene scripts have no Ghidra functions
- **Context:** E-0507: scene handlers (`Script_Start` 0x436db0, `pne140` 0x431050, ...)
  live in 0x421f00..0x436e20, which auto-analysis left undefined (reached only through
  pushed pointers).
- **What we checked:** raw disassembly of the two handlers.
- **Blocks:** decompiling the game script; listing all places.
- **Status:** open. Next: create functions over that range in Ghidra (each handler starts
  `mov eax,[esp+4]; cmp eax,1`), re-run decompile_all.
