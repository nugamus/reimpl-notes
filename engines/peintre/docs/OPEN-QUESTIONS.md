# Open questions (Peintre engine, Mission Sunlight)

Things we could not determine after checking the original code (Ghidra), the corpus and
traces. An unresolved field goes here and stays opaque (`unk_*`) in the format spec. It does
not get a guessed meaning.

Append only. When a question is answered, keep the entry, mark it `RESOLVED`, and link the
`EVIDENCE.md` entry that resolved it.

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

### Q-0001 — Does any other title share the PEINTRE 3D code?
- **Context:** E-0008 names the engine `peintre` after the program. Cryo and index+
  published other 3D titles in 1998–2000; if one of them runs the same code (same
  `.BFG/.3DC/.3DM` formats, `C_Monde`), the engine may need a broader name.
- **What we checked:** only this CD is in the corpus. X3D (Monet, 2000) is a different
  engine by 4X Technologies with Direct3D (engines/x3d), not this software renderer.
- **Blocks:** nothing now; a rename before upstreaming if a second game turns up.
- **Status:** open

### Q-0002 — What is the assembly at 0x455470–0x465bcf, and how is it entered?
- **Context:** E-0012. No function starts there after Ghidra's analysis.
- **What we checked:** raw disassembly of a few addresses only.
- **Blocks:** the rasteriser spec (texture mapping, shading) if it lives there.
- **Status:** open RESOLVED (see E-0511)

### Q-0003 — How do the drawers address texels of the four odd-sized textures?
- **Context:** E-0015: jardin `salon.3DM` has 512 texel bytes more than 256x256, musee
  `plafond.3DM`, `plafond2.3DM`, `plafond3.3DM` 256 fewer.
- **What we checked:** sizes only. The drawers (0x43c780, 0x444e20, …) are not read yet.
- **Blocks:** nothing if texel addressing is masked to 256x256 (the engine can pad or
  crop); the last row of the three short ones then reads the next heap object.
- **Status:** open RESOLVED (see E-0509)

### Q-0004 — .3DA: component order of rotation keys, meaning of track word 0 and key time units
- **Context:** E-0016.
- **What we checked:** data only (unit-length keys, times 0..30, word 0 = 30 in portev).
- **Blocks:** animation playback spec.
- **Status:** open RESOLVED (see E-0514)

### Q-0100 — What do the constant fields of the TGP "LZWCRYO" header mean?
- **Context:** `.TGP` single body (E-0100): `u32 0x24` at 8, two zero u32 at 0x14, `256`
  at 0x1C, `1` at 0x20, unpacked size at 0x24. `Tgp_Load2` (0x414779) reads them and
  uses only the packed size at 0x28.
- **What we checked:** the loader; all 110 files (the values never vary).
- **Observed range:** 0x24, 0, 0, 256, 1, 614400 in every file.
- **Blocks:** nothing (the engine ignores them); they stay `unk_*` in `tgp.ksy`.
- **Status:** open

### Q-0150 — What does the CVY mask colour (0x116A / 0x08AA) do after it is painted over a movie?
- **Context:** E-0205. Blit_CvyMask paints parts of the movie rectangle in one dark blue
  on the back buffer (0x6516a8) every frame.
- **What we checked:** the constants occur only at the four mask calls; no other code
  compares pixels with them (byte search of `.text`). Whether the colour is simply the
  interface background (masking the video to a non-rectangular window) or a key for a
  later pass (sprites, 3D) is not established.
- **Blocks:** nothing for decoding; the engine can paint the same colour. A capture of
  one masked movie (e.g. `A01_032A`) would settle what shows there.
- **Status:** open

### Q-0151 — Which movie does A13_052B.CVY belong to: A13_052B.HNM (94 frames) or the extensionless A13_052B (101)?
- **Context:** E-0204. The CVY has 101 masks; table entry `A13_052b` has has_cvy = 1 and
  the EXE opens `A13_052B.HNM` (94 frames), so masks 0..93 are used.
- **What we checked:** frame counts; the EXE never opens a file without `.HNM`.
- **Blocks:** whether masks line up with the 94-frame movie (a capture or a decoded frame
  comparison would show it).
- **Status:** open

### Q-0220 — chambreb: what starts the mirror track and the shoe track, and what are DAT_004abd60 / DAT_004abd70?
- **Context:** E-0332. `mirroir.3da` (on `mirroircas`) is only ever posed at its end or
  stopped by the 3D code; `chaussur.3da` has playing = 1 in .data and the entry clears it
  whenever the shoes are in the room. `DAT_004abd60` is set to 1 at entry when it and
  `DAT_004abd70` are 0 and `DAT_004abd14` = 1; nothing in the 3D code reads it.
- **What we checked:** every decompiled function of 0x419e50..0x42fbd6 (grep for the
  addresses). The 2D side receives the whole state block by pointer (E-0312) and may
  write these words by offset.
- **Blocks:** nothing in the 3D flow; possibly a mirror-breaking animation seen after
  zone 11.
- **Status:** open (0x4abd60 settled by E-0369: initial 1, written only; the mirror and shoe tracks remain)

### Q-0235 — Who sets DAT_004abc08 (mangeurs' cuckoo on entry)?
- **Context:** mangeurs' init `0x4298e5` sets `DAT_00599044` := (`DAT_004abc08` = 0); the
  frame plays `coucou` and clears `DAT_004abc08` when it was non-zero (E-0364).
- **What we checked:** all decompiled game3d functions; no other write. It lies in the saved
  block `0x4aba40` passed to the 2D side (E-0312), so a 2D zone may set it.
- **Blocks:** when the cuckoo sounds.
- **Status:** RESOLVED (E-0369): its initial value is 1; only mangeurs clears it

### Q-0236 — Are the never-started 3D tracks started elsewhere?
- **Context:** loaded tracks whose playing word no decompiled 3D function sets to 1:
  jardin `papiyon3.3da` (`0x4ad228`), maisonj `nuages.3da` (`0x4adba4`), mangeurs
  `buche.3da`, `chaise.3da`, `fagot.3da` (`0x4ae3ac`, `0x4ae424`, `0x4ae49c`) (E-0361,
  E-0363, E-0364).
- **What we checked:** the decompiled game3d functions (0x419f0e-0x42fbd5).
- **Blocks:** nothing for playback (they stay at their loaded pose); mangeurs' track ends
  hide the log/faggot and scroll `fire`, which would matter if they ran.
- **Status:** open

### Q-0237 — What leaves maisonj for hopiext (7 → 2)?
- **Context:** `0x41fda9` has an arrival for previous scene 7, target 2 (E-0308), but
  maisonj's frame `0x428e63` never sets `DAT_004e3144` := 2 (E-0363).
- **What we checked:** every write of `DAT_004e3144` in the decompiled 3D functions of batch B.
- **Blocks:** nothing; a missing exit would only drop an unused arrival.
- **Status:** open

### Q-0250 — Can the 3D side call Entry2D with zone 25?
- **Context:** Entry2D 0x40fdc6 rejects only zones > 0x19, but the zone table 0x4a6b18 has 25
  rows (0..24); row 25 would read the start of the object table (E-0408).
- **What we checked:** the 2D side only; the values the 3D side stores in 0x502860 are the
  world spec's.
- **Blocks:** nothing if no scene passes 25; an engine can reject it.
- **Status:** open

### Q-0251 — What does leaving a zone with -3 (RetourM) do on the 3D side?
- **Context:** 0x42f2c2 with -3 sets 0x50273c = 0, then 0x4e3144 (3D block +0x3C) = 0 and
  runs 0x41fda9 (E-0414); the 2D side calls the button "RetourM".
- **What we checked:** 0x42f2c2 only.
- **Blocks:** `ui.md` describes the effect by variables, not in game terms; world spec.
- **Status:** RESOLVED (E-0372): the museum, after the return movie of a complete scene

### Q-0252 — The rest of the 0x36C-byte 3D state block in the saves
- **Context:** `game.ksy` `state_3d`; E-0422 names only the fields the save glue touches.
- **What we checked:** 0x42f755, 0x42f873, 0x42edef, 0x42f2c2, Load3DGame, Load3DGGame.
- **Blocks:** nothing for loading and writing (the block is copied whole); naming the
  fields belongs to the world spec.
- **Status:** open

### Q-0200 — Does anything start the museum robot's third track (`robot03`)?
- **Context:** `musee.md` / E-0321: record 3 (`robot03.3da` on `robot`, playing flag
  0x4aef4c) hides the robot at its end, but no code sets 0x4aef4c to 1.
- **What we checked:** every reference to 0x4aef4c in `.text` (three: two writes of 0, one
  read); the museum's init and frame callbacks.
- **Blocks:** nothing: the engine can load the track and never play it, like the original.
  It matters only if a cut robot exit is to be restored.
- **Status:** open

### Q-0300 — Node +0xac, +0xc0, +0xd4, +0xd8: what are they?
- **Context:** `.3DC` node, `obj3d.ksy` (E-0504).
- **What we checked:** the renderer's per-node code (0x44fec0 and everything it calls, the
  pick hook 0x43a150) reads none of them; the corpus.
- **Observed range:** +0xac, +0xd4, +0xd8 = 0 and +0xc0 = 40 in all 560 nodes.
- **Blocks:** nothing for drawing; they stay `unk` in the ksy.
- **Status:** open

### Q-0301 — Face group +0x28, +0x30 and the material's second colour word and last 8 bytes
- **Context:** `.3DC` face group (+0x24 is the runtime draw list, E-0505) and material
  record (the first `unk_colour` word is the type-1 flat colour, E-0507).
- **What we checked:** the edge builders, the poly cull and the loader's binding (0x4338d0,
  0x434560); the corpus.
- **Observed range:** group +0x24 = 0 in all 1,235 groups; +0x28 = 0 in 1,041, small
  integers in the rest (1: 76, 3: 50, …); +0x30 non-zero in all, large varying values;
  material word 2 = 0x3DEF on the 15 DEFAULT materials, else 0; the last 8 bytes zero.
- **Blocks:** nothing for drawing.
- **Status:** open

### Q-0350 — What do the zones' onAbort functions do, and does Backspace latch until a puzzle step tests it?
- **Context:** `ui.md` "Running a slot": Backspace during a run calls the zone's `onAbort`
  (0x40d1ef, 0x402376, 0x402ac2, 0x4034f2, 0x403ea1, 0x404217, 0x404b5f, 0x4056ac,
  0x405f5b, 0x4076b2, 0x407dd1) and "puzzles then end on their next step with result 0";
  the puzzle docs say "Backspace ends the slot" only in some steps.
- **What we checked:** the specs only; the engine latches a flag set by Backspace and tests
  it in the steps the puzzle docs name, so a Backspace during a movie or voice step ends
  the puzzle at the next waiting step.
- **Blocks:** whether Backspace pressed outside those steps is kept or lost; what else
  onAbort stops (voices, sounds, the movie).
- **Status:** RESOLVED (E-0444): onAbort latches a flag (per object in some zones), cleared by onPlace, tested only in the named steps

### Q-0351 — At what tick rate do Retour, CapsOP and POT animate?
- **Context:** `ui.md` gives CapsAO (even ticks), CapsAC (odd ticks) and the magnifier (even
  ticks), not `Retour` (looping), `CapsOP` (state 10) or `POT` (state 0x1C).
- **What we checked:** the spec; the engine advances the three on odd ticks ("most sprite
  animations").
- **Blocks:** exact animation speed of those three.
- **Status:** RESOLVED (E-0440): CapsOP every tick, POT odd ticks, Retour odd ticks only while hovered in idle

### Q-0352 — After an object flies back to the bar (states 0x10..0x12), who closes the bar?
- **Context:** `ui.md` state 0xF opens the bar for the fly-back; state 0x12 waits "when the
  bar is closed" before redrawing the magnifier and the Retour buttons. Nothing in the spec
  closes it in between.
- **What we checked:** the spec; the engine goes to idle (5) with the bar open when it is
  open and still, and reopens the magnifier only when the bar is closed.
- **Blocks:** whether the bar closes by itself after the fly-back.
- **Status:** RESOLVED (E-0441): the bar closes at the end of the flight; 0x12 then reopens the magnifier and Retour

### Q-0353 — The sunflower drag: the grab offsets, the drop test and the snap-back picture
- **Context:** `ui.md` "The sunflower" and `a14.md` zone 0: `TOURN` "follows the cursor
  (grab offsets (122, 344), (132, 295), (166, 333))"; the drop is tested against the pot
  area (590, 400, 45, 80); a missed drop "snaps back".
- **What we checked:** the spec and the sprites: TOURN0..2 are RLE (centred) frames and each
  offset lies just below its sunflower rect, so the engine takes the offset as the resting
  centre and moves it with the cursor; it tests the cursor (not the sprite) against the
  pot area; after a miss it shows `PA..a`'s last frame again. `TOURN`, `tourneso`, `POT`
  and `vase` in step 2 are taken as loads, played later.
- **Blocks:** the exact look of the drag and of a miss.
- **Status:** RESOLVED (E-0442): offsets are TOURN's resting centre; the drop tests the sprite's point; a miss shows PA..a's last frame

### Q-0354 — Option menu buttons: press or release, and where frames 1..3 go
- **Context:** `ui.md` "Option menu": "`options` frame b drawn at its position while
  pressed". Frames 1..3 are the whole 267×85 Options panel with one row lit, not the
  128×19 rows of buttons 1..3.
- **What we checked:** a template match of `OPTIONS.SPR` on `GFX/OPTION.TGP`: frames 0, 4, 5
  sit at their rect's top-left, frames 1..3 at (187, 154). The engine draws them there and
  acts when the button is released over it.
- **Blocks:** the draw position (to confirm in 0x40e976) and when a button acts.
- **Status:** RESOLVED (E-0443): frames at 0x4a6620 ((187, 154) for 1..3); a pressed button acts on the release anywhere

### Q-0355 — Load page order without file times
- **Context:** `Save_ListGames` (0x40e78a) sorts slots 1..34 by last-write time, oldest
  first (E-0419). ScummVM's save-file manager has no file times.
- **What we checked:** nothing more; the engine lists the saves in slot order (roughly the
  order objects are placed).
- **Blocks:** matching the original's order when objects are replayed out of order.
- **Status:** open (engine side only: the original order is file time, E-0419; ScummVM saves carry none)

### Q-0356 — Does zone 0's state 0 draw the slots?
- **Context:** `ui.md` state 0: "zone 0: magnifier open, load the bar, `LoupeIn`, open the
  bar; others: draw slots, magnifier, Retour buttons". Zone 0 has object 0's slot, which
  the player drops the object on.
- **What we checked:** the spec; the engine draws the slots in both cases.
- **Blocks:** nothing visible if the background already shows the empty slot.
- **Status:** RESOLVED (E-0440): state 0 draws the slots and the open magnifier in every zone

### Q-0357 — Does a click skip one credits picture or all of them?
- **Context:** `ui.md` "Option menu" Credits: "each for 250 ticks or until a click or
  Space"; E-0418 (end credits, 0x409645): "a click or Space → end".
- **What we checked:** the specs; the engine skips one picture per click in the option menu
  and ends the end credits on a click.
- **Blocks:** skipping behaviour of both.
- **Status:** RESOLVED (E-0443): one picture per click in the menu; the end credits end on a click

### Q-0358 — The fly-back: when `cf_clic3` plays and where a scrolled-off slot flies to
- **Context:** `ui.md` "Result": the `OP` frame flies to "the bar slot" of its old list
  index over 32 ticks, "(sound `cf_clic3`)".
- **What we checked:** the spec; the engine plays `cf_clic3` when the flight starts and
  clamps the target to the visible bar slots 0..5.
- **Blocks:** the sound's timing and the target when the old index is scrolled off.
- **Status:** RESOLVED (E-0441): cf_clic3 at the start of the flight, the list scrolled so the index is visible

### Q-0400 — When does a scene track end, and which frame is "its last frame"?
- **Context:** the flow docs' animation tables ("stops at its end", "holds the last frame",
  "pose track n at its last frame", auberge's "length / 2"); scene.md "What a scene is made
  of" gives only `length` = the track's first word and `frame` += elapsed.
- **What we checked:** the flow docs and E-0318; the end tests of the per-scene anim steps
  (0x42b5fe, 0x41a2ab, …) are not written into the specs.
- **Blocks:** nothing visible: the `peintre` engine ends a track when `frame >= end` (end =
  length, or length / 2), holds `frame` at `end`, and poses "the last frame" at `length`.
  An off-by-one would show as a one-frame difference in the final pose.
- **Status:** RESOLVED (E-0368): ends at frame >= length; a special end returns unposed, a loop poses frame 1

### Q-0401 — The museum robot's screen scroll: which node, which way first?
- **Context:** `musee.md` "Speaking" (the screen scrolls every 10 ticks, 0x4399d0 with
  0x42ad1c) and E-0319 (0x42ad1c adds ±0x7f0000 to UV word 1, six steps each way).
- **What we checked:** the specs only.
- **Blocks:** the engine scrolls `ecran` (the node it retextures `ROBI3` ↔ `ROBI3N`), six
  steps of +0x7f0000 then six of −0x7f0000, counting 10 elapsed ticks per step. The node,
  the first direction and the step counter's start are to be confirmed.
- **Status:** open

### Q-0402 — Alternating tracks: does the second track restart from frame 1?
- **Context:** maisonet's bird (`oisaller` → `oisrturn` → `oisaller` …) and jardin's
  butterfly (`papiyon1` → `papiyon2` → `papiyon1`). The docs say the first track restarts
  "from frame 1" but not where the second one starts the next time; if its frame stayed at
  its end it would end again at once and the loop would lose it.
- **What we checked:** `maisonet.md`, `jardin.md`, E-0361, E-0362.
- **Blocks:** the engine resets the second track's frame to 1 when it ends, so the
  alternation shows both tracks every round.
- **Status:** RESOLVED (E-0368): each end sets both tracks' frames to 1

### Q-0403 — The café mirror: what does 0x650fe0 hold before the first swap?
- **Context:** `cafe.md` "The mirror": each frame the texture is swapped "from the current
  one (name kept in 0x650fe0)" to the one for the camera's z.
- **What we checked:** `cafe.md`, E-0331.
- **Blocks:** the engine starts from the texture name of `mirroir`'s first face group as
  loaded from the `.3DC`; a different initial name would leave the first swap without effect.
- **Status:** RESOLVED (E-0374): "MIRROIRG", the node's own texture

### Q-0404 — The museum star after it has been taken: hidden on the next visit?
- **Context:** `musee.md` Init lists no step that hides `etoile` when 0x4aba44 (the star
  taken) is set, and 0x4aeb24 (the star's track may pass frame 52) is not in the saved block.
- **What we checked:** `musee.md`, E-0321.
- **Blocks:** the engine follows the doc: `etoile` is visible and clickable again on every
  museum load, and 0x4aeb24 starts at 0 on each load. If the original hides it (through its
  track or elsewhere) the star can be taken twice here.
- **Status:** RESOLVED (E-0368): nothing hides it; untracked, it rests inside the stand

### Q-0405 — Carrying with a level-triggered click: does a long click drop the object at once?
- **Context:** interaction.md "Mouse": `click` is the button's level each tick. cafe,
  mangeurs and pont pick a node up on a click and drop it on the next click.
- **What we checked:** interaction.md, `cafe.md`, `mangeurs.md`, `pont.md`.
- **Blocks:** in the engine a click held over two 66 ms ticks picks the object up and puts
  it back on the second tick. Whether the original guards the carry (or reads the button
  less often) decides whether the engine needs an edge there.
- **Status:** RESOLVED (E-0018): the original has no guard either; a click that spans two
  frames drops the object again. The engine keeps the level behaviour (parity).

### Q-0406 — Who clears 0x4e3120 (back from the option menu) and 0x4e30f4 (back from zone 11)?
- **Context:** `musee.md` "Back from the option menu" reads 0x4e3120 (set by 0x42f515);
  `chambreb.md` Entry step 12 reads 0x4e30f4 (set by 0x42f2c2 for zone 11 while 0x4abd5c = 0).
  Neither doc says when the flag goes back to 0.
- **What we checked:** `musee.md`, `chambreb.md`, scene.md, E-0321, E-0332.
- **Blocks:** the engine clears each flag where it is used (the museum frame, the bedroom
  entry). If the original never clears 0x4e3120, the museum would reset the robot's
  speech on every frame after the first option menu; if it is cleared elsewhere (e.g. when
  the menu is opened outside the museum), a flag left over from another scene would not
  reach the museum.
- **Status:** RESOLVED (see E-0017)

### Q-0359 — Are the slots redrawn where a puzzle step names only a background?
- **Context:** `a03.md` zone 4, object 6, steps 3 and 4 ("voice `A03_012c`, background
  `a03_012a`, back to 2"; "Background and looping sprite `A03_012<e + h>`") say
  "background" without "the slots", unlike the other steps.
- **What we checked:** the spec; the engine follows it literally, so the object slots on the
  left are blank from those steps until the run ends (seen in a click run).
- **Blocks:** whether the slots stay visible during the moving-target step.
- **Status:** RESOLVED (E-0440): the slots are drawn
