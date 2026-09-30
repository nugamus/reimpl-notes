meta:
  id: gamedat
  title: Gilbert game database / saved game (MFC 6 CArchive written by ge.dll)
  file-extension: dat
  endian: le
  encoding: windows-1252
doc: |
  default.dat (and GESaveFile's saves): the game object's header, then 17 CObLists.
  Load 0x100031f0, save 0x100034e0 in ge.dll; evidence E-0100..E-0106.
  Kaitai cannot keep MFC's load array (classes and objects numbered in load order), so
  each list is typed by the one class ge.dll's text loaders put in it (checked by
  gamedat.py). An object reference (tag without 0x8000) has no body; default.dat has none.
seq:
  - id: walkmap_first
    type: u4
    doc: current walkmap ID when saved; read into +4, then overwritten by `walkmap`
  - id: start_x
    type: u4
    doc: +8, passed to GotoWalkmap by GEContinueGame (from an EXE callback when saved)
  - id: start_y
    type: u4
    doc: +0xc, as start_x
  - id: unk_10
    type: u4
    doc: +0x10, GotoWalkmap's fourth argument; saved as 0
  - id: num_vars
    type: u4
    valid: 200
  - id: vars
    type: s4
    repeat: expr
    repeat-expr: num_vars
    doc: game variables +0x4c (GEGetVariable / GESetVariable, event types 18..20)
  - id: walkmap
    type: u4
    doc: +4, current walkmap ID
  - {id: walkmaps, type: oblist(kind::walkmap), doc: "+0x36c"}
  - {id: inventory, type: oblist(kind::obj), doc: "+0x2f1d4, objects in the inventory"}
  - {id: useobjs, type: oblist(kind::use_obj), doc: "+0x2f20c"}
  - {id: events, type: oblist(kind::event), doc: "+0x2f228"}
  - {id: dialogs, type: oblist(kind::dialog), doc: "+0x2f244"}
  - {id: texts, type: oblist(kind::text), doc: "+0x2f264"}
  - id: num_books
    type: u4
    valid: 10
  - id: books
    type: oblist(kind::topic)
    repeat: expr
    repeat-expr: num_books
    doc: +0x2f280 + 0x1c * book type
  - {id: anims, type: oblist(kind::anim), doc: "+0x2fa24"}
enums:
  kind:
    1: walkmap
    2: cua
    3: obj
    4: obj_state
    5: use_obj
    6: event
    7: dialog
    8: dialog_choice
    9: text
    10: topic
    11: anim
types:
  cstring:
    doc: CArchive >> CString (0x1001ade2); the Unicode marker 0xfffe is not handled
    seq:
      - id: len8
        type: u1
      - id: len16
        type: u2
        if: len8 == 0xff
      - id: len32
        type: u4
        if: len8 == 0xff and len16 == 0xffff
      - id: value
        type: str
        size: 'len8 != 0xff ? len8 : len16 != 0xffff ? len16 : len32'
  count:
    doc: CArchive::ReadCount (0x1001b3ba)
    seq:
      - id: n16
        type: u2
      - id: n32
        type: u4
        if: n16 == 0xffff
    instances:
      value:
        value: 'n16 != 0xffff ? n16 : n32'
  oblist:
    doc: CObList::Serialize (0x1001565f)
    params:
      - id: kind
        type: u1
        enum: kind
    seq:
      - id: count
        type: count
      - id: items
        type: mfc_object(kind)
        repeat: expr
        repeat-expr: count.value
  mfc_object:
    doc: CArchive::ReadObject (0x1001a90c) / ReadClass (0x1001ab44)
    params:
      - id: kind
        type: u1
        enum: kind
    seq:
      - id: tag
        type: u2
        doc: 0xffff new class; 0x8000|n class n; 0x7fff big tag; else object reference n (0 = NULL)
      - id: big_tag
        type: u4
        if: tag == 0x7fff
      - id: new_class
        type: class_def
        if: tag == 0xffff
      - id: body
        if: has_body
        type:
          switch-on: kind
          cases:
            kind::walkmap: walkmap
            kind::cua: cua
            kind::obj: obj
            kind::obj_state: obj_state
            kind::use_obj: use_obj
            kind::event: event
            kind::dialog: dialog
            kind::dialog_choice: dialog_choice
            kind::text: text
            kind::topic: topic
            kind::anim: anim
    instances:
      has_body:
        value: 'tag == 0x7fff ? (big_tag & 0x80000000) != 0 : (tag & 0x8000) != 0'
  class_def:
    doc: CRuntimeClass::Load; schema 1 for all 11 classes
    seq:
      - id: schema
        type: u2
      - id: name_len
        type: u2
      - id: name
        type: str
        size: name_len
        encoding: ASCII
  walkmap:
    doc: CWalkmap::Serialize 0x1000acb0
    seq:
      - {id: cuas, type: oblist(kind::cua), doc: "+0x1c"}
      - {id: id, type: u4, doc: "+4"}
      - {id: title, type: cstring, doc: "+8, GEWalkmapGetTitle"}
      - {id: radar_left, type: s4, doc: "+0xc; GEWalkmapGetRadarRect"}
      - {id: radar_top, type: s4, doc: "+0x10"}
      - {id: radar_right, type: s4, doc: "+0x14"}
      - {id: radar_bottom, type: s4, doc: "+0x18"}
  cua:
    doc: CCUA::Serialize 0x10001720
    seq:
      - {id: objs, type: oblist(kind::obj), doc: "+0x20"}
      - {id: id, type: u4, doc: "+8"}
      - {id: name, type: cstring, doc: "+0xc"}
      - {id: first_event, type: u4, doc: "+0x10, run by GotoCUA while first_visit is set"}
      - {id: event, type: u4, doc: "+0x14, run by GotoCUA on later visits"}
      - {id: end_event, type: u4, doc: "+0x18, run by GECUAEnd"}
      - {id: first_visit, type: u4, doc: "+0x1c, 1 until the first visit"}
  obj:
    doc: CObj::Serialize 0x10009e90
    seq:
      - {id: states, type: oblist(kind::obj_state), doc: "+0x14"}
      - {id: cua_id, type: u4, doc: "+8"}
      - {id: id, type: u4, doc: "+0xc; object code = id * 100 + state"}
      - {id: visible, type: u4, doc: "+0x10, event types 15/16 set/clear it"}
      - {id: state, type: u4, doc: "number of the current state (+0x30 points to it)"}
  obj_state:
    doc: CObjState::Serialize 0x1000a230
    seq:
      - {id: state, type: u4, doc: "+4"}
      - {id: name, type: cstring, doc: "+8"}
      - {id: walkmap_anim, type: u4, doc: "+0xc, CAnim ID on the walkmap"}
      - {id: cua_anim, type: u4, doc: "+0x10, CAnim ID in the CUA"}
      - {id: click_event, type: u4, doc: "+0x14, GEClickObjectInCUA"}
      - {id: take_event, type: u4, doc: "+0x18, GEObjectToInventory"}
      - {id: unk_1c, type: u4, doc: "+0x1c, returned by GE*GetObjectData"}
      - {id: pickable, type: u4, doc: "+0x20, event types 12/13"}
      - {id: text, type: cstring, doc: "+0x24, returned by GE*GetObjectData"}
  use_obj:
    doc: CUseObj::Serialize 0x1000a980
    seq:
      - {id: obj, type: u4, doc: "+4, object code used"}
      - {id: target, type: u4, doc: "+8, object code used on"}
      - {id: event, type: u4, doc: "+0xc"}
  event:
    doc: CEvent::Serialize 0x10002100; meaning per type in README.md
    seq:
      - {id: id, type: u4, doc: "+4"}
      - {id: type, type: u4, doc: "+8"}
      - {id: cond, type: u4, doc: "+0xc"}
      - {id: var, type: u4, doc: "+0x10"}
      - {id: value, type: s4, doc: "+0x14"}
      - {id: jump, type: u4, doc: "+0x18"}
      - {id: walkmap, type: u4, doc: "+0x1c"}
      - {id: cua, type: u4, doc: "+0x20"}
      - {id: obj, type: u4, doc: "+0x24"}
      - {id: book, type: u4, doc: "+0x28"}
      - {id: topic, type: u4, doc: "+0x2c"}
      - {id: topic2, type: u4, doc: "+0x30"}
      - {id: dialog, type: u4, doc: "+0x34"}
      - {id: sound_38, type: u4, doc: "+0x38"}
      - {id: sound_3c, type: u4, doc: "+0x3c"}
      - {id: sound_name, type: cstring, doc: "+0x40"}
      - {id: sound_44, type: u4, doc: "+0x44"}
      - {id: unk_48, type: u4, doc: "+0x48"}
      - {id: video, type: cstring, doc: "+0x4c"}
      - {id: x, type: u4, doc: "+0x50"}
      - {id: y, type: u4, doc: "+0x54"}
      - {id: unk_58, type: u4, doc: "+0x58"}
      - {id: comment, type: cstring, doc: "+0x5c"}
  dialog:
    doc: CDialogs::Serialize 0x10001da0
    seq:
      - {id: choices, type: oblist(kind::dialog_choice), doc: "+4"}
      - {id: id, type: u4, doc: "+0x20"}
      - {id: title, type: cstring, doc: "+0x24, GEDialogGetTitle"}
      - {id: text, type: cstring, doc: "+0x28, GEDialogGetText"}
  dialog_choice:
    doc: CDialogChoice::Serialize 0x10001aa0
    seq:
      - {id: unk_04, type: u4, doc: "+4"}
      - {id: text, type: cstring, doc: "+8, GEDialogGetChoice"}
      - {id: event, type: u4, doc: "+0xc, GEDialogEnd"}
  topic:
    doc: CTopic::Serialize 0x1000a740
    seq:
      - {id: id, type: u4, doc: "+4"}
      - {id: title, type: cstring, doc: "+8, GEBookGetTopicTitle"}
      - {id: text, type: cstring, doc: "+0xc, GEBookGetTopic; markup in README.md"}
      - {id: shown, type: u4, doc: "+0x10"}
      - {id: index, type: s4, doc: "+0x14, rank among shown topics or -1; recomputed on load"}
  text:
    doc: CText::Serialize 0x1000a4c0
    seq:
      - {id: id, type: u4, doc: "+4"}
      - {id: text, type: cstring, doc: "+8, GETextGetText"}
  anim:
    doc: CAnim::Serialize 0x100011f0
    seq:
      - {id: time, type: u4, doc: "+4, ms into the anim (runtime)"}
      - {id: id, type: u4, doc: "+8"}
      - {id: next, type: u4, doc: "+0xc, anim that follows after duration"}
      - {id: name, type: cstring, doc: "+0x10"}
      - {id: duration, type: u4, doc: "+0x14, ms; 0 = never ends"}
      - {id: unk_18, type: u4, doc: "+0x18"}
      - {id: unk_1c, type: u4, doc: "+0x1c, returned by GE*GetObjectData"}
      - {id: unk_20, type: u4, doc: "+0x20, returned by GE*GetObjectData"}
      - {id: z, type: u4, doc: "+0x24, BuildSort z order"}
      - {id: unk_28, type: u4, doc: "+0x28, returned by GE*GetObjectData"}
      - {id: end_event, type: u4, doc: "+0x2c, run when duration passes"}
