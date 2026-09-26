# Evidence log (Peintre engine, Mission Sunlight)

Every factual claim in `engines/peintre/docs/` and `games/mission-sunlight/docs/` must have
an entry here that names the thing that proved it. Claims without evidence are bugs, not
shortcuts.

Append only. Do not rewrite history; if a claim turns out to be wrong, add a new entry
that supersedes it and mark the old one `SUPERSEDED by E-nnnn`.

## Entry format

```
### E-0001 — <one-line claim>
- **Binary/file:** games/mission-sunlight/discs/cd/Data/mission.___ | .../Scenes_3D/MUSEE.BFG | traces/<run>.log
- **Evidence:** Ghidra address (`0x004ab120`), trace line number, or corpus statistic
  ("all 94 .HNM files start with `HNM6`").
- **Method:** how it was obtained (decompiled `FUN_004ab120`; ran
  `engines/peintre/tools/parsers/bfg.py` over the corpus; trace of a scenario).
- **Confidence:** proven | strong | tentative
```

An entry at `tentative` confidence must also have a matching line in `OPEN-QUESTIONS.md`.
Addresses are virtual addresses in `/MISSION.EXE` of `ghidra_projects/Peintre.gpr` (image
base 0x400000); "file offset" means an offset in `Data/mission.___`.

## Entries

### E-0001 — The corpus: one CD, 877 files, 557,550,196 bytes
- **Binary/file:** `games/mission-sunlight/discs/cd/` extracted from
  `games/mission-sunlight/images/Mission Sunlight (1998)(Media Factory).iso` (559,339,520 B,
  MD5 `63abbda76eeebad76de2750334720603`)
- **Evidence:** 877 files (the MD5 table has 878 lines with its header); per directory
  `Data/SPRITES` 289, `Data/SOUND` 190, `Data/GFX` 134, `Data/MOVIES` 132, `Data/Graphs_2D`
  104, `Data/Scenes_3D` 15, `Data/FONTS` 3, `Data/` 4, root 4, `dx/` 2. Every file's MD5 in
  `engines/peintre/notes/corpus-md5.tsv`.
- **Method:** `python engines/peintre/tools/survey.py` (read-only walk, MD5 of every file).
- **Confidence:** proven

### E-0002 — mission.___ is the game: a Visual C++ 5.0 debug build of a program named PEINTRE
- **Binary/file:** `Data/mission.___` (1,751,552 B, MD5 `b03e8c7d1ca6af8a20e23f9fecf4559f`,
  PE timestamp 0x35f7a012 = 1998-09-10 09:46:58 UTC); installed as `mission.exe`
  (`AutoRun.exe` string `%s\mission.exe` at file offset 0x5e4f, read from registry
  `SOFTWARE\Cryo\Mission Sunlight`).
- **Evidence:** linker 5.10; Rich header linker id 19 build 8034 (x8), cvtomf id 3 build 7303,
  cvtres id 6 build 1668, 376 objects without ids (pre-VC6 compilers emit none). Debug CRT
  linked statically: `dbgheap.c`, `dbgrpt.c`, `_CrtDbgReport` strings, "Microsoft Visual
  C++ Debug Library". CodeView path `D:\Vangogh\Peintre\Debug\PEINTRE.pdb` (file offset
  0x1ab930). Sections `.text .rdata .data .idata .rsrc .reloc`, entry 0x476510.
  Imports: KERNEL32 (90), USER32 (44), GDI32 (15), ADVAPI32 (3: registry read), WINMM (4:
  `timeSetEvent`, `timeKillEvent`, `timeBeginPeriod`, `timeEndPeriod`), DDRAW
  (`DirectDrawCreate`, `DirectDrawEnumerateA`), DSOUND (ordinals 1, 2), DINPUT
  (`DirectInputCreateA`). No other DLL. The only assert strings with source files are
  the CRT's (`sprintf.c`, `fopen.c`, …; `aw_env.c`, `aw_map.c`, `aw_str.c` sit in the
  same cluster between `stdargv.c`/`ioinit.c` and `ungetc.c`, and are the CRT's ANSI/wide
  wrappers: the EXE imports `GetEnvironmentStrings`, `LCMapStringA`, `GetStringTypeA`). The game code has no asserts with source paths; its error
  strings name functions (`C_Monde::LoadScene => %s`, `LoadAnimscafe::%s manque`,
  `LoadTga::Erreur ouverture %s`) and its message box title is "Vangogh Erreur".
- **Method:** `survey.py` (`pefile`, Rich header, string scan; `notes/binaries.md`,
  `notes/exe-strings.md`).
- **Confidence:** proven

### E-0003 — The 2D, file, font, memory, DirectDraw and DirectSound layers are Cryo libraries by L. Guillang
- **Binary/file:** `Data/mission.___`
- **Evidence:** banners at file offsets 0xb1cb8 "Win32 File I/O high level library - Written
  by L. GUILLANG - (C) 1997 CRYO Interactive", 0xb1d10 "Win32 Fonts high level library",
  0xd2d70 "Memory Manager" (+ "Mem-Lib 1.1 - Log File on …" at 0xd3058), 0xd3d18
  "DirectDraw 5 high level library", 0xd3dc8 "DirectSound 5 high level library …
  (C) 1997-98". Cryo formats named in strings: `CRYO_APC` (0xb1b08), ADPCM error names
  (`ADPCMERR_*`, 0xb1b44..), HNM ("'%s': HNM version not supported ...", 0xa504c), and the
  data path templates `%sDATA\{SPRITES\%s.SPR, FONTS\%s.AWF, MOVIES\%s.HNM, MOVIES\%s.CVY,
  GFX\%s.TGP, SOUND\%s.APC, SOUND\%s.WAV}` and `%sSAVE\{USERS.BIN, GAME%02u%02u.BIN,
  GGAME%u.BIN}` (list in `notes/exe-strings.md`). Registry key `SOFTWARE\Cryo\Mission
  Sunlight` with values `Target`, `Language`, `Install Level` (0xa8688..0xa86d0).
- **Method:** `survey.py` string scan.
- **Confidence:** proven

### E-0004 — The EXE references no Direct3D interface: the 3D is drawn in software
- **Binary/file:** `Data/mission.___`
- **Evidence:** of the DirectX 5 interface IDs, only `IID_IDirectDraw2` (file offset
  0xa12d0), `IID_IDirectDrawSurface2` (0xa1300) and `IID_IDirectSound3DBuffer` (0xa13c0)
  occur; `IID_IDirect3D`, `IID_IDirect3D2`, the HAL/RGB/MMX/Ramp device IDs and both
  texture IDs are absent, no string contains "Direct3D" or "D3D", and D3D is not imported
  (E-0002). The ReadMe's claim that "display functions pass totally via Direct 3D" does
  not match the program. The DirectDraw library's own errors name only DirectDraw calls
  (0xd3198..0xd3c18).
- **Method:** `survey.py` GUID scan (`notes/exe-strings.md`); ReadMe.txt.
- **Confidence:** strong (the software rasteriser itself is to be located in Ghidra)

### E-0005 — No CD audio and no CD check in the program
- **Binary/file:** `Data/mission.___`
- **Evidence:** WINMM imports only the multimedia timer (E-0002): no `mciSendCommand`,
  `mciSendString`, `aux*` or `mixer*`; no string "cdaudio" or "mci"; `GetDriveTypeA` is not
  imported. The disc image is a single data track (ISO), and nothing in the program needs
  another. Sound is WAV and APC files (`%sDATA\SOUND\%s.{WAV,APC}`, E-0003) and HNM
  soundtracks. The data root comes from `%s` prefixes (registry `Target` or PEINTRE.INI,
  to be read in Ghidra).
- **Method:** import table and string scan.
- **Confidence:** strong

### E-0006 — Installer, uninstaller and autorun
- **Binary/file:** `Setup.exe` (960,000 B, MD5 `5c6365fc3766fc6ff48c3dee316c8c91`, MSVC
  linker 5.10, 1998-12-07), `Data/Uninst.___` (935,424 B, `08379e4901d07f637eb947a40b736b50`,
  MSVC linker 5.10, 1998-12-07), `AutoRun.exe` (31,232 B, `6dcb5428107046b0f7bc670e48a0c5c5`,
  Watcom C/C++32 run-time, 1998-12-07). `dx/dx5eng.exe`, `dx/dx5frn.exe`: DirectX 5
  redistributables (English, French).
- **Evidence:** `notes/binaries.md`. `Data/SETUP.INI` lists three install levels with byte
  sizes: `[LEVEL 3] 152000000` (GFX\*.TGP, CHAMBREB.BFG, PONT.BFG), `[LEVEL 2] 47250000`
  (SOUND\*.APC, JARDIN.BFG, EGLISE.BFG and 55 named WAVs), `[LEVEL 1] 15789258` (MUSEE,
  MANGEURS, MAISONET, MAISONJ .BFG, GRAPHS_2D\*.*, SPRITES\CURSEURS.SPR,
  SPRITES\CURSOPT.SPR). Files not listed are read from the CD.
- **Method:** `survey.py`; reading SETUP.INI.
- **Confidence:** proven

### E-0007 — Extension census of the data
- **Binary/file:** `games/mission-sunlight/discs/cd/Data/`
- **Evidence:** `.SPR` 289 (Data/SPRITES), `.TGP` 134 (Data/GFX), `.WAV` 122 (all `RIFF`),
  `.TGA` 104 (Data/Graphs_2D, all start `00 00 02 00`: no ID, uncompressed true colour),
  `.HNM` 94 (all `HNM6`) plus the extensionless `MOVIES/A13_052B` (`HNM6`), `.APC` 68 (all
  `CRYO`), `.CVY` 37 (MOVIES), `.BFG` 15 (Scenes_3D), `.AWF` 2 (FONTS), `TROBO.TTF`,
  `SETUP.INI`, `icon3.ico`. SPR first dwords: `04000080` 152, `04030040` 115, `04030000`
  12, `04030080` 10. Table in `notes/corpus-inventory.md`.
- **Method:** `survey.py`.
- **Confidence:** proven

### E-0008 — The engine is named `peintre`
- **Binary/file:** `Data/mission.___`
- **Evidence:** the program's own name is PEINTRE (E-0002: `D:\Vangogh\Peintre\Debug\
  PEINTRE.pdb`; it reads `\PEINTRE.INI`, "Fichier PEINTRE.INI introuvable" at file offset
  0xaadd0). The 3D part (scenes `C_Monde::LoadScene`, `.BFG/.3DC/.3DM/.3DA/.3DI`, a
  software rasteriser, E-0004) is game code in the same EXE, not a separate library; the
  Cryo libraries (E-0003) cover only 2D, files, sound and video, and their formats (HNM6,
  APC) already have readers in ScummVM (`video/hnm_decoder`, `audio/decoders/apc`). No
  other title is known to share the PEINTRE code, so the engine takes the program's name
  rather than the game's or Cryo's (Q-0001).
- **Method:** string scan; decision recorded here.
- **Confidence:** strong

### E-0009 — Ghidra project Peintre.gpr holds /MISSION.EXE, analysed: 1,191 functions
- **Binary/file:** `ghidra_projects/Peintre.gpr`, program `/MISSION.EXE` (copy of
  `Data/mission.___` in `build/peintre-import/`, MD5 as E-0002)
- **Evidence:** auto-analysis completed (`logs/peintre-import.log`, 36 s; no PDB found, as
  expected). 1,191 non-thunk functions; the incremental-link jump table at
  0x401000–0x4022bf holds the thunks every call goes through. Per-function strings,
  imports, callers and callees in `engines/peintre/notes/function-dump.tsv`.
- **Method:** PyGhidra headless `-import … -overwrite`, then
  `tools/ghidra/scripts/func_dump.py` (read-only).
- **Confidence:** proven

### E-0010 — The code is laid out by object file: shell, sound, users, 3D scenes in alphabetical order, 3D engine, Cryo libraries, CRT
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** module ranges and the strings that prove each in
  `engines/peintre/notes/module-map.md`. The 3D scene code runs auberge (0x419f0e
  `LoadBoxAuberge`), cafe (0x41b6ab), chambreb (0x41c8a7), chambrev (0x41dcad), champ
  (0x41e2b1), then the world/INI code (0x41ed13 `\PEINTRE.INI`, 0x421e56
  `C_Monde::LoadScene`), then eglise (0x42421b), hopiext (0x424978), hopiint (0x425420),
  jardin (0x426bf8), maisonet (0x4278d1), maisonj (0x4286e2), mangeurs (0x429813), musee
  (0x42aab8), pont (0x42ce08), terrasse (0x42dced): alphabetical, one object per scene.
  The Cryo libraries sit together at 0x465bd0–0x4746ff (APC codec, then file, fonts,
  memory manager, DirectDraw, DirectInput, DirectSound), before the CRT.
- **Method:** `func_dump.py` + `engines/peintre/tools/funcmap.py`.
- **Confidence:** strong (ranges are contiguous and every named function falls in its
  range; boundaries between unnamed functions are approximate)

### E-0011 — 83 functions named from their strings; the Cryo memory manager names itself
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** `engines/peintre/notes/function-map.csv` (address, module, name,
  evidence string). The Mem-Lib debug log strings give the memory functions' own names:
  0x4709e0 "> m__purge ()", 0x470a80 "> m__malloc (%u)", 0x470ba0 "> m__calloc (%u,
  %u)", 0x470e10 "> m__free (0x%08X)", 0x470ea0 "> m__defrag()". The scene loaders name
  themselves in their error strings (`LoadBox<Scene> => %s`, `LoadAnims<scene>::%s
  manque`), as does `C_Monde::LoadScene` (0x421e56). The other names are ours, each with
  the string that motivated it.
- **Method:** `funcmap.py` → `tools/ghidra/scripts/apply_names.py` (renamed in the project).
- **Confidence:** proven for the self-named ones, strong for the rest

### E-0012 — 64 KB of assembly at 0x455470–0x465bcf has no C functions
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** no function starts in the range after auto-analysis; the code is
  NOP-padded between routines (e.g. 0x4554e8) and register-only, e.g. 0x456000 `mov bl,
  al; mov cl, ah; shr eax, 5` (5-6-5 pixel packing shape). The 3D engine is software
  (E-0004), so this is the likely home of the span loops; not yet proven (Q-0002).
- **Method:** capstone disassembly of the raw bytes.
- **Confidence:** tentative (Q-0002)
