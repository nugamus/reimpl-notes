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
- **Status:** open

### Q-0100 — What is CObjState +0x1c?
- **Context:** `default.dat`, CObjState field 7 (E-0104). ge.dll only hands it to the EXE
  (out-parameter 3 of GEWalkmapGetObjectData / GECUAGetObjectData, 2 of
  GEInventoryGetObjectData).
- **What we checked:** every ge.dll user found by the decompiled exports.
- **Observed range:** 0..160, 120 distinct values; nonzero in 150 states (149 of them
  with a description text), counting up from 1 in file order at the start (1..19), then
  out of order (an inventory picture number?).
- **Blocks:** the inventory and object drawing in the engine.
- **Status:** open

### Q-0101 — What are CAnim +0x18, +0x1c, +0x20 and +0x28?
- **Context:** `default.dat`, CAnim (E-0104). +0x1c, +0x20 and +0x28 go to the EXE through
  GE*GetObjectData; +0x18 has no reader in the functions read.
- **What we checked:** ge.dll's anim users (StepAnim, ClearAnims, BuildSort, the
  GetObjectData exports).
- **Observed range:** +0x18 0 in all 1,182; +0x1c 0..1065 (197 values), +0x20 0..735
  (175) — screen or room coordinates by their range; +0x28 0..246 (247 values) — a picture
  number by its range.
- **Blocks:** drawing objects on walkmaps and in CUAs.
- **Status:** open

### Q-0102 — What do CEvent's sound operands +0x38, +0x3c, +0x44, +0x48 mean?
- **Context:** event types 6 and 17 (E-0105): with an empty +0x40 the EXE callback gets
  (+0x38, +0x3c, +0x48, 0), else (+0x40, +0x48, +0x44).
- **What we checked:** RunEvent; the callbacks are Gilbert.exe functions passed to GEInit
  (arguments 7, 8, 10, 11), not yet read.
- **Observed range:** one numbered sound (2, 0) in 671 type-6 records; +0x44 1 in 456,
  0 in 215; +0x48 0 in 458, 1 in 213 (a loop flag?).
- **Blocks:** sound playback.
- **Status:** open

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
- **Status:** open

### Q-0105 — Do the saved games match default.dat's layout byte for byte?
- **Context:** GESaveFile writes the layout LoadFile reads (E-0100); no saved game is in the
  corpus (the gilbert.ini slots `\data\game\game*`).
- **What we checked:** SaveFile 0x100034e0 against LoadFile 0x100031f0.
- **Observed range:** n/a.
- **Blocks:** reading original saves; `gamedat.py` should be run on one.
- **Status:** open
