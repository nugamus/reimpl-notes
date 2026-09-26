meta:
  id: game
  title: Mission Sunlight game save (SAVE\GAMEppss.BIN)
  file-extension: bin
  endian: le
doc: |
  pp = player index, ss = slot = id of the object just used (00..34). Written by
  Save_WriteGame 0x40ff77, read by Load3DGame 0x42ef0f (E-0419, E-0421, E-0422). No file in
  the corpus, no validator (E-0432). Spec: engines/peintre/docs/spec/save.md.
seq:
  - id: state_3d
    type: state_3d
    size: 0x36c
  - id: state_2d
    type: state_2d
    size: 0x100
types:
  state_3d:
    doc: Image of the 3D state at 0x4aba40; only the fields the save glue touches are named.
    seq:
      - id: view_size
        type: u1
      - id: unk_01
        size: 7
      - id: left_zone0_a
        type: u4
        doc: set to 1 when leaving zone 0
      - id: left_zone0_b
        type: u4
        doc: set to 1 when leaving zone 0
      - id: unk_10
        size: 0xc
      - id: end_running
        type: u4
        doc: 1 after leaving zone 21
      - id: unk_20
        size: 4
      - id: unk_24
        type: s4
        repeat: expr
        repeat-expr: 3
        doc: the 3D's three s16 at 0x651346
      - id: unk_30
        type: s4
        repeat: expr
        repeat-expr: 3
        doc: the 3D's three s16 at 0x651352
      - id: unk_3c
        type: u1
        doc: 3D byte 0x4e3144 (Q-0251)
      - id: unk_3d
        type: u1
        doc: 3D byte 0x4e3140
      - id: zone
        type: u1
        doc: 2D zone the game resumes in
      - id: unk_3f
        size: 1
      - id: held
        type: u4
        repeat: expr
        repeat-expr: 35
        doc: object held flags (inventory)
      - id: zone_solved
        type: u4
        repeat: expr
        repeat-expr: 25
      - id: unk_130
        size: 0x64
      - id: sunflowers
        type: u1
        doc: counter of the last zone's chapter
      - id: unk_195
        size: 0xb
      - id: unk_1a0
        type: u4
      - id: unk_1a4
        type: u4
      - id: unk_1a8
        size: 0x1c4
  state_2d:
    seq:
      - id: zone_done
        type: u4
        repeat: expr
        repeat-expr: 25
      - id: object_placed
        type: u4
        repeat: expr
        repeat-expr: 35
      - id: counters
        type: u4
        repeat: expr
        repeat-expr: 4
        doc: sunflower counters by the zone table's counter field
