meta:
  id: tgp
  title: Mission Sunlight full-screen and panorama image (Data/GFX/*.TGP)
  file-extension: tgp
  endian: le
doc: |
  RGB565 pixels, top row first, packed with Cryo's HLZ LZ (0x430700; same as ScummVM
  Image::HLZDecoder). Two bodies: `chunked` read by Tgp_Load (0x40d9c0), `single` read
  by Tgp_Load2 (0x414779); the caller decides, the file's magic tells them apart
  (E-0100, E-0101). Validator: engines/peintre/tools/parsers/tgp.py.
seq:
  - id: width
    type: u4
  - id: height
    type: u4
  - id: body
    type:
      switch-on: magic == "LZWCRYO"
      cases:
        true: single
        false: chunked
instances:
  magic:
    pos: 12
    type: strz
    size: 8
    encoding: ASCII
    doc: LZWCRYO marks the single body; in a chunked file these bytes are chunk data
types:
  chunked:
    doc: 24 files, panoramas; chunks unpack back to back into width*height*2 bytes
    seq:
      - id: count
        type: u4
      - id: chunks
        type: chunk
        repeat: expr
        repeat-expr: count
  chunk:
    seq:
      - id: packed_size
        type: u4
      - id: unpacked_size
        type: u4
      - id: data
        size: packed_size
        doc: one HLZ stream, ending exactly here
  single:
    doc: 110 files, all 640x480; Tgp_Load2 uses only packed_size
    seq:
      - id: unk_hdr_size
        type: u4
        doc: 0x24 in all 110 (the loader reads 0x24 bytes from here)
      - id: magic
        contents: ["LZWCRYO", 0]
      - id: unk_0
        type: u4
        doc: 0 in all 110
      - id: unk_1
        type: u4
        doc: 0 in all 110
      - id: unk_2
        type: u4
        doc: 256 in all 110
      - id: unk_3
        type: u4
        doc: 1 in all 110
      - id: unpacked_size
        type: u4
        doc: 614400 = 640*480*2 in all 110; not read by the engine
      - id: packed_size
        type: u4
      - id: data
        size: packed_size
        doc: one HLZ stream, ending at EOF
