meta:
  id: ring_cnm
  title: Ring engine video container (.cnm, .ci2; CNM UNR images in .at3)
  file-extension: [cnm, ci2]
  endian: le
doc: |
  Container and chunk headers; the payloads are bit streams (README "HBR video codec",
  "UNR video codec"; E-0028, E-0350..E-0357). Two variants by
  magic: "CNM HBR\0" (Ring DVD and CD version; RING_DVD.EXE aImageFileCin 0x42a6b0,
  aCinMov::Play 0x415990) and "CNM UNR\0" (Ring ISO version, Prophet; LEGEND.EXE
  aImageFileCinema::ReadHeader 0x421c30, aCinMov::Play 0x4a51c0). Chunk types: 'A' 'B' 'Z'
  sound (u32 size), 'S' 'U' image, 'T' tile data. HBR 'S' has a 20-byte header, 'T' a
  13-byte header followed by size + 2n + 2 bytes (n = its last header byte); UNR 'S'/'U'
  have a 0x2f-byte header, 'T' an 8-byte one. Evidence: EVIDENCE.md E-0024. Validator:
  engines/ring/tools/parsers/cnm.py.
seq:
  - id: magic
    size: 8
  - id: hbr
    type: hbr_header
    if: magic == [0x43, 0x4e, 0x4d, 0x20, 0x48, 0x42, 0x52, 0x00]
  - id: unr
    type: unr_header
    if: magic == [0x43, 0x4e, 0x4d, 0x20, 0x55, 0x4e, 0x52, 0x00]
  - id: chunks
    type: chunk
    repeat: eos
types:
  hbr_header:
    seq:
      - {id: channels, type: u1}
      - {id: bits, type: u1}
      - {id: rate, type: u4}
      - {id: frame_count, type: u4}
      - {id: unk_timing, type: u4, doc: "1250 in every Ring file"}
      - {id: unk_16, type: u1}
      - {id: width, type: u4}
      - {id: height, type: u4}
      - {id: unk_1f, type: u2}
      - {id: zero, size: 31}
  unr_header:
    seq:
      - {id: frame_count, type: u4}
      - {id: unk_timing, type: u4, doc: "1250 (Ring ISO), 1500 or 2500 (Prophet)"}
      - {id: unk_10, type: u1}
      - {id: width, type: u4}
      - {id: height, type: u4}
      - {id: unk_19, type: u1, doc: "32"}
      - {id: interlaced, type: u1, doc: "1: half the rows decoded, tiles at half scale (E-0352)"}
      - {id: tracks, type: u1}
      - {id: table_count, type: u4, doc: "= frame_count"}
      - {id: frame_count_2, type: u4}
      - {id: unk_table_size, type: u4}
      - {id: unk_flag, type: u4, doc: "1: table is all zero"}
      - {id: zero, size: 148}
      - {id: track_info, size: 16, repeat: expr, repeat-expr: tracks}
      - {id: table, type: u4, repeat: expr, repeat-expr: table_count * 2}
  chunk:
    seq:
      - {id: type, type: u1}
      - id: unr_picture
        type: unr_picture
        if: _root.magic[4] == 0x55 and (type == 0x53 or type == 0x55)
      - id: unr_tiles
        type: unr_tiles
        if: _root.magic[4] == 0x55 and type == 0x54
      - id: size
        type: u4
        if: _root.magic[4] == 0x48 or (type != 0x53 and type != 0x54 and type != 0x55)
      - id: rest
        size: >-
          (type == 0x53 or type == 0x55) ? 16 + size : type == 0x54 ? 8 + size : size
        if: _root.magic[4] == 0x48 or (type != 0x53 and type != 0x54 and type != 0x55)
        doc: header remainder and payload; HBR 'T' also has 2n + 2 bytes after the payload
  unr_picture:
    doc: "'S' / 'U' (E-0350)"
    seq:
      - {id: size, type: u4}
      - {id: map_size, type: u4, doc: "picture stream bytes; < size: a tile table follows"}
      - {id: ntiles, type: u2, doc: "tiles in the table, tile 0 included"}
      - {id: tile_width, type: u2, doc: "4 in every file"}
      - {id: width, type: u4}
      - {id: height, type: u4}
      - {id: unk_14, type: u4, doc: "1250 Ring ISO, 1500 or 2500 Prophet videos, 0 .at3"}
      - {id: unk_18, type: u4, doc: "= unk_14"}
      - {id: zero, size: 19}
      - {id: picture, size: "map_size < size ? map_size : size"}
      - {id: tiles, size: size - map_size, if: map_size < size}
  unr_tiles:
    doc: "'T', v2 only (E-0350)"
    seq:
      - {id: size, type: u4}
      - {id: ntiles, type: u2}
      - {id: tile_width, type: u2}
      - {id: tiles, size: size}
