# Open questions (Ring engine)

Things we could not determine after checking the original code (Ghidra), the corpus and
traces. An unresolved field goes here and stays opaque (`unk_*`) in the format spec. It does
not get a guessed meaning, and it does not take Templier's meaning on trust either.

Append only. When a question is answered, keep the entry, mark it `RESOLVED`, and link the
`EVIDENCE.md` entry that resolved it.

## Entry format

```
### Q-0001 — <one-line question>
- **Context:** where it came from (format + offset, function address, trace line).
- **What we checked:** the original code, the corpus, traces, Templier's engine.
- **Observed range:** for a data field, the set of values seen across the corpus.
- **Blocks:** what work is stalled or degraded by not knowing this.
- **Status:** open | RESOLVED (see E-nnnn)
```

## Questions

### Q-0001 — Which protection wraps Prophet's Legend.ex_, and where do its import slots lead?
- **Context:** E-0004: sections `.cms_t`/`.cms_d`, entry point in `.cms_t`, import calls in
  `.text` go through slots in `.cms_d` (e.g. `[0x4e82f0]`) instead of the IAT.
- **What we checked:** section layout, entropy, byte diff against the crack (diff oracle
  only). No product string found in `.cms_t`/`.cms_d`.
- **Observed range:** 323 differing runs in `.text`, most of them 3-byte slot addresses.
- **Blocks:** naming the Win32 calls in Prophet's code during RE. A slot → import map can be
  built site by site from the diff (same call site, IAT slot in the crack) without using the
  crack's code.
- **Status:** open

### Q-0002 — Where does the engine convert RGB555 image data to the display's 16-bit layout?
- **Context:** E-0017: packed images decode to 16-bit pixels that look right as RGB555.
  `RING_DVD.EXE` 0x414410 (string `aVideoDeviceRaw::CalculateMask…`) sets channel masks
  for four display layouts (555, 565, 655, 556), so the engine adapts to the surface.
- **What we checked:** the Bma loader copies table entries without conversion.
- **Blocks:** nothing for ScummVM (we pick the pixel format), but the spec of image
  loading should name the conversion step.
- **Status:** open

### Q-0003 — Does Prophet read only 10 layers of A03S02N05R01.aqc?
- **Context:** E-0020: 18,289 bytes after the tenth section of this file do not form a
  section (they start with a copy of the last entry). The engine reads as many sections as
  the rotation has layers (`this+0x48`, from the game code).
- **What we checked:** the file; LEGEND.EXE strings (rotation names are not stored whole).
- **Blocks:** nothing if the layer count is 10; the validator keeps the bytes as
  `unk_trailing` for this file only.
- **Status:** open (answer from Prophet's zone a03 code: the AddRot call for this node)

### Q-0004 — What does the original do with the 53 damaged DVD voice files?
- **Context:** E-0021: 52 DVD `.wac` files (SPA/ITA/HOL/SWE) break at a 64 KiB offset,
  one has no WAV header. The mono decoder reads `size + 2` bytes per chunk, so after the
  break it reads garbage sizes; a failed read raises `aSecComSouMono::Decompress -> raed
  Error`.
- **What we checked:** the decoder and the files; the good chain resumes about 4 KB later.
- **Blocks:** how our engine plays these lines (stop at the break like a read error, skip
  to the resumed chain, or fall back to another language's file). One precise run of the
  original DVD in Spanish on `AS/SOUND/SPA/1104.WAC` would answer what the player hears.
- **Status:** open

### Q-0005 — How does the ISO version play fos03n02_s05n01.cnm with its damaged frame 132?
- **Context:** E-0024: the chunk at the table's frame-132 video offset is not a chunk.
  If Play reads sequentially, the chain breaks there ("Error in typeCinData"); if it seeks
  by the table, only that frame is lost.
- **What we checked:** the file; the ISO EXE's Play has not been read yet.
- **Blocks:** faithful playback of one ISO-version video (FO zone transition).
- **Status:** open

### Q-0006 — How does the DVD EXE resolve a data path (install dir vs CD path)?
- **Context:** spec/boot.md: paths are built from app+0x6b (0x402460), the string at
  app+0x14 (0x402470, the `CDPATH` value set by 0x40b4d0) and the one at app+0x18
  (0x402480), with formats like `%s%s\%s\%s\%s`.
- **What we checked:** the three getters; not yet the callers' choice between them.
- **Blocks:** nothing for ScummVM (everything is under one game directory), but the spec
  of file lookup should say which prefix each kind of file uses.
- **Status:** open

### Q-0007 — How does the DVD find the AS zone's backgrounds?
- **Context:** E-0034: the AS set-up declares `.bma` backgrounds that exist only loose in
  `DATA/AS/IMAGE`, the DVD `fl.ini` has `ART_AS: 1` (archive), and a lookup in `AS.AT2`
  by those names fails (the archive holds the same pictures as `\image\old_ish.bmp`,
  `\image\ass01n01_v01.bmp`, …).
- **What we checked:** GetreadFrom, the ART flag parsing (atoi), the loader choice, the
  archive lookup; the installer only rewrites `CDPATH` in `fl.ini`.
- **Blocks:** nothing for our engine if it falls back to the loose file; whether the
  original shows these pictures at all (dead puzzles?) is unknown.
- **Status:** open (one run of the original DVD entering AS would answer it)

### Q-0008 — Which SY.AT2 does an installed DVD game read?
- **Context:** `aArtHandler::Open(1, 2)` builds `<install>DATA\sy.at2`; the DVD has
  `DATA/<LAN>/SY.AT2` for seven languages and no `DATA/SY.AT2`.
- **What we checked:** Open's format; not yet the installer's copy step or a language
  prefix in the install path.
- **Blocks:** ScummVM picks `DATA/<LAN>/SY.AT2` by the chosen language meanwhile.
- **Status:** open

### Q-0009 — Are the main menu's hot spots really 16 pixels above their pictures?
- **Context:** `games/ring/docs/sy.md`: object 90000's hot spot is (148, 69)–(500, 99)
  but its lit picture is drawn at (148, 85) and 30 pixels tall; the same 16-pixel shift
  holds for all seven entries. The dialogues on puzzle 1 and the other SY screens line up
  with their pictures.
- **What we checked:** the hit test (0x4238b0), the mouse globals (raw `GetCursorPos`),
  the hot spot and accessibility constructors, the presentation position (0x42d320) and
  puzzle drawing (0x41c320): no offset anywhere (E-0040).
- **Blocks:** nothing; the engine follows the data. One run of the original (move the
  mouse to y = 70 over "new game" and see whether it lights) would confirm it.
- **Status:** open

### Q-0010 — Which "ARX Pilgrim L" size does GDI pick for `lfHeight` 12?
- **Context:** `spec/text.md`: font 1 asks for a 12-pixel cell; `arxrin.fon` has cells of
  13, 16, 20, 24, 29, 37 pixels and GDI does not scale raster fonts except by whole
  multiples.
- **What we checked:** the `LOGFONTA` the EXE fills (E-0044); the font file (E-0043).
- **Blocks:** nothing; the engine uses the closest cell, 13 (8 points). One screenshot of
  the original's new-game question would settle it (text height of 11-pixel capitals).
- **Status:** open

### Q-0011 — How many frames per second does the original run, for the pan speed?
- **Context:** `spec/rotation.md`: looking around adds a fixed amount to alpha and beta per
  frame (0x4107f0), so the turning speed depends on the frame rate. The frame (0x40e9f0) is
  once per idle loop; whether `Flip` waits for the vertical blank (and at what refresh
  rate the game's 640 × 480 × 16 mode runs) is not established.
- **What we checked:** the pan code (E-0046); not the DirectDraw flip flags.
- **Blocks:** nothing; the engine runs the view at 60 frames per second meanwhile.
- **Status:** open

### Q-0012 — What is a rotation's byte +0x67 before a saved game sets it?
- **Context:** `spec/rotation.md`: +0x67 set disables looking around with the mouse. Only
  the saved-game restore writes it (0x40d34d / 0x40d359); the constructor (0x41da10)
  does not, and the object comes from `operator new` (not zeroed in a release build).
- **What we checked:** every byte store to +0x67 in `.text` (E-0046).
- **Blocks:** nothing; the engine takes 0 (the view turns with the mouse).
- **Status:** open

### Q-0020 — Who enters NI at entry 999?
- **Context:** `GameSetZoneNI` 0x44a840 entry 999 fills the bag with six NI objects, sets byte
  10106 and starts at 10415 (`games/ring/docs/ni.md`). No `GoZone(2, 999)` was found in the
  zone code read (AS, NI).
- **What we checked:** the NI and AS handlers; a linear scan for `GoZone` calls is unreliable
  (data in `.text`).
- **Blocks:** nothing (a test entry, likely).
- **Status:** open

### Q-0021 — NI's handle and speaker drags stop sound 10401 only when it is not playing
- **Context:** 0x4477d0 releases of 10103 and 10201: `if (!0x406ef0(10401)) stop(10401)`;
  the moves start it `if (!0x406ef0(10401))`. 0x406ef0 → 0x469540 is taken as "plays" from
  its other uses (0x445c80's 10901 test).
- **What we checked:** the decompile; 0x469540 not decompiled.
- **Blocks:** whether the scrape sound stops at release; the engine follows the code.
- **Status:** open

### Q-0022 — Does `BagAdd` of an object already in the bag add it twice?
- **Context:** NI's 10505 (AG cells) click gives `BagAdd(10505)` every time; its
  accessibility is never disabled. `BagAdd` → `aList::add` (0x406330).
- **What we checked:** `aApplication::BagAdd` only (`engines/ring/notes/decomp/bag/`).
- **Blocks:** the inventory spec.
- **Status:** open

### Q-0013 — What are `ObjAddBagAni`'s second and third arguments (1 and 3 in every call)?
- **Context:** `spec/bag.md` "Drawing". `ObjAddBagAni(object, 1, 3, frames, 12.5, 4)` passes
  them to `aAnimationImage::Init` (0x4219f0) next to a constant 4 (taken as the image kind,
  `LSTICON`, which matches where the frames are).
- **What we checked:** `aApplication::ObjAddBagAni` 0x402ed0; 0x4219f0's stores not mapped.
- **Blocks:** nothing (every call uses the same values).
- **Status:** open

### Q-0030 — Who calls RH's entry 999?
- **Context:** `games/ring/docs/rh.md` "Entering": entry 999 fills the bag with RH's late
  items and shows 20501, like NI's test entry (Q-0020).
- **What we checked:** no `push 0x3e7` followed by `push 3` before a `GoZone` call.
- **Blocks:** nothing.
- **Status:** open

### Q-0031 — Sound 23011 is stopped by RH but never started
- **Context:** RH's click handler stops 23011 (`1757.wav`, type 3) at the Daughter (20501
  `unk_19` 0 and 2); the only other reference is its `SouAdd` in the set-up (0x458727).
- **What we checked:** every `push 0x59e3` in the EXE (0x4448b8, 0x4449e8, 0x458727).
- **Blocks:** nothing (stopping a silent sound does nothing).
- **Status:** open

### Q-0040 — N2's handle plays sound 70401, which N2 never declares
- **Context:** `games/ring/docs/n2.md` "Drag": 0x4349b0 (70103) plays and stops 0x11301
  (70401); N2's set-up declares no sound 70401 (NI's handle uses its own 10401).
- **What we checked:** N2's `SouAdd` calls (E-0094's emulated list).
- **Blocks:** nothing (an unknown id is reported and ignored).
- **Status:** open

### Q-0041 — What does `CurSet(0x36)` show at N2's arrival?
- **Context:** entry 0 of `GameSetZoneN2` (0x4362c0) sets cursor 0x36, the kind-1 cursor with
  an empty name of `spec/boot.md`; tracking replaces the cursor every frame.
- **What we checked:** the `CurAdd` table of `spec/boot.md`; kind 1 is a Windows cursor.
- **Blocks:** nothing visible beyond one frame.
- **Status:** open

### Q-0042 — 0x433ee0 runs again at the end of line 70022
- **Context:** N2's sound handler (0x435a00), 70022 ended: 0x433ee0 (which, its conditions
  still holding, starts line 70017 again) and then play(70024), which cuts it.
- **What we checked:** nothing between the two calls changes 0x433ee0's conditions.
- **Blocks:** nothing (the later play wins).
- **Status:** open

### Q-0050 — FO's dead animation branches and test entry
FO's animation handler (0x442b60) reacts to ids 30002..30005 that no set-up call assigns,
shows / hides 30110 presentations 6 and 9 (30110 has four), and pauses 30110/1 at frame 202
of a 200-frame animation (never reached; timer 5 unpauses it anyway). Entry 999
(`GameSetZoneFO` 0x443760) has no caller found. Dead as coded, or reached by data not in
the DVD? (E-0165, E-0160)

### Q-0051 — FO's before-movability tests that cannot match
0x4420b0 tests kind 2 (puzzle → rotation) with `from` 30701..30704 (rotations) and 35111 →
30101 (35111 has no movability in the set-up). Both are unreachable as declared. (E-0164)

### Q-0052 — FO's button-down / take handler
0x441860 is FO's handler for both 0x40bd40 and 0x40bed0 and only reads the object in hand
for 30016; no FO object has flag 2 or 8. Left over from an earlier design? (E-0166)

### Q-0070 — WA's animations that are never shown
Object 51000's animations on the message puzzles 51001..51013, object 50001's on the
arrival close-ups 50001 / 50002, and 50700's presentations 2, 3 (puzzles 50701, 50702) are
declared in the set-up but no WA code shows them (`ObjPreSho` on them appears nowhere in
`engines/ring/notes/decomp/wa/` or the set-up). Unless `PuzSetAct` shows anything (it does
not, per `spec/animation.md`), they are never drawn. Checked against a capture of the
original? (E-0221, E-0225)

### Q-0071 — The tree's "item there" tests
0x437d60 (object 50503, nothing in hand) takes an item back when word 50000 % 10 == 1,
% 100 ≥ 2, % 1000 ≥ 12, % 10000 ≥ 112 for `unk_19` 0..3: the last three are not
per-digit tests (e.g. the Flower and the Leaf alone, 101, pass the Apple's 101 % 100 ≥ 2), so an
item not on its branch can be taken (the bag gets it, the word goes negative in that digit,
score −2). Kept as coded; not checked against the original. (E-0221)

### Q-0072 — WA's entry 999
`GameSetZoneWA(999)` fills the bag for the desk; no `GoZone(6, 999)` caller was found
(like Q-0020, Q-0030). (E-0220)

### Q-0060 — Why does RO clear the lever (byte 40804) when entering the egg puzzle?
- **Context:** the after-movability handler 0x43c450, kind 1, from 40000 or to 40010, sets
  byte 40804 (the pipe room's lever) to 0, although the lever is elsewhere (puzzle 40060)
  and is reset on leaving the pipe room anyway (0x43c290). Harmless as coded.
- **How to answer:** none needed for the engine (kept as coded); a trace of the original
  would only confirm.

### Q-0080 — How fast do the credits scroll?
`ScrollImage` (0x401260) draws one row more per loop with no delay of its own; each pass ends
with the video device's flip (vtable +0x30, E-0096). Whether that flip waits for the
vertical blank (and so the rate, 60 rows a second on a 60 Hz display) is not traced. The
engine scrolls one row per 1/60 s.

