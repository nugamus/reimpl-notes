# Formats (Gilbert engine)

One row per recovered format: status here, the Kaitai spec next to it (`<fmt>.ksy`), the
validator in `engines/gilbert/tools/parsers/<fmt>.py` (with `--selftest`), the proof in
`EVIDENCE.md`. A format is done only when its validator passes 100% of that type in
`games/gilbert/discs/cd`, every byte consumed.

| Format | Files | Validator | Spec | Evidence | Status |
|---|---:|---|---|---|---|
| `.wxi` picture collection | 234 (2,482 pictures) | `wxi.py` | `wxi.ksy` | E-0010 | done |
| `.wxs` / `.dxw` wave collection | 4 + 4 (identical pairs; 58 waves) | `wxi.py` | `wxi.ksy` | E-0010 | done (tail byte Q-0001) |
| `ctrl<room>.map` control map | 39 | `ctrlmap.py` | `ctrlmap.ksy` | E-0011 | done (cell meaning Q-0002) |
| `.mpg` film | 42 | ffprobe (standard format) | ISO 11172 | E-0007 | standard MPEG-1 system stream |
| `.wav` sound | 629 | none yet | RIFF | E-0001 | standard |
| `default.dat` game database (and saves) | 1 (7,661 objects) | `gamedat.py` | `gamedat.ksy` | E-0100..E-0107 | done (some fields opaque, Q-0100..Q-0105) |

## `.wxi`, `.wxs`, `.dxw` — DelphiX collections (E-0010)

A 16-bit Windows resource entry around a Delphi component stream:

```
u8  0xFF, u16 10            resource type RCDATA by ordinal
char name[]\0               WDXPICTURECOLLECTION | DELPHIXPICTURECOLLECTION | DELPHIXWAVECOLLECTION
u16 flags                   0x1030
u32 size                    = rest of the file
"TPF0" sstr class, sstr name ("")      class TPictureCollectionComponent | TWaveCollectionComponent
property "List" = collection (0x0E), items each 0x01 + properties + 0x00, then 0x00
0x00 (end of properties), 0x00 (no child components)
```

Delphi stream values used: 0x02 int8, 0x03 int16, 0x04 int32, 0x06 short string,
0x07 identifier, 0x08 false, 0x09 true, 0x0A binary (u32 length + bytes), 0x0B set,
0x0E collection. `sstr` is a length byte + Latin-1 text.

Picture items: `Name` (string), `x`, `y` (ints, `WDX…` files only), `PatternHeight`,
`PatternWidth` (ints; 64×64 on the room backgrounds, 0 = the whole picture),
`Picture.Data` (binary), `SystemMemory`, `Transparent` (booleans), `TransparentColor`
(identifier: `clFuchsia`, `clBlack`, …), optional `Hint` (string). 52 items have no
`Picture.Data`. `Picture.Data` = sstr `TDIB` + BITMAPINFOHEADER (40 bytes, `biCompression`
0, positive height = bottom-up) + `biClrUsed` or 2^bpp RGBQUADs for ≤ 8 bpp + pixel rows
padded to 4 bytes. Nothing follows the pixels.

Wave items: `Name`, optional `Looped` (boolean), `Wave.WAVE` (binary) = `RIFF` u32
riff_size `WAVE` `fmt ` u32 16 + PCMWAVEFORMAT + `data` u32 n + n bytes + u8 unk_tail.
riff_size = blob length + 2 in all 58 (Q-0001). Seen: PCM mono 11,025/22,050/44,100 Hz and
stereo 22,050 Hz, 8 and 16 bit.

## `ctrl<room>.map` — control map (E-0011)

wDx `TDxMaps` stream (`TDxMaps.ReadData` 0x44f50c):

```
"ML01"            magic (not checked by the loader)
s32 high          number of maps - 1 (0 in the corpus)
per map:
  u8  name_len, char name[15]   Delphi string[15]: "Map", rest uninitialised
  u32 width, u32 height         in 16×16-pixel cells
  u32 size                      width * height * 10
  u32 unk_ptr                   the editor's buffer pointer, meaningless on disk
  u32 cells[width * height]     row-major, values 0..29 (Q-0002)
  u8  unk_tail[6 * width * height]   zero (4 stray bytes in 5 files)
```

Rooms and their grids: 80×60 (1280×960), 64×48, 60×40, 56×48, 52×40, 48×40, 48×36,
44×28, 40×36. The room picture `w<room>.wxi` is the grid size × 16.

## `.mpg` — films (E-0007)

Plain MPEG-1 system streams: one 384×288 MPEG-1 video stream, one MPEG-1 layer II audio
stream (44.1 kHz). Played by `gempeg.dll` through DirectShow (E-0006). In ScummVM:
`Video::MPEGPSDecoder` (needs libmpeg2 for video and libmad for layer II audio).

## `default.dat` — game database (E-0100..E-0107)

An MFC 6 `CArchive` of ge.dll's game object (the one `GEInit` allocates, 0x2fa40 bytes;
class name not in the binary). `GELoadFile` → load 0x100031f0, `GESaveFile` → save
0x100034e0 (same layout, so saved games use it too, Q-0105). Little-endian. Offsets `+x`
below are member offsets in the objects in memory, which the field names carry.

```
u32 walkmap_first        current walkmap ID (read into +4, overwritten below)
u32 start_x   (+8)       GEContinueGame: GotoWalkmap(walkmap, start_x, start_y, unk_10)
u32 start_y   (+0xc)     saved from two EXE callbacks (GEInit arguments 13, 14)
u32 unk_10    (+0x10)    GotoWalkmap's 4th argument; saved as 0 (Q-0104)
u32 200                  checked: anything else fails the load
s32 vars[200] (+0x4c)    game variables (GEGetVariable/GESetVariable, event types 18..20)
u32 walkmap   (+4)       current walkmap ID again
CObList walkmaps  (+0x36c)    CWalkmap
CObList inventory (+0x2f1d4)  CObj in the inventory (empty in default.dat)
CObList useobjs   (+0x2f20c)  CUseObj
CObList events    (+0x2f228)  CEvent
CObList dialogs   (+0x2f244)  CDialogs
CObList texts     (+0x2f264)  CText
u32 10                   checked
CObList books[10] (+0x2f280 + 0x1c*n)  CTopic of book type n
CObList anims     (+0x2fa24)  CAnim
(end of file)
```

default.dat: walkmap 0, start 320,258, all variables 0; 40 walkmaps, 72 CUAs, 308 objects,
541 object states, 0 in the inventory, 203 use-objects, 3,712 event records (1,868 IDs),
354 dialogs with 786 choices, 9 texts, 227 + 177 + 17 + 33 topics in books 0..3 (4..9
empty), 1,182 anims. After loading, ge.dll sets each CObj's owner (+4) and rebuilds its
index lists and the topic ranks; `CAnim.time` and `CTopic.index` are runtime values that
happen to be stored.

**MFC primitives** (statically linked MFC, E-0101):
- `CObList`: count (u16; 0xFFFF then u32), then one object per element.
- Object: u16 tag. 0xFFFF = new class: u16 schema (1 for all 11 classes), u16 name length,
  ASCII name, then the object's body. 0x8000|n = object of the class numbered n, body
  follows. Other values = reference to object n already loaded, no body (0 = NULL; none in
  default.dat). 0x7FFF = big tag: u32 follows (bit 31 = class). Classes and objects share
  one numbering in load order, starting at 1.
- `CString`: u8 length; 0xFF → u16 length; 0xFFFF → u32 length; then Windows-1252 bytes
  (u16 0xFFFE would announce Unicode; not in the corpus).
- `int`: u32.

**Classes** (`Class::Serialize` address; fields in file order). Lists are nested
`CObList`s. An object code is `obj.id * 100 + state` (events, use-objects, the
`GE*GetObjectData` exports); an event ID names the records `DoEvent` runs.

| Class (size) | Serialize | Fields |
|---|---|---|
| CWalkmap (0x38) | 0x1000acb0 | `+0x1c` list of CCUA; `+4` id; `+8` title (GEWalkmapGetTitle); `+0xc..+0x18` radar rectangle left, top, right, bottom (16 raw bytes; GEWalkmapGetRadarRect returns x = left, y = top, w = right − left, h = bottom − top) |
| CCUA (0x3c) | 0x10001720 | `+0x20` list of CObj; `+8` id; `+0xc` name; `+0x10` first_event (GotoCUA runs it while first_visit is set, then clears it); `+0x14` event (later visits); `+0x18` end_event (GECUAEnd); `+0x1c` first_visit (1 in all 72) |
| CObj (0x34) | 0x10009e90 | `+0x14` list of CObjState; `+8` cua_id; `+0xc` id; `+0x10` visible (only visible objects are listed; events 15/16); u32 current state number (resolved to `+0x30`, the first state if absent) |
| CObjState (0x2c) | 0x1000a230 | `+4` state; `+8` name (Swedish, internal); `+0xc` walkmap_anim (CAnim ID on the walkmap); `+0x10` cua_anim (CAnim ID in a CUA); `+0x14` click_event (GEClickObjectInCUA, only if not pickable); `+0x18` take_event (GEObjectToInventory); `+0x1c` unk_1c (to the EXE, Q-0100); `+0x20` pickable (events 12/13); `+0x24` text (Danish description, to the EXE) |
| CAnim (0x30) | 0x100011f0 | `+4` time (ms into the anim); `+8` id; `+0xc` next (anim that replaces it when time passes duration); `+0x10` name; `+0x14` duration in ms (0 = never ends); `+0x18` unk_18 (0 in all); `+0x1c`, `+0x20` unk (to the EXE; 0..1065, 0..735); `+0x24` z (draw order, BuildSort); `+0x28` unk_28 (to the EXE; 0..246) (Q-0101); `+0x2c` end_event (run when duration passes) |
| CUseObj (0x10) | 0x1000a980 | `+4` obj (object code used); `+8` target (object code used on); `+0xc` event (GEUseObjectOnObject) |
| CEvent (0x60) | 0x10002100 | u32 `+4` id, `+8` type, `+0xc` cond, `+0x10` var, `+0x14` value, `+0x18` jump, `+0x1c` walkmap, `+0x20` cua, `+0x24` obj, `+0x28` book, `+0x2c` topic, `+0x30` topic2, `+0x34` dialog, `+0x38`, `+0x3c` sound numbers; CString `+0x40` sound name; u32 `+0x44`, `+0x48`; CString `+0x4c` video; u32 `+0x50` x, `+0x54` y, `+0x58` unk; CString `+0x5c` comment (logged; Swedish notes) |
| CDialogs (0x2c) | 0x10001da0 | `+4` list of CDialogChoice; `+0x20` id; `+0x24` title; `+0x28` text |
| CDialogChoice (0x10) | 0x10001aa0 | `+4` unk_04 (0..11, Q-0103); `+8` text; `+0xc` event (GEDialogEnd with the choice's index runs it) |
| CTopic (0x18) | 0x1000a740 | `+4` id; `+8` title; `+0xc` text (markup below); `+0x10` shown; `+0x14` index (rank among the book's shown topics, −1 if hidden; recomputed on load) |
| CText (0xc) | 0x1000a4c0 | `+4` id; `+8` text (GETextGetText: start-up messages) |

**Events** (`DoEvent` 0x10005f70, `RunEvent` 0x100060f0). `DoEvent(id)` runs every CEvent
with that id in list order; a record that returns a jump restarts `DoEvent` with the jump
ID and drops the rest. Only type 18 jumps. Entry points: event 1 (GEStartNewGame), the CCUA
and CObjState events, CAnim end events, CUseObj and dialogue-choice events, and
GEWalkmapAreaHit(n) → event `walkmap_id * 100 + n % 100`. Operands not listed are not read.

| Type | Log string | Operands | Effect |
|---:|---|---|---|
| 0, 11 | `EventID=%d, EventType=%d` | | nothing (0: 443 records, "dummy event"; 11 unused) |
| 1 | `eventRemoveObject: …` | obj | delete object obj/100 from the inventory, else from its CUA |
| 2 | `ChangeObjectsState: Object %d new state %d` | obj | set state obj%100 |
| 3 | `Goto CUA %d` | walkmap, cua | open CUA (error if either is 0) |
| 4 | `Goto Walkmap %d [Start at %d,%d]` | walkmap, x, y, unk_58 | end the open CUA; go to the walkmap at x, y |
| 5 | `Show Topic %d in book %d` | book, topic | topic shown = 1 |
| 6 | `Playing sound [%d:%d]` / `[%s %d]` | sound_38, sound_3c, unk_48 / sound name, sound_44, unk_48 | a numbered sound if the name is empty, else the named one (Q-0102) |
| 7 | `eventAddObjectToInventory: …` | obj | move object to the inventory, state obj%100, visible |
| 8 | `eventRemoveObject: … from inventory` | obj | delete object from the inventory |
| 9 | `Start Dialog %d` | dialog | open the dialogue |
| 10 | `StartVideo [%s]` | video | play the film (`intro.mpg` …) if the name is not empty |
| 12 / 13 | `MakeObjectPickable` / `MakeObjectNotPickable: Object %d State %d` | obj | that state's pickable = 1 / 0 |
| 14 | `IncrementObjectsState: …` | obj | current state number + 1 |
| 15 / 16 | `ShowObject` / `HideObject: Object %d` | obj | visible = 1 / 0, restart its anim |
| 17 | `Stop sound [%d:%d]` / `[%s]` | sound_38, sound_3c / sound name | stop the sound (unused) |
| 18 | `Jump if …`, `Jump to %d` | cond, var, value, jump | cond 0: vars[var] == value; 1: !=; 2: <; 3: >; 4: always; 5: `rand() % 101 <= value` ("Jump if random(%d) less than %d"); if true, jump to event ID `jump` |
| 19 | `Set Variable %d to %d` | var, value | vars[var] = value |
| 20 | `Add Variable %d with %d. New value %d` | var, value | vars[var] += value |
| 21 | `Show Topic %d in book %d` (sic) | book, topic | topic shown = 0 |
| 22 | `Add topic %d to %d in book %d` | book, topic, topic2 | join topic2's title and text onto topic's, empty topic2, show topic |

Records per type in default.dat: 0:443 1:57 2:314 3:117 4:239 5:5 6:671 7:163 8:74 9:474
10:43 12:30 13:1 14:7 15:96 16:51 18:417 19:324 20:58 21:1 22:127; type 18 conditions
0:236 1:3 3:29 4:127 5:22. Variables used: 0..199.

**Topic text markup** (`GEBookParseNext` 0x10007b00, token codes it returns): `\f<n>`
format n (2), `\g<n>` picture n (5), `\h<book>[:<topic>]` link (3; `\h` without a number
4), `\t` (6), line feed (7), a space or a run of other characters (1), end (0); any other
`\x` gives a backslash. Counts in the topics: `\f` 1,209, `\h` 974, `\t` 184, `\g` 33.

**Kaitai**: `gamedat.ksy` types each list by the class the text loaders put in it (a
class reference `0x8000|n` needs the load array, which Kaitai cannot keep); `gamedat.py`
follows the MFC numbering and checks that every list holds its one class.
