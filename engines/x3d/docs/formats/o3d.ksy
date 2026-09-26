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

  Validated by `engines/x3d/tools/parsers/o3d.py` against all 596 `.O3D` files in the corpus: every
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
      16-bit colour it caches alongside. Material slots and their use in lighting:
      E-0141, `engines/x3d/docs/spec/lighting.md`. `flags` is the render class (0 unlit,
      1 grey-lit, 2 RGB-lit); colours are ambient, diffuse, specular, light colour
      (`+0x2c`, `+0x32`, `+0x38`, `+0x3e`); the five u32s are shininess, shininess
      strength, transparency %, draw mode, tiling (`+0x44`, `+0x48`, `+0x4c`, `+0x50`,
      `+0x58`).
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
      `FUN_10011ea0`. A welded object (`welded` set, E-0054) belongs to a hierarchy whose
      top object holds one shared vertex array of `weld_vertex_count` vertices; every
      other welded object has `weld_vertex_count` 0 and uses the top's array. Each
      welded object transforms the vertices `weld_first_vertex` ..
      `weld_first_vertex + own_vertex_count - 1` of that array with its own world
      matrix, and faces index the whole array. The validator checks that these ranges
      partition the array (139 hierarchies, 5,613 welded objects).
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
      - id: own_vertex_count
        type: u4
        doc: Object `+0x44`, the number of vertices this object transforms.
      - id: welded
        type: u4
        doc: Object `+0x40`.
      - id: weld_first_vertex
        type: u4
        if: welded != 0
        doc: Object `+0x48`, first vertex of this object's range in the shared array.
      - id: weld_vertex_count
        type: u4
        if: welded != 0
        doc: Transform block `+0`, `X3d_Object_Get_Number_Weld`; size of the array here.
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
      - id: pivot
        type: vec3
        doc: Transform block `+0x14` (`X3d_Object_Get_Init_Pivot_Position`, E-0042).
      - id: local_position
        type: vec3
        doc: '`+0x44` (`X3d_Object_Get_Local_Init_Position`), relative to the parent''s pivot.'
      - id: local_scale
        type: vec3
        doc: '`+0x64` (`X3d_Object_Get_Local_Init_Scale`).'
      - id: matrix
        type: f4
        repeat: expr
        repeat-expr: 16
        doc: |
          4x4 row-vector matrix (translation in elements 12..14), copied to the object's
          live transform by `X3d_Matrice_Copy`. World matrix: E-0042.
    instances:
      vertex_count:
        value: "welded != 0 ? weld_vertex_count : own_vertex_count"
