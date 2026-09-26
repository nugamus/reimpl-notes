# The 3D side: mouse, picking, cursors, clicks, inventory bar

How the player acts in a 3D scene: the mouse cursor, what is under it, the cursor shapes,
what a click does, the inventory bar and carried objects, and the ways out of the 3D.
Scene loading and the 3D ↔ 2D switch are in `scene.md`, the tick and the keyboard in
`movement.md`; each scene's objects and reactions in `games/mission-sunlight/docs/<scene>.md`.
The 2D side (zones, their own inventory, the option menu) is `ui.md`.

## Mouse (E-0313)

- DirectInput mouse, relative (0x472710): each frame (0x420e07, step 1 of the frame,
  `movement.md`) the deltas are added to the cursor position (0x4aba34, 0x4aba38; 320, 240
  at start) and the result clamped to 0..639 × 0..479. No scaling.
- The **left button** state (bit 7 of `rgbButtons[0]`) goes to `click` (0x5b7fac), the
  right one to 0x5b7fa8 (unused by the 3D). It is the button's **level** at that tick: there
  is no edge detection, so a held button reads as a click on every tick; frame callbacks
  clear `click` when they end, and scene code guards its actions with state.
- The keyboard does not move the cursor.

## Picking (E-0313)

`Pick` (0x41eb20) returns the handle of the scene node under the cursor, or -1:

1. -1 when the cursor is outside the viewport (inclusive bounds): view size 0: 0..640 ×
   0..480; 1: 64..576 × 48..432; 2: 120..520 × 90..390; 3: 160..480 × 120..360.
2. The point tested is the cursor position, or, while a 3D object is carried (below), the
   centre of the current cursor image (position + half its width and height).
3. 0x439b90(camera, x, y) runs the renderer's scene traversal from the camera (0x450160)
   with a pick routine (0x43a150) in place of the polygon drawers and an initial depth of
   2^31; it keeps the node of the nearest polygon covering (x, y) and returns its handle
   (0x433740), -1 if none. Hidden nodes (flag bit 0) are skipped by the traversal
   (`scene.md`). The pick routine's own tests belong to the renderer spec.

Scene code compares the handle with its object table and, for distances, reads the node's
position relative to the camera (0x436200: the node's +0x4c) and takes the length of its
(x, z) part; the museum uses 1,200 for clicks and hover, other scenes their own limits
(flow docs).

## Cursors (E-0314)

The cursor images are 16-bit TGAs from `DATA\GRAPHS_2D\` loaded when a scene loads
(0x426594, `Cursor_Check` 0x4240f0 around `LoadTga`, E-0104) into a table of 66
`{pixels, width, height}` (0x599140). A missing file gives a 32×32 block of 0xFFFF. Pure
green is transparent when drawn (`Blit16Keyed`, E-0104).

| Index | File | Use |
|---:|---|---|
| 0..34 | `op_0` .. `op_34` | object in hand: the 35 inventory objects |
| 35, 36 | `def_0`, `def_1` | bar scroll arrows, pressed |
| 37 | `fleche` | **arrow**, the default |
| 38 | `main` | hand (hover, cursor type 2) |
| 39 | `curza` | zone (hover, cursor type 3: a 2D zone) |
| 40 | `curferme` | set by cafe, mangeurs and pont over a node while carrying; replaced before drawing (below) |
| 41 | `sablier` | hourglass (redraw frames, `movement.md`) |
| 42..57 | `Ct0` .. `Ct15` | sunflower counter on the bar |
| 58 | `curdoigt` | finger (hover, cursor type 4; return icon) |
| 59 | `acces` | access (hover, cursor type 6) |
| 60 | `deja_vu` | already seen (hover, cursor type 0x3C) |
| 61 | `buche` | carrying the log |
| 62 | `fagot` | carrying the faggot |
| 63 | `cle` | carrying the key (`clef`) |
| 64 | `manivel` | carrying the crank handle (`poignee04`) |
| 65 | `retour` | the return icon (drawn, never the cursor) |

The current cursor is the byte 0x5baf40 (set to 37 when a scene loads). It is drawn every
frame with its **top-left corner at the cursor position** (0x424190), after the scene and
the bar.

## Hover and click (E-0315)

Each scene's frame callback starts the same way (e.g. auberge 0x41a42b, museum 0x42b776):

1. `h = Pick()`.
2. If the cursor is a hover shape (38 hand, 39 zone, 58 finger, 59 access, 60 déjà vu), it
   is reset to the arrow (37). Object cursors (0..34) and carried-object cursors stay.
3. If `h` is in the scene's object table:
   - `click` set and cursor = arrow: the **scene's action** for that object (a zone, an
     exit, an animation, picking up an item, …; flow docs);
   - otherwise, cursor = arrow: the hover shape from the object's `cursorType` (+0x32):
     2 → hand, 3 → zone, 4 → finger, 6 → access, 0x3C → déjà vu, anything else (0, 0xFF…)
     → arrow. Scenes change an object's `cursorType` at run time, e.g. to 0xFF once it has
     been used. The museum knows only 2, 3 and 4 and requires the object within 1,200.
4. Using an object in hand on a scene object (cursor 0..34, or a carried object) is scene
   code (flow docs).
5. Clear `click`; advance the scene's playing animations (E-0318); if a reload or the 2D
   was requested this frame, redraw with the hourglass (0x4221f6).

Picking up an item (every scene the same way): hide its node (0x435970), set the cursor to
the item's index (0..34), open the bar (state 2, below) and set the scene's own "taken"
flag. The item is only in the inventory once it is dropped into the bar.

## Inventory bar (E-0316)

State `bar` (0x4acfa0): 0 hidden, 1 shown, 2 opening, 3 closing; `barY` (0x4acfa4, 480 at
start); the bar image `Invent.tga` (height `barH`). Every frame (0x426171):

- **opening**: the first frame plays `bar_obj` once; `barY -= 8`; at `480 - barH` → shown.
- **closing**: `barY += 8`; at 480 → hidden, and the resume file is written (autosave,
  0x42f873, `save.md`).
- opening, shown, closing: draw `Invent` opaque at (0, `barY`), 640 wide.
- Space (released) toggles: hidden → opening, shown → closing (0x4223e8).
- **Clicks while shown**, cursor = arrow (the hand does nothing): the left arrow box, x 12..44 and y
  `barY + 15`..`barY + 47` (0x425f71 bounds are inclusive), draws `def_0` at (10, `barY` +
  13) and scrolls left (`first` = 0x4e311c, minus 1, not below 0); the right arrow box at x
  500..532 draws `def_1` at (503, `barY` + 13) and scrolls right (`first` + 1, undone when
  fewer than `first` + 6 objects are held).
- **Clicks while shown**, cursor = an object (any other cursor), inside x 0..640, y `barY`
  - 30 .. `barY` + 70: play `cf_clic3`; `inventory[cursor] = 1` (the 35 u32 at 0x651220,
  shared with the 2D, `ui.md`); cursor = arrow; if more than 6 objects are held, `first` =
  count - 7; close the bar. A click with object 0 in hand while the bar is shown (inside the box or
  not) sets 0x4abbd8 (the museum's first step, `musee.md`).
- Held objects (0x426071): skip the first `first` held (in index order), draw at most 6
  with their `op_<n>` image centred on x = 100, 170, 250, 310, 380, 450 (table 0x4acfa8)
  and on y = `barY` + 30.
- Sunflowers (0x425ff2): image `Ct<n>` for the count n (byte 0x4abbd4) at x = 556, centred
  on y = `barY` + 31.

These draws happen in every state; while hidden `barY` = 480 puts them off screen.

## The return icon and the ways out (E-0310, E-0315)

- In any scene but the museum, with the bar hidden, when the cursor is inside x < `w` + 10
  and y > 474 - `h` (`w`, `h` of `retour`), the frame draws `retour` at (10, 474 - `h`)
  (0x426171) and the cursor becomes the finger (0x4223e8); a click there leaves to the
  museum like Backspace (`scene.md`).
- Escape: the option menu; Backspace: the museum; clicks on zone objects: a 2D zone; scene
  exits: another scene (`scene.md`).

## Carrying a 3D object (E-0317)

Some scenes let the player pick up a scene node and carry it to another (cafe, mangeurs,
pont; flow docs): the scene hides the node, sets 0x502734 = 1 and keeps the node's handle
in 0x502a80. While it is set, the frame (0x4223e8) picks the cursor by the carried node's
name: `fagot` → 62, `buche` → 61, `poignee04` → 64, `clef` → 63; and `Pick` uses the cursor
image's centre. The scene clears 0x502734 when the object is used or put back. The cafe,
mangeurs and pont frame callbacks set cursor 40 (`curferme`) while carrying over a node;
the callback runs after the cursor is drawn and the next frame's name rule replaces it
before the next draw, so for these four objects it is never seen.
