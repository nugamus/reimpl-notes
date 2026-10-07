meta:
  id: grumpa_fxi
  title: Grumpa .fxi 16-bit surface (Z-depth buffers in the corpus)
  file-extension: fxi
  endian: le
doc: |
  Loaded by FUN_00418de0 (the fxi case of FUN_004189d0) in the decrypted Grumpa.exe
  (E-0003, E-0008, E-0009). 16-bit surface, raw or block-compressed. Compressed: one
  control byte per 8x8 block (row-major); then per block two planes, the low nibble codes
  the high byte of each pixel, the high nibble the low byte. A plane is 8x8 bytes in one
  of 4 modes: 0 solid (1 byte), 1 1bpp (8-byte mask + 2 values), 2 2bpp (16-byte mask +
  4 values), 3 raw (64 bytes). Validator: engines/grumpa/tools/parsers/fxi.py (316/316).
seq:
  - id: version
    type: u1
    doc: 1 in every file
  - id: flag
    type: u1
    doc: 0 = raw pixels, non-zero = block-compressed
  - id: width
    type: u2
    doc: 800 in the whole corpus
  - id: height
    type: u2
    doc: 600 in the whole corpus
  - id: unk_field0
    type: u4
    doc: usually 0 (colour key?)
  - id: unk_field1
    type: u4
  - id: unk_field2
    type: u4
  - id: raw_pixels
    size: width * height * 2
    if: flag == 0
    doc: row-major 16-bit pixels
  - id: control
    size: (width / 8) * (height / 8)
    if: flag != 0
    doc: one byte per 8x8 block; low nibble = high-byte plane mode, high nibble = low-byte plane mode
  - id: blocks
    type: block(control[_index])
    repeat: expr
    repeat-expr: (width / 8) * (height / 8)
    if: flag != 0
types:
  block:
    params:
      - id: ctrl
        type: u1
    seq:
      - id: high_byte_plane
        type: plane(ctrl & 15)
      - id: low_byte_plane
        type: plane(ctrl >> 4)
  plane:
    params:
      - id: mode
        type: u1
    seq:
      - id: data
        type:
          switch-on: mode
          cases:
            0: solid
            1: bpp1
            2: bpp2
            3: raw64
  solid:
    seq:
      - id: value
        type: u1
  bpp1:
    seq:
      - id: mask
        size: 8
        doc: bit (1 << col) of row byte selects value1
      - id: value0
        type: u1
      - id: value1
        type: u1
  bpp2:
    seq:
      - id: mask
        size: 16
        doc: 2 bits per pixel, 2 bytes per row
      - id: values
        size: 4
  raw64:
    seq:
      - id: plane_bytes
        size: 64
