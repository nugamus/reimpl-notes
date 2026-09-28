# The 3D main loop, movement and collision

How the viewer moves in a 3D scene: the tick, the keyboard, speeds and turning, collision
against the scene's `.3DI` faces and the floor rule. Scene loading and start positions are
in `scene.md`; the mouse, picking and clicks in `interaction.md`. Units as in `scene.md`
(y down, angles in 1/4096 turn).

## The tick (E-0300)

- The 3D runs on a **multimedia timer of 66 ms** (`Timer3D_Begin` 0x42fb5e:
  `timeBeginPeriod(66)`, `timeSetEvent(66, 5, 0x42f955, 0, periodic)`), about 15.15 ticks
  per second. The callback (0x42f955) increments the tick counter (0x598ca4) and posts
  message 0x505 to the game window unless the previous tick is still being handled (busy
  flag 0x502a84). A tick that arrives while busy is dropped: slow frames lose ticks.
- The 3D window procedure (0x42f988, modes 0 and 4 of 0x42fbd6, `boot.md`) handles 0x505:
  1. set busy; read the keyboard into the other of two 256-byte buffers (E-0301);
  2. `elapsed` = ticks since the last handled tick, clamped to 1..10 (0x598ec0); animations
     and scene timers advance by `elapsed` (E-0318), **movement does not**: it is per
     handled tick;
  3. mode 0: if a reload was requested (0x4e313c), unload and load (`scene.md`); if the
     mode changed since the last tick (0x502740 ≠ 0x598cb0), load; if the 3D is running
     (0x4e4580), run **one frame** (0x4223e8, below);
     mode 4 (flight to a painting, `scene.md`): one flight step (0x41f9f8), and at the end
     the entry movie or the load (0x41faf9);
  4. clear busy.
- WM_DESTROY (0x42ed9c) stops the timer and frees everything; SC_SCREENSAVE is swallowed.

### One frame (0x4223e8)

1. Keyboard movement (0x422b98, below), then collision and floor (0x4216b6), then the mouse
   (0x420e07, `interaction.md`).
2. Fill the border around a small viewport (`scene.md`), draw the scene (0x4378f0, renderer
   spec) into the 640×480 16-bit frame (0x5baf80).
3. Overlays: the inventory bar and its items, the return icon (0x426171,
   `interaction.md`); the cursor (0x424190).
4. Copy the frame to the DirectDraw back buffer line by line and flip (skipped while the
   window is minimised).
5. Keys: Backspace released → leave to the museum (`scene.md`); Space released → open or
   close the inventory bar; Escape released → option menu (`scene.md`).
6. The scene's frame callback (`scene.md`).

Three debug features exist in the frame but are dead in the shipped program: their flags
are in zero-initialised `.bss` and have no writer anywhere in `.text` (one reference each):
the text overlay `DebugInfo` 0x421fca (0x4e3108: "Pos =>", "Angle =>", "pick name =>",
timer, memory, "NbTournesols"), the collision faces drawn as lines (0x432c30, 0x4e310c)
and a screenshot per frame to `D:/VANGOGH/TGA/%04d.TGA` (0x4e3104).

The "redraw only" frame (0x4221f6), used by the flight, before leaving the 3D and after
some script events, does steps 1–4 without keyboard movement: camera set from the stored
angles/position, collision, mouse, draw, the bar, and the **hourglass** cursor (`sablier`)
centred on the screen instead of the mouse cursor; it sets 0x4b0058 when the mode is 1
(the switch to 2D, `scene.md`).

## Keyboard (E-0301)

DirectInput keyboard state (0x472b80, `GetDeviceState` of 256 bytes) is read every tick
into one of two buffers (0x5b7fc0 and 0x5b80c0, alternating with 0x5bae2c). Scan codes
(DIK):

- **held** (0x41ece8): bit 7 of the key's byte in the current buffer;
- **released** (0x41ec7b): up in the current buffer and down in the previous one.

Movement uses held keys; Backspace (0x0E), Space (0x39) and Escape (0x01) act on release.
The buffers are cleared when a scene loads and on returning from 2D or the option menu.

## Walking and turning (E-0302)

The viewer state (s16): position (x, y, z) at 0x651352/54/56, angles (pitch, yaw, roll) at
0x651346/48/4a, and four velocities: forward speed `v` (0x651342), vertical speed `vy`
(0x651344), yaw rate `w` (0x65134e) and the accumulated pitch offset `p` (0x651340).
Each tick (0x422b98), in this order:

1. **Damping**: `v`: if `v > 10` or `v < -10` then `v -= v / 2` (C division, toward zero),
   else `v = 0`. `w`: the same. `vy`: if `vy ≠ 0` then `vy -= vy / 2`, else 0.
2. **Gravity**: if `vy < 6` then `vy += 5`.
3. **Keys** (held):

| Key | DIK | Effect | Limit |
|---|---|---|---|
| Up | 0xC8 | `v += 60` | while `v < 2500` |
| Down | 0xD0 | `v -= 60` | while `v > -2500` |
| Left | 0xCB | `w -= 40` | while `w > -300` |
| Right | 0xCD | `w += 40` | while `w < 300` |
| Page Up | 0xC9 | `p += 30`, pitch += 30 | while `p < 500` |
| Page Down | 0xD1 | `p -= 30`, pitch -= 30 | while `p > -500` |

4. `pitch &= 0xFFF`; `yaw = (yaw + w) & 0xFFF`; `roll &= 0xFFF`.
5. Build the rotation matrix M from (pitch, yaw, roll) (0x43a780, below) and move:
   `x += (M[2] · v) >> 15`, `z += (M[8] · v) >> 15` (the division rounds toward zero),
   `y += vy`.
6. Set the camera (0x422f30) from the new position and angles.

Consequences (from the rules, not measured): holding Up gives `v` = 60, 90, 105, 113, 117,
119, 120, 120 … so the walking speed settles at **120 units per tick** (about 1,800 per
second) and stops within four ticks of release; the limits of 2,500 are never reached.
Holding a turn key settles `w` at 80 per tick (7° per tick, about 106° per second).
There is no strafing and no running. Pitch moves by 30 per tick while held; `p` bounds the
pitch to ±500 (±44°) around wherever it was when the scene started (the start pitch
counts as 0), and `p` itself is never reset except by a scene load (the viewer block is
cleared there, 0x422869).

**Rotation matrix** (0x43a780; `S`, `C` = sine and cosine tables at 0x6ab5a0 and 0x6a7580,
built at start by 0x43a660: `C[i] = trunc(32768 · cos(2πi / 4096))`, `S[i]` the same with
sin, i = 0..4095; row-major M[0..8]; a = pitch, b = yaw, c = roll):

```
M[0] = S(c)S(a)S(b) + C(c)C(b)     M[1] = C(c)S(a)S(b) - C(b)S(c)     M[2] = S(b)C(a)
M[3] = S(c)C(a)                    M[4] = C(c)C(a)                    M[5] = -S(a)
M[6] = C(b)S(c)S(a) - C(c)S(b)     M[7] = C(c)C(b)S(a) + S(b)S(c)     M[8] = C(b)C(a)
```

(each product shifted right by 15 as it is formed.) At all angles 0 it is the identity
(0x8000 on the diagonal). The walking direction is (M[2], M[8]) = (sin yaw · cos pitch,
cos yaw · cos pitch) in (x, z): yaw 0 walks toward +z, growing yaw turns toward +x, and
looking up or down shortens the step by cos pitch. M[5] = -sin pitch is the view
direction's y, so a positive pitch looks up (y is down).

## Collision (E-0304)

The viewer is a **sphere of radius 250** (the collision body 0x650f9c, radius set at scene
load, `scene.md`) against the triangles of the registered box sets (`BOX.3DI` plus the
scene's current extra set). A `.3DI` face (0x60 bytes, E-0016) holds pointers to its three
vertices (+0, +4, +8) and to its unit normal `n` (Q15, +0xC), the plane constant `D`
(+0x10, `n·p / 32768 = D` on the plane), three edge planes (normals +0x14/+0x20/+0x2C,
constants +0x38/+0x3C/+0x40), the owning box set (+0x44) and an axis-aligned bounding box
(min +0x48, max +0x54).

Broad phase (0x430980–0x4310b0): the collision world keeps, per axis, the sorted list of
all face box ends; moving the body updates two candidate lists: faces whose box overlaps the
body's box on all three axes (**contacts**, body flag 4) and on x and z (**floors**, flag 8).
The viewer body has flags 0xF (both sides, both lists).

Narrow phase, sphere against a face (0x432220), with `d = n·c / 32768 - D` for the centre c
(integer: each of the three products divided by 32768 rounding toward zero, then summed;
the edge distances likewise, 0x431700). `d = 0` counts as in front:

- no contact unless `-250 < d < 250`, or if any edge-plane distance is below -250;
- the closest point: the projection of c on the plane when c is inside all three edges,
  else the closest point of the nearest edge segment (one edge outside) or vertex (two
  outside);
- contact if the distance from c to that point is below 250. The result is 2 for the face
  interior, 1 for an edge or vertex, **negated when c is behind the plane** (`d < 0`).

Per frame (0x4216b6), after the keyboard moved the camera:

1. Put the body at the camera. For every contact candidate: a face contact (2) adds the
   closest point to `F` and the face normal to `N`, counting `nf`; an edge contact (1),
   while no face contact has been found yet, adds the point to `E`, counting `ne`. Negative
   results (behind the face) are ignored.
2. If `nf > 0`: `N' = trunc(N / nf)`, `F' = F / nf`; the camera moves to
   `trunc(trunc(N' · 250 / 32768) + F')`: 250 units out from the average face point along
   the average normal.
   Else if `ne > 0`: `E' = E / ne`, `d = trunc(c - E')`, the camera moves to
   `trunc(trunc(d · 250 / |d|) + E')` (|d| = square root of the integer `d·d`): 250 units from the average edge point, away from it.
3. There is a single pass per frame; resolving one wall can push into another, which the
   next frame resolves.

**The closest point by edge mask** (0x432220): bit k set when edge distance k is below 0.
Mask 0: the projection of c on the plane (float, truncated). One bit: the closest point of
that edge, edge 0 from vertex 0 to 1, edge 1 from 1 to 2, edge 2 from 2 to 0. Two bits: the
vertex the two edges share (bits 0+1: vertex 1, 0+2: vertex 0, 1+2: vertex 2). All three:
the switch has no case and the previous face's point is reused (never seen in practice).

**Consequence: inside corners leak** (E-0367). Averaging two face contacts in an inside
corner leaves the viewer at `250 - step` from each wall instead of 250; walking diagonally
into the corner and then along it ends a tick behind a one-sided wall, which from behind is
ignored. `engines/peintre/tools/boxreach.py` (these rules, flood-filled over one tick's
walk) finds such paths in the museum with every box set: e.g. set 1 (zone 0 unsolved)
through the closed left doorway (the wall at x = -1693 meets the hall wall at z ≈ 3710) into
the act 1 gallery, and from the galleries' back walls out of the building. The engine
undoes a tick whose move crosses a wall face (|n.y| ≤ 16384) from its front through the
triangle (a bug fix, not in the original).

The per-frame counts are kept in 0x5bada8 (edges) / 0x5badac (faces); the last face's
box-set word (+0x44 → +0x18) in 0x5bada0; nothing in the 3D reads them back.

## Floor (E-0305)

After the push-out (0x4216b6, second half): put the body at the camera again; for every
floor candidate (0x431f90): if the camera's (x, z) lies inside the triangle's (x, z)
projection and the face is not vertical (`n.y ≠ 0`), the plane's height `yf` under the
camera is computed; it counts when the camera is on the face's front side. Take the
smallest `yf` that is **greater than the camera's y** (the nearest floor below). If there is
one, the camera's y becomes `yf - 250 - 450`: **the eye is always 700 units above the
nearest floor below**, which also carries the viewer up and down stairs and slopes in one
tick. The floor point is kept in 0x650f90. Without a floor below, `vy` (gravity) moves the
camera down by up to 10 per tick.

The data agree: in the museum the default start is y = -209 and `BOX.3DI` (and `BOX1.3DI`)
has one floor face under it, normal (0, -32767, 0), `D` = -491, i.e. y = 491 = -209 + 700;
the start camera is on its front side at distance 699.

Finally the new position is copied back to the viewer state (0x651352..).

Two more floor routines (0x4211a6: radius 250, floor offset 0x15E + 0x1C2; 0x4212f7: radius
200 then 0x15E) have no callers.
