# Evidence log (Grumpa engine)

Every factual claim in `engines/grumpa/docs/` and `games/grumpa/docs/` must have an entry
here that names the thing that proved it. Claims without evidence are bugs, not shortcuts.

Append only. Do not rewrite history; if a claim turns out to be wrong, add a new entry
that supersedes it and mark the old one `SUPERSEDED by E-nnnn`.

Ranges: survey, disc and protection E-0001..; later areas take the next free hundred.

## Entry format

```
### E-0001 — <one-line claim>
- **Binary/file:** games/grumpa/discs/cab/Profileshell/Grumpa.exe | .../Scenes/Scene_001.scn
- **Evidence:** Ghidra address, trace line, or corpus statistic.
- **Method:** how it was obtained.
- **Confidence:** proven | strong | tentative
```

An entry at `tentative` confidence must also have a matching line in `OPEN-QUESTIONS.md`.

## Entries

### E-0001 — The corpus: one CD image; 32 files on the ISO, 6,111 in its InstallShield cabinet
- **Binary/file:** `games/grumpa/images/Grumpa.bin` (788,891,376 B, MD5 `d71ad24b…`) with
  `Grumpa.cue` (one track, `MODE1/2352`); converted to `Grumpa.iso` (335,413 sectors,
  MD5 `2130011020…`), volume `Grumpa`, created 2002-03-12 09:16:48
- **Evidence:** `engines/grumpa/notes/corpus-inventory.md`: `games/grumpa/discs/cd` 32
  files, 340,577,965 B (9 in `DIRECTX8/`); `games/grumpa/discs/cab` 6,111 files,
  439,633,841 B in 78 file groups (56 files are the MFC runtime and InstallShield's own
  engine and support files). Game data by file group: `Bitmaps` 2,262, `Meshes` 1,638,
  `Scenes` 221, `Actors` 4, `UI` 125, `Sounds_` 550 plus `Sounds_<Language>` 241..280,
  `Local_<Language>` 4 each, `Shell_<Language>` 33 each, `Movies_<Language>` 1 each (the
  Swedish films are the ISO's `Movies/`), `Save` 20, `Profileshell` 36 (the programs).
  Every file's MD5 in `engines/grumpa/notes/corpus-md5.tsv`.
- **Method:** `python tools/disc/bin2iso.py`; 7-Zip extraction of the ISO; unshield 1.6.2
  (`third_party/unshield`, built statically with MSYS2 gcc into `build-mingw/`):
  `unshield -d games/grumpa/discs/cab x games/grumpa/discs/cd/data1.hdr` (6,111 files, no
  errors; log `logs/grumpa-unshield.log`); `python engines/grumpa/tools/survey.py`.
- **Confidence:** proven

### E-0002 — Idol FX's "Grumpa", a Nordic edition (Danish, Finnish, Norwegian, Swedish), published by Vision Park
- **Binary/file:** `cd/Setup.ini`, `cd/fxroute.ini`, `cd/Autorun.inf`,
  `cab/Local_Swedish/Credits.txt`, `cab/Profileshell/shellmedia/grumpa.shl`
- **Evidence:** `Setup.ini`: `AppName=Grumpa`, `[Languages] Default=0x001d count=4 key0=0x0006
  key1=0x000b key2=0x0014 key3=0x001d` (Windows primary language IDs: Danish, Finnish,
  Norwegian, Swedish; Swedish the default). `fxroute.ini`: `company = "Idol FX"`,
  `product = "Grumpa"`, `first = "setup.exe"`, `second = "FXProfileShell.exe"`.
  `Autorun.inf` opens `FXRoute.exe`. The credits (Swedish) list programmers Anders
  Åkerfeldt, Andreas Thorsén, Martin Eklund, a "FXSTRUCTOR" credit (Jörgen Strömbro) and a
  producer at Vision Park. `grumpa.shl` plays `vpark.avi` and `idolfx.avi`. Each language
  has its own `Local_*` texts, `Sounds_*` voices, `Shell_*` launcher files and intro film.
- **Method:** reading the files.
- **Confidence:** proven

### E-0003 — `Grumpa.exe` is an MSVC 6 program wrapped in SafeDisc 2.60.052: its code and data are encrypted on disc
- **Binary/file:** `cab/Profileshell/Grumpa.exe` (2,095,817 B, MD5 `4ff56a31…`, PE timestamp
  2002-01-28 10:09:13 UTC)
- **Evidence:** `engines/grumpa/notes/binaries.md`: linker 6.0, Rich header of Visual
  C++ 6 tools; imports only KERNEL32, USER32, GDI32, ADVAPI32, ole32, DDRAW, DSOUND, WINMM;
  sections `.text` (entropy 7.99) `.rdata` (4.46) `.data` (7.68) `.rsrc` `stxt774`
  `stxt371`; SafeDisc's marker `BoG_ *90.0&!!  Yy>` at file offset 0xfd4 followed by the
  version 2, 60, 52. `.text` and `.data` are ciphertext, and `.rdata` holds no readable
  strings either (no file names, no messages), so nothing of the game can be read
  statically. The disc carries SafeDisc's companions: `drvmgt.dll`, `secdrv.sys`,
  `00000001.TMP` (2,048 B), `00000000.016`/`.256` (800×600 splash bitmaps, 4 and 8 bit).
  The other programs are plain MSVC 6 (linker 6.0): `FXRoute.exe` (autorun menu),
  `FXProfileShell.exe` (the launcher, MFC), `GrumpaConfig.exe` (settings, MFC).
- **Method:** `python engines/grumpa/tools/survey.py`; a printable-string scan of
  `Grumpa.exe`.
- **Confidence:** proven

### E-0004 — The image keeps SafeDisc's signature: 598 sectors with bad EDC between two files
- **Binary/file:** `games/grumpa/images/Grumpa.bin`
- **Evidence:** `build/edcscan.exe games/grumpa/images/Grumpa.bin` → `sectors 335413 mode2 0
  bad-edc 598 runs 537 first 10761 last 20290`. The ISO directory places `00000001.TMP` at
  LBA 10314 and `SECDRV.SYS` at 20315..20329: the bad sectors lie in the unallocated gap
  between them (no file covers LBA 10315..20314). A plain `.iso` drops the EDC, so only
  the `.bin` can reproduce the disc check.
- **Method:** `tools/disc/edcscan.c` (EDC = CRC-32, reflected polynomial 0xD8018001, over
  bytes 0..0x80F of each mode-1 sector); ISO 9660 directory walk of `Grumpa.iso`.
- **Confidence:** proven

## Formats

Ranges: survey, disc and protection E-0001..E-0004; formats E-0005..E-0099.

### E-0005 — `.atx`: text actor/object definitions, `<type><name>{ fields }` blocks; 114/114 parse
- **Binary/file:** `games/grumpa/discs/cab/**/*.atx` (114 files: `Actors/`, `UI/*/`,
  `Meshes/*.atx`)
- **Evidence:** `engines/grumpa/tools/parsers/atx.py` parses 114/114 with no leftover
  bytes. A file is a sequence of blocks, each an optional `<type><name>` header then a
  `{ ... }` body of one field per line (a value, a whitespace-separated tuple, or a file
  name with spaces; trailing comment from the first `/`). The first field is the actor id;
  a header-less block overrides the one before it (`UI/090_Inventory/090_Inventory.atx`).
  Header type codes in the corpus: 2, 3 (42), 4, 5 (65), 6, 22, 23, 27, 28 (5), 31, 37
  (20), 38 (20), 39 (40) — CFX class codes. The loader
  `CFXActorFactory::CreateFromATXFile` and the `CFX*` class names are strings in the
  decrypted `Grumpa.exe` (E-0003).
- **Method:** `python engines/grumpa/tools/parsers/atx.py` (over `games/grumpa/discs/cab`).
- **Confidence:** proven (file shape; per-class field meaning is game logic, not yet specced)

### E-0006 — Text configuration: `.btn`/`.shl` shell, `.sts` player status, `.tma` matrices, `.txt` UI text
- **Binary/file:** `cab/**/*.btn` (30), `cab/Shell_*/grumpa.shl` (4), `cab/Save/**/Player.sts`
  (7), `cab/Bitmaps/*.tma` (2), `cab/**/*.txt` (19)
- **Evidence:** `.shl`/`.btn` are `key = value` ini for the InstallShield profile shell
  (`FXProfileShell.exe`): `grumpa.shl` names window, background, `mov_name_*`, `btn_name_*`;
  each `.btn` gives `image_lo/hi/bubble`, `pos_x/y`, `rect_l/t/r/b`, `sound_hoover/click`,
  `execute_cmd` (`grumpa.exe`, a URL, or `shellmedia\grumpa.hlp`), `shutdown`. `.sts` is two
  lines (player name, a counter), read by `CFXMenu::LoadPlayerInfo`. `.tma` is rows of
  tab-separated floats for the `effect`/`effect_item` materials. `.txt` is cp1252 UI text
  (`Text.txt` labels `Nytt Spel`/`Ladda Spel`/..., `Credits.txt`, `Help.txt`), one copy per
  language. `value.shl` under `_MFC_*`/`_Support_*` is InstallShield's, not the game's.
- **Method:** reading the files; `CFXMenu::LoadPlayerInfo` string in the decrypted EXE.
- **Confidence:** proven

### E-0007 — Images, sound and video are standard formats
- **Binary/file:** `cab/**/*.{jpg,tga,bmp,wav,avi,mpg}`
- **Evidence:** magic census (`engines/grumpa/notes/corpus-inventory.md`): `.jpg` 1745
  (`ff d8 ff e0` JFIF), `.tga` 317 (`00 00 02 00` uncompressed Targa), `.bmp` 65 (`BM`),
  `.wav` 1612 (`RIFF`), `.avi` 10 (`RIFF`), `.mpg` 4 (`00 00 01 ba` MPEG-1 system). The
  game wraps them in `CFXBitmap`/`CFXSound` (strings in the decrypted EXE, E-0003). Read
  with off-the-shelf decoders; not re-specced.
- **Method:** `python engines/grumpa/tools/survey.py`.
- **Confidence:** proven

### E-0008 — `.fxi` is a surface with a compressed body — SUPERSEDED by E-0009 (dimensions vary; codec found)
- **Binary/file:** `cab/**/*.fxi` (316 files)
- **Evidence:** 8-byte header `u8 ver=1; u8 flag(2|0); u16 width; u32 height`; every file
  is 800×600 (`width=0x0320`, `height=0x00000258`), but the body length varies per file
  and is never `width*height*{1,2,3,4}` (test in the survey scratch: 0/316 for each), so
  the pixels are compressed. 280 files have flag 2, 36 have flag 0. Loaded by
  `CFXSurface`/`CFXTexture`/`CFXZBuffer` (strings, E-0003). The codec is read from those
  methods in the decrypted EXE (Q-0004).
- **Method:** header-vs-size correlation over all `.fxi`.
- **Confidence:** proven (header + that the body is compressed); codec open (Q-0004)

### E-0009 — Ghidra project `Grumpa.gpr` on the decrypted dump; the `.fxi` codec; 316/316 parse
- **Binary/file:** `build/grumpa-import/GRUMPA.EXE` (= `build/grumpa/Grumpa.dump.exe`,
  E-0003); `games/grumpa/discs/cab/**/*.fxi`
- **Evidence:** the decrypted dump imports and analyses in Ghidra
  (`ghidra_projects/Grumpa.gpr`, folder `/grumpa-import/`) and decompiles cleanly — the
  `CFX*` methods are all reachable from their error strings. `.fxi` is loaded by
  `FUN_00418de0` (the `fxi` arm of the extension switch `FUN_004189d0`:
  `tga`/`raw`/`fxi`/`pcx`/`jpg` at `DAT_0049cc9c..8c`). It reads `u8 version, u8 flag,
  u16 width, u16 height`, allocates a 16-bit surface (`FUN_00418910(this, w, h, 0x10)`),
  reads three u32, then: flag 0 → `width*height*2` raw 16-bit pixels; flag != 0 →
  `(width/8)*(height/8)` control bytes (one per 8×8 block, row-major), then per block two
  sub-blocks (control byte low nibble, then high nibble), each a mode: 0 solid (1 B),
  1 two-colour (8-B 1bpp mask + 2×u16, 10 B), 2 four-colour (16-B 2bpp mask + 4×u16, 20 B),
  3 raw (64 B). `engines/grumpa/tools/parsers/fxi.py` parses 316/316 consuming every byte;
  dimensions vary (173 are 800×600, the rest smaller, down to 56×56); flags 0:36, 2:280;
  all four block modes occur. The stream reader is `FUN_004026c0(stream, dst, n)`.
- **Method:** `python -m pyghidra.ghidra_launch ... -process GRUMPA.EXE ... decompile_one.py`
  on `0x00455380`/`0x004555c0` (`CFXSurface::CreateFromFile` chain) and `0x00418de0`
  (the codec); `python engines/grumpa/tools/parsers/fxi.py`.
- **Confidence:** proven (container and codec structure; per-mode pixel maths pending, Q-0004)

### E-0010 — Grumpa is a pre-rendered 3D adventure: 2D backgrounds + `.fxi` Z-depth buffers
- **Binary/file:** `games/grumpa/discs/cab/Bitmaps/` (1745 `.jpg`, 317 `.tga`, 316 `.fxi`)
- **Evidence:** all 316 `.fxi` are 16-bit images named `*_IZ` / `*_Z*` and live only in
  `Bitmaps/`; decoded (E-0009, `fxi.py`) they are smooth depth ramps with the scene's
  silhouettes (e.g. `100_1_IZ.fxi`, a ship over water: the ship's depth against a
  water/sky depth plane). The loader `CFXZBuffer::CreateFromFile` reads `.fxi` as depth;
  `CFXSurface::CreateFromFile` reads the same format as RGB555 colour (`FUN_004555c0`:
  `(px>>7)&0xf8`, `(px>>2)&0xf8`, `px<<3` — a 555 unpack). So the scenes are pre-rendered:
  a 2D colour background (`.jpg`/`.tga`) plus a matching `.fxi` depth buffer, and the 3D
  actors (`.anb`/`.amb` meshes, `CFXCharacter`/`CFXItem`) are composited into it with
  depth test. This is the engine's core architecture (like Ring's pre-rendered nodes, but
  with a real per-pixel depth buffer).
- **Method:** decode + naming/dir census of `.fxi`; the `CFXSurface`/`CFXZBuffer` loaders.
- **Confidence:** proven (format and role); the compositing pipeline itself specced later

### E-0011 — Scene views: `<n>_<v>_IS.jpg` colour + `<n>_<v>_IZ.fxi` depth; `_Z####` animated depth
- **Binary/file:** `games/grumpa/discs/cab/Bitmaps/`
- **Evidence:** the naming pairs a colour background with a depth buffer: `100_1_IS.jpg`
  (Image Screen) ↔ `100_1_IZ.fxi` (Image Z), 173 such pairs (175 `_IS` colour views, 173
  with depth). A second group, 143 files `*_Z####.fxi` (e.g. `14_2_kista__Z0000..`,
  `14_2_pittrap__Z0000..`), are per-frame depth for animated scene elements (a chest
  "kista", a pit trap), matched by colour frame sequences. So a scene view = one
  pre-rendered 800×600 colour image plus its 16-bit depth (E-0010), and animated props
  carry their own depth frames. `<n>` is the scene/room number, `<v>` the view/node within
  it. This is the on-disk half of the node model the engine composites actors into.
- **Method:** naming/pairing census of `Bitmaps/`.
- **Confidence:** proven

### E-0012 — `.abi` = a stream of actor records (`u32 type, u32 id, class data`); type = the `.atx`/CFX class code
- **Binary/file:** `games/grumpa/discs/cab/**/*.abi` (118: `Actors/Characters.abi`,
  `Items.abi`, `Scenes/Scene_NNN.abi`, `Save/**/<id>_status.abi`)
- **Evidence:** `CFXActorFactory::CreateFromABIFile` (`FUN_0040cef0`) opens the file as a
  binary stream and loops until EOF: read `u32` (actor type), read `u32` (actor id),
  `FUN_0040d270`→`CreateActor` (`FUN_0040d2f0`) makes the object, then the object's
  serialize (vtable+4) reads its own fields from the stream; repeat. `CreateActor` is a
  switch on the type that `new`s a class-specific size (`engines/grumpa/notes/actor-types.txt`,
  34 types 0x02..0x2a). These type codes are the same as the `.atx` block `<type>` headers
  (E-0005: 2,3,4,5,6,0x16,0x17,0x1b,0x1c,0x1f,0x25,0x26,0x27...), so `.atx` defines actor
  templates by class, `.abi` stores actor instances/state by the same class code, and the
  save files (`Save/**/<id>_status.abi`, `global.abi`) use the same record format
  (`SaveGameStatus` `FUN_00410390`, `LoadGlobalGameStatus` `FUN_0040fdb0`). The scene loader
  `FUN_0040cb30` loads `Scenes/Scene_N.scn` then `Scene_N.abi` per scene.
- **Method:** decompile of `FUN_0040cef0`, `FUN_0040d2f0`, `FUN_0040cb30`.
- **Confidence:** proven (record framing and type table); per-class serialize bodies pending
  (Q-0006), so no byte-exact validator yet.

### E-0013 — `.amb` mesh = `u32 count` + count×(pos[3f] + normal[3f]); 588/588 parse
- **Binary/file:** `games/grumpa/discs/cab/Meshes/*.amb` (588)
- **Evidence:** `CFXAMeshEx::CreateFromFile` (`FUN_00416a90`) opens `<base>.amb` binary and
  reads a `u32` vertex count, then per vertex a 12-byte position (x,y,z, one block into
  `this+0x150`) and a 12-byte normal (three reversed `u32` into `this+0x154`: z, then y,
  then x). So `.amb` = `4 + count*24` bytes. `engines/grumpa/tools/parsers/amb.py` parses
  588/588 consuming every byte (585 full + 3 four-byte stubs — a count with no data, which
  the game tolerates); 8,043 vertices total. Faces, UVs and animation are not in `.amb`;
  `CreateFromFile` then calls `FUN_004157d0` for the companion `.anb` (Q-0007).
- **Method:** decompile of `FUN_00416a90`; `python engines/grumpa/tools/parsers/amb.py`.
- **Confidence:** proven

### E-0014 — `.anb` holds a mesh's topology/UV/animation (header counts + record arrays)
- **Binary/file:** `games/grumpa/discs/cab/Meshes/*.anb` (939)
- **Evidence:** `FUN_004157d0` (called by `CreateFromFile` after the `.amb` vertices) reads
  the `.anb`: a header of several `u32` counts (into `this+0x118`, and locals for the
  section sizes), then arrays — `iStack_53c` records of `0x18` (24) bytes each (read in one
  block, likely faces: indices + per-face data), `u16` separators, and `iStack_544` records
  of 8 bytes each (likely UV or edge pairs). More sections follow (the function is 3,750
  bytes, 27 callees). The full record semantics and the animation frames are not yet
  decoded.
- **Method:** decompile of `FUN_004157d0` (read-size census).
- **Confidence:** strong (section framing); field meaning open (Q-0007)
