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
