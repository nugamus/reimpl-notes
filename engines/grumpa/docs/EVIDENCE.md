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

### E-0107 — Type 0x0d sprite position, animation params and colour key
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
