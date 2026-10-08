# China: puzzles

Each puzzle is entered through `puzzle(n, m)` (engine spec `china-zones.md`, Puzzles,
E-0953): init, a blocking run loop, close. Evidence ids refer to
`engines/cryomni3d/docs/EVIDENCE.md`.

## Common frame (puzzles 1-4)

(E-1200)
- Files are read from `DATA/PUZZLES/<folder>/`; names are case-insensitive.
- Init: allocate a 640x480 16-bit buffer, load sounds into sound channels (channel 0, Go
  also 1), show the background still (`setImage`, the TGA) and copy the shown screen into
  the buffer; load the SPR sprites. Each sprite is drawn at its own SPR position (x, y
  from the SPR image ID, E-0505) with its key colour transparent; its click rectangle is
  the sprite's box (x..x+w-1, y..y+h-1).
- Run loop, every frame: pump window messages, update the music, poll the mouse; if the
  left button is down and its press latch is clear, set the latch and handle one click at
  the cursor's top-left point; copy the buffer to the back buffer, draw the shown sprites,
  draw the cursor, present (no frame limiter); then test the win condition; if not won,
  test Escape (DIK 1, held down) to leave. The cursor is the default cursor (set once on
  entry).
- End (solved or left): re-enter the current place (0x41f170), mark the puzzle done with
  its result (1 solved, 0 left). Close frees sprites, sounds and the buffer.
- Click areas are tested whether or not the sprite is currently shown, so a hidden piece
  can be clicked back at its place.
- No state is kept between visits: init resets every piece each time.

## 1 Penjing (PuzzlePenjing.cpp, folder PENJING)

Init 0x41c520, run 0x41cda0, close 0x41cd20 (E-1201).

- Files: background `PENJING.TGA`, click sound `PENJINGA.WAV` (channel 0), 24 sprites
  `<stem>_SPR.SPR` in 12 slots of two animals each, with a LABELS.TXT key per sprite.
- Slots (first animal shown at start; positions are the first sprite's; the second sits
  at its own SPR position, about the same place):

| Slot | First (label key) | Second (label key) | First at x,y |
|---:|---|---|---|
| 0 | HIRO (HIRONDELLE) | SERP (SERPENT) | 159,292 |
| 1 | GRUE (GRUE) | COQ (COQ) | 152,365 |
| 2 | TIGR (TIGRE) | LION (LION) | 231,55 |
| 3 | CHIN (CHIEN) | POUL (POULE) | 226,150 |
| 4 | CHAU (CHAUVE_SOURIS) | CHEV (CHEVAL) | 224,256 |
| 5 | POIS (POISSON) | SANG (SANGLIER) | 223,342 |
| 6 | LIEV (LIÈVRE) | RENA (RENARD) | 311,188 |
| 7 | CERF (CERF) | BEUF (BOEUF) | 310,273 |
| 8 | SING (SINGE) | TORT (TORTUE) | 311,373 |
| 9 | CHAT (CHAT) | RAT (RAT) | 400,141 |
| 10 | DRAG (DRAGON) | FAIS (FAISAN) | 401,229 |
| 11 | CHVR (CHÈVRE) | BICH (BICHE) | 399,353 |

  (È in the keys is byte 0xC8.)
- State: one flag per slot, "first shown", 1 at start.
- Click: every slot whose *first* sprite's rectangle contains the point flips its flag and
  plays channel 0.
- Hover, every frame: the first slot (in order) whose shown sprite's rectangle contains
  the cursor sets the hover label to that animal's label text; none clears it. The label
  is drawn after the cursor (cursor + 20, clipped).
- Draw: background, then each slot's shown animal.
- Win: the twelve Chinese zodiac animals shown: first shown in slots 2, 3, 6, 8, 10, 11
  (Tigre, Chien, Lièvre, Singe, Dragon, Chèvre), second shown in slots 0, 1, 4, 5, 7, 9
  (Serpent, Coq, Cheval, Sanglier, Boeuf, Rat). Result 1 at once (no extra sound or
  video). Escape: result 0.

## 2 Bouddha (PuzzleBoudha.cpp, folder BOUDDHA)

Init 0x41a3b0, run 0x41a6e0, close 0x41a660 (E-1202).

- Files: background `BOUDDHA.TGA`, click sound `BOUDDHAA.WAV` (channel 0), sprites
  `B1_SPR`, `B2_SPR` (group B) and `R1_SPR`, `R2_SPR`, `R3_SPR` (group R): a row of five
  small pieces, R1 230,393, B1 268,392, R2 306,392, B2 347,391, R3 382,393.
- State: a "shown" flag per piece, all 1 at start; two derived flags, *armed* and
  *cleared*.
- Click: every piece whose rectangle contains the point flips its shown flag and plays
  channel 0.
- Draw: background, B1, B2, R1, R2, R3 where shown.
- After each presented frame: if B1 or B2 is shown, *armed* = 0; else if R1, R2 and R3
  are all shown, *armed* = 1 (otherwise *armed* keeps its value). *cleared* = none of R1,
  R2, R3 shown. Win when *armed* and *cleared*: both B pieces hidden while all three R
  pieces were shown, then all three R hidden with the B pieces staying hidden. Shortest
  solution from the start: click B1, B2, then R1, R2, R3 (any order within each group).
  Result 1; Escape: result 0.

## 3 Sceaux (PuzzleSceaux.cpp, folder SCEAUX)

Init 0x41d020, run 0x41d630 (takes m), close 0x41d540 (E-1203).

- m selects the variant (answers Q-0950): m = 0 (`spfw101`, holding INDICE_CACHETS) uses
  background `FOND.TGA` and the imprint targets `EMPR1..3.SPR` (row at y 292); m = 1
  (`arbre3`, zone 0) uses `FOND2.TGA` and `EMPR1F..3F.SPR` (row at y 388). m = 0 also
  hands the player CIRE and allows the interface screen (below). Other m values format no
  background name (not used by the game).
- Files: sound `TMPN.WAV` (channel 0; `TMPN2.WAV` is never named by the program), ink pad
  `TAMPONS.SPR` (489,32), and for seal i = 1..3: `SCEAU<i>` (the seal), `OMBRE<i>` (its
  shadow), `DEMAT<i>`, `DEBRILL<i>` (two looks of the seal at about the same place),
  `EMPR<i>` / `EMPR<i>F` (the imprint on the paper). Positions: SCEAU1 12,43, SCEAU2
  192,42, SCEAU3 357,53; EMPR1 x 103, EMPR2 x 270, EMPR3 x 425.
- State per seal: a step (0..5, 0 at start), *held* (0), *shown* (1, never changed); per
  target: *imprinted* (0). Seal clicks use the seal's home rectangle (SCEAU sprite box).
- Click (only when the hands are empty, held object 36):
  - Seal i's rectangle: every *other* seal at step 1 goes back to 0. Then, only if no
    other seal is held: step 4 or 5 flips *held* (pick up / put back); step 1 goes to 3
    (m = 0) or 4 (m = 1); step 0 goes to 1.
  - Ink pad: every held seal at step 4 plays channel 0 and goes to 5 (inked).
  - Target 1 with seal 2 held at step 5, target 2 with seal 3, target 3 with seal 1:
    plays channel 0, that target becomes imprinted (the seal stays held and inked).
- Step 3 (m = 0 only): at the top of the next frame, for 1000 ms a loop redraws the scene
  with that seal as DEBRILL (input only polled, no clicks); the first time in the visit,
  object 21 CIRE becomes the held object (state 1, slot -1) and its sprite the cursor.
  Then the seal goes to step 4. While CIRE (or anything) is held, clicks are ignored until
  it is put away through the interface screen.
- Draw: background; per seal, if not held: step 1 draws DEMAT (at DEMAT's x, DEBRILL's
  y), step 3 DEBRILL, any other step the shadow then the seal; then that index's target
  imprint if imprinted; then the ink pad; the cursor; last, a held seal centred on the
  cursor point (point minus half its width and height).
- Win: the variant's three targets imprinted: the left target with the middle seal, the
  middle target with the right seal, the right target with the left seal (each seal first
  raised: two clicks, picked up: a third, inked on the pad). Result 1.
- Leaving: no Escape. With m = 0 only, Space (DIK 0x39) or a right click (button down,
  its latch clear) opens the interface screen (0x40efd0) when CIRE is not in the inventory
  (state 2); the puzzle ends with result 0 if the interface clears the run flag (which of
  its buttons do: Q-0953). With m = 1 the only way out is solving (Q-1200).

## 4 Go (PuzzleGO.cpp, folder PUZZLEGO)

Init 0x41b5d0, run 0x41b990, close 0x41b920 (E-1204).

- Files: background `GO1.TGA`, `GO1A.WAV` (channel 0, click), `GO1B.WAV` (channel 1, a
  bar appears), 25 stones `BOUT1..25.SPR`, 40 bars `BARRE1..40.SPR`.
- Board: 5x5 points, row r = 0..4 from the back (top of screen) to the front, column
  c = 0..4 from left to right. Point (r, c) is `BOUT<5r+5-c>` (BOUT5 175,180 back left;
  BOUT1 351,145 back right; BOUT25 213,326 front left). The horizontal bar between (r, c)
  and (r, c+1) is `BARRE<4r+4-c>` (1..20); the vertical bar between (r, c) and (r+1, c) is
  `BARRE<37+r-4c>` (21..40).
- State: a "placed" flag per point and per bar, all 0 at start.
- Click: every point whose rectangle contains the click flips its flag and plays channel
  0; the loop then waits until channel 0 has finished; then every bar is recomputed: on
  when both its points are placed, else off. A horizontal bar turning on plays channel 1;
  a vertical bar turning on plays channel 1 if channel 0 is not playing. Bars change only
  on click frames.
- Draw: background, placed stones, vertical bars, horizontal bars.
- Win: exactly these nine points placed, all others empty: (0,2); (1,1) (1,2) (1,3);
  (2,1) (2,2) (2,3); (3,2); (4,2), i.e. stones BOUT3, BOUT7..9, BOUT12..14, BOUT18,
  BOUT23 (bars follow by themselves). Result 1; Escape: result 0.

## Puzzles 5-8: common behaviour (E-1250..E-1254)

Each of these puzzles runs its own blocking frame loop over a 640x480 16-bit
background; files are under `DATA/PUZZLES/<folder>/`. Sprites are SPR files drawn at the
x, y in their own header, key colour transparent. "Pixel hit" = the point is inside the
sprite and the pixel there is not the key colour (0x41fc20; its bottom test accepts
y = top + height, one row too many); "rect hit" = inside the sprite rectangle
(0x420340). A press = the left button going down (the press latch, E-0900). Escape =
DirectInput key 1 down (0x414c70). Every exit re-enters the current place (0x41f170)
and returns the result (1 solved, 0 left). Masks, pixel hits and rect hits all use the
cursor's top-left point (not its hot point), and hover labels (Puzzle4, Boutons, Bombe;
Horloge has none) are placed from that top-left as elsewhere (E-1254).

## 5 Puzzle4 (Puzzle4.cpp, folder PUZZLE4) (E-1250)

Init 0x417e90, run 0x4189bc, free 0x41887e, ring rotate 0x41880e.

- Files: sound slot 0 `puzzle4a.wav` (ring click), slot 1 `puzzle4b.wav` (phase 2
  click); background `fond` (FOND.TGA); `mask.raw` (640x480 bytes, values 231..255);
  sprites `couleur1..8`, `animaux1..8`, `direct1..8` (three rings; entry i of a ring =
  file 8-i), `soleil`, `lune`, `mer`, `ciel` and their `...2` variants; phase 2
  background `puzenter` (PUZENTER.TGA). Not used by the code: `CPUZZL~1..3.SPR`,
  `FERM_.SPR`.
- Label rings (hover text, LABELS.TXT keys): ring 0 slots 0..7 = rouge, jaune, blanc,
  bleuc, noir, gris, vert, bleuf; ring 1 = OISEAU, rien, TIGRE, rien, TORTUE, rien,
  DRAGON, rien; ring 2 = SUD, rien, OUEST, rien, NORD, rien, EST, rien.
- Start: phase 1; each sprite ring shows entry 3 (`couleur5`, `animaux5`, `direct5`).
  For phase 2 all four `...2` variants are shown, the plain ones hidden.
- Every frame: m = mask[y][x] - 231. If m != 24 the hover label is ring m/8, slot m%8
  (in both phases).
- Phase 1 press: m in 0..7 / 8..15 / 16..23 rotates label ring 0 / 1 / 2 by one (slot
  k+1 takes slot k, slot 0 takes slot 7) and plays sound 0. Independently, for each
  sprite ring (couleur, animaux, direct) a pixel hit on its visible entry i hides it and
  shows entry i-1 (0 goes to 7); no sound for this part. The label ring follows the
  mask and the picture follows the sprite pixels; nothing ties them together.
- Phase 1 solved when all three rings show entry 7 (`couleur1`, `animaux1`, `direct1`):
  4 presses on each ring from the start. Phase 2 then starts: background
  `Puzzle4\puzenter` becomes the saved background (no sound, no video).
- Phase 2 press: for each of soleil, lune, mer, ciel, a rect hit on the plain sprite's
  rectangle toggles it (plain shown <-> `...2` shown) and plays sound 1.
- Phase 2 solved: the plain ones must be switched on in the order soleil, lune, mer,
  ciel, each while the later ones are still off (a chain of four steps checked every
  frame; switching an earlier one off clears the later steps).
- Draw: saved background, visible sprites, cursor, hover label. Phase 2's draw loop
  walks three rows of four where only two exist (Q-1250).
- Solved: re-enter, return 1 (no sound or video here; the place then plays `puzzl4`).
  Escape: return 0. No right click or interface screen.

## 6 Horloge, the clock (PuzzleHorloge.cpp, folder HORLOGE) (E-1251)

Init 0x41bd30, run 0x41c1d0, free 0x41c140.

- Files: sound slot 0 `clicaig.wav`; background `hrlgfnd`; `mask.raw` (values 0..54);
  hands A `aig01a..aig12a` and B `aig01b..aig12b` (the big dial, around 340,210), D
  `aig01d..aig12d` (small dial around 380,300, 12 positions), C `aig01c..aig30c` (small
  dial around 290,285, 30 positions).
- Start: A at 8, B at 4, D at 5, C at 18 (file numbers).
- Grab: while the button is held and nothing is grabbed, the first hand (A, B, D, C)
  whose visible sprite has a pixel hit is grabbed. Releasing the button drops it.
- Drag: each frame with a hand grabbed, v = mask[y][x]: A or B take v 1..12 (p = v), D
  v 13..24 (p = v-12), C v 25..54 (p = v-24); the hand shows position p+1, wrapping
  (12 -> 1, 30 -> 1). Other v leave it. When v changes during a drag to another value in
  1..54 (the previous one non-zero), sound 0 plays.
- Solved (checked each frame after drawing, only with nothing grabbed): A at 6, B at 9,
  D at 10, C at 8. Then video `puzhorlo`, re-enter, return 1.
- Escape: return 0. No right click or interface screen.

## 7 Boutons, the door (PuzzleBoutons.cpp, folder PORTE) (E-1252)

Init 0x41a8f0, run 0x41b0a0, free 0x41b010.

- Files: sound slot 0 `bouton1a.wav` (init first loads it from a hard-coded `C:\Chine`
  path, then from the real folder); background `porte`; three columns of six sprites
  (index 0..5), each with a LABELS.TXT label:
  - column 1 (x 202): app1 APPOSER, lett LETTRÉ, peti PETIT, parl PARLER, homm HOMME,
    gran GRAND;
  - column 2 (x 290): app2 APPOSER, ruis RUISSEAU, jade JADE, voya VOYAGER, coeu COEUR,
    femm FEMME;
  - column 3 (x 380): app3 APPOSER, lune LUNE, sole SOLEIL, mont MONTAGNE, chef CHEF,
    forc FORCE.
- Start: column 1 shows 2 (PETIT), column 2 shows 4 (COEUR), column 3 shows 0 (APPOSER).
- Press: a rect hit on a column's visible entry i shows entry i-1 instead (0 -> 5) and
  plays sound 0 (twice for 0 -> 5).
- Hover: the label of the visible entry under the cursor.
- Solved: all three show entry 0 (APPOSER); from the start, 2 presses on column 1 and
  4 on column 2. Then video `puzporte`, re-enter, return 1.
- Escape: return 0. No right click or interface screen.

## 8 Bombe, the bomb (PuzzleBombe.cpp, folder BOMBE) (E-1253)

Init 0x4192c0, run 0x419830, free 0x4197d0, hover cursor 0x41a390.

- Files: sound slots 2 `coussin`, 3 `tvis`, 4 `pese`, 5 `clang`, 6 `clic`, 7 `metal`,
  8 `tuyau` (not on the disc, Q-1251); first background `Trone`; click shapes (SPR,
  never drawn) `tronem`, `bombe1m`, `barre1..4`, `aiguille`, `baretav`, `baretar`,
  `capsular`, `capsulav`, `ecrouh`, `ecroub`, `grandt`, `petitt`. Only the background
  is shown; steps load the next background.
- A step s starts at 0 on every entry. One step per press, tested from the highest s
  down; "on X" = pixel hit on sprite X; "with X" = X is the held object:

  | s | press | effect |
  |---|---|---|
  | 0 | on tronem | sound 2, background Bombe1, s 1 |
  | 1 | on bombe1m | sound 4, Bombe2, s 2 |
  | 2..5 | on barre(s-1) | sound 7, Bombe21..24, s+1 |
  | 2..5 | on aiguille, not on that bar | video gamover1, end 0 |
  | 6 | on aiguille | video gamover1, end 0 |
  | 6 | anywhere else | Bombe3, s 7 |
  | 7 | on ecroub | sound 6, s 8 |
  | 8 | on ecrouh | sound 6, s 9 |
  | 7, 8 | on capsular or capsulav (not on the nut), with RUYI (22), MARTEAU (25) or TOURNEVIS (20) | video gamover2, end 0 |
  | 9 | on petitt with TOURNEVIS | Bombe31, s 10 |
  | 10 | on petitt with TOURNEVIS | Bombe32, s 11 |
  | 11 | on grandt with TOURNEVIS | sound 8, Bombe33, s 12 |
  | 12 | on baretav with TOURNEVIS | sound 3, Bombe34, s 13 |
  | 13 | on capsulav | sound 5, Bombe35, s 14 |
  | 14 | on baretar with TOURNEVIS | sound 3, Bombe36, s 15 |
  | 15 | on capsular | sound 5, Bombe37, s 16 |
  | 16 | anywhere | solved, end 1 |

- Hover label: AIGUILLE over aiguille at s 2..6; POISON over capsular at s 7..15 or
  capsulav at s 7..13.
- Cursor each frame: the held object's cursor, else `ptroug` (11). With empty hands
  only: `prendre` (10) over tronem/bombe1m/barre1..4 at s 0..5, ecroub at 7, ecrouh at
  8, capsulav at 13, capsular at 15, and anywhere at s 6 and 16; `util` (14) over
  petitt at 9..10, grandt at 11, baretav at 12, baretar at 14.
- A right click (latch clear) or Space opens the interface screen (0x40efd0), which is
  how an object is taken in hand here; if it returns "leave", the puzzle ends with 0.
- End (1 solved; 0 after a game-over video, Escape or the interface's leave): a held
  object goes back to the inventory (state 2, hands empty), re-enter, return. The game
  over is only the video: the place is re-entered and the bomb starts again at s 0.
  On 1 the place plays `fin` and the epilogue.
