# Zone RO (5): Alberich's world, the egg and the pipes (Ring, DVD)

Evidence: E-0190..E-0193. Addresses are `RING_DVD.EXE`; the set-up (0x458a90, extracted by
emulation, E-0094) is listed in `engines/ring/notes/zones/ro.md`, decompiles in
`engines/ring/notes/decomp/ro/`. Ids are decimal. Calls as in `ni.md`: play(id, n) 0x406de0
(n = 1 once, 2 looping), stop(id, r) 0x406e00, 0x406ef0(id) = the sound plays,
`PlyCin(name)` 0x401490 (`DATA\RO\PLA\<name>.cnm`), `PuzSetAct` 0x402490, `RotSetAct`, acc on
(object) 0x403030 / (object, from, to) 0x403070, acc off 0x403050 / `ObjSetAccOff` 0x403090,
puzzle movabilities on / off (puzzle, from, to) 0x404a70 / 0x404a90 (`PuzSetMovOnOrOff`),
`RotSetMovOff` 0x405850, rotation movabilities on 0x405830. "Show" / "hide" are `ObjPreSho` /
`ObjPreHid` (one presentation, or all with the one-argument forms). "Vol(s) = n" is the
sound's own volume (`SouSet_406e20`); "rnd20" is rand() × 20 / 32768. "In hand" 0x406530,
"held" 0x406550, "drop" 0x406570. "Frame" is 0x40f6c0. "Esc" is
`GetAsyncKeyState(VK_ESCAPE)`: a step loop with Esc stops early when Escape is held.

**Score.** RO is world 2's second part: it **sets** SY's float **90006** (N2's score, which N2
leaves at 50) to fixed values: 51.8, 64.3, 75.0, 78.6, 85.7, 100.0 (f32 constants written
by `VarSetFloa` 0x406230, E-0191).

## Places

- **The cave** 40000..40004 (`ROS00N01..05`, one layer each: object 40203's pictures, shown
  at the end of part 1): 40001 is the crossing (→ 40004 ride 1790, → 40003 1791, → 40000
  1792, → 40002 1793); 40000 → 40001 (1789) and → puzzle 40010 (the egg); 40002, 40003 →
  40001 (1794, 1795); 40004 → 40005 (1796, **disabled at set-up**) and → 40001 (1797).
- **40005** (`ROS00N06`, no layer): → 40004 (1798), → puzzle 40060 (the pipes).
- **The egg puzzles**: 40010 (the egg, `ROS00N01P01`), 40011 (the sliding tiles, `…L02`),
  40013 (the five dials, `…L01`), 40012 (the ring and crown, `…L03`); each returns to 40000
  by its bottom band (movability 0, `unk_19` 0).
- **The pipe room** 40060 (`ROS00N06P01`): the lever (object 40060, 72 pictures), seven
  pipes (object 40201, 14 animations), a keyboard (object 40202, 16 pictures); back to 40005
  by the bottom band.
- **Faces** 40100..40103 (`ROS00N01A01_A..D`) and 40104 (`RO_ERDA`): the dialogues' close-ups
  (object 40300's animation `ROS00N01A01_B` on 40101).
- Sounds: ambient 40001 (`1799.was`) on every rotation and the egg / face puzzles; ambient
  40604 (`1800.was`) declared on the rotations and 40060, **off** at set-up; 3D 40002
  (`1802.wav`) on the rotations and puzzles, 40003 (`1803.wav`) on the rotations.

## Variables

Bytes (initial 0 unless said): 40000 the Fire Power used on the egg; 40501..40577 the tile
grid (cell `rc` is byte 40501 + rc, rows 1..7, columns 1..7; 99 = wall, 0 = empty; at
set-up cell 12 = 0 and cells 21..24, 31..34, 41..44, 51..54 = their own number, i.e. the
tiles in order and the gap above column 2); 40601..40605 the dials (0..97); 40701 tiles
solved, 40702 dials solved, 40703 the crown placed; 40801 the ring placed; 40802 the pipes
solved; 40804 the lever (0..71); 40805 (56) the tile size in pixels; 40806, 40807 the two
self-turning dials' counters; 40200..40206 the pipes' switches (initial 1, 0, 1, 0, 0, 1,
0); 40901..40907 (26) and 40911..40917 (70) the last frame reported by each pipe's two
animations. Strings: 40901 `"0000000"` (the pipes played), 40902 `"00000000"` (the keys
played). SY's float 90006 is the score.

## Objects

| Object | Where | What |
|---:|---|---|
| 40000 "Fire Power" | bag (entry 0) | lit on the egg |
| 40012 "Ring", 40013 "Crown" | bag (entry 0) | placed on the egg (40012 puzzle) |
| 40010 "The Egg" | puzzles 40010 (#0 `unk_19` 0), 40011 (#1 1, disabled), 40012 (#2 2); presentations 0, 1 animations on 40012 | the egg |
| 40011 | puzzle 40011, one accessibility per cell (`unk_19` = the cell 12, 21..54); presentations 0..3 (rows 2..5) × 4 pictures `L01Trc.bmp` | the sliding tiles |
| 40101..40105 | puzzle 40013, 98 pictures each (`ROS00N01P01S02CFn.0001..`); 40101's five accessibilities `unk_19` 0..4 (0 and 1 have empty rectangles), drag | the five dials |
| 40060 | puzzle 40060, 72 pictures; eight accessibilities `unk_19` 0..7 (only #0 enabled), drag | the lever (stops 0, 10, …, 70) |
| 40201 | puzzle 40060, `unk_19` 0..6 (the seven pipes); presentations 0..6 animations ids 40100..40106 (70 frames), 7..13 ids 40201..40207 (26 frames), flags 6 | the pipes |
| 40202 | puzzle 40060, `unk_19` 0..14 disabled; presentation 0 the keyboard, 1..15 a key pressed; flags 3 | the keyboard |
| 40203 | layer 0 of 40000..40004 | the cave after part 1 |
| 40300 | puzzle 40101 animation | a face |

No object has flag 8: RO has no take path; it has no list-click, on-accessibility or
button-down handler beyond 40202's (below).

## Entering (`GameSetZoneRO` 0x43d910, entry)

N2's end calls 0x43d8f0(0) = `GoZone(5, 0)` (E-0132).

- **0**: rotation 40000 at alpha 0, ran 85.3, `RotSetAct`; `BagRem(70000)` (N2's Fire),
  `PlyCin(1506)`, `BagAdd` 40000, 40012, 40013, `PuzSetAct(40100)`, play(40700) (sound chain
  below).
- **10** (resumed after Erda): needs `<install>Data\Save\log.ars` (0x47bd10; else the log
  "Wrong Erda AS - RO -> Can not find file" and nothing); `BagRemAll`; byte 90018 = 0:
  `RotSetAct(dword 90022)` and `RotSetFreOn` / `Off` by byte 90026; else `PuzSetAct(dword
  90022)`; then `LoadSaveTimer("log", 1)` (failing: logged, stop) and 0x4696f0. RO and N2
  share "log" and world 2's variables (`spec/bag.md`, Erda).
- No other entry (no test entry 999).

## Handlers

**Object click (0x43afa0, object, `unk_19`)**. Other objects: nothing (no drop).

- 40010 the egg. Nothing in hand, `unk_19` 0: byte 40000 = 0: `PuzSetAct(40010)`; else by
  bytes 40701 / 40702 / 40703: 0/0/0 → `PuzSetAct(40011)`, 40011 shown (all), acc on 40011;
  1/0/0 → `PuzSetAct(40013)`; 1/1/0 → `PuzSetAct(40012)`. In hand: `unk_19` 0, held 40000
  and byte 40000 = 0: `PlyCin(1780)`, score = 51.8, `PuzSetAct(40011)`, a frame; when byte
  40701 = 0 the tiles are shuffled by 2000 random moves (cell (rand × 4 / 32768 + 2) × 10 +
  rand × 4 / 32768 + 1, the move rule below without sound); a frame; byte 40000 = 1.
  `unk_19` 2: held Ring: 40010/0 shown, `BagRem(40012)`, byte 40801 = 1; held Crown and byte
  40801 = 1: 40010/0 hidden, `PlyCin(1781)`, score = 78.6, `BagRem(40013)`, byte 40703 = 1,
  `PuzSetAct(40103)`, stop(40002, 0x400), `PuzSetAct(40101)`, play(40706) (the end of part 1,
  below). The object in hand is dropped in every in-hand case.
- 40011 a tile cell c (in hand: drop). When cell c holds tile t ≠ 0 (its picture:
  presentation t / 10 − 2, index t % 10 − 1, position from `ObjPreGetImgCooOnPuzX` /
  `…Y` 0x403850 / 0x403890): the first empty neighbour in the order **up** (c − 10), **down**
  (c + 10), **left** (c − 1), **right** (c + 1) takes t, cell c becomes 0, and the picture
  moves by byte 40805 (56) pixels that way (`ObjPreSetImgCooOnPuz` 0x4037c0); no empty
  neighbour: nothing moves. Then vol(40103) = 80 + rnd20, play(40103). A tile moved down
  out of cell 12 checks the grid: cells 21..24, 31..34, 41..44, 51..54 read in that order
  never decreasing → **solved**: a frame, 40011 hidden, acc off 40011 and 40010 #1, on 40010
  #2, byte 40701 = 1, `PlyCin(1782)`, score = 64.3, `PuzSetAct(40013)`, 40101..40105/0
  shown, timer 0 (every 50 ms) and timer 1 (every 30 ms) started.
- 40201 pipe p (in hand: drop): acc off 40060 (all), puzzle 40060's movability 0 off; lever
  stop s = (the lever's last position, 0x4a1cc0) / 10. s ≠ p + 1: byte 40200 + p toggled,
  40201/(p + 7) shown (the switch animation, id 40201 + p), vol(40602) = 80 + rnd20,
  play(40602). s = p + 1: 40201/p shown (the pipe plays, id 40100 + p) and string 40901 =
  its last six characters followed by the digit p (`VarGetStrg` 0x4062e0, `VarSetStrg`
  0x4062b0).

**Button down (0x43b9a0, object, `unk_19`)**: 40202 key k = `unk_19` (in hand: drop):
40202/1..15 hidden, /(k + 1) shown, play(40500 + k); for k ≥ 7 also string 40902 = its
last seven characters followed by the digit k − 7, and when it is `"01276534"`,
`"01476534"`, `"01276532"` or `"01476532"` (0x48db08, 0x48dafc, 0x48daf0, 0x48dae4):
score = 100, play(40603) (RO's end, below).

**Drag (0x43bbf0, object, `unk_19`, …, phase 1 start / 2 release / 3 move)**, with the drag
getters of `ni.md` and 0x406890 / 0x4068a0 = |current − previous| in x / y (0x426180 /
0x4261a0), 0x406730 / 0x406770 current x < / > previous x, 0x406710 / 0x4066d0 current y
> / < previous y; the position p is a float (0x4a1cd4):

- 40060 the lever. Start: mode 2, limit (0, 0)–(640, 480), play(40102, loop), max 71, p =
  byte 40804. Move (x changed; in hand: drop): play(40102, loop) when it does not play,
  vol(40102) = |dx| / 2 + 80; moving left p += |dx| / 6 (f64 [0x47e630]), moving right p −=
  |dx| / 6; clamped 0..71; 40060 hidden, /trunc(p) shown. Release: stop(40102, 0x400);
  n = trunc(p), the stop t = trunc(p × 0.1) × 10, + 10 when t + 5 < p; one picture per frame
  from n to t (Esc); acc off 40060, on 40060 #(n / 10); byte 40804 = n (0x4a1cc0 = n).
- 40101, `unk_19` d (the dial 40101 + d, byte 40601 + d). Start: p = byte 40601 + d, mode
  2, limit (0, 0)–(640, 480), play(40102, loop), max 97. Move (y changed; in hand: drop):
  play(40102) as above, vol(40102) = |dy| / 2 + 80; moving down p += |dy|, moving up p −=
  |dy|; **wrapping**: below 0 → 97, above 97 → 0; (40101 + d) hidden, /trunc(p) shown.
  Release: the same rounding to a multiple of 10, one picture per frame (Esc), stop(40102,
  0x400), byte 40601 + d = the position. **Solved** when bytes 40601..40605 are 10, 90, 60,
  50 and 50 or 40: byte 40702 = 1, 40101..40105 hidden and their accessibilities off,
  `PlyCin(1783)` (40605 = 50) or `PlyCin(1784)` (40605 = 40), score = 75.0,
  `PuzSetAct(40012)`. The dials 0 and 1 cannot be dragged (empty rectangles): timers 0 and
  1 turn them to 10 and 90.

**Before a movability (0x43c290, from, to, index, `unk_19`, kind)**: kind 2 from 40060 or
to 40005 (leaving the pipe room): vol(40102) = 100, play(40102, loop); the lever back to 0,
one picture per frame (byte 40804 shown then decreased while above 0; Esc); byte 40804 = 0,
stop(40102, 0x400); byte 40802 = 1: `PlyCin(1785)`; acc off 40060, on 40060 #0, on 40201,
off 40202; 40060, 40201, 40202 hidden; byte 40802 = 0; string 40902 = `"00000000"`;
0x4a1cc0 = 0.

**After a movability (0x43c450, to, from, index, `unk_19`, kind)**: kind 1: from 40000 or to
40010: byte 40804 = 0 (Q-0060); from 40005 or to 40060: play(40003, loop), vol(40003) = 88.
Kind 2: from 40060 or to 40005: vol(40003) = 82.

**Timer (0x43c500, id)**: 0: byte 40806 += 1, 40101/(byte 40806) shown; at 10 the timer
stops (`TimSto` 0x4065e0) and byte 40601 = 10. 1: byte 40807 += 1, 40102/(byte 40807)
shown; at 90 the timer stops and byte 40602 = 90. (Each frame is shown over the previous
ones, all at priority 1000.)

**Animation (0x43c5e0, id, name, frame)**:

- 40100 + p (pipe p playing, p = 0..6): frame 1: acc off 40060, 40201; vol(40600) = 80 +
  rnd20, play(40600). Frame 30: vol(40601) = 80 + rnd20, play(40601); byte 40200 + p ≠ 0:
  play(40200 + p), else play(40300 + p). Frame 70: acc on 40060 #(p + 1), on 40201, puzzle
  40060's movability 0 on; for p = 0 only, when string 40901 is `"6543210"` (0x48db44) and
  bytes 40200..40206 sum to 7: byte 40802 = 1, string 40901 = `"0000000"`, play(40400),
  score = 85.7, acc off 40060, 40201, the lever shown at 10, 9, …, 1, one per frame (Esc).
  Every frame of these animations: byte 40911 + p = the frame.
- 40201 + p (pipe p's switch, 26 frames): byte 40901 + p = the frame; when bytes
  40901..40907 are all 26 and 40911..40917 all 70 (every animation finished): acc on 40060
  #(byte 40804 / 10), puzzle 40060's movability 0 on.

**Sound (0x43d4a0, id, type, reason, ended)**, natural ends only:

- Arrival: 40700 → `PuzSetAct(40101)`, play(40701); 40701 → `RotSetAct(40000)`.
- The end of part 1 (after the crown): 40706 → 40102, 40707; 40707 → 40101, 40708; 40708
  → 40104, 40709; 40709 → 40102, 40710; 40710 → 40101, 40711; 40711 → 40103, 40702; 40702
  → 40102, 40703; 40703 → 40103, 40704 ("a → p, n" = `PuzSetAct(p)`, play(n)); 40704 →
  stop all (0x400), `PlyCin(1788)`, 0x4a1cc0 = 0, 3D sound 40002 off on rotations
  40000..40004 (`RotSet3DSouOff`), ambient 40001 off on 40000..40005 (`RotSetAmbSouOff`),
  ambient 40604 on on 40000..40005 (`RotSetAmbSouOn` 0x405de0) and puzzle 40060
  (`PuzSetAmbSouOn` 0x404b90), 40203 shown (all), `RotSetMovOff(40000, 1, 1)` (the egg),
  40004's movability 0 on (to 40005), `RotSetAct(40000)`, and the rides renamed
  (`RotSetMovRidNam` 0x405870): 40000 #0 `ro0102`, 40001 #2 `ro0201`, #3 `ro0203`, 40002 #0
  `ro0302`, 40003 #0 `ro0402`, 40004 #0 `1796`, #1 `ro0502`.
- 40400 (the pipes solved) → `PlyCin(1787)`, 40202/0 shown, acc on 40202.
- 40603 (the tune played) → stop(40003, 0x400), `TimStoAll`, `PlyCin(1786)`, AS's
  0x437750(2): **back to the hub, world 2 (N2 + RO) done** (`as.md`, E-0193).

RO handles no take (0x40bed0), list-click (0x40c1f0), on-accessibility (0x40ca80) or pause
event (0x40c910 is WA's, `spec/events.md`); "on a movability" (0x433b80) and "on nothing"
(0x442e30) are shared defaults.

## Game overs

None: RO never calls 0x408db0.

## Flow

1. Arrival (entry 0, from N2): the Fire leaves the bag; Fire Power, Ring and Crown are in
   it; video 1506 and the faces' dialogue (40700, 40701); the player stands in the cave
   (40000).
2. The egg (40000 → puzzle 40010): Fire Power on it (video 1780) shuffles the tile puzzle
   40011.
3. The tiles: slide them back in order with the gap above column 2 (the last move takes the
   tile out of cell 12 downwards): video 1782, the dials puzzle 40013; dials 0 and 1 turn
   by themselves to 10 and 90.
4. The dials: 60, 50 and 50 (or 40) on the three others: video 1783 / 1784, the ring and
   crown puzzle 40012.
5. The Ring, then the Crown, on the egg: video 1781 and the faces' long dialogue
   (40706..40704), video 1788; the cave changes (40203), the egg is closed, the way 40004 →
   40005 opens.
6. The pipe room (40005 → 40060): switch every pipe on (clicking a pipe with the lever on
   another stop toggles it; 40200..40206 all 1), then play the pipes 6, 5, 4, 3, 2, 1, 0,
   each with the lever on its stop (pipe p at stop p + 1); when pipe 0 ends, the pipes are
   solved (40400, video 1787) and the keyboard opens.
7. The keyboard: the last eight of keys 7..14 played as one of the four tunes
   (`01276534`, `01476534`, `01276532`, `01476532`, key k → digit k − 7): video 1786 and the
   return to the hub (AS 0x437750(2)). Leaving the pipe room before that resets the lever,
   the keyboard and byte 40802 (the pipes must be played again; the switches stay).

## Needs (beyond the engine as of the NI / RH / N2 work)

- `RotSetMovRidNam` (0x405870 → `aMovability::SetRideName`): a movability's ride video
  changed while playing.
- `ObjPreGetImgCooOnPuzX` / `…Y` (0x403850 / 0x403890) and `ObjPreSetImgCooOnPuz`
  (0x4037c0) at run time: a presentation picture's position read and moved.
- `RotSetAmbSouOn` (0x405de0) / `PuzSetAmbSouOn` (0x404b90) and `RotSetAmbSouOff` while
  playing (the engine's sound-item switch covers them).
- `VarSetStrg` (0x4062b0) besides N2's `VarDefStrg` / `VarGetStrg`.
- Escape held (`GetAsyncKeyState`) ending the handlers' step loops early.
- Sound own volume set while playing (`SouSet_406e20`) and puzzle movabilities on / off by
  range (`PuzSetMovOnOrOff`).
