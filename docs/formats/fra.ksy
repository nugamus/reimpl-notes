meta:
  id: monet_fra
  title: 2D frame (.FRA), Monet / X3D game layer (LFrameReader)
  file-extension: fra
  endian: le
  encoding: latin1

doc: |
  One 2D screen: a list of view objects, each followed by a property list. Read by
  `LFrameReader` (`LFrameReader.cpp:97`, 0x0042d290: `Data/2DFRA/<name>.fra`, whole file
  into memory) and built by `LClassCreator` (`LClassCreator.cpp:128`, 0x0042e4e0): for each
  object read a class tag, construct that class (its constructor reads the body), then
  read property tags until a 0 tag. Tags are MSVC multi-character constants registered by
  0x0042aab0; the file stores them little-endian, so '#BIT' appears as "TIB#". E-0100.

  Validated by tools/parsers/fra.py: 25/25 corpus files, every byte consumed.

seq:
  - id: num_objects
    type: u4
  - id: objects
    type: object
    repeat: expr
    repeat-expr: num_objects

types:
  object:
    seq:
      - id: tag
        type: str
        size: 4
      - id: view
        type: view
      - id: body
        type:
          switch-on: tag
          cases:
            '"TIB#"': bitmap
            '"POL#"': magnifier
            '"RCS#"': scroll
            '"AOL#"': scroll
            '"VAS#"': scroll
            '"cSU#"': scroll
            '"loV#"': vol
            '"BoV#"': vol
            '"AoV#"': vol
            '"nCC#"': video
            '"nIC#"': video
        # EIV# vop# bop# idE# dEU# dES#: no body beyond the view
      - id: props
        type: prop
        repeat: until
        repeat-until: _.tag == 0

  view:
    doc: '#VIE constructor 0x004342f0 reads 0x24 bytes.'
    seq:
      - id: id
        type: s4
        doc: looked up by the game (frame vtable +0x38(id))
      - id: x
        type: s4
      - id: y
        type: s4
      - id: w
        type: s4
        doc: 0 on a bitmap view means "bitmap width + bmp_dx" (0x004240c0)
      - id: h
        type: s4
      - id: visible
        type: s4
        doc: view +0x38; draw (0x00434480) and hit test (0x00426a00) require it; 1 in all 106
      - id: parent
        type: s4
        doc: id of the parent view, 0 = none; a child moves with its parent (0x00434670)
      - id: unk_7
        type: s4
        doc: view +0x3c; 1 = descendants are clipped to this view (0x00434530, E-0602)
      - id: unk_8
        type: s4
        doc: view +0x40; 1 = not clipped to ancestors (E-0602); 0 in all 106

  bitmap:
    doc: '#BIT constructor 0x00423ea0 reads 0x2c bytes.'
    seq:
      - id: bmp_dx
        type: s4
        doc: added to the view position when drawing (0x00424030)
      - id: bmp_dy
        type: s4
      - id: bitmap
        type: strz
        size: 32
        doc: Data/2DBIT/<name>, ".bmp" appended if no '.'; "0" = no bitmap (0x004240c0)
      - id: unk_blit
        type: s4
        doc: passed to the blit; 96 in all 49 corpus bitmaps

  magnifier:
    doc: '#LOP constructor 0x0042f310: #BIT body, then 8 bytes.'
    seq:
      - id: bitmap
        type: bitmap
      - id: unk_a
        type: s4
      - id: unk_b
        type: s4

  scroll:
    doc: '#SCR constructor 0x004325d0 reads 0x6c bytes (list with scroll bar).'
    seq:
      - id: name_a
        type: strz
        size: 32
        doc: scroll-bar bitmap, as tall as the view, drawn at its right edge (E-0600)
      - id: unk_a
        type: s4
        doc: up-arrow height, +0x54 (33 in the corpus)
      - id: unk_b
        type: s4
        doc: down-arrow height, +0x58 (33)
      - id: name_b
        type: strz
        size: 32
        doc: thumb bitmap
      - id: name_c
        type: strz
        size: 32
        doc: content bitmap of the base class; the three list classes ignore it
      - id: unk_c
        type: s4
        doc: row step, +0x5c; the three list classes replace it with 32

  vol:
    doc: '#Vol constructor 0x00434d30 reads 0x24 bytes.'
    seq:
      - id: unk_a
        type: s4
      - id: name
        type: strz
        size: 32

  video:
    doc: |
      nCC# / nIC#: registered in neither EXE (not in 0x0042aab0, bytes absent from both
      EXEs), so these frames cannot be loaded by the shipped game. Size from the corpus.
    seq:
      - id: unk_a
        type: s4
      - id: file
        type: strz
        size: 32

  prop:
    seq:
      - id: tag
        type: u4
      - id: body
        size: |
          tag == 0x40676375 ? 4 :
          tag == 0x40435552 ? 4 :
          tag == 0x40445241 ? 4 :
          tag == 0x40465241 ? 32 :
          tag == 0x40534352 ? 32 :
          tag == 0x4048494c ? 40 :
          tag == 0x40484947 ? 40 :
          tag == 0x40414e49 ? 56 :
          0
        doc: |
          ucg@ u4 cursor kind (0x00426ac0); RUC@ u4 (0x0042e8b0); ARD@ u4 (0x0042ea30);
          ARF@ char[32] frame name (0x0042d070); RCS@ char[32] command (0x004322f0);
          LIH@ / GIH@ char[32] bitmap + s4 dx + s4 dy (0x0042ec90, 0x0042ef90);
          INA@ 56 bytes (0x0042d4f0). Tag 0 ends the list.
