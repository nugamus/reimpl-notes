meta:
  id: ring_aqc
  title: Ring engine panorama node (.aqc)
  file-extension: aqc
  endian: le
doc: |
  One rotation (panorama) node: the full panorama as an index stream into a colour table,
  then sections of layer patches (single images or animation frames) as index streams
  over rectangles. Read by aSecComAqi::DecompressNode / DecompressChannel (RING_DVD.EXE
  0x429be0 / 0x429dc0) from CAquatorStream::InitFull (0x4111d0), which reads as many
  sections as the rotation has layers. Streams: README "Packed bit stream" (13-bit
  literals for indices, 16-bit for the table; index width 6). The table holds 32,400
  RGB565 values (converted to the display layout by 0x410ff0). Evidence: EVIDENCE.md
  E-0020. Validator: engines/ring/tools/parsers/aqc.py.
seq:
  - id: index_size
    type: u4
  - id: node
    type: header
  - id: index_stream
    size: index_size
    doc: data_size/8 13-bit indices (one per 4 pixels)
  - id: table_size
    type: u4
  - id: table_stream
    size: table_size
    doc: 16-bit values; 32,400 in every file
  - id: sections
    type: section
    repeat: eos
types:
  header:
    seq:
      - id: width
        type: u4
      - id: height
        type: u4
      - id: bytes_per_pixel
        type: u4
        doc: 2
      - id: unk_3
        type: s4
        doc: 0 in every header
      - id: unk_4
        type: f4
        doc: 360.0 in every header
      - id: unk_5
        type: f4
        doc: -60.0 (2048x688) or -75.0 (2048x856)
      - id: unk_6
        type: f4
        doc: 60.0 or 75.0
      - id: x0
        type: u4
      - id: x1
        type: u4
      - id: y0
        type: u4
      - id: y1
        type: u4
      - id: data_size
        type: u4
        doc: (x1-x0)*(y1-y0)*2
      - id: stride
        type: u4
        doc: (x1-x0)*2
  section:
    seq:
      - id: count
        type: u4
      - id: unk_a
        type: u4
        doc: 0 when count is 1 and static; else 0x41400000 (12.0 as f32)
      - id: unk_b
        type: u4
        doc: 0, or count - 1 when unk_a is set
      - id: entries
        type: entry
        repeat: expr
        repeat-expr: count
  entry:
    seq:
      - id: size
        type: u4
      - id: header
        type: header
      - id: index_stream
        size: size
