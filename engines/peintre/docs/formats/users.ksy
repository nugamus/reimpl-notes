meta:
  id: users
  title: Mission Sunlight player list (SAVE\USERS.BIN)
  file-extension: bin
  endian: le
doc: |
  Written by 0x418966, read by 0x41889c (E-0402). No file in the corpus, no validator
  (E-0432). Spec: engines/peintre/docs/spec/save.md.
seq:
  - id: num_players
    type: u4
    doc: 0..5 players
  - id: players
    type: player
    repeat: expr
    repeat-expr: num_players
types:
  player:
    seq:
      - id: name
        type: strz
        size: 32
        encoding: windows-1252
        doc: at most 20 characters typed on the player-name screen
      - id: volume
        type: s4
        doc: DirectSound attenuation in 1/100 dB, (percent - 100) * 50; 0 = full
      - id: view_size
        type: u4
        doc: 0..3 = 3D view 640x480, 512x384, 400x300, 320x240
