# Cursors, hot-spot tracking and clicks (Ring, DVD)

Evidence: E-0039 (cursors), E-0040 (tracking and clicks). Addresses are `RING_DVD.EXE`.

## The cursor handler (`aCursorHandler`, app+0x59)

A list of cursors, each with an id, a name, a kind, an offset (x, y) and a current index.
`Set(id)` (0x41f7a0, `CurSet` 0x402840) makes the cursor with that id current;
`SetOffset(id, x, y)` (0x41f820, `CurSetOffset` 0x402860) stores its offset.
`GetType` (0x41f8c0) returns the current cursor's kind, first selecting cursor 0x32 when
the current index is out of range.

`CurAdd` has two entry points into `Add` (0x41efb0):
`CurAdd(id, name, kind, unk_4, image_kind, load_from)` (0x402750, kinds 1..3; kind 4
is refused) passes `Add(id, name, kind, unk_4, 0, 0, 0, image_kind, load_from)`;
`CurAdd(id, name, 4, unk_4, frames, fps, flags, image_kind, load_from)` (0x4027c0) only
accepts kind 4. An id that already exists is refused.

| Kind | Object | Picture |
|---:|---|---|
| 1, 2 | vtable 0x47e588 | a Windows cursor: kind 1 looks the name up among `IDC_ARROW`, `IDC_APPSTARTING`, `IDC_CROSS`, `IDC_IBEAM`, `IDC_ICON`, `IDC_NO`, `IDC_SIZE`, `IDC_SIZEALL`, `IDC_SIZENESW`, `IDC_SIZENS`, `IDC_SIZENWSE`, `IDC_SIZEWE`, `IDC_UPARROW`, `IDC_WAIT` (0x42fd70), kind 2 loads the name from the EXE's resources |
| 3 | vtable 0x47e544 | one 32-bit TGA; must be 32 bits (`aCursorImage::Alloc`) |
| 4 | vtable 0x47e504 | an animation of `frames` 32-bit TGAs |

File names for kinds 3 and 4, with `image_kind` 3 (the only value the game uses) and the
load-from byte (`ART_CURSOR`, `spec/boot.md`):

- kind 3, archive: `\cursor\<name>.tga` in the language's `SY.AT2` (format 0x488228,
  folder string `CURSOR`); disk: `<prefix>cursor\<name>.tga`, and `dummy_p.tga` in the same
  folder when that file is missing (0x488214, 0x488200).
- kind 4, archive: `\cursor\<name>\<name>.NNNN.tga` with NNNN = frame index + 1, four
  digits (0x488ee4, `aAnimation::Alloc` 0x421d10, `DisplayActiveFrame` 0x422950); disk:
  `<prefix>cursor\<name>\<name>.NNNN.tga` (0x488eb4).

The archive holds `cur_idle.0001..0015`, `cur_muv.0001..0020`, `cur_hotspot.0001..0019`
and the single pictures `cur_back`, `cur_busy`, `cur_menuidle`, `cur_menuactive`,
`ni_handsel` (plus the inventory cursors, `spec/bag.md`). File lookup is
case-insensitive (`spec/resources.md`).

The cursors of the game set-up are listed in `spec/boot.md` ("Game set-up"); read with the
signatures above, `cur_idle` is `CurAdd(0x32, "cur_idle", 4, 1, 15, 12.5, 4, 3, …)`:
15 frames at 12.5 frames per second, flags 4.

## Animated cursors

`aCursorAnimation::Init` (0x42f8f0) initialises an animation (`aAnimation::Init` 0x416450
through `aAnimationImage::Init` 0x4219f0) with `frames`, `fps`, start frame 1 and `flags`,
draw type 3, and starts it at once (0x416670, with the tick count). `unk_4` = 1 makes it
load all frames at initialisation.

`aAnimation` in general (`aAnimation::Init`, advance 0x416870):

- The frame index starts at start frame − 1 (`SetStartFrame` 0x416bd0; the start frame
  counts from 1).
- `flags`: bit 2 (4) plays forward and loops to the start frame after the last; 8 plays
  backward and loops; 0x10 and 0x20 ping-pong (0x10 starts forward, 0x20 backward); bit 1
  (2) frees each frame's picture once it is replaced.
- Frame time: `1000 / fps` truncated to whole milliseconds (x87 division of 1000.0 by
  `fps`, then `__ftol`): 80 ms at 12.5.
- Each time the animation is drawn, it first advances: when the tick count has moved more
  than the frame time past the last step, the index moves one frame and the step time
  becomes now. The first call after starting only clears the start flag.

## Drawing the cursor

Every frame, after everything else (`spec/boot.md`, "Frame"; the draw is the handler's
`Set(HDC, x, y)` overload 0x41f720), when the current cursor is of kind 3 or 4 it is drawn at (mouse x − offset x, mouse y − offset y): kind 3 with draw
type 3, kind 4 by advancing and drawing its current frame with draw type 3
(`spec/drawing.md`). Kinds 1 and 2 are Windows cursors, set with `SetCursor`. The mouse
position is read once per frame with `GetCursorPos` (0x40f6c0) into screen coordinates.

## Hot-spot tracking (0x408dd0, every frame)

The frame calls it with the mouse position when tracking is on (a flag cleared by
0x40e610 when a busy phase starts; the first frame after that only sets it again). It
finds the first enabled hot spot under the mouse; a hot spot contains (x, y) when
`x1 ≤ x < x2` and `y1 ≤ y < y2` (0x4238b0). The search, in order:

1. When the inventory is shown, its own hit test (0x418a70) decides; on no hit the
   default below applies.
2. **Puzzle 1** (SY's dialogue puzzle): its accessibilities; in mode 2 (a dialogue is
   up, `PuzSetMod`) an accessibility of another object than the dialogue's object ends
   the search as "none". A hit: the cursor becomes the hot spot's cursor id, and the
   "on an accessibility" event (0x40ca80) gets (object, the hot spot's `unk_19`, puzzle id,
   1, x, y). In mode 1 its movabilities are then tested: a hit sets the hot spot's cursor
   and raises "on a movability" (0x40cc10). In mode 2 nothing else is tested: the cursor
   becomes 0x32 and SY's "nothing" handler (0x433bc0) runs.
3. The **current rotation** (app+0x89), unless its byte +0x28 is set: its accessibilities, then its
   movabilities, as above (the event's fifth argument is 0).
4. The **current puzzle** (app+0x81): its list of visuals (0x41d7a0) first, then its
   accessibilities and movabilities, as above (fifth argument 1).
5. Nothing: the cursor becomes 0x32 and the "nothing" event (0x40cde0) is raised.

While an object is being dragged, or an inventory object is in hand (0x406530), the
cursors chosen above are replaced: drag active → 4 on the dragged hot spot, else 3;
object in hand → 2 on an accessibility, 1 on nothing, a movability keeps its own
(`spec/bag.md`, E-0063).

The accessibility and "nothing" events are raised every frame the mouse is on (or off)
a hot spot, not once on entering. `unk_19` is the last argument of `ObjAddPuzAcc` /
`ObjAddRotAcc`; the zone code uses it to tell an object's accessibilities apart.

## Left click (`aApplication::MouseLeftEvent` 0x409d90)

Called when the left button is released (`WM_LBUTTONUP` with y < 465, 0x40af80) with the
mouse position of the last frame: the screen position for puzzle 1 and the current
position in the view (the panorama position for a rotation, 0x4107f0) for the rest
(E-0049). An active drag is ended first ("Dragging" below). The same search order as
tracking; on the first hit in puzzle 1, then the current puzzle (rotations:
`spec/rotation.md`):

- when the object's flag byte (`AddObj`'s last argument, object +0xc) has bit 0 set, the
  object-click event (0x40bbb0) gets (object, `unk_19`, puzzle id, 1); if the mode is now
  4 (a zone change is pending) the click ends;
- bit 3 set: the event 0x40bed0 (`spec/bag.md`);
- then tracking runs once more.

A click in puzzle 1 in mode 2 that hits nothing ends there. A hit on a movability takes
the player through it (`spec/rotation.md`).


## Dragging (drag control, app+0x99)

Evidence: E-0049. One drag at a time. Its state (0x426040 fills it, 0x4260d0 clears it):
the press position, the previous and current mouse positions, active (+0x20), the object
(+0x21), the accessibility index (+0x25), the hot spot (+0x2d), the hot spot's `unk_19`
(+0x31), the puzzle or rotation id (+0x35), 1 for a puzzle / 0 for a rotation (+0x39),
the press tick, a move count, the drag mode (+0x45, 1 after a start) and a limit
rectangle (+0x49; 0x4260d0 sets it to (0, 16)–(640, 464)).

- **Start** (left button down, 0x409630, not while the inventory is shown): the search
  order of tracking (puzzle 1 with its mode-2 rule, then the current puzzle, then the
  current rotation), first enabled hot spot under the mouse. When its object's flag byte
  has bit 1 (2) set, the "button down" event (0x40bd40) gets (object, `unk_19`, puzzle
  id, 1 for a puzzle); when it has bit 2 (4) set, the drag starts at the mouse position
  and the drag event (0x40c060) gets phase 1. Then tracking runs.
- **Starting** also replaces cursors 3 and 4 with the object's drag cursors (0x40b9b0,
  from `ObjSetPasDraCur` / `ObjSetActDraCur`): cursor 3 (passive) of the given kind; for
  kind 3 its picture is `<icon>_dp` (`dummy_dp` when the object has no icon, the third
  argument of `AddObj`), for kind 4 the animation is named `<icon>`; cursor 4 (active)
  likewise with `_da`. Each gets the offset given with it.
- **Move** (every frame while the button is down, 0x409520, not while the inventory is
  shown): when the drag is active and the mouse is inside the hot spot of the drag (drag
  mode 1) or inside the limit rectangle (drag mode 2), the current position becomes the
  mouse position and the drag event gets phase 3. Outside, nothing happens.
- **Release** (`MouseLeftEvent`, before anything else): when the drag is active, the drag
  event gets phase 2, the drag is cleared (with `aCursorHandler::DeleteTypeDelete(3)`) and, in drag mode 2,
  the click ends there; in drag mode 1 the click goes on as usual.

The drag event (0x40c060) passes (object, `unk_19`, puzzle or rotation id, 1 for a puzzle,
the drag state, phase) to the zone's handler; with puzzle 1 it goes to SY's handler
(0x4331b0) whatever the zone (`spec/events.md`). A handler may switch the drag to mode 2
and set the limit rectangle (0x406660, 0x406680, as SY's sliders do), and read the
horizontal distance from the press position (0x4068c0, |current x − press x|) and its
direction (0x4067d0, current x < press x).
