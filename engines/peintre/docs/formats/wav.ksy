meta:
  id: peintre_wav
  title: Mission Sunlight sound (Data/SOUND/*.WAV), RIFF WAVE
  file-extension: wav
  endian: le
doc: |
  Read by Snd_Load (0x417084): channels, rate, bits from fmt (format tag not checked),
  then the data chunk; chunks after data are never read. E-0208.
  Validator: engines/peintre/tools/parsers/wav.py.
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
    doc: fmt first, data second in all 122 files; then LIST / cue / smpl / plst in 40
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
        doc: 1 (118 files) or 2 (A03_06I..L)
      - id: rate
        type: u4
        doc: 22050 in all files
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
        doc: present (0) in 16 files
