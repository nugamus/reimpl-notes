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
