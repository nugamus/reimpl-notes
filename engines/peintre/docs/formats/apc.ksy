meta:
  id: cryo_apc
  title: Cryo APC sound (Data/SOUND/*.APC)
  file-extension: apc
  endian: le
doc: |
  Streamed by the '!' path of Snd_Load (0x417084) / Adpcm_StreamInit (0x4176c6), decoded by
  Apc_Decode (0x465d8e). Same header as ScummVM audio/decoders/apc.cpp. E-0207.
  Validator: engines/peintre/tools/parsers/apc.py.
seq:
  - id: magic
    contents: CRYO_APC
  - id: version
    contents: '1.20'
  - id: samples
    type: u4
    doc: per channel
  - id: rate
    type: u4
    doc: 22050 in all 68 files
  - id: left_start
    type: s4
    doc: initial predictor; 0 in all files
  - id: right_start
    type: s4
    doc: 0 in all files
  - id: flags
    type: u4
    doc: bit 0 stereo; 0 (mono) in all files
  - id: adpcm
    size: samples * 2 * (flags & 1 != 0 ? 2 : 1) / 4 + 1
    doc: IMA ADPCM, high nibble first; one byte more than the samples need (encoder 0x4662bd)
