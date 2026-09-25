# Main loop, movement, collision, picking

What the engine needs for first-person play in a unit (U01 first): the frame loop and its
clock, the keyboard camera, collision against the scene, the hand-over after U01's
scripted entry, and mouse hover/click. `s` is the scene scale from `#SCENE#` (U01: 40,
E-0039). Angles: yaw `a`, pitch `e` as in `scene.md` (e = π/2 is level, larger e looks up).

## Frame loop and clock (E-0046)

One iteration of the main loop, while the app is in mode 0 (running scene):

1. Pump window messages (key table, mouse, see below).
2. Animation/sound tick (scene vtable `+0x24`).
3. Unit frame (`+0x1c`): **render and present**, measure the frame time, then the unit's
   own per-frame logic (U01: timed ambient voices, trigger zones).
4. Unless input is suspended (app `+0x480`): **camera input** (`+0x40`), which moves the
   camera for the next frame.

There is exactly one logic step per rendered frame and no frame cap in the EXE (a cap, if
any, is the driver's page flip: Q-0022). The clock is `QueryPerformanceCounter`, read right
after the render: `fps = frequency / (counter − previous counter)`, i.e. the reciprocal of
the time between the last two presents. The X3D DLLs have no clock.

Movement uses `fps` (so it is per second); turning and pitching do not (per frame).

Blocking sequences (scripts, jumps, falls, camera moves) run their own loop of
steps 1–3 without step 4: `RunFor(ms)` repeats animation tick + render + message pump
until `timeGetTime` has advanced `ms` (0 = one frame).

### Engine model

Run logic in fixed ticks, render as often as possible, interpolate the camera between the
last two ticks. Movement: per tick move `speed · s · dt`. Turning: the original's 0.06 rad
per rendered frame has no per-second value until Q-0022 is answered; the engine uses
0.06 rad per tick with a tick rate constant (provisional, a deviation until then).

## Camera state (E-0047)

Defaults (constructor), then `SCENE.BIN` `#CAMERA#`, then scene load (E-0039):

| Field | Value |
|---|---|
| walk speed `v` | 2.0 (the `#CAMERA#` value is overwritten) |
| turn step | 0.06 rad per frame (1.0 × 0.06) |
| eye height `h` | 1.5 · s (U01: 60) |
| sphere radius `r` | 0.5 · s (U01: 20) |
| sphere Z offset `o` | h − 2r (U01 then sets 37.0 in `U01_Start`) |
| can move / can turn | 1 / 1 |
| run allowed / jump allowed | 0 / 0 (U01 never enables them) |
| collision | on |
| landing sound | on |

The collision sphere's centre is the eye position minus (0, 0, o).

## Keys (E-0047)

WM_KEYDOWN sets `held[vk]`, WM_KEYUP clears it; every frame reads `held`. Within one frame
the order is: Up, Down, Right, Left, PgUp, PgDn, so Down wins over Up.

| Key | Needs | Effect per frame |
|---|---|---|
| Up | can move | speed `v` := 2.0; walk forward; head bob |
| Down | can move | if `v` = 2.0 then `v` := 1.0; walk backward; head bob |
| Right / Left | can turn | a += / −= 0.06 |
| PgUp | can turn, Ctrl up, e < 2.7 | e += 0.06 (look up) |
| PgDn | can turn, Ctrl up, e > 0.6 | e −= 0.06 (look down) |
| Ctrl (held) | run allowed | mode "run" (×2) |
| Shift (press) | jump allowed, can move | jump (below) |
| Numpad 0 (press) | — | crouch (below) |
| Enter, Escape, Space | — | `boot.md` "Skipping" (E-0043) |

`v` stays at 1.0 after Down until the next Up. Pitch limits are checked before the step, so
e can end up to 0.06 past them. Mouse look does not exist; the mouse only picks.

### Walking

    d = (cos a · sin e, −sin a · sin e, −cos e)        (view direction, unit length)
    step = v · s / max(fps, 8)                           (U01: 80 units/s forward, 40 back)
    if the nearest face ahead is closer than 2r: step /= 2
    mode factor: run ×2, jump from run ×0.5, other jump ×0.25, crouch ×0.25
    velocity = ±(d.x · step, d.y · step, 0)

Only x and y of `d` are used, not renormalised: looking up or down slows walking by sin e.
"Face ahead": a segment from the sphere centre to centre + (10000·d.x, 10000·d.y, d.z),
nearest hit over collidable objects (object `+0x40` must also be 0: Q-0025).

### Head bob

While walking, roll += 1.0 / fps degrees, reversing direction at ±0.4°. The direction
persists across frames and scenes.

## Collision (E-0048)

Collidable objects: every object in the scene, visible or hidden (the `static\col*`
meshes and the visible geometry alike), depth-first through the hierarchy, except those
whose "no collision" flag (object `+0x118`) the unit code sets. U01 sets it on `Box203`
(and hides it). Faces are one-sided: collision uses the X3D face plane normal `n` (Q-0023).

After the key handling, if the velocity is non-zero and collision is on:

1. **Slide.** c = eye − (0, 0, o) + velocity. Resolve the sphere (c, r) against the scene,
   then eye' = c + (0, 0, o).
2. **Ground.** Cast a segment from eye' straight down 10000. Take the highest hit g.
   - no hit: keep eye'.
   - eye'.z − g ≤ 1.3 · h: eye'.z = g + h (steps and slopes up to 0.3 · h below the
     ground-level eye height, and any rise, snap instantly).
   - otherwise **fall** (blocking): z = eye'.z − 5.9 · s · t² (t in seconds of wall time,
     one frame per step) until it has dropped D = eye'.z − (g + h); then eye'.z = g + h.
     If D > 1.5 · s and the landing sound is on, play `<data root>/SAUT.WAV` at the eye.
     Then slide once more with the same velocity.
3. Set the camera to eye'. The velocity is cleared every frame.

**Sphere resolution.** Visit objects in order; skip an object whose world bounding sphere
does not overlap the collision sphere. For each face in order:

- signed distance d = (c − v₀) · n; only 0 < d < r counts (centre in front, penetrating).
- If c projects inside the polygon: contact q = c − d·n, push normal m = n.
- Otherwise q = the nearest point on the polygon's boundary (edge or vertex); it counts
  only if |c − q| < r; m = normalize(c − q).
- If |m.z| ≥ cos 45°: **stop** the whole resolution and keep c as it is now (floors and
  ceilings never push; the ground step handles them).
- Else c = q + m · r and continue with the next face, using the moved c.

**Segment casts** (ground, headroom, face ahead): a face is hit when the segment crosses its
plane from the front side (start on or in front of it) and the crossing point lies inside
the polygon. So the downward ray hits upward-facing faces, the upward ray downward-facing
ones.

## Jump and crouch (E-0049)

Not reachable in U01 (jump needs "jump allowed"); crouch is. Both block the main loop.

- **Jump** (Shift): mode ×0.5 if running, else ×0.25; Up/Down are sampled once at the
  start. Each frame: t += elapsed seconds; z = z₀ + s·t − s·t²/2 (peak s/2 at t = 1, lands
  at t = 2); stop if the ground under the eye rises above the feet (eye − ground < h) or
  headroom fails; walk-slide horizontally; render one frame.
- **Crouch** (Numpad 0): eye height h_c = 0.5 · s + 3, sphere offset h_c − r − 1; lower
  the camera by h − h_c over 1000 ms. Then each frame: arrows walk (×0.25) and turn;
  when Numpad 0 is up and there is headroom, raise the camera over 2000 ms and restore
  h and o.
- **Headroom:** the lowest downward-facing hit above the eye is at least 0.4 · s away.

## Scripted camera moves (E-0050)

`MoveTo(ms, position, yaw, pitch, fov)`: N = ⌊ms · fps / 1000⌋ frames (at least 1), with
`fps` the last measured value. Each frame adds 1/N of the difference to position, yaw,
pitch and FOV, then animation tick + render; finally snap to the target. Yaw and pitch are
reduced to [0, 2π) and take the short way round. 100.0 means "keep current" for yaw, pitch
and FOV; no position means keep it. `LookAt(ms, object)` is `MoveTo` with the yaw/pitch
toward the object's global position (for ms = 0: set at once, one frame).

## U01 hand-over (E-0050)

After the prologue, from E-0041's first shot (Escape is disabled throughout):

1. Run 1500 ms. Look at a character's `TETE` (head) object over 1000 ms.
2. Move to (−405.67, −494.31, 29.5), yaw 2.9, over 2500 ms; then to
   (−468.40, −481.30, 29.5), yaw 1.76, over 800 ms.
3. Wait while the voice plays (Enter skips), then 1000 ms. Start animation `_U01_03`;
   look at a second character's `TETE` over 1000 ms; run 400 ms.
4. Move to (−466.36, −452.495, 30.48), yaw 4.7, over 1400 ms; then pitch 1.4908 and FOV 45
   over 1800 ms. Wait for the camera animation to end (Enter skips).
5. Over 600 ms: pitch π/2, FOV back to 90. Start the `GiveCard` animation.
6. **Can move = 0, can turn = 0**, Escape allowed again. The player can only click.

Movement starts when the player performs the `TakeCard` action on the card: its handler
(`0x00401d30`) plays the take animation, waits for it, then sets can move and can turn to 1.
So the free-roam state is: position (−466.36, −452.495, 30.48), yaw 4.7, pitch π/2, FOV 90.
The first step's ground snap sets z to ground + 60.

## Mouse (E-0051)

- **Hover** (WM_MOUSEMOVE, and at every key release using the current cursor): ask X3D for
  the object under the cursor (`X3d_Scene_Pick_Object(x, y)` → object, distance). Nothing if
  the distance exceeds 4 · s (U01: 160). From the picked object walk up the parents to the
  first name containing `$`; the text after `$` names the hotspot. Set the cursor to match.
- **Click** (WM_LBUTTONDOWN): ignored if less than 1000/fps + 10 ms after the previous one,
  otherwise hover at the click point and queue the hotspot's action; the unit's click
  handler then dispatches queued actions by name (U01: `ClickControleur` … `MonterDansTrain`,
  and `TakeCard`).
- Picking internals, hotspot table and actions: Q-0024.
- Both are ignored while input is suspended or the app is not in mode 0.

## Debug mode (E-0049)

Typing `XHELP` (key releases) turns on the debug flag: an FPS overlay; Insert toggles
collision; Ctrl + Numpad +/−, P, M, O, A, Q, Z, S change camera parameters (Z/S: sphere
radius ±1). Not needed for play.
