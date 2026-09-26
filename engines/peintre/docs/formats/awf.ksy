meta:
  id: awf
  title: Mission Sunlight bitmap font (Data/FONTS/*.AWF)
  file-extension: awf
  endian: le
doc: |
  Font_LoadAwf (0x40acde) reads the 38-byte header into a font record and the rest into
  one block, turning the five offsets into pointers; the Cryo text routines 0x46ff9e
  (draw), 0x470110 (draw with shadow) and 0x47029e (measure) use it (E-0105).
  Validator: engines/peintre/tools/parsers/awf.py.
seq:
  - id: unk_0
    type: u4
    doc: 0 in both files; never read
  - id: unk_data_ptr
    type: u4
    doc: 0 in both files; the loader stores the data block pointer here
  - id: glyphs_ofs
    type: u4
    doc: start of the glyph bitmaps in data (= 4 * count)
  - id: glyph_table_ofs
    type: u4
    doc: 0 in both files
  - id: widths_ofs
    type: u4
    doc: 0 in the fixed-width font
  - id: spacing_a_ofs
    type: u4
  - id: spacing_b_ofs
    type: u4
  - id: first_char
    type: u1
  - id: count
    type: u1
  - id: baseline
    type: u1
    doc: rows above the pen; glyphs are drawn from y - baseline
  - id: unk_1f
    type: u1
    doc: 0 in both files; never read
  - id: flags
    type: u2
    doc: bit 0 = proportional
  - id: fixed_width
    type: u2
  - id: height
    type: u2
  - id: data
    size-eos: true
    type: font_data
types:
  font_data:
    doc: |
      u32 glyph_table[count] at glyph_table_ofs (offsets from glyphs_ofs), glyph bitmaps
      (height rows of ceil(w / 8) bytes, MSB = leftmost pixel, 1 = ink, w = widths[i] or
      fixed_width), then u8 widths[count], u8 spacing_a[count], s1 spacing_b[count] when
      proportional. Advance = fixed_width, or widths[i] + spacing_a[i] + spacing_b[i].
    seq:
      - id: raw
        size-eos: true
