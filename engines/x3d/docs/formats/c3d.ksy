meta:
  id: x3d_c3d
  title: X3D camera container (.C3D), 4X Technologies
  file-extension: c3d
  endian: le
  encoding: latin1

doc: |
  Camera container for the X3D engine, as loaded by `X3d_Load_Sdk_c3d` (`x3d.dll`
  `0x1000124e`) which dispatches to `FUN_100148e0` (`x3d.dll` `0x100148e0`).

  As with `.O3D`, `.A3D` and `.L3D`, the loader has no fixed-offset records. It reads
  through four stream primitives — `FUN_1000ba90` (u32), `FUN_1000baf0` (u8),
  `FUN_1000bb20` (f32) and `FUN_1000bb50` (n bytes) — and read order *is* the layout.

  Per-camera record: 32-byte name, then 10 f32s. The 10 f32s land at non-monotonic
  offsets inside the camera struct — `bb20` only advances the file cursor; the
  destination offset is a fixed camera-object slot. The parser tracks file order, not
  struct order: the f32s in the file are written to camera-struct offsets `+0x2C, +0x30,
  +0x34, +0x3C, +0x40, +0x44, +0x54, +0x58, +0x4C, +0x50`. The camera struct also
  carries an unknown u32 at `+0x08` (set to `1` by the loader before the name is read)
  which is not part of the file, so the parser does not see it.

  Validated by `engines/x3d/tools/parsers/c3d.py` against all 6 `.C3D` files in the corpus: every
  file parses, every byte is consumed. Totals: 6 cameras, 648 bytes.

  The 10 f32s are flagged `params` rather than guessed at. The most
  likely split into position / target / up triples at `+0x2C`, `+0x3C`, `+0x4C` is
  recorded as Q-0014; the other four remain opaque.

seq:
  - id: signature
    type: strz
    size: 32
    doc: |
      Compared with `strcmp` against `(c) 1998 4X Tech. 0.95 (C)` and
      `(c) 1998 4X Tech. 1.00 (C)`. Only the bytes up to the NUL matter; the remainder of
      the 32-byte field is uninitialised writer memory and differs between files. All 6
      corpus files are 0.95.
  - id: num_cameras
    type: u4
  - id: cameras
    type: camera
    repeat: expr
    repeat-expr: num_cameras

instances:
  version_1_00:
    value: "signature == '(c) 1998 4X Tech. 1.00 (C)'"
    doc: |
      Selects the loader's global at `x3d.dll` `DAT_1002d224`. No 1.00 `.C3D` file exists
      in the corpus, so the 1.00 path is described here but never cross-validated.

types:
  camera:
    seq:
      - id: name
        type: strz
        size: 32
        doc: NUL-padded 32-byte name. The game uses cp1252, French assets throughout.
      - id: params
        size: 40
        type:
          seq:
            - id: f0
              type: f4
              doc: |
                Camera struct offset `+0x2C` — first of three plausible vec3s. Likely
                position; unproven.
            - id: f1
              type: f4
              doc: Camera struct offset `+0x30`.
            - id: f2
              type: f4
              doc: Camera struct offset `+0x34`.
            - id: f3
              type: f4
              doc: |
                Camera struct offset `+0x3C` — second of three plausible vec3s. Likely
                target; unproven.
            - id: f4
              type: f4
              doc: Camera struct offset `+0x40`.
            - id: f5
              type: f4
              doc: Camera struct offset `+0x44`.
            - id: f6
              type: f4
              doc: |
                Camera struct offset `+0x54` — the `+0x4C` slot is read *after* this in
                file order, so the non-monotonic struct layout must be respected by any
                writer.
            - id: f7
              type: f4
              doc: Camera struct offset `+0x58`.
            - id: f8
              type: f4
              doc: |
                Camera struct offset `+0x4C` — third plausible vec3, likely up;
                unproven.
            - id: f9
              type: f4
              doc: Camera struct offset `+0x50`.
        doc: |
          10 f32s the loader writes into fixed camera-struct offsets. Meaning opaque;
          only the split into three likely-vec3s is suggested, the names are not proven.
          See Q-0014.