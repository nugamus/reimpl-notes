# China: zones, cursors, clicks and the place API

How *China: The Forbidden City* (`CHINE.EXE`) turns the mouse into navigation: the zone
list a place builds, the cursor and label shown on hover, what a click does, and the
calls a place procedure makes. Places themselves (procedures, messages 1/2/3/0, names)
are in `games/china/docs/places.md` (E-0700..E-0705); the warp view in `china-warp.md`.

## Zones

- At most 40 per place, tested in creation order, first hit wins (E-0701). Record:
  rect {top, left, bottom, right} (inclusive), disabled (1 = off), type, target, arg,
  alpha, beta (E-0701, E-0904).
- Coordinates: in a warp, warp-image pixels (x 0..2047, y 0..767 as returned by the
  screen-to-image mapping, E-0604); in a still (close-up), screen pixels 0..639 x 0..479
  with no projection (E-0906).
- The point tested is the cursor's hot point (E-0901). A disabled zone counts as no zone.
- Creating (E-0904):

| Call | Arguments | Type | Visit mode (variable 0 != 0) |
|---|---|---:|---|
| go | rect, disabled, target procedure, arg, alpha, beta | 0 | as given |
| look | rect, disabled, target procedure, arg | 2 | created disabled |
| take | rect, disabled, target procedure | 4 | created disabled |
| use | rect, disabled | 6 | created disabled |
| label | rect, disabled, LABELS.TXT key | 7 | as given; outside visit mode always disabled |
| doc | rect, disabled, documentation key | 8 | as given |
| talk | rect, disabled | 9 | created disabled |

  Alpha/beta are radians; -1 (and every non-go zone) means "keep the view". arg is 0 in
  all data (E-0903). Label and doc keys are looked up in LABELS.TXT case-insensitively at
  creation (E-0902).
- Reset empties the list. Disable(i) sets the flag. Enable(i) clears it, except in visit
  mode for use, label and talk zones, which then stay as they are (E-0904).

## Hover

Every frame, in this order (E-0508, E-0900, E-0901):

1. Mouse: the cursor's top-left moves by the relative motion, clamped to 0..640-w and
   0..480-h (start 320, 240).
2. Default cursor. In a warp, from the top-left (x, y):

   | | y < 100 | 100..380 | y > 380 |
   |---|---|---|---|
   | x < 100 | 4 `tri315` | 0 `tri270` | 7 `tri225` |
   | 100..540 | 2 `tri0` | held object's cursor, else 11 `ptroug` | 3 `tri180` |
   | x > 540 | 5 `tri45` | 1 `tri90` | 6 `tri135` |

   In a still: the held object's cursor, else 11.
3. Zone under the hot point.
4. The place's event part calls the zone handler, which clears the label, then over an
   enabled zone (and not on a press frame, below) sets:

   | Type | Cursor | Label |
   |---:|---|---|
   | 0 go | 8 `doigt` in a warp, 12 `doigt` in a still | |
   | 2 look | 9 `voir` | |
   | 4 take | 10 `prendre`; held object's cursor if holding one | |
   | 6 use | 14 `util`; held object's cursor if holding one | |
   | 7 label | unchanged (step 2) | LABELS.TXT text |
   | 8 doc | 15 `interrog` with empty hands; unchanged when holding | the entry's title (LABELS.TXT text for its key), empty hands only |
   | 9 talk | 16 `bouche` | |

Sprite table (`DATA/SPRITES/CURSEURS/<name>.SPR`, E-0901): 0 tri270, 1 tri90, 2 tri0,
3 tri180, 4 tri315, 5 tri45, 6 tri135, 7 tri225, 8 doigt, 9 voir, 10 prendre, 11 ptroug,
12 doigt, 13 inter, 14 util, 15 interrog, 16 bouche, 17 pointact.

Hot point (E-0901): the files' hot fields are ignored for these cursors, so the hot point
is the sprite centre (w/2, h/2, integer halves), except `inter` (1, 45). The held
object's cursor is its `r_` sprite (30x30, centre). The cursor is drawn at its top-left.
In a still, changing the cursor shifts the top-left by the size difference (E-0901).

Label (E-0902), warps only (not drawn over stills):
- Position from the cursor's top-left at hover: x = cx + 20, y = cy + 20. If
  x + width + 2 >= 640, x = 638 - width. Not drawn unless y + 20 < 479.
- Box: 15 rows, width + 1 columns at (x - 2, y - 2), each pixel halfway towards
  (10, 10, 10) in 5-bit channels (on a 565 screen the original only halves red and green;
  quirk, invisible enough to ignore).
- Text: font slot 0 (FONT01), width measured with slot 0; black at (x + 1, y + 1), then
  white 0xFFFF at (x, y). Text drawing is E-0801.
- Missing key: "ACCES LEGENDE INCONNU" / "ACCES BASE DOCUMENTAIRE INCONNU"; four label
  keys of the data are missing (Q-0900).

## Click and transitions

- A click is the first frame the left button is down while the press latch is clear;
  the latch clears whenever the button is up (E-0900). On hover frames the handler sets
  the clicked index to -1, so the place's code sees a zone only on the press frame.
- Press, by type (E-0900):
  - 0 go, 2 look, 4 take: set the latch. In a warp: turn towards the cursor's top-left
    (`turnToPoint`, 32 frames, E-0606), then `zoomIn(arg)` (arg is 0 in all data: no zoom
    frames, only the field of view reset, E-0903), then, if the zone's alpha >= 0, set the
    view to the zone's alpha and beta (only go zones carry angles; 93 of 609). In a still:
    none of this. Then, if the target is set, go there (handler returns 1); if not, the
    zone index is left for the place's code.
  - 6 use: set the latch; the place's code reacts (index left).
  - 8 doc with empty hands: open that documentation entry, then re-enter the current place
    (its entry part runs again). Holding an object: nothing.
  - 7 label, 9 talk: no latch, index left: the place's code sees the zone on every frame
    while the button stays down (talk zones start a dialogue, which blocks, and are then
    usually disabled).
- Goto (E-0903, E-0700): records the target as current, marks its entry pending, sets the
  display to nothing (the screen keeps its last frame), clears the clicked index, and
  switches music by the name. Next tick the target's entry runs.
- Warp load (E-0903): sets warp display and a cross-fade flag. The next draw is a
  cross-fade, 19 frames: old = the screen as last shown, new = the new warp rendered at
  the current angles. Frame k = 1..19 writes only every other column (odd columns on odd
  k, even on even k), each channel = old - (old - new) x min(16k, 256) / 256; the other
  columns keep the previous frame. Frames 16 and 17 complete the two column sets; 18 and
  19 repeat. No timer (one frame per loop, like the rest, E-0804). Skipped once after
  returning from the interface screen.
- Re-entering (doc zones, `0x41f170`) is a goto to the current place: the entry part
  rebuilds the zones and reloads the warp, so it cross-fades too.

## Place API

Calls a procedure makes (E-0703; arguments E-0904, E-0905, E-0906):

| Call | Effect |
|---|---|
| zones reset | empty the zone list |
| zone add (go/look/take/use/label/doc/talk) | Zones table above |
| zone enable(i) / disable(i) | Zones above |
| warp(name) | load `DATA/WARP/<name>.HNM`, warp display, cross-fade pending |
| image(name) | still display (close-up), lookup order E-0510; zones are screen pixels |
| video(name) | pause music, play `DATA/HNM/<name>.HNS`, blocking, skippable by Escape or left click, resume music |
| set angles(alpha, beta) | view angles for the next warp draw (also what a go zone's angles do) |
| goto(proc) | Click and transitions above |
| screen fade | blend the current screen to black with the cross-fade step (19 frames) |
| zone handler | Hover and Click above; returns 1 when it went somewhere |
| sound queue(name) / play-wait(name) / stop | Sounds below (E-0950) |
| voice(block) | voice-only DIAL.TXT chain over the place, Dialogues below (E-0951) |
| dialogue(block, stemA, stemB) | lip-sync dialogue, full-screen faces, Dialogues below (E-0952) |
| puzzle(n, m) | run puzzle n, blocking; returns its result, Puzzles below (E-0953) |
| in inventory(o) | object o's state is 2 (E-0954) |
| set label(o, key) | object o's LABELS.TXT name key (+0x2c) becomes key (E-0954) |
| set examine place(o, name) | object o's examine place (+0x20, a place procedure name) becomes name (E-0954) |
| key down(k) | DirectInput key k is down (1 Escape, 0x39 Space) (E-0954) |
| epilogue | the ending stills, Endings below (E-0954) |
| interface screen | Interface screen below (E-0955) |
| time ms | milliseconds from the performance counter (E-0804) |

Raw stores some places make (E-0954): display mode (0x48f200; 0 none, 1 warp, 2 still),
end of play (0x48f1fc = 1, then credits), "no autosave on the next goto" (0x48f2a4, the
fight), puzzle mode (0x48f2a8, jixw210), the fight's start time (0x530bf8). Every goto
writes the autosave unless visit mode is on or that flag is set.

Close-ups (E-0906): a look zone goes to a procedure that shows a still and adds its own
zones in screen pixels. The way back is usually a go zone across the whole bottom of the
screen (left 0, right 639, bottom 479, top 398..460; 54 of the 87 still procedures) whose
target is the place it came from, with the finger cursor; otherwise the code decides
(target 0). There is no special "back" cursor in the zone handler; `BACK.SPR`,
`LEFT2.SPR`, `RIGHT2.SPR` belong to other screens (Q-0902).

## Objects

36 records (0..35; 35 empty), 36 = "nothing held" (E-0905):

- Fields: index, name (`LISTE_BOITES`, `ORIGINAUX`, ..., `CLE_JARRE`), `c_<x>` sprite
  (36x36), `r_<x>` sprite (30x30, the hand cursor), `i_<x>` sprite (objects 0..18, the
  documents), a document key (0..18), state, slot (initially -1; Q-0902).
- Names, from the table: 0 LISTE_BOITES feuill, 1 ORIGINAUX origi, 2 POSTHUME letpos,
  3..6 CONFES1..4 conf1..4, 7..10 INDIC1..4 indic1..4, 11 LISTE_VICTIMES listvi,
  12 PROCLA procla, 13 EDI edit, 14 LETTRE_VIERGE papier, 15 REBU rebus, 16 PLBOMB plantr,
  17 INDICE_CACHETS and 18 INDICE_CACHETS2 indics, 19 SCEAUX soclsc, 20 TOURNEVIS tourne,
  21 CIRE cire, 22 RUYI ruyi, 23 PINCEAU posepi, 24 BURIN burin, 25 MARTEAU martea,
  26 CLE_WANG clef, 27 CURE_DENTS cured, 28 PINCEAU_ESP pincea, 29 PIECES monn,
  30..33 MANDAT1..4 mandat, 34 CLE_JARRE clef (sprite stems after `c_`/`r_`/`i_`).
- States: 0 initial, 1 held as the cursor, 2 in the inventory, 3 destroyed. New game
  sets all to 0 and slot -1, then object 30 (MANDAT1) to 2 (E-0506).
- To inventory: only from state 0. To cursor: not if already 1 or 2; the object held
  before goes to 2; this one becomes 1, held, and its `r_` sprite the cursor. Destroy:
  state 3, and if it was held, hands become empty.
- Taking: the zone handler only turns and goes (type 4 hover shows `prendre`); the
  place's code tests the zone index and calls to-inventory or to-cursor itself, usually
  with a video or line (e.g. `obj_to_inventory(INDICE_CACHETS)` in cpc410's event part).
- Saves store each object's state and slot (E-0905, E-0208).

## Sounds

Place sounds play on one channel (3) through a two-entry queue (E-0950):

- queue(name): if channel 3 is busy the call is dropped; otherwise the name is stored as
  pending (if nothing is pending). Non-blocking.
- Every frame (and at the start of queue), when channel 3 is idle the pending name is
  played once from `DATA/LOC/VOICES/<name>.WAV`, else `DATA/SOUND/<name>.WAV`; a missing
  file is dropped silently. Nothing loops. Volume: Q-0952.
- play-wait(name): wait for channel 3, play, wait until it ends; blocks with no drawing
  and no input.
- stop: stop channel 3 at once. Escape during play does the same (E-0508).
- Voice lines and dialogues first wait for channel 3 to end (E-0951, E-0952).

## Dialogues

Both kinds walk a DIAL.TXT block and its `GOTO` chain to `fin`, one voice file per block,
`DATA/LOC/VOICES/<block id>.WAV` (22050 Hz mono 16-bit), on voice channel 1.

Voice line, `voice(block)` (E-0951): the place stays on screen. Per block: start the
voice, draw the warp view with the block's text in the subtitle band (always, whatever the
subtitle option), flip, wait for the voice to end. Escape ends the current block (held, it
skips the rest). No other input. The music is set to duck (lower by 1 per tick to 20) and
back (raise by 10 per tick to 127) around it; the music does not tick meanwhile. A block id
missing from DIAL.TXT (both kinds) plays nothing and returns at once, even if the WAV
exists: `victime`'s `voice("victime")` and `jixw120`'s `dialogue("ANJIX41", ...)` (a slip
for `ANJJIX41`) are silent in every edition (E-0956).

Lip-sync dialogue, `dialogue(block, stemA, stemB)` (E-0952): blocking, full screen.
- Faces: `DATA/SYNC/<stem><k>.HNM`, k = 0, 1, 2 talking loops, 3 mouth shut; HNM6
  640x480, 7 frames each, drawn at (0, 0) over the whole screen. A speaker whose files
  fail to load shows black. stemA speaks the blocks whose id starts with the same 3
  letters as the first block's; stemB the others. Only the speaking face is shown.
- Lip sync from the voice amplitude: while the voice plays (until 0.5 s before its end),
  look 0.25 s ahead of the play position, average 5 samples; below 1024 = shut (loop 3,
  shown at most every 2 s), else a random talking loop (0..2), not the same one twice in
  a row (loop 2 excepted after its first repeat, a quirk). A talking loop plays 7 frames at
  51 ms or more each; the frame counter is per speaker and continues across loops.
- Per frame: music tick (the duck works here), Escape stops the voice and ends the whole
  dialogue, face frame, subtitle band only if the subtitle option is on, flip. No mouse.
- At the end it waits for the voice, restores the music and frees the faces; the place
  redraws on the next frame.

Subtitle band (E-0951): the text wrapped to 630 px in font slot 1; n lines give a black
band n x 15 + 10 rows high across the bottom of the screen; line i white at x 5,
y = 480 - band + 5 + 15 i. A line with a `$` is drawn from after it.

## Puzzles (entry and exit only)

puzzle(n, m) (E-0953): a held object returns to the inventory; puzzle mode is set; the
puzzle runs to its end in its own loop (blocking); puzzle mode clears; the call returns
the puzzle's result (1 solved, 0 left). Leaving re-enters the current place, so its entry
part runs again. On an error the previous result is returned. m matters only for Sceaux
(variant: background and target row, E-1203). Each puzzle's own rules and exits:
`games/china/docs/puzzles.md` (puzzles 1-4: E-1200..E-1204; others: Q-0951).

| n | Puzzle | Source | Data folder |
|---:|---|---|---|
| 1 (and any other) | Penjing | PuzzlePenjing.cpp | PUZZLES/PENJING |
| 2 | Bouddha | PuzzleBoudha.cpp | PUZZLES/BOUDDHA |
| 3 | Sceaux (seals), takes m | PuzzleSceaux.cpp | PUZZLES/SCEAUX |
| 4 | Go | PuzzleGO.cpp | PUZZLES/PUZZLEGO |
| 5 | Puzzle4 | Puzzle4.cpp | PUZZLES/PUZZLE4 |
| 6 | Horloge (clock) | PuzzleHorloge.cpp | PUZZLES/HORLOGE |
| 7 | Boutons (door buttons) | PuzzleBoutons.cpp | PUZZLES/PORTE |
| 8 | Bombe | PuzzleBombe.cpp | PUZZLES/BOMBE |

## Endings

The epilogue (end of `shs240`, E-0954): four stills in turn, ANJFR000, GEN_DAFR,
CONCUFR0, JONGFR00, each with its LABELS.TXT text (FIN_ANJING, FIN_DAMING, FIN_SHOUXIU,
FIN_PRINCE) in the subtitle band, 10 s each or until Escape (then until it is released).
Then the display is set to none and play ends with the credits.

## Interface screen (summary)

Opened by Space (after its release) or a right click (the button's latch clear), from the
frame loop or from the `fight` place (E-0508, E-0955). Modal, over a copy of the current
frame: an inventory row of 38 px slots at y 437..475 (hover: the object's label text;
click: take it as the cursor or put the held one back) and buttons (one disabled in
puzzle mode) whose screens are not yet identified (some re-enter the place, one returns
to the menu). Space or a right click closes it; the next warp draw skips its cross-fade. Full spec: china-interface.md (E-1100..E-1106).
