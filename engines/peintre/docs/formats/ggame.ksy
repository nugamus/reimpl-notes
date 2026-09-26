meta:
  id: ggame
  title: Mission Sunlight resume file (SAVE\GGAMEp.BIN)
  file-extension: bin
  endian: le
  imports:
    - game
doc: |
  Written by Save_WriteGGame 0x410153, read by Load3DGGame 0x42f111 (E-0420). No file in
  the corpus, no validator (E-0432). Spec: engines/peintre/docs/spec/save.md.
seq:
  - id: in_2d
    type: u4
    doc: 1 = quit from a 2D zone, resume there after the intro; 0 = resume in 3D
  - id: state_3d
    type: game::state_3d
    size: 0x36c
  - id: state_2d
    type: game::state_2d
    size: 0x100
