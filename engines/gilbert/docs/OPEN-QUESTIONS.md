# Open questions (Gilbert engine)

Things we could not determine after checking the original code (Ghidra), the corpus and
traces. An unresolved field goes here and stays opaque (`unk_*`) in the format spec. It
does not get a guessed meaning.

Append only. When a question is answered, keep the entry, mark it `RESOLVED`, and link the
`EVIDENCE.md` entry that resolved it. Ranges follow EVIDENCE.md (Q-0001.. survey and front
end, Q-0100.. `default.dat` and `ge.dll`).

## Entry format

```
### Q-0001 — <one-line question>
- **Context:** where it came from (format + offset, function address, trace line).
- **What we checked:** the original code, the corpus, traces.
- **Observed range:** for a data field, the set of values seen across the corpus.
- **Blocks:** what work is stalled or degraded by not knowing this.
- **Status:** open | RESOLVED (see E-nnnn)
```

## Questions

### Q-0001 — What are the wave blobs' trailing byte and their RIFF size (length + 2)?
- **Context:** E-0010, `Wave.WAVE` in `.wxs`/`.dxw`.
- **What we checked:** the corpus only; DelphiX's TWave writer not yet located in
  Gilbert.exe (unit `wave`).
- **Observed range:** tail byte 0 in all 58 blobs; RIFF size field = blob length + 2 in all.
- **Blocks:** nothing for playback (the `fmt `/`data` chunks are consistent); matters only
  for writing the files back.
- **Status:** open

### Q-0002 — What do the control-map cell values mean?
- **Context:** E-0011, `ctrl<room>.map` grid, values 0..29.
- **What we checked:** the corpus: 0 and 1 dominate (walkable floor and walls by their
  shapes in the ASCII plots), 2..29 form small blocks at doorways and objects. The users of
  the grid (`GEPathNewPath`, `GEWalkmapAreaHit`, Gilbert.exe's room code) not yet read.
- **Observed range:** 0..29; at most 17 distinct values per room.
- **Blocks:** walking, room exits and hot spots.
- **Status:** RESOLVED (see E-0409, E-0411; Gilbert.exe's side E-0305, E-0307): 0 floor, 1 wall (never walkable, the "no" cursor), 2..31 area n = value − 1: walkable only by a path whose target cell has the same value, and reached on a path it runs event walkmap × 100 + n (GEWalkmapAreaHit).

### Q-0100 — What is CObjState +0x1c?
- **Context:** `default.dat`, CObjState field 7 (E-0104). ge.dll only hands it to the EXE
  (out-parameter 3 of GEWalkmapGetObjectData / GECUAGetObjectData, 2 of
  GEInventoryGetObjectData).
- **What we checked:** every ge.dll user found by the decompiled exports.
- **Observed range:** 0..160, 120 distinct values; nonzero in 150 states (149 of them
  with a description text), counting up from 1 in file order at the start (1..19), then
  out of order (an inventory picture number?).
- **Blocks:** the inventory and object drawing in the engine.
- **Status:** RESOLVED (see E-0403): the inventory icon, a pattern (0..160) of the one 22×20-pattern picture in `inventory.wxi`, used in the inventory grid and for the carried object on the cursor.

### Q-0101 — What are CAnim +0x18, +0x1c, +0x20 and +0x28?
- **Context:** `default.dat`, CAnim (E-0104). +0x1c, +0x20 and +0x28 go to the EXE through
  GE*GetObjectData; +0x18 has no reader in the functions read.
- **What we checked:** ge.dll's anim users (StepAnim, ClearAnims, BuildSort, the
  GetObjectData exports).
- **Observed range:** +0x18 0 in all 1,182; +0x1c 0..1065 (197 values), +0x20 0..735
  (175) — screen or room coordinates by their range; +0x28 0..246 (247 values) — a picture
  number by its range.
- **Blocks:** drawing objects on walkmaps and in CUAs.
- **Status:** open for +0x18 (no reader in ge.dll's anim code); +0x1c, +0x20 and +0x28 answered for walkmaps (E-0308) and CUAs (E-0403): the picture's top-left corner and its item in `w<n>o.wxi` / `cua<id>.wxi`.

### Q-0102 — What do CEvent's sound operands +0x38, +0x3c, +0x44, +0x48 mean?
- **Context:** event types 6 and 17 (E-0105): with an empty +0x40 the EXE callback gets
  (+0x38, +0x3c, +0x48, 0), else (+0x40, +0x48, +0x44).
- **What we checked:** RunEvent; the callbacks are Gilbert.exe functions passed to GEInit
  (arguments 7, 8, 10, 11), not yet read.
- **Observed range:** one numbered sound (2, 0) in 671 type-6 records; +0x44 1 in 456,
  0 in 215; +0x48 0 in 458, 1 in 213 (a loop flag?).
- **Blocks:** sound playback.
- **Status:** RESOLVED (see E-0406): +0x38 wave list, +0x3c item (PlayWave), +0x48 loop flag (both forms), +0x44 stream kind for named sounds (0 room music, 1 dialogue voice, 2 other stream).

### Q-0103 — What is CDialogChoice +4?
- **Context:** `default.dat`, CDialogChoice field 1; GEDialogGetChoice and GEDialogEnd
  address choices by list index, not by +4.
- **What we checked:** ge.dll's dialogue exports and LoadDialogChoices.
- **Observed range:** 0..11 (1: 352, 9: 352, 2: 49, 3: 17, …); 351 of the 352 "Annuller"
  (cancel) choices carry 9.
- **Blocks:** nothing known; stays `unk_04`.
- **Status:** open

### Q-0104 — What is GotoWalkmap's fourth argument (header +0x10, CEvent +0x58)?
- **Context:** header u32 +0x10 (saved as 0) and CEvent +0x58 of type 4, both passed to
  the EXE's goto-walkmap callback (GEInit argument 1).
- **What we checked:** GotoWalkmap 0x10008fa0, SaveFile, RunEvent.
- **Observed range:** CEvent +0x58 in type 4: 0 (108), 16 (49), 24 (36), 8 (22), 28 (12),
  12, 4, 20 — multiples of 4 below 32 (a facing direction?).
- **Blocks:** placing Gilbert on entering a walkmap.
- **Status:** RESOLVED (see E-0300, E-0304): Gilbert.exe stores it as the facing direction (0 up, 4 up-right, 8 right, 12 down-right, 16 down, 20 down-left, 24 left, 28 up-left); it picks the standing frames and the shadow.

### Q-0105 — Do the saved games match default.dat's layout byte for byte?
- **Context:** GESaveFile writes the layout LoadFile reads (E-0100); no saved game is in the
  corpus (the gilbert.ini slots `\data\game\game*`).
- **What we checked:** SaveFile 0x100034e0 against LoadFile 0x100031f0.
- **Observed range:** n/a.
- **Blocks:** reading original saves; `gamedat.py` should be run on one.
- **Status:** open

### Q-0200 — How long should the loading panel's busy wait last?
- **Context:** E-0206, boot::LoadingStep 0x478234 → 0x477954(50): 50,000,000 iterations of
  a `dec`/`jnz` loop after each of the five loading steps.
- **What we checked:** the code; there is no clock involved, so the time depends on the CPU
  (roughly 25–100 ms on the 300–500 MHz machines of 1999, ~1 cycle per iteration).
- **Observed range:** —
- **Blocks:** the length of the loading screen in the engine (a fixed delay has to be
  chosen; a trace of the original on period hardware would settle it).
- **Status:** open

### Q-0201 — Which font measures the first loading line?
- **Context:** E-0206: the text width that centres the line is taken from the back
  buffer's canvas before 0x460d24 sets Arial 8, so each step measures with the font of the
  previous text; for step 2 that is the canvas's initial font.
- **What we checked:** the code order; the canvas's initial font is DelphiX/VCL state not
  read.
- **Observed range:** —
- **Blocks:** a pixel-exact x of the first loading line only (the engine can centre with
  Arial 8).
- **Status:** open

### Q-0202 — What exactly does FillRectAlpha's blend mode 8 compute?
- **Context:** E-0215, 0x45c670 → 0x4585ac with mode 8 and ColorToRGB(colour) or
  (alpha shl 24): the row highlights ((196, 38, 0), alpha 50) and the pulsing save field
  (alpha 0..80).
- **What we checked:** the call; DelphiX's `FillRectAlpha` passes
  DXR_BLEND_SRCALPHA1_ADD_INVSRCALPHA2 (colour × a + destination × (1 − a)) if that is the
  ninth value of TDXR_Blend; the blend routine 0x4585ac itself was not read.
- **Observed range:** modes used: 8 only.
- **Blocks:** exact highlight colours (the engine can use a plain alpha blend, a = alpha/255).
- **Status:** open

### Q-0203 — Which colour is transparent on the help and credits text surfaces?
- **Context:** E-0215: the text surfaces are filled with colour 0 and drawn with the
  transparent flag; the surfaces' TransparentColor is never set by the game.
- **What we checked:** the calls; DelphiX's default for an off-screen surface's colour key
  not confirmed in the binary.
- **Observed range:** —
- **Blocks:** nothing in practice (black transparent is the only reading that shows the
  backgrounds as intended).
- **Status:** open

### Q-0204 — Which InstallationType values does the installer write?
- **Context:** E-0201, E-0214, E-0216: the game only compares `InstallationType` with −1
  (the value when the registry key is missing); −1 disables saving.
- **What we checked:** Gilbert.exe's uses; the installer (`gSetup.exe`, `setup.ins`) not
  read.
- **Observed range:** −1 (default) and whatever the installer writes.
- **Blocks:** nothing for the engine (it has no installer: use a value ≠ −1).
- **Status:** open

### Q-0205 — How large is the GDI text in pixels?
- **Context:** E-0206, E-0215: TCanvas text with Font.Name 'Arial', Font.Size 8 (9, 11 in
  the credits) on the 640×480 surface's DC.
- **What we checked:** the font calls; the pixel height follows from the DC's logical DPI
  (96 → 11 px for size 8), and GDI may antialias; no capture.
- **Observed range:** sizes 8, 9, 11; styles regular and bold.
- **Blocks:** pixel-exact text; the engine needs an Arial-metric font.
- **Status:** open

### Q-0206 — Is primary+0x90 the IDirectDrawGammaControl?
- **Context:** E-0218: vtable slots 3 and 4 of the interface at primary+0x90, called with
  (0, ramp), fit GetGammaRamp and SetGammaRamp.
- **What we checked:** the calls and the ramp arrays; the QueryInterface that obtains the
  interface (in the DelphiX/wDx surface code) not located.
- **Observed range:** —
- **Blocks:** the room fade-in (rooms spec), not the menu.
- **Status:** open

### Q-0207 — What is the menu's real frame rate?
- **Context:** E-0204, E-0210: DXTimer1.Interval := 16 ms; each menu tick ends with a flip
  of a screen created with doWaitVBlank and doFlip (E-0004).
- **What we checked:** the interval; DelphiX's TDXTimer idle-loop scheduling and the
  vertical-blank wait not read, no trace.
- **Observed range:** —
- **Blocks:** speeds tied to ticks: the credits scroll (0.5 px per tick), the save-field
  pulse, the menu-music start (10th tick).
- **Status:** open

### Q-0300 — How long do the room fades last?
- **Context:** E-0301: FadeOut and FadeIn each call SetGammaRamp 256 times in a loop (one
  ramp entry changed per call), with no clock or wait of their own.
- **What we checked:** the two loops and their callers (room::Load, room::Draw's first
  frame); the driver's SetGammaRamp timing (a vertical-blank wait or not) is not in the EXE.
- **Observed range:** —
- **Blocks:** the length of the fade between rooms in the engine (a fixed duration has to be
  chosen; a capture of the original would settle it).
- **Status:** open

### Q-0301 — Is Gilbert's 120×120 shadow scaled into the 96×96 rectangle?
- **Context:** E-0303: DrawAlpha(gilbert.wxi item 1 `all`, Rect(X, Y, X + 96, Y + 96),
  pattern, 70); the item's patterns are 120×120.
- **What we checked:** DrawAlpha 0x463d8c passes the pattern's source rectangle and the
  destination rectangle to the surface blend 0x45c2a4 (blend 8 below alpha 255); the
  DelphiX rectangle-blend routine that would stretch or crop was not read.
- **Observed range:** —
- **Blocks:** the shadow's exact size and position (stretched: 0.8 scale; cropped: the top-left
  96×96 of the pattern).
- **Status:** open

### Q-0400 — What should SetState do when an object has no state with that number?
- **Context:** `CObj::SetState` 0x10009e40 (E-0405): without a matching state it stores
  `CObList::FindIndex(states, 0)`, a list node, as the current state, so the object's
  fields are read from the node (garbage). Reached by events 2 and 14 (state + 1).
- **What we checked:** every type-2 record names an existing state (314/314) and every
  type-14 record names a state whose successor exists (7/7); whether an event 14 can run
  twice on the same object at run time is not known statically.
- **Observed range:** —
- **Blocks:** nothing in the known data; the engine needs a defined fallback (the first
  state, as the code evidently intends).
- **Status:** open

### Q-0401 — Should changes to objects shown on the walkmap appear before the next rebuild?
- **Context:** the walkmap object list is rebuilt only by GotoWalkmap and CUAEnd (E-0402,
  E-0404). Events 2, 14, 15, 16 change a listed walkmap object without a rebuild (its
  entry keeps its old anim or visibility until then); events 1 and 8 delete an object but
  leave its pointer in the walkmap list and in FindObj's index (a dangling pointer in the
  original, E-0405).
- **What we checked:** default.dat: 20 objects have a walkmap anim; events touching them:
  type 15 (12), 2 (11), 1 (8), 16 (7), 7 (6). Whether these run while their walkmap is
  shown (area and anim-end events) or only inside CUAs was not traced.
- **Observed range:** —
- **Blocks:** faithful walkmap drawing after such events; the engine must at least drop
  deleted objects from its lists.
- **Status:** open
