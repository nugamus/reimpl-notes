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
- **Status:** RESOLVED (2026-10-08) — the dumper now rebuilds each procedure's if/else,
  `and`/`or` conditions and early returns from the machine code (E-0710, E-0711); every
  place's logic is in `games/china/docs/places-logic.md` (E-0712).

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

### Q-0900 — China: four label keys missing from LABELS.TXT
- **Context:** zones use the label keys `edicule`, `poesie`, `vase`, `vase_spf`, which
  the en-iso LABELS.TXT lacks, so the original shows "ACCES LEGENDE INCONNU" on hover
  (E-0902).
- **Status:** open: check the other editions' LABELS.TXT; if all lack them, an original
  bug (hide the label).

### Q-0901 — China: cursor and object sprite lookup order
- **Context:** the SPR loader 0x41f760 tries several `%s%s%s` paths (`sprites\`, `misc\`)
  before opening; cursors live in DATA/SPRITES/CURSEURS, objects in DATA/SPRITES/OBJETS.
  The exact order and the CD/local split were not traced (E-0901).
- **Status:** open; the engine can search the data tree by file name.

### Q-0902 — China: inventory, documentation screen and the `c_`/`i_` sprites
- **Context:** the zone handler uses only the `r_` sprite (hand cursor). Where `c_`
  (36x36) and `i_` are drawn, what the slot field +0x28 means, and what the right button
  (0x48f298) does in play were not traced (E-0905). The documentation opener 0x40c5a0 is
  also unspecced.
- **Status:** open; next lead: callers of 0x417de0 and the inventory screen 0x40efd0.

### Q-0950 — China: what `m` means for the Sceaux puzzle (puzzle 3)
- **Context:** `puzzle(3, 0)` and `puzzle(3, 1)` both occur; m is passed to the Sceaux run
  0x41d630 and preset as its result (E-0953). Its meaning inside the puzzle (which seal
  set, or a mode) was not traced.
- **Status:** resolved (E-1203): m 0 = FOND + EMPR targets, CIRE handed over, interface
  allowed; m 1 = FOND2 + EMPRxF targets, no exit (Q-1200). games/china/docs/puzzles.md.

### Q-0951 — China: each puzzle's own exits and result values
- **Context:** the run functions of Puzzle4 (0x4189bc) and Bombe (0x419830) were checked
  (1 solved, 0 Escape); Penjing, Bouddha, Sceaux, Go, Horloge, Boutons were assumed to
  follow the same done/result shape from their identical dispatchers (E-0953).
- **Status:** open; spec each puzzle in its own section when the engine implements it.

### Q-0952 — China: sound channel volumes
- **Context:** place sounds (channel 3) and voices (channel 1) play at the buffer slot's
  stored volume (0x52ad80 + slot x 0x1c), which the place API does not set (E-0950); the
  value written at load (0x416120) and any option scaling were not traced.
- **Status:** open; play at full volume meanwhile.

### Q-0953 — China: the interface screen in full
- **Context:** E-0955 outlines it: the copy of the frame, the inventory row (y 437..475,
  38 px slots), the hover label, and four button rects (0x4ffa14, 0x4ffafc, 0x4ffa34,
  0x4ff9bc) leading to 0x4013e0, 0x410030 (`loc\voices\`, likely the notes replay),
  0x411e60 and the menu. The slide-in animation (0x40f070 first loop), the button
  images and which button is which were not traced. Overlaps Q-0902.
- **Status:** open; next lead: 0x40ff30, 0x40f9e0, 0x40fb10 and the rect table.

### Q-1000 — The music cross-fade between tracks
- **Context:** E-0206: the music volume moves by 10 per tick (0..127) when the track
  changes; the engine switches tracks at once.
- **What we checked:** only the evidence entry; the exact fade sequence (out then in, or
  both at once) and its tick rate are not traced.
- **Blocks:** nothing; a small audible difference at area changes.
- **Status:** open. Decided: switch at once until the fade is traced, because the
  original's tick has no time base either (E-0804).

### Q-1100 — China: the map's hot spot table and the `ico_bat` button
- **Context:** E-1105: table 0x45af38 (9 dwords: rect, label, type, place/fiche) is not
  dumped; the travel conditions on variables 0, 0x18, 0x19, 0xcc, 0x7c for the places at
  0x45be00/0x45bde8/0x45bdf8; what 0x403040 and 0x401fb0 (`ico_bat`) do.
- **Status:** resolved (E-1150..E-1152, see "Q-1100 resolution").

### Q-1101 — China: document text for objects 14..18, and channel 3
- **Context:** E-1103: the text box table has 14 entries; objects 14..18 would read the
  following strings as a box (only matters if LABELS.TXT has their key). 0x415f90(3)
  after reading is probably a sound stop.
- **Status:** open; next lead: LABELS.TXT keys for lvierge/rebus etc.; 0x415f90.

### Q-1102 — China: the documentation base screens
- **Context:** E-1106: entry points and images known; the contents screen 0x4085d0 and
  the fiche screen 0x40c5a0 (6311 bytes: themes, links, scrolling, index) not traced.
- **Status:** open; next lead: 0x4085d0, then 0x40c5a0, 0x40de50, 0x40c100.

### Q-1103 — China: puzzle sprites drawn under the bar
- **Context:** E-1101: 0x40fb10 first draws a list 0x4ff9e8 (count 0x4ffa28); 0x41d630
  resets the count. Who fills it was not traced.
- **Status:** open.

### Q-1104 — China: notebook text drawing
- **Context:** E-1104: font, colour and line spacing of 0x411df0 and the wrapping of
  0x412330 not read.
- **Status:** open.

### Q-0953 / Q-0902 / Q-0100 — update (2026-10-08)
- Q-0953 answered by spec/china-interface.md (E-1100..E-1105); what remains is in
  Q-1100..Q-1104. Q-0902: `c_` is the slot picture, `i_` the cursor over the eye, slot
  +0x28 the inventory slot (E-1102); the documentation base is Q-1102. Q-0100: SPR
  `unk_16`/`unk_1a` are the sprite's screen x/y (E-1101).

### Q-1200 — China: Sceaux puzzle with m = 1 (arbre3) has no exit, and m = 0 can lock
The run loop 0x41d630 ends only on a win or when the interface screen clears its run
flag, and the interface is reachable only with m = 0 while CIRE is not in the inventory
(E-1203). With m = 1 the player cannot leave unsolved; with m = 0, once CIRE is in the
inventory and another object is held, clicks are ignored and the interface is closed off.
Open: is this intended (a trace of the original at arbre3) or a softlock to fix
(possible-bug)? Next lead: which interface buttons clear the flag (Q-0953).

### Q-1250 — China: Puzzle4's phase 2 draw reads a third row
- **Context:** 0x4189bc draws phase 2 over rows 0..2 of the soleil/lune/mer/ciel table
  (0x52ba30, rows of 0x60 bytes) but only rows 0 (plain) and 1 (`...2`) exist; row 2
  reads 0x52baf0.. (flags at 0x52bb04 + j*0x18). If that memory is zero nothing extra is
  drawn. Engine: draw two rows.
- **Status:** open (not traced).

### Q-1251 — China: the bomb's sound slot 8 `tuyau.wav` is missing from the disc
- **Context:** 0x4192c0 loads `Bombe\tuyau.wav` into slot 8, played at step 11 (grandt
  with the screwdriver). No TUYAU.WAV in the EN ISO's `DATA/PUZZLES/BOMBE`; other
  editions not checked. Probably silent in the original. Engine: skip a missing sound.
- **Status:** open.

### Q-1001 — The credits screen's background, font and skipping; what follows the end of play
- **Context:** E-0205 gives the credits' pages, colours, centring and 5 s timer; E-0954
  gives the end of play (`shs240` sets it after the epilogue).
- **What we checked:** E-0205 and E-0954 only; the background, the font slot, any key
  that skips a page, and whether the game returns to the menu or exits after the
  end-of-play credits are not traced.
- **Blocks:** exact look of the credits.
- **Status:** open. Decided: black background, font slot 1, Escape skips a page, and the
  menu follows the end-of-play credits, because a ScummVM game should not quit by itself.

### Q-1100 resolution (2026-10-08)
- Q-1100 is resolved by E-1150..E-1152 (tables dumped by `tools/china_map.py`, travel
  conditions, `ico_bat` building list).

### Q-1150 — China: length of the building list's rise animation
- **Context:** E-1152: as decompiled, 0x401fb0's opening loop runs (font height + 5) * n
  frames, each 4 rows higher, which would copy past the list image once it is fully up.
  Either the decompile misreads the bound or the original overruns.
- **Status:** open; engine: rise 4 px per frame until the whole list shows; next lead:
  read the loop's disassembly at 0x401fb0.

### Q-1151 — China: the four sprites the options screen loads
- **Context:** E-1153: 0x40de50 builds four names with "%s%s" and loads them with
  0x41f760; the screen never draws them, and only the Escape exit frees them (0x40def0).
- **Status:** open, harmless; next lead: the call's arguments in the disassembly.

### Q-1152 — China: map hot spot field `unk_8` and game variable 0
- **Context:** E-1150: dword 8 is 18 for CHS/SHS/SHM/SHP, 10 for SPF, 6 for PDC, else 0;
  not read by the map. Variable 0 non-zero lifts all travel conditions (E-1151); what sets
  it is not traced (visit mode?).
- **Status:** open; next lead: xrefs to 0x45af58, writers of variable 0.

### Q-1300 — China: does anything outside the place procedures write CHAPITRE?
- **Context:** games/china/docs/walkthrough.md was derived from the 270 place procedures
  only (E-0710..E-0712). They store CHAPITRE = 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 15,
  17, 18 and never 3, 7, 11 or 16, though some tests read ranges across those values
  (`>= 16`, `< 11`).
- **Open:** whether other code (save loading, the interface bar, a puzzle) writes
  variable 1; if not, the gaps are just unused story numbers.
- **Status:** open; lead: xrefs to the variable setter 0x4033c0 with argument 1 outside
  0x421f00..0x436e20.

### Q-1301 — China: conditions on variables that nothing sets
- **Context:** places-logic tests variables that no place sets: GCD3111 (cpc110),
  GIG3111, GIHD3111 (cpc110), GIJ3111 (cpc210), GILD3111, GIKDIK11 (aie200), GISD3111,
  GITD3111 (aie500), 3GIED11 (bpiw201), Cache_Wen (bpiw202), XPRD4111 (aie600b), PRND1011
  (espw201), VAR_Venant_de_JIX111 (posthum, only set to 2 after testing 1). Most look like
  slips for a neighbouring name (GIGD3111, GIED3111, ...). Effects: the CHAPITRE 9 talks
  ANXI3151 (bpiw201) and ANMW3151 (espw201) can never play; cpc110's second guard
  (zone 9) plays and sets GIGD3111 like the first; the rest only weaken guards' tests.
- **Open:** confirm in the variable table that these are distinct entries and that no
  non-place code sets them; then decide per case: original bug (lost dialogue, fix it) or
  content cut on purpose (file a possible-bug if the signs do not settle it).
- **Status:** open.

### Q-1302 — China: a doc zone clicked with an object in hand
- **Context:** china-zones.md (E-0900) says a doc zone (type 8) clicked while holding an
  object does "nothing" in the handler. The critical path needs the place's code to see
  that zone index: showing an object to a character is a click on a doc zone with it
  (bpiw201 17/18/20, bpiw202 18/19/21, espw201 2, pdc170 1, spfw101 3/4, lgaw101 5); pdc170
  zone 1 with LISTE_BOITES is the only way on at CHAPITRE 5. So the index must be left for
  the place.
- **Open:** whether the press latch is set in that case (if not, the place sees the zone
  on every frame while the button is held, harmless for the once-only dialogues).
- **Status:** open; the engine must leave the index (walkthrough steps 18, 21, 29, ...).

### Q-1102 / Q-0202 — resolved (2026-10-08)
Both screens are specified in spec/china-documentation.md (E-1300..E-1305). Index rows
show the text before `/` and open the label after it (E-1301); a table row's `<b>` is
shown beside or under it when the row is hovered (E-1305).

### Q-1350 — China: fiche viewer theme badge position
- **Context:** 0x40c100 draws ico_* at stored x, y plus per-theme offsets (E-1302); the
  stored x, y (e.g. 0x48f334/0x48f338 for ico_ying) are written nowhere in the dump except
  for ico_thei (from its sprite, 0x40c5a0). Zero would put badges near the top-left.
- **Next:** find writes to 0x48f334, 0x4cdd0c, 0x4cde2c, 0x4ce894, 0x4ff60c, 0x4cde9c,
  0x4cdf24 (data xrefs in Ghidra), or compare one frame of the original.
- **Status:** open; engine: use each badge sprite's own position plus the offset.

### Q-1351 — China: 0x409f20 (table 0's `<b>` box)
- **Context:** E-1305: called with (300, y, 630, 400, text, white, font 1, 1); probably
  Text::drawBox with link support (the chronology rows' text has no links in the corpus?).
- **Status:** open; engine: draw like Text::drawBox.

### Q-1104 / Q-1101 / Q-1100 — update (2026-10-08, interface bar implemented)
- Notebook timer: 0x416c90 is a millisecond counter (E-0804), so the hover scroll steps one line
  per 10 ms; at our 25 frames/s that is one line per frame.
- Q-1104: decided font 1, black, 15-px lines (as the documents, E-1103) because nothing else is
  known; the snap shows the text between the background's bullets at x 180.
- Q-1101: decided to stop the voice handle on leaving a document (the original's channel 3).
- Q-1100: the compass click only logs a warning; the map is not implemented.
