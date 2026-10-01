# Zone WA (6): Walhalla — Wotan's world (Ring, DVD)

Evidence: E-0220..E-0225. Addresses are `RING_DVD.EXE`; the set-up (0x44ab00, extracted by
emulation, E-0094) is listed in `engines/ring/notes/zones/wa.md`, decompiles in
`engines/ring/notes/decomp/wa/`. Ids are decimal. Calls as in `ni.md` / `n2.md`: play(id, n)
0x406de0 (n = 1 once, 2 looping), stop(id, r) 0x406e00 (here always 0x400), 0x406ef0(id) =
the sound plays, `PlyCin(name)` 0x401490 (`DATA\WA\PLA\<name>.cnm`), `PlyCinMul` 0x4016a0
(`as.md`), `PuzSetAct` 0x402490, acc on (object) 0x403030 / (object, from, to) 0x403070, acc
off 0x403050 / `ObjSetAccOff` 0x403090, rotation movabilities on (rotation, from, to)
0x405830 / `RotSetMovOff` 0x405850, a puzzle's movabilities all off 0x404a60. "Show" /
"hide" are `ObjPreSho` / `ObjPreHid` (one presentation, or all with the one-argument forms).
"In hand" 0x406530, "held" 0x406550, "drop" 0x406570; "cancel" = app+0x74 cleared (the
take path, `spec/bag.md` "Taking"). "Frame" 0x40f6c0. Variables: byte 0x4060e0 / 0x4060b0,
word 0x406160 / 0x406130, dword 0x4061e0 / 0x4061b0, float 0x406260 / 0x406230.

"Score +n" is SY's float **90008** += n (WA's score; NI 90005, N2 90006, FO 90007): f32
[0x47e314] 1, [0x47e624] 2, [0x47e620] 3, [0x47e2e0] 5. The ending sets it to 100.0.

**Progress** (the same block at 0x437d60 ×3, 0x4392a0, 0x43a050): byte 50012 += 1; then at 2:
50700/0 shown, acc off 50700, on 50700 #1, rotation 50103's movability 2 off and 3 on; at
4: 50700/1 shown, acc off 50700, on #2.

## Places

- **50001** (`WAS00N01`, arrival) → 50101 (1883, two halves around 0°). Close-ups 50001,
  50002 (the arrival's dialogue).
- **The path** 50101..50108 (`WAS01N0x`), one after another (rides 1884..1904); side ways:
  50102 → 50201 (1888), 50103 → 50701 (1891; #3, the same without a ride video, disabled),
  50104 → 50301 (1894), 50105 → 50401 (1897), 50106 → 50501 (1900). 50108 holds the writing
  desk (object 50100's rotation accessibility → puzzle 50100).
- **50201 / 50202** (`WAS02N0x`, three layers each): 50202 has objects 50202 (four
  accessibilities) and 50203 (the sky part, #0).
- **50301..50304** (`WAS03N0x`): 50301 → 50302 (#1, 1909; #3 1911 disabled), → 50104; 50302 →
  50301 / 50303 / 50304 (#0..2 with videos 1912..1914, #3..5 the same with 1915..1917,
  disabled); 50303 → 50302 (#0 1918, #1 1919 disabled); 50304 → 50302 (no video). 50303:
  object 50300 (rotation #0 and puzzle 50303); 50304 (six layers): the Conch 50301.
- **50401 / 50402** (`WAS04N0x`): 50401 → 50105, → 50402 (#1 1921; #2 1922 disabled); 50402
  → 50401, → puzzle 50400 (#1, 1924: the golem) and puzzle 50401 (#2, disabled: the grid).
  50402's layer 1 is the Flower (50402).
- **50501 / 50502** (`WAS05N0x`, seven layers on 50502): the tree; 50502 holds the Sword
  (50501), the Apple (50502) and the four branches (object 50503 `unk_19` 10..13 → puzzles
  50501..50504).
- **50601 / 50602** (`WAS06N0x`): 50601 → 50108, → 50602, → puzzles 50601 (#3, the four
  switches) and 50602 (#4); 50602 → 50601; object 50601 on 50602 (three accessibilities).
- **50701** (`WAS07N01`): object 50700 (#0 on; #1, #2 off), puzzles 50701..50703 (the
  dialogue's faces) → 50103.
- Message puzzles 51001..51013 (`TR_WA_*`, the ending).
- Music (type 2, looping, one per area): 51006 the path, 51002 + 51012 at 50201, 51004
  (+ 51013 after 50300) at 50301, 51003 + 51010 at 50401, 51001 + 51011 at 50501, 51007 at
  50701; 51008 at the ending. Ambient 50017 on puzzle 50602.

## Variables

Bytes (all initial 0): 50001 the leaf task (1 the sword on 50202, 2 the conch on 50203, 3
done), 50003 50300 done (the beam), 50004 (declared only), 50005 the conch (1 lit, 2 freed,
3 taken), 50006 (declared only), 50007..50010 the four switches of puzzle 50601, 50011 the
letter's hold (1 while it waits for the ashes), 50012 progress (0..4; 5 the letter burnt;
6 the beam aligned). Word 50000 the tree (digits: 1 Flower, 10 Apple, 100 Leaf, 1000 Bark;
1111 done → 11111); words 50101..50105 the desk (101, 103, 102, 104 as each step is made).
Dword 50000 the golem (sum of the parts' values); dwords 51000..51077 the grid (51000 + slot
= the piece there). SY's float 90008 is the score.

## Objects

| Object | Where | What |
|---:|---|---|
| 50000 "Beam of light" | bag (entry 0) | used on 50300 and the Conch |
| 50400 "Golem" (`FO_Golem`) | bag (entry 0); puzzle 50400 #0; layer 0 of 50401 / 50402 (presentation 0) | |
| 50401 "Feather", 50201 "DeadLeaf", 50302 "Bark", 50402 "Flower", 50501 "Sword", 50502 "Apple", 50504 "Rope" | bag | |
| 50101 "Ink", 50102 "Paper", 50103 "Stylet", 50104 "Ink & Stylet" | puzzle 50100 (`unk_19` 0, 1, 2 / 8, 9), flags 8 | the desk |
| 50105 "Ashes" | puzzle 50100 (0) | |
| 50100 | rotation 50108 (0); puzzle 50100 pictures 0..6, animations 7 (id 50003, 50 frames, flags 6, start frame 1) and 8 (id 50004) | the desk |
| 50600 | puzzle 50601 #0..3 (the switches); animations 0 (id 50001, puzzle 50601) and 1 (id 50002, puzzle 50602), pictures 2..7 | |
| 50601 | rotation 50602 #0..2 | the Rope's place |
| 50431..50437 "Head front", "Head back", "Belly", "Arm right", "Arm left", "Legs", "Heart" | puzzle 50400: #0 on the golem (`unk_19` 0), #1 the socket (`unk_19` 1, 20, 300, 4000, 50000, 600000, 7000000), disabled; flags 8 | the golem's parts |
| 50451..50457 | puzzle 50401: #0 the column (x 125..160, 37 apart), #1..#49 the grid cells (`unk_19` 10 × column + row + 1), disabled except #0 of 50451..50456; flags 8 | the pieces (`WA_glava`, `droka`, `lroka`, `trup`, `lnoga`, `dnoga`, `srce`) |
| 50499 | puzzle 50401: 49 cells (x 162 + 53c, y 115 + 37r, `unk_19` 10c + r), flags 8 | the grid |
| 50500 | presentations 0..6 on 50501 / 50502 layers and puzzles 50501..50504 | the tree's items; 5 (the apple) shown at set-up |
| 50503 | puzzles 50501..50504 (`unk_19` 0..3), rotation 50502 (10..13) | the branches |
| 50202 | rotation 50202 (0..3) | |
| 50203 | rotation 50202 (0) | |
| 50300 | rotation 50303 (0), puzzle 50303 (0) | |
| 50301 "Conch" | rotation 50304 #0 (0), #1 (1, disabled), puzzle 50304 #0; layers 0..5 of 50304 | |
| 50700 | rotation 50701 #0..2 | the Norns |
| 51000 | puzzles 51001..51013 (animations, never shown: Q-0070) | |

## Entering (`GameSetZoneWA` 0x43ad50, entry)

AS enters through 0x43ad00(0): `GoZone(6, 0)` while SY's byte 90012 is 0, else
`GoZone(dword 90016, 10)` (E-0091).

- **0**: `BagRemAll`, `BagAdd` 50000 (the Beam), 50400 (the Golem), `PlyCin(1880)`,
  `PlyCin(1881)`, rotation 50001 alpha 320, `RotSetAct(50001)`, `PuzSetAct(50002)`,
  play(50001): the arrival (sound chain below).
- **10** (resumed after Erda): needs `<install>Data\Save\bru.ars` (0x47bd10; else the log
  "Wrong Erda AS - WA -> Can not find file" and nothing); `BagRemAll`; byte 90020 = 0:
  `RotSetAct(dword 90024)` and `RotSetFreOn` / `Off` by byte 90028; else `PuzSetAct(dword
  90024)`; then `LoadSaveTimer("bru", 1)` (failing: logged, stop) and 0x4696f0 (`spec/bag.md`).
- **999**: `BagAdd` 50000, 50504, 50400, 50501, 50402, 50502, 50201, 50302; float 90008 =
  90.0; object 1 shown (all); byte 50012 = 4; `PuzSetAct(50100)`. No caller (Q-0072).

## Handlers

**Object click (0x437d60, object, `unk_19`)** (the place id is not read). Objects not listed
do nothing, even with an object in hand.

- 50100 (the desk, at 50108): in hand: drop. Byte 50012 = 4: `RotSetRolTo(50108, 250, 15,
  85.7)`, `PlyCin(1849)`, `PuzSetAct(50100)`, stop 51006. Byte 50012 > 4: `PlyCin(1850)`,
  rotation 50601 alpha 250, `RotSetAct(50601)`, stop 51006.
- 50105 the Ashes: in hand: drop. Byte 50011 = 1 (the letter waits):
  `ObjPrePauFraAni(50100, 8, 50, 1000, 2)`, byte 50012 = 5, score +3, 50100/8 shown, /7
  hidden.
- 50202: in hand: held Sword: `PlyCin(1855)`, score +5, 50202/0 shown, byte 50001 = 1, acc off
  50202; drop.
- 50203: in hand: held Conch: without the Feather in the bag `PlyCin(1859)`; with it
  `PlyCin(1856)` and, when byte 50001 = 1: 50202/0 hidden, /1 shown, byte 50001 = 2,
  `PlyCin(1857)`, score +5, acc off 50203, and when byte 50003 = 1 also: /1 hidden, /2 shown,
  byte 50001 = 3, `PlyCin(1858)`, `BagAdd(50201)` (the Leaf), score +5, **progress**. Drop.
- 50300: nothing in hand: `PuzSetAct(50303)`. Held Beam: 50300/0 shown, acc off 50300, acc on
  50302 (the Bark), byte 50003 = 1, score +5, play(51013, loop), rotation movabilities: 50301
  #0..1 off, #2..3 on; 50302 #0..2 off, #3..5 on; 50303 #0 off, #1 on (the same ways with
  other videos); byte 50005 < 2: 50301/3 shown, else 50301 hidden, /1 shown and, at 3, /2;
  50300/0 shown, `PlyCin(1854)`, **progress**. Any held: then `RotSetAct(50303)`, drop.
- 50301 the Conch. In hand: held Beam and byte 50005 = 0: 50301/0 shown, byte 50005 = 1,
  `PlyCin(1852)`, rotation 50304 alpha 190, beta 15, `RotSetAct`. Held Sword and byte 50005 =
  1: `BagRem(50501)`, `RotSetRolTo(50304, 145, 9, 85.7)`, byte 50005 = 2, score +5, 50304's
  movability 0 off, 1 on, acc on 50301 #1, 50301 hidden, a frame, `PlyCin(1853)`, rotation
  50304 alpha 190, beta 15, `RotSetAct`, 50301/1 shown, and /4 when byte 50003 = 0. Drop.
  Nothing in hand: `unk_19` 1 and byte 50005 = 2: byte 50005 = 3, 50301/2 shown, score +5,
  acc off 50301 #1, `BagAdd(50301)`. `unk_19` 0: byte 50005 < 2: `PuzSetAct(50304)`; else
  50301/5 shown, acc off 50301 #0, `BagAdd(50501)` (the Sword back).
- 50302 the Bark (flags 9): nothing in hand: `BagAdd(50302)`, score +5, acc off 50302 (it
  also goes in hand); in hand: drop.
- 50400 the Golem (puzzle 50400): held Golem, `unk_19` 0: `BagRem(50400)`, 50400/1 shown,
  50431..50437/0 shown, acc on 50431..50436 (all), 50437 #1, acc off 50400 #0, puzzle
  50400's movabilities off (the way out closes until the golem is done), score +2; drop.
- 50402 the Flower (flags 9), 50501 the Sword, 50502 the Apple: nothing in hand:
  `BagAdd(object)`, acc off it, and: Flower 50402 hidden (all), score +2; Sword score +2,
  50500/0 shown; Apple 50500/5 hidden, score +3. In hand: drop.
- 50503 the branches. `unk_19` 10..13, nothing in hand: `PuzSetAct(unk_19 + 50491)`
  (50501..50504). `unk_19` 0..3, nothing in hand: takes the item back when word 50000 says it
  is there (as coded: 0 when `word % 10 == 1`, 1 when `word % 100 ≥ 2`, 2 when `word % 1000 ≥
  12`, 3 when `word % 10000 ≥ 112`, Q-0071): `BagAdd` the Flower / Apple / Leaf / Bark,
  50500/(`unk_19` + 1) hidden, word − 1 / 10 / 100 / 1000, score −2. In hand: held Flower with
  0 / Apple with 1 / Leaf with 2 / Bark with 3: `BagRem`, 50500/(`unk_19` + 1) shown, word +
  1 / 10 / 100 / 1000, score +2; then (any held) when word 50000 = 1111: word = 11111,
  50500/6 shown, a frame, `PlyCin(1851)`, `RotSetAct(50502)`, `BagAdd(50504)` (the Rope),
  score +3, **progress**; drop.
- 50600 (the switches, puzzle 50601) `unk_19` n = 0..3: in hand: drop. Else play(50018),
  `ObjPreUnPauAni(50600, 0)`, 50600/6, /7 hidden, /1 shown; byte 50007 + n toggled, with
  50600/(2 + n) shown when it becomes 1, hidden when 0.
- 50601 (at 50602): in hand: held Rope and byte 50012 = 6: `BagRem(50504)`, float 90008 =
  100.0, `PlyCin(1860)`, `PlyCin(1861)`, `PlyCinMul(1863 for languages 4, 5, 7; 1864 for 6;
  else 1862)`, `PuzSetAct(51001)`, play(50021): **the ending**. Drop.
- 50700 (the Norns): nothing in hand: `PuzSetAct(50701)`, score +5, play(50009); in hand:
  drop.

**Take (0x4392a0, object, `unk_19`)**: raised for flag-8 objects after the click; unless
said, it ends with cancel (the clicked object does not go in hand) and drops what is held.

- The desk, objects 50101..50104 (`unk_19` 0..2 Ink, Paper, Stylet; 9 Ink & Stylet's place; 8
  the Stylet's second place):
  - nothing in hand: `unk_19` < 3 and the object not in the bag: `BagAdd(object)`,
    50100/`unk_19` hidden (taken: no cancel). `unk_19` 9, word 50102 > 0 and 50104 not in the
    bag: 50100/6 hidden, `BagAdd(50104)` (taken). Otherwise cancel.
  - in hand, `unk_19` < 3 and held = the object: `BagRem`, 50100/`unk_19` shown (put back).
  - `unk_19` 9: held Ink and word 50101 = 0: 50100/4 shown, `BagRem`, acc off 50101 #0, word
    50101 = 101. Held Stylet and word 50101 > 0: 50100/4 hidden, /6 shown, acc off 50103 #0,
    `BagRem`, word 50102 = 103.
  - `unk_19` 8: held Paper: 50100/3 shown, `BagRem`, acc off 50102 #0, word 50103 = 102.
    Held Ink & Stylet and word 50103 > 0: 50100/5 shown, `BagRem`, word 50105 = 104,
    `ObjPrePauFraAni(50100, 7, 30, 10000, 2)`, 50100/7 shown (the letter, id 50003), score +5.
- The golem's parts 50431..50437: nothing in hand, `unk_19` 0, not in the bag: object/0
  hidden, `BagAdd` (taken); otherwise cancel. In hand, held = the object and `unk_19` ≥ 1 (its
  socket): object/1 shown, acc off object #0..1, score +1, dword 50000 += `unk_19`; at
  7654321 (all seven): `PlyCin(1865)`, `PlyCin(1866)`, rotation 50401 movability 1 off, 2
  on, 50402 movability 1 off, 2 on (the grid opens), 50400/0 shown (the golem on the
  rotations), rotation 50402 alpha 180, beta 0.3, `RotSetAct`; at 654321 (all but the heart):
  acc on 50437 (all). Held another part: held/0 shown (back on the golem). Then `BagRem(held)`.
- The grid (50499, `unk_19` v = 10 × column + row) with a piece 50451..50457 in hand: the
  piece's pictures moved to (162 + 53 × column, 115 + 37 × row)
  (`ObjPreSetImgCooOnPuz(held, 0, x, y)` 0x4037c0), dword 51000 + v = held, acc on held #(i +
  1), acc off 50499 #i (i = 7 × row + column), held shown, score +1 for each right piece in
  its cell (50451 at 30, 50452 at 61, 50453 at 1, 50454 at 33, 50455 at 26, 50456 at 46, 50457
  at 42), `BagRem(held)`. With the first six right: acc on 50457 #0; with the seventh too:
  `PlyCin(1867)`, rotation 50402's movability 2 off, `BagAdd(50401)` (the Feather), score
  +2, rotation 50402 alpha 180, beta 0.3, `RotSetAct`, **progress**.
- A piece 50451..50457 clicked: nothing in hand, `unk_19` 0 (the column): hidden,
  `BagAdd`, acc off #0 (taken). `unk_19` ≥ 1 (in the grid at cell `unk_19` − 1): score −1 if
  it was right there, dword 51000 + cell = 0, acc off the piece's cell, acc on 50499's cell,
  hidden, `BagAdd` (taken). In hand a piece, clicking the column or a filled cell: the held
  piece back to its declared place (`ObjPreSetImgOriCooOnPuz(held, 0)` 0x403810), acc on held
  #0, shown, `BagRem`.

**Before a movability (0x439f40, from, to, …, kind)**, kind 0 only: 50001 → 50101: play(51006,
loop) when it does not play. 50304 → 50302: byte 50003 ≠ 0: `PlyCin(1870)` (byte 50005 < 2)
or 1871; else 1868 or 1869. 50103 → 50701: stop 51006, play(51007, loop).

**After a movability (0x43a050, to, from, …, kind)**, kind 0 only, the music by area:
to 50201 from 50102: stop 51006, play 51002, 51012 (loop); to 50201 (any): byte 50001 = 2
and byte 50003 = 1: the leaf as at 50203 (50202/1 hidden, /2 shown, byte 50001 = 3,
`PlyCin(1858)`, `BagAdd(50201)`, score +5, **progress**). To 50102 from 50201: stop 51002,
51012, play 51006. To 50301 from 50104: stop 51006, play 51004, and 51013 when byte 50003 >
0. To 50104 from 50301: stop 51004, 51013, play 51006. To 50401 from 50105: stop 51006, play
51003, 51010; back: stop them, play 51006. To 50501 from 50106: stop 51006, play 51001,
51011; back: stop them, play 51006. To 50103 from 50701: stop 51007, play 51006. To 50108 from
50601: play 51006.

**Animation (0x43a400, id, name, frame)**: 50001 (the switches' wheel, 50600/0), by the
switches (bytes 50007..50010 = s0..s3) and the frame:

- s0 and s2, frame 35 or 12; s1 and s3, frame 49 or 24: `ObjPrePauAni(50600, 0)`, 50600/1
  and /6 hidden, /7 hidden (s0 s2) or shown (s1 s3), stop 50018; when byte 50012 = 6: score −5,
  byte 50012 = 5.
- s1 and s2, frame 17 or 41; s0 and s3, frame 4 or 30: `ObjPrePauAni(50600, 0)`, 50600/1 and
  /7 hidden, /6 shown, stop 50018, byte 50012 = 6, score +5: **the beam aligned**.

**Hold on a frame (0x43a6f0, phase, id)** (the event 0x40c910 of `spec/animation.md`
"Pausing on a frame", WA only, E-0224):

- id 50003 (the letter): phase 1 (the hold starts): byte 50011 = 1. Phase 2 (10 s passed,
  no ashes): byte 50011 = 0, 50100/3..6 hidden, /0..2 shown, words 50101..50105 = 0, acc on
  50101..50104 (all): the desk is reset.
- id 50004 (the ashes), phase 2: 50100 hidden (all), rotation 50601 alpha 250,
  `RotSetAct(50601)`, `PlyCin(1872)`.

**Sound (0x43a860, id, type, reason, ended)**, natural ends only ("a → p, n" =
`PuzSetAct(p)`, play(n)):

- The arrival: 50001 → 50001, 50002; 50002 → `RotSetAct(50001)`, play(50003); 50003 →
  play(51006, loop).
- The Norns: 50009 → 50703, 50010; 50010 → 50702, 50011; 50011 → 50703, 50012; 50012 →
  50701, 50013; 50013 → 50703, 50014; 50014 → 50702, 50015; 50015 → 50703, 50016; 50016 → acc
  off 50700, `RotSetAct(50701)`.
- The ending: 50021 → `PlyCinMul(1873 for languages 4, 5, 7; 1874 for 6; else 1875)`, 51002,
  50022; 50022 → `PlyCinMul(1876 / 1877 / 1878 likewise)`, `PuzSetAct(51003)`, play(51008,
  loop), play(50026); 50026 → 51004, 50027; 50027 → 51005, 50028; … 50035 → 51013, 50036;
  50036 → `PlyCin(1879)`, `TimStoAll`, stop all (0x400), AS's 0x437750(4): **back to the hub,
  world 4 done**.

WA handles no timer, button-down, drag, on-accessibility or list-click event (`spec/events.md`).

## Game overs

None.

## Flow

1. Arrival (entry 0): the Beam and the Golem in the bag; videos 1880, 1881 and a dialogue
   (50001..50003) at 50001; the path 50101..50108 with its side ways.
2. Four tasks, each counted by byte 50012 (**progress**; at 2 and 4 the Norns at 50701 have
   something new to say: 50700 → dialogue 50009..50016):
   - **50300** (at 50303): the Beam on it: the Bark becomes takeable (50302), score +5.
   - **The golem** (50402 → puzzle 50400): the Golem put down, its seven parts taken off and
     put in their sockets (the heart last) → the grid (puzzle 50401): the seven pieces in
     their cells (head at column 3 row 0, right arm 6/1, left arm 0/1, body 3/3, left leg 2/6,
     right leg 4/6, heart 4/2) → the Feather.
   - **The leaf** (50202): the Conch (50304: the Beam lights it, the Sword from the tree frees
     it, it is taken) — the Sword on 50202, the Conch on 50203 with the Feather in the bag, and
     the 50300 task done → the Leaf.
   - **The tree** (50502): the Flower (50402), the Apple, the Leaf and the Bark put on the four
     branches (puzzles 50501..50504) → the Rope.
3. Progress 4: the desk at 50108 (puzzle 50100): Ink, Paper and Stylet taken; Ink then Stylet
   on the inkwell make Ink & Stylet; the Paper and then Ink & Stylet on the paper's place
   write the letter (animation 7 holds 10 s on frame 30); the Ashes clicked during the hold
   burn it (byte 50012 = 5) and lead to 50601 (video 1872); otherwise the desk resets.
4. 50601's switches (puzzle 50601): two switches set (s1 s2 or s0 s3) make the wheel stop with
   the beam aligned (byte 50012 = 6); the other pairs stop it wrong.
5. The Rope used at 50602 (object 50601) with the beam aligned: the ending (videos 1860..1864,
   the message puzzles 51001..51013 with sounds 50021..50036, video 1879) and AS's return
   0x437750(4) (score 100).

## Needs (beyond the engine as of the NI / RH / N2 / FO work)

- The hold-on-frame event 0x40c910 (phase 1 at the hold's start, 2 at its end, with the
  animation id) to the zone: WA's 0x43a6f0 (E-0224 corrects E-0092, which said only RO).
- `ObjPreSetImgCooOnPuz(object, presentation, x, y)` (0x4037c0 → 0x42eba0: every picture of
  the presentation moved) and `ObjPreSetImgOriCooOnPuz(object, presentation)` (0x403810 →
  0x42ebf0: back to the declared place) while playing.
- `ObjPreAniSetStaFra` in the set-up (50100/7 start frame 1; the engine skips it).
- `RotSetBet` while playing (the zone sets beta: the `rot` helper covers it); score float
  90008.
- The message animations 51000 and the arrival's 50001 are declared but never shown (Q-0070).
