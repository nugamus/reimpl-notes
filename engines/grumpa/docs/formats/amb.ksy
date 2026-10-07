meta:
  id: grumpa_amb
  title: Grumpa .amb mesh vertex set
  file-extension: amb
  endian: le
doc: |
  CFXAMeshEx::CreateFromFile (FUN_00416a90, decrypted Grumpa.exe; E-0003, E-0013).
  u32 count, then count x (pos[3], normal stored z, y, x). A few files are 4-byte stubs
  (count with no data) that the game tolerates. Validator: engines/grumpa/tools/parsers/amb.py.
seq:
  - id: count
    type: u4
  - id: vertices
    type: vertex
    repeat: expr
    repeat-expr: '_io.size == 4 ? 0 : count'
types:
  vertex:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4
      - id: normal_z
        type: f4
      - id: normal_y
        type: f4
      - id: normal_x
        type: f4
