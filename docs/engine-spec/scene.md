# Scene loading and the static view

What the engine needs to load a unit (U01 first) and draw it from a fixed camera.
Movement, animation playback and the main loop are separate specs.

## Which scene

A new game loads the scene named by the first 30 bytes of `App.bin` chunk `#GAME#`,
`U01.X3D` in the corpus (E-0037). The unit number is the two digits after the first
character; U01 builds unit class 1 (E-0033). `U##D.X3D` scripts are backdrops for the
painting view, not playable scenes.

## Loading a unit (E-0036, E-0039)

For scene file `Uxx.X3D`:

1. Asset directory `Data/Uxx/` (U00 uses `U04/`, E-0034). Map search path
   `Data/Uxx/Maps/`.
2. `Data/Uxx/SCENE.BIN` (`.BIN` chunk container, E-0025):
   `#SCENE#` gives the ambient light colour (r, g, b as u32) and the scene scale (f32);
   `#CAMERA#` gives the horizontal field of view in degrees, the collision sphere radius
   and Z offset, and an unused speed. U01: ambient (255, 255, 255), scale 40, FOV 90.
3. Run the `.X3D` script (grammar in `docs/formats/README.md`). In file order:
   - `object=`: load the `.O3D` and add its objects. Objects from a path starting
     `static\col` are loaded but hidden: they are collision geometry.
   - `lod=`: attach a lower-detail `.O3D` to the last object (see Levels of detail).
   - `animation=`: attach an `.A3D` to the last object. Not played in the static view.
   - `light=`: load an `.L3D`; every light affects every object.
   - `camera=`: load a `.C3D` (U01 has it commented out).

## Geometry (`.O3D`, `docs/formats/o3d.ksy`)

- A face is a polygon of `num_vertices` indices into its object's vertex array (or its
  parent's, when the object has none of its own). Draw it as a triangle fan.
- Per-face-vertex UVs when `has_uv`; the face's material index selects the file's material.
- Vertices are object-local (E-0042). World position of a vertex v (a row vector) is
  v · W, with the object's world matrix
  - root: W = Tr(−pivot) · diag(local_scale) · M · Tr(local_position)
  - child: W = Tr(−pivot) · diag(local_scale) · M · Tr(parent.pivot) · Tr(local_position) · W(parent)

  where Tr(t) is the identity with t in row 3 and M the object's stored 4×4 (row-vector
  form, translation in elements 12..14). The parent is the named object loaded earlier in
  the same file. World space is Z up.
- Objects whose faces index their parent's vertices ("weld" objects, the characters) are
  drawn with the vertex owner's W: the bind pose (Q-0020).
- Faceless objects (splines, helpers) are not drawn; some carry garbage coordinates.

## Levels of detail (E-0052)

- `object=` yields the file's first object (its root). `lod="file,d"` pairs the LOD file's
  root with that root, then recursively the i-th child of each base object with the i-th
  child of its partner, children in file order; a base child with no partner gets no LOD.
  Each partner becomes a LOD of its base object with threshold d² (d < 0 counts as 0).
  Several `lod=` lines on one object add more partners.
- Every frame, for each base object: s = squared distance from the object's world origin
  (row 3 of its W) to the camera position. Draw the partner with the largest threshold
  ≤ s; if none qualifies, draw the base object. The chosen object is drawn with its own
  geometry, materials and W (the LOD file's hierarchy). LOD files are never drawn on
  their own.

## Materials and textures (E-0038)

- A material's `texture_map` name ends `.TGA`; replace the extension with `.dmf` and load
  it from the map search path. Materials without a map draw their second colour.
- `.DMF` pixels: bpp 8 through a B, G, R, x palette; bpp 15 as RGB555; bpp 16 as RGB565.
- A map with an `fb21` colour key: texels equal to the key are transparent (the loader
  sets a "keyed" flag; how the rasteriser uses it is inferred).
- UV v = 0 is the first stored row: upload the rows in file order (E-0044).

## Lighting

Not specified yet (Q-0019). The static view draws textures at full brightness modulated
by the ambient colour / 255 (U01's ambient is white).

## Camera and projection (E-0040)

- Camera state: position p, yaw a, pitch e (e measured from straight down: π/2 is level),
  roll r in degrees (0 in U01), horizontal FOV f in degrees.
- View direction (cos a · sin e, −sin a · sin e, −cos e); up is world +Z when e = π/2.
  Camera axes (row-vector X3D form): right = (−sin a, −cos a, 0),
  up = (cos e · cos a, −cos e · sin a, sin e), forward = (sin e · cos a, −sin e · sin a, −cos e).
  Camera up is screen up and right is screen right (E-0044).
- x is scaled by 1 / tan(f/2); y by 4/3 of that, whatever the output size: the original
  frames every mode as 4:3 (E-0040). Near plane 0.1, far 1,000,000.
- Widescreen (engine goal, not the original): keep the vertical extent of the 4:3 frame
  and widen the horizontal one.

## U01 start camera (E-0041)

p = (−258.44, −508.20, 29.546), a = 1.31, e = π/2 (1.5707960). This is the first shot of
U01's scripted entry, right after the prologue video.

## Camera-facing objects

Objects whose names contain `$XYZ$`, `$Z$` or `$XZ$` get camera types 1, 2, 3 (E-0045);
how they are oriented is not specified yet (Q-0021). The static view draws them as stored.

## Validation

`tools/proxy/run.ps1` + `snap.ps1` capture of the original at the same moment, side by
side with `snap.ps1 … scummvm`. Done for U01's first shot (E-0044); open differences in
Q-0021.
