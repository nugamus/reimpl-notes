meta:
  id: china_cfg
  title: China options file (CHINE/chine.cfg)
  endian: le
doc: |
  Read by Options::load 0x405870, written by Options::save 0x4059f0, field by field in
  this order; the options screen (Options::run 0x40e630) edits them. A missing file
  leaves the defaults of Options::setDefaults 0x4056c0. E-0207.
  Validator: engines/cryomni3d/tools/parsers/cfg.py.
seq:
  - id: speed
    type: u4
    enum: speed
    doc: Omni3D navigation speed; the view step divides by (5 - speed). Default 2.
  - id: subtitles
    type: u4
    doc: 1 = subtitles shown during dialogues. Default 1.
  - id: music
    type: u4
    doc: 1 = music on. Default 1.
  - id: save_auto
    type: u4
    doc: |
      1 = automatic saves (one per player emblem, written on every place change),
      0 = manual named saves. Stored inverted in memory (0x48f238 = save_auto == 0).
enums:
  speed:
    0: very_slow
    1: slow
    2: normal
    3: rapid
    4: very_rapid
