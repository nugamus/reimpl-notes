meta:
  id: x3d_l3d
  title: X3D light container (.L3D), 4X Technologies
  file-extension: l3d
  endian: le
  encoding: latin1

doc: |
  Light container for the X3D engine, as loaded by `X3d_Load_Sdk_l3d` (`x3d.dll`
  `0x100012fd`) which dispatches to `FUN_10014d50` (`x3d.dll` `0x10014d50`).

  As with `.O3D` and `.A3D`, the loader has no fixed-offset records. It reads through
  four stream primitives — `FUN_1000ba90` (u32), `FUN_1000baf0` (u8), `FUN_1000bb20`
  (f32) and `FUN_1000bb50` (n bytes) — and read order *is* the layout.

  Per-light record: 32-byte name, 3-f32 position, 3-u8 RGB, 3-f32 unknown, 2-u32
  unknown, u32 is_spot. When `is_spot != 0`, a further 3-f32 spot target and 2-f32 cone
  angles follow. Spot-light data is parsed but no corpus sample exists — every `.L3D` in
  the corpus is omni.

  Validated by `tools/parsers/l3d.py` against all 5 `.L3D` files in the corpus: every
  file parses, every byte is consumed. Totals: 78 lights, 0 spot, 5,718 bytes.

  Fields named "extra_*" are opaque on purpose (CLAUDE.md rule 5). Their width is proven;
  their meaning is not, and no name is guessed at.

seq:
  - id: signature
    type: strz
    size: 32
    doc: |
      Compared with `strcmp` against `(c) 1998 4X Tech. 0.95 (L)` and
      `(c) 1998 4X Tech. 1.00 (L)`. Only the bytes up to the NUL matter; the remainder of
      the 32-byte field is uninitialised writer memory and differs between files. All 5
      corpus files are 0.95.
  - id: num_lights
    type: u4
  - id: lights
    type: light
    repeat: expr
    repeat-expr: num_lights

instances:
  version_1_00:
    value: "signature == '(c) 1998 4X Tech. 1.00 (L)'"
    doc: |
      Selects the loader's global at `x3d.dll` `DAT_1002d224`. No 1.00 `.L3D` file exists
      in the corpus, so the 1.00 path is described here but never cross-validated.

types:
  vec3:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4

  rgb:
    seq:
      - id: r
        type: u1
      - id: g
        type: u1
      - id: b
        type: u1

  light:
    seq:
      - id: name
        type: strz
        size: 32
        doc: NUL-padded 32-byte name. The game uses cp1252, French assets throughout.
      - id: position
        type: vec3
      - id: color
        type: rgb
      - id: extra_floats
        type: vec3
        doc: |
          Three f32s the loader writes into light struct offsets `+0x34`, `+0x38`, `+0x3c`.
          Field meaning unproven; one of them is plausibly the intensity multiplier (the
          `X3d_Light_Set_Multiplier` export covers that surface) but the others are not
          named. Read but unnamed per CLAUDE.md rule 5.
      - id: extra_u32s
        size: 8
        type:
          seq:
            - id: a
              type: u4
            - id: b
              type: u4
        doc: |
          Two u32s into light struct offsets `+0x40`, `+0x44`. In the corpus they are
          almost always `(0, 1)`. Field meaning unproven.
      - id: is_spot
        type: u4
        doc: |
          Non-zero selects the spot-light branch, which appends a target vec3 and two cone
          angles. Every corpus file has `is_spot == 0`; the spot branch is parsed but
          never cross-validated.
      - id: spot
        type: spot_light
        if: is_spot != 0

  spot_light:
    seq:
      - id: target
        type: vec3
      - id: angles
        size: 8
        type:
          seq:
            - id: theta
              type: f4
              doc: Cone inner angle, used as `cos(theta * pi / 180 * RAD2DEG)`.
            - id: phi
              type: f4
              doc: Cone outer angle, used the same way.
