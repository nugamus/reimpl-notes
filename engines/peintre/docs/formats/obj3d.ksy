meta:
  id: obj3d
  title: Mission Sunlight 3D objects inside BFG entries (.3DC, .3DM, .3DA, .3DI)
  endian: le
doc: |
  The unpacked BFG entry (bfg.ksy) minus its 20-byte object header. Memory images: the
  loader relocates stored offsets into pointers (E-0013, E-0014). Validator:
  engines/peintre/tools/parsers/obj3d.py. Only the layout is described here; the
  meaning of fields is in docs/spec/scene.md as the code proves it.
types:
  scene_3dc:
    seq:
      - id: num_nodes
        type: u4
      - id: node_ofs
        type: u4
        repeat: expr
        repeat-expr: num_nodes
        doc: body-relative; [0] is the root; the list holds every node of the tree
      - id: num_materials
        type: u4
      - id: materials
        type: material
        repeat: expr
        repeat-expr: num_materials
      - id: tree
        size-eos: true
        doc: |
          nodes and their arrays; every pointer inside is a 1-based offset from the
          root node (0 = none)
  material:
    seq:
      - id: name
        type: strz
        size: 16
        encoding: ASCII
        doc: matched by name against face groups (0x4338d0)
      - id: texture
        type: strz
        size: 16
        encoding: ASCII
        doc: '<texture>.3DM' is loaded from the same BFG (0x434560); empty = none
      - id: unk_colour
        type: u2
        repeat: expr
        repeat-expr: 2
        doc: 0x3DEF twice on the DEFAULT material of each scene, else 0
      - id: unk_2
        size: 8
  node:
    doc: 0xDC bytes
    seq:
      - id: name
        type: strz
        size: 12
        encoding: ASCII
      - id: flags
        type: u4
        doc: bit 0 hidden (not drawn), bit 2 not drawn, 0x10/0x20 in the files
      - id: parent
        type: u4
      - id: child
        type: u4
      - id: sibling
        type: u4
      - id: position
        type: s4
        repeat: expr
        repeat-expr: 3
      - id: rotation
        type: s4
        repeat: expr
        repeat-expr: 9
        doc: 3x3, Q15 (0x8000 = 1)
      - id: unk_world_position
        type: s4
        repeat: expr
        repeat-expr: 3
        doc: recomputed every frame (0x44fec0)
      - id: unk_world_rotation
        type: s4
        repeat: expr
        repeat-expr: 9
        doc: recomputed every frame (parent world x local, 0x43b060)
      - id: num_vertices
        type: u4
      - id: vertices
        type: u4
        doc: vertex[num_vertices]
      - id: num_uvs
        type: u4
      - id: uvs
        type: u4
        doc: uv[num_uvs]
      - id: num_vertex_normals
        type: u4
      - id: vertex_normals
        type: u4
      - id: num_face_normals
        type: u4
      - id: face_normals
        type: u4
      - id: unk_9c
        type: u4
        doc: 0 in the corpus
      - id: unk_a0
        type: u4
        doc: pointer, 0 in the corpus
      - id: face_groups
        type: u4
        doc: linked list of face_group
      - id: vertex_groups
        type: u4
        doc: linked list of vertex_group
      - id: unk_ac
        size: 0x30
  vertex:
    doc: 40 bytes
    seq:
      - id: flags
        type: u4
        doc: 0 or 0x80
      - id: position
        type: s4
        repeat: expr
        repeat-expr: 3
      - id: unk_runtime
        size: 24
  uv:
    seq:
      - id: u
        type: s4
        doc: 16.16, texels (0..256)
      - id: v
        type: s4
  normal:
    seq:
      - id: xyz
        type: s4
        repeat: expr
        repeat-expr: 3
        doc: Q15
      - id: unk_3
        type: s4
  face_group:
    doc: 0x34 bytes, then its polys elsewhere
    seq:
      - id: next
        type: u4
      - id: type
        type: s4
        doc: corpus 3 (839), -6 (384), 1 (11), -4 (1); selects poly size and drawer (0x447c30)
      - id: unk_material
        type: u4
        doc: set at load to the material's slot (0x4338d0)
      - id: material_name
        type: strz
        size: 16
        encoding: ASCII
      - id: num_polys
        type: u4
      - id: polys
        type: u4
      - id: unk_24
        size: 8
      - id: poly_size
        type: u4
        doc: 0x38 for types -2, 1, 4, 0x11, 0x1B; else 0x44
      - id: unk_30
        type: u4
  poly_44:
    seq:
      - id: unk_0
        type: u4
      - id: unk_next
        type: u4
        doc: pointer or 0
      - id: corners
        type: corner
        repeat: expr
        repeat-expr: 3
      - id: face_normal
        type: u4
      - id: unk_30
        type: s4
      - id: uv
        type: u4
        repeat: expr
        repeat-expr: 3
      - id: unk_40
        type: u4
  poly_38:
    seq:
      - id: unk_0
        type: u4
      - id: unk_next
        type: u4
      - id: corners
        type: corner
        repeat: expr
        repeat-expr: 3
      - id: face_normal
        type: u4
      - id: unk_30
        type: s4
      - id: unk_34
        type: u4
  corner:
    seq:
      - id: vertex
        type: u4
      - id: vertex_normal
        type: u4
      - id: vertex_group_item
        type: u4
  vertex_group:
    doc: 0x18 bytes; items are 100 B (types 3, -4, -6 ...), 0x70, 0x58 or 0x3C B (type 1 ...)
    seq:
      - id: next
        type: u4
      - id: type
        type: s4
      - id: num_items
        type: u4
      - id: items
        type: u4
      - id: unk_runtime
        size: 8
  texture_3dm:
    seq:
      - id: shades
        type: u4
        repeat: expr
        repeat-expr: 8192
        doc: 32 levels x 256 colours; RGB565 in the high 16 bits; level 0 brightest
      - id: texels
        size-eos: true
        doc: 256 x 256 colour indices (Q-0003 for the 4 odd sizes)
  anim_3da:
    seq:
      - id: num_tracks
        type: u4
      - id: track_ofs
        type: u4
        repeat: expr
        repeat-expr: num_tracks
        doc: body-relative
  track:
    seq:
      - id: unk_length
        type: u4
      - id: num_rot
        type: u4
      - id: num_pos
        type: u4
      - id: rot_keys
        type: u4
        doc: body-relative; rot_key[num_rot]
      - id: pos_keys
        type: u4
  rot_key:
    seq:
      - id: time
        type: u4
      - id: quaternion
        type: s4
        repeat: expr
        repeat-expr: 4
        doc: Q15; (0, 0, 0, 0x8000) at rest
  pos_key:
    seq:
      - id: time
        type: u4
      - id: position
        type: s4
        repeat: expr
        repeat-expr: 3
  boxes_3di:
    seq:
      - id: num_vertices
        type: u4
      - id: vertices
        type: u4
        doc: 1-based from the body; 12-byte xyz
      - id: num_faces
        type: u4
      - id: faces
        type: u4
        doc: 0x60-byte records; words 0..3 and 17 are pointers
      - id: num_items
        type: u4
      - id: items
        type: u4
        doc: 12-byte records
      - id: unk_18
        type: u4
        doc: leftover memory
