# Zone RH (3): the Rhine — Alberich's world, second part (Ring, DVD)

Evidence: E-0100..E-0104. Addresses are `RING_DVD.EXE`; the set-up is listed in
`engines/ring/notes/zones/rh.md`, decompiles in `engines/ring/notes/decomp/rh/`. Ids are
decimal. Calls as in `ni.md`: play(id, n) 0x406de0 (n = 1 once, 2 looping), stop(id, r)
0x406e00, `PlyCin(name)` 0x401490 (`DATA\RH\PLA\<name>.cnm`), `PuzSetAct` 0x402490,
acc on (object[, from, to]) 0x403030 / 0x403070, acc off 0x403050 / `ObjSetAccOff` 0x403090,
mov on 0x405830 / `RotSetMovOff` 0x405850. "Show" / "hide" are `ObjPreSho` / `ObjPreHid`
(one presentation, or all with the one-argument forms). "Score +n" is SY's float 90005 +=
n (f32 [0x47e314] 1, [0x47e624] 2, [0x47e620] 3, [0x47e2e0] 5). "In hand" is 0x406530,
"held" 0x406550, "drop" 0x406570. "Game over n" is 0x408db0(n) (`ni.md`, "Game over").
`b` below is byte 21001 (the tunnel the player is in: 0, 1, 2).

## Places

- **Tunnels** 20010, 20020, 20030 (`RHS00N0x`), one after the other (rides 1709), each with
  a guard close-up 20011 / 20021 / 20031 (movability 0, ride 1708 / 1713 / 1717) and the
  guards' common puzzle 20000; 20030 leads on to 20101 (1718).
- **20101** (`RHS01N01`): the key Disgust (20007, an animated layer, id 20003, with the 3D
  sound 23014 declared off); its movability 1 to 20201 (1695) opens when the four keys are
  in the bag.
- **The goldfish** 20201..20203 (`RHS02N0x`): 20201 the fish (20201, animated layer);
  puzzles 20202 (the necklace on its stand, object 20202), 20203; the key machines 20204
  (one puzzle for the four keys: objects 20204, 20304, 20404, 20502, presentation 1 each).
- **20301..20305** (`RHS03N0x`): puzzles 20301, 20302, 20303; 20305 leads to 20401 (1734).
- **20401..20403** (`RHS04N0x`): rotation 20401 has a statue whose head follows the view
  (object 20401, layer 0, 28 frames, paused; timer 0 below); puzzle 20401 holds the
  anti-gravitation cells (20403); 20403 leads to 20501 (1739).
- **20501..20504** (`RHS05N0x`): the Daughter of the Rhine (20501; puzzles 20501..20503);
  20504 leads to 20601 (1744).
- **20601** (`RHS06N01`): the dive (accessibility of Helmet&Frog 10504) to **20701**
  (`RHS07N01`, juggle on, `RotSetJugOn(20701, 10, 1)`): the Rhine Gold (20700).
- Message puzzles 22001..22003 (`TR_NI_RH_BP0x`, the arrival).

## Variables

Bytes: 21001 the tunnel (0..2); 20200 (initial 1, the fish may be taken), 20201 (initial
1), 20202 the necklace's state (0 on its stand, 1 taken, 2 the fish given); 20301 the
necklace given at 20303; 20500 the Daughter (0..4). 21000, 20009 and word 20000 are
declared and never read. SY's 90005 is the score.

## Objects

| Object | Where | What |
|---:|---|---|
| 10504 "Helmet&Frog" | rotation 20601 accessibility; bag (from NI) | the dive |
| 20001..20003 | guard puzzles 20011 / 20021 / 20031: #0 the guard, #1 the whole screen (cursor 53) | the guards; presentations 1 (speaking), 2 / 3 (animation "a01_a", 5 frames), 4 |
| 20004 "Indifference", 20005 "Mistrust", 20006 "Selfishness" | guard puzzles (disabled), flags 9 (click, take) | keys; animations on the puzzles |
| 20007 "Disgust" | rotation 20101 (two halves around 0°), flags 9 | key; layer animation id 20003 |
| 20201 "GoldFish" | rotation 20201 #0 (`unk_19` 1), flags 9 | the fish |
| 20202 | puzzle 20202 (#0 enabled, #1, the bottom band `unk_19` 9), rotation 20201 (#3, #4 `unk_19` 2, disabled; #5 `unk_19` 1) | the necklace's stand |
| 20203 "Necklace" | bag | |
| 20204, 20304, 20404, 20502 | rotations 20202, 20304, 20402, 20503 (one accessibility each) | the key machines |
| 20301, 20302, 20303 | rotations 20301..20303 (`unk_19` 0 the way on, 1), puzzles (`unk_19` 2, 9) | |
| 20401 | rotation 20401 | the statue; layer 0 animation, frame set by timer 0 |
| 20402 | puzzle 20401 (presentations 0, 1) | |
| 20403 "Anti gravitation cells" | puzzle 20401 | |
| 20501 "Daughter of the Rhine" | rotation 20501 (#0, #1, #2 disabled), puzzle 20502 (#3 disabled, the band `unk_19` 9) | |
| 20700 "Rhine Gold" | rotation 20701 | |
| 21001 | puzzle 20000 (animation) | |
| 21003 | presentations 0, 1, 2 (rotation pictures shown as the machines open) | |
| 22000 | message puzzles 22001..22003 (animations) | |

## Entering (`GameSetZoneRH` 0x445740, entry)

- **0** (from NI's second water, `GoZone(3, 0)`): `BagRem(10505)` (the AG cells),
  play(23005, loop), `PlyCin(1706)`, `PuzSetAct(22001)`, play(22001): the message (sound
  chain below).
- **10** (resumed after Erda): needs `<install>Data\Save\alb.ars` (0x47bd10; else the log
  "Wrong Erda AS / RH" and nothing); `BagRemAll`; byte 90017 = 0: `RotSetAct(dword 90021)`
  and `RotSetFreOn` / `Off` by byte 90025; else `PuzSetAct(dword 90021)`; then
  `LoadSaveTimer("alb", 1)` (failing: logged, stop) and 0x4696f0 (the saved sounds).
  NI and RH share the file "alb" and SY's variables of world 1 (`spec/bag.md`, Erda).
- **999**: `BagRemAll`, `BagAdd` 10000, 10504, 20203, 20004, 20005, 20006, 20007,
  `RotSetAct(20501)`. No caller found (Q-0030).

## Handlers

**Object click (0x443990, object, `unk_19`)** (the place id is not read). Unless listed, an
object in hand is dropped and nothing else happens.

- 20001..20003 (the guard of tunnel b, nothing in hand): `PuzSetAct(20000)`, 21001/0 shown;
  `unk_19` 0: play(20021 + b); else play(20031 + b).
- 20004..20006 (a key on a guard's puzzle, nothing in hand): `BagAdd(object)`, score +2,
  the object hidden and its accessibilities off; rotation 20010 + 10b: movability 0 off, 1
  on, `RotSetAct`; with 20004..20007 all in the bag: rotation 20101's movability 1 on,
  play(23009).
- 20007 Disgust: in hand: drop, app+0x74 cleared. `unk_19` 0: `BagAdd(20007)`, score +2,
  20007/0 hidden, acc off 20007 #0..1, then the four-keys test as above.
- 20201 GoldFish. In hand: held GoldFish: `BagRem(20201)`, byte 20200 = 1, 20202's
  accessibility #5 on, #3..4 off, 20201/0 shown; then (any object) app+0x74 cleared, drop.
  Nothing in hand, `unk_19` 1, byte 20200 = 1: byte 20202 ≠ 0: app+0x74 cleared,
  `PlyCin(1694)`; else `PlyCin(1693)`, `BagAdd(20201)`, byte 20200 = 0, 20202 #5 off, #3..4
  on, 20201/0 hidden (app+0x74 stays set: the fish also goes in hand, `spec/bag.md`
  "Taking"). Otherwise app+0x74 cleared.
- 20202 the stand. In hand: `unk_19` 0, held Necklace: byte 20202 = 0, `BagRem(20203)`,
  20202 hidden, /0 shown; `unk_19` 2, held GoldFish: `BagRem(20201)`, score +3, acc off
  20201, byte 20202 = 2, `PlyCin(1688)`, 20202 hidden, `PuzSetAct(20203)`, play(20201);
  then drop. Nothing in hand: `unk_19` 0, byte 20201 = 1 and byte 20202 = 0: byte 20202 =
  1, `BagAdd(20203)`, 20202 hidden, /1 shown. `unk_19` 1: when byte 20201 ≠ 0:
  `PlyCin(1690)` (byte 20202 ≠ 0) or 1689, 20202 hidden, /(byte 20202 ≠ 0) shown; then
  `PuzSetAct(20202)`. `unk_19` 9: `PlyCin(1692)` (byte 20202 ≠ 0) or 1691,
  `RotSetAct(20201)`.
- 20204 / 20304 / 20404 / 20502 (the machines), held Disgust / Mistrust / Selfishness /
  Indifference: `BagRem`, score +5, its accessibilities off, `PuzSetAct(20204)`,
  play(20202 / 20304 / 20402 / 20504); for 20502 also byte 20500 = 4. Drop.
- 20301. In hand: `unk_19` 2, held Necklace: score +2, `BagRem(20203)`, `PlyCin(1676)`,
  acc off 20301 #1, `RotSetAct(20301)`; drop. Nothing in hand: `unk_19` 0: byte 20202 = 2
  and the Necklace not in the bag: `PlyCin(1678)`, rotation 20302 at alpha 10,
  `RotSetAct`; else `PlyCin(1677)`, **game over 1**. `unk_19` 1: `RotSetRolTo(20301, 42,
  23, 85.7)`, `PlyCin(1679)`, `PuzSetAct(20301)`, play(20301). `unk_19` 9: `PlyCin(1680)`,
  `RotSetAct(20301)`.
- 20302 (nothing in hand): `unk_19` 0: the Necklace in the bag: `PlyCin(1682)`, rotation
  20303 at alpha 10, `RotSetAct`; else `PlyCin(1681)`, **game over 1**. `unk_19` 1:
  `RotSetRolTo(20302, 320, 26, 85.7)`, score +2, acc off 20302 #1..2, `PlyCin(1683)`,
  `PuzSetAct(20302)`, play(20302).
- 20303. In hand: `unk_19` 1, held Helmet&Frog: 20303/0 shown, `PlyCin(1684)`,
  play(23010, loop), `PuzSetAct(20303)`; `unk_19` 2, held Necklace: byte 20301 = 1, acc on
  20303 #0, score +2, acc off 20303 #1..2, 20303/0 hidden, play(20303); drop. Nothing in
  hand: `unk_19` 0, byte 20301 = 1: `PlyCin(1685)`, `RotSetAct(20304)`. `unk_19` 1:
  `RotSetRolTo(20303, 140, 26, 85.7)`, `PlyCin(1686)`, **game over 3**. `unk_19` 9:
  stop(23010, 0x400), `PlyCin(1687)`, `RotSetAct(20303)`.
- 20401 (the statue), held Brutality (10000): `PlyCin(1675)`, score +3, `PuzSetAct(20401)`;
  drop.
- 20403 (the cells), held Necklace: `BagRem(20203)`, 20402/1 hidden, score +2,
  play(20401); drop.
- 20501 the Daughter (nothing in hand). `unk_19` 0: byte 20500 ≠ 0: `PuzSetAct(20502)`;
  else byte 20500 = 1, stop(23011, 0x400) (never started, Q-0031), `PuzSetAct(20501)`,
  score +2, play(20501). `unk_19` 1: byte 20500 < 2: `PlyCin(1670)`, **game over 4**; = 3:
  `PlyCin(1671)`, score +2, rotation 20503 at alpha 0, `RotSetAct`. `unk_19` 2, byte 20500 =
  2: byte 20500 = 3, stop(23011, 0x400), `PlyCin(1672)`, acc on 20501 #1, off #2,
  `PuzSetAct(20503)`, play(20503). `unk_19` 3: `PlyCin(1673)`, byte 20500 = 2, 20501/0
  hidden, acc off 20501 #0..1, on #2, `RotSetAct(20501)`. `unk_19` 9: `RotSetAct(20501)`.
- 10504 Helmet&Frog (the dive at 20601): held Helmet&Frog: `PlyCin(1668)`, play(23010,
  loop), rotation 20701 at alpha 0, `RotSetAct`; drop. Nothing in hand: `PlyCin(1669)`,
  **game over 3**.
- 20700 the Rhine Gold (nothing in hand): byte 20500 ≠ 4: `PlyCin(1667)`, **game over 2**.
  Else score +1, stop all (0x400), `PlyCin(1666)`, `BagRem(20403)`, 0x44a7d0(3): NI's
  entry 3 (`GoZone(2, 3)`, `ni.md`): back to Nibelheim (E-0101).

**Before a movability (0x444b40, from, …)**: from 20401: timer 0 stopped (0x4065e0).

**After a movability (0x444ba0, to, from, index, `unk_19`, kind)**:

- to 20401: timer 0 started, every 50 ms (0x4065a0).
- kind 0, in this order (each test independent, so the last that holds wins): to ≥ 20010:
  byte 21001 = 0 and, without 20004 in the bag, rotation 20010's movability 0 on, 1 off;
  to ≥ 20020: byte 21001 = 1 and the same with 20005 and 20020; to ≥ 20030: byte 21001 = 2
  and the same with 20006 and 20030.
- kind 1, to 20011..20031 (a guard): (20001 + b)/0 shown, the id of its presentation 2's
  animation set to 20001 (`ObjPreSetAniIdeOnPuz(20001 + b, 2, 0, 20001)`), /2 shown.

**Timer (0x444d30, id)**: 0 (the statue's head, re-entry guarded by 0x4a1cd8): a =
trunc(`RotGetAlp(20401)` − 35) (`RotGetAlp` 0x405ab0: the stored alpha + 135, less 360
above 360); for 0 < a < 146, f = trunc(a × 0.2632 (f64 [0x47e690] = 5/19)); for 1 ≤ f ≤ 28
and f not the last one set (0x4a1cdc): `ObjPreAniSetActFra(20401, 0, f)` (E-0103).

**Animation (0x444dc0, id, name, frame)**: 20001 frame 5: (20001 + b)/2 hidden, /4 shown,
play(20011 + b). 20003 frame 2: play(23014).

**Sound (0x444e60, id, type, reason, ended)**, natural ends only:

- 20011..20013 (a guard's first words): (20001 + b)/2 and /4 hidden, presentation 2's
  animation id 20002, /3 shown, acc on (20001 + b) #0..1.
- 20021..20023: `PlyCin("rh_<b + 1>")`, `PlyCin(1696)`, 20001 + b hidden; rotation 20010 +
  10b: movability 0 off, 1 on, `RotSetAct`: the guard lets the player on.
- 20031..20033: `PlyCin("rh_<b + 1>_l0")`, acc off 20001 + b, acc on 20004 + b, (20004 +
  b)/0 shown, 20001 + b hidden, `PuzSetAct(20011 + 10b)`: the guard leaves its key.
- 20201: `PlyCin(1698)`, `BagAdd(20203)`, play(23009), acc off 20202, `RotSetAct(20201)`,
  its movability 0 on.
- 20202: `PlyCin(1699)`, 21003/0 and 20204/0 shown, rotations 20202 movabilities 2 and 0
  off, 20203 movability 0 off, 20202 #1 on, 20203 #1..3 on, `RotSetAct(20202)`.
- 20301: 20301/1 hidden. 20302: 20302/1 hidden, `BagAdd(20203)`, `PlyCin(1700)`, beta of
  20302 = 0.3, `RotSetAct(20302)`. 20303: stop(23010, 0x400), `PlyCin(1687)`, play(23009),
  rotation 20303 at alpha 325, beta 0.3, `RotSetAct`.
- 20304: `PlyCin(1701)`, 20304/0 and 21003/1 shown, 20304 movabilities 2 and 0 off, 20305
  #0 off, 20304 #1 on, 20305 #1..2 on, `RotSetAct(20304)`.
- 20401: `PlyCin(1674)`, `BagAdd(20403)`, play(23009), 20402 hidden, `PlyCin(1702)`, alpha
  of 20402 = 0, `RotSetAct(20402)`. 20402: `PlyCin(1703)`, 20404/0 and 21003/2 shown,
  20402 #0 and 20403 #0 off, 20402 #1 on, 20403 #1..2 on, `RotSetAct(20402)`.
- 20501 → `PuzSetAct(20502)`, play(20502). 20502: 20501/2 hidden, acc on 20501 #3..4.
  20503: 20501/3 hidden, `PlyCin(1704)`, alpha of 20501 = 0, `RotSetAct(20501)`. 20504:
  `PlyCin(1705)`, 20502/0 shown, 20503 #0 and 20504 #0 off, 20504 #1..2 on,
  `RotSetAct(20503)`.
- The message: 22001 → `PuzSetAct(22003)`, play(22003); 22003 → `PuzSetAct(22002)`,
  play(22002); 22002 → `PlyCin(1697)`, `BagAdd(10000)`, `BagAdd(10504)`, rotation 20010
  at alpha 1.5, beta −4.3, ran 79.3, `RotSetAct`.

RH handles no button-down, drag, on-accessibility, take (0x40bed0) or list-click event;
"on a movability" (0x44a1b0) and "on nothing" (0x442e30) are empty (`spec/events.md`).

## Game overs

0x408db0(n) (`ni.md`): 1 at 20301 or 20302 going on without the right necklace state
(videos 1677, 1681); 2 the Rhine Gold before the Daughter's machine (1667); 3 at 20303
`unk_19` 1 (1686) or the dive without Helmet&Frog in hand (1669); 4 at 20501 `unk_19` 1
too early (1670).

## Flow

1. Arrival (entry 0): the AG cells leave the bag; the message of NI (22001, 22003, 22002)
   plays, then Brutality and Helmet&Frog are (again) in the bag; the player stands in the
   first tunnel (20010).
2. Each tunnel's guard (20011, 20021, 20031): talking to him (`unk_19` 0, sound 20021 + b,
   video rh_<b+1>) opens the tunnel's way on; clicking elsewhere (20031 + b, rh_<b+1>_l0)
   makes him leave his key (Indifference, Mistrust, Selfishness), and taking it also opens
   the way on. Arriving in a tunnel closes again the way on of every tunnel up to it whose
   key is not in the bag and reopens its guard.
3. 20101: Disgust; with the four keys in the bag the way to the goldfish (20201) opens.
4. The goldfish: the necklace from its stand (20202 `unk_19` 0); the fish taken (20201
   `unk_19` 1) and given at the stand (`unk_19` 2): the necklace comes back (sound 20201)
   and 20201's way to 20202 opens; Disgust in the machine at 20202 (20204) opens 20202 →
   20203 → 20301.
5. 20301..20305: the necklace given (20301 `unk_19` 2, 20303 `unk_19` 2), Helmet&Frog at
   20303, Mistrust in 20304's machine opens 20305 → 20401.
6. 20401: Brutality on the statue opens its puzzle; the necklace on the cells gives the AG
   cells (sound 20401); Selfishness in 20404's machine opens 20403 → 20501.
7. The Daughter of the Rhine (20501): her questions (bytes 20500 1..3), Indifference in
   20502's machine (byte 20500 = 4) opens 20504 → 20601.
8. The dive with Helmet&Frog in hand (20601) reaches the Rhine Gold (20701); taking it
   (byte 20500 = 4) ends RH: the AG cells leave the bag and NI is entered at 3 (`ni.md`:
   the heater's ending).

## Needs (beyond the engine as of the NI work)

- `ObjPreAniSetActFra(object, presentation, frame)` (0x4039b0 → `aObject` 0x420ce0 →
  0x42efd0 → `aAnimation::SetActiveFrame` 0x416aa0 on every animation of the presentation:
  current frame = frame − 1 when 1 ≤ frame ≤ frames); `RotGetAlp` (stored alpha + 135).
- `ObjPreSetAniIdeOnPuz` while playing (the engine applies it only in the set-up).
- The take path's cancel: a zone handler clearing app+0x74 keeps the clicked object out of
  the hand (`spec/bag.md` "Taking"); RH's click handler does it for 20007 and 20201.
- `RotSetBet` / `RotSetRan` while playing; `RotSetJugOn` (20701; the juggle is not
  specified); `PlyCin` with formatted names.
- The resume entry 10 shares NI's "alb" state.
