# Animations (Ring, DVD)

`aAnimation` drives cursors (`spec/cursor.md`, "Animated cursors"), puzzle animations and
rotation layers (`spec/rotation.md`, "Layers"). Evidence: E-0039 (cursors), E-0054.
Addresses are `RING_DVD.EXE`.

## State (`aAnimation::Init` 0x416450)

`Init(frames, fps, start, flags, unk)`: id (+0, 0; `ObjPreSetAniIdeOnRot` /
`…OnPuz(object, presentation, index, id)` sets it, 0x42f220), frame count (+8), fps
(+0xc), start frame − 1 (+0x10, `SetStartFrame` 0x416bd0, `ObjPreAniSetStaFra`), mode
(+0x14) from the flags: 4 forward, else 8 backward, else 0x10 / 0x20 ping-pong (forward /
backward first); stop at the wrap (+0x2d) = flag bit 1 (2); restart on start (+0x20) = 1
(cleared for a rotation layer without flag 2); timing +0x21 = 1 (by ticks); current frame
(+0x22): the start frame for mode 4 and 0x10, the last frame for 8 and 0x20; active
(+0x26) 0; paused (+0x27) 0; "just started" (+0x4e) 1; frame time (+0x53) = trunc(1000 /
fps); last reported frame (+0x61) −5; the pause-at-frame and loop controls at +0x28..+0x4a
all 0 (set by calls not yet specified).

## Starting and stopping

Start (0x416670, time): active; when restart is set the current frame goes back to the
start frame (last frame for 8 / 0x20, direction reset for ping-pong); last step time =
time; last reported −5. Stop (0x416710): inactive, "just started" set.

`ObjPreSho(object, presentation)` (`aObject::ShowPresentation` 0x420990 → 0x42ecd0)
marks the presentation shown, starts all its animations (puzzle +0xd and rotation +0x25)
with the current tick count and shows its rotation layers (0x4103d0(layer, 1)).
`ObjPreHid` (0x4209f0 → 0x42ee80) marks it hidden, stops its animations and hides its
layers. `ObjPrePauAni` / `ObjPreUnPauAni(object, presentation)` (0x420db0 → 0x42f090 /
0x420e00 → 0x42f0f0) set / clear the paused flag of all the presentation's animations.

## Advancing (0x416870, time)

Returns the current frame + 1. Nothing happens for an inactive animation. Otherwise
(E-0058):

1. The first call after a start only clears "just started" and goes to step 4, paused or
   not: a started animation reports its frame once even when paused.
   Otherwise, for a paused one (0x416720: +0x27 set) the frame stays and no event is raised.
2. When `time − last step > frame time`: one step (never more), last step = time.
3. Mode 4: frame + 1; at the frame count it wraps to the start frame. Mode 8: frame − 1;
   below the start frame it wraps to the last. Ping-pong: forward to the last frame, then
   backward to the start frame, and so on. At each wrap (and ping-pong turn) the loop
   counter (+0x58) grows and, with stop at the wrap, the animation stops.
4. If still active and frame + 1 differs from the last reported frame, the animation event
   (0x40cff0) goes to the zone's handler with (id, the name at the owner's +4, frame + 1);
   the last reported frame becomes frame + 1.

## Puzzle animations (`ObjPreAddAniToPuz`, E-0090)

`ObjPreAddAniToPuz(object, presentation, puzzle, name, ext, x, y, drawType, priority,
frames, fps, flags)` (0x403460 → `aObject::addAnimationToPuz` 0x420650 →
`aObjectPresentation::addAnimationToPuzzle` 0x42e480 → `aAnimationImage::Init` 0x4219f0):

- the animation is `aAnimation::Init(frames, fps, start 1, flags, priority)`; without flag
  bit 1 (2) it is not restarted when started (+0x20 = 0), as for rotation layers;
- it holds one image handle per frame (0x42d320: name, x, y, active, draw type, priority,
  the zone being set up, kind app+0x5d, load-from app+0x58, extension index `ext`);
- the presentation keeps it in its puzzle-animation list (+0xd; `ObjPreSetAniIdeOnPuz`'s
  index counts in it), and the puzzle gets the presentation (`aPuzzle::AddPreAni`
  0x41cd90) and the first frame's handle among its pictures by priority
  (`aPuzzle::AddPreImg` 0x41cb70), so an animation is drawn in the pictures' order.

Frame files (0x422950): frame k (0-based) is `<name>.<k + 1 as %04d>.<ext>` in the
directory `ANI\<name>`: archive member `\ANI\<name>\<name>.0001.bmp` for load-from `'f'`,
`<prefix>DATA\<zone>\ANI\<name>\<name>.0001.bmp` from disk (prefix by kind as in
`spec/resources.md`). The extension is 0x40b7f0(`ext`): 0 `bmp`, 1 `tga`, 2 `cin`, 3 `cnm`,
5 `bma`, 6 `tgc` (the set-ups use 0 and 1).

Each frame of a puzzle (`aPuzzle::Update` 0x41c320, `spec/drawing.md`): first every
animation of the puzzle's presentations advances (0x416870, raising animation events),
unless puzzle +0x28 is set; then, in the pictures' order, an animation's handle is drawn
when the handle is active and its presentation shown, by 0x422940: the current frame at
(x, y) with the draw type, but only while the animation is active (+0x26); a paused one
still shows its frame (+0x2c is 1 from `Init`).
