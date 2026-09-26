meta:
  id: bfg
  title: Mission Sunlight scene bundle (Data/Scenes_3D/*.BFG)
  file-extension: bfg
  endian: le
doc: |
  Read whole into memory by LoadSceneFile (0x42e85c); entries are looked up by name
  (0x42e67f, strcmp over `count` slots) and unpacked by the Cryo LZ routine 0x466bc3
  (E-0013). Validator: engines/peintre/tools/parsers/bfg.py.
seq:
  - id: count
    type: u4
    doc: used directory slots (1..100)
  - id: slots
    type: slot
    repeat: expr
    repeat-expr: 100
    doc: only the first `count` are read; the rest hold leftover memory in some files
  - id: pad
    size: 4
    doc: zero in all 15 files
  - id: data
    size-eos: true
    doc: entries back to back from 0xE18, in directory order
types:
  slot:
    seq:
      - id: name
        type: strz
        size: 28
        encoding: ASCII
        doc: bytes after the NUL are leftover memory
      - id: offset
        type: u4
        doc: from 0xE18
      - id: size
        type: u4
  packed_entry:
    doc: |
      method 1 = stored; anything else = LZ: u16 flag word (LSB first) per 16 items;
      flag 0 = literal byte; flag 1 = b0 b1, copy (b0 & 15) + 1 bytes from distance
      ((b0 & 0xF0) << 4) + b1. The stream ends exactly at the entry's end.
    seq:
      - id: method
        type: u1
      - id: unk_1
        size: 3
      - id: payload
        size-eos: true
  object_header:
    doc: first 20 bytes of every unpacked entry; the engine overwrites all but `type`
    seq:
      - id: unk_handle
        type: u4
      - id: unk_size
        type: u4
      - id: type
        type: u4
        enum: object_type
      - id: unk_prev
        type: u4
      - id: unk_next
        type: u4
enums:
  object_type:
    1: scene_3dc
    3: texture_3dm
    4: anim_3da
    5: boxes_3di
