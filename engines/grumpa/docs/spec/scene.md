# Scene load, views and drawing (engine behaviour)

How the engine loads a scene (`.abi` + `.scn`), which pre-rendered view it shows, and how it
draws the view, its sprites and its 3D actors. Formats: `docs/formats/README.md` (`.abi`,
`.scn`, `.fxi`, `.anb`). Evidence: E-0100..E-0104, E-0300..E-0305.

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

A visible 0x1a actor draws its `.anb` (frame 0 here) in world space (no world transform)
through the current view's camera, as Direct3D 7's fixed pipeline does:

- **culling**: counter-clockwise triangles on screen are dropped (D3DCULL_CCW);
- **lighting**, per vertex (Gouraud), material = the texture's (default diffuse and ambient
  white; a `<texture>.tma` overrides it): `colour = ambient 0x1e1e1e + Σ lights on, within
  range: diffuse · max(0, N·L) / (a0 + a1·d + a2·d²)`, clamped to 1;
- **texture**: modulated with the lit colour, bilinear filtering, wrap addressing. A 32-bit
  `.tga` keeps its alpha and is blended (SRCALPHA, INVSRCALPHA), any other is RGB555;
- **depth**: `z16 ≤ z-buffer` passes and writes `z16`.

Characters (type 0x03) are drawn the same way, after their own world placement
(`spec/characters.md`).
