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

### E-0013 — BFG: 100-slot directory, entries from 0xE18, each LZ-packed with a 20-byte typed object header
- **Binary/file:** `/MISSION.EXE`; `Data/Scenes_3D/*.BFG` (15 files)
- **Evidence:** `C_Monde::LoadScene` (0x421e56) builds `<scene>.BFG` and calls
  `LoadSceneFile` (0x42e85c): the whole file is read into one `m__malloc` block
  (DAT_00598cac), from `<Target>DATA\SCENES_3D\` if the file exists there (0x42e7d0) else
  from the other root. Objects are opened by name (0x435400 → 0x42e6e0): 0x42e67f compares
  the name with `strcmp` against the first `count` slots (stride 0x24, name at +4); the
  entry at `file + 0xE18 + slot.offset` of `slot.size` bytes is unpacked by 0x466bc3
  (byte 0 == 1: copy `size-4` bytes from +4; else the LZ loop: u16 flags, bit 0 literal,
  bit 1 `dist = (b0 & 0xF0) * 16 + b1`, `len = (b0 & 0xF) + 1`, until the source pointer
  equals the end). CheckHeader (0x4348c0) then fills the header's words 0, 1, 3, 4 (handle,
  size, list links) and rejects `type` outside 0..6 ("Type d'entete non valide !!!!");
  types 1, 2, 4, 6 get their pointer table relocated (0x4343c0), 4 and 6 more pointers
  (0x434470, 0x4344a0), 5 its own (0x4344d0), 1 its textures loaded (0x434560).
  Corpus: `bfg.py` validates 15/15 files, every byte consumed (entries contiguous in
  directory order, the last ends at EOF, 4 zero bytes before 0xE18, every LZ stream ends
  exactly at its entry's end); 594 entries, all LZ; type = 1 for all 15 `.3DC`, 3 for 504
  `.3DM`, 4 for 48 `.3DA`, 5 for 27 `.3DI`.
- **Method:** decompiled the functions named; `engines/peintre/tools/parsers/bfg.py`.
- **Confidence:** proven

### E-0014 — .3DC layout: node table, materials, then a node tree with 1-based root-relative pointers; 15/15 fully covered
- **Binary/file:** `/MISSION.EXE`; the 15 `.3DC` entries of the BFGs
- **Evidence:** `Obj_CheckHeader` (0x4348c0) for type 1: `Obj_RelocTable` (0x4343c0)
  turns the `n` body-relative node offsets into pointers; 0x434350 walks the tree from
  node [0] (child at +0x14, sibling at +0x18, parent at +0x10) and 0x434270 adds
  `root - 1` to the node fields +0x10/+0x14/+0x18/+0x80/+0x88/+0x90/+0x98/+0xa0/+0xa4/
  +0xa8, then to face groups (0x433b70: +0 next, +0x20 polys; per poly the words at
  +4..+0x2c, and +0x34..+0x3c when the poly is 0x44 bytes; 0x38-byte polys for group types
  -2, 1, 4, 0x11, 0x1b) and vertex groups (0x433ff0: +0 next, +0xc items; item sizes
  100/0x70/0x58/0x3c by type; words 0, 7, 8 of each item). `Obj_LoadTextures` (0x434560)
  reads `num_materials` 44-byte records after the node table and loads `<name at +16>.3DM`
  for each, refcounting textures in 15-word slots (texel pointer = entry data + 0x8014).
  0x4338d0 binds each face group to its material by name (strcmp at group +0xc). Node
  flags (0x450160, 0x44fec0): bit 0 or bit 2 set = the node is not processed. World
  position/rotation are recomputed per frame (0x44fec0: 0x43b060 multiplies the parent's
  +0x58 by the local +0x28 into +0x58; +0x4c..+0x54 = rotated position + parent's).
  Corpus (`obj3d.py`): 15/15 bodies covered exactly once by the structures reached; the
  node table lists exactly the tree's nodes in all 15; node[0] follows the materials;
  `+0x2c` of every face group equals the poly size the loader uses; node +0x9c/+0xa0 are
  0 everywhere; material tail = `ef3d ef3d` + 8 zero bytes on the 15 DEFAULT materials, 12
  zero bytes on the other 485; vertex flags 0 (57,007) or 0x80 (713); node flags 0 (352),
  0x10 (132), 0x20 (50), 0x30 (26); names at most 10 characters.
- **Method:** decompiled the named functions; `engines/peintre/tools/parsers/obj3d.py`.
- **Confidence:** proven for the layout; the Q15 / 16.16 readings are strong (values
  0x8000 on matrix diagonals and normals, UVs 0..0xFF0000)

### E-0015 — .3DM: 32x256 RGB565 shade table in u32 high halves, then 256x256 8-bit texels
- **Binary/file:** 504 `.3DM` entries
- **Evidence:** `Obj_LoadTextures` stores `data + 0x8014` (header 0x14 + table 0x8000) as
  the texel pointer. All 504 tables have zero low halves; mean luminance falls
  monotonically from level 0 to 31 (chambrev `sol.3DM`: 128, 119, 112 … 68 at levels 0,
  4, 8 … 28). Decoding chambrev `sol.3DM` with level 16 gives a coherent wood-plank image
  (256x256). 500 textures have exactly 65,536 texel bytes; jardin `salon.3DM` has 66,048
  (512 extra) and musee `plafond.3DM`, `plafond2.3DM`, `plafond3.3DM` 65,280 (one row
  short) (Q-0003).
- **Method:** `obj3d.py`; decode script over the extracted entry.
- **Confidence:** proven (layout); strong (RGB565: images decode with natural colours)

### E-0016 — .3DA tracks of rotation/position keys; .3DI box sets; layouts fully covered
- **Binary/file:** 48 `.3DA`, 27 `.3DI` entries
- **Evidence:** 3DA (type 4): 0x4343c0 relocates the track table body-relative, 0x434470
  relocates each track's +0xc and +0x10. Track = u32, u32 nrot, u32 npos, rot ptr, pos
  ptr; rot keys 20 B, pos keys 16 B cover every body exactly (48/48). chambrev
  `portev.3da`: 3 tracks of length 30; its first position key (0, -385, -532, 1001)
  equals the position of chambrev's root node `Object03`; rotation keys like (0, 0, -1429,
  0, 32736) are unit Q15 quaternions (norm 32767). 3DI (type 5): 0x4344d0 adds `body - 1`
  to +4, +0xc, +0x14 and, per 0x60-byte face (count at +8), to words 0, 1, 2, 3 and 17.
  Layout vertices (12 B) / faces (0x60) / items (12 B) plus a 0x1c-byte header covers
  27/27; the header's last word is leftover memory. `C_Monde::LoadScene` loads `BOX.3DI`
  for every scene; `LoadBox<Scene>` loads the extra ones (`BOX1.3DI`, `BOXBAS/BOXHAUT`).
- **Method:** as E-0014.
- **Confidence:** proven (layouts); tentative (quaternion component order, track field 0 =
  length in frames: Q-0004)

### E-0100 — TGP: width, height, then either HLZ chunks (Tgp_Load) or one LZWCRYO-headed HLZ stream (Tgp_Load2); RGB565 top-down
- **Binary/file:** `/MISSION.EXE`; `Data/GFX/*.TGP` (134 files)
- **Evidence:** `Tgp_Load` (0x40d9c0) opens `%sDATA\GFX\%s.TGP`, reads `u32 w`, `u32 h`,
  allocates `w*h*2` (0x408c10), reads `u32 count`, then per chunk `u32 packed`, `u32
  unpacked`, `packed` bytes, unpacks them with 0x40918c → 0x430700 at `dest + running
  total` and adds `unpacked`; when DAT_006516bc is set it runs 0x40b266 over `w*h` pixels,
  which maps `v` to `(v >> 1) & 0x7FE0 | v & 0x1F` (RGB565 → RGB555), so the pixels are
  RGB565. `Tgp_Load2` (0x414779) seeks to 8, reads 0x24 bytes, uses only the last u32
  (file offset 0x28) as the packed size, reads that many bytes and unpacks them into
  DAT_006516a8, converting 0x4B000 = 640*480 pixels on 555 surfaces. Corpus: `tgp.py`
  validates 134/134, every byte consumed: 110 files have `"LZWCRYO\0"` at 12 with
  `w, h = 640, 480`, `u32 0x24` at 8, zeros at 0x14..0x1B, `256, 1` at 0x1C, unpacked
  size 614,400 at 0x24 and packed size = file size − 0x2C at 0x28; the other 24 are
  chunked (4 to 9 chunks of at most 600,000 unpacked bytes, one side 1,500 px), their
  chunks sum to `w*h*2` and the last ends at EOF. Decoding A01_02.TGP (single) and
  A01_02B.TGP (chunked) as RGB565 top-down gives the same painting, upright, in natural
  colours. Callers: `Tgp_Load` from the shell main loop 0x4122bb and 0x411a28.
- **Method:** decompiled the functions named (`notes/decomp/MISSION.EXE__Tgp_Load.c`,
  `__Tgp_Load2.c`, `__FUN_0040b266.c`); `engines/peintre/tools/parsers/tgp.py`.
- **Confidence:** proven (the meaning of the LZWCRYO header's constant fields is not
  needed by the engine and stays `unk`)

### E-0101 — TGP packing is Cryo HLZ, identical to ScummVM's Image::HLZDecoder
- **Binary/file:** `/MISSION.EXE` 0x430700; `../scummvm/image/codecs/hlz.cpp`
- **Evidence:** 0x430700 (hand-written asm, register calling convention) keeps a u32
  bit register loaded little-endian with a sentinel bit and shifts out MSB first: bit 1
  copies one literal byte; bits 01 read a u16 `v`, `offset = (v >> 3) | 0xFFFFE000`,
  `count = v & 7`, and if 0 a count byte, where 0 ends the stream (returns bytes
  written); bits 00 read two bits of count and one offset byte `| 0xFFFFFF00`; every
  match copies `count + 2` bytes forward from `dest + offset`. This is exactly
  `Image::HLZDecoder::decodeFrameInPlace` (`offset = (tmp >> 3) - 0x2000`, `stream.readByte()
  - 0x100`, `repeat_count += 2`). `tgp.py` implements it and every one of the 110 + 149
  streams in the corpus unpacks to exactly its stated size with its end marker on its
  last byte.
- **Method:** decompiled 0x430700 (`notes/decomp/MISSION.EXE__FUN_00430700.c`), compared
  with the ScummVM source; corpus run of `tgp.py`.
- **Confidence:** proven

### E-0102 — SPR: u32 head (raw/band bits + palette end), RGB palette, bank of offset-indexed frames `{u16 a, u16 b, data}` padded to 4
- **Binary/file:** `/MISSION.EXE`; `Data/SPRITES/*.SPR` (289 files)
- **Evidence:** `Sprite_LoadFile` (0x40a766) opens `%sDATA\SPRITES\%s.SPR`, reads `u32
  head`: bit 31 → bank flag +0x1C (raw), else bit 30 → bank flag +0x20 (band); `head &
  0x3FFFFFFF` is the palette end: if it is not 4, `(end − 4) / 3` RGB triples are read and
  stored as `u32` whose high half is RGB565 (`(r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3`)
  or, when DAT_006516bc is set, RGB555 (`(r & 0xF8) << 7 | (g & 0xF8) << 2 | b >> 3`).
  The rest of the file (from `end` to EOF) is read as one block; its first u32 / 4 is the
  frame count and that many u32 offsets are relocated by the block address. Raw banks
  without palette get 0x40b266 (565 → 555) over `u16[0] * u16[1]` pixels after each
  frame's 4-byte header when DAT_006516bc is set. 0x470951 returns a frame's `u32[0] &
  0xFFFF` and `>> 16` as its width and height (used by `Sprite_Open` 0x40a24c to size
  buffers). Corpus: `spr.py` validates 289/289, every byte consumed: every palette end is
  4 (152 files) or 772 (137 files, 256 colours); offsets[0] = 4 × count and offsets rise;
  every frame is a multiple of 4 long and its 0..3 bytes after the data are zero; 115
  band banks (3,619 frames, 26 of them the empty `a = b = 0` frame, every `a + b <= 480`,
  every row within 640 px), 12 RLE banks (124 frames, every row within `a`), 152 raw16
  (1,938 frames), 10 raw8 (146 frames). Decoded frames (CURSEURS arrows, CAPSAC00 round
  buttons, A01_032A portraits, A01_02A band silhouettes over the A01_02 painting) look
  right.
- **Method:** decompiled `Sprite_LoadFile`, `Sprite_Open`, 0x470951; `engines/peintre/tools/parsers/spr.py`.
- **Confidence:** proven

### E-0103 — SPR drawing: bank kind picks the blitter; RLE frames are centred and keyed by skips, band frames span the screen from row `a`, raw frames are opaque from the top-left
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** `Sprite_Draw` (0x409d76; unclipped) and `Sprite_DrawClipped` (0x409e44)
  switch on the bank flags: not raw and not band → 0x4703be / 0x47049a; band →
  0x4705da (unclipped only); raw without palette → 0x46fb4b / 0x46fbc6 (via 0x47037a,
  0x47039c); raw with palette → 0x47067d / 0x470793. 0x4703be and 0x47049a start at
  `(x − w/2, y − h/2)` (`w >> 1`, `u32 >> 17`) and read per row: `0x80` ends the row,
  `c < 0x80` advances `c` pixels without writing, `c > 0x80` writes `c & 0x7F` pixels
  looked up in the palette (high half of the u32 entry). 0x4705da ignores x/y: it starts
  at screen row `u32[0] & 0xFFFF` column 0, draws `u32[0] >> 16` rows of the same RLE,
  and returns at once for a zero header. 0x47067d / 0x470793 draw `w*h` palette indices
  from (x, y) with no transparency; 0x46fb4b copies `w*h` u16 pixels from (x, y) with no
  transparency. The background-save routine 0x409f09 uses the same rectangles: centred
  for RLE, `(0, a, 640, b)` for band, `(x, y, w, h)` for raw, clipped to 640×480.
- **Method:** decompiled the functions named (`notes/decomp/`).
- **Confidence:** proven

### E-0104 — TGA: plain uncompressed 16-bit TGA (X1R5G5B5, bottom-up); the engine reads only width, height and pixels; pure green is the key colour
- **Binary/file:** `/MISSION.EXE`; `Data/Graphs_2D/*.TGA` (104 files)
- **Evidence:** `LoadTga` (0x41ad98) and `LoadTga2` (0x41af1c; into a caller's buffer)
  build `<dir><name>.TGA`, seek to 12, read `u16 w`, `u16 h`, seek to 18 and read
  `w*h*2` bytes, then 0x41acfa swaps rows `i` and `h−1−i` (the file is bottom row first)
  and, when DAT_005b7fa4 == 16, 0x41aae0 maps each pixel `v` to `(v >> 10) << 11 |
  ((v & 0x3E0) >> 5) << 6 | v & 0x1F` (RGB555 → RGB565). 0x41b1d5 (called from 0x424190)
  copies a clipped rectangle skipping source pixels equal to 0x07C0 when DAT_005b7fa4 ==
  16, else 0x03E0: pure green in the current format. 0x41b061 (from 0x426171) is the
  opaque copy; its loops run `rows + 1` and `cols + 1` times (0x41b061 `local_c + 1`,
  `local_8 + 1`). Callers: 0x426594 loads the cursor images (strings `op_`, `fleche`,
  `main`, `curza`, `def_0`, `def_1`, `curdoi`), 0x4240f0 ("Curseur->Buf => NULL"),
  0x42e97f ("Loading", "intro") uses `LoadTga2`. Corpus: `tga.py` validates 104/104, every
  byte consumed: all have id length 0, no colour map, type 2, origin 0, depth 16,
  descriptor 0 (93) or 1 (11), bit 15 clear in every pixel; 11 end with the 26-byte TGA
  2.0 footer (both offsets 0, `TRUEVISION-XFILE.\0`), the rest end with the pixels; 49 use
  0x03E0. Decoding cle.TGA with the rows flipped shows an upright key on the green key.
  ScummVM's `Image::TGADecoder` reads this variant, but maps it to ARGB1555 with
  `attributeBits` alpha bits (`image/tga.cpp`), which makes the 11 descriptor-1 files
  fully transparent (bit 15 is 0): an engine must take the pixels as RGB555 and ignore
  alpha, then key on 0x03E0.
- **Method:** decompiled the functions named (`notes/decomp/`); `engines/peintre/tools/parsers/tga.py`.
- **Confidence:** proven

### E-0105 — AWF: 38-byte font record + data (glyph offset table, 1-bpp glyphs MSB first, width/spacing tables when proportional)
- **Binary/file:** `/MISSION.EXE`; `Data/FONTS/TOPAZ8.AWF`, `TROBO12.AWF`
- **Evidence:** `Font_LoadAwf` (0x40acde; 6 slots, stride 0x26 at DAT_004e1ad0) opens
  `%sDATA\FONTS\%s.AWF`, reads 0x26 bytes into the slot, the remaining `size − 0x26`
  bytes into one `m__malloc` block stored at slot+4, and adds the block address to the
  u32s at +8, +0xC, +0x10, +0x14, +0x18. The draw wrappers 0x40af8c / 0x40afba and the
  measure wrapper 0x40afe8 pass the slot to 0x46f457 / 0x46f4c0 / 0x46f529, which copy
  +8 (glyph base), +0xC (glyph offset table), +0x10, +0x14, +0x18 (three byte tables),
  byte +0x1C (first char), byte +0x1D (count, measure only), byte +0x1E (subtracted from
  y), u16 +0x20 (bit 0 tested), u16 +0x22 (fixed width), u16 +0x24 (rows) into the
  library's globals. Drawing (0x46ff9e) starts at `(x, y − [+0x1E])` and for each byte
  `c >= first` (a zero byte ends the string) takes glyph `base + table[c − first]`,
  height rows of `(w + 7) >> 3` bytes, writing the text colour for each set bit, MSB
  first; `w` is +0x22 when bit 0 is clear, else `table10[i]`, and the pen advances by
  +0x22, or by `(u8)(table18[i] + table14[i]) + table10[i]`. 0x470110 is the same and
  also writes 0 one row down and one pixel right of every ink pixel (a black shadow; the
  proportional path writes a u32 there, two pixels). 0x47029e returns the width:
  `chars × (+0x22 + 1)` for fixed fonts (one more than the draw advance), else the sum of advances over chars with
  `0 <= c − first <= [+0x1D]` (table18 read as signed). Corpus: `awf.py` validates 2/2,
  every byte consumed: TOPAZ8 fixed 8×8, chars 32..165, baseline 6, three table
  offsets 0, data = 134 u32 offsets + 134 × 8 bytes; TROBO12 proportional, height 17,
  chars 32..122, baseline 12, data = 91 u32 offsets, bitmaps up to +0x10 = 0x8DC, then
  three 91-byte tables to EOF (every +0x14 entry is 2, every +0x18 entry 0); glyph
  offsets are contiguous in both. Rendering both gives
  readable text (TROBO12 draws a placeholder `x` for its missing punctuation). The Cryo
  font format ScummVM has (`engines/cryomni3d/fonts/cryofont.cpp`, big-endian,
  `CRYOFONT` magic) is a different format.
- **Method:** decompiled the functions named (`notes/decomp/`); `engines/peintre/tools/parsers/awf.py`.
- **Confidence:** proven

### E-0200 — HNM6 files: 64-byte header, one superchunk per frame, a zero u32 at the end; 95/95 validate
- **Binary/file:** `/MISSION.EXE`; `Data/MOVIES/*.HNM` (94) and `Data/MOVIES/A13_052B` (no extension)
- **Evidence:** Hnm_Open (0x40ba64) reads 64 header bytes and fails unless the tag is
  `HNM6` ("HNM version not supported"), the u32 at +0x1C (`max_frame_size`) is >= 1
  ("corrupted header"), width is 640 and height 480 ("video width/height not
  supported"); it keeps `frame_count` (+0x10), the audio flags (+6) and `file_size - 0x40`
  (+0x0C) as the byte count to stream. Corpus (`hnm.py`): 95/95 files, every byte
  consumed: `file_size` = file length, exactly `frame_count` superchunks (size in the low
  24 bits, high byte 0 in all), then 4 zero bytes; chunks padded to 4 bytes with zeros;
  chunk flags 0; header `unk_04` 0, `bpp` 16, `unk_14` 0, `unk_18` 0, `unk_1a` 2, author
  "Pascal URRO  R&D", "-Copyright CRYO-" in all 95. Chunks: 21,363 `IX`, 80 `AA`, 18,208
  `BB`; frame 0 of every file is an `IX` key frame (quality < 0). The extensionless
  `A13_052B` (101 frames) differs from `A13_052B.HNM` (94 frames); the EXE only opens
  `%s.HNM`.
- **Method:** decompiled 0x40ba64; `engines/peintre/tools/parsers/hnm.py`.
- **Confidence:** proven

### E-0201 — HNM playback: a read thread fills a 512 KB ring; one superchunk per Hnm_Stream call; IX/IV video, AA/BB sound
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** Hnm_Open allocates `0x32000 + 0x80004` bytes, reads the first 0x80000
  (Hnm_ReadBlock 0x40c13a, 1 KB reads) and starts Hnm_StartReadThread (0x40c3d8); the
  thread (0x40c38a) waits on two events and refills the ring (Hnm_FillRing 0x40c1b3,
  0x5000 or 0x8000 bytes per read). Hnm_NextSuperchunkSize (0x40c50a) reads
  `u32 & 0xFFFFFF`; Hnm_ParseChunks (0x40c5c2) walks the chunks to `start + size`,
  next = `data + ((size - 5) >> 2) * 4` (4-byte padding), keeps `0x4141` AA / `0x4242` BB
  as sound (kind 1 / 2) and `0x5649` IV / `0x5849` IX as the video chunk;
  Hnm_DecodeVideo (0x40c725) passes it and the two 0x96000-byte frame buffers
  (alternating; Hnm_AllocDecBuffers 0x40b992) to 0x4674c9. Hnm_Stream (0x40c072) decodes
  the next frame while `frame < frame_count - 1`, else closes the movie (Hnm_Close
  0x40bf9e) and returns 0.
- **Method:** decompiled the functions named (`notes/names/media.csv`).
- **Confidence:** proven (the video codec 0x4674c9 itself not read, see E-0206)

### E-0202 — Movie sound: the audio flags give rate and channels; AA holds 32 frames of sound, each BB one frame
- **Binary/file:** `/MISSION.EXE`; `Data/MOVIES`
- **Evidence:** Hnm_InitSound (0x40c9aa): no sound if DirectSound is off or frame 0 has
  no AA/BB; channels = `((flags & 0x80) >> 7) + 1`, rate = `((flags & 0x60) >> 4) *
  11025`, 16 bits; the movie buffer (Snd_InitMovieBuffer 0x4166f1) has 32 slices of
  `(AA_payload * 4 - 0x80) >> 5` bytes (one frame of PCM each) and is filled first with
  the whole AA chunk (Hnm_DecodeAudio 0x40c783: Apc_InitState on the AA header, then
  `(AA_payload * 2 - 0x40) / channels` samples). Each later frame decodes its BB chunk
  into the next of 8 staging slices and Hnm_QueueAudio (0x40c8b5) copies one into slot
  `n & 31`; a frame without a sound chunk gives a slice of silence (memset 0).
  Corpus: every AA ADPCM size is a multiple of 32 and every BB is exactly that / 32
  (all 80 sound files); 1,836 samples per frame mono (58 files), 1,837 stereo (21), 1,764
  in `a03_05a.hnm`. The sample count in AA's APC header is the soundtrack's (e.g.
  `A13_051.HNM` 690,134 = `SOUND/a13_051.APC`) and the player does not use it.
- **Method:** decompiled 0x40c9aa, 0x40c783, 0x40c8b5, 0x4166f1; `hnm.py -v`.
- **Confidence:** proven

### E-0203 — Movie frame rate: a multimedia timer of 1000 / fps ms with sound, 80 ms without
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** Hnm_InitSound stores `fps = rate * channels * 16 / (AA_payload - 32)`
  (float at 0x4e1e58). Hnm_Open 0x40bf27: `FLD 1000.0 (0x4a2054); FDIV [0x4e1e58];
  CALL __ftol` gives the frame period; without sound 0x40bf59 stores 0x50 (80) instead.
  Timer_StartPeriodic (0x41059a) then runs `timeSetEvent(period, 5, …, periodic)`.
  Corpus: 22050 * 16 / 29376 = 12.010 fps → 83 ms (58 files), stereo 12.003 → 83 ms (21),
  `a03_05a` 12.5 → 80 ms, silent → 80 ms (15).
- **Method:** decompiled 0x40c9aa, 0x41059a; disassembled 0x40bf1e..0x40bf59.
- **Confidence:** proven

### E-0206 — ScummVM's HNMDecoder reads the corpus as is; IX frames carry a 28-byte header
- **Binary/file:** `Data/MOVIES`; `../scummvm/video/hnm_decoder.cpp`, `image/codecs/hnm.cpp`
- **Evidence:** ScummVM's HNM6 path reads the same header fields (audio flags +6, width,
  height, frame count, frame size +0x1C), superchunk `& 0xFFFFFF`, 4-byte-aligned chunks,
  `IX`/`IW` video and `AA`/`BB` APC sound (`APCAudioTrack`: rate `((flags >> 4) & 6) *
  11025`, stereo bit 7, the same as E-0202). `HNM6::DecoderImpl::decodeFrame` reads a
  24-byte header (quality, bit, motion, short-motion, JPEG, end offsets), then
  `end - 24` bytes. Corpus (`hnm.py`): in all 21,363 IX payloads the first stream offset
  is 28, the offsets ascend, `end` = payload size <= `max_frame_size`, and the u32 at +24
  (`unk_18`) = `end`, so ScummVM reads it into its buffer and never uses it. Audio:
  `(AA samples & 31) == 0` and `BB samples == AA samples / 32` in all 80 files, so
  `HNM6VideoTrack::newFrame`'s asserts hold. Difference: a silent HNM6 defaults to 66 ms
  per frame (the EXE: 80, E-0203).
- **Method:** read the ScummVM sources; `hnm.py`.
- **Confidence:** strong (no frame decoded here; the header and stream bounds match)

### E-0204 — CVY: frame count, buffer size, offset table, one HLZ stream per frame; the movie table decides which movie uses one
- **Binary/file:** `/MISSION.EXE`; `Data/MOVIES/*.CVY` (37)
- **Evidence:** Hnm_Open (0x40ba64), when the movie record's u32 at +0xC is set, opens
  `%sDATA\MOVIES\%s.CVY`, reads `u32 count`, `u32 size` (m__malloc(size): "could not
  alloc CVY buffer"), `count * 4` bytes of table ("CVY table"), and the rest of the file
  (file size - `count * 4 - 8`: "CVY lz-buffer"). Cvy_UnpackFrame (0x40c759) unpacks
  `lz + table[n]` into the buffer with 0x40918c → Hlz_Unpack 0x430700 (E-0101); Hnm_Open
  calls it for frame 0 and Hnm_Stream for each next frame. The records are the table at
  0x4a7a08 (stride 0x24, 68 entries; Movie_Open 0x414ace: `record = 0x4a7a08 + n * 0x24`):
  name, has_cvy (+0xC), x (+0x10), y (+0x14), w (+0x18), h (+0x1C), and +0x20 written by
  Hnm_Open (1 when the movie has sound). Movie_Open / Movie_Step (0x414bf8) blit the
  frame with Blit_SetMovieRect (0x46f716: `dst += y * pitch + x * 2`, source stride
  640 * 2) and Blit_MovieFrame (0x46fe55: copies `w` pixels by `h` lines from the start of
  the frame buffer), then, if has_cvy, Blit_CvyMask on the same rectangle. Movie_Step
  closes the movie early when Movie_Open's third argument was 0 and 0x40e4ef returns
  non-zero (not yet identified; probably input). Corpus
  (`cvy.py`): 37/37 files, every byte consumed (offsets multiples of 4, each stream ends
  0..3 bytes before the next offset or EOF, unpacked size <= `buffer_size`), 2,900
  frames; 24 table entries have has_cvy = 1 and a CVY file; 13 files are only in entries
  with has_cvy = 0; mask counts = HNM frame counts except `A03_023A` 44/118, `A03_023K`
  44/70, `A14_032A` 447/480 (all unused) and `A13_052B` 101/94.
- **Method:** decompiled 0x40ba64, 0x40c759, 0x414ace, 0x414bf8, 0x414cd9, 0x414d60;
  disassembled 0x46f716..0x46ff9d; table read from `Data/mission.___` (same MD5 as the
  Ghidra copy); `engines/peintre/tools/parsers/cvy.py`.
- **Confidence:** proven

### E-0205 — A CVY frame is a line-run mask painted in one colour (0x116A / 0x08AA) over the movie rectangle
- **Binary/file:** `/MISSION.EXE`; `Data/MOVIES/*.CVY`
- **Evidence:** Blit_CvyMask (0x46f78b → 0x46ff0d, assembly): colour in EAX doubled to a
  u32; `EDI = screen + y * pitch + x * 2`, `EBX = h`; per record byte `DL`: `DL > 0`
  → `EDI += DL * pitch`, `EBX -= DL`, stop when `EBX <= 0`; `DL = 0` → run the line saved
  at 0x4d3d1c again; `DL < 0` → save it, `DL & 0x7F` run bytes `CL`: `CL < 0` →
  `REP STOSD (CL & 0x7F) + 1`, else `EDI += (CL + 1) * 4`; then `EBX -= 1`. There is
  no end marker: the loop ends on the height. The callers (0x414ace, 0x414bf8, 0x414cd9,
  0x414d60) pass 0x116A when 0x6516bc = 0, else 0x08AA (the only uses of these constants in
  `.text`). Corpus: every mask line's runs add up to 320 u32 (a full 640-pixel line, so
  each line starts at x again); no mask starts with a repeat; bytes after 480 lines are
  zero padding (the empty masks); for the 24 opened files every mask covers >= h lines
  and paints only lines < h.
- **Method:** disassembly of 0x46ff0d; `cvy.py`.
- **Confidence:** proven (what the colour is for: Q-0150)

### E-0207 — APC: CRYO_APC 1.20 header + IMA ADPCM of samples / 2 + 1 bytes; 68/68 validate; the EXE decodes with the IMA shift-add
- **Binary/file:** `/MISSION.EXE`; `Data/SOUND/*.APC` (68)
- **Evidence:** Apc_InitState (0x4667ad) and Apc_GetInfo (0x4666dc) check `CRYO_APC`
  and `1.20` (`strncmp` 8 and 4 bytes), take stereo from bit 0 of +0x1C, samples per
  channel from +0xC (PCM size = `samples * (stereo ? 4 : 2)`), rate +0x10, start
  predictors +0x14 / +0x18, data at +0x20. The encoder Apc_Encode (0x4662bd, no callers)
  requires an output size of `pcm_bytes / 4 + 0x21` and writes the header the same way.
  Apc_Decode (0x465d8e): high nibble first (stereo: low nibble = right), diff =
  `(c & 4 ? step : 0) + (c & 2 ? step >> 1 : 0) + (c & 1 ? step >> 2 : 0) + (step >> 3)`,
  negated if `c & 8`, index += table 0x4b2900 (-1 -1 -1 -1 2 4 6 8), clamped 0..88,
  steps at 0x4b2790 = the 89-entry IMA table; the predictor is an int, stored to the
  output as a short without clamping. ScummVM `audio/decoders/apc.cpp` uses
  `(2 * (c & 7) + 1) * step / 8` (e.g. step 7, c = 7: 13 against the EXE's 11) and
  truncates its predictor to 16 bits at every sample. Corpus (`apc.py`): 68/68 files,
  `CRYO_APC 1.20`, 22050 Hz, flags 0 (mono), start predictors 0, ADPCM size =
  `samples * 2 * channels / 4 + 1` in every file; the extra byte is 0 when `samples` is
  even (36) and holds the last nibble with a zero low nibble when odd (32).
- **Method:** decompiled 0x4667ad, 0x4666dc, 0x4662bd, 0x465d8e; tables read with
  pefile; `engines/peintre/tools/parsers/apc.py`.
- **Confidence:** proven

### E-0209 — Sound paths: static WAV, streamed WAV ('_'), streamed APC ('!'), all through Snd_Load; streams are 22050 Hz mono 16-bit
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** Snd_Init (0x416650) registers Snd_Load (0x417084) and Adpcm_StreamInit
  (0x4176c6) as the Cryo DirectSound library's load callbacks (0x472bc0) and sets the
  primary format to 1 channel, 22050 Hz, 16 bits. Snd_PlayStreamApc (0x416874) and
  Snd_PlayStreamWav (0x416787) save the name's first letter (0x4e292c), replace it by `!`
  / `_`, and create a 0x10000-byte stream buffer; Snd_Load sees the marker, puts the
  letter back and forces the format to 1 channel, 22050 Hz, 16 bits: `!` opens
  `DATA\SOUND\%s.APC` (kind 2), `_` the WAV (kind 1, data chunk played raw). Without a
  marker it is a static WAV with the format of its `fmt ` chunk (Snd_CreateStatic
  0x416d9f). Streams refill 0x2000 PCM bytes at a time: raw WAV reads (0x416a39) or 0x800
  APC bytes decoded to 0x1000 samples (0x416bb9); past the length (`samples * 2` for
  APC, the data size for WAV) the rest is filled with silence and refills stop (no loop). One
  stream plays at a time (Snd_StopStream 0x4169ad first). A `++` name gives the movie
  buffer's format. Streamed WAVs are started only from the 3D scene code at 0x41d167,
  0x42b776 (musee) and 0x42ddbf (terrasse). `Wav_Open` (0x416e7f) has no callers.
- **Method:** decompiled the functions named; callers via Ghidra references.
- **Confidence:** proven

### E-0208 — WAV: plain RIFF PCM, 16-bit 22050 Hz (118 mono, 4 stereo); the game reads fmt and data only; 122/122 validate
- **Binary/file:** `/MISSION.EXE`; `Data/SOUND/*.WAV` (122)
- **Evidence:** Snd_Load (0x417084) requires `RIFF` and `WAVE` ("not a wav file"),
  then walks chunk headers: `fmt ` must be >= 14 bytes ("corrupted header"); it keeps
  channels (+2), rate (+4) and bits (+0xE), never the format tag; `data` gives the
  file position and size; it returns once both are seen, so later chunks are not read.
  Corpus (`wav.py`): 122/122 files, RIFF size = file size - 8, chunks walked to EOF with
  even padding; format tag 1 (PCM), 16 bits, 22050 Hz in all; 118 mono, 4 stereo
  (`A03_06I`, `J`, `K`, `L`); `fmt ` of 16 bytes (106) or 18 with cbSize 0 (16); chunk
  orders `fmt data` (82), `fmt data LIST` (22), `fmt data LIST cue LIST` (10),
  `fmt data smpl LIST` (7), `fmt data cue LIST plst` (1).
- **Method:** decompiled 0x417084; `engines/peintre/tools/parsers/wav.py`.
- **Confidence:** proven

### E-0330 — auberge (scene 1): object/anim tables, entry, clicks, zones 20 and 21, box sets BOXBAS/BOXHAUT
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init `0x41a0b0`, per frame `0x41a42b`, anim step `0x41a2ab`, sounds
  `0x419fb3`, `LoadBoxAuberge` `0x419f0e`, `LoadAnimsauberge` `0x419fde`, box-set switch
  `0x419e50` (removes the current set with `0x432e40`, registers `BOX.3DI` / `BOXBAS.3DI` /
  `BOXHAUT.3DI` with `0x432e10`, keeps the index in `DAT_004e312c`). Object table
  `0x4a9950` (12 × 0x3c, count `0x4a9948`), anim table `0x4a9c28` (3 × 0x78, count
  `0x4a9c20`), dumped from .data. Click targets by name (`porte01`, `porte02`,
  `saccoche`, `sac`, `sac01`, `stetoscop`, `casquette`, `tableau`, `portebas`,
  `portehaut`) recovered with `build/pw-decomp/calls.py` at 0x41a4f0..0x41a66e; zone
  numbers 0x14 and 0x15 written to `DAT_00502860` with mode 1. `portehaut`'s click writes
  `DAT_004a9a72` (= `portebas` +0x32). Entry tests sunflowers = 5, the frame tests 0x22.
- **Method:** decompiled the functions named (listings in `engines/peintre/notes/decomp/`);
  table dumps with a .data reader over `Data/mission.___`.
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/auberge.md`

### E-0331 — cafe (scene 5): tables, the key carry, the cue and shadow, the clock timer, the mirror by camera z, zones 4, 5, 6
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init `0x41b77d`, per frame `0x41bbcf`, anim step `0x41ba80`, sounds
  `0x41b5a0`, clock UV callback `0x41b613` (thunk `0x40160e`, applied through `0x4399d0`),
  `LoadAnimscafe` `0x41b6ab`. Object table `0x4aa050` (15 × 0x3c), anim table `0x4aa3d8`
  (`billard.3da` on `ke`, `portebar.3da` on `barporte`). Mirror texture thresholds on
  `DAT_00651356`: 0xaf1, 0x8fd, 0x7d1, 0x321, 0x1f5, 0x72 (0x41c19d..0x41c35a); clock step
  when `DAT_00650fd8 - DAT_00650fd4 > 199` (unsigned). Zones 5 (`gant`), 6 (`mirroir`,
  cursor 3 or 0x3c), 4 (`lampe4`).
- **Method:** as E-0330.
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/cafe.md`

### E-0332 — chambreb (scene 6 with DAT_004abd14 = 1): 27 objects, 6 tracks, zones 7..11, shoes and mirror unlocked by the 2D returns
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init `0x41c979`, per frame `0x41d167`, anim step `0x41cee9`, sounds
  `0x41c810`, `LoadAnimschambreb` `0x41c8a7`. Object table `0x4aa880` (27 × 0x3c; entries
  10 `mirroircas` and 19 `mirroirmor` start hidden), anim table `0x4aaed8` (`chaise`,
  `chaussur` on `perpompe` with playing word 1 in .data, `mirroir` on `mirroircas`,
  `papier`, `porte`, `tiroir`). Zones: `oreiller` 7, `tabpay` 8, `TIROIR` 9, `tab02` 10,
  `tab01` 11. `DAT_004abd50` and `DAT_004abd4c`/`DAT_004e30f4` are set by the 2D return
  `0x42f2c2` for zones 8 and 11. No write of `mirroir.3da`'s playing word (`0x4ab03c`) other
  than := 0 in the decompiled 3D code (Q-0220).
- **Method:** as E-0330.
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/chambreb.md`

### E-0333 — chambrev (scene 6 with DAT_004abd14 = 0): one door track, exit to maisonj
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init `0x41dd7f`, per frame `0x41ded8`, anim step `0x41de65`, sounds
  `0x41dc70`, `LoadAnimschambrev` `0x41dcad`; objects `porte`, `porte02` (`0x4ab5c8`),
  track `portev.3da` on `porte` (`0x4ab648`). The callbacks are installed only by
  `0x41fda9`'s 7 → 6 case when `DAT_004abd14` = 0 (thunks `0x40188e` → 0x41dd7f,
  `0x40111d` → 0x41ded8).
- **Method:** as E-0330.
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/chambrev.md`

### E-0334 — champ (scene 12): scythe, gun and crows, zones 22 and 24, walk-out exits
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init `0x41e383`, per frame `0x41e5de`, anim step `0x41e4cc`, sounds
  `0x41e250`, `LoadAnimschamp` `0x41e2b1`. Objects `faux`, `coclicot`, `gun`, `sabots`
  (`0x4ab750`); tracks `korbeaux.3da` on `corbopere`, `faux.3da` on `animfaux01`
  (`0x4ab848`). `faux` shown only when `DAT_004abbd4` = 4. Exits: `DAT_00651352` < −16000
  → 12 → 13; `DAT_00651356` < −0x157c → 12 → 11.
- **Method:** as E-0330.
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/champ.md`

### E-0335 — eglise (scene 13): kite and sheaf, zone 23, walk-out exits
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init `0x4242ed`, per frame `0x424467`, anim step `0x4243cb` (frame +=
  elapsed >> 1, reset on equality), sounds `0x4241f0`, `LoadAnimsEglise` `0x42421b`.
  Objects `cerf`, `gerbe`, `eglise10` (`0x4ac408`); track `eglise.3DA` on `cerf`, playing
  word 1 in .data (`0x4ac534`). Exits: `DAT_00651352` > −2000 → 13 → 12; `DAT_00651356`
  > 0x5fb4 → 13 → 11.
- **Method:** as E-0330.
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/eglise.md`

### E-0336 — hopiext (scene 2): bell, gate and box set BOX1, zone 14 within 1500, exits to hopiint and pont
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init `0x424af7`, per frame `0x424d93`, anim step `0x424c4c`, sounds
  `0x424aa8`, `LoadBoxHopiExt` `0x424978`, box-set switch `0x4248f0`,
  `LoadAnimsHopiExt` `0x4249d6`. Objects (`0x4ac5e0`, 11 × 0x3c) and tracks `grille.3da`
  on `ciel`, `cloche.3da` on `cloche` (`0x4ac878`). Distance limit: float 1500.0 at
  `0x4a2534` compared with √(x² + z²) of `0x436200`'s output. Exit: `DAT_00651356` < −1000
  → 2 → 9; `porteent` → 2 → 8.
- **Method:** as E-0330.
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/hopiext.md`

### E-0360 — hopiint (scene 8): wardrobe, four items, zones 13 and 15, PLAK exit within 3000
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init `0x425541`, per frame `0x42579a`, anim step `0x4256af`, sounds
  `0x4254f2`, `LoadAnimshopiint` `0x425420`. Objects `0x4acb08` (9 x 0x3c: `ARMOIRE`,
  `LAMPE`, `BONNET`, `CROIX`, `BOUGIE`, `MIRROIRVG`, `FOU`, `PLAK`, `ECHIK`), tracks
  `hopiint.3da` on `ARMOIRE`, `fou.3da` on `FOU` (`0x4acd28`). Items: `BOUGIE` 22, `LAMPE`
  21, `BONNET` 20, `CROIX` 23. Zones: `MIRROIRVG` 15, `FOU`/`ECHIK` 13. `PLAK` → 8 → 2 when
  √(x² + z²) of `0x436200`'s output < 3000.0 (`0x4a2538`); `fou.3da`'s playing word
  (`0x4ace14`) := that distance to `ECHIK` < 1500.0 (`0x4a253c`), every frame.
- **Method:** decompiled with PyGhidra `decompile_one.py` (read-only copy of Peintre.gpr);
  call arguments the decompiler dropped read from the pushes before each call (capstone);
  tables read from .data through pefile's mapped image.
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/hopiint.md`

### E-0361 — jardin (scene 11): 0x14/0x34-byte tables, gate box set, kite, butterfly timer, zone 19, three exits
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init `0x426d9b`, per frame `0x427069`, anim step `0x426f34`, sounds
  `0x426c7a`, box sets `0x426b70`/`0x426c56`, `LoadBoxJardin` `0x426bf8` (`BOX1.3DI`),
  `LoadAnimsjardin` `0x426cc9`. Object table `0x4ad080`, 8 x 0x14 bytes (cursor +0xa, handle
  +0xc, hidden +0x10: `0x426d9b`, `0x427069`); anim table `0x4ad128`, 5 x 0x34 (node name
  +0xf, handle +0x20 .. playing +0x30: `LoadAnimsjardin`, `0x426f34`). Items: `rato` 30,
  `fuzz`/`aild`/`ailg` 29. `partoche` zone 19; `porte01`/`porte02` → 11 → 1. Position exits:
  z < 300 and x > 10000 → 11 → 13; z < -500 and x < -0x2454 → 11 → 12. Butterfly timer
  `DAT_00599064`/`DAT_00599074` (5, += 0x14). `papiyon3.3da`'s playing word (`0x4ad228`) is
  not written by any decompiled 3D function (Q-0236).
- **Method:** decompiled with PyGhidra `decompile_one.py` (read-only copy of Peintre.gpr);
  call arguments the decompiler dropped read from the pushes before each call (capstone);
  tables read from .data through pefile's mapped image.
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/jardin.md`

### E-0362 — maisonet (scene 3): hen and bird by distance, spade reveals the earth, zone 1, door within 5000
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init `0x4279a3`, per frame `0x427e04`, anim step `0x427b98` (tracks 2, 3
  step by elapsed >> 1, at least 1), sounds `0x427870`, `LoadAnimsMaisonet` `0x4278d1`.
  Objects `0x4ad390` (7 x 0x40), tracks `0x4ad558` (`poule2`, `pelle`, `oisaller`,
  `oisrturn`). Items: `plume` 2, `terre` 1. `nid` zone 1; `porte04` → 3 → 4 when the distance
  < 5000.0 (`0x4a2544`). Hen starts within 2000.0 (`0x4a2548`) of `poule`; bird within 5000
  of `nid` (handle `0x4ad508`). The "dug" pose adds track 0's length (`DAT_004ad5c4`) to
  track 1's base (`0x4279a3`).
- **Method:** decompiled with PyGhidra `decompile_one.py` (read-only copy of Peintre.gpr);
  call arguments the decompiler dropped read from the pushes before each call (capstone);
  tables read from .data through pefile's mapped image.
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/maisonet.md`

### E-0363 — maisonj (scene 7): pots, rain movie, world map textures, DAT_004abd14 := 1, gate/door box sets, zone 12, three edge exits
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init `0x42897f`, per frame `0x428e63`, anim step `0x428c8c`, sounds
  `0x4287d1`, `LoadBoxMaisonj` `0x4286e2` (`BOX1..3.3DI`), box sets `0x4285e0`/`0x428904`,
  `LoadAnimsmaisonj` `0x428832`. Objects `0x4ad8d0` (8 x 0x3c, `nuages` hidden), tracks
  `0x4adab8` (`escargot`, `nuages`, `portail`, `porte-mj`, `train` on `TRAIN02` playing in
  .data). `pot01` plays `pluie` (`Hnm_AllocDecBuffers` + `0x42f6a0`, mode 2) while
  `DAT_0059905c` = 0; `pot02` swaps `WMAP0n` → `JMAP0n` on `world` (`0x435dc0`) and sets
  `DAT_004abd94`, `DAT_004abd14`. `escargot` item 11; `pendule` zone 12. Exits: z < -0x30d4
  → 7 → 9; x < -0x2134 → 7 → 10; -0x1859 < x < -6000 and z > 2000 → 7 → 6. Train step:
  `pastrain` once when frame > 0x46, playing word cleared at the end. `nuages.3da`'s
  playing word (`0x4adba4`) is written by no decompiled 3D function (Q-0236); no maisonj
  code sets 7 → 2 although `0x41fda9` has that arrival (Q-0237).
- **Method:** decompiled with PyGhidra `decompile_one.py` (read-only copy of Peintre.gpr);
  call arguments the decompiler dropped read from the pushes before each call (capstone);
  tables read from .data through pefile's mapped image.
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/maisonj.md`

### E-0364 — mangeurs (scene 4): stove, faggot and log carried to the fire, baby/window, kettle, zones 2 and 3
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init `0x4298e5`, per frame `0x429dd6`, anim step `0x429b94`, sounds
  `0x429758` (9), `LoadAnimsmangeurs` `0x429813`; UV callbacks `0x4296d0`, `0x4296e7`,
  `0x4296fe`, `0x42972b` (thunks `0x40110e`, `0x401663`, `0x40100f`, `0x40109b`). Objects
  `0x4ae060` (12 x 0x3c, `vapeur` hidden), tracks `0x4ae338`. Carry: `fagot` on `fire` →
  `finfeu`, `DAT_004abc3c`; `buche` on `fire` → `feu` looped, `DAT_004abc2c`, `DAT_004abc18`;
  else `0x4359a0(DAT_00502a80)`. Items: `theieres` 3, `patat01` 4. Zones: `bersso` 2, `POT` 3.
  `porte` → 4 → 3. Timers: baby after `DAT_00599024` > 0x32, window auto-shut after
  `DAT_00599034` > 500, steam after `DAT_00599040` > 0x96. `DAT_004abc08` is only read at
  entry and cleared by the cuckoo in 3D code (Q-0235); tracks `buche`, `chaise`, `fagot`
  have no writer of their playing word (Q-0236).
- **Method:** decompiled with PyGhidra `decompile_one.py` (read-only copy of Peintre.gpr);
  call arguments the decompiler dropped read from the pushes before each call (capstone);
  tables read from .data through pefile's mapped image.
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/mangeurs.md`

### E-0365 — pont (scene 9): crank handle carried to the pulley lowers the bridge, trapdoor, apples by distance, zone 18
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init `0x42cfe2`, per frame `0x42d489`, anim step `0x42d26a`, sounds
  `0x42ce66`, `LoadBoxPont` `0x42ce08` (`BOX2.3DI` = set 1), box sets `0x42cd80`, handle fit
  `0x42cf99`, `LoadAnimspont` `0x42cec7`. Objects `0x4af610` (7 x 0x3c), tracks `0x4af7b8`
  (`pond`, `arbres` on `ciel`; `trappe`; `pommes` on `apple01`; `train` on `train01`). Items:
  `apple01` 7, `encre01` 28; the `de` branch (item 26) is unreachable (`de` not in the
  table). `chemise` zone 18. Apples within 2000.0 (`0x4a255c`). Exits: x > 12000 → 9 → 7;
  x > 0x157c and z > 11000 → 9 → 2.
- **Method:** decompiled with PyGhidra `decompile_one.py` (read-only copy of Peintre.gpr);
  call arguments the decompiler dropped read from the pushes before each call (capstone);
  tables read from .data through pefile's mapped image.
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/pont.md`

### E-0366 — terrasse (scene 10): awning crank, die/letter/spectacles, zones 16 and 17, doors to the café
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init `0x42ddbf`, per frame `0x42e023`, anim step `0x42df65`, sounds
  `0x42dcb0`, `LoadAnimsterrasse` `0x42dced`. Objects `0x4afc08` (9 x 0x3c), track
  `terrasse.3da` on `storeho` (`0x4afe28`). First visit streams `apierre`
  (`Snd_PlayStreamWav`, `DAT_004abd78`). Items: `lettre` 27, `lunette` 17, `de` (via
  `platode`) 26. Zones: `KASKET` 17, `drapo` 16 (needs `DAT_004abd74`). `porte01`/`porte02`
  → 10 → 5; z < -0x9c4 → 10 → 7.
- **Method:** decompiled with PyGhidra `decompile_one.py` (read-only copy of Peintre.gpr);
  call arguments the decompiler dropped read from the pushes before each call (capstone);
  tables read from .data through pefile's mapped image.
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/terrasse.md`

### E-0400 — Boot order: registry, players, player screen, DirectInput, paths/DirectDraw, resume file, loading screen, intro
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** WinMain 0x42e97f (called from the CRT entry 0x476510): `App_Init` 0x4180c0
  (Registry_Read 0x418416, USERS.BIN read 0x41889c, `Users_CheckSessions` 0x41861d, window
  class `WC_MS_ACCUEIL` with WndProc 0x418c21 via thunk 0x401654, message loop until
  message 0x502 whose wParam/lParam are kept at 0x4e298c / `*param_2`; lParam 0 → 0x4187ba
  deletes the player's saves; 0x418966 writes USERS.BIN; `DI_Create`, mouse 0x472590(0, 0xD)
  and 0x4726a0, keyboard 0x472a20(5) and 0x472b10); then 0x470970(0x1000000),
  `SetWindowLongA(GWL_WNDPROC, 0x40139d → 0x42fbd6)`, `App3D_InitPaths` 0x42eb21 (0x4712e0
  with 640, 480, 16; 0x472240 returning 1 → 0x6516bc = 1; 0x40fb60; `Snd_Init`; two page
  clears), `Load3DGGame` when lParam = 1, else 0x28 zero ints at 0x651220; if 0x50273c = 0:
  `LoadTga2("Loading")`, blit, mode 0, 0x41fda9; then mode 2 and
  `Hnm_AllocDecBuffers(hwnd, "intro")`, then the `GetMessage` loop.
- **Method:** decompiled 0x42e97f, 0x4180c0, 0x42eb21 (PyGhidra, `notes/decomp/`).
- **Confidence:** proven

### E-0401 — Registry: HKLM\SOFTWARE\Cryo\Mission Sunlight\{Path: Target, CD; Language: LOC; Install Level: IL}
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** Registry_Read 0x418416 opens key 0x4a9688, subkey "Path" (0x4a96a8): value
  "Target" (0x104 bytes → 0x6514c0, then `lstrcatA "\"`), value "CD" (0x4a96bc, 0x80 bytes
  → 0x6515e0); subkey "Language", value "LOC" (DWORD → 0x6515c4); subkey "Install Level",
  value "IL" (DWORD → 0x651464). Any failure returns 0 and App_Init calls FatalError.
- **Method:** decompiled 0x418416; strings read with pefile.
- **Confidence:** proven

### E-0402 — USERS.BIN = u32 count + 40-byte records {name[32], volume, view size}; player screen controls and outcomes
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x41889c reads `%sSAVE\USERS.BIN` ("rb"): u32 into 0x4e2994, then count ×
  0x28 bytes into 0x4e29c8; a missing file leaves 0 players. 0x418966 writes the same
  ("wb"). Record fields: name at +0 (0x4183a7, `lstrcpyA`); +0x20 read by `Snd_Init` into
  the volume 0x4e2908 (0x4183d7) and written by 0x416ded as `(v - 100) * 50` (0x418400);
  +0x24 view size (0x4183c4 / 0x4183ea; 0x42f515 maps 0..3 to `FUN_00435170` 640×480,
  512×384, 400×300, 320×240). Accueil_WndProc 0x418c21: WM_CREATE loads ACCUEIL_BMP,
  BOUTONS_BMP, font "Trobo" 16, creates buttons 0x66 (0x197, 0x18c, 0x24×0x17), 0x67 (0x1d4,
  0x18c, 0x48×0x1b), one per player 0x68+i (0x5a, 0xd9 + 0x22 i, 0xa2×0x1b), edit 0x65
  (0x158, 0xce, 0xa3×0x1a, EM_LIMITTEXT 20), all relative to the centred 640×480;
  WM_DRAWITEM blits BOUTONS_BMP (x 0 / 0x28, y 0 / 0x1c when selected) or the name
  (colours 0xd6c6b5 / 0xffffff on brush 0x785400); WM_COMMAND 0x66: `__strcmpi` against
  the list; known → post 0x502 (index, 1); new with count < 5 → append with +0x20 = +0x24
  = 0, post (index, 0); count = 5 → ACCUEIL2_BMP, edit destroyed, selection 0; in that mode
  OK copies the name into the selected slot, zeroes +0x20/+0x24, posts (slot, 0); 0x67 →
  WM_CLOSE; key-up Enter/Escape → 0x66/0x67 (edit subclass 0x418b31); background brush
  0x502810.
- **Method:** decompiled 0x41889c, 0x418966, 0x4183a7..0x418400, 0x418c21, 0x418a2d,
  0x418b31, 0x419684, 0x416ded, 0x416e0f, `Snd_Init`.
- **Confidence:** proven

### E-0403 — The player screen's bitmaps are 8-bit 640×480 / 160×100 resources in the EXE
- **Binary/file:** `Data/mission.___` `.rsrc`
- **Evidence:** RT_BITMAP `ACCUEIL_BMP` (RVA 0x2b8600, 308,138 B, 640×480 8 bpp),
  `ACCUEIL2_BMP` (0x3039b0, 308,002 B, 640×480 8 bpp), `BOUTONS_BMP` (0x34ecd8, 17,064 B,
  160×100 8 bpp), RT_GROUP_ICON `GAME_ICON`; all language 1036. No WAVE resource.
- **Method:** `pefile` resource walk.
- **Confidence:** proven

### E-0404 — Data paths come from the registry; PEINTRE.INI is never read
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** App3D_InitPaths 0x42eb21: 0x599460 = Target + `DATA\GRAPHS_2D\`, 0x5bae40 =
  CD + `DATA\SCENES_3D\`, 0x502880 += `\DATA\`, 0x598ee0 = 0x502880 + `\SCENES\`, 0x598aa0 =
  Target + `SAVE\`; the 2D loaders format `%sDATA\...` with 0x6514c0 (Target).
  ReadPeintreIni 0x41ed13 (which would fill 0x502880) is reached only by the thunk
  0x40128a, and no `call`/`jmp` rel32 in `.text` and no absolute pointer in any section
  targets that thunk or the function.
- **Method:** decompiled 0x42eb21, 0x41ed13; scan of every E8/E9 rel32 target and every
  4-byte value in the image.
- **Confidence:** proven

### E-0405 — Window procedure 0x42fbd6 dispatches on the mode byte 0x598cb0; end of intro and end movies
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x42fbd6: modes 0/4 → 0x42f988; 1/3 → `MainWndProc` 0x4122bb unless
  0x4b0058 ≠ 0 (then 0x42f755 → Entry2D); 2 → on 0x500 `FUN_00472710` (DirectInput mouse,
  button 0 → 0x5b7fac) or `Hnm_Stream` = 0 closes the movie (0x40ba0b); then: 0x4aba5c = 1
  → play `cinefin2` once (0x4e3148 1 → 2), afterwards mode 1 + `Timer_Begin`; else
  0x502864 = 0, 0x4e4580 = 0, 0x50273c = 0 → mode 0, 0x41fda9, `Timer3D_Begin`; 0x4e4580 =
  0 and 0x50273c = 1 → mode 1, `Entry2D(hwnd, 0x502860, 0x651220, 0x4aba40, 0x36c)`.
  0x42f2c2 plays `cinefin` when the zone left is 0x15 (0x4aba5c = 1, 0x4e3148 = 1).
- **Method:** decompiled 0x42fbd6, 0x42f2c2, 0x42f755.
- **Confidence:** proven

### E-0406 — The 2D timer: 40 ms multimedia timer posting 0x500 / 0x503 / 0x504 unless 0x4e22fc is set
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x410365 → 0x41059a(0x28): `timeSetEvent(40, 5, 0x401181 → 0x41224c)`;
  0x40fccb: `timeSetEvent(0x28, 5, 0x4012f3 → 0x412271)`; Timer_Begin 0x40fbe9: callback
  0x40183e → 0x412296. Each callback posts 0x500 / 0x503 / 0x504 to 0x651694 when 0x4e22fc
  = 0; 0x41222e / 0x41223d set / clear it around loads.
- **Method:** decompiled the functions; thunks resolved with capstone.
- **Confidence:** proven

### E-0407 — 2D input: relative DirectInput mouse ×2 into a software cursor; keys fire on release; Esc, Space, Backspace, arrows
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x40e3e1 adds `2 * dx, 2 * dy` from 0x472910 (GetDeviceState, 16 bytes)
  and clamps to 0..0x27f / 0..0x1df; 0x40e4ef returns `rgbButtons[0] >> 7` via 0x4727d0.
  MainWndProc toggles buffer 0x4e27c4 and reads 256 bytes into 0x4e2350 + 0x100·buffer
  (0x472b80); 0x410c21(k) is true when the key was down in the other buffer and is up now.
  Calls in MainWndProc (disassembly): 0x410c21(1) → 0x4e25e4, (0x39) → 0x4e2634, (0x0e) →
  0x4e2678. 0x40dcf3 tests 0xc8, 0xd0, 0xcb, 0xcd with 0x410c8e / 0x410cb9.
- **Method:** decompiled 0x40e3e1, 0x40e4ef, 0x410c21, 0x4727d0, 0x472910, 0x472b80,
  0x40dcf3; capstone on 0x4122bb.
- **Confidence:** proven

### E-0408 — Entry2D contract; zone table 0x4a6b18 (25 × 0x6C) and object table 0x4a75a8 (35 × 0x20); handlers only through the table
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** Entry2D 0x40fdc6 (Ghidra shows a thiscall; the real arguments are hwnd,
  zone, flags, state, size): zone > 0x19 → FatalError "Entrée 2D: n° de ZA (%u) pas
  valide"; builds 0x4e2688 from the 35 flags; 0x410365; zone 0x15 →
  `Save_WriteGGame(state, size, 0)`. 0x410365: `0x4e266c = 0x4a6b18 + zone * 0x6c`,
  `Tgp_Load2(entry + 0x14)`, view rects from +0x38/+0x3c, per object `+8 + 4i` → 0x414a95.
  MainWndProc calls `entry[0x12]` (+0x48, args object, slot), `entry[0x13]` (+0x4c, on
  Backspace), `entry[0x14 + slot]` (+0x50, args tick, &result); +0x40 indexes TOURN and
  its rects, +0x44 indexes 0x4e2318, +0x5c is patched at byte 99 to 'a'/'b'/'c' (0x414e3a,
  0x414ea8), +0x68 is set when the zone is done and saved (0x40ff77). Rows read from
  `mission.___` `.data` (file offset = VA − 0x401000); row 25 would start at 0x4a75a4,
  inside the object table. Object k at 0x4a75a8 + 0x20 k: id, name pointer (0x4a8398 + 8k,
  `OP_GENE`/`OPnn`), sprites +8 CapsE (0x414a95), +0xc CapsOP, +0x10 CapsAO, +0x14 CapsAC
  (0x4149d1), +0x18 placed, +0x1c sound (0x4148a5). No handler has a direct caller
  (function-dump.tsv); 0x403ddb (zone 9's onPlace, target of thunk 0x40122b) is not a
  Ghidra function: 34 bytes, `push 0; push 0x3b; call Movie_Open`, then stores its args.
- **Method:** decompiled 0x40fdc6, 0x410365, 0x410624; table dumps with pefile; thunk
  targets with capstone; `define_and_decompile.py` on 0x403ddb.
- **Confidence:** proven

### E-0409 — MainWndProc 0x4122bb: a per-tick state machine on 0x4e27e4
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** message 0x500 reads input, then `switch (0x4e27e4)` over states 0..0x24
  as tabled in `docs/spec/ui.md`, then the magnifier step, 0x410e30 (bar), 0x410d68
  (dragged sprite), 0x41474a (cursor + `Display_Flip`). E.g. state 8: 0x4116a8 hit test,
  0x4112f7 removes from the list, `CapsOP` start, `placed` = 1, 0x4e2658 = 1; state 0xF:
  result 0x4e2640 = 0 and 0x4e2658 ≠ 0 → back to the bar; state 0x21: 0x410b80, 0x42eede,
  `Save_WriteGame(0x4e267c)`.
- **Method:** decompiled 0x4122bb; argument pushes checked in its disassembly.
- **Confidence:** proven

### E-0410 — Inventory bar: geometry tables 0x4a68e8..0x4a6aa8 and the 30-step slide
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x40fb86 fills 0x4e2550[30] with `__ftol(cos(π/2 − 3° i) · 60)` (0x4a2058
  = 0.0523598775, 0x4a2060 = 60.0; 0x475794 uses `fcos`); 0x410e30 sets the bar y
  0x4e2714 = 0x1df − T[i] while opening (i up to 0x1e → 0x1a4) and closing (down to −1 →
  0x1e0). Tables (i32): arrow frames at (13, 0), (504, 0); arrow rects (13, 435, 23, 30),
  (509, 435, 22, 30); slot rects (88 + 70i, 436, 28, 27); icons (67 + 70i, 0); drag origins
  (101 + 70i, 30); zone slot drop rects (12, 53/143/233, 59, 58) at 0x4a69d8; slot draw
  (0, 29/116/222); placed-slot rects 0x4a6a20; fly-back origins (40, 83/172/263); Retour
  (605, 437, 24, 29), RetourM (11, 437, 24, 29), their sprites at (600, 435), (8, 432);
  counter (558, 21), pot (558, 2), pot area (590, 400, 45, 80); sunflower rects 0x4a6ab8,
  grab offsets 0x4a6ae8. 0x411514 scrolls when `(0x4e27e8 & 7) == 0`. Sprites and sounds
  from 0x414fbf, 0x4148a5.
- **Method:** decompiled 0x40fb86, 0x410e30, 0x411153, 0x411454, 0x411514, 0x411649,
  0x4113e0, 0x414fbf, 0x4148a5; tables dumped with pefile.
- **Confidence:** proven

### E-0411 — Magnifier states and the two views (panorama `<zone>b`, animation `<zone>a`)
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x4e2348: 0x411807(0,…) draws the last `LoupeOut` frame → 2; 0x4119c2 plays
  `LoupeOut` → 1; 0x41195b plays `LoupeIn` (+ `bar_outi`) → 0; the end of MainWndProc's
  0x500 turns 1 → 2 and 0 → 3 on even ticks. 0x411454 returns 2 for (x + 0x4e, y, 0x41,
  0x24) and 1 for (x + 2, …) when 0x4e2348 = 2. State 2: `Tgp_Load(entry + 0x2c)`,
  0x40dc22; state 1: 0x40dcf3 until a click. State 4: 0x409310(entry + 0x20)
  (`Tgp_Load2`, `Sprite_Open`, `pas_VG2`); state 3: 0x4093cb until it returns 1.
- **Method:** decompiled the functions; call arguments from the disassembly of 0x4122bb.
- **Confidence:** proven

### E-0412 — Object placement, slot run protocol and result
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** states 8, 10, 0xE, 0xD, 0xF, 0x10–0x12, 0xC, 0xB of 0x4122bb; 0x41170e draws
  CapsE (not placed) / CapsAC (slot = argument) / CapsAO (placed); fly-back in state
  0x11: `t = (sin(3π/2 − n·π/32) + 1) / 2` (0x4a2068..0x4a2088; 0x475b84 uses `fsin`),
  `x = bar·t + slot·(1 − t)`; state 0xF sets entry[0x1a] = 1 and goes to 0x1A when all
  zone objects have `placed` ≠ 0 and the zone is not 0.
- **Method:** decompiled 0x4122bb, 0x41170e, 0x4116a8, 0x4112f7, 0x41138b; disassembly
  0x413818..0x413940.
- **Confidence:** proven

### E-0413 — Sunflower sequence: PA<zone>a/b/c, TOURN<n>, POT, sounds pas_VG, tourneso, vase
- **Binary/file:** `/MISSION.EXE`; `Data/SPRITES`, `Data/SOUND`
- **Evidence:** 0x414e3a (PA..a, PA..b, `pas_VG`), 0x414ea8 (PA..c), 0x414f64 (`TOURN%u`
  with entry +0x40, `tourneso`), 0x4150b0 (`POT`, `vase`); states 0x1A, 0x16, 0x17, 0x18,
  0x1C, 0x1D, 0x19, 0x1B of 0x4122bb; the frame-12 test at 0x413ce9 stops 0x4e2664
  (`pas_VG`), state 0x19 starts it at frame 12; state 0x1C increments 0x4e2318[entry +
  0x44]. Corpus: `PA*A/B/C.SPR` for every zone with a Van Gogh name, `TOURN0..2.SPR`,
  `POT.SPR`, `PAS_VG.WAV`, `TOURNESO.WAV`, `VASE.WAV`.
- **Method:** decompiled; disassembly for thunk arguments; corpus listing.
- **Confidence:** proven

### E-0414 — Leaving a zone: 0x42f2c2(flags, counter, code) with -1, -2, -3 or a save number
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** state 0x20: 0x410624 (free), 0x410b80(0x4e2720), 0x42f2c2(0x4e2720,
  0x4e2318[entry + 0x44], 0x4e25dc). 0x4e25dc = −1 from Retour / Backspace / zone 0 /
  zone 21, −3 from RetourM, −2 / n from OptionMenu. 0x42f2c2 copies the flags to 0x651220,
  0x4abbd4 = counter; counter > 0x598fe0 → `0x4abb0c[zone] = 1` (u32, disassembly
  0x42f32e); −3 → 0x50273c = 0, later 0x4e3144 = 0 and 0x41fda9; −2 → PostQuitMessage;
  n ≥ 0 → Load3DGame(n); zone 0 → 0x4aba48 = 0x4aba4c = 1; zone 0x15 → `cinefin`.
- **Method:** decompiled 0x42f2c2, 0x410b80; disassembly.
- **Confidence:** proven

### E-0415 — Option menu 0x40ecd4: pages, rects, volume, view size, load list, quit
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x40e620 (`option`, `options`, `cursopt`, `lcaps`, `trobo12`, volume
  `0x416e0f() * 0xd3 / 100`, view size from the player, Save_ListGames), 0x40e976 (six rects
  0x4a65c0; volume bar 0x4a6660 → 10, knob 0x4a6670 moved by 0x4a6658 + v → 11; buttons
  1..3 ignored while the volume row is open), 0x40ea4f (0x4a66a0), 0x40ea9a (0x4a6730,
  arrows 0x4a6770/0x4a6780), 0x40eb34 (0x4a66f0), 0x40ebd9 (`lcaps` frame = slot at
  0x4a6710, "Game %u" at x 0x130 colour 0xce59), OptionMenu states 0..0x12 (load →
  `player * 100 + slot`; quit yes → 0x410b80/0x42eede when opened from 2D,
  `Save_WriteGGame(state, size, from2D)`, 0x418966, −2; credits `Credit%02u` 250 ticks),
  0x40e6fb (restore, volume `v * 100 / 0xd3`, view size). Backgrounds `load`, `scrsize`,
  `keyboard`, `quit`. Opened from 3D: 0x42edef → 0x40fccb (mode 3); on close 0x42f515(result).
- **Method:** decompiled; tables dumped with pefile; disassembly 0x4124b8.
- **Confidence:** proven

### E-0416 — Cursor table 0x4a64e8: 14 entries {frame, dx, dy} of Curseurs.SPR
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x40e25a(_, n) loads `0x4a64e8 + 12n` into 0x4e1fcc / 0x4e1fdc / 0x4e1fe0;
  0x40e2fc draws frame 0x4e1fcc at cursor − (dx, dy); 0x40e200 opens `Curseurs`. Uses:
  0x40dcf3 (1..8), 0x408118 (10), hit tests (11, 12), drags (13), waits (9).
- **Method:** decompiled 0x40e200, 0x40e25a, 0x40e2fc; table dump.
- **Confidence:** proven

### E-0417 — 2D movies are opened by index into the 0x4a7a08 table; the second argument forbids skipping
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** Movie_Open 0x414ace(n, p): record 0x4a7a08 + 0x24 n; 0x4e2300 = (p == 0);
  Movie_Step 0x414bf8 ends on a click only when 0x4e2300 ≠ 0. Generic slot functions:
  0x414dcc sets result 1 and returns Movie_Step's end; 0x414dec sets result 1, waits while
  0x651678 = 0 and no click, then stops the stream (0x4169ad). Each zone's movie index and
  flag: E-0426..E-0431.
- **Method:** decompiled 0x414ace, 0x414bf8, 0x414dcc, 0x414dec.
- **Confidence:** proven

### E-0418 — End credits: sound `Credits`, 16 pictures `Credit00..15`, 250 ticks each, then quit
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** MainWndProc 0x504: first 0x409600 (`Credits` static, looping), then
  0x409645(0x4e2634 = Space fired, disassembly 0x4125ec): `Credit%02u` via Tgp_Load2,
  > 0xfa ticks → next, 16 → end; a click or Space → end; the end waits for the button up
  and stops the sound; then 0x40fca8 and 0x42f508 (`PostQuitMessage(0)`). Corpus:
  `GFX/CREDIT00..15.TGP`, `SOUND/Credits.wav`.
- **Method:** decompiled 0x409600, 0x409645, 0x42f508; disassembly.
- **Confidence:** proven

### E-0419 — GAME save = 0x36C-byte 3D block + 0x100-byte 2D block; slot = object id; list = slots 1..34 by file time
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** Save_WriteGame 0x40ff77(slot): `%sSAVE\GAME%02u%02u.BIN` (player 0x41839d,
  slot); writes 0x4e2624 (0x4aba40) × 0x4e2610 (0x36c) bytes, then 0x100; its only call
  passes 0x4e267c, the current object (disassembly 0x4139e0). Save_ListGames 0x40e78a:
  slots 1..0x22 through 0x466f10 (file time), bubble sort on CompareFileTime > 0.
  Load3DGame 0x42ef0f(n): `%sSAVE\GAME%04d.BIN`, size < 0x801, 0x36c bytes to 0x4aba40,
  the rest to 0x40fed7, then Entry2D with +0x3e.
- **Method:** decompiled 0x40ff77, 0x40e78a, 0x42ef0f; disassembly.
- **Confidence:** proven

### E-0420 — GGAME resume file = u32 in_2d + the same two blocks; writers and reader
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** Save_WriteGGame 0x410153(state, size, flag): `%sSAVE\GGAME%u.BIN`, writes
  the flag (4 bytes), `size` bytes of state, 0x100 bytes. Callers: OptionMenu quit (flag
  = 0x4e2000, 1 when opened from 2D), Entry2D zone 0x15 (0), 0x42f873 (0; called from
  0x41bbcf, 0x426171, 0x429dd6, 0x42d489). Load3DGGame 0x42f111: size < 0x801; u32 →
  0x50273c, 0x36c → 0x4aba40, rest → 0x40fed7; returns 0, −1 (no file) or the size.
- **Method:** decompiled 0x410153, 0x42f111, 0x42f873; callers from function-dump.tsv.
- **Confidence:** proven

### E-0421 — The 2D block: 25 zone-done flags, 35 object-placed flags, 4 counters
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x40ff77 / 0x410153 build `u32[25]` from 0x4a6b80 + 0x6c i (zone +0x68),
  `u32[35]` from 0x4a75c0 + 0x20 i (object +0x18), `u32[4]` from 0x4e2318; 0x40fed7
  restores from offsets 0, 0x64, 0xf0.
- **Method:** decompiled.
- **Confidence:** proven

### E-0422 — 3D block fields touched by the save glue
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x42f755, 0x42f873, 0x42edef write +0x24..+0x2c and +0x30..+0x38 from the
  s16 at 0x651346 and 0x651352 (movsx), +0x3c/+0x3d/+0x3e from bytes 0x4e3144/0x4e3140/
  0x502860, +0x40 (0x8c bytes) from 0x651220; Load3DGame/Load3DGGame restore them into
  0x5b7fb0.., 0x5b7f80.., 0x4e3144, 0x4e3140, 0x502860, 0x651220, reset byte +0x194
  (0x4abbd4) when 3 with +0x1a0 = 0 or 15 with +0x1a4 = 0, and copy byte +0 to the player's
  view size. 0x42f2c2 writes +0x08, +0x0c, +0x1c, +0xcc + 4·zone, +0x194. App3D_InitPaths
  zeroes 100 bytes at +0xcc.
- **Method:** decompiled; field widths from the disassembly.
- **Confidence:** proven

### E-0423 — Loading a game always resumes inside the saved 2D zone
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** Load3DGame 0x42ef0f ends with mode 1, `Timer3D_End`, `Entry2D(hwnd, +0x3e,
  0x651220, 0x4aba40, 0x36c)`; GAME files are written only in state 0x21 of the 2D shell
  (Save_WriteGame's single caller).
- **Method:** decompiled 0x42ef0f; callers of 0x40ff77.
- **Confidence:** proven

### E-0424 — Users_CheckSessions discards players without GGAME and does not rename the later players' files
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x41861d: for i < count, `GGAME%u` missing → delete `GAME%02u%02u` for
  0..0x22, MessageBox 0x4a9710 / 0x4a9770, count − 1, `memmove` of the later 0x28-byte
  records, i − 1. No file is renamed. 0x4187ba (new player) deletes `GGAME%u` and
  `GAME%02u%02u` 0..0x22 of the chosen index.
- **Method:** decompiled 0x41861d, 0x4187ba.
- **Confidence:** proven

### E-0425 — Voice and movie waits used by the puzzles
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x416874(name) starts the streamed voice (`!` prefix, E-0209) and clears
  0x651678; 0x4169ad stops it; 0x414dec waits while 0x651678 = 0 and 0x40e4ef = 0. The
  puzzles' hint timers are tick counters compared with 0xfa, 0x271 or 500 (per zone, E-0426..
  E-0431).
- **Method:** decompiled 0x416874, 0x4169ad, 0x414dec and the puzzle functions.
- **Confidence:** proven

### E-0426 — A01 zones 1–2 (`games/mission-sunlight/docs/a01.md`)
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x40d0f0 (Movie_Open(0x1d, 0)); 0x40d112 (object 2 → voice `A01_031`;
  object 3 → background `a01_032a`, Movie_Open(0, 1), sprite `a01_032a`, `pt_clic1..3`,
  `reussit`), 0x40d1ef, 0x40d207, 0x40d293 (states 0..7 as written; piece table 0x4a62c0
  stride 0x28: x, y, pick rect, drop rect). Movies 0..6 = `A01_032a..f`, `A01_032l`.
- **Method:** decompiled; tables dumped with pefile.
- **Confidence:** proven

### E-0427 — A03 zones 4, 7, 12, 13, 16, 18 (`a03.md`)
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** zone 4: 0x4022c0, 0x402376, 0x40238e (0x4a4f88), 0x4023d9 (0x4a4fb8 +
  0x10·(f − 4)), 0x4023fa (0x4a5078 + 0x10·(f − 16)), 0x40241b; zone 7: 0x4029f5, 0x402ac2,
  0x402ada, 0x402b51, 0x402bc8 (0x4a5168), 0x402c20 (letters 0x4a5198 + 4h + 0x18·mask,
  movies 0x4a51a4 + 4h + 0x18·mask); zone 12: 0x404130; zone 13: 0x404152, 0x404217,
  0x40422f, 0x40429c (0x4a4f18), 0x404306 (0x4a4f48), 0x404351 (0x4a4f78), 0x404378 (hint
  start 0x177, limit 0x271); zone 16: 0x4055bb, 0x405659, 0x4056ac, 0x4056bb/0x405725
  (0x4a4b88 stride 0x38), 0x405766/0x4057be (0x4a4cd8/0x4a4ce8 stride 0x20), 0x405816
  (board rect 0x9e, 0xd2, 0x142, 0x96; `a03_05f/g/h` by attempts < 2, < 4, else); zone 18:
  0x405e8c, 0x405f26, 0x405f5b, 0x405f6a (windows 0x4a5138, rect 0x4a5158), 0x405fa6.
- **Method:** decompiled; tables dumped with pefile.
- **Confidence:** proven

### E-0428 — A04 zones 19, 22, 23 (`a04.md`)
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x4074c0 (object 0x1d → voice `A04_01`; 0x1e → Movie_Open(0x43, 0));
  0x407b83 (0x23, 0); 0x407ba5 (0x24, 0); slot functions 0x414dec / 0x414dcc (zone table).
- **Method:** decompiled.
- **Confidence:** proven

### E-0429 — A11 zone 3 (`a11.md`)
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x40d271: Movie_Open(0x3c, 0); slot function 0x414dcc.
- **Method:** decompiled.
- **Confidence:** proven

### E-0430 — A13 zones 5, 6, 8, 9, 10, 11, 14, 15, 17 (`a13.md`)
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** movie-only onPlace functions 0x4029b1 (0x15), 0x4029d3 (0x3d), 0x403ddb
  (0x3b), 0x40410e (0x3a), 0x40474b (0x25, 0x26), 0x405e6a (0x3f), all with 0; zone 8:
  0x403346, 0x4034f2, 0x403501, 0x4035fb (rects 0x4a4b50, answers 0x4a4b70, frame test
  0xf), 0x403a1a (hint counter +2 per tick, limit 0x271), 0x403215 (0x4a4a90, 0x4a4b30),
  0x402e76 (0x4a4a30, 0x4a4a80; frame formulas as written, including `(s ^ 1) + 10`
  without × 14), rect save/restore 0x46f7be/0x46f818 (0x6e, 0x1d, 0x1e2, 0x182); zone 10:
  0x403dfd, 0x403e7e, 0x403ea1, 0x403eb9 (0x4a4ed8), 0x403f04; zone 15: 0x404a47, 0x404b5f,
  0x404b77, 0x404793/0x404834/0x4048d0/0x40497d (0x4a4d98 stride 0x10, order 0x4a4e98,
  board limits 0x9c..0x1e3 × 0x1d..0x1ac, snap ±4), 0x404bde.
- **Method:** decompiled; tables dumped with pefile.
- **Confidence:** proven

### E-0431 — A14 zones 0, 20, 21, 24 (`a14.md`)
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** zone 0: 0x4119fc (Movie_Open(0x20, 1), 0x4e27c0 = 0), 0x411a28 (states
  0..0xC: views through 0x411454, 250-tick timeout, Movie_Open(0x21, 1), `a14_031c`,
  `A14_031a` frames at (0x1f, 0xc6), 0x4e2318[entry + 0x44] = 1, Movie_Open(0x22, 0),
  `a14_031d`, 40 ticks); zone 20: 0x407509 (start states 0x4e0538..0x4e0540 = 2, 2, 1),
  0x407617, 0x4076b2, 0x4076c1 (0x4a57d8), 0x40770c (goal array 0x4e0558: in `.bss`, past
  the 0x3c400 raw bytes of `.data`, and its only reference in `.text` is the read at
  0x407979; names 0x4a5808 + 8·state + 0x18·wheel; s5 ends at count > 0x32, s7 at count
  = 0x3c on the same counter); zone 21: 0x412065 (rect 0x4a6b08, movies 0x40, 0x41);
  zone 24: 0x407bc7 (calloc 0x2d420, last 3 bytes 0xff, brush = `Curseurs` frame 10 size
  via 0x40e2b8), 0x407d43, 0x407dd1, 0x407de0/0x407e38 (0x4a5850/0x4a5860 stride 0x20),
  0x407e83 (area 0x70..0x24f × 0x1d..0x1a0, stride 0x1df, done when < 0x2423 of 0xb508
  words ≠ −1), 0x40804c, 0x4080b6 (0x4a58f0), 0x408118 (drop point + 0x20, hint 0x7d /
  500).
- **Method:** decompiled; tables dumped with pefile; section sizes from pefile; `.text`
  scan for 0x4e0558.
- **Confidence:** proven

### E-0432 — The corpus holds no save file
- **Binary/file:** `engines/peintre/notes/corpus-md5.tsv`
- **Evidence:** no path containing `SAVE` and no `.BIN` file among the 877 files.
- **Method:** `grep -i "save\|\.bin" corpus-md5.tsv` (no match).
- **Confidence:** proven

### E-0300 — The 3D tick: a 66 ms multimedia timer posting 0x505, dropped while busy; elapsed ticks clamped to 1..10; one frame per handled tick
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** `Timer3D_Begin` 0x42fb5e: `timeBeginPeriod(0x42)`, `timeSetEvent(0x42, 5,
  0x40104b → 0x42f955, 0, 1)`; 0x42f955 increments 0x598ca4 and posts 0x505 unless 0x502a84.
  The window procedure 0x42fbd6 sends modes 0/4 to 0x42f988, which on 0x505 sets 0x502a84,
  reads the keyboard into buffer `0x5b7fc0 + 0x100 · (0x5bae2c ^= 1)` (0x472b80 =
  `GetDeviceState(256)`), sets 0x598ec0 = tick delta clamped to 1..10, then in mode 0 runs
  0x422aa6 + 0x41fda9 when 0x4e313c, 0x41fda9 when 0x502740 ≠ 0x598cb0, 0x4223e8 when
  0x4e4580 = 1; in mode 4 0x41f9f8 then 0x41faf9 when it returns 0; clears 0x502a84.
  WM_DESTROY → 0x42ed9c; WM_SYSCOMMAND 0xF140 swallowed. Frame 0x4223e8: 0x422b98, 0x4216b6,
  0x420e07, border fill (0x114a / 0x8aa by 0x5b7fa4), `0x4378f0(0x5baf80)`, 0x426171,
  cursor (0x424190), 480 rows of 0x500 bytes to the surface (0x472030/0x471fd0/0x471d40),
  keys 0x0E / 0x39 / 0x01 by 0x41ec7b, then `(*0x651358)()`. Debug flags 0x4e3104,
  0x4e3108, 0x4e310c lie in `.bss` (`.data` raw data ends at 0x4e0400) and a byte scan of
  `.text` finds one reference each (0x42260b, 0x422481, 0x42248f), all reads. 0x4221f6 = the
  same without 0x422b98 (camera from 0x651346.. through 0x422f30) and with `sablier` centred;
  sets 0x4b0058 in mode 1.
- **Method:** decompiled (listings in `engines/peintre/notes/decomp/`); thunk targets
  resolved from the `jmp rel32` stubs; byte scan of `.text` for the flag addresses.
- **Confidence:** proven
- **Doc:** `engines/peintre/docs/spec/movement.md` "The tick"

### E-0301 — Keyboard: two 256-byte DirectInput buffers; held = bit 7 now, released = up now and down before
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x41ece8(k) = `buf[cur][k] & 0x80`; 0x41ec7b(k) returns 1 only when
  `buf[cur][k] & 0x80` = 0 and `buf[prev][k] & 0x80` ≠ 0. Buffers cleared in
  `Alloc3DMemory` 0x422869, 0x42f2c2, 0x42f515.
- **Method:** decompiled.
- **Confidence:** proven
- **Doc:** `movement.md` "Keyboard"

### E-0302 — Walking: per-tick velocities with halving damping, +60 forward / ±40 yaw rate / ±30 pitch, direction (M[2], M[8]) of the angle matrix
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x422b98: damping of 0x651342 (|v| > 10 → `v -= v/2`, else 0), 0x651344
  (`vy -= vy/2`, then +5 when < 6), 0x65134e; keys 0xC8 (+0x3c while < 0x9c4), 0xD0 (-0x3c
  while > -0x9c4), 0xD1 (0x651340 and 0x651346 -0x1e while > -500), 0xC9 (+0x1e while < 500),
  0xCB (-0x28 while > -300), 0xCD (+0x28 while < 300); `0x651348 = (0x651348 + 0x65134e) &
  0xfff`; `0x43a780(pitch, yaw, roll, m)`; x += (m[2]·v) >> 15, y += vy, z += (v·m[8]) >> 15
  (signed shift with the +0x7fff bias = division toward zero); 0x422f30 sets the camera
  (0x436160 position, 0x4360f0 matrix) and copies the six values back. 0x43a780's nine terms
  as in the spec; 0x43a660 fills 0x6a7580 with `fcos(θ)·32768` and 0x6ab5a0 with
  `fsin(θ)·32768`, θ from 0 in steps of 2π/4096 for 4096 entries. `Alloc3DMemory` clears
  0x651340..0x651357 before the start camera is set.
- **Method:** decompiled; FPU constants read from `.rdata` (0x4a25e8 = 0.0f, 0x4a25f8 =
  -0.0015339808f subtracted per step, 0x4a25f0 = 32768.0).
- **Confidence:** proven (rules); the derived speeds in the spec are arithmetic on them
- **Doc:** `movement.md` "Walking and turning"

### E-0304 — Collision: sphere of radius 250 against .3DI triangles, front side only; push out from the average face point along the average normal, else from the average edge point
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** body created by `0x432e70(0xf)` (flags byte +0x10 = 0xF, 0x431630) in
  `C_Monde::LoadScene`; radius `0x432f30(body, 0xfa)` (+0xc) in `Alloc3DMemory`. Broad phase
  0x4310b0 per axis; 0x430db0 adds a face to list +0x30 when its axis bits are 7 (body flag
  4) and to list +0x34 when bits 0 and 2 are set and the axis is not 1 (flag 8); face box
  ends at +0x48 / +0x54 (0x430c30). 0x432220: `d = (n·c) >> 15 - face[4]` with n =
  `*face[3]`; bounds `-r < d < r` for flags 1|2; edge distances 0x431700 (normals +0x14 +
  12i, constants +0x38 + 4i), any below -r → 0; mask of negatives → 0x431920 (projection),
  0x431d30 (edge), vertex copy; returns ±2 for mask 0, else ±1 when |closest - c|² < r²;
  sign `(d >= 0) ? 1 : -1`. 0x4216b6 (disassembly 0x4217a7..0x421b72): counts result 1
  only while no result 2 was seen, sums its points (0x5b7f90..) into [ebp-0x84..]; result 2
  sums points into [ebp-0xc..] and normals (0x433050's fifth argument = `face[3]`) into
  [ebp-0x90..]; with faces: `fdivr 1.0` by the count, `__ftol` of the normal average, times
  `250 / 32768.0` (0x4a2528), `__ftol`, plus the point average, `__ftol`, `0x436160(0, p)`;
  else with edges: average, `__ftol(c - E)`, `sqrt` of the integer square sum (0x476464),
  times `250 / len`, `__ftol`, plus E, `__ftol`, set.
- **Method:** decompiled; FPU sequences read from the disassembly (capstone), the
  decompiler dropped their operands.
- **Confidence:** proven
- **Doc:** `movement.md` "Collision"

### E-0305 — Floor: the eye is set 700 above the nearest front-facing face below; y points down
- **Binary/file:** `/MISSION.EXE`; `Data/Scenes_3D/MUSEE.BFG`, `AUBERGE.BFG`, `MAISONET.BFG`
- **Evidence:** 0x4216b6 second half: for each list-+0x34 face, 0x431f90 (point inside the
  (x, z) triangle by three cross-product signs, `n.y ≠ 0`, y on the plane, returns 1 on the
  front side); keeps the smallest `y > camera y` (start 9999999); then `y = yf - 0xfa -
  0x1c2` (disassembly 0x421c10..0x421c3c) and 0x436160. In the corpus (extracted with
  `bfg.py --extract`, faces read with the E-0016 layout): MUSEE `BOX.3DI` and `BOX1.3DI`
  have one face under the default museum start (-39, -209, 361), normal (0, -32767, 0), D =
  -491, plane y = 491, signed distance 699, and -209 = 491 - 700; AUBERGE `BOX.3DI` under
  (0, 0, 0): y = 838; MAISONET under its start (1149, 141, -1491): y ≈ 930. 0x4211a6 and
  0x4212f7 have no callers (function-dump.tsv).
- **Method:** decompiled + disassembly; a script over the extracted `.3DI` faces.
- **Confidence:** proven
- **Doc:** `movement.md` "Floor"

### E-0306 — Scene table: 14 scenes, their bundles, init/frame callbacks, completion zones, entry/return movies
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x41fda9 switch on 0x4e3144 → bundle strings (0 "musee", 1 "auberge",
  2 "hopiext", 3 "maisonet", 4 "mangeurs", 5 "cafe", 6 "chambrev"/"chambreb" by 0x4abd14,
  7 "maisonj", 8 "hopiint", 9 "pont", 10 "terrasse", 11 "jardin", 12 "champ", 13 "eglise").
  0x41ee1d sets the callback pair 0x651460/0x651358 per scene; thunks resolved: 0x40141a →
  0x42ad92, 0x401645 → 0x42b776, 0x4012fd → 0x41a0b0, 0x4014c4 → 0x41a42b, 0x401271 →
  0x424af7, 0x401771 → 0x424d93, 0x401078 → 0x4279a3, 0x401802 → 0x427e04, 0x4017f8 →
  0x4298e5, 0x401140 → 0x429dd6, 0x401555 → 0x41b77d, 0x40191a → 0x41bbcf, 0x40168b →
  0x41c979, 0x401028 → 0x41d167, 0x40188e → 0x41dd7f, 0x40111d → 0x41ded8, 0x401776 →
  0x42897f, 0x40182a → 0x428e63, 0x401726 → 0x425541, 0x401848 → 0x42579a, 0x401839 →
  0x42cfe2, 0x401023 → 0x42d489, 0x4012e4 → 0x42ddbf, 0x4018c0 → 0x42e023, 0x401424 →
  0x426d9b, 0x401172 → 0x427069, 0x4012cb → 0x41e383, 0x4017da → 0x41e5de, 0x4011f4 →
  0x4242ed, 0x401005 → 0x424467. Completion 0x41efc5 (u32 flags 0x4abb10 … 0x4abb6c =
  0x4abb0c + 4·zone; 1, 2, 11 return 0). Entry movies 0x41faf9 ("maisa", "mangeurs",
  "cafe", "chamba", "maisonj", "hopi", "pont", "terrasse", "jardin", "champ", "eglise"),
  return movies 0x41f14b ("maisr", "mangeurr", "cafer", "chambr", "maisonjr", "hopir",
  "pontr", "terr", "jardinr" unreachable (case 11 returns first), "champr", "eglr"); all
  present in `Data/MOVIES` as `.hnm` (`terr` as `Terr.hnm`).
- **Method:** decompiled; strings and thunks read from the image (pefile).
- **Confidence:** proven (numbers, bundles, callbacks); the place names in the spec are ours
- **Doc:** `engines/peintre/docs/spec/scene.md` "The scene table"

### E-0307 — Scene load: 7 MB 3D heap, BFG image, .3DC under the camera, BOX.3DI in the collision world, a name table of ≤ 200 nodes, init callback, BFG freed
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** `Alloc3DMemory` 0x422869: clears 0x5badc0[20], 0x6511e0[10];
  `m__malloc(0x700000)` + memset; 0x421d73 (heap 0x434e70 creates the object "Camera" with
  flag 0x400; viewport 0x435170 per 0x4aba3c; then 0x4353c0(0x40), 0x4353d0(80000)); cursor
  0x25; callbacks; `C_Monde::LoadScene`; keyboard buffers cleared; 0x43c220(0); 0x426594;
  0x421c98; 0x432f10 + 0x432f30(0xfa); 0x4e4580 = 1; init callback; `m__free(0x598cac)`
  (the BFG image, E-0013); 0x439a10 when 0x5b7fa4 = 15. `C_Monde::LoadScene` 0x421e56:
  `<name>.BFG` (0x42e85c), `<name>.3DC` (`Obj_Load`), 0x435880(root, 0), 0x435930(root,
  0xf), `BOX.3DI`, 0x432df0, 0x432e70(0xf), 0x432e10(box), `CheckObjectCount` 0x4210b9 +
  0x420e99/0x420fa9 (records 0x38 bytes at 0x5b81e0, handle at +0x34 = 0x5b8214, first
  child 0x435fb0, next sibling 0x436020; > 200 → MessageBox). 0x41edc9 = strcmp search.
  0x422aa6 = unload. 0x435970 / 0x4359a0 set / clear bit 0 of node +0xc; 0x435dc0 renames
  face-group textures (+0xa4 list, `puVar2[2]` texture id); 0x4395d0 loads `<file>.3DM` as
  a named texture (texel pointer = entry + 0x8014); 0x436200 copies node +0x4c.
  0x435170(w, h, x, y, 480): centre, 0x6af5fc = `480·w/640`, 0x6af654 = `h·4.0 / (w·3.0)`
  (0x4a2570 = 4.0, 0x4a2578 = 3.0), 0x4353c0(0x80), 0x4353d0(65000); 0x432c30 draws only
  when z > 0x6af5bc (the near clip). 0x42f515 calls 0x435170 alone.
- **Method:** decompiled.
- **Confidence:** proven
- **Doc:** `scene.md` "What a scene is made of", "Camera and view"

### E-0308 — Start positions: per scene from the museum, per painting in the museum, per doorway between scenes, saved spot with pitch 0 after 2D
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x41fda9: `Alloc3DMemory(name, 0xf, init, frame, x, y, z, pitch, yaw, roll)`
  immediates (case A, both switches), the `local_1c..local_8` assignments per
  (0x4e3140, 0x4e3144) pair (case B), and the 0x5b7f80.. branch passing 0 for pitch
  (case C, taken when 0x502740 ≠ 0x598cb0). 0x4aba5c = 1 → "musee" at (0x4d0, -0xd0,
  0x106f, 0, 0xd52, 0). The else-branch's locals are only assigned for the listed pairs.
- **Method:** decompiled; every hex immediate converted and checked twice (the museum rows
  equal the flight targets of 0x41f506).
- **Confidence:** proven
- **Doc:** `scene.md` "Start positions"

### E-0309 — Museum → scene: 20-step camera flight (mode 4), then the entry movie unless the scene is complete
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x41f506: target per 0x4e3144 (same values as the museum rows of 0x41fda9),
  differences 0 → 1, angle wrap ±0x800, divided by 0x4aba30 (= 20 in `.data`), mode 4.
  0x41f9f8: add the step, 0x4221f6, counter 0x5b7fa0 += 1 (elapsed < 3) or elapsed >> 1,
  returns 0 when the counter ≥ 21. 0x41faf9: mode 2, stop stream, stop statics, 0x41efc5 = 0
  → `Hnm_AllocDecBuffers(movie)` + 0x42f6a0; else mode 0 and 0x4e313c = 1. Mode-2 end in
  0x42fbd6: 0x41fda9 + `Timer3D_Begin` when 0x502864 = 0x4e4580 = 0x50273c = 0.
- **Method:** decompiled.
- **Confidence:** proven
- **Doc:** `scene.md` "Moving between the museum and the scenes"

### E-0310 — Scene → museum: Backspace or the return icon; return movie when the scene is complete
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x4223e8: `0x41ec7b(0xe)` and 0x4e3144 ≠ 0, or `click` with 0x4acfa0 = 0 and
  the cursor in (x < w65 + 10, y > 0x1da - h65), → 0x4221f6, 0x4e3140 = 0x4e3144, 0x4e3144 =
  0, 0x4e313c = 1, 0x41f14b. 0x41f14b: per scene the same flags as 0x41efc5 (cases 0, 1, 2,
  11 return); else mode 2, stream stop, statics freed, return movie, 0x4e3138 = 1, 0x4e3144
  = 0, `*(0x4abb70 + 4·0x502860) = 1`. 0x42f988 handles 0x4e313c (0x422aa6 + 0x41fda9).
- **Method:** decompiled.
- **Confidence:** proven
- **Doc:** `scene.md`, `interaction.md` "The return icon"

### E-0311 — Back from 2D: zone solved when the sunflower count rose; actions -1/-2/-3/slot; special zones 0, 7, 8, 11, 21
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x42f2c2(flags, count, action) (called from `MainWndProc` at 0x412e76):
  clears keyboard buffers, copies 0x8c bytes to 0x651220, 0x4abbd4 = count, count > 0x598fe0
  → `0x4abb0c[0x502860] = 1`; -3 → 0x50273c = 0, 0x4e3140 = 0x4e3144; -2 → `PostQuitMessage`;
  ≥ 0 → `Load3DGame`; zone 0 → 0x4aba4c = 0x4aba48 = 1; 0x15 → 0x4aba5c = 1, movie
  "cinefin", 0x4e3148 = 1; 0xb → 0x4abd4c = 1 when 0, 0x4e30f4 = 1 when 0x4abd5c = 0; 7 →
  0x4abd54 = 0x4abd58 = 1; 8 → 0x4abd50 = 1 when 0; -1 → 0x41fda9 with 0x502740 = 1 (case
  C), else 0x41f14b; -3 → 0x4e3144 = 0 and 0x41fda9; `Timer3D_Begin` unless mode 2.
  0x598fe0 is set to 0x4abbd4 before every `Entry2D` (0x42fbd6, 0x42f755).
- **Method:** decompiled; caller found by scanning `MainWndProc` calls through the thunk
  0x4015c3.
- **Confidence:** proven
- **Doc:** `scene.md` "3D ↔ 2D"

### E-0312 — Into 2D: scene code sets the zone and mode 1; the redraw sets 0x4b0058; 0x42f755 saves the camera and calls Entry2D; Escape → option menu
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** scene frames set `0x502740 = 0, 0x598cb0 = 1, 0x502860 = zone` (e.g. 0x41a42b
  `casquette` → 0x14) and end with 0x4221f6 when 0x598cb0 = 1, which sets 0x4b0058.
  0x42fbd6 modes 1/3 with 0x4b0058 ≠ 0 → 0x42f755: 0x4aba70/74/78 = position,
  0x4aba64/68/6c = angles, 0x4aba7e = zone, 0x4aba7c = 0x4e3144, 0x4aba7d = 0x4e3140, the
  same into 0x5b7f80.. / 0x5b7fb0.., 0x422aa6, 0x598fe0 = 0x4abbd4, 0x8c bytes 0x651220 →
  0x4aba80, `Timer3D_End`, `Entry2D(hwnd, zone, 0x651220, 0x4aba40, 0x36c)`. Escape
  (0x41ec7b(1)) → 0x42edef: same copies, mode 3, 0x4221f6, 0x416961, `Timer3D_End`,
  0x40fccb (option menu, 40 ms timer). 0x42f515(action) (called from `MainWndProc`
  0x4124bc): -2 quit, slot → `Load3DGame`, 0x435170 by 0x4aba3c, static volumes
  (0x416e68), 0x416987, `Timer3D_Begin`. 0x42f873 (bar closed): the same copies and
  `Save_WriteGGame(0x4aba40, 0x36c, 0)`.
- **Method:** decompiled; callers found through the thunks 0x4010b9, 0x4013cf, 0x401244.
- **Confidence:** proven
- **Doc:** `scene.md` "3D ↔ 2D"

### E-0313 — Mouse and picking: relative DirectInput mouse clamped to 640×480, left-button level; pick = renderer pass at the cursor (or the cursor centre while carrying), -1 outside the viewport
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x472710 (`GetDeviceState(0x10)`: lX, lY, `rgbButtons[0] >> 7`,
  `rgbButtons[1] >> 7`, disassembly 0x47276e..0x47279c); 0x420e07 adds and clamps 0..0x27f,
  0..0x1df; 0x4aba34/38 = 320/240 in `.data`. `Pick` 0x41eb20: bounds per 0x4aba3c
  (0/0x280/0/0x1e0, 0x40/0x240/0x30/0x1b0, 0x78/0x208/0x5a/0x186, 0xa0/0x1e0/0x78/0x168),
  offset by half the cursor's size when 0x502734 = 1, 0x439b90(0, x, y): 0x6af5a0/0x6af5b4
  = x/y, depth 0x6af5b0 = 0x4f000000, drawer pointers swapped to 0x43a150 around 0x450160,
  result 0x433740(0x6af5b8). Frames clear 0x5b7fac at their end (0x41a42b, 0x42b776).
- **Method:** decompiled + disassembly.
- **Confidence:** proven (the pick routine's internals are the renderer's)
- **Doc:** `interaction.md` "Mouse", "Picking"

### E-0314 — Cursors: 66 TGA slots, their files and indices
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x426594: `op_` + itoa(0..34) → slots 0..34, `fleche` 0x25, `main` 0x26,
  `curza` 0x27, `def_0` 0x23, `def_1` 0x24, `curdoigt` 0x3a, `curferme` 0x28, `sablier`
  0x29, `acces` 0x3b, `deja_vu` 0x3c, `fagot` 0x3e, `buche` 0x3d, `manivel` 0x40, `cle` 0x3f,
  `retour` 0x41, `Ct` + itoa(0..15) → 0x2a..0x39; `Invent` → 0x599078; sounds `bar_obj`,
  `cf_clic3` (0x425f00). `Cursor_Check` 0x4240f0: on failure 32×32, `m__malloc(0x800)`
  memset 0xff. Cursor drawn at (0x4aba34, 0x4aba38) with 0x424190 → `Blit16Keyed`.
  Writers of 0x28: 0x41bbcf, 0x429dd6, 0x42d489 (while 0x502734 = 1 and a pick).
- **Method:** decompiled; strings read with pefile.
- **Confidence:** proven
- **Doc:** `interaction.md` "Cursors"

### E-0315 — Scene object tables and the hover/click skeleton of the frame callbacks
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** init callbacks resolve names with 0x41edc9 and hide `startHidden` = 1
  (0x42ad92: stride 0x40, name at +0, cursor type +0x32, handle +0x38, hidden +0x3c, count
  0x4ae7e0; 0x41a0b0: stride 0x3c, handle +0x34, hidden +0x38, count 0x4a9948). Frames
  0x41a42b and 0x42b776: reset of 0x26/0x27/0x3a/0x3b/0x3c to 0x25; with `click` and cursor
  0x25 the per-object action; else hover mapping 2 → 0x26, 3 → 0x27, 4 → 0x3a, 6 → 0x3b,
  0x3c → 0x3c, default 0x25 (the museum: 2/3/4 only and `sqrt(x² + z²) < 1200.0f`
  (0x4a2550) of 0x436200's result).
- **Method:** decompiled; tables dumped from `.data`.
- **Confidence:** proven
- **Doc:** `interaction.md` "Hover and click"

### E-0316 — Inventory bar: slides 8 px per frame, arrows scroll, a click with an object stores it, 6 visible, sunflower counter, autosave on close
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x426171 (states of 0x4acfa0, 0x4acfa4 ± 8, `bar_obj` via 0x599138,
  `Blit16` of 0x599078 at (0, y) 640 × 0x599128, arrows 0x425f71(x, y, 12 / 500, y + 15,
  32, 32) → `def_0` at (10, y + 13) / `def_1` at (0x1f7, y + 13), 0x4e311c scroll rules,
  store box (0, y - 0x1e, 0x280, 100), `cf_clic3`, `0x651220[cursor] = 1`, cursor 0x25,
  `first = count - 7` when count > 6, state 3; 0x4abbd8 = 1 when the cursor is 0);
  0x426071 (slots at 0x4acfa8 = 100, 170, 250, 310, 380, 450; y + 0x1e centred), 0x425ff2
  (`Ct` slot 0x2a + 0x4abbd4 at 0x22c, y + 0x1f centred), 0x425fb1 (held count), closing →
  0x42f873. Space in 0x4223e8: 0 → 2, 1 → 3. Return icon drawn in 0x426171 when 0x4e3144 ≠
  0, bar hidden, cursor in the corner.
- **Method:** decompiled; `.data` values read with pefile.
- **Confidence:** proven
- **Doc:** `interaction.md` "Inventory bar"

### E-0317 — Carrying a 3D node: 0x502734 / 0x502a80, cursor by the node's name
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x4223e8: when 0x502734 = 1, `strcmp(BadHandle(0x502a80), "fagot" /
  "buche" / "poignee04" / "clef")` → cursor '>' 0x3e / '=' 0x3d / '@' 0x40 / '?' 0x3f.
  Writers of 0x502734 = 1: the cafe, mangeurs and pont frames (0x41bbcf, 0x429dd6,
  0x42d489); `App3D_InitPaths` clears it.
- **Method:** decompiled; strings read with pefile.
- **Confidence:** proven
- **Doc:** `interaction.md` "Carrying a 3D object"

### E-0318 — Animation records: 3DA handle + node handle, length = first word, frame advanced by elapsed ticks, posed with 0x438290
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** `LoadAnimsmusee` 0x42ac4a: records of 0x78 bytes from 0x4aed70 (count
  0x4aed68), `Obj_Load(name)` → +0x64, 0x437d90 (`*0x4338a0(h)`, the first word of the
  object's data) → +0x6c, +0x70 = 1, 0x41edc9(name at +0x32) → +0x68; 0x42b5fe adds 0x598ec0
  to +0x70, per-record end rules, then `0x438290(+0x68, +0x64 + frame, +0x64 + frame, 0,
  0)`. 0x438290: key handles carry the frame in their low 16 bits; equal high halves →
  one-object interpolation `((256 - t)·f1 + t·f2) / 256` (0x4a25ac = 1/256).
- **Method:** decompiled.
- **Confidence:** proven (the pose computation itself is the renderer's / Q-0004's)
- **Doc:** `scene.md` "What a scene is made of"

### E-0319 — Box-set swap helper and the texture/visibility helpers scene code uses
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x42a980(n) (museum): unregister the set in 0x4e312c (0 = `BOX.3DI` 0x5bada4,
  1..4 = 0x6511e0..0x6511ec) with 0x432e40, register set n with 0x432e10, 0x4e312c = n.
  `LoadBoxMusee` 0x42aab8 loads `BOX1.3DI`..`BOX4.3DI`; `LoadBoxAuberge` 0x419f0e
  `BOXBAS.3DI`, `BOXHAUT.3DI`. Helpers as in E-0307; 0x4399d0(node, fn) calls fn on each of
  the node's 8-byte UV records (+0x84 count, +0x88 array), e.g. 0x42ad1c adds ±0x7f0000 to
  word 1 for six steps each way.
- **Method:** decompiled.
- **Confidence:** proven
- **Doc:** `scene.md` "What a scene is made of"

### E-0320 — Static sounds per scene: slots at 0x5badc0, count 0x650f80, ambience 0x50286c looped
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x42abf1 (museum: `robot2`, `etoile`, `musee` = ambience, count 4, slot 0
  empty), 0x419fb3 (auberge: `auberge`, count 1); 0x416e24(s, loop) = volume 0x4e2908 then
  play (0x473300); 0x416e51 stop; 0x416dd6 free. Init callbacks start the ambience with
  0x416e24(s, 1) (0x42ad92, 0x41a0b0); 0x42fbd6 restarts 0x50286c after the entry movie;
  0x41faf9 / 0x41f14b stop / free all slots.
- **Method:** decompiled.
- **Confidence:** proven
- **Doc:** `scene.md` "What a scene is made of"

### E-0321 — musee (scene 0): object and track tables, acts and box sets, paintings retextured when complete, the robot's lines and hints, zone 0 through the vase
- **Binary/file:** `/MISSION.EXE`; `Data/SOUND` (`a50_01*.wav`, `robot2`, `etoile`, `musee`)
- **Evidence:** init 0x42ad92 (table 0x4ae7e8 × 22 of 0x40, count 0x4ae7e0; `LoadAnimsmusee`
  0x42ac4a over 0x4aed70 × 4 of 0x78; `LoadBoxMusee` 0x42aab8; 0x42abf1; sunflower resets;
  0x42a980 box-set lines; 0x4aec1a (= `vase` +0x32); 0x4abbd8 = 0 → viewer reset to (0xffd9,
  0xff2f, 0x169, 0xfe2, 0x14, 0); 0x4395d0 / 0x435dc0 argument pairs read from the pushes
  (e.g. 0x42b3da: `0x435dc0(Find("m01_03"), "MANGEUR", "RVBMANGE")`); 0x4aba48 → cursor
  types 0xff at +0x32 of entries 11, 17..21). Frame 0x42b776 (painting names per branch read
  from the pushes at 0x42b886..0x42bc82: m04_02 → 0xc, m04_03 → 0xd, m03_05 → 0xa, m01_02 →
  3, m03_02 → 6 + 0x4abd14 = 1, m03_04 → 8, m03_01 → 5, m04_01 → 0xb, m03_06 → 9, m03_03 →
  7, m01_03 → 4; `vase` 0x42bce7; `etoile` 0x42bd26; parts 0x42bd9d..0x42bdf7; line table
  0x4aef50 = "a50_01", "a50_01c", "a50_01d", "a50_01e", "a50_01h"; hints push 0x4af358 /
  0x4af360 / 0x4af368 / 0x4af37c..0x4af3a4, all "a50_01d"; 1200.0f (0x4a2550) and 1500.0f
  (0x4a2554); `fin` 0x4af378 when 0x4aba5c and z < 0xdac). 0x42b5fe track ends. 0x416a2f
  returns 0x651678, cleared by `Snd_PlayStreamWav` (0x416813) and set to 1 by the refill
  routines at the stream's end (0x416bab, 0x416d91). A byte scan of `.text` for 0x4aef4c
  finds only 0x42b20d (init, 0), 0x42b6f3 (0x42b5fe, 0) and 0x42bf75 (read): `robot03` is
  never started. 0x4abbfa (0x42c0ec) and 0x4e3124 (0x42bd84) are written and never read.
- **Method:** decompiled; arguments and branch strings from the disassembly
  (`build`-side script listing the pushes before each call); tables from `.data` (pefile).
- **Confidence:** proven
- **Doc:** `games/mission-sunlight/docs/musee.md`

### E-0500 — One 3D frame: tree walk from the camera, per-node transform/cull/clip/project, edge building, then a scanline span resolve
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x4378f0 (the frame's draw call, 0x4221f6/0x4223e8): `0x450160(camera)`,
  the optional hook 0x4e33c8 (0 in `.data`, never written), 0x450650, then
  `(*0x4b01cc)(dest)`, 0x4b01cc = 0x44ab80 in `.data` (its only other writer, 0x4378a0,
  has no reference). 0x450160: 0x433670 (heap mark), 0x455470, then a depth-first walk of
  the camera's subtree (child +0x14, sibling +0x18, parent +0x10) that skips a node and
  its subtree when flag bit 0 is set, calls 0x44fec0 on the way down and
  `*0x4b135c` (0x447d90) on the way up. 0x44fec0: world rotation `+0x58 = parent.+0x58 ·
  +0x28 >> 15` (0x43b060), world position `+0x4c = trunc(parent.+0x58 · +0x1c / 32768) +
  parent.+0x4c`; resets each vertex group's cursor (+0x14 = +0xc); if flag bit 2 clear:
  0x44bb10 (flags &= 0x1891, bounding-sphere cull), and unless culled (bit 3, see
  E-0504): 0x44bd60 (vertices to camera space), 0x44c100 (eye in node space), 0x44d980
  (poly cull, near clip 0x44c370), 0x44dc30 + 0x44df60 (lights, E-0508), 0x44db30
  (projection), `*0x4b1358` (0x447c30, edge builders) unless flag 0x1000, 0x44fb10 if
  flag 0x800. 0x450650 walks the tree again calling 0x4503b0 (node +0x9c boxes, 0 in the
  corpus, E-0513). 0x44ab80: per scanline from the viewport top for its height, moves
  the edges bucketed for that line (0x69de60 starts, 0x69ee60 continuations, 0x69fe60 ends) into a
  sorted active list, steps every active edge, and resolves spans (0x44a6b0, or 0x44a820
  when a negative-type surface is on the line) into a span list walked by 0x454a8e.
- **Method:** decompiled the functions named (`notes/decomp/MISSION.EXE__FUN_*.c`);
  pointers read from `.data` with pefile; xref scans in a read-only project copy.
- **Confidence:** proven

### E-0501 — Camera: node `Camera` (handle 0, flag 0x400) whose world matrix is the inverse of its local pose; scenes hang under it
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x434e70 builds the first node, named "Camera" (0x4b023c), flags 0x400,
  both matrices identity (0x43a750), and stores it in 0x6af650, the root every frame
  walks. 0x436160(h, pos) writes local +0x1c; 0x4360f0(h, M) writes local +0x28; for a
  flag-0x400 node both then set world rotation `+0x58 = transpose(+0x28)` (0x43b0c0) and
  world position `+0x4c = -(+0x58 · +0x1c >> 15)` (0x43b0f0, 0x43b190 negates). The root
  itself is never passed to 0x44fec0 (0x450160 starts at its child), so every node's
  world matrix is camera space: `v_cam = Mᵀ (v_world − eye)`. `C_Monde::LoadScene`
  attaches the scene root under handle 0 (0x435880: child.parent = parent, child.sibling
  = parent.child, parent.child = child). Camera pose from angles: E-0307 / `movement.md`
  (0x422f30, 0x43a780).
- **Method:** decompiled 0x434e70, 0x436160, 0x4360f0, 0x43b0c0, 0x435880; disassembled
  0x43b190.
- **Confidence:** proven

### E-0502 — Projection: focal 480 · w / 640 on both axes, centre of the viewport, truncated to integer pixels; near 64 / far 80,000
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x435170(w, h, x0, y0, 480): `fx` (0x6af5fc) = `480·w / 640` (integer
  division), `fy` (0x6af5f4) = `fx · (h·4.0)/(w·3.0)` (0x4a2570 = 4.0, 0x4a2578 = 3.0),
  centre `cx = w/2 + x0` (0x6af670), `cy = h/2 + y0` (0x6af66c); all four view sizes
  (0x421d73) are 4:3, so `fx = fy = 0.75 · w` and the field of view is the same in all:
  `tan(hfov/2) = 320/480`, `tan(vfov/2) = 240/480` (67.4° × 53.1°). 0x44db30 and the tail
  of 0x44bf20 (asm 0x44c0a0): `1/z` stored as `2^30 / z` (float, +0x24; 0x4a26e8 =
  2^30), `sx = __ftol(fx · x / z + cx)`, `sy = __ftol(fy · y / z + cy)` (MSVC `__ftol`
  truncates), then outcodes against the viewport: sx < x0 → 2, sx > x0 + w → 1, sy ≤ y0 →
  4, sy > y0 + h → 8. 0x44bd60 sets 0x10 when `trunc(z) < near` (0x6af5bc) and 0x20 when
  `≥ far` (0x6af6c4) unless node flag 0x80, and view-cone bits from `K = −(w/2 << 15) /
  fx` (0x6af674) and the same for y (0x6af6a8) (0x435020). Near/far: 0x4353c0/0x4353d0,
  64 and 80,000 after a scene load (0x421d73), 128 and 65,000 after 0x435170 alone
  (E-0307). The four side planes of 0x435020 (0x6af630, 0x6af680, 0x6af610, 0x6af660)
  are the view-cone normals `(∓fx, 0, −w/2)` and `(0, ∓fy, −h/2)` normalised to Q15
  (0x43b270), used only by the sphere cull (E-0504).
- **Method:** decompiled; x87 operands from the disassembly (`notes/decomp/
  MISSION.EXE__asm_render.s`); constants from `.rdata` with pefile.
- **Confidence:** proven

### E-0503 — Coordinates: camera x right, y down, z forward (right-handed); world y is down; front faces run counter-clockwise on screen
- **Binary/file:** `/MISSION.EXE`; the 15 `.3DC`
- **Evidence:** E-0502: `sx` grows with camera x, `sy` with camera y, depth is +z. With
  the camera matrix identity the world axes are the camera's, so world y points down
  (E-0305 gets the same from the floor code). Drawers 0x444e20 and 0x43c780 draw a
  triangle only when `(y2−y1)(x1−x0) − (y1−y0)(x2−x1) < 0.0` in integer screen
  coordinates (0x4a2690 = 0.0), i.e. corners 0, 1, 2 counter-clockwise as seen on the
  y-down screen. `engines/peintre/tools/winding_check.py` projects every poly of the 15
  scenes from 60 random cameras with these rules: the screen test and the plane test of
  E-0505 agree on 82,165 of 82,657 polys (99.4 %; the rest are nearly edge-on).
- **Method:** decompiled; corpus check script.
- **Confidence:** proven

### E-0504 — Node culling by bounding sphere; node flag bits; nodes with 0x10 use their parent's 0x80 vertices
- **Binary/file:** `/MISSION.EXE`; the 15 `.3DC`
- **Evidence:** 0x44bb10 keeps flag bits 0x1891 and recomputes the rest each frame: the
  sphere of centre node +0xb4..+0xbc (local, transformed like a vertex) and radius +0xb0
  is tested against the four side planes (distance > r → bit 3, "culled"; otherwise bit
  0x20) and against near and far (straddling → 0x40; wholly before
  near, or beyond far without flag 0x80 → bit 3). 0x44fec0 draws a node when bit 3 is
  clear, or when it has flag 0x10 and its parent is not culled; a 0x10 node first makes its
  parent transform and project the parent's vertices flagged 0x80 (0x44bf20, once per
  frame through parent bit 1). Corpus: all 1,628 poly corners that point outside their own
  node's vertex array are in 0x10 nodes and point into the parent's array, at vertices
  flagged 0x80. Runtime writers of node flags in the game code are only 0x435970 (set bit
  0, hide) and 0x4359a0 (clear bit 0) (scan of all stores to `[reg+0xc]`); flags 0x4, 0x80,
  0x800, 0x1000 never occur in the files (flags 0, 0x10, 0x20, 0x30: E-0014).
  Radius +0xb0: 379 distinct values; +0xac, +0xc4..+0xcc, +0xd4, +0xd8 = 0 and +0xc0 = 40
  in all 560 nodes, +0xd0 = 15 in all.
- **Method:** decompiled; corpus scan (script over `bfg.py`/the node layout of E-0014).
- **Confidence:** proven (+0xac, +0xc0, +0xd4, +0xd8: no reader found, unk)

### E-0505 — Backface culling: poly +0x30 is the plane distance; poly flag 8 tests in camera space instead
- **Binary/file:** `/MISSION.EXE`; the 15 `.3DC`
- **Evidence:** 0x44c100 stores in each face normal's word 3 `n · e >> 15`, e = the camera
  position in node space (`−(Wᵀ · +0x4c)`, asm). 0x44d980, per poly of each face group
  (list head copied from +0x20 to +0x24): if poly word 0 lacks bit 3, it is back-facing
  when `normal.w3 − poly.+0x30 < 0`; with bit 3 it is back-facing when `v0 · ((v0−v1) ×
  (v1−v2)) ≥ 0` in camera space (floats scaled by 0.0625, 0x4a26ec). Back-facing, or all
  three vertices outside one side (AND of outcodes & 0x3F), or any vertex beyond far (OR &
  0x20) → poly word 0 |= 1, not drawn; any vertex before near (OR & 0x10) → 0x44c370
  replaces it by clipped polys (new corners, UVs interpolated, original |= 3); else its
  vertices get 0x40 (to be projected). Corpus: `+0x30 = (n · v0) >> 15` exactly for
  37,742 of the 37,798 polys without bit 3 (the rest have one of the 63 malformed normals
  or differ by a unit); bit 3 is set on 1,275 polys, all in 0x10 nodes. No poly is
  two-sided.
- **Method:** decompiled; corpus scan.
- **Confidence:** proven

### E-0506 — No z-buffer: a scanline span buffer ordered by 1/z, filled by type-indexed span routines
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** vertex-group items are the edges: 0x447d90 (per vertex group, on the way
  up the tree) runs 0x447640 for types 3/−6/−4/…, which puts each edge built this frame
  into the per-scanline start bucket (0x69de60, a 16-byte `{next, edge, type}` node) and
  its end bucket (0x69fe60), pre-stepped to the viewport top when it starts above it.
  The edge record (100 bytes for types 3/−6/−4, filled by 0x444e20): +4 state, +8 x
  (20.12), +0xc dx/dy, +0x10 1/z at the edge's x on the current line, +0x14 its per-line step, +0x18
  d(1/z)/dx, +0x28 next edge of the same poly side, +0x2e shade row (byte), +0x2f mip
  level (type 0x14 only), +0x30 bucket link, +0x3c/+0x40 u/z and v/z, +0x44/+0x48 their
  per-line steps, +0x4c/+0x50 their x gradients, +0x54 texel pointer, +0x58..+0x60 the
  three x gradients × 16. 0x44ab80 turns the edges into 0x24-byte surfaces `{type, …,
  x, …, edge}` in an x-sorted active list; 0x44a370/0x44a4d0/0x44a630 insert a surface in
  front of the current one when its `1/z` at x (edge 1/z + (x − edge.x) · d(1/z)/dx) is
  larger, or within 100 (0x4a26dc = −100.0) and its d(1/z)/dx is larger. Spans `{x_end,
  x_start, type, edge}` go to 0x454a8e, which calls `table[type]` (0x4b20dc + 4 · type)
  with ebx = x start, ecx = count, edi = destination, ebp = edge, from the last span to
  the first. The frame's background is a permanent surface of type 0x4b12d4 = 14 (its only
  writer 0x44b860 has no caller) behind everything: 0x458760 fills with the colour at
  0x4e3600 = 0 (black, never written). Sentinels (types 4 and 16) call a bare `ret`.
- **Method:** decompiled; tables from `.data`; disassembly of 0x454a8e.
- **Confidence:** proven

### E-0507 — The corpus face-group types: 3 textured opaque, −6 textured colour-keyed, −4 textured 50 % translucent, 1 flat colour
- **Binary/file:** `/MISSION.EXE`; the 15 `.3DC`
- **Evidence:** edge builders by type (0x447c30): 3, −6, −4 → 0x444e20; 1 → 0x43c780.
  Span routines (`.data` table 0x4b20dc): 3 → 0x45ee50, −6 → 0x460450, −4 → 0x45a3b0
  (0x45bae0 on 555), 1 → 0x45809a. 0x444e20, per poly: per-vertex 1/z, u/z, v/z (UV
  16.16 from poly +0x34..+0x3c times the vertex's 2^30/z), their x and y gradients over the
  triangle, the shade row `31 − (node.+0xd0 & 0xFF)` (or `31 − poly.+0x40` when the node
  has lights), texel pointer `**group.+8` (the texture slot's word 2 = `.3DM` data +
  0x8014, E-0014). 0x45ee50 (type 3): exact `u = (u/z)/(1/z)` every 16 pixels (divide by
  0x4b2364) and linear steps between, 16.16 u/v with 8-bit fractions, texel = `texels[
  (v >> 16) · 256 + (u >> 16)]` with no mask, pixel = high half of `table[row · 256 +
  texel]`, two pixels per dword store; every pixel written. 0x460450 (type −6): the same,
  but the texel offset is ANDed with 0xFFFF (u and v wrap at 256) and texels of value 0
  set a skip bit (`sub al,1; adc ebp,ebp`) so their pixels are not written. 0x45a3b0
  (type −4): texel offset `((v >> 16) & 0xFF) << 8 | (u >> 16) & 0xFF`, pixel =
  `((src & 0xF7DE) + (dst & 0xF7DE)) >> 1` per RGB565 pixel (mask 0xF7DEF7DF on pixel
  pairs, `rcr`), no key. 0x43c780 (type 1): colour = low 16 bits of `group.+8`, which
  0x4338d0 points at the texture slot's word 11 = the material's first `unk_colour` word
  (slot words 3..13 are the 44-byte material record, 0x434560); without lights the colour
  grows by 0x1388 (mod 0x10000) for each poly of the group (0x43c7c5, `add edi,
  0x13881388` before every poly); 0x45809a fills the span with it. Corpus: type −4 is
  one group (pont `eau`); type 1 is 11 groups (38 polys, all material DEFAULT, colour
  0x3DEF) in chambreb `perpompe`, champ `animfaux01`, `corbopere`, hopiext `porche02`,
  musee `brul`..`brul05`, terrasse `drapoanim` (0 polys). Texel 0 occurs in 379 of the 384
  type −6 textures.
- **Method:** decompiled the builders; disassembled the span routines
  (`notes/decomp/MISSION.EXE__asm_render.s`); corpus scan.
- **Confidence:** proven

### E-0508 — Every textured pixel uses shade row 16; the lighting code never runs
- **Binary/file:** `/MISSION.EXE`; the 15 `.3DC`
- **Evidence:** the row is `31 − brightness`, brightness = node +0xd0 low byte when node
  +0xc4 (light count) is 0 (0x444e20). +0xd0 = 15 in all 560 nodes of the files, and its
  only writer, 0x435930 (all nodes of an object, `value & 0x1F1F`), is called with 15 by
  `C_Monde::LoadScene` (0x421f22) and by cafe's init for `mirroir` (0x41b7ef..0x41b7ff).
  +0xc4 = 0 in all nodes and no game code stores to it (the stores to `[reg+0xc4]` are in
  the Cryo library, 0x4686b8, on other structures); the light count 0x4e3658 is 0 in
  `.data` and never written. So 0x455470 (lights to camera space), 0x44dc30 and 0x44df60
  (per-poly brightness from type-1 directional / type-2 point lights with inner/outer
  radii, 0x94-byte records at 0x68b1e0, into poly +0x34/+0x40/+0x41..) do nothing in
  this game.
- **Method:** decompiled; store scans; corpus scan.
- **Confidence:** proven

### E-0509 — Texel addressing and the odd-sized textures (Q-0003)
- **Binary/file:** `/MISSION.EXE`; jardin `salon.3DM`, musee `plafond*.3DM`
- **Evidence:** row stride is 256 in all three routines (E-0507); only −6 and −4 wrap.
  Type 3 reads `texels + floor(v)·256 + floor(u)` unbounded, so u past 256 continues on
  the next row and negative or large v reads outside the texel block. The groups using the
  four odd textures are all type 3 or −6 with u ≤ 254.004 and v in [0.996, 255.0] (27
  groups): the 255-row `plafond*` textures are read at row 255 only where v reaches
  exactly 255.0; salon's rows 256 and 257 are never addressed. Of 485 textured
  (type, material, scene) triples, 12 have UVs outside [0, 256]: maisonj `BORDS` and
  `GRILLE` (−6, u up to 4,114.9 and 1,280), musee `PLANTE` (−6, u −14,336..2,549), and
  type 3 in maisonj only (`SOL` u ≤ 764, `TUILES` v ≥ −554.8, `VAN02` v ≥ −237.1,
  `MAISBGROUND` u ≥ −255, and four that exceed by under 20).
- **Method:** disassembly; corpus scan of UVs per face group.
- **Confidence:** proven

### E-0510 — The 555 display path converts pixel formats only
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x42e97f calls 0x43c200 when 0x6516bc = 1 (555 surface, E-0100); 0x439a10
  (from `Alloc3DMemory` 0x422a87 when the depth byte 0x5b7fa4 = 15) calls 0x43c200 once
  (guard 0x4e35d8) and converts every loaded texture's shade table once (slot word 14
  bit 0): `565 → 555` by `r << 10 | (g6 >> 1) << 5 | b`. 0x43c200 = 0x454af0 + 0x4549f0:
  in both span tables swap the entries of types −4 ↔ −18, −3 ↔ −17, −2 ↔ −16, −19 ↔ −14,
  −20 ↔ −7; the pairs are the 565 and 555 versions of the blending routines (0x45a3b0
  masks 0xF7DEF7DF, 0x45bae0 masks 0x7BDE7BDF).
- **Method:** decompiled; disassembly.
- **Confidence:** proven

### E-0511 — The assembly at 0x455470–0x465bcf: one C function, then span routines entered only through two type-indexed tables (Q-0002)
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x455470 is a C function (Ghidra made it: 119 bytes, called by 0x450160)
  transforming the lights to camera space (E-0508). From 0x4554f0 the code is
  hand-written span routines with a register interface (ebx = first x, ecx = count, edi =
  destination pixel, ebp = edge record, esi = span list, st0 = 1.5·2^52 from 0x4b2360),
  reached only by `call [eax*4 + 0x4b20dc]` in 0x454a8e (table 0x4b2084..0x4b215c, types
  −22..32; 0x454ad7 for type −1 ends the walk) and `call [eax*4 + 0x4b21cc]` in 0x454b90
  (a second walker with its own table 0x4b2174..0x4b224c, which nothing references).
  Routines per type in E-0507 for the corpus; 0 (0x458090) only advances, 14 (0x458760)
  fills the background, 15 (0x458793) copies from a buffer at 0x69ce54, 27 (0x4580d1)
  fills 0x0101.
- **Method:** capstone disassembly; table dumps; byte scans for absolute and relative
  references.
- **Confidence:** proven

### E-0512 — Picking: nearest drawn triangle under the point, by screen-space inside test and ray depth
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x439b90(h, x, y) stores x, y (0x6af5a0, 0x6af5b4), depth 2^31
  (0x6af5b0 = 0x4f000000), clears 0x4b135c and walks from node h with 0x43a150 as the
  draw hook, so every node gets the whole per-node pipeline of E-0500 except edge
  bucketing. 0x43a150 (made a function in a scratch copy): skips the node when (x, y) is
  outside its projected bounding circle; for each poly of the node's draw list without
  bit 0 (so visible, front-facing, clipped polys included, every group type, texel 0
  ignored): bounding-box test, then the three edge functions of the projected corners ≤
  0.0 (inside or on the edge), then the depth along the view ray through (x, y) of the
  poly's camera-space plane; the smallest depth wins and 0x439b90 returns that node's
  handle (0x433740).
- **Method:** decompiled (function created with `define_and_decompile.py` in a
  throw-away project copy).
- **Confidence:** proven

### E-0513 — Code present but idle in this game
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x44b120 (a second span resolver, set only by the unreferenced 0x4378a0);
  0x454b90 (unreferenced span walker); 0x447f50 (9 KB rasteriser, no reference); 0x454870
  (draw hook exporting projected triangles, installed when 0x4e3654 ≠ 0, which is 0 and
  never written); 0x44fb10 (sphere-mapped UVs from camera-space vertex normals for flag
  0x800, never set); mip selection for group type 0x14 (0x444e20, `(&0x6a0e80)[level]`,
  thresholds 0x4a26a0..0x4a26c8; no type-0x14 group in the corpus); 0x4503b0 (world
  bounds of node +0xa0 boxes, count +0x9c = 0 everywhere).
- **Method:** xref and byte scans; decompiled.
- **Confidence:** proven

### E-0514 — .3DA playback: track i poses node i; keys (time, x, y, z, w); time in 66 ms ticks; track 0's first word is the length (Q-0004)
- **Binary/file:** `/MISSION.EXE`; 48 `.3DA`
- **Evidence:** 0x438290(obj, keyA, keyB, t, mask) (E-0318): handles are `object << 16 |
  frame`; for i below the scene object's node count (object +0x14, nodes +0x18.., the
  `.3DC` node table) it poses node i with the anim object's track i (+0x18..). Same
  animation: time `((256 − t)·fA + t·fB) / 256` (float) → 0x437da0; two animations: each
  sampled at its own integer frame and the results blended by t/256 (0x437f80).
  0x437da0(node, track, time, mask): rotation unless mask bit 0 and only if the track has
  ≥ 2 keys; binary search for the first key k ≥ 1 with `key.time ≥ time` (k = n − 1
  past the end); `key.time ≤ time` → that key as is, else fraction `trunc((time −
  prev.time) · 256 / (key.time − prev.time))` (0x4a25a8 = 256.0) and 0x43b740 between
  the two; 0x43b480 writes node +0x28. Position the same (mask bit 1), linear with the
  same 8-bit fraction into +0x1c. 0x43b480: `m0 = 1 − 2(q1²+q2²)`, `m1 = 2(q0q1 − q3q2)`,
  `m2 = 2(q0q2 + q3q1)`, `m3 = 2(q0q1 + q3q2)`, `m4 = 1 − 2(q0²+q2²)`, `m5 = 2(q1q2 −
  q0q3)`, `m6 = 2(q0q2 − q3q1)`, `m7 = 2(q1q2 + q0q3)`, `m8 = 1 − 2(q0²+q1²)` (Q30 >> 14):
  the key is (x, y, z, w). 0x43b740: `cos = a·b >> 15`; `1 − cos < 21/32768` → linear
  blend; `1 + cos ≤ 20/32768` → a perpendicular quaternion (−a1, a0, −a3, a2) rotated in;
  else slerp through the angle table 0x6a0ee0 (0x43a660: `0x4786b0(i / 2048) · 4096 / 2π`,
  i = −2048..2047) and the sine table 0x6ab5a0; no sign
  flip toward the shorter arc. 0x437d90(h) returns track 0's first word, which every
  `LoadAnims<scene>` stores as the length (E-0318); frames advance by elapsed 66 ms ticks
  (E-0300). Corpus: 44 of 48 `.3DA` have exactly as many tracks as their scene has nodes
  (jardin one with 57 of 59, maisonj one with 16 of 17, mangeurs one with 23 of 25);
  every first rotation key has time 0; of 2,951 consecutive rotation-key pairs 36 have a
  negative dot product, 385 fall under the linear threshold, none under the opposite one.
  All 51 `call 0x438290` sites push mask 0 and t 0 (capstone scan of the pushes).
- **Method:** decompiled; corpus scan.
- **Confidence:** proven

### E-0017 — 0x4e3120 is cleared only by the museum frame when it acts on it; 0x4e30f4 is never cleared
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** the museum frame 0x42b776 tests `0x4e3120 == 1 && scene (0x4e3144) == 0 &&
  0x4aba48 == 0`, and only inside that branch sets the six robot parts' cursor type to 4,
  clears 0x59901c (speaking) and writes 0x4e3120 = 0; the only writer of 1 is 0x42f515
  (return from the option menu). So the flag stays set while it does not act (another
  scene, or 0x4aba48 = 1) and fires on the next museum frame that qualifies. 0x4e30f4 is
  written 1 by 0x42f2c2 (zone 11 return) and only read by the chambreb init 0x41c979
  (`== 1 && 0x4abd5c == 0` → 0x4abd5c = 1, play the static sound `miroir` once); nothing
  writes it back to 0, so the saved 0x4abd5c alone prevents a replay.
- **Method:** grep of the cited decompiler listings `notes/decomp/MISSION.EXE__FUN_0042b776.c`
  (lines 372–381), `…__FUN_0041c979.c` (156–159), `…__FUN_0042f2c2.c`, `…__FUN_0042f515.c`.
- **Confidence:** strong (the cited listings only; a Ghidra xref listing of both addresses
  would make it proven)

### E-0018 — The carry click has no edge: a button held over two frames picks up and drops
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x472710 reads the mouse with `IDirectInputDevice::GetDeviceState` (vtable
  +0x24, 16-byte DIMOUSESTATE) and stores `rgbButtons[0] >> 7` into `click` (0x5b7fac) every
  frame (called from 0x420e07). The mangeurs frame 0x429dd6: with 0x502734 = 0, `click == 1`
  and cursor 0x25 over a carriable node set 0x502734 = 1 and 0x502a80 = the node; with
  0x502734 = 1, any `click == 1` over a node (fire, stove or anything else) acts and writes
  0x502734 = 0. Nothing between the two waits for the button to go up; the frame clears
  `click` only at its end (lines 222–223), and the next 0x420e07 sets it again while held.
- **Method:** decompiler listings `notes/decomp/MISSION.EXE__FUN_00472710.c`,
  `…__FUN_00429dd6.c` (lines 38–90, 222–223).
- **Confidence:** proven for mangeurs (cafe 0x41bbcf and pont 0x42d489 follow the same
  pattern per E-0317; not re-read line by line)

### E-0440 — Zone screen start, cursors and animation rates in MainWndProc
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** MainWndProc 0x4122bb (`notes/decomp/MISSION.EXE__MainWndProc.c`): state 0
  calls `0x411807(0, -1, retour)` for every zone, which draws the last `LoupeOut` frame
  (magnifier state 2) and the slots (0x41170e), and starts `Retour`/`RetourM` (0x409c25,
  last argument 0 = looping) only when the third argument is 1 (zones ≠ 0); zone 0 then
  loads the bar (0x414fbf) and plays `LoupeIn` (0x41195b) → state 7. States 0, 4, 10, 0xB,
  0xC, 0xE, 0xF, 0x10..0x12, 0x16, 0x19..0x1D and 0x1F/0x1E set cursor 9 (0x40e25a(0, 9)).
  State 10 steps `CapsOP` (0x4099a4) on every tick; 0xB steps `CapsAO` on even ticks; 0xC
  and 0x1A step `CapsAC` on odd ticks; 0x1C steps `POT` on odd ticks. In state 5, `Retour`
  / `RetourM` are stepped (0x4099a4) only on odd ticks, with the bar closed, when the hit
  test (0x411454) returns 3 / 4, i.e. while the cursor is over them. Zone 4's puzzle 0x40241b
  also draws the slots (0x41170e) after both backgrounds of its steps 3 and 4 (lines 112–122).
- **Method:** decompiler listing lines 197–300, 476–520, 776–790; 0x411807; 0x40241b.
- **Confidence:** proven

### E-0441 — Result, fly-back and the end of a slot sequence
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** MainWndProc state 0xD: when the slot function returns, zones ≠ 0 reload the
  background and call `0x411807(-1, slot, 0)` (magnifier state 3 without drawing, slots
  with the run slot as `CapsAC`). State 0xF: result 0 on a just-placed object → `placed` =
  0, bar opens (0x4e25c8 = 1), sound `bar_obj` → 0x10; otherwise `CapsAC` plays, `fermcaps`;
  a zone ≠ 0 not yet done with every object placed → done = 1, state 0x1A (no magnifier);
  else the magnifier opens if closed (0x4119c2) → 0xC. State 0x10, once the bar has stopped:
  0x41138b re-inserts the object at its list index, `first` = index − 5 when index − first
  > 5, the bar and slots are redrawn, the `OP` sprite is drawn at the fly origin and sound
  0x4e265c (`cf_clic3`) plays → 0x11: 32 steps along the sine ease, then 0x411228,
  0x411153 and the bar closes (0x4e25c8 = −1) → 0x12: once the bar has stopped, the
  magnifier opens (0x4119c2), `Retour`/`RetourM` start → 5. State 0xC: zone 0 goes to the
  autosave (0x21) as soon as `CapsAC` ends; other zones on an even tick with the magnifier
  open (state 2) and `CapsAC` ended: 0x21 if just placed, else Retour → 5. State 0x21 after
  `Save_WriteGame`: zone 0 → 0x20 (−1); others start Retour and open the magnifier if
  closed → 5.
- **Method:** decompiler listing lines 500–660, 845–860.
- **Confidence:** proven
- **Supersedes:** the fly-back and 0x12 description in E-0412 (the bar closing was missing).

### E-0442 — Drags: rest position, sprite point and the sunflower drop
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x410ce4(mx, my, px, py, sprite, frame) stores the offset (px − mx, py − my)
  and the sprite; 0x410d68 draws it every tick at cursor + offset; 0x410dfa returns cursor
  + offset. State 0x17 calls 0x410ce4 with the cursor and 0x4a6ae8[TOURN index], so the
  grab offsets are TOURN's resting centre. State 0x18 on release tests 0x410dfa's point
  (the sprite's centre), not the cursor, against the pot area 0x4a6aa8; a miss draws
  `PA..a`'s last frame again (0x409c12 − 1) and plays `cf_clic3` → 0x17. Zone 0's slot
  function 0x411a28 does the same (0x410ce4, 0x410dfa, 0x4a6aa8; lines 163–193).
- **Method:** `notes/decomp/MISSION.EXE__FUN_00410ce4.c`, `…00410d68.c`, `…00410dfa.c`
  (decompiled from a read-only copy of the project), MainWndProc lines 683–775.
- **Confidence:** proven

### E-0443 — Option menu buttons, Quit and the credits skipping
- **Binary/file:** `/MISSION.EXE`; `Data/mission.___`
- **Evidence:** OptionMenu state 0: a click on button b (0x40e976; buttons 1..3 ignored
  while the volume row is open) draws `options` frame b at 0x4a6620[b] = (186, 66),
  (187, 154) × 3, (187, 243), (187, 331) → state 1, which on the release (any position)
  hides it and goes to page b + 2. Quit page (states 0xB, 0xC): a click on Yes/No (0x40eb34)
  draws frame 11 + i at 0x4a66e0[i] = (255, 281), (357, 281) → on release Yes writes the
  flags, GGAME, USERS and returns −2, No reloads `option`. Menu credits (state 0xE): > 250
  ticks, Space or the button down → next picture; after 16 back to `option`. End credits
  0x409645: Space or the button down → end of all pictures (state 3 waits for the button
  up, stops the sound).
- **Method:** `notes/decomp/MISSION.EXE__OptionMenu.c`, `…__FUN_0040e976.c`,
  `…__FUN_00409645.c`; tables read from `mission.___` (file offset = VA − 0x401000).
- **Confidence:** proven

### E-0444 — onAbort latches a per-zone flag; puzzles test it in their waiting steps
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** the eleven onAbort functions set a flag, some only for their puzzle's
  object: 0x40d1ef (0x4e1f74 when object 3), 0x402376 (0x4e039c when 6), 0x402ac2 (12),
  0x403ea1 (17), 0x404217 (21), 0x404b5f (24), unconditional 0x4034f2, 0x4056ac, 0x405f5b
  (0x4e039c), 0x4076b2, 0x407dd1 (0x4e0528). Each onPlace clears it (e.g. 0x4022c0,
  0x4029f5, 0x403346, 0x40d112, 0x407509, 0x407bc7). The flag is read only in the puzzle
  steps the zone docs name (e.g. 0x40241b cases 2 and 6, 0x40d293 case 3, 0x408118 cases
  1 and 6), which free the puzzle's sprites and sounds and return result 0; MainWndProc
  0xD calls onAbort when Backspace fired (0x4e2678). A Backspace outside those steps stays
  latched until the next such step.
- **Method:** `notes/decomp/MISSION.EXE__FUN_*.c` for the functions named; grep of the flag
  addresses over all listings.
- **Confidence:** proven

### E-0019 — The autosave and Escape store the view in the 3D block; the autosave skips the pitch
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x42f873 (autosave) writes camera x, y, z (0x651352/54/56) to block +0x30/+0x34/
  +0x38, yaw and roll (0x651348/4a) to +0x28/+0x2c, zone 0x502860 to +0x3e, scene 0x4e3144 to
  +0x3c, previous scene 0x4e3140 to +0x3d, copies 0x8c bytes from 0x651220 to +0x40, sets
  +0x00 from 0x4aba3c and calls `Save_WriteGGame(0x4aba40, 0x36c, 0)`. The pitch
  (0x651346) goes to 0x5b7fb0 only, not to +0x24. 0x42edef (Escape, when 0x598cb0 = 0)
  writes the same fields and the pitch to +0x24, like 0x42f755.
- **Method:** decompiler listings `notes/decomp/MISSION.EXE__FUN_0042f873.c`, `…0042edef.c`,
  `…0042f755.c`.
- **Confidence:** proven

### E-0020 — After the intro, a 3D resume starts at the scene's own start position (case A/B)
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** 0x42fbd6, mode 2, end of a movie with 0x4aba5c = 0, 0x502864 = 0, 0x4e4580 = 0 and
  0x50273c (the GGAME in_2d word, set by `Load3DGGame`) = 0: writes 0x502740 = 0x598cb0 = 0,
  then calls 0x41fda9, which picks case C only when 0x502740 ≠ 0x598cb0 (line 80). The
  camera `Load3DGGame` copied to 0x5b7f80.. is therefore not used.
- **Method:** decompiler listings `notes/decomp/MISSION.EXE__FUN_0042fbd6.c` (lines 50–90),
  `…__FUN_0041fda9.c`, `…__Load3DGGame.c`.
- **Confidence:** proven

### E-0367 — The one-pass averaged push-out leaks through one-sided walls at inside corners
- **Binary/file:** `/MISSION.EXE`; `Data/Scenes_3D/MUSEE.BFG` (`BOX.3DI`, `BOX1..4.3DI`)
- **Evidence:** rules of E-0304/E-0305 as read (integer `d` and edge distances with
  per-product truncation, 0x432220 / 0x431700; the mask cases of 0x432220's switch) run by
  `engines/peintre/tools/boxreach.py` from the museum entrance (-39, -209, 361), steps of 120
  per tick in 16..48 directions: `BOX1.3DI` (the closing wall x ≈ -1693, z 3699..4458,
  normal +x, two triangles) is crossed after a diagonal walk into the corner with the hall
  wall z ≈ 3710 (normal +z): two face contacts average to a push of 125 on each axis, the
  camera stays about 120 from the closing wall, the next step ends at d < 0 and the face is
  ignored. Traced path (sim): (-1584, -208, 3946) → (-1685, -208, 3786) → (-1707, -208,
  3955) → the act 1 gallery. With 32 directions every museum box set lets the viewer leave the
  building (200,000 cells, x to -25,000). With a check that undoes a tick crossing a wall
  triangle from its front: set 1 stays within x -1693..1729, z -168..5354; set 2 opens the
  left gallery (x to -5236), set 3 also the centre (z to 8701), sets 4 and none all three.
- **Method:** simulation of the spec'd rules over the corpus data; not observed in the
  original (running it needs the user's OK), so "the original leaks" follows from the rules.
- **Confidence:** likely
- **Doc:** `movement.md` "Collision"

### E-0368 — Scene track steps: end at frame >= length, special ends return unposed, loops pose frame 1; the museum star stops at 52; alternating tracks both restart at 1
- **Binary/file:** `/MISSION.EXE`
- **Evidence:** the per-scene step functions 0x41a2ab (auberge), 0x41cee9, 0x424c4c,
  0x4256af, 0x426f34, 0x427b98 (maisonet), 0x428c8c, 0x429b94, 0x42b5fe (musee), 0x42d26a:
  each adds the step (`DAT_00598ec0`, some `>> 1`) to `frame`, tests `length <= frame` (or
  `length / 2 <= frame`), and in the per-record branches sets flags and `return`s before
  the common tail; the tail sets `frame = 1` when `length <= frame` and calls
  `0x438290(animHandle, base + frame, base + frame, 0, 0)`. 0x42b5fe record 0 (the star):
  `frame >= 0x34` and `0x4aeb24 == 0` → `playing = 0, frame = 0x34`; else `length <= frame`
  → `playing = 0`; both fall through to the pose. 0x42b776 line "start the star's track"
  tests `0x4aba44 == 0 && frame != 0x34` (not the playing flag). 0x427b98 records 2/3
  (maisonet's bird): each end sets both frames to 1 and swaps the playing flags. Musee init
  0x42ad92 has no write to the star's node or its record: after the star is taken the node
  stays at its rest pose (inside the stand; only a tip shows in the engine's frame).
- **Method:** decompiled (the files in `notes/decomp/`).
- **Confidence:** proven
- **Doc:** `scene.md` "What a scene is made of"; resolves Q-0400, Q-0402, Q-0404

### E-0369 — A new player's 3D block is the EXE's initial data (non-zero words listed)
- **Binary/file:** `/MISSION.EXE` (`mission.___`)
- **Evidence:** the 0x36C bytes at 0x4aba40 in the image (`pefile` memory-mapped image):
  40 non-zero bytes, words listed in `save.md`. No `memset`/copy over the block on the
  new-player path: 0x4187ba only deletes the player's files; `Load3DGGame` 0x42f111 runs
  only for a known player (`boot.md` steps 3, 6); the player-name screen runs once per
  process. Every instruction whose operand falls in those words (capstone over all
  functions of `function-dump.tsv`): 0x4abc08 `cmp` in Mangeurs_Init 0x429989, `mov 0` in
  Mangeurs_Frame 0x42a35d; 0x4abcd8 `cmp 1` in Eglise_Init 0x42435f, `mov 0` in
  Jardin_Frame 0x42723a; 0x4abd60 `cmp 0` / `mov 1` in Chambreb_Init 0x41caec / 0x41cb07;
  byte 0x4abbfa `mov 2` in Musee_Frame 0x42c0ea; nothing else. No access by block offset
  (`[reg + 0x1c8]`, `+ 0x320`, `+ 0x330`) outside stack frames.
- **Method:** static read of the image and an operand scan.
- **Confidence:** proven
- **Doc:** `save.md` "A new player's block"; resolves Q-0235 (nothing writes 0x4abc08 but
  mangeurs' clear: its initial 1 makes the cuckoo sound on a new player's first visit) and
  the 0x4abd60 half of Q-0220 (initial 1, so chambreb's test never passes; written only)

