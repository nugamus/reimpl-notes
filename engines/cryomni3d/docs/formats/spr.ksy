meta:
  id: china_spr
  title: China sprite (*.SPR), one picture in a TGA container
  file-extension: spr
  endian: le
doc: |
  Not Mission Sunlight's SPR bank. A TGA header with a 12-byte image ID, then 15-bit
  pixels, top row first. Read by CHINE.EXE 0x41f760 (header, the three ID fields, depth
  15 or 16 accepted, width*height*2 pixel bytes). All 448 files: E-0102.
  Validator: engines/cryomni3d/tools/parsers/spr.py.
seq:
  - id: id_length
    contents: [12]
    doc: the loader never reads it; it always takes 12 ID bytes
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
    contents: [15]
  - id: descriptor
    contents: [0x20]
    doc: top row first
  - id: key
    type: u4
    doc: |
      555 colour kept with the sprite (converted to 565 with the pixels on 565 screens);
      27 values, 0x001F in 184 files; 304 files contain it
  - id: unk_16
    type: s4
    doc: kept with the sprite; 0..603 in the corpus (Q-0100)
  - id: unk_1a
    type: s4
    doc: kept with the sprite; 0..458 in the corpus (Q-0100)
  - id: pixels
    size: width * height * 2
    doc: X1R5G5B5, bit 15 always 0
