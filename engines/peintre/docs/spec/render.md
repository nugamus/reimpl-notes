# The 3D renderer

How PEINTRE draws a 3D frame, and what an OpenGL (or TinyGL) engine has to do to give the
same picture. The original has no Direct3D (E-0004): it transforms, culls and clips in C,
builds edge lists, resolves visibility per scanline with a span buffer, and fills the
spans with hand-written assembly on a 16-bit DirectDraw surface. None of that machinery
needs reproducing; its rules do. Addresses are in `/MISSION.EXE`. The camera pose and
the view sizes come from `scene.md` and `movement.md`, picking's use from
`interaction.md`, the `.3DC`/`.3DM` layouts from `docs/formats/obj3d.ksy`, animation from
`animation.md`.

## In one paragraph (what the engine needs first)

Draw the camera's subtree of nodes; each node's matrix is `parent × local` (Q15
rotation, integer position). Camera space is **x right, y down, z forward** and so is
the world (right-handed). Project with focal length `0.75 · viewport width` on both axes
around the viewport centre, near plane 64, far 80,000 (E-0502): a 67.4° × 53.1° field of
view whatever the view size. Triangles are single-sided: **front faces run
counter-clockwise on screen** (E-0503). Visibility is exact per pixel by 1/z (use a depth
buffer). Every textured triangle is point-sampled from its `.3DM` with **shade row 16**
as its palette (E-0508), perspective-correct. Group type **3** is opaque, **−6** does not
draw texel 0 (alpha test), **−4** is a 50 % blend with what is behind, **1** is a flat
colour (E-0507). No lighting, no fog, no mipmaps, black background (E-0506, E-0508).

## Per frame (E-0500)

`Render_Frame` (0x4378f0), called once per handled 66 ms tick by the 3D frame (E-0300):

1. Walk the tree depth first from the camera node (`Render_WalkTree` 0x450160): first
   child, then next sibling, back up through the parent. A node with flag bit 0 (hidden,
   `Node_Hide`) is skipped **with its whole subtree**. The camera itself is not drawn.
2. For each node on the way down (`Render_Node` 0x44fec0):
   - world rotation `W = P.W · L >> 15` (Q15, each element truncated), world position
     `T = trunc(P.W · p / 32768) + P.T`, where P is the parent and `L`, `p` the node's
     local rotation (+0x28) and position (+0x1c). "World" here is camera space: the
     camera's own W, T are its inverse pose (below).
   - skip the rest if flag bit 2 is set;
   - cull the node by its bounding sphere (E-0504, below);
   - transform its vertices to camera space and project the ones that are used; cull and
     near-clip its polys (E-0505);
   - build the edges of its face groups (`Render_BuildEdges` 0x447c30) unless flag
     0x1000.
3. On the way back up, put the node's new edges into per-scanline buckets
   (`Render_BucketEdges` 0x447d90).
4. Resolve every scanline of the viewport into spans (`Span_ResolveFrame` 0x44ab80) and
   fill them (E-0506).

An engine does steps 1–2 as a scene-graph traversal and draws the triangles with the
rules below; steps 3–4 are the software visibility algorithm a depth buffer replaces.

## Camera and view transform (E-0501, E-0502)

- The camera is node `Camera`, handle 0, flag 0x400, the root of everything drawn; each
  loaded scene is attached as its child (`Node_AttachTo` 0x435880).
- Setting its position `eye` and rotation `R` (`scene.md`: 0x422f30 from pitch, yaw, roll
  through `Matrix_FromAngles` 0x43a780, `movement.md`) stores `W = Rᵀ` and
  `T = −(Rᵀ · eye >> 15)`. So for any world point: `v_cam = Rᵀ · (v − eye)`. The columns
  of R are the camera's right, down and forward axes in world space; at angles 0 the
  camera looks along +z with +y down.
- Every other node's W, T is therefore the product view × model: in GL terms the
  modelview matrix of a node is `[W | T]` (divide W by 32768).

## Projection (E-0502)

Viewport (from the view size, `scene.md`): width `w`, height `h`, top-left `(x0, y0)` on
the 640×480 screen. With `f = 480 · w / 640` (integer division), `cx = w/2 + x0`,
`cy = h/2 + y0`:

```
sx = trunc(f · x / z + cx)          (MSVC __ftol: toward zero)
sy = trunc(f · y / z + cy)
depth key = 2^30 / z                 (float; larger is nearer)
```

The vertical focal length is `f · (4h)/(3w)`, equal to `f` for all four view sizes (all
4:3). Hence the field of view is fixed: `tan(hfov/2) = 2/3`, `tan(vfov/2) = 1/2`
(67.38° × 53.13°), and a smaller view size only shrinks the picture.

**Near and far**: near = 64 and far = 80,000 after a scene load; after the option menu's
viewport change alone, 128 and 65,000 (`scene.md`, E-0307). Triangles crossing the near
plane are clipped (new corners interpolate position and UV, 0x44c370). A triangle with
**any** corner at or beyond far is dropped whole (unless its node has flag 0x80, which no
file uses); a GL far plane at the same distance differs only by clipping per pixel
instead, which the scenes (much smaller than 80,000 units) never show.

**Integer snapping**: projected corners are truncated to whole pixels before
rasterisation (E-0502). A faithful mode can snap `sx, sy` the same way (the slight
jitter of the original); otherwise use sub-pixel GL coordinates.

For GL: an off-centre-free perspective with `x_ndc = x·f/(z·w/2)`, `y_ndc = −y·f/(z·h/2)`
(y flipped, because camera y is down), near 64, far 80,000, drawn into the viewport
rectangle of the current view size; outside it the frame shows the 2D border
(`scene.md`).

## Node culling and node flags (E-0504)

- Bounding sphere: centre node +0xb4..+0xbc (node space), radius +0xb0. The node is
  culled (flag bit 3) when the sphere lies wholly outside one side plane of the view
  cone, wholly before near, or wholly beyond far (without flag 0x80). GL clipping gives
  the same picture; the test is only an optimisation — with one exception:
- **Flag 0x10** (132 + 26 nodes in the files): the node's polys may use vertices of its
  **parent** (those flagged 0x80 in the parent's array; 1,628 corners in the corpus). Such
  a vertex moves with the parent's matrix, not the child's. An engine must transform each
  vertex with the node that owns its array. A 0x10 node is drawn even when its own
  sphere is culled, provided its parent is not.
- Flag bit 0 (hidden) is the only flag the game changes at runtime (`Node_Hide` /
  `Node_Show`); bits 0x4, 0x80, 0x800, 0x1000 never occur (E-0504, E-0513).

## Back faces (E-0505, E-0503)

- Poly word 0 bit 3 clear (the usual case): the poly is front-facing when
  `n · e >> 15 ≥ plane_distance` (poly +0x30), n = face normal (Q15, node space), e = the
  eye in node space. `plane_distance = (n · v0) >> 15` in the files.
- Bit 3 set (1,275 polys, all in 0x10 nodes): front-facing when
  `v0 · ((v0 − v1) × (v1 − v2)) < 0` with the corners in camera space — the plane cannot
  be precomputed because corners belong to two nodes.
- The span builders then draw only triangles with negative signed area on the y-down
  screen: `(y2−y1)(x1−x0) − (y1−y0)(x2−x1) < 0`, i.e. corners 0 → 1 → 2 counter-clockwise
  as the player sees them. The corpus agrees with the plane test (99.4 % of 82,657
  projected polys, `tools/winding_check.py`), so an engine can use GL back-face culling
  alone: with the y flip above, GL's default `glFrontFace(GL_CCW)` + `glCullFace(GL_BACK)`
  keeps exactly these.
- No face is two-sided; zero-area triangles are not drawn.

## Visibility (E-0506)

There is no z-buffer. Per scanline, surfaces are ordered by their `2^30/z` at the current
x (from the left edge's value plus `(x − edge.x) · d(1/z)/dx`); a surface wins when that
value is larger, or when it is within 100 of the current one and its x-gradient of 1/z is
larger (a tie-break for coplanar and touching surfaces). This is a per-pixel "nearest
1/z wins" test, so a depth buffer (with `GL_LEQUAL` or a small polygon offset for
decals, if z-fighting appears where the original's tie-break picks consistently) gives
the same picture. Lines on which a negative-type surface (−6, −4) is active are resolved
by a second routine (0x44a820) that also emits the spans behind it: the −6 fill skips
key pixels and the −4 fill reads the pixel already there, so what lies behind them shows
through. With GL: alpha test for −6, blending after the opaque pass for −4.

The **background** is a permanent surface behind everything, filled with colour 0
(black) (type 14, colour 0x4e3600 never changes). Clear the viewport to black.

## Face groups: types and how their pixels are made (E-0507)

A node's polys come in face groups, one per material; the group's `type` selects the
edge builder and, per span, the fill routine. Only four types occur in the corpus:

| Type | Groups | Texture | Pixel | Addressing |
|---:|---:|---|---|---|
| 3 | 839 | yes | opaque: every pixel written | `texels[floor(v)·256 + floor(u)]`, no wrap |
| −6 | 384 | yes | texel 0 is not drawn (colour key) | offset `& 0xFFFF`: u and v wrap at 256 |
| −4 | 1 (pont `eau`, the water) | yes | `(src + dst) / 2` per RGB565 channel, via `((src & 0xF7DE) + (dst & 0xF7DE)) >> 1`; no key | u and v each wrap at 256 |
| 1 | 11 (38 polys) | no | flat colour (below) | — |

Common to the textured types (0x444e20 builds, 0x45ee50 / 0x460450 / 0x45a3b0 fill):

- **Texture**: the group's material names a `.3DM` (E-0015): a 32 × 256 shade table of
  RGB565 colours (high half of each u32) and 256-wide rows of 8-bit texel indices. The
  pixel colour is `shade[row][texel]`.
- **Shade row**: `31 − brightness`, brightness = the low byte of node +0xd0, which is 15
  in every node and set to 15 at every scene load: **row 16 for everything** (E-0508).
  The engine can build each texture once as RGB565 (or RGB888) from row 16.
- **UVs**: poly +0x34..+0x3c point at 16.16 UVs in texel units (0..256). Mapping is
  perspective-correct: 1/z, u/z, v/z are interpolated and divided exactly every 16
  pixels, linearly in between (Quake-style); GL's perspective-correct interpolation is
  indistinguishable. Sampling is **nearest** (texel = integer part, 8-bit fractions),
  no filtering, no mipmaps (the mip code of type 0x14 has no group in the corpus,
  E-0513).
- **Addressing for GL**: −6 and −4 wrap → `GL_REPEAT` is exact. Type 3 does not wrap:
  `u ≥ 256` runs on into the next texel row and v outside 0..255 reads memory outside
  the texture. Only 8 type-3 groups, all in maisonj, have UVs outside [0, 256] (E-0509);
  `GL_REPEAT` there shows the tiling the artists meant, off by one row per 256 texels of u
  (e.g. `SOL`, u up to 764) — accept it, or emulate by shifting v by `floor(u / 256)`
  rows.
- **Odd sizes** (Q-0003, E-0509): jardin `salon.3DM` has 258 rows, musee `plafond`,
  `plafond2`, `plafond3` 255. Rows are always 256 texels; the corpus UVs never go past
  row 255 (and reach it only at v = 255.0 exactly). Use the first 256 rows; pad a 255-row
  texture with a copy of its last row.
- **Colour key** (type −6): texel index 0, whatever colour row 16 gives it. With GL,
  make texel 0 transparent in the texture and alpha-test (discard) — draw type −6 with
  the opaque pass (depth write on).
- **Blend** (type −4): draw after the opaque and keyed geometry, depth test on, depth
  write off, `glBlendFunc(GL_CONSTANT_ALPHA …)` with 0.5 or `GL_SRC_ALPHA` with alpha
  0.5; the original's halving truncates each channel's LSB first (not visible).

**Type 1, flat colour** (0x43c780, 0x45809a): the colour is the RGB565 `colour` of the
material (`obj3d.ksy`), 0x3DEF on every DEFAULT material — **plus 0x1388 per poly** in
group order, wrapping at 0x10000 (the original's code, E-0507): poly k of the group is
drawn in `(colour + (k + 1) · 0x1388) & 0xFFFF` read as RGB565, k counting every poly
of the group's draw list (file order, culled ones included). These are 38 polys on
helper objects (chambreb `perpompe`, champ `animfaux01`, `corbopere`, hopiext
`porche02`, musee `brul`…`brul05`, terrasse `drapoanim` with none); whether the game
shows them depends on the scene code hiding them (flow docs).

## Lighting (E-0508)

The engine contains per-poly lighting (directional and point lights with inner/outer
radii, brightness into poly +0x34/+0x40, rows chosen per poly), but no scene has a light
(node +0xc4 = 0, light count never set) and the brightness of every node is 15. **The
game is unlit**: every textured pixel uses row 16 of its shade table. Nothing else varies
the shade row (no distance fog). Rows 0..15 (brighter) and 17..31 (darker) are never
displayed.

## Picking (E-0512)

`Pick_Node` (0x439b90) re-runs the per-node pipeline for the current camera with a test
in place of the drawing: for every visible, front-facing, not-culled poly of every group
type (near-clipped pieces included, colour key ignored) whose projected triangle contains
the point `(x, y)` — edges inclusive, integer corners as drawn — it computes the depth of
the poly's plane along the view ray through the point; the node of the nearest wins.
The engine can ray-cast the same triangles (or render node ids without alpha test) and
must skip hidden subtrees exactly as the drawing does. Hidden nodes are not pickable;
transparent texels of −6 groups are.

## Colour formats (E-0510)

Everything is RGB565. On a 15-bit (RGB555) display the original converts each loaded
shade table once (`r << 10 | (g >> 1) << 5 | b`) and swaps its blend routines for 555
versions; that is a pixel-format detail, not a difference in the picture. An engine
renders from the RGB565 data.

## Not used by this game (E-0513)

Sphere-mapped UVs (node flag 0x800), mip levels (type 0x14), the other 30 or so group
types the dispatch tables know (−22..32), a second span resolver and walker, a triangle
export hook, node bounding boxes (+0x9c/+0xa0), the lights above. None needs
implementing.

## Where the assembly fits (Q-0002, E-0511)

The 64 KB at 0x455470–0x465bcf is `Render_LightsToCamera` (a C function) followed by the
span routines, entered only through the type-indexed tables at 0x4b2084 (used by the span
walker 0x454a8e) and 0x4b2174 (used by nothing). Their interface: ebx = first x, ecx =
pixel count, edi = destination, ebp = the edge record carrying the gradients, shade row
and texture pointer. The routines the corpus reaches are described above; the listing is
in `notes/decomp/MISSION.EXE__asm_render.s`.
