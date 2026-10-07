meta:
  id: china_zik
  title: China music (DATA/MUSIC/*.ZIK), headerless PCM
  file-extension: zik
  endian: le
doc: |
  No header: signed 16-bit little-endian stereo PCM at 22050 Hz from byte 0 to the end
  (Music::start 0x412740 builds the DirectSound format: PCM, 2 channels, 22050 Hz,
  16 bits; Music::update 0x412740 streams the file into a 512 KiB looping buffer and
  seeks back to byte 0 at the end, so the whole file loops). E-0206.
  Validator: engines/cryomni3d/tools/parsers/zik.py.
seq:
  - id: frames
    type: frame
    repeat: eos
types:
  frame:
    seq:
      - id: left
        type: s2
      - id: right
        type: s2
