# Lighting

How X3D colours each drawn vertex: scene ambient plus the `.L3D` lights, per vertex,
recomputed every frame, then modulated with the texture by Direct3D. Replaces the
"texture × ambient / 255" stand-in of `scene.md`.

## Inputs

**Scene ambient** A = (r, g, b) from `#SCENE#` (E-0039), 0..255 per channel.

**Light** (`.L3D`, E-0140), in file order after the name, position P and colour C (RGB
bytes):

| Field | Meaning |
|---|---|
| f32 `inner` | full-strength radius |
| f32 `outer` | radius beyond which the light contributes nothing |
| f32 `multiplier` | scales the contribution; **negative values darken** |
| u32 `hidden` | non-zero: the light is skipped |
| u32 `attenuate` | 0: no distance limit (inner, outer ignored); non-zero: falloff below |
| u32 `is_spot` | spot branch (target T, angles θ, φ in degrees); no corpus sample (Q-0013) |

A light's world position is its file position (lights are not parented in the corpus).

**Material** (`.O3D`, E-0141), fields in file order:

| Offset | Field | Used for |
|---|---|---|
| `+0` | `flags` = render class | 0: unlit; 1: monochrome lit (no corpus material); 2: RGB lit |
| `+0x2c` | colour 0: ambient | an optional outline pass only |
| `+0x32` | colour 1: diffuse | untextured faces only |
| `+0x38` | colour 2: specular | untextured faces only |
| `+0x3e` | colour 3: light colour | nothing in the renderer |
| `+0x44` | u32 shininess (0..100) | untextured specular table |
| `+0x48` | u32 shininess strength | untextured specular table |
| `+0x4c` | u32 transparency % | blending (`scene.md`, E-0482), not lighting |
| `+0x50` | u32 draw mode (1, 3: colour key; 2: additive) | drawer choice (`scene.md`), not lighting |
| `+0x58` | u32 tiling | 0: clamp texture coordinates, non-zero: wrap |

Corpus: 1,537 materials have class 2, 596 class 0, none class 1. Every class-0 material
is textured; the 104 untextured materials are class 2 (`DEFAULT`, mostly collision
meshes). Material colours do **not** enter the lighting of textured faces.

**Which lights reach an object.** Each object keeps a list of lights. `light=` in the
`.X3D` adds every light of the file to every object loaded so far (and their children);
an `.O3D` object's own light-index list adds more (empty in U01). A LOD stand-in uses the
lights and world matrix of the object it replaces (E-0142).

## Per-vertex colour (render class 2, E-0142)

For each drawn object, every frame, for each of its vertices i (for a welded object, its
own vertex range; animation.md):

- world position Vᵢ = vᵢ · W, world normal Nᵢ = nᵢ transformed by W without translation
  (the `.O3D` vertex normals; face normals are not used; renormalisation as in
  animation.md).
- start: D = (A.r, A.g, A.b), S = (0, 0, 0).
- for each light in the object's list with `hidden` = 0, omni case:
  - L = P − Vᵢ, d² = |L|², c = (L / |L|) · Nᵢ. Skip if c ≤ 0.
  - if `attenuate`: k = 1 if d² ≤ inner²; k = 1 − (d² − inner²) / (outer² − inner²) if
    inner² < d² < outer²; skip if d² ≥ outer². (Linear in the *squared* distance.)
    Otherwise k = 1.
  - D += C · (multiplier · k · c), per channel.
  - Shortcut (exact when the bounding sphere holds): with `attenuate`, the light is
    skipped for the whole object when |P − centre| ≥ outer + radius, where centre is the
    object's bounding-sphere centre in world space and radius its radius times the
    largest scale factor of W.
- spot case (unexercised): D̂ = normalise(P − T); a = D̂ · Nᵢ, skip if a ≤ 0;
  s = (L / |L|) · D̂; with cos_in = cos(θ/2), cos_out = cos(φ/2): skip if s ≤ cos_out;
  if s < cos_in, s ← s · (1 − (cos_in − s) / (cos_in − cos_out)). Then
  D += C · (multiplier · k · a · s), with k as for omni.
- clamp per channel: if D > 255, S = min(D − 255, 255) and D = 255; if D < 0, D = 0.

So brightness above 255 is not lost: it becomes a white-ish additive "specular" term.

Render class 1 (no corpus material) computes one grey value instead: start from
(A.r + A.g + A.b) / 3, add grey(C) · multiplier · k · c with grey(C) = (C.r + C.g + C.b) / 3
(integer), clamp to 0..255, no overflow term. How the renderer applies it is not
specified (no corpus material uses it).

## Drawing (E-0143)

- **Class 2, textured:** Gouraud-shaded triangle fan; vertex diffuse = (D.r, D.g, D.b)
  truncated to integers, alpha 0; vertex specular = S truncated; specular enabled.
  Pixel = texture · D / 255 + S, each channel saturated at 255. (The texture blend state
  is never set, so it is Direct3D's default modulate.)
  The specular term is part of the same pixel, so a colour-keyed texel (`scene.md`) is
  dropped with its specular: light never shows where the map is cut out (E-0626). An
  engine that adds S in a second pass must cut that pass by the same key and threshold.
- **Class 2, untextured:** diffuse = ⌊material.diffuse · D / 256⌋ per channel; specular
  per channel = T[⌊material.specular · D / 256⌋] with the material's table T:
  w = 128 − ⌊shininess · 120 / 100⌋, t₀ = 256 − w, step = ⌊strength · 256 / (w · 100)⌋,
  T[i] = 0 for i < t₀, else ⌊material.specular · step · (i − t₀) / 256⌋.
- **Class 0 (self-illuminated):** vertex colour 0x00FFFFFF (white, alpha 0), flat
  shading, no specular: the texture is drawn as stored. This is why the state-3 drawer
  writes 0x00FFFFFF: it is the class-0 drawer, not a colour-key rule.
- Texture addressing: material `+0x58` = 0 clamps U and V, non-zero wraps.
- Fog is never enabled.

## When

Every frame, for every object that survives culling. X3D has a per-object cache (lit
colours stored as bytes and reused), but the flag that enables it is never set by
`x3d.dll` or `xd3d.dll` (E-0144), so nothing is cached. An engine may cache results for
objects whose world matrix and lights did not change: the output is the same.

## U01 (E-0145)

Ambient (255, 255, 255). Five omni lights, all `attenuate`: Omni01, 02, 03, 05 have
multiplier −1 (grey, darkening within 120..164 units), Omni04 has +1 and colour
(196, 140, 52) (inner 104.8, outer 125.2), which, where no darkening light
overlaps it, only adds to S (an orange glow) because D is already saturated. Everything farther than `outer` from every light draws
at exactly texture colour.
