meta:
  id: wxi
  title: Gilbert DelphiX collection (.wxi pictures, .wxs/.dxw waves)
  endian: le
doc: |
  A 16-bit Windows resource entry (RCDATA) around a Delphi binary component stream
  (TPF0) of a DelphiX TPictureCollectionComponent or TWaveCollectionComponent (E-0010).
  The stream is a generic property tree, so this spec stops at the TPF0 body; the
  validator engines/gilbert/tools/parsers/wxi.py walks the properties, the TDIB picture
  data and the RIFF waves, consuming every byte (242/242 files).
seq:
  - id: res_type_marker
    contents: [0xff]
  - id: res_type
    contents: [0x0a, 0x00]
    doc: RT_RCDATA by ordinal
  - id: res_name
    type: strz
    encoding: ascii
    doc: WDXPICTURECOLLECTION, DELPHIXPICTURECOLLECTION or DELPHIXWAVECOLLECTION
  - id: res_flags
    type: u2
    doc: 0x1030 in all files
  - id: body_size
    type: u4
  - id: body
    type: tpf0
    size: body_size
types:
  sstr:
    seq:
      - id: len
        type: u1
      - id: value
        type: str
        size: len
        encoding: windows-1252
  tpf0:
    seq:
      - id: magic
        contents: "TPF0"
      - id: class_name
        type: sstr
      - id: object_name
        type: sstr
      - id: properties
        size-eos: true
        doc: |
          Name/value pairs (sstr name, u1 value type, value), ended by an empty name,
          then an empty child list. The only property is "List", a collection (0x0E)
          of items, each 0x01 + properties + 0x00. See formats/README.md.
