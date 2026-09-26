meta:
  id: x3d_lip_index
  title: X3D lip-sync table (`#INDEX#` chunk of Sound/*.bin), 4X Technologies
  endian: le

doc: |
  Payload of the `#INDEX#` chunk, the only chunk of `Data/U##/Sound/<voice>.bin` (the
  `.BIN` chunk container is E-0025). Read by `Talker_LoadLipBin` (`0x00421960`): finds
  `INDEX`, reads `u32 count`, then `count * 8` bytes. Behaviour is in
  `engines/x3d/docs/spec/sound.md` (E-0124, E-0125).

  Validated by `engines/x3d/tools/parsers/lip.py`: 81/81 files, 10,373 records, every byte consumed.

seq:
  - id: count
    type: u4
  - id: records
    type: record
    repeat: expr
    repeat-expr: count

types:
  record:
    seq:
      - id: time_ms
        type: u4
        doc: Milliseconds since the talk started; non-decreasing, 0 in the first record of every file.
      - id: shape
        type: u2
        doc: "Mouth slot 1..8: 1 closed, 2 Ch, 3 Ch_yeux, 4..8 open (the engine picks the open shape at random)."
      - id: unk_pad
        type: u2
        doc: 0xCDCD in every record (MSVC debug-heap fill); never read as a field.
