meta:
  id: grumpa_scn
  title: Grumpa .scn scene (walk mesh, scene links, view list)
  file-extension: scn
  endian: le
doc: |
  LoadScene (FUN_0040cb30) reads Scenes/Scene_%03d.scn with CreateFromABIFile (FUN_0040cef0):
  records of u32 type, u32 id, body, to EOF (E-0500). Three records occur once each, ids
  600/601/602: 0x08 walk mesh (FUN_00432880), 0x14 CFXToScene links (FUN_00447cd0),
  0x09 view list (FUN_0045a750). Validator: engines/grumpa/tools/parsers/scn.py (110/110).
seq:
  - id: records
    type: record
    repeat: eos
types:
  record:
    seq:
      - id: type
        type: u4
      - id: id
        type: u4
      - id: body
        type:
          switch-on: type
          cases:
            0x08: walk_mesh
            0x14: scene_links
            0x09: view_list
  walk_mesh:
    seq:
      - id: vertex_count
        type: u2
      - id: face_count
        type: u2
      - id: vertices
        type: mesh_vertex
        repeat: expr
        repeat-expr: vertex_count
      - id: faces
        type: tri
        repeat: expr
        repeat-expr: face_count
        doc: vertex index triples
      - id: unk_face
        type: u2
        repeat: expr
        repeat-expr: face_count
  mesh_vertex:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4
      - id: unk
        type: f4
        repeat: expr
        repeat-expr: 5
  tri:
    seq:
      - id: idx
        type: u2
        repeat: expr
        repeat-expr: 3
  scene_links:
    seq:
      - id: param_count
        type: u4
      - id: params
        type: u4
        repeat: expr
        repeat-expr: param_count
        doc: parameters (State, Scene_ID)
      - id: exit_count
        type: u4
      - id: exits
        type: exit
        repeat: expr
        repeat-expr: exit_count
      - id: entry_count
        type: u4
      - id: entries
        type: entry
        repeat: expr
        repeat-expr: entry_count
  exit:
    doc: FUN_0045a370 over FUN_0044c750
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4
      - id: radius
        type: f4
      - id: scene
        type: u4
  entry:
    doc: FUN_0045a2a0 over FUN_00401c00
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4
      - id: rx
        type: f4
      - id: ry
        type: f4
      - id: rz
        type: f4
      - id: scene
        type: u4
  view_list:
    seq:
      - id: view_count
        type: u4
      - id: views
        type: view
        repeat: expr
        repeat-expr: view_count
      - id: unk_m1
        size: 64
        repeat: expr
        repeat-expr: view_count
        doc: 4x4 f32 each
      - id: unk_m2
        size: 64
        repeat: expr
        repeat-expr: view_count
        doc: 4x4 f32 each
  view:
    seq:
      - id: color
        type: pstr
        doc: .jpg
      - id: depth
        type: pstr
        doc: .fxi
  pstr:
    seq:
      - id: len
        type: u4
        doc: length including the NUL
      - id: text
        type: str
        size: len
        encoding: latin1
