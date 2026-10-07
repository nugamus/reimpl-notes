# China: places, zones and what clicking does

China has no level files: every place is a procedure in `CHINE.EXE` (E-0700). This page
describes how those procedures are built, what a hotspot ("zone") is, the verbs a place can
use, the naming of warps, videos and dialogue lines, and works through the first place of a
new game. The list at the end gives every procedure; the full call listing of any of them
comes from the dumper:

    uv run engines/cryomni3d/tools/china_places.py            # every place
    uv run engines/cryomni3d/tools/china_places.py pne140     # one place

The dumper prints, per procedure, its entry part and event part as a sequence of API calls
with decoded arguments (rects, strings, procedure names, variable and object names, angles)
and the clicked-zone tests (`zone == n ?`). It does not yet rebuild the if/else structure
of the variable tests (Q-0702).

## Place procedures (E-0700)

- A place is a procedure taking one message number:
  - 1: answers the next procedure in the global list (the last answers nothing). The list
    starts at `Script_Start` (0x436db0) and holds all 270 procedures. Finding a place by
    name (map, loading a save) walks this list comparing names.
  - 2: answers the place's name (e.g. `pne140`). The first three letters choose the music
    on arrival: PNE, AIE, AIO, CTP, CGC play `Allee`; CPC, LGE, SPF `Bureaux1`; LGA, BPI,
    ESP, NWF, BAN, BDA `Bureaux2`; PDC `Concub`; JIX `Jardins`; CTH, CHS, SHS `SalleHS`
    (DATA/MUSIC/*.ZIK). Other names (close-ups, puzzles) keep the current music.
  - 3: entry. Run once, on the first tick after the game went to this place. A place's
    entry clears the zone list, adds its zones, loads its warp, and adjusts zones to the
    current state; it then runs the event part too.
  - anything else (0 every frame): event part. First the generic zone handler runs
    (hover cursor, standard click actions, below); if that did not already leave the place,
    the procedure reacts to the clicked zone (its index, in creation order) with its own
    code: tests on game variables and object states, then dialogues, videos, images,
    variable changes, inventory changes, puzzles, and a goto.
- Going to a place records it as current and plays its music; its entry runs on the next
  tick. The arrival view (alpha, the horizontal angle in radians, and beta, vertical) is
  whatever was set before the goto: by the zone (its alpha/beta, when alpha is not
  negative) or by the code (a set-angles call right before the goto).
- Not every procedure is a panorama: close-ups, puzzle entries and cut-scene steps use the
  same shape with an image or video instead of a warp (88 of the 270 load no warp).

## Zones (E-0701, E-0702)

- A zone is a rectangle {top, left, bottom, right} (inclusive) in the warp picture's own
  coordinates: x 0..2047 around the panorama, y 0..767. A zone across the seam at x = 0 is
  added twice. The mouse position on screen is projected into the warp (Omni3D library)
  and zones are tested in creation order; the first hit wins. At most 40 zones per place.
- Each zone has a disabled flag (1 = inactive), a type, a target and two angles. Places
  enable and disable zones by index while running.
- Types, with their hover cursor (sprite in DATA/SPRITES/CURSEURS) and click:

| Type | Use | Target | Hover cursor | Click |
|---:|---|---|---|---|
| 0 | go | a place procedure, or none | finger (`doigt`) | turn towards the click, set the zone's angles if given, go to the target; with no target the place's own code reacts |
| 2 | look | a close-up procedure | eye (`voir`) | as type 0 |
| 4 | take | a procedure, or none | hand (`prendre`) when nothing is held, else the held object's cursor | as type 0 |
| 6 | use | none | `util` when nothing is held, else the held object's cursor | the place's code reacts (usually: is the right object held?) |
| 7 | label | a LABELS.TXT key | unchanged; the label text shows | none |
| 8 | documentation | a Fichetxt.txt key | question mark (`interrog`) with empty hands; the entry's title shows | opens that documentation entry, then re-enters the place |
| 9 | talk | none | mouth (`bouche`) | the place's code reacts (dialogue) |

  Types 1, 3, 5 exist in the handler but no place creates them.
- Visit mode (variable `MODE_VISITE`, the menu's "visite"): look, take, use and talk zones
  are created disabled and labels exist only in this mode; enabling a zone later keeps use,
  label and talk zones off in visit mode.

## What a place can do (E-0703)

Load a warp (`DATA/WARP/<name>.HNM`); play a video (`DATA/HNM/<name>.HNS`, transitions
and cut-scenes); show a still image (`DATA/IMAGES/<name>.TGA`, close-ups); play a synced
dialogue (a DIAL.TXT line with its voice `DATA/LOC/VOICES/<id>.WAV`, and two talking-head
videos, the other character's and Anjing's, each `DATA/SYNC/<stem>0..3.HNM`); play a
voice-only line; set and test game variables (220 named variables; 0 `MODE_VISITE`,
1 `CHAPITRE`, the rest mostly named after the dialogue line, video or event they record:
`GICD1011`, `Venant_de_HORLOGE`, `VAR_Pieces`); test and change object states (initial,
held as cursor, in inventory, destroyed) for the 36 objects; start a puzzle by number; add
a note to the notebook (MINUTES.TXT key, e.g. `MIN001`); queue, play or stop a sound
effect; set the view angles; go to another procedure.

## Names (E-0704)

- Warp: three-letter area + optional `w` + three digits (`pne140`, `jixw111`, `cpc600`;
  one `aie600b`). Area codes are the music groups above.
- Transition and cut-scene videos: mostly `<area or character>h<nnn>` (`jixh111`, `pneh202`, `DAMH501`), a few plain words (`arbre`, `fin`), in DATA/HNM as .HNS.
- Synced dialogue: a line id such as `GICD1011` (block `#GICD1011#` in DIAL.TXT, which
  chains further lines with `GOTO`; voice `GICD1011.WAV`) plus two video stems such as
  `D140gia` and `D140ANJ`: a letter and three digits naming the scene (here the place
  pne140), then the three-letter character (`ANJ` is Anjing, the player). Each stem has
  four files, 0..3. Line ids: two letters of the speaker, one of the listener, a letter,
  then the act digit and three more (Q-0701).
- `CHAPITRE` is a story step from 1 to 18, set as the plot advances, not the chapter
  shown to the player.

## Worked example: the first place, pne140 (E-0705)

New game goes to `Script_Start`, which clears zones, sets `CHAPITRE` to 1, adds note
`MIN001`, sets the view to alpha 4.7, beta 0, and goes to `pne140` (procedure 0x431050).

pne140, entry: warp `pne140`; zones in this order:

| # | Rect (top, left, bottom, right) | Type | Start | Target |
|---:|---|---|---|---|
| 0 | 277, 974, 439, 1084 | go | on | pne150 |
| 1 | 381, 1483, 512, 1517 | talk | off | (code) |
| 2 | 381, 1584, 512, 1616 | talk | off | (code) |
| 3 | 244, 1471, 475, 1612 | go | off | (code) |
| 4 | 295, 1990, 439, 2047 | go | on | pne130 |
| 5 | 295, 0, 439, 48 | go | on | pne130 |
| 6 | 354, 1358, 460, 1408 | label `lionne_pne` | visit mode only | |
| 7 | 358, 1702, 454, 1756 | label `lion_pne` | visit mode only | |

Then, in visit mode, zone 3 is enabled. Zone 0 and 4/5 keep the view (no angles).

Event part, every frame after the generic handler:
- Zones 1 and 2 (the two guards, `gia` and `gib`) are enabled when either
  `CHAPITRE` is 1 and none of `XNED1011`, `GICD1011`, `GIDD1011` is set, or
  `CHAPITRE` is 9, `ENED3111` is 1 and neither `GICD3111` nor `GIDD3111` is set.
- Click on zone 1: at step 1 (same test as above) synced dialogue `GICD1011` with videos
  `D140gia` and `D140ANJ`, set `GICD1011`, disable zones 1 and 2. At step 9 (same test as
  above) dialogue `GICD3111` with the same videos, set `GICD3111`, add note `MINAO311`,
  disable zones 1 and 2.
- Click on zone 2: the same with guard `gib` (`D140gib`), lines `GIDD1011` / `GIDD3111`
  and variables of those names.
- Click on zone 3 (the gate): set the view to alpha 1.58, beta 0; in visit mode go to
  `pne210` (outside visit mode zone 3 stays disabled, so the gate is reached otherwise).

## Every procedure

In list order (the order of message 1). Zones = zones created by the entry part; "goes to"
= targets of go/look/take zones and of gotos in the code.

| Procedure | Address | Warp | Zones | Goes to (zones and code) |
|---|---|---|---:|---|
| Script_Start | `0x436db0` | - | 0 | pne140 |
| cth140 | `0x436cc0` | cth140 | 5 | cth130, cth150, cth210 |
| cth210 | `0x436ba0` | cth210 | 6 | cth130, cth140, cth150, cth220, cth230, cth290 |
| cth130 | `0x436a60` | cth130 | 8 | cth110, cth120, cth140, cth210, cth230 |
| cth230 | `0x436970` | cth230 | 5 | cth130, cth210, cth220, cth240 |
| cth120 | `0x4368a0` | cth120 | 5 | cth110, cth130 |
| cth110 | `0x4367e0` | cth110 | 4 | chs150, cth120, cth130 |
| cth150 | `0x4366b0` | cth150 | 7 | cth140, cth160, cth170, cth210, cth290 |
| cth170 | `0x4365d0` | cth170 | 5 | chs110, cth150, cth160 |
| cth160 | `0x4364e0` | cth160 | 6 | cth150, cth170 |
| cth290 | `0x4363f0` | cth290 | 5 | cth150, cth210, cth220, cth280 |
| cth220 | `0x436330` | cth220 | 4 | cth210, cth230, cth290 |
| cth280 | `0x436280` | cth280 | 4 | cth270, cth290 |
| cth240 | `0x4361e0` | cth240 | 3 | cth230, cth250 |
| cth250 | `0x4360d0` | cth250 | 6 | cth240, cth260, cth310, cth330, cth340 |
| cth270 | `0x435fa0` | cth270 | 7 | cth260, cth280, cth310, cth360, cth370 |
| cth260 | `0x435eb0` | cth260 | 5 | cth250, cth270, cth310 |
| cth310 | `0x435d90` | cth310 | 6 | cth250, cth260, cth270, cth320, cth330, cth360 |
| cth330 | `0x435c60` | cth330 | 7 | cth250, cth310, cth320, cth340, cth350 |
| cth340 | `0x435ba0` | cth340 | 4 | cth250, cth330, cth350 |
| cth320 | `0x435ab0` | cth320 | 5 | cth310, cth330, cth360 |
| cth360 | `0x435980` | cth360 | 7 | cth270, cth310, cth320, cth370, cth380 |
| cth350 | `0x435880` | cth350 | 7 | cgc220, cth330, cth340 |
| cth380 | `0x435770` | cth380 | 8 | cgc210, cth360, cth370 |
| cth370 | `0x435680` | cth370 | 5 | cth270, cth360, cth380 |
| chs150 | `0x435590` | chs150 | 7 | chs140, cth110 |
| chs110 | `0x4354a0` | chs110 | 7 | chs120, cth170 |
| chs120 | `0x435350` | chs120 | 9 | chs110, chs130, chs240, chs250 |
| chs130 | `0x435220` | chs130 | 7 | chs010, chs120, chs140, chs240, chs250, chs260 |
| chs250 | `0x435030` | chs250 | 14 | chs120, chs130, chs140, chs210, chs220, chs230, chs240, chs260 |
| chs240 | `0x434ea0` | chs240 | 12 | chs120, chs130, chs210, chs220, chs250 |
| chs140 | `0x434d50` | chs140 | 9 | chs130, chs150, chs250, chs260 |
| chs010 | `0x434c80` | chs010 | 5 | chs130, shs140 |
| chs260 | `0x434b20` | chs260 | 10 | chs130, chs140, chs220, chs230, chs250 |
| chs210 | `0x4349e0` | chs210 | 10 | chs220, chs240, chs250 |
| chs220 | `0x434830` | chs220 | 13 | chs210, chs230, chs240, chs250, chs260 |
| chs230 | `0x4346e0` | chs230 | 11 | chs220, chs250, chs260 |
| shs140 | `0x434580` | shs140 | 10 | chs010, shs130, shs150, shs240 |
| shs270 | `0x4344a0` | shs270 | 6 | shs170, shs260 |
| shs260 | `0x4343d0` | shs260 | 4 | shs160, shs250, shs270 |
| shs250 | `0x434300` | shs250 | 4 | shs150, shs240, shs260 |
| shs240 | `0x4340b0` | shs240 | 17 | shs140, shs230, shs250 |
| trone | `0x434030` | - | 2 | bombe1, shs240 |
| bombe1 | `0x433f80` | - | 2 | bombe2, shs240 |
| bombe2 | `0x433f40` | - | 0 |  |
| shs230 | `0x433e70` | shs230 | 4 | shs130, shs220, shs240 |
| shs220 | `0x433da0` | shs220 | 4 | shs120, shs210, shs230 |
| shs210 | `0x433cb0` | shs210 | 6 | shs110, shs220 |
| shs170 | `0x433c20` | shs170 | 2 | shs160, shs270 |
| shs160 | `0x433b50` | shs160 | 4 | shs150, shs170, shs260 |
| shs150 | `0x433a80` | shs150 | 4 | shs140, shs160, shs250 |
| shs130 | `0x4339b0` | shs130 | 4 | shs120, shs140, shs230 |
| shs120 | `0x4338e0` | shs120 | 4 | shs110, shs130, shs220 |
| shs110 | `0x433830` | shs110 | 3 | shs120, shs210 |
| cpc330 | `0x433740` | cpc330 | 5 | cpc320, cpc340, cpc440 |
| cpc720 | `0x4335f0` | cpc720 | 10 | cpc600, cpc710, cpc730 |
| cpc350 | `0x433500` | cpc350 | 5 | cpc340, cpc360, cpc540 |
| cpc600 | `0x433470` | cpc600 | 2 | cpc340, cpc720 |
| cpc340 | `0x433380` | cpc340 | 5 | cpc330, cpc350, cpc600 |
| cpc440 | `0x4332b0` | cpc440 | 4 | cpc330, cpc420, cpc430, cpc450 |
| cpc320 | `0x4331d0` | cpc320 | 5 | cpc310, cpc330 |
| cpc450 | `0x433120` | cpc450 | 3 | cpc430, cpc440, cpc710 |
| cpc310 | `0x433090` | cpc310 | 2 | cpc140, cpc320 |
| cpc140 | `0x432fa0` | cpc140 | 5 | cpc130, cpc310, cpc420 |
| cpc130 | `0x432eb0` | cpc130 | 5 | cpc120, cpc140, cpc420 |
| cpc120 | `0x432ce0` | cpc120 | 7 | bpiw101, bpiw102, cpc110, cpc130, cpc420 |
| cpc110 | `0x432880` | cpc110 | 10 | aio200, cpc120, cpc410 |
| cpc410 | `0x432650` | cpc410 | 10 | bpiw201, cpc110, cpc420, cpc430 |
| cpc420 | `0x432510` | cpc420 | 7 | cpc120, cpc130, cpc140, cpc410, cpc430, cpc440 |
| cpc430 | `0x432410` | cpc430 | 6 | cpc410, cpc420, cpc440, cpc450 |
| cpc540 | `0x432310` | cpc540 | 5 | cpc350, cpc520, cpc530, cpc550 |
| cpc360 | `0x432280` | cpc360 | 2 | cpc350, cpc370 |
| cpc550 | `0x4321d0` | cpc550 | 3 | cpc530, cpc540, cpc730 |
| cpc370 | `0x432120` | cpc370 | 3 | cpc230, cpc360 |
| cpc230 | `0x431f90` | cpc230 | 8 | cpc220, cpc370, cpc520, espw101, espw102 |
| cpc520 | `0x431e90` | cpc520 | 5 | cpc220, cpc230, cpc510, cpc530, cpc540 |
| cpc530 | `0x431d70` | cpc530 | 7 | cpc510, cpc520, cpc540, cpc550 |
| cpc510 | `0x431c60` | cpc510 | 7 | cpc210, cpc520, cpc530 |
| cpc210 | `0x431880` | cpc210 | 8 | aie200, cpc220, cpc510 |
| cpc220 | `0x4317d0` | cpc220 | 3 | cpc210, cpc230, cpc520 |
| cpc710 | `0x431680` | cpc710 | 11 | cpc450, cpc720 |
| cpc730 | `0x431550` | cpc730 | 10 | cpc550, cpc720 |
| pne150 | `0x431430` | pne150 | 3 | lgaw101, lgaw102, pne140 |
| pne140 | `0x431050` | pne140 | 8 | pne130, pne150, pne210 |
| pne130 | `0x430fa0` | pne130 | 3 | pne120, pne140 |
| pne120 | `0x430f10` | pne120 | 2 | pne110, pne130 |
| pne210 | `0x430e20` | pne210 | 6 | pne140, pne220, pne230 |
| pne220 | `0x430cf0` | pne220 | 9 | pne210, pne240 |
| pne240 | `0x430bf0` | pne240 | 7 | pne220, pne230, pnew310 |
| pne230 | `0x430b20` | pne230 | 5 | pne210, pne240 |
| pne110 | `0x430a70` | pne110 | 3 | aio100, pne120 |
| pnew310 | `0x4308a0` | pnew310 | 19 | pne240 |
| ctp110 | `0x430770` | ctp110 | 9 | aio500, ctp310 |
| ctp310 | `0x4306a0` | ctp310 | 5 | ctp110, ctp320 |
| ctp320 | `0x4305a0` | ctp320 | 7 | ctp310, ctp330 |
| ctp330 | `0x4303c0` | ctp330 | 7 | ctp320, ctp340, spfw100, spfw101, spfw102 |
| ctp340 | `0x4302e0` | ctp340 | 6 | ctp330, ctp350 |
| ctp350 | `0x430200` | ctp350 | 5 | ctp210, ctp340 |
| ctp210 | `0x430070` | ctp210 | 9 | aie500, ctp350, lgew100 |
| lgew100 | `0x42ff60` | lgew100 | 4 | coffre, ctp210 |
| coffre | `0x42fec0` | - | 2 | cachwen1, lgew100 |
| natte | `0x42fe30` | - | 2 | lgew100 |
| cachwen1 | `0x42fd60` | - | 2 | cachwen2, cachwen3, lgew100 |
| cachwen2 | `0x42fcc0` | - | 1 | lgew100 |
| cachwen3 | `0x42fc40` | - | 1 | lgew100 |
| pdc005 | `0x42fbb0` | pdc005 | 2 | aie600b, pdc010 |
| pdc010 | `0x42f7b0` | pdc010 | 5 | pdc005, pdc011, pdc012, pdc110, pdc112 |
| pdc011 | `0x42f720` | pdc011 | 0 | pdc010 |
| pdc012 | `0x42f670` | pdc012 | 0 | pdc010 |
| pdc110 | `0x42f590` | pdc110 | 5 | pdc010, pdc120, pdc160 |
| pdc140 | `0x42f480` | pdc140 | 7 | pdc130, pdc150, pdc170 |
| pdc170 | `0x42f1c0` | pdc170 | 5 | pdc140, pdc178 |
| pdc178 | `0x42f140` | pdc178 | 0 | pdcw171 |
| pdc179 | `0x42f070` | pdc179 | 0 | pdc170 |
| pdc130 | `0x42efb0` | pdc130 | 4 | pdc110, pdc120, pdc140 |
| pdc150 | `0x42eef0` | pdc150 | 4 | pdc110, pdc140, pdc160 |
| pdc120 | `0x42ee10` | pdc120 | 6 | pdc110, pdc130 |
| pdc160 | `0x42ec00` | pdc160 | 8 | pdc110, pdc150, pdcw510 |
| pdcw510 | `0x42ead0` | pdcw510 | 10 | pdc160, pdcw520 |
| pdcw520 | `0x42e8d0` | pdcw520 | 21 | pdcw510 |
| pdc112 | `0x42e7f0` | pdc112 | 5 | pdc010, pdc122, pdc162 |
| pdc142 | `0x42e6e0` | pdc142 | 7 | pdc132, pdc152, pdc172 |
| pdc172 | `0x42e5f0` | pdc172 | 5 | pdc142 |
| bougies | `0x42e550` | - | 2 | lvierge, pdcw512 |
| lvierge | `0x42e4e0` | - | 0 | rebus |
| rebus | `0x42e480` | - | 1 | pdcw512 |
| pdc132 | `0x42e3c0` | pdc132 | 4 | pdc112, pdc122, pdc142 |
| pdc152 | `0x42e300` | pdc152 | 4 | pdc112, pdc142, pdc162 |
| pdc122 | `0x42e220` | pdc122 | 4 | jarre2, pdc112, pdc132 |
| jarre2 | `0x42e100` | - | 2 | pdc122, pierre2, pierre21, pierre22 |
| pierre2 | `0x42dff0` | - | 5 | jarre2, pierre21 |
| pierre21 | `0x42df60` | - | 1 | pierre22 |
| pierre22 | `0x42df00` | - | 1 | pdc122 |
| pdc162 | `0x42dac0` | pdc162 | 11 | arbre1, jarre1, pdc112, pdc152, pdc175, pdc176, pdc177, pdcw512 |
| pdc175 | `0x42da10` | pdc175 | 0 | pdc162 |
| pdc176 | `0x42d960` | pdc176 | 0 | pdc162 |
| pdc177 | `0x42d8b0` | pdc177 | 0 | pdc162 |
| jarre1 | `0x42d810` | - | 2 | pdc162, pierre1 |
| arbre1 | `0x42d760` | - | 3 | arbre2, pdc162 |
| arbre2 | `0x42d6a0` | - | 3 | arbre3, pdc162 |
| arbre3 | `0x42d5d0` | - | 2 | arbre2, pdc162 |
| fsceaux | `0x42d590` | - | 0 |  |
| pierre1 | `0x42d470` | - | 8 | jarre1 |
| pdcw171 | `0x42d3f0` | - | 3 | boite11, boite21, boite31 |
| boite11 | `0x42d350` | - | 2 | boite12, pdcw171 |
| boite12 | `0x42d270` | - | 4 | boite11, pdcw171 |
| boite21 | `0x42d1d0` | - | 2 | boite22, pdcw171 |
| boite22 | `0x42d130` | - | 3 | pdcw171 |
| boite31 | `0x42d090` | - | 2 | boite32, pdcw171 |
| boite32 | `0x42cfe0` | - | 2 | boite31, boite331 |
| boite33 | `0x42cf70` | - | 1 | origine |
| boite331 | `0x42cf00` | - | 1 | origine |
| origine | `0x42ce30` | - | 2 | pdc179 |
| penjing | `0x42cdf0` | - | 0 |  |
| penjing2 | `0x42cd60` | - | 1 | proclam |
| proclam | `0x42cbf0` | - | 2 | bpiw202 |
| pdcw512 | `0x42c7d0` | pdcw512 | 14 | lvierge, pdc162, pdcw522 |
| pdcw522 | `0x42c4e0` | pdcw522 | 20 | pdcw512, penjing2 |
| aie100 | `0x42c460` | aie100 | 2 | aie200, cgc160 |
| aie200 | `0x42c1f0` | aie200 | 6 | aie100, aie300, cpc210 |
| aie300 | `0x42c150` | aie300 | 3 | aie200, aie400 |
| aie400 | `0x42c0b0` | aie400 | 3 | aie300, aie500 |
| aie500 | `0x42bb00` | aie500 | 8 | aie400, aie600b, ctp210 |
| aie600b | `0x42b5c0` | aie600b | 7 | aie500, jixw110, jixw111, jixw112, pdc005 |
| bpiw100 | `0x42b490` | bpiw100 | 9 | bpiw200, cpc120 |
| bpiw200 | `0x42b320` | bpiw200 | 14 | bpiw100 |
| bpiw101 | `0x42b130` | bpiw101 | 19 | bpiw201, cpc120 |
| bpiw201 | `0x42a930` | bpiw201 | 25 | bpiw101 |
| bpiw102 | `0x42a790` | bpiw102 | 15 | bpiw202, cpc120 |
| bpiw202 | `0x42a1d0` | bpiw202 | 23 | bpiw102 |
| aio100 | `0x429f80` | aio100 | 8 | aio200, cgc120, pne110 |
| aio200 | `0x429d00` | aio200 | 7 | aio100, aio300, cpc110 |
| aio300 | `0x429c60` | aio300 | 3 | aio200, aio400 |
| aio400 | `0x429bc0` | aio400 | 3 | aio300, aio500 |
| aio500 | `0x4297e0` | aio500 | 7 | aio400, ctp110 |
| lgaw100 | `0x429730` | lgaw100 | 4 | pne150 |
| lgaw101 | `0x429080` | lgaw101 | 9 | meuble1, pne150 |
| lgaw102 | `0x428ea0` | lgaw102 | 6 | meuble1, pne150 |
| indice1 | `0x428dd0` | - | 2 | lgaw101 |
| confess1 | `0x428d20` | - | 2 | bouddha3 |
| bouddha2 | `0x428c90` | - | 2 | confess1 |
| bouddha3 | `0x428c00` | - | 2 | indice1 |
| meuble1 | `0x428b10` | - | 2 | lgaw101, lgaw102, meuble2 |
| meuble2 | `0x4287c0` | - | 7 | lgaw101, lgaw102, meuble1, meuble30, meuble31, meuble40, meuble41, meuble42, meuble43, meuble5 |
| meuble30 | `0x4286c0` | - | 5 | meuble2, meuble31 |
| meuble31 | `0x428630` | - | 2 | meuble2 |
| meuble40 | `0x4284e0` | - | 7 | meuble2, meuble41, meuble42 |
| meuble41 | `0x428400` | - | 4 | meuble2, meuble43 |
| meuble42 | `0x428310` | - | 5 | meuble2, meuble43 |
| meuble43 | `0x428280` | - | 2 | meuble2 |
| meuble5 | `0x428160` | - | 3 | bouddha2, meuble2, meuble5 |
| espw100 | `0x427fe0` | espw100 | 14 | cpc230, espw201 |
| espw101 | `0x427dc0` | espw101 | 15 | cpc230, espw201, go20 |
| espw200 | `0x427c50` | espw200 | 13 | espw100 |
| espw201 | `0x4272f0` | espw201 | 20 | espw101, table, table10 |
| table | `0x427210` | - | 3 | espw201, table, table10 |
| table10 | `0x4270f0` | - | 4 | espw201, table11 |
| table11 | `0x426f10` | - | 4 | table10, table12, table13, table14 |
| table12 | `0x426d90` | - | 3 | table10, table13, table14 |
| table13 | `0x426c10` | - | 3 | table10, table12, table14 |
| table14 | `0x426b20` | - | 1 | espw201 |
| espw102 | `0x426940` | espw102 | 14 | cpc230, espw202 |
| espw202 | `0x4267b0` | espw202 | 15 | espw102 |
| cgc110 | `0x426530` | cgc110 | 7 | bpiw202, cgc120, nwfw100, nwfw101, nwfw102 |
| cgc120 | `0x4263d0` | cgc120 | 12 | aio100, cgc110, cgc130 |
| cgc130 | `0x4262a0` | cgc130 | 9 | cgc120, cgc140, cgc310 |
| cgc140 | `0x426120` | cgc140 | 12 | cgc130, cgc150, cgc230, cgc310 |
| cgc150 | `0x425fe0` | cgc150 | 10 | cgc140, cgc160, cgc310 |
| cgc160 | `0x425ec0` | cgc160 | 9 | aie100, cgc150 |
| cgc210 | `0x425db0` | cgc210 | 8 | cgc230, cth380 |
| cgc220 | `0x425ca0` | cgc220 | 8 | cgc230, cth350 |
| cgc230 | `0x425b90` | cgc230 | 8 | cgc140, cgc210, cgc220 |
| cgc310 | `0x425a00` | cgc310 | 12 | cgc130, cgc140, cgc150, porte |
| porte | `0x425980` | - | 2 | cgc310, porte1 |
| porte1 | `0x4258e0` | - | 2 | porte, porte2 |
| porte2 | `0x425830` | - | 2 | bouton1, cgc310 |
| bouton1 | `0x425790` | - | 1 | bouton20, porte |
| bouton20 | `0x425710` | - | 1 | confess3 |
| bouton21 | `0x425690` | - | 1 | indice3 |
| confess3 | `0x4255e0` | - | 2 | bouton21 |
| confess2 | `0x4254c0` | - | 2 | bpiw101, go21 |
| indice2 | `0x4253c0` | - | 2 | espw101, go22 |
| indice3 | `0x4252b0` | - | 2 | cgc310 |
| go1 | `0x4251d0` | - | 2 | espw101, go20 |
| go20 | `0x425110` | - | 1 | confess2, indice2 |
| go21 | `0x425080` | - | 1 | indice2 |
| go22 | `0x425020` | - | 1 | bpiw101 |
| fight | `0x424e60` | - | 1 | bdaw100, nwfw100 |
| fight2 | `0x424de0` | - | 0 | fight |
| nwfw100 | `0x424c20` | nwfw100 | 7 | banw100, bdaw100, cgc110, fight2 |
| nwfw101 | `0x424af0` | nwfw101 | 4 | banw111, banw112, bdaw101, cgc110 |
| nwfw102 | `0x424a40` | nwfw102 | 3 | banw121, cgc110 |
| banw100 | `0x424920` | banw100 | 10 | nwfw100 |
| banw111 | `0x4247e0` | banw111 | 5 | banw112, nwfw101, registre |
| banw112 | `0x4246f0` | banw112 | 4 | nwfw101, registre |
| registre | `0x4245a0` | - | 2 | banw111, banw112, cahiers |
| cahiers | `0x4244c0` | - | 2 | banw111, banw112, lboites |
| lboites | `0x4243c0` | - | 2 | banw111, banw112 |
| banw121 | `0x424320` | banw121 | 4 | nwfw102 |
| banw122 | `0x424280` | banw122 | 4 | nwfw102 |
| bdaw100 | `0x4240d0` | bdaw100 | 12 | horloge2, nwfw100, pinceau |
| edit | `0x424000` | - | 2 | bdaw100 |
| plbombe | `0x423f80` | - | 1 | horloge3 |
| horloge1 | `0x423ef0` | - | 2 | bdaw100, horloge2 |
| horloge2 | `0x423e70` | - | 1 | plbombe |
| horloge3 | `0x423e00` | - | 1 | edit |
| pinceau | `0x423d60` | - | 4 | bdaw100 |
| bdaw101 | `0x423950` | bdaw101 | 7 | nwfw101 |
| spfw100 | `0x4237d0` | spfw100 | 15 | ctp330 |
| spfw101 | `0x4234d0` | spfw101 | 17 | ctp330 |
| spfw102 | `0x423300` | spfw102 | 14 | ctp330 |
| jixw111 | `0x423210` | jixw111 | 3 | aie600b, jixw121 |
| jixw121 | `0x422f90` | jixw121 | 12 | jixw111 |
| jixw131 | `0x422ee0` | jixw131 | 3 | jixw121, jixw210 |
| posthum | `0x422e00` | - | 2 | jixw111 |
| confess4 | `0x422d50` | - | 2 | puzzle43 |
| indice4 | `0x422cc0` | - | 1 | jixw210 |
| jixw110 | `0x422c10` | jixw110 | 3 | aie600b, jixw120 |
| jixw120 | `0x422ac0` | jixw120 | 3 | jixw110, victime |
| jixw130 | `0x422a10` | jixw130 | 3 | jixw120, jixw210 |
| jixw112 | `0x422930` | jixw112 | 3 | aie600b, jixw122 |
| victime | `0x422880` | - | 0 | jixw210 |
| jixw122 | `0x4227d0` | jixw122 | 3 | jixw112, jixw132 |
| jixw132 | `0x422530` | jixw132 | 5 | jixw122, jixw210 |
| jixw210 | `0x422420` | jixw210 | 2 | jixw132, soupir |
| soupir | `0x422130` | - | 7 | jixw210, soupir2 |
| soupir2 | `0x422030` | - | 2 | jixw210, puzzle42 |
| puzzle41 | `0x421ff0` | - | 0 |  |
| puzzle42 | `0x421f70` | - | 1 | confess4 |
| puzzle43 | `0x421f00` | - | 1 | indice4 |
