meta:
  id: x3d_save_chunks
  title: Monet save-file chunk payloads (Save/*.bin, Save/User_<i>/Gamesave.<n>)
  endian: le
  encoding: windows-1252

doc: |
  Payloads of the chunks in the save files; the files themselves are the `.BIN` chunk
  container (E-0025, binchunk.py), so each type below is one chunk's payload, named by
  the chunk. Writers and readers: E-0181..E-0183; behaviour: docs/engine-spec/save.md.
  Strings are fixed-size and NUL-terminated; bytes after the NUL are writer garbage.
  `#ACTIONS#`, `#ANIMATIONS#` and `#PORTEF#` are sized by the chunk (read to its end).

  Validated by `tools/parsers/savegame.py` over the samples of two runs of the original
  (`traces/save/`, not in git): 2/2 Gamesave files, 7/7 Info/InfoPara/USERINFO files,
  every byte consumed; `--selftest`.

types:
  current:          # #CURRENT#, Save/Info.bin
    seq:
      - id: player
        type: u2
  filter:           # #FILTER#, Save/InfoPara.bin
    seq:
      - id: bilinear
        type: u4
        doc: 0 = point sampling, otherwise bilinear.
  userinfo:         # #USERINFO#, Save/User_<i>/Info.bin
    seq:
      - id: name
        type: strz
        size: 64
      - id: unit
        type: u2
        doc: Unit number of the player's last save (0 when created).
  game:             # #GAME#, always the first chunk at offset 0
    seq:
      - id: name
        type: strz
        size: 64
      - id: unit
        type: u2
      - id: scene
        type: strz
        size: 20
  scene:            # #SCENE#
    seq:
      - id: ambient
        size: 3
        doc: r, g, b
      - id: unk_pad
        type: u1
  cursor:           # #CURSOR#
    seq:
      - id: image
        type: strz
        size: 30
      - id: mode
        type: u4
      - id: pending
        type: u4
  actions:          # #ACTIONS#
    seq:
      - id: exhausted
        type: u4
        repeat: expr
        repeat-expr: 256
      - id: runs
        type: u4
        repeat: expr
        repeat-expr: 256
      - id: conditions
        type: strz
        size: 256
        repeat: eos
  camera:           # #CAMERA#
    seq:
      - id: pos
        type: f4
        repeat: expr
        repeat-expr: 3
      - id: unk_w
        type: u4
      - id: yaw
        type: f4
      - id: pitch
        type: f4
      - id: sphere_radius
        type: f4
      - id: sphere_z
        type: f4
      - id: can_move
        type: u4
      - id: can_turn
        type: u4
      - id: collide
        type: u4
      - id: eye_height
        type: f4
  objects:          # #OBJECTS#: same records as INFOOBJ.BIN (infoobj.ksy entry)
    seq:
      - id: count
        type: u4
      - id: entries
        size: 68
        repeat: expr
        repeat-expr: count
  animations:       # #ANIMATIONS#
    seq:
      - id: nodes
        type: anim_node
        repeat: eos
  anim_node:
    seq:
      - id: name
        type: strz
        size: 64
      - id: count
        type: u2
      - id: active
        type: u2
      - id: slots
        type: anim_slot
        repeat: expr
        repeat-expr: count
  anim_slot:
    seq:
      - id: slot
        type: u2
      - id: path
        type: strz
        size: 260
      - id: name
        type: strz
        size: 64
      - id: enabled
        type: u4
      - id: paused
        type: u4
      - id: loop
        type: u4
      - id: pingpong
        type: u4
      - id: backward
        type: u4
      - id: frame
        type: f4
      - id: fps
        type: f4
      - id: first
        type: u4
      - id: last
        type: u4
      - id: unk_1cc
        type: u4
      - id: unk_1d0
        type: u4
  jauge:            # #JAUGE#
    seq:
      - id: name
        type: strz
        size: 30
      - id: visible
        type: u4
      - id: duration_ms
        type: u4
      - id: elapsed_ms
        type: u4
  portef:           # #PORTEF#
    seq:
      - id: last_index
        type: s4
      - id: items
        type: strz
        size: 30
        repeat: expr
        repeat-expr: last_index + 1
  train_changed:    # #TRAIN_CHANGED# (U01)
    seq:
      - id: train2_loaded
        type: u4
      - id: on_train
        type: u4
  timevendeuse:     # #TIMEVENDEUSE# (U02, u02.md)
    seq:
      - id: call_start
        type: u4
        doc: raw timeGetTime value (Q-0092)
      - id: call_period
        type: u4
      - id: call_off
        type: u4
      - id: magpie
        type: u4
  params:           # #PARAMS# (U04): unit +0x6ec, +0x6e8, +0x6e4
    seq:
      - id: unk
        type: u4
        repeat: expr
        repeat-expr: 3
  planche:          # #PLANCHE# (U07): unit +0x6c8
    seq:
      - id: unk
        type: u4
