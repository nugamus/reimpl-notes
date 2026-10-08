# China: the interface bar (inventory, documents, notebook, map)

Not a full screen: a 65-row bar over the bottom of the current frame (y 415..479), with
the inventory row and five buttons. `Interface.cpp` 0x40efd0 (entry), 0x40f070 (loop).
Coordinates are screen pixels (640x480, 16-bit).

## Opening and closing

- Opened from the frame loop by Space (after its release; the display is redrawn first)
  or the right button with the latch 0x48f2a0 clear; also from inside two puzzles
  (0x419830, 0x41d630; the latter only while object 21 CIRE is not in the inventory)
  (E-0955, E-1100).
- The right-button latch 0x48f2a0 is only ever cleared (on right release), never set:
  in practice "right button down" opens, and a right button still down when the bar's
  loop starts closes it again (E-1100). An engine should use a proper press edge.
- Open: copy the current frame; rebuild the slot table (Inventory below); cut rows
  415..479 and blend every pixel halfway towards the colour 0x39CA (RGB565; 0x1CEA in
  RGB555), per channel (E-1100). Then 16 frames: frame k (0..15) shows the blended band
  rows from 479-4k down to 479 and the bar's sprites drawn 64-4k rows lower than their
  place. Afterwards the band is drawn whole at 415..479 every frame.
- Every frame: the saved frame, the band, the bar sprites (Layout), the hover label, the
  cursor; music ticks.
- Closes on: Space down; the right button down (latch above); the exit spiral; an object
  held and the cursor moved above y 400 after it had once been below y 400 (to use the
  object on the scene; the object stays held); or a map journey. Except after a map
  journey, the band slides out in 17 frames (64, 60, .. 0 rows visible, sprites lower by
  the same amount) (E-1100).
- The entry returns a flag: 0 if the exit spiral was clicked, else 1. The frame loop
  then sets the skip-cross-fade flag 0x48f1ec (the next warp draw is a plain draw,
  E-0903); the puzzles leave the puzzle when it is 0 (E-1100).

## Layout

Every bar sprite carries its own screen position in its SPR image ID (`unk_16` = x,
`unk_1a` = y, E-1101); files in `DATA/INVENT/`:

| Sprite | Size | Position | Role |
|---|---|---|---|
| `spirsort.spr` | 26x26 | 11, 442 | exit spiral: hidden in puzzle mode (0x48f2a8) unless the current place is `jixw210` |
| `oeil.spr` | 26x26 | 72, 442 | eye: read the held document |
| `cadres.spr` | 477x36 | 111, 437 | the ten slot frames |
| `bnote.spr` | 26x24 | 603, 426 | notebook: hidden and inert while game variable 0 is set |
| `bouss.spr` | 26x23 | 603, 450 | compass (map): only outside puzzle mode and in warp display (0x48f200 = 1) |

Draw order: puzzle-supplied sprites (list 0x4ff9e8, count 0x4ffa28, at their own
positions; Q-1103), frames, slot objects, notebook, compass, spiral, eye (E-1101).

## Inventory

- Ten slots, no scrolling: slot i at x 111+49i, y 437, the object's `c_` sprite
  (36x36). Hit box: x strictly between 111+49i and 149+49i, y strictly between 437
  and 475 (E-1102). (The `fl_*` arrows belong to the notebook and the documentation
  base, not here.)
- On opening (0x40ff30): slots cleared; every object in state 2 with a slot goes to that
  slot; every object in state 2 without one (slot -1) takes the first free slot; the
  object in state 1 becomes held (its `r_` sprite the cursor); objects not in state 2
  lose their slot (E-1102).
- Left click (press edge, latch 0x48f29c) on slot i:
  - hand empty, slot full: the object is taken: state 1, slot -1, held, `r_` cursor;
  - hand full, slot empty: put back: state 2, slot i, hand empty (cursor 11);
  - both full: swapped (the held one into the slot, the slot's one held).
- Hover on a full slot: the object's label (LABELS.TXT key at +0x2c) at x 3, y 415 in
  white, joined to the slot by a line in colour 0xF520: across at y 428 from x 3 to the
  slot centre (130+49i), then down to y 437 (E-1102).
- Over the eye with a held object that has an `i_` sprite: the cursor becomes the `i_`
  sprite (objects 0..18, the documents); elsewhere the held `r_` sprite.

## Documents

Click on the eye with a held object that has an `i_` sprite (E-1103):
1. Show the still `Images\<key>` (key = object +0x20, `lboites`, `origine`, ...; the
   still loader 0x402e20 tries its extensions; display mode becomes still).
2. Unless the object is 1 (ORIGINAUX), play `loc\voices\<key>` on sound channel 10.
3. Until a left click: redraw the still with the held cursor, plus the LABELS.TXT text
   for `<key>` (if any) in black, font 1, wrapped to the box width, 15-px lines, inside
   a per-object box (x0, y0, x1, y1) from 0x45c9a8: 0 (10,10,275,350), 1 (10,10,200,50),
   2 (10,270,500,470), 3 (10,10,160,300), 4 (10,10,330,300), 5 and 6 (10,10,275,300),
   7 (200,10,400,50), 8 (10,300,200,400), 9 (10,400,275,500), 10 (100,10,300,50),
   11 (10,10,275,250), 12 and 13 (10,10,400,300). Objects 14..18 have no entry (Q-1101).
4. Restore the saved frame, stop channel 3 (Q-1101), put the object back in the first
   free slot, hand empty, and re-enter the current place (0x41f170): the bar stays open.

## Notebook

Click on `bnote` (while game variable 0 is clear) opens the minutes screen (E-1104):
- Background: the still `Fond` (DATA/INTERF); sprites in `DATA/INTERF/`: exit
  `som_spir.spr` (21, 435; `i_sprinv.spr` when hovered), up arrow `fl_hautr.spr`
  (138, 54; `fl_hautj.spr` when active), down arrow `fl_basr.spr` (138, 405;
  `fl_basj.spr` when active).
- Content: for each MINUTES.TXT key held (added by 0x411d80, kept in the save,
  E-0202), in the order added, its text wrapped at 400 px into lines (at most 41
  entries counted). 22 lines shown from x 180, y 80; it opens scrolled to the end.
- Scrolling: hovering an arrow moves one line every 10 ticks of the timer 0x416c90 while
  there is more in that direction; the arrow shows its active sprite meanwhile.
- Leaves on a click on the exit or Escape; back to the bar. Text drawing details: Q-1104.

## Map

Click on the compass (warp display, not puzzle mode) opens `carte.cpp`'s map (E-1105):
- Left 373 columns: a 373x480 window on `granplan.tga` (846x1228). Right x 373..639:
  `petiplan.tga` (267x480) with `cadre.spr` (the window's frame) and `point.spr` (you
  are here).
- **You are here** (E-1150): the current place name is looked up in two tables of
  (name, x, y): first the prefix table (the first three letters of the place name; the last
  match wins), then the full-name table (exact name; a match overrides). `point.spr` is
  drawn with its top-left at (x + 373 - 2, y - 2). No match in either table: the original
  draws at an uninitialised position; draw no marker. On opening, the window is scrolled
  as if the cursor were on the marker.
- Moving the cursor over the small map (x 373..639 and y 0..386; clamped to x 435..580,
  y 79..312) scrolls the big map: x offset (mx-435)*846/267 (0..473), y offset
  (my-79)*1228/391 (0..747). `cadre.spr` is drawn at (mx - 62, my - 79) of the clamped
  point (E-1105, E-1151).
- **Hot spots** (95 records at 0x45af38, 36 bytes = 9 LE dwords: top, left, bottom, right
  in `granplan` coordinates (inclusive; on screen subtract the scroll offsets, only while
  the cursor is at x <= 373), the label text (filled at start-up from LABELS.TXT by the
  key; ` pas de label ` when the key has none), the LABELS.TXT key, type, a pointer to
  {target place name, view angle float}, `unk_8`) (E-1150, E-1151). Each frame the cursor
  is set to 11; under the first spot that contains the cursor the label is drawn in white
  (0xffff) at x 380, y 425 (if it is ` pas de label `, the key follows it on the same
  line), and the cursor becomes 8 for a type 0 spot whose travel is allowed, 15 for type
  8, 11 for type 7.
  - Type 0, travel: allowed always if variable 0 is non-zero; otherwise allowed unless the
    target is `cpc600` (needs variable 0x18 or 0x19 non-zero), `ctp330` (needs 0xcc) or
    `pdc010` (needs 0x7c). A click on an allowed spot looks the place up (0x41f680); if
    found, the next place starts at that view angle (alpha = the float, beta = 0), the
    scene changes to it (0x41f190) and the map returns "travelled" (closes the bar without
    the slide-out). A forbidden spot does nothing.
  - Type 8, documentation: a click opens the documentation base on the spot's key
    (0x40c5a0), then re-enters the current place (0x41f170) and the map stays open.
  - Type 7: label only.
- **Buttons** (rects from each sprite's position and size): `spirs.spr` (387, 449) leaves
  the map ("not travelled") back to the bar; `ico_bat.spr` (587, 449) opens the building
  list (E-1152). There is no keyboard exit. On leaving, the building-list image is freed.
- **Building list** (`ico_bat`, 0x401fb0, E-1152): ten LABELS.TXT keys (list ends early at
  the first key with no label). The list is pre-rendered: white (0xffff) background, rows
  font height + 5 high, labels in 0x7000 at x 5 of the row, first key in the bottom row;
  width = widest label rounded up to a multiple of 4, plus 10. It rises from y 440 with its
  left edge at 501 - width/2, 4 pixels per frame (Q-1150), over a saved copy of the map
  screen. While open, the row under the cursor (x 502 - w/2 .. 511 + w/2) is filled with
  0x7000 and its label redrawn in white at x 506 - w/2. A click anywhere closes it; a click
  on a row first moves the small-map point to that building's position and scrolls the big
  map from it with the same formulas (no clamping). Closing sinks it 4 pixels per frame.

Tables (game data, dumped by `tools/china_map.py`; `--selftest` checks the counts):

Prefix table 0x452040 (first three letters of the place name):

| place | x, y | place | x, y | place | x, y | place | x, y | place | x, y | place | x, y | place | x, y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `shs` | 132, 205 | `shm` | 132, 118 | `shp` | 132, 160 | `poc` | 132, 127 | `ptt` | 132, 66 | `spf` | 132, 79 | `ppc` | 132, 91 |
| `nwf` | 100, 135 | `ban` | 100, 135 | `esp` | 144, 127 | `lga` | 86, 116 | `bda` | 100, 135 | `pdc` | 164, 50 | `bpi` | 115, 122 |

Full-name table 0x452fb8 (checked after the prefix table; a match wins):

| place | x, y | place | x, y | place | x, y | place | x, y | place | x, y | place | x, y |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `pne310` | 96, 105 | `pne210` | 96, 113 | `pne220` | 91, 111 | `pne230` | 101, 111 | `pne240` | 96, 111 | `pne110` | 107, 115 |
| `pne120` | 107, 117 | `pne130` | 104, 117 | `pne140` | 96, 117 | `pne150` | 89, 117 | `jixw120` | 143, 31 | `jixw121` | 143, 31 |
| `jixw122` | 143, 31 | `jixw130` | 143, 28 | `jixw131` | 143, 28 | `jixw132` | 143, 28 | `jixw110` | 143, 35 | `jixw111` | 143, 35 |
| `jixw112` | 143, 35 | `jixw210` | 143, 23 | `cpc110` | 115, 155 | `cpc120` | 115, 120 | `cpc130` | 115, 125 | `cpc140` | 121, 125 |
| `cpc210` | 150, 115 | `cpc220` | 150, 125 | `cpc230` | 147, 125 | `cpc310` | 127, 125 | `cpc320` | 127, 122 | `cpc330` | 129, 122 |
| `cpc340` | 132, 122 | `cpc350` | 136, 122 | `cpc360` | 139, 122 | `cpc370` | 139, 125 | `cpc410` | 119, 115 | `cpc420` | 119, 120 |
| `cpc430` | 123, 115 | `cpc440` | 129, 120 | `cpc450` | 129, 110 | `cpc510` | 147, 115 | `cpc520` | 147, 120 | `cpc530` | 142, 115 |
| `cpc540` | 136, 120 | `cpc550` | 136, 110 | `cpc600` | 132, 115 | `cpc710` | 129, 100 | `cpc720` | 132, 100 | `cpc730` | 136, 100 |
| `aio100` | 112, 127 | `aio200` | 112, 115 | `aio300` | 112, 104 | `aio400` | 112, 91 | `aio500` | 112, 77 | `aie100` | 152, 127 |
| `aie200` | 152, 115 | `aie300` | 152, 104 | `aie400` | 152, 91 | `aie500` | 152, 77 | `aie600b` | 152, 60 | `ctp110` | 121, 77 |
| `ctp310` | 128, 77 | `ctp320` | 128, 82 | `ctp330` | 132, 82 | `ctp340` | 137, 82 | `ctp350` | 137, 77 | `ctp210` | 143, 77 |
| `cgc110` | 100, 135 | `cgc120` | 115, 140 | `cgc130` | 123, 140 | `cgc140` | 132, 140 | `cgc150` | 141, 140 | `cgc160` | 152, 137 |
| `cgc210` | 117, 153 | `cgc220` | 147, 153 | `cgc230` | 132, 153 | `cgc310` | 132, 135 | `chs010` | 132, 214 | `chs110` | 117, 211 |
| `chs120` | 124, 214 | `chs130` | 132, 214 | `chs140` | 141, 214 | `chs150` | 148, 211 | `chs240` | 124, 218 | `chs210` | 124, 222 |
| `chs220` | 132, 222 | `chs230` | 141, 222 | `chs250` | 132, 218 | `chs260` | 141, 218 | `cth110` | 147, 203 | `cth120` | 147, 198 |
| `cth130` | 142, 197 | `cth140` | 133, 197 | `cth150` | 123, 197 | `cth160` | 132, 197 | `cth170` | 118, 203 | `cth210` | 132, 191 |
| `cth220` | 132, 188 | `cth230` | 139, 188 | `cth240` | 139, 182 | `cth250` | 139, 174 | `cth260` | 132, 174 | `cth270` | 126, 174 |
| `cth280` | 126, 182 | `cth290` | 126, 188 | `cth310` | 132, 174 | `cth320` | 132, 168 | `cth330` | 139, 168 | `cth340` | 149, 168 |
| `cth350` | 149, 164 | `cth360` | 125, 168 | `cth370` | 117, 168 | `cth380` | 117, 164 | `cth410` | 139, 182 | `cth420` | 151, 182 |
| `cth430` | 155, 182 | `cth440` | 161, 182 | `cth450` | 161, 175 | `cth510` | 126, 182 | `cth520` | 115, 182 | `cth530` | 111, 182 |
| `cth540` | 105, 182 | `cth550` | 105, 175 |  |  |  |  |  |  |  |  |

| # | top, left, bottom, right | key | type | target place (view angle) | unk_8 |
|---|---|---|---|---|---|
| 0 | 416, 295, 433, 305 | `NWF` | 0 | `cgc110` (3.13) |  |
| 1 | 394, 459, 412, 477 | `ESP` | 0 | `cpc230` (4.73) |  |
| 2 | 378, 355, 395, 372 | `BPI` | 0 | `cpc120` (2.40) |  |
| 3 | 694, 410, 709, 434 | `CHS` | 0 | `chs220` (1.51) | 18 |
| 4 | 647, 407, 671, 444 | `SHS` | 0 | `shs140` (1.56) | 18 |
| 5 | 594, 413, 617, 435 | `SHM` | 0 | `cth220` (1.56) | 18 |
| 6 | 525, 413, 547, 435 | `SHP` | 0 | `cth310` (1.51) | 18 |
| 7 | 429, 407, 453, 438 | `POC` | 0 | `cgc140` (3.13) |  |
| 8 | 355, 287, 378, 321 | `PNE` | 0 | `pne140` (1.57) |  |
| 9 | 348, 410, 370, 435 | `CPC` | 0 | `cpc600` (1.50) |  |
| 10 | 255, 413, 274, 436 | `SPF` | 0 | `ctp330` (1.60) | 10 |
| 11 | 100, 443, 141, 476 | `JIX` | 0 | `aie600b` (1.73) |  |
| 12 | 171, 519, 190, 541 | `PDC` | 0 | `pdc010` (0.07) | 6 |
| 13 | 416, 305, 433, 317 | `NWF` | 8 |  |  |
| 14 | 1054, 378, 1091, 463 | `CRE` | 8 |  |  |
| 15 | 1054, 350, 1178, 378 | `PDM` | 7 |  |  |
| 16 | 1054, 464, 1178, 492 | `PDM` | 7 |  |  |
| 17 | 870, 391, 902, 453 | `PHS` | 8 |  |  |
| 18 | 869, 311, 1049, 532 | `CRE` | 7 |  |  |
| 19 | 741, 534, 796, 558 | `PBA` | 7 |  |  |
| 20 | 742, 286, 795, 308 | `PNR` | 7 |  |  |
| 21 | 623, 385, 671, 461 | `SHS` | 8 |  |  |
| 22 | 557, 408, 588, 438 | `SHM` | 8 |  |  |
| 23 | 490, 394, 521, 453 | `SHP` | 8 |  |  |
| 24 | 430, 293, 466, 312 | `PAG` | 7 |  |  |
| 25 | 431, 535, 467, 553 | `PFS` | 7 |  |  |
| 26 | 393, 405, 412, 441 | `POC` | 8 |  |  |
| 27 | 418, 313, 427, 346 | `GDC` | 8 |  |  |
| 28 | 313, 261, 380, 344 | `PNE` | 8 |  |  |
| 29 | 272, 396, 302, 453 | `PPC` | 8 |  |  |
| 30 | 234, 413, 255, 436 | `SPF` | 8 |  |  |
| 31 | 197, 396, 225, 453 | `PTT` | 8 |  |  |
| 32 | 63, 350, 161, 500 | `JIX` | 8 |  |  |
| 33 | 0, 399, 35, 453 | `PGM` | 7 |  |  |
| 34 | 131, 503, 186, 556 | `PPF` | 7 |  |  |
| 35 | 189, 503, 243, 556 | `PRC` | 7 |  |  |
| 36 | 247, 503, 306, 556 | `PBS` | 7 |  |  |
| 37 | 131, 564, 186, 617 | `PYS` | 7 |  |  |
| 38 | 189, 564, 243, 617 | `PHE` | 7 |  |  |
| 39 | 247, 564, 306, 617 | `PBE` | 7 |  |  |
| 40 | 65, 503, 128, 663 | `CLN` | 7 |  |  |
| 41 | 257, 620, 306, 658 | `MDS` | 7 |  |  |
| 42 | 200, 620, 253, 658 | `MDS` | 7 |  |  |
| 43 | 136, 632, 153, 667 | `PSMC` | 7 |  |  |
| 44 | 313, 501, 391, 554 | `PDJ` | 7 |  |  |
| 45 | 313, 594, 379, 657 | `SCA` | 7 |  |  |
| 46 | 129, 231, 183, 285 | `PBU` | 7 |  |  |
| 47 | 188, 231, 248, 285 | `PPE` | 7 |  |  |
| 48 | 249, 231, 302, 285 | `SPA` | 7 |  |  |
| 49 | 130, 293, 189, 346 | `PEA` | 7 |  |  |
| 50 | 191, 293, 242, 346 | `PAE` | 7 |  |  |
| 51 | 247, 293, 305, 346 | `PLE` | 7 |  |  |
| 52 | 256, 178, 282, 199 | `PFP` | 8 |  |  |
| 53 | 387, 261, 397, 344 | `OCI` | 7 |  |  |
| 54 | 194, 177, 210, 199 | `SFP` | 7 |  |  |
| 55 | 140, 210, 153, 230 | `JFG` | 7 |  |  |
| 56 | 62, 158, 130, 231 | `JJFG` | 7 |  |  |
| 57 | 64, 275, 124, 308 | `PFP` | 7 |  |  |
| 58 | 64, 241, 124, 273 | `SVP` | 7 |  |  |
| 59 | 43, 12, 122, 51 | `TRC` | 7 |  |  |
| 60 | 79, 98, 100, 134 | `SFE` | 7 |  |  |
| 61 | 196, 100, 219, 131 | `PLP` | 7 |  |  |
| 62 | 374, 86, 394, 117 | `PSE` | 7 |  |  |
| 63 | 397, 152, 427, 200 | `PTC` | 7 |  |  |
| 64 | 310, 72, 656, 246 | `PJID` | 7 |  |  |
| 65 | 908, 0, 962, 26 | `PFO` | 7 |  |  |
| 66 | 852, 155, 880, 198 | `SBM` | 7 |  |  |
| 67 | 1023, 97, 1039, 205 | `MDL` | 7 |  |  |
| 68 | 986, 85, 1000, 110 | `SPS` | 7 |  |  |
| 69 | 223, 787, 242, 811 | `PSA` | 8 |  |  |
| 70 | 200, 729, 255, 774 | `SNC` | 8 |  |  |
| 71 | 141, 729, 174, 774 | `HLJ` | 7 |  |  |
| 72 | 111, 733, 133, 771 | `CHP` | 7 |  |  |
| 73 | 81, 734, 96, 770 | `PFA` | 7 |  |  |
| 74 | 66, 789, 75, 818 | `PFB` | 7 |  |  |
| 75 | 64, 775, 77, 788 | `PSB` | 7 |  |  |
| 76 | 209, 700, 220, 715 | `CFP` | 7 |  |  |
| 77 | 168, 697, 181, 717 | `HIA` | 7 |  |  |
| 78 | 92, 705, 111, 725 | `PER` | 7 |  |  |
| 79 | 65, 685, 254, 729 | `JQL` | 7 |  |  |
| 80 | 384, 734, 400, 769 | `POT` | 7 |  |  |
| 81 | 306, 723, 334, 780 | `SPI` | 7 |  |  |
| 82 | 274, 725, 295, 779 | `PLT` | 7 |  |  |
| 83 | 1018, 579, 1036, 597 | `GDS` | 7 |  |  |
| 84 | 1018, 615, 1036, 669 | `AGS` | 7 |  |  |
| 85 | 1018, 671, 1036, 724 | `MDA` | 7 |  |  |
| 86 | 910, 611, 929, 648 | `PFL` | 7 |  |  |
| 87 | 856, 608, 882, 650 | `SFL` | 7 |  |  |
| 88 | 825, 609, 846, 650 | `SPS` | 7 |  |  |
| 89 | 782, 607, 801, 651 | `PEL` | 7 |  |  |
| 90 | 986, 793, 1016, 810 | `LGI` | 7 |  |  |
| 91 | 908, 818, 963, 844 | `PFE` | 7 |  |  |
| 92 | 537, 684, 659, 796 | `TLS` | 7 |  |  |
| 93 | 541, 643, 658, 656 | `OTC` | 7 |  |  |
| 94 | 544, 579, 564, 614 | `KTC` | 7 |  |  |

| row (bottom first) | key | point x, y |
|---|---|---|
| 0 | `SHS` | 506, 252 |
| 1 | `ESP` | 520, 157 |
| 2 | `PNE` | 468, 135 |
| 3 | `SPF` | 506, 95 |
| 4 | `JIX` | 517, 79 |
| 5 | `PPF` | 539, 100 |
| 6 | `CPC` | 506, 140 |
| 7 | `BPI` | 487, 150 |
| 8 | `POC` | 506, 157 |
| 9 | `NWF` | 470, 165 |

## Documentation base

Not reachable from the bar itself. Entered from the main menu's documentation entry
(0x407140 -> 0x4085d0, the contents screen: background `fond_som`, theme icons
`som_ying`, `som_tron`, `som_the`, `som_pinc`, `som_boul`, `som_arch`, `som_pers`,
`som_lieu`, exit `som_spir`, arrows `fl_hajau`/`fl_bajau`/`fl_hablc`/`fl_bablc`, index
`ico_indx`, highlights `i_indinv`/`i_sprinv`), from documentation zones (0x41f430
type 8, E-0903) and from map type-8 spots; the fiche screen 0x40c5a0 uses one of eight
backgrounds `fondbeig..fondviol` (0x40b7e0) and the `ico_*`/`fl_*` sprites (0x40b8e0);
data from Fichetxt.txt and Liste.txt (E-0203, E-0204). Behaviour: Q-1102 (E-1106).

## Other buttons

There are no save or menu buttons on the bar; saving and the menu are reached by Escape
in the frame loop (E-0508). The exit spiral puts any held object back in the first free
slot, empties the hand and closes the bar with result 0 (E-1100).
