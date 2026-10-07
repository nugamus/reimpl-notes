meta:
  id: grumpa_anb
  title: Grumpa .anb animated mesh
  file-extension: anb
  endian: le
doc: |
  CFXAMeshEx, FUN_004157d0 in the decrypted Grumpa.exe (E-0003, E-0014, E-0600). Frame 0
  geometry per section, then frames 1..F-1 (every section's vertices, sum(vert_count)*24
  bytes per frame), then a tail the loader never reads (one stored frame more in 521 files,
  4,456 bytes in 012_D2D_Grumpa_In_Boat.ANB). Kaitai cannot sum the section vertex counts,
  so frames and tail stay one opaque blob (anim_and_tail); anb.py splits them.
  Validator: engines/grumpa/tools/parsers/anb.py (939/939).
seq:
  - id: frame_count
    type: u4
  - id: section_count
    type: u4
  - id: sections
    type: section
    repeat: expr
    repeat-expr: section_count
  - id: anim_and_tail
    size-eos: true
    doc: (frame_count - 1) frames of sum(vert_count) * 24 bytes (pos[3f] + normal[3f]), then the unread tail
types:
  section:
    seq:
      - id: vert_count
        type: u4
      - id: uv_count
        type: u4
      - id: face_count
        type: u4
      - id: vertices
        type: vertex
        repeat: expr
        repeat-expr: vert_count
      - id: faces
        type: tri
        repeat: expr
        repeat-expr: face_count
        doc: vertex index triples
      - id: uvs
        type: uv
        repeat: expr
        repeat-expr: uv_count
      - id: face_uvs
        type: tri
        repeat: expr
        repeat-expr: face_count
        doc: uv index triples
  vertex:
    seq:
      - id: pos
        type: f4
        repeat: expr
        repeat-expr: 3
      - id: normal
        type: f4
        repeat: expr
        repeat-expr: 3
  tri:
    seq:
      - id: idx
        type: u2
        repeat: expr
        repeat-expr: 3
  uv:
    seq:
      - id: u
        type: f4
      - id: v
        type: f4
