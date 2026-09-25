meta:
  id: x3d_infoobj_bin
  title: X3D per-unit object-info container (.INFOOBJ.BIN), 4X Technologies
  file-extension: bin
  endian: le
  encoding: latin1

doc: |
  Per-unit object-info container. One file per `U##` subdirectory of `Data/`. Read by
  two loaders in `MissionMonet.exe`:

    * `FUN_0041d490` (`0x0041d490`) — opens INFOOBJ.BIN and dispatches to the OBJECTS sub-loader
    * `FUN_0041d6f0` (`0x0041d6f0`) — the OBJECTS sub-loader itself

  `FUN_0041d6f0` is the loader that pins the format. It does:

      FUN_00415190(this, "OBJECTS")             # seek to OBJECTS tag
      FUN_004153a0(this, &count, 4)             # u32 count
      FUN_004153a0(this, buf, count * 0x44)     # raw bytes; 68 bytes per entry
      FUN_00415180(this)                        # close the section

  The trailing `#OBJECTS#` terminator carries `count = 0`, so the loader returns early
  there. The real entries sit in a fixed prefix before that terminator, with no leading
  section tag of their own. Every corpus file follows exactly:

      [u32 count][count * 68-byte entries][32-byte terminator]

  where the terminator is

      [10 b "#OBJECTS#\0"][10 b 0xCD pad][u32=0][u32=obj_offset][u32=1]

  and `obj_offset` is the file offset of the `#OBJECTS#` tag itself (a back-reference).

  Each 68-byte entry is:

      [8  b NUL-terminated name, e.g. "*U04_03\0"]
      [32 b reserved: 0xCD on every corpus file — MSVC uninitialised-heap pattern]
      [4  b u32 field_a]
      [4  b u32 field_b]
      [4  b u32 field_c]
      [4  b f32 field_d]
      [4  b u32 field_e]
      [4  b u32 field_f]
      [4  b u32 field_g]

  Entry names mirror the per-unit scene asset names (`*U04_03`, `*Ernest`, `*U02_06a`,
  ...). The reserved 32 bytes are written by the engine to disk as 0xCD but the runtime
  loader overwrites entry offset `+0x2C` (byte 44, field_b) with a pointer to the loaded
  object's handle, so this slot is repurposed as a pointer at runtime. The seven numeric
  fields after the reserved block are not yet understood — their meaning is opaque
  (see OPEN-QUESTIONS). The reserved 32 bytes and the seven trailing fields are kept in
  the spec as raw bytes/ints so the validator can detect any future deviation.

  Validated by `tools/parsers/infoobj.py` against all 9 `INFOOBJ.BIN` files in the corpus:
  every file parses, every byte is consumed. Totals: 183 entries, 12,768 bytes.

seq:
  - id: count
    type: u4
    doc: Number of object-info entries that follow.
  - id: entries
    type: entry
    repeat: expr
    repeat-expr: count
  - id: terminator
    type: terminator

types:
  entry:
    doc: |
      One 68-byte object-info record. The seven numeric fields after the reserved block
      carry per-object state; their semantic names are unknown.
    seq:
      - id: name
        type: strz
        size: 8
        doc: |
          NUL-terminated object name, padded to 8 bytes. Examples from the corpus:
          `*U04_03`, `*Ernest`, `*U02_06a`, `*Eteint01`. The leading `*` is consistent
          across every corpus file.
      - id: reserved
        size: 32
        doc: |
          Fixed 32-byte region. Every byte is `0xCD` in every corpus file — MSVC's
          uninitialised-heap pattern (`0xCDCDCDCD`). The runtime loader overwrites the
          first 4 bytes of this region (entry offset `+0x2C`, see `field_b`) with a
          pointer to the loaded object's handle, so this slot becomes a pointer at
          runtime even though the on-disk value is meaningless. Left as raw bytes here
          so the validator surfaces any deviation.
      - id: field_a
        type: u4
        doc: Entry offset `+0x28`. Values seen in the corpus: 4, 5, 6.
      - id: field_b
        type: u4
        doc: |
          Entry offset `+0x2C`. The on-disk value is overwritten at runtime with a
          pointer, so its semantic meaning is that of a runtime pointer rather than an
          integer. On-disk values seen in the corpus: 0, 2, 3, 4, 5.
      - id: field_c
        type: u4
        doc: Entry offset `+0x30`. Mostly `1` in the corpus (180/183 entries).
      - id: field_d
        type: f4
        doc: |
          Entry offset `+0x34`. Almost always `1.0`; one entry in U01 has `20.0`. Looks
          like a scalar parameter rather than a flag.
      - id: field_e
        type: u4
        doc: Entry offset `+0x38`. Mostly `1` in the corpus.
      - id: field_f
        type: u4
        doc: |
          Entry offset `+0x3C`. Mostly `15` in the corpus (170/183 entries), with outliers
          of `0`, `2`, `4`, `50`. The strong mode at 15 looks like a default category ID
          or a type tag.
      - id: field_g
        type: u4
        doc: Entry offset `+0x40`. Mostly `1` in the corpus (139/183), with `0` in the
          rest. Looks like a boolean flag.

  terminator:
    doc: |
      32-byte fixed footer. The `obj_offset` field is a back-reference to the file
      offset of the embedded `#OBJECTS#` tag (i.e. the offset of this terminator
      itself). `terminator_count` is always `0` — the loader short-circuits on a zero
      count, so this terminator is the EOF marker.
    seq:
      - id: tag
        type: strz
        size: 10
        doc: |
          Literal bytes `#OBJECTS#\0`. The `#` framing is on disk; the loader compares
          only against the inner `OBJECTS` substring (`s_OBJECTS` at `0x00441bc0`).
      - id: pad
        size: 10
        doc: |
          10 bytes of `0xCD` padding — same MSVC uninit pattern as `entry.reserved`,
          preserved here as raw bytes for the validator.
      - id: terminator_count
        type: u4
        doc: Always `0`; the loader returns `1` immediately on a zero count.
      - id: obj_offset
        type: u4
        doc: File offset of the `tag` field above (back-reference). Useful as a sanity
          check — must equal `4 + count * 68`.
      - id: flag
        type: u4
        doc: Always `1` in every corpus file. Probably a `has_more` flag.
