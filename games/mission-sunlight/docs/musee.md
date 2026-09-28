# musee — the museum (scene 0)

Scene index 0 (`musee.BFG`, E-0306), the hub. Callbacks: init `0x42ad92`, per frame
`0x42b776` (E-0321). The player walks the museum's galleries; each painting on the wall is
a door into a 3D scene; a robot guide talks; the first 2D zone (zone 0) is played from
here. Generic mechanics (loading, start positions, the flight to a painting, hover
cursors, inventory bar, animations, box sets) are in `engines/peintre/docs/spec/`; this
file lists what the museum's own code does.

## Arrival (E-0308)

The start spot depends on the scene the player comes from (`scene.md` "Start positions",
case A, museum table): the entrance (-39, -209, 361) at the game's start or on a reload,
otherwise in front of the painting of the scene just left. After the end of the game
(0x4aba5c = 1) the start is (1232, -208, 4207), yaw 3410.

## Scene data (E-0321)

Object table at `0x4ae7e8`, 22 entries of 0x40 bytes (count at `0x4ae7e0`): name at +0,
cursor type at +0x32, bytes +0x33 = 0xFF and +0x34 = 0xFE in every entry (never read,
`unk`), handle at +0x38, start-hidden at +0x3c.

| # | Object | Cursor type | Hidden | Role |
|---:|---|---|---|---|
| 0 | `m01_02` | 4 (finger) | | painting → maisonet (3), act 1 |
| 1 | `m01_03` | 4 | | painting → mangeurs (4), act 1 |
| 2 | `m03_01` | 4 | | painting → cafe (5), act 2 |
| 3 | `m03_02` | 4 | | painting → bedroom (6, `chambreb`), act 2 |
| 4 | `m03_03` | 4 | | painting → maisonj (7), act 2 |
| 5 | `m03_04` | 4 | | painting → hopiint (8), act 2 |
| 6 | `m03_05` | 4 | | painting → terrasse (10), act 2 |
| 7 | `m03_06` | 4 | | painting → pont (9), act 2 |
| 8 | `m04_01` | 4 | | painting → jardin (11), act 3 |
| 9 | `m04_02` | 4 | | painting → champ (12), act 3 |
| 10 | `m04_03` | 4 | | painting → eglise (13), act 3 |
| 11 | `robot` | 4 | | the guide; talks when clicked |
| 12 | `etoile` | 2 (hand) | | the star, object 0 |
| 13 | `prtholl` | 1 | yes | door node, shown while act 1 is unfinished |
| 14 | `prtarles` | 1 | yes | door node, act 2 |
| 15 | `prtauvers` | 1 | yes | door node, act 3 |
| 16 | `vase` | 0xFF | | opens zone 0 once the star is taken |
| 17 | `ecran` | 4 | | the robot's screen (talks when clicked) |
| 18 | `cou` | 4 | | robot part (talks) |
| 19 | `oeild` | 4 | | robot part (talks) |
| 20 | `oeilg` | 4 | | robot part (talks) |
| 21 | `tete` | 4 | | robot part (talks) |

The museum's hover only knows cursor types 2, 3, 4 and requires the object within 1,200
of the camera ((x, z) of the node's camera-relative position, `interaction.md`); clicks
need the same distance.

Animation records at `0x4aed70` (4 × 0x78, count `0x4aed68`):

| # | Track | Node | Playing flag | End of track (0x42b5fe) |
|---:|---|---|---|---|
| 0 | `etoile.3da` | `etoile` | 0x4aede4 | holds at frame 52 until the star is taken (0x4aeb24), then runs to its length and stops |
| 1 | `robot01.3da` | `robot` | 0x4aee5c | stops and starts record 2 |
| 2 | `robot02.3da` | `robot` | 0x4aeed4 | loops from frame 1 |
| 3 | `robot03.3da` | `robot` | 0x4aef4c | hides the robot and stops records 1..3; never started (Q-0200) |

Box sets (`LoadBoxMusee`): `BOX1.3DI` .. `BOX4.3DI` in slots 1..4, swapped with 0x42a980
(slot 0 = `BOX.3DI`, `scene.md`). Static sounds (0x42abf1): slot 1 `robot2`, slot 2
`etoile`, slot 3 `musee` (the ambience, looped from init); slot 0 empty.

Textures: the init loads the robot screen texture `ROBI3N` and the colour versions of the
paintings (`RVBTERRA`, `RVBMAISO`, `RVBCAFE`, `RVBPONT`, `RVBPATAT`, `RVBCHAMB`, `RVBPOSTE`,
`RVBHOSTO`, `RVBMANGE`, `RVBCHAMP`, `RVBJARDI`, `RVBEGLIS`); `RVBPOSTE` and `RVBJARDI` are
loaded but never applied.

## State (E-0321)

| Variable | Role |
|---|---|
| `zoneSolved[0..24]` (0x4abb0c) | the 2D zones solved (`scene.md`) |
| 0x4aba50 / 0x4aba54 / 0x4aba58 | act 1 / 2 / 3 started (a painting of the act was clicked once) |
| 0x4abbdc / 0x4abbe0 / 0x4abbe4 | the current act (one of them 1) |
| 0x4aba48 | set by the flight to any painting (0x41f506) and by leaving zone 0: the robot no longer talks when clicked |
| 0x4aba44 | the star has been taken |
| 0x4abbe8 | the star was clicked; the vase opens zone 0 (cleared when it does) |
| 0x4abbd8 | object 0 (the star) has been dropped into the bar (0x426171) |
| 0x4abbf0 | the robot has met the player |
| 0x4aeb24 | the star's track may pass frame 52 |
| 0x4aef64 | 1 = no act is left unfinished (see init); 0 = box set 4 with a door shown |
| 0x59901c | a robot line is playing; 0x599020 = index of the next line |
| 0x599014 | a hint line is playing |
| 0x599010 | the robot's screen scrolls (every 10 ticks, 0x4399d0 with 0x42ad1c) |
| 0x4abbfa, 0x4e3124 | written only (2 and 1), never read |
| byte 0x4abbd4 | the sunflower count |

## Init (0x42ad92)

1. Resolve the object table; hide `prtholl`, `prtarles`, `prtauvers`; 0x4aef64 = 1.
2. Sunflower count: set to 0 when it is 1 and act 1 has not started, 3 and act 2 has not
   started, or 15 and act 3 has not started.
3. Load the tracks, the box sets and the sounds; pose `robot` at frame 1 of `robot01`.
4. **Box set** (the last matching line wins):
   - box set 1;
   - zone 0 solved and act 1 not started: box set 2, hide `prtarles`;
   - zones 1, 2, 3 solved and act 2 not started: box set 3, hide `prtarles`;
   - zones 4 … 18 all solved and act 3 not started: box set 0 (`BOX.3DI` alone), hide
     `prtauvers`;
   (each of these three also clears the current act 0x4abbdc/e0/e4)
   - current act 1, act 1 started, one of zones 1..3 unsolved: box set 4, show `prtholl`,
     0x4aef64 = 0;
   - current act 2, act 2 started, one of zones 4..18 unsolved: box set 4, show
     `prtarles`, 0x4aef64 = 0;
   - current act 3, act 3 started, one of zones 19..24 unsolved: box set 4, show
     `prtauvers`, 0x4aef64 = 0;
   - after the end (0x4aba5c): box set 1.
5. `vase` cursor type: 0xFF when zone 0 is solved, else 3 (zone) when the star was taken.
6. If the star is not yet in the bar (0x4abbd8 = 0): stop the robot tracks, 0x4abbf0 = 0,
   and put the viewer at the entrance (-39, -209, 361; angles 4066, 20, 0) whatever the
   arrival spot was.
7. If the robot has met the player (0x4abbf0): `robot02` plays (looping) from its current
   frame.
8. Clear the dialogue state; the robot's screen is retextured from `ROBI3` to `ROBI3N`
   (its idle look).
9. **Paintings in colour**: each painting whose scene is complete is retextured from its
   grey texture to the colour one: `m01_03` `MANGEUR` → `RVBMANGE` (zones 2, 3), `m01_02`
   `PATATHOM` → `RVBPATAT` (1), `m03_01` `CAFE` → `RVBCAFE` (4, 5, 6), `m03_02` `CHAMBRE` →
   `RVBCHAMB` (7..11), `m03_04` `HOSTO` → `RVBHOSTO` (13, 14, 15), `m03_05` `TERRASSE` →
   `RVBTERRA` (16, 17), `m03_06` `PONT` → `RVBPONT` (18), `m03_03` `MAISONJ` → `RVBMAISO`
   (12), `m04_02` `CHAMP` → `RVBCHAMP` (22, 24), `m04_03` `EGLISE` → `RVBEGLIS` (23).
   (`m01_02` `PATATHOM` pairs with maisonet, `m01_03` `MANGEUR` with mangeurs.)
10. Start the ambience. If 0x4aba48 is set, the robot's six parts get cursor type 0xFF.

## Clicks (0x42b776; left button, arrow cursor, object within 1,200)

- **A painting**: `prevScene` = 0, `scene` = its scene (table above; `m03_02` also sets
  0x4abd14 = 1 so that the bedroom is `chambreb`), request the reload, start the flight
  (0x41f506, `scene.md`). The first click on a painting of an act starts that act: its
  "started" flag = 1 and it becomes the current act (the other two cleared).
- **`vase`**, when 0x4abbe8 = 1: **zone 0** (mode 1, zone 0), 0x4abbe8 = 0.
- **`etoile`**: hide it; 0x4aeb24 = 1; the cursor becomes object 0 (the star); open the bar;
  the star's track plays from frame 166; 0x4abbe8 = 1, 0x4aba44 = 1; `vase` gets cursor
  type 3. Dropping the star into the bar sets 0x4abbd8 (`interaction.md`).
- **`ecran`, `robot`, `cou`, `oeild`, `tete`, `oeilg`**, when no line is playing and
  0x4aba48 = 0: the robot speaks (below), and the six parts get cursor type 0xFF.

## Automatic events (0x42b776)

- **Meeting the robot**: while no robot track plays and the robot has not met the player,
  when the `robot` node is within 1,500 ((x, z) of its camera-relative position): the
  robot speaks, `robot01` starts (then `robot02` loops), the `robot2` sound plays looped,
  0x4abbf0 = 1, the six parts get cursor type 0xFF.
- **The screen scroll** (E-0375): a tick counter 0x599018 grows every frame; while the
  screen scrolls and it is past 10, `ecran`'s UVs go through 0x42ad1c one by one (v up by
  0x7f0000, counting; after 6 UVs down, counting back to 0, then up again) and it restarts.
- **Speaking** uses the streamed voice lines of the table at 0x4aef50: `a50_01`,
  `a50_01c`, `a50_01d`, `a50_01e`, `a50_01h` (index 0x599020). Starting plays line 0
  (`a50_01`), the screen unchanged. Each time the stream ends (the stream-ended flag
  0x651678, read by 0x416a2f) while speaking: at index 1 the next line plays (`a50_01c`),
  the screen is retextured `ROBI3N` → `ROBI3` and scrolls; at index 2 the screen goes back
  `ROBI3` → `ROBI3N`, scrolling stops, and if the star is not yet taken and its track is
  not waiting at frame 52 the star's track starts with the `etoile` sound; the parts get
  cursor type 4 again; speaking ends. Lines 2..4 of the table are never reached.
- **Hints** (`a50_01d`, one at a time until its stream ends; only once the robot has met
  the player and when no line is playing):
  - while a door is shown (0x4aef64 = 0), not after the end of the game: current act 1 and
    x > -3000 and z < 4600; act 2 and z < 6500; act 3 and x < 3000 and z < 4600;
  - otherwise (0x4aef64 = 1), with R1 = {z ≥ 5301 and -429 ≤ x ≤ 199} and R2 = {x > 1500
    and 3950 < z < 4500}: zone 0 solved and act 1 not started: in R1 or R2; zones 1, 2, 3
    solved and act 2 not started: in R2; zone 0 not solved: x < -1400 and 3950 < z < 4500,
    or R1 or R2.
- **Back from the option menu** (0x4e3120, set by 0x42f515) in the museum while 0x4aba48 =
  0: the parts get cursor type 4, speaking is reset.
- **The end**: after the end of the game (0x4aba5c), when the viewer's z < 3500: stop the
  sounds, play `MOVIES\fin.hnm` (mode 2), 0x4aba60 = 1; the movie's end leads to the credits
  (`boot.md`, 0x42fbd6).

## Exits

- The eleven paintings (clicks above). Backspace and the return icon do nothing here
  (`scene` = 0).
- Zone 0 through the vase.
