meta:
  id: china_sav
  title: China save game (Data/Saved/_game<n>.sav, Data/Saved/<NAME>.sav)
  endian: le
doc: |
  Specced from CHINE.EXE only (no save in the corpus). Written by Save::write
  0x4115b0 (automatic) / 0x4117b0 (named), read back by Save::read 0x4114b0 / 0x4116b0,
  each block by its own routine in this order. E-0208.
  Validator: engines/cryomni3d/tools/parsers/sav.py (selftest round trip; --tables prints
  the variable and object names from the executable).
seq:
  - id: variables
    type: u4
    repeat: expr
    repeat-expr: 227
    doc: |
      The value field of each entry of the variable table at 0x45eec4 (12-byte entries
      {name, value, id}), in table order (Vars::write 0x420170). Entries 0..219 are
      named (MODE_VISITE, CHAPITRE, ...), 220..224 have an empty name, 225 is the
      id-0 terminator, and the 227th dword lies past the table (padding before the name
      strings), always 0 in a fresh game.
  - id: objects
    type: object
    repeat: expr
    repeat-expr: 36
    doc: |
      The first two dwords of each 0x30-byte entry of the object table at 0x45d5e4
      (Objects::write 0x417d40): 35 objects (LISTE_BOITES .. CLE_JARRE), then 8 bytes
      past the table.
  - id: place
    size: 256
    type: strz
    encoding: windows-1252
    doc: |
      The current place's name (Save::placeName 0x41f3c0), NUL-terminated; the bytes
      after the NUL are whatever was on the stack.
  - id: view_0
    type: f4
    doc: View angle 0x53485c (passed first to 0x441df0).
  - id: view_1
    type: f4
    doc: View angle 0x534844 (passed second to 0x441df0).
  - id: num_minutes
    type: u4
    doc: Minutes the player holds (0x500e88); the game has 50 slots and never checks.
  - id: minutes
    type: minute
    repeat: expr
    repeat-expr: num_minutes
types:
  object:
    seq:
      - id: unk_0
        type: u4
        doc: 0 in the initial table.
      - id: unk_4
        type: s4
        doc: -1 in the initial table.
  minute:
    seq:
      - id: len
        type: u4
      - id: id
        size: len
        type: str
        encoding: windows-1252
        doc: A MINUTES.TXT id, no NUL; read into a 15-byte slot (Minutes::read 0x412510).
