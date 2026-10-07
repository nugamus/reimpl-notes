meta:
  id: china_tga
  title: China picture (*.TGA)
  file-extension: tga
  endian: le
doc: |
  Plain uncompressed Truevision TGA, 16 or 24 bits. CHINE.EXE 0x416510 (MyTga.cpp) reads
  the 18-byte header, skips id_length bytes, reads width*height*2 (depth 16) or *3
  (depth 24) bytes, flips the rows when descriptor bit 5 is clear; the footer is never
  read. All 151 files: E-0103. Validator: engines/cryomni3d/tools/parsers/tga.py.
seq:
  - id: id_length
    contents: [0]
  - id: color_map_type
    contents: [0]
  - id: image_type
    contents: [2]
  - id: color_map_spec
    contents: [0, 0, 0, 0, 0]
  - id: x_origin
    contents: [0, 0]
  - id: y_origin
    contents: [0, 0]
  - id: width
    type: u2
  - id: height
    type: u2
  - id: depth
    type: u1
    valid:
      any-of: [16, 24]
    doc: 16 in 150 files, 24 in DATA/SPRITES/LOAD/FOND.TGA
  - id: descriptor
    type: u1
    doc: 0 (112 files) or 1 (39 files, all with the footer); bottom row first
  - id: pixels
    size: width * height * (depth / 8)
    doc: depth 16 X1R5G5B5 with bit 15 always 0; depth 24 B, G, R
  - id: footer
    type: footer
    if: not _io.eof
types:
  footer:
    doc: TGA 2.0 footer, 40 files
    seq:
      - id: extension_offset
        contents: [0, 0, 0, 0]
      - id: developer_offset
        contents: [0, 0, 0, 0]
      - id: signature
        contents: ["TRUEVISION-XFILE.", 0]
