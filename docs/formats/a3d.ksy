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
  `FUN_10012ee0`. Validated by `tools/parsers/a3d.py` against all 429 `.A3D`
  files in the corpus: every file parses, every byte is consumed. Totals:
  16,852 animations, 555,288 keyframes, 22,422,652 bytes.

  Each animation carries five keyframe tracks. The first three (translation,
  scale, rotation) follow the same template with different value widths;
  track D is "hide" data and track E is morph data with per-key normals and
  positions. When a track's count is zero the loader reads no per-key data,
  including no inner counts or tails — a zero count means "this track has no
  keys" and skips the rest.

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
      - id: unknown
        type: u4
        repeat: expr
        repeat-expr: 3
      - id: track_a
        type: track
        doc: Translation; `value_floats` = 3.
        params:
          value_floats: 3
      - id: track_b
        type: track
        params:
          value_floats: 3
      - id: track_c
        type: track
        doc: Rotation; quaternion-like values, `value_floats` = 4.
        params:
          value_floats: 4
      - id: track_d
        type: track
        doc: |
          Hide track; two u32s per key (frame time and key info), no value floats.
        params:
          value_floats: 0
          extra_key_u32s: 2
      - id: track_e
        type: track_e

  track:
    doc: |
      A count, a companion u32, `count` frame ids, then per-key data. For tracks
      A/B/C the per-key data is `count × (5f + value_floats f)`; for track D it is
      `count × extra_key_u32s u32` (no value floats).
    params:
      value_floats: { type: s4 }
      extra_key_u32s: { type: s4, default: 0 }
    seq:
      - id: count
        type: u4
      - id: unknown
        type: u4
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
      Morph track. When count is zero the loader reads no per-key data: no
      inner count, no positions, no normals, no tail. When count is non-zero
      the loader reads an inner count, then `count × inner` positions,
      `count × inner` normals, then `count × 7` tail floats.
    seq:
      - id: count
        type: u4
      - id: unknown
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
      - id: positions
        type: vec3
        repeat: expr
        repeat-expr: count * inner_count
        if: count != 0
      - id: normals
        type: vec3
        repeat: expr
        repeat-expr: count * inner_count
        if: count != 0
      - id: tail
        type: f4
        repeat: expr
        repeat-expr: count * 7
        if: count != 0
