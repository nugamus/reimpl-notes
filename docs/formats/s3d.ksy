meta:
  id: x3d_s3d
  title: X3D scene super-container (.S3D), 4X Technologies
  file-extension: s3d
  endian: le
  encoding: latin1

doc: |
  Scene super-container for the X3D engine, as loaded by `X3d_Load_Sdk_s3d` (`x3d.dll`
  `0x100010e1`). `S3D` does **not** introduce its own per-record shapes — it sequences
  the already-recovered per-format record readers against a single shared file cursor:

    1. cameras     (`.C3D` body, no signature)
    2. lights      (`.L3D` body, no signature)
    3. materials   (`.O3D` body, no signature)
    4. objects     (`.O3D` body, no signature)
    5. animations  (`.A3D` body, no signature)

  Each section starts with a u32 count, then that many records of the per-format shape.
  No per-section signature — the cursor advances straight from one section into the next.
  This is why the engine can write a scene out as a single `.S3D` instead of carrying
  five separate files; the on-disk shapes are byte-for-byte the same as the standalone
  formats.

  Validated by `tools/parsers/s3d.py` against the 1 `.S3D` file in the corpus: every
  byte is consumed. Totals: 0 cameras, 0 lights, 5 materials, 53 objects, 53 animations,
  73,916 bytes.

  The per-record field schemas live in `o3d.ksy`, `a3d.ksy`, `l3d.ksy` and `c3d.ksy` —
  this spec only describes the section sequence.

seq:
  - id: signature
    type: strz
    size: 32
    doc: |
      Compared with `strcmp` against `(c) 1998 4X Tech. 0.95 (S)` and
      `(c) 1998 4X Tech. 1.00 (S)`. Only the bytes up to the NUL matter; the remainder of
      the 32-byte field is uninitialised writer memory and differs between files. The 1
      corpus file is 0.95.
  - id: cameras
    type: camera_section
  - id: lights
    type: light_section
  - id: materials
    type: material_section
  - id: objects
    type: object_section
  - id: animations
    type: animation_section

instances:
  version_1_00:
    value: "signature == '(c) 1998 4X Tech. 1.00 (S)'"
    doc: |
      Selects the loader's global at `x3d.dll` `DAT_1002d224`. No 1.00 `.S3D` file exists
      in the corpus, so the 1.00 path is described here but never cross-validated.

types:
  camera_section:
    doc: |
      `.C3D` body shape (no leading signature). See `c3d.ksy` for the per-record fields.
    seq:
      - id: num_cameras
        type: u4
      - id: cameras
        type: camera
        repeat: expr
        repeat-expr: num_cameras

  camera:
    seq:
      - id: name
        type: strz
        size: 32
      - id: params
        size: 40
        type:
          seq:
            - id: f0
              type: f4
            - id: f1
              type: f4
            - id: f2
              type: f4
            - id: f3
              type: f4
            - id: f4
              type: f4
            - id: f5
              type: f4
            - id: f6
              type: f4
            - id: f7
              type: f4
            - id: f8
              type: f4
            - id: f9
              type: f4

  light_section:
    doc: |
      `.L3D` body shape (no leading signature). See `l3d.ksy` for the per-light fields.
    seq:
      - id: num_lights
        type: u4
      - id: lights
        type: light
        repeat: expr
        repeat-expr: num_lights

  light:
    seq:
      - id: name
        type: strz
        size: 32
      - id: position
        type: vec3
      - id: color
        type: rgb
      - id: extra_floats
        type: vec3
        doc: Opaque — see Q-0013.
      - id: extra_u32s
        size: 8
        type:
          seq:
            - id: a
              type: u4
            - id: b
              type: u4
      - id: is_spot
        type: u4
      - id: spot
        type: spot_light
        if: is_spot != 0

  spot_light:
    seq:
      - id: target
        type: vec3
      - id: angles
        size: 8
        type:
          seq:
            - id: theta
              type: f4
            - id: phi
              type: f4

  material_section:
    doc: |
      `.O3D` body shape (no leading signature). See `o3d.ksy` for the material record.
    seq:
      - id: num_materials
        type: u4
      - id: materials
        type: material
        repeat: expr
        repeat-expr: num_materials

  material:
    seq:
      - id: name
        type: strz
        size: 32
      - id: flags
        type: u4
      - id: colors
        size: 12
        type:
          seq:
            - id: c0
              size: 3
            - id: c1
              size: 3
            - id: c2
              size: 3
            - id: c3
              size: 3
      - id: unknown_u32s
        size: 20
        type:
          seq:
            - id: u0
              type: u4
            - id: u1
              type: u4
            - id: u2
              type: u4
            - id: u3
              type: u4
            - id: u4
              type: u4
      - id: has_texture
        type: u4
      - id: texture_map
        type: map_ref
        if: has_texture != 0
      - id: has_light_map
        type: u4
      - id: light_map
        type: map_ref
        if: has_light_map != 0

  map_ref:
    seq:
      - id: name
        type: strz
        size: 32
      - id: flags
        type: u4

  object_section:
    doc: |
      `.O3D` body shape (no leading signature). See `o3d.ksy` for the object record.
    seq:
      - id: num_objects
        type: u4
      - id: objects
        type: object
        repeat: expr
        repeat-expr: num_objects

  object:
    seq:
      - id: name
        type: strz
        size: 32
      - id: has_parent
        type: u4
      - id: parent
        type: strz
        size: 32
        if: has_parent != 0
      - id: vertex_count_a
        type: u4
      - id: vertex_flag
        type: u4
      - id: vertex_extra
        type: u4
        if: vertex_flag != 0
      - id: vertex_count
        type: u4
        if: vertex_flag != 0
      - id: positions
        type: vec3
        repeat: expr
        repeat-expr: vertex_flag != 0 ? vertex_count : vertex_count_a
      - id: normals
        type: vec3
        repeat: expr
        repeat-expr: vertex_flag != 0 ? vertex_count : vertex_count_a
      - id: num_faces
        type: u4
      - id: faces
        type: face
        repeat: expr
        repeat-expr: num_faces
      - id: bounds
        size: 40
        type:
          seq:
            - id: f0
              type: f4
            - id: f1
              type: f4
            - id: f2
              type: f4
            - id: f3
              type: f4
            - id: f4
              type: f4
            - id: f5
              type: f4
            - id: f6
              type: f4
            - id: f7
              type: f4
            - id: f8
              type: f4
            - id: f9
              type: f4
      - id: num_lights
        type: u4
      - id: lights
        type: u4
        repeat: expr
        repeat-expr: num_lights
      - id: unknown
        type: u4
      - id: position
        type: vec3
      - id: scale
        type: vec3
      - id: rotation
        type: vec3
      - id: matrix
        size: 64
        type:
          seq:
            - id: f0
              type: f4
            - id: f1
              type: f4
            - id: f2
              type: f4
            - id: f3
              type: f4
            - id: f4
              type: f4
            - id: f5
              type: f4
            - id: f6
              type: f4
            - id: f7
              type: f4
            - id: f8
              type: f4
            - id: f9
              type: f4
            - id: f10
              type: f4
            - id: f11
              type: f4
            - id: f12
              type: f4
            - id: f13
              type: f4
            - id: f14
              type: f4
            - id: f15
              type: f4

  face:
    seq:
      - id: vertex_count
        type: u4
      - id: indices
        type: u4
        repeat: expr
        repeat-expr: vertex_count
      - id: has_uv
        type: u4
      - id: uv
        size: 8
        type:
          seq:
            - id: u
              type: f4
            - id: v
              type: f4
        repeat: expr
        repeat-expr: has_uv != 0 ? vertex_count : 0
      - id: material
        type: u4
      - id: normal
        type: vec3

  animation_section:
    doc: |
      `.A3D` body shape (no leading signature). See `a3d.ksy` for the animation record.
    seq:
      - id: num_animations
        type: u4
      - id: animations
        type: animation
        repeat: expr
        repeat-expr: num_animations

  animation:
    seq:
      - id: name
        type: strz
        size: 32
      - id: has_parent
        type: u4
      - id: parent
        type: strz
        size: 32
        if: has_parent != 0
      - id: pivot
        type: vec3
      - id: unknown_u32s
        size: 12
        type:
          seq:
            - id: u0
              type: u4
            - id: u1
              type: u4
            - id: u2
              type: u4
      - id: track_a
        type: track_v
      - id: track_b
        type: track_v
      - id: track_c
        type: track_v
      - id: track_d
        type: track_d
      - id: track_e
        type: track_e

  track_v:
    seq:
      - id: count
        type: u4
      - id: unknown
        type: u4
      - id: frames
        type: u4
        repeat: expr
        repeat-expr: count
      - id: keys
        size: 20
        type:
          seq:
            - id: k0
              type: f4
            - id: k1
              type: f4
            - id: k2
              type: f4
            - id: k3
              type: f4
            - id: k4
              type: f4
        repeat: expr
        repeat-expr: count
      - id: values
        size: 12
        type:
          seq:
            - id: v0
              type: f4
            - id: v1
              type: f4
            - id: v2
              type: f4
        repeat: expr
        repeat-expr: count

  track_d:
    seq:
      - id: count
        type: u4
      - id: unknown
        type: u4
      - id: frames
        type: u4
        repeat: expr
        repeat-expr: count
      - id: keys
        size: 8
        type:
          seq:
            - id: a
              type: u4
            - id: b
              type: u4
        repeat: expr
        repeat-expr: count

  track_e:
    seq:
      - id: count
        type: u4
      - id: unknown
        type: u4
      - id: frames
        type: u4
        repeat: expr
        repeat-expr: count
      - id: keys
        size: 20
        type:
          seq:
            - id: k0
              type: f4
            - id: k1
              type: f4
            - id: k2
              type: f4
            - id: k3
              type: f4
            - id: k4
              type: f4
        repeat: expr
        repeat-expr: count
      - id: inner_count
        type: u4
        if: count != 0
      - id: positions
        type: vec3
        repeat: expr
        repeat-expr: count != 0 ? count * inner_count : 0
      - id: normals
        type: vec3
        repeat: expr
        repeat-expr: count != 0 ? count * inner_count : 0
      - id: tail
        size: 28
        type:
          seq:
            - id: f0
              type: f4
            - id: f1
              type: f4
            - id: f2
              type: f4
            - id: f3
              type: f4
            - id: f4
              type: f4
            - id: f5
              type: f4
            - id: f6
              type: f4
        if: count != 0

  vec3:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4

  rgb:
    seq:
      - id: r
        type: u1
      - id: g
        type: u1
      - id: b
        type: u1