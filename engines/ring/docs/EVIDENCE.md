# Evidence log (Ring engine, Arxel Tribe)

Every factual claim in `engines/ring/docs/` and `games/{ring,prophet-and-assassin}/docs/`
must have an entry here that names the thing that proved it. Claims without evidence are
bugs, not shortcuts.

Append only. Do not rewrite history; if a claim turns out to be wrong, add a new entry
that supersedes it and mark the old one `SUPERSEDED by E-nnnn`.

## Entry format

```
### E-0001 — <one-line claim>
- **Binary/file:** games/ring/discs/dvd-edition/RING.EXE | .../DATA/AS.AT2 | traces/<run>.log
- **Evidence:** Ghidra address (`0x004ab120`), trace line number, or corpus statistic
  ("all 57 .CNM files start with `CNM UNR\0`").
- **Reference:** optional: the matching place in Templier's engine
  (`reference/templier-scummvm-ring/engines/ring/<file>:<line>`). A reference alone is
  never proof: confirm it in the original binary or the data.
- **Method:** how it was obtained (decompiled `FUN_004ab120`; ran
  `engines/ring/tools/parsers/cnm.py` over the corpus; trace of a scenario).
- **Confidence:** proven | strong | tentative
```

An entry at `tentative` confidence must also have a matching line in `OPEN-QUESTIONS.md`.

## Entries

### E-0001 — The corpus: 13 disc roots, 17,213 files, 11,800,243,161 bytes
- **Binary/file:** `games/ring/discs/{dvd-edition, cd-version/disc1..6, iso-version/disc1..4}`,
  `games/prophet-and-assassin/discs/cd1..2`
- **Evidence:** file and byte counts per root in `engines/ring/notes/corpus-inventory.md`
  (DVD 8,138 files / 4,565,370,040 B; CD version 3,488 files over six discs; ISO version
  3,519 over four; Prophet 2,068 over two). Every file's MD5 in
  `engines/ring/notes/corpus-md5.tsv`.
- **Method:** `python engines/ring/tools/survey.py` (read-only walk, MD5 of every file).
- **Confidence:** proven

### E-0002 — Ring's DVD and ISO RING.EXE are Visual C++ 6 programs, not Borland
- **Binary/file:** `games/ring/discs/dvd-edition/RING.EXE` (618,496 B, MD5
  `0622e19627b565b43895c0badda3fb8f`, PE timestamp 0x37de8931 = 1999-09-14 17:43:13 UTC);
  `games/ring/discs/iso-version/disc1/ring.exe` (663,552 B, `4a694e87e3f6a2680e89ea1fd6247708`,
  0x375e463b = 1999-06-09 10:47:23 UTC)
- **Evidence:** linker version 6.0; sections `.text .rdata .data .rsrc`; Rich header lists
  tool id 11 (C++ compiler) build 8168 x100 (ISO x110) and id 10 (C) build 8168; the only
  runtime banner is "Microsoft Visual C++ Runtime Library"; no "Borland" string; no MSVC
  RTTI (`.?AV`) and no source paths. Imports: KERNEL32, USER32, GDI32, DDRAW
  (`DirectDrawCreate` only), WINMM (`mmio*`, `timeGetTime`), SHELL32 (`SHFileOperationA`),
  DSOUND (by ordinal). No VCL/Borland DLL is imported: the Borland runtime on the discs
  (E-0006) belongs to setup, autorun and installer. Error strings name the methods they
  come from (`aApplication::AddRot -> Node File does not exist -> `), the naming anchor
  for the Ghidra phase.
- **Method:** `pefile` (sections, imports, `parse_rich_header`), string scan; table in
  `engines/ring/notes/binaries.md`.
- **Confidence:** proven

### E-0003 — The CD version's ring.exe is a Borland C++ build
- **Binary/file:** `games/ring/discs/cd-version/disc6/ring.exe` (712,192 B, MD5
  `3e34b057d4001a4ad923d8f7d60d2d99`)
- **Evidence:** string "Borland C++ - Copyright 1996 Borland Intl."; TLINK layout (linker
  2.25, sections `.text .data .tls .rdata .idata .edata .rsrc .reloc`); entry point at the
  first byte of `.text` (0x401000). The PE timestamp field 0x79552541 does not decode to a
  plausible date (2034-07-04). Same Win32 imports as E-0002 plus threading and
  `AddFontResourceA`. `Trailer.exe` beside it (712,192 B, `2be441c6…`) is the same build family.
- **Method:** `pefile`, string scan.
- **Confidence:** proven

### E-0004 — Prophet's Legend.ex_ is Visual C++ 6 with a copy-protection layer that redirects imports
- **Binary/file:** `games/prophet-and-assassin/discs/cd1/Legend.ex_` (1,112,195 B, MD5
  `f9e2258edf62584ce0539e5274b275ec`, PE 0x39d9f6ac = 2000-10-03 15:09:32 UTC);
  `Legend16.ex_` (same size, `4e4f44e476d5b47d8a4a57a70883bb09`, 98 s later)
- **Evidence:** linker 6.0; Rich header id 11 build 8447 x116; extra sections `.cms_t`
  (entropy 7.24) and `.cms_d`; entry point 0x4dfd12 lies in `.cms_t`; 51,331-byte overlay.
  `.text` is plain code: against `crack/LEGEND.EXE` it differs in 20,910 bytes in 323 short
  runs, and the runs are import calls, e.g. at 0x40171d the original has
  `call [0x4e82f0]` (a slot in `.cms_d`) where the crack has `call [0x4ab250]` (the IAT in
  `.rdata`). `.data` and `.rsrc` are identical. Imports besides E-0002's set: `mmximage.dll`
  (`mmxImage32PreAlpha`, `mmxImage32Copy`, `mmxImage32CopyAlpha`).
- **Method:** `pefile` section diff of the original against `crack/LEGEND.EXE` (the crack is
  used only as a diff oracle, never as an RE target), capstone at the differing offsets.
- **Confidence:** proven (the redirection); the protection's identity is Q-0001.

### E-0005 — The DVD's TRAILER.EXE is RING.EXE with one immediate changed (999 → 998)
- **Binary/file:** `games/ring/discs/dvd-edition/{RING,TRAILER}.EXE` (both 618,496 B)
- **Evidence:** 237 differing bytes: the PE timestamp, the icon resource (file 0x96108..
  0x96307), and one code byte at 0x431172: RING.EXE `push 0x3e7; push 7; mov ecx, esi;
  call 0x402280`, TRAILER.EXE `push 0x3e6` in the same place.
- **Method:** byte diff, capstone at 0x431160.
- **Confidence:** proven (what the call does is for the Ghidra phase)

### E-0006 — Launcher, setup and installer programs are Borland C++ Builder
- **Binary/file:** every edition's `AUTORUN.EXE`, `SETUP.EXE`, `INSTALL/*.EXE`, cleanup and
  uninstall programs; runtime `VCL35.BPL`, `VCLX35.BPL`, `BCBSMP35.BPL`, `CP3240MT.DLL`,
  `BORLNDMM.DLL` (Ring; identical MD5s in DVD, CD disc 6 and ISO disc 1) and `vcl40.bpl`,
  `vclx40.bpl`, `bcbsmp40.bpl`, `cp3245mt.dll`, `borlndmm.dll` (Prophet).
- **Evidence:** `engines/ring/notes/binaries.md` (TLINK 2.25 layout, VCL runtime).
  Exception: Prophet's `Setup.exe` is linker 6.0 (Microsoft).
- **Method:** `survey.py`.
- **Confidence:** proven

### E-0007 — ScummVM-style detection MD5s (first 5,000 bytes) of our files
- **Binary/file:** DVD `RING.EXE` `10e21ce9cf937c56c5891113ac1cfcc2`; DVD `DATA/AS.AT2`
  `5f65ee721fdf50bc074dd25bb28592fb` (1,533,273 B); ISO `ring.exe`
  `88a6962191f6c5aa35c93d49115a59ce`; CD `ring.exe` `daa9454d0a6383d8c69172a3873713a5`;
  Prophet `Legend.ex_` `169ea41f544cfecc37b1549ecd7a706b`, `Legend16.ex_`
  `e3d5126309af08534c00e3a1f5fa2d81`, `data/eng/sy.at3` `1b7bd7cd45930beb894e6f9a29b90cc4`
  (8,506,050 B).
- **Evidence:** `hashlib.md5(data[:5000])`.
- **Reference:** `reference/templier-scummvm-ring/engines/ring/detection.cpp`: his "ring"
  entry (`RING.EXE` 618,496 / `AS.AT2` 1,533,273) and "pilgrim2" entry (`Legend.exe`
  1,112,195 / `sy.at3` 8,506,050) carry exactly these DVD and Prophet MD5s, so his Ring is
  our DVD edition and his Pilgrim 2 is our Prophet CD. He has no entry for the CD or ISO
  version.
- **Method:** script over the files named.
- **Confidence:** proven

### E-0008 — Data layout: one directory and one archive per zone, a disc number in CD.INI
- **Binary/file:** `DATA/` of every edition.
- **Evidence:** Ring zones `AS FO N2 NI RH RO WA` each have `DATA/<zone>/` and
  `DATA/<zone>.AT2`; the system zone is `DATA/SY/` (subfolders `DIA IMAGE PLA SOUND VISUAL`)
  with `SY.AT2` per language: DVD `DATA/{ENG,FRA,GER,HOL,ITA,SPA,SWE}/SY.AT2`, CD and ISO
  `data/{eng,fra,ger}/sy.at2` (ISO also has `data/sy.at2`). Saves: `DATA/SAVE/{SAVE,ZERO}.ABA`
  (4 bytes of zeros each) and `DUMMYLS.BMP`. `DATA/CD.INI` holds the disc number: "1" on the
  DVD, "1".."6" on the CD discs, "1".."4" on the ISO discs. Zone archives by disc: CD
  as→1, ni→2, rh→3, n2+ro→4, fo→5, wa→6; ISO ro→1, as+ni→2, rh+wa→3, fo+n2→4.
  Prophet: zones `a01..a05` with `data/a0N/` and `data/a0N.at3` (a01, a05 on cd1; a02..a04 on
  cd2), `data/eng/sy.at3`, `data/SAVE/{USER,ZERO}.ABA`. DVD `INSTALL/` has `.LAN .LIS .UNI` for
  ENG FRA GER GRE HEB HOL ITA SLO SPA SWE and root fonts `ARXRIN.{FON,GRE,HEB,SLO}`.
- **Method:** `survey.py` layout listing, `cat` of every `CD.INI`.
- **Confidence:** proven

### E-0009 — Most Ring data is byte-identical across the three editions
- **Binary/file:** `engines/ring/notes/identical-files.md`
- **Evidence:** 2,461 distinct contents are in all three Ring editions; the DVD has 3,807 of
  its own (mostly `.dia`, `.wac`, `.dan`: the extra languages). `AS.AT2`, `FO.AT2`,
  `N2.AT2`, `NI.AT2`, `RH.AT2`, `RO.AT2`, `WA.AT2` are identical in all three editions.
  English `SY.AT2` (12,211,188 B, `9aaa7190…`) is identical in DVD `ENG/`, CD `eng/` and ISO
  `data/sy.at2`; the ISO's `eng/fra/ger/sy.at2` (13.1 MB) differ from the others. Six
  contents are shared by Ring and Prophet: `aPre.ini`, `data/cd.ini` ("1", "2"), the empty
  `.aba` saves, `dsetup*.dll`.
- **Method:** `survey.py` (MD5 sets per edition group, DirectX folders excluded).
- **Confidence:** proven

### E-0010 — Videos: the DVD holds the CD version's videos under numbered names; the ISO re-encoded them
- **Binary/file:** every `.cnm` in the Ring corpus
- **Evidence:** CD and ISO both have the same 443 `.cnm` names (e.g.
  `ass00n01_s00n02.cnm`, `tr_as_fo_a.cnm`) and no name has the same content in both. The DVD
  has 452 `.cnm`, 426 with numeric names (`1001.cnm`…); 442 of the CD's 443 contents are
  among them under other names (the 443rd, `logo.cnm`, differs); 10 DVD videos
  (`1160 1161 1163 1863 1864 1873 1874 1876 1877 1911`) are not in the CD version.
  All 1,351 Ring `.cnm` and all 67 Prophet `.ci2` start with `CNM `.
- **Method:** MD5 and name comparison over `corpus-md5.tsv`.
- **Confidence:** proven

### E-0011 — Extension × magic census (Ring and Prophet)
- **Binary/file:** `engines/ring/notes/corpus-inventory.md`
- **Evidence:** all 35 `.at2` start `AT_I`, all 6 `.at3` `ATII`; `.cnm`/`.ci2` `CNM `;
  `.dan` start `1\r\n1` (text) but for two Prophet files (`1\r\n0`); `.dia`, `.lan`, `.lis`,
  `.uni`, `.ini` are text; `.wav` RIFF; `.tga` `00 00 02 00`; `.wac`, `.was`, `.aqc`, `.bma`
  have no constant magic (the first dword varies per file). Counts per edition in the
  inventory.
- **Method:** `survey.py`.
- **Confidence:** proven

### E-0012 — Ghidra project Ring.gpr holds the four game EXEs, analysed
- **Binary/file:** `ghidra_projects/Ring.gpr`: `/RING_DVD.EXE`, `/RING_ISO.EXE`, `/RING_CD.EXE`,
  `/LEGEND.EXE` (renamed copies in `build/ring-import/` of DVD `RING.EXE`, ISO disc 1
  `ring.exe`, CD disc 6 `ring.exe`, Prophet cd1 `Legend.ex_`; MD5s as E-0002..E-0004)
- **Evidence:** auto-analysis succeeded for all four (`logs/ring-import.log`); function
  counts 1,940 / 1,954 / 3,111 / 2,079.
- **Method:** PyGhidra headless `-import … -overwrite` (the command is in CLAUDE.md, Ring).
- **Confidence:** proven

### E-0013 — ~370 functions per EXE are named from the method names in their error strings
- **Binary/file:** the four programs of E-0012; results in `engines/ring/notes/names/*.csv`
- **Evidence:** functions referencing strings that name exactly one method
  (`aClass::Method -> …`, `Method(args) -> …`, `Method -> …`): DVD 367 named of 377,
  ISO 368/379, CD 499/512, Prophet 367/379; the rest reference two methods and are only
  commented (`RING-STR:`). 60 class names occur (`aApplication`, `aPuzzle`, `aRotation`,
  `aObject`, `aObjectPresentation`, `aSecComAqi`, `aCin`, `aImageFileBMP`…); Prophet adds
  `aZone`, `aEpizode`, `aFileIoArt`, `aCinemaCompression`, `aImageFileCinema`. A name means
  the function raises that method's messages; where the compiler inlined a callee, the
  name is its caller's messages' owner. Confidence strong, not proven, for that reason.
- **Method:** `tools/ghidra/scripts/ring_string_namer.py` (PyGhidra postScript, raw scan of
  the data blocks for NUL-terminated strings, xrefs to functions).
- **Confidence:** strong

### E-0014 — Few virtual methods: 34 vtables in the DVD EXE, most with one entry (entry counts SUPERSEDED by E-0023)
- **Binary/file:** the four programs; `engines/ring/notes/vtables/*.md`
- **Evidence:** tables installed by `MOV dword ptr [reg], imm32` whose target is a run of
  function entries: DVD 34 (0x47e380..0x47f100), ISO 35, CD 39, Prophet 34; 28 of the DVD's
  34 have a single entry, most written by exactly two functions (constructor and destructor shape). Only
  `aSecComSou` (0x47f0a8) and `aSecComSouMono` (0x47f0d4) get a class name from their
  entries in the MSVC builds; the CD build names 10. Class names therefore come from the
  error strings (E-0013), not from vtables.
- **Method:** `tools/ghidra/scripts/ring_vtables.py`.
- **Confidence:** proven (the table census); a table's class is only as strong as E-0013.

### E-0015 — DVD Init ends with 0x402280(this, 7, 999); TRAILER.EXE passes 998
- **Binary/file:** `RING_DVD.EXE` 0x431140 (named `Init` by its strings; the call at
  0x431171 is the E-0005 difference); 0x402280
- **Evidence:** 0x402280 takes (zone byte, int): with the int 1000 it tests globals
  0x49534d (== 7) and 0x49534f/0x495354 against 0x13882..0x1388a/0x138e5; otherwise it reads
  a file through `GameZoneOnCD` (0x4312c0) and, when the zone is available, calls 0x402210
  and 0x40d220 (the function carrying `aApplication::GameSetZone` and
  `aApplication::LoadSave` strings); if not, it stores the int in 0x495238 and shows the
  `InsertCD` message (0x40e5b0, 0x40df20).
- **Reference:** `reference/templier-scummvm-ring/engines/ring/shared.h:238` names
  998 `kSetupType998`, 999 `kSetupTypeStartZone`, 1000 `kSetupTypeLoading`, and
  `Application::setZone(ZoneId, SetupType)` in `base/application.h:74`.
- **Method:** decompiled with `tools/ghidra/scripts/decompile_one.py` (output in
  `engines/ring/notes/decomp/`).
- **Confidence:** strong (the control flow is proven; the parameter meanings are the
  reference's until the zone setup functions are read)

### E-0016 — .at2/.at3 archive layout; 41 archives parse completely
- **Binary/file:** every `.at2` (35) and `.at3` (6) in the corpus (23 distinct contents);
  `RING_DVD.EXE` `aArt::Init` 0x4194d0, `aArt::GetRec` 0x4198e0; `LEGEND.EXE` 0x41e470,
  0x41e880
- **Evidence:** `aArt::Init` reads 0x20 header bytes into the object at +4 and loops
  `*(this+0x10)` (header +0xc) times reading 0xff-byte records whose dwords at +0xf3,
  +0xf7, +0xfb it keeps; `GetRec` seeks to the record's +0xf3 and reads +0xf7 bytes (and
  rejects more than 10,000,000). Prophet's pair is the same. In the data: magic
  `AT_II\0\0\0` (.at2) / `ATIII\0\0\0` (.at3), u32 dir size = count × 255, u32 count, u32 255,
  three u32 zeros; members follow the directory contiguously in directory order to EOF;
  names are unique. 37,183 Ring members (14,315 `.bmp`, 22,868 `.tga`) and 2,045 Prophet
  members (1,214 `.bmp`, 831 `.tga`); in every one the third dword differs from the size, and
  it is the unpacked size (921,654 for `\image\end.bmp` = a 640×480×24 BMP). Ring members
  begin with a 16-byte header then `BM`; Prophet members begin with `CNM UNR\0`.
- **Reference:** `reference/templier-scummvm-ring/engines/ring/base/art.cpp` `Art::init`
  (same layout; he names the third dword `field_FB`).
- **Method:** decompiled the four functions (`engines/ring/notes/decomp/`);
  `python engines/ring/tools/parsers/at2.py`: files 41, distinct 23, passed 23, 100%.
- **Confidence:** proven

### E-0017 — Packed images (BMA) and the engine's packed bit stream
- **Binary/file:** `RING_DVD.EXE` `aImage::Load` 0x413150, `aImageFileBma::Init` 0x42ba40,
  header copy 0x42bb90, `aImageFileBma::ReadImage` 0x42bbf0, bit decoder 0x4308e0; every
  loose `.bma` and every `.bmp` member of every `.at2`
- **Evidence:** `aImage::Load` picks the loader by the last three letters of the name
  (strings 0x485b00 `bmp`, 0x485afc `tga`, 0x485af0 `bma`, 0x485aec `tgc`, 0x485af4 `cnm`):
  from an archive ('f') `bmp`/`bma` go to the Bma loader (ctor 0x42b980) and `tga`/`tgc` to
  the Tgc loader (ctor 0x42b120); from disk ('e') `bmp` goes to the plain BMP loader
  (0x42a860). The header copy reads dwords at +4, +8, +0xc, +0x10 and a word at +0x14 of the
  member; ReadImage decodes bits 0x260 .. 0x260 + 8·seq_size with literal width = bit length
  of the word at +4 and index width 6, then from byte 0x50 + seq_size a 16-bit stream of
  (dword at 0x4c + seq_size) bytes; it expands each index to 3 pixels of a 16-bit image
  created with `aImage::Create(16, …)`, and copies the 6 header bytes at +0x10 over the last
  3 pixels. Decoder 0x4308e0: MSB-first bits, 64-slot cache with bit-position stamps, codes
  `0`+literal, `10`+index, `11` repeat (README "Packed bit stream"). Corpus: 14,414 files,
  6 of them `BOGUS*.BMA`, which hold `.dia` text (MD5 `00a84375…`, the string "bogus" is in
  no EXE except as Borland RTL text in the CD one); the other 14,408 (4,895 distinct) end
  exactly after the core stream, have 3 pixels per entry, indices below core_count, and
  each stream yields its expected code count or one more. Decoded pixels shown as RGB555,
  rows bottom-up, give a coherent picture (`DATA/AS/IMAGE/ASV01.BMA`); as RGB565 they do
  not.
- **Reference:** `reference/templier-scummvm-ring/engines/ring/base/stream.cpp`
  `CompressedStream::decode` / `decompressIndexed` (same algorithm and offsets 608/640).
- **Method:** decompiles in `engines/ring/notes/decomp/`; `python
  engines/ring/tools/parsers/bma.py` (C decoder `ringdec.c` checked against the Python one
  by `bitstream.py --selftest`): 100%.
- **Confidence:** proven (layout, decoder); strong (RGB555, from the picture, see Q-0002)

### E-0018 — Packed TGA (TGC): chunks of bit stream that unpack to a 32-bit TGA
- **Binary/file:** `RING_DVD.EXE` 0x42b230 (strings `aImageFileTgc::Init`), `ReadInfo`
  0x42b540, `ReadImage` 0x42b600; every `.tga` member of every `.at2`
- **Evidence:** Init reads u32 chunk count, u32 output size, then per chunk u32 packed
  size, u32 unpacked size and decodes the packed bytes (16-bit literals, 6-bit indices)
  to the output, advancing by the unpacked size. ReadInfo takes the TGA header from the
  output and rejects type ≠ 2 and fewer than 32 bits; ReadImage copies rows from the last
  one up (8, 24, 32 bpp cases). Corpus: 22,868 members (1,501 distinct), chunk counts 1..18;
  every chunk yields its size or one extra code; the unpacked sizes sum to the header
  size, which is the archive's unpacked size; each result is an 18-byte header, type 2,
  32 bpp, w·h·4 pixel bytes and, in 24 distinct files, the 26-byte TGA 2.0 footer.
- **Method:** decompiles; `python engines/ring/tools/parsers/tgc.py`: 100%.
- **Confidence:** proven

### E-0019 — Plain BMP and TGA files on disk
- **Binary/file:** loose `.bmp`/`.tga` (DVD `DATA/SY/IMAGE/BEG0..6.BMP`,
  `DATA/SAVE/DUMMYLS.BMP`, `DATA/SY/VISUAL/*.TGA`, Prophet `data/sy/image/osc.bmp`,
  `data/sy/visual/*.bmp`, and the CD/ISO copies)
- **Evidence:** 56 files: 3 are `BOGUS2.BMP` (E-0017); the other 53 (21 distinct) are 24-bit
  BI_RGB BMPs with a 40-byte header (6 distinct end with two zero bytes counted by the size
  field) or type-2 TGAs; all consumed to the last byte. Loader choice as E-0017.
- **Method:** `python engines/ring/tools/parsers/bmp.py`: 100%.
- **Confidence:** proven

### E-0020 — .aqc panorama nodes: index stream, colour table, layer sections
- **Binary/file:** `RING_DVD.EXE` `aApplication::AddRot` 0x404dc0, `CAquatorStream::InitFull`
  0x4111d0 (its error strings name it), `aSecComAqi::DecompressNode` 0x429be0,
  `DecompressChannel` 0x429dc0, decoders 0x430600 (13-bit literals) and 0x430770 (16-bit),
  table conversion 0x410ff0; all 587 `.aqc` (351 distinct)
- **Evidence:** AddRot builds `%s%s\%s\%s\%s.aqc` when the global at app+0x54 is set,
  `.aqi` otherwise (and `_%03d.aqc` channel files only on the `.aqi` path; the corpus has
  no `.aqi` and no `_nnn.aqc`). InitFull opens the `.aqc`, calls DecompressNode once and
  DecompressChannel once per layer (count at `this+0x48`). DecompressNode: u32 size A,
  13 dwords of header, A bytes decoded with 13-bit literals to buffer+0x34, u32 B, B bytes
  decoded with 16-bit literals after the index area. DecompressChannel continues at the
  cursor: u32 count, two u32, then per entry u32 size, 13-dword header, bits. 0x410ff0
  rewrites 0xfd20 table words from 565 layout (`v & 0x1f` blue, `v & 0x7e0` green,
  `v >> 8 & 0xf8` red) into the display's masks. Corpus: headers are 2048×688 (113 files,
  floats 360/−60/60) or 2048×856 (238, 360/−75/75); data_size = (x1−x0)(y1−y0)·2,
  stride = (x1−x0)·2; node index count = data_size/8 (+1 padding code at most); the table
  is 32,400 values (8,100 entries of 4) in every file; every index < 8,100. Sections:
  784 static (count 1, 0, 0), the rest animations with unk_a = 0x41400000 (12.0) and
  unk_b = count − 1 (up to 403 frames). One file (Prophet `A03S02N05R01.aqc`, MD5
  `9a1d45d0…`) has 18,289 bytes after its tenth section that do not form a section (Q-0003).
- **Reference:** `reference/templier-scummvm-ring/engines/ring/base/stream.cpp`
  (`decompressNode`, `decompressChannel`, `decodeChannel` 13 bits, `decodeNode` 16 bits).
- **Method:** decompiles in `engines/ring/notes/decomp/`; `tools/ghidra/scripts/callers.py`;
  `python engines/ring/tools/parsers/aqc.py`: 587 files, 351 distinct, 100%.
- **Confidence:** proven (layout, counts); what the 4 pixels per index are is the
  rotation renderer's spec.

### E-0021 — .wac is mono DPCM in 256-sample chunks, .was stereo packed bit stream; 53 DVD files are damaged
- **Binary/file:** `RING_DVD.EXE` vtables 0x47f0a8 (`aSecComSou`: 0x47a900, Init 0x47a970,
  0x47aa90, DecompressHeader 0x47aaf0, Decompress 0x47ac90, …) and 0x47f0d4
  (`aSecComSouMono`: …, Init 0x47b0d0, DecompressHeader 0x47b250, Decompress 0x47b3b0);
  decoders 0x430a80 and 0x47bc20; every `.wac` and `.was`
- **Evidence:** Init calls the vtable slot +0xc (DecompressHeader). Stereo header: 0x3c
  bytes = chunk count, WAV size, 11 dwords (44-byte WAV header), first packed and unpacked
  size; each chunk read is packed+8 bytes (the next sizes ride along) and decoded by
  0x430a80, the packed bit stream with literals `<< 4` (called with 12, 6). Mono header:
  0x36 bytes = count, size, 44 bytes, u16 first chunk size; each chunk is decoded by
  0x47bc20 (called with 10 from 0x47bbf0) which starts 3 bits in and emits 0x100 samples:
  `0`+10 bits d (d > 0x1ff → 0x200 − d), delta = d·0x40; `1` = previous delta; sample +=
  delta, both carried over. Split functions: 0x47ac90 and 0x47b3b0 were inside 0x47aaf0 /
  0x47b250 after auto-analysis (`tools/ghidra/scripts/split_function.py`). Corpus: 4,690
  files; 4,637 (2,638 distinct) parse to the last byte: mono wav_size = 44 + 512·count,
  every chunk's 256 samples end fewer than 8 bits before its end, the 3 leading bits are 0
  in every chunk; stereo wav_size = 44 + Σ unpacked, codes = unpacked/2 (+1). Rates 22,050
  (all but two), 16,000 (one .was), 44,100 (one .wac); 6 headers have `fact` after `fmt `.
  53 files (53 distinct), all DVD `SOUND/{SPA,ITA,HOL,SWE}/*.WAC`, are damaged: in 52 the
  chunk chain breaks at a chunk that crosses a 64 KiB file offset (the size field there
  is wrong and about 4 KB of bytes after it decode as nothing; a valid chain resumes
  later, e.g. `AS/SOUND/ITA/1106.WAC` breaks at 0xff93 and resumes at 0x11144); in
  `N2/SOUND/ITA/1437.WAC` the 44 header bytes are not a WAV header.
- **Reference:** `reference/templier-scummvm-ring/engines/ring/sound/sound_loader.cpp`
  (same split into mono and stereo loaders).
- **Method:** decompiles; `python engines/ring/tools/parsers/wac.py` (C `ring_dpcm` and
  Python `py_dpcm` agree, `bitstream.py --selftest`): 100% of the undamaged files; the
  damaged list `parsers/wac_damaged.txt`.
- **Confidence:** proven

### E-0022 — Plain .wav files are standard RIFF WAVE
- **Binary/file:** 744 `.wav` (210 distinct), e.g. DVD `DATA/SY/SOUND`, CD disc 6 `data/WA`
- **Evidence:** RIFF size + 8 = file size; chunks even-padded to the end; PCM `fmt ` and
  `data` in every file. The EXEs import WINMM `mmioOpenA`/`mmioDescend`/`mmioRead`
  (E-0002).
- **Method:** `python engines/ring/tools/parsers/wav.py`: 100%.
- **Confidence:** proven

### E-0023 — E-0014's vtable entry counts are lower bounds
- **Binary/file:** `RING_DVD.EXE` vtable 0x47f0a8
- **Evidence:** the table continues past the 3 entries `ring_vtables.py` reported
  (0x47aaf0, 0x47ac90, 0x47afe0, … are slots +0xc, +0x10, …, used through `call [eax+0xc]`
  in `aSecComSou::Init`): the script stops at the first slot that Ghidra has not made a
  function, and vtable-only methods often are not. The table census stands; entry counts
  and "single entry" do not.
- **Method:** raw dwords at 0x47f0a0, decompile of `aSecComSou::Init`.
- **Confidence:** proven

### E-0024 — Video containers: "CNM HBR" (Ring DVD/CD) and "CNM UNR" (Ring ISO, Prophet)
- **Binary/file:** `RING_DVD.EXE` `aCinMov::Init` 0x415340, `aCinMov::Play` 0x415990,
  `aCinMov::SkipSound` 0x4158c0, header read 0x42a6b0 (0x40 bytes), `aCin::SControl`
  0x42ccf0, TControl 0x42cbf0, `aCin::Decompress` 0x42cb90; `LEGEND.EXE`
  `aImageFileCinema::ReadHeader` 0x421c30, SControl 0x422fc0, TControl 0x423170,
  `aCinemaCompression::SkipFrame` 0x422f20, `aCinMov::Play` 0x4a51c0; every `.cnm`, `.ci2`
  and every `.at3` member
- **Evidence:** HBR: Play reads one type byte per chunk: 0x41/0x42/0x5a sound (SkipSound:
  u32 size, skip), 0x53 image (Decompress/SControl read a 0x14-byte header whose first
  dword is the payload size), 0x54 tiles (TControl reads 0xd bytes, then size + 2·b + 2
  with b the header's last byte); it stops when the image count reaches the header
  dword at +0xe; width/height at +0x17/+0x1b (0x42a6b0). UNR: ReadHeader reads 0xc0
  bytes (width +0x11, height +0x15, tracks byte +0x1b ≤ 3, table count +0x1c), tracks ×
  16 bytes, table count × 8 bytes; Play's chunk types are 'A' 'B' 'S' 'U' 'T' 'Z'; S/U
  read a 0x2f-byte header, T an 8-byte header, each followed by its first dword's size.
  Corpus: Ring DVD 452 and CD 443 `.cnm` are HBR; Ring ISO 456 `.cnm`, Prophet 67 `.ci2`
  and 2,045 `.at3` members are UNR. 3,462 files (2,780 distinct) walk to the last byte with
  image chunks = frame count; HBR headers: 1 channel, 16 bits, 22,050 Hz, 640×448, +0x12 =
  1250; UNR: Ring ISO tables point at the chunk chain; Prophet `.ci2` and members have
  +0x28 = 1 and an all-zero table. One HBR content (`DVD RH/PLA/1672.CNM` = CD
  `RHS05N01_S05N02.cnm`) has a 300th image chunk cut off by the end of the file after its
  299 frames (never read: Play stops at 299). ISO disc 4 `fo/Pla/fos03n02_s05n01.cnm`
  (MD5 `c1827c4f…`) has no valid chunk at the table's frame-132 video offset 0x6d4d29.
- **Reference:** `reference/multimedia_cx/Game_Formats/CNM.md` (container, chunk types,
  codec description); Templier's `graphics/movies/cinematic*.cpp`.
- **Method:** decompiles in `engines/ring/notes/decomp/`; `python
  engines/ring/tools/parsers/cnm.py`: 100% at container level.
- **Confidence:** proven (container); the frame codec is not yet specified.

### E-0025 — .dia subtitle and .dan timing files (count of unterminated files SUPERSEDED by E-0027)
- **Binary/file:** `RING_DVD.EXE` `aDialog::Init` 0x426ef0 (paths `%s%s\%s\%s\%s\%sdia`,
  `…dan`), `ReadLyrics` 0x427090, `ParseLyricLine` 0x427550, `ReadDialogAnimation`
  0x4271b0; all `.dia` and `.dan`
- **Evidence:** ReadLyrics `_lread`s at most 0x1000 bytes, zeroes each `\n` and the byte
  before it, and parses each line ending in `\n`; ParseLyricLine skips `isspace`, reads
  `isdigit` digits, optionally `,` digits `:` digits `.` digits, skips spaces, splits the
  rest at `#` (and for language 9 turns 0xa0 into spaces). ReadDialogAnimation needs
  `fscanf("%d") == 1` then loops `fscanf("%d %d %d") == 3`. Corpus: 7,755 files (4,498
  distinct), all under 0x1000 bytes (largest 1,613); every `.dan` is 1 + 3n integers; in 5
  DVD `.dia` (HOL/ITA/SWE 1160/1161/1163) lines end in bare `\n`, so the engine drops their
  last character (a `#`); 20 `.dia` end without `\n`, so their last line (`… END`) is never
  parsed.
- **Method:** `python engines/ring/tools/parsers/dia.py`: 100%.
- **Confidence:** proven

### E-0026 — Configuration files and save lists
- **Binary/file:** `RING_DVD.EXE` `aApplication::Init` 0x407b80 (`fl.ini`), `aPreFer::Load`
  0x428870, 0x402280 (`data\cd.ini`), 0x4213d0 (`aObj.ini`), `GetMultiLanMes` 0x40e150
  (`%sames.ini`), `aFileList::Load` 0x47a1d0; every `.ini` and `.aba`
- **Evidence:** fl.ini: `fscanf("%d")` then that many `fscanf("%s %s")`, keys compared
  with `CDPATH:` … `CHECKLOADSAVE:` (24 strings at 0x4858b0..0x4859f8); aPre.ini:
  `"%d %d %d %d"` must give 4; aObj.ini: `"%d\n"` then 10 lines (loop to 0xb) per object,
  the line whose first 3 characters equal the language name split at its last two `#`;
  aMes.ini: `"%s\n"` tokens until the key, then lines matched on 3 characters.
  aFileList::Load reads a u32 record count. Corpus: 38 files (19 distinct) parse; DVD
  `aObj.ini` has 96 objects × 10 languages (ENG GER FRA ITA SPA HOL SWE HEB GRE SLO), CD/ISO
  5, Prophet 7; `fl.ini` has 24 pairs (Prophet 17); every `.aba` is a zero count.
- **Method:** `python engines/ring/tools/parsers/ini.py`: 100%.
- **Confidence:** proven

### E-0027 — 22 .dia files end without a final newline (corrects E-0025's 20)
- **Binary/file:** all `.dia`
- **Evidence:** 22 files (22 distinct) end in an unterminated `… END` line and 3 in
  unterminated spaces; the engine parses neither (E-0025).
- **Method:** census over `dia.py`'s `ignored_tail`.
- **Confidence:** proven

### E-0028 — The HBR video codec (Ring DVD and CD version), all 453 distinct files decoded
- **Binary/file:** `RING_DVD.EXE` `aImageFileCin::ReadImage` 0x42a6f0 (`aImage::Create`
  once, then `aCin::SControl` into the same image every frame), `aCin::SControl` 0x42ccf0,
  TControl 0x42cbf0, stream decoder 0x42ce30; `aCinMov::Play` 0x415990 allocates the image
  once before its loop; every HBR `.cnm`
- **Evidence:** 0x42ce30 reads bytes and nibbles as in README "HBR video codec": ring of
  128 dwords at `this+0x32` (write pointer reset to its start per call), memo table of
  0x800 × {pointer, bytes} at `this+0x2a` (zeroed by SControl/TControl), codes `> ntiles`
  and `< 0x780` walk the run list from `this+0x42` (`p += *p + 1`), codes `>= 0x780` use memo
  entries SControl fills from the back buffer (`this+0x15`) with the u16 lengths `<< 3`
  stored before the tile table. TControl decodes into the back buffer (limit 1,200,000
  bytes), SControl into the picture (limit 0x8cfff bytes); nothing else checks the size.
  S header: u32 size, u32 runs size, u16 tile count, u16 tile words (4), u32 width, u32
  height. Corpus (453 distinct HBR files, 895 in all): every chunk decodes without an
  out-of-range tile, run or segment; 'S' frames: 19,644 exactly 640×448 pixels, 18,965 over
  (mostly one tile from the final nibble), 17 short; 'T': 3,923 exactly the segment total,
  3,865 over. Decoded frames shown as RGB555 bottom-up give a coherent picture (e.g. frame
  30 of DVD `AS/PLA/1001.CNM`).
- **Reference:** `reference/multimedia_cx/Game_Formats/CNM.md` "version 1" describes a
  different scheme (3-bit delta tiles, motion vectors); the binary does not do that for
  HBR. Templier's `graphics/movies/cinematic1.cpp` was not followed.
- **Method:** decompiles in `engines/ring/notes/decomp/`; Python prototype then
  `ring_hbr` in `parsers/ringdec.c`; `python engines/ring/tools/parsers/cnm.py`: 100%.
- **Confidence:** proven

### E-0029 — Video sound chunks are raw PCM; the language channel picks 'Z', 'A' or 'B'
- **Binary/file:** `RING_DVD.EXE` `aCinMov::ReadSound` 0x415770, `aCinMov::Play` 0x415990;
  DVD `.cnm`
- **Evidence:** ReadSound reads a u32 byte count (rejects > 10,000,000), reads that many
  bytes and hands them unchanged to 0x46a590 (the stream sound), or frees them when sound
  is off; the format is the header's (1 channel, 16 bits, 22,050 Hz). Play reads 'Z' when
  the channel at `this+0x61` (Init's 5th argument) is 0 or 1, 'A' when it is 2, 'B' when
  3, and skips the others (SkipSound). DVD corpus: 26,799 non-empty and 12,229 empty 'Z'
  chunks, 7,111/1,585 'A', 7,234/1,462 'B', all of even length; 14 DVD videos carry all
  three tracks, 306 only 'Z' with sound, 132 only empty 'Z'.
- **Method:** decompiles; census over the DVD `.cnm`.
- **Confidence:** proven

### E-0030 — Boot sequence, zone numbering, start-up screens and the frame loop (DVD)
- **Binary/file:** `RING_DVD.EXE`: CRT entry 0x46fbfc → WinMain 0x40f720; 0x40f460 (window,
  DirectDraw, timer 100); window procedure 0x40eec0 (timers 100/101, mouse, keys,
  `WM_CLOSE`); `aApplication::Init` 0x407b80; 0x430ed0, 0x431040, 0x4314a0; frame 0x40e9f0;
  zone folders 0x402010, characters 0x4020b0, `GetreadFrom` 0x402130
- **Evidence:** as written in `engines/ring/docs/spec/boot.md`, each step read from the
  named function: `CreateWindowExA(8, "Ring", "Ring", 0x90000000, 0, 0, 0x280, 0x1e0)`,
  0x40e740(0x280, 0x1e0, 0x10), `SetTimer(100, 3000)`; timer 100 creates the application
  (`operator new(0xa6)`, 0x407750), calls Init, 0x430ed0, 0x431040 and `SetTimer(0x65,
  2000)`; timer 0x65 calls 0x4314a0 and `StartMenu(0)`. 0x402010 returns `sy ni rh fo ro wa
  as n2` for 1..8; 0x4020b0 returns "" for 1, Alberich (2, 3), Siegmund (4), Loge (5, 8),
  Brünnhilde (6), Dril (7). Init stores the `ART_SY`, `ART_AS`, `ART_NI`, `ART_N2`,
  `ART_RO`, `ART_RH`, `ART_WA`, `ART_FO` values at app+0x4b..0x52 in that order;
  `GetreadFrom` maps zone 1..8 to +0x4b, +0x4d, +0x50, +0x52, +0x4f, +0x51, +0x4c, +0x4e.
  0x431040 calls 0x4662a0, 0x4635a0, 0x45eb30, 0x45b610, 0x458a90, 0x455a50, 0x44f3e0,
  0x44ab00 with app+0x58 set from +0x4b, +0x4c, +0x4d, +0x4e, +0x4f, +0x50, +0x52, +0x51
  (so they are the SY, AS, NI, N2, RO, RH, FO, WA set-ups). 0x4314a0 plays `logo`
  (0x401490 builds `…\PLA\` + name + `.cnm`; DVD `DATA/SY/PLA/LOGO.CNM`) and fades the
  `beg*.bmp` pictures (20 frames, holds 3000/0/6000 ms) with Escape checks between.
  The frame clears the rectangles (0, 0)–(640, 16) and (0, 0x1d0)–(640, 0x1e0) with a
  colour fill, then switches on 0x40b7c0 (0..4).
- **Reference:** Templier's `shared.h` zone ids (SY 1, NI 2, RH 3, FO 4, RO 5) agree; his
  `ApplicationRing::setup`/`showStartupScreen` cover the same steps.
- **Method:** decompiles in `engines/ring/notes/decomp/` (define_and_decompile for the
  window procedure and 0x40e9f0).
- **Confidence:** proven

### E-0031 — The zone API: declarations, their wrappers and the model classes (DVD) (call count SUPERSEDED by E-0032)
- **Binary/file:** `RING_DVD.EXE`: the 58 callees of the eight zone set-ups (0x4662a0 SY,
  0x4635a0 AS, 0x45eb30 NI, 0x45b610 N2, 0x458a90 RO, 0x455a50 RH, 0x44f3e0 FO, 0x44ab00
  WA; E-0030); ctors `aPuzzle` 0x41b740, rotation 0x41da10, `aObject` 0x41f940,
  `aAccesibility` 0x4230c0, `aMovability` 0x423280, hot spot 0x423770, transition setter
  0x423730, `aSoundItem::Init` 0x41a150, sound list 0x4683c0
- **Evidence:** `ring_calls.py` lists 4,146 calls in the eight set-ups
  (`engines/ring/notes/calls/*_setup.jsonl`); each callee decompiled
  (`engines/ring/notes/decomp/api/`, `…/model/`) and its argument flow written in
  `spec/api.md`: the id lookups (objects app+0x79, puzzles app+0x7d, rotations app+0x85),
  the delegate calls and their argument order, the constructors' field offsets, the
  movability kinds passed by the four `…AddMov…` wrappers (0, 1, 2, 3), the default
  transition (0, 0, 0x42aa0000, 0, 2, 0, 0, 0x42aa0000), the transition layouts set by
  `PuzSetMovToRot`/`RotSetMovToPuz`/`RotSetMovToRot`, the fade check of `aSoundItem::Init`
  (`1 < fade`, stored `fade − 1`). The unnamed wrappers delegate as follows and are named
  after it (Ghidra, `rename.py`): 0x402210 SetZone, 0x403090 → `ObjSetAccOnOrOff(…, 0, …)`,
  0x405850 → `RotSetMovOnOrOff(…, 0, …)`, 0x406080/0x4060b0/0x406100/0x406180/0x406200/
  0x406280 → `aVar::VarDefByte`/`VarSetByte`/`VarDefWord`/`VarDefDwrd`/`VarDefFloa`/
  `VarDefStrg`, 0x405e80 (strings `RotAdd3DSou`) → `aRotation::Add3DSound`.
- **Reference:** Templier's `Application` has the same set under long names
  (`objectAddPuzzleAccessibility`, …) and names several parameters (volume, pan, frame
  count, frame rate, amplitude/speed); those names are not taken over where the binary
  does not show the use (they stay `unk_*` in `spec/api.md`).
- **Method:** decompiles; `tools/ghidra/scripts/ring_calls.py`.
- **Confidence:** proven for what `spec/api.md` states; `unk_*` are open.

### E-0032 — The eight zone set-ups make 4,149 calls (corrects E-0031's 4,146)
- **Binary/file:** `engines/ring/notes/calls/*_setup.jsonl`
- **Evidence:** 286 (SY) + 373 (AS) + 657 (NI) + 477 (N2) + 399 (RO) + 415 (RH) + 924 (FO)
  + 618 (WA) = 4,149 lines.
- **Method:** line count.
- **Confidence:** proven

### E-0033 — Seventeen zone dispatchers route engine events to per-zone handlers (DVD)
- **Binary/file:** `RING_DVD.EXE`: the callers of 0x402450 (current zone) that switch on it:
  0x40bbb0, 0x40bd40, 0x40bed0, 0x40c060, 0x40c1f0, 0x40c2b0, 0x40c420, 0x40c590,
  0x40c650, 0x40c7a0, 0x40c910, 0x40ca80, 0x40cc10, 0x40cde0, 0x40ced0, 0x40cff0,
  0x40d130 (0x40d1f0 and 0x40d220 also read the zone); key handler 0x40b060; right button
  0x40afe0; `MouseLeftEvent` 0x409d90
- **Evidence:** each dispatcher's cases 1..8 and its callers (table in `spec/events.md`,
  generated from the decompiles in `engines/ring/notes/decomp/flow/` and `callers.py`).
  Cases map to zones by the numbering of E-0030. The `(param_3 == 1 && param_4 == 1)`
  override precedes the switch in 0x40bbb0, 0x40bd40, 0x40bed0, 0x40c060, 0x40ca80.
  0x40b060 compares the key with each enabled hot spot's key (0x423950) of the puzzle's or
  rotation's accessibility list and calls 0x40af80/0x40afb0 on a match.
- **Method:** decompiles; `tools/ghidra/scripts/callers.py`.
- **Confidence:** proven (routing); the event names in the table are from the callers
  and are refined in the zone specs.

### E-0034 — Image and archive paths, decoder choice, archive lookup (DVD) (SY count SUPERSEDED by E-0035)
- **Binary/file:** `RING_DVD.EXE`: image handle ctor 0x42d260, `aPuzzle::Alloc` 0x41bdc0
  (disassembly 0x41bdc0..0x41bfa9), `aImage::Load` 0x413150, `aArtHandler::Open`
  0x419bc0, `GetData` 0x419e10, index 0x419b50, `aArt` name lookup 0x419890 with
  0x479410, `GameSetZone` 0x40d220; the DVD's `DATA/AS/IMAGE/*.BMA` and `DATA/AS.AT2`
- **Evidence:** the ctor stores zone (+0x79), app+0x5d (+0x7a) and load-from (+0x7b);
  Alloc builds `sprintf("%s%s\%s\%s\%s", 0x402470()|0x402480(), "DATA",
  0x402010(zone), "IMAGE", name)` for `'e'` with +0x7a = 1|2, `sprintf("\%s\%s",
  "IMAGE", name)` for `'f'`, `sprintf("%s%s", 0x42d710(), name)` for kind 5, then
  `aImage::Load(path, loadFrom, zone, kind)`. Open builds `sprintf("%s%s\%s.at2", prefix,
  "DATA", 0x402010(zone))`. 0x419b50 maps kinds 2..5 to (zone 1, kind 2). 0x479410 is a
  case-folding compare. `GameSetZone` opens the zone's archive with kind 1 when
  `GetreadFrom(zone) == 'f'` and the zone is not 1. Corpus: of the image names the AS
  set-up declares, 96 of 96 exist only as loose files; in NI, FO, WA and SY the declared
  images are archive members (NI 51 of 51, FO 72 of 72, WA 68 of 68, SY 66 of 67; SY's
  `osc.bmp` is neither), sounds are loose files.
- **Method:** decompiles and disassembly; name census over `notes/calls/*_setup.jsonl`
  against the archives and `DATA/<zone>/`.
- **Confidence:** proven

### E-0035 — SY declares 57 distinct puzzle images, 56 of them in SY.AT2 (corrects E-0034)
- **Binary/file:** `notes/calls/sy_setup.jsonl` (`PuzAddBgrImg`, `ObjPreAddImgToPuz`),
  DVD `DATA/ENG/SY.AT2`
- **Evidence:** 57 distinct names, 56 archive members; `osc.bmp` is not a member (it is a
  loose file only in Prophet). NI 51/51, FO 72/72, WA 68/68 distinct stand.
- **Method:** set comparison.
- **Confidence:** proven

### E-0036 — Draw types, alpha, and puzzle drawing order (DVD)
- **Binary/file:** `RING_DVD.EXE`: video device vtable 0x47e388 (slot 9 = 0x414790),
  0x42c210, 0x42c180, 0x42c0a0 (constant 0x47e4fc = 1/255), `aPuzzle::Update` 0x41c320,
  `aPuzzle::AddPreImg` 0x41cb70, image handle ctor 0x42d320 and setters 0x42d760 (+0x6b),
  0x42d770 (+0x67), 0x42d790 (+0x66), getters 0x42d780/0x42d7a0/0x42d7c0/0x42d810
- **Evidence:** 0x414790 switches on the device depth (+0x20) and the image depth (+0x15):
  8/16-bit images go to `aImage::Display1`; 24/32-bit ones by the type byte: 1 Display1,
  2 locks the surface and writes converted pixels except where the three source bytes
  are 0, 3 locks and calls 0x42c210, which per row calls 0x42c180: `a = src & 0xff0000;
  a == 0 → skip; a != 0xff0000 → per channel mask m: (src & m) + ((dst & m) × (0xff −
  a>>16) >> 8) & m`. 0x42c0a0 (disassembly): factor = alpha × 1/255 (x87), each of the
  three channels × factor truncated (`__ftol`), shifted into the display masks, alpha to
  bits 16..23. `aPuzzle::Update` draws the background with type 1, advances animations
  when +0x28 is 0, then walks +0x10 drawing kind-1 handles with `draw(h, +0x55, +0x59,
  +0x66)` when active and shown, kind-2 through 0x422940. `AddPreImg` inserts before the
  first entry whose +0x67 is greater. The declarations place backgrounds at (0, 16) and
  `RenderFrame` fills (0,0)–(640,16) and (0,0x1d0)–(640,0x1e0).
- **Method:** decompiles and disassembly.
- **Confidence:** proven

### E-0037 — Video timing, skipping and sound; the DisFad fade (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x401490 (`PlyCin`), `aCinMov::Init` 0x415340,
  `aCinMov::Play` 0x415990, `aCin::Decompress` 0x42cb90, `DisFad` 0x4018c0, wait 0x402890;
  constants 0x47e270 (1000.0 double), 0x47e408 (0.01 double), 0x47e278 (0.0)
- **Evidence:** Init sets `this+0x5c = 1000.0 / (hdr[+0x12] × 0.01)`; PlyCin overrides it
  with `1000.0 / rate` when rate ≠ 0 and calls `Play(0, 0x10)`, whose picture draw is the
  device's slot 0x14 with those coordinates. In the 'S' case with sync on (+0x5b = 1):
  elapsed ≤ due → (after the first picture) busy-wait while `elapsed + 0x32 < due`, then
  ReadImage; elapsed > due → `aCin::Decompress`, which reads the 0x14-byte header and
  seeks past the payload. ReadSound passes the bytes to 0x46a590; the first sound chunk
  starts the stream (0x46a4b0). The loop polls `GetAsyncKeyState(VK_ESCAPE)` and ends when
  the picture count reaches the header's. DisFad: both images loaded, equal width/height
  and depth 24 required (errors "Height is not the same", "Only true color images");
  per byte `(short)((from − to) / frames)`; `aAnimation::Init(frames, 0x41c80000 (25.0),
  1, 4, 0)`; per new animation frame subtract the steps from the from-image bytes and draw
  it with slot 0x14 at (0, 0x10); afterwards draw the to-image, then `0x402890(hold)`,
  which loops on `GetTickCount` until `hold` ms passed or Escape is down.
- **Method:** decompiles and disassembly (0x401f05..0x401f19, 0x402890..0x4028c5).
- **Confidence:** proven

### E-0038 — The ten languages and their channels; PlyCin plays channel 0
- **Binary/file:** `RING_DVD.EXE` `aApplication::Init` 0x407b80 (calls at the top of the
  function), strings 0x485a48..0x485a6c; `PlyCin` 0x401490
- **Evidence:** `AddLanguage(1, ENG, ENG, 1)`, `(2, FRA, FRA, 2)`, `(3, GER, GER, 3)`,
  `(4, ITA, ITA, 1)`, `(5, SPA, SPA, 2)`, `(6, SWE, SWE, 1)`, `(7, HOL, HOL, 3)`,
  `(8, HEB, HEB, 1)`, `(9, GRE, GRE, 1)`, `(10, SLO, SLO, 1)`. PlyCin calls
  `aCinMov::Init(path, name, device, 1, 0)`: channel 0.
- **Method:** decompile.
- **Confidence:** proven

### E-0039 — Cursor kinds, files, animation clock and drawing (DVD)
- **Binary/file:** `RING_DVD.EXE`: `CurAdd` 0x402750 / 0x4027c0, `CurSet` 0x402840,
  `CurSetOffset` 0x402860, `aCursorHandler::Add` 0x41efb0, `Set` 0x41f7a0, draw overload
  `Set(HDC, x, y)` 0x41f720, `SetOffset` 0x41f820, `GetType` 0x41f8c0; cursor vtables
  0x47e588 (kinds 1/2: 0x42fd70 load, 0x430250 `SetCursor`, 0x430270 `DrawIcon`),
  0x47e544 (kind 3: `aCursorImage::Alloc` 0x42fb80, draw 0x42fc20), 0x47e504 (kind 4:
  `aCursorAnimation::Init` 0x42f8f0, draw 0x42f9d0 → 0x423030 = 0x416850 + 0x422950);
  base slots 0x423bb0 (id, +4), 0x423660 (kind, +0xc), 0x430e90 (offset +0x10/+0x14);
  `aAnimation::Init` 0x416450, `SetStartFrame` 0x416bd0, advance 0x416870, start 0x416670,
  `aAnimationImage::Init` 0x4219f0, `aAnimation::Alloc` 0x421d10; strings 0x488200,
  0x488214, 0x488228, 0x488eb4, 0x488ee4, 0x48cd50..0x48cd8c (`IDC_*`); frame 0x40ede5
  (disassembly); `DATA/ENG/SY.AT2` member list
- **Evidence:** Add switches on the kind: 1/2 → ctor 0x42fc70, 3 → 0x42f9f0, 4 →
  0x42f7d0 + `aCursorAnimation::Init`; kind 3 builds `\%s\%s.tga` (archive) or
  `%s%s\%s.tga` / `dummy_p.tga` (disk) only when its 8th argument is 3 or 4. 0x402750
  refuses kind 4 and passes `(id, name, kind, a4, 0, 0, 0, a5, a6)`; 0x4027c0 accepts only
  kind 4 and passes all nine. Disassembly of 0x42f8f0: `aAnimationImage::Init(name, 1, 0,
  0, 0, 3, frames, fps, 1, flags, a4, 0, a8, a9)`, which calls `aAnimation::Init(frames,
  fps, 1, flags, 0)` and stores the 6th argument (3) as the draw type (+0x7d) and a4 at
  +0x81 (1 → `Alloc` at once). `aAnimation::Init`: +8 frames, +0xc fps, flags 4/8/0x10/0x20
  → +0x14 loop mode, bit 2 → +0x2d; +0x53 = `__ftol(1000.0 / fps)` (fdivr of 0x47e270).
  `SetStartFrame(n)` stores n − 1 at +0x10 and +0x22. 0x416870 (+0x21 = 1): when `now −
  last > +0x53` the index moves by 1 and `last = now`; mode 4 wraps to +0x10 after the
  last frame. 0x422950 loads frame `+0x22 + 1` with `%04d` and draws it through the device
  slot 0x24 with the draw type +0x7d. 0x42fc20 draws the kind-3 image at (x − +0x10,
  y − +0x14) with type 3; 0x42f9d0 the same offsets for kind 4. The frame (0x40ede5 on)
  calls `GetType` and, for 3 or 4, 0x41f720(0, mouse x, mouse y). 0x42fd70: kind 1
  compares the name with the `IDC_*` strings and calls `LoadCursorA(0, IDC_…)`, else
  `LoadCursorA(hInstance, name)`. The archive holds `cur_idle.0001..0015`,
  `cur_muv.0001..0020`, `cur_hotspot.0001..0019`.
- **Method:** decompiles (`engines/ring/notes/decomp/cursor/`), capstone disassembly of
  the call sites, archive listing.
- **Confidence:** proven
- **Reference:** Templier's `base/cursor.cpp` has the same kinds; not used for any value.

### E-0040 — Hot-spot tracking and left click search order (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x408dd0 (tracking), `MouseLeftEvent` 0x409d90,
  hot spot getters 0x4238b0 (contains), 0x423910 (+0x15 cursor), 0x423920 (+0x19),
  0x423930 (+0x10 enabled), 0x40f6c0 (`GetCursorPos` → 0x4956a4/0x4956a8 and
  0x495584/0x495594, then the frame 0x40e9f0), 0x406530, 0x40e610
- **Evidence:** 0x4238b0: enabled && x1 ≤ x < x2 && y1 ≤ y < y2 (`jl`/`jge`).
  0x408dd0: bag shown (app+0x8d +0x94) → 0x418a70; else puzzle 1 (0x40b760(1)):
  accessibilities (mode +0x24 = 2 and object ≠ +0x29 → break), hit → `CurSet(hot spot
  cursor)` and 0x40ca80(object, +0x19, puzzle id, 1, x, y); mode 1 → movabilities → 0x40cc10;
  mode 2 → `CurSet(0x32)` + 0x433bc0, return; then app+0x89 (when +0x28 = 0) with
  0x41e370/0x41e470 lists, fifth argument 0; then app+0x81 (0x41d7a0 first); none →
  `CurSet(0x32)` and 0x40cde0. Drag (app+0x99 +0x20) → 3/4; 0x406530 (app+0x8d +0x95 ≠ 0)
  → 2 / 1. `MouseLeftEvent` walks puzzle 1 then app+0x81 the same way and calls 0x40bbb0
  when the object's byte +0xc has bit 0, 0x40bed0 for bit 3, then 0x408dd0. The two
  mouse globals are both the raw `GetCursorPos` result; no path adds or subtracts 16.
- **Method:** decompiles, disassembly (0x40f6c0, the hot spot getters, a scan of the
  input paths for `0x10` adjustments).
- **Confidence:** proven
- Supersedes the event names "hot spot entered / left" of E-0033 for 0x40ca80 / 0x40cc10
  (routing unchanged).

### E-0041 — Zone SY: main menu, dialogues and their handlers (DVD)
- **Binary/file:** `RING_DVD.EXE` `aApplication::StartMenu` 0x40dc80, `PuzSetAct`
  0x402490, `PuzSetMod` 0x404ab0 → 0x41d000, `ObjPreSho` 0x403c80, `ObjPreHid` 0x403d00,
  `ObjPreHidDeaPuz` 0x403f00 → 0x420b30, `ObjSetAccOnOrOff` 0x4030b0 (0x403030 on,
  0x403050 off), question 0x40e090 / 0x40e120, warning 0x40dfd0 / 0x40e060,
  `aApplication::Init` 0x431140; SY handlers 0x4335a0, 0x433b80, 0x433bc0, 0x431660;
  `DATA/ENG/SY.AT2` pictures
- **Evidence:** as listed in `games/ring/docs/sy.md` from the decompiles in
  `engines/ring/notes/decomp/sy/`. 0x431660's new-game branch falls through into the
  `unk_19` 3 case (disassembly 0x431807..0x43181b: `Init`, then 0x40e120(2)).
  0x431140 loads the preferences and calls 0x402280(7, 999). The `gm_*.bmp` pictures are
  BMA 352×30 (`bma.py`), `Exit.bmp` 320×150 with the question drawn in, `ex_yes.bmp` 56×24.
- **Method:** decompiles, disassembly, rendering the pictures with the validators.
- **Confidence:** proven (the handlers); the unexplained 16-pixel offset is Q-0009.

### E-0042 — Argument counts of `ObjPreSho` and `SouAdd` (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x403c80, 0x403e00, 0x406970, 0x406ba0;
  `engines/ring/notes/calls/*_setup.jsonl`
- **Evidence:** the callee's `ret n` (the `purge` field) over all 4,149 extracted calls:
  0x403c80 pops 8 bytes (34 calls, object and presentation; the decompile passes the second
  argument to `aObject::ShowPresentation`), 0x403e00 pops 4 (8 calls; its error string is
  `ObjPreSho(INT id)`); 0x406ba0 pops 24 (468 calls), 0x406970 pops 16 (23 calls). The
  table in `engines/ring/tools/zonedecl.py` had both pairs the other way round; the notes
  in `engines/ring/notes/zones/` are regenerated, and its selftest now checks every
  call's argument count against the purge.
- **Method:** script over the call lists; decompiles of 0x403c80 / 0x403d00 / 0x403f00.
- **Confidence:** proven

### E-0043 — Fonts: `arxrin.fon` and the DVD's `ARXRIN.*` are NE raster font files
- **Binary/file:** `games/ring/discs/*/arxrin.fon` (3 copies, MD5 `1005a256…`),
  `dvd-edition/ARXRIN.GRE`, `.HEB`, `.SLO`; `prophet-and-assassin/discs/cd1/Legend.FON`;
  `RING_DVD.EXE` 0x407b80 (`AddResource("arxrin.fon")`), 0x4265b0 (`AddFontResourceA`)
- **Evidence:** `engines/ring/tools/parsers/fon.py`: 7 files, 4 distinct, 100% parsed; every
  byte of every font resource accounted for (header, character table, glyph bitmaps, face
  name; zero or, in `ARXRIN.SLO`'s first font, 0xFF padding after dfSize). Contents in
  `docs/formats/README.md` "Fonts". `ARXRIN.HEB`'s charset (2) is the `lfCharSet` the EXE
  sets for language 8 (E-0044).
- **Method:** validator over the corpus, `--selftest`.
- **Confidence:** proven

### E-0044 — Texts: font 1, `aText`, text drawing, `GetMultiLanMes` (DVD)
- **Binary/file:** `RING_DVD.EXE` `aApplication::Init` 0x407b80 (lines with `FonAdd`),
  `FonAdd` 0x406900, `aFontHandler::Add` 0x426820, 0x4262d0 (`CreateFontIndirectA`),
  `GetFontHandler` 0x426a90, `ObjPreAddTxtToPuz` 0x403b10 → 0x42f270, `aText::Init`
  0x42c450, set string 0x42c550 (`GetTextExtentPoint32A`), 0x42f520, 0x42f5d0, text draw
  0x414df0 (`SetBkMode`, `SetBkColor`, `SetTextColor`, `TextOutA`), `aPuzzle::Update`
  0x41c320 (texts after images), `GetMultiLanMes` 0x40e150 (format strings `%sames.ini`
  0x4861e4, `rt` 0x4823e4, `%s\n` 0x4861a8), question 0x40e090, warning 0x40dfd0;
  `AMES.INI`
- **Evidence:** as described in `engines/ring/docs/spec/text.md`, from the decompiles in
  `engines/ring/notes/decomp/text/`. `FonAdd(1, face, height, 1, 2, 2, 2)` with face
  `ArxelHebrew`/12 for language 8, `Arial`/16 for 9, `ARX Pilgrim L`/12 otherwise; weight
  `(arg != 1 ? 300 : 0) + 400`. Question and warning lines at (0xe1, 0xc1) and (0xe1, 0xd5).
- **Reference:** Templier's `base/text.cpp` and `base/font.cpp` cover the same classes; not used as proof.
- **Method:** decompiles, string reads with `pefile`.
- **Confidence:** proven (behaviour); GDI's size choice for height 12 is Q-0010.

### E-0045 — Keys on accessibilities (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x40b060, 0x41d890, 0x40af80, 0x406e40 → 0x469150;
  SY key handler 0x433d30; `ObjSetPuzAccKey` calls in `engines/ring/notes/zones/sy.md`
- **Evidence:** as written in `spec/events.md` "Keys and accessibilities", from the
  decompiles in `engines/ring/notes/decomp/flow/` (0x40b060) and
  `engines/ring/notes/decomp/text/`. Puzzle 1 in mode 2 is searched without calling the zone's key handler (the handler call
  is on the path where puzzle 1 is missing or not in mode 2).
- **Method:** decompiles.
- **Confidence:** proven
- Supersedes the order in E-0033's summary of the key path ("first the zone's key handler,
  otherwise the current puzzle"): the handler is skipped while puzzle 1 is in mode 2.

### E-0046 — Rotation rendering, looking around and rotation hot-spot coordinates (DVD)
- **Binary/file:** `RING_DVD.EXE` renderer state at 0x495710 (grid u at +8, v at +0x4008,
  64 words per row; columns +0x8028, rows +0x802c; corners +0x8030..+0x805c; ranges
  0x49d794..0x49d7b0): 0x40f900 (40 × 28 blocks, 640 × 448), 0x40f7d0.. defaults,
  0x40f9e0 (camera: ran clamp 30/87 at 0x47e2fc/0x47e2f8, `ran × π / 360`, alpha wrap
  0/360 at 0x47e278/0x47e27c, beta margin 5 at 0x47e2e0, forward from alpha/beta with
  1/180 at 0x47e2dc, 0x410a20 look-at, 0x410bb0), 0x411c90 (grid: asin = 0x46fd50, which is
  `fpatan(x, sqrt((1+x)(1−x)))`; the quadrant fix at 0x41203b..0x41206c; scale 2048 at
  0x4862d8 and 65536 at 0x47e330), 0x412180 / 0x4123c0 (v clamp), 0x412230 / 0x4116e0
  (block fill; sampler at 0x41177a: `(v & 0xfff0000) >> 5` plus `(u & 0x7ff0000) >> 16`,
  `>> 2` into the index array at +0x1fa40, `x & 3` into the table entry), 0x410410 / 0x412640
  (header words at stream+8, table at +0x3c, indices 0x1fa40 after it), 0x4107f0 (panning:
  1/640 0x47e32c, 1/480 0x47e328, 0.25 0x47e320, 48 0x47e318; `VK_UP`/`VK_DOWN`), 0x4119e0
  and 0x412360 (mouse to panorama, tenths of a degree: factor 10 at 0x47e358),
  `RotSetAlp` 0x405920 (−135 at 0x47e280), `RotSetBet` 0x4059b0, `RotSetRan` 0x405a30,
  `aApplication::RotSetAct` 0x4025b0 (`SetCursorPos(0x140, 0xf0)`), frame 0x40e9f0 (draw
  at `pitch × 16`); AS entry 0x437ba0 case 999: `RotSetAlp(80001, 90)`,
  `RotSetRan(80001, 85.3)`, `RotSetAct(80001, 1, 1)`, timers 2, 3, 4
- **Evidence:** as written in `spec/rotation.md`, from the decompiles and disassembly in
  `engines/ring/notes/decomp/rot/` (and `as/`). Hot-spot x values in the zone set-ups
  reach 3,596 (`notes/zones/*.md`), consistent with tenths of a degree, not columns.
  Writes to rotation byte +0x67 in the whole `.text` (linear capstone sweep): only
  0x40d34d and 0x40d359.
- **Reference:** Templier's `base/rotation.cpp` (`updateView`, `setCoordinates`) names the
  same constants; his renderer (`ImageHeaderEntry::drawBuffer`) is unimplemented. Not used
  as proof.
- **Method:** decompiles, disassembly (capstone), constant reads with `pefile`.
- **Confidence:** proven for the formulas; the pan speed's time base is Q-0011.
- Supersedes the api.md reading (under E-0031) of `ObjAddRotAcc` coordinates as "the
  panorama's 2048-wide space"; the row is corrected.

### E-0047 — Clicking movabilities and animated turns (DVD)
- **Binary/file:** `RING_DVD.EXE` `aApplication::MouseLeftEvent` 0x409d90 (rotation part
  from 0x40ab.., puzzle part before it), 0x40af80 (sets app+0xa5), 0x4101c0 (animated
  turn: −135 at 0x47e280, fold at 0xb4/0x168, factor 0.8 at 0x47e30c), 0x410170,
  0x40c2b0 / 0x40c420 (events), `PlyCin` 0x401490
- **Evidence:** as written in `spec/rotation.md` "Clicking a movability", from
  `engines/ring/notes/decomp/flow/RING_DVD.EXE__aApplication__MouseLeftEvent.c`,
  `notes/decomp/rot/range/RING_DVD.EXE__004101c0.c` and the disassembly of 0x4101c0.
- **Method:** decompiles, disassembly.
- **Confidence:** proven

### E-0048 — The preferences screen and `aPre.ini` (DVD)
- **Binary/file:** `RING_DVD.EXE` SY object click 0x431660 (cases 0x15f91, 0x15ff5..0x15ffb),
  on-accessibility 0x4335a0, on-nothing 0x433bc0, drag event 0x4331b0, `aPreFer::Load`
  0x428870, `aPreFer::Save` 0x428920, 0x4289c0 (store), 0x4289e0 (apply: 0x406e80(5, v0)
  → 0x469350 = every sound whose channel (+8) is not 5; 0x406e60(5, v1) → 0x4692f0 =
  channel 5; `aSoundHandler::SetLR` 0x41b5b0 (1 → 1.0, −1 → −1.0 at 0x487748); app+0xc
  +0x28 = v3), 0x406ee0 → 0x468310 (0x4a1d04 != 0), credits 0x431350; the dialogue
  handler is app+0xc (0x407b80 allocates it, "Can not Allocate aDialogHandler"), its
  constructor sets +0x28 = 1 (0x427b4d) and 0x427e9d skips the two text draws (0x414df0)
  when +0x28 is 0; the SY set-up (`notes/zones/sy.md`); `aPre.ini` of all three editions.
- **Evidence:** as written in `games/ring/docs/sy.md` "Preferences"; decompiles in
  `engines/ring/notes/decomp/sy/` and `notes/decomp/drag/`. Slider arithmetic: 0x13a
  (314), divisor 5, clamp 0x36 (54), offset 0x2e (46); opening places the picture at
  value × 5 + 0x54. Save's third argument is `(-(swapped != 0) & 2) - 1`. The corpus
  `aPre.ini` files are all `100 100 -1 1`.
- **Reference:** Templier's `ring_zonesystem.cpp` calls 90103 "subtitles" and 90104
  "reverse stereo"; both confirmed above (the +0x28 test, `SetLR`).
- **Method:** decompiles, disassembly of 0x40c060 and 0x427e80..0x427ecb.
- **Confidence:** proven

### E-0049 — Dragging; the left click comes on release (DVD)
- **Binary/file:** `RING_DVD.EXE` window procedure 0x40eec0 (`WM_LBUTTONDOWN` 0x201 →
  0x409630, `WM_LBUTTONUP` 0x202 → 0x40af80 / 0x40afb0, both only for y < 0x1d1), frame
  0x40e9f0 (0x409520 while the button is down, 0x495704), 0x40f6c0 (GetCursorPos into
  0x495584/0x495594 and 0x4956a4/0x4956a8; the rotation's 0x4107f0 then rewrites the
  latter), 0x409630, 0x409520, `MouseLeftEvent` 0x409d90 (drag release at its top),
  0x40c060 (6 arguments, `ret 0x18`; SY with puzzle 1 and flag 1), drag control 0x426040
  (start), 0x426140 (move), 0x4260d0 (clear, limit (0, 16, 640, 464), cursor kind 3
  entries dropped), 0x426240, 0x426290, 0x406660, 0x406680, 0x4067d0, 0x4068c0,
  0x40b9b0 (drag cursors 3/4: `%s_dp` / `%s_da` with the icon or `dummy`, 0x485b14..
  0x485b24).
- **Evidence:** as written in `spec/cursor.md` "Dragging" and "Left click". Pushes before
  each 0x40c060 call: phase 1 at 0x4098aa / 0x409b07 / 0x409cf4, 3 at 0x409589 /
  0x4095e5, 2 at 0x409e5c; the fifth argument is the drag control. app+0x76 is only ever
  set to 1 (0x407830 and five other stores), so the "clear when 0" branches after a start
  or a move never run. SY.AT2 holds `ni_handsel_dp.tga`, `ni_handsel_da.tga`,
  `dummy_dp.tga`, `dummy_da.tga`.
- **Method:** decompiles (`engines/ring/notes/decomp/drag/`), disassembly, byte scan for
  the stores to +0x76.
- **Confidence:** proven

### E-0050 — The sound list, volume and pan, playing, stopping, sound events (DVD)
- **Binary/file:** `RING_DVD.EXE` `SouAdd` 0x406ba0 (extensions `wav`/`wac`/`was` at
  0x484c1c/18/14, paths `%s%s\%s\%s\%s` 0x482060 and `%s%s\%s\%s\%s\%s` 0x484bf8 with `DATA`
  0x482070 and `SOUND` 0x484c0c), 0x4683c0 (list 0x4a1cf0.., kind ≠ 1 → vtable 0x47e86c,
  +0x111/+0x115 = 100, +0x119 = 0, +0x121 format), 0x468170, 0x468100 (disassembly: fild
  +0x115 × 0.01 (0x47e478) × fild +0x111 × 0.01 × [0x4932a8] 1.0 × −10000 (0x47e840),
  ftol, −10000 − x → vtable +4; (fild +0x119 + 100 (0x47e83c)) × −100 (0x47e838), ftol,
  −10000 − x → vtable +8), clamps 0x468060 / 0x468090 / 0x4680c0; wrappers 0x406de0..0x406f00
  (0x406de0 passes `n != 1`: disassembly `cmp edx, 1; setne al`); `NoiceIdPlay` 0x468e20;
  0x469010, 0x469150, 0x4693b0, 0x469540, 0x4695b0; stream play 0x468ae0 (+0x11d = flag,
  0x46ab00 stores it at stream +0x28), stream thread 0x46b300 (`cmp [esi+0x28], 0` at
  0x46b3ec: zero → silence and stop, else rewind), stop 0x468c90 (+0x10c = 0); frame check
  0x40f6c0 → 0x468da0 → 0x4681d0, 0x40f690 (`push 0x1001`, skips type 5); event dispatcher
  0x40ced0 (splits bit 0x1000; disassembly `and esi, 0x1000; and bh, 0xef`); 0x40b650
  (0x406e40(4, 0x10), 0x406e40(5, 0x10)); type names: Templier `shared.h`
  `kSoundType*` (Reference), confirmed for 2, 3 by the `ASOUNDTYPE_AMBIENTMUSIC/EFFECT`
  checks in the four Add wrappers and for 5 by the dialogue branches.
- **Evidence:** as written in `spec/sound.md` "The sound list" .. "Playing, stopping,
  events"; decompiles in `engines/ring/notes/decomp/sound/`. Corpus: every `SouAdd` in the
  set-ups passes kind 2 (491 calls in `ring/setup.cpp`).
- **Method:** decompiles, disassembly (`/tmp`-style capstone reads of the listed
  addresses), call-site scan for 0x40ced0.
- **Confidence:** proven (the DirectSound unit mapping is DirectSound's documented one)

### E-0051 — Dialogues: `.dia` timing and subtitles, `.dan` lip sync (DVD)
- **Binary/file:** `RING_DVD.EXE` `aDialog::Init` 0x426ef0 (`%s%s\%s\%s\%s\%sdia` 0x486afc,
  `DIA` 0x486b10, install prefix 0x402480; `…dan` 0x48a0d4), `ReadLyrics` 0x427090,
  `ParseLyricLine` 0x427550, `ReadDialogAnimation` 0x4271b0 (disassembly 0x427222..0x427288:
  `%d %d %d` read into (a, b, c) and stored as (b, c, a); 0x42738f..0x4273f5 stored as
  read), `AddDialog` 0x427f20, `RemoveDialog` 0x428050 → 0x4279b0, 0x427880, 0x427900,
  0x427940, 0x427980, 0x427a10, the per-frame 0x427c70 (`push 0x1001` at 0x427cd4),
  0x427b30 / 0x427c20 (called from 0x407b80 with 1, 200, 200, 0x1e, 0, 0, 0, 0x1cd, 3);
  corpus `DATA/AS/DIA/ENG/1060.DIA` (`5000   END`), `1072.DIA`, `DATA/FO/DIA/ENG/1322.DAN`
  (`1`, `1 30101 0`, then `0 28 0`, `29 1286 1`, …).
- **Evidence:** as written in `spec/sound.md` "Dialogues".
- **Method:** decompiles (`notes/decomp/dialog/`), disassembly.
- **Confidence:** proven

### E-0052 — Ambient and 3D sounds, the place-change transition (DVD)
- **Binary/file:** `RING_DVD.EXE` `PuzAddAmbSou` 0x404b00, `RotAddAmbSou` 0x405d50,
  `PuzAdd3DSou` 0x404c30, `RotAdd3DSou` 0x405e80, `aPuzzle::AddAmbientSound` 0x41d080 →
  0x41a120 (Init with 0.0, 0x14), `aPuzzle::Add3DSound` 0x41d250, `aRotation::Add3DSound`
  0x41e9f0 (amplitude pushed as an int, 0x41ea43), `aSoundItem::Init` 0x41a150, 0x41a220 /
  0x41a280 (on/off), 0x41a2e0, 0x41a310, 0x41a350, 0x41a3b0, 0x41a3e0..0x41a500, 0x41a4a0
  (disassembly: angle × π/180 (0x47e410) + [+0x21], fsin, × [+0x1d], ftol, × 0x41b5f0),
  0x41b5f0 (LR == 1.0 → 1 else −1), 0x41ee10, 0x41ecc0, 0x41d530, the handler functions
  0x41a820, 0x41a990, 0x41a9a0, 0x41a9b0, 0x41aa00, 0x41aee0, 0x41b130, 0x41b180, 0x41b350,
  0x41b520; `PuzSetAct` 0x402490, `RotSetAct` 0x4025b0, `MouseLeftEvent` (0x40a254..
  0x40a360), `aCinMov::Init` (0x41aee0 with the frame count), `aCinMov::Play` (0x41b180 /
  0x41b350 per frame, and with the total on Escape).
- **Evidence:** as written in `spec/sound.md` "Ambient and 3D sounds"; decompiles in
  `engines/ring/notes/decomp/ambient/`. Set-up example: `RotAdd3DSou(80001, 80206, 1, 1, 10,
  90, 270.0, 20)`.
- **Method:** decompiles, disassembly, call-site scans for 0x41aa00..0x41b350.
- **Confidence:** proven

### E-0053 — 3D sound pans follow the view every frame (supersedes part of E-0052) (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x410610 (the rotation's per-frame update, called from
  the frame at 0x40ec4a) calls 0x41ed80 at 0x41076b; 0x41ed80 runs 0x41a460(item, alpha +
  135) for every item whose sound has type 3; 0x41a460 = 0x41a4a0 (the pan) then 0x41a310
  (item +0xc and the sound's pan).
- **Evidence:** disassembly of 0x41a460; call-site scan. E-0052 said the pan was not
  updated while looking around: wrong.
- **Method:** disassembly.
- **Confidence:** proven

### E-0054 — Rotation layers and animations (DVD)
- **Binary/file:** `RING_DVD.EXE` `CAquatorStream::InitFull` 0x4111d0, 0x411150, 0x410d70
  (reads count, +4, +0x4c, then 0x412640 per entry; +0x4c = −1 for one entry), 0x410e50
  (0x412600 backup rectangle, 0x412720 copy from the panorama), 0x410610 (per-frame
  rotation update: 0x416870 over rotation +0x18's presentations' +0xd / +0x25 lists; per
  layer 0x410f50 (animated) → +0x26 clear: 0x4103d0(i, 0), else 0x411530(i, +0x22);
  0x41ed80; 0x4114c0), 0x4114c0 (dirty → 0x4126b0 with the backup when +0x5c is 0, else
  frames[+8]), 0x4126b0 (copies (x1 − x0) >> 2 u16 per row, rows y0..y1, destination
  row stride width >> 2), 0x411530, 0x411580, 0x4103d0; `aRotation::AddPreAni` 0x41e640,
  `aObjectPresentation::addImageToRotation` 0x42e720, `addAnimationToRotation` 0x42e910
  (flag bit 1 clear → animation +0x20 = 0), show 0x42ecd0, hide 0x42ee80,
  `aObject::ObjPrePauAni` 0x420db0 → 0x42f090, `ObjPreUnPauAni` 0x420e00 → 0x42f0f0,
  `ObjPreAniSetStaFra` 0x420c80 → 0x42ef60, `ObjPreSetAniIdeOnRot` 0x42f220;
  `aAnimation::Init` 0x416450, start 0x416670, stop 0x416710, advance 0x416870, pause
  check 0x416720, event dispatcher 0x40cff0 (AS: 0x437110).
- **Evidence:** as written in `spec/rotation.md` "Layers" and `spec/animation.md`;
  decompiles in `engines/ring/notes/decomp/layers/`. AS example: object 80018 presentation
  1 = `ObjPreAddAniToRot(80018, 1, 80101, 1, 49, 12.5, 4)`, id 80001, shown and paused at
  set-up; the AS animation handler compares the frame argument with byte variable 80004.
- **Method:** decompiles.
- **Confidence:** proven for the paths described; the pause-at-frame and loop controls
  (+0x28..+0x4a, 0x416720's other branches, events 0x40c7a0 / 0x40c910) are not traced.

### E-0055 — Variables and timers (DVD)
- **Binary/file:** `RING_DVD.EXE` `aVar::VarDef*` / `VarSet*` / `VarGet*` 0x424a50..0x425640
  (error strings "ID already exists", "ID does not exist"), wrappers 0x4060e0, 0x406230,
  0x406260 (0.0 from 0x47e278 without the list); `aTimer::StartTimer` 0x425c00 (`SetTimer`
  with the window 0x4956d8), 0x425700 (record), 0x425d80 (`KillTimer`), `StopAll` 0x425b30,
  0x425f00, 0x425730, `WM_TIMER` 0x40b4a0 → 0x40c590 (AS 0x436df0).
- **Evidence:** as written in `spec/api.md` "Variables" and "Timers"; decompiles in
  `engines/ring/notes/decomp/vartim/`.
- **Method:** decompiles.
- **Confidence:** proven

### E-0056 — Zone AS: entries, handlers, returning from a world, `GoZone` (DVD)
- **Binary/file:** `RING_DVD.EXE` `GameSetZoneAS` 0x437ba0 (entries 999, 998, 5, 6), object
  click 0x4364a0, animation 0x437110, before / after a movability 0x436c10 / 0x436d60, timer
  0x436df0, sound 0x437190, return from a world 0x437750, world entries 0x44a7d0 (NI),
  0x436270 (N2), 0x443710 (FO), 0x43ad00 (WA), `GoZone` 0x402280 → 0x40d220; helpers
  0x406530 (an object in hand), 0x406550 (which), 0x406570 (drop it), 0x4060e0 (byte
  variable), `PlyCinMul` 0x4016a0, `GetLanID` 0x4076b0, `GetLanCha` 0x407720.
- **Evidence:** as written in `games/ring/docs/as.md`; decompiles in
  `engines/ring/notes/decomp/as/`. The set-up (0x4635a0) is `engines/ring/notes/zones/as.md`.
- **Method:** decompiles.
- **Confidence:** proven for the handlers; the video names are the `DAT_0048d8..` strings
  of the decompiles.

### E-0057 — `TimSta` is 0x4065a0, `TimSto` 0x4065e0 (supersedes the addresses in E-0055) (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x4065a0 pushes two arguments and calls 0x425c00
  (`aTimer::StartTimer`), `ret 8`; 0x4065e0 pushes one and calls 0x425d80 (kill), `ret 4`.
  AS's new-game entry calls 0x4065a0 with (2, 100000), (3, 220000), (4, 150000) at 0x437d20.
- **Evidence:** disassembly (capstone). E-0055 had the two wrappers' addresses swapped;
  `spec/api.md` "Timers" corrected.
- **Method:** disassembly.
- **Confidence:** proven

### E-0058 — A started animation reports its frame once, even when paused (supersedes part of E-0054) (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x416870: the "just started" byte (+0x4e) is tested
  before the pause check 0x416720; when set it is cleared and the event 0x40cff0 is raised
  with frame + 1 if that differs from the last reported (+0x61, −5 after a start). Only the
  other branch calls 0x416720, which returns the frame (no step, no event) when +0x27
  (paused) is set.
- **Evidence:** `engines/ring/notes/decomp/layers/RING_DVD.EXE__FUN_00416870.c`. AS relies
  on it: the dial (80018 presentation 1) is shown then paused at set-up; on the first frame
  of rotation 80101 it reports frame 1, which equals byte 80004's initial 1, so the AS
  handler (0x437110) enables the dial's accessibilities and sets byte 80005 = 1; the turns
  then reach 11, 21, 31, 41, the values the "go" accessibility tests (`games/ring/docs/as.md`).
- **Method:** decompile.
- **Confidence:** proven

### E-0059 — AS timer 5: periods in ms and the sway constants (refines E-0056) (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x436df0: `TimSta(5, 0x14 / 0x1e / 10)` and
  `TimSta(6, 10)` (milliseconds, as every `TimSta`); 0x437014 `fmul dword [0x47e300]` = 0.5,
  0x43703a `fmul qword [0x47e338]` = −1.0, 0x43705c `fmul qword [0x47e628]` = 0.8333….
- **Evidence:** disassembly (capstone) and the constants read from the EXE;
  `games/ring/docs/as.md` "Timer" corrected (it gave the periods in seconds and named the
  constants only by address).
- **Method:** disassembly.
- **Confidence:** proven

### E-0090 — Puzzle animations: arguments, frame files, advancing and drawing (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x403460 (`ObjPreAddAniToPuz`), 0x420650, 0x42e480
  (`addAnimationToPuzzle`: `Init` arguments, flag bit 1 → +0x20 = 0, lists +0xd / +0x11,
  `AddPreImg` with the first frame's handle, `AddPreAni`), 0x4219f0 (`aAnimationImage::Init`:
  x +0x71, y +0x75, draw type +0x7d, one 0x42d320 handle per frame), 0x42d320 (handle
  fields +0x70 ext, +0x79 zone, +0x7a kind, +0x7b load-from), 0x422950 (frame path
  `\%s\%s\%s.%04d.%s` with `ANI`, the name twice, frame + 1, 0x40b7f0(+0x70); disk
  formats with `DATA` and the zone folder; draws only while +0x26 is set), 0x40b7f0
  (extensions `bmp tga cin cnm` for 0..3, `bma tgc` for 5, 6), `aPuzzle::Update` 0x41c320.
- **Evidence:** `engines/ring/notes/decomp/puzani/`, `img/RING_DVD.EXE__aPuzzle__Update.c`;
  `NI.AT2` holds `ni
is02n01p03s01
is02n01p03s01.0001.bmp` … (`parsers/at2.py --file`).
  The set-ups' 140 calls use ext 0 (137) and 1 (3, draw type 3), flags 4, 6, 10, 16, 32.
- **Method:** decompiles, disassembly (sprintf arguments), corpus listing.
- **Confidence:** proven

### E-0070 — Zone NI: entries, handlers, the heater, the Flow (DVD)
- **Binary/file:** `RING_DVD.EXE` `GameSetZoneNI` 0x44a840 (entries 0, 3, 10, 999), object
  click 0x445c80, button down 0x4472b0, drag 0x4477d0, on an accessibility 0x44a120, on a
  movability 0x44a1b0 (empty), before / after a movability 0x449080 / 0x449320, timer
  0x4497b0, animation 0x4499e0, sound 0x44a1c0 (dispatcher table, `spec/events.md`); the
  heater 0x445a10, the hologram 0x445930, NI → RH 0x445720 (`GoZone(3, 0)`); the set-up's
  picture loops at 0x461018 (13), 0x4613f9 (19 + 19), 0x4615b7 (14), 0x4617d8 (14),
  0x461cd7 / 0x461e0d (1..12), 0x462355 (1..12 after an empty 0), 0x462622 / 0x4626f1 /
  0x4627c3 (48). Score constants f32 [0x47e624] 2, [0x47e620] 3, [0x47e2e0] 5, [0x47e69c] 8
  (`fadd dword`, e.g. 0x445dd1, 0x446a89). Video names from the `DAT_0048e0..` strings.
  One-argument `ObjPreSho` / `ObjPreHid` calls are 0x403e00 / 0x403e80 (e.g. 0x446c3e,
  0x44aad2). Drag getters 0x4066b0 (reference +8/+0xc), 0x4066f0, 0x406750, 0x406790,
  0x4067b0, 0x4067d0, 0x4067f0, 0x406810, 0x406850, 0x4068c0..0x4068f0 → 0x426200..0x426260;
  0x426140 shifts current → previous on a move; 0x426040 sets all three points to the press.
- **Evidence:** as written in `games/ring/docs/ni.md`; decompiles in
  `engines/ring/notes/decomp/ni/`. Set-up list `engines/ring/notes/zones/ni.md`.
- **Method:** decompiles, disassembly (capstone) for constants, loop counts and call targets.
- **Confidence:** proven for the handlers; the Flow is read from them, not played.

### E-0071 — Game over: 0x408db0(n), mode 4, 0x431190(zone, n), `End.bmp` (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x408db0: 0x40b7b0(4), app+0x70 = n, 0x406ea0(0x40).
  0x431190: jump table 0x431280 by zone − 2; zone 2: `SetZone(1)` (0x402210(1)), then by n − 1
  the table 0x43129c → 0x4311c6 / 0x4311d4 / 0x431213, each pushing 0x65 + (app+0x4b ≠ 0),
  2, 4000, 16, 0, "End.bmp" (0x48cf10) and calling 0x401000; all then `StartMenu(0)`
  (0x40dc80). 0x401000 loads the picture (load-from 'e'/'f') and shows it (waits for
  Escape's release first).
- **Evidence:** disassembly of 0x431190..0x43127b; decompiles of 0x408db0, 0x401000 in
  `engines/ring/notes/decomp/ni/`.
- **Method:** disassembly, decompiles.
- **Confidence:** proven for zone 2; 0x401000's timing is not traced.

### E-0072 — NI's exits: to RH, from FO, back to AS (DVD)
- **Binary/file:** `RING_DVD.EXE` object 10460's click → 0x445720(0) → `GoZone(3, 0)`;
  FO's 0x4447a5..0x4447c1: `PlyCin("1666")`, `BagRem(20403)`, 0x44a7d0(3) → `GoZone(2, 3)`;
  NI entry 3 sets byte 10303 = 1; timer 1 with byte 10432 ≥ 11 and byte 10303 = 1: float
  90005 = 100.0 (0x42c80000), `PlyCin(1539)`, 0x437750(1).
- **Evidence:** decompiles 0x445c80, 0x445720, 0x44a840, 0x4497b0; disassembly at 0x4447a5.
- **Method:** decompiles, disassembly.
- **Confidence:** proven

### E-0073 — AS's entry into NI reads byte 90009 and dword 90013 (corrects E-0056's as.md wording) (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x44a7d0(0): byte 0x15f99 (90009) = 0 → `GoZone(2, 0)`; else
  `GoZone(VarGetDwrd(0x15f9d = 90013), 10)` (0x4061e0 is `aVar::VarGetDwrd`). NI's resume
  entry 10 reads byte 90017, dword 90021, byte 90025. Float 90005 is NI's score
  (`VarSetFloa` 0x406230). `games/ring/docs/as.md` says "dwords 90005..90008 hold the zone"
  and "dword 90005.."; for NI the zone is dword 90013 and 90005 is a float.
- **Evidence:** `engines/ring/notes/decomp/as/RING_DVD.EXE__FUN_0044a7d0.c`,
  `RING_DVD.EXE__FUN_004061e0.c`; NI decompiles.
- **Method:** decompiles.
- **Confidence:** proven for NI; the other worlds' entries (0x436270, 0x443710, 0x43ad00) not
  re-read here.

### E-0091 — AS's world entries: bytes 90009..90012, dwords 90013..90016 (supersedes E-0056's wording, with E-0073) (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x44a7d0 / 0x436270 / 0x443710 / 0x43ad00 (argument 0):
  byte 0x15f99 / 0x15f9a / 0x15f9b / 0x15f9c is 0 → `GoZone(2 / 8 / 4 / 6, 0)`; else
  `GoZone(VarGetDwrd(0x15f9d / 0x15f9e / 0x15f9f / 0x15fa0), 10)`.
- **Evidence:** `engines/ring/notes/decomp/as/` (the four functions); `games/ring/docs/as.md`
  "Variables" and the 80019 handler corrected.
- **Method:** decompiles.
- **Confidence:** proven


### E-0060 — The inventory (`aList`, app+0x8d): fields, set-up, pictures, hot spots (DVD)
- **Binary/file:** `RING_DVD.EXE` constructor 0x416d70; `aApplication::Init` 0x408920..0x408a38
  (0x417d20(0, 0), 0x417d40(18, 42, 44, 100), 0x417d60(0, 0), 0x417dd0(6), 0x417d80(0, 24,
  30, 448), 0x417da0(610, 24, 30, 448), 0x4192a0(7, 48), 0x4192c0(627, 48), 0x417de0(335,
  8), 0x419280(500); `aList::openImage` 0x417440 with "bagbgr.tga", "bagarr.tga" (×2),
  "menu_gur.tga" and the fixed "erda_gun.tga" / "erda_gur.tga", folder "LIST\"); setters
  disassembled (capstone, 0x417d40/0x417d80/0x417da0 are not functions in Ghidra); hot
  spots 0x4178c0; `SetZone` 0x402210 → 0x417cc0 / 0x417cf0 (Erda on / off).
- **Evidence:** `engines/ring/notes/decomp/bag/` (`FUN_00416d70`, `aList__openImage`,
  `FUN_004178c0`, `aApplication__SetZone`); the pictures are members `\list\*.tga` of the
  language `SY.AT2` (`bagbgr` 640×87, `bagarr` 6×6, `menu_gur` 52×16, `erda_gu?` 52×40, read
  with `tools/parsers/at2.py` + `tgc.py`). Written up in `spec/bag.md` "Fields", "Hot spots".
- **Method:** decompiles, disassembly, corpus.
- **Confidence:** proven

### E-0061 — Inventory contents: add, remove, remove all, is in (DVD)
- **Binary/file:** `RING_DVD.EXE` `BagAdd` 0x406330, `BagRem` 0x4063e0, `BagRemAll`
  0x406470, `BagIsIn` 0x4064a0; `aList::add` 0x417e80 (returns at once when 0x4184d0 finds
  the object; inserts object and item at index 0; icon "%s%s%s.tga" with "LSTICON\",
  "\LSTICON\%s.tga" for the archive, "dummy.tga"; count +0x2c, scroll +0x28 = 0 when count >
  +0x24), 0x4181c0 (remove; scroll 0 when count ≤ +0x24), 0x418360, 0x4184d0;
  `ObjAddBagAni` 0x402ed0; `aAnimation::Alloc` 0x421d10 (image kind switch at 0x421d82:
  1, 2 `ANI`, 3 `CURSOR`, 4 `LSTICON`).
- **Evidence:** decompiles in `engines/ring/notes/decomp/bag/`; `SY.AT2` holds
  `\lsticon\<icon>.tga` and `\lsticon\<icon>\<icon>.NNNN.tga` (74 folders/files families,
  1,434 members); the zones' `ObjAddBagAni` arguments from `engines/ring/notes/zones/*.md`.
  Answers Q-0022 (another agent's): a second `BagAdd` of the same object does nothing.
- **Method:** decompiles, corpus.
- **Confidence:** proven (the meaning of `ObjAddBagAni`'s second and third arguments: Q-0013)

### E-0062 — Opening and closing the inventory; drawing it (DVD)
- **Binary/file:** `RING_DVD.EXE` window procedure 0x40eec0 (`WM_RBUTTONUP` → 0x40afe0 at
  0x40f1ef); 0x40afe0, show 0x4192e0, hide 0x419350 (→ 0x417e00), 0x40de90 / 0x40ded0
  (0x4103c0 writes rotation +0x67); draw 0x418ca0 from `RenderFrame` 0x40ed20 (after puzzle
  1, before 0x409520 / 0x408dd0 / 0x427c70 / the cursor); `StartMenu` 0x40dc80 hides it at
  0x40dccd and 0x40de36 and drops the object in hand; 0x40b7b0 (sets app+0x66) is called
  only with 1, 2, 4 and a value loaded from a save (call-site scan), so mode 3 is unused.
- **Evidence:** decompiles `FUN_0040afe0`, `FUN_004192e0`, `FUN_00419350`, `FUN_0040de90`,
  `FUN_0040ded0`, `FUN_00418ca0`, `RenderFrame`, `aApplication__StartMenu`, `WndProc` in
  `engines/ring/notes/decomp/bag/`; capstone for 0x4103c0. `spec/bag.md` "Opening and
  closing", "Drawing".
- **Method:** decompiles, disassembly.
- **Confidence:** proven

### E-0063 — Inventory tracking and clicks; Erda (DVD)
- **Binary/file:** `RING_DVD.EXE` tracking 0x408dd0 (bag shown → 0x418a70 only; object in
  hand → cursor 2 on accessibilities, 1 on nothing); 0x418a70 (arrows scroll with the 500 ms
  repeat, menu flag 0x4a1928, slot → the name text 0x42c550 / 0x414df0 at y +0x59 = 90,
  Erda flag 0x4a1929); `MouseLeftEvent` 0x409d90 (bag shown → 0x418520; on 1: event
  0x40c1f0, hide, app+0x77 / app+0x78, 0x40b860, `SetCursorPos(320, 240)`);
  `aList::checkClickOnListHotSpots` 0x418520 (Erda: `LoadSaveTimer("alb" / "sie" / "log" /
  "bru", 2)`, `VarSetDwrd` 0x4061b0 and `VarSetByte` on 90009..90028, 0x437750(13)); the
  window procedure passes the raw window position while the bag is shown; app+0x77 is only
  ever set to 1 and app+0x78 cleared only by FO's 0x441d50 (byte-store scan of `.text`).
- **Evidence:** decompiles in `engines/ring/notes/decomp/bag/` (`FUN_00408dd0`,
  `FUN_00418a70`, `aList__checkClickOnListHotSpots`, `aApplication__MouseLeftEvent`,
  `FUN_0040c1f0`, `FUN_00441d50`); strings at 0x487388 "alb", 0x487340 "sie", 0x4872f8
  "log", 0x4872b0 "bru". `spec/bag.md` "Tracking", "Clicking".
- **Method:** decompiles, disassembly scan.
- **Confidence:** proven

### E-0064 — The object in hand: cursors, dropping, using, taking (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x406530 / 0x406550 / 0x406570 (bag +0x95,
  `DeleteTypeDelete(2)`); 0x40b860 (`CurAdd(1, "%s_p" or icon, …, 2, …)`, `CurAdd(2, "%s_a"
  or icon, …)` from object +0x15.. / +0x32.., `CurSetOffset` 0x402860); `MouseLeftEvent`:
  object click 0x40bbb0 without a drop, flag-8 event 0x40bed0 then (app+0x74) drop +
  `aList2::SetObjectClicked` 0x4191f0 + 0x40b860, app+0x75 drop after the "movability
  done" event (0x40af60); app+0x74 cleared by WA (0x43932e..0x439f30) and RH
  (0x443c49..0x443e1d), app+0x75 never (byte-store scan).
- **Evidence:** decompiles in `engines/ring/notes/decomp/bag/`; the zones' `ObjSetPasCur` /
  `ObjSetActCur` arguments (`engines/ring/notes/zones/*.md`), `SY.AT2` members
  `\cursor\<icon>_p.tga`. `spec/bag.md` "The object in hand".
- **Method:** decompiles, disassembly scan, corpus.
- **Confidence:** proven

### E-0065 — Opening the inventory writes rotation +0x67 (refines E-0046)
- **Binary/file:** `RING_DVD.EXE` 0x4103c0 `mov byte [ecx+0x67], (arg != 0)`, called by
  0x40de90 (1, bag opened) and 0x40ded0 (0, bag closed).
- **Evidence:** disassembly. E-0046 listed the save loader's stores (0x40d34d / 0x40d359) as
  the only writes of +0x67; this setter is another. Q-0012 (the value before either) stays
  open.
- **Method:** disassembly.
- **Confidence:** proven

### E-0092 — Pausing an animation on a frame (`ObjPrePauFraAni`) (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x403ac0, `aObject::ObjPrePauFraAni` 0x420e50, 0x42f150
  (both animation lists), `aAnimation::PauseExactOnFrame` 0x416af0 (+0x42, +0x46, +0x4a = 1,
  the direction choice), 0x416720 (the +0x4a branch), 0x416870 (+0x60 = 1 on a step),
  0x416c90 (+0x14 = +0x18, +0x4a = 0, +0x60 = 0, 0x40c910(2)), 0x40c910 (only RO's
  0x43a6f0, `spec/events.md`).
- **Evidence:** `engines/ring/notes/decomp/pausefra/`, `layers/RING_DVD.EXE__FUN_00416720.c`,
  `layers/RING_DVD.EXE__FUN_00416870.c`; `spec/animation.md` "Pausing on a frame". NI uses
  it for Glug and the speaker (`games/ring/docs/ni.md`).
- **Method:** decompiles.
- **Confidence:** proven; the other controls of 0x416720 (+0x28, +0x32) stay unspecified.

### E-0093 — `LoadSaveTimer` keeps the timers, the bag and the playing sounds (DVD)
- **Binary/file:** `RING_DVD.EXE` `aApplication::LoadSaveTimer` 0x40d4b0: the path
  `%s%s\%s\%s.ars` (install prefix 0x402480), mode 1 reads / otherwise writes
  (0x4295e0's access flags), then `aTimer::LoadSave(file, mode, GetTickCount(), 1)`,
  `aList::LoadSave(file, mode)` (the bag, app+0x8d) and 0x469790(file, mode, tick, 0) (the
  sounds); nothing else.
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__aApplication__LoadSaveTimer.c`;
  `spec/bag.md` (Erda).
- **Method:** decompile.
- **Confidence:** proven for what is written; the record layouts are not read here.

### E-0094 — The zone set-ups' loops, unrolled by emulation (corrects the call lists of E-0028..) (DVD)
- **Binary/file:** `RING_DVD.EXE` zone set-ups (SY 0x4662a0, NI 0x45eb30, RH 0x455a50, FO
  0x44f3e0, RO 0x458a90, WA 0x44ab00, AS 0x4635a0, N2 0x45b610) contain 24 counted loops
  around `sprintf` 0x46f069 (e.g. NI 0x46101a: `mov ebx, 0xd`, i = 0..12,
  `sprintf(buf, "NIS01N01P02S01.%04d.bmp", i + 1)`, `ObjAddPre(10103)`,
  `ObjPreAddImgToPuz(10103, i, 10100, buf, 504, 194, 1, 1, 1000)`, `dec ebx; jne`); the
  static extraction (ring_calls.py) recorded one iteration with unknown arguments.
- **Evidence:** `engines/ring/tools/ringemu.py` runs each set-up in Unicorn with every callee
  of the static list stubbed (arguments read from the stack, the callee's purge applied;
  `sprintf` formatted): its `--selftest` finds every fully resolved static call, with the
  same arguments and in order, among the emulated ones. Calls: SY 285, NI 1142 (static
  646), RH 415, FO 1021 (923), RO 1607 (392), WA 1120 (617), AS 373, N2 581 (473); the
  static "?" arguments (e.g. `SouAdd`'s fourth and sixth) are now known.
- **Method:** emulation of the original code, checked against the static extraction.
- **Confidence:** proven for the paths the set-ups take (they have no data-dependent branches
  outside the loops).

### E-0095 — The juggle effect (DVD)
- **Binary/file:** `RING_DVD.EXE` `RotSetJugOn` 0x405c70 (+0x66 = 1, +0x39, +0x41),
  0x40f990 (defaults: +0x39 = 30.0), 0x410410 (first load: +0x31 = 0, tick 0x495708, the
  weight table 0x49d7b8..0x49f7b8, 32 floats per 0x100-byte row, `rand()` × +0x39 ×
  [0x47e310] = 1/32767), 0x410610 (0x49d7b4 = (tick − 0x4a17b8) × 0.001; +0x31 += it below
  1.0, then 1.0 at 0x4107ab), 0x40f9e0 (0x40ffb3..0x410065: for rows 0..[0x49d738] and
  columns 0..[0x49d73c], `sin(t × +0x41 × 1.05)` [0x47e2ac] and `cos(t × +0x41 × 0.95 + w)`
  [0x47e2a8], × +0x31 × w, ×65536 [0x47e330] to int (0x410900), added to the grid's u
  (0x495718) and v (0x499718) entries (0x410920)), 0x410361 (+0x31 during a turn).
- **Evidence:** disassembly and `engines/ring/notes/decomp/juggle/`; the set-ups call it
  twice: `RotSetJugOn(10406, 10, 1)` (NI's water) and `RotSetJugOn(20701, 10, 1)`.
- **Method:** disassembly, decompiles.
- **Confidence:** proven; the wave (+0x65) is not traced (no set-up enables it).

### E-0100 — Zone RH: entries, object clicks, movabilities, timer, animation and sound handlers (DVD)
- **Binary/file:** `RING_DVD.EXE` `GameSetZoneRH` 0x445740 (entries 0, 10, 999), object click
  0x443990, before / after a movability 0x444b40 / 0x444ba0, timer 0x444d30, animation
  0x444dc0, sound 0x444e60; "on a movability" 0x44a1b0 and "on nothing" 0x442e30 are empty;
  no button-down, drag, on-accessibility, take or list handler (`spec/events.md`). Video
  names from the `DAT_0048de44..0048df90` strings (1666..1706), `rh_%d` 0x48df88 and
  `rh_%d_l0` 0x48df74 with byte 21001 + 1 (`inc` at 0x444f56 / 0x445039; the files are
  `RH_1..3.CNM`, `RH_1..3_L0.CNM`); score constants f32 [0x47e314] 1, [0x47e624] 2,
  [0x47e620] 3, [0x47e2e0] 5 (`fadd dword` at 0x443b23.., 0x444781). 0x444b40 calls
  0x4065e0 (`TimSto(0)`), 0x444ba0 0x4065a0 (`TimSta(0, 0x32)`); 0x444ba0's three
  `to` tests are independent (`cmp edi, 0x4e2a / 0x4e34 / 0x4e3e`, each falling through).
- **Evidence:** as written in `games/ring/docs/rh.md`; decompiles in
  `engines/ring/notes/decomp/rh/`; the set-up `engines/ring/notes/zones/rh.md`.
- **Method:** decompiles, disassembly (capstone), strings from the EXE.
- **Confidence:** proven for the handlers.

### E-0101 — RH ends by entering NI at 3 (corrects `ni.md`'s caller of 0x44a7d0(3)) (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x4447c1 `call 0x44a7d0` with 3 lies in RH's object-click
  handler 0x443990 (the Rhine Gold, object 20700, after `PlyCin(1666)` and `BagRem(20403)`
  at 0x4447b8), not in FO. `games/ring/docs/ni.md` ("Entering", entry 3) names FO as its
  caller; NI's entry 3 is the return from RH (byte 10303 "back from FO" is set by it).
- **Evidence:** disassembly 0x444750..0x4447dd; `engines/ring/notes/decomp/rh/RING_DVD.EXE__FUN_00443990.c`.
- **Method:** disassembly.
- **Confidence:** proven

### E-0102 — RH's entry 10 reads NI's world record "alb" (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x445740 entry 10: `%sData\Save\alb.ars` (0x48e00c) tested
  with 0x47bd10, SY's byte 90017, dword 90021, byte 90025 (world 1), `LoadSaveTimer` with
  "alb" (0x487388), then 0x4696f0.
- **Evidence:** `engines/ring/notes/decomp/rh/RING_DVD.EXE__aApplication__GameSetZoneRH.c`;
  `spec/bag.md` (Erda's file per zone).
- **Method:** decompile.
- **Confidence:** proven

### E-0103 — RH's statue head follows the view: timer 0 and `ObjPreAniSetActFra` (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x444d30: `RotGetAlp(20401)` (0x405ab0: stored alpha +
  135.0 [0x47e280], less 360.0 [0x47e27c] above it) `fsub dword [0x47e698]` (35.0), `__ftol`;
  0 < a < 0x92; `fmul qword [0x47e690]` (0.263157… = 5/19), `__ftol`; 1..0x1c and ≠
  [0x4a1cdc]: 0x4039b0(20401, 0, f). `ObjPreAniSetActFra` 0x4039b0 → `aObject` 0x420ce0 →
  0x42efd0 (both animation lists of the presentation) → `aAnimation::SetActiveFrame`
  0x416aa0 (+0x22 = f − 1 for 1 ≤ f ≤ frames, else logged).
- **Evidence:** disassembly (capstone); `engines/ring/notes/decomp/rh/`.
- **Method:** disassembly, decompiles.
- **Confidence:** proven

### E-0104 — RH's click handler clears app+0x74 for Disgust and the goldfish (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x443990: `mov byte [this+0x74], 0` on the 20201 paths
  (in hand; `unk_19` 1 with byte 20202 ≠ 0; the default LAB_00443c49) and on 20007 with an
  object in hand; the 20004..20006 handler and 20007 `unk_19` 0 and 20201's first taking
  leave it set, so those objects (flags 9) also go in hand (`spec/bag.md` "Taking").
- **Evidence:** `engines/ring/notes/decomp/rh/RING_DVD.EXE__FUN_00443990.c`; set-up flags in
  `engines/ring/notes/zones/rh.md` (`AddObj(..., 9)`).
- **Method:** decompile.
- **Confidence:** proven

### E-0130 — Zone N2: entries, handlers and set-up (DVD)
- **Binary/file:** `RING_DVD.EXE` `GameSetZoneN2` 0x4362c0 (entries 0, 10, 999), AS's entry
  0x436270, object click 0x4341e0, button down 0x434740, drag 0x4349b0, before / after a
  movability 0x435390 / 0x435410, timer 0x435470, animation 0x4354b0, on an accessibility
  0x435970, sound 0x435a00, helpers 0x433ee0 (the test's start), 0x433fa0 / 0x4340c0 (the
  heater off / on), 0x43d8f0 (`GoZone(5, 0)`); wrappers 0x404a50 / 0x404a60 (a puzzle's
  movabilities on / off), 0x405830, 0x403030 / 0x403050 / 0x403070, 0x406130 / 0x406160
  (`VarSetWord` / `VarGetWord`), 0x4062e0 (`VarGetStrg`), `PuzSet3DSouVol` 0x404d70. Video
  names from the pushed `DAT_0048d7..` strings (capstone): 1389, 1494..1508.
- **Evidence:** as written in `games/ring/docs/n2.md`; decompiles in
  `engines/ring/notes/decomp/n2/`; the set-up in `engines/ring/notes/zones/n2.md` (E-0094).
- **Method:** decompiles, disassembly.
- **Confidence:** proven for the handlers as described.

### E-0131 — N2's cross: NI's code without the dam base, writing NI's byte 10104 (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x4349b0, case 0x111da (70106): the start (0x4066b0(243,
  276), `DAT_004a1c78` = sector − word 70016) and move are NI's 10106 code without the base
  or 0x445930; the release (0x434f5a) stores word 70016 and `VarSetByte(0x2778, 0 / 1)`:
  0x2778 = 10104, NI's "cross at 12" byte, then toggles rotation 70101's movabilities 1 / 2.
- **Evidence:** `engines/ring/notes/decomp/n2/RING_DVD.EXE__FUN_004349b0.c`.
- **Method:** decompile.
- **Confidence:** proven (the write to NI's variable is the code as shipped).

### E-0132 — N2 ends by `GoZone(5, 0)` with score 50 (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x435a00, sound 0x11173 (70003) ended: `PlyCin("1504")`,
  `PlyCin("1505")`, `TimStoAll`, 0x406ea0(0x400), `VarSetFloa(0x15f96, 0x42480000)` (90006
  = 50.0), 0x43d8f0(0) → `GoZone(5, 0)` (RO). N2's score is float 90006 (every score
  change in 0x4341e0 / 0x4349b0 uses 0x15f96).
- **Evidence:** the decompiles above.
- **Method:** decompile.
- **Confidence:** proven

### E-0133 — Alberich's test: rounds, videos, sounds (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x4341e0 (the creature given: byte 0x1117f = (char)held −
  100, play(0x11562 + it)), 0x435a00 (0x11559 / 0x1155a..b: `sprintf("N2_%dA", byte
  0x1117e)`; 0x11562..0x11564: `sprintf("N2_%d%c", byte 0x1117e, byte 0x1117f + 0x43)`
  (disassembly 0x435fe1..0x436007), play(byte 0x1117f + (byte 0x1117e + 0x1bc5) × 10);
  0x115bc..0x115d9: the round tests and game over 2 (0x4360a9)). Videos `N2_1A`..`N2_3E`
  exist in `DATA\N2\PLA`.
- **Evidence:** the decompiles above; directory listing.
- **Method:** decompile, disassembly.
- **Confidence:** proven

### E-0160 — Zone FO: entries, world entry and resume (DVD)
- **Binary/file:** `RING_DVD.EXE` `GameSetZoneFO` 0x443760 (entries 0, 10, 999; 10 reads
  `%sData\Save\sie.ars`, bytes 0x15fa3 = 90019, 0x15fab = 90027, dword 0x15fa7 = 90023,
  `LoadSaveTimer("sie", 1)`), AS's world entry 0x443710 (byte 0x15f9b = 90011, dword
  0x15f9f = 90015); video names from the `DAT_0048dd..` strings (1217, 1218).
- **Evidence:** `games/ring/docs/fo.md` "Entering"; decompiles `engines/ring/notes/decomp/fo/`.
- **Method:** decompiles, strings read from the EXE.
- **Confidence:** proven

### E-0161 — Zone FO: object clicks (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x43dac0 (switch on the object; the shared tails
  0x43e058 (scroll order), 0x43ed58 (pedestals solved), 0x43edfe (drop)); score constants
  f64 [0x47e640] 100, [0x47e648] 2.2, [0x47e650] 9.9, [0x47e658] 4.4, [0x47e660] 1.1,
  [0x47e668] 6.6, [0x47e670] 3.3, [0x47e678] 5.5, [0x47e680] 4.0 added to SY's float 90007
  (0x406260 / 0x406230); 0x405820 = `RotSetMovOnOrOff(rotation, 0)`, 0x404a70 / 0x404a90 =
  `PuzSetMovOnOrOff(puzzle, 1 / 0, from, to)`, 0x406e60 the type volume.
- **Evidence:** `games/ring/docs/fo.md` "Object click", "The end".
- **Method:** decompile, constants read from the EXE.
- **Confidence:** proven

### E-0162 — Zone FO: the dial drag and the drag getters (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x441890 (phase 1: 0x406660(2), play(30500, 2),
  0x4066b0(0x1b8, 0xf8); phase 2: stop(30500, 0x400); phase 3: the four quadrant tests,
  byte 30016 ± 1 wrapping 0..48, then volume(30500, trunc(0x4068b0 + [0x47e688] 80.0)));
  getters 0x406870 (ref x < cur x), 0x406830 (ref y < cur y), 0x406770 (prev x < cur x),
  0x406730 (cur x < prev x), 0x406710 (prev y < cur y), 0x4066d0 (cur y < prev y), 0x4068b0 →
  0x4261c0 (√ of 0x426180² + 0x4261a0², |cur − prev| in x and y).
- **Evidence:** `engines/ring/notes/decomp/fo/`; disassembly at 0x441cf1..0x441d04.
- **Method:** decompiles, disassembly.
- **Confidence:** proven

### E-0163 — Zone FO: the bag click (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x441d50: the place = 0x402720 (current puzzle, app+0x81)
  when 0x402700, else 0x402730 (current rotation) when 0x402710; object 30019 only; each
  handled case writes app+0x78 = 0; `RotGetAlp` 0x405ab0, `RotGetBet` 0x405b40, `RotGetRan`
  0x405bb0.
- **Evidence:** `games/ring/docs/fo.md` "Bag click".
- **Method:** decompile.
- **Confidence:** proven

### E-0164 — Zone FO: before and after a movability (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x4420b0 (from, to, index, `unk_19`, kind), 0x442580 (to,
  from, …, kind); `RotSetMovRidNam` 0x405870 (rotation, index, name →
  `aMovability::SetRideName`), the name "fom" at 0x48dd58.
- **Evidence:** `games/ring/docs/fo.md`.
- **Method:** decompiles.
- **Confidence:** proven

### E-0165 — Zone FO: timers, animations, sounds and the ending (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x442810 (timers 0..5), 0x442b60 (animation ids 30000,
  30001, 30006, 30007, 30008; 30002..30005 assigned nowhere in the set-up), 0x442e40 (sound
  ends; 30120..30136 with SY's object 6 and 0x437750(3)); animation ids from the set-up
  (`ObjPreSetAniIdeOn*`: 30025/0 → 30006, 30040/4 → 30008, 30045/7 → 30000, 30050/1 →
  30009, 30109/0 → 30007, 30110/1 → 30001; 30110/1 has 200 frames, 30109/0 202).
- **Evidence:** `games/ring/docs/fo.md`; `engines/ring/notes/zones/fo.md`, `sy.md` (object 6).
- **Method:** decompiles, the emulated set-up (E-0094).
- **Confidence:** proven

### E-0166 — Zone FO: button down and take do nothing; no game over (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x441860 (object 30016: reads 0x406530 / 0x406550,
  nothing else); every `AddObj` of the FO set-up has flags 1 except 30016 (4), so neither
  0x40bd40 (flag 2) nor 0x40bed0 (flag 8) is raised; the FO handlers call no 0x408db0.
- **Evidence:** the decompiles' call lists, `engines/ring/notes/zones/fo.md`.
- **Method:** decompiles, set-up listing.
- **Confidence:** proven

### E-0220 — WA's entries and AS's way in (DVD)
- **Binary/file:** `RING_DVD.EXE` `aApplication::GameSetZoneWA` 0x43ad50 (entries 0, 10 with
  `%sData\Save\bru.ars` 0x48dab8 and `LoadSaveTimer("bru", 1)`, 999), 0x43ad00 (byte 90012,
  dword 90016), the zone switch 0x40d220 (case 6); videos `1880` 0x48da3c, `1881` 0x48da34.
- **Evidence:** `engines/ring/notes/decomp/wa/`; `games/ring/docs/wa.md` "Entering".
- **Method:** decompiles; strings read from the EXE.
- **Confidence:** proven

### E-0221 — WA's object click handler (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x437d60 (objects 50100, 50105, 50202, 50203, 50300,
  50301, 50302, 50400, 50402, 50501..50503, 50600, 50601, 50700); the progress block (byte
  50012, 50700's presentations and accessibilities, rotation 50103's movabilities 2 / 3);
  videos 1849..1864 (0x48d93c..0x48d9b4); score float 90008 (0x15f98) with f32 constants
  [0x47e314] 1, [0x47e624] 2, [0x47e620] 3, [0x47e2e0] 5, the ending's 0x42c80000 = 100.0.
- **Evidence:** `engines/ring/notes/decomp/wa/RING_DVD.EXE__FUN_00437d60.c`; `wa.md` "Object click".
- **Method:** decompile.
- **Confidence:** proven

### E-0222 — WA's take handler: the desk, the golem's parts, the grid (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x4392a0 (objects 50101..50104, 50431..50437, 50451..50457,
  50499; app+0x74 cleared on every path but the takings; dword 50000 sums 7654321 / 654321;
  the grid's cells `ObjPreSetImgCooOnPuz` 0x4037c0 → 0x42eba0 with x = 53 × (v / 10) + 162,
  y = 37 × (v % 10) + 115, dwords 51000 + v, the right cells 51030, 51061, 51001, 51033,
  51026, 51046, 51042 for 50451..50457; `ObjPreSetImgOriCooOnPuz` 0x403810 → 0x42ebf0 (the
  handle's +0x55 / +0x59 = +0x5d / +0x61); videos 1865..1867).
- **Evidence:** `engines/ring/notes/decomp/wa/RING_DVD.EXE__FUN_004392a0.c` and the
  `ObjPreSetImg*` decompiles; `wa.md` "Take".
- **Method:** decompiles.
- **Confidence:** proven

### E-0223 — WA's movability handlers: the music by area (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x439f40 (before), 0x43a050 (after; the leaf's second way);
  videos 1868..1871.
- **Evidence:** `engines/ring/notes/decomp/wa/`; `wa.md` "Before / After a movability".
- **Method:** decompiles.
- **Confidence:** proven

### E-0224 — The hold-on-frame event 0x40c910 goes to WA, not RO (supersedes part of E-0092) (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x40c910: id 1 goes to the empty default 0x44a110; any
  other id, by the zone (0x402450): case 6 (WA) → 0x43a6f0(phase, id), every other zone the
  empty default. E-0092 / `spec/animation.md` said "only RO handles it"; `spec/events.md`'s
  table already shows WA. WA's 0x43a6f0: id 50004 phase 2, id 50003 phases 1 and 2; video
  `1872` 0x48d9f4.
- **Evidence:** `engines/ring/notes/decomp/wa/RING_DVD.EXE__FUN_0040c910.c`,
  `RING_DVD.EXE__FUN_0043a6f0.c`; `wa.md` "Hold on a frame".
- **Method:** decompiles.
- **Confidence:** proven

### E-0225 — WA's animation and sound handlers; the ending to AS (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x43a400 (animation 50001: the switches' pairs and frames),
  0x43a860 (sound chains 50001..50003, 50009..50016, 50021..50036; `PlyCinMul` videos
  1873..1878 by language, 1879; then `TimStoAll`, 0x406ea0(0x400), 0x437750(4)).
- **Evidence:** `engines/ring/notes/decomp/wa/`; `wa.md` "Animation", "Sound", "Flow".
- **Method:** decompiles.
- **Confidence:** proven

### E-0190 — Zone RO: set-up, entries, places and objects (DVD)
- **Binary/file:** `RING_DVD.EXE` set-up 0x458a90 (`engines/ring/notes/zones/ro.md`, emulated,
  E-0094), `GameSetZoneRO` 0x43d910 (entry 0: alpha 0, ran 85.3, `BagRem(70000)`,
  `PlyCin("1506")` 0x48db9c, `BagAdd` 40000, 0x9c4c, 0x9c4d, `PuzSetAct(0x9ca4)`,
  play(0x9efc); entry 10: `%sData\Save\log.ars`, bytes 0x15fa2 / 0x15faa, dword 0x15fa6,
  `LoadSaveTimer("log", 1)`), 0x43d8f0 (`GoZone(5, 0)`, called by N2, E-0132).
- **Evidence:** `engines/ring/notes/decomp/ro/`; `games/ring/docs/ro.md` "Places",
  "Variables", "Objects", "Entering".
- **Method:** decompiles, set-up call list.
- **Confidence:** proven

### E-0191 — Zone RO: object click, button down, the tiles, the pipes, the keyboard (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x43afa0 (40010, 40011 cells with bytes 0x9e35 + c, the
  neighbours 0x9e2b / 0x9e3f / 0x9e34 / 0x9e36 + c, step byte 0x9f65, the solution test over
  0x9e4a..0x9e71, the 2000-move shuffle; 40201 with 0x4a1cc0 / 10, `"%d"` 0x4823e0, string
  0x9fc5), 0x43b9a0 (40202: play(0x9e34 + k), `"%1d"` 0x48db14 of k − 7, string 0x9fc6, the
  codes 0x48db08 / 0x48dafc / 0x48daf0 / 0x48dae4), the score writes `VarSetFloa(0x15f96)`
  with f32 0x424f3333 (51.8), 0x4280999a (64.3), 0x42960000 (75.0), 0x429d3333 (78.6),
  0x42ab6666 (85.7), 0x42c80000 (100.0); videos 0x48dacc "1780", 0x48dad4 "1781", 0x48dadc
  "1782", 0x48db20 "1783", 0x48db18 "1784"; `VarSetStrg` 0x4062b0 → `aVar::VarSetStrg`
  0x4255b0.
- **Evidence:** `engines/ring/notes/decomp/ro/RING_DVD.EXE__FUN_0043afa0.c`, `…0043b9a0.c`;
  disassembly at 0x43afca (the `"%d"` argument is `unk_19`) and 0x43ba29 (k − 7).
- **Method:** decompiles, disassembly, strings read from the EXE.
- **Confidence:** proven

### E-0192 — Zone RO: drags, timers, movabilities, animations (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x43bbf0 (lever 0x9c7c: limit (0, 0)–(640, 480), max 0x47,
  |dx| × f64 [0x47e630] = 1/6, release rounding with f32 [0x47e638] = 0.1; dials 0x9ca5 +
  `unk_19`: max 0x61, wrap, the solution bytes 0x9e99..0x9e9d = 10, 90, 60, 50, 50 or 40,
  videos 0x48db20 / 0x48db18), drag getters 0x406890 / 0x4068a0 (0x426180 / 0x4261a0),
  0x406730 / 0x406770 / 0x406710 / 0x4066d0; 0x43c500 (timers 0, 1: bytes 0x9f66 / 0x9f67
  to 10 / 90); 0x43c290 (before: kind 2, from 0x9c7c or to 0x9c45; "1785" 0x48db34;
  `"00000000"` 0x48db28); 0x43c450 (after); 0x43c5e0 (ids 0x9ca4..0x9caa frames 1, 0x1e,
  0x46; `"6543210"` 0x48db44, `"0000000"` 0x48db3c; ids 0x9d09..0x9d0f, bytes 0x9fc5..0x9fcb
  = 0x1a, 0x9fcf..0x9fd5 = 0x46); `PuzSetMovOnOrOff` wrappers 0x404a70 (on) / 0x404a90
  (off).
- **Evidence:** `engines/ring/notes/decomp/ro/`; disassembly of 0x43bbf0's `__ftol` inputs.
- **Method:** decompiles, disassembly.
- **Confidence:** proven

### E-0193 — Zone RO: sounds and the end; RO leads back to AS (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x43d4a0: chains 0x9efc → 0x9efd, 0x9f02..0x9f07 →
  0x9efe → 0x9eff → 0x9f00; 0x9f00: stop all 0x400, "1788" 0x48db84, `RotSet3DSouOff`,
  `RotSetAmbSouOff` / `RotSetAmbSouOn` 0x405de0 / `PuzSetAmbSouOn` 0x404b90 (0x9e9c),
  `RotSetMovRidNam` 0x405870 (`ro0102` 0x48db7c … `1796` 0x48db54, `ro0502` 0x48db4c);
  0x9dd0: "1787" 0x48db8c; 0x9e9b: stop(0x9c43), `TimStoAll`, "1786" 0x48db94,
  0x437750(2). No call to 0x408db0 in 0x43afa0..0x43d910.
- **Evidence:** `engines/ring/notes/decomp/ro/RING_DVD.EXE__FUN_0043d4a0.c`,
  `RING_DVD.EXE__RotSetMovRidNam.c`. `spec/events.md` lists the pause event 0x40c910's only
  handler (0x43a6f0) under WA, not RO.
- **Method:** decompiles, strings read from the EXE.
- **Confidence:** proven

### E-0096 — The credits: `ScrollImage` (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x431350 (the credits: stop all, `SetZone(6)`, play(51002,
  2), `SetZone(1)`, `ScrollImage` of `cre_01.bma` .. `cre_10.bma` with 0 and `cre_11.bma` with
  5000, kind 2, load-from 0x65 'e', stopping at a return of 2, stop(51002)),
  `aApplication::ScrollImage` 0x401260 (Escape wait, path `%s%s\%s\%s\%s`, the loop to
  height − 0x1c0, `Display(img, 0, 0x10, 0x280, 0x1d0, 0, i)` at 0x4013d7..0x4013e9, the
  wait 0x402890(hold) after a full scroll, return 1 + escaped), 0x414c20 (GetDC, 0x413c10,
  ReleaseDC, the device's vtable +0x30), 0x413c10 (`StretchDIBits` from source row
  height − h − i of the bottom-up DIB: the window's top is row i).
- **Evidence:** `engines/ring/notes/decomp/credits/`; disassembly of the call; `bma.py --file`:
  `CRE_01.BMA` .. `CRE_11.BMA` 640 × 896.
- **Method:** decompiles, disassembly.
- **Confidence:** proven; the rate of the device's flip is not traced (Q-0080).

### E-0097 — Ride videos named by the set-ups but on no disc (DVD, CD, ISO)
- **Binary/file:** the movabilities' ride names in `engines/ring/notes/calls/*_setup.jsonl`
  (`RotAddMovToRot` / `RotAddMovToPuz` / `PuzAddMovTo*`) against every `.cnm` of the corpus
  (`games/ring/discs/**`).
- **Evidence:** absent everywhere: RH `1723`; FO `1232 1239 1241 1243 1245 1250 1256 1258
  1259 1262`; N2 `1377 1385`. `PlyCin` of a missing file logs and plays nothing (the ride
  is skipped, `spec/video.md`); the scripted play-throughs of worlds 2 and 3 pass these
  rides without them.
- **Method:** corpus scan.
- **Confidence:** proven for the corpus we have.


### E-0250 — Game save file: path, header, the ring.exe check (DVD)
- **Binary/file:** `RING_DVD.EXE` `aApplication::LoadSave` 0x40d6a0: `sprintf(buf,
  "%s%s\%s\%s.ars", install 0x402480, "DATA" 0x482070, "SAVE" 0x485cc0, name)` at
  0x40d6c8..0x40d6ec; open with access 0x80000000 for mode 1, else 0x40000000, which
  0x4295e0 turns into `CreateFileA(OPEN_EXISTING)` / `CREATE_ALWAYS`; `_stat` (0x47bf41) of
  `"%sring.exe"` (0x485f00); header 0x14 bytes = `"ArxSav 1.00"` (0x485ef4, copied with its
  NUL into a 12-byte buffer), `st_size`, `st_mtime`; load compares the string (error "CODE is
  not the same"), then size and time only when app+0x53 is set ("SIZE"/"MTIME is not the
  same"). app+0x53 is fl.ini's `CHECKLOADSAVE` (`aApplication::Init` 0x407b80, key string
  0x4858b0, stored after the key compare at 0x408428).
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__aApplication__LoadSave.c`,
  `…__FUN_004295e0.c`; `CHECKLOADSAVE: 1` in `games/ring/discs/dvd-edition/FL.INI`,
  `cd-version/disc6/FL.INI`, `iso-version/disc1/fl.ini`.
- **Method:** decompile, disassembly of the sprintf arguments, corpus.
- **Confidence:** proven.

### E-0251 — Game save body order, trailer, and entry 1000 (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x40d6a0 after the header: puzzles (app+0x7d,
  `aPuzzle::LoadSave` 0x41bb70), rotations (app+0x85, 0x41df30), objects (app+0x79,
  0x41fcd0), `aVar::LoadSave` (app+0x95), `aList::LoadSave` (app+0x8d), `aTimer::LoadSave`
  (app+0x91, tick, 1), then 0x1a bytes at 0x495348 (filled at 0x40db21..0x40dbe7 from
  app+0x66, +0x6a, +0x6e, 0x402700/0x402720, 0x402710/0x402730, 0x495570, app+0x5d, +0x54,
  (char)app+0x58), then on save 0x469790(file, mode, tick, 0) and close. On load: the trailer
  read, 0x40b7b0(mode) (`mov [ecx+0x66]`), app+0x6a, `GoZone(zone, 1000)` 0x402280, file left
  open. 0x40d220 (`GameSetZone`) with entry 1000: no zone dispatch; `PuzSetAct(id, 0, 1)`,
  `RotSetAct(id, 0, 1)` and rotation +0x67 from 0x495358, app+0x5d/+0x54/+0x58, 0x469790 with
  the load's mode, close, `aPreFer::Load`, 0x4696f0. The AS exception (zone 7 with puzzle
  80002..80010 or rotation 80101: no archive reopen, no CD check) in both 0x402280 and
  0x40d220. app+0x54 = 1 in `Init` (`aApplication::Init`, with app+0x58 = 0x65 and app+0x5d = 1).
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__aApplication__LoadSave.c`,
  `…__FUN_00402280.c`, `…__FUN_0040d220.c`, `…__FUN_0040b7b0.c`;
  `notes/decomp/bag/RING_DVD.EXE__aApplication__Init.c` (app+0x54, +0x58, +0x5d).
- **Method:** decompiles, data references to 0x49534e..0x49535e.
- **Confidence:** proven for the layout and the restore; the meaning of app+0x54 is open
  (Q-0091).

### E-0252 — Per-class save records (DVD)
- **Binary/file:** `RING_DVD.EXE` `aPuzzle::LoadSave` 0x41bb70 (image +4, movabilities +8,
  sound items +0x1c, visual objects +0x20 via virtual +0x20, 9 bytes +0x24/+0x28/+0x29);
  `aRotation::LoadSave` 0x41df30 (image +0x29, movabilities +0x10, per layer
  `aAnimation::LoadSave` + u32 via 0x4103f0/0x4103d0, sound items +0x24, 0x44 bytes +0x28,
  +0x31..+0x61, +0x65..+0x67, +0x68..+0x70); `aImageHandle::LoadSave` 0x42d480 (strings
  +0x4d, +0x51 if set; 13 bytes +0x55, +0x59, +0x65, +0x79, +0x7a, +0x70, +0x7b);
  `aMovability::LoadSave` 0x423470 (hot spot +8, string +0x10, 0x25 bytes);
  `aHotSpot::LoadSave` 0x4237c0 (0x21 bytes); `aAccesibility::LoadSave` 0x423120 (hot spot
  +4); `aSoundItem::LoadSave` 0x41a080 (+8, +0xc, +0x18); `aObject::LoadSave` 0x41fcd0 (0x74
  bytes +0x15..+0x88, accessibilities +0xd, presentations +0x11, `aAnimationImage` +0x89);
  `aObjectPresentation::LoadSave` 0x42e020 (images +5, animations +0xd, texts +0x29 and
  +0x31, u8 +4); `aText::LoadSave` 0x42c340 (string +0, 0x1d bytes +4..+0x1d);
  `aAnimation::LoadSave` 0x416070 (0xa1 bytes; times +0x28, +0x32, +0x4a converted when
  above the double 1.0 at 0x47e2a0, +0x4f unless 0); `aAnimationImage::LoadSave` 0x421930
  (animation, then +0x71, +0x75, +0x89); `aString` record 0x428be0 (u32 strlen + 1, bytes).
  Both visual object kinds have virtual +0x20 = 0x46efe0 (`mov al, 1; ret 0xc`; vtables
  0x47e8dc, 0x47e924).
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__a*__LoadSave.c`,
  `…__FUN_00428be0.c`; vtable dump and disassembly of 0x46efe0.
- **Method:** decompiles, disassembly.
- **Confidence:** proven for the layouts; several fields' meanings open (Q-0091).

### E-0253 — Variables, bag and timers in saves (DVD)
- **Binary/file:** `RING_DVD.EXE` `aVar::LoadSave` 0x424290 (u32 count + 5/6/8/8-byte
  entries for byte, word, dword, float lists via `aByte` 0x423980, `aWord` 0x423a70,
  `aDoubleWord` 0x423b20, `aFloat` 0x423be0; strings via `aVarString::LoadSave` 0x423d20:
  u32 id, u32 strlen + 1, bytes; load clears with 0x424860 and redefines with `VarDef*`);
  `aList::LoadSave` 0x4172a0 (u32 count, ids written from the last index down, u32 +0x95;
  load `add`s in file order); `aTimer::LoadSave` 0x425910 (u32 count, 16 bytes per timer:
  +0 id 0x423a10, tick − +4 0x423bb0, +8 0x425740, +0xc 0x423660; load `StartTimer(id,
  period)` when the last argument is set, then 0x423c70(tick − elapsed), 0x425750).
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__aVar__LoadSave.c`, `…aByte…`,
  `…aWord…`, `…aDoubleWord…`, `…aFloat…`, `…aVarString…`, `…aList__LoadSave.c`,
  `…aTimer__LoadSave.c`; disassembly of the timer getters.
- **Method:** decompiles, disassembly.
- **Confidence:** proven.

### E-0254 — Sounds in saves (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x469790(file, mode, tick, keep): f32 at 0x4932a8 (1.0);
  per sound of 0x4a1cfc (count 0x4a1cf4) 12 bytes +0x111, +0x115, +0x119; u32 count + ids
  where virtual +0x24 is true; u32 count + (id, +0x11d) where virtual +0xc is true (or the
  kept list 0x4a1f08 when `keep`). The streamed sound's vtable 0x47e86c: +0xc 0x468a90
  (`GetStatus` & 1), +0x1c 0x468cc0 (`ret`), +0x24 0x468cd0 (`xor eax, eax; ret`). Load:
  first list → 0x4690c0 (virtual +0x1c), second → 0x4a1f08; 0x4696f0 plays it with
  `NoiceIdPlay(id, value)` and frees it. Callers: 0x40d38d (entry 1000), 0x40d64f
  (`LoadSaveTimer`), 0x40dc34 (save); all pass 0.
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__FUN_00469790.c`,
  `…__FUN_004696f0.c`; disassembly of the vtable slots; call scan.
- **Method:** decompile, disassembly.
- **Confidence:** proven; whether any sound object answers +0x24 is open (Q-0092).

### E-0255 — Animation names in saves carry uninitialised bytes (DVD)
- **Binary/file:** `RING_DVD.EXE` `aAnimation::LoadSave` 0x416070, save branch: the name
  (`*(this+4)+4`, or "" 0x49523c) is copied with an inline `strcpy` (`repne scasb`, `rep
  movsd/movsb`, length strlen + 1) into the 0xa1-byte stack buffer `local_a4`, which is not
  cleared before; the 0xa1 bytes are written whole. Load passes the buffer to `SetName`
  0x416cd0, which reads up to the NUL.
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__aAnimation__LoadSave.c`.
- **Method:** decompile.
- **Confidence:** proven from the code (no save file of the original examined).

### E-0256 — `Save.aba` and the shipped save folder (DVD, CD, ISO)
- **Binary/file:** `RING_DVD.EXE` `aFileList::Init` 0x47a0e0 → `Load` 0x47a1d0 (path
  `"%s\data\Save\%s"` 0x494d1c, u32 count, records read by 0x479f10 = three `aString`
  records), `Save` 0x47a470 (`CREATE_ALWAYS`, u32 count, 0x479f80), `Add` 0x47a5e0 (record
  set by 0x479ff0 from three strings, appended at the list's end), remove 0x47a790, getters
  0x47a890 (string 0), 0x47a810 (1), 0x47a850 (2). Corpus: `DATA/SAVE/SAVE.ABA` and
  `ZERO.ABA` are `00 00 00 00` in all three editions; `DUMMYLS.BMP` 104 bytes, 4×4, 24 bpp,
  black; the EXE names `dummyLS.bmp` (0x493b20, `aList::Add` 0x46e4a0) but not `zero.aba`.
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__aFileList__*.c`,
  `…__FUN_00479*.c`, `…__FUN_0047a*.c`; `games/ring/discs/*/…/save/`; string scan.
- **Method:** decompiles, corpus, string scan.
- **Confidence:** proven.

### E-0257 — `StartMenu(1)` saves `SaveGame` and takes the snapshot; continue (DVD)
- **Binary/file:** `RING_DVD.EXE` `aApplication::StartMenu` 0x40dc80: when app+0x6f is 0 and
  the argument is set: busy cursor 0x402840(0x33), 0x40e610, 0x40f6c0, 0x419350(bag),
  `LoadSave("SaveGame" 0x486034, 2)` (failure returns without opening the menu), a new
  `aImage` at 0x49556c, `Create(24, 2, 640, 480)`, `aVideoDeviceRaw::CopyBufferToImage`.
  Object click 90004 (0x431660 case 0x15f94): 0x408bc0, 0x431040, `LoadSave("SaveGame", 1)`;
  on failure again 0x408bc0, 0x431040, `aApplication::Init`, `CanNotCountineGame`.
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__aApplication__StartMenu.c`,
  `…__FUN_00431660.c`.
- **Method:** decompiles.
- **Confidence:** proven.

### E-0258 — Opening the save screen: description, thumbnail (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x431660 case 0x15f93 (90003): busy cursor, name buffer
  0x4a1a68 emptied, `ObjPreSetTxtToPuz(90313, 0, 0, …)`, `ObjPreSetTxtCooToPuz(…, 344, 181)`,
  `ObjPreSetAniCooOnPuz(90313, 0, 346, 181)`; 0x470411 (CRT), 0x47036a (`_strtime`) into
  [esp+0x60], 0x4702e6 (`_strdate`: `GetLocalTime`, the year modulo 100) into [esp+0x564]; 0x4020b0(app+0x6f);
  `sprintf(0x4a1b6c, "%s  %s   %s" 0x48d4b4, character, time, date)` at 0x4320a1..0x4320c7;
  text 1 at (344, 155) (0x4320e4: 0x9b, 0x158); `aImage::Zoom(snapshot, 0.40645
  (0x3ed01a37), 1.0)` at 0x43210a; `aImage::Save` 0x4135a0 to `"%s\data\SY\Image\%s.bmp"`
  0x48d470 with `"osc"` 0x48d488; `PuzSetAct(90003, 1, 1)`. `aImage::Zoom` 0x413a90: new
  size = width (+0x29) × first float, height (+0x2d) × second (`fild/fmul` at 0x413b06..),
  24-bit, rows 0 .. h − 2 filled. Set-up (0x467a25..0x467b19): object 90313's texts, the
  `kybcur` animation (6, 12.5), `osc.bmp` at (0, 0).
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__FUN_00431660.c`,
  `…__aImage__Zoom.c`, `…__aImage__Create.c`; disassembly at 0x432075..0x43218e and of
  0x413a90; `engines/ring/notes/zones/sy.md`.
- **Method:** decompiles, disassembly.
- **Confidence:** proven; how the 480-row picture shows on the screen is open (Q-0090).

### E-0259 — The save screen's OK and cancel (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x431660, ids 0x160c5 (90309) and 0x160c6 (90310): the
  compare at 0x432893..0x43289b sends 90310 to `PuzSetAct(90000, 1, 1)` (0x4328a1) and 90309
  to 0x4328b6: busy cursor, `FindTempFileName("%s\data\Save" 0x48d240, "ArSa" 0x48d230,
  ".ars" 0x48d238)` (0x40e620: `"%s\%s%d%s"` 0x4862a0, n = 1.., `_access` 0x47bd10, up to
  100000), `sprintf("ArSa%d")`, `SHFileOperationA` (wFunc 2 copy, fFlags 0x214) of
  `SaveGame.ars` 0x48d1dc, `SY\Image\osc.bmp` 0x48d1a4, `alb/log/sie/bru.ars` (when they
  exist) to `%s.ars`, `%s.bmp`, `%s_ALB/_LOG/_SIE/_BRU.ars`; `aFileList::Init("Save.aba")`,
  `Add(name, 0x4a1b6c, 0x4a1a68)`, `Save`; 0x408bc0, 0x431040, `LoadSave("SaveGame", 1)`;
  errors `CanNotSaveGame` 0x48d220 through 0x40e5b0 + 0x40dfd0.
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__FUN_00431660.c`,
  `…__aApplication__FindTempFileName.c`, `…__FUN_0040e5b0.c`, `…__FUN_0040dfd0.c`;
  disassembly at 0x432886..0x432955.
- **Method:** decompile, disassembly.
- **Confidence:** proven.

### E-0260 — Opening the load screen (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x431660 case 0x15f92 (90002): `aFileList::Init("Save.aba"
  0x48d704)`; for i: `AddObj(0x16184 + i, string 1 + "#" 0x48d534 + string 2, string 0, 1)`
  (0x431eeb..0x431f6a), `VisLisAdd(1, 90002, 90500 + i)` (0x407280 → `aList::Add` 0x46e4a0,
  which inserts at index 0 and resets +0xc9 = 0, +0xcd = +0xd1 = −1, and +0xc1 = 0 when the
  count exceeds +0xbd); `PuzSetAct(90002, 1, 1)` only when the list was read.
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__FUN_00431660.c`,
  `…__aApplication__VisLisAdd.c`, `…__aList__Add.c`; disassembly at 0x431ec9..0x431f79.
- **Method:** decompiles, disassembly.
- **Confidence:** proven.

### E-0261 — The load screen's OK, cancel and delete (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x431660: 0x16060 (90208): busy cursor,
  `VisLisGetIndCli(1, 90002)` (+0xcd; −1 → `SelectGame` 0x48d568), `Save.aba` string 0 at
  `VisLisGetNumIte − index − 1`, `VisLisRemAll(1, 90002, 1)`, 0x408bc0, 0x431040,
  `LoadSave(name, 1)`, then copies `%s_ALB/_LOG/_SIE/_BRU.ars` → `alb/log/sie/bru.ars` when
  `_access` finds them; failure: `LoadSave("SaveGame", 1)`, else `Init`; `CanNotLoadGame`
  0x48d334. 0x1605f (90207): `PuzSetAct(90000)`, `VisLisRemAll`. Question kind 4, `unk_19` 4:
  `VisLisGetObjCli` (null → close, `SelectGame`), the `.aba` entry removed (0x47a790) and
  saved (0x47a460), `VisLisRem(1, 90002, object, 1)`, `SHFileOperationA` wFunc 3 (delete),
  fFlags 0x214 on `%s.ars` 0x48d600, `%s.bmp` 0x48d5d4, `%s_ALB/_LOG/_SIE/_BRU.ars`;
  `CanNotDeleteSavedGame` 0x48d668; `unk_19` 5 closes kind 4. Hover handler 0x4335a0:
  0x1605f/0x16060 and 0x160c5/0x160c6 show one lit picture and hide the other, 0x16121 shows
  its own.
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__FUN_00431660.c`,
  `…__FUN_004335a0.c`, `…__aApplication__VisLis*.c`, `…__FUN_0047a790.c`.
- **Method:** decompiles.
- **Confidence:** proven.

### E-0262 — SY's key handler: the save name and Delete (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x433d30 (disassembly): only when a puzzle is current
  (0x402700); puzzle 0x15f92 and key 0x2e: `GetMultiLanMes("DoYouWantToDeleteSavedGame")`,
  question 4; puzzle 0x15f93: key 8 removes the last byte of 0x4a1a68 when not empty
  (0x433e51..0x433e6e), key 13 returns, key 27 copies "" (0x433dce), else
  `ObjPreGetTxtWid(90313, 0, 0)` ≥ 0x118 returns, otherwise `wsprintfA("%c" 0x48d778, key)`
  is appended; all three then `ObjPreSetTxtToPuz(90313, 0, 0, buf)`,
  `ObjPreSetTxtCooToPuz(…, 0x158, 0xb5)`, `ObjPreSetAniCooOnPuz(90313, 0, width + 0x15a,
  0xb5)` (0x433df3..0x433e46).
- **Evidence:** disassembly of 0x433d30..0x433e98;
  `engines/ring/notes/decomp/save/RING_DVD.EXE__FUN_00433d30.c`; `spec/events.md` (E-0045).
- **Method:** disassembly.
- **Confidence:** proven.

### E-0263 — The visual object list (`aVisualObjectList`) on the load screen (DVD)
- **Binary/file:** `RING_DVD.EXE` set-up call 0x467c7e `VisAddLisToPuz(1, 90002, 65, "",
  <install>"Data\Save\" (0x492f5c, 0x467ba3), "", up_gun, up_gur, "", up_gua, down_gun,
  down_gur, "", down_gua, load_gun, load_gua, 3, 0,0, 0,0, 335,127,300,35,45,3, 330,349,
  320,339,40,40, 330,380, 320,370,40,40, 0,0,0,1, 311,137, 4, 255,95,0,245,235,50, -1,-1,-1,
  1, 101)` (arguments from `notes/calls/sy_setup.jsonl`, names from the strings
  0x492ee8..0x492f4c). 0x406f90 → 0x46b990 (vtable 0x47e8dc), init 0x46d130 (flags +0xb9,
  icon dir +0xd, images +0x1d..+0x45 from `Data\<zone>\Visual\` with load-from 0x65, two
  `aText` +0xd6/+0xda), setters 0x46dcf0 (+0x49), 0x46dd10 (+0x51), 0x46dd30 (+0x59..+0x6d),
  0x46dd60 (+0x71), 0x46dd80 (+0x79), 0x46dda0 (+0x81..), 0x46ddd0 (+0x91..), 0x46de00
  (+0xa1..+0xad), 0x46de30 (+0xb1, +0xb5), 0x46e330 (+0xbd = 4), 0x46e340 (colours
  +0xe2..+0xf6), 0x46e3f0 (background +0xfa.. = −1), 0x46e460 (font +0xde); hot spots
  0x46de50 (up kind 1, down kind 2, rows kind 3 from +0x59/+0x5d/+0x61/+0x65/+0x69). Draw
  0x46bf90, click 0x46bc50, hover 0x46bd80 (cursor 0x39), key virtual +0x14 = 0x46f030
  (`xor eax, eax`). Background pictures decoded from `DATA/ENG/SY.AT2` (`load.bmp`,
  `save.bmp`, `gamestat.bmp`, 640×448, bottom-up): a 260-pixel-wide panel on the left, the
  arrows and rows where the values put them.
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__aApplication__VisAddLisToPuz.c`,
  `…__FUN_0046d130.c`, `…__FUN_0046bf90.c`, `…__FUN_0046bc50.c`, `…__FUN_0046bd80.c`,
  `…__FUN_0046d020.c`; disassembly of the setters and of 0x46de50; `bma.py` decode.
- **Method:** decompiles, disassembly, corpus.
- **Confidence:** proven for the values and behaviour.

### E-0264 — The game status bars (DVD)
- **Binary/file:** `RING_DVD.EXE` set-up 0x467ca8 `VisAddShoToPuz(2, 90004, 1, 4, 295, 343,
  28, 4, 300, 38655)` → 0x4074f0 → 0x46ebb0 (vtable 0x47e924), fields via 0x46eff0 (+0xd ..
  +0x29); draw 0x46ec60 (4 × 0x415230: `CreateSolidBrush`, `SelectObject`, `Rectangle`);
  virtual +0x18 0x46ed40 (once per +0x2d: `VarGetFloa` 0x406260 of 0x15f95..0x15f98, clamped
  with 100.0 0x47e640 and 0.0, `sprintf("%3.1f" 0x493b34)` into object 0x16122's text k,
  length `__ftol(ceil(300 × v × 0.01 (0x47e408)))`; 0x470abe runs with control word 0x1b3f,
  rounding up: `ceil`); +0x1c 0x46efd0 clears +0x2d. The floats' owners: `push 0x15f95`
  occurs in RH's and NI's handlers (0x443b16..0x44a4d4), 0x15f96 in N2's and RO's
  (0x434324..0x43c7f9), 0x15f97 in FO's (0x43de6b..0x4430b8), 0x15f98 in WA's
  (0x437de5..0x43addb).
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__FUN_0046ec60.c`,
  `…__FUN_0046ed40.c`, `…__FUN_0046eff0.c`, `…__aApplication__VisAddShoToPuz.c`;
  disassembly of 0x415230, 0x470abe; push scan; `spec/events.md` handler table.
- **Method:** decompiles, disassembly, scan.
- **Confidence:** proven.

### E-0265 — `aImage::Zoom`'s pixel mapping (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x413b53..0x413bbc: per destination row y (0 .. height − 2)
  the source row is `__ftol(y / zy)` (`fild`, `fdiv [esp+0x38]`, 0x46fe1c), per column x
  (0 .. width − 1) the source column `__ftol(x / zx)`; the three bytes of the source pixel
  (`SetOffset` 0x412dc0) are copied. `__ftol` truncates. With zx = 0.40645 and zy = 1.0 the
  picture is 260 × 480 and pixel (x, y) is the snapshot's (trunc(x / 0.40645), y).
- **Evidence:** disassembly of 0x413b40..0x413bc4;
  `engines/ring/notes/decomp/save/RING_DVD.EXE__aImage__Zoom.c`.
- **Method:** disassembly.
- **Confidence:** proven.

### E-0266 — The load list's row layout and draw type (DVD)
- **Binary/file:** `RING_DVD.EXE` 0x46bf90 with flag bit 0 (rows one under the other): text 1
  (+0xd6) at y = row step (+0x69, 45) × r − its height (+0x18) / 2 + 45 / 2 + row y (+0x5d,
  127) + origin y (+0x4d, 0); text 2 (+0xda) at y = gap (+0x6d, 3) − its height / 2 + text
  1's height + 45 / 2 + 45 r + 127; the icon (+0x41, `load_gua`'s height +0x2d) at x = +0xb1
  (311) + origin x, y = +0xb5 (137) − height / 2 + 45 / 2 + 45 r + origin y. Init 0x46d130
  creates every list picture with `FUN_0042d320(…, name, 0, 0, 1, param_15, 1000, …)`, where
  param_15 is the argument after the picture names in the set-up call (3, E-0263), the draw
  type the draw reads back (0x42d7a0).
- **Evidence:** `engines/ring/notes/decomp/save/RING_DVD.EXE__FUN_0046bf90.c` (row text and
  icon placement), `…__FUN_0046d130.c`; `engines/ring/notes/calls/sy_setup.jsonl`.
- **Method:** decompiles.
- **Confidence:** proven for the formulas; equal text heights give line 2 = line 1 + height + 3.

### E-0300 — The DVD's numbered media and the CD/ISO names pair one to one (DVD, CD, ISO)
- **Binary/file:** `engines/ring/notes/corpus-md5.tsv` (every file under `data/<zone>/<folder>/`
  of the three editions), `engines/ring/notes/calls-iso/string-pairs.tsv` (E-0304).
- **Evidence:** `engines/ring/tools/namemap.py` (`--selftest`) writes
  `engines/ring/notes/media-names.tsv`, 1,420 DVD names that differ on the CD/ISO: 441 videos
  byte-identical to a CD file (`1001.cnm` = `ass00n01_s00n02.cnm`) and 1 by size (E-0301);
  469 sounds and 432 dialogue files byte-identical (same zone, folder, language; a number
  names the same file in all its languages, no conflict); 14 sounds and 13 dialogue files
  whose bytes several CD names share, decided by the name the ISO's code uses in the
  number's place (`1359.wav` = `fos06n02_sun.wav`, `md5-code`) or the same-numbered
  sound's stem (`1061.dia` = `as_drill02.dia`, `md5-stem`); `FO_PLA.WAV` =
  `fo_planets_show.wav` (`md5-dup`: the bytes of eight CD names, no code names it); 10 AS
  pictures (`ASV01.BMA` = `ass01n01_v01.bma`, `ASP01L01.BMA` = `ass01n01p01l01.bma`) and
  8 SY list pictures (`UP_GUN.TGA` = `larup_gun.tga`, `DOWN_*` = `lardown_*`, `LOAD_*` =
  `larload_*`) byte-identical; 22 videos and 9 subtitle files on no CD/ISO disc, named by
  their code (`code`, E-0304, E-0305). The CD's and the ISO's video names are the same set
  (443), and every CD file pairs. The 936 string pairs found at the same place in matched
  DVD/ISO functions all agree with the table, but for files on no CD/ISO disc (E-0304).
- **Method:** MD5/size join per (zone, folder, language), checked against the code.
- **Confidence:** proven.

### E-0301 — CD `logo.cnm` is the DVD's; the CD video without a DVD twin is `1911` with 20 bytes changed (corrects E-0010)
- **Binary/file:** `games/ring/discs/dvd-edition/DATA/{SY/PLA/LOGO.CNM, WA/PLA/1911.CNM}`,
  `cd-version/disc1/data/sy/pla/logo.cnm`, `cd-version/disc6/data/WA/pla/WAS03N01_S03N02_VAR2.cnm`.
- **Evidence:** `logo.cnm` has MD5 `16852d03…` (8,370,541 B) on the DVD and CD disc 1 (E-0010
  said it differs). The CD video with no DVD twin by MD5 is `was03n01_s03n02_var2.cnm`
  (5,144,408 B, `80d1eb42…`); DVD `1911.CNM` has the same size, `a627ac85…`, and differs in
  20 bytes at offsets 845,734..845,823 (inside one frame's video data); `cnm.py --file`
  decodes both (50 frames, HBR). DVD videos with no CD/ISO file: 9, `1160 1161 1163 1863
  1864 1873 1874 1876 1877` (E-0010 counted 10 with `1911`).
- **Method:** MD5 join, byte diff, `engines/ring/tools/parsers/cnm.py --file`.
- **Confidence:** proven.

### E-0302 — CD and ISO disc layout; the discs merge into one folder without conflicts (CD, ISO)
- **Binary/file:** `engines/ring/notes/corpus-md5.tsv`, `games/ring/discs/{cd-version/disc1..6,
  iso-version/disc1..4}`.
- **Evidence:** folders by disc (lower-cased): CD 1 `data/as/{image,node,pla}`,
  `data/sy/{dia,image,pla,sound,visual}`, `data/{eng,fra,ger}/sy.at2`, `as.at2`; CD 2
  `data/<zone>/{dia,sound}/eng` for AS FO N2 NI RH RO WA, `data/ni/{node,pla}`; CD 3 the same
  in `fra`, `data/rh/{node,pla}`; CD 4 in `ger`, `data/{n2,ro}/{node,pla}`; CD 5
  `data/fo/{node,pla}`; CD 6 programs, `data/<zone>/sound/` (non-language) for all zones,
  `data/wa/{node,pla}`. ISO 1 programs, every `dia/<lan>` and `sound[/<lan>]` in eng/fra/ger,
  `data/as/image`, 13 AS videos, `data/ro/{node,pla}`, `data/sy`, `data/sy.at2`; ISO 2
  `data/{as,ni}/{image,node,pla}`; ISO 3 `data/{rh,wa}/{node,pla}`; ISO 4
  `data/{fo,n2}/{node,pla}` (zone archives as in E-0008). Paths on several discs: CD only
  `data/cd.ini` (contents "1".."6"); ISO `data/cd.ini` ("1".."4") and 29 AS files on discs
  1 and 2 with the same MD5. No other path repeats.
- **Method:** grouping of `corpus-md5.tsv` by edition, disc and folder; path × MD5 check.
- **Confidence:** proven.

### E-0303 — The ISO's and CD's zone set-ups are the DVD's but for names and four CD details (CD, ISO)
- **Binary/file:** `RING_ISO.EXE` set-ups SY 0x46eaa0, NI 0x467330, RH 0x45e250, FO 0x457be0,
  RO 0x461290, WA 0x453300, AS 0x46bda0, N2 0x463e10 (called by 0x439780 in the DVD's
  order); `RING_CD.EXE` SY 0x473b18, NI 0x469244, RH 0x463c20, FO 0x4559f0, RO 0x44a1e4, WA
  0x441c10, AS 0x450530, N2 0x43ba24 (called from 0x455270).
- **Evidence:** `engines/ring/tools/ringemu.py --edition iso|cd` (emulation as E-0094; it
  reproduces `notes/calls/` exactly from the DVD, `--selftest`). ISO: 6,544 calls, the
  DVD's count in every zone, all callees matched; after renaming per E-0300 every call is
  the DVD's with the same arguments except SY's `VisAddLisToPuz` (picture names
  `larup_gun.tga`.. for `up_gun.tga`..). CD (Borland: `this` first on the stack, caller
  pops): SY 282 calls, no `ObjSetActDraCur`/`ObjSetPasDraCur` for 90105 and 90106; FO
  `ObjAddRotAcc(30102, 30101, 924, 165, 1207, 406, 1, 52, 0)` where ISO and DVD pass
  0, 0, 0, 0; AS 381 calls: 0x453548(app, k) stores app+0x5e = k and 0x4190b4/0x4190a8
  store app+0x59 = `'e'`/`'f'` at the places where the DVD's AS set-up stores app+0x5d and
  app+0x58 inline (0x4635b1, 0x46379f, 0x4638e1, 0x4638f6, 0x46550a, 0x46551a; the ISO the
  same stores). `notes/calls-{iso,cd}/diff-vs-dvd.md` list every difference.
- **Method:** Unicorn emulation, difflib alignment, capstone of the helpers.
- **Confidence:** proven.

### E-0304 — DVD and ISO functions matched; the zone handlers differ in names and a few places (ISO)
- **Binary/file:** `RING_DVD.EXE`, `RING_ISO.EXE`, `RING_CD.EXE`; features from
  `tools/ghidra/scripts/ring_features.py` (`build/ring-features/`).
- **Evidence:** `engines/ring/tools/handlers.py` (`--selftest`) matches 1,454 of the DVD's
  1,793 functions in the ISO EXE, every handler of `spec/events.md` included; per handler
  (with its local helpers) strings, pushed constants 1000..999999 and named API calls are
  the same but in SY object click (language videos, E-0305), NI object click and
  after-movability (score, rides; E-0313), WA object click (sound 51006, E-0313; language
  videos), WA and AS sound-finished (language videos; game-over pictures, E-0307), RH and
  N2 sound-finished (`sprintf` formats `rh_%d` → `rhs00n0%dp01sa04`, `rh_%d_l0` →
  `rhs00n0%dp01sa03_l0`, `N2_%d%c`/`N2_%dA` → `N2EXTN01P01A0%d%c`/`N2EXTN01P01A0%dA`)
  (`notes/calls-iso/handlers-vs-dvd.md`). 936 string pairs at the same place in matched
  functions (`notes/calls-iso/string-pairs.tsv`) agree with E-0300's table except the 22
  names of files on no CD/ISO disc and the format strings. CD: 820 functions matched, 67 of
  the 78 handler entries (not the "on a movability" and "on an accessibility" ones);
  against the ISO's (`notes/calls-cd/handlers-vs-iso.md`) constants and API counts differ
  throughout (Borland keeps ids in compare chains and calls small functions VC6 inlines),
  so only strings are compared (E-0314).
- **Method:** name seeds, set-up callee map, call-list alignment, unique signatures,
  callers; feature comparison; decompiles of the differing pairs in
  `notes/decomp/editions/`.
- **Confidence:** proven for the ISO's handler list; coarse for the CD (Q-0100).

### E-0305 — The extra-language videos are chosen by language id (DVD, ISO)
- **Binary/file:** `RING_DVD.EXE` 0x437ba0 (AS entries; ISO 0x4403e0), 0x437d60 (WA object
  click 0xc5a9; ISO 0x4405a0), 0x43a860 (WA sound finished 0xc365, 0xc366; ISO 0x443030).
- **Evidence:** entry 998 (0x3e6): `GetLanID` < 4, or > 5 and ≠ 7 → `PlyCinMul(INTROM /
  1164, GetLanCha)`, else `INTROM_2` / `1163`. Entry 6 and the WA rides: `switch
  (GetLanID)`: 4, 5, 7 → `<name>_2`, 6 → `<name>_3`, default → `<name>` (`TR_WA_MM` 1162 /
  `_2` 1160 / `_3` 1161; `tr_wa_a01` 1862 / 1863 / 1864; `tr_wa_a07` 1875 / 1873 / 1874;
  `tr_wa_a10` 1878 / 1876 / 1877). The ISO's code is the DVD's with names for numbers
  (normalised decompile diff). Language ids 1..3 (ENG FRA GER) always take the base video.
- **Method:** decompiles `notes/decomp/editions/RING_{DVD,ISO}.EXE__FUN_*.c`.
- **Confidence:** proven.

### E-0306 — New Game enters AS at 999 on the DVD and CD, at 998 (the intro) on the ISO (DVD, CD, ISO)
- **Binary/file:** `games/ring/discs/iso-version/disc1/{ring.exe,Trailer.exe}`,
  `cd-version/disc6/{ring.exe,Trailer.exe}`, DVD `RING.EXE`/`TRAILER.EXE` (E-0005).
- **Evidence:** `aApplication::Init` (DVD 0x431140, ISO 0x439900) ends `push n; push 7;
  call 0x402280` (`GoZone(7, n)`): ISO `ring.exe` at 0x439932 `68 e6 03` (998), its
  `Trailer.exe` `68 e7 03` (999), the files otherwise differing in the timestamp and the
  icon (237 bytes, as E-0005). CD `ring.exe` 0x455464 `push 0x3e7` (999), `trailer.exe`
  `push 0x3e6` (998); the CD pair differs in 782 bytes, one of them in `.text` (0x455465).
  DVD: `RING.EXE` 999, `TRAILER.EXE` 998 (E-0005). AS entry 998 plays `INTROM` and the
  intro's chain, 999 the hub at once (`games/ring/docs/as.md`).
- **Method:** byte diffs, capstone, decompile of the ISO's `Init`.
- **Confidence:** proven.

### E-0307 — Game over: `End.bmp` on the DVD and CD, one of `End01..08.bmp` per cause on the ISO
- **Binary/file:** `RING_DVD.EXE` 0x431190, `RING_ISO.EXE` 0x439950, `RING_CD.EXE`.
- **Evidence:** both switch on zone − 2 (tables DVD 0x431280, ISO 0x439b1c): zones 2 (NI) and
  3 (RH) by cause 1..4 (tables 0x43129c/0x4312ac, ISO 0x439b38/0x439b48), 8 (N2) causes 1
  and 2; zone 7 with cause 0 switches to SY, calls 0x402490(1, 1, 1), hides object 7 and
  plays sound 90001 (no picture); other zones return. Each picture case calls `0x401000(name, 0,
  0x10, 4000, 2, ART_SY ? 'f' : 'e')`, then `StartMenu(0)`. DVD: `End.bmp` (0x48cf10) for
  every case. ISO: NI 1..4 → `End01`..`End04`, RH 1 → `End05`, 2 → `End06`, 3 → `End02`
  (0x439aa9 jumps to the End02 call), 4 → `End07`, N2 1 → `End03`, 2 → `End08`. The CD's
  EXE has the string `End.bmp` and none of `End01..08` (raw scan).
- **Method:** disassembly of the functions and their jump tables, string scan.
- **Confidence:** proven for DVD and ISO; strong for the CD (string only).

### E-0308 — SY's archive per edition (CD, ISO)
- **Binary/file:** `DATA/<LAN>/SY.AT2` of every edition, ISO `data/sy.at2`,
  `iso-version/disc1/install/{eng,fra,ger}.lis`, DVD `INSTALL/ENG.LIS`.
- **Evidence:** members by MD5 (`parsers/at2.py`): CD `eng/sy.at2` equals DVD `ENG/SY.AT2`
  (1,654 members); CD `ger` differs from DVD `ENG` in the menu pictures (`end.bmp`,
  `exit.bmp`, `gm_*.bmp`, ...), as DVD `FRA` does. ISO `data/sy.at2` equals DVD `ENG`. ISO
  `eng/sy.at2` has 1,661 members: `\image\end01.bmp`..`end08.bmp` added, `\list\menu_gun.tga`
  missing, `end.bmp`, `insertcd.bmp`, the menu pictures and `\ani\kybcur\kybcur.0006.bmp`
  different; `fra` 1,662 members, the same additions. The install lists of ISO and DVD
  name `data\<lan>\sy.at2` with code 17 (other files 1, 18, 19).
- **Method:** `at2.parse` member MD5s; reading the `.lis` files.
- **Confidence:** proven (the meaning of code 17 is Q-0103).

### E-0309 — `GameZoneOnCD`'s zone → disc tables (DVD, CD, ISO)
- **Binary/file:** `RING_DVD.EXE` 0x4312c0 (table 0x431328), `RING_ISO.EXE` 0x439b60 (table
  0x439bb8), `RING_CD.EXE` 0x4555d0 (table 0x4555f6).
- **Evidence:** returns 1 when the dword at app+0x1d (CD app+0x1e) is 0, else the disc of
  zone 1..8: DVD and CD SY 0, NI 2, RH 3, FO 5, RO 4, WA 6, AS 1, N2 4 (the CD layout,
  E-0008); ISO SY 0, NI 2, RH 3, FO 4, RO 1, WA 3, AS 2, N2 4 (the ISO layout).
- **Method:** disassembly, jump tables read with pefile.
- **Confidence:** proven.

### E-0310 — `fl.ini` differs only in `CHECKCD` (DVD 0, CD and ISO 1)
- **Binary/file:** `dvd-edition/FL.INI`, `cd-version/disc6/FL.INI`, `iso-version/disc1/fl.ini`.
- **Evidence:** the 24 lines are the same text but `CHECKCD:` (0 on the DVD, 1 on the CD and
  ISO); the CD's and the ISO's files are identical.
- **Method:** reading the files.
- **Confidence:** proven.

### E-0311 — Languages per edition (DVD, CD, ISO)
- **Binary/file:** `RING_ISO.EXE` 0x407bf0, `RING_CD.EXE` 0x4119ec..0x411b77; corpus.
- **Evidence:** the ISO's `aApplication::Init` registers the DVD's ten languages with the
  same ids and channels (push sequence at 0x407bf0 = the DVD's). The CD EXE has no language
  table: `LANGUAGE:` is compared with `ENG FRA GER ITA SPA`, storing 1..5 at app+0x1c (else
  1, ENG). Voices and subtitles on the CD and ISO discs exist for `eng fra ger` only, as do
  `data/<lan>/sy.at2` (E-0302, E-0008).
- **Method:** capstone of the registration code; corpus listing.
- **Confidence:** proven.

### E-0312 — `aMes.ini` and `aObj.ini` across editions (CD, ISO)
- **Binary/file:** `AMES.INI`, `AOBJ.INI` (DVD), `ames.ini`, `aobj.ini` (ISO disc 1),
  `ames.ini`, `aObj.ini`, `aObj.BAK` (CD disc 6).
- **Evidence:** `aMes.ini`: CD and ISO identical; their ENG, FRA and GER texts equal the
  DVD's for all 18 messages (the ISO/CD file has one stray line). `aObj.ini`: ENG, FRA, GER
  texts equal the DVD's except object 40000: missing from the CD's file; ISO FRA `Feu
  Force`, GER `Vuurkracht` where the DVD has `Force d'feu`, `Feuerkraft`. The CD's
  `aObj.BAK` is an older list (no 20403, 40000, 70000; 13 ENG names differ).
- **Method:** parsing the blocks per id and language.
- **Confidence:** proven.

### E-0313 — The ISO's handler logic that differs from the DVD's besides names (ISO)
- **Binary/file:** `RING_DVD.EXE` 0x437d60, 0x445c80, 0x449320, 0x435a00; `RING_ISO.EXE`
  0x4405a0, 0x44e460, 0x451b20, 0x43e230.
- **Evidence:** WA object 0xc3b4: the DVD calls stop(51006, 0x400) (0x406e00) inside the
  byte-50012 = 4 and > 4 branches; the ISO once after both tests. NI object 10430 (0x28be):
  with object 10305 in hand (`unk_19` 1) the score float 90005 rises by [0x47e620] = 3
  (DVD) / [0x4872e0] = 5 (ISO); taking it back (byte 10430 = 1) lowers it by 3 on the DVD
  only. NI after-movability: the ISO adds 5 after `TR_NI_RH_Bshort`; the DVD's (0x449320)
  does not. NI object 10450 (0x28d2) and N2 sound-finished (byte 70014) differ in control
  flow (normalised decompile diffs).
- **Method:** decompiles in `notes/decomp/editions/`, normalised diff; constants read with
  pefile.
- **Confidence:** proven for the listed differences; the NI 10450 and N2 flows not analysed
  (Q-0101).

### E-0314 — The CD EXE against the ISO's: string differences (CD)
- **Binary/file:** `RING_CD.EXE`, `RING_ISO.EXE`.
- **Evidence:** of the strings the ISO's code references (4+ characters), absent anywhere
  in the CD EXE: runtime ones, `End01..08.bmp`, `INTROM_2`, `TR_WA_MM_2/_3`,
  `tr_wa_a01/a07/a10_2/_3`, `%s  %s   %s` (the load list's line), `aCinemaCompression`
  strings. Of the CD's, absent from the ISO EXE: Borland runtime, `End.bmp`, `%s
  %02d.%02d.%d  %02d:%02d:%02d`, `Nibelheim`, `Nibelheim II`, `Rock Of Gods`, `Walkirien`,
  `Asteriod` (0x409a34.., a zone → name switch), `Ring Alpha 1.0` (the window title,
  0x41a182), `errSystemLog.txt`, `LEVER:%d` (after an unconditional jump at 0x462eab),
  `CAS 1.10`. All three save as `ArxSav 1.00` with `%sring.exe` (CD 0x91cb4).
  `ASS01N01P01a01`.. (the hub videos) are in the CD EXE (0x9e81c) though its Ghidra
  functions do not reference them: the CD's features are incomplete.
- **Method:** raw case-blind byte search of each EXE for the other's code strings.
- **Confidence:** proven for the strings; what each CD-only string does beyond the noted
  uses is not analysed (Q-0100).
