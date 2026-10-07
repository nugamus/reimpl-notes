meta:
  id: grumpa_abi
  title: Grumpa .abi scene graph / actor database (serialised CFXActorFactory tree)
  file-extension: abi
  endian: le
doc: |
  CFXActorFactory::CreateFromABIFile (FUN_0040cef0, decrypted Grumpa.exe; E-0003,
  E-0100..E-0103, E-0400, E-0401): records of u32 type, u32 id, body (each class's
  Serialize in mode 1) until EOF; a tail shorter than 8 bytes ends the loop and is kept as
  `record.tail`. Bodies are field order and size only; unknown fields are opaque unk_*.
  Recurring classes: EC = 5 u32, CC = 5 u32 + n x EC. Validator:
  engines/grumpa/tools/parsers/abi.py (113/113 in Scenes/ and Actors/); the .ksy also parses the 5 Save/Current
  files (118/118).
seq:
  - id: records
    type: record
    repeat: until
    repeat-until: _io.size - _io.pos < 8
  - id: tail
    size-eos: true
    doc: "0..7 bytes the original never reads"
types:
  record:
    doc: "a record, or the 0..7-byte tail the original never reads (only `tail` set)"
    seq:
      - id: tail
        size-eos: true
        if: _io.size - _io.pos < 8
      - id: type
        type: u4
        if: not _io.eof
      - id: id
        type: u4
        if: not _io.eof
      - id: body
        if: not _io.eof
        type:
          switch-on: type
          cases:
            3: rec_03
            5: rec_05
            7: rec_07
            13: rec_0d
            17: rec_11
            24: rec_18
            42: rec_18
            25: rec_19
            26: rec_1a
            29: rec_1d
            30: rec_1e
            32: rec_20
            33: rec_21
            34: rec_22
            37: rec_22
            35: rec_23
            38: rec_23
            36: rec_24
            39: rec_24
  rec_11:
    doc: "0x11 view (FUN_0043d200)"
    seq:
      - id: unk_head
        size: 12
      - id: ecs
        type: ec_vec
      - id: unk_a
        size: 8
      - id: ccs_a
        type: cc_vec
      - id: ccs_b
        type: cc_vec
      - id: unk_b
        size: 4
      - id: unk_c
        size: 104
  rec_18:
    doc: "0x18 / 0x2a CFXSound (FUN_004492d0)"
    seq:
      - id: unk_head
        size: 12
      - id: ecs
        type: ec_vec
      - id: unk_a
        size: 40
      - id: sub
        type: sub_456d70
      - id: name
        type: pstr
      - id: ccs
        type: cc_vec
  rec_19:
    doc: "0x19 CFXTrigger / CFXSprite (FUN_00457ea0); bubbles only when mode == 2"
    seq:
      - id: unk_head
        size: 12
      - id: ecs
        type: ec_vec
      - id: unk_a
        size: 32
      - id: unk_b
        size: 76
      - id: sub
        type: sub_456d70
      - id: ecs_194
        type: ec_vec
      - id: ccs_128
        type: cc_vec
      - id: path_count
        type: s4
      - id: path_points
        size: 'path_count > 0 ? path_count * 8 : 0'
      - id: unk_c
        size: 16
      - id: unk_d
        size: 4
      - id: mode
        type: u4
      - id: bubble_count
        type: u4
        if: mode == 2
      - id: bubbles
        type: bubble
        repeat: expr
        repeat-expr: bubble_count
        if: mode == 2
  rec_0d:
    doc: "0x0d (FUN_0044ccb0); two extra u32 only when gate == 1"
    seq:
      - id: unk_head
        size: 12
      - id: ecs
        type: ec_vec
      - id: unk_a
        size: 32
      - id: unk_b
        size: 4
      - id: gate
        type: u4
      - id: ccs_150
        type: cc_vec
      - id: sub
        type: sub_456d70
      - id: unk_gated
        size: 8
        if: gate == 1
      - id: ccs_130
        type: cc_vec
      - id: ccs_140
        type: cc_vec
      - id: filename
        type: pstr
  rec_1a:
    doc: "0x1a (FUN_00452100)"
    seq:
      - id: unk_head
        size: 12
      - id: ecs
        type: ec_vec
      - id: unk_a
        size: 72
      - id: sub
        type: sub_456d70
      - id: sub_a
        type: sub_401c00
      - id: sub_b
        type: sub_401c00
      - id: pairs
        type: pair_vec
      - id: ccs
        type: cc_vec
        repeat: expr
        repeat-expr: 8
        doc: 8 CC vectors
      - id: str_a
        type: pstr
      - id: str_b
        type: pstr
  rec_1d:
    doc: "0x1d (FUN_0044a250)"
    seq:
      - id: unk_head
        size: 12
      - id: ecs
        type: ec_vec
      - id: unk_a
        size: 8
      - id: elem_count
        type: u4
      - id: elems
        type: elem_1d
        repeat: expr
        repeat-expr: elem_count
  rec_05:
    doc: "0x05 CFXItem (FUN_0043c4f0)"
    seq:
      - id: unk_head
        size: 16
      - id: anb
        type: pstr
      - id: tex_a
        type: pstr
      - id: tex_b
        type: pstr
      - id: tex_c
        type: pstr
      - id: unk_a
        size: 40
      - id: pairs
        type: pair_vec
  rec_07:
    doc: "0x07 (FUN_00429d40)"
    seq:
      - id: unk_head
        size: 12
      - id: ecs
        type: ec_vec
      - id: unk_a
        size: 4
      - id: name
        type: pstr
      - id: unk_b
        size: 4
      - id: unk_c
        size: 76
      - id: ccs
        type: cc_vec
  rec_20:
    doc: "0x20 (FUN_00434550)"
    seq:
      - id: unk_head
        size: 12
      - id: ecs
        type: ec_vec
      - id: unk_transforms
        size: 80
  rec_21:
    doc: "0x21 (FUN_0042e670)"
    seq:
      - id: unk_head
        size: 12
      - id: ecs_a
        type: ec_vec
      - id: unk_a
        size: 4
      - id: ecs_b
        type: ec_vec
      - id: ccs
        type: cc_vec
  rec_1e:
    doc: "0x1e (FUN_0045b6f0)"
    seq:
      - id: unk_head
        size: 12
      - id: ecs
        type: ec_vec
      - id: unk_a
        size: 24
  rec_22:
    doc: "0x22 / 0x25 (FUN_00428b10)"
    seq:
      - id: unk_head
        size: 12
      - id: ecs
        type: ec_vec
      - id: unk_a
        size: 8
      - id: ccs
        type: cc_vec
  rec_23:
    doc: "0x23 / 0x26 (FUN_00417180)"
    seq:
      - id: unk_head
        size: 12
      - id: ecs
        type: ec_vec
      - id: unk_a
        size: 12
      - id: ccs
        type: cc_vec
  rec_24:
    doc: "0x24 / 0x27 (FUN_00431810)"
    seq:
      - id: unk_head
        size: 12
      - id: ecs
        type: ec_vec
      - id: unk_a
        size: 4
      - id: ccs
        type: cc_vec
  rec_03:
    doc: "0x03 CFXCharacter (FUN_00422f80, arm 0x4231f0); the id is re-read by Serialize so only two more u32 follow (abi.py t_03)"
    seq:
      - id: unk_head
        size: 8
      - id: n_u32
        type: u4
      - id: u32s
        size: n_u32 * 4
      - id: unk_a
        size: 4
      - id: unk_b
        size: 24
      - id: unk_c
        size: 20
      - id: rule_count
        type: u4
      - id: rules
        type: class_d
        repeat: expr
        repeat-expr: rule_count
      - id: ccs_640
        type: cc_vec
      - id: ccs_650
        type: cc_vec
      - id: msg_count
        type: u4
      - id: msgs
        type: msg
        repeat: expr
        repeat-expr: msg_count
      - id: ccs_630
        type: cc_vec
      - id: react_count
        type: u4
      - id: reacts
        type: react
        repeat: expr
        repeat-expr: react_count
      - id: unk_d
        size: 4
      - id: anbs
        type: names
      - id: wavs
        type: names
      - id: unk_e
        size: 4
      - id: tgas
        type: names
      - id: attach_count
        type: u4
      - id: attaches
        type: attach
        repeat: expr
        repeat-expr: attach_count
      - id: unk_f
        size: 12
      - id: pairs
        type: pair_vec
  elem_1d:
    doc: "one 0x1d element (stride 0x12c)"
    seq:
      - id: sub
        type: sub_401c00
      - id: n
        type: u4
      - id: run
        size: n * 4
  bubble:
    doc: "0x19 bubble"
    seq:
      - id: unk_a
        size: 8
      - id: has_name
        type: u4
      - id: name
        type: pstr
        if: has_name != 0
  msg:
    doc: "0x03 message (shown by opcode 0x44)"
    seq:
      - id: text
        type: pstr
      - id: commands
        type: cc_vec
  react:
    doc: "0x03 reaction (AddReactCharacter)"
    seq:
      - id: other_id
        type: u4
      - id: commands
        type: cc_vec
  attach:
    doc: "0x03 carried object"
    seq:
      - id: anb
        type: pstr
      - id: tga
        type: pstr
      - id: unk_a
        size: 12
  names:
    doc: "u32 n, n pascal strings"
    seq:
      - id: count
        type: u4
      - id: items
        type: pstr
        repeat: expr
        repeat-expr: count
  class_d:
    doc: "ClassD (FUN_00409cf0): EC vector + CC vector"
    seq:
      - id: ecs
        type: ec_vec
      - id: ccs
        type: cc_vec
  ec:
    doc: "EC (FUN_00409920): 5 u32"
    seq:
      - id: unk_a
        size: 20
  cc:
    doc: "CC (FUN_00409150): 5 u32, n, n x EC"
    seq:
      - id: unk_a
        size: 20
      - id: n
        type: u4
      - id: ecs
        type: ec
        repeat: expr
        repeat-expr: n
  ec_vec:
    doc: "u32 n; n x EC"
    seq:
      - id: n
        type: u4
      - id: items
        type: ec
        repeat: expr
        repeat-expr: n
  cc_vec:
    doc: "u32 n; n x CC"
    seq:
      - id: n
        type: u4
      - id: items
        type: cc
        repeat: expr
        repeat-expr: n
  pair_vec:
    doc: "u32 n; n x (u32, u32)"
    seq:
      - id: n
        type: u4
      - id: items
        size: n * 8
  pstr:
    doc: "pascal string (FUN_00430c50): s32 len, len bytes only when len > 0"
    seq:
      - id: len
        type: s4
      - id: data
        size: 'len > 0 ? len : 0'
  sub_456d70:
    doc: "embedded object (ctor 0x456cf0): 14 u32"
    seq:
      - id: unk_a
        size: 56
  sub_401c00:
    doc: "embedded object (ctor 0x401bb0): 2 x 0xc"
    seq:
      - id: unk_a
        size: 24
