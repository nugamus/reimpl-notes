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
