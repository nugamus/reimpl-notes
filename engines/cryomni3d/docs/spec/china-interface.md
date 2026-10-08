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
  are here: the current place's position from the table at 0x452040, 264-byte records
  keyed by the first three letters of the place name, or the full-name table 0x452fb8).
- Moving the cursor over the small map (x 435..578, y 79..312) scrolls the big map:
  x offset (mx-435)*846/267 (0..473), y offset (my-79)*1228/391 (0..747).
- Hot spots of the big map (table 0x45af38, 9 dwords each, offsets subtracted): hover
  shows the label text at x 380, y 425 and the cursor 8 (travel), 15 (documentation) or
  11 (type 7). A click on a travel spot (subject to game variables 0, 0x18, 0x19, 0xcc,
  0x7c for three special places, Q-1100) goes there (goto 0x41f190) and closes both the
  map and the bar without the slide-out: the player can travel by the map. A click on a
  type-8 spot opens the documentation base on that spot's entry, then re-enters the
  current place.
- Buttons: `spirs.spr` (387, 449) leaves the map back to the bar; `ico_bat.spr`
  (587, 449) runs 0x401fb0 (Q-1100).

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
