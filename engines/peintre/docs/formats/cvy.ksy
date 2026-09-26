meta:
  id: cvy
  title: Mission Sunlight movie mask (Data/MOVIES/*.CVY)
  file-extension: cvy
  endian: le
doc: |
  Read whole by Hnm_Open (0x40ba64) when the movie table entry (0x4a7a08) has has_cvy;
  frame n is HLZ-unpacked (Cvy_UnpackFrame 0x40c759 -> 0x430700) into a buffer_size
  buffer and painted over the movie frame by Blit_CvyMask (0x46ff0d). E-0204, E-0205.
  Validator: engines/peintre/tools/parsers/cvy.py.
seq:
  - id: frame_count
    type: u4
  - id: buffer_size
    type: u4
  - id: offsets
    type: u4
    repeat: expr
    repeat-expr: frame_count
    doc: from the end of this table, multiples of 4
  - id: data
    size-eos: true
    doc: HLZ streams, each padded to 4 bytes with leftover memory
types:
  mask_line:
    doc: |
      Unpacked frame = these records until the rectangle's height is covered; units are
      u32 (two pixels) on a 640-pixel line, from the rectangle's origin.
    seq:
      - id: head
        type: u1
        doc: 1..0x7F skip that many lines; 0 repeat the previous line; 0x80 | n = n runs
      - id: runs
        type: u1
        repeat: expr
        repeat-expr: 'head >= 0x80 ? head & 0x7f : 0'
        doc: 0x80 | k paint k+1 u32; k skip k+1 u32; a line adds up to 320
