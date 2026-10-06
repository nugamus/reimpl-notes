# Matching the original's 3D

Three of our games have 3D: Grumpa (Direct3D 7 meshes composited into pre-rendered
scenes), Mission Sunlight (the game's own software rasteriser on DirectDraw, no Direct3D at
all), Monet (its own 3D engine, drawn with OpenGL or TinyGL in ScummVM). The goal is the
original's picture, not a modern one.

**Find out what really rasterised it.** Interface ids in the binary tell: Direct3D
(`IID_IDirect3D7`, `D3DIM.DLL` imports) or only DirectDraw (then the game rasterises
itself, as Mission Sunlight, E-0004). A software rasteriser's own rules (fixed point,
sub-pixel precision, fill convention, perspective correction or affine spans) are spec
material: port them, don't approximate them with OpenGL.

**Direct3D 7 state that changes the picture**, to read from the original's render-state
calls and reproduce: culling (`D3DRENDERSTATE_CULLMODE`, Grumpa's meshes are CCW-culled),
z-test and z-write, shading (`D3DSHADE_GOURAUD`), texture filtering (Grumpa: bilinear),
colour-key transparency and alpha blending, fog, lighting (`D3DLIGHT7` point and
directional lights with the material's ambient/diffuse; Grumpa's 0x11 records are lights),
the viewport and the projection and view matrices the game sets (Grumpa's per-view
matrices come from the `.scn`, E-0301). apitrace's `d3d7` mode logs these calls in the
running original (observing-the-original.md).

**Compositing into pre-rendered scenes.** A pre-rendered background plus a depth image
(Grumpa's `_IZ.fxi`) is a z-buffer filled before the meshes draw: decode the depth the way
the original's device read it (format, near/far, linear or 1/z; Grumpa's Q-0008), then draw
meshes with the same projection so their depths compare. A wrong depth mapping shows as
characters vanishing behind or popping in front of foreground objects: test with a scene
where an actor stands behind foliage (Grumpa `grumpa_scene=7_1`).

**Where ScummVM draws 3D.** For fidelity, a software renderer in the engine (as Grumpa's
`render3d.cpp`), or TinyGL, which mimics OpenGL 1.x in software and runs on every port
(Monet). Hardware OpenGL is an option for higher resolutions, never the only path, since
ScummVM runs on devices without it. Build with optimisations: TinyGL is several times
slower without them.

**Proving parity.** Scenarios that snap the same view as a frame captured from the
original (snap.ps1 on the windowed original, or a playthrough frame from longplay.py),
compared side by side on the review page; differences in filtering or depth show at
edges first, so pick views with silhouettes against the background.
