# .3DA animation playback

How a `.3DA` animation poses the nodes of a scene. Which animations play, when, and what
happens at their end is scene code (`scene.md` "Animations", the flow docs in
`games/mission-sunlight/docs/`); this is the sampling. Layout in
`docs/formats/obj3d.ksy` (E-0016). Addresses in `/MISSION.EXE`. Proof: E-0514 (sampling),
E-0318 (records), E-0300 (ticks).

## Units

- **Time** is in 3D ticks of 66 ms (the multimedia timer, E-0300); a playing record
  adds the elapsed ticks (1..10 per frame) to its frame counter. Key times are integers
  in the same unit; every first rotation key is at 0.
- **Length**: the first word of track 0 (`Anim_Length` 0x437d90). Other tracks' first
  word is not read.
- **Rotation keys** are `(time, x, y, z, w)`, unit quaternions in Q15 (32767 ≈ 1).
- **Position keys** are `(time, x, y, z)` in world units, the node's local position.

## Speed (E-0378)

The scene step functions advance a playing record in one of three ways per handled tick:
by `elapsed` (almost all: real time, one frame per 66 ms whatever the frame rate); by 1
(chambreb's six tracks, chambrev's, the café bar door, mangeurs' stove door: one frame per
drawn frame, slower in real time when frames take longer than a tick); or by `elapsed >> 1`
(maisonet's bird out and back, with a floor of 1; mangeurs' rocking chair and eglise's
kite, without). At the full 15 frames per second the last kind runs at double its design
speed (the bird) or not at all (chair, kite: `1 >> 1 = 0`); it runs as designed only where
frames take two ticks, as on the recommended machines of the ReadMe (Pentium 133 to
Pentium II, software rendering, view sizes offered for speed). The engine steps these
three tracks one frame per two ticks (a bug fix); the others as the original at 15 frames
per second.

## Which node a track drives

Track i drives node i of the scene's node table (the `.3DC`'s table, root first), for i
below the scene's node count (`Anim_Pose` 0x438290). 44 of the 48 `.3DA` have exactly one
track per node; three have fewer (jardin 57 of 59, maisonj 16 of 17, mangeurs 23 of 25),
whose use would run past their track table in the original. A track with fewer than two
rotation keys leaves the node's rotation alone, and likewise for positions: a static
track does not reset a node.

## Sampling one track at time t (`Anim_PoseNode` 0x437da0)

For the rotation keys (skipped if the mask has bit 0), then the same for the position
keys (mask bit 1), with n ≥ 2 keys:

1. Find k: the first key index in 1..n−1 with `key[k].time ≥ t` by bisection (lo = 0,
   hi = n − 1; while lo + 1 < hi: mid = (lo + hi) / 2, `key[mid].time < t` → lo = mid,
   else hi = mid; k = hi). Past the last key, k = n − 1.
2. If `key[k].time ≤ t`: use key k as is.
3. Else `f = trunc((t − key[k−1].time) · 256 / (key[k].time − key[k−1].time))` (0..255)
   and interpolate from key k−1 to key k by f/256:
   - position: `p = (p1 · f + p0 · (256 − f)) >> 8` per axis;
   - rotation (`Quat_Slerp` 0x43b740), with `c = (q0 · q1) >> 15`:
     - `32768 − c < 21`: linear, `q = (q0 · (256 − f) + q1 · f) / 256` (as
       `(q0 · ((256 − f)·32768/256) + q1 · (f·32768/256)) >> 15`);
     - `32768 + c ≤ 20` (opposite keys): the original mixes q0 with `(−q0.y, q0.x,
       −q0.w, q0.z)` by sines of `(0.5 − f/256)·π/2` and `(f/256)·π/2`, for three
       components only and without renormalising; no pair of consecutive keys in the
       corpus is that close to opposite, so an engine needs no special case;
     - else slerp: `θ = acos(c / 32768)` (table), `q = (q0 · sin((256 − f)θ/256) + q1 ·
       sin(fθ/256)) / sin θ`, all in Q15 through the tables.
     There is **no flip to the shorter arc** when `c < 0`: such keys turn the long
     way. Of the 2,951 pairs of consecutive rotation keys in the corpus, 36 have
     `c < 0`; 385 are within the linear threshold.
4. Rotation → the node's local rotation matrix (`Quat_ToMatrix` 0x43b480, standard
   form, Q15): `m0 = 1 − 2(y² + z²)`, `m1 = 2(xy − wz)`, `m2 = 2(xz + wy)`,
   `m3 = 2(xy + wz)`, `m4 = 1 − 2(x² + z²)`, `m5 = 2(yz − wx)`, `m6 = 2(xz − wy)`,
   `m7 = 2(yz + wx)`, `m8 = 1 − 2(x² + y²)` (row-major, column vectors, like every node
   matrix in `render.md`). Position → the node's local position.

The frame's traversal then recomputes world matrices from these local ones
(`render.md`).

## Blends between two poses (`Anim_Pose` 0x438290)

`Anim_Pose(scene, keyA, keyB, t, mask)`: keys are `animation << 16 | frame`.

- Same animation: sample every track at `t_s = ((256 − t) · frameA + t · frameB) / 256`
  (a float, so between keys the fraction of step 3 uses it unrounded).
- Two animations: sample each at its own frame, then mix the two results by t / 256
  (slerp for rotations, linear for positions, as in step 3).

All 51 calls in the scene code pass t = 0 and mask 0, with the same key twice (E-0318):
in this game a pose is always one animation at an integer frame.
