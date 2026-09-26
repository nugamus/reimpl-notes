meta:
  id: ring_wac
  title: Ring engine packed sound (.wac mono DPCM, .was stereo)
  file-extension: [wac, was]
  endian: le
doc: |
  .wac: aSecComSouMono (RING_DVD.EXE DecompressHeader 0x47b250, Decompress 0x47b3b0,
  DPCM 0x47bc20). Each chunk: 3 zero bits, then 256 codes: 0 + 10 bits = new delta
  (d > 0x1ff: 0x200 - d, times 64), 1 = previous delta; each code adds the delta to the
  running 16-bit sample; sample and delta carry over between chunks.
  .was: aSecComSou (DecompressHeader 0x47aaf0, Decompress 0x47ac90, decoder 0x430a80):
  packed bit stream (README) with 12-bit literals shifted left by 4, 6-bit indices.
  Evidence: EVIDENCE.md E-0021. Validator: engines/ring/tools/parsers/wac.py.
seq:
  - id: chunk_count
    type: u4
  - id: wav_size
    type: u4
    doc: size of the unpacked WAV file (44 + samples bytes)
  - id: wav_header
    size: 44
    doc: first 44 bytes of the unpacked WAV (RIFF, WAVE, fmt PCM 16-bit, then 'data' or 'fact')
  - id: mono_chunks
    type: mono_chunk
    repeat: expr
    repeat-expr: chunk_count
    if: _root.wav_header[22] == 1
  - id: stereo_chunks
    type: stereo_chunk
    repeat: expr
    repeat-expr: chunk_count
    if: _root.wav_header[22] == 2
types:
  mono_chunk:
    seq:
      - id: size
        type: u2
      - id: data
        size: size
        doc: 3 zero bits, 256 DPCM codes, fewer than 8 padding bits
  stereo_chunk:
    seq:
      - id: packed_size
        type: u4
      - id: unpacked_size
        type: u4
      - id: data
        size: packed_size
