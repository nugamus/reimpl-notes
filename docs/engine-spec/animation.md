# Animation and welded characters

What the engine needs to pose and animate U01's objects: `.A3D` keyframes, how
`animation=` binds them, the per-frame clock, and how welded characters (the mayor
`U01_01`, `U01_02`, Ernest `U01_E`) turn one shared vertex array into a skinned mesh.
Transforms, W and the row-vector convention are those of `scene.md` (E-0042). Formats:
`docs/formats/a3d.ksy`, `o3d.ksy`.

## Object transform state (E-0042, E-0055)

Each object keeps a *live* pivot, position, scale and 3×3 rotation M, initialised from
the `.O3D` fields at load. W is always built from the live values (the formula in
`scene.md`). An animation writes position, scale and M; it never changes the pivot in
Monet (the EXE always passes "use the object's own pivot"). Every `.O3D` M has a zero
translation row, so M is a pure rotation (with any baked scale).

## `.A3D` content (E-0055)

A file is a hierarchy of animations (name, optional parent, children in file order) with
a header shared by all of them: `num_frames`, `first_frame`, `last_frame`. Each
animation has five tracks; a track is `count` keys, each with an integer frame number,
five key parameters (tension T, continuity C, bias B, ease-in, ease-out) and a value:

| Track | Value | Written to | Sampling |
|---|---|---|---|
| translation | vec3 | live position | TCB Hermite (Monet always uses the spline variant) |
| scale | vec3 | live scale | linear |
| rotation | quaternion (w, x, y, z), absolute | live M | slerp |
| hide | u32 | object `+0x5c` | step (key i) |
| morph | per key: the object's own vertex positions and normals, bounds | the object's vertex range | linear |

A track with no keys leaves its field untouched. Frames are floats during playback; key
frame numbers are integers. The corpus has no hide or morph keys and no non-zero track
flags; the only non-zero key parameter is C (19,046 of 555,288 keys). Note the header
range is 1-based while keys start at 0 (`U01_02/ATTENTE`: frames 1..100, keys 0..90):
use the numbers as stored; frames past the last key hold the last key.

### Key lookup

For frame f and key frames f₀ < … < f₍ₙ₋₁₎:
- f < f₀: i = j = 0 (the spline variant takes i = 0, j = 1 and may extrapolate; playback
  never goes below f₀ = 0 in the corpus).
- f ≥ f₍ₙ₋₁₎: i = j = n − 1 (track flags & 3 would wrap instead; never set).
- otherwise i = the largest index with fᵢ < f, j = i + 1.

Parameter s = (f − fᵢ) / (fⱼ − fᵢ), or 0 when fᵢ = fⱼ.

### Linear and slerp

Scale: vᵢ + s (vⱼ − vᵢ). Rotation: q = slerp(qᵢ, qⱼ, s) with d = qᵢ · qⱼ (4D dot, **no
sign flip for d < 0**):
- 1 + d ≤ 1e-5 (opposite): r = (qᵢ.z, −qᵢ.y, qᵢ.x, −qᵢ.w) in (w, x, y, z) order;
  q = sin((1−s)·π/2) qᵢ + sin(s·π/2) r.
- 1 − d ≤ 1e-5: q = (1−s) qᵢ + s qⱼ (not renormalised).
- else θ = acos d: q = (sin((1−s)θ) qᵢ + sin(sθ) qⱼ) / sin θ.

Quaternion to M (row-major, used as v · M), with k = 2 / (w² + x² + y² + z²):

    row 0: 1 − k(y² + z²)   k(xy − wz)       k(xz + wy)
    row 1: k(xy + wz)       1 − k(x² + z²)   k(yz − wx)
    row 2: k(xz − wy)       k(yz + wx)       1 − k(x² + y²)

Key 0 of `U01_01/ATTENTE` reproduces the `.O3D` matrices exactly with this rule.

### Translation spline

Tangents of key i, with p = max(i−1, 0), n = min(i+1, count−1), positions P:
- if fₚ = fₙ both are 0; otherwise
- h = (fₙ − fₚ)/2, a = (fᵢ − fₚ)/h, b = (fₙ − fᵢ)/h, c = |C|,
  a′ = a + c − c·a, b′ = b + c − c·b, t = (1 − T)/2, d₀ = Pᵢ − Pₚ, d₁ = Pₙ − Pᵢ
- Inᵢ = a′ · t · ((1−C)(1+B) d₀ + (1+C)(1−B) d₁)
- Outᵢ = b′ · t · ((1+C)(1+B) d₀ + (1−C)(1−B) d₁)

Ease: eₒ = key i's ease-out (float 4), eᵢ = key j's ease-in (float 3). If eₒ + eᵢ ≠ 0:
if the sum exceeds 1 divide both by it; g = 1 / (2 − eₒ − eᵢ); then s := g/eₒ · s² for
s < eₒ, (2s − eₒ) · g for s < 1 − eᵢ, else 1 − g/eᵢ · (1 − s)².

Position = (2s³ − 3s² + 1) Pᵢ + (s³ − 2s² + s) Outᵢ + (−2s³ + 3s²) Pⱼ + (s³ − s²) Inⱼ.

### Applying to a hierarchy

`Animate(object, animation, f)` samples the pair, then recurses: the object's first child
with the animation's first child, each next sibling with the next sibling, **by
position, not by name** (in U01 every pair also matches by name). Afterwards every
affected W is rebuilt before drawing.

## Binding `animation=` (E-0056)

`animation="file.a3d[,fps]"` (fps default 30) after `object=` loads the file; its first
animation is the root R, O is the `object=` result (the `.O3D` file's first object).
- R's name contains `*` (the characters: `*U01_01`, `*U01_02`, `*Ernest`): one playback
  node for (R, O).
- otherwise (props rooted at `$$$DUMMY.Dummy01`): one node per direct child C of R,
  bound to the object named like C (case-insensitive exact) found depth-first among O's
  children and their siblings; children with no such object get no node. R itself is not
  played.

A node: animation, object, fps, frame = `first_frame`, loop on, running, direction
forward, no ping-pong, no stop target, named after its object.

## Per-frame playback (E-0056, E-0046)

Once per main-loop iteration, and once per step of every blocking `RunFor`/`MoveTo`
loop, before rendering, for every node (the order does not matter: nodes drive
disjoint objects):
1. If the node has an active sub-slot (below), process that slot's node instead.
2. If running, advance: dt = seconds between the last two presents (the same
   QueryPerformanceCounter pair as `fps` in `movement.md`).
   - ping-pong: at or past `last_frame` go backward from `last_frame`, at or before
     `first_frame` go forward from `first_frame`;
   - frame ±= dt · fps (− when backward);
   - not looping: clamp to [first, last]; on reaching the end (forward: ≥ last,
     backward: ≤ first) stop running unless ping-pong;
   - looping: if frame > last, frame = fmod(frame, last) + first; if frame < first,
     frame = last − (first − frame);
   - stop target set and |frame − target| ≤ 2 · dt · fps: frame = target, stop running,
     clear the target.
3. Animate(object, animation, frame) — also when not running, so a stopped node holds
   its pose.

So playback is wall-clock: fps frames per second whatever the render rate.

### Sub-slots (scripted clips, E-0057)

A node can hold clips in slots 1..15 (slot 0 is the node itself). Adding a clip loads a
whole `.A3D` (root to root, no `*` splitting) onto the node's object, copying the node's
fps, loop and running flags, starts it, and optionally makes it the active slot. While a
slot ≠ 0 is active only that clip advances and poses the object; the base node's frame
is frozen.

### U01's scripted calls (E-0050, E-0057)

- `_U01_03`: set the node `*U01_03` (object `*U01_03`, crank prop `U01_03.A3D`, frames
  1..30, looping, 30 fps) running.
- `GiveCard`: on the `U01_02` node, add `Anim/U01_02/Action03.A3D` in slot 1, active, then
  loop off: it plays frames 1..25 once and holds the last pose.
- `TakeCard`: slot 1 backward with stop target 1.0, run frames until it stops; then make
  slot 0 active and running with its frame set to 1.0 (clamped); then movement is
  enabled.
- The mayor's `U01_01/ATTENTE.A3D` spans frames 1..10 with keys at 0 and 1 only: it
  loops but always shows key 1's pose.

## Transitions (E-0500, E-0501)

`Transition(object, A at fa, B at fb, t, usePivot, recurse)` poses an object between two
clips. Only U03 calls it (`U03::AnimateTransition`), always with usePivot = recurse = 1.
Per object, and per track only when **both** clips have keys on it:
- Key lookup as above (never the spline): sA, sB from each clip's bracketing keys.
- Translation, scale: vA = lerp(A keys, sA), vB = lerp(B keys, sB); value = vA + t (vB − vA).
- Rotation: q = slerp(slerp(A qᵢ, A qⱼ, sA), slerp(B qᵢ, B qⱼ, sB), t), the slerp above
  (no sign flip), converted to M.
- Morph: every morph value (positions, normals, bounds) as translation.
- Hide: only while t < 0.5: apply A's step value at fa, then B's at fb (B wins where it has
  keys); at t ≥ 0.5 leave it.
- Pivot: (1 − t)·A pivot + t·B pivot (usePivot = 1).
- Recursion pairs children by position, as `Animate` does. A negative frame makes the
  call fail (not reachable from U03).

`U03::AnimateTransition(a, b, n, fa, fb)` (a, b: slots on the same object; fa, fb = −1
take each slot's current frame once, before the loop). For i = 1..n:
1. Animation tick (every node advances and poses its object).
2. `Transition(object, a at fa, b at fb, i/n, 1, 1)`.
3. `RunFor(0)`: animation tick again, render, pump.

Step 3's tick re-poses the object from its active slot, which in every U03 call is a or b,
so the blended pose of step 2 is **never drawn**: what the player sees is n frames of the
active clip at its own frame, while every running node in the scene advances twice per
frame (both ticks use the same dt). An engine reproduces the original with n × (tick,
tick, render); computing the blend is optional, and a real crossfade would be an
enhancement, not parity.

## Welded objects (E-0054)

In a welded hierarchy the top object holds the only vertex array (N =
`weld_vertex_count` positions and normals); every welded object o, the top included, owns
the range [`weld_first_vertex`, `weld_first_vertex` + `own_vertex_count`), and the ranges
partition [0, N). Stored vertices are local to their owner. Each frame:

1. Build every object's W (after the animation tick).
2. For each vertex i: world position = Vᵢ · W(owner(i)); normal = the owner's W without
   translation applied to the normal (X3D flags chains with a scale ≠ 1 for its normal
   transform; renormalising those is inferred).
3. Draw every object's faces: its indices address the top's array, so a face may join
   vertices owned by different objects and stretches when they move apart (the "weld").

A non-welded object is the special case: it owns [0, count) of its own array. This
replaces `scene.md`'s rule of drawing weld faces with the vertex owner's W: that is the
top's W for every vertex, which garbles the characters. Objects with no range and no
faces (`$$$DUMMY…`, the joints between segments) only carry transforms.

LOD partners of welded objects are not needed in U01 (its character `lod=` lines are
commented out).

## Engine model

- Advance node frames in the fixed logic tick with dt = the tick length. For rendering
  above the tick rate, sample each node at the frame interpolated between the last two
  ticks (skip interpolation across a loop wrap); sampling is continuous in the frame, so
  this matches the original's per-present sampling. Re-apply every enabled node in list
  order, interpolated or not: a node that did not move (a paused mouth slot) must still
  override the earlier nodes that did (E-0606, E-0612).
- Hide and morph can be left unimplemented for U01 (no keys in the corpus), but keep the
  parsed data.

## Validation

- Pose check: the mayor, `U01_02` and Ernest at the hand-over viewpoint of E-0053, engine
  against `snap.ps1` of the original (`traces/u01-mayor-compare.png` shows the garbled
  static-view version).
- Timing check: `U01_02`'s idle loop (100 frames at 30 fps = 3.3 s) against a capture.
