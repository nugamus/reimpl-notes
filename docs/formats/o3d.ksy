meta:
  id: x3d_o3d
  title: X3D object/scene geometry (.O3D), 4X Technologies
  file-extension: o3d
  endian: le
  encoding: latin1

doc: |
  Geometry container for the X3D engine, as loaded by `X3d_Load_Sdk_o3d`
  (`x3d.dll` `0x10001302`).

  The loader has no fixed-offset records. It reads through four stream primitives —
  `FUN_1000ba90` (u32), `FUN_1000baf0` (u8), `FUN_1000bb20` (f32) and `FUN_1000bb50`
  (n bytes) — each of which advances a cursor, so read order *is* the layout and record
  sizes vary with the flags and counts inside them.

  Validated by `tools/parsers/o3d.py` against all 596 `.O3D` files in the corpus: every
  file parses, every byte is consumed, and no index falls out of range. Totals: 2,133
  materials, 13,950 objects, 130,797 faces, 140,129 vertices, 14,700,676 bytes.

  Fields named "unknown" are opaque on purpose (CLAUDE.md rule 5). They are read and
  their width is proven; their meaning is not, and no name is guessed at.

seq:
  - id: signature
    type: strz
    size: 32
    doc: |
      Compared with `strcmp` against `(c) 1998 4X Tech. 0.95 (O)` and
      `(c) 1998 4X Tech. 1.00 (O)`. Only the bytes up to the NUL matter; the remainder of
      the 32-byte field is uninitialised writer memory and differs between files, which is
      why byte 28 takes 41 distinct values across the corpus. All 596 corpus files are
      0.95.
  - id: num_materials
    type: u4
  - id: materials
    type: material
    repeat: expr
    repeat-expr: num_materials
  - id: num_objects
    type: u4
  - id: objects
    type: object
    repeat: expr
    repeat-expr: num_objects

instances:
  version_1_00:
    value: "signature == '(c) 1998 4X Tech. 1.00 (O)'"
    doc: |
      Selects the loader's global at `x3d.dll` `DAT_1002d224`. Under 1.00, `FUN_10012920`
      reads a LOD block after each object — a u32 count, then that many full object
      records each followed by an f32 switch distance. No 1.00 file exists in the corpus,
      so that block is described here but deliberately not implemented in the validator.

types:
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

  uv_pair:
    seq:
      - id: u
        type: f4
      - id: v
        type: f4

  map_ref:
    doc: |
      Passed to `X3d_Map_Create` / `X3d_Map_Init` / `X3d_Scene_Add_Map`. Every map name in
      the corpus ends `.TGA` (1,476 of them) although the corpus ships no `.TGA` file —
      see Q-0011.
    seq:
      - id: name
        type: strz
        size: 32
      - id: flags
        type: u4

  material:
    doc: |
      `FUN_10011450`. The loader folds each RGB triple through `X3d_Rgb_To_16` into a
      16-bit colour it caches alongside; which triple is ambient, diffuse, specular or
      emissive is not established.
    seq:
      - id: name
        type: strz
        size: 32
      - id: flags
        type: u4
      - id: colors
        type: rgb
        repeat: expr
        repeat-expr: 4
      - id: unknown
        type: u4
        repeat: expr
        repeat-expr: 5
      - id: has_texture_map
        type: u4
      - id: texture_map
        type: map_ref
        if: has_texture_map != 0
      - id: has_light_map
        type: u4
      - id: light_map
        type: map_ref
        if: has_light_map != 0

  face:
    doc: '`FUN_10011ea0`, body of the per-face loop.'
    seq:
      - id: num_vertices
        type: u4
      - id: indices
        type: u4
        repeat: expr
        repeat-expr: num_vertices
        doc: Indexes the owning object's vertex array; see `object`.
      - id: has_uv
        type: u4
      - id: uv
        type: uv_pair
        repeat: expr
        repeat-expr: num_vertices
        if: has_uv != 0
      - id: material
        type: u4
        doc: Index into the file's material array; passed to `X3d_Face_Set_Material`.
      - id: normal
        type: vec3

  object:
    doc: |
      `FUN_10011ea0`. When `vertex_flag` is set the vertex array lives in a shared
      structure rather than this object's own, and `vertex_count_b` is the count that
      applies. In the corpus that count is frequently 0: 5,193 objects have no vertices of
      their own yet carry faces, and every one of them names a parent whose vertices its
      faces index. The validator resolves indices up the parent chain.
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
      - id: vertex_unknown
        type: u4
        if: vertex_flag != 0
      - id: vertex_count_b
        type: u4
        if: vertex_flag != 0
      - id: positions
        type: vec3
        repeat: expr
        repeat-expr: vertex_count
      - id: normals
        type: vec3
        repeat: expr
        repeat-expr: vertex_count
      - id: num_faces
        type: u4
      - id: faces
        type: face
        repeat: expr
        repeat-expr: num_faces
      - id: bounds
        type: f4
        repeat: expr
        repeat-expr: 10
        doc: Fanned out by the loader into a cached bounding box.
      - id: num_lights
        type: u4
      - id: lights
        type: u4
        repeat: expr
        repeat-expr: num_lights
        doc: Scene light indices; each is passed to `X3d_Light_Include_Object`.
      - id: unknown
        type: u4
      - id: position
        type: vec3
      - id: scale
        type: vec3
      - id: rotation
        type: vec3
      - id: matrix
        type: f4
        repeat: expr
        repeat-expr: 16
        doc: 4x4, copied to the object's live transform by `X3d_Matrice_Copy`.
    instances:
      vertex_count:
        value: "vertex_flag != 0 ? vertex_count_b : vertex_count_a"
