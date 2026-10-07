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

### Q-0100 — What are the two s32 fields in China's SPR image ID (unk_16, unk_1a)?
- **Context:** E-0102: the loader 0x41f760 keeps them in the sprite (offsets 12 and 16 of
  its in-memory header); values 0..603 and 0..458, often beyond the sprite's own size.
- **What we checked:** the loader and the corpus ranges only; no reader of the two fields.
- **Blocks:** nothing in the format; drawing sprites at the right place may need them.
- **Status:** open. Find the blitters that read sprite+12/+16 (likely a screen position).

### Q-0101 — Which CHINE.EXE routine reads WAV files, and which fmt fields does it use?
- **Context:** E-0104: all 763 WAVs are plain PCM; the loader was not traced (callers with
  `%s%s.wav`: 0x403640, 0x404710, 0x404d00; `MySound.cpp` from 0x415bb0).
- **What we checked:** the decompile index for wav strings only.
- **Blocks:** nothing for playback through ScummVM's WAV reader; whether the game honours
  the 44100 Hz rate of `SOUND/BOITE32A.WAV` is unknown.
- **Status:** open.

### Q-0700 — What does 0x417400 do with a go zone's fourth argument?
- **Context:** E-0702: clicking a type 0/2/4 zone in a warp calls 0x417500 (mouse) and
  0x417400 (record field 7) before the goto; field 7 is 0 in all 608 decoded type-0
  zones (one undecoded).
- **Blocks:** the exact camera motion on a click (turn towards the zone? zoom?).
- **Status:** open. Decompile 0x417400/0x417500.

### Q-0701 — What do the letters of China's dialogue ids mean?
- **Context:** E-0704: GICD1011, GIDD1011, ANGC1011, XPRD4101: two speaker letters, then
  one, then D/C/H/Q/..., then act + three digits. Only partly read.
- **Blocks:** nothing (ids are opaque keys); naming in docs only.
- **Status:** open. Tabulate DIAL.TXT ids against their speakers' sync videos.

### Q-0702 — China place dumper: conditions are not rendered
- **Context:** `engines/cryomni3d/tools/china_places.py` lists API calls and zone tests in
  address order; the variable/object tests and their branches are not turned into
  if/else, so a place's logic must still be read from its listing (done for pne140 in
  `games/china/docs/places.md`).
- **Blocks:** writing every place's spec mechanically.
- **Status:** open. Next: follow the conditional jumps (cmp/test + jcc) into a tree.

### Q-0200 — What are the two saved dwords of each China object entry?
- **Context:** E-0208: the save keeps the first two dwords (`unk_0`, initially 0, and
  `unk_4`, initially -1) of each 0x30-byte entry of the object table at 0x45d5e4.
- **What we checked:** the save routines 0x417d40/0x417ce0 and the initial table only.
- **Blocks:** naming the fields in `china_sav.ksy`; restoring the inventory from a save.
- **Status:** open. Next: the Object.cpp functions (0x417a30..0x417e90) that write them.

### Q-0201 — Which of China's saved view floats is yaw and which pitch?
- **Context:** E-0208: the save stores 0x53485c then 0x534844, the two arguments of
  `Warp::setView` 0x441df0; Q-0501 asks for the warp angle units.
- **What we checked:** the save code and MyWarp::updateView 0x4170a0 (both updated there).
- **Blocks:** naming `view_0`/`view_1` in `china_sav.ksy`.
- **Status:** open. Next: 0x441df0, together with Q-0501.

### Q-0202 — How does China show the index rows and the table fiches' second column?
- **Context:** E-0203: LISTE.TXT gives rows `-C-`, `-` and `id/text`; E-0204: a table row
  keeps its second column as a pointer at the `<` (never cut at `>`), or none for `<>`.
- **What we checked:** the two loaders only, not the drawing code (0x4095a0 and the
  documentation screens).
- **Blocks:** drawing the documentation screens faithfully.
- **Status:** open.

### Q-0800 — What frame rate should China's warp view run at?
- **Context:** E-0804: the original never waits (BltFast, no vsync, no timer), so frame rate
  and with it the edge-scroll turning speed (E-0509, per frame) were the machine's speed.
- **What we checked:** main loop, flip, timer functions.
- **Blocks:** matching turning speed. Safe reading: cap at a fixed rate typical of the
  period hardware (a choice, not a fact); a longplay video's turning speed could settle it
  (`tools/longplay.py`).
- **Status:** open.

### Q-0010 — Which cursor does China show over the plain warp, and where is its hot spot?
- **Context:** the first engine slice (boot to `pne140`) needs a cursor before zones are
  implemented. Zone cursors are known (E-0700..E-0705: finger, eye, hand, `util`, mouth,
  question mark, table at 0x45d1d0), the cursor over no zone and the hot spot per sprite
  are not yet specced.
- **What we checked:** games/china/docs/places.md, spec/china-warp.md (the hit test uses
  the sprite's hot-spot offset or its centre).
- **Blocks:** the exact cursor outside zones.
- **Status:** open. Decided for now: `SPRITES/CURSEURS/PTROUG.SPR` with its centre as the
  hot spot, because the hit test falls back to the centre (E-0604).

### Q-0011 — The ANJGEN41 dialogue and the menu music in the first slice
- **Context:** spec/china-boot.md "Before the menu" (E-0504): between INTRO and ITB the
  game plays the lip-synced dialogue ANJGEN41, then starts `ALLEE.ZIK`.
- **What we checked:** ZIK is raw 16-bit stereo 22050 Hz PCM (E-0206); the synced dialogue
  player is not specced yet.
- **Blocks:** nothing; the engine skips both until the dialogue player exists.
- **Status:** open (implementation order, not an unknown). Decided: skip them in the boot
  slice because the dialogue player comes with the dialogue slice.

### Q-0012 — Saves in the engine before the scene logic exists
- **Context:** the menu's Load/Save need the save layout (E-0208) and the game state it
  holds (variables, objects, place, angles, minutes).
- **Blocks:** the Load button stays disabled in the boot slice.
- **Status:** open (implementation order). Decided: ScummVM saves come with the state
  slice; the original's `.sav` layout is read for import later.
