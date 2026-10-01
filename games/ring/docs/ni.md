# Zone NI (2): Nibelheim — Alberich's world (Ring, DVD)

Evidence: E-0070..E-0073. Addresses are `RING_DVD.EXE`; the set-up (0x45eb3b ..) is listed
in `engines/ring/notes/zones/ni.md`, decompiles in `engines/ring/notes/decomp/ni/`. Ids are
decimal. Calls as in `as.md`: play(id, n) 0x406de0 (n = 1 once, 2 looping), stop(id, r)
0x406e00, 0x406ef0(id) = the sound plays, `PlyCin(name)` 0x401490 (`DATA\NI\PLA\<name>.cnm`),
`PuzSetAct` 0x402490, acc on / off (object[, from, to]) 0x403030 / 0x403050 / 0x403070 /
`ObjSetAccOff` 0x403090, mov on / off of a rotation 0x405830 / 0x405820 / `RotSetMovOff`,
of a puzzle 0x404a50 / 0x404a60 / 0x404a70. "Show" / "hide" are `ObjPreSho` / `ObjPreHid`
(one presentation, or all with the one-argument forms 0x403e00 / 0x403e80). "Score +n" is
float 90005 += n (f32 constants [0x47e624] 2, [0x47e620] 3, [0x47e2e0] 5, [0x47e69c] 8).
"In hand" is 0x406530 (an object is held), "held" its id (0x406550), "drop" 0x406570.
"Frame" is 0x40f6c0: one frame drawn (`RenderFrame`) and the sound ends checked (0x468da0)
from inside the handler.

## Places

- **Rail line** (`NIS00N0x`, two layers each: the car "Bike" 10003 at its stop): rotations
  10000, 10001, 10002, 10004, 10005, joined by rides 1551..1564; 10002 also to 10003
  (`NIS00N05`), 10000 also to 10401 (ride 1552, `unk_19` 41) and 10201 (1553, 21); 10005
  to 10101 (1563). Movability `unk_19` 1 = forward, 2 = back (see "After a movability").
- **Mime's place** 10301 (`NIS03N01`, the Mime animated on layer 0, 25 frames, 10 fps, id
  10300): puzzle 10300 (his table: the Tear, the Tile, the Frog), dialogue close-ups 10390,
  10391, 10392; way to 10003 (ride 1570, `unk_19` 100).
- **Console room** 10101 / 10102 (`NIS01N0x`): console close-up puzzle 10100, hologram
  puzzle 10102; from 10102 two movabilities with the same rectangle to 10601 (1567,
  `unk_19` 16; 1568, `unk_19` 0), one of them enabled at a time.
- **Speaker** 10201 (`NIS02N01`): puzzle 10200 (speaker and handle), close-ups 10202..10205.
- **Valves and heater** 10401, 10402 (`NIS04N0x`; two animated layers, the steam, object
  10432 presentations 1, 2): valve puzzles 10400 (left, `unk_19` 41) and 10401 (right, 42);
  10403: heater puzzle 10410 (temperature, way to the tear casing 10411, disabled, and ride
  1581 to 10404); 10404: the door 10440; 10405 / 10415: water 10450; 10406 (juggle on,
  `RotSetJugOn(10406, 10, 1)`): water 10460, the way out to RH.
- **Tiles** 10601 (`NIS06N01`): puzzle 10600 (three rotating tiles, `unk_19` 61).
- **Erda's room** 10501 (`NIS05N01`): puzzles 10500 / 10510 / 10520 and their zooms 10501 /
  10511 / 10521 (helmet on 10501); 10521's movability "1582" to itself (`unk_19` 55) is the
  message to RH (pictures 12001..12003, `TR_NI_RH_BP0x`).
- Music: 14001 (`1583.was`) on the rail line, 14002 on 10201, 14003 elsewhere (0x449320).

## Variables

Bytes (initial 0 unless said): 10000 Glug fed; 10100..10113 console (10102 tile placed,
10103 hologram on, 10104 cross at 12, 10105 dam open, 10106 cross solved, 10107 boiling,
10108..10112 mosaic entries, 10113 mosaic count); 10200 speaker done once; 10300 frog taken,
10301 Mime's state (0, 1 tile asked, 2 tile given), 10302, 10303 back from RH (E-0101); 10420 /
10421 valve open; 10430 tear in the casing, 10431 heater on; 10432 heat counter; 10500
helmet taken, 10501 (initial 1) AG cells taken. Words 10100 (cross position 0..18), 10101,
10600 / 10601 / 10602 (tile positions 0..47, initial 12, 0, 24). Dwords 10000 (where Glug
was called from), 10001 (that rotation's alpha). SY's float 90005 is the world's score.

## Objects

| Object | Where | What |
|---:|---|---|
| 10000 "SP/Brutality" | bag | Alberich's Brutality (inventory, icon `NI_Brutality`) |
| 10001 "Glug" | bag; puzzles 10000 (0), 10001 (1), 10002 (2), rotations 10003 / 10401 / 10201 (3), bottom bands (4) | the creature that moves the car; presentation 0 animation on 10002 (5 frames, id 10000) |
| 10002 "Minerals" | bag | Glug's food |
| 10003 "Bike" | layers: presentation 0 = 10003 layer 1, 1 = 10201 layer 0, 3..7 = layer 0 of 10000, 10001, 10002, 10004, 10005, 8..12 = layer 1 of the same | the car at its stops; 0 and 1 shown at set-up |
| 10100 "Console" | 10100 four border bands (`unk_19` 0, cursor 53), rotation 10101 (1) | entering / leaving the console |
| 10101 / 10102 "CCButton1/2" | 10101 (1); 10100 (0, 1, disabled); flag 2 (button down) | the console's two covers; presentations: pictures and animations ids 10100..10106 |
| 10103 "CCHandle" | 10100 (1), drag, cursor 10000 | calls the car to 10005; presentations 0..12 `NIS01N01P02S01.%04d` |
| 10104 "CCTileHold" | 10100 (0, disabled) | where the Tile goes |
| 10105 "CCHolo" | 10100 two (0, disabled) | the hologram, takes Brutality |
| 10106 "CCHoloCross" | 10102 (0), drag | the cross: 0..18 `NIS01N01P03L01S01`, 19..37 the `_a` set, 38, 39 pictures |
| 10107 "CCHoloDam1" | 10102 (0) and (1, disabled), drag | the dam: 0..13 `NIS01N01P03L01S02` |
| 10109 "CCMosaicBtns" | 10100 six (0..5, disabled), flags 3 | mosaic buttons; presentations 0..5 |
| 10110 | 10100 five (1..5, disabled) | mosaic voices (play 10032 + `unk_19`) |
| 10200 "Speaker" | 10200 (0) | animations on 10202..10205 (id 10200 on 10203) |
| 10201 "Handle" | 10200 (0, disabled), drag | 0..13 `NIS02N01P01S01` |
| 10300 "Mime" | rotation 10301 (0) | animated layer id 10300; dialogue animations on 10390..10392 |
| 10302 "Frog", 10303 "Tile", 10305 "Loge's Tear" | puzzle 10300 | taken by talking to the Mime |
| 10304 "Rhine Gold" | — | declared only |
| 10420 / 10421 "LValve/RValve" | 10400 / 10401 (0) and (1, disabled), drag | 0 = frame 12, 1..12 frames |
| 10430 "TearCasing" | 10411 (0), (1, 2 disabled), flags 3 | pictures 0, 1; animations ids 10422..10425 (presentations 2..5), 6 the tear |
| 10431 "Temperat" | 10410 | 0 empty, 1..12 the thermometer |
| 10432 | 10410 (presentation 0: three bubbles, ping-pong), 10401 / 10402 layers (1, 2) | the boiling |
| 10440 "Door", 10450 / 10460 "Water" | 10404; 10405 + 10415; 10406 | |
| 10503 "Helmet", 10504 "Helmet&Frog", 10505 "AGCells" | 10501 puzzle / bag; rotation 10501 | |
| 10600 "UTiles", 10601..10603 "UTile1..3" | 10600 bottom band (0); tiles (drag) | 48 frames each |
| 12000 | 12001..12003 | the message pictures' animations |

## Entering (`GameSetZoneNI` 0x44a840, entry)

AS enters through 0x44a7d0(0): `GoZone(2, 0)` when SY's byte 90009 is 0, else
`GoZone(dword 90013, 10)` (E-0073). 0x44a7d0(3) is `GoZone(2, 3)` (called by RH's Rhine Gold, 0x4447c1, E-0101,
after `PlyCin(1666)` and `BagRem(20403)`); 0x44a7d0(9) starts timer 9 (1 s).

- **0**: `PlyCin(1540)`, play(14001, loop), `PlyCin(1541)`, `BagRemAll`, `BagAdd(10000)`,
  `PuzSetAct(10390)`, play(10001): the Mime's welcome (sound chain below).
- **3** (back from RH): `TimStoAll`, puzzle 10410's movability 0 on (0x404a70), `PlyCin(1550)`,
  rotation 10301 at alpha 160, ran 85.7, `RotSetAct`, then `PuzSetAct(10392)`, play(14001,
  loop), play(10021), byte 10303 = 1.
- **10** (resume): needs `Data\Save\alb.ars` (else the error "Wrong Erda AS / NI"),
  `BagRemAll`; byte 90017 = 0: `RotSetAct(dword 90021)` and `RotSetFreOn/Off` by byte 90025;
  else `PuzSetAct(dword 90021)`; then `LoadSaveTimer` and 0x4696f0 (replays the saved
  sounds). Saved games only (`spec/save.md`, to come).
- **999**: `BagRemAll`, `BagAdd` 10000, 10001, 10002, 10303, 10305, 10504, byte 10106 = 1,
  object 1 shown (0x403e00), play(10409, loop), `RotSetAct(10415)`. No caller found (Q-0020).

## Handlers

**Object click (0x445c80, object, `unk_19`, place id)**. Unless listed, an object in hand is
dropped and nothing else happens.

- 10001 Glug. In hand, `unk_19` 1, held Glug: `PlyCin(1513)`, `BagRem(10001)`, score +2,
  `PuzSetAct(10002)`, byte 10000 = 1, Glug shown, `ObjPrePauFraAni(10001, 0, 1, 1000, 0)`,
  play(10800, loop); drop. In hand, `unk_19` 2, held Minerals and Glug not in the bag
  (`BagIsIn`): stop 10800, `PlyCin(1514)`, movability 0 of 10003, 10201, 10401 off, on for
  dword 10000's rotation; when 10901 does not play: play(10900), play(10901, loop); the car
  shown at that rotation's stop (dword 10000 = 10401: presentations 8..12, others hidden;
  else 3..7); drop. Nothing in hand, `unk_19` 0 or 3: dword 10000 = place id, dword 10001
  = its alpha (truncated), `PuzSetAct(10000)`, 200 ms of frames, then byte 10000 set:
  `PuzSetAct(10002)`, play(10800, loop); else `PuzSetAct(10001)`; play(10803). `unk_19` 4:
  `PuzSetAct(10000)`, 200 ms of frames, play(10804), back to dword 10000's rotation at
  alpha dword 10001, beta 60, ran 85.7.
- 10100 Console, `unk_19` 1: `RotSetRolTo(10101, 270.4, 10.4, 85.7)` (the animated turn,
  0x4101c0), `PuzSetAct(10100)`, acc on 10101 #0, #2, 10102 #0, #2 and all of 10100,
  `SetCursorPos(505, 205)`.
- 10104 Tile holder, held Tile, byte 10102 = 0: play(10106), byte 10102 = 1, score +5,
  10100 presentation 1 shown, `BagRem(10303)`, acc off 10104, on 10109, 10110; drop.
- 10105 Hologram: held Brutality, byte 10103 = 0: byte 10103 = 1, score +3, `PlyCin(1510)`,
  10100/2 shown, play(10104), 10102/2 shown, acc off 10100, 10101, 10102, 10103, 10105 #1;
  drop. Nothing in hand and byte 10103 = 1: `PuzSetAct(10102)`.
- 10109 Mosaic, `unk_19` 0 (the centre): play(10106), 10109/0 hidden, a frame; bytes
  10108..10112 = 5, 2, 3, 4, 1: acc off 10109, 10110, puzzle 10100's background becomes
  `NIS01N01P02.0001.bmp` (`PuzAddBgrImg` at run time), byte 10113 = 9, 10101/0 hidden,
  10101/5 and /6 shown, 10109 hidden; otherwise bytes 10108..10113 = 0.
- 10110 Mosaic voices: play(10032 + `unk_19`).
- 10200 Speaker: acc off 10200, play(10022) (chain below).
- 10300 Mime, held Brutality: `PlyCin(1512)`; byte 10301 = 1: byte 10301 = 2,
  `PuzSetAct(10390)`, play(10014); else `PuzSetAct(10390)`, play(10015 + rand() × 3 / 32768);
  drop.
- 10302 Frog: byte 10301 = 0, `PuzSetAct(10392)`, play(10010).
- 10303 Tile: `PuzSetAct(10392)`, play(10012).
- 10305 Tear: byte 10301 = 0, `PuzSetAct(10392)`, play(10005).
- 10430 Tear casing. Held: Tear and `unk_19` 1: score +3, 10430/6 and /1 shown,
  `BagRem(10305)`, byte 10430 = 1; drop, then 0x445a10. Nothing in hand: byte 10431 = 0;
  `unk_19` 1 with byte 10430 = 1: /1, /6 hidden, `BagAdd(10305)`, score −3, byte 10430 = 0;
  `unk_19` 1 or 2: 0x445a10. `unk_19` 0: 10430 hidden, puzzle 10411's movabilities off,
  acc off 10430 #0; byte 10430 = 0: /2 shown, else /4 and /1; /0 shown; 0x445a10.
- 10440 Door, nothing in hand: bytes 10106 and 10431 both 1: play(10414) only. Byte 10106
  ≠ 0: `PlyCin(1516)`, play(10409, loop) when byte 10106 = 1 and it does not play, rotation
  10415 at alpha 270, beta 0.3, ran 85.7; else `PlyCin(1515)`, rotation 10405 likewise.
- 10450 Water: byte 10106 ≠ 1: `PlyCin(1519)`, game over 1. Held Helmet&Frog: `PlyCin(1517)`,
  score +8, rotation 10406 at alpha 270, beta 0.3, ran 85.7, acc off 10450, drop. Otherwise
  `PlyCin(1518)`, game over 2.
- 10460 Water, nothing in hand: `TimStoAll`, stop all (0x400), `PlyCin(1520)`, score +3,
  `GoZone(3, 0)` (0x445720): on to RH.
- 10503 Helmet, byte 10500 = 0: 10503 shown (all), byte 10500 = 1, acc off 10503,
  `BagAdd(10503)`, score +2; with the Frog in the bag: score +5, `BagRem` 10302 and 10503,
  `BagAdd(10504)`, `PlyCin(1522)`.
- 10505 AG cells: `PlyCin(1521)`, byte 10501 = 1, `BagAdd(10505)` (never disabled, Q-0024).
- 10600 Tiles (bottom band): until the three positions are 12, 0, 24: play(10401) when it
  does not play; each tile not at its rest steps by one (wrapping 0..47) and is redrawn
  (`ObjPreHidDeaPuz`, show); the direction is fixed at the click: tile 1 −1 when word 10600
  + 36 (− 48 above 47) < 37, else +1; tile 2 −1 when word 10601 < 25; tile 3 −1 when word
  10602 + 24 (− 48 above 47) < 25; a frame per step. Then `RotSetAct(10601)`.

**Button down (0x4472b0, object, `unk_19`)**:

- 10109, nothing in hand: play(10106), 10109 hidden, /`unk_19` shown; `unk_19` ≠ 0: byte
  10108 + byte 10113 = `unk_19`, byte 10113 += 1.
- 10101 (in hand: drop). `unk_19` 1: `RotSetRolTo(10101, 270.4, 10.4, 85.7)`,
  `PuzSetAct(10100)`, 10102 hidden, play(10102), acc off 10101 #1..2, 10102 #1..2, 10100,
  10103; byte 10102 = 0: 10101/0 then /1 shown (opening animation, id 10101); else byte
  10113 = 9: 10101/0 hidden, /5 shown, otherwise acc on 10110; 10100/1 shown, 10101/2
  (id 10103); then 10100/0 shown. `unk_19` 0: play(10103), acc off 10101 #1..2, 10104,
  10109, 10110; 10101/3 (byte 10102 = 0, id 10100) or /4 (id 10102) shown; 10100 and 10109
  hidden.
- 10102 (in hand: drop), only when byte 10113 = 9. `unk_19` 1: 10102 hidden; byte 10102 ≠
  1: turn and `PuzSetAct(10100)` as above, 10102/4 shown for four frames, hidden, acc on
  10101 #0, #2. Else play(10104), acc off 10101 #1..2, 10102 #1..2, 10100, 10103, turn,
  `PuzSetAct(10100)`, 10102/0 shown, then byte 10103 = 0: 10102/1 (id 10105); else 10100/2
  and 10102/2 (id 10104). `unk_19` 0: acc off 10102 #1..2; byte 10103 = 0: acc off 10105,
  `PuzSetAct(10100)`, 10102/0 and 10100 hidden, acc on 10102 #0, #2; else play(10105), acc
  off 10105, 10102/3 shown (id 10106), 10100 hidden.
- 10430 `unk_19` 2: acc off 10430 #1..2, /3 (byte 10430 = 0, id 10423) or /5 (id 10425)
  shown, /0 and /1 hidden: closing the casing.

**Drag (0x4477d0, object, `unk_19`, …, phase 1 start / 2 release / 3 move)**. The drag
state (`spec/cursor.md`, "Dragging") holds the press position (+0, +4), a reference point
(+8, +0xc: the press position at the start, 0x4066b0 sets it), the previous (+0x10, +0x14)
and current (+0x18, +0x1c) positions (0x426140 shifts them on each move). Read here:
|cur − press| x 0x4068c0, y 0x4068d0; |cur − ref| x 0x4068e0, y 0x4068f0; no x / y move since
the last 0x406750 / 0x4066f0; cur x < press x 0x4067d0, press x < cur x 0x4067f0, cur y <
press y 0x406790, press y < cur y 0x4067b0, cur x < ref x 0x406850, cur y < ref y 0x406810.
"Steps" below advance one presentation per frame (hide, show, frame).

- 10103 handle: start: counter 0, mode 2, limit (495, 194)–(598, 284). Move (x changed):
  counter = |dx| / 5, 0 when moving left, clamped 0..12, shown. Release: stop 10401 when it
  does *not* play (as coded, Q-0021); acc off 10103; counter < 7: steps back to 0, acc on;
  else steps to 12, 1 s of frames, steps back to 0, acc on, the car shown at 10005
  (presentations 3..7), `PlyCin(1511)`, rotation 10005 at alpha 270, ran 85.7, its
  movabilities off then #1 on, play(10901, loop).
- 10106 cross: start: reference (243, 276); from the press point relative to it (x, y =
  ±|cur − ref|, negative left / above) a sector angle: x < 1: y > 0: 30 + (y + 40 + x) / 6,
  else 20 + (y − x + 40) / 6; x ≥ 1: y > 0: 0 + (x − y + 40) / 6, else 10 + (40 − y − x) /
  6 (each part at least 0); offset = (angle − word 10100) mod 19; base = 19 when byte 10105
  = 1, else 0. Move (x changed, |x|, |y| ≤ 40): value = (offset + angle) mod 19, shown at
  base + value, word 10100 = value, 0x445930. Release: value 1..6 and 13..15 step −1, 7..11
  and 16..18 +1, to 0 or 12 (wrapping 0..18; redrawn with 0x445930 each frame); word 10100
  = value; value 12: byte 10104 = 1, rotation 10102's movability 1 off, 2 on; else byte
  10104 = 0, 1 on, 2 off; 0x445a10; byte 10106 = 1: play(10101); 0x445930.
- 0x445930 (the hologram): byte 10105 = 1: 10106 hidden, /38 and /(word + 19) shown, word
  0: /39 shown and byte 10106 = 1. Else 10106 hidden, /word shown, byte 10106 = 0.
- 10107 dam: start: mode 2, limit (295, 255)–(345, 375). Move (y changed): `unk_19` 0: |dy|
  / 3, 0 when moving up; 1: 13 − |dy| / 3, 13 when moving down; byte 10105 = 0; above 12:
  13 and byte 10105 = 1; shown, 0x445930. Release: |dy| < 20: back where it was (0 /
  13, byte 10105 = 0 / 1); else `unk_19` 0 and moved down (or 1 and moved up) flips: 13
  with acc #0 off, #1 on (or 0 with #0 on, #1 off), byte 10105 = 1 (or 0); 0x445a10; byte
  10106 = 1: play(10101); 0x445930.
- 10201 speaker handle: start: mode 2, limit (299, 214)–(431, 356). Move (y changed):
  |dy| / 5, 0 when moving up, clamped 0..13, shown; play(10401) when it does not play.
  Release: stop 10401 as for 10103; below 4: steps back to 0; above 10: acc off 10201,
  steps to 13, 1 s, back to 0, `PlyCin(1525)`, `PlyCin(1526)`, acc on 10200; else steps to
  6, 1 s, back to 0, `PlyCin(1527)`, then byte 10200 ≠ 0: `PuzSetAct(10202)`, play(10030);
  else byte 10200 = 1, `PuzSetAct(10203)`, play(10027), score +2.
- 10420 / 10421 valves: start: mode 2, limit (263, 206)–(390, 341); flag 0x4a1cec =
  (`unk_19` ≠ 0). Move (y changed): `unk_19` 0: |dy| / 5 + 1 (1 when moving up), 1: 11 −
  |dy| / 5 (12 when moving down), clamped 1..12, shown (`ObjPreHidDeaPuz`). Above 8 with the
  flag clear: play(10402), flag set, score +3; boiling (byte 10107): byte 10432 halved,
  (10420 only: acc off 10420), play(10404), 0x445a10. At 4 or below with the flag set:
  stop 10404, play(10403), score −3, flag clear. Release: hidden; `unk_19` 0: |dy| ≥ 30
  and not up: 12 shown, acc #0 off, #1 on, byte = 1; else 1 shown, byte = 0. `unk_19` 1:
  |dy| ≥ 30 and not down: 1, #0 on, #1 off, byte = 0; else 12, byte = 1. Then 0x445a10.
- 10601..10603 tiles (word 10600..10602): start: counter = word. Move (x changed): word −
  |dx| / 12 moving left, + when moving right, wrapped 0..47, shown; play(10401) when it does
  not play. Release: word = counter; all three 0: words back to 12, 0, 24, `PlyCin(1524)`,
  rotation 10501 at alpha 232, `RotSetAct(10501)`.

**On an accessibility (0x44a120, object, `unk_19`, …, mouse x, mouse y)**, every frame: 10100
`unk_19` 0 (the console's border): `RotSetAct(10101)`, acc on 10101 #0, #2, 10102 #0, #2,
10100 #4, `SetCursorPos(x, y)`: the mouse at the edge leaves the console.

**Before a movability (0x449080, from, to, index, `unk_19`, kind)**:

- kind 0, 10005 → 10101: stop 10901, play(13001 + rand() × 9 / 32768).
- kind 1: `unk_19` 41: `PlyCin(1529)` (byte 10420 set) or 1528; 42: 1531 / 1530 by byte
  10421; 61: words 10600..10602 = 12, 0, 24 and the tiles shown so.
- kind 2: 41: 1534 / 1533 by byte 10420; 42: 1536 / 1535 by byte 10421.
- kind 3: to 10501 / 10511 / 10521 with `unk_19` 0: play(10501); from them: play(10502);
  from 10001: play(10804); from 10002: play(10804), stop 10800.

**After a movability (0x449320, to, from, index, `unk_19`, kind)**:

- `unk_19` 100: movability 0 of `to` off. 110: stop 10800; 10901 playing: play(10902); stop
  10901; to 10301: play(10300, loop), byte 10301 = 0.
- kind 3, `unk_19` 55: `PlyCin(1537)`, `PuzSetAct(12001)`, play(12001); other kinds ≠ 0 end.
- kind 0: the music (to 10201: 14002; above 10201 or 10101: 14003; 10000..10005: 14001;
  each when not already playing, the other two stopped). Then by `unk_19`: 1: `to`'s
  movabilities off, #0 on, and #2 for 10000 and 10002; 2: off, #1 on; 5 or 21: the car at
  layer 0 (10003/3..7 shown, 8..12 hidden), #0 on; 41: the car at layer 1 (8..12), #0 on;
  3: #0 off; 16: **game over 3**. From 10005 to 10101: stop 13001..13009; from 10415: stop
  10409; to 10406: play 10410 and 10411 looping when 10410 does not play.

**Timer (0x4497b0, id)**:

- 0 (1 s, boiling): byte 10432 += 1; 11..69: thermometer 10431/((v − 10) / 5); 100:
  /12. Every max(5, (120 − v) / 10) ticks: play(10415), 10432/(1 + rand() × 2 / 32768)
  shown (a burst on the layers). Volume of 10412 = min(100, v / 5 + 80). Above 120: timer 0
  stopped, sound types 3 and 1 stopped (0x406e40), `PlyCin(1538)`, **game over 4**.
- 1 (1 s, steady steam): byte 10432 += 1; from 11 with byte 10303 = 1 (back from RH):
  `TimStoAll`, stop all (0x400), float 90005 = 100, `PlyCin(1539)`, **AS 0x437750(1)**: NI done.

**0x445a10 (the heater)**, after every valve, casing or cross change: with h = bytes 10431 +
10106 and v = bytes 10420 + 10421:

- byte 10107 = 0, h = 2, v ≠ 2: play(10412, loop), 10432/0 shown, volume 80, byte 10432 =
  0, timer 1 stopped, timer 0 (1 s), byte 10107 = 1: boiling.
- h = 2, v = 2 (byte 10107 either): play(10412, loop), 10432/0, volume 80, timer 0 stopped,
  bytes 10107 = 0, 10432 = 0, (when it was boiling, timer 1 stopped), timer 1 (1 s),
  10431 hidden, /6 shown: steady.
- byte 10107 = 1, h ≠ 2: stop 10412, 10432 and 10431 hidden, byte 10107 = 0, timers 0 and
  1 stopped. (Byte 10107 = 0 and h ≠ 2: nothing.)

**Animation (0x4499e0, id, name, frame)**:

- 10000 frame 1: `ObjPrePauFraAni(10001, 0, 1, n × 300, 0)`, n = rand() × 10 / 32768, 0
  when above 4. 10200 frame 1: `ObjPrePauFraAni(10200, 1, 1, n × 1000, 0)` likewise.
- 10106 frame 1 (cover 2 closed): 10101/0, 10102/0 hidden, `PuzSetAct(10100)`, acc on
  10101 #0, #2, 10102 #0, #2, 10100, 10103. 10100 frame 1 / 10102 frame 36 (cover 1
  closed): `PuzSetAct(10100)`, 10101/3 (or /4 and /0) hidden, then 10101/0 (or /5) hidden
  and the same acc on.
- 10101 frame 36 (cover 1 open): acc on 10104, off 10109, on 10101 #1. 10103 frame 1: acc
  off 10104, 10109, on 10101 #1; byte 10113 ≤ 8: acc on 10109.
- 10104 frame 15: acc on 10102 #1, 10105 #0. 10105 frame 36: acc on 10105 #1, 10102 #1.
- 10300 frame 3: `RotSet3DSouOn(10301, 10301)`, `RotSet3DSouOff(10301, 10301)`, play(10301).
- 10422 (casing opening, empty): 1: acc on 10430 #1..2; 2: stop 10407; 14: play(10407);
  15: stop 10405; 26: play(10405). 10424 (opening, with the tear): 1: 10432/0 hidden,
  10430/6 shown, acc on 10430 #1..2; 2, 14, 15, 26 as 10422.
- 10423 (closing, empty): 27: puzzle 10411's movabilities on, acc on 10430 #0; 26: stop
  10406, 10408; 15: play(10406); 2: play(10408). 10425 (closing, with the tear): 26: the
  same and byte 10431 = 1, 10432/0 shown, 0x445a10, stop 10406, 10408; 15: play(10406);
  2: play(10408), 10430/6 hidden.

**Sound (0x44a1c0, id, type, reason, ended)**, natural ends only:

- Mime: 10001 → 10300/2 shown, `PuzSetAct(10391)`, play(10002); 10002 → `BagAdd` 10001,
  10002, `PlyCin(1543)`, `PuzSetAct(10392)`, play(10003); 10003 → 10391, 10004; 10004 →
  rotation 10301 at alpha 160, ran 85.7. 10005 → 10390, 10006 → 10392, 10007 → 10390, 10008
  → 10392, 10009 → `PlyCin(1544)`, `BagAdd(10305)`, score +5, 10305 hidden, /0 shown, acc
  off 10305. 10010 → 10391, 10011 → `PlyCin(1545)`, `BagAdd(10302)`, score +2, acc off
  10302, byte 10300 = 1, with the Helmet in the bag: Helmet&Frog as for 10503. 10012 →
  `PlyCin(1546)`, byte 10301 = 1, 10391, 10013. 10014 → `PlyCin(1547)`, `BagAdd(10303)`,
  score +5, 10303/0 shown, acc off 10303. 10015..10017 → 10392, play(10018 + rand() × 3 /
  32768). Ends of 10004, 10009, 10011, 10013, 10014, 10018..10021: `RotSetAct(10301)`.
  ("a → p, n" = `PuzSetAct(p)`, play(n).)
- Speaker: 10022 → 10202, 10023 → 10200, 10024 → 10202, 10025 → 10200, 10026 → acc on 10201
  #0 (the handle). 10027 → 10205, 10028 → 10203, 10029 → 10204, 10030 → 10203, 10031 →
  10204, 10032 → `PlyCin(1548)`, `PlyCin(1549)`, acc on 10200, `RotSetAct(10201)`, its
  movability 0 off.
- Message: 12001 → `PuzSetAct(12003)`, play(12003); 12003 → 12002, play(12002); 12002 →
  `PlyCin(1542)`, `PuzSetAct(10521)`.

## Game over (0x408db0(n))

Mode 4 (0x40b7b0), app+0x70 = n, stop all sounds (reason 0x40). The next frame (mode 4,
`spec/boot.md`) reloads the set-ups (0x408bc0, 0x431040) and calls 0x431190(2, n): `SetZone(1)`,
for n = 1..4 the picture `End.bmp` at (0, 16) for 4 s (0x401000("End.bmp", 0, 16, 4000, 2,
'e' or 'f')), then `StartMenu(0)` (E-0071). NI's causes: 1 water without the hologram, 2
water without Helmet&Frog, 3 riding from 10102 with the cross not at 12, 4 the heater above
120.

## Flow

1. Arrival (entry 0): the Mime welcomes Alberich (videos 1540, 1541, dialogue 10001..10004)
   and gives Glug and the Minerals; the player stands at 10301 with Brutality.
2. The Mime: Brutality on him gives the Tile once he asked for it (10012, then 10014); the
   Frog and Loge's Tear are taken from his table (10010..10011, 10005..10009).
3. Glug moves the car: call Glug at a stop (10003, 10201, 10401), put Glug down (`unk_19` 1),
   feed it the Minerals (2): the car comes to that stop and its way opens. The car rides the
   line 10000..10005.
4. The console (10101): the handle calls the car to 10005 (drag past 7); the Tile on its
   holder, the mosaic 5, 2, 3, 4, 1 (with cover 1 open), Brutality on the hologram, cover 2:
   the hologram puzzle 10102. Cross at 12 lets the ride 10102 → 10601 live (else game over
   3).
5. The tiles (10601): all three to 0 opens Erda's room 10501: the Helmet (with the Frog:
   Helmet&Frog), the AG cells, and the message to RH (10521).
6. The speaker (10201): its dialogue, then the handle pulled to the middle (4..10) plays the
   second dialogue.
7. Back on the console, the dam open and the cross at 0 set byte 10106 (the way past the
   door); the Tear in the casing (10411) and closed turns the heater on (byte 10431); both
   valves open keep it steady, one closed makes it boil (timer 0; game over at 120 s;
   opening a valve halves the heat).
8. The door (10404) to 10415, the water with Helmet&Frog to 10406, the water there: on to RH
   (`GoZone(3, 0)`). RH leads back here (entry 3, byte 10303; `rh.md`, E-0101).
9. With byte 10303 set, the heater steady (hologram, tear, both valves): after 11 s of timer
   1, `PlyCin(1539)` and AS's return 0x437750(1): NI is done (score 100).

## Needs (beyond the engine as of E-0059)

- The inventory: `BagAdd` / `BagRem` / `BagRemAll` / `BagIsIn`, the object in hand
  (0x406530 / 0x406550 / 0x406570), clicks with it, `ObjAddBagAni` icons.
- Puzzle animations (`ObjPreAddAniToPuz`, `ObjPreSetAniIdeOnPuz`) and their events;
  `ObjPrePauFraAni` (0x403ac0 → `aObject::ObjPrePauFraAni`: the pause-at-frame controls of
  `spec/animation.md`, not yet specified); ping-pong flags (32).
- `RotSetRolTo` (0x405c20 → the animated turn 0x4101c0), `RotSetFreOn/Off`, `RotSetJugOn`
  (10406), `RotSet3DSouOn/Off`, `PuzSetMovOnOrOff`, `RotSetMovOnOrOff` on, `PuzAddBgrImg` at
  run time, `ObjPreHidDeaPuz`, `SetCursorPos`.
- Word and dword variables; timers 0 and 1; the "on an accessibility" event (0x40ca80).
- Drawing frames from inside a handler (0x40f6c0) and `GetTickCount` waits; the drag state's
  reference point (0x4066b0) and the getters above (`spec/cursor.md` to extend).
- Game over (0x408db0, mode 4, 0x431190, the picture display 0x401000); `GoZone` to RH;
  the resume entry 10 (saves).
