meta:
  id: x3d_a3d
  title: X3D keyframe animation (.A3D), 4X Technologies
  file-extension: a3d
  endian: le
  encoding: latin1

doc: |
  Animation container for the X3D engine. Same family as `.O3D` — a 32-byte
  `(c) 1998 4X Tech. 0.95 (A)` signature, then a sequential stream through the
  loader's four cursor primitives (`FUN_1000ba90`, `FUN_1000baf0`, `FUN_1000bb20`,
  `FUN_1000bb50`).

  Derived from `X3d_Load_Sdk_a3d` (`x3d.dll` `0x10001091`), which dispatches to
  `FUN_10012ee0`. Validated by `engines/x3d/tools/parsers/a3d.py` against all 429 `.A3D`
  files in the corpus: every file parses, every byte is consumed. Totals:
  16,852 animations, 555,288 keyframes, 22,422,652 bytes.

  Each animation carries five keyframe tracks: translation, scale, rotation, hide and
  morph (the loader's allocation error strings name them, E-0055). When a track's count
  is zero the loader reads no per-key data, including no inner counts. No corpus file
  has hide or morph keys; their layout is the loader's. Playback semantics:
  `engines/x3d/docs/spec/animation.md`.

  Fields marked "unknown" are opaque on purpose (CLAUDE.md rule 5).

seq:
  - id: signature
    type: strz
    size: 32
    doc: |
      Compared with `strcmp` against `(c) 1998 4X Tech. 0.95 (A)` and
      `(c) 1998 4X Tech. 1.00 (A)`. Bytes past the NUL are uninitialised writer
      memory. All 429 corpus files are 0.95.
  - id: num_animations
    type: u4
  - id: animations
    type: animation
    repeat: expr
    repeat-expr: num_animations

types:
  vec3:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4

  animation:
    doc: '`FUN_10012ee0`. Each animation has a name and optionally a parent.'
    seq:
      - id: name
        type: strz
        size: 32
      - id: has_parent
        type: u4
      - id: parent
        type: strz
        size: 32
        if: has_parent != 0
      - id: pivot
        type: vec3
        doc: Animation `+0xb4`; equals the `.O3D` object's pivot in U01's files.
      - id: num_frames
        type: u4
        doc: '`X3d_Animation_Get_Number_Frame` (`+0x34`).'
      - id: first_frame
        type: u4
        doc: '`X3d_Animation_Get_First_Frame` (`+0x38`); playback starts here.'
      - id: last_frame
        type: u4
        doc: '`X3d_Animation_Get_Last_Frame` (`+0x3c`).'
      - id: track_a
        type: track
        doc: Translation (`+0x40`); values are the local position.
        params:
          value_floats: 3
      - id: track_b
        type: track
        doc: Scale (`+0x54`); values are the local scale.
        params:
          value_floats: 3
      - id: track_c
        type: track
        doc: Rotation (`+0x68`); values are absolute quaternions (w, x, y, z).
        params:
          value_floats: 4
      - id: track_d
        type: track
        doc: Hide (`+0xa0`); one u32 per key (`+0xb0`), no floats.
        params:
          value_floats: 0
          extra_key_u32s: 1
      - id: track_e
        type: track_e
        doc: Morph (`+0x7c`).

  track:
    doc: |
      A count, a flags u32, `count` frame numbers, then per-key data. For
      translation/scale/rotation it is `count` × 5 f32 key parameters (tension,
      continuity, bias, ease in, ease out: E-0055) then `count` × `value_floats` f32;
      for hide it is `count` × `extra_key_u32s` u32.
    params:
      value_floats: { type: s4 }
      extra_key_u32s: { type: s4, default: 0 }
    seq:
      - id: count
        type: u4
      - id: flags
        type: u4
        doc: Bits 0-1 make the key lookup wrap past the last key; 0 in every corpus track.
      - id: frames
        type: u4
        repeat: expr
        repeat-expr: count
      - id: keys
        type: f4
        repeat: expr
        repeat-expr: count * 5
        if: extra_key_u32s == 0
      - id: values
        type: f4
        repeat: expr
        repeat-expr: count * value_floats
        if: extra_key_u32s == 0
      - id: key_info
        type: u4
        repeat: expr
        repeat-expr: count * extra_key_u32s
        if: extra_key_u32s != 0

  track_e:
    doc: |
      Morph track. When count is zero the loader reads nothing more. Otherwise: key
      parameters, one inner count, then per key the inner positions and normals (they
      replace the object's own vertex range when sampled), a bounding sphere and a
      bounding box.
    seq:
      - id: count
        type: u4
      - id: flags
        type: u4
      - id: frames
        type: u4
        repeat: expr
        repeat-expr: count
      - id: keys
        type: f4
        repeat: expr
        repeat-expr: count * 5
        if: count != 0
      - id: inner_count
        type: u4
        if: count != 0
      - id: morphs
        type: morph_key(inner_count)
        repeat: expr
        repeat-expr: count
        if: count != 0

  morph_key:
    params:
      inner_count: { type: u4 }
    seq:
      - id: positions
        type: vec3
        repeat: expr
        repeat-expr: inner_count
      - id: normals
        type: vec3
        repeat: expr
        repeat-expr: inner_count
      - id: sphere
        type: f4
        repeat: expr
        repeat-expr: 4
        doc: Centre and radius (object `+0x68..0x70`, `+0x78`).
      - id: box
        type: f4
        repeat: expr
        repeat-expr: 6
        doc: Minimum then maximum corner, expanded to eight corners at `+0x7c`.
