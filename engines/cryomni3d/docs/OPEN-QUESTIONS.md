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
