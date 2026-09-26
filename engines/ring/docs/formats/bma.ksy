meta:
  id: ring_bma
  title: Ring engine packed 16-bit image (loose .bma, .bmp members of .at2)
  file-extension: [bma]
  endian: le
doc: |
  Read by aImageFileBma::Init/ReadImage (RING_DVD.EXE 0x42ba40/0x42bbf0, header copy
  0x42bb90). Two packed bit streams (see README "Packed bit stream"): a table of
  core_count entries of 3 RGB555 pixels, and width*height*2//3//2 indices into it; each
  index emits its 3 pixels, rows bottom-up; last_pixels overwrite the final 3 pixels.
  Evidence: EVIDENCE.md E-0017. Validator: engines/ring/tools/parsers/bma.py.
seq:
  - id: seq_size
    type: u4
  - id: core_count
    type: u2
  - id: pixels_per_entry
    type: u2
    doc: 3 in every file
  - id: width
    type: u4
  - id: height
    type: u4
  - id: last_pixels
    type: u2
    repeat: expr
    repeat-expr: 3
  - id: unk_bmp_header
    size: 54
    doc: a 24-bit Windows BMP header ("BM"); the loader does not read it
  - id: seq_stream
    size: seq_size
    doc: bit stream, literals of bit_length(core_count) bits, 6-bit cache indices
  - id: core_size
    type: u4
  - id: core_stream
    size: core_size
    doc: bit stream, 16-bit literals, 6-bit cache indices
