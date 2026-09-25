# Mouse interaction: picking, hotspots, cursors, actions

What the engine needs for the mouse in a unit (U01 first): which object is under the
cursor, which hotspot that is, which cursor to draw, and what a click does. Input flow
(hover on mouse move and key release, click rate limit, mode gating) is in
`movement.md` "Mouse"; this file supersedes its hotspot detail (the marker is `*`, not
`$`). `s` is the scene scale (U01: 40).

## Picking (E-0070)

`pick(x, y)` returns the object whose surface is nearest the camera under the pixel, and
that surface's depth. `x`, `y` are window client pixels of the 640×480 frame, as floats,
no half-pixel offset. It uses the render projection of `scene.md` (E-0040) with the current
camera, recomputed at pick time, not the last frame's.

1. Walk every object: each top-level object, depth first through children and siblings.
   Skip an object when:
   - it is hidden (`X3d_Object_Hide`: collision meshes, hidden hotspots), or
   - its bounding box is entirely outside the view frustum (near 0.1, far 1,000,000), or
   - it is a welded object below its hierarchy top (its faces are tested with the top's
     mesh, E-0054; a hit on one of its faces reports the welded object itself, E-0076).

   Children are visited even when the parent is skipped. The LOD actually drawn
   (E-0052) supplies the faces; the reported object is the base object.
2. For each face of the object, in camera space (vertices after the model-view matrix):
   - Skip back faces: with n = (v0 − v1) × (v2 − v1), the face is kept only if
     n · v0 < −0.01 (Q-0040).
   - Skip faces with every vertex outside one frustum plane; clip the rest against the
     near and far planes.
   - Project each vertex: `sx = cx + fx · X / Z`, `sy = cy − fy · Y / Z`, with the viewport
     centre (cx, cy) = (320, 240) and half extents (fx, fy) = (320, 240) for the 640×480
     mode (X, Y already carry the FOV and 4:3 scale of E-0040).
   - The pixel hits the face when it lies inside the projected polygon's bounding box and
     on the inner side of every edge: for each edge (i → i+1),
     `(y − sy_i) · (sx_{i+1} − sx_i) + (x − sx_i) · (sy_i − sy_{i+1}) ≤ 0`.
   - Depth: intersect the view ray through the pixel,
     `r = ((x − cx) / fx, (cy − y) / fy, 1)`, with the face's plane:
     `d = (m · v0) / (m · r)`, m the unit normal from the first three vertices. `d` is the
     camera-space Z of the hit (world units; the view matrix does not scale Z).
3. Keep the face with the smallest `d`. Start from `d` = far (1,000,000) and no object.

The game ignores the pick when `d > 4 · s` (U01: 160 units): too far to interact.

Engine note: any aspect ratio works if the engine picks with the same projection it
renders with; only the cursor position must be mapped back to that frame. A GPU pick
(ID buffer) or a CPU ray/triangle test over the same front faces and hidden flags gives the
same object.

## Hotspots (E-0072)

A hotspot is one entry of the unit's `INFOOBJ.BIN` (`docs/formats/README.md`); nothing else
creates them. At scene load, for each entry: find the scene object whose name equals the
entry name (case-insensitive, depth first), create a hotspot bound to it, then apply the
entry's state: cursor, visibility (hide the object if `visible` = 0), and, if the object
has an `animation=` node (E-0056), that node's frame, paused flag, frame rate and loop
flag. U01 has 25 hotspots: `*U01_01` … `*U01_24`, `*Ernest`.

Hover: from the picked object, walk up the parents to the first name containing `*`; look
the text from the `*` on up in the hotspot list (case-insensitive equality, else the list
name contains it). No match: keep walking up from that object's parent. No hotspot: none.

Hotspot `type` (entry field) pairs a hotspot with its actions. 6 marks a character: a
voice step (op 1) on a type-6 target plays through the character's talk system. In U01,
4 is used by takeable things, 5 by fixtures (door, phone, drawers, switch, fuse box).

## Cursors (E-0074)

The game draws its own cursor into the frame. Images are
`RT_BITMAP` resources in `MissionMonet.exe` (20×20, 24-bit), white (FFFFFF) transparent:

| Kind | Resource | Hotspot (x, y) | Use |
|---:|---|---|---|
| 0 | `Cur_default.BMP` | 0, 0 | nothing under the cursor |
| 1 | `CUR_WAIT.BMP` | 9, 2 | |
| 2 | `CUR_CLIC.BMP` | 9, 2 | click |
| 3 | `CUR_VOICE.BMP` | 10, 10 | talk |
| 4 | `CUR_TAKE.BMP` | 10, 4 | take |
| 5 | `CUR_USE.BMP` | 10, 10 | use / use item on |
| 6..13 | `LOUPEB`, `LOUPED`, `LOUPEDB`, `LOUPEDH`, `LOUPEG`, `LOUPEGB`, `LOUPEGH`, `LOUPEH` | 10, 10 | magnifier views (not U01) |

(`CUR_DROP.BMP` is in the resources but not loaded.) The image is drawn with its top-left
at cursor − hotspot. The engine reads these with `Common::PEResources` from the EXE on the
CD (`INSTALL/02_PR/MissionMonet.exe`).

Each hotspot carries a cursor kind (initially the INFOOBJ `cursor` field; actions and unit
code change it). Cursor modes:

- **Normal:** hover sets kind = the hotspot's cursor kind, or 0 with no hotspot.
- **Holding an item** (after a take step): the cursor is the item's 32×32 image, drawn
  centred (offset 16, 16), named `<object name without *>C`, e.g. `U01_04C`
  (`Data/2dbit/U01_04C.BMP` exists for every U01 item; the loader path is Q-0041). Over a
  hotspot whose kind is 5 it blinks: item, nothing, item, … at 6 frames per second;
  elsewhere it is steady.

## Click → action (E-0073)

A click (after the rate limit) hovers at the click point; if there is a hotspot and the
unit's "actions enabled" flag is set (U01: cleared by `U01_Start`, set at the hand-over),
it triggers that hotspot:

1. Trigger kind: 7 (use item) when holding an item, else 8 (click).
2. Candidates: the unit's actions (`INFOACT.BIN`, E-0071) whose `hotspot_type` equals the
   hotspot's type and whose `hotspot` names it, in file order.
3. Run the first candidate whose `trigger` is the kind, whose condition holds, which is not
   exhausted, and (kind 7) whose `item` is the held item's name.

**Condition** (lower-cased, left to right): `true` → true, `false` → false; `mNN` or `NN` →
action NN is exhausted; `!mNN` → it is not; `&` and `|` combine, `( )` group. Action ids
are the records' `id`s.

**Run:** execute the steps in order, then count the run; when `max_runs` < 100 and the
count reaches it, the action is exhausted (never runs again, satisfies conditions naming
it). `max_runs` ≥ 100: unlimited.

**Steps** (`op`, `arg`; "hotspot" = the action's hotspot, "target" = its target):

| op | Effect |
|---:|---|
| 1 | Voice `arg`: if the target is a character (type 6), it says `Sound/<arg>.wav` (lip data `Sound/<arg>.bin` if present); else play it at the hotspot's position. |
| 2 | Take the target: its cursor kind = 0, hide it, cursor holds item `<target>C`. `arg` unused. |
| 3 | Use up the held item: cursor back to normal kind 0, target's cursor kind = 0. |
| 4 | Start (unpause) the animation node named `arg`. |
| 6 | Wait `arg` ms (blocking, as `RunFor`). Not in the corpus. |
| 7 | Set the target's cursor kind to `arg`. |
| 9 | Show the target if `arg` ≠ 0, else hide it. |
| 10 | Queue the action for the unit's code under name `arg` (below). |
| 12 | Play `Sound/<arg>.WAV` (non-positional). Not in the corpus. |
| 13 | Play `Sound/<arg>.WAV` at the hotspot's position (`arg` ending `.wav` is used as is). |
| 14 | Run the action named `arg` now, if runnable. |
| 15 / 16 | Set the condition of the action named `arg` to `TRUE` / `FALSE`. |
| 101 | Play `Sound/<arg>.WAV` on the second sound channel, stopping what plays there. |

`Sound/` is `Data/Uxx/Sound/`.

**Unit code (E-0075).** After triggering, the unit drains its queue (up to 10 actions); for each
queued action it checks the op-10 names in its steps against a fixed list and runs the
matching script. U01 (`U01_DispatchClickActions`, `0x00401d30`):

| Name | From (INFOACT) | Does |
|---|---|---|
| `TakeCard` | M02, click the mayor's card `*U01_04` | card animation back to frame 1 and wait; enable walking and looking (E-0050); a hotspot's cursor → talk |
| `ClickMaire` | M03, click the mayor `*U01_02` after M02 | mayor says a line (`U01_02` talk) |
| `OpenDoor` | M08, use item `U01_05` on the door `*U01_07` | door animation to frame 12 at 2.5 fps, `OpenDoor` sound |
| `CloseDoor` | none in U01 data | `CloseDoor.wav`, door animation back to 0 at 4 fps |
| `TakeCarteHorloge` | M18, take `*U01_19` | phone `*U01_11`'s cursor → click |
| `OpenBoitier` | M15 (use `U01_12` on `*U01_13`), M22 | toggle fuse box `*U01_13` between frames 0 and 10 |
| `BaisserManette` | M16, click lever `*U01_14` after M15 | lever animation to frame 10 |
| `ClicTel` | M10, phone `*U01_11` after M18 | phone rings/answers (`TelGrisi`, `telgrisi2.wav`); may disable other actions and change `*U01_01`'s cursor |
| `OpenTiroir1` / `OpenTiroir2` | M12 / M13, drawers `*U01_15` / `*U01_16` | toggle the drawer animation between 0 and 10, sound `s1_05` |
| `MonterSurToit` | M20, use `U01_08` on `*U01_09` (and M20's repeat) | unhide `*U01_10`, scripted camera climb onto the roof |
| `DoInterrupteur` | M21, switch `*U01_21` | switch animation, `s1_13`, camera looks at the lamp and back |

Also, after the queue: hovering `*U01_09` with the camera below z = 100 while the queue's
`+0x460` flag is set runs `MonterSurToit` (flag meaning open, Q-0042). `Light255` (M09)
has no U01 handler. Each script's details belong in a later spec.
