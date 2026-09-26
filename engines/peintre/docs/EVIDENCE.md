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
