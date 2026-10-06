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
(E-0207). Until the engine has a moving player character (type 0x03, Q-0006), a click
stands in for walking there: it passes the gate and also fires walk-in triggers inside
their polygon. Open: the sphere fields' layout (the trigger's
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

### Q-0008 RESOLVED again (2026-10-03, E-0300, E-0301) — the 0x11 block is a light; the camera is in the `.scn`
The 0x68 block of E-0103 is a `D3DLIGHT7` (`IDirect3DDevice7::SetLight`, E-0300), not a camera.
The cameras are the Direct3D view and projection matrices of the `.scn`'s CFXView record,
set with `SetTransform` on a view switch (E-0301); the z-buffer value is the projection's
z/w × 65535 and is compared less-or-equal against the `_IZ.fxi` loaded into it.

### Q-0009 RESOLVED (2026-10-03, E-0302, E-0305) — sprite placement, key and depth
Position `+0x190/+0x194`, its view `+0x1c8`, its layer `+0x114` (1 behind the 3D actors,
4 in front). The colour key is on when `+0x1f8` = 1: the COLORREF `+0x208`, or frame 0's
pixel (0,0). Otherwise the sprite is opaque: no blend modes, the smoke and water sprites are
opaque patches of their background. Depth frames `_Z####.fxi` are copied into the z-buffer.

### Q-0011 RESOLVED (2026-10-03, E-0301, E-0304) — view k is entry k of the `.scn` view list
Each view carries its own background, depth and camera. View 0 is shown on scene entry.
185 op 30 switches the view, and so does the player's floor cell.

### Q-0501 RESOLVED (2026-10-03, E-0301) — matrix A is the Direct3D VIEW, B the PROJECTION

## Q-0404 — The sign of a character's yaw

A character's orientation `+0x160` has only `y` set (E-0402). The engine turns the idle mesh
by it as D3DX's `RotationY` does (x' = x cos + z sin, z' = −x sin + z cos); the original's
world-matrix build for characters is not read yet. Dev `grumpa_vm=1;...;snap` shows Grumpa
standing on the hut floor behind the pitchfork, which fits the position but does not decide
the sign.

### Q-0007 RESOLVED (2026-10-03, E-0600) — the `.anb` frame count is F
The loader reads frame 0 with the sections and `F-1` frames after them, then closes the
file: the extra stored frame of 521 files and the boat's 4,456 bytes are never read. Frame 0
is the first frame of the clip (the rest pose is not a separate frame).

### Q-0600 — The 0x1a fields that are not animation
- **Context:** E-0601. `+0x1bc` bubble flags (1, 2, 8, 0x10) with `+0x1e4`, `+0x220..+0x228`
  and the 3rd..7th command lists drive collision tests of bubbles that follow mesh vertices
  (`FUN_004539a0`, on by `+0x1e0`, ops 14/15); `+0x1d0` = 1 (14 records) registers the actor
  with the object at `DAT_004b9bc4 + 0x960` on op 23; `+0x29c` = 1 (16) takes the texture of a
  character's current skin on op 23 (`+0x2a0` = the character, or 3/4/0x5b..0x5d for
  manager slots); `+0x27c..+0x290`; the two `0x401bb0` sub-objects.
- **Blocks:** nothing of the drawing; the bubble hits are combat/interaction (with Q-0403).
- **Status:** open

### Q-0601 — The per-frame vector table on a character clip (`mesh + 0x150`)
- **Context:** E-0603. The character update reads 12 bytes per frame from a table at
  `+0x150` of the current clip's mesh and adds to the character's position / heading; the
  `.anb` has no such block (E-0600), so it is built at load or comes from another file.
- **Blocks:** walking (Q-0403).
- **Status:** open

### Q-0200 RESOLVED (2026-10-03, E-0701) — R = 50, the device's frame rate

### Q-0202 PARTLY RESOLVED (2026-10-03, E-0705) — the sphere fields
The trigger's sphere is the four floats after its polygon; the character's is its position
raised by its radius `[0x290]` from Characters.abi. Still open: the player's character does
not move in the engine (Q-0403), so a click keeps standing in for walking into the sphere.

### Q-0700 — Does the ambience already play under the main menu?
- **Context:** E-0702: loading `global2.atx` plays the start index (0, the jungle). The
  global actors are loaded at boot and again by a new game (E-0501, E-0402).
- **What we checked:** the ambience class; not whether the boot load runs before the menu or
  whether the menu silences it.
- **Blocks:** nothing in play: the engine starts the ambience with the first scene of a game.
- **Status:** open

### Q-0502 RESOLVED (2026-10-03, E-0901) — the weapon slot and the two buttons

### Q-0700 RESOLVED (2026-10-03, E-0902) — the ambience plays from boot, under the main menu

### Q-0900 — Which picture is cursor kind 2 (and 1, 7)?
- **Context:** E-0900: hovering an item (and a hotspot) sets the cursor's kind 2
  (`FUN_004461a0`); the panel buttons need kind 1. `002_Cursor.atx` lists nine pictures
  (`default`, `grabing`, `pointpush`, `pull`, `push`, `stop`, `attack`, `itemglitter`,
  `arrow1_`).
- **What we checked:** the setter; not the cursor's draw, which maps the kind to a picture.
- **Blocks:** nothing: the engine shows `grabing` over hotspots and items, `default` else.
- **Status:** resolved (2026-10-06, E-1720, E-1721): kind k = picture slot k (1 default, 2 grabing, 7 attack, 9..24 arrows).

### Q-0500 PARTLY RESOLVED (2026-10-06, E-0800..E-0804)
The walk mesh code reads only vertex floats 0..2; floats 3..7 (normal (0,1,0) and two more,
likely uv) are never read by the floor, so the engine can ignore them. The per-face u16 is
the floor type (E-0803: 12/13 water-like, 19/20/21 blocking walls toggled by floor opcodes
5/6). The exit's fourth float is the sphere radius; exits change scene, entries place the
player (E-0804). Still open: Q-0800.

### Q-0800 — Floor types 1, 2, 3, 8 and the meaning of mode `+0x48c`
- **Context:** E-0803: the character stores the floor type at `+0x450`; only types 12, 13,
  >18 and the platform value 15 are tested in the update. Corpus face counts: 0 35917,
  1 7426, 13 2981, 2 2931, 3 1192, 19 503, 12 273, 20 108, 8 46, 21 6.
- **What we checked:** the update at `0x421a60`; the dump has no other reader of `+0x450`
  (it may be read through a pointer, e.g. footstep sounds or the actor 3/4 holders).
- **Blocks:** nothing for walking; footsteps / swimming detail.
- **Status:** open

### Q-0202 update (2026-10-06) — items use the same stand-in
Items lying in a scene (E-0900) are hovered and picked up only with the player's character
within 160 units. Until the character walks, the engine skips that reach test, as the click
stands in for walking to the item (`inventory.cpp` update). Restore it with the trigger sphere.

### Q-0805 — The cursor angle's exact formula
- **Context:** E-0812: mouse actor `+0x154` = π ± acos(one component of the normalized
  cursor-minus-character screen vector), negated when d.x > 0; view yaw `+0xdf4` the same
  from the view matrix. Which component goes to acos (`FUN_0047c9f0` after `FUN_00473ddd`
  at `0x445360`) is not read; nor the setter of the turn lock `+0x4dc` and what
  `FUN_004219f0(−2.0)` does (the bump on a too-high step).
- **Blocks:** the exact steering direction toward the cursor.
- **Status:** open

### Q-0806 — Combat: the stance, attacks and the hit test
- **Context:** E-0811/E-0812: Ctrl = stance; left = random attack slot 0x12..0x14, right =
  0x15 (adds 5 to `+0x44c` of the role mesh while it plays); the hit timer `+0x2b4` runs
  `FUN_00446db0`: characters of actors 91..94 within 140 units and in front (dot < −0.8)
  get `FUN_00425730(attacker, damage from mesh +0x334)`.
- **Blocks:** combat.
- **Status:** open

### Q-0807 — Six `.amb`/`.anb` frame-count mismatches
- **Context:** E-0815: e.g. `008_N2D_Grumpa_On_Dragonfly` 22 vs 40, `008_N2D_PirateRat1` 22
  vs 23. The update indexes the table by frame with no bound, so the original reads past it.
- **Blocks:** nothing for walking; clamp in the engine.
- **Status:** open

### Q-0601 RESOLVED (2026-10-06, E-0814, E-0815) — the table is the clip's `.amb`
Per frame an (x, y, z) root motion in the character's frame plus an unused rotation triple.

### Q-0404 RESOLVED (2026-10-06, E-0814) — yaw follows D3DX RotationY
Local +z moves along (sin yaw, 0, cos yaw), as the engine already turns the mesh.

### Q-0403 / Q-0202 update (2026-10-06, E-0810..E-0814) — the player walks by the mouse
Hold the left button: the character walks toward the cursor (turning 10% of the error per
tick), Shift runs, Space jumps, release stops; actor 3 is the controller. Still open:
combat (Q-0806), followers and mounts (roles 2..7).

### Q-0800 note (2026-10-06, E-0812) — floor types 0..4 are views
Actor 3's update reads the character's `+0x450`: types 0..4 select the camera view.

### Q-0805 PARTLY RESOLVED (2026-10-06, E-0817) — acos of the normalized screen y
Still open: the turn lock `+0x4dc` setter, `FUN_004219f0(-2.0)`, and where the character's
screen point `+0x158/+0x15c` is written (not in Draw `0x4226a0`; likely through a pointer
with the hover RECT `+0x148`).

### Q-0810 — Walking on platforms
- **Context:** E-0802/E-0803: `CFXFloor::Move` first tests the active 0x1a actors of its
  platform list (those with `+0x1d0` = 1, 14 records) on their frame-0 vertices, rides their
  current frame's height (floor type 15, a step limit of 80).
- **What we checked:** the Move code; not which scenes need it (bridges, rafts?).
- **Blocks:** walking onto moving meshes. The engine walks the static mesh only.
- **Status:** open

### Q-0811 — The proximity gate's bits 2 and 4
- **Context:** E-0705: bit 2 of a trigger's `+0x188` tests actor 4's character (or actor 95's)
  against `+0x14c`, bit 4 the characters of actors 91..94. Actors 4 and 91..95 (followers,
  enemies) are not modelled, so the engine's gate passes on bit 1 only.
- **Blocks:** triggers walked into by a companion or an enemy.
- **Status:** open

### Q-0812 — Who makes Grumpa the player on a new game
- **Context:** E-0816: actor 3's character is set only by character opcode 0x2c; actor 3's
  entry handling (E-0830) works on that character. Which command list sends 0x2c to
  character 10 on a new game is not located.
- **Blocks:** nothing yet: the engine's player is Grumpa (10) from the start, and sets his
  home on an entry only after the first one.
- **Status:** open

### Q-0401 RESOLVED (2026-10-06, E-1620)
The "talking flag" is the speaker character's state slot 5 (1 while one of its lines plays).
No animation, mouth or input code reads it; event conditions do (31, all on the companion
c16, `[5]==0`), so a companion hint line or trigger waits until he stops talking.

### Q-1400 — Combat leftovers: death callback and the hit-clip side effects
- **Context:** E-1403: `FUN_00425e30` runs when the death timer `+0x47c` (= N2D's F) ends;
  clip 0x17 start sets `+0x474` = 1 and zeroes `+0x11c` of `[DAT_004ba74c + 0xc]`; `+0x478`
  is 1 for the five characters whose body stays. None of these were read.
- **Blocks:** what a killed enemy leaves behind (drops, score, reactions).
- **Status:** open

### Q-0810 RESOLVED
- E-1600: the platform list is filled on scene entry (op 0x17) by flagged 0x1a actors after
  the floor clears it; Move tests pos+delta against each active platform's frame-0 faces
  (uv-index triples into the vertex buffer, all sections, the floor's face test), takes the
  current frame's y of the face's first corner as height (y = 0.4·y + 0.6·h), no x/z riding;
  the character allows +80 steps and floor type 15 on a platform.

### Q-1500 — Who sends the combat roles 0x2e/0x2f/0x30 and where a scripted mount stands
- **Context:** E-1500: these ops never occur in scene data; 0x4b does (bosses), 0x54 comes
  from `FUN_00430960`. E-1502: scene mounts (`0x2c` to 12/13/88) set no position; the form
  stands wherever its home/position put it (Characters.abi or an earlier 0x29/0x47).
- **Next lead:** callers of `FUN_0041e0d0` with constants 0x2e..0x30 (type 0x1c actors or
  global2.atx); for positions, trace scene 40 entering with Grumpa on the bear.
- **Blocks:** enemy engagement order; exact mount placement.
- **Status:** open

### Q-1420 — Combat: actor 301, the hit-reaction clip, the meaning of clips 35..37
- **Context:** E-1430..E-1433: the first engaged fighter sends DoCommand 0 to actor 301, the
  last released one DoCommand 1 (combat music or HUD, not identified). Neither hit path
  (E-1432) requests the hit clip 0x17 (`023_N2H2N`); who plays it on a Life minus (score to
  character?) is not traced. Fighters request `.anb` 35..37 (S05..S07) at 140..180 units and
  as 1/3 of close-range choices (taunt or guard, known by name only).
- **Next lead:** actor 301's class in the global `.atx`/`.abi`; the score's DoCommand 0x33 path
  to the character; the character update where clip 0x17 starts (`+0x474` = 1).
- **Status:** open

### Q-1710 — Cursor picture animation timing; kinds 3..6; the cursor's initial kind
- **Context:** E-1720/E-1721. CFXSprite steps a frame every (timer rate / `+0x1e0`) updates
  (`+0x1e0` = 50 by default, `0x44da50`) only while `+0x1d0` (playing) is 1, with loop modes
  in `+0x1e4` (`0x44dd80`); the cursor never starts its sprites explicitly. The kind after
  load is the ctor's −1 (draws nothing) until a hold/message sets it; the four ATX ints
  (`2 1 1 9`) are read but their targets were not traced. `+0x11c`'s `+0x104` gets the kind
  (1 for arrows) every update: unknown object.
- **Next lead:** `0x40a990` targets in `0x444b60` (disassembly); sprite `+0x128`/`+0x1cc`;
  raw scan for `mov [reg+0x130], 3..6` on the mouse.
- **Blocks:** nothing: show frame 0 of each picture; 9 at scene start.
- **Status:** open

### Q-0812 RESOLVED (2026-10-06, E-1530) — `global2.atx` `<22>` makes actor 3 hold Grumpa 10


### Q-1800 — Is Captain c69 meant to be fought on the first boarding of scene 102?
- **Known:** 102's walk-in trigger 660 is active in the file and starts the captain's line,
  whose end activates c69 (E-1804); the cork (109 trigger 661) later sends 660 opcode 11,
  which a latched trigger ignores. So by the data the captain is up on the first visit and the
  hold (104..109) is not strictly needed for the ending; the design reads as "go below, pull
  the cork, come back on the sinking deck".
- **Next lead:** combat (Q-0806): can Grumpa win at strength 5/16 against c69 (life 400,
  slots 2/3 = 40/18); does the original's latch really ignore 660's 11 (events.md).
- **Blocks:** the walkthrough lists the designed order; nothing in the engine.
- **Status:** open

### Q-1801 — Do the boat and the dragonfly reach scene 101 over scene 100's 8-face mesh?
- **Known:** on foot, every entry of scene 100 reaches only the exits to 58 and 82
  (`walkplan.py reach 100`), not 101; the boat (c11) and dragonfly (c12) forms dismount at 101
  (triggers 661/662). Whether mounts use the floor at all is unspecced (Q-0403).
- **Blocks:** the surface route to the ship (the walkthrough uses the underwater one).
- **Status:** open

