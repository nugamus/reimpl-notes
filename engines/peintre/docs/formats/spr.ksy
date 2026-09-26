meta:
  id: spr
  title: Mission Sunlight sprite bank (Data/SPRITES/*.SPR)
  file-extension: spr
  endian: le
doc: |
  Loaded by Sprite_LoadFile (0x40a766), drawn by Sprite_Draw (0x409d76) and
  Sprite_DrawClipped (0x409e44) through the Cryo sprite blitters (0x4703be..0x470793,
  0x46fb4b). The bank kind comes from the two top bits of `head` and the presence of a
  palette (E-0102, E-0103). Validator: engines/peintre/tools/parsers/spr.py.
seq:
  - id: head
    type: u4
    doc: |
      bit 31 = raw frames; bit 30 = band frames (only when bit 31 is clear);
      bits 0..29 = palette_end, the file offset of the bank
  - id: palette
    type: rgb
    repeat: expr
    repeat-expr: (palette_end - 4) / 3
    doc: 256 entries or none; converted to RGB565 (or 555) by dropping low bits
  - id: bank
    type: bank
    size-eos: true
instances:
  palette_end:
    value: head & 0x3fffffff
  is_raw:
    value: (head >> 31) != 0
  is_band:
    value: (head >> 31) == 0 and ((head >> 30) & 1) != 0
types:
  rgb:
    seq:
      - id: r
        type: u1
      - id: g
        type: u1
      - id: b
        type: u1
  bank:
    doc: |
      offsets are relative to the start of the bank; frame i (type `frame`) runs from
      offsets[i] to offsets[i+1], the last one to the end of the bank
    seq:
      - id: first_offset
        type: u4
        doc: offsets[0]; the frame count is first_offset / 4
      - id: more_offsets
        type: u4
        repeat: expr
        repeat-expr: first_offset / 4 - 1
  frame:
    doc: |
      u16 a, u16 b, data, then 0..3 zero bytes to a multiple of 4.
      rle   (bits 00): a = width, b = height; b rows of RLE; drawn at (x - a/2, y - b/2)
      band  (bits 01): a = first screen row, b = row count; b rows of RLE across the
                       640-pixel screen from x = 0; a = b = 0 is an empty frame
      raw8  (bit 1, palette): a = width, b = height; a*b palette indices; drawn at (x, y)
      raw16 (bit 1, no palette): a = width, b = height; a*b RGB565 u16; drawn at (x, y)
      RLE row: c = 0x80 ends the row; c < 0x80 skips c transparent pixels;
      c > 0x80 is followed by c & 0x7f palette indices.
    seq:
      - id: a
        type: u2
      - id: b
        type: u2
      - id: data
        size-eos: true
