# Scene load, views and drawing (engine behaviour)

How the engine loads a scene (`.abi` + `.scn`), which pre-rendered view it shows, and how it
draws the view, its sprites and its 3D actors. Formats: `docs/formats/README.md` (`.abi`,
`.scn`, `.fxi`, `.anb`). Evidence: E-0100..E-0104, E-0300..E-0305, E-0600..E-0602.

## `.abi` load (E-0100, E-0104)

A `.abi` file is a flat stream of actor records read to end-of-file by
`CFXActorFactory::CreateFromABIFile`:

    record = u32 type, u32 id, <Serialize(mode 1)>

`CreateActor` maps `type` to a `CFX*` class (34 codes, object sizes in
`notes/actor-types.txt`), allocates it, and injects the shared render device into the new
actor before deserialising. A trailing chunk shorter than the 8-byte type+id header ends the
loop (`Scene_400.abi` has 4 such padding bytes). The per-type mode-1 read grammar — the only
thing the engine needs to walk the stream and find the records it cares about — is the
reference parser `tools/parsers/abi.py` (111/111 scene/item files, byte-exact). Shared
members: `EC` (20 bytes), `CC` (= 5 u32 + count + n·EC), pascal strings (u32 len + bytes),
and two inline sub-objects (56 and 24 bytes). Type 0x03 `CFXCharacter` (the `Characters.abi`
/ `Actors/*.abi` database) is not yet modelled (Q-0006).

A scene is `Scenes/Scene_<NNN>.scn` (walk mesh, exits, views; E-0500) then
`Scenes/Scene_<NNN>.abi` (its actors), both read by the same loader (E-0301).

## Views (E-0301, E-0304)

The `.scn`'s last record is the CFXView (type 9, id 602):
`u32 9, u32 602, u32 n, n × (pstr "<v>_IS.jpg", pstr "<v>_IZ.fxi"), n × view matrix,
n × projection matrix` (4×4 little-endian floats each). View k is entry k: its colour
background, its depth buffer and its camera, the Direct3D 7 VIEW and PROJECTION transforms
(row vectors, left-handed):

    clip   = (x, y, z, 1) · View_k · Proj_k
    screen = ((clip.x/clip.w + 1) · 400,  (1 − clip.y/clip.w) · 300)
    z16    = clip.z/clip.w · 65535          // the z-buffer value

On scene entry view 0 is shown. 185 op 30 fades to view `arg1`. While the player walks, the
view follows the floor cell the character stands on (E-0304). Showing view k loads its
`_IS.jpg` as the background and its `_IZ.fxi` into the 16-bit z-buffer.

## Lights (E-0300)

A type-0x11 record (`CFXLight`) ends with `u32` (unused) and a `D3DLIGHT7` (26 floats): `[0]`
type (1 = point), `[1..4]` diffuse rgba, `[13..15]` position, `[19]` range, `[21..23]`
attenuation. Light index = id − 630. It is set and enabled at load; opcodes 2/3 switch it
on/off; update mode `+0x1b8` 1 flickers it, mode 2 varies its colour like fire.

## Drawing order (E-0305)

Each frame: the view's background and depth, then every visible actor by layer `+0x114`,
ascending: layer-1 sprites, layer-3 mesh actors (0x1a), layer-4 sprites (layer 8: the
fades of 185).

## Sprites (type 0x0d CFXSprite, E-0106, E-0302)

A visible sprite is drawn when its view `+0x1c8` is −1 or the current view, at `+0x190,
+0x194`, clipped to 800×600:

1. if it has depth frames, the frame's depth is copied into the z-buffer over its
   rectangle (no key);
2. the colour frame is copied to the page, skipping the key colour when `+0x1f8` = 1 (key =
   COLORREF `+0x208` = 0x00BBGGRR, or frame 0's pixel (0,0) when −1; an exact 16-bit match),
   else opaque.

Frame files: a name `<stem>0000.<ext>` animates; frame i is `<stem>%04d.<ext>` while it
exists; depth frames `<stem>_Z%04d.fxi`. Any other name is a still with depth
`<name without ext>_Z.fxi`. Animation: one frame every `50/fps` game ticks of 20 ms (`+0x1e0`
fps), mode bits `+0x1e4` as E-0208.

## Mesh actors (type 0x1a CFXStaticCharacter, E-0303)

A visible 0x1a actor draws its `.anb` at its current frame (below; nothing when the frame is
outside `0..F-1`) in world space (no world transform) through the current view's camera, as
Direct3D 7's fixed pipeline does. Each triangle corner is the vertex the loader stored for
the corner's uv index (the last corner naming that uv index in face order, E-0600), with
that vertex's stored normal (x, y, z, not normalised):

- **culling**: counter-clockwise triangles on screen are dropped (D3DCULL_CCW);
- **lighting**, per vertex (Gouraud), material = the texture's (default diffuse and ambient
  white; a `<texture>.tma` overrides it): `colour = ambient 0x1e1e1e + Σ lights on, within
  range: diffuse · max(0, N·L) / (a0 + a1·d + a2·d²)`, clamped to 1;
- **texture**: modulated with the lit colour, bilinear filtering, wrap addressing. A 32-bit
  `.tga` keeps its alpha and is blended (SRCALPHA, INVSRCALPHA), any other is RGB555;
- **depth**: `z16 ≤ z-buffer` passes and writes `z16`.

- **clipping**: triangles are clipped to the near plane (and z beyond the far plane is not
  drawn), as Direct3D clips in homogeneous space.

### Mesh animation (E-0601, E-0602)

From the record: fps `+0x1b4`, mode `+0x1b8` (bits as sprites: 1 loop, 2 ping-pong, 4
forward, 8 backward, 0x10 forward on one play and back on the next), playing `+0x1d4`, start
frame `+0x1c0`, autoplay `+0x1dc`, and a delay timer (on, counting, random, min/max ms, fixed
ms, ticks left). Running and direction start at 0, so nothing moves until the actor is played
(or its timer, saved counting, runs out).

- **play** (ops 0, 500, and 23 when autoplay): mode & 6 → frame 0; mode & 8 → frame F; playing
  on; with the timer on, start the timer (ticks = ms × 50 / 1000, random in [min, max) when
  random) instead of running; else running on. Always restarts, playing or not.
- **stop** (ops 1, 501): playing off; a looping animation runs to the end of its cycle.
- **update** (every 20 ms update, while active): running → after `R / fps` updates (R = 50,
  Q-0200) advance one frame. Not running with the timer on: while playing and the timer
  counts, one tick a update; at 0 it stops counting, reloads, and running goes on; not
  playing → the timer reloads and running stays off.
- **advance**, by the first of bits 4, 8, 2, 0x10: forward → frame + 1, at F: running off;
  without loop frame F−1 and run the end list (the 7th in the file, `+0x19c`; E-1807 corrects E-0601); with loop, frame F−1 if stopped,
  else frame 0 and restart. Backward → mirror (frame 0 / F−1, end list). Ping-pong → up to
  F−1, then down (F−2, …); below 0: running off, frame 1, direction up; without loop the end
  list, with loop and playing restart. 0x10 → up to F−1, then running off, direction down,
  forward-end list (1st); on the next play down to 0, then running off, direction up,
  backward-end list (2nd). Restart = play again when the timer is on, else running on.
- **ops**: 2/3 visible, 11/12 active, 13 latch (inactive, invisible; ignores all but 52), 52
  unlatch, 14/15 contact tests on/off, 86 reload mesh and texture, 92 texture.
- **contact spheres** (E-1681, E-1683): each `(vertex, radius)` rides a vertex of the current
  frame, the vertex counted as the renderer's buffer counts them: one per uv index, across the
  sections in order, at the position of the vertex that uv index's corner names. With flag bit
  1 the player's body sphere touching one runs the third list (once per touch with `once`).
  The air bubbles (Air +10) and scene 90's rolling stones (Life −22, then op 15) use it.
  The full test (E-1684), only while contact tests are on (op 14/15): for each sphere in
  order, the kinds by flag bit, in this order; the first one that runs a list ends the update:
  - bit 1: the player's (actor 3's) character → 3rd list (`+0x14c`);
  - bit 2: the follower's (actor 4's) character, or fighter 95's when there is no actor 4 →
    4th list (`+0x15c`);
  - bit 8: the spheres of the mesh named in the file (`+0x228`; it must be active and have
    its own tests on) → 6th list (`+0x18c`);
  - bit 0x10: the characters held by fighters 91, 92, 93, 94, in that order → 8th list
    (`+0x16c`, "the fighters' contact list"); bit 4 is never tested.
  Each kind has its own latch (bit 0x10: one per fighter) when `once` = 1: a hit with the
  latch set passes on to the next kind; a miss clears it. Latches are per mesh, so on a
  mesh with several spheres a later sphere's miss re-arms a touch the first still has. With
  `once` = 0 a touch runs its list every update. Character-id filters (`+0x220`, `+0x224`)
  are never loaded (−1). The 5th list (`+0x17c`) is never run. In the data: bit 0x10 in 27
  (ants vs the crocodile boss), 105 (barrels vs the pirate rat) and 33 (the falling stone);
  bit 8 in 9 (boulder → snake 716) and 13 (bananas → 713); bit 2 only on meshes without
  spheres (1, 3, 211), so it never fires.
- **scene status**: active, visible, latch, playing, running, direction, frame and autoplay are
  kept; autoplay is kept as 0, so a revisited scene does not autoplay again (E-0602).

Characters (type 0x03) are drawn the same way, after their own world placement
(`spec/characters.md`).
