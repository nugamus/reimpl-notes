# The 2D side: player screen, zones, inventory, option menu, credits

Everything drawn by the 2D shell (0x408cf1–0x41664f) and the player window (0x4180c0–
0x419f0d). The screen is 640×480 (x right, y down). The per-zone puzzles are in
`games/mission-sunlight/docs/a*.md`; they use the building blocks defined here.
Image, sprite, font, movie and sound formats: `docs/formats/README.md` (E-0100..E-0209).

Words used below:

- **tick**: one 2D timer message, every 40 ms (`boot.md` "Program modes"). "Odd tick" =
  the tick counter (0x4e25d0, +1 mod 4 per tick) has bit 0 set; most sprite animations
  advance one frame on odd ticks (12.5 fps), some on even ticks.
- **click** = the left mouse button is down on this tick (0x40e4ef); **release** = it is
  up. Most screens act on the first tick the button is down and then wait for a release.
- **cursor n** = frame n of `SPRITES\Curseurs.SPR` with its hot spot ("Cursors").
- **background X** = `GFX\X.TGP` (single form, `Tgp_Load2`) drawn full screen.
- **movie n** = entry n of the 2D movie table (E-0204, "2D movies"); **voice X** = the
  streamed sound `SOUND\X.APC` (E-0209); **sound X** = the static sound `SOUND\X.WAV`.

## Player-name screen (E-0402, E-0403)

A popup window as large as the desktop, background brush RGB(16, 40, 80). The 640×480
bitmap resource `ACCUEIL_BMP` (8-bit, in `mission.___`'s `.rsrc`, language 1036) is drawn
centred; `(ox, oy)` = its top-left corner. Controls, at `(ox, oy) +`:

| Control | Id | Position, size | Look |
|---|---|---|---|
| Name field | 0x65 | (344, 206), 163×26 | edit, 20 characters max, font "Trobo" 16 px, white on RGB(0, 84, 120), focused and selected |
| OK | 0x66 | (407, 396), 36×23 | `BOUTONS_BMP` (160×100) at (0, 0); pressed (0, 28) |
| Quit | 0x67 | (468, 396), 72×27 | `BOUTONS_BMP` at (40, 0); pressed (40, 28) |
| Player i (i < count) | 0x68 + i | (90, 217 + 34 i), 162×27 | the name in "Trobo" at (2, 2) on RGB(0, 84, 120), RGB(181, 198, 214), white while pressed |

Clicking a player button copies its name into the field. Enter = OK, Escape = Quit (the
field forwards their key-up to the window). OK with an empty field does nothing; with a
name (compared case-insensitively):

- a known name: that player, **known** (0x502 lParam 1);
- a new name with fewer than 5 players: appended with volume 0 and view size 0, **new**
  (lParam 0);
- a new name with 5 players: the background becomes `ACCUEIL2_BMP`, the field disappears,
  player 0 is selected (white text) and clicking a player button selects it; OK then gives
  the selected slot the new name (volume 0, size 0) and ends as **new**.

Quit closes the window and the program. The screen ends with message 0x502 (`boot.md`).

## Input (E-0407)

- **Mouse**: DirectInput, relative. Each tick the 2D cursor moves by twice the mouse
  motion and is clamped to 0..639 × 0..479 (0x40e3e1). The shell draws the cursor itself.
- **Keyboard**: DirectInput state of 256 DIK codes, read once per tick into one of two
  buffers. A key **fires** on the tick it is released (down on the previous tick, up now:
  0x410c21). Esc (DIK 1) = option menu, Space (0x39) = inventory bar, Backspace (0x0E) =
  leave the zone / abort a puzzle. The panorama view reads the arrow keys (held).

## Cursors (E-0416)

`Curseurs.SPR` frame and hot-spot offset (the frame's centre is drawn at cursor + offset;
table 0x4a64e8, `{frame, dx, dy}`, set by 0x40e25a):

| n | dx, dy | Use |
|---:|---|---|
| 0 | -7, -10 | default |
| 1..8 | (-9, 0) (8, 0) (0, -9) (0, 8) (-9, -9) (8, -9) (-9, 9) (8, 9) | panorama scroll left, right, up, down, up-left, up-right, down-left, down-right |
| 9 | 0, 0 | busy (nothing clickable) |
| 10 | 2, -8 | brush (zone 24) |
| 11 | 0, -9 | over a button / hot spot |
| 12 | 0, -6 | over something that can be taken |
| 13 | 0, -6 | dragging |

## Entering a zone (E-0408)

The 3D side calls `Entry2D(window, zone, flags[35], state, 0x36C)` (0x40fdc6): `zone` must
be 0..25 (25 reads past the 25-row table, Q-0250), `flags` are the 35 object-held flags,
`state` the 3D state block (kept for saves, `save.md`). It rebuilds the **inventory list**:
the held object ids in increasing order (0x4e2688, `count` 0x4e27dc), then `ZoneInit`
(0x410365):

- zone 21: only the ending (`a14.md`), state 0x24; `Entry2D` also writes `GGAME` (flag 0).
- other zones: background = the zone's name; sprites `LoupeOut`, `Retour`, `RetourM`;
  sprites `CapsE<nn>` for each object of the zone; the bar's sprites and sounds
  (`Invent`, `OPI`, `OP`, `count`, `LoupeIn`, `bar_obj`, `fleche`, `cf_clic3`); for each
  zone object held or already placed: `CapsAO<nn>`, `CapsAC<nn>`, `CapsOP<nn>`, sounds
  `ouvrcaps`, `fermcaps` and the object's own sound; sounds `clic_1`, `bar_outi`.
- starts the 40 ms timer; the state machine starts in state 0.

### Zone table (0x4a6b18, 25 × 0x6C)

`{u32 id; u32 count; u32 objects[3]; char background[12], viewA[12], viewB[12];
i32 magX, magY; u32 tournIndex; u32 counter; fn onPlace, onAbort, slotRun[3];
char vanGogh[8]; u32 unk_64; u32 done}`. viewA/viewB are the background name + `a` / `b`
in every row. `done` is saved (`save.md`).

| Zone | Background | Objects | Magnifier x, y | TOURN | Counter | onPlace | onAbort | Slot 0 | Slot 1 | Slot 2 | Van Gogh |
|---:|---|---|---|---:|---:|---|---|---|---|---|---|
| 0 | `A14_031a` | 0 | 325, 430 | 1 | 0 | 0x4119fc | - | 0x411a28 | - | - | - |
| 1 | `A01_02` | 1 | 436, 290 | 2 | 1 | 0x40d0f0 | - | 0x414dcc | - | - | `PA01_02a` |
| 2 | `A01_03` | 3, 2 | 436, 373 | 0 | 1 | 0x40d112 | 0x40d1ef | 0x40d293 | 0x414dec | - | `PA01_03a` |
| 3 | `A11_01` | 4 | 436, 398 | 0 | 1 | 0x40d271 | - | 0x414dcc | - | - | `PA11_01a` |
| 4 | `A03_01` | 5, 6, 7 | 441, 417 | 0 | 2 | 0x4022c0 | 0x402376 | 0x414dec | 0x40241b | 0x414dcc | `PA03_01a` |
| 5 | `A13_08` | 8 | 329, 430 | 0 | 2 | 0x4029b1 | - | 0x414dcc | - | - | `PA13_08a` |
| 6 | `A13_04` | 9 | 436, 413 | 0 | 2 | 0x4029d3 | - | 0x414dcc | - | - | `PA13_04a` |
| 7 | `A03_02` | 10, 12, 11 | 436, 412 | 0 | 2 | 0x4029f5 | 0x402ac2 | 0x402ada | 0x402c20 | 0x402b51 | `PA03_02a` |
| 8 | `A13_03` | 13, 14 | 436, 404 | 0 | 2 | 0x403346 | 0x4034f2 | 0x4035fb | 0x403a1a | - | `PA13_03a` |
| 9 | `A13_02` | 15 | 436, 331 | 2 | 2 | 0x403ddb | - | 0x414dcc | - | - | `PA13_02a` |
| 10 | `A13_05` | 16, 17 | 333, 430 | 0 | 2 | 0x403dfd | 0x403ea1 | 0x414dcc | 0x403f04 | - | `PA13_05a` |
| 11 | `A13_07` | 18 | 326, 430 | 0 | 2 | 0x40410e | - | 0x414dcc | - | - | `PA13_07a` |
| 12 | `A03_03` | 19 | 436, 406 | 0 | 2 | 0x404130 | - | 0x414dcc | - | - | `PA03_03a` |
| 13 | `A03_04` | 21, 20 | 436, 411 | 0 | 2 | 0x404152 | 0x404217 | 0x404378 | 0x414dec | - | `PA03_04a` |
| 14 | `A13_01` | 22, 23 | 436, 412 | 0 | 2 | 0x40474b | - | 0x414dcc | 0x414dcc | - | `PA13_01a` |
| 15 | `A13_06` | 24, 25 | 333, 430 | 0 | 2 | 0x404a47 | 0x404b5f | 0x404bde | 0x414dcc | - | `PA13_06a` |
| 16 | `A03_05` | 26 | 331, 430 | 0 | 2 | 0x4055bb | 0x4056ac | 0x405816 | - | - | `PA03_05a` |
| 17 | `A13_09` | 27 | 332, 430 | 0 | 2 | 0x405e6a | - | 0x414dcc | - | - | `PA13_09a` |
| 18 | `A03_06` | 28 | 441, 429 | 0 | 2 | 0x405e8c | 0x405f5b | 0x405fa6 | - | - | `PA03_06a` |
| 19 | `A04_01` | 29, 30 | 436, 271 | 2 | 3 | 0x4074c0 | - | 0x414dec | 0x414dcc | - | `PA04_01a` |
| 20 | `A14_01` | 31 | 338, 430 | 0 | 3 | 0x407509 | 0x4076b2 | 0x40770c | - | - | `PA14_01a` |
| 21 | `A14_032a` | - | 325, 430 | 0 | 3 | - | - | - | - | - | - |
| 22 | `A04_02` | 32 | 436, 270 | 2 | 3 | 0x407b83 | - | 0x414dcc | - | - | `PA04_02a` |
| 23 | `A04_03` | 33 | 331, 430 | 0 | 3 | 0x407ba5 | - | 0x414dcc | - | - | `PA04_03a` |
| 24 | `A14_02` | 34 | 436, 417 | 0 | 3 | 0x407bc7 | 0x407dd1 | 0x408118 | - | - | `PA14_02a` |

The handlers are reached only through this table (no direct callers); 0x403ddb is one
Ghidra did not make a function (34 bytes, E-0408). Puzzle flows per zone:
`games/mission-sunlight/docs/` (`a01.md` zones 1–2, `a11.md` 3, `a03.md` 4, 7, 12, 13,
16, 18, `a13.md` 5, 6, 8–11, 14, 15, 17, `a04.md` 19, 22, 23, `a14.md` 0, 20, 21, 24).

### Object table (0x4a75a8, 35 × 0x20)

`{u32 id; char *sound; sprite capsE, capsOP, capsAO, capsAC; u32 placed; sound snd}`.
`sound` is `OP<nn>` for objects 3, 6, 8, 12, 14, 15, 18, 19, 21, 22, 25, 27, 28, 29, 32, 34
and `OP_GENE` for the others. `placed` (1 = the object sits in its zone slot) is saved.
Sprites per object nn (two digits): `CapsE<nn>` (the empty slot), `CapsOP<nn>` (put in),
`CapsAO<nn>` (opening), `CapsAC<nn>` (closing); on the bar `OPI` frame nn, while dragged
`OP` frame nn.

## The zone screen (E-0409..E-0413)

Layout: the background; the zone's objects in slots on the left: slot s at (0, 29), (0,
116), (0, 222) for s = 0, 1, 2 (drawn: `CapsE` frame 0 when not placed, `CapsAO` frame 0
when placed, `CapsAC` frame 0 for the slot being run; 0x41170e); the **magnifier** at
the zone's (magX, magY); `Retour` at (600, 435) and `RetourM` at (8, 432), both looping.

**Magnifier** (0x4e2348: 0 closing, 1 opening, 2 open, 3 closed). Open = last frame of
`LoupeOut`, closed = `LoupeIn` played to its end (sound `bar_outi`). Open, it has two
buttons: **view B** (magX + 2, magY, 65×36) and **view A** (magX + 78, magY, 65×36). It
opens when the zone is shown and after each object sequence; it closes when the bar opens.

**Hit test** on a click (0x411454), in this order: view A (if open) → 2; view B (if open)
→ 1; (605, 437, 24, 29) → 3 "Retour"; (11, 437, 24, 29) → 4 "RetourM"; the last two only
while the bar is closed and not moving. Cursor 11 over them.

### States (0x4e27e4, one step per tick, `MainWndProc` 0x4122bb)

| State | What happens | Next |
|---:|---|---|
| 0 | zone 0: magnifier open, load the bar, `LoupeIn`, open the bar; others: draw slots, magnifier, Retour buttons | 7 / 5 |
| 5 | **idle**, see "Idle" | many |
| 2, 0x13, 1 | view B: `GFX\<zone>b.TGP` panorama (`Tgp_Load`), wait for release, run the panorama until a click (sound `clic_1`), redraw | 5 |
| 4, 0x13, 3 | view A: `<zone>a` animation (below), redraw | 5 |
| 6 | wait until the bar is closed; reopen the magnifier; Retour buttons | 5 |
| 7 | load the bar; if the magnifier is closed, open the bar (sound `bar_obj`) | 5 |
| 8, 0x15 | dragging an object from the bar (8: it belongs to this zone; 0x15: it does not) | 10 / 5 |
| 10 | `CapsOP` plays at the slot; when done and the bar is closed | 0xE |
| 0xB | `CapsAO` plays at the slot (even ticks); when done, bar closed, magnifier closed | 0xE |
| 0xE | call the zone's `onPlace(object, slot)`; draw the slots | 0xD |
| 0xD | run the slot (below) | 0xC / 0xF |
| 0xF | the slot's result (below) | 0x10 / 0x1A / 0xC |
| 0x10, 0x11 | the object flies back from the slot to the bar (below) | 0x12 |
| 0x12 | when the bar is closed: magnifier, Retour buttons | 5 |
| 0xC | `CapsAC` plays (odd ticks); when done and the magnifier is open: autosave if an object was just placed (state 0x21), else Retour buttons | 0x21 / 5 |
| 0x1A..0x1D, 0x16..0x19, 0x1B | the sunflower (below) | 0x21 |
| 0x21 | autosave `GAME<player><object>.BIN` (`save.md`); zone 0 then leaves | 5 / 0x20 |
| 0x1F, 0x1E | option menu (below) | 5 / 0x20 |
| 0x22 | wait for the bar to close | 0x1F |
| 0x23 | wait for the bar to close, centre the cursor | 0x20 |
| 0x24 | zone 21's ending (`a14.md`) | 0x20 |
| 0x20 | leave the zone (below) | - |

After the state's step, on even ticks the magnifier animation advances (1 → 2 when
`LoupeOut` ends, 0 → 3 when `LoupeIn` ends); then the bar moves one step (0x410e30), a
dragged sprite follows the cursor (0x410d68), the cursor is drawn and the page flipped.

### Idle (state 5)

Cursor 0; 11 over the magnifier buttons and Retour buttons, 12 over a bar object.

- **Backspace** (not while the bar moves): bar closed → centre the cursor, leave with -1;
  bar open → close it, then leave (0x23).
- **Esc**: close the bar first if it is open (0x22), then the option menu (0x1F).
- **Space** (magnifier open or closed, not moving): bar closed → `LoupeIn` if the
  magnifier is open, then open the bar (7); bar open → close it (6).
- **Click** (bar not moving):
  - on an object of the open bar (six slots `(88 + 70 i, 436, 28, 27)`): pick it up:
    cursor 13, the `OP` frame follows the cursor, offset so that the slot position
    `(101 + 70 i, 450)` stays under the grab point; state 8 if the object is one of the
    zone's, else 0x15;
  - on view B / view A: sound `clic_1`, state 2 / 4;
  - on Retour: leave with -1; on RetourM: leave with -3 (both centre the cursor);
  - on a slot whose object is placed (slot rects (12, 53 + d, 59, 58), d = 0, 90, 180):
    replay it: `CapsAO` from frame 0, sound `ouvrcaps`, close the bar, `LoupeIn` if the
    magnifier is open; state 0xB;
  - on the bar's arrows (bar open): scroll (below).

### Inventory bar (E-0410)

`Invent.SPR`: frame 0 the bar (640×60), 1/3 left arrow up/down at (13, y), 2/4 right
arrow at (504, y). The bar's top y slides from 480 (closed) to 420 (open) over 30 ticks:
`y = 479 - T[i]`, `T[i] = trunc(60 sin(3° i))`, i = 0..29, then 420; closing runs the
table backwards to 480 (0x40fb86, 0x410e30). Open request 0x4e25c8 = 1, close = -1.

Six visible slots; slot i shows `OPI` frame = the object at list index `first + i` at
(67 + 70 i, y). `count.SPR` frame = the counter of the zone's chapter (if > 0) at (558,
y + 21). Arrows (13, 435, 23, 30) and (509, 435, 22, 30): while held, every 8th tick scroll
the list by one (sound `fleche`), left while `first > 0`, right while more than 6 remain.

### Placing an object (E-0412)

On release after a drag from the bar (state 8): if the drop point (cursor + grab offset) is
in the object's slot rect (12, 53 + d, 59, 58) of this zone, the object leaves the list,
`placed` = 1, `CapsOP` plays at the slot, the bar closes, the object's sound plays, and it
counts as **just placed**. Otherwise (or state 0x15) the list is redrawn, sound
`cf_clic3`, back to 5.

**Running a slot** (states 0xE, 0xD): `onPlace(object, slot)` starts the slot's movie,
voice or puzzle; then every tick `slotRun[slot](tick, &result)` until it returns non-zero.
Backspace during a run first calls `onAbort()` (puzzles then end on their next step with
result 0). A slot without a function plays `CapsAC` at once (sound `fermcaps`). When the
run ends the background is redrawn (not in zone 0) with the slots.

Two generic slot functions (E-0425):

- **movie** (0x414dcc): result 1; steps the 2D movie started by `onPlace`; ends with it,
  or on a click when the movie was started skippable.
- **voice** (0x414dec): result 1; waits while the streamed voice plays; a click stops it.

**Result** (state 0xF): result 0 on a just-placed object → it goes back: `placed` = 0,
the bar opens (sound `bar_obj`), `OP` frame flies from `(40, 83 + d)` (d = 0, 89, 180 per
slot) to the bar slot over 32 ticks along `p = from (1 - t) + to t`,
`t = (sin(3π/2 - π n / 32) + 1) / 2`, n = 1..32 (sound `cf_clic3`), and it is re-inserted
at its old list index. Otherwise `CapsAC` plays (sound `fermcaps`); if the zone is not
`done` and every object of the zone is placed, the zone gets its sunflower (state 0x1A,
`done` = 1).

### The sunflower (E-0413)

1. (0x1A) Once `CapsAC` has ended: open `<vanGogh>` with the last letter `a` and `b`
   (`PA<zone>a/b.SPR`), sound `pas_VG` (looping), play `PA..a` once (0x16).
2. (0x16) `PA..a` on odd ticks; at frame 12 the footsteps stop; at its end it holds its last
   frame; `TOURN<tournIndex>.SPR`, sound `tourneso`, `POT.SPR`, sound `vase`.
3. (0x17) The player clicks the sunflower (rect by tournIndex: 0 (127, 313, 30, 26),
   1 (111, 244, 24, 32), 2 (148, 290, 30, 26); cursor 12 over it): `PA..b` frame 0, the bar
   opens (`bar_obj`), `TOURN` follows the cursor (grab offsets (122, 344), (132, 295),
   (166, 333)), sound `tourneso`, cursor 13.
4. (0x18) Release on the pot area (590, 400, 45, 80): `POT` plays at (558, 422), sound
   `vase`, the counter frame follows it (0x1C); anywhere else the sunflower snaps back
   (sound `cf_clic3`) and step 3 repeats.
5. (0x1C) When `POT` ends: the zone's counter + 1, the bar closes.
6. (0x1D, 0x19) `PA..c` plays once (Van Gogh leaves), footsteps from frame 12; then the
   sprites are freed (0x1B) and the game autosaves (0x21).

### Views

- **View B** (panorama): `GFX\<zone>b.TGP` (chunked form, larger than the screen) shown
  centred; the cursor is centred. Each tick: with the cursor within 64 px of an edge, the
  view scrolls by half the distance into that margin (cursor 1..8 shows the direction);
  held arrow keys build a speed of ±1 per tick up to ±32 per axis instead (and re-centre
  the cursor); clamped to the image. A click ends it (sound `clic_1`). (0x40dc22, 0x40dcf3)
- **View A** (animation): background `<zone>a`, sprite `<zone>a.SPR` from frame 0, one
  frame per odd tick while the button is up, sound `pas_VG2` looping from frame 0 and
  stopped 10 frames before the end; after the last frame a click ends it; a click during
  it ends it at once. (0x409310, 0x4093cb)

### Leaving a zone (E-0414)

State 0x20 frees the zone, builds the 35 held flags from the list (0x410b80) and calls
the 3D side (0x42f2c2) with the flags, the zone's counter and a code:

| Code | From | 3D side |
|---|---|---|
| -1 | Retour, Backspace, end of zone 0 / 21 | back to 3D where the player was |
| -3 | RetourM | back to 3D with state byte +0x3C set to 0 and the 3D start (0x41fda9) run again (Q-0251) |
| -2 | option menu Quit | `PostQuitMessage` |
| n ≥ 0 | option menu Load | `Load3DGame(n)`, which re-enters the saved 2D zone |

If the counter passed is higher than the one the 3D side held, the zone is marked
solved in the 3D state (+0xCC + zone, `save.md`). Zone 21 plays the end (`boot.md`).

## 2D movies (E-0204, E-0417)

`Movie_Open(n, noSkip)` (0x414ace) plays entry n of the table at 0x4a7a08 inside its
rectangle over the current screen, with the `.CVY` mask when flagged (media spec);
`noSkip` = 0 lets a click end it. Entries used by the zones are named in the puzzle docs.

## Option menu (E-0415)

Opened by Esc in a zone (state 0x1F: saves the screen) or from 3D (message 0x503).
Background `option`; `options.SPR` (buttons), `cursopt.SPR` (volume knob), `lcaps.SPR`
(load icons), font `trobo12`. Buttons (`options` frame b drawn at its position while
pressed; cursor 11 over them):

| b | Rect | Opens |
|---:|---|---|
| 0 | (186, 66, 268, 85) | Load: background `load`, the saved games |
| 1 | (325, 166, 128, 19) | Volume: `options` frame 6 at (188, 162) and the knob |
| 2 | (325, 186, 128, 19) | View size: background `scrsize` |
| 3 | (325, 206, 128, 19) | Keyboard: background `keyboard` (a picture; Esc returns) |
| 4 | (187, 243, 268, 85) | Credits: `Credit00`..`Credit15` |
| 5 | (187, 331, 268, 83) | Quit: background `quit` |

While the volume row is open only buttons 0, 4, 5 and the volume controls respond: the
knob is `cursopt` frame 0 at (214 + v, 201), v = 0..210; clicking the bar
(205, 199, 227, 9) or dragging the knob ((214 + v - 6, 197, 15, 10)) sets v = x - 214.
v = volume % × 211 / 100; the player's volume is stored as DirectSound attenuation
`(percent - 100) × 50` (0 = full).

- **View size** (0x4a66a0): four rects (284, 174, 69, 15), (284, 238, 60, 15),
  (284, 301, 71, 15), (283, 357, 66, 15) for 640×480, 512×384, 400×300, 320×240 (the 3D
  view, 0x42f515); the current one shows `options` frame 7 + i at (246, 174), (244, 237),
  (246, 300), (246, 356). Stored in the player record.
- **Load** (0x40e78a, 0x40ebd9): the player's `GAME<player><slot>.BIN`, slots 1..34 that
  exist, oldest first; four rows at y = 168, 239, 309, 379: `lcaps` frame = slot (the
  object's icon) at (222, y) and "Game %u" (list position + 1) in `trobo12` colour 0xCE59
  at (304, y + 5). Row i clicks at (194, 140 / 211 / 281 / 351, 57, 57); arrows (436, 135, 13, 12) and (436, 401, 13, 12) scroll by one. Clicking a row closes the
  menu with `player × 100 + slot`.
- **Quit**: Yes (255, 281, 33, 17) / No (358, 281, 36, 17), `options` frame 11 + i at
  (255, 281) / (357, 281); No preselected (frame 12). Yes: from a zone, the held flags go
  into the 3D state; `GGAME` is written (first u32 = 1 from a zone, 0 from 3D),
  `USERS.BIN` rewritten, close with -2. No: back to the menu.
- **Credits**: `Credit%02u` for 0..15, each for 250 ticks or until a click or Space;
  then the menu.
- Esc anywhere in the menu goes back to its first page; Esc on the first page closes it
  (-1). Closing restores the screen, frees the sprites, applies volume and view size.

From 3D, closing the menu calls 0x42f515 (-2 quits, n loads, -1 resumes 3D).

## Credits after the end (E-0418)

Message 0x504 (mode 1 after `cinefin2`): sound `Credits` looping; `Credit00`..`Credit15`
full screen, 250 ticks each; a click or Space ends early; after the last, wait for the
button to be up, stop the sound and quit the program (0x409600, 0x409645, 0x42f508).
