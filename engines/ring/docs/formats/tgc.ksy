meta:
  id: ring_tgc
  title: Ring engine packed TGA (.tga members of .at2)
  file-extension: [tgc]
  endian: le
doc: |
  Read by aImageFileTgc::Init (RING_DVD.EXE 0x42b230), ReadInfo 0x42b540, ReadImage
  0x42b600. Chunks of packed bit stream (README "Packed bit stream", 16-bit literals,
  6-bit indices) that concatenate to a TGA file: type 2, 32 bpp, BGRA rows bottom-up,
  optional TGA 2.0 footer. Evidence: EVIDENCE.md E-0018. Validator:
  engines/ring/tools/parsers/tgc.py.
seq:
  - id: chunk_count
    type: u4
  - id: unpacked_size
    type: u4
    doc: sum of the chunks' unpacked sizes
  - id: chunks
    type: chunk
    repeat: expr
    repeat-expr: chunk_count
types:
  chunk:
    seq:
      - id: packed_size
        type: u4
      - id: unpacked_size
        type: u4
      - id: data
        size: packed_size
