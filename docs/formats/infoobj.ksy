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

  Each 68-byte entry is the initial state of one hotspot (E-0072): a 40-byte object name
  followed by seven u32/f32 fields. `FUN_0041d8e0` (Scene_LoadObjectInfo) binds each entry
  to the scene object of that name and applies it with `FUN_004210d0`; the savegame's
  `OBJECTS` chunk (`FUN_0041d6f0`) writes the same layout back from the live state.

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
    doc: One hotspot's initial state (E-0072).
    seq:
      - id: name
        type: strz
        size: 40
        doc: |
          Scene object name, NUL-terminated (`*U01_04`, `*Ernest`); the bytes after the NUL
          are writer garbage (0xCD in every corpus file). Looked up case-insensitively,
          depth first.
      - id: type
        type: u4
        doc: |
          Hotspot type (entry `+0x28`, hotspot `+4`); an INFOACT action applies only when its
          `hotspot_type` equals it. 6 = character (op 1 talks through the character).
          Corpus: 4, 5, 6.
      - id: cursor
        type: u4
        doc: |
          Cursor kind shown over the hotspot (object `+0x128`): 0 default, 2 click,
          3 voice, 4 take, 5 use. Corpus: 0, 2, 3, 4, 5.
      - id: visible
        type: u4
        doc: 0 = hide the object at load (save writes object `+0x5c` == 0).
      - id: anim_frame
        type: f4
        doc: Frame of the object's animation node (node `+0x74`).
      - id: anim_paused
        type: u4
        doc: |
          0 = set the frame (clamped to the animation's range) and leave the node as it is
          (running); otherwise set the frame and pause the node (node `+0x60`).
      - id: anim_fps
        type: u4
        doc: Node frame rate (node `+0x78`, as a float). Corpus: mostly 15.
      - id: anim_loop
        type: u4
        doc: Node loop flag (node `+0x68`).

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
