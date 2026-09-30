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
