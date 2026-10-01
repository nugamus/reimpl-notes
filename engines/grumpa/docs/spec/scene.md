# Scene load and per-view camera (engine behaviour)

How the engine loads a `.abi` scene graph and sets up the camera for a pre-rendered view.
Formats: see `docs/formats/README.md` (`.abi`, `.fxi`). Evidence: E-0100..E-0105.

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

A scene is `Scenes/Scene_<NNN>.abi`; its views are the type-0x11 records. The colour
background and depth of a view are the paired files `<view>_IS.jpg` + `<view>_IZ.fxi`
(E-0011); the `.fxi` holds the render device's own 16-bit z-buffer, so an actor composites
into the view by the per-pixel depth test `actor_z16 < fxi_z16` (E-0010).

## Per-view camera (E-0103, E-0105)

A type-0x11 view ends with `u32 cam_id` then a 0x68-byte block of 26 little-endian floats,
which the original hands straight to the render device
(`dev->vtable[0x38]()->vtable[0x48](handle, block)`). Across the whole corpus only these
indices (0-based) are non-zero:

| index | meaning |
|---|---|
| 1, 21 | constants (1.0) |
| 2, 3 | projection scale x, y (1.0 ⇒ 90° FOV; smaller ⇒ wider) |
| 13, 14, 15 | camera eye position x, y, z |
| 19 | far / range (scene-sized) |

The nine orientation slots are 0 in every view, so the views are orientation-identity: the
eye sits above and in front of the geometry (which lies toward −Z), so the camera looks along
**−Z**, up **+Y**. Engine camera:

    eye     = (block[13], block[14], block[15])
    forward = (0, 0, -1),  up = (0, 1, 0),  right = (1, 0, 0)
    NDC     = (block[2] * vx/vz,  block[3] * vy/vz)        // vz = -(view-space Z)
    screen  = ((0.5 + 0.5*NDC.x) * W,  (0.5 - 0.5*NDC.y) * H)
    far     = block[19]

Open (Q-0008 sub-point): the exact device projection — whether `block[2]/[3]` are
`cot(fov/2)` diagonal terms (assumed here) and how view-space Z maps to the `.fxi` 16-bit
depth (linear vs 1/z) — awaits the device `vtable[0x48]` decompile. The model above is
calibrated against the pre-rendered backgrounds; when static and runtime disagree, the
rendered result wins.
