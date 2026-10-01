# Zone AS (7): the hub — Ish's world and the ring dial (Ring, DVD)

Evidence: E-0056. Addresses are `RING_DVD.EXE`; the set-up (0x4635a0) is listed in
`engines/ring/notes/zones/as.md`. Ids are decimal (the code has them in hex: 80001 =
0x13881). Calls: play(id, n) is 0x406de0 (n = 1 once, `spec/sound.md`), `PlyCin(name)`
0x401490 and `PlyCinMul(name, channel)` 0x4016a0 play `DATA\AS\PLA\<name>.cnm`
(`spec/video.md`; `PlyCinMul` first stops sound types 4 and 5 with reason 0x100 and plays
the language's channel, `GetLanCha`), `GoZone(zone, entry)` is 0x402280 (below).

## Places

- Rotations 80001..80011, 80013..80015 (`ASS00Nnn`, one layer each) are the island of
  Ish, joined by movabilities with ride videos 1001..1046; 80003 leads down (1013) to
  80101 (`ASS01N01`, six layers): the chamber of the ring dial.
- Puzzles: 80001 (`Old_Ish.bma`), 80011..80014 (`DRIL_*`, the intro's stills), 80002..80005
  (`ASV01..04`), 80006..80010 (`ASP01L01`..`ASP05L01`, the four destinations and one
  more); each of 80002..80010 has a movability at the bottom band (0, 420)–(640, 464),
  cursor 55, back to 80101 (arrival alpha as declared).
- Ambient: 80200 (`1048.was`) on every rotation 80001..80015 and 80101; puzzle ambient
  80201, 80203..80205, 80207 on 80002..80010; 3D sound 80206 on 80001 (angle 270, amplitude
  20, volume 90).

## Variables

Bytes 80000..80005 (initial 0, 0, 1, 0, 1, 0); floats 80001 = 1, 80002 = 2, 80003 = 100.
Byte 80004 is the dial's target frame, 80005 the dial's current frame, 80003 cleared after
a destination ride. SY's bytes 90001..90004 say whether the four worlds (NI, N2, FO, WA)
are done; their dwords 90005..90008 hold the zone and 90009.. the entries to resume in
(`GoZone`).

## Objects

| Object | Where | What |
|---:|---|---|
| 80007 | 80101 accessibility (1314, 183)–(1397, 226) | the ring's place; used with Death in hand at the end |
| 80012 | 80005 ×6, 80008, 80011 accessibilities, `unk_19` 0..7 | sound points: each plays one sound |
| 80016 | layer 0 of every AS rotation, presentations 0..13 | (not shown by AS code) |
| 80018 | 80101: layers 0 (pres. 0), 1 animated (pres. 1, 49 frames, 12.5 fps, loop, id 80001, shown, paused), 2..5 (pres. 2..5); four accessibilities (disabled) | the dial and the four worlds' marks |
| 80019 | puzzles 80006..80010, (159, 161)–(477, 393), `unk_19` 0..5 (1 disabled); presentation 0 `ASP01L02.bma` on 80006 | entering a world |
| 80020 | "Death", icon `AS_Nor_d` | inventory object given when all four worlds are done |
| 80021 | 80101, five accessibilities `unk_19` 0..4 | the dial: 0 go, 1..4 turn |
| 80022 | 80101, (0, −580)–(3600, −279) | the sky: leave (entry 5) |

## Entering (`GameSetZoneAS` 0x437ba0, entry)

- **999** (new game): rotation 80001 at alpha 90, ran 85.3; timers 2 (100 s), 3 (220 s),
  4 (150 s).
- **998**: `PlyCinMul(1164, channel)` (1163 for languages 4, 5 and 7), `PlyCin(1166)`,
  `PuzSetAct(80011)`, play(80100, 1): the intro's sound chain (below).
- **5**: `PlyCin(1047)`, rotation 80003 at alpha 270, beta 0, ran 85.3.
- **6**: `PlyCinMul(1162, channel)` (1161 for language 6; 1160 for 4, 5, 7),
  `PuzSetAct(80001)`, play(80107, 1): the end.

## Handlers

**Object click (0x4364a0, object, `unk_19`)** — with an inventory object in hand
(0x406530), every case below first drops it (0x406570) and ends, except 80007:

- 80007: with Death (80020) in hand: `BagRemAll`, stop all sounds (0x400), `TimStoAll`,
  `GoZone(7, 6)`; the object in hand is dropped in any case.
- 80012: play once 80028, 80025, 80021, 80024, 80022, 80026, 80027, 80023 for `unk_19`
  0..7.
- 80018 `unk_19` n = 0..3, when byte 90001 + n is 1 (that world done): `PuzSetAct(80002 +
  n)`, own volume of sound 80201 + {0, 2, 3, 4}[n] set to 80 / 90 / 90 / 80, play(80040 /
  80049 / 80058 / 80068, 1) (a monologue chain, below).
- 80019 `unk_19` 0 and 2 → world NI when byte 90001 is 0; 1 and 4 → N2 when 90002 is 0;
  3 → FO when 90003 is 0; 5 → WA when 90004 is 0: `TimStoAll` then the world's entry
  (0x44a7d0 / 0x436270 / 0x443710 / 0x43ad00 with 0): `GoZone(world, 0)` the first time,
  else `GoZone(dword 90005.. , 10)` (resume).
- 80021 `unk_19` 0 (go): by byte 80004 — 1: `PuzSetAct(80006)` and `PlyCin(1141)` when
  byte 90001 is 0, else `PlyCin(1142)` and presentation 0 of 80019 shown; 11:
  `PuzSetAct(80007)`, `PlyCin(1143)`; 21: `PuzSetAct(80009)`, `PlyCin(1144)`; 31:
  `PuzSetAct(80008)`, `PlyCin(1145)`; 41: `PuzSetAct(80010)`, `PlyCin(1146)`.
  `unk_19` 1..4 (turn by 10, 20, 30, 40): play(80080, 1) and play(80082, 1); byte 80004 =
  byte 80005 + 10 × `unk_19`, less 50 when above 49; the dial's animation (80018
  presentation 1) unpaused; 80021's accessibilities 0..4 disabled.
- 80022: `GoZone(7, 5)` (0x437750(5)).

**Animation (0x437110, id, name, frame)**: for id 80001 (the dial), when the frame is
byte 80004: the animation paused, 80021's accessibilities 0..4 enabled, sound 80082
stopped (0x400) and play(80081, 1). Then byte 80005 = frame.

**Before a movability (0x436c10, from, to, index, `unk_19`, kind)**, kind 2 (a puzzle to a
rotation), to 80101: from 80006 → `PlyCin(1151)` when byte 90001 is 0, else `PlyCin(1152)`;
80007 → 1153; 80009 → 1154; 80008 → 1155; 80010 → 1156.

**After a movability (0x436d60, to, from, …, kind)**: kind 2, to 80101 from 80006..80010:
byte 80003 = 0.

**Timer (0x436df0, id)**:

- 2, 3, 4: play(80018 / 80019 / 80020, 1); timer 5 started (20 / 30 / 10 s) and timer 6
  (10 s) when not running; when no dialogue plays (type 5), play(80004 + rand() × 12 /
  32768, 1).
- 5: byte 80001 += 1; the current rotation's beta += float 80001 × float 80002, its alpha +=
  float 80001 × float 80002 × [0x47e300]; float 80001 × [0x47e338], float 80002 ×
  [0x47e628]; when byte 80001 reaches 51: byte 80001 = 0, float 80002 = 2.0, timers 5 and
  6 stopped (`TimSto`), 80016 hidden.
- 6: rand() × 10 / 32768 even → 80016's presentations shown, odd → hidden.

**Sound (0x437190, id, type, reason, ended)**, natural ends only:

- the monologue chains 80040 → 80041 → … → 80048, 80049 → … → 80057, 80058 → … → 80067,
  80068 → … → 80080: each plays the next once; at 80048 / 80057 / 80067 / 80080's end: own
  volume 100 for sound 80201 / 80203 / 80204 / 80205 and byte 80002 = 2 / 3 / 4 / 5;
- the intro: 80100 → `PuzSetAct(80012)`, play(80101); 80101 → `PuzSetAct(80011)`,
  play(80102); 80102 → `PuzSetAct(80012)`, play(80103); 80103 → `PlyCin(1157)`,
  `PuzSetAct(80013)`, play(80104); 80104 → play(80105); 80105 → `PlyCin(1158)`,
  `PuzSetAct(80014)`, play(80106); 80106 → timers 2, 3, 4 (100, 220, 150 s), rotation
  80001 at alpha 270, beta −26, ran 85.3;
- the end: 80107 → `PlyCin(1159)`, 0x431190(7, 0) (`games/ring/docs/sy.md`: Isha's
  picture, her words 90001, the credits, the menu).

## Returning from a world (0x437750, n)

n = 1..4 (from NI, N2, FO, WA): `SetZone(7)`; 80018's accessibility n − 1 enabled; byte
90000 + n = 1; `BagRemAll`; when bytes 90001..90004 are all 1, `BagAdd(80020)` (Death);
80018 presentation n + 1 shown (the world's mark on the dial); rotation 80101 at alpha 90,
ran 85.3; play(80040 / 80049 / 80058 / 80068, 1); for n = 1 also 80019's accessibility 0
disabled and 1 enabled; for n = 3 the type volume of type 2 set to 100.
n = 5: `GoZone(7, 5)`. n = 13: `BagRemAll`, `TimStoAll`, stop all sounds (0x400),
`SetZone(7)`, rotation 80101 at alpha 90, ran 85.3, the inventory hidden, timers 2, 3, 4.

## `GoZone(zone, entry)` (0x402280)

Decides whether the zone's data is available (always on the DVD: the CD check reads
`<CD>data\cd.ini`), then leaves the place (0x40b650), stops all sounds (reason 8), clears
the ambient lists (0x41a820), closes the zone archive unless the zone is SY, `SetZone`, and
calls the zone's entry function (0x40d220 → `GameSetZone<zone>`). Without the data it
shows the "insert CD" screen (not needed for the DVD).

## Flow

1. A new game starts on the island (80001) with timers 2..4: at 100 / 220 / 150 s and then
   periodically, ambient voices (80018..80020) and random whispers (80004..80015) play, and
   timer 5 sways the view (a dizziness that fades out over 50 ticks) while timer 6 makes
   80016 flicker.
2. The player walks down to the chamber (80101). The dial (80021 `unk_19` 1..4) turns the
   ring animation by 10..40 frames; it stops at the target frame (the animation event).
   `unk_19` 0 rides to the world facing the ring's position (frames 1, 11, 21, 31, 41 →
   puzzles 80006, 80007, 80009, 80008, 80010).
3. On a world's puzzle, clicking the picture (80019) enters the world (NI, N2, FO, WA);
   the band at the bottom rides back to the chamber.
4. Finishing a world returns here (0x437750(n)): its mark shows on the dial and a
   monologue plays; the dial's marks (80018 `unk_19` n) then show the world's puzzle and
   its monologue again.
5. When all four are done the player gets Death; using it on the ring's place (80007)
   plays the end (entry 6) and Isha's words, then the credits.
