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

  Per-light record: 32-byte name, 3-f32 position, 3-u8 RGB, f32 inner, f32 outer,
  f32 multiplier, u32 hidden, u32 attenuate, u32 is_spot (E-0140). When `is_spot != 0`, a further 3-f32 spot target and 2-f32 cone
  angles follow. Spot-light data is parsed but no corpus sample exists — every `.L3D` in
  the corpus is omni.

  Validated by `engines/x3d/tools/parsers/l3d.py` against all 5 `.L3D` files in the corpus: every
  file parses, every byte is consumed. Totals: 78 lights, 0 spot, 5,718 bytes.

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
      - id: inner
        type: f4
        doc: Light `+0x38` (`X3d_Light_Set_Inner`); full-strength radius (E-0140).
      - id: outer
        type: f4
        doc: Light `+0x34` (`X3d_Light_Set_Outer`); zero-contribution radius (E-0140).
      - id: multiplier
        type: f4
        doc: Light `+0x3c` (`X3d_Light_Set_Multiplier`); negative darkens (E-0140).
      - id: hidden
        type: u4
        doc: Light `+0x40` (`X3d_Light_Get_Hide_State`); non-zero skips the light.
      - id: attenuate
        type: u4
        doc: Light `+0x44` (`X3d_Light_Attenuate`); non-zero enables inner/outer falloff.
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
              doc: Full cone angle in degrees, stored as `cos(theta * pi / 360)` (half angle, E-0140).
            - id: phi
              type: f4
              doc: Cone outer angle, used the same way.
