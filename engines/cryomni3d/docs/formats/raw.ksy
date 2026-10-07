meta:
  id: china_raw_mask
  title: China puzzle mask (DATA/PUZZLES/{HORLOGE,PUZZLE4}/MASK.RAW)
  file-extension: raw
doc: |
  640x480 bytes, no header, top row first; CHINE.EXE looks up mask[y * 640 + x] under the
  mouse (PUZZLE4 0x4189bc: value - 0xE7 = zone 0..23, 0xFF none; HORLOGE 0x41c1d0: 0
  none, 1..54 zones). E-0106. Validator: engines/cryomni3d/tools/parsers/raw.py.
seq:
  - id: rows
    size: 640
    repeat: expr
    repeat-expr: 480
