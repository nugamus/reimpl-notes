# The 3D world: scenes, loading, start positions, scene objects

What the engine needs to load one 3D scene of Mission Sunlight and put the viewer in it:
the scene table, what a scene is made of, where the viewer starts, how the per-scene code
plugs in, and how the program moves between scenes, the museum and the 2D zones.
Addresses are in `/MISSION.EXE`. Movement and collision are in `movement.md`, picking,
cursors and the inventory bar in `interaction.md`; each scene's own logic in
`games/mission-sunlight/docs/<scene>.md`. The file formats (`.BFG`, `.3DC`, `.3DM`, `.3DA`,
`.3DI`) are in `docs/formats/`; the renderer (projection, drawers, lighting) has its own spec.

Units: positions are integers in world units, **y points down** (floors have larger y
than the eye, E-0305). Angles are integers in 1/4096 of a turn, masked with `& 0xFFF`;
the camera's three angles are stored in the order (pitch, yaw, roll) (E-0302).

## The scene table (E-0306)

The current scene is the byte `scene` at 0x4e3144, the scene the viewer comes from
`prevScene` at 0x4e3140. Each scene has a BFG in `DATA\SCENES_3D\`, an **init** callback
run once after loading, and a **frame** callback run every tick (0x41ee1d; the addresses
below are the functions behind the incremental-link thunks).

| # | Scene | Bundle | Init | Frame | Entry movie | Return movie | Complete when zones solved |
|---:|---|---|---|---|---|---|---|
| 0 | museum | `musee` | 0x42ad92 | 0x42b776 | — | — | — |
| 1 | Auberge Ravoux | `auberge` | 0x41a0b0 | 0x41a42b | — | — | never (see below) |
| 2 | hospital, outside | `hopiext` | 0x424af7 | 0x424d93 | — | — | never |
| 3 | cottage (Nuenen) | `maisonet` | 0x4279a3 | 0x427e04 | `maisa` | `maisr` | 1 |
| 4 | potato eaters | `mangeurs` | 0x4298e5 | 0x429dd6 | `mangeurs` | `mangeurr` | 2, 3 |
| 5 | night café | `cafe` | 0x41b77d | 0x41bbcf | `cafe` | `cafer` | 4, 5, 6 |
| 6 | bedroom | `chambrev` / `chambreb` | 0x41dd7f / 0x41c979 | 0x41ded8 / 0x41d167 | `chamba` | `chambr` | 7, 8, 9, 10, 11 |
| 7 | yellow house | `maisonj` | 0x42897f | 0x428e63 | `maisonj` | `maisonjr` | 12 |
| 8 | hospital, inside | `hopiint` | 0x425541 | 0x42579a | `hopi` | `hopir` | 13, 14, 15 |
| 9 | Langlois bridge | `pont` | 0x42cfe2 | 0x42d489 | `pont` | `pontr` | 18 |
| 10 | café terrace | `terrasse` | 0x42ddbf | 0x42e023 | `terrasse` | `terr` | 16, 17 |
| 11 | garden | `jardin` | 0x426d9b | 0x427069 | `jardin` | (`jardinr`, never played) | never |
| 12 | wheat field | `champ` | 0x41e383 | 0x41e5de | `champ` | `champr` | 22, 24 |
| 13 | church at Auvers | `eglise` | 0x4242ed | 0x424467 | `eglise` | `eglr` | 23 |

- Scene 6 loads `chambreb` when the byte 0x4abd14 is set, else `chambrev` (0x41fda9); the
  callbacks follow the bundle. Arriving from the museum always loads `chambreb` with its
  callbacks (the museum's painting sets 0x4abd14 first, `musee.md`).
- The place names are ours (the bundles' names and their paintings); the program only
  knows the numbers and bundle names.
- "Zones" are the 2D puzzle screens (`Entry2D`, `ui.md`). A zone is **solved** when the
  player leaves it with more sunflowers than on entry: `zoneSolved[zone]` (u32 array at
  0x4abb0c, 25 entries, part of the 3D block) is set to 1 (0x42f2c2, E-0311).
- A scene is **complete** (0x41efc5) when all its zones in the last column are solved;
  scenes 1, 2 and 11 never are.

## What a scene is made of (E-0307)

Loading a scene (`Alloc3DMemory` 0x422869, called by 0x41fda9 with the bundle name, the
two callbacks and the start camera):

1. Clear the static-sound table (20 slots at 0x5badc0) and the extra box-set handles (10
   at 0x6511e0).
2. Allocate the 3D heap: 0x700000 bytes (7 MB), zeroed. The 3D engine's object table, the
   camera object (handle 0, name `Camera`) and the heap live in it (0x434e70). Set the
   viewport from the view size (below).
3. `C_Monde::LoadScene` 0x421e56: read the whole `<scene>.BFG` into memory (E-0013); load
   the entry `<scene>.3DC` (the scene tree, E-0014, with its `.3DM` textures); attach it
   under the camera object (0x435880: the scene root becomes a child of handle 0); set the
   word at +0xd0 of every node of the scene's handle group to 0xF (0x435930, `15 & 0x1F1F`;
   the brightness: shade row 31 - 15 = 16 for every pixel, `render.md` "Lighting", E-0508); load
   `BOX.3DI`, the scene's collision faces (E-0016), start the collision world (0x432df0)
   with one moving body, the viewer (0x432e70, flags 0xF, `movement.md`), and register
   `BOX.3DI` in it (0x432e10).
4. Build the **name table** (`CheckObjectCount` 0x4210b9, 0x420e99, 0x420fa9): every node of
   the scene tree, depth first (node, then its first child's subtree, then its next
   sibling's), as `{char name[0x34]; i32 handle}` records at 0x5b81e0, count at 0x5b7f7c.
   More than 200 nodes shows "NbObjets > MAX_OBJETS_SCENE" (and goes on). Scene code finds
   objects by name through this table (0x41edc9: first `strcmp` match, -1 if none).
5. Clear both keyboard buffers; load the cursors and the inventory bar (0x426594,
   `interaction.md`); set the camera (0x421c98, below); put the viewer body at the start
   position and set its radius to 250 (0x432f10, 0x432f30).
6. Mark the 3D as running (0x4e4580 = 1), clear the mouse buttons, run the scene's **init**
   callback.
7. Free the BFG file image (every entry the scene needs is now unpacked in the 3D heap; the
   init callback loads its extra entries before this point).
8. On a 15-bit (RGB555) display convert the loaded textures' shade tables (0x439a10).

Unloading (0x422aa6): unregister `BOX.3DI` and the extra box sets, close the collision
world, free the static sounds, the 3D heap, the cursors and the bar image (0x426872), stop
the sound stream; 0x4e4580 = 0.

What the init callbacks add (every scene the same way, per-scene lists in the flow docs):

- **Object table**: per scene a static array in `.data` (0x3C or 0x40 bytes per entry;
  jardin 0x14) of `{char name[..]; ... u8 cursorType at +0x32; i32 handle; i32 startHidden}`.
  Init resolves each name to a handle (0x41edc9) and hides the ones with `startHidden` = 1.
  The table is what the frame callback compares picks against (`interaction.md`).
- **Animations** (`LoadAnims<scene>`): per scene a static array of 0x78-byte records
  (0x34 in jardin) `{char anim[0x32]; char node[0x32]; i32 animHandle; i32 nodeHandle;
  i32 length; i32 frame; i32 playing}` (musee: anim at +0, node name at +0x32, handles at
  +0x64/+0x68, length +0x6c, frame +0x70, playing +0x74). Each `<name>.3da` is loaded from
  the bundle (missing: "LoadAnims<scene>::%s manque"), `length` is the first word of its
  data (0x437d90), the node is found by name. A playing record advances `frame` by the
  elapsed ticks each frame and poses the node (0x438290 with `animHandle + frame` as both
  keys, blend 0); what happens at the end (stop, loop, flag) is per scene (E-0318). The
  step functions share one shape (E-0368): `frame += step`; the end is `frame >= length`
  (some records use `length / 2`); a record with its own end rule applies it and returns
  **without posing**, so the node keeps the previous tick's frame; any other record
  wraps to frame 1 and is posed there in the same tick (a loop never shows `length`). A
  scene init that shows a finished track poses "its last frame", which is always frame
  `length - 1` (E-0373).
- **Static tables** (E-0370): the object table, the animation records and the scene code's
  own variables are initialised data of the EXE, set once per run. A load resolves the
  handles and resets the frames to 1 (`LoadAnims<scene>`), and the init sets what it sets;
  everything else keeps the value the last visit left: an object's changed cursor type
  (0xFF once used), a track's playing flag, a scene's timers and flags outside the saved
  block. None of it is saved, so a restart of the program starts them afresh.
- **Extra box sets** (`LoadBox<Scene>`): more `.3DI` entries (`BOX1.3DI`..`BOX4.3DI`,
  `BOXBAS`/`BOXHAUT`) loaded into the handles at 0x6511e0.., swapped in and out of the
  collision world by a per-scene helper keeping the current one in 0x4e312c
  (unregister the current, register the new: 0x432e40 / 0x432e10, E-0319).
- **Static sounds**: `Snd_CreateStatic` into the slots at 0x5badc0, count at 0x650f80; one
  of them is the ambience (0x50286c), started looping (0x416e24(sound, 1)) (E-0320).
- **Textures**: `0x4395d0(name, file)` loads `<file>.3DM` from the bundle as texture `name`;
  `0x435dc0(object, from, to)` retextures every face group of `object` using texture
  `from` to `to` (E-0319).
- **Visibility**: `0x435970(h)` sets bit 0 of the node flags (+0xc), which the renderer and
  the pick pass skip (E-0014); `0x4359a0(h)` clears it (E-0319).

## Camera and view (E-0307, E-0300)

- The camera is object handle 0. `0x422f30(x, y, z, pitch, yaw, roll)` sets its position
  (0x436160) and its rotation matrix from the three angles (0x43a780, `movement.md`), and
  copies all six into the viewer state (position s16 at 0x651352/54/56, angles s16 at
  0x651346/48/4a). The scene start calls it through 0x421c98 (which first resets the
  camera's matrix to identity).
- View size (`viewSize`, byte 0x4aba3c, the player's option; 0x4183c4): viewport rectangles
  (0x421d73, 0x435170):

| viewSize | Viewport | At |
|---:|---|---|
| 0 | 640 × 480 | 0, 0 |
| 1 | 512 × 384 | 64, 48 |
| 2 | 400 × 300 | 120, 90 |
| 3 | 320 × 240 | 160, 120 |

  Around a smaller viewport the frame is filled with 0x114A (RGB565) or 0x08AA (RGB555)
  every frame before drawing (0x4223e8). The fifth argument of 0x435170 is 480, scaled by
  width / 640 (0x6af5fc); the aspect factor is `(h · 4) / (w · 3)`. The scene load then
  sets the renderer's near clip (0x6af5bc) to 64 and 0x6af6c4 to 80,000 (0x4353c0,
  0x4353d0); returning from the option menu calls only 0x435170, which leaves them at 128
  and 65,000 (0x42f515). The meaning of these for projection is the renderer spec's.

## Start positions (E-0308)

0x41fda9 picks the bundle and the start camera (x, y, z, pitch, yaw, roll) for `scene`,
given `prevScene`. Three cases:

**A. Entering from the museum, or reloading** (`prevScene` = 0, or `scene` = 0, or both
equal): the scene's own start, or for the museum the spot in front of the painting of
`prevScene`:

| Scene | x | y | z | pitch | yaw | roll |
|---|---:|---:|---:|---:|---:|---:|
| 1 auberge | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 maisonet | 1149 | 141 | -1491 | 0 | 275 | 0 |
| 4 mangeurs | -106 | 6 | 100 | 3946 | 145 | 0 |
| 5 cafe | 393 | -175 | -136 | 3976 | 92 | 0 |
| 6 chambreb | -628 | -336 | -268 | 3946 | 150 | 0 |
| 7 maisonj | -3350 | 489 | -5996 | 60 | 3944 | 0 |
| 8 hopiint | -67 | -78 | -345 | 4036 | 17 | 0 |
| 9 pont | 7805 | 1167 | 2183 | 30 | 3265 | 0 |
| 10 terrasse | -123 | -102 | -846 | 4066 | 31 | 0 |
| 11 jardin | -46 | -335 | 1263 | 0 | 4052 | 0 |
| 12 champ | 2140 | 253 | 2270 | 4006 | 214 | 0 |
| 13 eglise | -7189 | 802 | 102 | 210 | 3756 | 0 |

Scene 2 (hopiext) has no row: it is only entered from other scenes (case B).

Museum (scene 0), by `prevScene` (the same spots are the targets of the flight to a
painting, 0x41f506):

| prevScene | x | y | z | pitch | yaw |
|---|---:|---:|---:|---:|---:|
| 0 (game start, reload) | -39 | -209 | 361 | 4066 | 20 |
| 1, 11 | 3230 | -297 | 5166 | 4036 | 3073 |
| 2, 8 | 538 | -297 | 8256 | 4036 | 290 |
| 3 | -3125 | -297 | 5252 | 4066 | 1008 |
| 4 | -4849 | -297 | 5195 | 4036 | 3101 |
| 5 | -562 | -296 | 6923 | 4036 | 2355 |
| 6 | -909 | -297 | 7462 | 4066 | 3062 |
| 7 | -466 | -297 | 8184 | 4066 | 3788 |
| 9 | 703 | -297 | 6902 | 4036 | 1782 |
| 10 | 933 | -297 | 7535 | 0 | 988 |
| 12 | 4403 | -297 | 5867 | 4006 | 339 |
| 13 | 4524 | -297 | 4758 | 4006 | 1791 |

(roll 0 everywhere.) After the end of the game (0x4aba5c = 1) the museum is loaded at
(1232, -208, 4207), pitch 0, yaw 3410 regardless.

**B. Walking from one scene to another** (`prevScene` ≠ `scene`, neither 0): the start is
the doorway on the new side, for these pairs only (0x41fda9). Another pair would load the
target's bundle and callbacks (0x41ee1d runs first) with an uninitialised camera; no scene
code asks for one (the 7 → 2 row is itself never requested, Q-0237):

| From → to | x | y | z | pitch | yaw |
|---|---:|---:|---:|---:|---:|
| 1 → 11 | -6620 | 182 | -578 | 4066 | 1128 |
| 2 → 8 | -1318 | -11 | 8435 | 4036 | 1476 |
| 2 → 9 | 4933 | -22 | 13060 | 0 | 2581 |
| 2 → 7 | 3320 | 358 | 12464 | 0 | 2264 |
| 3 → 4 | -384 | 35 | 1373 | 3946 | 1701 |
| 4 → 3 | 7310 | 183 | 5921 | 0 | 2873 |
| 5 → 10 | -430 | 63 | 3711 | 4066 | 1519 |
| 6 → 7 | -6199 | 358 | 737 | 0 | 1657 |
| 7 → 6 | 100 | -336 | 439 | 3946 | 3446 |
| 7 → 9 | 11579 | -56 | -2069 | 30 | 3253 |
| 7 → 2 | 17495 | 6733 | 14500 | 4036 | 2018 |
| 7 → 10 | 677 | -63 | -2216 | 4066 | 68 |
| 8 → 2 | 9533 | 6735 | 11297 | 4066 | 1727 |
| 9 → 7 | -831 | 489 | -9000 | 4066 | 72 |
| 9 → 2 | 17028 | 6815 | -389 | 4036 | 4086 |
| 10 → 7 | -7605 | 358 | -1698 | 0 | 1054 |
| 10 → 5 | 1617 | -90 | -116 | 3976 | 3788 |
| 11 → 12 | 2425 | 160 | -4360 | 4006 | 3989 |
| 11 → 13 | -19321 | 841 | 23485 | 0 | 1651 |
| 11 → 1 | 0 | 0 | 0 | 0 | 0 |
| 12 → 13 | -2500 | -634 | 384 | 60 | 3279 |
| 12 → 11 | -8760 | 228 | -928 | 3946 | 973 |
| 13 → 12 | -13857 | -522 | 9973 | 4006 | 1241 |
| 13 → 11 | 6743 | 235 | -1283 | 4006 | 3036 |

(roll 0 everywhere.) 7 → 6 loads `chambreb` or `chambrev` by 0x4abd14.

**C. Back from a 2D zone, the option menu or a loaded game** (the previous mode differs
from the current one, 0x502740 ≠ 0x598cb0): the position and yaw/roll saved when the 3D
was left (0x5b7f80.., 0x5b7fb4..; they are the 3D block's +0x30 and +0x24, `save.md`), with
**pitch 0**, and the callbacks already set.

The floor snap (`movement.md`) moves the eye to 700 above the floor on the first frame, so
the stored y only has to be above the right floor.

## Moving between the museum and the scenes (E-0309, E-0310)

- **Museum → scene**: clicking a painting (`musee.md`) sets `prevScene` = 0, `scene` = the
  target, and 0x41f506 starts **mode 4**: the camera flies in 20 steps to the painting's
  spot (table above): per step `(target - current) / 20` (C division) for position and
  angles, where a zero difference is first replaced by 1 (so it divides to 0), and an angle
  difference below -0x800 gets +0x1000, above 0x800 -0x1000 (E-0371). Each tick (0x41f9f8)
  adds one step and redraws without input, then, while the step counter is below 21, grows
  it by 1 (by `elapsed / 2` when 3 or more ticks elapsed) and goes on; the call that finds
  it at 21 or more has still added its step (22 steps at one per tick, so the flight
  overshoots the spot by two steps), and ends the flight: 0x41faf9 stops the
  stream and the static sounds and, if the target scene is not complete, plays
  `MOVIES\<entry movie>.hnm` (mode 2); when the movie ends the scene is loaded (the mode-2
  branch of 0x42fbd6 calls 0x41fda9 and restarts the timer). A complete scene (or 1, 2) is
  loaded at once, without the movie (0x4e313c = 1: the next tick unloads and loads).
- **Scene → museum**: Backspace (released) or a click on the return icon (`interaction.md`)
  in any scene but the museum redraws the frame with the hourglass (0x4221f6), sets
  `prevScene` = `scene`, `scene` = 0, requests the reload (0x4e313c = 1) and runs 0x41f14b:
  if the scene just left is complete, the static sounds are freed, its return movie plays
  (mode 2), and the u32 at 0x4abb70 + 4 × (last zone number) is set to 1; the museum then
  loads when the movie ends. Otherwise the next tick unloads and loads the museum (0x42f988).
- **Scene → scene**: the scene code sets `prevScene` = its own number, `scene` = the target
  and 0x4e313c = 1 (flow docs). The next tick (0x42f988) unloads and loads.
- Every load goes through 0x41fda9 and `Alloc3DMemory`; nothing survives in the 3D heap.
  What persists is the 3D block (0x4aba40, 0x36C bytes, `save.md`): `zoneSolved`, the
  inventory flags, the sunflower count (byte 0x4abbd4), and each scene's own flags. The
  scenes' static tables and variables persist too, for the run (E-0370).

## 3D ↔ 2D (E-0311, E-0312)

- **Into a zone**: scene code sets the zone number (byte 0x502860), 0x502740 = 0 and mode
  (0x598cb0) = 1. The frame ends with the hourglass redraw (0x4221f6), which sets 0x4b0058;
  the window procedure, now in mode 1 with 0x4b0058 set, calls 0x42f755: copy the camera
  (position, angles) and `scene`, `prevScene`, zone into the 3D block (+0x30, +0x24, +0x3C,
  +0x3D, +0x3E), the 35 inventory flags into +0x40, unload the scene, stop the 3D timer and
  call `Entry2D(window, zone, inventory, block, 0x36C)`. The 2D side is `ui.md`.
- **Back from a zone** (0x42f2c2, called by the 2D shell at 0x412e76 with the inventory,
  the sunflower count and an action): clear the keyboard buffers, take the inventory and the
  count; if the count is higher than when the zone was entered (0x598fe0), the zone is
  solved (`zoneSolved[zone]` = 1). Action -1: reload the scene at the saved spot (case C);
  -2: quit; -3: start over from the museum (`prevScene` = `scene`, then `scene` = 0 and a
  reload); n ≥ 0: load save n (`Load3DGame`, `save.md`). Special zones: leaving zone 0 sets
  the block's +0x08/+0x0C; zone 21 (the ending) sets 0x4aba5c and plays `cinefin` (then
  `cinefin2` and the credits, `boot.md`); zone 11 sets 0x4abd4c (and 0x4e30f4 when 0x4abd5c
  is 0); zone 7 sets 0x4abd54/0x4abd58; zone 8 sets 0x4abd50. The 3D timer restarts unless
  a movie plays.
- **Option menu**: Escape (released) in 3D (0x42edef) saves the camera and state into the
  block like 0x42f755, redraws with the hourglass, switches to mode 3 and opens the option
  menu (0x40fccb). Closing it calls 0x42f515 (from 0x4124bc) with -2 (quit), -1 (resume) or
  a save slot: re-apply the view size (viewport table), restore the static sounds' volume,
  restart the 3D timer.
- **Autosave**: closing the inventory bar writes the resume file (0x42f873: the 3D block
  with the camera, scene, previous scene and inventory, `Save_WriteGGame`, `save.md`). Unlike
  0x42f755 and Escape it does not store the pitch: +0x24 keeps its last value (E-0019).
