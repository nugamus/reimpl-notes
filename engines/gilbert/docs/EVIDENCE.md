# Evidence log (Gilbert engine)

Every factual claim in `engines/gilbert/docs/` and `games/gilbert/docs/` must have an entry
here that names the thing that proved it. Claims without evidence are bugs, not shortcuts.

Append only. Do not rewrite history; if a claim turns out to be wrong, add a new entry
that supersedes it and mark the old one `SUPERSEDED by E-nnnn`.

Ranges: survey, binaries and the Delphi front end E-0001..; `default.dat` and `ge.dll`'s
database E-0100..; later areas take the next free hundred.

## Entry format

```
### E-0001 — <one-line claim>
- **Binary/file:** games/gilbert/discs/cd/Program/Gilbert.exe | .../Data/maps/100/w100.wxi
- **Evidence:** Ghidra address (`0x0047a190`), trace line, or corpus statistic.
- **Method:** how it was obtained.
- **Confidence:** proven | strong | tentative
```

An entry at `tentative` confidence must also have a matching line in `OPEN-QUESTIONS.md`.

## Entries

### E-0001 — The corpus: one CD, 2,433 files, 568,683,243 bytes
- **Binary/file:** `games/gilbert/images/GILBERT.ISO` (572,676,096 B, ISO 9660, volume
  created 1999-10-19 15:46:12), extracted to `games/gilbert/discs/cd`
- **Evidence:** file and byte counts in `engines/gilbert/notes/corpus-inventory.md`; 1,442
  of the files are redistributables (`Program/REDIST/`: DirectX 6 and Media Player; the
  Acrobat Reader installer). Game data under `Program/Data/`: `maps/` (39 rooms + `!global`),
  `anims/gilbert.wxi`, `game/default.dat`, `mpg/` (42), `Sounds/{Dialog,MUSIC,misc}`,
  `misc/` (4 text files). Every file's MD5 in `engines/gilbert/notes/corpus-md5.tsv`.
- **Method:** 7-Zip extraction; `python engines/gilbert/tools/survey.py`.
- **Confidence:** proven

### E-0002 — The disc is the Danish edition of Pir New World Media's "Gilbert"
- **Binary/file:** `Program/Gilbert.exe` version resource; `Program/Data/misc/*.txt`;
  `Program/License.txt`; `Program/vejledning.pdf`
- **Evidence:** version resource: CompanyName "Pir New World Media", ProductName
  "Gilbert -  Den kemystiska ön" (Swedish), FileVersion 1.0.0.3. The player-facing texts are
  Danish: `language.txt` ("Indsæt venligst Gilbert-cd'en", "Gilbert og den kemystiske ø"),
  `credits.txt` ("Produceret af Pir new world media AB for Snille Læroæventyr og
  Kemifrämjandet"), `License.txt` (licence of "Levende Bøger"), the manual `vejledning.pdf`.
  The object descriptions in `default.dat` are Danish, their internal names Swedish
  (`Handduk` / "Livredderens håndklæde"). Text files are Windows-1252.
- **Method:** `pefile` version info; reading the files.
- **Confidence:** proven

### E-0003 — Gilbert.exe is a Delphi program on DelphiX and wDx; the game logic is in ge.dll
- **Binary/file:** `Program/Gilbert.exe` (582,144 B, MD5 `5a21405e16e50d3eb7a19886e90cfcc1`)
- **Evidence:** sections `CODE DATA BSS .idata .tls .rdata .reloc .rsrc`, PE timestamp
  0x2a425e19 (Delphi's fixed value), "Portions Copyright (c) 1983,97 Borland",
  `SOFTWARE\Borland\Delphi\RTL`; RCDATA `PACKAGEINFO`, `DVCLAL` and three form streams
  (`TGMAIN`, `TFRMOPENLIB`, `TFRMOPENMAP`). The unit list (`notes/exe-forms.md`) holds the
  VCL, DelphiX (`dxclass directx dxinput dxsounds dxsprite dib wave dxrender`), wDx
  ("wDx 32-bit Delphi Components V6.0", "(C) 1998 by Patric Weber": `wdx wdxmap wdxmlo
  wdxbmp wdxilib wdxilo`), `dshow`, and the game's own units, flags 0x00: `minput control
  book wrappers outscreen sounds data main gmenu io init kinput`. Imports: 40 functions of
  `GE.DLL` (all `GE*`), 3 of `GEMPEG.DLL`, WINMM `timeGetTime joyGetPosEx joyGetDevCapsA`;
  DirectDraw, DirectSound and DirectInput are reached through COM (their interface IDs
  are in the file, `notes/exe-strings.md`), not imported.
- **Method:** `pefile`; `engines/gilbert/tools/survey.py`; `engines/gilbert/tools/exeres.py`.
- **Confidence:** proven

### E-0004 — The main form: one 640×480 16-bit full-screen DelphiX surface, a 10 ms timer
- **Binary/file:** `Gilbert.exe` RCDATA `TGMAIN`
- **Evidence:** `gMain: TgMain` (parent `TDXForm`), ClientWidth 640, ClientHeight 480,
  BorderStyle bsNone, WindowState wsMaximized. Child `DxScreen1: TDxScreen` 640×480,
  `Display.BitCount = 16`, Options `doWaitVBlank doSelectDriver doHardware doFullScreen
  doAllowPalette256 doNoWindowChange doFlip doAllowReboot`, handlers `DxScreen1Initialize
  KeyDown MouseDown MouseMove MouseUp`; image libraries 1..8 and map libraries bound to
  `DXImageList1..10` and `DxMapLib3`. `DXTimer1`: Interval 10, MaxLag 400, OnTimer
  `DXTimer1Timer`, Enabled False at load. Six `TDXSound` objects (`soExclusive`, not
  auto-initialised) and four `TDXWaveList`s, one `TDXSpriteEngine`, `DXInput1` with the
  keyboard and joystick enabled and the mouse disabled.
- **Method:** `engines/gilbert/tools/exeres.py` → `notes/exe-forms.md`.
- **Confidence:** proven

### E-0005 — ge.dll is an MSVC 6 MFC DLL by Fantasy Arts & Media: the game database and its rules
- **Binary/file:** `Program/ge.dll` (196,608 B, MD5 `a7e0418ebf79a2bec93da7bd165cf53b`, PE
  timestamp 1998-11-19 18:21:08 UTC)
- **Evidence:** linker 6.0, Rich header present, MSVC RTTI names of MFC classes
  (`.?AVCArchiveException@@`, `.?AVCObList@@`, `CWinApp`); version resource CompanyName
  "Fantasy Arts & Media", "Copyright (C) 1998". 47 exports (`GEInit GELoadFile GESaveFile
  GEStartNewGame GEContinueGame GEEllapsed GEWalkmap* GECUA* GEPath* GEInventory*
  GEDialog* GEBook* GEText* GEGet/SetVariable GEUseObjectOnObject …`, list in
  `notes/binaries.md`). Eleven serialisable classes with CRuntimeClass records (name,
  object size, schema 1): CAnim 48, CCUA 60, CDialogChoice 16, CDialogs 44, CEvent 96,
  CObj 52, CObjState 44, CText 12, CTopic 24, CUseObj 16, CWalkmap 56. Each class's vtable
  is `GetRuntimeClass, scalar deleting destructor, Serialize` (e.g. CWalkmap vtable
  0x10020528, Serialize 0x1000acb0; all in `notes/names/GE.DLL-rtti.csv`). Debug strings
  name the database sources `db\walkmaps.txt db\cuas.txt db\objects.txt db\books.txt
  db\anims.txt db\useobjs.txt db\events.txt db\dialogs.txt db\texts.txt
  db\dialogchoice.txt` (not on the disc) and the event commands (goto walkmap / CUA,
  conditional jumps on variables, set/add variable, show/hide object, object states,
  inventory, books, dialogues, sounds, video).
- **Method:** `pefile`; byte search for the CRuntimeClass records and the
  `mov eax, rtc; ret` GetRuntimeClass bodies, then their vtables.
- **Confidence:** proven

### E-0006 — gempeg.dll plays the MPEG films through DirectShow's multimedia streaming
- **Binary/file:** `Program/gempeg.dll` (98,304 B, MD5 `6f514f4284142a6e3add54aa93ee200a`)
- **Evidence:** MSVC 6 / MFC; exports `MPOpenStream MPRenderFrame MPCloseStream`; holds
  `IID_IAMMultiMediaStream` (file offset 0x00d408) and imports `CoCreateInstance`; contains
  no decoder of its own (98 KB with MFC). Gilbert.exe imports the three exports.
- **Method:** `pefile`; `survey.py` interface-ID search.
- **Confidence:** strong (the decoding is the system's MPEG-1 filter; not traced)

### E-0007 — The 42 films are MPEG-1 system streams, 384×288, MPEG-1 layer II audio at 44.1 kHz
- **Binary/file:** `Program/Data/mpg/*.mpg`
- **Evidence:** all 42 start with a pack header (`00 00 01 BA`, MPEG-1 marker `0x2_`);
  ffprobe: one `mpeg1video` 384×288 stream and one `mp2` stream at 44,100 Hz per file (41
  stereo, 1 mono); durations 3.4 s (shortest) to 181.4 s; the sequence header's frame-rate
  code is 4 (29.97) in 35 files, 5 (30) in 4, 3 (25) in 2, 2 (24) in 1.
- **Method:** header scan in Python; `ffprobe` on each file.
- **Confidence:** proven

### E-0008 — Ghidra project Gilbert.gpr: Gilbert.exe, ge.dll, gempeg.dll, Splash.exe, analysed
- **Binary/file:** `ghidra_projects/Gilbert.gpr`, folder `/gilbert-import/`: `GILBERT.EXE`,
  `GE.DLL`, `GEMPEG.DLL`, `SPLASH.EXE` (copies in `build/gilbert-import/`)
- **Evidence:** headless import and auto-analysis succeeded for all four
  (`logs/gilbert-import.log`). Functions after analysis: Gilbert.exe 2,322, ge.dll 1,252,
  gempeg.dll 527 (`notes/function-dump-*.tsv`, with strings, callers, callees, APIs).
  Ghidra missed some vtable-only methods in ge.dll; `define_and_decompile.py` created them.
- **Method:** PyGhidra headless `-import build/gilbert-import -overwrite`; `func_dump.py`.
- **Confidence:** proven

### E-0009 — Gilbert.exe's Delphi classes and methods, named from their VMTs
- **Binary/file:** `/gilbert-import/GILBERT.EXE`
- **Evidence:** 232 VMTs found by their self-pointer at −76 (Delphi 4/5 layout: class name
  −44, instance size −40, parent −36, published methods −52, TObject virtuals −32..−4);
  753 method names (published methods, TObject virtuals, new virtual slots) in
  `notes/names/GILBERT.EXE-vmt.csv`, 246 of them at existing functions applied to the
  project. The game's own classes are `TgMain` (VMT 0x469a1c, parent TDXForm, 17
  published handlers) and `TPlayerSprite` (VMT 0x475b20, parent TImageSprite); the rest of
  the game code is plain unit procedures. Class tree in `notes/delphi-classes.md`.
- **Method:** `engines/gilbert/tools/delphi_vmt.py`; `apply_names.py`.
- **Confidence:** proven

### E-0010 — `.wxi` / `.wxs` / `.dxw`: DelphiX picture and wave collections in a resource wrapper; 242/242 parse
- **Binary/file:** 234 `.wxi` (Data/anims, Data/maps), 4 `.wxs` + 4 `.dxw` (Sounds/misc)
- **Evidence:** every file is one 16-bit `.RES` entry: `FF 0A 00` (type RCDATA by ordinal),
  NUL-terminated name (`WDXPICTURECOLLECTION` 150, `DELPHIXPICTURECOLLECTION` 84,
  `DELPHIXWAVECOLLECTION` 8), u16 flags 0x1030, u32 size = the rest of the file; the body
  is a Delphi binary component stream (`TPF0`) of one `TPictureCollectionComponent` or
  `TWaveCollectionComponent` with one property `List`, a collection. Picture items carry
  `Name, x, y, PatternHeight, PatternWidth, Picture.Data, SystemMemory, Transparent,
  TransparentColor` (`x y` only in the `WDX…` files, `Hint` in 10 items; 52 items have no
  picture). `Picture.Data` is the class name `TDIB` then a BITMAPINFOHEADER (size 40,
  uncompressed, bottom-up), its palette and the pixels, nothing more: 2,273 8-bit, 135
  4-bit, 8 1-bit, 66 24-bit pictures. Wave items (`Name`, optional `Looped`, `Wave.WAVE`)
  hold a RIFF WAVE of 44 header bytes + data + one byte (0 in all 58), with the RIFF size
  field = blob length + 2. `.wxs` and `.dxw` of the same name are byte-identical.
  Validator result: 242/242 parsed, every byte consumed.
- **Method:** `python engines/gilbert/tools/parsers/wxi.py` (+ `--selftest`).
- **Confidence:** proven (layout); the wave tail byte and size field are opaque (Q-0001)

### E-0011 — `ctrl<room>.map`: a wDx TDxMaps file holding one u32 grid of 16×16-pixel cells; 39/39 parse
- **Binary/file:** 39 `.map` in `Data/maps/*`; loader in `/gilbert-import/GILBERT.EXE`
- **Evidence:** `TDxMaps` LoadFromFile 0x44f5c4 opens a TFileStream and calls ReadData
  0x44f50c: read 4 bytes (magic, not checked), read s32 `high`, then for each of
  `high + 1` maps read a 32-byte record, allocate `record+0x18` bytes into `record+0x1c`
  and read them. `TDxMaps::virtual_004` (DefineProperties) registers the same reader as
  the "MapLib" property. Corpus: magic `ML01`, high 0 in all 39; record = name as
  string[15] ("Map", uninitialised tail), width, height, size = width×height×10, a stale
  pointer; the first 4×width×height data bytes are a row-major u32 grid with values 0..29,
  the remaining 6×width×height bytes are zero except 4 stray bytes in 5 files. Grid ×16 px
  = the room's `w<room>.wxi` picture (80×60 ↔ 1280×960 in room 100, 64×48 ↔ 1024×768 in
  150, 40×36 ↔ 640×576 in 463). The room loader 0x47a190 builds the names from
  `\data\maps\`, `.wxi`, `m.wxi`, `ctrl`, `.map`, `o.wxi` and calls LoadFromFile.
  Validator result: 39/39 parsed, every byte consumed.
- **Method:** decompiled 0x44f5c4, 0x44f50c, 0x44f710, 0x47a190;
  `python engines/gilbert/tools/parsers/ctrlmap.py` (+ `--selftest`).
- **Confidence:** proven (layout); meaning of the cell values open (Q-0002)

### E-0100 — `default.dat` is an MFC 6 CArchive: a header and 17 CObLists of 11 classes; 1/1 parses, every byte consumed
- **Binary/file:** `Program/Data/game/default.dat` (702,971 B); `/gilbert-import/GE.DLL`
- **Evidence:** `GELoadFile` 0x100026a0 → `GameObj::LoadFile` 0x100031f0 opens the file
  with CFile mode 0x8000 (binary read), builds a loading CArchive, reads the header
  (E-0102), then calls slot 2 of the CObList vtable 0x10020564 (`CObList::Serialize`
  0x1001565f) on the members +0x36c, +0x2f1d4, +0x2f20c, +0x2f228, +0x2f244, +0x2f264,
  reads u32 10, calls it on the ten 0x1c-byte members from +0x2f280, then on +0x2fa24.
  `GESaveFile` 0x100026c0 → `GameObj::SaveFile` 0x100034e0 (mode 0x9001) writes the same
  sequence. Validator: `default.dat: 7661 objects, 11 classes, 0 object references`;
  CWalkmap 40, CCUA 72, CObj 308, CObjState 541, CUseObj 203, CEvent 3,712 (1,868 IDs),
  CDialogs 354, CDialogChoice 786, CText 9, CTopic 454 (books 0..3: 227 177 17 33),
  CAnim 1,182; every list holds only its class; `1/1 parsed, every byte consumed`.
  Function names in `notes/names/GE.DLL-gamedat.csv`, applied to the project.
- **Method:** PyGhidra decompilation of the functions named there;
  `python engines/gilbert/tools/parsers/gamedat.py` (+ `--selftest`).
- **Confidence:** proven

### E-0101 — ge.dll's CArchive primitives are MFC 6's (statically linked): tags, counts, CStrings
- **Binary/file:** `/gilbert-import/GE.DLL`
- **Evidence:** `CObList::Serialize` 0x1001565f: storing, WriteCount 0x1001b38c (u16, or
  0xFFFF + u32 from 0xFFFF on) then WriteObject 0x1001a88d per node; loading, ReadCount
  0x1001b3ba then ReadObject 0x1001a90c + AddTail. ReadClass 0x1001ab44: u16 tag, 0x7FFF →
  u32 big tag, else tag & 0x7FFF with bit 15 moved to bit 31; bit 31 clear → object
  reference by index; 0xFFFF → CRuntimeClass load (u16 schema, u16 length, name) and a new
  map entry; else class by index. WriteObject numbers new objects in the same map
  (+0x30 counter) and writes 0x7FFF + u32 above 0x7FFE. CString: `<<` 0x1001ad12 writes u8
  length < 0xFF, else 0xFF + u16 < 0xFFFE, else 0xFF 0xFFFF + u32, then the bytes; `>>`
  0x1001ade2 via 0x1001ad8b (u16 0xFFFE = Unicode marker). int `>>` 0x100014c0 / `<<`
  0x10001490 move 4 bytes at the buffer cursor +0x24 (end +0x28); mode bit 0 at +0x14 =
  loading. In default.dat the first tags are at 0x338 (`28 00` count 40, `FF FF 01 00 08 00
  CWalkmap`), class references appear as 0x8005 etc., and no object reference occurs.
- **Method:** decompiled the addresses above; validator statistics.
- **Confidence:** proven

### E-0102 — The header: current walkmap, start position, 200 game variables
- **Binary/file:** `default.dat` bytes 0x000..0x337; `/gilbert-import/GE.DLL`
- **Evidence:** LoadFile 0x100031f0 reads u32 → +4, +8, +0xc, +0x10, then a u32 that must
  be 200 (else the load fails), 200 u32 into +0x4c.., then u32 → +4 again. SaveFile
  0x100034e0 writes the current walkmap's ID (`*(+0x388)+4`), the results of the GEInit
  callbacks 13 and 14 (DAT_100285dc, DAT_100285d8), 0, 200, the 200 variables, the walkmap
  ID. `GEContinueGame` → 0x100031c0 calls GotoWalkmap 0x10008fa0(+4, +8, +0xc, +0x10); the
  event "Goto Walkmap %d [Start at %d,%d]" (type 4) calls it with walkmap, x, y, unk, so +8
  and +0xc are the start position. `GEGetVariable`/`GESetVariable` → 0x10005490 /
  0x100054b0 read/write +0x4c + 4n for n < 200. default.dat: 0, 320, 258, 0, 200, all
  variables 0, 0.
- **Method:** decompilation; validator.
- **Confidence:** proven (the meaning of +0x10 is open, Q-0104)

### E-0103 — Which class each list holds, from ge.dll's text loaders and finders
- **Binary/file:** `/gilbert-import/GE.DLL`
- **Evidence:** `GELoadTextFiles` → 0x100037e0 opens `db\walkmaps.txt` … and calls the
  loaders, each of which `new`s one class (by size) and AddTails it: LoadWalkmaps
  0x10003eb0 (0x38, +0x36c), LoadCUAs 0x10004080 (0x3c, into the walkmap's +0x1c),
  LoadObjects 0x100042c0 (CObj 0x34 into the CUA's +0x20; CObjState 0x2c into the object's
  +0x14; column 2 split as id = n / 100, state = n % 100), LoadBooks 0x10004600 (0x18 into
  +0x2f280 + 0x1c·booktype, "Invalid booktype" when ≥ 10), LoadAnims 0x10004830 (0x30,
  +0x2fa24), LoadUseObjs 0x10004a50 (0x10, +0x2f20c), LoadEvents 0x10004bc0 (0x60,
  +0x2f228), LoadDialogs 0x10004ec0 (0x2c, +0x2f244), LoadDialogChoices 0x10005070 (0x10,
  into the dialog's +4), LoadTexts 0x10005290 (0xc, +0x2f264). The inventory list
  +0x2f1d4 receives CObjs from ObjectToInventory 0x10008b50 and event type 7; UpdateInventory
  0x10009230 lists its objects with +0x10 set. After loading, BuildIndexLists 0x10005d70
  and LoadFile set each CObj's owner +4 to its CCUA, IndexTopics 0x100077e0 renumbers
  CTopic +0x14.
- **Method:** decompilation; the validator checks the class of every list element.
- **Confidence:** proven

### E-0104 — The eleven Serialize layouts and the fields' meanings from their users
- **Binary/file:** `/gilbert-import/GE.DLL`
- **Evidence:** Serialize bodies (loading branch): CWalkmap 0x1000acb0 list +0x1c, u32 +4,
  CString +8, 16 bytes +0xc; CCUA 0x10001720 list +0x20, +8, CString +0xc, +0x10..+0x1c;
  CObj 0x10009e90 list +0x14, +8, +0xc, +0x10, u32 state → SetState 0x10009e40 (FindState
  0x10009e70 by CObjState +4, else the first); CObjState 0x1000a230 +4, CString +8,
  +0xc..+0x20, CString +0x24; CAnim 0x100011f0 +4, +8, +0xc, CString +0x10, +0x14..+0x2c;
  CUseObj 0x1000a980 +4, +8, +0xc; CEvent 0x10002100 +4..+0x3c, CString +0x40, +0x44,
  +0x48, CString +0x4c, +0x50, +0x54, +0x58, CString +0x5c; CDialogs 0x10001da0 list +4,
  +0x20, CString +0x24, +0x28; CDialogChoice 0x10001aa0 +4, CString +8, +0xc; CTopic
  0x1000a740 +4, CString +8, +0xc, +0x10, +0x14; CText 0x1000a4c0 +4, CString +8. Users:
  walkmap title `GEWalkmapGetTitle` (+8), radar rectangle GetRadarRect 0x10005500 and the
  loader (x, y, x+w, y+h); FindWalkmap 0x100054d0 (+4), FindCUA 0x10005e20 (CCUA +8),
  FindObj 0x10005e40 (CObj +0xc), FindAnim 0x10005eb0 (CAnim +8), FindUseObj 0x10005ee0
  (+4, +8), FindDialog 0x10005f10 (+0x20), GetText 0x10005f40 (CText +4 → +8). GotoCUA
  0x10009090 runs +0x10 and clears +0x1c if +0x1c ≠ 0, else runs +0x14; CUAEnd 0x10008930
  runs +0x18. ClickObjectInCUA 0x10008a20 runs state +0x14 unless state +0x20;
  ObjectToInventory 0x10008b50 runs state +0x18; MakeObject(Not)Pickable set state +0x20.
  BuildWalkmapObjects 0x10008170 takes the anim of state +0xc, BuildCUAObjects 0x10008220
  and CUAGetObjectData 0x10008830 of state +0x10, both only for CObj +0x10 ≠ 0.
  StepAnim 0x10008520 adds the timeGetTime delta to anim +4; past +0x14 it switches to anim
  +0xc and returns +0x2c, which Ellapsed 0x10008590 runs as an event. BuildSort
  0x10007e90/0x10008000 order by anim +0x24 ("ZOrder"). GE*GetObjectData hand state +0x1c,
  +0x20, +0x24 and anim +0x1c, +0x20, +0x28 to the EXE. UseObjectOnObject 0x10008cc0
  matches (+4, +8) and runs +0xc; DialogEnd 0x10008f60 runs the choice's +0xc;
  GEDialogGetTitle/Text return +0x24/+0x28 (0x10008e50, 0x10008eb0), GEDialogGetChoice the
  choice's +8. GEBookGetTopicTitle/GetTopic return topic +8/+0xc; FindTopic 0x10007880
  (+4). Corpus: every CObj's state and cua_id match (308/308), object IDs unique, all
  27 walkmap and 503 CUA anim IDs, 137 click and 35 take events, 203/203 use-object
  events and codes, 413/417 jump targets resolve; 1,180 of 1,182 `next` IDs exist.
- **Method:** decompilation; corpus checks in Python over `gamedat.parse`.
- **Confidence:** proven (fields marked `unk_*` stay open: Q-0100..Q-0103)

### E-0105 — CEvent types: RunEvent's switch on +8, and DoEvent's jump rule
- **Binary/file:** `/gilbert-import/GE.DLL`
- **Evidence:** RunEvent 0x100060f0 logs CString +0x5c, then switches on +8 with cases
  1..10, 12..22 (log strings and operands in `docs/formats/README.md`); any other type
  (0, 11) reaches the default, which logs "EventID=%d, EventType=%d". Case 18 switches on
  +0xc: 0 ==, 1 !=, 2 <, 3 > of GetVariable(+0x10) against +0x14, 4 always, 5
  `rand() % 101 <= +0x14`; when true it returns +0x18, every other path returns 0. DoEvent
  0x10005f70 walks the event list for records with +4 == id, calls RunEvent on each and,
  on a nonzero return, starts again with that ID. GEStartNewGame 0x10002680 → 0x100031a0
  runs event 1; GEWalkmapAreaHit 0x10008710 runs `n % 100 + walkmap_id * 100`. Corpus:
  records per type 0:443 1:57 2:314 3:117 4:239 5:5 6:671 7:163 8:74 9:474 10:43 12:30 13:1
  14:7 15:96 16:51 18:417 19:324 20:58 21:1 22:127 (no 11, no 17); type 18 conditions
  0:236 1:3 3:29 4:127 5:22.
- **Method:** decompilation; string table dump; validator.
- **Confidence:** proven

### E-0106 — Topic text markup, from GEBookParseNext
- **Binary/file:** `/gilbert-import/GE.DLL` 0x10007b00; the CTopic texts in `default.dat`
- **Evidence:** the tokenizer returns 0 at the end; for `\` it reads the next letter: `f` →
  number into +0x2f3c8 (GEBookParseGetFormat), returns 2; `g` → number into +0x2f3d4
  (GetPicture), 5; `h` + digit → book into +0x2f3cc, optional `:` + topic into +0x2f3d0
  (GetLinkBook/GetLinkTopic), 3, `h` without digit 4; `t` 6; other letters give a `\` text
  token. Line feed → 7; a space or a run of characters up to a space/control/`\` → 1 with
  the text in +0x2f3c4 (GEBookParseGetText). Corpus: `\f` 1,209, `\h` 974, `\t` 184, `\g`
  33, no other codes.
- **Method:** decompilation; regular-expression count over the topics.
- **Confidence:** proven

### E-0107 — `gamedat.ksy` compiles and parses all of default.dat
- **Binary/file:** `engines/gilbert/docs/formats/gamedat.ksy`
- **Evidence:** kaitai-struct-compiler (`-t python`) compiles it; the generated parser reads
  default.dat to offset 702,971 of 702,971 with 40 walkmaps, 3,712 events, books 227 177 17
  33 0 0 0 0 0 0 and 1,182 anims, the same as `gamedat.py`.
- **Method:** compile to Python in a temporary folder and run it on the file.
- **Confidence:** proven

### E-0200 — Start-up: the program entry, TgMain's fields, DxScreen1Initialize
- **Binary/file:** `/gilbert-import/GILBERT.EXE` 0x47bad4, 0x469ecc; VMTs of TgMain 0x469a1c,
  TImagelibHolder 0x459474, TDxScreen 0x459c50, TDXImageList 0x45a7a0,
  TPictureCollectionItem 0x45a3b8, TDXTimer 0x445940
- **Evidence:** entry 0x47bad4: Application.Initialize, Title := "Gilbert" (0x442ac4),
  CreateForm(TgMain) (0x442ea0), Run (0x442f20). TgMain's published field table: DxScreen1
  +0x2f4, DxMapLib3 +0x2f8, DXTimer1 +0x2fc, DXInput1 +0x300, DXImageList1..12
  +0x304..+0x330 (step 4), DXImageList14 +0x334, DXWaveList1..4 +0x338..+0x344,
  DXSound1..6 +0x348..+0x35c, DXSpriteEngine1 +0x360. RTTI: TDxScreen.ImageLibs is field
  +0xdc4 (a TImagelibHolder) whose Imagelib1..8 are fields +0x48..+0x64; with the form's
  bindings (E-0004) Imagelib1 = DXImageList6, Imagelib2 = DXImageList7, Imagelib3 =
  DXImageList8, Imagelib4 = DXImageList1, Imagelib5 = DXImageList10, Imagelib8 =
  DXImageList9. TDXImageList.Items is field +0x28; TPictureCollectionItem x, y are fields
  +0x58, +0x5c; TDXTimer's Enabled setter is 0x446240, Interval setter 0x446280.
  DxScreen1Initialize 0x469ecc: Rect(64, 50, 576, 430) (Rect 0x40ee54 takes left, top,
  right, then bottom and the result pointer on the stack) passed to 0x460cd4, which copies
  it to screen+0x278 and to +0x9c of the surfaces at screen+0x26c (the back buffer, target
  of every draw) and screen+0x268 (the primary); the same rect is then copied into both
  again; Screen.Cursor := −1 (crNone; 0x441370 is TScreen.SetCursor: compares +0x38,
  GetCursorPos, WindowFromPoint); boot::Run 0x47b2f0; DXTimer1.Enabled := True. The picture
  draw 0x45bef8 clips to the destination surface's +0x9c rect; the fill 0x45c644 is a
  whole-surface Blt with DDBLT_COLORFILL | DDBLT_WAIT (0x1000400) and the colour in EDX.
- **Method:** capstone disassembly (`pefile`); the Delphi field table (VMT −56) and RTTI
  property lists (VMT −60) read in Python.
- **Confidence:** proven

### E-0201 — Settings in the registry: names, types, defaults, clamping
- **Binary/file:** `GILBERT.EXE` 0x476d14 (read), 0x47705c (write)
- **Evidence:** read: TRegistry (class 0x44c258), RootKey HKEY_LOCAL_MACHINE (0x80000002),
  OpenKey('\SOFTWARE\Pir\Gilbert\1.0', CanCreate False). Key missing: CDPath := HDPath :=
  ExtractFilePath(Application.ExeName) (0x4433e8; 0x40826c keeps up to the last `\` or
  `:`, trailing `\` included), FirstTime := 0, FullscreenVideo := 0, SoundVolume := 4,
  MusicVolume := 5, InstallationType := −1. Key present: CDPath and HDPath with ReadString
  (0x44c5e4), one trailing `\` removed from each; FirstTime and FullscreenVideo := (ReadInteger
  (0x44c670) = 1); InstallationType := ReadInteger; SoundVolume, MusicVolume := ReadInteger,
  replaced by 4 resp. 5 when outside 1..6. Globals: CDPath 0x47ce38, HDPath 0x47ce3c,
  FirstTime 0x47ce70, FullscreenVideo 0x47cf18 (byte), SoundVolume 0x47cf14, MusicVolume
  0x47cf10, InstallationType 0x47ce40. Write (called only from boot::Exit): OpenKey(same
  key, CanCreate False; result ignored), WriteInteger (0x44c65c) FirstTime 0, SoundVolume,
  MusicVolume, FullscreenVideo (1 or 0). Code references: FirstTime is read nowhere else;
  InstallationType is only compared with −1 (0x46fd0f new game, 0x477307 save).
- **Method:** disassembly; code references found by byte search for the globals and their
  pointer cells in DATA.
- **Confidence:** proven

### E-0202 — The CD check and the HD/CD path resolution
- **Binary/file:** `GILBERT.EXE` 0x477738, 0x4775d8; `Data/misc/language.txt`
- **Evidence:** 0x477738: FileExists(CDPath + '\data\misc\gilbert.nfo'), else
  FileExists(HDPath + the same); if neither, loop: MessageDlg(line 19, mtConfirmation (3),
  [mbRetry, mbCancel] (set 0x0028 at 0x477850), HelpCtx 0) (0x44b228); result 2 (mrCancel)
  → boot::Exit 0x47b5fc and leave the loop (boot::Run then carries on, E-0204); otherwise
  test the two files again. 0x4775d8(rel): HDPath + rel if FileExists, else CDPath + rel if
  FileExists, else the result is empty after MessageDlg(line 0 + CR CR + HDPath + rel +
  ' ' + line 18 + CR + CDPath + rel + CR CR + line 1, mtError (1), [mbOK] (set 0x0004), 0)
  and boot::Exit. Lines (E-0203): 0 "Kunne ikke finde filen:", 1 and 19 "Indsæt venligst
  Gilbert-cd’en", 18 "eller".
- **Method:** disassembly; the TMsgDlgBtn sets read from the file.
- **Confidence:** proven

### E-0203 — language.txt: the line reader
- **Binary/file:** `GILBERT.EXE` 0x477854, 0x407f74; `Data/misc/language.txt` (738 B, 26 CR LF)
- **Evidence:** 0x477854(n): opens files::ResolvePath('\data\misc\language.txt') as a Delphi
  text file and reads it character by character; each CR ends a line (kept when the line
  count equals n) and increments the count; every other character, LF included, is
  appended; the kept line is Trim()med (0x407f74 drops characters ≤ ' ' at both ends).
  Line n is therefore the n-th CR-terminated line, 0-based. Lines used by the boot: 11
  "Initialiserer grafik...", 12 "Initialiserer Gilbert...", 13 and 14 "Initialiserer
  gamma...", 15 "Initialiserer logik..." (Windows-1252).
- **Method:** disassembly; reading the file.
- **Confidence:** proven

### E-0204 — boot::Run 0x47b2f0: the order of the boot
- **Binary/file:** `GILBERT.EXE` 0x47b2f0, 0x47b740
- **Evidence:** ReadSettings 0x476d14; CheckCD 0x477738; CoInitialize(nil) (result kept at
  0x484adc); the FullscreenVideo byte saved in BL; Fill(back, 0), Flip, Fill, Flip, Fill;
  movie::Play('logo1.mpg'); Fill, Flip, Fill, Flip, Fill; movie::Play('logo2.mpg');
  FullscreenVideo := BL (movie::Play does not write it); Fill, Flip, Fill; sound::Init
  0x474b7c; LoadInterfaceImages 0x47ab54; LoadingStep(line 11, 2); 0x485880 := nil;
  InitSlotRects 0x471108; LoadInventoryImages 0x47aad0; LoadGilbertImages 0x47acc0;
  LoadingStep(line 12, 3); CreatePlayerSprite 0x47b740; LoadingStep(line 13, 4);
  ReadSlotNames 0x4774dc; LoadingStep(line 14, 5); mode 0x47ce74 := 0; DXTimer1.Interval :=
  16; slot 3 of the COM interface at primary+0x90 called with (0, 0x480a8c) (E-0218);
  LoadingStep(line 15, 6); GEInit(22 callbacks, E-0217); DXTimer1.Enabled := True;
  sound::PlayMenuMusic('menu1', 1). 0x47b740: sprite engine clip rect (64, 50, 576, 430),
  engine size 512×380, a TPlayerSprite with gilbert.wxi item 0, X 272.0, Y 210.0 (doubles),
  96×96, rect (112, 98, 528, 322).
- **Method:** disassembly.
- **Confidence:** proven

### E-0205 — Pictures: which collection goes into which image list; Draw and BoundsRect
- **Binary/file:** `GILBERT.EXE` 0x47ab54, 0x47aad0, 0x47acc0, 0x47aa4c, 0x463cdc, 0x463c00,
  0x464428; `Data/maps/!global/*.wxi`, `Data/anims/gilbert.wxi`
- **Evidence:** each loader passes files::ResolvePath(name) to 0x4646e8 on list+0x28:
  `\data\maps\!global\interface1.wxi` → DXImageList1 (+0x304), `map.wxi` → DXImageList3,
  `interface2.wxi` → DXImageList6 (+0x318 = ImageLibs.Imagelib1, holder+0x48),
  `cursor.wxi` → DXImageList14 (+0x334), `inventory.wxi` → DXImageList7,
  `\data\anims\gilbert.wxi` → DXImageList9, `bookimages.wxi` → DXImageList12 (0x47aa4c).
  0x464428(list, i) returns item i. Draw 0x463cdc: EAX item, EDX destination, ECX x, stack
  y then pattern (ret 8); if the item has a picture and 0 ≤ pattern < count it draws with
  the item's Transparent flag (+0x41) and stores x, y into +0x58, +0x5c. BoundsRect
  0x463c00: Rect(+0x58, +0x5c, +0x58 + width, +0x5c + height). All 170 interface2 items
  and the single interface1 item are Transparent with TransparentColor clFuchsia; every
  stored x, y in interface2.wxi is 0. Items used by the boot and the menu, index: name
  (size): 0 0bkg (512×324), 1 ssky05, 2 1m01bkg (217×304), 3 credbkg (512×310), 0xb..0x12
  a1m11..a1m17 1m18, 0x13..0x1a a1m21..a1m27 1m28, 0x1b..0x22 a1m31..a1m37 1m38, 0x24
  a1m41, 0x25 a1m44 (the buttons, 154×31), 0x23 2m03bkg, 0x32 ilockbkg, 0x33 ioff11, 0x37
  a2mi_11, 0x38 2ml_bkg2, 0x39 2ms_bkg1, 0x3a laddbkg (169×125), 0x3b a2mi_01, 0x3c
  2mi_off, 0x3e a2mi_02, 0x3f a2ml_sky, 0x40 a2ms_sky, 0x44 a2msl13b, 0x45 a2msl14b, 0x48
  a2msl23b, 0x49 a2msl24b, 0x4c a2msl33b, 0x4d a2msl34b, 0x60..0x62 laddb21..laddb23
  (41×41), 0x63..0x68 pil11 pil21 pil31 pil12 pil22 pil32, 0x6f s03bkg, 0x70 ioff21, 0x71
  2mi_on, 0x72 ioff31, 0x73..0x75 0tillb11 0tillb21 0tillb31, 0x77 0tillbkg, 0x7d
  a2mi_vbkg, 0x84..0x89 pil15 pil25 pil35 pil16 pil26 pil36, 0x8a..0x8f and 0x90..0x95
  2mi_k1..2mi_k6 (29×29), 0x96 2mi_kv, 0x97 filmsm (512×380); interface1 item 0 ibkg03.bmp
  (512×380); cursor.wxi 0 VANLIG, 1 KLICK, 2 LEFT, 3 RIGHT, 4 UP, 5 DOWN, 6 EJ, 7 TOPOINTER
  (32×32).
- **Method:** disassembly; `python engines/gilbert/tools/parsers/wxi.py`; the pictures
  rendered to PNG and looked at (button labels Fortsæt spil, Nyt spil, Åbn spil, Gem spil,
  Indstillinger, Hjælp, Om Gilbert, Intro, Afslut; three looks per button: plain, yellow
  text, yellow text with an orange border; a1m41/a1m44 have red backgrounds).
- **Confidence:** proven

### E-0206 — boot::LoadingStep 0x478234: the loading panel
- **Binary/file:** `GILBERT.EXE` 0x478234, 0x460d24, 0x477954
- **Evidence:** only when TDxScreen.CanDraw (0x45ff8c); switch on the step (table
  0x478284): each step 2..6 draws interface2 0x3a at (235, 178); step 2 also 0x60 at
  (251, 244) and 0x61 at (296, 244); 3: 0x61; 4: 0x61 and 0x62 at (341, 244); 5 and 6:
  0x62. Then the text twice with 0x460d24 (EAX screen, EDX x, ECX y; stack text, colour,
  style, size, font name; it takes the back buffer's canvas, Brush.Style := bsClear, sets
  Font.Name, Size, Style, Color, TextOut(x, y, text), releases the canvas): x = 320 −
  TextWidth(text) div 2 (TextWidth 0x41a028 runs before 0x460d24 sets the font), first y 201
  in colour 0, then y 200 in $008EBDDD, 'Arial', size 8, style byte 0 (0x478670). Then Flip
  and BusyWait(50): 0x477954 counts 50 × 1,000,000 down in a `dec`/`jnz` loop. laddbkg has
  no fuchsia pixel, so every step repaints the whole panel.
- **Method:** disassembly; pixel check of laddbkg.
- **Confidence:** proven

### E-0207 — Sounds: wave lists, the play call, music streams, volume levels
- **Binary/file:** `GILBERT.EXE` 0x474b7c, 0x4753c4, 0x475624, 0x475764, 0x475008,
  0x474c44, 0x474d84, 0x474ec8, 0x475380, 0x475318, 0x4757f0, 0x4758d4;
  `Data/Sounds/misc/menu.wxs`
- **Evidence:** sound::Init: TDXSound.Initialize (0x449c74) on DXSound1..6;
  LoadWaveList(1, 'menu.wxs'), LoadWaveList(2, '2.wxs'); the stream pointers
  0x484ac8..0x484ad8 := nil. LoadWaveList(n, file): ResolvePath('\data\sounds\misc\' + file)
  into DXWaveList n (1..4, all bound to DXSound6), a loaded flag per list, then
  SetSoundVolume. PlayWave 0x475624(list, index, looped, wait): Items[index].Looped :=
  looped (setter 0x44a37c); Items[index].Play(wait) (0x44a240). The music calls create a
  TAudioFileStream (class 0x447730) on one DXSound's DirectSound, FileName :=
  ResolvePath(folder + name + '.wav'), Looped := (argument ≠ 0), MusicVolume applied,
  Position := 0 (0x448ff8): 0x474c44 → stream 0x484ac8 on DXSound1, `\data\sounds\music\`,
  Play at once, flag 0x47cee4; 0x474d84 → 0x484acc, DXSound2, `\data\sounds\dialog\`, Play,
  flag 0x47cee8; 0x474ec8 → 0x484ad0, DXSound3, music folder, Play, flag 0x47ceec;
  0x475008 → 0x484ad4, DXSound4, music folder, no Play (the main loop starts it, E-0210),
  flag 0x47cef0. Each first frees its own stream. StopAll 0x475380 clears the five flags and
  frees the five streams. Volume tables (0x475804, 0x4758e8): level 1 −5000, 2 −4000, 3
  −3000, 4 −2000, 5 −1000, 6 (and 0) 0; SetMusicVolume sets the streams 0x484ac8..0x484ad4,
  SetSoundVolume the stream 0x484ad8 and every item of each loaded wave list. menu.wxs
  items: 0 "click 1", 1 "click 2", 2 "click 3", 3 "click 4", 4 "click 5", 5 "click 6", 6..9
  walk sounds, 10 "NewTop"; mono 16-bit 22,050 Hz except 2 and 5 (44,100 Hz) and 10
  (11,025 Hz); none Looped.
- **Method:** disassembly; RTTI of TWaveCollectionItem; `wxi.py` `parse_wave`.
- **Confidence:** proven

### E-0208 — movie::Play 0x4797f0: windowed and full-screen films, Esc, the frame picture
- **Binary/file:** `GILBERT.EXE` 0x4797f0, 0x479b34; `GEMPEG.DLL` MPOpenStream 0x100010b0,
  MPRenderFrame 0x10001290, MPCloseStream 0x10001230
- **Evidence:** 0x4797f0(PChar name): isFilm := name is none of 'logo1.mpg', 'logo2.mpg',
  'logo3.mpg' (exact LStrCmp); the back-buffer canvas released; DXTimer1.Enabled := False;
  sound::StopAll. FullscreenVideo = 1: 0x479b34(WideString path, back buffer, Rect(0, 0,
  640, 480), 0, 1, 1, 0): CoCreateInstance(CLSID_AMMultiMediaStream), Initialize(read),
  AddMediaStream(IDirectDraw, MSPID_PrimaryVideo), AddMediaStream(nil, MSPID_PrimaryAudio,
  flag 1), OpenFile(path), IDirectDrawMediaStream.GetFormat → the film's width and height;
  an off-screen surface of that size, CreateSample on it; StopAll; Fill/Flip three times and
  a Fill (both buffers black); stretch-Blt the sample surface to (0, 0, 640, 480) with
  DDBLT_WAIT (table 0x47ce30, index 0); SetState(run); DXTimer1 off; loop: sample Update(0,
  0, 0, 0); S_OK → Blt again, Flip, then GetAsyncKeyState(VK_ESCAPE) < 0 → SetState(stop),
  free the surface, Fill primary and back, Flip, done; any other result → the same ending.
  This path never draws a frame picture (argument 6 = 1 skips item 0x98). FullscreenVideo
  ≠ 1: path := ResolvePath('\data\mpg\' + name); MPOpenStream(path, IDirectDraw, back
  buffer's IDirectDrawSurface, 127, 80) (stdcall, `ret 0x14`) sets up the same streams and
  CreateSample on the back buffer with the rect (x, y, x + width, y + height), runs, returns
  0 on success. On success: if isFilm, draw interface2 0x97 (filmsm) at (64, 50), Flip, draw
  it again; then while not skipped and MPRenderFrame() (Update(0, 0, 0, 0) = S_OK): skip :=
  GetAsyncKeyState(VK_ESCAPE) < 0; Flip. MPCloseStream (SetState(stop), release). After
  either path: if the flag 0x47cf54 is set → clear it, 0x47ce6c := 9,
  PlayMenuMusic('menu1', 1); else if the room music name 0x47cf08 is not empty →
  PlayRoomMusic(name, 1). DXTimer1.Enabled := True. GUIDs checked by value: 49c47ce5…
  CLSID_AMMultiMediaStream, bebe595c… IID_IAMMultiMediaStream, a35ff56a…/a35ff56b…
  MSPID_PrimaryVideo/Audio, f4104fce… IID_IDirectDrawMediaStream.
- **Method:** disassembly of both binaries; GUID bytes read from the files.
- **Confidence:** proven

### E-0209 — boot::Exit 0x47b5fc
- **Binary/file:** `GILBERT.EXE` 0x47b5fc
- **Evidence:** DXTimer1.Enabled := False; WriteSettings 0x47705c; FullscreenVideo := 0;
  Fill, Flip, Fill, Flip, Fill; movie::Play('logo3.mpg'); free the objects at 0x485880 (the
  credits surface), 0x485884 (a surface of the book code 0x46aa54) and 0x486b60 when set;
  finalize (0x449ba0) DXSound1..6; GEExit; CoUninitialize when CoInitialize had returned 0;
  Application.Terminate (0x442fd4). movie::Play re-enables the timer and may restart the
  room music (E-0208) before the terminate takes effect.
- **Method:** disassembly.
- **Confidence:** proven

### E-0210 — TgMain.DXTimer1Timer 0x469fa0: the main loop and the menu mode
- **Binary/file:** `GILBERT.EXE` 0x469fa0, 0x46b490
- **Evidence:** every tick: GEEllapsed(); v := GEGetVariable(198); v ≠ 0 → mode 0x47ce74
  := 0, 0x47cf50 := 0, 0x47cf4c := 0. Switch on the mode byte (table 0x469ff7): 0 →
  gmenu::Draw 0x46b490, 0x474100 (empty), gmenu::HandleMouse 0x471380, ui::DrawCursor
  0x477d90, Flip; then if 0x47ce6c = 10 and stream 0x484ad4 exists → its Play (0x448f10);
  if 0x47ceec → Update (0x44930c) of 0x484ad0; if 0x47cef0 and 0x47ce6c > 10 → Update of
  0x484ad4. 1, 2, 4, 5 → the game screens (0x478674, 0x4794c0, 0x46ec90, 0x46f630 first); 3
  and any other value (0x99 while a room loads, 0x47a1f3) → nothing. At the end 0x47ce5c
  ^= 1. gmenu::Draw increments 0x47ce6c while it is below 20 (0x46b629). Initial values in
  DATA: mode 0x99 (the boot sets 0), 0x47ce6c 0; the byte flags 0x47cf4c, 0x47cf50,
  0x47cf54, 0x47ce68, 0x47cf88, 0x47cfb4, 0x47cf78 0; 0x47cf1c, 0x47cf20, 0x47cf34,
  0x47cf40, 0x47cf44, 0x47cf48 −1; 0x47cf58, 0x47cf5c, 0x47cf64, 0x47cf68, 0x47cf6c,
  0x47cf70, 0x47cf80, 0x47cf90 0.
- **Method:** disassembly; initial values read from the DATA section.
- **Confidence:** proven

### E-0211 — Menu input: mouse events, the mouse rectangle, keys, the cursor
- **Binary/file:** `GILBERT.EXE` TgMain.DxScreen1MouseMove 0x46a488, MouseDown 0x46a518,
  MouseUp 0x46a568, KeyDown 0x46a800, ui::DrawCursor 0x477d90
- **Evidence:** MouseMove (Shift in CL, X, Y on the stack): 0x48169c := X, 0x4816a0 := Y,
  0x4816a4 := Rect(X − 3, Y − 3, X + 3, Y + 3); if the button state 0x47ceb4 = −1: ssLeft
  (0x08) → 1, ssRight (0x10) → 2. MouseDown: if 0x47ceb4 = −1: mbLeft → 1, mbRight → 2
  (mode 2 also calls 0x475c14). MouseUp: 0x47ceb4 := −1, 0x47ceb8 := −1 (modes 1 and 2 may
  call 0x475d04). KeyDown: c := MapVirtualKey(Key, 2); c in {0x20, 0x30..0x3a, 0x40..0x5c,
  0xc4, 0xc5, 0xd6} is appended to the save name 0x47cf74 when the save row 0x47cf70 > 0,
  the page 0x47cf60 = 4, editing 0x47cf78 = 1 and the name is shorter than 20 characters;
  Key 8 deletes the last character of 0x47cf74 whenever it is not empty; no other key is
  handled (GetAsyncKeyState is called only for VK_ESCAPE in the film players and VK_CONTROL
  at 0x474108). DrawCursor: X clamped to 72..568 and Y to 58..422, each clamp followed by
  SetCursorPos(X, Y); draws cursor.wxi item 0x47ce8c at (X − 16, Y − 16). HandleMouse sets
  0x47ce8c := 0 (VANLIG) first.
- **Method:** disassembly; call-site search for GetAsyncKeyState.
- **Confidence:** proven

### E-0212 — gmenu::Draw 0x46b490 and the button column 0x46b644
- **Binary/file:** `GILBERT.EXE` 0x46b490, 0x46b644 (Ghidra merged it into 0x46b490)
- **Evidence:** only when CanDraw. Fill(back, 0). Credits flag 0x47cfb4 = 1: interface2 3
  at (64, 50) (a float at 0x47cfbc += 0.5, wrapping at 200.0, read elsewhere only by an
  unused film branch), interface1 0 at (64, 50). Otherwise: interface2 0 at (64, 50), 2 at
  (352, 56), interface1 0 at (64, 50). Both: interface2 0x32 at (64, 337). Then 0x46b644: if
  0x47cfb4 = 0 and 0x47cf88 = 0, the column at x 384: y 70 item 0xb (0x24 when 0x47cf4c =
  0), 104 0xc, 138 0xd, 172 0xe (0x25 when 0x47cf50 = 0), 206 0xf, 240 0x10, 274 0x11, 308
  0x12, 380 0x33. If 0x47cfb4 = 1: 0x77 at (509, 336) and 0x73 at (513, 340). If both flags
  are 0: hover 0x47cf1c (tables 0x46b975/0x46b99e): 0xb → 0x13 (only if 0x47cf4c), 0xc..0x12
  → 0x14..0x1a (0xe → 0x16 only if 0x47cf50), 0x33 → 0x70, at the item's column place;
  then pressed 0x47cf20 (tables 0x46bbf2/0x46bc1b): 0xb → 0x1b and gmenu::Action(0xb) (only
  if 0x47cf4c), 0xc..0x12 → 0x1c..0x22 and Action(item) (0xe only if 0x47cf50), 0x33 →
  0x72 and Action(0x33). Otherwise: hover 0x73 → 0x74 at (513, 340); pressed 0x73 → 0x75 at
  (513, 340) and Action(0x73). Last: page 0x47cf34 ≠ −1 → gmenu::DrawPage(page). Back in
  0x46b490: 0x47ce6c += 1 while it is below 20.
- **Method:** disassembly with the two-level Delphi case tables decoded.
- **Confidence:** proven

### E-0213 — gmenu::HandleMouse 0x471380: hit tests, press, rows
- **Binary/file:** `GILBERT.EXE` 0x471380, 0x471108
- **Evidence:** hover: if IntersectRect(mouse rect, Rect(320, 50, 512, 440)) or 0x47cfb4 =
  1 or 0x47cf88 = 1, test in this order 0xb (only if 0x47ce68 = 1), 0xc, 0xd, 0xe, 0xf,
  0x10, 0x11, 0x12, 0x73, 0x33 with IntersectRect(mouse rect, BoundsRect(item)); the first
  hit → 0x47cf1c := item, none → −1; when the gate fails 0x47cf1c is left as it was. Left
  half, the same gate with Rect(0, 0, 320, 440): page-item hover 0x47cf44 from 0x44, 0x45,
  0x63, 0x66, 0x73, 0x84, 0x87 (none → −1); load-row hover 0x47cf64 := the first k in 1..6
  whose rect 0x484ae0[k] meets the mouse rect, else 0; save-row hover 0x47cf68 from
  0x484b50[1..5], else 0. A new press (0x47ceb4 ≠ 0x47ceb8) with 0x47ceb4 = 1 runs the same
  tests into 0x47cf20 (column item or −1, under the right gate), 0x47cf48 (page item from
  0x44, 0x45, 0x63, 0x66, 0x73, 0x84, 0x87, 0x8a..0x96, or −1, under the left gate),
  0x47cf6c (load row 1..6, unchanged when none) and 0x47cf70 (save row 1..5, unchanged
  when none); then, if 0x47cfb4 = 0, 0x47cf88 = 0 and 0x47cf20 ≠ −1: page 0x47cf34 :=
  0x47cf20 − 10. Always 0x47ceb8 := 0x47ceb4. Rows (0x471108): load k = 1..6 and save
  k = 1..5: Rect(111, 107 + 30(k − 1), 298, 134 + 30(k − 1)); save 6 = Rect(111, 269, 298,
  292).
- **Method:** disassembly.
- **Confidence:** proven

### E-0214 — gmenu::Action 0x46fa74 in the menu (mode 0)
- **Binary/file:** `GILBERT.EXE` 0x46fa74, 0x46f9d4, 0x46fa48, 0x46fa5c, 0x4704d3
- **Evidence:** first := (item ≠ 0x47cf40); nothing at all when the mode is 0x99. Mode 0
  (tables 0x46fad3/0x46fb5f): 0xb: if first {PlayWave(1, 4, 0, 0); StopAll; room music 0x47cf08 ≠ ''
  → PlayRoomMusic(name, 1)}; CloseAll; mode := 1. 0xc: if first {PlayWave(1, 4); StopAll;
  GEExit; GEInit(callbacks); if GELoadFile(HDPath + '\data\game\default.dat') ≠ 0
  {ResetState 0x477964; GEStartNewGame; if InstallationType ≠ −1 → 0x47cf50 := 1};
  0x47cf4c := 1}; CloseAll. 0xd, 0xe: if first {PlayWave(1, 5); ReadSlotNames; 0x47cf64,
  0x47cf68, 0x47cf6c, 0x47cf70 := 0}; 0x47cf88 := 0x47cfb4 := 0. 0xf: if first
  PlayWave(1, 5); the two flags 0. 0x10: if first {PlayWave(1, 5); BuildHelpText};
  0x47cf88 := 1, 0x47cfb4 := 0. 0x11: if first {PlayWave(1, 5); StopAll; BuildCreditsText;
  PlayCreditMusic('credit', 1)}; 0x47cf88 := 0, 0x47cfb4 := 1, 0x47cfb8 := 0. 0x12: if first
  {0x47cf54 := 1; movie::Play('intro.mpg')}; 0x47cf20 := −1; the two flags 0; page := −1.
  0x33: StopAll; if first PlayWave(1, 3, 0, wait); CloseAll; boot::Exit. 0x44 (save):
  PlayWave(1, 0); if 0x47cf70 > 0 → SaveSlot(0x47cf5c + 0x47cf70, 0x47cf74); CloseAll;
  flags 0; ClearPageItem; 0x47cf78 := 0. 0x45 (load): PlayWave(1, 0); if 0x47cf6c > 0
  {GEExit; GEInit; GELoadFile(SlotFileName(0x47cf58 + 0x47cf6c)) ≠ 0 → ResetState,
  0x47cf4c := 0x47cf50 := 1, GEContinueGame; = 0 → 0x47cf4c := 0x47cf50 := 0};
  ClearPageItem; 0x47cf78 := 0. 0x63: PlayWave(1, 1); page 3: 0x47cf78 := 0, 0x47cf58 −= 1
  if > 0; page 4: 0x47cf78 := 0, 0x47cf5c −= 1 if > 0; ClearPageItem. 0x66: PlayWave(1, 1);
  page 3: 0x47cf58 += 1 if < 44; page 4: 0x47cf5c += 1 if < 45 (0x47cf78 := 0 in both);
  ClearPageItem. 0x73: PlayWave(1, 4, 0, wait); if 0x47cfb4 = 1 {StopAll; 0x47ce6c := 9;
  PlayMenuMusic('menu1', 1)}; CloseAll; ClearPageItem; 0x47cf90 := 0. 0x84, 0x87:
  ClearPageItem only. 0x8a..0x8f: PlayWave(1, 0); MusicVolume := 1..6; SetMusicVolume;
  ClearPageItem. 0x90..0x95: SoundVolume := 1..6; SetSoundVolume; PlayWave(1, 0);
  ClearPageItem. 0x96: PlayWave(1, 0); FullscreenVideo := 1 − FullscreenVideo;
  ClearPageItem. At the end 0x47cf40 := item. CloseAll 0x46f9d4: page, 0x47cfd0, 0x47cfc8,
  0x47cf20, 0x47cf1c, 0x47cf30, 0x47cf2c, 0x47cf3c, 0x47cf38 := −1; 0x47cf88 := 0x47cfb4 :=
  0. 0x46fa48: 0x47cf88 := 0x47cfb4 := 0. ClearPageItem 0x46fa5c: 0x47cf48 := 0x47cf44 :=
  −1. Mode 1's item 0x26 (0x4704d3): PlayWave(1, 2); StopAll; 0x47ce6c := 0;
  PlayMenuMusic('menu1', 1); hover, press and page state −1; mode := 0. GE thunks: GEExit
  0x474184, GEInit 0x47416c, GELoadFile 0x47418c, GEStartNewGame 0x474174, GEContinueGame
  0x47417c, GESaveFile 0x474194, GEEllapsed 0x4741ac, GEGetVariable 0x47419c.
- **Method:** disassembly; thunks resolved through their `jmp [IAT]`.
- **Confidence:** proven

### E-0215 — gmenu::DrawPage 0x46bf58: the pages
- **Binary/file:** `GILBERT.EXE` 0x46bf58 (merged into Ghidra's 0x46b490), 0x46daac,
  0x47afbc, 0x47ad38, 0x45c670; `Data/misc/help.txt`, `credits.txt`
- **Evidence:** 0x47cf60 := page; switch (table 0x46bfac): 1 → Action(0xb) if 0x47cf4c; 2 →
  Action(0xc); 3 (load): interface2 0x23 and 0x3f at (102, 63), 0x38 at (104, 100); hover
  row 0x47cf64 > 0 → FillRectAlpha(load rect[k], $000026C4, 50); rows k = 1..6: the text
  IntToStr(0x47cf58 + k) + ': ' + name[0x47cf58 + k] at (119, 85 + 30k), Arial 8, style 0,
  colour $008EBDDD, or $0000FFFF when k = 0x47cf6c, clear brush; 0x45 at (258, 302), 0x63
  at (301, 107), 0x66 at (301, 272). 4 (save, only if 0x47cf50): 0x23 and 0x40 at (102,
  63), 0x39 at (104, 100); hover row 0x47cf68 > 0 → FillRectAlpha(save rect[k], $26C4, 50);
  if 0x47cf70 > 0 and (0x47cf78 = 0 or (0x47cf70 ≠ 0x47cf7c and 0x47cf78 = 1)) → 0x47cf74
  := name[0x47cf5c + 0x47cf70], 0x47cf7c := 0x47cf70, 0x47cf78 := 1; if 0x47cf70 > 0: the
  alpha 0x47cf80 goes down by 2 to 0, then up by 5 to 80 (direction 0x47cf84),
  FillRectAlpha(save rect 6, $26C4, alpha) and 0x47cf74 at (119, 274) in $008EBDDD; rows k
  = 1..5 as on page 3 with 0x47cf5c and 0x47cf70; 0x44 at (258, 302), 0x63 at (301, 107),
  0x66 at (301, 241). 5 (settings): 0x23 and 0x37 at (102, 63); 0x7d at (112, 288); 0x71
  if FullscreenVideo else 0x3c at (279, 293); 0x96 at (246, 294); 0x3b at (108, 97); 0x3c
  at x = 114 + 33j (j = 0..5), y 122, and 0x71 over the MusicVolume-th (switch 0x46ca36);
  0x8a..0x8f at the same x, y 153; 0x3e at (108, 192); 0x3c at y 216 and 0x71 over the
  SoundVolume-th; 0x90..0x95 at y 247. 6 → 0x46daac: interface2 0 and 0x6f at (64, 50);
  when 0x47cf8c = 1 the help surface's Rect(0, 0x47cf90, 355, 0x47cf90 + 320) at (135, 95),
  transparent; interface1 0 at (64, 50); 0x32 at (64, 337); 1 at (192, 56); 0x77 at (509,
  336); 0x73 at (513, 340); 0x84 at (503, 93); 0x87 at (503, 313). 7 (only if 0x47cfb4 =
  1): the credits surface's Rect(0, t, 440, t + 280), t = Trunc(0x47cfb8), at (102, 55),
  transparent; 0x47cfb8 += 0.5; when the surface's height (3000) is not above it, 0. Then
  the page-item hover 0x47cf44: 0x44 or 0x45 → page 3: 0x49, page 4: 0x48, at (258, 302);
  0x63 → 0x64 at (301, 107) (pages 3, 4); 0x66 → 0x67 at (301, 272) (3) or (301, 241) (4);
  0x73 → 0x74 at (513, 340) (6); 0x84 → 0x85 at (503, 93) (6); 0x87 → 0x88 at (503, 313)
  (6). Pressed 0x47cf48 (tables 0x46d5e9/0x46d63c): 0x44 or 0x45 → page 3: 0x4d and Action(0x45),
  page 4: 0x4c and Action(0x44), at (258, 302); 0x63 → 0x65 at (301, 107) (3, 4), then
  Action(0x63); 0x66 → 0x68 at (301, 272) or (301, 241), then Action(0x66); 0x73 → 0x75 at
  (513, 320) and Action(0x73) (6); 0x84 → 0x86 at (503, 93) and Action (6); 0x87 → 0x89 at
  (503, 313) and Action (6); 0x8a..0x96 → Action(item) (page 5). The help scroll 0x47cf90 is
  only ever set to 0 (0x470149, 0x477c2a). BuildHelpText: a 440×1400 surface (made once),
  Fill 0; help.txt through ResolvePath, char by char: '#' style [], '$' [fsBold], '%' []
  (bytes 0x47b1ec, 0x47b1f0); CR or LF: TextOut(0, y) of the collected line, Arial 8,
  colour $00404080, clear brush, y += 10 from 0; 0x47cf8c := 1. BuildCreditsText: 0x47cfb4
  := 0; a 440×3000 surface, Fill 0; credits.txt: '#' size 9 colour $008EBDDD, '$' size 9
  $0000FFFF, '%' size 11 $00FFFFFF; CR or LF: TextOut(221 − w div 2, y + 1) in $00021603,
  then (220 − w div 2, y) in the colour, Arial, style 0, y += 10 from 300; 0x47cfb4 := 1.
  FillRectAlpha 0x45c670: ColorToRGB(colour) or (alpha shl 24) passed to the rectangle
  blend 0x4585ac with mode 8. Trunc 0x4028ec runs under control word 0x1f32 (chop). help.txt
  is 100 B in 4 lines; credits.txt 2,192 B in 114 lines.
- **Method:** disassembly; reading the text files.
- **Confidence:** proven (the drawing); the blend formula and the colour key: Q-0202, Q-0203

### E-0216 — Save slots: gilbert.ini, file names, saving
- **Binary/file:** `GILBERT.EXE` 0x4774dc, 0x477198, 0x4772e0; `Program/gilbert.ini`
- **Evidence:** ReadSlotNames: TIniFile('.\gilbert.ini') (the current directory); for i =
  1..50: name[i] (array 0x487e3c + 4i) := ReadString('SLOT' + IntToStr(i), 'name',
  'default'). SlotFileName(n): n = 0 → HDPath + '\data\game\default.dat'; else HDPath +
  '\data\game\' + ReadString('SLOT' + n, 'file', 'default.dat'). SaveSlot(n, name): nothing
  when InstallationType = −1; n = 0 → GESaveFile(HDPath + '\data\game\default.dat'); else
  WriteString('SLOT' + n, 'file', 'game' + n + '.dat'), WriteString('SLOT' + n, 'name',
  name), GESaveFile(HDPath + '\data\game\game' + n + '.dat'). The shipped gilbert.ini:
  `[SAVEDGAMES] total=50`, then `[SLOT1]`..`[SLOT50]`, each with an empty `file=` and
  `name=`.
- **Method:** disassembly; reading the file.
- **Confidence:** proven

### E-0217 — GEInit's 22 callbacks
- **Binary/file:** `GILBERT.EXE` 0x47b50b..0x47b58f (the same list at 0x46fc20 and 0x46ff3d)
- **Evidence:** pushed 0x474914 first and 0x47491c last, so (stdcall) arguments 1..22 are
  0x47491c GotoWalkmap (5 stack arguments: three values and a byte into 0x480a6c, a flag,
  then the room loader 0x47a190 with argument 4), 0x474964 (walkmap objects through
  GEWalkmapGetNumObjects and GetObjectData), 0x474a28 (1 argument → 0x47a838, CUA),
  0x474a38 (CUA objects), 0x474afc (inventory objects), 0x47454c (dialogue:
  GEDialogGetTitle, GetText, GetNumChoices, GetChoice), 0x4748dc (4 → PlayWave), 0x474900
  (2 → StopWave), 0x4748cc (1 → 0x475548, a wave list), 0x474804 (3: name, loop, kind 0 room
  music, 1 dialogue stream, 2 0x47513c), 0x4748c4 (empty), 0x47453c (1 → movie::Play),
  0x474340 and 0x47435c (Trunc of the player sprite's +0x1c / +0x24 double, adjusted),
  0x4742e8 and 0x4742f0 (empty), 0x4742f8 and 0x47431c (map width, height ÷ 16), 0x474378
  (2 → a cell of map layer 3), 0x4743ac (not read), 0x4742c4 (1 → 0x47ce98 := 1,
  PlayWave(1, 10)), 0x474914 (empty).
- **Method:** disassembly.
- **Confidence:** strong (roles read from the bodies; the details belong to the room and
  ge.dll specs)

### E-0218 — The primary surface's gamma interface
- **Binary/file:** `GILBERT.EXE` 0x47b4d2, 0x477f20, 0x478674
- **Evidence:** the boot calls vtable slot 3 (+0xc) of the interface at primary+0x90 with
  (this, 0, 0x480a8c); the fade 0x477f20 fills three 256-entry word arrays and calls slot 4
  (+0x10) of the same interface with (this, 0, ramp) in a loop; the room draw 0x478674 calls
  slot 4 with 0x480a8c after it. These are the shapes of IDirectDrawGammaControl's
  GetGammaRamp and SetGammaRamp; the interface is not identified by its IID.
- **Method:** disassembly.
- **Confidence:** tentative (Q-0206)

### E-0400 — GEInit, GEExit, the export wrappers and which ge.dll function calls each call-back
- **Binary/file:** `/gilbert-import/GE.DLL`
- **Evidence:** `GEInit` 0x10002560 stores arguments 1..22 in 0x1002860c, 0x10028608,
  0x10028604, 0x10028600, 0x100285fc, 0x100285f8, 0x100285f4, 0x100285f0, 0x100285e4,
  0x100285ec, 0x100285e8, 0x100285e0, 0x100285dc … 0x100285b8 (13..22 descending), then
  `new` 0x2fa40 → `GameObj::GameObj` 0x10002ce0: +0x388 walkmap := 0, +0x38c CUA := 0,
  PathMap ctor 0x10009350 on +0x390 (items, directions, count := 0), +0x2f1cc := 0, +0x2f1d0
  (stopped) := 1, +0x2f260 dialogue := 0, +0x2fa1c/+0x2fa20 counts := 0, then
  `srand(time(0))` (0x1000bc49 / 0x1000bc78). `GEExit` calls the virtual destructor and
  clears the pointer 0x10028610; every export tests it first and returns 0, "" (0x100284e4)
  or, for `GETextGetText`, 0. Cross-references to the call-back slots (capstone sweep of
  `.text`): 1 GotoWalkmap 0x10008fa0; 2 GotoWalkmap and RefreshWalkmap 0x10009080 (called by
  CUAEnd 0x10008930 and Ellapsed 0x10008590); 3 GotoCUA 0x10009090; 4 GotoCUA and UpdateCUA
  0x10009190; 5 UpdateInventory 0x10009230; 6 StartDialog 0x10009300; 7, 8, 10, 11, 12, 21
  RunEvent 0x100060f0; 13, 14 SaveFile 0x100034e0, PathNewPath 0x100055a0, PathEllapsed
  0x10005890; 15, 16 PathNewPath, PathEllapsed; 17, 18, 19 PathNewPath; 20 PathEllapsed and
  PathStop 0x10005d00; 9 and 22 only stored. `GameObj::Log` 0x10009340 is a bare `ret`.
- **Method:** decompilation (`engines/gilbert/notes/decomp/`), disassembly; names in
  `notes/names/GE.DLL-logic.csv`, applied to the project.
- **Confidence:** proven

### E-0401 — GEEllapsed and StepAnim: the tick
- **Binary/file:** `/gilbert-import/GE.DLL` 0x10008590, 0x10008520
- **Evidence:** Ellapsed: dt = timeGetTime() − +0x2f3d8, +0x2f3d8 := now; if +0x38c (CUA)
  is 0 it steps the +0x2fa1c objects of +0x2f3dc, else the +0x2fa20 objects of +0x2f56c,
  collecting each end event in a local array; if any step returned 1: RefreshWalkmap
  (call-back 2) resp. UpdateCUA, then DoEvent for each nonzero end event in array order;
  PathEllapsed(0) at the end in both branches. StepAnim: anim = state(+0x30)+0x28; skipped
  if 0 or duration +0x14 is 0; `if (duration < time + dt)`: out = +0x2c, time := (time + dt)
  % duration, state +0x28 := FindAnim(+0xc) if found, new anim time := 0, return 1; else
  time := (time + dt) % duration, return 0. BuildWalkmapObjects and BuildCUAObjects(1) set
  +0x2f3d8 := timeGetTime().
- **Method:** decompilation.
- **Confidence:** proven

### E-0402 — The walkmap and CUA object arrays, ClearAnims, BuildSort, GetObjectData
- **Binary/file:** `/gilbert-import/GE.DLL`; `default.dat`
- **Evidence:** BuildWalkmapObjects 0x10008170 walks the current walkmap's CUA list (+0x20
  head) and each CUA's object list (+0x24 head), keeps objects with +0x10 ≠ 0 whose state
  +0xc anim exists, sets state +0x28 to it, stops at 100 (`99 < n`), then ClearAnims
  0x10008300, timeGetTime, BuildSort 0x10007e90. BuildCUAObjects 0x10008220 (disassembly:
  stores into +0x2f56c) keeps visible objects of the current CUA whose state +0x10 anim
  exists, no +0x28 store, ClearAnims + time only when its argument ≠ 0, then 0x10008000.
  ClearAnims, per listed object, per state (CObList::FindIndex 0x10015616 over +0x14, count
  +0x20): anim field +0xc (walkmap) or +0x10 (CUA), skipped if 0, FindAnim or return 0,
  state +0x28 := anim, anim +4 := 0. BuildSort (both): selection by `if (best <= z)` with
  best from 0, z = FindAnim(state +0xc / +0x10)+0x24, into a scratch array 800 bytes on,
  copied back. WalkmapGetObjectData 0x10008750 writes code (state +4 + obj +0xc × 100),
  anim(+0x28)+0x28, state +0x1c, anim +0x1c, anim +0x20, state +0x20, state +0x24, returns
  1; CUAGetObjectData 0x10008830 takes x/y from FindAnim(state +0x10) and the picture from
  state +0x28 (−1 when 0). Corpus (`engines/gilbert/tools/logic_stats.py`): 1,182 anims,
  1,181 IDs (40340 twice), no ID 0, z 0..10, duration 0 in 460, next = own ID in 470, end
  events in 58, 5 anim IDs used by two objects of one walkmap or CUA; at most 72 objects
  per walkmap and 31 per CUA.
- **Method:** decompilation and disassembly; `python engines/gilbert/tools/logic_stats.py`.
- **Confidence:** proven

### E-0403 — What the EXE does with the object data: pictures, positions, inventory icons
- **Binary/file:** `GILBERT.EXE` 0x474964, 0x474a38, 0x474afc, 0x479544, 0x4796f8;
  `Data/maps/<room>/w<room>o.wxi`, `cua<id>.wxi`, `Data/maps/!global/inventory.wxi`
- **Evidence:** call-back 2 (0x474964) calls GEWalkmapGetObjectData(i, rec, rec+4, rec+8,
  rec+0x10, rec+0x14, rec+0x18, rec+0xc) into 0x2c-byte records, takes item `rec+4` of the
  image list at [+0x2f4]+0xdc4 → +0x58, gets its rectangle and stores (x + 64, y + 50,
  x + 64 + …, y + 50 + …) with x, y = rec+0x10, rec+0x14; call-back 4 (0x474a38) does the
  same with GECUAGetObjectData and the list at +0x50. Call-back 5 (0x474afc):
  GEInventoryGetObjectData(i, rec, rec+8, rec+0xc). The inventory draw (0x4796f8) draws
  item 0 of the list at +0x4c with pattern `rec+8` in a 6-column grid (26 px rows); the
  carried-object cursor (0x479544) draws item 0 of TgMain+0x31c (DXImageList7 =
  `inventory.wxi`, E-0205) with pattern `rec+8` of the CUA or inventory record.
  `inventory.wxi` holds one picture 3,563×20 with PatternWidth 22 (161 patterns); state
  +0x1c ranges 0..160. Every CUA anim +0x28 of a CUA's objects is below the item count of
  that CUA's `cua<id>.wxi` (477/477), every walkmap anim +0x28 below that of `w<room>o.wxi`
  (27/27).
- **Method:** disassembly (capstone); `wxi.py`; `logic_stats.py`.
- **Confidence:** strong (the collections behind +0x50/+0x58 are inferred from the counts;
  the rooms spec loads them)

### E-0404 — Places, objects and inventory exports
- **Binary/file:** `/gilbert-import/GE.DLL`
- **Evidence:** GotoWalkmap 0x10008fa0: PathStop, FindWalkmap → +0x388, if found
  BuildWalkmapObjects, call-back 1(id, x, y, arg4, 0), call-back 2. GotoCUA 0x10009090:
  PathStop, FindCUA over +0x14 (all CUAs, BuildIndexLists 0x10005d70) → +0x38c, if found
  BuildCUAObjects(1), call-back 3(id), call-back 4, then DoEvent(+0x10) and +0x1c := 0 when
  +0x1c ≠ 0, else DoEvent(+0x14); its first argument is unused. CUAEnd 0x10008930: returns 0
  without a CUA; keeps +0x18, clears +0x38c, BuildWalkmapObjects + call-back 2 if +0x388,
  then DoEvent. WalkmapAreaHit 0x10008710: DoEvent(n % 100 + (+0x388)+4 × 100).
  GetRadarRect 0x10005500: with a CUA, rect of CUA +4 (its walkmap, set by
  BuildIndexLists), else of +0x388, else zeros; `GEWalkmapGetRadarRect` returns left, top,
  right − left, bottom − top. ClickObjectInCUA 0x10008a20: DoEvent(state +0x14) only if
  state +0x20 = 0. ObjectToInventory 0x10008b50: CObList::Find on owner +4 → +0x20, RemoveAt,
  owner := 0, AddTail +0x2f1d4, DoEvent(state +0x18), BuildCUAObjects(0), UpdateCUA,
  UpdateInventory. UseObjectOnObject 0x10008cc0: FindUseObj(+4, +8) → DoEvent(+0xc) and the
  three updates. UpdateInventory: RemoveAll +0x2f1f0, AddTail each +0x2f1d4 object with
  +0x10 ≠ 0, call-back 5. InventoryGetObjectData 0x10008da0 walks +0x2f1f4 (head of
  +0x2f1f0); GEInventoryGetNumObjects → +0x2f1fc. FindObj 0x10005e40 searches +0x30, which
  BuildIndexLists fills with every CUA's objects and the inventory at load time. CObj
  default ctor 0x10009cf0 sets owner +4 := 0; CObjState ctor 0x1000a140 sets +0x28 := 0.
- **Method:** decompilation.
- **Confidence:** proven

### E-0405 — Event types: the effects, their call-backs and order; SetState's fallback
- **Binary/file:** `/gilbert-import/GE.DLL` 0x100060f0, 0x10009e40; `default.dat`
- **Evidence:** RunEvent per case (decompilation and, for 22, disassembly 0x1000742f..): 1
  Find on +0x2f1d4 → delete (vtable +4, 1), RemoveAt, UpdateInventory; else Find on owner
  +0x20 → delete, RemoveAt, BuildCUAObjects(0), UpdateCUA. 2 SetState, 0x100082c0,
  BuildCUAObjects(0), UpdateCUA. 3 error unless +0x1c and +0x20 ≠ 0, GotoCUA. 4 CUAEnd if
  +0x38c ≠ 0, GotoWalkmap(+0x1c, +0x50, +0x54, +0x58). 5 FindTopic, +0x10 := 1, IndexTopics,
  call-back 21(1). 6 +0x40 length 0 → call-back 7(+0x38, +0x3c, +0x48, 0), else call-back
  10(+0x40, +0x48, +0x44). 7 returns early if owner +4 = 0 or Find fails; RemoveAt, owner
  := 0, AddTail inventory, SetState(+0x24 % 100), +0x10 := 1, UpdateInventory,
  BuildCUAObjects(0), UpdateCUA. 8 inventory branch of 1 only. 9 StartDialog(+0x34). 10
  call-back 12(+0x4c) if its first byte ≠ 0. 12/13 FindObjWithState 0x10005e60 then
  FindState → +0x20 := 1/0. 14 SetState(state +4 + 1), 0x100082c0, BuildCUAObjects(0),
  UpdateCUA. 15/16: FindAnim(state +0x10) else log and leave; state +0x28 := anim, time 0;
  +0x10 := 1/0; (15: 0x100082c0); BuildCUAObjects(0), UpdateCUA, UpdateInventory. 17
  call-back 8(+0x38, +0x3c) or call-back 11(). 21 +0x10 := 0, IndexTopics, call-back 21(0).
  22: both FindTopic, requires t2 title or text non-empty; t.title = t.title + t2.title,
  t.text = t.text + t2.text (CString operator+ 0x10016122), t2's strings := empty;
  IndexTopics, then +0x10 := 1, call-back 21(1). SetState: FindState, else
  `FindIndex(+0x14, 0)` — a list node, not its data — stored in +0x30. Corpus
  (`logic_stats.py`): object and state exist for all type 2 (314), 7 (163), 12 (30), 13 (1)
  records; state + 1 exists for all 7 type-14 records; every type-15/16 object has a CUA
  anim in some state (96, 51); type 3 walkmap operand = the CUA's walkmap in 76/117 (the
  rest mostly CUA 999 from other walkmaps); no type-18 record jumps to its own ID; all 127
  type-22 targets are shown in default.dat.
- **Method:** decompilation, disassembly; `logic_stats.py`.
- **Confidence:** proven

### E-0406 — Sound operands: list, index, loop and stream kind (event 6)
- **Binary/file:** `/gilbert-import/GE.DLL` RunEvent case 6; `GILBERT.EXE` 0x4748dc,
  0x474804; `default.dat`
- **Evidence:** case 6 passes (+0x38, +0x3c, +0x48, 0) to call-back 7 and (+0x40, +0x48,
  +0x44) to call-back 10 (E-0405). Call-back 7 = 0x4748dc: PlayWave(arg1, arg2, arg3 ≠ 0,
  arg4 ≠ 0) (0x475624, boot spec's PlayWave(list, index, looped, wait)). Call-back 10 =
  0x474804(name, loop, kind): kind 0 plays `name` as room music (only if it differs from the
  current room music name, which it then remembers), kind 1 stops all and plays the
  dialogue stream, kind 2 stops all and calls 0x47513c; each with `loop`. Corpus: 670 named
  records, +0x44 = 0 in 214 and 1 in 456, +0x48 = 1 in 213; one numbered record (list 2,
  index 0, loop 0).
- **Method:** decompilation (`GILBERT.EXE__FUN_00474804.c`), disassembly; `logic_stats.py`.
- **Confidence:** proven

### E-0407 — Dialogues, texts and variables
- **Binary/file:** `/gilbert-import/GE.DLL`
- **Evidence:** StartDialog 0x10009300: PathStop, FindDialog → +0x2f260 (0 if none),
  call-back 6. DialogGetTitle 0x10008e10 / GetText 0x10008e70: CDialogs +0x24 / +0x28, or
  "\*NO DIALOG\*" (0x10026da0) without a dialogue. GetNumChoices 0x10008ed0: CDialogs +0x10
  (the choice list's count) or 0. GetChoice 0x10008ef0: FindIndex(+4, i) → choice +8, else
  "\*NO CHOICE\*" (0x10026dac). DialogEnd 0x10008f60: +0x2f260 := 0, then FindIndex and
  DoEvent(choice +0xc). GetText 0x10005f40: first CText with +4 = id → +8, else ""
  (0x10028638). GetVariable 0x10005490 returns 0 for n > 199; SetVariable 0x100054b0 stores
  for n < 200; neither checks n < 0.
- **Method:** decompilation; string dump.
- **Confidence:** proven

### E-0408 — Book exports and the topic parser in detail
- **Binary/file:** `/gilbert-import/GE.DLL` 0x100077e0, 0x10007840..0x10007b00; `default.dat`
- **Evidence:** IndexTopics numbers each book's +0x10 ≠ 0 topics into +0x14 from 0 (else
  −1) and their count into +0x2f398[book]. FindTopicByRank 0x10007840 searches the book by
  +0x14. GetNumBookTypes 0x100078c0 counts books until one whose list count (+0x2f28c +
  0x1c·n) is 0; GetNumTopics 0x100078e0 returns +0x2f398[book], 0 for book > 9; GetTopicTitle
  0x10007900 / GetTopic 0x10007a20: +8 / +0xc by rank, "" for book ≥ 10 or no match;
  GetTopicFromIndex 0x10007a00: +4 by rank or 0; GetIndexFromTopic 0x100079c0: +0x14 of the
  topic with that +4 or 0 (no book bound check). ParseFirst 0x10007ae0: cursor +0x2f3c0 :=
  text, ParseNext. ParseNext 0x10007b00: numbers through 0x1000be87 (C `atol`: white space,
  sign, digits), digits skipped with the ctype digit test 0x1000bf1d, one ' ' skipped after
  \f, \g, \h; \h stores the topic only after ':'; `\t` returns 6 without skipping; another
  `\x` leaves the cursor on x with text "\" (0x10026bfc); LF (10) text "\n" (0x10026bf4) → 7;
  ' ' text " " → 1; a byte < 0x20 is skipped before a run; runs end at '\', a byte 0..0x20
  or NUL (signed compare: bytes ≥ 0x80 continue the run); an empty run sets "". default.dat:
  books 0..3 non-empty, 4..9 empty; shown at start 15, 177, 17, 33.
- **Method:** decompilation and disassembly; `gamedat.py`.
- **Confidence:** proven

### E-0409 — The path finder: grid, walkable cells, search, step cost, path arrays
- **Binary/file:** `/gilbert-import/GE.DLL` 0x100055a0, 0x10009350..0x10009c30;
  `GILBERT.EXE` 0x4742e8, 0x4742f0, 0x472bf6
- **Evidence:** PathNewPath: call-backs 18 (h), 17 (w), 16, 15; "Path: Gridsize invalid" if
  15 or 16 returns 0; start = (cb13 / cb15, cb14 / cb16) unsigned, target = (x / cb15, y /
  cb16) signed; "Invalid map size" unless w < 0x65 and h < 0x51; PathMap +4 := w, +8 := h;
  cells[x + 100y] (+0xc) := call-back 19(x, y); FindPath 0x100095a0; success → PathEllapsed(1)
  and return 1, else PathStop and return 0. The EXE's call-backs 15 and 16 are `mov eax,
  0x10; ret`; it calls GEPathNewPath(mouse x − [0x47d1b0], mouse y − [0x47d120]), the same
  offsets call-backs 13/14 subtract from Gilbert's sprite position. Walkable 0x10009930:
  PtInRect(+0x2ee10), cell 1 → no, 0 → yes, else cell = cell(target +0x2ee28/+0x2ee2c).
  FindPath: ResetNodes 0x100094f0 (nodes of 0x14 bytes at +0x7d0c: parent, next, x, y, cost
  0x7fffffff); rect = NormalizeRect(start, target) → InflateRect(3, 3, 4, 4) (0x1001c167:
  left −= 3, top −= 3, right += 4, bottom += 4) → IntersectRect with (0, 0, w, h); Search
  0x10009b60; if target +0 (parent) = 0: reset, rect = (0, 0, w, h), Search again; count the
  parent chain from the target; fewer than 2 nodes → 0; else allocate count − 1 directions
  (+0x2ee30) and cells (+0x2ee34), count at +0x2ee38 (GameObj +0x2f1c0/+0x2f1c4/+0x2f1c8),
  filled backwards: direction = table 0x10026e2c[(dy·3 + dx) + 4] = 3 2 1 4 0 0 5 6 7, cell
  = the parent's x, y. Search: tail +0x2ee0c := start, cost 0, loop Expand, next, clear next.
  Expand 0x10009a70: skip the target; TryStep 0x100099c0 for (x+1,y) 0, (x+1,y−1) 1, (x,y−1)
  2, (x−1,y−1) 3, (x−1,y) 4, (x−1,y+1) 5, (x,y+1) 6, (x+1,y+1) 7: PtInRect, Walkable,
  StepCost(x, y, tx, ty, d), Relax 0x100098d0: c = from.cost + cost; `jge` to.cost ≥ c →
  cost, parent; appended when to.next = 0 and to ≠ tail. StepCost 0x100097d0 (x87 code):
  fild dx = tx − x, ndy = y − ty; dx ≠ 0: fpatan(ndy/dx, 1) × 57.29577951307855 (0x100204e8),
  __ftol; dx = 0: 0, 90 or −90; dx < 0: +180; `(angle + 45·(16 − d)) mod 360` (idiv),
  ≥ 180 → 359 − r; (r + 22.5 (0x100204e0)) × 0.0222… (0x100204d8) + 1.0, × 1.41 (0x100204c8)
  for odd d, __ftol. `GEPathGetItem` returns +0x2f1c4[i] or (0, 0); `GEPathGetMapData` →
  PathMap::GetCell 0x100094b0 (0 outside).
- **Method:** decompilation and disassembly (capstone); constants read from the image.
- **Confidence:** proven

### E-0410 — Path stepping and the direction codes (settles GotoWalkmap's fourth argument)
- **Binary/file:** `/gilbert-import/GE.DLL` 0x10005890, table 0x10026190; `GILBERT.EXE`
  0x4743ac, 0x47491c, 0x47a6ed, 0x4765d2..0x4768da
- **Evidence:** PathEllapsed(start): call-back 20(table[dirs[0]]), target := items[count > 1],
  +0x2f1cc := 1, +0x2f1d0 := 0, flag 0x10028618 and distance 0x10028634 := 0, last position
  := call-backs 13/14. PathEllapsed(0), when +0x2f1d0 = 0 and count ≠ 0: index ≥ count →
  call-back 20(−1), +0x2f1d0 := 1; Gilbert's cell (cb13/cb15, cb14/cb16) = target →
  call-back 20(table[dirs[k]]), k + 1, target := items[min(k, count − 1)], flag and distance
  := 0; else distance += __ftol(fsqrt(dx² + dy²)) (0x10005c03), last := position; distance²
  > cb16² + 2·cb15² sets the flag, ≤ returns unless the flag is set; then 8 if cell x <
  target x, 0x18 if >, else 0x10 if cell y < target y (or equal), else 0; call-back 20 with
  it. Table 0x10026190 = 8 4 0 28 24 20 16 12 for direction indices 0..7. PathStop 0x10005d00:
  call-back 20(−1), +0x2f1d0 := 1. EXE call-back 20 (0x4743ac) sets the walking key set
  [0x47d2f8]: codes 4, 8, 12 → 0x08, 20, 24, 28 → 0x04, 0, 4, 28 → 0x01, 12, 16, 20 → 0x02,
  others clear them; the look-ahead in 0x476c00 moves x −16 for 0x04, +16 for 0x08, y −16
  for 0x01, +16 for 0x02, so 0 N, 4 NE, 8 E, 12 SE, 16 S, 20 SW, 24 W, 28 NW. Call-back 1
  (0x47491c) stores its fourth argument as a byte at +0xc of [0x47d6ac]; the room loader
  (0x47a6ed) copies it to Gilbert's sprite +0x68, which the walking code sets to 4, 28,
  12, 20, 16, 24, 8 (and one computed value) per direction (0x4765d2..0x4768da). CEvent
  +0x58 in type 4: 0 (108), 4 (4), 8 (22), 12 (5), 16 (49), 20 (3), 24 (36), 28 (12).
  SaveFile writes 0 for it (E-0102).
- **Method:** decompilation and disassembly; data dump of the Delphi set constants
  0x47451c.. (08, 04, 01, 02); `logic_stats.py`.
- **Confidence:** proven

### E-0411 — Control-map areas: the EXE's area hits and the events they reach (settles Q-0002)
- **Binary/file:** `GILBERT.EXE` 0x476c00, 0x476cbc, 0x47055d; `/gilbert-import/GE.DLL`
  0x10008710; the 39 `ctrl*.map`, `default.dat`
- **Evidence:** 0x476c00 (called from the eight walking branches 0x476589..0x4768a8): Gilbert's
  position (call-backs 13/14) moved 16 px along the walking keys, cell value v from map
  layer 3 at (x >> 4, y >> 4) (the call-back 19 source); if 0x476cbc (Gilbert's current cell
  is one of GEPathGetItem's cells) and 2 ≤ v ≤ 31: GEWalkmapAreaHit(v − 1). In game mode the
  button item 0x27 (`ibutt15`) plays wave 1/4 and calls GEWalkmapAreaHit(99999)
  (0x47055d via 0x470402). ge.dll adds walkmap × 100 (E-0404). Corpus: for 245 of the 247
  (room, value ≥ 2) pairs of the control maps an event `room × 100 + v − 1` exists (missing:
  room 556 value 10, room 558 value 10); values 0 and 1 in 38 rooms, 2..10, 12..16, 22..29
  elsewhere; events `w × 100 + 99` exist for 32 walkmaps, e.g. 10099 = type 3 to CUA 999,
  comment "Till karta för snabb förflyttning". With E-0409's walkable rule: 0 floor, 1 wall,
  ≥ 2 an area (walkable only towards the same area, and reporting its event).
- **Method:** disassembly; `logic_stats.py`; `gamedat.py` dump.
- **Confidence:** proven (ge.dll side and the value mapping); the layer-3 source of the
  cells is the rooms spec's

### E-0412 — New game, continue, load and save: what they run
- **Binary/file:** `/gilbert-import/GE.DLL` 0x100031a0, 0x100031c0, 0x100031f0, 0x100034e0
- **Evidence:** StartNewGame: DoEvent(1), UpdateInventory. ContinueGame: GotoWalkmap(+4,
  +8, +0xc, +0x10), UpdateInventory. LoadFile (after DeleteAll 0x10002f90): the lists, then
  IndexTopics, BuildIndexLists, owner +4 of every CUA's objects; it does not touch +0x388,
  +0x38c, +0x2f260 (the EXE always loads into a fresh object after GEExit/GEInit, boot spec
  E-0214). SaveFile writes the current walkmap +4, call-backs 13 and 14, 0, then the lists
  as they are in memory (E-0100).
- **Method:** decompilation.
- **Confidence:** proven

### E-0300 — room::Load 0x47a190: GotoWalkmap's files, lists, start scroll and position
- **Binary/file:** `GILBERT.EXE` 0x47491c (GEInit callback 1), 0x47a190, 0x4612a4, 0x44f5c4;
  `GE.DLL` GEInit, GameObj::GotoWalkmap 0x10008fa0; `Data/maps/<n>/`
- **Evidence:** callback 1 (stdcall, `ret 0x14`) stores its arguments in the record 0x480a6c:
  +0 walkmap, +4 x, +8 y, +0xc byte (argument 4), +0xd := (argument 5 ≠ 0), then calls
  0x47a190. 0x47a190: sound::StopAll; if the current room 0x47ced4 ≠ −1 → FadeOut 0x477eac
  (E-0301); shown 0x47ce68 := 0; DXTimer1.Enabled := False; 0x47ce78 := 1; mode 0x47ce74 :=
  0x99. Only when the walkmap differs from 0x47ced4: clear DXImageList4 (+0x310), 5
  (+0x314), 10 (+0x328); ResolvePath of `\data\maps\` + IntToStr(n) + `\` + `w`/`ctrl` + n +
  `.wxi`/`m.wxi`/`.map`/`o.wxi` (strings 0x47a7bc, 0x47a7d0, 0x47a7dc, 0x47a7e8, 0x47a7f8,
  0x47a808, 0x47a818, 0x47a828); load `w<n>o.wxi` → DXImageList10, `w<n>.wxi` →
  DXImageList4, `ctrl<n>.map` → TDxMaps.LoadFromFile 0x44f5c4 on screen+0xdc8 (the
  TMaplibHolder) +0x30 (Maplib3 = DxMapLib3) +0x24, `w<n>m.wxi` → DXImageList5. Then 0x47ceac
  := +0xd (no other reader: its pointer cell 0x47d5d8 is used once); 0x47ced4 := n;
  UpdateLayerSize(3), UpdateLayerSize(4). Start scroll, x = +4: x ≥ 512 → sx := 256 − x,
  raised to −(holder+0x11c − 512) if below; x < 512 → sx := 0; sprite X (+0x1c double) :=
  |x| − |sx|. y = +8 the same with 320, 160 and holder+0x13c − 320 → sprite Y (+0x24). Then
  0x47ce60 := sx + 64, 0x47ce64 := sy + 50; the direction set 0x47ce54 := the 5 bytes at
  0x47a830 (all zero); sprite +0x68 := byte +0xc; mode := 0x47ce78 (1); RefreshWalkmapObjects
  0x474964; GEWalkmapGetRadarRect → 0x47ce7c, 0x47ce80, 0x47ce84, 0x47ce88; object count
  0x47ced0 := 0; if the room music name 0x47cf08 ≠ '' → PlayRoomMusic(name, 1);
  DXTimer1.Enabled := True. ge.dll's GotoWalkmap calls callback 1 with (walkmap, x, y,
  argument 4, 0) and then callback 2 (GEInit stores argument 1 in 0x1002860c, 2 in
  0x10028608). TMaplibHolder (screen+0xdc8) per layer k = 1..8: Maplib +0x24 + 4k, Tilelib
  +0x44 + 4k, PatternTile +0x67 + k, ShowTiles +0x6f + k, AutoMap +0x77 + k, columns +0xcc
  + 4k, rows +0xec + 4k, width +0x10c + 4k, height +0x12c + 4k (UpdateLayerSize: AutoMap →
  item 0's picture size and size ÷ pattern size; else the map's cells × item 0's pattern
  size). The form (notes/exe-forms.md): Maplib3 = DxMapLib3, Tilelib2..5 = DXImageList2..5,
  ShowTiles3 = False, AutoMap3 = False, all others True. Corpus: 38 room folders (100 … 650),
  each with `w<n>.wxi`, `w<n>m.wxi`, `w<n>o.wxi`, `ctrl<n>.map` and `cua999.wxi`; in all 38
  the room and `m` pictures are one item each, the same size, 64×64 patterns, Transparent
  with clFuchsia, width and height multiples of 64 and equal to the control grid × 16;
  `map.wxi` (Tilelib3) is one 512×16 item with 16×16 patterns. default.dat's walkmaps 900 and
  999 have no folder. The `o` pictures: 182 items, PatternWidth/Height 0, Transparent, 62
  clFuchsia, 120 clBlack, 52 of the latter without Picture.Data.
- **Method:** capstone disassembly (a scratch annotator in `build/`); ge.dll decompiles in
  `notes/decomp/`; `wxi.py`/`ctrlmap.py` parsing of every room folder.
- **Confidence:** proven

### E-0301 — Room fades: FadeOut 0x477eac, FadeIn 0x477f20
- **Binary/file:** `GILBERT.EXE` 0x477eac, 0x477f20, 0x478674
- **Evidence:** FadeOut (its argument 0x40 unused): for i = 0..255: work ramp 0x48108c (red
  +0, green +0x200, blue +0x400, words) entry i := saved ramp 0x480a8c entry i shr 2 (each
  channel), then SetGammaRamp(0, work) (primary+0x90, slot 4) — 256 calls, no clock.
  FadeIn: for i = 255 down to 0: 0x48168c, 0x481690, 0x481694 := 0 (no other reader); work
  entry i := saved entry i; SetGammaRamp(0, work); after the loop shown 0x47ce68 := 1. The
  work ramp is zero-initialised data and is only written by these two functions. room::Draw
  calls SetGammaRamp(0, saved) after FadeIn (E-0302).
- **Method:** disassembly; pointer-cell reference search for the three globals.
- **Confidence:** proven (the calls); the interface itself: Q-0206; the duration: Q-0300

### E-0302 — room::Draw 0x478674 and TMaplibHolder::DrawLayer 0x461bc0
- **Binary/file:** `GILBERT.EXE` 0x478674, 0x461bc0, 0x46248c, 0x479544
- **Evidence:** only when CanDraw. X := Trunc(sprite +0x1c), Y := Trunc(+0x24); Fill(back,
  0); DrawLayer(3, origin (0x47ce60, 0x47ce64), Rect(X, Y, X + 96, Y + 96)); DrawLayer(4, the
  origin, Rect(64, 50, 576, 370)); DrawObjectsAndGilbert 0x47897c; DrawLayer(5, the origin,
  Rect(X, Y, X + 96, Y + 96)); DrawRoomPanel 0x46dce8. If shown = 1 → DrawCarriedObject
  0x479544 (carried CUA object 0x47cec0 from the records 0x482810 and inventory object
  0x47cebc from 0x48396c, inventory.wxi, at the mouse − 16 and − the grab offset
  0x47cec8/0x47cecc). If shown = 0: Flip; the same five steps again; Flip; FadeIn;
  SetGammaRamp(0, saved); shown := 1. DrawLayer(holder EAX, layer DX, dest ECX; stack: a
  flag never read, the rectangle R, origin y, origin x, and three zero words overwritten as
  first column, first row, map index; `ret 0x1c`): nothing if ox > clip right (screen
  +0x280) or oy > clip bottom (+0x284) or ox > R.right or oy > R.bottom; tile size = item
  0's pattern size of the layer's Tilelib; if ox < clip left (+0x278) and ox < R.left:
  first column c0 := (R.left − ox) div tile width, x := ox + c0·tile width (rows the same
  with +0x27c and R.top); rows while y < clip bottom and y < R.bottom and row < rows; per
  row, columns while x < clip right and x < R.right and column < columns; tile index =
  (r0 + row)·columns + c0 + column when AutoMap, else the map cell; drawn only when
  ShowTiles: PatternTile → Draw(item 0, x, y, pattern index), else Draw(item index, x, y,
  pattern 0). The clip rectangle is (64, 50, 576, 430) (E-0200).
- **Method:** disassembly, the layer switch tables 0x461c15 and 0x462527 decoded.
- **Confidence:** proven

### E-0303 — room::DrawObjectsAndGilbert 0x47897c: depth split, shadow, frame
- **Binary/file:** `GILBERT.EXE` 0x47897c, 0x463d8c, 0x45c2a4; `Data/anims/gilbert.wxi`
- **Evidence:** only when CanDraw. Pass 1, i = count 0x47ced0 − 1 down to 0 over the records
  0x4816b4 (0x2c bytes): h := GetHeight(DXImageList10 item rec+4) (PatternHeight, else the
  picture height, 0x463c30); if not (sprite Y + 96.0 (single at 0x479014) < oy + rec+0x14 +
  h) → Draw(item, back, ox + rec+0x10, oy + rec+0x14, pattern 0). Shadow: if the frame
  0x47cea4 ≤ 0x77 → DrawAlpha(gilbert.wxi item 1, back, Rect(X, Y, X + 96, Y + 96), pattern
  = frame, alpha 0x46); else by sprite +0x68 (byte table 0x478b2a, jump table 0x478b47): 0 →
  pattern 15, 4 → 60, 8 → 30, 12 → 90, 16 → 105, 20 → 75, 24 → 0, 28 → 45, other values →
  no shadow. Gilbert: Draw(gilbert.wxi item 0, back, Trunc(X), Trunc(Y), frame). Pass 2: the
  same loop, drawing the records pass 1 skipped. DrawAlpha 0x463d8c (EAX item, EDX dest, ECX
  rect, stack pattern then alpha, `ret 8`): pattern in range → the surface blend 0x45c2a4
  with the pattern's source rectangle and the item's Transparent flag, which picks blend 8
  for alpha < 255 and 1 (copy) at 255. gilbert.wxi: item 0 `gilbert` 20,736×96, 96×96
  patterns (216), fuchsia; item 1 `all` 14,391×120, 4 bpp, 120×120 patterns (119), fuchsia —
  black silhouettes (looked at).
- **Method:** disassembly; pictures rendered to PNG and looked at.
- **Confidence:** proven (order, tests, patterns); the scaling of the 120×120 shadow into the
  96×96 rectangle: strong (DelphiX's rectangle blend), Q-0301

### E-0304 — Gilbert's movement: TPlayerSprite::DoMove 0x476520, the move count, Ctrl
- **Binary/file:** `GILBERT.EXE` VMT 0x475b20 (slot +8 = 0x476520), 0x469fa0, 0x474108,
  0x465a48, 0x464f5c, 0x446040, 0x47b740
- **Evidence:** mode 1 of the main loop: 0x478674, 0x4728ec, 0x474108, (dialogue open
  0x47cf94: 0x4740fc (empty), 0x473f74, 0x479018), 0x469854 on DXInput1,
  DXSpriteEngine1.Move(1000 div (LagCount + 0x47cea8)) (0x465a48 → TSprite.Move 0x464f5c:
  DoMove when +0x19, then the children), DrawCursor, Flip, stream updates (0x484ac8 when
  0x47cee4 = 1 and shown = 1; 0x484acc when 0x47cee8; 0x484ad0 when 0x47ceec; 0x484ad4 when
  0x47cee4; 0x484ad8 when 0x47cef4). 0x474108: GetAsyncKeyState(VK_CONTROL (0x11)) < 0 →
  0x47cea8 := 20, else 30 (ResetState: 30). TDXTimer idle 0x446040: when timeGetTime − last ≥
  Interval: LagCount := Max((elapsed) div Max(Interval, 1), 1). DoMove(MoveCount m):
  inherited DoMove (TImageSprite 0x4651b8, AnimSpeed never set); f := Trunc(+0x5c single);
  then by the set 0x47ce54 (bits 1 up, 2 down, 4 left, 8 right), first match: up+right: Y −=
  m·0.053, X += m·0.053, base 60, +0x68 := 4; up+left: Y −, X −, 45, 28; down+right: Y +, X
  +, 90, 12; down+left: Y +, X −, 75, 20; up: Y −= m·0.075, 15, 0; down: Y +, 105, 16; left: X
  −= m·0.075, 0, 24; right: X +, 30, 8 (extended constants 0x476bd0 = 0.053, 0x476bdc =
  0.075); each first calls StepAreaCheck 0x476c00 (E-0307, always true); frame 0x47cea4 :=
  base + (f > 15 ? 0 : f), walking +0x6c := 1. No bit: f > 11 → 0; frame := table
  (+0x68 via 0x47690a/0x476927): 0 → 168 + f, 4 → 144, 8 → 156, 12 → 204, 16 → 120, 20 →
  192, 24 → 180, 28 → 132 (+ f); other facings leave the frame; +0x6c := 0. Counter +0x5c
  += m·0.002 (0x476be8) idle, limit 11, or m·0.02 (0x476bf4) walking, limit 14; above the
  limit → 0. Walking and f ≠ 0x47ceb0: f = 0 → PlayWave(1, 6, 0, 0), f = 6 → PlayWave(1, 7,
  0, 0); 0x47ceb0 := f always. +0x6d := +0x6c. Clamps: Trunc(X) − 0x47ce60 < −48 → X :=
  0x47ce60 − 48; W − 48 ≤ Trunc(X) − 0x47ce60 → X := W − 49 + 0x47ce60 (W = holder+0x118);
  Y the same with 0x47ce64 and holder+0x138. CreatePlayerSprite 0x47b740: +0xfc :=
  DXImageList9, +0x5c := 0, +0x60 := 11, +0x64 := 0, +0x68 := 0, image gilbert.wxi item 0, X
  272, Y 210, 96×96; the rect (112, 98, 528, 322) goes to 0x480a7c (no reader). The
  direction set is written only by room::Load and GEInit callback 20 (E-0308).
- **Method:** disassembly; 80-bit constants decoded; pointer-cell reference search.
- **Confidence:** proven

### E-0305 — room::HandleMouse 0x4728ec: buttons, walking, cursors, edge scrolling
- **Binary/file:** `GILBERT.EXE` 0x4728ec, 0x46a518, 0x46a568, 0x475d04
- **Evidence:** pressed 0x47cf30 := −1; 0x475b48 (inventory hovers 0x47ce4c/0x47ce50);
  hover 0x47cf2c := the first of interface2 8, 0x26, 0x27, 0x2c, 0x2d whose BoundsRect meets
  the mouse rect, else −1. Rects A (74, 60, 566, 420), (72, 370, 132, 422) (built, not
  used), C (289, 328, 351, 380), D (509, 336, 539, 366), E (74, 360, 566, 420). If
  PtInRect(A, mouse) and not C, D or E: if the button state 0x47ceb4 = 1 →
  GEPathNewPath(mx − 0x47ce60, my − 0x47ce64) (every tick); 0x47cec4 := 0; v := GetCell(3,
  (mx − 0x47ce60) div 16, (my − 0x47ce64) div 16) as a signed 16-bit value: 1 → cursor
  0x47ce8c := 6, ≥ 2 → 7, else 0. Otherwise cursor := 0 and: 64 ≤ mx ≤ 74 and 0x47ce60 <
  64 → cursor 2, 0x47ce60 += 6, X += 6.0 (0x473004); else 566 ≤ mx ≤ 576 and 0x47ce60 ≥
  −(holder+0x118 − 586) → cursor 3, 0x47ce60 −= 6, X −= 6; then my ≤ 60 and 0x47ce64 < 50 →
  cursor 4, 0x47ce64 += 6, Y += 6; else 420 ≤ my ≤ 430 and 0x47ce64 ≥ −(holder+0x138 − 394)
  → cursor 5, 0x47ce64 −= 6, Y −= 6 (0x47cec4 := 1 in these branches; it has no reader).
  New button state (0x47ceb8 ≠ 0x47ceb4): hover := −1; if left: pressed := the first hit of
  8, 0x26, 0x27, 0x2c, 0x2d, else −1; 0x47ceb8 := 0x47ceb4. MouseDown sets 0x47ceb4 (1 left,
  2 right) only when it is −1; MouseUp sets it and 0x47ceb8 to −1 and, in modes 1 and 2 with
  a carried object, calls 0x475d04, which outside mode 2 only clears 0x47cec0 and 0x47cebc.
  The object records 0x4816b4 are read only by the draw (pointer cell 0x47d130: 0x47498b,
  0x4789b9, 0x478f4a).
- **Method:** disassembly.
- **Confidence:** proven

### E-0306 — ui::DrawRoomPanel 0x46dce8 and the room buttons' actions
- **Binary/file:** `GILBERT.EXE` 0x46dce8, 0x46fa74 (mode 1 branch 0x4703ed);
  `Data/maps/!global/interface2.wxi`
- **Evidence:** interface1 item 0 at (64, 50); v := GEGetVariable(199) (kept in 0x47ce44):
  0 → i2[4] iscr12, 1..6 → i2[0x99..0x9e] egg1..egg6, at (296, 374) (other values: none);
  i2[6] iscr_radar (115×75) at (151, 347); pulse a = 0x47ce90 with direction 0x47ce94: down
  by 1 to 0, then up by 1 to 50; R := (152 + l, 348 + t, 152 + l + w, 348 + t + h) from the
  radar values (GEWalkmapGetRadarRect returns left, top, right − left, bottom − top of the
  CWalkmap's +0xc..+0x18); FillRectAlpha(R, $008EBDDD, a); on the back buffer's canvas:
  Pen.Mode 4, Pen.Style 0, Pen.Color $0028B5F9, Brush.Style 1, Rectangle(R); i2[0x26]
  ibutt11 "Menu" at (70, 368), i2[0x27] ibutt15 "Kort" at (70, 396), i2[0xa8] ibutt43 at
  (537, 380), i2[0xa9] ibutt42 at (537, 400); new-topic flag 0x47ce98 = 0 → i2[8] ibutt14 at
  (298, 333); else b = 0x47ce9c with direction 0x47cea0: down by 2 to 50, then up by 8 to
  200; i2[8] at (298, 333), then DrawAlpha(i2[0xa], Rect(298, 333, 346, 373), pattern 0,
  alpha b). Hover: 8 → i2[9] at (298, 333), 0x26 → i2[0x28] at (70, 368), 0x27 → i2[0x29] at
  (70, 396). Pressed: 8 → i2[0xa] at (298, 333), Action(8); 0x26 → i2[0x2a] at (70, 368),
  Action(0x26); 0x27 → i2[0x2b] at (70, 396), Action(0x27). Action in mode 1: 8: PlayWave(1,
  4); LoadBookImages; 0x46aa54(1, 0); 0x47cfd4 := 0x47cffc := 0; 0x47ce98 := 0; 0x47cfd8 :=
  0x47cfd0 := 0x4e; hover/press/page state −1; mode := 4. 0x26: E-0214. 0x27: PlayWave(1,
  4); GEWalkmapAreaHit(99999); state −1; mode := 2. 0x2c: PlayWave(1, 1); if 0x47cedc ≥ 6:
  −6 and 0x475ea4. 0x2d: PlayWave(1, 1); if 0x47cedc + 12 ≤ 0x47cee0: +6 and 0x475ea4.
  Names and sizes from `wxi.py`; pictures looked at (Menu, Kort, the scroll, arrows, radar
  island, eggs).
- **Method:** disassembly; pictures rendered to PNG.
- **Confidence:** proven

### E-0307 — Area hits: StepAreaCheck 0x476c00, GilbertOnPath 0x476cbc, GetCell 0x462f8c
- **Binary/file:** `GILBERT.EXE` 0x476c00, 0x476cbc, 0x462f8c; `Data/maps/*/ctrl*.map`
- **Evidence:** StepAreaCheck ignores its register arguments: gx := GilbertX (0x474340), gy
  := GilbertY (0x47435c); −16 on gx if left, +16 if right, −16 on gy if up, +16 if down (the
  set 0x47ce54); v := GetCell(3, gx div 16, gy div 16) (sign-extended 16-bit); if
  GilbertOnPath: v − 2 in 0..29 → GEWalkmapAreaHit(v − 1) (three identical branches for
  2..11, 12..21, 22..31); returns 1 in every case. GilbertOnPath: cx := GilbertX shr 4, cy :=
  GilbertY shr 4 (logical shifts); true when some i < GEPathGetNumItems has
  GEPathGetItem(i) = (cx, cy) (out-parameters 2 and 3). GetCell(holder, layer, map, stack x
  then y): layer 3 without AutoMap: x > the map's width or x < 0 or y > height or y < 0 → 0;
  else the low word of the u32 at index y·width + x of the map's data (TDxMaps.ReadData
  0x44f50c reads the whole `size` = width·height·10 bytes, so x = width or y = height reads
  the next row or the tail). Corpus: cell values 0 (52,995), 1 (65,847), 2..16 and 22..29;
  the tails are zero except in 170 (u32 6,948 and 0x80000007 at tail indices 7 and 8, i.e.
  row 36, x 7 and 8), 400, 461, 463, 550 (beyond the first row).
- **Method:** disassembly; `ctrl*.map` statistics in Python.
- **Confidence:** proven

### E-0308 — The room's GEInit callbacks 2, 7..10, 13, 14, 17..21
- **Binary/file:** `GILBERT.EXE` 0x474964, 0x4748dc, 0x474900, 0x4748cc, 0x475548,
  0x475624, 0x474804, 0x47513c, 0x474340, 0x47435c, 0x4742f8, 0x47431c, 0x474378, 0x4743ac,
  0x4742c4; `GE.DLL` GameObj::WalkmapGetObjectData 0x10008750, BuildWalkmapObjects
  0x10008170
- **Evidence:** 2: count := GEWalkmapGetNumObjects → 0x47ced0; for i: GEWalkmapGetObjectData(i,
  &rec+0, &+4, &+8, &+0x10, &+0x14, &+0x18, &+0xc) into rec = 0x4816b4 + 0x2c·i; ge.dll fills
  them with obj.id·100 + state, the anim's +0x28, the state's +0x1c, the anim's +0x1c, +0x20,
  the state's +0x20 (pickable), +0x24 (text); ge.dll lists at most 100 visible objects whose
  state has a walkmap anim. The EXE then stores PatternRect(DXImageList10 item +4, 0) at
  +0x1c..+0x28 and offsets it: +0x1c := x + 64, +0x20 := y + 50, +0x24 := right + x + 64,
  +0x28 := bottom + y + 50. 7: PlayWave(a1, a2, a3 ≠ 0, a4 ≠ 0). 8: StopWave(a1, a2). 9:
  0x475548(n): if n ≠ 0x47cf0c: `\data\sounds\misc\` + n + `.wxs` → DXWaveList3, 0x47cf0c :=
  n, flag 0x47cf00, SetSoundVolume. PlayWave(list, …) first calls 0x475548(list) when list ≠
  1 and list ≠ 0x47cf0c, then plays item index of DXWaveList `list` (1..4). 10 (name, loop,
  kind): kind 0 → if name ≠ 0x47cf08: PlayRoomMusic(name, loop); 0x47cf08 := name; kind 1
  → StopAll, PlayDialogStream; kind 2 → StopAll, 0x47513c: `\data\sounds\misc\` + name +
  `.wav` into stream 0x484ad8, SoundVolume, started, flag 0x47cef4. 13: Trunc(X) − 0x47ce60 +
  0x30; 14: Trunc(Y) − 0x47ce64 + 0x30. 17: holder+0x118 div 16; 18: holder+0x138 div 16.
  19 (a1, a2): GetCell(3, map 0, x = a1, y = a2) sign-extended. 20 (d): right := d ∈ {4, 8,
  12}; left := d ∈ {20, 24, 28}; up := d ∈ {0, 4, 28}; down := d ∈ {12, 16, 20} (set include
  0x402b88 / exclude 0x402b94 with the constants 0x47451c = 8, 0x474524 = 4, 0x47452c = 1,
  0x474534 = 2). 21: 0x47ce98 := 1, PlayWave(1, 10, 0, 0). 12: movie::Play (E-0208).
  Corpus: the 27 states with a walkmap anim all name a picture below their room's
  `w<n>o.wxi` item count.
- **Method:** disassembly; ge.dll decompiles; default.dat through `gamedat.py`.
- **Confidence:** proven

### E-0309 — ResetState 0x477964: the room variables at a new game or load
- **Binary/file:** `GILBERT.EXE` 0x477964
- **Evidence:** among others: 0x47ce44 := 0, 0x47ce4c, 0x47ce50 := −1, 0x47ce5c := 1,
  0x47ce60 := 0x47ce64 := 0, shown 0x47ce68 := 0, 0x47ce6c := 0, mode and 0x47ce78 := 0x99,
  radar 0x47ce7c..0x47ce88 := 0, cursor 0x47ce8c := 0, 0x47ce90 := 0, 0x47ce94 := 1,
  0x47ce98 := 0, 0x47ce9c := 0, 0x47cea0 := 1, frame 0x47cea4 := 0, 0x47cea8 := 30,
  0x47ceb0, 0x47ceb4, 0x47ceb8, 0x47cebc, 0x47cec0 := −1, 0x47cec4 := 0, 0x47cec8 :=
  0x47cecc := 0, 0x47ced0 := 0, current room 0x47ced4 := −1, 0x47ced8, 0x47cedc, 0x47cee0
  := 0, the stream flags 0x47cee4..0x47cef4 := 0, 0x47cf0c := 0, MusicVolume 0x47cf10 := 5,
  SoundVolume 0x47cf14 := 4, FullscreenVideo 0x47cf18 := 0, the menu state (E-0210 values),
  0x47cf94 := 0. The room music name 0x47cf08 is not reset.
- **Method:** disassembly.
- **Confidence:** proven

### E-0500 — cua::Load 0x47a838 (GEInit callback 3): the close-up's pictures, mode 2
- **Binary/file:** `GILBERT.EXE` 0x474a28, 0x47a838; `Data/maps/<room>/cua*.wxi`,
  `Data/maps/!global/kartmap.wxi`, `Data/maps/cua999.wxi`; `default.dat`
- **Evidence:** callback 3 (0x474a28) passes its one argument (the CUA ID) to 0x47a838:
  DXTimer1.Enabled := false (0x446240); StopAll; DXImageList8 (TgMain+0x320,
  `ImageLibs.Imagelib3`, holder+0x50) emptied (0x4105a0) if it has items; ID = 999 (0x3e7) →
  ResolvePath(`\data\maps\!global\kartmap.wxi`) loaded into DXImageList8 (0x4646e8); else
  ResolvePath(`\data\maps\` + IntToStr(0x47ced4, the current room) + `\` + `cua` +
  IntToStr(ID) + `.wxi`) (six-piece LStrCatN 0x403d10, strings 0x47aa18/0x47aa2c/0x47aa38/
  0x47aa44), then GEWalkmapGetRadarRect(&l, &t, &w, &h) into 0x47ce7c..0x47ce88 (not for 999);
  both: CUA object count 0x47ced8 := 0, mode 0x47ce74 := 2; room music 0x47cf08 ≠ '' →
  PlayRoomMusic(name, looped); DXTimer1.Enabled := true. No gamma call (no fade). ge.dll's
  GotoCUA 0x10009090 calls callback 3 (DAT_10028604) with the CUA ID, then callback 4, then
  the first or later event. Corpus: 38 room folders each hold `cua999.wxi`, identical to
  `kartmap.wxi` and `maps/cua999.wxi` (MD5 e0b62fa5…, 19 items); the loader never builds
  that name for 999. 106 other `cua<n>.wxi`; item 0 is the background (`!cu<n>` 70, `!bk…`
  in the 999 copies, one `!Cu`): 512×320 (68), 512×340 (2), 580×340 (1), kartmap 512×324.
  Type-3 events name (walkmap, CUA) pairs: 105 pairs, all with a file in that walkmap's folder
  except (250, 210) and (250, 209) (events 20011, 20012), whose files are in `maps/200/`;
  their IDs 200·100 + 11/12 are area hits of room 200, so the current room's folder has them.
- **Method:** disassembly; `wxi.py`; MD5; `gamedat.py` statistics.
- **Confidence:** proven

### E-0501 — gecb::RefreshCUAObjects 0x474a38 (callback 4): the CUA object table
- **Binary/file:** `GILBERT.EXE` 0x474a38, 0x463c58; `GE.DLL` GameObj::CUAGetObjectData
  0x10008830, BuildCUAObjects 0x10008220, BuildSort 0x10008000, ClearAnims 0x10008300,
  StepAnim 0x10008520; `default.dat`
- **Evidence:** count := GECUAGetNumObjects → 0x47ced8; for i < count, record r = 0x482810 +
  0x2c·i: GECUAGetObjectData(i, &r+0, &r+4, &r+8, &r+0x10, &r+0x14, &r+0x18, &r+0xc) (pushed
  last to first). ge.dll fills: +0 obj.id·100 + state number; +4 the state's current anim
  (CObjState +0x28, set by ClearAnims to the cua_anim and replaced by StepAnim along `next`)
  +0x28, or −1 when there is none; +8 the state's +0x1c; +0x10, +0x14 the cua_anim's +0x1c,
  +0x20 (the first anim of the state, not the current one); +0x18 pickable (+0x20); +0xc the
  text (+0x24). Then PatternRect(DXImageList8 item r+4, pattern 0) (0x463c58 copies the
  pattern's source rectangle, (0, 0, w, h) for unpatterned pictures) and +0x1c := x + 64,
  +0x20 := y + 50, +0x24 := w + x + 64, +0x28 := h + y + 50. ge.dll lists at most 100
  visible objects of the CUA whose state has a cua_anim that exists, ordered by BuildSort:
  repeatedly the remaining object with the largest anim z (+0x24; ties → the later one), so
  index 0 has the highest z. Corpus: following every state's cua_anim through `next`, 1,138
  anim steps name a picture index (+0x28) below the item count of their CUA's file (0 out of
  range); picture 1 of cua101.wxi is `10101_00` = object 10101's anim 10180 with +0x28 = 1.
- **Method:** disassembly; ge.dll decompiles; `gamedat.py` + `wxi.py` cross-check.
- **Confidence:** proven

### E-0502 — cua::Draw 0x4794c0, cua::DrawObjects 0x479618 and the mode 2 tick
- **Binary/file:** `GILBERT.EXE` 0x469fa0 (case 2 at 0x46a1bf), 0x4794c0, 0x479618, 0x479544
- **Evidence:** tick in mode 2: 0x4794c0; if dialogue open (0x47cf94): 0x4740fc (ret),
  dialog::HandleMouse 0x473f74, dialog::Draw 0x479018; 0x47412c (ret); cua::HandleMouse
  0x473008; ui::DrawCursor; Flip; stream updates (room music only when shown 0x47ce68,
  dialogue, credits, menu, fifth). 0x4794c0 (only when CanDraw): Fill(back, 0); DXImageList8
  item 0 at (64, 50); 0x479618; cua::DrawFrame 0x46e414; 0x479544. 0x479618: for i from
  count − 1 down to 0, skipping i = carried CUA index 0x47cec0: if r+4 (unsigned) < the item
  count of DXImageList8 → Draw(item r+4, back, 64 + r+0x10, pattern 0, 50 + r+0x14).
  0x479544 (named ui::DrawCarriedObject by rooms, E-0302): carried CUA index ≠ −1 →
  DXImageList7 item 0 (`inventory.wxi`), pattern = its r+8, at (mouse x − 16, mouse y − 16);
  carried inventory index 0x47cebc ≠ −1 → the same strip, pattern = inventory r+8, at (mouse
  x − 0x47cec8, mouse y − 0x47cecc).
- **Method:** disassembly.
- **Confidence:** proven

### E-0503 — cua::DrawFrame 0x46e414: the panel in mode 2
- **Binary/file:** `GILBERT.EXE` 0x46e414, 0x4796f8, 0x477fbc
- **Evidence:** interface1 item 0 at (64, 50); GEGetVariable(199) (push 0xc7) into 0x47ce44:
  0 → i2[4] at (296, 374), 1..6 → i2[0x99..0x9e]; i2[5] iscr13 (167×50) at (371, 375);
  inventory::Draw 0x4796f8; i2[6] at (151, 347); radar pulse 0x47ce90 (direction 0x47ce94):
  down by 1 below 1 → 0 and up, up by 1 from 150 (cmp 0x96) → 150 and down; FillRectAlpha
  (152 + l, 348 + t, 152 + l + w, 348 + t + h) in $008EBDDD with that alpha; Pen.Mode 4,
  Style 0, Color $0028B5F9, Brush clear, Rectangle of the same; i2[0x26] at (70, 368), i2[0x98]
  ibutt45 (the red "Kort") at (70, 396), i2[0x2c] ibutt13 at (537, 380), i2[0x2d] ibutt12 at
  (537, 400); new-topic flag 0x47ce98: 0 → i2[8] at (298, 333), else the blink of E-0306
  (0x47ce9c down 2 to 50, up 8 to 200; i2[8] then DrawAlpha i2[0xa] in (298, 333)–(346,
  373)); i2[0x77] at (509, 336), i2[0x73] at (513, 340). Hover 0x47cf2c: 0x26 → i2[0x28] at
  (70, 368), 0x2c → i2[0x2e] at (537, 380), 0x2d → i2[0x2f] at (537, 400), 0x73 → i2[0x74] at
  (513, 340). Pressed 0x47cf30: 0x26 → i2[0x2a], Action(0x26); 0x2c → i2[0x30], Action(0x2c);
  0x2d → i2[0x31], Action(0x2d); 0x73 → i2[0x75], Action(0x73), same places. Then
  ui::DrawTooltip(0x47ce4c, −1) and (−1, 0x47ce50). Items 8 and 0x27 get no hover or pressed
  picture and no Action here; the only Action call sites with 0x27 are 0x46e405 (room panel)
  and 0x46f9cb (mode 5). Pictures looked at: 0x98 and 0x76 are red "disabled" looks.
- **Method:** disassembly; call-site scan of 0x46fa74 over 0x469000..0x47c000; PNGs.
- **Confidence:** proven

### E-0504 — cua::HandleMouse 0x473008 and gmenu::Action in mode 2
- **Binary/file:** `GILBERT.EXE` 0x473008, 0x46fa74 (mode 2 branch), 0x4741e4, 0x47421c
- **Evidence:** 0x47cf30 := −1; cua::HoverObjects 0x475b48; cursor 0x47ce8c := 0; hover
  0x47cf2c := first of i2 items 8, 0x26, 0x27, 0x2c, 0x2d, 0x73 whose BoundsRect intersects
  the mouse rectangle 0x4816a4, else −1. If the button state 0x47ceb4 differs from the last
  seen 0x47ceb8: hover := −1; if the state is 1 (left): for every i < count whose rectangle
  r+0x1c contains the mouse point (PtInRect) and the point is not in (509, 336)–(589, 396):
  GEClickObjectInCUA(r+0); then 0x47cf30 := the same first-hit chain; 0x47ceb8 := state.
  Action mode 2: 0x2c: PlayWave(1, 1), if 0x47cedc > 5: −6 and inventory::Layout; 0x2d:
  PlayWave(1, 1), if 0x47cedc + 12 ≤ 0x47cee0: +6 and Layout; 0x26: PlayWave(1, 2), StopAll,
  hover/press/page state −1, mode 0 (no menu frame counter reset, no `menu1`); 0x27:
  PlayWave(1, 4), state −1, mode 5; 0x73 when no dialogue is open: PlayWave(1, 4), StopAll,
  state −1, mode 1, GECUAEnd, room music (looped) if set. Every branch clears 0x47cfd0,
  0x47cfc8, 0x47cf1c..0x47cf3c. ge.dll ClickObjectInCUA runs click_event only when the
  state is not pickable.
- **Method:** disassembly; ge.dll decompile.
- **Confidence:** proven

### E-0505 — Descriptions: cua::HoverObjects 0x475b48 and ui::DrawTooltip 0x477fbc
- **Binary/file:** `GILBERT.EXE` 0x475b48, 0x477fbc, 0x478228
- **Evidence:** 0x475b48: 0x47ce4c := the first CUA index (only in mode 2) whose r+0x1c
  rectangle contains the mouse point, else −1; 0x47ce50 := the last inventory index whose
  rectangle contains it, else −1. 0x477fbc(c, n) (nothing when both −1): c ≠ −1 → text :=
  CUA r+0xc, x := r+0x1c, y := r+0x20 + (r+0x28 − r+0x20) div 2; n ≠ −1 → text := inventory
  r+0xc, x := r+0x1c, y := r+0x20 − 10; empty text → nothing. Font Arial 8, style [] (byte
  0x478230 = 0), colour $008EBDDD; w := TextWidth; x := min(x, 560), x := max(x, 80), y :=
  max(y, 66); x + w > 560 → x −= w; FillRectAlpha((x − 4, y − 2, x + w + 4, y + 16), colour
  0, alpha 0x78); TextOut(x, y) in the same font and colour.
- **Method:** disassembly.
- **Confidence:** proven

### E-0506 — Carrying: mouse events, cua::PickUp 0x475c14, cua::Drop 0x475d04
- **Binary/file:** `GILBERT.EXE` 0x46a488, 0x46a518, 0x46a568, 0x475c14, 0x475d04;
  `GE.DLL` ObjectToInventory 0x10008b50, UseObjectOnObject 0x10008cc0; `default.dat`
- **Evidence:** MouseMove stores the point (0x48169c, 0x4816a0) and the rectangle (x − 3,
  y − 3, x + 3, y + 3) (0x4816a4); with the state −1 it sets 1 when Shift has ssLeft, 2 with
  ssRight. MouseDown: state −1 → 1 (left) / 2 (right) / −1; then in mode 2 (any button)
  0x475c14: for each CUA i whose rectangle contains the point and r+0x18 ≠ 0: carried CUA
  0x47cec0 := i, offset (0x47cec8, 0x47cecc) := point − (left, top) (last match wins); for
  each inventory i whose rectangle contains the point: carried inventory 0x47cebc := i, the
  same offset. MouseUp (any button): state and last state := −1; in modes 1 and 2 with
  something carried → 0x475d04. 0x475d04: mode ≠ 2 → both carries := −1. CUA count 0 →
  both −1. Carried CUA ≠ −1 and the point in Rect(364, 367, 576, 429) →
  GEObjectToInventory(CUA r+0 of the carried index). Then for each CUA j ≠ carried CUA index
  whose rectangle contains the point: GEUseObjectOnObject(CUA r+0 at the carried CUA index,
  CUA r+0 of j) (with no CUA object carried this reads index −1: the dword 44 bytes before
  0x482810, i.e. record 100 of the walkmap table 0x4816b4 (0x482810 − 0x4816b4 = 101·44),
  which ge.dll never fills (at most 100 walkmap objects): 0). Then carried inventory ≠ −1:
  for each CUA j containing the point: GEUseObjectOnObject(inventory r+0, CUA r+0 of j).
  Finally both carries := −1. ge.dll: ObjectToInventory moves the object to the inventory,
  runs take_event, rebuilds the CUA list, calls callbacks 4 and 5; UseObjectOnObject finds
  the CUseObj (obj, target), runs its event, same refresh; not found → a log line only.
  Corpus: no CUseObj has obj 0 (203 use-objects).
- **Method:** disassembly; ge.dll decompiles; `gamedat.py`.
- **Confidence:** proven

### E-0507 — The inventory: the strip, the table, layout and drawing (Q-0100: see E-0403)
- **Binary/file:** `GILBERT.EXE` 0x474afc, 0x475ea4, 0x4796f8, 0x46fa74; `GE.DLL`
  InventoryGetObjectData 0x10008da0, UpdateInventory 0x10009230; `Data/maps/!global/inventory.wxi`,
  `inventory-num.wxi`; `default.dat`
- **Evidence:** `inventory.wxi`: one item `inv`, 3563×20, PatternWidth 22, PatternHeight 0
  (the whole height), fuchsia transparent: 161 cells (3563 div 22), indices 0..160. CObjState
  +0x1c in default.dat: 0..160; all 69 pickable states have it ≠ 0; the 391 states with 0 are
  not pickable. Callback 5: count := GEInventoryGetNumObjects → 0x47cee0; for i:
  GEInventoryGetObjectData(i, &r+0, &r+8, &r+0xc) into r = 0x48396c + 0x2c·i (ge.dll: code,
  state +0x1c, text); then 0x475ea4. ge.dll's inventory list is the objects moved to it that
  are visible, in the order they arrived. 0x475ea4: first := 0x47cedc, last := min(first +
  12, count); for k < count: first ≤ k < last, c := (k − first) mod 6, row := (k − first)
  div 6 → r+0x1c := Rect(377 + 27c, 377 + 26row, 404 + 27c, 403 + 26row); else (0, 0, 0,
  0). 0x4796f8: for k in first..last − 1, k ≠ carried inventory index: Draw(DXImageList7
  item 0, back, 378 + 27c, pattern r+8, 377 + 26row). Scrolling: Action 0x2c / 0x2d (E-0504).
  ResetState sets 0x47cedc := 0 (E-0309). `inventory-num.wxi` (128 items of 22×20 named
  `<obj>_<state>`, `DELPHIXPICTURECOLLECTION`) has no loader in Gilbert.exe (no string).
- **Method:** disassembly; `wxi.py`; `gamedat.py` statistics.
- **Confidence:** proven

### E-0508 — gecb::Dialog 0x47454c (callback 6) and the print message
- **Binary/file:** `GILBERT.EXE` 0x47454c, 0x4747e8, 0x4747f4, 0x474800, 0x470b56;
  `Data/misc/language.txt`
- **Evidence:** print flag 0x47cfb0 = 0: title 0x484d5c := GEDialogGetTitle, length < 3 →
  '  ' (two spaces, 0x4747e8); text 0x484d60 := GEDialogGetText, the same rule; n :=
  GEDialogGetNumChoices → 0x484bc4; choice i := GEDialogGetChoice(i) into 0x484bc8[i];
  dialogue open 0x47cf94 := 1. Flag set (book button 0x50, 0x470b56: PlayWave(1, 2); flag 1;
  0x47454c; flag 0; open; pressed := tab): title := '   ' (0x4747f4); text := line 20 + LF,
  then line + LF for each of lines 21..24 longer than 2 characters; one choice, line 25.
  Lines (Danish): 20 "Hvis du vil udskrive tekster fra Ordlisten, Eksperimenterne eller
  Gilberts venner:", 21 "1. Gem dit spil.", 22 "2. Luk Gilbert-spillet.", 23 "3. Klik på
  knappen Start og vælg Programmer. Der vil du finde Gilbert-mappen.", 24 "4. Klik på Bed om
  udskrift", 25 "Okay". ge.dll StartDialog 0x10009300 sets the current dialogue and calls
  callback 6. Corpus: 354 dialogues, choices per dialogue 1 (2), 2 (303), 3 (32), 4 (10), 5
  (5), 6 (1), 11 (1); texts with LF: 75, at most 7 LFs; 5 texts shorter than 3 characters;
  titles are internal Swedish names ("Badvakt 01").
- **Method:** disassembly; `language.txt` read; `gamedat.py`.
- **Confidence:** proven

### E-0509 — dialog::Layout 0x475fdc and dialog::Draw 0x479018
- **Binary/file:** `GILBERT.EXE` 0x475fdc, 0x479018, 0x463d3c, 0x476514, 0x476518, 0x4794bc
- **Evidence:** Layout, on the back buffer's canvas: Arial 8, style [] (0x476514 = 0); for
  each choice (cx, cy) := TextExtent → 0x484ef8[i]; W := the largest cx; H := 18·n. Style
  [fsBold] (0x476518 = 1), size 9: W := max(W, TextWidth(title)); 0x47cfa0 := that width;
  H += TextHeight(title). Lines: text split at each LF (char 10), each piece Trimmed, into
  0x484d64[0..L] (L = number of LFs, 0x47cf98). off 0x47cf9c := TextHeight(line 0) · L,
  still in bold 9. Arial 8 []: W := max(W, TextWidth(line)); H += TextHeight(line) for each
  line. Box 0x485870 := (310 − W div 2, 240 − H div 2, 330 + W div 2, 240 + H div 2).
  Choice k: 0x485220[k] := (left + 5, top + 25 + 18k + off, right − 5, top + 41 + 18k +
  off). Draw: Layout; FillRectAlpha((left, top − 16, right, bottom), 0, 0xb4); i2[0x9f] dh1
  at (left − 2, top − 17), i2[0xa0] dh2 at (right − 8, top − 17), i2[0xa1] dh3 at (left − 2,
  bottom − 8), i2[0xa2] dh4 at (right − 8, bottom − 8); StretchDraw (0x463d3c: item, dest,
  rect, pattern 0) i2[0xa3] dl1 (10×3) to (left + 2, top − 17, right − 2, top − 14) and
  (left + 2, bottom − 1, right − 2, bottom + 2), i2[0xa4] dl2 (3×10) to (left − 2, top − 14,
  left + 1, bottom − 8) and (right − 1, top − 14, right + 2, bottom − 8); line i: TextOut
  (left + 10, top − 6 + 12i, $008EBDDD, style 0, 8, Arial); choice k: TextOut(left + 10, top
  + 20 + 18k + off) in $008EBDDD when k is the hover 0x47cfa8 or the pressed 0x47cfac, else
  $007F7F7F. The title is never drawn: its only readers are 0x47454c (write) and Layout
  (0x476173..0x4761fc, measure); 0x47cfa0 is otherwise only written (Layout, ResetState).
- **Method:** disassembly; xref scan of the pointer slots.
- **Confidence:** proven

### E-0510 — dialog::HandleMouse 0x473f74, GEDialogEnd, voices
- **Binary/file:** `GILBERT.EXE` 0x473f74, 0x469fa0, 0x474804; `GE.DLL` DialogEnd
  0x10008f60; `default.dat`; `Data/Sounds/Dialog/`
- **Evidence:** Layout; 0x47cfac := −1, 0x47cfa8 := −1; hover := the last k whose Rect(left
  of choice k, its top, left + cx[k] + 10, its bottom) intersects the mouse rectangle. On a
  change of the button state: if the state is 1, pressed := the last such k; pressed ≠ −1 →
  dialogue open := 0, GEDialogEnd(pressed); last state := state. Main loop: modes 1, 2 and 4
  run 0x473f74 and 0x479018 while 0x47cf94 is set (mode 4 instead of its own mouse handler;
  mode 2 before cua::HandleMouse, which then sees no state change). ge.dll DialogEnd(i)
  clears the current dialogue and runs choice i's event; with none current it does nothing.
  Voices: callback 10 (E-0308) kind 1 plays `Sounds/Dialog/<name>.wav`. default.dat type-6
  records: 455 with a numeric name, +0x44 = 1, +0x48 = 0; 213 with a music name, +0x44 = 0,
  +0x48 = 1. The event that starts a dialogue holds the voice: e.g. event 9200000 = type 9
  (dialogue 20000) and type 6 ("2156", +0x44 1). 377 distinct voice names; 611 files; one
  name without a file ("8456"); 235 files never named.
- **Method:** disassembly; ge.dll decompile; `gamedat.py` statistics; directory listing.
- **Confidence:** proven

### E-0511 — book::Draw 0x46ec90 and the mode 4 tick
- **Binary/file:** `GILBERT.EXE` 0x469fa0 (case 4 at 0x46a2ae), 0x46ec90, 0x45bef8
- **Evidence:** tick: 0x46ec90; dialogue open → 0x4740fc, 0x473f74, 0x479018; else 0x474130
  (ret), book::HandleMouse 0x4734b8; ui::DrawCursor; Flip only when 0x47ce5c ≠ 0 (toggled at
  the end of every tick); stream updates. 0x46ec90: i2[0] at (64, 50), i2[0x6f] s03bkg at
  (64, 50); list ready 0x47cff8 and list view 0x47d008 → 0x45bef8(back, 135, 95, transparent,
  list surface 0x486b60, Rect(0, 0, 355, 320)); page ready 0x47cfc4 and not list view →
  0x45bef8(back, 135, 95, transparent, page surface 0x485884, Rect(0, t, 355, t + 320)), t =
  Trunc(scroll 0x47cfd4); interface1 at (64, 50); i2[0x41] ilbkg01 at (64, 337); buttons
  i2[0x4e] (88, 354), 0x4f (443, 387), 0x50 (325, 387), 0x51 (206, 387), 0x52 (206, 354),
  0x53 (88, 387); arrows i2[0x69] pil13 (115, 93), 0x7e pil15 (503, 93), 0x81 pil16 (503,
  343). Arrow hover 0x47cf44: 0x69 → 0x6a, 0x7e → 0x7f, 0x81 → 0x82; pressed 0x47cf48: 0x69
  → 0x6b + Action(0x69), 0x7e → 0x80 + Action(0x63), 0x81 → 0x83 + Action(0x66). Button
  hover 0x47cfc8: 0x4e..0x53 → 0x54..0x59; pressed 0x47cfd0: → 0x5a..0x5f, and for 0x4e,
  0x51, 0x52, 0x53 tab 0x47cfd8 := pressed; Action(pressed) when hover = pressed. Title at
  (192, 56) by tab: 0x4e → i2[0x7b] "Ordliste", 0x51 → 0x78 "Eksperimenter", 0x52 → 0x7a
  "Tips", 0x53 → 0x79 "Gilberts venner". Button labels seen: 0x4e Ordliste, 0x4f Tilbage, 0x50
  Udskriv, 0x51 Eksperimenter, 0x52 Tips, 0x53 Gilberts venner.
- **Method:** disassembly; pictures rendered and composed.
- **Confidence:** proven

### E-0512 — book::BuildList 0x46aa54, book::BuildPage 0x46ada0, book::SetFormat 0x46b2dc
- **Binary/file:** `GILBERT.EXE` 0x46aa54, 0x46ada0, 0x46b2dc, 0x46b2d8, 0x46b44c..0x46b454;
  `GE.DLL` 0x100078e0, 0x10007900, 0x10007a00, 0x10007a20, 0x100079c0, 0x10007840,
  0x10007ae0, BookParseNext 0x10007b00; `default.dat`
- **Evidence:** BuildList(book, first): list ready := 0; the 355×320 surface 0x486b60 is
  created once, colour key $FF00FF, filled with $FF00FF; canvas Brush clear, Arial 8 [],
  colour $0026C4; x := 10, y := 0, count := 0, book 0x47d004 := book; last := min(first +
  20, GEBookGetNumTopics(book)); for i = first..last − 1 (k = i − first): book[k] := book,
  topic[k] := GEBookGetTopicFromIndex(book, i); rect[k].left := x + 135, top := y + 95 + 8;
  parse GEBookGetTopicTitle(book, i): text → w := TextWidth, colour $192D80, TextOut(x, y),
  x += w; format → SetFormat; tab → x := (x div 20 + 1)·20; LF → y += 12, x := 10; links and
  pictures ignored; then rect[k].right := x + 135, bottom := y + 95 + 12 + 8; y += 12; x := 10.
  count 0x47d000 := last − first; list ready, list view := 1. BuildPage(book, topic): 0x47cff0
  := book, 0x47cff4 := topic; page ready 0x47cfc4 := 0; index := GEBookGetIndexFromTopic(book,
  topic); the 355×1000 surface 0x485884 created once, key and fill $FF00FF; Arial 8 []
  (0x46b2d0), colour $1A2E40; SetFormat(0); x := 10, y := 10, links 0x47cfec := 0, line
  height h := 12; parse GEBookGetTopic(book, index): text: w := TextWidth; x + w > 344 → y
  += h, x := 10, h := 12; a pending link → colour $192D80, style + fsUnderline (0x46b2d8 = 4),
  link rect left := x + 135, top := y + 103; TextOut(x, y); x += w. Format → SetFormat. Link
  (3) → linkBook 0x486518[n] := GEBookParseGetLinkBook, linkTopic 0x48683c[n] :=
  GetLinkTopic, pending. Link end (4) → right := x + 135, bottom := y + 115, colour $1A2E40,
  style − fsUnderline, n += 1, SetFormat(current 0x47cfe4). Picture (5) p: w := width of
  bookimages item p (0x463cc8); x + w > 354 → new line; Canvas.Draw(x, y, the item's
  graphic) (0x419d34); x += w; h := max(h, picture height). Tab → x := (x div 50 + 1)·50,
  then > 344 → new line. LF → y += h, x := 10, h := 12. End: page ready, list view := 0.
  SetFormat(f): 0 size 8 style []; 1 size 8, style + fsBold; 2 size 8, + fsUnderline; 3 size
  8, + both; 4 size 10, []; 5 size 10, [fsBold]; others: nothing; 0x47cfe4 := f. ge.dll:
  GetNumTopics(b) = the number of shown topics of book b; TopicFromIndex, GetTopicTitle,
  GetTopic look a topic up by its rank +0x14 among the shown ones (0x10007840: the first
  topic of the book whose +0x14 equals the argument); GetIndexFromTopic(b, id) = that topic's
  +0x14 (−1 when hidden, 0 when there is no such ID). Parse tokens: 1 text (a single space,
  or a run of characters up to a backslash or a character ≤ space), 2 `\f<n>`, 3 `\h<b>[:<t>]`,
  4 `\h` without a number, 5 `\g<n>`, 6 `\t`, 7 LF (E-0106). Book topics: book 0 227 (15
  shown at the start, titles `\f1Beduin`, …), 1 177 (all shown; `\f1 Advarselstekst`, …), 2
  17, 3 33.
- **Method:** disassembly; ge.dll decompiles; `gamedat.py`.
- **Confidence:** proven

### E-0513 — book::HandleMouse 0x4734b8 and gmenu::Action in mode 4
- **Binary/file:** `GILBERT.EXE` 0x4734b8, 0x46fa74 (mode 4 table 0x470a13/0x470a7d), 0x4710fc
- **Evidence:** 0x47cfc8 := −1, 0x47cf44 := −1, cursor 0x47ce8c := 0. List view: any list
  rect k intersecting the mouse rectangle while the state is not 1 → cursor 7. Page view:
  link rect n minus (0, t, 0, t) (t = Trunc(scroll)) the same. Mouse rectangle in (64, 360)–
  (576, 430) → hover button := first of 0x4e..0x53 whose BoundsRect it hits, else −1. In
  (500, 90)–(525, 360) or (114, 90)–(130, 125) → hover arrow := first of 0x7e, 0x81, 0x69,
  else −1. On a change of the button state: page view, state 1, link n hit → cursor 7; book
  0x47d004 := linkBook[n] and hover and pressed button := 0x52 / 0x4e / 0x53 / 0x51 for link
  book 0 / 1 / 2 / 3, scroll := 0 (other books: no change); BuildPage(linkBook[n],
  linkTopic[n]). List view, state 1, rect k hit → cursor 7, BuildPage(book[k], topic[k]).
  Then, unless the cursor is 7 and only with state 1: pressed button 0x47cfd0 := the button
  hit in the bar region (−1 if none), unchanged outside it; pressed arrow 0x47cf48 likewise.
  Last state := state. Action mode 4 (first = item ≠ last action item): 0x4e: first and book
  ≠ 1 → PlayWave(1, 2), BuildList(1, 0), scroll 0x47cfd4 := 0, first 0x47cffc := 0; 0x51: the
  same with book 3; 0x52: book 0; 0x53: book 2; each then hover := −1. 0x4f: first →
  PlayWave(1, 4), scroll := first := 0; pressed, hover, 0x47cf30, 0x47cf2c := −1; mode := 1.
  0x50: E-0508. 0x63 (up): PlayWave(1, 1); page view: scroll −= 24.0, below 0.0 → 0; list
  view: first −= 10, below 0 → 0, BuildList(book, first). 0x66 (down): PlayWave(1, 1); page
  view: scroll += 24.0, ≥ 1000.0 → 999.0; list view: first += 10, above NumTopics(book) − 20
  → that, below 0 → 0, BuildList. 0x69: PlayWave(1, 1), BuildList(book, 0), scroll := first
  := 0. 0x63, 0x66, 0x69 clear the arrow hover and press. Opening from the room (item 8,
  E-0306): LoadBookImages (`bookimages.wxi` into DXImageList12, E-0205), BuildList(1, 0),
  tab and pressed 0x4e, mode 4.
- **Method:** disassembly (floats 24.0, 0.0, 1000.0 at 0x4710fc..0x471104; 999.0 =
  0x4479c000).
- **Confidence:** proven

### E-0514 — The map is CUA 999; mode 5 is unreachable
- **Binary/file:** `GILBERT.EXE` 0x470570, 0x46f630, 0x472598, 0x46fa74; `default.dat`;
  `Data/maps/!global/kartmap.wxi`
- **Evidence:** room button "Kort" (0x27, E-0306) → GEWalkmapAreaHit(99999) (push 0x1869f):
  event walkmap·100 + 99. default.dat: each of the 38 room walkmaps has that event, one type-3
  record (walkmap = the room, CUA 999, comment "Till karta för snabb förflyttning");
  walkmaps 900 and 999 have none. Walkmap 999 holds CUA 999 (9 objects 99901..99909,
  visible, not pickable, texts "Til stranden", "Til ørkenen", "Til molen", "Til skoven" (2),
  "Til gletsjeren", "Til lysningen", "Til laboratoriet", "Til minen"; anims with duration 0,
  pictures 1, 3, 5, 7, 8, 11, 13, 15, 17 of kartmap.wxi (items bea1, des1, fis1, for1, for11,
  gla1, hou1, lab1, min1; the other ten are never named). Click events 9901..9909: type 4
  (walkmap 100, 352, 150, 552, 557, 600, 550, 254, 400 with a start point) and type 6.
  Mode 5 is set only by Action(0x27) in mode 2 (0x470848) and its own Action branch
  (0x470e43); Action(0x27) is called only from the room panel (mode 1) and from mode 5's
  frame. Mode 5's frame draws DXImageList11 item 0, but no code loads DXImageList11 (only
  0x46f654 reads TgMain+0x32c) and the form gives it no items.
- **Method:** disassembly; call-site and field-offset scans; `gamedat.py`.
- **Confidence:** proven

### E-0219 — Page presses dispatch on the page, not on which of 0x44/0x45 was hit; stale rectangles on Settings
- **Binary/file:** `GILBERT.EXE` 0x46d5c9 (tables 0x46d5e9/0x46d63c), 0x46d68c, 0x46d731,
  0x46d7c2, 0x471e24; `interface2.wxi` item sizes
- **Evidence:** the pressed-page-item switch sends both 0x44 and 0x45 to 0x46d68c, which
  tests the page (EDI): 3 → draw 0x4d, Action(0x45) (load); 4 → draw 0x4c, Action(0x44)
  (save); any other page → nothing. So a press on (258, 302) loads on page 3 and saves on
  page 4 whichever of the two the hit test found first (it tests 0x44 before 0x45,
  0x471e24). 0x63 (0x46d731) and 0x66 (0x46d7c2) draw their pressed picture only on pages
  3/4 but call Action(0x63/0x66) on every page; the action changes a scroll only on pages
  3/4 and always plays click 1. Each of 0x63, 0x66 is one item drawn every frame by the
  current page before HandleMouse runs, so on pages 3/4 its rectangle is the current one.
  Sizes: 0x44, 0x45 61×24; 0x63, 0x66 15×12; 0x96 and 0x90..0x95 29×29. On page 5 the stale
  rectangles of 0x44/0x45 (258, 302)–(319, 326) overlap the video button 0x96 (246, 294)–
  (275, 323), and the stale 0x66 ((301, 272)–(316, 284) after Load, (301, 241)–(316, 253)
  after Save) overlaps sound button 6 0x95 (279, 247)–(308, 276); these are tested first,
  so a press there does nothing (0x44/0x45) or only plays click 1 (0x66).
- **Method:** disassembly; item sizes from `wxi.py`.
- **Confidence:** proven
