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

### E-0014 — `.anb` = the full mesh: geometry, UVs and vertex animation; 938/939 parse
- **Binary/file:** `games/grumpa/discs/cab/Meshes/*.anb` (939)
- **Evidence:** `FUN_004157d0` reads: `u32 frameCount F`, `u32 sectionCount S`, then per
  section `u32 A (verts), u32 B (uvs), u32 C (faces)`, `A*24` frame-0 vertices (pos[3f] +
  normal[3f], normal stored z,y,x), `C*6` face vertex-index triples (3×u16), `B*8` texture
  coordinates (2×f32), `C*6` face uv-index triples (3×u16); then a trailing block of
  `K*(ΣA)*24` = further animation frames (vertices only). `engines/grumpa/tools/parsers/anb.py`
  parses 938/939 consuming every byte (193,420 base vertices, 358,673 triangles); the one
  failure (`012_D2D_Grumpa_In_Boat.ANB`) carries 4,456 extra trailing bytes (a special
  composite). K = F-1 frames for most meshes, K = F for the `X2Y` transition-animation clips
  (N2N idle, N2W normal→walk, W2R walk→run, ...); the in-file discriminator between the two
  is not yet pinned (Q-0007). A `.amb` (E-0013) is the same vertex block for a mesh that has
  no `.anb`. This is the renderable geometry for the 3D actors.
- **Method:** decompile of `FUN_004157d0`; `python engines/grumpa/tools/parsers/anb.py`.
- **Confidence:** proven (geometry, UVs, byte layout); the K=F vs F-1 discriminator open (Q-0007)

### E-0015 — The `.anb`/`.amb` geometry decode is correct (meshes render as their objects)
- **Binary/file:** `games/grumpa/discs/cab/Meshes/*.anb`
- **Evidence:** projecting a parsed mesh's frame-0 vertices and triangles (E-0014) to an
  image gives the recognisable object — `000_N2N_Bear.ANB` (252 verts, 500 tris) renders as a
  low-poly bear (body, clawed arms, legs, eared head); `000_N2N_Boat.ANB` as a boat hull.
  Confirms the vertex/face/winding decode, not just the byte counts.
- **Method:** orthographic front-view render of `anb.parse()` output.
- **Confidence:** proven

### E-0016 — The 3D device: a software rasteriser on an 800×600×16 DirectDraw surface
- **Binary/file:** decrypted `Grumpa.exe`; `FUN_00436aa0` (init), `FUN_0042db40` (device factory)
- **Evidence:** `FUN_00436aa0` creates the `IFXDirectFX` device via `FUN_0042db40`
  (`&DAT_00490538`, the "CreateFXDirectX" object) and initialises it through the device
  vtable `+0x1c` with `(hwnd, 800, 600, 0x10, 0x10, 0x75)` — 800×600, 16-bit. It then
  fetches a render context (vtable `+0x38`) and sets render states (`+0x94`: state 0x10/0x11
  =2, 2=2, 3=0). The device imports only DDRAW/DSOUND (no Direct3D, E-0003), so the 3D is a
  software rasteriser writing the 16-bit DirectDraw surface — the same 800×600 RGB555 page
  the engine uses (E-0010). The ScummVM engine now has its own equivalent: `render3d.cpp`
  (a perspective, z-buffered, flat-shaded triangle rasteriser) renders `.anb` meshes (E-0014)
  correctly (verified: `000_N2N_Bear` renders as a bear).
- **Method:** decompile of `FUN_00436aa0`; the engine's `render3d.cpp` + `grumpa_mesh` dev dump.
- **Confidence:** proven (device setup, screen format, and that the renderer works); the
  per-view camera (eye/orientation/FOV) that places actors in each pre-rendered scene is set
  during the scene render tick from scene data not yet located (Q-0008)

### E-0017 — `.fxi` depth is a standard screen-linear z-buffer; `startScene.txt` boots into a scene
- **Binary/file:** `games/grumpa/discs/cab/Bitmaps/*_IZ.fxi`; `Grumpa.exe` `FUN_00436aa0`
- **Evidence:** on a view with a flat floor (`85_1_IZ.fxi`), the decoded 16-bit depth down a
  column is a straight linear ramp (0xa200, 0x94c0, 0x8780, … 0x1000, step ≈ 0xd40). A
  perspective z-buffer value is affine in screen space across any planar surface, so a flat
  floor giving a linear ramp confirms `.fxi` stores a perspective depth-buffer value
  (`~1 - n/Z` scaled to 16 bit), not world Z. Compositing an actor needs the same
  near/far/scale and the per-view camera to turn the actor's view-space Z into this value.
  Separately, `FUN_00436aa0` opens `startScene.txt` from the data folder and parses it
  (`FUN_004025a0`/`FUN_00407e70`): a dev hook to boot directly into a given scene, skipping
  the menu — the way to reach a scene for a runtime read of the live camera.
- **Method:** depth-column analysis of `85_1_IZ.fxi`; decompile of `FUN_00436aa0`.
- **Confidence:** proven (z-buffer nature; the startScene.txt hook); near/far/scale + camera open (Q-0008)

### E-0018 — The gameplay layer: triggers (hotspots), scene commands, per-class actor serialize
- **Binary/file:** decrypted `Grumpa.exe`; `FUN_00457ea0` (`CFXTrigger::Serialize`),
  `FUN_0040f7b0` (`CFXActorFactory::LoadSceneCommands`)
- **Evidence:** interaction/navigation is driven by `CFXTrigger` actors (type in the `.abi`,
  E-0012): `CFXTrigger::Serialize` reads a region/position (`this+0x108..0x110`), a list of
  `0x118`-byte sub-records, a block of fields (`0x170..0x188`), a 19-entry array, and a
  `CFXSprite` — i.e. a hotspot with sub-triggers, a bubble/sprite and action data.
  `LoadSceneCommands` reads `%s\Current\%s` (a count then that many command records): the
  per-playthrough event/command list, stored in `Save/Current/` and updated as the game
  runs (the dynamic scripting state). So the game logic = static `.abi` actors (triggers,
  spawn/warp points, characters, items) + a dynamic command list per scene. Decoding each
  CFX class's serialize (Q-0006) and the command set is the bulk of the remaining work — a
  large layer on top of the rendering core that is complete.
- **Method:** decompile of `FUN_00457ea0`, `FUN_0040f7b0`.
- **Confidence:** strong (the layer's shape and the two entry points); per-class/per-command
  fields open (Q-0006)

### E-0019 — The actor serialize dispatch: type -> constructor -> Serialize (vtable[1])
- **Binary/file:** decrypted `Grumpa.exe`; `FUN_0040d2f0` (CreateActor), `FUN_0040cef0`
  (CreateFromABIFile)
- **Evidence:** `.abi` records are `u32 type, u32 id, <class serialize>` (E-0012).
  `CreateFromABIFile` calls the actor's `Serialize` via `obj->vtable[1]`
  (`(**(code**)(*actor + 4))()`). `CreateActor` news each type's object and runs its
  constructor (the 4th arg to the array-ctor helper `FUN_0047bea5`), which installs the
  vtable; so type -> ctor -> vtable -> `Serialize` (`engines/grumpa/notes/actor-types.txt`).
  Confirmed: type 6 ctor `0x413a60` -> vtable `0x4903dc` -> serialize `0x414090`; type 0x19
  ctor `0x457b80` -> serialize `0x457ea0` (`CFXTrigger::Serialize`). Decoding every type's
  serialize (the fields each reads) is the systematic work that turns the `.abi` into a 100%
  parser and the game-state model (Q-0006).
- **Method:** decompile of `FUN_0040d2f0`/`FUN_0040cef0`; `tools/ghidra/scripts/actor_vtables.py`.
- **Confidence:** proven (the dispatch mechanism and two mappings); the per-type serialize
  fields remain (Q-0006)

### E-0100 — `.abi` container: a flat record stream to EOF, serialize mode 1
- **Binary/file:** decrypted `Grumpa.exe`; `CFXActorFactory::CreateFromABIFile`
  (`FUN_0040cef0`); `games/grumpa/discs/cab/{Scenes,Actors}/*.abi`
- **Evidence:** `CreateFromABIFile` opens the file as a C++ `ifstream` and loops: read
  `u32 type` (`FUN_004026c0(&arc,&t,4)`), break on EOF, read `u32 id`, break on EOF,
  `CreateActor(t,id)`, then `actor->vtable[1](&arc, mode)`. The mode pushed at the call
  (`0x40d0b8 CALL [EDX+4]` with `PUSH EDI`/`PUSH EAX`) is **1**: type 0x05's full-load path
  is its `case 1` arm (it has no `case 2`), and `Actors/Items.abi` parses exactly as that
  arm. A trailing chunk shorter than 8 bytes (a `type` with no `id`) just ends the loop;
  `Scene_400.abi` has 4 such padding bytes. So `.abi = { u32 type, u32 id, Serialize1 }*`.
- **Method:** decompile `FUN_0040cef0`, `FUN_004026c0`/`FUN_00402220`; disasm of the call
  site 0x40d02e..0x40d0b8; validator `engines/grumpa/tools/parsers/abi.py`.
- **Confidence:** proven (container + mode; parser consumes 100% of scene + item files).

### E-0101 — `.abi` shared vector element classes EC, ClassC, ClassD
- **Binary/file:** decrypted `Grumpa.exe`; `FUN_00409920`, `FUN_00409150`, `FUN_00409cf0`;
  vtables `PTR_FUN_004902ec`/`_004902e4`/`_004904b8`.
- **Evidence:** actors hold std::vectors of three recurring classes, resolved via the resize
  prototypes' vtables and serialized through `vtable[1]`:
  `EC` (`0x409920`, stride 0x118) reads 5 u32 (20 B, a leaf);
  `ClassC` (`0x409150`, stride 0x128) reads 5 u32 + `u32 n` + `n`×EC;
  `ClassD` (`0x409cf0`, stride 0x124, type 3 only) reads an EC-vector then a ClassC-vector.
  Two embedded inline sub-objects also recur, serialized in place with no type/id prefix:
  `0x456d70` (14 u32 = 56 B) and `0x401c00` (2×0xc = 24 B). Pascal strings are read by
  `FUN_00430c50` (`u32 len` + `len` bytes).
- **Method:** decompile of the three serializers + `read_ptr.py` on their vtable[1] slots.
- **Confidence:** proven (the parser reproduces every counted vector byte-for-byte).

### E-0102 — `.abi` actor-type field layouts (mode-1 Serialize) decoded; validator at 100%
- **Binary/file:** decrypted `Grumpa.exe`; the per-type serializers (see
  `engines/grumpa/notes/actor-types.txt`); `engines/grumpa/tools/parsers/abi.py`.
- **Evidence:** the mode-1 read sequence of every actor type present in the corpus is
  decoded: 0x11 view, 0x18/0x2a `CFXSound`, 0x19 `CFXTrigger`/`CFXSprite`, 0x0d, 0x1a, 0x07,
  0x1d, 0x1e, 0x20, 0x21, 0x22/0x25, 0x23/0x26, 0x24/0x27, 0x05 `CFXItem`. Two are
  value-dependent: 0x19 reads a "bubble" array only when its +0x1ac field == 2, and 0x0d
  reads two extra u32 only when its +0x20c field == 1. Type 0x20's transform vector is
  pre-sized to 5 by its ctor `FUN_00434200`, so it reads 5×0x10 bytes with no in-stream
  count. **Counts:** `abi.py` parses **111/111** scene + item `.abi` consuming every byte —
  2004 records (0x05:66, 0x07:4, 0x0d:310, 0x11:180, 0x18:365, 0x19:397, 0x1a:260, 0x1d:47,
  0x1e:40, 0x20:106, 0x21:158, 0x22:16, 0x23:31, 0x24:24), 4 trailing padding bytes total
  (Scene_400). The 2 `CFXCharacter` (type 0x03) database files are not modelled (Q-0006).
- **Method:** decompile of each serializer; iterative validation against the corpus.
- **Confidence:** proven for the 14 listed types (byte-exact over the whole scene corpus);
  type 0x03 open (Q-0006).

### E-0103 — The per-view camera block (Q-0008)
- **Binary/file:** decrypted `Grumpa.exe`; `CFX*View::Serialize` `FUN_0043d200`; the corpus
  scene views.
- **Evidence:** at the end of a type-0x11 view record (after its two `ClassC` vectors) the
  view reads `u32 cam_id` then a **0x68-byte block = 26 little-endian floats**, stores it at
  `this+0x14c` and hands it to the render device:
  `dev=*(this+0x148); dev->vtable[0x38]()->vtable[0x48](*(this+0x1b4), block)` (the handle
  `*(this+0x1b4) = view[0x108] - 0x276`). Over the 107 single-view scenes the only
  non-zero/varying floats are: `f1=1.0`, `f2∈[0.75,1.0]`, `f3∈[0.70,1.0]` (projection
  scale), `f13,f14,f15` = camera **position** x,y,z (range ±~7000), `f19` = range/far
  (157..10291, scales with scene extent), `f21=1.0`; floats 0,4–12,16–18,20,22–25 are 0 in
  the whole corpus (the rotation fields — these views are axis-aligned). The engine can
  place actors at world position `f13..f15` and project with `f2/f3` + `f19`.
- **Method:** decompile `FUN_0043d200`; `abi.py` camera extraction over all scenes.
- **Confidence:** strong (block location, size and the position/range fields proven across
  107 views); exact meaning of f2/f3/f19 and the device consumer `vtable[0x48]` not yet
  decompiled (Q-0008 sub-point).

### E-0104 — The `.abi` scene-load model and render-device injection
- **Binary/file:** decrypted `Grumpa.exe`; `CFXActorFactory::CreateFromABIFile` `FUN_0040cef0`,
  `CFXActorFactory::CreateActor` `FUN_0040d2f0`.
- **Evidence:** `CreateFromABIFile` opens the file as a C++ ifstream (`FUN_00412c30(...,0x21)`
  = `ios::in|ios::binary`) and loops to EOF: `read u32 type` (`FUN_004026c0(&stream,&type,4)`),
  `read u32 id`, `CreateActor(type,id,&actor)` (`FUN_0040d270`→`FUN_0040d2f0`), then
  `actor->vtable[1](&stream, 1)` — the Serialize of each `CFX*` class run in **load mode 1**.
  `CreateActor` requires the factory's render device `*(factory+0x128)` (errors
  `CFXActorFactory::CreateActor - m_pDevice NULL` when 0), `operator_new`s the class by its
  type-keyed size (switch of 34 cases, sizes in `notes/actor-types.txt`), and immediately
  injects the device: `actor->vtable[2](*(factory+0x128))`. So every actor holds the shared
  render device at its own `+0x148`; the type-0x11 view's camera consumer
  (`dev->vtable[0x38]()->vtable[0x48]`, E-0103) is that device.
- **Method:** read `FUN_0040cef0` and `FUN_0040d2f0` (in `notes/decomp/`).
- **Confidence:** proven (the record loop and the device-injection call are explicit).

### E-0105 — Per-view camera block field values across the corpus
- **Binary/file:** the scene `.abi` camera blocks (E-0103), extracted with `abi.py`.
- **Evidence:** the 0x68 block is 26 little-endian floats; across every scene view the only
  non-zero entries (0-based index) are: `[1]=1.0` and `[21]=1.0` (constants), `[2]` and `[3]`
  = per-axis projection scale (x,y; 1.0 ⇒ 90° field of view, smaller ⇒ wider, e.g. Scene_001
  `[2]=0.88 [3]=0.83`), `[13][14][15]` = camera eye position (x,y,z; e.g. Scene_007
  `47.9, 530.9, 1146.1`), `[19]` = far/range (scene-sized, 157..10291). All other indices,
  including the nine that would hold a 3×3 orientation, are 0 in the whole corpus, so the
  views are orientation-identity: with the eye above and in front (+Y, +Z) of geometry that
  sits toward −Z, the camera looks along **−Z** with up **+Y**. Engine camera model:
  `eye=[13,14,15]`, `forward=(0,0,-1)`, `up=(0,1,0)`, NDC `= ([2]·vx/vz, [3]·vy/vz)`,
  far `=[19]`. The exact device projection math (`vtable[0x48]`) is still to be decompiled;
  this model is validated against the pre-rendered backgrounds (Q-0008 sub-point).
- **Method:** `abi.py` camera extraction; corpus statistics over all scene views.
- **Confidence:** strong (values proven over the corpus); projection formula empirical.

### E-0106 — Type 0x0d is an animated 2D sprite prop (JPG frame sequence)
- **Binary/file:** decrypted `Grumpa.exe` `FUN_0044ccb0` (type 0x0d Serialize); scene `.abi`;
  the `Bitmaps/` corpus.
- **Evidence:** a 0x0d record ends with a pascal string naming a JPG frame base — e.g.
  Scene_100 `cannons_0000.jpg`, `flagga_0000.jpg`; Scene_007 `butterfly3_0000.jpg`,
  `burningroots_0000.jpg` — and the disc holds the matching frame sequence
  (`cannons_0000.jpg`..`cannons_0009.jpg`+, `butterfly3_0000..0007.jpg`). The record's 8-u32
  header holds small animation parameters (frame count / rate / loop flags, e.g. `18,5,-1`
  and `25,3,-1`), and its `sub_456d70` block is all-zero (no 3D transform). So the bulk of a
  scene's moving content is **animated 2D sprites** composited over the pre-rendered
  background, and the `.anb`/`.amb` 3D meshes are for characters (type 0x03) — the engine's
  3D camera path applies to characters, the 2D sprite path to props.
- **Method:** `abi.py` field extraction over the scene corpus; `Bitmaps/` frame listing.
- **Confidence:** strong (JPG frame base and anim parameters proven; per-frame screen
  placement and the depth/alpha mechanism are open, Q-0009).

### E-0107 — Type 0x0d sprite position, animation params and colour key — the +0x1e0/+0x1e4 reading SUPERSEDED by E-0208
- **Binary/file:** `FUN_0044ccb0` (0x0d Serialize); scene `.abi`; the `Bitmaps/` sprites.
- **Evidence:** a 0x0d record's gate field (+0x20c) is 1 for every placed prop seen; when 1
  the Serialize reads two more u32 at +0x190/+0x194 — the sprite's **screen position (x, y)**
  in 800×600 pixels (cannons 272,256; flagga 392,48; butterfly3 120,240; fork_AI 520,32;
  Boulder_left_cam2 229,560 — all inside the frame). The 8-u32 block before the gate holds
  animation parameters (e.g. cannons `…,18,5,-1,…`, flagga `…,25,3,-1,…` = frame count, rate,
  loop). The sprite JPGs are small (butterfly3 48×48, flagga 62×56, cannons 216×128), so each
  is a positioned overlay, not a full frame; `sub_456d70` and the EC/CC vectors are empty for
  these props. Transparency is a **colour key**: keyed sprites (butterfly3, w) are pure blue
  `(0,0,254)` outside the art; the two leading header ints `h[0],h[1]` (0/1) likely select the
  blend/key mode (smoke sprites like cannons use a different blend). Per-frame depth vs the
  scene `_IZ.fxi` is still open (Q-0009).
- **Method:** `abi.py` field extraction; Pillow inspection of the sprite JPGs.
- **Confidence:** strong for position and frame/rate; colour-key value empirical; blend-mode
  flags and depth open (Q-0009).

### E-0108 — Type 0x19 is a clickable hotspot polygon (CFXTrigger)
- **Binary/file:** `FUN_00457ea0` (0x19 Serialize); scene `.abi`.
- **Evidence:** after its header, flag blocks, `sub_456d70`, EC and CC vectors, a 0x19 record
  reads a count `k` then `k` pairs of **float (x, y)** — a screen-space polygon, the clickable
  hotspot region — followed by a 16-byte tail (4 floats) and a mode u32; when mode==2 it adds
  a list of named "bubbles". Example: Scene_007 id=660 polygon
  `(355,306)(363,105)(481,115)(463,316)` is the central jungle path in view `7_1` (the
  "walk forward" region). The action the hotspot triggers (e.g. go to another scene) is **not
  an inline field** (the 19-u32 block is all zero); it binds through the game's event/command
  system (Q-0010).
- **Method:** `abi.py` field extraction over the scene corpus.
- **Confidence:** strong (polygon shape and screen placement proven; action binding open).

### E-0109 — The scene command/event list (CC vector on actors)
- **Binary/file:** scene `.abi`; the `CC`/`EC` element classes (`FUN_00409150`/`FUN_00409920`).
- **Evidence:** the `CC` vector carried by triggers (0x19) and other actors is a **command
  list**. Each `CC` entry is a 5-int command `(-1, targetId, opcode, arg, flag)` plus a nested
  list of `EC` 5-int conditions `(id, a, opcode, b, flag)`. The `targetId` references another
  actor in the same scene by its record id: in Scene_007 the central-path trigger id=660 lists
  commands on ids 730 and 733 (the `burningroots`/`roots_with_acid` sprite props), 732
  (`roots`), 660/663 (triggers) and 640/663 — so clicking the hotspot drives the other actors
  (enable/play/animate), not a single "go to scene" field. The opcode column recurs (13 on
  many self/other targets; 500, 42, 16, 11, 72, 50, 99, …) and is the command verb; the EC
  sublists are guard conditions. This is the game's event system — triggers, puzzle state,
  navigation and interactions all run through these per-actor command lists.
- **Method:** `abi.py` extraction of the EC/CC vectors on 0x19 records.
- **Confidence:** strong for the structure and the id cross-references; the opcode semantics
  (the verb table) need the trigger's command-execution code (Q-0010).

### E-0110 — The event VM: global command queue and per-actor DoCommand dispatch
- **Binary/file:** `FUN_0040efa0` (the dispatcher); `FUN_0040d270` (actor registration);
  `FUN_0040f4c0`/`FUN_0040f7b0` (Save/LoadSceneCommand); globals `DAT_004b9bc4` (actor table),
  `DAT_004b9b9c` (command list), `DAT_004b9ba0` (pending count).
- **Evidence:** actors are registered in a **flat global array indexed by id**:
  `FUN_0040d270` stores the new actor at `DAT_004b9bc4[id]` and writes the id to `actor+0x108`.
  Events run through a **global command list** `DAT_004b9b9c` (a doubly linked list). Each node
  is a 5-int command `(when, targetId, opcode, arg1, arg2)` (the CC base fields, E-0109). The
  dispatcher `FUN_0040efa0` walks the list and, for every command whose `when` equals the
  factory's current time (`factory+0x130`), calls the target's **`DoCommand` = vtable index 6
  (offset 0x18)**: `actor->vtable[6](opcode, arg1, arg2)`; a `targetId` of −1 broadcasts to
  every actor in the table. The command is then unlinked and the pending count decremented.
  So: triggers (0x19) enqueue their CC command templates; the dispatcher routes each to
  `DAT_004b9bc4[targetId]->DoCommand(opcode, …)`; **the opcode meaning is per actor class** (a
  sprite interprets play/show/hide, a trigger enable/disable, etc.). Navigation, puzzles,
  inventory and dialogue all run on this one queue.
- **Method:** decompile `FUN_0040efa0`, `FUN_0040d270`; xref of the two globals.
- **Confidence:** proven (the dispatch loop, the id-indexed table and the vtable[6] call are
  explicit). The per-class opcode tables (each class's `DoCommand`) are the next step (Q-0010).

### E-0111 — The command opcode vocabulary (per-class DoCommand)
- **Binary/file:** `FUN_0044e2c0` (sprite 0x0d DoCommand), `FUN_004594e0` (trigger 0x19
  DoCommand), `FUN_00408670` (base, empty). Called as `actor->vtable[6](opcode, arg1, arg2)`
  by the dispatcher (E-0110).
- **Evidence:** a shared command vocabulary (same opcodes across classes, each toggling the
  actor's state flags `+0x10c` "active/updating" and `+0x110` "visible/drawn"):
  `0` play/start, `1` stop, `2` show (+0x110=1), `3` hide (+0x110=0), `11` activate (+0x10c=1),
  `12` deactivate (+0x10c=0), `13` disable + set the one-shot latch (+0x210 sprite / +0x184
  trigger; turns the actor fully off and blocks further commands until re-enabled), `52`
  (0x34) clear the latch (re-enable — the only opcode honoured while latched), `86` (0x56)
  reset/init, `500` full on (show + activate + play), `501` (0x1f5) full off. Trigger extras:
  `14`/`15` set/clear +0x154, `18` and `22` take an argument (`FUN_00459640`/`FUN_00459a40`),
  `23` sets the global `DAT_0049f200=-1`. Worked example — Scene_007's central-path trigger
  (id 660, E-0109) on click: `burningroots`(730)→500 on, `roots_with_acid`(733)→500 on,
  `roots`(732)→13 off, self(660)→13 off (one-shot), trigger 663→11 activate: the burn-the-roots
  puzzle step.
- **Method:** decompile the two `DoCommand` overrides; cross-check against the Scene_007
  command list.
- **Confidence:** strong (the opcode switches are explicit); a few sub-handlers
  (`FUN_0044d7e0`, `FUN_00459640/a40`) and the opcodes on other classes (sound, character,
  scene/navigation) remain to decode.

### E-0112 — Commands are timed and condition-guarded (the puzzle VM) — timing SUPERSEDED by E-0200
- **Binary/file:** scene `.abi` trigger command lists (E-0109); the dispatcher `FUN_0040efa0`
  (E-0110).
- **Evidence:** the first int of a command (the `when` field the dispatcher compares to the
  factory's current time) is a **delay in ticks**: `-1` fires immediately when the trigger is
  clicked, a non-negative N fires N ticks later. Each command also carries a nested `EC`
  **condition list** (the sublist in the CC, E-0109): the command runs only if the condition
  holds. A condition `EC` tests another actor's state — e.g. Scene_061's gate trigger (661)
  branches on actor 269 (a state variable): commands guarded by `(269,0,0,…)` run when its
  value is 0, those guarded by `(269,0,1,…)` when it is 1. Worked example (trigger 661):
  immediately hide the `doorclosed` sprite (open the gate) and deactivate itself; then at
  +10 ticks show the door again, trigger sounds (ids 600/644), and — depending on variable
  269 — activate triggers 664/665. So a trigger enqueues a **timed, conditional command
  sequence**: this is the game's puzzle/logic VM. A first engine slice runs only the immediate
  (`when==-1`), unconditional commands (verified: the gate opens on click); the timed and
  guarded commands need a per-tick command queue and the variable/counter actor classes.
- **Method:** dump the trigger command lists with their `when` and condition fields; confirm
  against the running engine (scene 61 gate).
- **Confidence:** strong (the delay semantics match the dispatcher; the condition shape and
  the variable branch are clear). The full timed/conditional execution and the variable actor
  classes are the remaining work (Q-0010).

### E-0113 — Trigger click dispatch and command enqueue
- **Binary/file:** `FUN_00459640` (trigger DoCommand opcode 18), `FUN_00459740` (enqueue),
  `FUN_004010f0` (point-in-polygon), `FUN_00408760` (push onto the global queue).
- **Evidence:** the scene's input broadcasts a **click as opcode 18** carrying the packed
  (x, y) (short lo/hi) to triggers. A trigger's handler (`FUN_00459640`) fires only if it is
  active (`+0x10c`), the click is inside its polygon (`FUN_004010f0` on `this+0x140`), and its
  state gate passes (`this+0x174` == the current value of a referenced variable actor, plus
  flags at `+0x178/+0x17c/+0x180`); it then calls the enqueue `FUN_00459740`. The enqueue
  walks the trigger's command vector (`this+0x12c`, stride 0x128) and copies each command —
  `+0x104` when, `+0x108` targetId, `+0x10c` opcode, `+0x110`/`+0x114` args, `+0x118`
  conditions — into a new node pushed onto the global command queue (`FUN_00408760`). This
  pins the command field layout used by the dispatcher (E-0110) and confirms the engine's
  click→fire model: a hit trigger queues its whole timed/conditional sequence.
- **Method:** decompile the trigger DoCommand opcode-18 handler and the enqueue.
- **Confidence:** proven (the polygon test, the field copy and the queue push are explicit).

### E-0114 — Type 0x1a is a textured 3D animated mesh actor (scene characters/props)
- **Binary/file:** `FUN_00452100` (0x1a Serialize); scene `.abi`; `Meshes/`, `Bitmaps/`.
- **Evidence:** a 0x1a record ends with two pascal strings naming an `.ANB` mesh and a `.tga`
  texture, e.g. Scene_061: `061_Sword of Might Pullout.ANB`/`som.tga`,
  `grumpa_try_sword_061.ANB`/`000_grumpa.tga`, `grumpa_success_sword_061.ANB`,
  `boulder B_at ground.ANB`/`boulder.tga`, `plattform_up.anb`/`plattform.tga`,
  `blade_up.ANB`. So **type 0x1a is the scene's 3D animated-mesh actor** — the characters
  (Grumpa's per-scene animations) and 3D props — rendered through the per-view camera
  (E-0105) with the `.anb` geometry (E-0014) and `.tga` texture, composited against the
  `_IZ.fxi` depth. It carries a world transform (the `sub_456d70`/sub-object blocks of its
  record) and **eight** `CC` command lists (distinct event hooks: enter, click, success, …;
  E-0109). The scene's moving content is therefore 2D sprite props (0x0d, E-0106) plus 3D
  mesh actors (0x1a); the standalone character database is type 0x03 (Q-0006).
- **Method:** `abi.py` extraction of the 0x1a record strings across scenes.
- **Confidence:** strong (mesh/texture names proven); the transform offset and the eight
  command hooks' roles remain to pin down.

### E-0115 — The per-view camera is a look-at camera (eye -> scene target ~origin)
- **Binary/file:** the scene view camera blocks (E-0105); the 0x1a meshes (E-0114); the
  pre-rendered backgrounds.
- **Evidence:** the camera block stores an eye position (`block[13..15]`) but no orientation
  (all would-be rotation floats are 0, E-0105), yet different views of one scene have very
  different eye positions (Scene_061: view 630 eye (-1453,-320,83), view 633 (16,352,5)). The
  camera therefore **looks at a fixed scene target** (≈ the origin): `forward =
  normalize(target - eye)`, up +Y (or +Z for a near-vertical top-down view). Projecting the
  scene's world-space 0x1a meshes through this camera lands them on their features in the
  matching background — Scene_061 view 633 (eye above, looking down) over the top-down
  background `61_1` puts the `plattform` mesh on the floor's circular socket, and view 630
  (eye to the side) over the side background `61_2` stands the platform as a pillar on the
  corridor floor. So the top-down view pairs with the top-down background and the side view
  with the side background (the view→background selection rule, Q-0011, is still to be pinned,
  but the camera geometry is confirmed). NDC = `(block[2]·vx/vz, block[3]·vy/vz)`; the exact
  target point and any field-of-view scaling (a small residual offset remains) are the
  remaining calibration (Q-0008).
- **Method:** wireframe overlay of the meshes through each view's camera on each background.
- **Confidence:** strong (look-at model confirmed visually on two angles); exact target/FOV
  and the view→background rule open.

### E-0116 — Navigation: go-to-scene and change-view commands (reserved managers 185/186) — the 186 part SUPERSEDED by E-0206
- **Binary/file:** scene `.abi` trigger commands (E-0109); `FUN_0040e980` (scene-manager
  tick), `FUN_0040cb30` (LoadScene), `FUN_00441fb0` (transition); reserved actors
  `DAT_004b9bc4[0xb9]` (185) and `[0xba]` (186).
- **Evidence:** the scene-manager is reserved actor id 0; its tick `FUN_0040e980` loads a
  pending scene (`this+0x4d`) by calling `LoadScene` and broadcasting leave/enter commands.
  **Navigation is a command to reserved actor 185 with opcode 31 (0x1f): `arg1` is the
  destination scene number** — Scene_001's trigger 663 is `(185, 31, 211)` (tutorial → scene
  211), Scene_061's trigger 660 is `(185, 31, 10)` (→ scene 10); 47 such commands across the
  corpus, `arg1` always a valid other scene. **Changing the camera view within a scene is a
  command to reserved actor 186 with opcode 16 (0x10): `arg1` is the view index** (Scene_001
  `(186, 16, 1)`) — this is the view-selection rule (resolves Q-0011: the shown
  background/camera is chosen by a 186/op16 command, not a fixed order). Other reserved
  managers: 8, 10, 12, 13 (state/sound/music; opcodes 50/54/70), 600, 750/751, 940/941, 901.
- **Method:** scan the trigger command lists for commands whose arg is a different scene
  number; confirm the target/opcode with the scene-manager tick and transition code.
- **Confidence:** strong (185/op31 = go-to-scene proven by arg = destination across 47 sites;
  186/op16 = view change by arg = view index). The exact per-manager opcode set is further work.

### E-0117 — Reserved manager actors are created at boot (navigation mgr 185 = type 0x12)
- **Binary/file:** `FUN_00436aa0` (boot init) and `FUN_00435a00`, which call the actor
  register `FUN_0040d270` with fixed ids; `DAT_004b9bc4` (actor table).
- **Evidence:** the game creates its reserved manager actors at boot by id (not from a `.abi`):
  `FUN_00436aa0` registers id `0xb9` (185) as **type 0x12** (`FUN_0040d270(factory, 0x12,
  0xb9, …)`), i.e. the navigation / scene manager that handles opcode 31 = go-to-scene
  (E-0116). The other reserved managers (id 0 the scene loader, 186 the view/camera manager,
  269 a state variable, 600/750/751/901/940/941 sound/music/state) are created the same way,
  by id, in the boot setup. Their per-class `DoCommand`s (reached via the global dispatcher,
  E-0110) implement go-to-scene, change-view, variable set/test, etc. Decoding these manager
  `DoCommand`s is what remains for the full event VM (the per-tick queue + conditions, E-0112)
  and the exact view→camera selection (Q-0008/Q-0011).
- **Method:** decompile `FUN_00436aa0`; the `FUN_0040d270(factory, type, id, …)` call.
- **Confidence:** proven for id 185 = type 0x12; the other reserved ids are created by the
  same mechanism (their exact types/classes are the next step).

### E-0200 — The command queue: conditions checked at push; `when` = a scene number, not a delay
- **Binary/file:** `FUN_00408760` (push with conditions), `FUN_00408a80` (push without),
  `FUN_0040f2c0` (run the immediate list), `FUN_0040efa0` (dispatcher), `FUN_00410bf0`
  (enter scene), `FUN_0040cb30` (LoadScene: `factory+0x130 = scene`), `FUN_00410c60`
  (returns `actor0+0x130`); `engines/grumpa/tools/events.py` over the 110 scene `.abi`.
- **Evidence:** a push first evaluates the command's condition list (`FUN_00408c30`); a false
  guard drops the command. A surviving command with `when == -1` or `when ==` the current
  scene number (`factory+0x130`, set by LoadScene) goes to an **immediate** vector
  (`DAT_004b9ba8`); any other `when` is linked into the **deferred** list `DAT_004b9b9c`.
  `FUN_0040f2c0` copies the immediate vector, empties it, then calls each target's `DoCommand`
  (`vtable[6]`, target `-1` = every actor id >= 1); commands pushed meanwhile wait for the
  next run. The dispatcher `FUN_0040efa0` runs only from `FUN_00410bf0` (entering a scene)
  and fires every deferred command whose `when` equals the scene just loaded. Corpus: of
  3,693 scene commands, 3,467 have `when = -1` and the other 226 name **another existing
  scene** (none their own scene, none a non-scene number). So `when` defers a command until
  the player enters that scene (Scene_061's gate trigger 661 queues work for scene 10, the
  scene its exit leads to, E-0116: its deferred targets 664, 665, 644 and 731 exist in
  Scene_010 and not in Scene_061; over the corpus 211 of the 223 deferred commands on scene
  actors name an actor of the `when` scene; of the other 12, six name id 600, the `.scn`
  scene actor).
  SUPERSEDES the "delay in ticks" reading of E-0112.
- **Method:** decompiled the push, run and dispatch functions; `events.py` statistics.
- **Confidence:** proven.

### E-0201 — Conditions: `(actor, slot, value, mode, link)` on the actor's state slots
- **Binary/file:** `FUN_00408c30` (evaluate a list), `FUN_00408f30/f60/f90/fc0` (tests),
  `FUN_00408350` (base actor ctor), `FUN_00408680`/`FUN_00408690` (`vtable[7]`/`[8]`).
- **Evidence:** every actor owns a vector of state slots (`+0x118`, begin `+0x11c`, stride
  0x118, value at `+0x104`); the base ctor creates one slot named "State" with value 0; the
  `.abi` header's EC vector serializes into the existing slots. `vtable[7]` returns slot 0,
  `vtable[8](v)` sets it. A condition EC is `(id, slot, value, mode, link)`: it reads
  `actor[id].slot[slot]` and tests mode 0 `==`, 1 `>`, 2 `<`, 3 `!=` against `value`.
  `link` chains them: consecutive conditions with `link = 0` are ANDed; `link = 1` closes a
  group, and a true group makes the whole list true (an OR of AND groups); an empty list is
  true; a missing actor leaves the running result unchanged. When the list comes out true
  and the last tested actor is an item (type 5, `+0x104 == 5`), actor 186's target is set to
  it (`FUN_0043cc70`, E-0206). Corpus: 528 guarded commands, 831 conditions, modes
  0/1/2/3 = 536/75/75/145, link 0/1 = 639/192; 728 test global actors (ids < 600), the 103
  on scene actors all test type-0x24 flags.
- **Method:** decompile; `events.py`.
- **Confidence:** proven.

### E-0202 — The main loop: 50 updates a second; scene entry and exit broadcasts
- **Binary/file:** `FUN_0040e980` (factory tick), `FUN_0040e8f0` (update), `FUN_00410bf0`,
  `FUN_0040cb30`, `FUN_00410390`/`FUN_0040fab0` (Save/LoadGameStatus), `FUN_0040ef40`,
  `FUN_00417000` (`DAT_004ba730`), `DAT_0049cb28` = 50, float 0.02 at `0x490350`.
- **Evidence:** the factory accumulates elapsed time and runs one update per 0.02 s (only one
  when more than 1 s behind), then draws. An update runs the immediate list
  (`FUN_0040f2c0`), then every actor's `vtable[4]` and then `vtable[5]`, ids 2 upwards.
  `DAT_004ba730 = 1000 / 50 = 20` ms is the step timers add. Changing scene
  (`factory+0x134` pending): broadcast opcode 25 (`arg1` = the old scene), run the immediate
  list, then LoadScene: write the old scene's actors (ids >= 600) to
  `Current/<n>_status.abi` (SaveGameStatus, Serialize mode 4), delete ids 600..979, load
  `Scene_<n>.scn` then `Scene_<n>.abi` (`factory+0x130 = n` between them), then
  `FUN_00410bf0`: read `Current/<n>_status.abi` back if it exists (LoadGameStatus, mode 4,
  so a revisited scene keeps its state), run the deferred commands for scene n, broadcast 23
  (`arg1 = n`) and run the immediate list, broadcast 86 and run it, push `(185, 33, 24)`
  (fade in).
- **Method:** decompile; disassembly of `0x410bf0` (the enter sequence).
- **Confidence:** proven.

### E-0203 — What each class keeps in a scene status (Serialize mode 4)
- **Binary/file:** the `case 4` arms of `FUN_0044ccb0` (0x0d), `FUN_00457ea0` (0x19),
  `FUN_0042e670` (0x21), `FUN_00428b10` (0x22), `FUN_00417180` (0x23), `FUN_00431810`
  (0x24), `FUN_00452100` (0x1a), `FUN_004492d0` (0x18).
- **Evidence:** every class writes `active` (`+0x10c`), `visible` (`+0x110`) and (bar 0x21)
  its state slots; then 0x0d its latch `+0x210`, playing `+0x1cc`, running `+0x1d0`,
  direction `+0x1ec`, frame `+0x1c4`, autoplay `+0x1d4`; 0x19 its latch `+0x184`; 0x21 its
  latch `+0x14c`; 0x22 its count `+0x12c`; 0x23 its elapsed `+0x128`; 0x24 nothing more
  (its latch is not kept); 0x1a its latch `+0x250` and animation fields; 0x18 `+0x1a0`,
  `+0x1b4`.
- **Method:** decompile.
- **Confidence:** proven.

### E-0204 — Logic classes: 0x21 script, 0x22 counter, 0x23 timer, 0x24 flag
- **Binary/file:** vtables found by their Serialize pointer (`0x4905bc` 0x21, `0x4904cc`
  0x22, `0x490418` 0x23, `0x490658` 0x24; CreateActor maps 0x25/0x26/0x27 to the same
  classes); DoCommand (`vtable[6]`) `FUN_0042eaf0`, `FUN_00428a30`, `FUN_00417e40`,
  `FUN_00431780`; updates `FUN_0042e650`, `FUN_00417140`; helpers `FUN_00429730/40/90`,
  `FUN_004297e0`, `FUN_00429800`, `FUN_00417f30/50/80/90`, `FUN_00432330/60`,
  `FUN_0042ebd0`; Serialize mode-1 field order `FUN_00428b10`, `FUN_00417180`,
  `FUN_00431810`, `FUN_0042e670`.
- **Evidence:** all four take 13 (latch: ignore everything else) and 52 (unlatch).
  **0x21 script** (`+0x128` guarded, conditions `+0x12c`, commands `+0x13c`): 0 runs its
  commands now; 23 (the scene-entry broadcast) marks it pending if its conditions hold (or
  it is unguarded) and its update runs the commands. **0x22 counter** (`+0x130` max,
  `+0x148` fire, commands `+0x134`; count `+0x12c`): 57 adds `arg1` (1 if `arg1 < 1`) while
  below max; reaching max sets state 1 and, with fire = 1, runs its commands; 58 clears
  state 1 and subtracts (floor 0); 59 sets max; 62 zeroes count and state. **0x23 timer**
  (`+0x12c` limit in ms, `+0x130`, `+0x134`, commands `+0x13c`; elapsed `+0x128`): its
  update adds 20 ms while `active`; past the limit it stops (elapsed 0, inactive) and runs
  its commands; 64 restarts with limit `arg1`; 65 sets the limit; 66 activates; 67 stops.
  **0x24 flag** (`+0x12c` fire, commands `+0x134`): 16 and 56 set state = `arg1`, then with
  state 1 and fire = 1 run its commands. "Run the commands" pushes each through the
  conditioned push (E-0200); the trigger and script versions skip a command that targets
  the actor itself with opcode 0.
- **Method:** decompile.
- **Confidence:** proven.

### E-0205 — `global.atx`: 80 global counters, timers and flags (ids 200..279)
- **Binary/file:** `games/grumpa/discs/cab/Actors/global.atx`; `events.py` (`parse_global`).
- **Evidence:** types 37 (20 counters, ids 200..219), 38 (20 timers, 220..239), 39 (40
  flags, 240..279) = classes 0x25/0x26/0x27 (E-0204). Text layout: `id, active, visible, n,
  n state values`, then 37: `max, fire`; 38: `limit, +0x130, +0x134`; 39: `fire`; then a
  command count and the commands as `when, target, opcode, arg1, arg2, n, n x (id, slot,
  value, mode, link)`. 80/80 blocks consume every token. Named examples: 269 "Snake Dead",
  246..249 the island flags, 222 "Dragon-Time" (120,000 ms), 220 "Syretimer" (4,000 ms).
  They are created at boot and never deleted (ids < 600), so scene conditions read them
  across scenes.
- **Method:** `events.py` over the file.
- **Confidence:** strong (layout from the corpus; consistent with the mode-1 field order of
  the three classes).

### E-0206 — Actor 185 is the fade/scene manager (30 view, 31 scene); 186 is a forwarding proxy
- **Binary/file:** CreateActor call sites `0x4377cd` (`FUN_0040d270(0x12, 0xb9)`),
  `0x4432a6` (`(0x28, 0xba)`), `0x4432cd` (`(0x29, 0xbb)`); 0x12 ctor `FUN_0042ef00`
  installs vtable `0x4905e0`: DoCommand `FUN_0042f210`, update `FUN_0042f540`; 0x28 ctor
  `FUN_0043cbb0` installs `0x490798`: DoCommand `FUN_0043cc20`; `FUN_0045ae00` (view switch
  on actor 602); `events.py`.
- **Evidence:** 185 (type 0x12): 30 fades out over 20 updates, then switches actor 602's
  view to `arg1` (`FUN_0045ae00`: `+0xdd0 = view`, loads that view's matrices, broadcasts 26
  with `arg1` = view) and fades in; 31 fades out (over 20 updates, or at once when
  `arg2 = -1`) and then asks the factory for scene `arg1`; 32 / 33 fade out / in over `arg1`
  updates. 186 (type 0x28): 63 sets its target id (`+0x128`) to `arg1`; every other opcode
  is forwarded to the target's DoCommand. A true condition list on an item points 186 at
  that item (E-0201), so `(186, 16, x)` acts on the item the guard just tested, not on the
  view. The 186 part of E-0116 ("186/op16 = change view") is superseded; the view command is
  `(185, 30, v)`. Corpus: 64 scenes use view indices (trigger gates, 185/30); in all of them
  the highest index + 1 <= the number of `<n>_<k>_IS.jpg` backgrounds.
- **Method:** disassembly of the CreateActor call sites, decompile; `events.py`.
- **Confidence:** proven for the opcodes; the index -> background name (`v` <-> `<n>_<v+1>`)
  is tentative (Q-0201).

### E-0207 — Triggers (0x19): click, walk-in and their gates
- **Binary/file:** `FUN_004594e0` (DoCommand), `FUN_00459640` (18), `FUN_00458f50`
  (update), `FUN_00459a60` (proximity gate), `FUN_00457b80` (ctor), `FUN_00457ea0`
  (Serialize), `FUN_0044c6e0`; `events.py`.
- **Evidence:** the 8 u32 after the header EC vector are `+0x170` edge, `+0x174` view
  (-1 any), `+0x178` click (1) or walk-in (0), `+0x17c` proximity-gated, `+0x180` has
  conditions (the second EC vector, `+0x190`), `+0x188` gate bits, `+0x14c`, `+0x150`
  required character id (-1 any). Ctor defaults: `+0x154 = 1`, `+0x174 = -1`,
  `+0x17c = 1`, `+0x188 = 1`, `+0x170 = 1`. DoCommand: latch `+0x184` (13 sets it and
  clears active/visible; 52 clears it); 0 activates and runs the commands; 1 deactivates;
  2/3 show/hide; 11 and 500 set active and visible; 12 and 501 clear both; 14/15 set/clear
  `+0x154`; 18 = a click at packed `(x, y)`; 22 = the mouse position; 86 reset. A click
  fires when the trigger is active, the mouse actor's state is not 7, its view gate matches
  actor 602's view, `+0x178 = 1`, the point is inside the polygon, the proximity gate passes
  when `+0x17c = 1`, and its conditions hold when `+0x180 = 1`. The update fires a walk-in
  trigger (`+0x178 = 0`) on each update the gate passes. The proximity gate needs
  `+0x154 = 1`; bit 1 of `+0x188`: the player character (actor 3's `+0x298`, of id `+0x150`
  when set) has a sphere overlapping the trigger's (`FUN_0044c6e0`); bits 2 and 4: the same
  for actor 4's character and for actors 91..94; with `+0x170 = 1` it passes once per
  entry. Corpus (397 triggers): `+0x178` 0/1 = 235/162, `+0x17c = 1` on 367, `+0x188`
  bit 1 on 373.
- **Method:** decompile; `events.py`.
- **Confidence:** proven (the gate logic); the sphere fields' layout is tentative (Q-0202).

### E-0208 — Sprite (0x0d) animation: modes, frame timing and end hooks
- **Binary/file:** `FUN_0044e2c0` (DoCommand), `FUN_0044ed10` (play), `FUN_0044ed80`
  (stop), `FUN_0044da50` (update), `FUN_0044dd80` (advance), `FUN_0044e9a0`/
  `FUN_0044e3e0`/`FUN_0044e6c0` (hooks), `FUN_0044ccb0` (Serialize); scene `.abi` statistics.
- **Evidence:** the header fields after the EC vector are `+0x114, +0x314, +0x1e0` fps,
  `+0x1e4` mode bits, `+0x1c8, +0x1f8, +0x208, [+0x48c]`, then `+0x1d4` autoplay,
  `+0x20c`; the three command vectors in file order are `+0x14c` (end), `+0x12c` (forward
  end), `+0x13c` (backward end). Mode bits: 1 loop, 2 ping-pong, 4 forward, 8 backward,
  0x10 forward-then-backward (corpus `+0x1e4`: 5 x129, 4 x100, 3 x66, 2 x7, 16 x5, 17 x3;
  fps 15/25/10/1/12/8/20/6 most common). E-0107 read `+0x1e0` as a frame count and
  `+0x1e4` as a rate: it is the other way round, and the frame count is that of the loaded
  frames. Play (0, 500; 23 when autoplay = 1): unless playing, rewind (frame 0 for bits
  2|4, last frame for 8), set playing and running. Stop (1, 501) clears playing only: a
  looping animation finishes its cycle. While active and running, the update advances one
  frame every `R / fps` updates (R from a device call, Q-0200). Forward/backward without
  loop: at the end stop (playing, running 0, frame held) and run the end commands; with
  loop: wrap while still playing, else hold. Ping-pong: forward, then back to 0; once
  through unless loop. 0x10: one play runs forward to the last frame, stops and runs the
  forward-end commands; the next play runs back to 0 and runs the backward-end commands (a
  door's open/close). Opcodes: 2/3, 11/12, 13 latch (`+0x210`; clears active, visible,
  playing), 52 unlatch, 86 reset (reload frames), 500 active + visible + play, 501 clear +
  stop.
- **Method:** decompile; field statistics over the corpus.
- **Confidence:** proven (logic); R tentative (Q-0200).

### E-0500 — `.scn` = three actor records (walk mesh 0x08, scene links 0x14, view list 0x09) read by `CreateFromABIFile`; 110/110 parse
- **Binary/file:** decrypted `Grumpa.exe`: `FUN_0040cb30` (LoadScene), `FUN_0040cef0`
  (CreateFromABIFile), Serialize `FUN_00432880` (type 8), `FUN_00447cd0` (type 0x14,
  "CFXToScene" in its error strings), `FUN_0045a750` (type 9), element serializers
  `FUN_0045a370`/`FUN_0044c750`, `FUN_0045a2a0`/`FUN_00401c00`, `FUN_00409000` (state
  slot); `games/grumpa/discs/cab/Scenes/*.scn`
- **Evidence:** LoadScene builds `%s\Scenes\Scene_%03d.scn` and passes it to the same
  `CreateFromABIFile` as the `.abi`, then loads `Scene_%03d.abi`. CreateFromABIFile reads
  `u32 type, u32 id`, then seeks back 4 bytes (`streambuf vtable[0x20](…, -4)`), so each
  Serialize re-reads the id as `+0x108`. Every `.scn` holds exactly three records:
  type 8 id 600 (`u16 nv, u16 nf, nv×32 B vertices, nf×3 u16 indices, nf×u16`; then
  `FUN_00432c60` builds per-face neighbours from shared edges), type 0x14 id 601 (`u32 np,
  np×u32` — the base class's "State" slot and the class's "Scene_ID" slot, 4 bytes each via
  `FUN_00409000` —, `u32 n, n×20 B` exits, `u32 m, m×28 B` entries), type 9 id 602
  (`u32 n, n×(pstr .jpg, pstr .fxi), n×64 B, n×64 B`). `parsers/scn.py` parses **110/110**,
  every byte consumed: 33,397 vertices, 51,383 faces, 214 exits, 268 entries, 166 views.
  Corpus statistics: vertex floats 3..5 are always (0, 1.0, 0); floats 6, 7 vary (0 in
  ~58 %, −1.7e38 in ~8 %); the per-face u16 takes 0 (70 %), 1, 13, 2, 3, 19, 12, 20; the two
  0x14 slots are 0 in all 110 files. An exit is `f32 x,y,z, f32 r, u32 scene` (e.g.
  Scene_003 → scenes 308, 303, 306, 307), an entry `f32 x,y,z, f32 rx,ry,rz, u32 scene`
  (Scene_001: (116.9, 60.8, 206.3), ry = −3.08, scene 211); each scene in an exit list has
  an entry in the other direction. Type 9 names the view backgrounds (`1_1_IS.jpg`,
  `1_1_IZ.fxi`) in view order; its first 64-byte matrix per view is a rotation +
  translation (Scene_001: orthonormal 3×3, last row (−35.8, 1.28, 471.7, 1)), the second has
  the shape of a Direct3D projection (1, 1.3333, Q = 1.0203, 1 at [2][3], −60.78 at [3][2]).
- **Method:** decompile of the functions above (PyGhidra headless on a copy of the
  project); `python engines/grumpa/tools/parsers/scn.py` (+ `--selftest`).
- **Confidence:** proven (layout, 100 % of the corpus); the meaning of the exit radius, the
  vertex floats 3..7, the per-face u16 and the two matrices is tentative (Q-0500, Q-0501).

### E-0501 — Status files are written with Serialize mode 5 (id first); global actors and the queue have their own files; new game empties `Current\`
- **Binary/file:** `FUN_00410390` (SaveGameStatus), `FUN_004100c0`/`FUN_0040fdb0`
  (Save/LoadGlobalGameStatus), `FUN_0040f4c0` (SaveSceneCommands), `FUN_0040c7d0`
  (factory ctor), `FUN_00441fb0` (new game), `FUN_00443220`; `Save/Current/*`
- **Evidence:** complements E-0202/E-0203. SaveGameStatus calls each scene actor's Serialize
  with mode 5, which writes `+0x108` (the id) and then the mode-4 fields, so a status file is
  `{u32 id, mode-4 body}*`, which LoadGameStatus reads back (id, then mode 4). The global
  actors (ids < 600) go to `Current\global.abi` the same way. The factory ctor names the
  queue file `remote.abi`; the shipped one is 4 zero bytes (count 0). The shipped
  `001/211/307/500_status.abi` start with id 600 (walk mesh: mode 4 reads `+0x10c`,
  `+0x110` and 0x71 bytes at `+0x3048`). Mode 4 of the two inventory classes: item (type 5)
  `+0x10c`, `+0x110`, its slots, `+0x288` scene, `+0x28c` position, `+0x298` rotation,
  `+0x4f0` latch; inventory (type 4) `+0x10c`, `+0x110`, `+0x140` (9 occupied flags),
  `+0x164` (9 item ids), `+0x218` (2 flags) and `+0x220` (2 ids: the equipment slots).
  New game (`FUN_00441fb0`): broadcast ops 25 and 36, run the immediate list, empty
  `Current\` (`FUN_00441950`), reload the global actors (`FUN_00443220`: Characters.abi,
  Items.abi, global/global2.atx, the score and inventory `.atx`), then LoadScene(start
  scene, 0) — so the shipped `Current\` files never reach a new game (resolves Q-0203).
- **Method:** decompile.
- **Confidence:** proven

### E-0502 — A saved game is a copy of `Current\` in `Save\Player<n>\` plus `Player.sts` and `Player.tga`
- **Binary/file:** `FUN_004420d0` (save into a slot), `FUN_00442d40` (load a slot),
  `FUN_00441950` (empty `Current\`), `FUN_00441c20` (empty `Player<n>\`), `FUN_00441240`
  (LoadPlayerInfo); `games/grumpa/discs/cab/Save/Player*/`, `Local_Swedish/Help.txt`
- **Evidence:** saving: empty `%s\Player%d`, SaveGlobalGameStatus, SaveGameStatus(current
  scene `FUN_00410c60`), SaveSceneCommands, then FindFirstFile/copy every file of
  `\Current\` into `\Player%d\`, then write `Player.sts` (the player's name, newline, the
  current scene number from `FUN_00410c60`) and `Player.tga` (a screenshot via
  `CFXSurface::SaveToFile`; the shipped templates are 38,444 B). Loading: broadcast ops 25
  and 36, run the immediate list, empty `Current\`, copy `\Player%d\*` into `\Current\`.
  Six slots `Player1..6` ship with `Player.sts` = `Player 1\r\n0`; `Save/Player/` is the
  template. Help.txt: saving and loading go through two icons on the inventory panel (a
  diskette: the saved games, click a box to save there; a door with an arrow: the main
  menu, whose Load entry lists them).
- **Method:** decompile; reading the corpus.
- **Confidence:** proven (file flow); the panel icons' code path is Q-0502.

### E-0503 — Items: global type-5 actors 100..179; State 1 gone, 3 carried, 4 in a scene, 6 on the cursor
- **Binary/file:** `FUN_00443220`, CFXItem vtable `0x49076c`: Serialize `FUN_0043c4f0`,
  DoCommand `FUN_0043bd30`, draw `FUN_0043baf0`, drop `FUN_0043c340`; cursor
  `FUN_00446150`/`FUN_00446640`; `Actors/Items.abi`
- **Evidence:** Items.abi = 66 type-5 records, ids 100..179. Mode 1 reads `+0x108` id,
  `+0x10c` active, `+0x110` visible, `+0x4d8`, the "State" slot, four strings (`IO_*.ANB`
  world mesh, `IT_*.tga` its texture, `IC_*.tga` the 32×32 inventory icon, `IS_*.wav` the
  spoken name), `+0x288` scene (−1 none), `+0x28c` position, `+0x298` rotation, `+0x7d8`,
  `+0x7ec`, `+0x7f0`, a pair list. DoCommand: 52 clears the latch `+0x4f0` (everything else
  is ignored while latched); 0/1 play/stop the spoken name; 2 show; 3/11/12 visible/active;
  13 disable (drops it from the cursor, State 1, latch, scene −1); 16 `SetState(arg)` (and
  drops it from the cursor unless arg is 6); 23 arg = current scene; 42 add to the
  inventory (actor 90, State 3), or — inventory full — drop it beside Grumpa (State 4 at
  actor 3's position, checked against the walk mesh actor 600); 43 reload; 54 arg: put in
  scene arg (State 4); 71 arg: place at actor arg's position (State 4); 86 load if it lies
  in the current scene, else unload. Op 18 (a click, `arg1 = x | y<<16`): if State 4, in
  the current scene and shown, the click is in its screen rectangle `+0x4dc` (widened to
  60 px when narrower than 40) and the cursor (actor 2) holds nothing, add it to the
  inventory (State 3) and play the pick-up sound. Holding an item (`FUN_00446150(cursor,
  id)`) stores the id at cursor `+0x140` and sets the item's State to 6; −1 clears it.
  Special adds (`FUN_004387d0`): 174 (Water Drop) sends (8, 50, 100), 177..179 (coins) send
  (8, 9, 1), and set State 1 — counted by actor 8, not carried.
  Corpus (scene command lists, `abi.py` grammar): 53 commands send 42 to an item, 45 send
  43, 37 send 16; conditions on items are `(item, 0, 6, 0, 0|1)` 209 times and
  `(item, 0, 3|1, 0, …)` 7 times — slot 0 (State) == 6, "this item is on the cursor", is how
  using an item on a hotspot is written (e.g. Scene_007 trigger 660: 133 Wood Splinter On
  Fire held → the burning roots; Scene_001 trigger 663: 100 and 134 carried → scene 211).
- **Method:** decompile; corpus scan.
- **Confidence:** proven

### E-0504 — The inventory panel (actor 90, type 4): 9 slots and two equipment slots, toggled by op 19 (right click)
- **Binary/file:** type 4 vtable `0x49071c`: Serialize `FUN_004388e0`, DoCommand
  `FUN_00437d00`, draw `FUN_00438500`, layout `FUN_00438660`, add `FUN_004387d0`;
  `FUN_004106c0` (CreateFromATXFile); `UI/090_Inventory/090_Inventory.atx`,
  `Local_Swedish/Help.txt`
- **Evidence:** CreateFromATXFile skips lines until one holds `<`, then reads the type and
  expects `{`, so a block without a `<type><name>` header is skipped: the second block of
  `090_Inventory.atx` is never read (the "overrides" reading in `docs/formats/README.md`
  does not hold). Mode 6 reads id 90, two zeros (`+0x10c`, `+0x110`: hidden), x 480,
  y 170, the panel image `Inventory.jpg` (307×139), the slot image
  `InventorySlot_####.jpg` (96×96, frames 0..2) and the "inventory is full" voice. Layout
  (`FUN_00438660`): equipment slots (x, y, 96×96) and (x+210, y, 96×96); nine 86×86 slot
  rectangles in a 3×3 grid, left edge x + (panelW − 258)/2, top y + panelH; two buttons
  (x+70..x+100, y+96..y+132) and (x+200..x+232, y+96..y+132). Draw (when visible): the
  panel at (x, y), then per slot the slot image at frame = the slot's occupied flag and
  the item's icon at slot + (32, 32), then the icons of the two equipment slots at
  slot + (32, 32). DoCommand: 19 toggles (show + activate; or hide + deactivate), ignored
  while Ctrl is down (`GetKeyState(0x11)`) or while locked; 11 unlock, 12 lock (and
  hide); 0/1 deactivate; 2/3 visible. Op 18 (click), per slot: empty cursor and an item in
  the slot → the item goes on the cursor (State 6) and its name is spoken, the slot
  empties; an item on the cursor and the slot empty → it goes into that slot (State 3);
  both → the held item is added to the first free slot. The right equipment slot takes only
  134 (Shield) or 138 (Shield of Protection) and tells actor 10 to wear it
  (`FUN_00421780(…, 0|5, 1)`), taking it back out sends `(…, 0|5, 0)`. Add: an item already
  in a slot is not added twice; the first slot with flag 0 takes it; with none free, the
  "inventory full" voice plays and the item drops beside Grumpa. Help.txt: right click
  shows the inventory; nine items; a weapon goes in the box left of Grumpa, a shield right;
  left click an item to make it the cursor, then click a glittering object to use it;
  clicking where nothing glitters drops it on the ground beside Grumpa.
- **Method:** decompile; reading the corpus.
- **Confidence:** proven for slots, add and toggle; the left equipment slot and the two
  buttons are Q-0502.

### E-0400 — Every `.abi` Serialize reads the id again; the actor header is `id, active, visible, n × u32`
- **Binary/file:** `CFXActorFactory::CreateFromABIFile` `FUN_0040cef0`; Serialize arms of type
  0x0d (`0x44ceb8`), 0x11 (`FUN_0043d200`), 0x18 (`FUN_004492d0`), 0x03 (`0x4231f0`).
- **Evidence:** after reading `u32 type` and `u32 id` the loader seeks back 4 bytes
  (`0x40d073..0x40d087`: `push 1; push 1; push -4; call streambuf->vtable[0x20]` = seekoff(-4,
  cur, in), skipped only on a failed stream), so each Serialize starts at the id and reads it
  again into `+0x108`. Every Serialize (mode 1) then reads `+0x10c` (**active**, the flag
  `Update` tests), `+0x110` (**visible**, the flag `Draw` tests; E-0403), then `u32 n` and `n`
  elements of the class at vtable `0x4902dc`, whose Serialize (`0x409107`) reads one u32 into the
  element's `+0x104`. Over the non-character records of the 111 scene files and Items.abi, `n`
  is always 1 and the element 0, except one 0x22 record (element 1); characters have n = 6
  (E-0402). `abi.py`'s older per-type grammars read the same byte counts with other boundaries
  (`raw(12)` = active, visible, n; then the element counted as an "EC vector" count), so the byte
  totals hold but the field meanings in those grammars and in `scene.cpp`'s 0x0d/0x1a readers
  are shifted by one u32 (their "visible" is `n`). Run under Unicorn (`tools/abiemu.py`), the
  original's 0x11 Serialize on `Scene_001.abi` reads `+0x108 = 0x276` (the id), `+0x10c = 1`,
  `+0x110 = 0`, `n = 1`, element 0, then `+0x1c8`, `+0x1b8`, ...
- **Method:** disassembly of the loader; emulation of the original Serialize; corpus count.
- **Confidence:** proven.

### E-0401 — `CFXCharacter` (type 0x03) layout, from the original's own Serialize run on the corpus
- **Binary/file:** constructor `0x41c9b0` (object 0x698 B, `CreateActor` case 3 at `0x40d5ab`),
  vtable `0x49046c`: [1] Serialize `FUN_00422f80` (modes 1, 2 and 8 share the arm `0x4231f0`),
  [2] SetDevice `FUN_0041daf0`, [3] Draw `FUN_004226a0`, [5] Update `FUN_00421a60`,
  [6] DoCommand `FUN_0041e0d0`. `Actors/Characters.abi` (44 records, 51,645 B) and
  `Scenes/Characters.abi` (44 records, 46,648 B).
- **Evidence:** `tools/abiemu.py` maps the decrypted dump, builds each record's object with its
  constructor, runs SetDevice up to `0x41df6e` (it sizes the attachment arrays `+0x368..+0x38c`
  first; past that point it only creates DirectDraw surfaces) and runs Serialize(mode 1) with the
  archive read `FUN_004026c0`, `operator new` and `delete` replaced. The original code consumes
  **both files completely: 44 + 44 records, every byte**, and logs each read with its caller. The
  record grammar from that trace and the read sites (after the type; `[x]` = object offset):

      u32 id [0x108], active [0x10c], visible [0x110]; u32 n; n × u32     (E-0400; n = 6)
      u32 [0x444] home scene; f32×3 [0x16c] position; f32×3 [0x160] orientation (y = yaw, rad)
      f32 [0x28c], f32 [0x5fc], f32 [0x290]; u32 [0x48c]; u32 [0x490]
      u32 n; n × ClassD (EC-vec + CC-vec)                        0x423321 -> [0x660] rules
      CC-vec                                                     0x4234fa -> [0x640]
      CC-vec                                                     0x4236c9 -> [0x650]
      u32 n; n × {pstr text; CC-vec}                             0x423898 -> [0x674]/[0x684]
      CC-vec                                                     0x423ac0 -> [0x630]
      u32 n; n × {u32 character id; CC-vec}                      0x423c8f -> FUN_004254c0
      u32 [0x434]; u32 n [0x2e8]; n × pstr  .anb animations
      u32 n [0x330]; n × pstr .wav sounds; u32 [0x440] texture index
      u32 n [0x30c]; n × pstr .tga textures
      u32 n [0x344]; n × {pstr .ANB; pstr .tga; u32 [0x36c+4i]; u32 [0x37c+4i]; u32 [0x38c+4i]}
      u32 [0x128]; u32 [0x13c]; u32 [0x140]; u32 n; n × (u32, u32) [0x12c]

  (CC = 5 u32 + `u32 m` + m × EC, EC = 5 u32; E-0101.) The message block's loop body
  (`0x4238a8..0x423aaa`) reads a pascal string into a heap copy pushed on `+0x674`, then a CC
  vector pushed on `+0x684`; its count is 0 in all 88 records, so that body is known from the
  code only. `FUN_004254c0` is `CFXCharacter::AddReactCharacter` (error string at `0x42552b`).
  `tools/parsers/abi.py` `t_03` implements the grammar; its record boundaries equal the
  emulator's for all 88 records; `abi.py` now parses **113/113 `.abi` files (2,092 records,
  15 types)** consuming every byte.
- **Method:** emulation of the original Serialize (Unicorn) with a logged read primitive;
  disassembly of the loops whose counts are 0 in the corpus.
- **Confidence:** proven (the original code parses the files); field meanings in E-0402.

### E-0402 — `CFXCharacter` field meanings and the database load
- **Binary/file:** `FUN_00443220` (boot), `CFXCharacter::DoCommand` `FUN_0041e0d0`,
  `Actors/Characters.abi`.
- **Evidence:** `FUN_00443220` loads `"%s\Actors\Characters.abi"` then `"%s\Actors\Items.abi"`
  through `CreateFromABIFile(path, 8)` (`push 8` at `0x44324b`, `0x44327a`); mode 8 takes the same
  Serialize arm as mode 1 for type 3. No string names `Scenes\Characters.abi`; the copy in
  `Scenes/` is not loaded (it differs: an older build of the same 44 ids). One record per
  character *form*; the database (by id): 10 Grumpa (`000_N2N_Grumpa.anb`, 26 animations,
  5 textures, 6 carried objects), 11 Grumpa in the boat, 12 on the dragonfly, 13 on the bear,
  88 on the seahorse; 16 the Scharlakanskraken companion; 19/42 Monkey Champion; 20/22/25 Golem;
  17 Hulk; 23 Parrot; 26 Foxy Lady; mounts 21 Dragonfly, 27 Boat, 28 Bear, 87 Seahorse; the
  rest enemies (pirate rats 30..32/34/35, snake 33, turtle boss 36, rat leaders 37/38,
  crocodiles 39..41, sharks 43/44/85, crocodile boss 47, hyena boss 55, scorpion 56, spider 64,
  captain Ratbeard 69, skeleton captain 78, diver 79, octopus 80, piranhas 81..83). Fields:
  `[0x444]` the scene the character is in (−1: none, placed by a spawner, E-0404); `[0x16c]`
  world position and `[0x160]` orientation (only `y` is non-zero bar one record: the yaw);
  `[0x128]` 0 = a creature, 1 = a mount, 2 = a rider form whose parts are `[0x13c]` and
  `[0x140]` (11 = 10 + 27, 12 = 10 + 21, 13 = 10 + 28, 88 = 10 + 87); a mount's pair list
  `(10, form)` names the rider form it makes with Grumpa (Boat `(10, 11)`, Dragonfly `(10, 12)`,
  Bear `(10, 13)`, Seahorse `(10, 88)`); Grumpa's pairs (87→88, 27→11, 21→12, 28→13) the
  reverse. The animation names follow `<nnn>_<from>2<to>_<name>.anb` (N normal, W walk, R run,
  D down, J jump, A1..A3 attacks, ...): entry 0 is the idle `N2N`. `[0x440]` selects the
  texture (DoCommand 0x35 sets it, clamped to the `[0x30c]` count). The `n × u32` header vector
  (E-0400) holds 6 values per character (Q-0402).
- **Method:** disassembly; the decoded database (E-0401).
- **Confidence:** proven for the load, home scene, position, mount links and lists; the stat
  vector's meaning is open (Q-0402).

### E-0403 — When a character is in the scene; its `DoCommand` opcodes
- **Binary/file:** `FUN_004226a0` (Draw), `FUN_00421a60` (Update), `FUN_0041e0d0` (DoCommand),
  `FUN_00410bf0` (scene entry).
- **Evidence:** Draw runs only if `visible [0x110]` and `[0x444] == [0x448]`
  (`0x4226c2..0x4226dc`); Update only if `active [0x10c]` and `[0x444] == [0x448]`
  (`0x421a6b..0x421a85`). `[0x448]` is the current scene: scene entry (`FUN_00410bf0`, after
  `LoadScene`) queues the broadcast `(when −1, target −1, opcode 0x17, arg1 = scene number)`
  (`0x410c0d..0x410c1e`) and DoCommand 0x17 stores `arg1` in `[0x448]`. Opcodes: 2 show
  (`visible = 1`, `[0x444] = [0x448]`: the character joins the current scene), 3 hide, 0xb/0xc
  active on/off, 0xd disable (state 2, active = visible = 0, `[0x444] = −1`, latch `[0x46c]`
  that only 0x34 clears), 0x29 place at another actor's position/orientation and show, 0x47
  place at actor `arg1`'s position, 0x35 texture index, 0x36 move to scene `arg1`
  (`[0x444] = arg1`), 0x2c/0x2d/0x2e/0x2f/0x30/0x54 take a role (control, follow, mount: they
  set `[0x444] = [0x448]`, active, visible and a role in the mesh object's `+0x564`), 0x44 show
  message `arg1` (E-0405).
- **Method:** disassembly and decompilation.
- **Confidence:** proven for the presence rule and the listed opcodes; the role opcodes'
  behaviour (combat, following, riding) is not specced (Q-0403).

### E-0404 — Spawners (type 0x1d) place characters whose home scene is −1
- **Binary/file:** type 0x1d Serialize `FUN_0044a250`, spawn `FUN_0044b120`, strings
  `"Spawn C_ID: %d S_ID: %d"` (`0x49e9f4`, `0x49e9b8`).
- **Evidence:** a 0x1d actor holds spawn points (stride 300 = `0x12c`): a position (`+0x104`
  vec3), an orientation (`+0x110` vec3) and a list of character ids (`+0x120`). Spawning point
  `i` picks a random id from its list (re-drawn if that character is already spawned, list at
  `+0x148`, at most 60 tries), moves the character there (`FUN_004250a0`), sets its orientation,
  `active = visible = 1`, DoCommand(2) (so `[0x444]` becomes the current scene), state 5, and
  records the id.
- **Method:** decompilation.
- **Confidence:** proven.

### E-0405 — Voice lines: `CFXSound` (0x18/0x2a), its speaker and its on-end commands; no subtitles
- **Binary/file:** CFXSound vtable `0x49089c` ([1] Serialize `FUN_004492d0`, [2] Init
  `FUN_00448840`, [4] Update `FUN_00448db0`, [6] DoCommand `FUN_00448a40`); load `FUN_00448970`,
  play `FUN_00449200`/`FUN_00448f70`, stop `FUN_00449280`/`FUN_00449040`, on-end
  `FUN_00448bb0`; manager 185 `FUN_0042f4e0`; `Local_*`, `Sounds_*`.
- **Evidence:** after the header (E-0400) the sound reads ten u32 — `[0x184]` volume flag,
  `[0x188]` volume (DirectSound hundredths of a dB, e.g. −690), `[0x190]` pan flag, `[0x194]`
  pan, `[0x198]` frequency flag, `[0x19c]` frequency (11025/22050/44100), `[0x1a4]` loop,
  `[0x1a0]` playing, `[0x1b0]` play on scene entry, `[0x3ac]` **speaker** (a character id, 0 =
  none) — then a timer sub-object (56 B), the file name (pascal string, `[0x208]`) and a CC vector
  of commands. The file opened is `sprintf("%s%s", soundDir, name)` (`0x448983..0x448999`), where
  `soundDir` (`0x4ba1e8`) is `"%s\Sounds"` of the data path (`0x43723e..0x437262`); the flags
  apply volume (`IDirectSoundBuffer::SetVolume`, vtable `0x3c`, `FUN_00449180`), pan (`0x40`),
  frequency (`0x44`). DoCommand: 0 and 500 play (deferred to the next Update while `[0x1bc]` is
  set), 1 and 501 stop, 0xb/0xc active, 0xd stop and latch, 0x17 (scene entry) plays if
  `[0x1b0] == 1`, 0x56 load. Play (`FUN_00448f70`) marks the speaker talking (its mesh object's
  `+0x67c = 1`, after `FUN_00425980` on it) and starts the buffer, looping iff `[0x1a4] == 1`;
  stop clears the talking flag. A non-looping sound stops itself when its timer runs out, and
  stopping (`FUN_00449280`) queues every command of its CC vector (`FUN_00448bb0`): the
  sound's own list runs "on end". So a dialogue is a chain of voice lines, each a CFXSound whose
  speaker talks while it plays and whose end commands start the next line. In the scenes the
  speaker is 0 (323 sounds), 16 (39: the Scharlakanskraken companion, the `*_sch_*` / `Sch_*` files), 26 (2, Foxy Lady) or 69 (1, Ratbeard). There is
  no text: `Local_<lang>` holds only `Text.txt` (14 menu strings), `Help.txt`, `Credits.txt`,
  `license.txt`, and the characters' message lists (E-0401) are empty; a message would be
  shown by character opcode 0x44 through manager 185 opcode 16 (`FUN_0042f4e0`: copy the string
  to `+0xbd4`, alpha 255 fading by 255/arg per step). Files: `Sounds_` holds 550
  language-independent sounds, `Sounds_<lang>` 241..280 voices; 182..203 names exist in both,
  never with the same bytes.
- **Method:** decompilation; corpus listing of the 0x18 fields (`abi.py` grammar); `cmp`.
- **Confidence:** proven for the fields, playback, speaker and on-end commands; how the
  installer merges `Sounds_` and `Sounds_<lang>` into one `Sounds` folder is Q-0400.

### E-0406 — A sound starts on scene entry if it was saved playing or is marked "on entry" (completes E-0405)
- **Binary/file:** `CFXSound::DoCommand` `FUN_00448a40`, opcode 0x17 arm (`0x448b0a..0x448b4f`).
- **Evidence:** on the scene-entry broadcast 0x17 the sound sets its deferred-play flag
  `[0x1b8]` if `[0x1a0] == 1` (the "playing" field read from the file) while it has no
  DirectSound buffer yet (`[0x13c] == 0`, true right after loading), and also if
  `[0x1b0] == 1`; its next Update then plays it. E-0405 named only `[0x1b0]`. In the scenes
  `(playing, on entry)` is (0, 0) for 274 sounds, (1, 1) for 76, (0, 1) for 11, (1, 0) for 4.
- **Method:** decompilation; corpus count (`abi.py` grammar).
- **Confidence:** proven.
