# Rooms: the walkmap mode (Gilbert)

What `Gilbert.exe` does while a room (a *walkmap* in ge.dll's terms) is on screen: mode 1
of the main loop (boot.md), entered through GEInit call-back 1 (GotoWalkmap). Covered: the
room load, the per-frame drawing (room picture, objects, Gilbert, the foreground mask, the
panel), the mouse (walking, cursors, scrolling, the panel's buttons), Gilbert's movement and
animation, area hits, and the call-backs ge.dll uses in a room. ge.dll's side (path finder,
events, what an area hit runs) is `logic.md`; close-ups (mode 2), the inventory strip, the
dialogue overlay and the book (mode 4) are the screens specs. Addresses are `Gilbert.exe`;
names in `engines/gilbert/notes/names/GILBERT.EXE-rooms.csv`.

## Conventions

As in boot.md (640×480 back buffer, every picture clipped to the view window (64, 50)–
(576, 430), pictures drawn top-left at the given point with their own transparent colour,
`i1[n]`/`i2[n]`/`cur[n]` for items of `interface1.wxi`/`interface2.wxi`/`cursor.wxi`). Also:

- **Room pixels:** coordinates in the room picture `w<n>.wxi`, (0, 0) at its top-left. The
  room picture, its mask and the control grid × 16 have the same size in every room
  (E-0300).
- **Origin (ox, oy):** the screen position of room pixel (0, 0). A room pixel (px, py) is
  drawn at (ox + px, oy + py). ox ≤ 64 and oy ≤ 50 except for the small overshoot of edge
  scrolling (below).
- **Gilbert's frame (X, Y):** two doubles, the screen position of the top-left corner of his
  96×96 frame. **Gilbert's position** (what ge.dll sees) is the frame's centre in room
  pixels: (Trunc(X) − ox + 48, Trunc(Y) − oy + 48) (E-0308).
- **Cells:** the control map `ctrl<n>.map` has 16×16-pixel cells; cell (cx, cy) covers room
  pixels (16cx, 16cy)–(16cx + 15, 16cy + 15). `div` is integer division rounding toward zero.
- **W, H:** the room's width and height in pixels (control grid × 16).
- **The direction set:** four flags up, down, left, right, set only by call-back 20 and
  cleared by the room load (E-0304, E-0308).
- **Facing:** 0 up, 4 up-right, 8 right, 12 down-right, 16 down, 20 down-left, 24 left, 28
  up-left (E-0304, E-0308; Q-0104).

## State

| Name here | Global | Reset (E-0309) | Meaning |
|---|---|---|---|
| current room | 0x47ced4 | −1 | walkmap whose files are loaded |
| ox, oy | 0x47ce60, 0x47ce64 | 0, 0 | origin |
| shown | 0x47ce68 | false | the room's first frame (with its fade-in) has been drawn |
| frame | 0x47cea4 | 0 | Gilbert's picture: pattern of `gilbert.wxi` item 0 |
| facing | sprite +0x68 | 0 (sprite creation) | as above |
| counter | sprite +0x5c | 0 | animation position (single) |
| walking | sprite +0x6c | — | Gilbert moved this tick |
| last step frame | 0x47ceb0 | −1 | for the walk sounds |
| move divisor | 0x47cea8 | 30 | 20 while Ctrl is held |
| objects | 0x4816b4, count 0x47ced0 | 0 | room objects, 0x2c-byte records |
| radar l, t, w, h | 0x47ce7c..0x47ce88 | 0 | from GEWalkmapGetRadarRect |
| cursor | 0x47ce8c | 0 | `cursor.wxi` item drawn at the mouse |
| hover, pressed | 0x47cf2c, 0x47cf30 | −1 | panel button under the mouse / pressed this tick |
| radar pulse | 0x47ce90, 0x47ce94 | 0, rising | alpha 0..50 |
| new topic | 0x47ce98 | false | the book button blinks |
| blink | 0x47ce9c, 0x47cea0 | 0, rising | alpha 50..200 |
| room music | 0x47cf08 | not reset | name of the room music stream |

ResetState (after every successful new game or load, boot.md) also sets MusicVolume to 5,
SoundVolume to 4 and FullscreenVideo to 0 in memory, whatever the settings were (E-0309).

## Entering a room (call-back 1, GotoWalkmap)

ge.dll calls call-back 1 with (walkmap n, x, y, facing, flag) — its own GotoWalkmap passes
flag 0 — and then call-back 2 (E-0300). The EXE (room::Load 0x47a190):

1. Stops every sound stream (StopAll). If a room was loaded before (current room ≠ −1):
   **fade out** (below). shown := false; the timer stops; mode := 0x99 (the main loop does
   nothing, the menu actions nothing).
2. If n ≠ current room, loads (each path through *resolve*, boot.md):

   | File | Into | Role |
   |---|---|---|
   | `Data/maps/<n>/w<n>o.wxi` | DXImageList10 | object pictures |
   | `Data/maps/<n>/w<n>.wxi` | DXImageList4 = map layer 4 | room picture |
   | `Data/maps/<n>/ctrl<n>.map` | DxMapLib3 = map layer 3 | control map |
   | `Data/maps/<n>/w<n>m.wxi` | DXImageList5 = map layer 5 | foreground mask |

   The three image lists are emptied first. Re-entering the loaded room keeps them. The
   `cua*.wxi` files are the close-ups' (not loaded here). The flag argument is stored and
   never read. current room := n.
3. Layer sizes: layer 3 is W × H (grid × 16, the 16×16 patterns of `map.wxi`), layer 4 is
   the room picture's size in 64×64 tiles (E-0300).
4. **Start scroll and Gilbert:**
   - x ≥ 512: sx := max(256 − x, 512 − W); x < 512: sx := 0. X := x + sx.
   - y ≥ 320: sy := max(160 − y, 320 − H); y < 320: sy := 0. Y := y + sy.
   - ox := sx + 64, oy := sy + 50.

   So the view shows 512×320 room pixels above the panel, with the start point centred
   when the room allows it. Gilbert's frame's top-left lands on room pixel (x − 64, y − 50),
   his position is (x − 16, y − 2) (E-0300).
5. The direction set is cleared; facing := the facing argument.
6. mode := 1. Call-back 2's work (below) runs once here, then the object count is set to 0;
   ge.dll's own call-back 2 right after the goto fills the list again (E-0300).
7. The radar rectangle := GEWalkmapGetRadarRect() (left, top, width, height).
8. If a room music name is set, it restarts from the start, looped (so a room change always
   restarts the music). The timer runs again.

### Fades (E-0301)

The display's gamma ramp is saved at boot (boot.md). A work ramp (three 256-entry channels,
initially all zero) is sent to the display after each step:

- **Fade out** (room load): for entry i = 0 … 255, work[i] := saved[i] ÷ 4 (each channel),
  send. The picture ends at a quarter of its brightness.
- **Fade in** (the room's first frame): for i = 255 down to 0, work[i] := saved[i], send;
  then the saved ramp is sent once more.

Each fade is 256 ramp updates without a clock (Q-0300). Consequences: the first room after
starting the program fades in from black (the work ramp is still zero); a new game or a load
later in the same session has no fade-out (current room was reset to −1) and a fade-in from
the full ramp left by the previous fade-in, i.e. none visible.

## The main loop in mode 1

Each 16 ms tick (boot.md, Q-0207), after GEEllapsed and the variable-198 check (E-0304):

1. **Draw** the room (room::Draw, below).
2. **Mouse** (room::HandleMouse, below).
3. **Run key:** Ctrl held (GetAsyncKeyState) → move divisor 20, else 30.
4. If a dialogue is open: the dialogue's mouse and drawing (dialogue spec).
5. DXInput is updated (nothing in the room reads it).
6. **Gilbert moves:** DoMove(m) with m = 1000 div (LagCount + move divisor), LagCount =
   max(ms since the previous tick div 16, 1). On time: m = 32 walking, 47 with Ctrl.
7. The cursor (boot.md's DrawCursor: mouse clamped to x 72..568, y 58..422; `cur[cursor]` at
   (x − 16, y − 16)); flip.
8. Streams get their update: the room music (only once shown), the dialogue stream, the
   credits and menu streams, the sound stream (the menu stream's update is gated by the
   room-music flag).

The frame drawn in step 1 therefore shows the hover state and position of the previous
tick.

## Drawing (room::Draw 0x478674)

In this order (E-0302):

1. Clear.
2. Map layer 3 (the control map) with the rectangle around Gilbert: it has ShowTiles off, so
   nothing is drawn.
3. **Room picture:** layer 4 at the origin, rectangle R = (64, 50, 576, 370).
4. **Objects and Gilbert** (below).
5. **Foreground mask:** layer 5 at the origin, rectangle R = Gilbert's frame (Trunc(X),
   Trunc(Y), + 96, + 96).
6. **Panel** (below).
7. If shown: the carried object at the mouse (inventory spec). If not shown (the room's first
   frame): flip, draw steps 1–6 again, flip, fade in, shown := true.

### Map layers (TMaplibHolder::DrawLayer 0x461bc0)

A layer is one picture cut into 64×64 tiles, `cols` × `rows` of them, tile k = pattern k
(row-major). Drawn at origin (ox, oy) inside rectangle R:

- Nothing if ox > 576 or oy > 430 or ox > R.right or oy > R.bottom.
- First column c0 = (R.left − ox) div 64 if ox < 64 and ox < R.left, else 0; first row r0 =
  (R.top − oy) div 64 if oy < 50 and oy < R.top, else 0.
- Rows r = r0, r0 + 1, … while the row's y = oy + 64r is below 430 and below R.bottom and r
  < rows; in each, columns c = c0, … while x = ox + 64c is left of 576 and of R.right and c <
  cols: tile (r·cols + c) drawn at (x, y), fuchsia transparent, clipped to the view window.

For the mask this means: every whole mask tile from column c0 and row r0 up to the ones that
reach into Gilbert's frame is redrawn over the scene — with c0 or r0 = 0 whenever the room is
not scrolled on that axis, so tiles above and left of Gilbert are included then (E-0302).
The mask is the room's foreground (fuchsia elsewhere); it covers Gilbert and whatever
objects lie in those tiles.

### Objects and Gilbert (room::DrawObjectsAndGilbert 0x47897c)

The object records come from call-back 2 (below): picture p (item of `w<n>o.wxi`), room
position (x, y). An object's bottom is oy + y + h, h = the picture's height (E-0303).

1. Objects **behind** Gilbert: for i = count − 1 down to 0, if bottom ≤ Y + 96: draw picture
   p, pattern 0, at (ox + x, oy + y) with its transparent colour (items without a picture
   draw nothing).
2. **Shadow:** `gilbert.wxi` item 1 (`all`, black silhouettes, 120×120 patterns, 119 of them)
   drawn into the rectangle (X, Y, X + 96, Y + 96) with blend 8 at alpha 70 (Q-0202,
   Q-0301). Pattern: the frame itself when frame ≤ 119 (frame 119 is past the last pattern:
   no shadow); otherwise by facing: 0 → 15, 4 → 60, 8 → 30, 12 → 90, 16 → 105, 20 → 75, 24 →
   0, 28 → 45 (the first walking frame of that direction).
3. **Gilbert:** `gilbert.wxi` item 0, pattern *frame*, at (Trunc(X), Trunc(Y)), fuchsia
   transparent.
4. Objects **in front**: the same loop for the objects with bottom > Y + 96.

## Gilbert (TPlayerSprite::DoMove 0x476520)

Gilbert is a DelphiX sprite created at boot (boot.md) whose DoMove is called once per tick
with the move count m (E-0304). f := Trunc(counter).

**Walking.** The first matching case of the direction set moves him and picks the frame
base; each case first runs the area check (below), which never blocks the move:

| Set | X | Y | Base | Facing |
|---|---|---|---:|---:|
| up + right | + 0.053m | − 0.053m | 60 | 4 |
| up + left | − 0.053m | − 0.053m | 45 | 28 |
| down + right | + 0.053m | + 0.053m | 90 | 12 |
| down + left | − 0.053m | + 0.053m | 75 | 20 |
| up | | − 0.075m | 15 | 0 |
| down | | + 0.075m | 105 | 16 |
| left | − 0.075m | | 0 | 24 |
| right | + 0.075m | | 30 | 8 |

frame := base + f (f > 15 → 0); walking := true. At m = 32: 2.4 px per tick straight, 1.7 px
per axis diagonally.

**Standing** (no direction): f > 11 → f := 0; frame := standing base + f with the base by
facing: 0 → 168, 4 → 144, 8 → 156, 12 → 204, 16 → 120, 20 → 192, 24 → 180, 28 → 132 (any
other facing keeps the frame); walking := false.

`gilbert.wxi` item 0 thus holds 8 walking cycles of 15 frames (0 left, 15 up, 30 right, 45
up-left, 60 up-right, 75 down-left, 90 down-right, 105 down) and 8 standing cycles of 12
(120 down, 132 up-left, 144 up-right, 156 right, 168 up, 180 left, 192 down-left, 204
down-right).

**Counter:** + 0.02m walking (wraps to 0 above 14), + 0.002m standing (wraps above 11). At m
= 32 a step cycle takes about 23 ticks, a standing cycle about 188.

**Walk sounds:** while walking, when f differs from the last step frame: f = 0 → click list
1 item 6, f = 6 → item 7 (`menu.wxs`, E-0207). The last step frame := f every tick.

**Clamps** (after moving): Trunc(X) − ox < −48 → X := ox − 48; Trunc(X) − ox ≥ W − 48 → X :=
ox + W − 49; the same for Y with oy and H. Gilbert's position stays within the room.

The view does **not** follow Gilbert: only edge scrolling moves it (below).

## Walking and area hits

- **Target:** while the left button is held with the mouse in the walking area (below),
  every tick calls GEPathNewPath(mx − ox, my − oy): the mouse point in room pixels (E-0305).
  Dragging moves the target.
- **Following:** ge.dll's GEEllapsed walks the path, reading Gilbert's position (call-backs
  13, 14) and the cells (19), and sets the direction set through call-back 20 (logic.md).
- **Area check** (room::StepAreaCheck 0x476c00, on every moving tick, E-0307): the probe
  point is Gilbert's position moved 16 px in each set direction (− left, + right, − up, +
  down); v := the control cell under it (16-bit signed). If Gilbert's own cell (position
  div 16) is one of the current path's cells (GEPathGetItem) and 2 ≤ v ≤ 31:
  **GEWalkmapAreaHit(v − 1)**. This repeats on every tick the conditions hold.
- **Control cells as the EXE reads them:** 0 nothing, 1 the "no" cursor, 2..31 an area
  (n = v − 1: the room event walkmap·100 + n, logic.md). Cells outside the grid read 0
  (x < 0, y < 0, x > width, y > height); x = width reads the first cell of the next row and
  y = height reads past the grid into the file's tail (E-0307).

## Mouse (room::HandleMouse 0x4728ec)

The mouse rectangle is (x − 3, y − 3)–(x + 3, y + 3) and the button state as in boot.md
(left 1, right 2; a press is a change of the state). Each tick (E-0305):

1. pressed := −1. Inventory hovers are computed (inventory spec).
2. **Hover:** the first of `i2` items 8 (book), 0x26 (Menu), 0x27 (Kort), 0x2c, 0x2d (the
   inventory arrows) whose last drawn rectangle meets the mouse rectangle; none → −1.
3. **Walking area:** the point is in (74, 60)–(566, 420) and not in (289, 328)–(351, 380)
   (book button), (509, 336)–(539, 366) or (74, 360)–(566, 420) (the panel) — rectangles
   include their left and top edges, not their right and bottom:
   - left button held → GEPathNewPath (above);
   - cursor by the control cell under the mouse ((mx − ox) div 16, (my − oy) div 16): 1 →
     `cur[6]` EJ, ≥ 2 → `cur[7]` TOPOINTER, else `cur[0]` VANLIG.
4. **Otherwise:** cursor `cur[0]`, then edge scrolling, 6 px per tick, moving Gilbert's frame
   with the room so he stays on the same room pixel:
   - 64 ≤ mx ≤ 74 and ox < 64: ox += 6, X += 6, cursor `cur[2]` LEFT;
   - else 566 ≤ mx ≤ 576 and ox ≥ 586 − W: ox −= 6, X −= 6, cursor `cur[3]` RIGHT;
   - and independently my ≤ 60 and oy < 50: oy += 6, Y += 6, cursor `cur[4]` UP;
   - else 420 ≤ my ≤ 430 and oy ≥ 394 − H: oy −= 6, Y −= 6, cursor `cur[5]` DOWN.

   With the mouse clamped to 72..568 × 58..422 this happens at x 72–73, x 566–568, y 58–59
   and y 420–422, and also over the panel's left and right ends (the whole height).
5. **Press:** on a new button state: hover := −1; a left press sets pressed to the first hit
   of the same five items (else −1).

HandleMouse never selects `cur[1]` KLICK. Right presses do nothing in the room. Releasing the
button drops a carried object without effect outside the close-ups (E-0305). Room objects
are not clickable: everything in the room happens through control-map areas. No key does
anything in the room except Ctrl (running); Escape only skips films.

## Panel (ui::DrawRoomPanel 0x46dce8)

Drawn over the room every frame (E-0306):

1. `i1[0]` ibkg03 (the copper frame) at (64, 50).
2. **Eggs:** v = GEGetVariable(199): 0 → `i2[4]` iscr12 (empty slot), 1..6 → `i2[0x99..0x9e]`
   egg1..egg6, at (296, 374); other values nothing.
3. **Radar:** `i2[6]` iscr_radar (the island, 115×75) at (151, 347). The room's rectangle
   R = (152 + l, 348 + t, 152 + l + w, 348 + t + h) is filled with tan (221, 189, 142) at
   alpha a (blend 8, Q-0202) and outlined with a 1-pixel GDI rectangle in (249, 181, 40)
   (hollow brush; GDI's Rectangle draws the outline inside R). a pulses: − 1 per frame
   down to 0, then + 1 up to 50, and so on.
4. `i2[0x26]` "Menu" at (70, 368), `i2[0x27]` "Kort" at (70, 396), the arrows `i2[0xa8]` at
   (537, 380) and `i2[0xa9]` at (537, 400).
5. **Book button** `i2[8]` at (298, 333). While a new topic is flagged (call-back 21), `i2[0xa]`
   is also blended over it in (298, 333)–(346, 373) at alpha b, b falling by 2 per frame to
   50 and rising by 8 to 200, and so on.
6. **Hover** (from the previous tick): book → `i2[9]` at (298, 333); Menu → `i2[0x28]` at (70,
   368); Kort → `i2[0x29]` at (70, 396).
7. **Pressed** (one frame, from the previous tick's press): book → `i2[0xa]` at (298, 333),
   then the action; Menu → `i2[0x2a]` at (70, 368); Kort → `i2[0x2b]` at (70, 396); each then
   runs its action. The arrows 0x2c/0x2d have no picture and no action here.

### Actions in the room (gmenu::Action, mode 1)

| Item | Action |
|---|---|
| Book 8 | click 4 (list 1 item 4); load `bookimages.wxi`; the book set-up 0x46aa54(1, 0) (book spec); clear the new-topic flag; panel state −1; mode 4 |
| Menu 0x26 | boot.md: click 2, stop all sounds, menu music, mode 0 |
| Kort 0x27 | click 4; GEWalkmapAreaHit(99999) (event walkmap·100 + 99, formats README; logic.md); panel state −1; mode 2 (close-ups) |
| 0x2c / 0x2d | inventory scroll by 6 (inventory spec); not reachable from the room panel |

(E-0306; the book's arguments and globals are the book spec's.)

## Call-backs used in rooms

GEInit's call-backs (boot.md list; E-0308):

| # | Arguments | Gilbert.exe |
|---:|---|---|
| 1 | walkmap, x, y, facing, flag | room load (above) |
| 2 | — | object list: count := GEWalkmapGetNumObjects (at most 100); for each i, GEWalkmapGetObjectData(i) → record: object code (id·100 + state), picture index in `w<n>o.wxi` (the anim's +0x28), the state's +0x1c (Q-0100), the anim's x, y (+0x1c, +0x20; room pixels of the picture's top-left), pickable, text; plus the picture's rectangle offset by (64, 50) (not read in the room) |
| 7 | list, index, looped, wait | PlayWave: a list other than 1 and than the last loaded number first loads `Data/Sounds/misc/<list>.wxs` into wave list 3; then item *index* of wave list *list* (1..4) plays |
| 8 | list, index | StopWave |
| 9 | n | load `Data/Sounds/misc/<n>.wxs` into wave list 3 unless n is the last loaded |
| 10 | name, loop, kind | 0: room music — start `Data/Sounds/MUSIC/<name>.wav` if the name differs from the current one; remember the name. 1: stop all, dialogue stream `Data/Sounds/Dialog/<name>.wav`. 2: stop all, `Data/Sounds/misc/<name>.wav` at the sound volume |
| 12 | film name | movie::Play (boot.md); the room music restarts after it |
| 13 | — | Gilbert's x: Trunc(X) − ox + 48 |
| 14 | — | Gilbert's y: Trunc(Y) − oy + 48 |
| 17 | — | W div 16 (grid width) |
| 18 | — | H div 16 (grid height) |
| 19 | x, y | control cell (x, y), as read above |
| 20 | d | direction set: right if d ∈ {4, 8, 12}, left if d ∈ {20, 24, 28}, up if d ∈ {0, 4, 28}, down if d ∈ {12, 16, 20}; anything else clears all four (Gilbert stands) |
| 21 | — | new topic: flag on (the book button blinks), list 1 item 10 "NewTop" |

## Quirks kept from the original

- The view never follows Gilbert; he can walk out of sight and the player scrolls with the
  edges (E-0305).
- Edge scrolling steps 6 px without clamping to the limit: scrolling left or up can
  overshoot by up to 5 px (black strip), right stops 4–9 px short of the room's right edge
  and down 18–24 px short of the bottom (E-0305).
- The foreground mask is drawn only around Gilbert, and from the first row or column when
  the room is not scrolled on that axis; objects are not masked elsewhere (E-0302).
- Frame 119 (last frame of walking down) has no shadow (E-0303).
- The area hit repeats every tick while Gilbert keeps walking into the area on his path
  (E-0307).
- A room change restarts the room music even when it stays the same (E-0300).
- After a new game or a load, the volumes and full-screen video are back to 5, 4 and off in
  memory until changed on the Settings page (E-0309).
