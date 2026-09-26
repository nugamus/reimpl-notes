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

### E-0025 — .dia subtitle and .dan timing files
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
