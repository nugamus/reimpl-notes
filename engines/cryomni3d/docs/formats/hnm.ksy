meta:
  id: china_hnm6
  title: China video, still and warp (*.HNM, *.HNS), Cryo HNM6
  file-extension: [hnm, hns]
  endian: le
doc: |
  Same layout as Mission Sunlight's HNM6 (engines/peintre/docs/formats/hnm.ksy) plus the
  IW warp chunk, which ScummVM engines/cryomni3d/image/hnm.cpp and image/codecs/hnm.cpp
  (warp mode) already read. All 764 China files: E-0100, E-0101.
  Validator: engines/cryomni3d/tools/parsers/hnm.py.
seq:
  - id: header
    type: header
  - id: frames
    type: superchunk
    repeat: expr
    repeat-expr: header.frame_count
  - id: terminator
    contents: [0, 0, 0, 0]
types:
  header:
    seq:
      - id: tag
        contents: HNM6
      - id: unk_04
        type: u2
        doc: 0 in all files
      - id: audio_flags
        type: u1
        doc: |
          bit 0 sound; (audio_flags & 0x60) >> 4 = rate / 11025 and bit 7 = stereo, agreeing
          with the APC header in all 44 sound files. Corpus: 0x00 (720), 0xA1 22050 Hz stereo
          (37), 0x21 22050 Hz mono (5), 0xC1 44100 Hz stereo (2)
      - id: bpp
        type: u1
        doc: 16 in all files
      - id: width
        type: u2
        doc: 640, or 2048 in the 191 warps
      - id: height
        type: u2
        doc: 480, or 768 in the 191 warps
      - id: file_size
        type: u4
        doc: file length; file length - 4 (terminator not counted) in the 191 warps
      - id: frame_count
        type: u4
      - id: unk_14
        type: u4
        doc: 0 in all files
      - id: unk_18
        type: u2
        doc: 0 in all files
      - id: unk_1a
        type: u2
        doc: 2, or 1 in the 191 warps
      - id: max_frame_size
        type: u4
        doc: |
          at least the largest video payload; 0x300000 (2048 * 768 * 2) in warps, which
          ScummVM does not use for IW ("not reliable on IW")
      - id: author
        size: 16
        doc: '"Pascal URRO  R&D" in all files'
      - id: copyright
        size: 16
        doc: '"-Copyright CRYO-" in all files'
  superchunk:
    seq:
      - id: size_flags
        type: u4
        doc: size (low 24 bits, with these 4 bytes); the high byte is 0 in all files
      - id: chunks
        type: chunks
        size: (size_flags & 0xffffff) - 4
  chunks:
    seq:
      - id: chunk
        type: chunk
        repeat: eos
  chunk:
    seq:
      - id: size
        type: u4
        doc: with this 8-byte header; the next chunk starts at the next multiple of 4
      - id: type
        type: str
        size: 2
        encoding: ASCII
        doc: |
          IX (video, every frame of non-warps), IW (warp picture, the only chunk of a
          one-frame warp), AA (first sound chunk, frame 0), BB (later sound)
      - id: flags
        type: u2
        doc: 0 in all files
      - id: data
        size: size - 8
        type:
          switch-on: type
          cases:
            '"IX"': video_ix
            '"IW"': video_iw
            '"AA"': audio_aa
      - id: pad
        size: (4 - size % 4) % 4
  video_ix:
    doc: streams decoded by ScummVM image/codecs/hnm.cpp
    seq:
      - id: quality
        type: s4
        doc: negative = key frame
      - id: bit_start
        type: u4
        doc: 28 in all frames
      - id: motion_start
        type: u4
      - id: shortmotion_start
        type: u4
      - id: jpeg_start
        type: u4
      - id: end
        type: u4
        doc: = payload size in every frame
      - id: unk_18
        type: u4
        doc: = end in every frame; ScummVM skips it
      - id: streams
        size: end - 28
  video_iw:
    doc: |
      warp picture, a key picture decoded in warp mode (8x8 blocks: key block, motion or
      4x4 split) by ScummVM image/codecs/hnm.cpp; 24-byte header, no unk_18
    seq:
      - id: quality
        type: s4
        doc: 85 in all 191 warps; ScummVM asserts > 0 in warp mode
      - id: bit_start
        type: u4
        doc: 24 in all warps
      - id: motion_start
        type: u4
      - id: shortmotion_start
        type: u4
      - id: jpeg_start
        type: u4
      - id: end
        type: u4
        doc: = payload size in every warp
      - id: streams
        size: end - 24
  audio_aa:
    seq:
      - id: apc_header
        size: 32
        doc: CRYO_APC 1.20 header (engines/peintre/docs/formats/apc.ksy)
      - id: adpcm
        size-eos: true
        doc: sound for the first 32 frames (all of it in the 9 files without BB)
