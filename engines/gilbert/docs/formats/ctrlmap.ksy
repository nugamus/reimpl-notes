meta:
  id: ctrlmap
  title: Gilbert control map (Data/maps/<room>/ctrl<room>.map), wDx TDxMaps stream
  file-extension: map
  endian: le
doc: |
  Read by TDxMaps.ReadData (Gilbert.exe 0x44f50c) through LoadFromFile (0x44f5c4): the
  magic is read but not checked, then high + 1 map records, each followed by its data
  (E-0011). All 39 files hold one map named "Map". Validator:
  engines/gilbert/tools/parsers/ctrlmap.py.
seq:
  - id: magic
    contents: "ML01"
  - id: high
    type: s4
    doc: number of maps - 1; 0 in the corpus
  - id: maps
    type: map
    repeat: expr
    repeat-expr: high + 1
types:
  map:
    seq:
      - id: name_len
        type: u1
      - id: name
        type: str
        size: name_len
        encoding: windows-1252
      - id: unk_name_tail
        size: 15 - name_len
        doc: string[15] storage beyond the name, uninitialised editor memory
      - id: width
        type: u4
        doc: cells across; a cell is 16x16 pixels of the room picture
      - id: height
        type: u4
      - id: size
        type: u4
        doc: width * height * 10
      - id: unk_ptr
        type: u4
        doc: the editor's buffer pointer, overwritten by the loader
      - id: cells
        type: u4
        repeat: expr
        repeat-expr: width * height
        doc: row-major; values 0..29, meaning open (Q-0002)
      - id: unk_tail
        size: size - 4 * width * height
        doc: zero, except 4 stray bytes in 5 files
