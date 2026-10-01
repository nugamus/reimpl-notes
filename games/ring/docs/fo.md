# Zone FO (4): the Forest — Siegmund's world (Ring, DVD)

Evidence: E-0160..E-0166. Addresses are `RING_DVD.EXE`; the set-up (0x44f3e0, loops
unrolled by emulation, E-0094) is listed in `engines/ring/notes/zones/fo.md`, decompiles in
`engines/ring/notes/decomp/fo/`. Ids are decimal. Calls as in `ni.md`: play(id, n) 0x406de0
(n = 1 once, 2 looping), stop(id, r) 0x406e00, volume(id, v) 0x406e20, pan(id, p) 0x406ec0,
`PlyCin(name)` 0x401490 (`DATA\FO\PLA\<name>.cnm`), `PuzSetAct` 0x402490, acc on (object,
from, to) 0x403070, acc off all 0x403050 / `ObjSetAccOff` 0x403090. "Show" / "hide" are
`ObjPreSho` / `ObjPreHid` (one presentation, or all with the one-argument forms 0x403e00 /
0x403e80). **Timers:** `TimSta(id, ms)` is 0x4065a0, `TimSto(id)` 0x4065e0 (Ghidra names
both `TimSta`; the stop takes one argument, E-0057); "restart t at ms" = `TimSto(t)` then
`TimSta(t, ms)`. "In hand" is 0x406530, "held" 0x406550, "drop" 0x406570. **Score**: FO's is
SY's float **90007** (not NI's 90005): "+n" adds the f64 constants [0x47e660] 1.1, [0x47e648]
2.2, [0x47e670] 3.3, [0x47e680] 4.0, [0x47e658] 4.4, [0x47e678] 5.5, [0x47e668] 6.6,
[0x47e650] 9.9; "(first)" means guarded by a byte set on the first time. rand(n) is
`rand() × n / 32768`. FO has **no game over** (no call to 0x408db0).

## Places

- **The forest** 30001..30012 (`FOS00N0x`): 30001..30004 the clearing (30004 also to the
  sword puzzle 35019, mov 5), 30005/30006/30008 the path to the wolves' hall 30301, 30009..
  30012 the way to the fire 30011 and 30501; 30003 has the hare (object 30025, animated layer)
  and the door to Sieglinde (30025 #1).
- **The wolves' hall** 30301 (`FOS03N01`): seven pedestals 30002..30008 for the scrolls, seven
  lamps 30200, the wolf statue puzzle 35011 (mov 1); **30302 / 30303** the same room seen
  normally / with the Wolf Vision (30303 → the dial puzzle 35001).
- **Sieglinde's hut** 30101 (`FOS01N01`): Sieglinde (object 30102, `unk_19` 1), her
  close-ups 35103..35111 (a dialogue of pictures), the door puzzles 35100 / 35101 outside
  (from 30003).
- **The fire** 30011 (object 30051: the fire, the bow) and 30401/30402/30801 (berries puzzle
  35002 at 30801), 30501 (object 30050, the tree; to 30601).
- **The smithy** 30601/30602 (`FOS06N0x`): puzzles 35003 (the hunter's wall: hares, bow),
  35004 (the furnace), 35005 (the press), 35006 (the mine: pan, ingots), 35007 (the mold,
  seven metals), 35008 (the golem), 35009 (the bells, from 30602's object 30045 #7).
- **The lake** 30701..30704: fishing puzzle 35010 (from 30703), worms puzzle 35020 (from
  30704).
- Rotations with a layer of object 30061 (30001, 30010, 30301, 30008, 30009, 30702, 30703):
  the lightning (timer 0).

## Variables

Bytes (0 unless said): 30009..30015 the pedestals' scrolls (initial 2, 1, 3, 4, 5, 6, 7; 0
empty, k = scroll 30008 + k), 30016 the dial (initial 25, 0..48), 30017 the Wolf Vision on,
30019 furnace lit, 30020 pan on the furnace, 30021 tear in the furnace, 30022 / 30023 mine
doors open, 30024 pan taken, 30025..30031 the mold's slots of Gold, Silver, Copper, Lead,
Steel, Tin, Mercury, 30032 golem made, 30033 pole out, 30034 fire arrow shot, 30035 dial
solved, 30036, 30037 arrived at 30501 from 30402, 30038 worms on the pole, 30039, 30040..30042
panels placed, 30043 medallion taken, 30047 bells ride, 30049 + k hares/bow taken (30050..
30055), 30056 (initial 1) the door may be knocked, 30060..30064 the press, 30066 / 30067 the
wolf / Sieglinde's medallion on the sword, 30069 (initial 1), 30070 pole puzzle state, 30071
first time at 30501, 30072 Sieglinde given the poison, 30073 lightning state, 30074 hut
visited, 30075 / 30076 berries taken, 30077 hare given, 30078, 30201..30211 the scores'
first-time guards. Floats 30046 (−10), 30042 (1): never read here.

## Objects

| Object | Where | What |
|---:|---|---|
| 30001 | puzzle 35011 #0..4 (#1..4 off) | the wolf statue: #0 the lock (fish key), #1..3 the panels' places, #4 the medallion |
| 30002..30008 | rotation 30301, one accessibility each | the pedestals |
| 30009..30015 "Saturn, Mercury, Venus, Moon, Mars, Jupiter, Sun" | bag | the scrolls |
| 30016 | puzzle 35001 (drag, flags 4), presentations 0..48 | the dial |
| 30017 "Berries" | puzzles 35002 #0..4, 35005 #5 | the bushes (#0, #4 poison) and the press (#5) |
| 30018 "Poison berries", 30031 / 30032 the juices | bag | |
| 30019 "Wolf Vision" | bag (start) | used through the bag click (below) |
| 30020 "Rabbit hare", 30026 "Hunting bow" | puzzle 35003 #0..6 (30026) | the hunter's wall |
| 30021..30023 "Panel" | bag | for the wolf statue |
| 30025 | rotation 30003 #0 (the hare, layer 0, anim id 30006), #1 (the door) | |
| 30027 | puzzle 35001 | the dial's centre |
| 30028 | puzzle 35004 #0..1 | the furnace |
| 30029 "Pan", 30041 "Ignots", 30033..30039 the metals | bag | |
| 30030 "Loge's Tear" | bag (start) | the furnace's fire |
| 30040 | puzzle 35006 #0..5 | the mine (anim id 30008 on /4) |
| 30042 | puzzle 35007 #0..7 | the mold |
| 30043 "Golem" | bag | |
| 30044 | puzzle 35008 #0..1 | the golem's place |
| 30045 | puzzle 35009 #0..6, rotation 30602 #7 (anim id 30000) | the bells |
| 30046 "Fishing pole", 30047 "…and worms", 30048 "Fish", 30054 "Key form the fish", 30049 "Worms" | puzzle 35010 / rotation 30703 (30046), puzzle 35020 (30049) | |
| 30050 | rotation 30501 (anim id 30009) | the tree |
| 30051 | rotation 30011 #0..3 | the fire; 30053 "Inflamed arrow and bow" |
| 30055 "Medallion", 30056 "Sieglinde's Medallion" | bag | |
| 30058 "Sword Notung" | puzzle 35019 #0 (off) | the end |
| 30059 | rotations 30302, 30303 | |
| 30061 | layer 0 of seven rotations | the lightning |
| 30100 | puzzle 35100 #0 (door), #1 (off) | |
| 30102 | rotation 30101 #1 | Sieglinde |
| 30108 | puzzle 35109 | Sieglinde's cup |
| 30109 | puzzle 35111 (anim id 30007, 202 frames) | |
| 30110 | rotation 30101 layers (presentations 0..3; anim id 30001 on /1) | |
| 30200 | rotation 30301 #0..6 | the lamps |
| 6 (SY's) | puzzle 1, presentations 0..26 (`FO_WOT*` / `FO_BRU*` pictures) | the ending's words |

## Entering (`GameSetZoneFO` 0x443760, entry)

AS enters through 0x443710(0): `GoZone(4, 0)` while SY's byte 90011 is 0, else
`GoZone(dword 90015, 10)` (E-0091; FO is SY's world 3).

- **0**: `BagRemAll`, `BagAdd(30030)` (Loge's Tear); timers 0 (5000 ms), 1 (3000), 2 (5000),
  3 (17000), 4 (10000), 5 (10); `BagAdd(30019)` (the Wolf Vision); `PlyCin(1217)`,
  `PlyCin(1218)`; rotation 30003 at alpha 180, `RotSetAct`.
- **10** (resumed after Erda): needs `<install>Data\Save\sie.ars` (0x47bd10; else the log
  "Wrong Erda AS / FO" and nothing); `BagRemAll`; byte 90019 = 0: `RotSetAct(dword 90023)`,
  then `RotSetFreOn` / `Off(dword 90023)` by byte 90027; else `PuzSetAct(dword 90023)`;
  `LoadSaveTimer("sie", 1)` (failing: logged, stop) and 0x4696f0 (the saved sounds).
- **999**: `BagAdd` 30019, 30054, 30021, 30022, 30023, `PuzSetAct(35011)`. No caller found
  (Q-0050).

## Handlers

**Object click (0x43dac0, object, `unk_19`)**. Unlike NI and RH, an object in hand is
**not** dropped for objects the handler does not list (only the branches saying "drop" do).

- **30001** (wolf statue, 35011). Nothing in hand: `unk_19` 4 only: `BagAdd(30055)`, 30001/4
  hidden, acc off #4, score +4.0, byte 30043 = 1. In hand: held Key form the fish (30054) at
  #0: /0 shown, acc off #0, on #1..3; with bytes 30040..30042 all 1: /4 shown, acc on #4;
  else for each placed panel k (byte 30039 + k): /k shown, acc off #k. Held a Panel (30021..
  30023) at #k (1..3): byte 30039 + k = 1, /k shown, acc off #k, `BagRem(held)`; when all
  three are placed: `PlyCin(1167)`, /1..3 hidden, /4 shown, acc on #4, acc on 30025 #1 (the
  door). Drop (any object).
- **30002..30008** (pedestal k = 1..7 of 30301, slot byte 30008 + k). Nothing in hand: slot ≠
  0: `BagAdd(slot + 30008)`, `PlyCin(1171)`, play(30109 + k), slot = 0. Held a scroll
  (30009..30015): slot 0: slot = the scroll's number (scroll − 30008), `BagRem`,
  `PlyCin(1168)`; else `PlyCin(1169)`. Then (any object in hand) when the slots read 1..7 in
  order: acc off all of 30002..30008, `PlyCin(1170)`, score +5.5, `RotSetAct(30302)`, timers
  1 and 3 stopped. Drop.
- **30017** (berries, 35002 / the press 35005). In hand, `unk_19` 5: held Poison berries and
  byte 30060 = 0: `BagRem`, byte 30063 = 1, /4 shown; held Berries and byte 30063 = 0:
  `BagRem`, byte 30060 = 1, /4 shown; drop. Nothing in hand: `unk_19` 1..3: `BagAdd(30017)`;
  byte 30017 (Wolf Vision) = 1 and `unk_19` 0 or 4: `BagAdd(30018)`, score +3.3 (first),
  /3 hidden, byte 30075 = 1, acc off #0, `BagAdd(30022)` (a Panel), score +3.3, /0 and /2
  hidden, byte 30076 = 1. `unk_19` 5 (the press): neither juice started: `PlyCin(1173)`;
  byte 30060 and not 30061: `PlyCin(1174)`, byte 30061 = 1, /4 hidden, /5 shown; both:
  `BagAdd(30031)`, /5 hidden, bytes 30060, 30061 = 0; byte 30063 and not 30064:
  `PlyCin(1175)`, byte 30064 = 1, /4 hidden, /5 shown; both: `BagAdd(30032)`, score +6.6
  (first), /5 hidden, bytes 30063, 30064 = 0.
- **30025** (rotation 30003). In hand: held Rabbit hare at #0: `BagRem`, acc off #0,
  `PlyCin(1176)`, timer 2 stopped, stop(30501, 0x400); byte 30077 = 0: `PlyCin(1177)`,
  `BagAdd(30023)`, score +5.5, byte 30077 = 1. Drop. Nothing in hand: `unk_19` 0:
  `PlyCin(1178)`. `unk_19` 1: byte 30074 ≠ 0: `PlyCin(1179)`, `RotSetAct(30101)`, alpha 130,
  beta 20 (set after the `RotSetAct`); else byte 30056 ≠ 0: `PuzSetAct(35100)`; else
  `PlyCin(1178)`.
- **30026** (35003). In hand: drop. `unk_19` 0: play(30511), all shown, acc off #0, then
  /k hidden for each byte 30049 + k set (k = 1..6). `unk_19` k = 1..6: play(30512), /k
  hidden, acc off #k, byte 30049 + k = 1; k < 5: `BagAdd(30020)`, score +1.1 (first); k = 5
  or 6: `BagAdd(30026)`, score +1.1, /5, /6 hidden, acc off #5..6, bytes 30054, 30055 = 1.
- **30027** (the dial's centre, 35001), nothing in hand and byte 30016 = 0: `PlyCin(1172)`,
  score +3.3, own volume 90 for sounds 30300..30326, byte 30017 = 0, byte 30035 = 1, 30402's
  movability 2 on (0x405830), 30050/0 and /2 shown, `RotSetAct(30501)`, alpha 88, beta 13,
  acc off all of 30002..30008.
- **30028** (the furnace, 35004). In hand at #1: held the Tear: byte 30019 = 0:
  `PlyCin(1180)`; else `PlyCin(1181)`, `BagRem(30030)`, byte 30021 = 1, and when byte 30020 =
  0: /0 hidden, /1 shown. Held the Pan with bytes 30019 and 30021 set: /0 hidden, /2 shown,
  byte 30020 = 1, `BagRem(30029)`. Held the Ignots with byte 30020: `BagRem(30041)`, `BagAdd`
  30033..30039 and 30030, score +4.4 (first), `BagAdd(30029)`, `PlyCin(1182)`, 30028 and /3
  hidden, bytes 30019..30021 = 0, acc on #0. Drop. Nothing in hand: `unk_19` 0 with byte 30020
  = 0: `PlyCin(1183)`, /0 and /3 shown, byte 30019 = 1, acc off #0. `unk_19` 1: byte 30021 and
  not 30020: `PlyCin(1184)`, hidden, /0 shown, byte 30021 = 0, `BagAdd(30030)`; bytes 30021
  and 30020: /2 hidden, /1 shown, byte 30020 = 0, `BagAdd(30029)`, score +1.1.
- **30040** (the mine, 35006), nothing in hand; each move plays 30508 after the accessibility
  changes: `unk_19` 0 with byte 30022 = 0: byte 30024 = 0: /1 shown, acc on #4; else /0 shown;
  byte 30022 = 1, acc off #0, #1, on #2. `unk_19` 1 with byte 30023 = 0: /2 shown, byte 30023
  = 1, acc off #0, #1, on #3, on #5. `unk_19` 2 with byte 30022 = 1: /0, /1 hidden, byte 30022
  = 0, acc off #2, #4, on #1, on #0. `unk_19` 3 with byte 30023 = 1: /2 hidden, byte 30023 =
  0, acc off #3, #5, on #0, on #1. `unk_19` 4: `BagAdd(30029)`, /0 shown, /1 hidden, acc off
  #4, byte 30024 = 1 (no sound). `unk_19` 5: `BagAdd(30041)`, score +1.1 (first), acc off #5,
  #3, /4 shown (the animation id 30008).
- **30042** (the mold, 35007). In hand at #k (1..7): play(30509); held metal m (30033..30039):
  byte 30025 + (m − 30033) = k, `BagRem(m)`, /k shown, acc off #k. Then with the slots Gold
  1, Silver 2, Copper 3, Lead 4, Steel 5, Tin 6, Mercury 7: hidden, score +9.9, byte 30032 =
  1, `PlyCin(1185)`, `BagAdd(30043)`, `RotSetAct(30601)`, acc off all, drop. All seven filled
  otherwise: hidden, `PlyCin(1186)`, `RotSetAct(30601)`, acc on #0, the slots 0 (the metals
  stay used up). Drop. Nothing in hand, `unk_19` 0: byte 30019 ≠ 0: /0 shown, /8 hidden,
  30028/0 and /3 hidden, byte 30019 = 0, acc on #1..7, off #0, acc on 30028 #0,
  `PlyCin(1187)`; else /8 shown, /0 hidden, acc off #0, play(30508).
- **30044** (the golem's place, 35008). In hand: held Golem: #0: shown, acc off #0, on #1,
  `BagRem(30043)`, `PlyCin(1188)`; #1: shown. Held Poison berries juice at #1: hidden, acc off
  #1, `BagAdd(30043)`, `BagAdd(30021)`, `PlyCin(1189)`, 30601's movability 9 off, acc off
  all, score +3.3. Drop.
- **30045** (the bells), nothing in hand: `unk_19` k = 0..6: hidden, /k shown, play(30150,
  30151, 30154, 30152, 30155, 30156, 30153 for k = 0..6); `unk_19` 7 (rotation 30602):
  play(30201), byte 30047 = 1, `RotSetRolTo(30602, 175, −23, 85.3)`.
- **30046** (fishing). In hand at #3 (rotation 30703): held pole and worms: byte 30034 = 0:
  `BagAdd(30048)`, score +2.2 (first), `PlyCin(1190)`; else `BagAdd(30054)`, score +5.5,
  `PlyCin(1191)`; then `BagAdd(30046)`, `BagRem(30047)`, byte 30038 = 0. Held the pole:
  `PlyCin(1192)`. Drop. Nothing in hand: `unk_19` 0: play(30508); byte 30033 = 0: /0 hidden,
  /1 shown, acc off #0, on #1..2; else /0 shown, /1 hidden, acc off #0..1, on #2; byte 30070
  = 1. `unk_19` 1: /1 hidden, /0 shown, acc off #0..1, byte 30033 = 1, and byte 30038 ≠ 0:
  `BagAdd(30047)`, score +6.6 (first), `BagRem(30049)`; else `BagAdd(30046)`. `unk_19` 2:
  play(30511); byte 30070 ≠ 0: hidden, acc on #0, off #1..2, byte 30070 = 0; else /0 (byte
  30033) or /1 shown, byte 30070 = 0.
- **30049** (the worms, 35020), held the Golem and byte 30038 = 0: byte 30033 = 0:
  `BagAdd(30049)`, score +2.2 (first); else `BagAdd(30047)`, score +6.6 (first),
  `BagRem(30046)`; `PlyCin(1193)`, byte 30038 = 1; then byte 30076 = 0: `BagAdd(30022)`,
  `BagAdd(30018)`, score +3.3 twice, bytes 30076, 30039 = 1, `PlyCin(1194)`, 30049/0, /1,
  30017/0 hidden, acc off all 30049, drop. Drop in the other cases with an object in hand.
- **30050** (the tree, 30501), nothing in hand: byte 30035 = 0: /1 shown, play(30514).
  Bytes 30035 and 30037 = 1: `PlyCin(1195)`, score +4.4, 30051/2 shown, 30050 hidden, bytes
  30035 = 0, 30036 = 1, 30037 = 0, 30402's movability 2 off, 30011's movability 1 off.
- **30051** (the fire, 30011). In hand: `unk_19` 1 or 2 with the bow: `BagAdd(30053)`, score
  +4.4 (first), `BagRem(30026)`. `unk_19` 0: held 30053: `BagRem`, `BagAdd(30026)`, byte
  30034 = 1, `PlyCin(1196)`, score +5.5, /2 hidden, acc off #0, #3; then held the bow:
  `PlyCin(1197)`. `unk_19` 3: held 30053: `PlyCin(1198)`, `BagRem`, `BagAdd(30026)`; then
  held the bow: `PlyCin(1197)`. Drop.
- **30058** (the Sword Notung, 35019). In hand: held a medallion (30055 → byte 30066, 30056 →
  byte 30067): `BagRem`, its byte = 1; both set: **the end** (below); else `PlyCin(1201)`,
  /2 shown. Drop. Nothing in hand, one byte set: `PlyCin(1202)`, /2 hidden, the medallion
  back in the bag (`BagAdd`) and its byte 0 (30055 when byte 30066 is set, else 30056).
- **30059** (30302 / 30303), nothing in hand: `PlyCin(1203)` (`unk_19` 0) or 1204; score
  +1.1 (first). In hand: drop.
- **30100** (the door, 35100). In hand: drop. `unk_19` 0: own volume of 30506 = 91 +
  rand(10), puzzle 35100's movability 0 off (0x404a90), play(30506), acc off #0 (the knock;
  sound end below). `unk_19` 1: acc off #1, `PuzSetAct(35101)`, play(30100).
- **30102** (Sieglinde, 30101 #1). In hand: held the Medallion (30055) with byte 30072:
  `PuzSetAct(35104)`, play(30105); drop. Nothing in hand: byte 30072 = 0:
  `RotSetRolTo(30101, 130, 20, 85.3)`, `PuzSetAct(35104)`, play(30102) (her story, sound
  chain); else byte 30078 = 0: `PuzSetAct(35103)`, play(30118).
- **30108** (Sieglinde's cup, 35109), held the Poison berries juice: `PlyCin(1199)`, 30110/1
  hidden, /2 shown, `RotSetAct(30101)`, alpha 130, beta 20, acc off 30102 #0, byte 30072 = 1,
  score +6.6, drop. Other objects: drop.
- **30109** (35111), nothing in hand: `PuzSetAct(35109)`; in hand: drop.
- **30200** (the lamps), nothing in hand: play(30162 + `unk_19`); in hand: drop.

**The end** (30058 with both medallions): 30058/3 shown, `PlyCin(1200)`, float 90007 = 100,
rotation 30001 at alpha 180, `RotSetAct`, type volume of type 2 = 0 (0x406e60), `TimStoAll`,
play(30007, loop), acc off all of every FO object, every FO rotation's movabilities off
(0x405820), SY's object 6 /0 and /5 shown (on puzzle 1), play(30120), drop. The sound chain
30120..30136 (below) shows Wotan's and Brünnhilde's words over a tour of the forest, then
returns to AS.

**Button down / take (0x441860, object)**: for 30016 it reads the object in hand and does
nothing else; no FO object has flag 2 or 8, so neither event is raised (Q-0052).

**Drag (0x441890, object 30016 the dial, phase)**. The drag state as in `ni.md`; read here:
cur x > reference x 0x406870, cur x < reference x 0x406850, cur y < reference y 0x406810,
cur y > reference y 0x406830, moved right (prev x < cur x) 0x406770, moved left 0x406730,
moved down (prev y < cur y) 0x406710, moved up 0x4066d0, the move's length √(dx² + dy²) from
the previous position 0x4068b0.

- start: drag mode 2 (the limit stays (0, 16)–(640, 464)), play(30500, loop), reference (440,
  248).
- move: around the reference, a clockwise move adds 1 to byte 30016 (above 48 → 0), a
  counter-clockwise one subtracts 1 (below 0 → 48), the presentation shown each time:
  right of and above it: moved right and down +1, left and up −1; right of and below: left
  and down +1, right and up −1; left of and below: left and up +1, right and down −1; left of
  and above: right and up +1, left and down −1 (a move along one axis only changes nothing).
  Then own volume of 30500 = trunc(length + 80) (f32 [0x47e688] = 80).
- release: stop(30500, 0x400).

**Bag click (0x441d50, object)** (`spec/bag.md`, list click with app+0x78): the place is the
current puzzle when one is current, else the current rotation. Only the Wolf Vision (30019)
is handled; each case below clears app+0x78 (the object is not taken in hand):

- at 30302 / 30303: byte 30017 ≠ 1: 30302's alpha, beta, ran copied to 30303 (`RotGetAlp` /
  `Bet` / `Ran`) and `RotSetAct(30303)`; else the reverse to 30302; byte 30017 toggled.
- at 35020: byte 30017 = 0: = 1, 30049/0, /1 shown, acc on #0; else = 0, hidden, acc off #0.
- at 35019: byte 30017 = 1: = 0, 30058 hidden, acc off #0; else = 1, acc on #0, /0 shown, and
  /2 when byte 30066 or 30067 is set.
- at 35002: byte 30017 = 0: = 1, 30017/1 shown, /3 hidden when byte 30075 is set else shown,
  /2 hidden when byte 30076 is set else shown; else /1..3 hidden, byte 30017 = 0.
- elsewhere app+0x78 stays set: the Wolf Vision goes in hand as any object.

**Before a movability (0x4420b0, from, to, index, `unk_19`, kind)**:

- kind 0, 30402 → 30501: byte 30037 = 1, 30051/0 shown, 30050 hidden, /3 shown, 30011's
  movabilities 1..2 off, acc on 30051 #0, #3.
- kind 1, 30601 → 35003: acc on 30026 #0.
- kind 2: 35002 → 30801 with byte 30076 = 0: 30017 hidden, byte 30017 = 0. 35003 → 30601:
  30026 hidden. 35006 → 30601: 30040 hidden, bytes 30022, 30023 = 0, acc on #0..1, off
  #2..5. 35007 → 30601: 30042 hidden, acc off #1..7, on #0, bytes 30025..30031 = 0. 35004 →
  30601 with bytes 30019 and 30021: `PlyCin(1184)`, `BagAdd(30030)`, with byte 30020 also
  `BagAdd(30029)` and byte 30020 = 0, 30028 hidden, /0 and /3 shown, byte 30021 = 0. 35008 →
  30601 with byte 30032: `BagAdd(30043)`, 30044/0 hidden. 35009 → 30601: 30045 hidden; →
  30602: `PlyCin(1205)`, 30045/7 shown. (Tests for 30701..30704 and 35111 → 30101 cannot
  match: Q-0051.) Then for every kind 2: acc off 30058 #0, 30058 hidden, 30049/0, /1 and
  30017/3, /1 hidden, byte 30017 = 0 (the Wolf Vision ends), acc off 30049 #0.

**After a movability (0x442580, to, from, index, `unk_19`, kind)**:

- kind 0: to 30501 from 30012: timers 1 and 3 stopped; byte 30071 = 0: play(30117), byte
  30071 = 1. To 30012 from 30501: timers 1 and 3 stopped, then restarted at 10 ms. To 30401
  from 30011: own volume 85 for 30300..30326; to 30011 from 30401: 100. To 30101 from 30003:
  80 then 100 for 30300..30313 (net 100). To 30008 from 30006: 80 for 30300..30313; to 30006
  from 30008: 100; to 30006 from 30005: `RotSetMovRidNam(30005, 1, "fom")` (the way back
  from 30005 to 30006 plays `fom.cnm` from now on).
- kind 2: to 30703 from 35010: acc on 30046 #0, off #1..2, 30046 hidden. To 30301 from
  35011: 30001 hidden, acc off #1..3, and acc on #0 while byte 30043 = 0.

**Timer (0x442810, id)**:

- 0 (the lightning, byte 30073): 0: 30061 shown, state 1, restart at 100 ms; 1: hidden, state
  2, restart at 10 ms; 2: shown, state 3, 100 ms; 3: hidden, state 0, restart at (rand(10) +
  15) × 1000 ms.
- 1: s = 30301 + rand(15), pan(s, 10 − rand(20)), play(s); restart at (rand(10) + 10) × 500.
- 2: 30025/0 unpaused (the hare); timer 2 stopped.
- 3: s = 30316 + rand(3), own volume 95, play(s); restart at (rand(10) + 30) × 500.
- 4: s = 30319 + rand(9), pan(s, 5 − rand(10)), play(s); restart at (rand(10) + 5) × 4000.
- 5: 30110/1 and 30109/0 unpaused, acc off 30109 #0; restart at rand(10) × 2000 + 15000.

**Animation (0x442b60, id, name, frame)**:

- 30000 (the bells' ride) frame 28 with byte 30047: `PlyCin(1207)`, byte 30047 = 0,
  `PuzSetAct(35009)`.
- 30001 / 30007 frame 10: play(30505), volume 90 / 95; frame 90: play(30503), 90 / 95; frame
  125: play(30504), 95 / 100; frame 202: 30001: 30110/1 paused (never reached, 200 frames:
  Q-0050); 30007: 30109/0 paused, acc on 30109 #0.
- 30002 / 30003 / 30004 / 30005 frame 19: 30110/6 shown / hidden, /9 shown / hidden (no
  animation has these ids and 30110 has 4 presentations: Q-0050).
- 30006 (the hare) frame 10: play(30502); frame 26: 30025/0 paused, restart timer 2 at
  (rand(10) + 5) × 1000.
- 30008 frame 25: acc on 30040 #5, #3.

**Sound (0x442e40, id, type, reason, ended)**, natural ends only:

- The door: 30100 → play(30101); 30101 → `PlyCin(1179)`, `RotSetAct(30101)`, alpha 130,
  beta 20, score +2.2 when byte 30074 = 0, byte 30074 = 1. 30506 (the knock): byte 30043 = 1
  and the Poison berries juice in the bag (`BagIsIn(30032)`): `PlyCin(1216)`, 30100/0 shown,
  acc off #0, on #1; else acc on 30100 #0, puzzle 35100's movability 0 on (0x404a70).
- Sieglinde's story: 30102 → `PuzSetAct(35103)`, play(30103); 30103 → 35104, 30104; 30104 →
  `PlyCin(1208)`, 35105, 30106; 30106 → `PlyCin(1209)`, 35110, 30107; 30107 → `PlyCin(1210)`,
  35106, 30108; 30108 → `PlyCin(1211)`, 35107, 30161; 30161 → `PlyCin(1212)`, 35108, 30109;
  30109 → `PlyCin(1213)`, `PuzSetAct(35111)`, 30109/0 shown. ("v → p, n" = `PlyCin(v)`,
  `PuzSetAct(p)`, play(n).)
- 30105 (the medallion shown to her): `PlyCin(1214)`, `BagAdd(30056)`, score +3.3, 30110/3
  shown, acc off 30102 #1, `RotSetAct(30101)`, alpha 130, beta 20. 30118: `RotSetAct(30101)`,
  alpha 130, beta 20, byte 30078 = 1.
- The ending, 30120..30136: each end frees one or two of object 6's pictures
  (`ObjPreHidDeaPuz`), sets the next rotation and plays the next sound, showing the next
  picture(s): 30120 → 30002 (/1), 30121 → 30003 (/2, /6), 30122 → 30004 (/3), 30123 → 30005
  (/4, /7), 30124 → 30006 (/8, /9), 30125 → 30008 (/10), 30126 → 30009 (/11, /15), 30127 →
  30010 (/12), 30128 → 30011 (/13, /16), 30129 → 30012 (/14), 30130 → 30701 (/17, /18),
  30131 → 30702 (/19), 30132 → 30703 (/20, /24), 30133 → 30704 (/21, /25), 30134 → 30401
  (/22), 30135 → 30402 (/23, /26); 30136: /23, /26 freed, `BagRemAll`, `TimStoAll`, stop all
  (0x400), `PlyCin(1215)`, **AS 0x437750(3)**: FO done (AS sets type 2's volume back to 100).

## Flow

1. Arrival (entry 0): videos 1217, 1218; the player at 30003 with Loge's Tear and the Wolf
   Vision; the forest's sounds and lightning run on timers.
2. The hunter's wall (35003 at 30601): hares and the bow; a hare given to the hare at 30003
   gives a Panel (30023). The press (35005) turns berries and poison berries (seen with the
   Wolf Vision at 35002, which also gives a Panel 30022) into juices.
3. The smithy: the Tear lights the furnace (35004); the mine (35006) gives the Pan and the
   Ignots; the furnace melts the Ignots into seven metals; the mold (35007) with the metals in
   order (Gold..Mercury = 1..7) makes the Golem; the Golem and the poison juice at 35008 give
   the third Panel (30021). With the Wolf Vision the worms at 35020 (with the Golem in hand)
   go on the fishing pole; fishing at 30703 after the fire arrow (byte 30034) gives the Key
   form the fish.
4. The fire (30011): the bow and the inflamed arrow (byte 30034).
5. The wolves' hall (30301): the scrolls on the pedestals in order 1..7 open 30302; the Wolf
   Vision shows 30303 and the dial (35001): turned to 0, its centre opens the way to the
   tree (30501, byte 30035); the tree after arriving from 30402 (byte 30037) ends that leg.
6. The wolf statue (35011): the fish key, then the three Panels; the Medallion (30055).
7. Sieglinde (30101): the door knocked with the poison juice in the bag and the medallion
   taken; her story; the poison in her cup (35109); the medallion shown gives Sieglinde's
   Medallion (30056).
8. The Sword Notung (35019, visible with the Wolf Vision): both medallions on it end FO
   (score 100, Wotan's and Brünnhilde's words, back to AS: 0x437750(3)).

## Needs (beyond the engine as of the RH work)

- The bag-click event 0x40c1f0 with app+0x78 (`spec/bag.md`), handled here for the Wolf
  Vision.
- `RotSetMovRidNam(rotation, index, name)` (0x405870 → `aMovability::SetRideName`): a
  movability's ride video changed at run time.
- `RotGetBet` / `RotGetRan` (0x405b40 / 0x405bb0), `RotSetBet` / `RotSetRan` on a rotation at
  run time; the pan of a sound (0x406ec0); the type volume (0x406e60, type 2 → 0).
- `PuzSetMovOnOrOff` on / off for puzzles (0x404a70 / 0x404a90) and all of a rotation's
  movabilities off (0x405820 → `RotSetMovOnOrOff(rotation, 0)`).
- `ObjPreHidDeaPuz` on SY's object 6 (puzzle 1) from zone code.
- The score in SY's float 90007.
- Timers restarted with new periods (`TimSto` then `TimSta`).
