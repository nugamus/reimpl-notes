meta:
  id: ring_at2
  title: Ring engine archive (.at2 Ring, .at3 Prophet)
  file-extension: [at2, at3]
  endian: le
  encoding: windows-1252
doc: |
  Zone archive of the Ring engine. Read by aArt::Init (Ring DVD 0x4194d0, Prophet
  0x41e470) and aArt::GetRec (0x4198e0 / 0x41e880). Members are stored back to back in
  directory order from the end of the directory to the end of the file. The archive does
  not decompress: unpacked_size is the size the member's own format expands to.
  Evidence: engines/ring/docs/EVIDENCE.md E-0016. Validator:
  engines/ring/tools/parsers/at2.py.
seq:
  - id: magic
    size: 8
    doc: '"AT_II\0\0\0" in .at2 (Ring), "ATIII\0\0\0" in .at3 (Prophet)'
  - id: dir_size
    type: u4
    doc: count * 255
  - id: count
    type: u4
  - id: record_size
    type: u4
    doc: always 255
  - id: unk_zero
    type: u4
    repeat: expr
    repeat-expr: 3
    doc: 0 in every archive of the corpus
  - id: records
    type: record
    repeat: expr
    repeat-expr: count
types:
  record:
    seq:
      - id: name
        type: strz
        size: 243
        doc: path inside the zone, e.g. "\image\end.bmp", NUL-padded
      - id: offset
        type: u4
      - id: size
        type: u4
      - id: unpacked_size
        type: u4
        doc: equals size for members stored raw
    instances:
      data:
        io: _root._io
        pos: offset
        size: size
