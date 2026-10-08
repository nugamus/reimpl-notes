meta:
  id: cryo_crf
  title: Cryo font (*.CRF), China and Versailles
  file-extension: crf
  -games: [china, versailles]
  endian: be
doc: |
  The layout upstream ScummVM engines/cryomni3d/fonts/cryofont.cpp reads for Versailles.
  CHINE.EXE 0x413420 (MyFont.cpp) loads the whole file and indexes the glyphs from offset
  48 for characters 0x20.. while they lie inside the file. 224 glyphs (0x20..0xFF) in all
  11 China files; ScummVM reads 223. E-0105. Validator: engines/cryomni3d/tools/parsers/crf.py.
seq:
  - id: magic
    contents: CRYOFONT
  - id: unk_08
    type: u2
    doc: 1 in all China files
  - id: unk_0a
    type: u2
    doc: 1 in all China files
  - id: unk_0c
    type: u2
    doc: byte-swapped by CHINE.EXE on load; 9..24 in China
  - id: height
    type: s2
  - id: comment
    size: 32
    doc: 32 '?' in all China files
  - id: glyphs
    type: glyph
    repeat: eos
types:
  glyph:
    seq:
      - id: h
        type: u2
      - id: w
        type: u2
      - id: off_x
        type: s2
      - id: off_y
        type: s2
      - id: advance
        type: u2
      - id: bitmap
        size: w * h
        doc: one byte per pixel, 0 or 255 in China
