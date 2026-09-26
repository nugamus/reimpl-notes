meta:
  id: hnm6
  title: Mission Sunlight movie (Data/MOVIES/*.HNM), Cryo HNM6
  file-extension: hnm
  endian: le
doc: |
  Opened by Hnm_Open (0x40ba64), streamed through a 0x80000-byte ring by a read thread
  (0x40c1b3), one superchunk per frame (Hnm_Stream 0x40c072, chunk walk 0x40c5c2).
  Same layout as ScummVM video/hnm_decoder.cpp (HNM6). E-0200..E-0203.
  Validator: engines/peintre/tools/parsers/hnm.py.
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
        doc: 0 in all 95 files; not read by the EXE or ScummVM
      - id: audio_flags
        type: u1
        doc: |
          bit 0 sound; (audio_flags & 0x60) >> 4 = rate / 11025; bit 7 stereo (0x40c9aa).
          Corpus: 0x00 (15 files), 0x21 22050 Hz mono (59), 0xA1 22050 Hz stereo (21)
      - id: bpp
        type: u1
        doc: 16 in all files
      - id: width
        type: u2
        doc: the EXE accepts only 640
      - id: height
        type: u2
        doc: the EXE accepts only 480
      - id: file_size
        type: u4
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
        doc: 2 in all files
      - id: max_frame_size
        type: u4
        doc: largest video payload; the EXE rejects < 1, ScummVM sizes its decode buffer with it
      - id: author
        size: 16
        doc: '"Pascal URRO  R&D"'
      - id: copyright
        size: 16
        doc: '"-Copyright CRYO-"'
  superchunk:
    seq:
      - id: size_flags
        type: u4
        doc: size (low 24 bits, with these 4 bytes); the high byte is 0 in all files
      - id: chunks
        type: chunk
        size: (size_flags & 0xffffff) - 4
  chunk:
    seq:
      - id: size
        type: u4
        doc: with this 8-byte header; the next chunk starts at the next multiple of 4
      - id: type
        type: str
        size: 2
        encoding: ASCII
        doc: IX (video, every frame), AA (first sound chunk, frame 0), BB (later sound)
      - id: flags
        type: u2
        doc: 0 in all files
      - id: data
        size: size - 8
      - id: pad
        size: (4 - size % 4) % 4
  video_ix:
    doc: payload of an IX chunk; streams decoded by ScummVM image/codecs/hnm.cpp
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
  audio_aa:
    seq:
      - id: apc_header
        size: 32
        doc: CRYO_APC 1.20 header (apc.ksy); its sample count is the soundtrack's, unused
      - id: adpcm
        size-eos: true
        doc: sound for the first 32 frames
