meta:
  id: x3d_dmf
  title: X3D texture map (.DMF), 4X Technologies
  file-extension: dmf
  endian: le

doc: |
  Read by `x3d.dll` (`FUN_10016020` -> `FUN_10010ba0` -> `FUN_100108a0`) for every material
  map; `X3d_Map_Init` rewrites the `.TGA` name stored in the `.O3D` to `.dmf` (E-0038).
  Validated by `tools/parsers/dmf.py`: 518/518 corpus files, every byte consumed.

seq:
  - id: magic
    contents: [0x00, 0xfb]
  - id: file_size
    type: u4
  - id: chunks
    type: chunk
    repeat: eos

types:
  chunk:
    seq:
      - id: id
        type: u2
        enum: chunk_id
      - id: size
        type: u4
        doc: Includes this 6-byte header.
      - id: body
        size: size - 6
        type:
          switch-on: id
          cases:
            chunk_id::header: header
            chunk_id::palette: palette
            chunk_id::color_key: color_key
            chunk_id::unk_fb22: u4
            chunk_id::unk_fb23: u4

  header:
    seq:
      - id: bpp
        type: u2
        doc: 8 (paletted), 15 (RGB555) or 16 (RGB565).
      - id: width
        type: u2
      - id: height
        type: u2

  palette:
    seq:
      - id: entries
        type: bgrx
        repeat: expr
        repeat-expr: 256

  bgrx:
    seq:
      - id: b
        type: u1
      - id: g
        type: u1
      - id: r
        type: u1
      - id: pad
        type: u1

  color_key:
    seq:
      - id: r
        type: u1
      - id: g
        type: u1
      - id: b
        type: u1
      - id: unk
        type: u1

enums:
  chunk_id:
    0xfb10: header
    0xfb20: palette
    0xfb21: color_key
    0xfb22: unk_fb22
    0xfb23: unk_fb23
    0xfb30: pixels
    0xfb31: vq_pixels
