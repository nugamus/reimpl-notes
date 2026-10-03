# Open questions (Grumpa engine)

Things we could not determine after checking the original code (Ghidra), the corpus and
traces. An unresolved field goes here and stays opaque (`unk_*`) in the format spec. It
does not get a guessed meaning.

Append only. When a question is answered, keep the entry, mark it `RESOLVED`, and link the
`EVIDENCE.md` entry that resolved it. Ranges follow EVIDENCE.md (Q-0001.. survey, disc and
protection).

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

### Q-0001 — How do we obtain a decrypted `Grumpa.exe` to read?
- **Context:** E-0003: SafeDisc 2.60.052 encrypts `.text` and `.data`; the key comes from
  SafeDisc's run-time check (its DLLs unpacked from the stub, the `secdrv.sys` driver, the
  disc signature of E-0004). Windows 10/11 no longer load `secdrv.sys`.
- **What we checked:** the static bytes (no readable code or strings); nckstwrt's
  SafeDiscLoader2 (GPL-3.0, github.com/nckstwrt/SafeDiscLoader2): it emulates `secdrv`
  and patches the check inside the running game, calling SafeDisc's own decryption, so
  it is a run-time route, not a static decryptor. The classic Safedisc2Cleaner (closed
  freeware) unwraps versions below 2.7 to a file, also by running the stub.
- **Blocks:** Ghidra on the game code: every spec (boot, rendering, scenes, actors) and the
  meaning of every format field.
- **Status:** open

### Q-0002 — Is the engine Idol FX's own and used by this game only (engine name `grumpa`)?
- **Context:** the engine is named after the game, as for Gilbert, until the code shows
  otherwise. The credits name a "FXSTRUCTOR" (E-0002), maybe Idol FX's editor.
- **What we checked:** the corpus only; the EXE's strings are encrypted (E-0003).
- **Blocks:** nothing now; the name of `../scummvm/engines/<engine>`.
- **Status:** open

### Q-0003 — Where does the installer put each file group?
- **Context:** the cabinet is unpacked by file group (E-0001); the installed layout (which
  folder `Grumpa.exe` reads `Scenes/`, `Meshes/`, … from, which language's files it
  takes) is set by the InstallScript `setup.inx` and by the EXE's paths.
- **What we checked:** file-group names only.
- **Blocks:** the run folder for the original and the engine's data paths.
- **Status:** open

### Q-0004 — The `.fxi` block codec's per-mode pixel maths — RESOLVED (see E-0009)
- **Context:** E-0009. The container and byte layout are proven (`fxi.py`, 316/316); what
  remains is how each sub-block mode fills the 8×8 block from its mask + colours: mode 1
  (1bpp, 2 colours), mode 2 (2bpp, 4 colours), mode 3 (raw 8×4 ×2), and how the low- and
  high-nibble sub-blocks combine into the block. `FUN_00418de0`'s write branches are elided
  in the decompiler output; they need the assembly.
- **What we checked:** `FUN_00418de0` structure and byte reads; the surface fill loop in
  `FUN_004555c0`.
- **Blocks:** actually rendering `.fxi` (backgrounds, textures); a round-trip test.
- **Status:** RESOLVED (E-0009). Each control byte's low nibble codes the high
  byte of the block's pixels, its high nibble the low byte; per plane, mode 0 solid, 1
  1bpp/2 values, 2 2bpp/4 values, 3 raw. `fxi.py` decodes 316/316. From the blit at
  `0x00419f7a` and the mode writes at `0x004198c0`+.

### Q-0005 — `.scn` scene record layout
- **Context:** 110 files; header `08 00 00 00`, `58 02 00 00` (600), then a float stream
  (positions with a near-constant Y). Body length is not a whole number of 4-byte floats,
  so the header/record size is not yet right.
- **What we checked:** the corpus; not yet the `CFXScene` loader.
- **Blocks:** scene geometry / collision.
- **Status:** open

### Q-0006 — `.abi` per-class actor serialize bodies
- **Context:** E-0012. The record framing is known (`u32 type, u32 id, class data`, looped
  to EOF) and the 34 actor types with their object sizes
  (`engines/grumpa/notes/actor-types.txt`). What remains for a byte-exact validator is each
  class's serialize (vtable+4): the fields each actor type reads from the stream. The
  common base (id, position, state) is shared; subclasses add their own.
- **What we checked:** `CreateFromABIFile`, `CreateActor`; not yet each serialize.
- **Blocks:** a 100% `.abi` validator; save/load; actor state.
- **Status:** MOSTLY RESOLVED (2026-10-01, E-0100..E-0102). The serialize mode is 1; the 14
  actor types that occur in the corpus are decoded and `engines/grumpa/tools/parsers/abi.py`
  parses **111/111** scene + item `.abi` consuming every byte. Remaining: **type 0x03
  `CFXCharacter`** (`Scenes/Characters.abi`, `Actors/Characters.abi`). Its ~37 KB serialize
  `FUN_00422f80` decompiles with broken control flow (the decompiler's field order does not
  match the bytes), so it was not modelled. Structure read so far, in order: header `f3`
  + EC-vector (+0x11c); fixed block (+0x444, two vec3 at +0x16c/+0x160, five u32); a
  `ClassD` vector (+0x664, `0x409cf0`); then — from the data, not the decompiler — a
  character body with per-state string lists (`.anb` animations, `.wav` sounds, `.tga`
  textures, each a `u32 count` + that many pascal strings, with a "normal" and an
  "In_Boat" set), a 6-entry attachment/weapon table of `{pascal .ANB name, pascal .tga
  name, 3 u32}`, and an opaque **binary skeleton blob** (~400 B of packed non-float data,
  no obvious length prefix) that is the sticking point. Finishing type 0x03 needs a
  disassembly-level reverse of `FUN_00422f80` (the decompiler is unusable for it).

### Q-0007 — The `.anb` trailing-frame count: F vs F-1
- **Context:** E-0014. `.anb` geometry, UVs and the animation block are decoded (938/939
  parse). The trailing animation block is `K*(ΣA)*24` bytes: K = F-1 frames for most meshes
  but K = F for the `X2Y` transition-animation clips (their names carry the state pair). The
  discriminator here is the file name, not yet a field found inside the file; and
  `012_D2D_Grumpa_In_Boat.ANB` has 4,456 unexplained trailing bytes.
- **What we checked:** `FUN_004157d0` (the final read is `(F-1)*ΣA*24`, yet the X2Y files
  hold one more frame); a name/prefix census of all 939 files.
- **Blocks:** knowing which stored frame is the rest pose; nothing for a static render.
- **Status:** open (find the in-file flag; the parser accepts K in {F-1, F})

### Q-0008 — The per-view camera (to composite actors into pre-rendered scenes)
- **Context:** E-0016. Each scene view is a pre-rendered 800×600 background + `.fxi` depth
  (E-0011); actors are placed in world 3D and projected with the camera the view was
  rendered at, then depth-tested against the `.fxi`. The engine's rasteriser works
  (E-0016) but needs that camera (eye position, look direction, vertical FOV, near/far) per
  view, and the mapping from `.fxi` depth values to world Z, to place and occlude actors
  correctly.
- **What we checked:** the device init (`FUN_00436aa0`, 800×600×16, no projection there);
  the `.scn` load path (`FUN_0040cb30` opens `Scene_N.scn` but does not parse camera data in
  that function); the mesh upload (`FUN_004154b0`). The camera is set during the scene
  render tick, from scene data whose location is not yet found.
- **Blocks:** scene-accurate actor rendering and occlusion; picking/hotspots.
- **Status:** open. Plan: boot into a scene with `startScene.txt` (E-0017) through
  SafeDiscLoader2 (as `sddump.py` does), then read the live view/projection matrix from the
  decrypted process — the fastest ground truth for the camera, near/far and scale. The
  static alternative is to trace the scene render tick to the device `SetTransform`.
  Runtime prerequisites found: the original resolves its data via the registry key
  `SOFTWARE\Idol FX\Grumpa` value `DataPath` (`FUN_00447840`/`FUN_00436aa0`; the read is
  behind a SafeDisc stub) and errors "Cant Find Registry Key, Fatal Error" if absent — so a
  runtime run needs that key set to the `cab` data folder, plus `startScene.txt` with a scene
  number, launched through SafeDiscLoader2. Then dump the decrypted process (as `sddump.py`
  does) and locate the perspective projection matrix (recognisable: 1/tan(fov) diagonal, a
  ±1 in the w column) and the per-view world matrix near the device object.
  The exact registry key is `HKLM\Software\Idol FX\Grumpa` value `DataPath` (the
  InstallShield template `Software\COMPANY_NAME\TITLE_MAIN` in `data1.hdr`; for the 32-bit
  game, `HKLM\Software\WOW6432Node\Idol FX\Grumpa`). Setting it needs admin, which this
  session lacks (HKCU is ignored by the game), so the runtime route is blocked here — it
  needs the user to run once (elevated):
  `reg add "HKLM\Software\WOW6432Node\Idol FX\Grumpa" /v DataPath /t REG_SZ /d "<cab path>" /f`.
  The on-disk EXE is SafeDisc-encrypted so it cannot be patched to read HKCU instead.


### Q-0008 UPDATE (2026-10-01) — camera is in the scene `.abi`; runtime routes SafeDisc-blocked
- A scene view has only `<n>_<v>_IS.jpg` + `_IZ.fxi`; per scene only `Scene_N.scn` (the
  walkmesh: nodes of position + up-vector, constant Y, E-0017 revisited) and `Scene_N.abi`
  (actors). So the per-view camera is in `Scene_N.abi`, reachable only by parsing the actor
  serialize tree. Scene_001.abi's first record is type 0x11, a container whose serialize
  (`FUN_0043d200`) reads three lists of sub-objects (0x118/0x128/0x128-byte each) before a
  0x68 (104-byte) block that may be the view matrix — so reaching it needs the nested
  sub-object serializes (a deep, multi-function decode; Q-0006).
- Runtime extraction is blocked: the user set `HKLM\Software\WOW6432Node\Idol FX\Grumpa  DataPath`, and dgVoodoo2 (third_party/dgVoodoo2_87_3, DDraw/D3DImm in `C:\GrumpaRun`)
  lets SafeDiscLoader2 get further, but SafeDisc init hangs deterministically at 19/159
  resolved imports (never reaches the scene). Safedisc2Cleaner fails ("can't get 2nd DLL" —
  needs secdrv). The decrypted dump's 140 stub imports stay unresolved. So the live camera
  cannot be read on this modern-Windows setup.
- **Conclusion:** the camera (and thus actors-in-scenes) needs either a machine that runs
  the SafeDisc original, or the deep offline `.abi` serialize-tree decode (Q-0006). Both are
  multi-session. The rendering engine is ready for the camera once it is known.

### Q-0008 RESOLVED (2026-10-01, E-0103) — the camera block is decoded (offline `.abi` route)
The offline decode won. The type-0x11 view serialize `FUN_0043d200` reads, after its two
`ClassC` vectors, a `u32 cam_id` and then a **0x68 block = 26 little-endian floats** at
`this+0x14c`, handed to the render device
`dev->vtable[0x38]()->vtable[0x48](*(this+0x1b4), block)`. Profiled over all 107
single-view scenes (`abi.py`), the only non-zero/varying floats are: `f1=1.0`,
`f2∈[0.75,1.0]`, `f3∈[0.70,1.0]` (projection scale/aspect/FOV), **`f13,f14,f15` = camera
eye position (x,y,z)** (range ±~7000, scene-sized), `f19` = range/far (157..10291, scales
with scene extent), `f21=1.0`; every other float (0, 4–12, 16–18, 20, 22–25) is 0 across the
whole corpus — the rotation fields, zero because these views are axis-aligned. The engine
can place actors at world `f13..f15` and project with `f2`/`f3` + `f19`.
- **Remaining sub-point:** the exact meaning of `f2`/`f3`/`f19` (aspect vs vertical FOV vs
  focal length, and near/far split) and the rotation fields need the device consumer
  `vtable[0x48]` decompiled, or a non-axis-aligned view in a later corpus; the position is
  unambiguous and sufficient to start compositing.

### Q-0001 RESOLVED (2026-10-01) — runnable SafeDisc-free Grumpa.exe
The user supplied a no-CD `Grumpa.exe` (Grumpa_NoCD_Win_SV-NO-FI-DA): `.text` decrypted
(entropy 6.53), `stxt*` loader sections gone, all 8 import DLLs resolved. Runs under
dgVoodoo2 (C:\GrumpaNoCD); imported to Ghidra as `/grumpa-import/GRUMPA_NOCD.EXE` with full
imports. Supersedes the SafeDiscLoader2 dump (which had unresolved stub imports).

### Q-0003 RESOLVED (2026-10-01) — installed data layout
Grumpa.exe reads `<DataPath>/{Scenes,Bitmaps,Meshes,Actors,UI,Sounds,Movies,Save}`, DataPath
from HKLM\Software\Idol FX\Grumpa. The installer maps cab file groups to it: Bitmaps/Meshes/
Scenes/Actors/UI/Save keep names; `Sounds_`+`Sounds_<Lang>` merge into `Sounds/`;
`Movies_<Lang>` (or ISO `Movies/`) -> `Movies/`. Proven by the no-CD's error
`CFXSound::CreateFromFile ...\Sounds\ambient_combat.wav`. `C:\GrumpaData` reproduces it.

## Q-0009 — How a type-0x0d sprite prop is placed and composited

E-0106 shows 0x0d props are animated JPG frame sequences, but the record's integer header
fields are animation parameters (frame count/rate/loop), not screen coordinates, and no
`_Z####.fxi` depth file accompanies the sampled props (`cannons`, `butterfly3`). Open: the
per-frame screen position, the compositing order/depth against the background, and the
transparency (colour key? the JPG has no alpha). Needs the 0x0d draw path (not just
`Serialize`) in the decrypted `Grumpa.exe`.

## Q-0010 — How a 0x19 hotspot's action (scene change, interaction) is bound

E-0108 recovers the clickable polygon, but the record has no inline target. The action (go to
scene, play a sound, set a state, pick up an item) must come from the game's event/command
system — the EC/CC vectors on the trigger, an id-keyed command table, or the per-scene script.
Needs the 0x19 click-handling and event-dispatch code in the decrypted `Grumpa.exe`. This is
the entry point to the game-logic layer (navigation, puzzles, dialogues, inventory).

## Q-0011 — The view -> background mapping (which camera a shown background uses)

A scene has several type-0x11 views, each with its own camera eye (E-0105), but a different
number of background views `<n>_<k>_IS.jpg`: Scene_061 has 4 views (ids 630..633) but 2
backgrounds (61_1, 61_2); Scene_100 has 2 views, 1 background; Scene_007 has 1 view, 1
background. So the displayed background does not map 1:1 to `views[0]`. To place the 3D mesh
actors (type 0x1a, E-0114, meshes authored in world space) and to drive multi-view
navigation, the engine needs to know which view's camera matches the shown background. The
view's camera "handle" is `view[+0x108] - 0x276` (FUN_0043d200); candidates: a background-index
field in the view record, a handle->background convention, or a link in the `.scn` file
(Q-0005). Needs the scene-display/camera-select code.

## Q-0200 — Sprite frame rate: the device value R in `R / fps`

A sprite advances one frame every `R / fps` updates (E-0208), R from a device call
(`+0x15c` object, vtable `0x28`). The engine takes R = 50 (the update rate, so `fps` is
frames per second). Needs that device function's return value.

## Q-0201 — View index -> background file

Views are numbered from 0 (`actor602+0xdd0`, triggers' `+0x174`, `(185, 30, v)`); the
backgrounds are `<n>_<k>_IS.jpg` from k = 1. The corpus fits `k = v + 1` (E-0206), but the
switch code (`FUN_0045ae00`) loads view matrices, not files; the file choice is elsewhere
(`.scn`, actor 602).

## Q-0202 — The proximity gate without a player character

Click triggers are gated on the player character's sphere overlapping the trigger's
(E-0207). Until the engine has a player character (type 0x03, Q-0006), it lets clicks pass
the gate and never fires walk-in triggers. Open: the sphere fields' layout (the trigger's
`+0x13c` sub-object, the character's position from `FUN_00424e90`).

## Q-0203 — The shipped `Save/Current/*_status.abi`

`Save/Current/` on the disc holds `001_status.abi`, `211_status.abi`, `307_status.abi`,
`500_status.abi` and `remote.abi`. LoadGameStatus reads `Current/<n>_status.abi` on scene
entry (E-0202), so these would seed scenes 1, 211, 307 and 500 on a first visit unless a new
game clears the folder. Who clears or copies `Current/` (new game, load) is not read yet.

### Q-0005 RESOLVED (2026-10-02, E-0500) — `.scn` = walk mesh + scene links + view list
`parsers/scn.py` parses 110/110. Field meanings still open are Q-0500/Q-0501.

### Q-0203 RESOLVED (2026-10-02, E-0501) — new game empties `Current\`

### Q-0500 — `.scn` fields without a meaning yet
- **Context:** E-0500: the walk mesh's vertex floats 3..7 and per-face u16, the exit's
  fourth float (a radius?), and the two 0x14 slots (State, Scene_ID).
- **What we checked:** the Serialize functions and corpus statistics (floats 3..5 always
  0, 1.0, 0; floats 6, 7 vary, −1.7e38 in ~8 %; face u16 ∈ {0,1,2,3,12,13,19,20}).
- **Blocks:** walking / collision and scene-exit regions (the walk code, not yet read).
- **Status:** open

### Q-0501 — The view list's two 4×4 matrices
- **Context:** E-0500: type 9 has two 64-byte matrices per view; the first looks like a
  view matrix, the second like a Direct3D projection (near ≈ 59.6).
- **What we checked:** values in Scene_001; not the code that consumes them
  (`FUN_0045ae00` loads them on a view switch, Q-0201).
- **Blocks:** the exact camera for 3D actors (Q-0008).
- **Status:** open

### Q-0502 — The inventory's left equipment slot and its two buttons
- **Context:** E-0504: `FUN_00437d00` op 18 — the left equipment slot rect `+0x228` and
  the buttons `+0x258`/`+0x248` (they send 61/60 to actor 1, the second only when the
  current scene is not 1) lie behind `ud2` bytes in the dump, where the decompile stops.
- **What we checked:** decompiler; disassembly up to the `ud2`.
- **Blocks:** weapons in the inventory; the panel's save/load icons (Help.txt: diskette =
  saved games, door = main menu). The engine uses ScummVM's save/load instead.
- **Status:** open

## Q-0400 — How `Sounds_` and `Sounds_<lang>` merge into the installed `Sounds` folder

The game opens `<data>\Sounds\<name>` (E-0405). The cabinet has a common group `Sounds_` (550
files) and one per language (`Sounds_Swedish` 241 ... `Sounds_Danish` 280); 182..203 names are
in both with different bytes. The engine assumes the language group is installed over the
common one (the language file wins). Needs the setup script (`<Support>Script` group) or an
installed copy.

## Q-0401 — What the speaker's talking flag does

Playing a voice line sets `+0x67c = 1` in the speaker's mesh object (E-0405). Whether that
selects a talk animation, moves the mouth, or only blocks other lines is not read yet. The
engine logs the speaker.

## Q-0402 — The six-value header vector of a character

`n × u32` after `visible` (E-0400): 6 values per character, e.g. Grumpa (32, 100, 5, 2, 1, 0),
pirate rat (20, 60, 12, 0, 0, 0), Ratbeard (32, 400, 40, 18, 1, 0). The second looks like
health; the others need the combat code.

## Q-0403 — Character roles: following, riding, combat

DoCommand opcodes 0x2c..0x30 and 0x54 give a character a role (mesh `+0x564` = 1..7: player
control, follower, ...), and the rule/reaction lists (E-0401) drive behaviour. Not specced:
movement, the animation state machine over the `.anb` list, combat.

### Q-0006 RESOLVED (2026-10-02, E-0400, E-0401) — type 0x03 `CFXCharacter`
The original's own Serialize, run under Unicorn on both `Characters.abi` files
(`tools/abiemu.py`), consumes every byte (44 + 44 records) and gives the grammar; `abi.py`
`t_03` implements it and now parses 113/113 `.abi` files. The "binary skeleton blob" was the
ClassD rule vector and CC command lists; the decompiler's broken control flow no longer matters.
Field meanings: E-0402; the shared actor header (`id` read twice) is E-0400.

### Q-0402 narrowed (2026-10-03, E-0407)
The six values are the character's state slots (slot 0 "State"); which opcodes change slots
1..5 and what they mean is still open.

### Q-0501 RESOLVED (2026-10-03, E-0301) — the view list's matrices are the D3D view and projection
`FUN_0045ae00` (SetView, 185 op 30) passes `this+0x13c+v*0x40` to
`IDirect3DDevice7::SetTransform(VIEW)` and `this+0x27c+v*0x40` to `SetTransform(PROJECTION)`
(grumpa-render, E-0301); the format stays in E-0500 / `scn.py`.
