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
        doc: "<texture>.3DM is loaded from the same BFG (0x434560); empty = none"
      - id: colour
        type: u2
        doc: |
          RGB565 flat colour of untextured (type 1) face groups (0x4338d0, 0x43c780,
          E-0507); 0x3DEF on the DEFAULT material of each scene, else 0
      - id: unk_colour2
        type: u2
        doc: 0x3DEF on DEFAULT, else 0 (Q-0301)
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
        doc: |
          bit 0 hidden (subtree skipped, 0x435970/0x4359a0), bit 2 not processed,
          0x10 uses the parent's 0x80 vertices (E-0504), 0x80 never far-culled,
          0x400 camera; bits other than 0x1891 are recomputed every frame (0x44bb10)
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
      - id: world_position
        type: s4
        repeat: expr
        repeat-expr: 3
        doc: runtime, camera space (0x44fec0, E-0500, E-0501)
      - id: world_rotation
        type: s4
        repeat: expr
        repeat-expr: 9
        doc: runtime, camera space = parent world x local (0x43b060)
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
      - id: num_boxes
        type: u4
        doc: 0 in the corpus
      - id: boxes
        type: u4
        doc: 0x118-byte records whose 8 corners 0x4503b0 bounds; 0 in the corpus (E-0513)
      - id: face_groups
        type: u4
        doc: linked list of face_group
      - id: vertex_groups
        type: u4
        doc: linked list of vertex_group
      - id: unk_ac
        type: u4
        doc: 0 in the corpus (Q-0300)
      - id: bound_radius
        type: s4
        doc: bounding sphere radius (0x44bb10, E-0504)
      - id: bound_centre
        type: s4
        repeat: expr
        repeat-expr: 3
        doc: bounding sphere centre, node space
      - id: unk_c0
        type: u4
        doc: 40 in the corpus (Q-0300)
      - id: num_lights
        type: u4
        doc: 0 in the corpus and never set; the lighting code is idle (E-0508)
      - id: light_ids
        type: u1
        repeat: expr
        repeat-expr: 8
        doc: indices into the light table 0x68b1e0
      - id: brightness
        type: u4
        doc: |
          low byte b picks shade row 31 - b for every textured poly of the node; 15 in the
          corpus and set to 15 at load (0x435930), so row 16 (E-0508)
      - id: unk_d4
        type: u4
        doc: 0 in the corpus (Q-0300)
      - id: unk_d8
        type: u4
        doc: 0 in the corpus (Q-0300)
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
      - id: runtime
        size: 24
        doc: |
          per frame: camera-space x, y, z (f4), screen x, y (s4, truncated), 2^30 / z (f4)
          (0x44bd60, 0x44db30, E-0502); flags gain outcode bits 0x1..0x40 at runtime
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
      - id: runtime_dot
        type: s4
        doc: runtime; for face normals n . eye >> 15, compared with poly plane_distance (0x44c100)
  face_group:
    doc: 0x34 bytes, then its polys elsewhere
    seq:
      - id: next
        type: u4
      - id: type
        type: s4
        doc: corpus 3 (839), -6 (384), 1 (11), -4 (1); selects poly size and drawer (0x447c30)
      - id: material_slot
        type: u4
        doc: |
          runtime: pointer into the texture slot (0x4338d0): word 2 (texel pointer) for
          textured types, the material colour for type 1 (E-0507)
      - id: material_name
        type: strz
        size: 16
        encoding: ASCII
      - id: num_polys
        type: u4
      - id: polys
        type: u4
      - id: draw_list
        type: u4
        doc: runtime head of the polys to draw (0x44d980); 0 in the files
      - id: unk_28
        type: u4
        doc: Q-0301
      - id: poly_size
        type: u4
        doc: 0x38 for types -2, 1, 4, 0x11, 0x1B; else 0x44
      - id: unk_30
        type: u4
  poly_44:
    seq:
      - id: flags
        type: u4
        doc: |
          bit 3 (file): back-face test from camera-space corners instead of the plane
          (0x44d980, E-0505); bits 0/1 set at runtime when culled or replaced by clipping
      - id: next
        type: u4
        doc: next poly of the group (the following record, 0 on the last)
      - id: corners
        type: corner
        repeat: expr
        repeat-expr: 3
      - id: face_normal
        type: u4
      - id: plane_distance
        type: s4
        doc: (face_normal . corner 0 vertex) >> 15; front-facing when n . eye >> 15 >= this
      - id: uv
        type: u4
        repeat: expr
        repeat-expr: 3
      - id: shade
        type: u4
        doc: runtime brightness from lights (low byte, 0x44df60); 0 in the files, unused (E-0508)
  poly_38:
    seq:
      - id: flags
        type: u4
        doc: |
          bit 3 (file): back-face test from camera-space corners instead of the plane
          (0x44d980, E-0505); bits 0/1 set at runtime when culled or replaced by clipping
      - id: next
        type: u4
        doc: next poly of the group (the following record, 0 on the last)
      - id: corners
        type: corner
        repeat: expr
        repeat-expr: 3
      - id: face_normal
        type: u4
      - id: plane_distance
        type: s4
        doc: as in poly_44
      - id: shade
        type: u4
        doc: runtime brightness from lights (0x44df60, 0x43c780); 0 in the files (E-0508)
  corner:
    seq:
      - id: vertex
        type: u4
      - id: vertex_normal
        type: u4
      - id: vertex_group_item
        type: u4
  vertex_group:
    doc: |
      0x18 bytes; items are 100 B (types 3, -4, -6 ...), 0x70, 0x58 or 0x3C B (type 1 ...).
      The items are the group's edges, filled every frame by the edge builders (E-0506):
      words 7 and 8 point at the edge's two vertices; each poly corner points at the edge
      that starts there
    seq:
      - id: next
        type: u4
      - id: type
        type: s4
      - id: num_items
        type: u4
      - id: items
        type: u4
      - id: unk_10
        type: u4
      - id: cursor
        type: u4
        doc: runtime, reset to items every frame (0x44fec0)
  texture_3dm:
    seq:
      - id: shades
        type: u4
        repeat: expr
        repeat-expr: 8192
        doc: |
          32 levels x 256 colours; RGB565 in the high 16 bits; level 0 brightest; the game
          draws with level 16 only (E-0508)
      - id: texels
        size-eos: true
        doc: |
          colour indices, rows of 256; 256 rows except the 4 odd sizes, whose extra or
          missing rows the corpus UVs never reach (E-0509)
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
      - id: length
        type: u4
        doc: track 0's is the animation length in 66 ms ticks (0x437d90, E-0514); unread elsewhere
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
        doc: Q15 x, y, z, w (0x43b480, E-0514); (0, 0, 0, 0x8000) at rest
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
