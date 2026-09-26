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
