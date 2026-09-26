meta:
  id: tga
  title: Mission Sunlight 2D overlay image (Data/Graphs_2D/*.TGA)
  file-extension: tga
  endian: le
doc: |
  Plain uncompressed 16-bit Truevision TGA, the only variant in the corpus (104 files).
  LoadTga (0x41ad98) / LoadTga2 (0x41af1c) read width and height at 12 and the pixels
  from 18, flip the rows (0x41acfa) and convert 555 to 565 on 565 screens (0x41aae0);
  every other field is ignored (E-0104). Validator: engines/peintre/tools/parsers/tga.py.
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
    contents: [16]
  - id: descriptor
    type: u1
    doc: 0 (93 files) or 1 (11 files, the ones with the footer); never read
  - id: pixels
    size: width * height * 2
    doc: X1R5G5B5, bottom row first, bit 15 always 0; 0x03E0 (pure green) is the key
  - id: footer
    type: footer
    if: not _io.eof
types:
  footer:
    doc: TGA 2.0 footer, 11 files; never read
    seq:
      - id: extension_offset
        contents: [0, 0, 0, 0]
      - id: developer_offset
        contents: [0, 0, 0, 0]
      - id: signature
        contents: ["TRUEVISION-XFILE.", 0]
