# The inventory (`aList`, the "bag") (Ring, DVD)

Evidence: E-0060..E-0065. Addresses are `RING_DVD.EXE`; decompiles in
`engines/ring/notes/decomp/bag/`. The class names itself `aList` in its error strings
(`aList::add`, `aList::openImage`, `aList::checkClickOnListHotSpots`); the application
keeps it at app+0x8d (`AGV_bag`). All its coordinates are window pixels (the 640×480
client area, the 16-pixel black band at the top included).

## Fields (constructor 0x416d70)

| Offset | Meaning | Value |
|---|---|---|
| +0x00 | objects in the bag (list of object pointers) | empty |
| +0x04 | their display items, parallel to +0x00 (an icon picture or the bag animation) | empty |
| +0x08 | hot spots (below) | empty |
| +0x0c, +0x10, +0x14, +0x18 | first slot x, slot y, slot height, slot width (0x417d40) | 18, 42, 44, 100 |
| +0x1c, +0x20 | origin added to every position (0x417d20) | 0, 0 |
| +0x24 | visible slots (0x417dd0) | 6 |
| +0x28 | scroll: index of the first visible object | 0 |
| +0x2c | object count | 0 |
| +0x30, +0x34 | background position (0x417d60) | 0, 0 |
| +0x38 | background picture | `bagbgr.tga` |
| +0x40 | left arrow picture | `bagarr.tga` |
| +0x48..+0x54 | left arrow hot spot x, y, width, height (0x417d80) | 0, 24, 30, 448 |
| +0x58, +0x5c | left arrow picture position (0x4192a0) | 7, 48 |
| +0x60, +0x64 | right arrow picture position (0x4192c0) | 627, 48 |
| +0x6c | right arrow picture | `bagarr.tga` |
| +0x74..+0x80 | right arrow hot spot x, y, width, height (0x417da0) | 610, 24, 30, 448 |
| +0x84 | "menu" highlight picture | `menu_gur.tga` |
| +0x88, +0x8c | its position (0x417de0) | 335, 8 |
| +0x94 | shown (byte) | 0 |
| +0x95 | the object in hand (id, 0 = none) | 0 |
| +0x9d | scroll repeat time in ms (0x419280, which also stores the tick at +0xa1) | 500 |
| +0xa1 | tick of the last scroll | 0 |
| +0xa5 | the name text (`aText`) | — |
| +0xa9 | its font | 1 |
| +0xad, +0xb1, +0xb5 | its colour | 245, 235, 50 |
| +0xb9, +0xbd, +0xc1 | its background colour (opaque, `spec/text.md`) | 0, 0, 0 |
| +0xc5 | the name's y | 90 |
| +0xc9 | load-from byte of the bag's pictures | Init's app+0x58 |
| +0xca, +0xce | Erda pictures, normal / lit | `erda_gun.tga`, `erda_gur.tga` |
| +0xd2 | Erda available (byte) | 0 |

The values in the last column other than the constructor's are set once in
`aApplication::Init` (0x408941..0x4089e8). The pictures come from
`aList::openImage(bgr, "", arr, "", "", arr, "", menu_gur, load_from)` (0x417440, called at
0x408a1f): with load-from `'f'` (the DVD) the archive member `\LIST\<name>` of the
language's `SY.AT2` (format `\%s%s` with `LIST\`), with `'e'` the file
`<install path>LIST\<name>`; `erda_gun.tga` and `erda_gur.tga` are fixed names. In the
archive: `bagbgr` 640×87, `bagarr` 6×6, `menu_gur` 52×16, `erda_gun` / `erda_gur` 52×40
(all packed TGA). Then 0x4178c0 builds the hot spots.

## Hot spots (0x4178c0)

In list order (hot spot test 0x4238b0: enabled, x0 ≤ x < x1, y0 ≤ y < y1; the first hit
wins):

| # | Rectangle | Enabled at first | Type (+0x19) | Value (+0x15) |
|---:|---|---|---:|---:|
| 0 | left arrow: (0, 24)–(30, 472) | no | 0x3e9 | 0x3e9 |
| 1 | right arrow: (610, 24)–(640, 472) | no | 0x3ea | 0x3ea |
| 2 | "menu": (200, 0)–(640, 30) | yes | 0x3eb | 0x3eb |
| 3 | Erda: (90, 0)–(150, 30) | +0xd2 | 0x3ed | 0x3ed |
| 4.. | slot i (0..5): (19 + 100i, 42)–(117 + 100i, 87) | no | 0x3ec | i |

The drawing enables and disables 0, 1 and the slots every frame (below). Hot spot 3 and
+0xd2 follow the zone: `SetZone` (0x402210) disables Erda in zones 1 (SY) and 7 (AS)
(0x417cf0) and enables it in every other zone (0x417cc0).

## Contents

- `BagAdd(id)` (0x406330): refused for id 0 or an id that is not an object; else
  `aList::add` (0x417e80): nothing when the object is already in the bag (0x4184d0);
  otherwise the object is inserted **at the front** of +0x00, and its display item at the
  front of +0x04: the object's bag animation when it has one (`ObjAddBagAni`, object
  0x4210f0), its current frame becoming the animation's picture; else an icon picture
  (0x42d260): `\LSTICON\<icon>.tga` in the archive (load-from `'f'`), or
  `<install path>LSTICON\<icon>.tga` on disk, `dummy.tga` when that file is missing
  (`<icon>` = `AddObj`'s third argument, 0x426cb0). Count = list size; when the count
  exceeds the visible slots the scroll goes back to 0.
- `BagRem(id)` (0x4063e0 → 0x4181c0): removes the object and its item (an animation item
  is stopped, 0x422290); count updated; when the count is at most the visible slots the
  scroll goes back to 0.
- `BagRemAll` (0x406470 → 0x418360): empties both lists.
- `BagIsIn(id)` (0x4064a0 → 0x4184d0): whether the object is in the bag.

## Opening and closing (right button, 0x40afe0)

`WM_RBUTTONUP` (window procedure 0x40f1ef) calls 0x40afe0. When no drag is active, the
menu is not up (app+0x6f) and puzzle 1 is missing or not in mode 2:

- shown → hide (0x419350: +0x94 = 0, 0x417e00 frees the icon pictures and stops the
  animations), then 0x40ded0: the rotation frozen at opening gets +0x67 = 0 (looking
  around with the mouse resumes, `spec/rotation.md`);
- hidden → drop the object in hand (0x406570), show (0x4192e0: +0x94 = 1, every bag
  animation started with the tick count), remember the current rotation's +0x67
  (0x495570, for Erda below), then 0x40de90: when a rotation is current (app+0x89) its
  +0x67 = 1 (0x4103c0; looking around stops) and it is remembered (0x495244).

Nothing else pauses: timers, sounds, rotation layers and animations go on. `StartMenu`
(0x40dc80; both its branches, 0x40dccd and 0x40de36) hides the bag (without 0x40ded0) and
drops the object in hand.

## Drawing (0x418ca0, every frame while shown)

Drawn after the view and puzzle 1, before the drag, tracking, dialogues and the cursor
(`RenderFrame` 0x40ed20). Nothing is drawn unless the background, both arrows and the
menu picture loaded. With origin (ox, oy) = (+0x1c, +0x20), all with draw type 3:

1. The background at (ox + 0, oy + 0).
2. Scroll 0: hot spot 0 disabled; else the left arrow at (ox + 7, oy + 48) and hot spot 0
   enabled.
3. Scroll + 6 < count: the right arrow at (ox + 627, oy + 48) and hot spot 1 enabled;
   else hot spot 1 disabled.
4. When the "menu" flag (0x4a1928) is set: `menu_gur` at (ox + 335, oy + 8); the flag is
   cleared.
5. When Erda is available (+0xd2): `erda_gur` at (ox + 103, oy) if the Erda flag
   (0x4a1929) is set (then cleared), else `erda_gun` at (ox + 103, oy).
6. The objects scroll .. min(scroll + 6, count) − 1, slot k = 0, 1, …: slot left
   x = ox + 18 + 100k, y = oy + 42. An icon (item type 1, +0x6c) is loaded if needed
   (`\LSTICON\<icon>.tga` again) and drawn at (x + 50 − w / 2, y), w its width (+0x29);
   an animation item (type 2) advances (0x416870 with the tick count) and draws its
   current frame there (0x422950). The item keeps the slot centre x + 50 (+0x55) and the
   name's y, 90 (+0x59).
7. Slot hot spots: slot k enabled when an object is drawn in it, disabled otherwise.

Bag animations (`ObjAddBagAni(object, 1, 3, frames, 12.5, 4)`: 20 frames in 82 of the 85
calls, 13 in two, 1 in one) run at 12.5 frames per second, looping (flags 4), from
`\lsticon\<icon>\<icon>.NNNN.tga` (frames 0001.. in `SY.AT2`;
image kind 4 is the `LSTICON` folder in `aAnimation::Alloc` 0x421d10).

## Tracking while shown (0x408dd0 → 0x418a70)

With the bag shown, tracking tests only the bag (the window position), nothing else:

- left / right arrow: when the scroll can move (left: scroll > 0; right: scroll < count)
  and more than 500 ms passed since the last scroll, it moves by one; the cursor is not
  changed. Holding the mouse on an arrow scrolls every half second.
- "menu": sets 0x4a1928 (the highlight is drawn next frame).
- slot k: object scroll + k's name (object +4, 0x426c10; `AddObj`'s second argument) is set
  as the text (0x42c550) and drawn at once (0x414df0) at x = centre − width / 2, clamped to
  0 .. 640 − width, y = 90: font 1, colour (245, 235, 50) on black. The cursor is not
  changed.
- Erda (when available): sets 0x4a1929.
- On the menu band, Erda or nothing, the cursor becomes 0x32 (1 with an object in hand, 3
  during a drag); the "nothing" event (0x40cde0) is raised in every case.

## Clicking while shown (`MouseLeftEvent` 0x409d90 → 0x418520)

The left-button release (and a key's click, 0x40b060) passes the window position. Only
the bag is tested:

- left arrow: scroll − 1 when above 0; right arrow: scroll + 1 when below the count; the
  repeat clock restarts. Nothing else.
- "menu": `StartMenu(1)`.
- Erda: by zone (0x402450): SY or AS: logged, nothing. Otherwise the world is left for the
  hub: `LoadSaveTimer(<file>, 2)` saves the world (`alb` for zones 2 NI and 3 RH, `sie` for
  4 FO, `log` for 5 RO and 8 N2, `bru` for 6 WA; `spec/save.md`, to come), then SY's
  variables for that world: dword 90013 / 90015 / 90014 / 90016 = the zone, byte 90009 /
  90011 / 90010 / 90012 = 1, and where the player was: when a puzzle is current byte 90017
  / 90019 / 90018 / 90020 = 1 and dword 90021 / 90023 / 90022 / 90024 = the puzzle, else
  byte 90017.. = 0, dword 90021.. = the rotation and byte 90025 / 90027 / 90026 / 90028 =
  its +0x67 before the bag opened (0x495570). Then AS's 0x437750(13): the hub chamber
  (`games/ring/docs/as.md`). A failed save is logged and nothing happens.
- slot k: the object scroll + k goes in hand (+0x95). Then:
  1. the inventory list click event (0x40c1f0) gets the object (only FO has a handler,
     0x441d50; it uses some objects at once and then clears app+0x78);
  2. app+0x77 is 1 (set by `Init` and never cleared in the DVD): the bag is hidden
     (0x419350, 0x40ded0);
  3. app+0x78 cleared → set back to 1 and the object dropped (0x406570); otherwise the
     object's cursors are installed (0x40b860, below);
  4. the mouse is moved to (320, 240) (`SetCursorPos`).

## The object in hand

`0x406530` tells whether there is one (+0x95 ≠ 0), `0x406550` returns it. 0x40b860(object)
replaces cursors 1 and 2 with the object's (`ObjSetPasCur` / `ObjSetActCur`, object
+0x15.. / +0x32..: offset x, offset y, frames, kind, fps, flags, image kind, load-from):

- cursor 1 (passive): kind 3 → `CurAdd(1, "<icon>_p", 3, 2, image kind, load-from)`; kind 4
  → `CurAdd(1, "<icon>", 4, 2, frames, fps, flags, image kind, load-from)`; then its
  offset (`CurSetOffset` 0x402860);
- cursor 2 (active): likewise with `<icon>_a` for kind 3.

Most objects use `ObjSetPasCur(o, 22, 22, 0, 3, 0, 0, 3)` and `ObjSetActCur(o, 22, 22,
20, 4, 12.5, 4, 4)` (79 each): passive = the picture `\cursor\<icon>_p.tga`, active = the
bag animation (image kind 4, `\lsticon\<icon>\…`), both offset (22, 22). Four use the
offset (2, 43); three have an animated passive cursor (`ObjSetPasCur(o, 22, 22, 1, 4, 1,
4, 4)`); the active frame counts follow their bag animations (13, 1). The 2 passed to `CurAdd` is the cursors' type: dropping deletes all type-2
cursors.

Tracking with an object in hand (`spec/cursor.md`): cursor 2 on an accessibility, 1 on
nothing, movabilities keep their own cursor.

**Dropping** (0x406570): +0x95 = 0 and `aCursorHandler::DeleteTypeDelete(2)` (cursors 1
and 2 go). It happens: when the bag opens, through a movability (after the "movability
done" event, when app+0x75 is set, which is always), on `StartMenu`, and when a zone
handler calls it.

**Using** an object: a click on an accessibility goes to the zone's object-click event
(0x40bbb0) with the object **still in hand**; the zone handler reads it (0x406530 /
0x406550) and drops it itself (e.g. AS 0x4364a0). A click on nothing keeps it.

**Taking** an object from the scene: a click on an accessibility whose object has flag
bit 3 (8, `AddObj`'s last argument) raises the event 0x40bed0 (FO 0x441860, WA 0x4392a0);
then, unless the handler cleared app+0x74 (WA and RH do, 0x43932e.., 0x443c49..), the
object in hand is dropped, the clicked object goes in hand (`aList2::SetObjectClicked`
0x4191f0: any object of the object list, not only bag objects) and its cursors are
installed (0x40b860); app+0x74 is set back to 1.

## Not covered

The bag in saved games (`aApplication::LoadSave`, "Bag"); app mode 3 (draws the bag as the
view) is never set by the DVD's code (0x40b7b0 is only called with 1, 2, 4 and a loaded
value), so it only matters after loading a save (`spec/save.md`, to come).
