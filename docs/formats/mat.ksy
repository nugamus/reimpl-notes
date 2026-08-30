meta:
  id: x3d_mat
  title: X3D material script (.MAT), 4X Technologies
  file-extension: mat
  encoding: latin1

doc: |
  Plain ASCII material script for the X3D engine. No magic; no binary primitives; no
  per-record signatures. Layout taken directly off the sample bytes per the
  03-HANDOFF-PHASE-2.md §2 loader-list note that says `.MAT` is plain ASCII beginning
  with `;-------...`.

  Every file starts with a three-line header banner (47-dash separator, `; <path>`
  comment, separator), followed by zero or more 16-line material blocks separated by
  banner lines. Each block has exactly 16 lines in a fixed order; the `REFLECTION=`
  key appears twice (once before `LIGHT_MAP=` and once after), a stable writer artefact
  observed across all 5 corpus files.

  Validated by `tools/parsers/mat.py` against all 5 `.MAT` files: every line is
  consumed, 12 materials / 4,858 bytes.

  Key names are not guessed: they are the literal ASCII labels the writer emits. The
  parser's REQUIRED_KEYS tuple mirrors the sample layout. Field meanings not exposed
  by a name follow CLAUDE.md rule 5 and stay labelled by key.

seq:
  - id: header
    type: header
  - id: sections
    type: section
    repeat: eos

instances:
  separator:
    value: "';' + ('-' * 47)"
    doc: |
      Banner line emitted as the file header and between material blocks. Always
      `;` followed by exactly 47 dashes; length verified across all 5 corpus files.

types:
  header:
    doc: |
      Three fixed lines: banner, `; <path>`, banner. The path comment is the source
      authoring path; the shipped file lives under `Data/`, not the comment path.
    seq:
      - id: banner_top
        contents: [';', '-'.repeat(47)]
        doc: |
          48-character banner: `;` followed by 47 dashes. Verbatim from every corpus file.
      - id: path_comment
        type: line
      - id: banner_bottom
        contents: [';', '-'.repeat(47)]

  line:
    doc: A single line of text without the trailing newline.
    seq:
      - id: value
        type: str
        size-eos: true
        encoding: latin1
        terminator: 0x0a

  section:
    doc: |
      Either a banner separator line (possibly empty) or a material block. The first
      line of a material block is `MATERIAL="<name>"`; everything that follows is
      fixed-shape `KEY=VALUE` lines in the documented order.
    seq:
      - id: first_line
        type: line
      - id: body
        type: material
        if: first_line.value.starts_with("MATERIAL=")

  material:
    doc: |
      A 16-line material block. Two `REFLECTION=` lines are part of the fixed shape;
      the writer emits them unconditionally in every corpus sample.
    seq:
      - id: name_line
        type: kv_line
        doc: 'MATERIAL="<name>".'
      - id: type_line
        type: kv_line
        doc: |
          TYPE=<type>. Two observed values: `MATERIAL_GOURAUD_RGB` and
          `MATERIAL_SELF_ILLUM`.
      - id: ambient
        type: rgb_line
      - id: diffuse
        type: rgb_line
      - id: specular
        type: rgb_line
      - id: light_color
        type: rgb_line
      - id: shininess
        type: int_line
      - id: shininess_strength
        type: int_line
      - id: transparency
        type: int_line
      - id: binary_opacity
        type: int_line
      - id: two_sided
        type: int_line
      - id: tiling
        type: int_line
      - id: texture_map
        type: kv_line
        doc: 'TEXTURE_MAP="<path>".'
      - id: reflection_pre
        type: int_line
        doc: |
          `REFLECTION=` line that appears before `LIGHT_MAP=`. Both pre and post
          `LIGHT_MAP` `REFLECTION` lines exist in the file unconditionally — see
          `reflection_post` and the notes.
      - id: light_map
        type: kv_line
        doc: |
          `LIGHT_MAP="<path>"`. Path may be the empty string `""` when no light map
          is bound.
      - id: reflection_post
        type: int_line
        doc: |
          Trailing `REFLECTION=` line; emits unconditionally. The writer treats the
          two `REFLECTION=` slots as distinct fields even though they share a name.

  kv_line:
    doc: A `KEY=VALUE` line. Keys are fixed ASCII labels.
    seq:
      - id: key
        type: str
        size-eos: true
        encoding: latin1
        terminator: '='
      - id: raw
        type: str
        size-eos: true
        encoding: latin1
        terminator: 0x0a

  rgb_line:
    doc: A `KEY=<r>,<g>,<b>` line; values are 0-255.
    seq:
      - id: key
        type: str
        size-eos: true
        encoding: latin1
        terminator: '='
      - id: values
        type: 'rgb3'
        doc: Three comma-separated `u1` values.

  int_line:
    doc: A `KEY=<int>` line; observed values are non-negative.
    seq:
      - id: key
        type: str
        size-eos: true
        encoding: latin1
        terminator: '='
      - id: value
        type: str
        size-eos: true
        encoding: latin1
        terminator: 0x0a

  rgb3:
    seq:
      - id: r
        type: u1
      - id: _g_sep
        contents: ','
      - id: g
        type: u1
      - id: _b_sep
        contents: ','
      - id: b
        type: u1