meta:
  id: x3d_infoact_actions
  title: X3D per-unit action table (`#ACTIONS#` chunk of INFOACT.BIN), 4X Technologies
  endian: le
  encoding: latin1

doc: |
  Payload of the `#ACTIONS#` chunk, the only chunk of `Data/U##/INFOACT.BIN` (the `.BIN`
  chunk container is E-0025). Read by `Scene_LoadActions` (`0x0041da90`): `u32 count`,
  then `count * 0x440` bytes, one action per record (`FUN_0041e020`). Behaviour of the
  fields is in `engines/x3d/docs/spec/interaction.md` (E-0071, E-0073). Strings are
  NUL-terminated; bytes after the NUL are writer garbage (0xCD).

  Validated by `engines/x3d/tools/parsers/infoact.py`: 9/9 files, 198 records, every byte consumed.

seq:
  - id: count
    type: u4
  - id: actions
    type: action
    repeat: expr
    repeat-expr: count

types:
  action:
    seq:
      - id: id
        type: u4
        doc: Slot in the unit's action table; conditions name actions by it (`M02` = 2).
      - id: name
        type: strz
        size: 30
        doc: "`M01`, `M02`, ...; steps 14..16 find actions by it."
      - id: condition
        type: strz
        size: 258
        doc: "`TRUE`, `FALSE`, or an expression over other actions' exhausted flags (`M11 & !M15`)."
      - id: max_runs
        type: s4
        doc: Exhausted after this many runs; 100 or more = never.
      - id: trigger
        type: u4
        doc: 7 = the held item used on the hotspot, 8 = plain click; others never fire from a click.
      - id: item
        type: strz
        size: 32
        doc: Held item name for trigger 7 (`U01_05`).
      - id: hotspot_type
        type: u4
        doc: Must equal the hotspot's INFOOBJ `type`.
      - id: hotspot
        type: strz
        size: 32
        doc: Hotspot the action is attached to (`U01_04`, matched against `*U01_04`).
      - id: target_type
        type: u4
        doc: 6 = character target for op 1.
      - id: target
        type: strz
        size: 32
        doc: Hotspot the steps act on.
      - id: step_count
        type: u4
        doc: Number of used steps, at most 10.
      - id: steps
        type: step
        repeat: expr
        repeat-expr: 10
        doc: Only the first `step_count` are used; the rest are garbage.

  step:
    seq:
      - id: op
        type: u4
        doc: Step operation, see interaction.md.
      - id: arg
        type: strz
        size: 64
