meta:
  id: china_wav
  title: China sound (*.WAV), RIFF WAVE
  file-extension: wav
  endian: le
doc: |
  Standard RIFF WAVE, PCM. All 763 files: E-0104 (the game's reader: Q-0101).
  Validator: engines/cryomni3d/tools/parsers/wav.py.
seq:
  - id: riff
    contents: RIFF
  - id: riff_size
    type: u4
    doc: file size - 8
  - id: wave
    contents: WAVE
  - id: chunks
    type: chunk
    repeat: eos
    doc: fmt, data in 320 files; fmt, data, LIST in 440; fmt, data, LIST, cue, LIST in 3
types:
  chunk:
    seq:
      - id: id
        type: str
        size: 4
        encoding: ASCII
      - id: size
        type: u4
      - id: body
        size: size
        type:
          switch-on: id
          cases:
            '"fmt "': fmt
      - id: pad
        size: size % 2
  fmt:
    seq:
      - id: format_tag
        type: u2
        doc: 1 (PCM) in all files
      - id: channels
        type: u2
        doc: 1 in all files
      - id: rate
        type: u4
        doc: 22050, or 44100 in DATA/SOUND/BOITE32A.WAV
      - id: byte_rate
        type: u4
      - id: block_align
        type: u2
      - id: bits
        type: u2
        doc: 16 in all files
      - id: cb_size
        type: u2
        if: not _io.eof
