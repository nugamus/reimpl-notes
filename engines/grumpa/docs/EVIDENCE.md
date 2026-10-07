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

### E-0016 — The 3D device: a software rasteriser on an 800×600×16 DirectDraw surface — SUPERSEDED by E-0303 (it is Direct3D 7)
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

### E-0103 — The per-view camera block (Q-0008) — SUPERSEDED by E-0300 (a light, not a camera)
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

### E-0105 — Per-view camera block field values across the corpus — SUPERSEDED by E-0300
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

### E-0115 — The per-view camera is a look-at camera (eye -> scene target ~origin) — SUPERSEDED by E-0301
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

### E-0407 — A character's six header values are its state slots
- **Binary/file:** `CFXCharacter` ctor `0x41c9b0` (six inserts into `+0x118`), Serialize
  `0x423235..0x423277`; E-0201 (the state-slot vector).
- **Evidence:** the `n × u32` vector after `visible` (E-0400) is the actor's state-slot vector
  of E-0201 (`+0x118`, stride 0x118, value at `+0x104`): the constructor builds six slots, and
  Serialize loops over the existing slots, reading one u32 into each. Conditions read them as
  `(character id, slot, value, mode)` — e.g. `(13, 4, 1, !=)` on the bear rider (grumpa-events,
  E-0201). Slot 0 is the base class's "State"; the per-slot meaning of 1..5 is not read
  (Q-0402 narrowed).
- **Method:** disassembly (E-0401 trace: caller `0x409119` per slot).
- **Confidence:** proven for the mechanism.

### E-0300 — Type 0x11 is `CFXLight`: its 0x68-byte block is a `D3DLIGHT7` (a point light)
- **Binary/file:** decrypted `Grumpa.exe`: device ctor `0x42c4f0` (vtable `0x490548`),
  `FUN_0042de80` (device creation), `FUN_0043d200` (0x11 Serialize), `FUN_0043d080` (0x11
  update), `FUN_0043ce90`; scene `.abi`.
- **Evidence:** the render device's `vtable[0x38]` (`0x42d8d0`) returns `this+0x18`, which
  `FUN_0042de80` fills with `IDirect3D7::CreateDevice` (IID_IDirect3DHALDevice or
  IID_IDirect3DRGBDevice, strings `0x49d774`/`0x49d748`) on the `IDirect3D7` it queried from
  DirectDraw 7 (`0x49d810`); `vtable[0x34]` of that object is "SetViewport" in the error at
  `0x49d734`, as in `IDirect3DDevice7` (index 13). So the 0x11 call
  `dev->vtable[0x38]()->vtable[0x48](id-0x276, block)` (E-0103) is `IDirect3DDevice7::SetLight`
  (index 18), followed by `vtable[0xb0]` = `LightEnable(index, TRUE)`; the u32 read before
  the block is overwritten by it. The 0x68 bytes are a `D3DLIGHT7`: `[0]` type = 1
  (D3DLIGHT_POINT) in all 180 lights of the corpus, `[1..4]` diffuse rgba (1.0, 0.75–1,
  0.70–1, 0), `[5..12]` specular/ambient 0, `[13..15]` **position**, `[16..18]` direction 0,
  `[19]` range, `[21]` attenuation0 = 1.0, the rest 0. The string `CFXLight::Initialize` is
  used at `0x43ce98`, inside the 0x11 class. Update `FUN_0043d080`: mode `+0x1b8` = 1 flickers
  the light on/off at random, mode 2 sets diffuse = (1, 0.70 + r·0.01, 0.65 + r·0.01),
  r ∈ [0,30), and calls SetLight again (fire). Opcodes 2/3 of its DoCommand switch it on/off
  (`LightEnable`). So the "camera" of E-0103/E-0105/E-0115 is a light; the camera is E-0301.
- **Method:** decompile of the functions above; corpus count with `abi.py` (180 records).
- **Confidence:** proven

### E-0301 — The views and their cameras are the `CFXView` record (type 9, id 602) of `Scene_<NNN>.scn`
- **Binary/file:** `FUN_0045a750` (type 9 Serialize, vtable `0x490ae0`), `FUN_0045ae00`
  (SetView), `FUN_0040cef0`, `FUN_0040cb30`; `Scenes/*.scn`.
- **Evidence:** `LoadScene` reads `Scene_<N>.scn` with the same `CreateFromABIFile` as the
  `.abi` (which seeks back over the id, so Serialize reads it again as `+0x108`). Type 9's
  ctor `FUN_0045a410` sets class 9; its Serialize reads the id, `u32 n` (`+0xdd8`), n × (pstr
  `<v>_IS.jpg`, pstr `<v>_IZ.fxi`) into the background and z-buffer surfaces, then n×64 bytes
  to `+0x13c` and n×64 bytes to `+0x27c`. `FUN_0045ae00(v)` (v ≤ n and not the current one)
  stores `+0xdd0 = v` and calls `IDirect3DDevice7::SetTransform(2 = VIEW, this+0x13c+v*0x40)`
  and `SetTransform(3 = PROJECTION, this+0x27c+v*0x40)`, then broadcasts opcode 26 with v.
  So the first matrices are the Direct3D **view** matrices and the second the **projection**
  matrices (row vectors, left-handed; e.g. Scene_007: x scale 2.4142 = cot 22.5°, y 3.2189 =
  ×4/3, Q = 1.0802, −Q·zn = −387.6, so near 358.9 and far ≈ 4833). The record ends the file
  in 110/110 `.scn` (n = 1: 78, 2: 14, 3: 13, 4: 4, 5: 1). Projecting the 0x1a meshes through
  view 0 lands them on their features: `boulder B_at ground` in Scene_061 view 0 covers
  x 270..317, y 462..512, and its z/w·65535 is a median 598 below the `_IZ.fxi` under it,
  so it rests on the floor. Format side: `parsers/scn.py` (E-0500).
- **Method:** decompile; `python engines/grumpa/tools/viewcheck.py --selftest` (110/110,
  the boulder); engine dev `grumpa_actors=61` (meshes on the platform, behind the floor
  edges), `grumpa_actors=1` (the dead father under the table, hidden by its legs).
- **Confidence:** proven

### E-0302 — CFXSprite (0x0d) drawing: layer, view, colour key, depth frames, frame timing
- **Binary/file:** `FUN_0044ccb0` (Serialize), `FUN_0044db20` (render, vtable[3]),
  `FUN_0044da50`/`FUN_0044dd80` (update), `FUN_0044ed90` (frame files), `FUN_0044e100`/
  `FUN_0044e1b0` (colour key), `FUN_00436aa0`; `Scenes/*.abi`, `Bitmaps/`.
- **Evidence:** the fields in Serialize order after the EC vector are: `+0x114` layer,
  `+0x314`, `+0x1e0` fps, `+0x1e4` animation flags, `+0x1c8` view, `+0x1f8` key on, `+0x208`
  key colour. Render draws nothing unless the sprite is visible (`+0x110`) and has frames,
  and `+0x1c8` is −1 or the CFXView's current view (`DAT_004b9bc4[602]+0xdd0`). The rectangle
  is the position `+0x190` plus the frame size, clipped to 800×600. If depth frames exist,
  it first `BltFast`s the frame's depth surface into the z-buffer without a key (device
  `vtable[0x40]` = `this+0x10`, the Z_Buffer surface). Then it `BltFast`s the colour frame
  to the back buffer (`vtable[0x48]` = `this+0xc`), with `DDBLTFAST_SRCCOLORKEY` when
  `+0x1f8` = 1, else `NOCOLORKEY`. The key is set with `SetColorKey(DDCKEY_SRCBLT)` on every
  frame. It is the COLORREF `+0x208`, converted through a GetDC/SetPixel/Lock round trip, or
  frame 0's pixel (0,0) when `+0x208` = −1. Frame files: a name `<stem>0000<ext>` animates,
  and frame i is `<stem>%04d<ext>` as long as the file exists. Depth frames are
  `<stem>_Z%04d.fxi`, or `<name>_Z.fxi` for a still (format strings `0x49ed08`, `0x49ecf0`,
  `0x49ece4`, ...). The update steps one frame every `50/fps` game ticks: `FUN_00436aa0`
  sets the device frame rate to 50 with `vtable[0x24](0x32)`. The flags are as in E-0208.
  Corpus: layers 1 (223) and 4 (87); view −1 or 0..4. The key is on in 202 of 310 sprites,
  with key colour 0xFF0000 (blue) in 14 of them and −1 in the rest. All 44 opaque view-bound
  sprites in multi-view scenes match their own view's background best (mean difference
  ≈ 1–8, against 20–70 on the other views).
- **Method:** decompile; `viewcheck.py sprites <scene>` over all scenes.
- **Confidence:** proven

### E-0303 — The 3D device is Direct3D 7; how a 0x1a mesh actor is drawn and lit
- **Binary/file:** `FUN_0042de80`, `FUN_00436aa0`, `FUN_00450da0` (0x1a render),
  `FUN_004166e0` (mesh draw), `FUN_00456920`/`FUN_004569f0`, `0x455e30` (CFXTexture ctor),
  `FUN_00455ff0`, `FUN_00456400`; `Bitmaps/*.tma`.
- **Evidence:** the device is an `IDirect3DDevice7` (HAL, or the RGB software device) on a
  DirectDraw 7 surface with an attached 16-bit Z_Buffer (`FUN_0042de80`). There is no
  `d3d*.dll` import because IDirect3D7 comes from DirectDraw (this corrects E-0016). Boot
  sets `D3DRENDERSTATE_AMBIENT = 0x1e1e1e` and, on texture stage 0, MAG/MINFILTER = LINEAR,
  COLORARG1 = TEXTURE and COLORARG2 = DIFFUSE (modulate). The 0x1a render (vtable[3]) runs
  only when visible (`+0x110`): BeginScene, `SetMaterial` and `SetTexture` from its
  CFXTexture, the mesh's `DrawIndexedPrimitive(TRIANGLELIST, FVF 0x112 = XYZ|NORMAL|TEX1)`,
  EndScene. It sets no world transform (the meshes are in world space) and no cull mode
  (default D3DCULL_CCW). Lighting is on by default, so the scene's lights (E-0300) light the
  vertices. CFXTexture's material defaults to diffuse and ambient (1,1,1,1), specular and
  emissive 0, power 0, unless `<texture>.tma` exists (17 floats in that order; two such files
  in the corpus). A 32-bit .tga becomes an ARGB8888 texture with alpha blending (`+0x154`:
  SRCBLEND SRCALPHA, DESTBLEND INVSRCALPHA, alpha from the texture); any other .tga becomes
  RGB555. The class's layer `+0x114` is 3 (ctor, `0x4500de`).
- **Method:** decompile.
- **Confidence:** proven

### E-0304 — The shown view: view 0 on scene entry, 185 op 30, and the player's floor cell
- **Binary/file:** `FUN_00447270` and `0x446f70` (CFXPlayer, type 0x16); `FUN_0042f210`,
  `FUN_0042f410` and `FUN_0042f540` (type 0x12, id 185); `FUN_00433010` (CFXFloor); corpus.
- **Evidence:** placing the player at a scene entry calls `SetView(0)` (or, the first time
  after a load, the saved view). The player's tick switches to the view number its character
  stands on when that number is 0..4. The number is `+0x450`, set from the floor cell's u16
  table `+0x134` by `FUN_00433010`. 185's opcode 30 fades out (20 steps), calls
  `SetView(arg1)` and fades in. In the corpus its arg is always below the scene's view count
  (5 commands). 186/op16 is not a view change (grumpa-events, E-0206).
- **Method:** decompile; corpus scan of `(185, 30, arg)` against the `.scn` view counts.
- **Confidence:** proven (where the floor cell's value sits in the `.scn` is E-0500/Q-0500)

### E-0305 — Render order: actors by layer, ascending
- **Binary/file:** `FUN_0040ec20` (render list), `0x40eab0` (factory render).
- **Evidence:** after a scene loads, the factory collects every actor (id ≥ 2) whose layer
  `+0x114` is 0..8 as (actor, layer) pairs and sorts them by layer. Each frame it calls each
  actor's render (vtable[3]) in that order. Layers: 0 the base default (CFXView, the
  background), 1 and 4 the sprites (E-0302), 3 the 0x1a mesh actors (E-0303), 8 the 185
  manager (fades). So the layer-1 sprites draw before the meshes, and their depth frames hide
  parts of the meshes; the layer-4 sprites draw over them.
- **Method:** decompile.
- **Confidence:** proven (the order inside one layer comes from std::sort and is not pinned)

### E-0209 — The event VM runs in the engine (dev checks)
- **Binary/file:** `../scummvm/engines/grumpa/events.cpp` (commit `871171bb`), dev
  `grumpa_vm` (`dev.cpp`); `Actors/Items.abi` (66 records, all type 5, ids 100..179).
- **Evidence:** dev runs, logs at `-d2`: (1) Scene_061, view 1 (`185, 30, 1`), click
  (254,157): trigger 661 fires, sprite 730 (`doorclosed`) hides, 661 deactivates; its 8
  commands for scene 10 wait (flag 269 = 0 keeps the five guarded `== 0` and drops the two
  `== 1`); entering scene 10 delivers them (664/665 → 12, 644 → 0, 710 → 500, 730 → 2,
  731 → 3). With `(269, 56, 1)` first, 664/665 → 11 instead and 644/710 are dropped.
  (2) Timer 222 started by `(222, 64, 1000)`: its commands `(12, 51, 200)`, `(222, 13)`
  are delivered on the 52nd update (elapsed 1,020 ms > 1,000 on the 51st, run the next).
  (3) Scene 1, click (597,140): trigger 663 fires, `(185, 31, 211)` loads Scene_211.
  (4) Sprites animate by updates (two snapshots 7 updates apart differ). (5) Save in scene
  61 after (1), new game, load: the 8 deferred commands are back and reach scene 10.
- **Method:** `grumpa_vm` runs off-screen (SDL offscreen, surfacesdl).
- **Confidence:** proven (for these paths).

### E-0600 — The `.anb` loader reads exactly F frames; the rest of a file is never read; normals are x, y, z
- **Binary/file:** `FUN_004157d0` (`CFXAMeshEx` load), `FUN_004166e0` (draw), `FUN_004154b0`
  (per-frame bounding boxes); `Meshes/*.anb` (939).
- **Evidence:** after the sections the loader makes one read of `(F-1)·ΣA·24` bytes (frames
  1..F-1, each the vertices of every section in section order, frame after frame) and closes
  the file, so a stored frame beyond F is never read: 521 files store one (the `X2Y` and
  `N2N` clips, Q-0007), `012_D2D_Grumpa_In_Boat.ANB` 4,456 stray bytes. It then builds the
  Direct3D vertex buffer: per frame, one `D3DVERTEX` (FVF 0x112) per **uv index**, filled by
  walking the faces in order, corner by corner, with the corner's vertex (24 bytes copied as
  they are: pos x, y, z, normal x, y, z) and its uv; a uv index used by corners with different
  vertices keeps the last one written (105 files have such indices). The index buffer is the
  face uv-index triples (offset by the section's uv base). The draw is
  `DrawIndexedPrimitive(TRIANGLELIST, 0x112, buffer + frame·ΣB·32, ΣB, indices, ΣC·3)`, the
  frame being the mesh's `+0x11c`. The normal order is the stored one: averaged face normals
  ((b−a)×(c−a)) agree with the stored (x, y, z) at mean cosine 0.92 over 6,987 vertices of 30
  files, with the reversed order at 0.27 (this corrects E-0014's "stored z, y, x"). Normals
  are not unit length and Direct3D uses them as they are. `parsers/anb.py`: 939/939 parse,
  17,867 frames read, every byte accounted for (frames read + unread tail).
- **Method:** decompile; `python engines/grumpa/tools/parsers/anb.py`; a face-normal check
  over the parser output.
- **Confidence:** proven

### E-0601 — 0x1a `CFXStaticCharacter` animation: fields, play, stop, advance, delay timer
- **Binary/file:** vtable 0x490910: `FUN_00452100` Serialize [1], `FUN_004503e0` Initialize
  [2], `FUN_00450da0` render [3], `FUN_00450cc0` update [4], `FUN_00450f30` DoCommand [6];
  ctor `FUN_0044fc60`; `FUN_00454680` play, `FUN_004546e0` stop, `FUN_00453760` advance,
  `FUN_00451e20`/`FUN_004540c0`/`FUN_004543a0` the end lists; the delay timer (ctor
  `0x456cf0`, Serialize `FUN_00456d70`, `FUN_004578d0` start, `FUN_00457960` reload,
  `FUN_004578b0` tick, `FUN_00457850` expired, `FUN_00457750`/`FUN_004577f0`); scene `.abi`.
- **Evidence:** the 18 u32 after the state slots are `+0x1b4` fps, `+0x1b8` mode, `+0x1bc`
  bubble flags, `+0x1e4`, `+0x21c`, `+0x228`, `+0x1d0`, `+0x27c..+0x290` (6), `+0x1d4`
  playing, `+0x1c0` frame, `+0x1dc` autoplay, `+0x29c`, `+0x2a0`; then the delay timer's 14
  u32 (`+0x108` on, `+0x104`, `+0x10c`, `+0x110` counting, `+0x114`, `+0x118` random,
  `+0x11c`, `+0x120`, `+0x124` min ms, `+0x128` max ms, `+0x12c`, `+0x130` fixed ms, `+0x134`,
  `+0x138` ticks left); then two sub-objects, the bubbles, eight command lists (1st `+0x12c`
  forward end, 2nd `+0x13c` backward end, 8th `+0x19c` end; 3rd..7th belong to the bubble
  tests, `FUN_004539a0`), the `.anb` and `.tga` names. The ctor leaves running `+0x1d8`,
  direction `+0x1cc` and the tick counter `+0x1e8` at 0. **Render** draws mesh 0 at frame
  `+0x1c0` only when visible and `0 ≤ frame < F` (nothing is drawn otherwise). **Update**
  (when active `+0x10c`): if running, `counter + 1`; when `R / fps ≤ counter` (R from the
  device, Q-0200) counter = 0 and advance. Not running, with the timer on: playing → if the
  timer counts, tick it (`ticks − 1`) and when `ticks < 1` stop counting, reload it and set
  running; if it does not count, return; not playing → reload the timer, running = 0.
  **Advance** by mode bit, first match of 4, 8, 2, 0x10: 4 forward: frame + 1; at F running
  = 0 and: no loop (bit 1) → frame F−1, end list; loop, not playing → frame F−1; loop,
  playing → frame 0 and restart (below). 8 backward: frame − 1; below 0 running = 0 and: no
  loop → frame 0, end list; loop, not playing → 0; loop, playing → frame F−1, restart. 2
  ping-pong: direction 0: frame + 1, at F direction 1 and frame F−2; direction 1: frame − 1,
  below 0 running = 0, direction 0, frame 1 and: no loop → end list; loop and playing →
  restart. 0x10: direction 0: frame + 1, at F running = 0, frame F−1, direction 1, forward-end
  list; direction 1: frame − 1, below 0 direction 0, running = 0, frame 0, backward-end list
  (playing is left set). Restart: with the timer on, play (below); else running = 1. **Play**
  (op 0, 500, and 23 when autoplay): mode & 6 → frame 0, mode & 8 → frame F (one update with
  nothing drawn, then F−1); playing = 1; timer on → start it (counting, ticks = fixed ms · 50
  · 0.001, or with random a random value in [min, max) ms the same way; `DAT_0049f1e8` = 50,
  the float at 0x490aa8 = 0.001), else running = 1. It does not test "already playing".
  **Stop** (op 1, 501) clears playing only. Op 14/15 set/clear `+0x1e0` (bubble tests, on
  from the ctor). Op 86 reloads mesh and texture; op 92 the texture. Corpus (260 records):
  fps 15 ×166, 25 ×15, 12 ×13, 14 ×10, 8 ×8, 60 ×8; mode 4 ×95, 5 ×92, 3 ×31, 0x14 ×17, 2
  ×10, 0x10 ×7; playing 1 ×136; autoplay 1 ×104; frame 0 ×99; timer on 13; 237 meshes have
  F > 1; `Scene_027` `myra_1` starts at frame 56 = F (not drawn until played).
- **Method:** decompile; field census over the 110 scene `.abi`.
- **Confidence:** proven (logic); R as for sprites (Q-0200).

### E-0602 — A 0x1a scene status keeps the animation, and saving it clears autoplay
- **Binary/file:** `FUN_00452100` `case 4` / `case 5`.
- **Evidence:** mode 5 writes id, active, visible, latch `+0x250`, the state slots, playing
  `+0x1d4`, running `+0x1d8`, direction `+0x1cc`, frame `+0x1c0`, and autoplay `+0x1dc` after
  setting it to 0; mode 4 reads the same back. A revisited scene's meshes go on from where
  they were and do not autoplay again. The delay timer is not in the status.
- **Method:** decompile.
- **Confidence:** proven

### E-0603 — A character's animation clock: 0.46 frame per update, the clip looping
- **Binary/file:** CFXCharacter vtable 0x49046c ([3] render `FUN_004226a0`, [4] update
  `FUN_00421a60`, split out of `0x421a50` in the working copy).
- **Evidence:** the update returns unless active (`+0x10c`) and at home (`+0x444` = `+0x448`);
  it adds 0.46 (float at 0x4904a0) to `+0x4a4` and returns unless the sum exceeds 1.0 (0x49034c),
  then subtracts 1.0 and steps the frame `+0x494`; when frame + 1 reaches the clip's F the frame
  is 0 and the next clip is taken from the queue at `+0x404` (`+0x434` = the clip index into
  the mesh table `+0x2dc`, `+0x498` = its F). The render draws clip `+0x434` with the mesh's
  frame `+0x11c` set to `+0x494` by the update. So with nothing queued the clip loops at 0.46 ×
  50 = 23 frames a second. The update also moves the character by a per-frame vector table on
  the clip's mesh (`+0x150`, 12 bytes a frame; Q-0601).
- **Method:** decompile, disassembly at 0x421bf4..0x42206e.
- **Confidence:** proven (clock and wrap); the queue is part of Q-0403.

### E-0700 — Actor 185 is `CFXFadeEffect`: a fade to black by gamma ramp, its timing, and how view and scene changes wait for it
- **Binary/file:** type 0x12 ctor `FUN_0042ef00` (vtable `0x4905e0`), `FUN_0042f350` (base
  ramp), SetDevice `FUN_0042f040` (error string `CFXFadeEffect::Initialize(IFXDi…`), DoCommand
  `FUN_0042f210`, update `FUN_0042f540`, render `FUN_0042f730`, helpers `FUN_0042f290`
  (fade in), `FUN_0042f310` (fade out), `FUN_0042f410` (fade out, then a view),
  `FUN_0042f450` (fade out, then a scene), `0x42f4e0` (fade out, then a film); window
  procedure `FUN_00410cb0`; constants `0x49034c` (1.0), `0x490610` (1/255), `0x490608` (255.0).
- **Evidence:** the state is a level L (`+0x7bc`, 0..255), a step S (`+0x7c0`), a running flag
  (`+0x7b4`), a hold counter H (`+0x7c8`), a "black" flag (`+0x7b8`), a pending view
  (`+0x7d0`, −1 none), a pending scene (`+0x7cc`, −1 none) and a pending film name (`+0xbd4`).
  **Output:** with `DDCAPS2_PRIMARYGAMMA` the primary surface's gamma ramp is set to
  `base[i]·L` for red, green and blue, `base[i] = 255·(i/255)^(1/1.0) = i`, so every colour
  channel is scaled by L/255 (the whole screen); without it the render (layer 8, E-0305) draws
  an 800×600 quad of colour (L, L, L) blended ZERO·src + SRCCOLOR·dest, the same
  multiplication. **Update** (each 20 ms, while running): if H > 0, H −= 1 and the ramp is
  re-applied at the current L (a hold); else L += S; L ≥ 255 → L = 255, stopped, black = 0;
  L ≤ 0 → L = 0, stopped, black = 1. When it stops: a pending view is shown (`FUN_0045ae00`:
  view switch and broadcast 26) and a fade in over 20 starts; a pending film is handed to
  actor 187 (`FUN_0042bf80`) and L jumps back to 255 (`FUN_0042f290(0)`); a pending scene is
  requested from the factory (`FUN_0040cb20`). **Starts** (each sets H = 4 and running):
  fade out over n = L 255, S = −255/n (integer division); fade in over n = L 0, S = 255/n;
  fade in over 0 = L 255, S = 1, update and render at once. **DoCommand:** 30 → fade out over
  20, pending view `arg1`; 31 → `arg2 ≠ −1`: fade out over 20, pending scene `arg1`;
  `arg2 = −1`: L = 0 at once (S = −1, H = 4, update and render now), pending scene — the
  screen goes black at once and the scene changes after the 4-update hold; 32 → fade out over
  `arg1`; 33 → fade in over `arg1`. Timings: fade out over 20 = 4 held updates + 22 steps of
  12 (255 − 12·21 = 3, then ≤ 0); fade in over 20 the same; the scene entry's fade in over 24
  (E-0202) = 4 + 26 steps of 10. **Escape:** the window procedure broadcasts opcode 60 on
  Escape only when actor 185 exists, L ≠ 0 and it is not running; mouse input is not gated by
  the fade. **Films:** `0x42f4e0(n, name, arg)` (fade out over n, then the film) has one
  caller, `CFXCharacter::DoCommand` opcode 0x44 (`0x41e97a`: n = 16, the character's list
  `+0x678`/`+0x688` at index `arg1`); actor 187 (type 0x29) plays it through DirectShow
  (`FUN_0042b7b0`, `CoCreateInstance`). Those lists are the message block of E-0401, empty in
  all 44 characters, so no scene command reaches a film this way.
  SUPERSEDES the "31: none if `arg2 = −1`" reading of E-0206.
- **Method:** decompile; disassembly of the ramp loop at `0x42f350`; byte scan of `.text` for
  the fade fields (only `0x410f60`/`0x410f78` use them outside the class).
- **Confidence:** proven.

### E-0701 — The sprite rate R is 50: the device's frame-rate field (resolves Q-0200)
- **Binary/file:** device vtable `0x490548` (ctor `0x42c4f0`, made by `FUN_0042db40`): slot
  `0x24` `0x42d7e0`, slot `0x28` `0x42d800`; device ctor `0x42c58f`; `0x437591`;
  sprite update `FUN_0044da50`, SetDevice `FUN_0044d710`, ctor `FUN_0044c800`.
- **Evidence:** the sprite reads R from `+0x15c` (the device, stored by its SetDevice) through
  vtable `0x28` = `0x42d800`, which returns the device field `+0x58`. Slot `0x24`
  (`0x42d7e0`, set frame rate r) writes `+0x58 = r` and `+0x64 = 1000 / r`; the device ctor
  writes `+0x58 = 0x32`, and device init calls slot `0x24` with `push 0x32` at `0x437591`. Of
  the 23 indirect `call [reg+0x24]` in `.text`, the others are thiscall or pass a pointer
  (other interfaces). So a sprite steps one frame when its counter (incremented first)
  reaches `50 / fps` (unsigned division): every max(1, 50/fps) updates. The sprite ctor
  defaults fps (`+0x1e0`) to 50 and the mode (`+0x1e4`) to 4. Confirms E-0302's note.
- **Method:** disassembly.
- **Confidence:** proven.

### E-0702 — Actor 180 (type 6) is the ambience: ten looping `ambient_*.wav`, cross-faded by opcode 73
- **Binary/file:** `Actors/global2.atx` (block `<6>`), type 6 ctor `FUN_00413a60` (vtable
  `0x4903dc`), Serialize `FUN_00414090`, DoCommand `FUN_00413bd0`, update `FUN_00413fe0`,
  play `FUN_00413c00`, stop `FUN_00413f90`; CFXSound (vtable `0x49089c`): `FUN_004491b0`
  (loop flag `+0x1a4`), `FUN_00448f70` (play), `FUN_00449040` (stop), `FUN_00449180`
  (volume), `FUN_004490b0` (fade in), `FUN_004490f0` (fade out), update `FUN_00448db0`;
  `FUN_004491f0` (`"Sounds"`), `DAT_0049c81c` (−500); scene `.abi` commands.
- **Evidence:** mode 6 reads id 180, active, visible, `+0x148` the start index (0), a count
  (10) and the names (`ambient_jungle2.wav`, `ambient_monkey2.wav`, `ambient_ship2.wav`,
  `ambient_ShipUnderwater2.wav`, `ambient_desert2.wav`, `ambient_Indoor2.wav`,
  `ambient_surface2.wav`, `ambient_swamp2.wav`, `ambient_undersea2.wav`,
  `ambient_alternativ2.wav`); one CFXSound per name, set to loop; then, unless the start index
  is −1, Play(start). **Play(i)** (opcode 73, `arg1 = i`; ignored when out of range): if i is
  the current sound (`+0x140`), restart it only if it is not playing; else load
  `Sounds\<name i>`, and on success the old current becomes the previous (`+0x144`), i the
  current, its target volume −500 (hundredths of a dB: −5 dB); if i is the start index its
  volume is set to −500 at once, else it fades in from −5000 by 50 every update (100 updates,
  2 s); it plays looping; the previous one (if any) fades out: its volume counter starts at
  0 and falls by 50 every update (so it first jumps to 0 dB), and below −5000 it is stopped.
  **Stop** (opcode 74): stop the current and the previous. **Update** (every update, `active`
  not tested): the previous sound's update and, once it no longer plays, it is released
  (previous = −1); then the current sound's update. Status (mode 4/5, `Current\global.abi`):
  active, visible and the current index, played again on load (−1 none). Corpus: 59
  `(180, 73, i)` commands (i 0..9), 1 `(180, 74)` (scene 96). The files are in the cabinet's
  `Sounds_/`.
- **Method:** decompile; `events.py` walker.
- **Confidence:** proven.

### E-0703 — Actor 8 (type 0x1b) is `CFXGrumpaScore`: the HUD of coins, life, air and the current form
- **Binary/file:** `UI/008_Score/008_Score.atx` (block `<27><Score>`), ctor `FUN_00438da0`
  (vtable `0x490740`), Serialize `FUN_004393d0`, SetDevice `FUN_004396b0`, render
  `FUN_004396e0`, update `FUN_00439730`, DoCommand `FUN_004397a0`, layout `FUN_00439b80`,
  add `FUN_0043a2d0`, subtract `FUN_0043a430`, form `FUN_0043a590`, number `FUN_0043a100`,
  form lookup `FUN_0043a630`; CFXSprite setters `FUN_0044d9d0` (`+0x1d8`), `FUN_0044d9e0`
  (`+0x110`), `FUN_0044da00` (`+0x190/+0x194`), `FUN_0044da40` (`+0x1e4`), `FUN_0044e0b0`
  (frame, ignored out of range), `FUN_0044e100` (`+0x1f8`), `FUN_0044e1a0` (`+0x208`),
  `FUN_0044ecb0` (width `+0x1f0`), `FUN_00453990` (frame count `+0x1c0`), advance
  `FUN_0044dd80`; strings at `0x49e0f8` (`Air`, `Life`, `Coins`).
- **Evidence:** layer 6. **Slots:** 0 State, 1 "Coins" = 0, 2 "Life" = 99, 3 "Air" = 99
  (ctor). Mode 6 reads id 8, active 1, visible 1, the coin position (10, 10), the heart
  position (758, 10), the digit gap 10 and the digit spacing 2, 13 image names and 6 sound
  names (all under `UI/008_Score/`). Elements are CFXSprites (the 0x0d class, its frame-file
  rule E-0302): 0 `curage_star`, 1 `scare_star`, 2 `coin`, 3 `heart`, 4 `air`, 5
  `scorefont`, 6 `poison_icon`, 7 `strength_icon`, 8..12 the form icons (`grumpa`, `bear`,
  `boat`, `seahorse`, `dragonfly`); sounds 0 `SX_currage`, 1 `SX_scare`, 2 `coin`, 3
  `SX_addair`, 4 `SX_subair`, 5 `coin`. Every element: visible, active, colour key on with the
  key = frame 0's pixel (0, 0), view −1. Layout: coin at (10, 10); heart at (758, 10); the
  form icons at (758 − width − 8, 10), hidden; the air bar left of the form icon (x − 8 − its
  width), then poison and strength further left the same way, all three hidden; the two stars
  at (687, 0), ping-pong (mode 2), hide when done (`+0x1d8 = 1`: the advance clears active
  and visible at the end), hidden; then the current form's icon shown. Form map (`+0x2e0`,
  index `+0x2ec`, initially 0): character 10 → icon 8, 13 → 9, 11 → 10, 88 → 11, 12 → 12.
  **Add(k, n)** (k = 2 coins, 3 life, 4 air; slot k − 1): value += n, at most 99; coins: sound
  2; life and air: the bar's frame = frame count − value/9 − 1 (99 → frame 0), and when n ≠ 0
  and the value is not 99: life plays star 0 (play, show, active) and sound 0, air sound 3.
  **Sub(k, n):** value −= n, at least 0; life and air: frame = count − value/9 − 1 (99 →
  count − 1); if the old value was not 0: life plays star 1 and sound 1, air sound 4; coins
  silent. **DoCommand:** 2/3 visible on/off, 11/12 active on/off; 9/10 coins add/sub `arg1`;
  76/77 air add/sub; 78/79 show/hide the air bar, 80/81 the poison icon, 82/83 the strength
  icon; 85 the form: the score's Life = character `arg1`'s slot 1, hide icons 8..12, show the
  form's icon, Add(3, 0) (refresh the heart); 50/51 life add/sub `arg1` with `arg2`: 0 → the
  score's Life, then the current form character's slot 1 = Life; > 0 → character `arg2`'s
  slot 1 ± `arg1` (on 51, if it stays above 0 the character plays animation 0x17) and, if
  `arg2` is the current form, the score's Life too; −10 / −11 → forwarded as
  `(50|51, arg1, −10|−11)` to actor 3 / 4. **Render** (visible): every element but the font
  draws itself; then the coin count at x = coin x + coin width + 10, y = coin y: a value above
  9 draws two digit frames (the second at x + digit width + 2), else one. **Update** (active):
  the elements' animation (not the font's) and the sounds' updates. Status (mode 4/5): active,
  visible, form index, air/poison/strength shown, Coins and Air (not Life: re-read from the
  character on op 85). Files: `heart`/`air` have 11 frames, the stars 5, `scorefont` 10.
  Corpus: commands to 8: 9 ×2, 10 ×11, 50 ×25, 51 ×25, 76 ×29, 78 ×14, 79 ×12; the 129
  conditions on actor 8 all test slot 1 (Coins).
- **Method:** decompile, disassembly of the setters; corpus (`events.py` walker).
- **Confidence:** proven (logic); what the character's animation 0x17 is belongs to Q-0403.

### E-0704 — Character opcodes that reach the score, and the life/air slots
- **Binary/file:** `CFXCharacter::DoCommand` `FUN_0041e0d0`.
- **Evidence:** 0x32/0x33 (50/51) forward `(op, arg1, own id)` to actor 8 (E-0703), so a
  scene's `(10, 51, 11)` takes 11 life from Grumpa. 0x2c (44, make it the player's character
  through actor 3) also sends `(8, 85, id)`. On the character's own slots (`+0x11c` vector,
  value at `+0x104`, stride `0x118`): 0x58 / 0x59 add / subtract `arg1` on slot 2 (floor 0),
  0x5a / 0x5b the same on slot 3, 0x5d / 0x5e / 0x5f set slot 2 / 3 / 1. Corpus to characters
  10/12/13: 88 ×2 and 90 ×2; 50/51 via the forward; 44, 70 (0x46, split a rider form) and 72
  (0x48) belong to the role code (Q-0403).
- **Method:** decompile.
- **Confidence:** proven.

### E-0705 — The proximity gate's spheres: the trigger's from its record, the character's from Characters.abi
- **Binary/file:** `FUN_00457ea0` (trigger Serialize), `FUN_0045a0b0`, `FUN_00459a60` (gate),
  `FUN_0044c6e0` (sphere test), `FUN_00424e90` (character sphere), `FUN_00446a00`/
  `FUN_00446b10`/`FUN_00447790` (actor 3), `FUN_004354d0` (actor 4), `FUN_00430b40`/
  `FUN_0042fb50`/`FUN_0042fc20` (type 0x1c actors 91..95), `FUN_00422670`.
- **Evidence:** the four u32 after a trigger's polygon (`parsers/abi.py` "358,370,36c,368")
  are floats `x, y, z, r`: `FUN_0045a0b0` makes the sphere object `+0x13c` with centre
  `+0x104..+0x10c` = (x, y, z) and radius `+0x110` = r. Two spheres overlap when the centre
  distance < r1 + r2 (`FUN_0044c6e0`). A character's sphere: centre = its position `+0x16c`
  with y raised by its radius, radius `+0x290`, the third float of the `f32 [0x28c],
  f32 [0x5fc], f32 [0x290]` group of Characters.abi (E-0401). Gate (with `+0x154 = 1`): bit 1
  of `+0x188`: actor 3 (type 0x16) holds a character (`+0x298` ≥ 0) that is present
  (`visible` and at home, `FUN_00422670`), its sphere overlaps, and `+0x150` is −1 or that
  character's id; bit 2: the same for actor 4's character (`+0x290`; if actor 4 is absent,
  actor 95's `+0x2a0`) against `+0x14c`; bit 4: the characters of actors 91, 92, 93, 94
  (`+0x2a0`), no id test. With `+0x170 = 1` each source passes once per entry (its own latch
  `+0x158`, `+0x15c`, `+0x160..+0x16c`, cleared while it is outside). Refines E-0207.
- **Method:** decompile.
- **Confidence:** proven.

### E-0706 — Fades, score and ambience run in the engine (dev checks)
- **Binary/file:** `../scummvm/engines/grumpa/events.cpp`, `score.cpp`, `grumpa.cpp` (commit
  `db3577a1`); dev `grumpa_vm` (`snap` draws the whole frame, commit `3c7c0d11`).
- **Evidence:** dev runs off-screen, logs at `-d2`: (1) scene 1: 2 updates after entry the
  frame is black (mean luminance 0), 22 updates later 15.9, at rest 27.0; clicking (597, 140)
  fires trigger 663, 10 updates later 16.1, 30 updates later black with scene 211 entered,
  70 updates later scene 211 at full brightness ("fade ended at 0/255" in the log at the
  expected updates). (2) Score: `(8, 9, 5)`, `(8, 9, 7)` show "12" beside the coin; `(10, 51,
  30)` lowers the heart and plays the scare star at (687, 0), hidden 20 updates later;
  `(8, 78)`, `(8, 77, 40)` show the lowered air bar left of Grumpa's icon. (3) `(180, 73, 4)`
  switches from the jungle to the desert ambience; save, `(8, 10, 12)`, load: the coins are
  12 again and the desert ambience plays.
- **Method:** `grumpa_vm` runs (SDL offscreen, surfacesdl), PNG snapshots.
- **Confidence:** proven (for these paths).

### E-0900 — Items in the world: drawn spinning at their place, hovered and picked up within 160 units of the player
- **Binary/file:** CFXItem (vtable `0x49076c`, ctor `FUN_0043af70`): draw `FUN_0043baf0`,
  update `FUN_0043b850`, DoCommand `FUN_0043bd30` (op 18 at `0x43bf3a..0x43c043`), load
  `FUN_0043b3e0`, drop `FUN_0043c340`, `FUN_0043c2d0` (step forward), `FUN_0043d8c0`
  (`D3DXMatrixRotationYawPitchRoll` `0x473e71` with yaw = rot.y, pitch = rot.x, roll =
  rot.z); mesh class: draw `FUN_004166e0`, bounding boxes `FUN_004154b0`, screen rectangle
  `FUN_00415350`; global item effects loaded by `FUN_00435a00` (`Meshes\effect_item.ANB`,
  `Bitmaps\effect_item.tga`, `Sounds\effect_item.wav` into `DAT_004c01a0/a4/9c`); cursor
  `FUN_004461a0` (set kind); constants `0x490790` 160.0, `0x490794` 0.05, `0x490768` 2π,
  `0x4904c0` 30.0, `0x49049c` 20.0.
- **Evidence:** layer 3 (ctor `+0x114 = 3`), like the 0x1a meshes. **Draw** when visible, its
  scene (`+0x288`) is the current scene (`+0x4f8`, set by the entry broadcast 23) and State
  is 4: load the mesh (`Meshes\IO_*.ANB`), texture (`Bitmaps\IT_*.tga`) and name sound
  (`Sounds\IS_*.wav`) on first use; when the rotation changed, world = RotationYawPitchRoll
  (yaw rot.y, pitch rot.x, roll rot.z) with the translation = position `+0x28c`; draw the
  mesh's current frame (always 0 for items) with that world matrix through the view camera,
  as the 0x1a meshes are drawn (E-0303). The mesh object transforms the 8 corners of that
  frame's axis-aligned bounding box with the same matrices (`ProcessVertices`) and keeps
  their screen bounding rectangle (min/max x and y); the item copies it to `+0x4dc`. While
  the glow flag `+0x500` is set it also draws `effect_item.ANB` with `effect_item.tga` at the
  same matrix with z writes off. **Update** when active, in the current scene and State 4:
  every 50/25 = 2 updates the yaw rot.y grows by 0.05 rad (wrapping at 2π), and while the
  glow flag is set the glow mesh steps one frame and a counter `+0x504` counts up; past 10
  steps the glow ends. Then, unless the cursor's state is 7 or the inventory panel (actor
  90) is shown: the rectangle `+0x4dc`, widened to centre ± 30 px in each dimension that is
  narrower than 40, contains the mouse, and the player's character (actor 3's) is within
  160 units of the item's position (3D distance): the cursor takes kind 2 (the same as a
  hotspot under the mouse, trigger update `0x4591ec`), the item speaks its name (DoCommand
  0) once per entry (`+0x4f4`), and the hovered flag `+0x4fc` is set; otherwise `+0x4f4 = 1`,
  `+0x4fc = 0`. **Pick-up** (op 18, a click `x | y << 16`): State 4, in the current scene,
  hovered, the click inside the widened rectangle, the cursor holding nothing → the panel's
  add (`FUN_004387d0`; success → State 3) and `effect_item.wav` plays. **Placing:** op 71
  `a`: position = actor `a`'s position with y + 30, rotation = actor `a`'s orientation
  (`+0x160..`), active, visible, State 4, scene = current, the glow restarts at frame 0,
  `effect_item.wav` plays; op 54 `n`: scene = `n`, State 4 (position kept). **Drop beside
  Grumpa** (panel full): position = the player's character's position with y + 20, rotation =
  its orientation, then 30 units forward (x += sin yaw · 30, z += cos yaw · 30); if that point
  is off the walk mesh (actor 600, `FUN_00433830`) 30 units back instead; if that fails too,
  the player's position; State 4, scene current, active, visible, glow, sound.
- **Method:** decompile; disassembly where the decompiler stops at SafeDisc's two-byte traps
  (`int3 int3` / `ud2` after `PtInRect`, read as `test eax, eax`: the next instruction is a
  conditional jump on its result).
- **Confidence:** proven (logic); the cursor kinds' pictures are Q-0900.

### E-0901 — The panel's weapon slot and its two buttons (resolves Q-0502)
- **Binary/file:** panel DoCommand `FUN_00437d00` op 18 (`0x437d97..0x438446`), layout
  `FUN_00438660`, `FUN_00410c60` (an actor's `+0x130`; on the cursor = its kind),
  `FUN_00421780` (a character wears / takes off an attachment), jump tables `0x43848c`/
  `0x4384a0` and `0x4384b0`/`0x4384c4`; `Actors/Items.abi`.
- **Evidence:** op 18 tests, in this order: the door button `+0x248` (x+200..x+232,
  y+96..y+132): with the cursor of kind 1 (the plain pointer) push `(1, 60)` (actor 1, the
  menu: the main menu, as Escape); the diskette button `+0x258` (x+70..x+100): with kind 1,
  push `(1, 61)` (the saved games); the nine slots (E-0504); the shield slot `+0x238`
  (x+210, y); the weapon slot `+0x228` (x, y, 96×96). The trap after the weapon slot's
  `PtInRect` (`0x43811e`) is the `test eax, eax` before `je`. **Weapon slot:** nothing on the
  cursor and a weapon in the slot (`+0x220`): actor 10 takes off the weapon's attachment
  (`FUN_00421780(kind, 0)`), the weapon goes on the cursor (State 6), push `(weapon, 0)` (its
  name), the slot empties (`+0x218 = 0`). An item on the cursor: if it is a weapon, a weapon
  already in the slot goes back to the inventory (add), the slot takes the held one
  (`+0x218 = 1`, State 3), the cursor empties and actor 10 wears it (`FUN_00421780(kind,
  1)`); any other item is added to the inventory and the cursor empties. Weapons and their
  attachment kinds: 100 Father's Sword (broken) 4, 101 Father's Sword 1, 110 Sword of Might
  3, 113 Hammer 2. The shield slot is the same with 138 (Shield of Protection, kind 0) and
  134 (Shield, kind 5). SUPERSEDES the "second button only when the scene is not 1" of
  E-0504/Q-0502: the test is the cursor's kind, not the scene.
- **Method:** disassembly.
- **Confidence:** proven; what actor 1 shows on 60/61 is the menu actor's code (type 0x1f,
  not read), named here from Help.txt (diskette = saved games, door = main menu).

### E-0902 — The ambience starts at boot, before the main menu (answers Q-0700)
- **Binary/file:** boot `0x437600..0x4377f7` (inside `FUN_00436aa0`): loads
  `UI\001_Menu\001_Menu.atx` (`0x43769d`), then `FUN_00435a00` (`0x4376ec`), which loads
  `Actors\global2.atx` (`CreateFromATXFile`), so actor 180 is created and plays its start
  sound (E-0702); then the inventory, cursor and 185 (fade in over 10). The menu class
  (type 0x1f, `0x43db00..0x441fb0`) has no push of actor 180 or of opcodes 73/74.
- **Evidence:** the jungle ambience (index 0) plays from boot under the main menu, at −5 dB;
  nothing in the menu stops it.
- **Method:** disassembly of the boot sequence; byte scan of the menu class for the pushes.
- **Confidence:** strong (static; whether the intro film's playback mutes it is not read).

### E-0800 — CFXFloor (type 0x08, id 600): layout and point-in-face test
- **Binary/file:** ctor `0x432600` (vtable `0x49067c`: [1] Serialize `0x432880`, [2] Initialize
  `0x432790`, [6] event handler `0x4327c0`), CreateBuffers `0x432e10`, `FUN_00432c60`,
  `FUN_00433040`/`FUN_00433250`/`FUN_00433450`, `FUN_00433830`, `FUN_00433880`.
- **Evidence:** fields: `+0x12c` vertices (32 B each; only bytes 0..11, x y z, are ever read by
  the floor code), `+0x130` faces (3×u16), `+0x134` per-face u16 "floor type", `+0x138`
  neighbours (3×s16, −1 = boundary; slot i = edge v[i]→v[(i+1)%3]), `+0x13c` nv, `+0x13e` nf,
  `+0x140` last face, `+0x148` vector of platform actor ids, `+0x164` wall-contact triples,
  `+0x3044` their float count, `+0x3048` 29 floor-type blocking flags (ctor sets all to 1).
  Face test (`0x433040`): reject by the triangle's x and z min/max box (inclusive), then three
  2D edge functions in x/z for edges (v1,v0), (v2,v1), (v0,v2) must all be > 0.0 (strict; one
  winding only). Face search `0x433830` = linear scan 0..nf−1, first hit, stored in `+0x140`,
  else −1. `0x433880` = try the hint face, then its three neighbours in slot order, then the
  linear scan.
- **Method:** decompile + byte scan of call sites; constants read from `.rdata`
  (`0x49045c` = 0.0f).
- **Confidence:** proven

### E-0801 — Floor height: inverse-distance blend of the three edges' closest points
- **Binary/file:** `FUN_00433490` (called from `0x433cf0`, `0x433f0c`).
- **Evidence:** on the static mesh (platform == −1) for each edge (v0v1, v1v2, v2v0) the
  point is projected in x/z onto the edge's infinite line (parameter t, not clamped), y is
  lerped along the edge at t, and weighted by 1/d (d = x/z distance to that projection; if
  |d| < 1e−7 the weight is 1e15). Height = Σ w·y / Σ w. On a platform the height is the y of
  the face's first vertex in the platform mesh's current frame (vertex index +
  frame×verts-per-frame).
- **Method:** decompile; doubles at `0x4906a0..0x4906b8` = 1.0, 1e15, −1e−7, 1e−7.
- **Confidence:** proven

### E-0802 — CFXFloor::Move (`0x433bb0`): platforms, wall slide, height smoothing
- **Binary/file:** `FUN_00433bb0(pos*, delta*, radius, platform*, face*)`, `FUN_00433950`;
  one caller, the character update `0x421a60` (call at `0x4220cb`; Ghidra had no function
  there, decompiled read-only).
- **Evidence:** 1) Platforms: for each id in `+0x148` whose actor is active (`+0x10c` == 1),
  test pos+delta against every face of that mesh's (frame-0) vertices; on a hit store face
  and platform index, pos += delta, y = 0.4·y + 0.6·height, return 1. 2) Else platform = −1
  and, if face is −1, a full face search at pos. 3) Up to 100 iterations: find the face under
  pos+delta (`0x433880`); none → pos += delta, face = −1, return 1 (unconstrained). Else
  flood from that face (`0x433950`): per edge, the x/z closest point on the segment (t clamped
  0..1); if its distance < radius then a boundary edge (−1) records (dist, cx−px, cz−pz),
  an interior edge recurses into the unvisited neighbour. If contacts exist, take the
  nearest (start 999999) and add (d/dist)·(dist−radius) to delta's x and z (pushes the target
  out to exactly `radius` from that wall); repeat until no contact. 4) pos += delta,
  y = 0.4·y + 0.6·height (E-0801), return 0.
- **Method:** decompile; floats `0x4906c4` = 0.4, `0x490640` = 0.6, `0x4906c0` = 999999,
  `0x49034c` = 1.0.
- **Confidence:** proven

### E-0803 — How the character uses the floor result (floor types)
- **Binary/file:** `0x421a60` (character update, after `0x4220cb`), `FUN_00433010`,
  `FUN_00432a80`, `FUN_004327c0`, `FUN_00450f30` (`0x451156`).
- **Evidence:** the character keeps pos `+0x16c`, move delta `+0x294` (zeroed after the
  call), radius `+0x28c`, old pos `+0x2a0`, face `+0x44c`, platform `+0x454`, floor type
  `+0x450`, mode `+0x48c`. After Move: face −1 → back to the old position (the mesh is a hard
  boundary). New y above old y + 20 (static) or + 80 (platform) → back to old and
  `FUN_004219f0(−2.0)`. Floor type = the face's u16 (15 on a platform, `0x433010`). Type > 18
  and flag `+0x3048+4·type` == 1 → back to old (types 19, 20, 21 are walls until opened).
  Mode 1 → y = −0.5 and only type 13 faces walkable; type 13 with mode 2 → y = −0.5;
  on types 12/13 animation states 15..17 (and type 12 with mode 2) keep the old y. Floor
  opcodes (vtable[6]): 5 arg → flag[arg−1] = 1 (arg 0: all 29), 6 → flag = 0, 23 (scene
  entry) clears the platform list; the setter only accepts arg−1 in 1..28, the reader
  type in 1..28. 0x1a mesh actors with `+0x1d0` == 1 add their id to the platform list at
  device init (`0x451156`).
- **Method:** decompile; floats `0x49049c` = 20, `0x490498` = 80, `0x490460` = 1.0.
- **Confidence:** proven (types 1, 2, 3, 8: no reader found, Q-0800)

### E-0804 — Scene links (0x14 id 601): exits fire scene change, entries place the player
- **Binary/file:** `CFXToScene` vtable `0x490878` ([4] update `0x448210`, [6] `0x447ba0`),
  `FUN_00448360`, `FUN_00448250`, `FUN_00447270`, `FUN_0044c6e0`, `FUN_00446b10`.
- **Evidence:** exits (vector `+0x130`) / entries (`+0x144`). Each update the player sphere
  (holder actor 3, `0x446b10`) is tested against each exit sphere (`0x44c6e0`); the first
  hit while the latch `+0x15c` is clear sets the latch, remembers the exit's scene
  (`+0x168`) and pushes (now, actor 185, opcode 31, arg1 = exit scene): a scene change with
  the fade. The latch clears when the player is out of the sphere of the remembered scene.
  On scene entry the player holder (`0x447270`) calls `0x448250` with the previous scene:
  the entry whose scene equals it gives position (`+0x104`) and rotation (`+0x110`); if
  none, an entry with scene −2 means keep the current place; else the first entry. This is
  skipped on the first entry after a load/new game (holder `+0x2c8` == 0, the saved view is
  used).
- **Method:** decompile (vtable from `.rdata`).
- **Confidence:** proven

### E-0810 — Player input: mouse buttons as broadcasts, four keys polled
- **Binary/file:** window procedure `FUN_00410cb0`; mouse actor 2 handlers `FUN_00445660`
  (WM_LBUTTONDOWN), `FUN_00445bf0` (UP), `FUN_00445920` (WM_RBUTTONDOWN), `FUN_00445e90` (UP),
  `FUN_00446350` (WM_MOUSEMOVE); actor 3 update `0x446f70` (decompiled read-only; its
  `GetAsyncKeyState` is the SafeDisc IAT slot `sd_004901dc`).
- **Evidence:** the window procedure passes mouse messages (when no message box `DAT_004ba724`
  and no menu) to actor 2, which queues a command with packed `(x | y << 16)`: 0x12 left
  down, 0x14 left up, 0x13 right down, 0x15 right up, 0x16 move; target −1 (broadcast), or 90
  (the inventory panel) while actor 2's `+0x148` is 1. Right down without Ctrl toggles that
  `+0x148` first. WM_KEYDOWN handles only Escape (0x1b: the fade/menu path) and Space (closes
  a message box). Character control keys are polled by actor 3 every animation tick: Ctrl
  (0x11) combat stance, Space (0x20) jump, Shift (0x10) run while the left button is held,
  Backspace (0x08) leave/dismount (opcode 0x46 or 0x37 to actor 4's character). No arrow or
  WASD keys and no DirectInput exist in the program.
- **Method:** decompile.
- **Confidence:** proven

### E-0811 — Actor 3 (type 0x16) is the player controller
- **Binary/file:** ctor `FUN_00446850` (0x2d0 B, `CreateActor` case 0x16), vtable `0x490854`:
  [1] Serialize `0x4474e0`, [4] Update `0x446f70`, [6] DoCommand `0x446ba0`; `FUN_004473c0`,
  `FUN_00447270`, `FUN_00446db0`, `FUN_00446a30`/`a70`/`ac0`/`b10`.
- **Evidence:** DoCommand: 0x12/0x14 set/clear left-held `+0x2bc`, 0x13/0x15 set/clear
  right-held `+0x2c0`, each stores the cursor in `+0x29c/+0x2a0` and `+0x2a4/+0x2a8` and
  calls `FUN_004473c0`; 0x16 is ignored. 0x17 (scene entry) stores the scene and runs
  `FUN_00447270` (entry placement, E-0804, then the character's request 5 = reset to idle).
  0x23 sets/clears `+0x2c8`; 0x37 forwards 1 to the character and releases it; 0..3, 0xb..0xd,
  0x32..0x36, 0x48, 500, 501 are forwarded to the character `+0x298`. `FUN_004473c0` turns
  buttons into a request (`FUN_0041fde0(req, turn)`, E-0813): in combat stance (`+0x2c4`):
  left held while the clip is 0 or 0x20 → a random attack slot 0x12 + rand()%3; right held →
  slot 0x15; stance with no button while the clip is 2 or 5 → 2 (stop). Otherwise: if
  actor 2's cursor kind (`FUN_00410c60`) is not 9..25 the left flag is cleared (clicks on
  hotspots do not walk); left held → request 0 (walk) with the turn `+0x2b8`, else request 2
  (stop). Accessors copy the character's position `+0x16c` (`ac0` → `+0x150`), orientation
  (`a70` → `+0x144`), screen point `+0x158/+0x15c` (`a30`) and sphere (`b10`).
- **Method:** decompile (vtable read from memory).
- **Confidence:** proven

### E-0812 — Actor 3's update: the steer angle from the cursor, keys, view by floor type
- **Binary/file:** `0x446f70`, mouse actor `FUN_00445360` (via `FUN_00445440`), view list 602
  `FUN_0045ae00` (`+0xdf4`).
- **Evidence:** runs on the 0.46/update clock (`+0x28c`, as E-0603). Order: copy the
  character's position and orientation; if the character's floor type `+0x450` is 0..4 and
  its mode `+0x48c` != 1, that type is a **view index**: the first time it selects the view
  (`FUN_0045ae00`), later a change queues (185, 30, type) (view change with fade); then the
  turn `+0x2b8` = mouse angle (actor 2 `+0x154`) − (yaw `+0x164` − view yaw (602 `+0xdf4`)) − π;
  attack hit timer `+0x2b4` → `FUN_00446db0`; Ctrl polled (stance only if clip slot 0x12
  exists; cursor kind 7); Space (floor type not 13, not in stance, `DAT_004c04b4` == 0) →
  request 3; Shift with left held → request 1; Backspace as E-0810; last, unless the clip is
  0xf/0x10/0x11 or `DAT_004c04b0` is set, if the cursor is more than 20 px from the
  character on screen (actor 2 `+0x150`) → request −1 (turn only). The mouse actor's angle:
  d = cursor − character's screen point, `+0x150` = |d|, `+0x154` = π ± acos(a component of
  normalized d), negated when d.x > 0 (component: Q-0805). View yaw `+0xdf4` comes from the
  view matrix's forward vector the same way.
- **Method:** decompile; floats `0x4904a0` 0.46, `0x490850` π, `0x49084c` 1, `0x49049c` 20,
  `0x49081c` π.
- **Confidence:** proven (the acos operand not read)

### E-0813 — Character requests: the clip-queue table and the turn smoothing
- **Binary/file:** `FUN_0041fde0(char, req, turn)`; clip queue (deque) `+0x404`, count `+0x430`.
- **Evidence:** turn (when the countdown lock `+0x4dc` is 0): wrap yaw `+0x164` and `turn` into
  [−π, π], then `+0x4ac` = 10 steps of `+0x4b8` = turn × 0.1; each animation tick of the
  character update adds one step to yaw (not in clips 8, 0xc, 0x12..0x14). It is re-aimed on
  every call, so while walking the yaw closes 10% of the error per tick. req −1 stops there.
  Every other request clears the queue, then pushes (current clip → queued slots; "cut" =
  frame set to the clip's F, so the queue advances on the next tick): **0 walk**: 0/0xb →
  cut, 1, 2; 1, 2, 3 → 2; 0xd → cut, 1, 2; 0x20 → cut, 0x21, 1, 2; others nothing. **1 run**
  (one burst, re-requested while Shift is held): 0/0xb → 1, 4, 5, 6, 2; 1/2 → 4, 5, 6, 2;
  3 → 1, 4, 5, 6, 2; 5 → 5, 6, 2; 0x20 → 0x21, 1, 4, 5, 6, 2. **2 stop**: 1 or 2 → 3, 0;
  5 → 7, 0; else → 0. **3 jump** (needs slot 0x10): 0/0xb → 0xf, 0; 1/3 → 0x10, 0; 2 → switch
  now to 0x10 frame 0, then 0; 5 → now 0x11, then 0; 0x20 → 0x21, 0xf, 0. **4 die**: 8, 0xc.
  **5 reset**: clip 0 frame 0, queue 0, clock 0.6. **0x12..0x15, 0x17, 0x1f..0x28**: that
  slot, then 0. Slots are the `.anb` file numbers (E-0815): 0 N2N idle, 1 N2W, 2 W2W walk
  loop, 3 W2N, 4 W2R, 5 R2R run loop, 6 R2W, 7 R2N, 8 N2D, 0xc D2D, 0xf N2J2N, 0x10 W2J2N,
  0x11 R2J2N, 0x12..0x14 attacks, 0x15 N2D2N, 0x17 N2H2N (hit), 0x1f..0x21 S01..S03. The
  update (`0x421a60`) also queues 0x1f, 0x20 after 11 idle cycles in a row if slot 0x1f exists
  (the fidget; walking from 0x20 plays 0x21 first).
- **Method:** decompile (`FUN_00426d40` clear, `FUN_00426a40` push in the jump arm).
- **Confidence:** proven for the table; the idle variants 0xb/0xd not traced.

### E-0814 — Character motion per animation tick: root motion from the clip, yaw sign
- **Binary/file:** character update `0x421a60` (`0x421bf4..0x4220cb`).
- **Evidence:** on each animation tick (0.46/update, E-0603), after the frame step and the yaw
  step: if the clip is not 0, take the clip mesh's table `+0x150` at the current frame
  (x, y, z) and add to the move delta `+0x294`: dx = z·sin(yaw) + x·cos(yaw), dz = z·cos(yaw) −
  x·sin(yaw); y is added to `+0x178`, not the position. The delta then goes to the floor's
  Move (E-0802, radius `+0x28c`) and is zeroed. No speed constant: the speed is authored per
  frame in the `.amb` (Grumpa W2W ≈ 5.1, R2R ≈ 8.5..9.7 units a tick, ≈ 118 and ≈ 210 units/s
  at 23 ticks/s). Local +z is forward = (sin yaw, 0, cos yaw), the D3DX RotationY convention
  the engine already uses (Q-0404).
- **Method:** decompile; corpus values from `Meshes/002_W2W_Grumpa.amb`, `005_R2R_Grumpa.amb`.
- **Confidence:** proven

### E-0815 — `.amb` is a clip's per-frame root motion; the clip slot is the name's number
- **Binary/file:** `CFXAMeshEx::CreateFromFile` `FUN_00416a90`, `CFXCharacter::LoadResources`
  `FUN_0041f2b0`; `Meshes/*.amb`, `*.anb`.
- **Evidence:** the `.amb` count is the clip's frame count and each 24-byte record is a
  frame: a translation (x, y, z) into `+0x150` and a rotation triple into `+0x154` (stored
  reversed). Not vertices and normals (supersedes E-0013's reading; the byte layout stands).
  Corpus: count == `.anb` F for 580 of 586 pairs (6 differ, Q-0807). Grumpa: idle all zero,
  N2W x only, W2W/R2R z ≈ 5/9 a frame, the rotation triple almost always zero.
  LoadResources puts each listed `.anb` at slot `atoi(name)` (`FUN_0047c0ce`) of the 44-slot
  table `+0x2dc` (SetDevice sizes it to 0x2c): `004_W2R` is slot 4, `031_S01` slot 0x1f.
- **Method:** decompile; corpus script over `Meshes/`.
- **Confidence:** proven

### E-0816 — Who is the player's character: opcode 0x2c; the scene follows the player
- **Binary/file:** `CFXCharacter::DoCommand` `FUN_0041e0d0` (case 0x2c), actor 3
  `FUN_00447780` (setter of `+0x298`), `FUN_00447270` (actor 3 op 0x17), `FUN_004250e0`.
- **Evidence:** character opcode 0x2c: if actor 3 already holds a character, that one is sent
  opcode 1 (deactivate) and its role mesh `+0x564` set to 0; then actor 3's `+0x298` = this
  character's id (`+0x108`), the character becomes active and visible, home `+0x444` = the
  current scene `+0x448`, and its role `+0x564` = 1. Actor 3's `+0x298` is written only by
  this setter (and released to −1 by actor 3's op 0x37). On each scene entry, actor 3's
  op 0x17 places the held character at the entry point (E-0804) and, if that character is
  active (`+0x10c` == 1), sets its home `+0x444` to the new scene (`FUN_004250e0` stores its
  argument there); visible is untouched (stays 1). So the held character is present in every
  scene it walks into.
- **Method:** decompile.
- **Confidence:** proven (which command list sends 0x2c to character 10 on a new game not
  located)

### E-0817 — The cursor angle: acos of the normalized screen y; the cursor arrow follows it
- **Binary/file:** mouse actor `FUN_00445360` (`0x44537b..0x445430`).
- **Evidence:** d = cursor (`+0x158`, `+0x15c`, ints) − the held character's screen point
  (actor 3 `FUN_00446a30`); `+0x150` = |d|; d is normalized (D3DXVec2Normalize `0x473ddd`)
  and acos (`0x47c9f0`) is taken of the **normalized y** (screen y, down positive); the result
  is negated when the raw d.x > 0; `+0x154` = π + that. When the cursor kind `+0x130` is in
  9..24 it is replaced by 9 + int(angle × k1 − k2) (`0x490848`, `0x490844`, via
  `FUN_00446130`): the 16 walk-arrow cursors point toward the walk direction. Resolves Q-0805's
  operand.
- **Method:** disassembly.
- **Confidence:** proven

### E-1000 — The CD's cabinet names files by file group; the game runs from the CD as is
- **Binary/file:** `games/grumpa/discs/cd/data1.hdr` (685,933 B), `data1.cab` (4,206,704 B),
  `data2.cab` (282,887,848 B); `Movies/`; `Setup.ini`.
- **Evidence:** an InstallShield cabinet of major version 6: the descriptor's directory table
  has only 16 entries, all leaf folders (`""`, `shellmedia`, `Current`, `Player`,
  `Player1..6`, `001_Menu`, `002_Cursor`, `008_Score`, `090_Inventory`, `DIRECTX8`, a URL);
  the top folders are the file groups (descriptor `+0x3e`: 71 hash chains of
  `name, descriptor, next`; a group descriptor is `name, 0x12 bytes, first file, last file`,
  as unshield reads it). A file's path is `<file group>/<directory>/<name>`: `Bitmaps` 2,262,
  `Meshes` 1,638, `Scenes` 221, `Actors` 4, `UI` 125 (in `001_Menu` .. `090_Inventory`),
  `Sounds_` 550, `Sounds <Language>` 241..280, `Local <Language>` 4, `Shell <Language>` 33,
  `Movies Danish/Finnish/Norwegian` 1 each (`grumpa_intro.mpg`, 16,310,276 B, three md5s),
  `Save` 20, `Profileshell` 36; 67 installer files. No `Movies Swedish` file: the Swedish
  intro (md5 `7ac8c3b9…`) and the language-free `grumpa_death`, `grumpa_outro`, `unplug.mpg`
  are only on the CD in `Movies/`. 328 file names occur in more than one group (the language
  `Sounds` groups, `Text.txt` in each `Local` and `UI/001_Menu`, `Characters.abi` in `Actors`
  51,645 B and `Scenes` 46,648 B), so a cabinet named by file name alone (ScummVM's
  `makeInstallShieldArchive` default) loses them. Language groups are spelled with a space
  (`Sounds Swedish`), which unshield writes as `_`; 11 names are cp1252 (`släpp_lös_mig_sv.wav`,
  `dödgrumpapappa.tga`), which unshield writes with `_`. `Setup.ini` lists languages
  0x0006, 0x000b, 0x0014, 0x001d (Danish, Finnish, Norwegian, Swedish), default 0x001d.
- **Method:** `unshield l`/`g` (1.6.2); the engine's cabinet, named by file group, listed
  6,111 members, identical to `games/grumpa/discs/cab` (spaces as `_`) but for the 67
  installer files and the 11 cp1252 names. Scripted runs on the CD folder (dev
  `grumpa_vm=1;ticks 50;snap`: pixel-identical to the `hut` reference made from the unpacked
  cabinet; `grumpa_menu=1`; `grumpa_vm=211;op 646 0 0 0;wait 600`: the voice lines play).
  Detection md5s by `tools/detection_entry.py`: `data1.hdr` `0fb9940d…`, `Actors/Items.abi`
  `293eee0f…` (named alone in the cabinet).
- **Confidence:** proven

### E-0818 — Scene exits are armed only after the player has been outside them
- **Binary/file:** `CFXToScene` ctor `FUN_00447920` (`CreateActor` case 0x14, 0x170 B),
  update `0x448210` (decompiled read-only), exit test `FUN_00448360`, DoCommand `0x447ba0`.
- **Evidence:** the constructor sets latch `+0x15c` = 1, first-update flag `+0x160` = 1 and
  remembered scene `+0x168` = 0; the object comes with the scene's `.scn` (record 601), so
  every scene entry starts latched. The update tests the player sphere (actor 3) against each
  exit with no other gate (no clip, movement, fade or actor 185 test; DoCommand handles only
  0x17, which stores the scene number in its sub-object). Per exit: a hit remembers that
  exit's scene in `+0x168` and fires (185, 31, scene) only if the latch is clear, then sets
  it; a miss clears the latch when that exit's scene equals `+0x168`. After the loop, if
  `+0x160` is still 1 and no exit was hit, both `+0x160` and the latch clear. So a player
  placed inside an exit on arrival does not bounce back: the latch stays set until the
  player leaves that exit's sphere, then re-entering it fires.
- **Method:** decompile.
- **Confidence:** proven

### E-0830 — The floor Move runs every animation tick; actor 3's entry resets the clip every entry
- **Binary/file:** character update `0x421a60`, actor 3 op 0x17 `FUN_00447270`.
- **Evidence:** in the update the root-motion block is the only part conditioned on the clip
  being non-zero; the call to `CFXFloor::Move` (`0x4220cb`) follows it unconditionally (it
  returns only when the floor object `DAT_004b9bc4 + 0x960` is absent), so every active
  character at home is moved through the floor on each animation tick, with a zero delta when
  idle (pushed out to its radius from walls, y smoothed onto the floor). `FUN_00447270`, when
  actor 3 holds a character: the entry placement (`FUN_00448250`) only when `+0x2c8` is 1;
  then, when the character's `+0x2d4` is 0, its position and orientation from actor 3's copy
  and the request 5 (reset to clip 0) on every entry; home = the scene if active; the view is
  the saved `+0x280` on the first entry (`+0x2c8` 0), else 0; then `+0x2c8` = 1. So a new
  game's start clip `[0x434]` (Grumpa 0x20) is reset to the idle on entry.
- **Method:** decompile (control-flow outline of the read-only listings).
- **Confidence:** proven (the meaning of the character's `+0x2d4` not read)

### E-0831 — The engine walks (dev checks); the face test's sign holds for every entry point
- **Binary/file:** `games/grumpa/discs/cab/Scenes/*.scn` (`tools/parsers/scn.py`); engine
  `walk.cpp`, `character.cpp`; scenario `engines/grumpa/tests/walk.toml`.
- **Evidence:** corpus: with the edge function `(q.x − p.x)(z − p.z) − (q.z − p.z)(x − p.x)` over
  (v1, v0), (v2, v1), (v0, v2) all > 0 (E-0800), all 268 entry points of the 110 `.scn` files
  lie on a face of their scene's floor; the opposite sign finds none. Of 205 entry/return-exit
  pairs, 22 put the player's sphere inside the exit on arrival (scene 211 from 1: 204 units
  from an exit of radius 197, Grumpa's sphere 30), which E-0818's entry latch covers. Dev run
  `walk.toml` (-d1 `where`): scene 1, left held below Grumpa: N2W then W2W (clip 2), he moves
  (116.9, 206.3) → (244.1, 115.0) along the hut's back wall, release → W2N, idle at
  (253.6, 93.4); scene 211 entered from 1: placed at the entry (1031.4, 1712.4), floor type 1
  selects view 1, no bounce; walked out of the exit sphere and back: "exit to scene 1", scene
  1 entered, Grumpa at its entry from 211. Grumpa's `[0x28c]`, `[0x5fc]`, `[0x290]` = 25, 125,
  30.
- **Method:** corpus script; scripted dev run.
- **Confidence:** proven (corpus); verified (engine)

### E-0832 — Save version 4 keeps the characters; older saves place the player at the first entry
- **Binary/file:** engine `saveload.cpp`, `character.cpp` (`Characters::syncState`, `enter`);
  scenario `engines/grumpa/tests/walk.toml`; `tools/savecompat.py`.
- **Evidence:** the original keeps the characters with the global actors in `global.abi`
  (docs/spec/save.md, mode 4), and the first entry after a load does no entry placement
  (E-0804, E-0830), so the player's place must come from the save. Version 4 appends per
  character position, yaw, home, active, visible. Dev run `walk.toml`: Grumpa walked to
  (228.5, 141.0) in scene 1, saved, taken to scene 211, loaded: back in scene 1 at
  (228.5, 141.0), then walks on (clip 2). `savecompat.py grumpa`: the archived version-3
  saves (generations d432d9f6, 63dc2d19, scene 61) load without error; Grumpa now stands at
  scene 61's first entry, and his floor type selects that view, so their snaps differ from
  the version-3 references (46 %), as intended.
- **Method:** scripted dev runs.
- **Confidence:** verified (engine)

### E-1300 — `CFXCharacter` scene status: what Serialize mode 4 reads (mode 5 writes)
- **Binary/file:** `CFXCharacter::Serialize` `0x422f80` (`case 4` read arm, `case 5` write arm;
  reads through `FUN_004026c0`, writes through `FUN_00402220`); state slot Serialize read arm
  `0x409107` (one u32 at slot `+0x104`); `FUN_004100c0` SaveGlobalGameStatus (`"%s\Current\global.abi"`,
  every actor 0..599 through `vtable[1]`, error `"CFXActorFactory::SaveGloba..."`),
  `FUN_0040fdb0` LoadGlobalGameStatus (reads `u32 id` then `actor[id]->vtable[1]` to EOF);
  `FUN_00421780` (equip / unequip a carried object).
- **Evidence:** mode 4 reads, in order: `active [0x10c]`, `visible [0x110]`; each state slot's
  value (the existing vector `+0x11c`, stride 0x118, one u32 each, E-0407); home scene
  `[0x444]`; position `[0x16c]` f32×3; orientation `[0x160]` f32×3; texture index `[0x440]`;
  `u32 n [0x344]` (the carried-object count) and n × u32 from the array `[0x39c]`; the
  disable latch `[0x46c]` (set by opcode 0xd, cleared only by 0x34, E-0403). Mode 5 writes
  `id [0x108]` first, then the same fields in the same order (so a status record is
  `{u32 id, mode-4 body}`); for Grumpa 10 (6 carried objects) the body is 4 × (2 + 6 + 1 + 3 +
  3 + 1 + 1 + 6 + 1) = 96 bytes. `[0x39c][i]` is the "object i is worn" flag:
  `FUN_00421780(i, on)` clears the other worn object of its group (group {0, 5} or {1..4}),
  subtracting its bonus, then sets flag i and adds the bonus — `[0x38c+4i]` to state slot 3
  (`+0x11c → +0x44c`) for objects 0 and 5, `[0x37c+4i]` to slot 2 (`+0x334`) for 1..4. So the
  slots carry the equipment bonuses and the flags say which carried objects are worn.
  **Not kept:** the current clip / frame, the request queue, the talking flag `+0x67c`, the
  current scene `[0x448]` (rebuilt by the entry broadcast 0x17), the floor/walk fields
  `[0x28c] [0x290] [0x48c] [0x490]`, and nothing of the mesh object (no call into it; its role
  `+0x564` from 0x2c..0x30/0x54 is lost). Characters (ids 10..88) are global actors (< 600),
  so they go to `global.abi`, not a scene's status file.
- **Method:** decompile (`0x422f80` defined in memory, read-only project; not in the dump).
- **Confidence:** proven for the field order and the global file; the save/load functions'
  mode arguments (5 / 4) follow from the id being written by mode 5 and read by the loader.

### E-1220 — Actor 4 (type 0x17) is `CFXFollower`: layout, vtable, Serialize
- **Binary/file:** `CreateActor` case 0x17 (`operator new(0x298)` = count word + one 0x294-byte
  object), ctor `FUN_004349a0`, dtor `FUN_00434a90`, vtable `0x4906f4`: [1] Serialize
  `0x4351e0`, [2] device `0x434af0` (error string `CFXFollower::Initialize`), [4] Update
  `0x435080`, [6] DoCommand `0x434c50`. 0x4351e0/0x434af0/0x434c50 are not functions in the
  project; decompiled after defining them in memory (read-only project).
- **Evidence:** fields: type `+0x104` = 0x17, active `+0x10c` = 1, visible `+0x110` = 1,
  orientation `+0x144` (yaw `+0x148`), position `+0x150`, a copy of the character's 0x110-byte
  block `+0x15c..+0x26c` (`FUN_00434bc0`, from the character's `FUN_00424e90`; ctor puts 60.0
  at `+0x26c`), step direction `+0x270..+0x278`, place-on-entry flag `+0x27c` = 1, turn-freeze
  countdown `+0x280` = 0, update divider `+0x284` = 0, last request state `+0x288` = −1, entry
  scene `+0x28c`, held character id `+0x290` = −1 (getter `FUN_004354d0`, setter
  `FUN_004354c0`). Serialize mode 6 (`.atx`) reads two integers (global2.atx `<23>`: 4, 16)
  and, if `+0x290` then names a character, sets that character's role (`+0x118`→`+4`→`+0x564`)
  to 2; mode 7 writes two. Save (mode 4) writes active, visible, position (12), orientation
  (12), character; load (mode 5) reads the id `+0x108` first, then the same.
- **Method:** decompile; vtable and constants read from `GRUMPA.EXE`.
- **Confidence:** proven (which two fields mode 6 fills is inferred from the file, 4 = id,
  16 = character, since the reader calls lost their arguments).

### E-1221 — CFXFollower::Update: every second update, walk/run/stop toward the player
- **Binary/file:** `0x435080` → `FUN_00434b70` (character position `+0x16c` → `+0x150`),
  `FUN_00434b20` (character orientation `+0x160` → `+0x144`), `FUN_00434dd0` (the rule);
  player position from actor 3 `FUN_00446ac0`; acos `FUN_0047c9f0` (argument checked in the
  disassembly at `0x434e57`); floats `0x4906ec` π, `0x490718` 170, `0x4904a4` 100,
  `0x49063c` 70, `0x490494` 4, `0x490458` 0.5.
- **Evidence:** nothing happens unless `+0x290` names an existing character. `+0x284` counts
  updates; on the second it resets to 0 and the rule runs (so every 40 ms). With F the
  follower's character position and P the player character's: d = (F.x−P.x, 0, F.z−P.z)
  normalised, heading = acos(d.z), negated when d.x < 0; turn = π + heading − yaw(`+0x148`)
  (the relative turn to face the player). If `+0x280` > 0, turn = 0 and `+0x280` −= 1.
  dist = full 3D |F−P|. dist > 170: request 1 (run, E-0813) with turn, state `+0x288` = 1;
  100 < dist ≤ 170: request 0 (walk) with turn, state 1; dist ≤ 100: request 2 (stop) with
  turn only if state ≠ 2, then state 2. Then, if dist < 70: u = (F−P)/|F−P| (3D); the
  character is moved to (F.x + 4·u.x, F.y, F.z + 4·u.z) (`FUN_004250a0`), given request 0 with
  turn + π·0.5, state 0, and `+0x280` = 20 (turn frozen for 20 rule runs).
- **Method:** decompile + disassembly.
- **Confidence:** proven

### E-1222 — CFXFollower::DoCommand and scene-entry placement
- **Binary/file:** `0x434c50`, entry `FUN_004350d0`, step `FUN_00435430`, character
  `FUN_0041fd70`, `FUN_004250e0`, `FUN_00425fc0`.
- **Evidence:** forwarded unchanged to the held character's DoCommand (dropped when none):
  0..3, 0xb..0xd, 0x32..0x36, 0x48, 500, 501. **0x17** (scene entry, `arg1` = scene):
  `+0x28c` = scene; if `+0x27c` == 1, the follower takes the player's position and
  orientation (actor 3 `ac0`/`a70`) and steps −20 along the player's yaw (x += −20·sin yaw,
  z += −20·cos yaw, y unchanged): 20 units behind the player; else `+0x27c` is set back to 1
  and the stored position/orientation (last copied from the character) is kept. Then the
  character is placed there (position, orientation `+0x160` = `+0x144`), gets request 5
  (reset to idle), and if active (`+0x10c` == 1) its home `+0x444` = the scene; then
  `FUN_0041fd70` (if home == scene and a global `+0x960` flag is set: clears `+0x44c/+0x450/
  +0x454` to −1 and the per-state slot flags, request 5 again); finally `+0x280` = 0.
  **0x23**: `arg1` ≠ 0 → `+0x27c` = 0 (skip the next entry placement, one-shot), 0 → 1.
  **0x37** (release): if holding, the character gets DoCommand(1, 0, 0) (deactivate), role
  `+0x564` = 0, `FUN_00425fc0` (rebuilds its `+0x640` list; effect opaque), and `+0x290` = −1;
  then if actor 95 (type 0x1c, global2.atx) exists and is active, its `+0x2bc` = 0.
  Everything else is ignored.
- **Method:** decompile.
- **Confidence:** proven

### E-1223 — Character opcode 0x2d makes the character the follower; 0x48 queues a voice slot
- **Binary/file:** `CFXCharacter::DoCommand` `FUN_0041e0d0` (cases 0x2d, 0x32/0x33, 0x48),
  `FUN_00425cc0`.
- **Evidence:** 0x2d: only if actor 4 exists and holds no character (`+0x290` == −1): actor
  4's `+0x290` = this character's id, home `+0x444` = current scene `+0x448`, active and
  visible = 1, role `+0x564` = 2; otherwise ignored (no replacement, unlike 0x2c). 0x32/0x33:
  sent on to actor 8 (score) as (op, `arg1`, this character's id), so a score Life ± with
  `arg2` −10/−11 travels score → actor 3/4 → its character → score with the character id,
  and lands on that character's slot 1 (`docs/spec/score.md`). 0x48 `arg1` = n (`FUN_00425cc0`, 0..99):
  sound slot n of the character's table `+0x324` (loaded on demand, `FUN_0041f2b0`); ignored
  if n is already queued; n < 60 and n ≠ 32 plays at once; otherwise n is appended to the
  speech queue `+0x3d0` (count `+0x3fc`) and, if it is the only entry and the speaker is not
  already talking (mesh `+0x67c` == 0), plays now and marks talking. So 63/64 are queued
  voice lines of the companion/player.
- **Method:** decompile.
- **Confidence:** proven

### E-1224 — Role 2 in the character update: nothing follower-specific; others are pushed off
- **Binary/file:** character update `0x421a60` (`0x4223ff..`), `FUN_0044c6e0` (volume
  overlap), follower block `FUN_00434bc0`.
- **Evidence:** the update reads `+0x564` in three places: clip sounds (role ≠ 0 → the clip
  number goes through `FUN_00425cc0`), when the `+0x480` countdown set after request 4 (die) ends, roles 3/4/5 tell actors 0xb1/0xb2/
  0xb3 op 0x47), and role 0. Role 2 has no branch of its own: the following lives entirely in
  actor 4. A role-0 character overlapping the player's volume (actor 3 `b10`) or the
  follower's copied volume (`+0x15c`) is moved 4 units away from that character horizontally,
  then given request 0 with turn π·0.5 and request 2 (a shuffle aside).
- **Method:** decompile.
- **Confidence:** proven for the branches; `FUN_0044c6e0`'s exact test not read.

### E-1740 — The idle fidget: counter `+0x4a8`, 11 idle cycles, queue 0x1f then 0x20 (looping)
- **Binary/file:** character update `0x421a60` (clip-change block, labels near `0x421def`, `0x421e51`; decompile
  lines 102..217); ctor `0x41c9b0` (sets `+0x4a8` = 0); spawn `FUN_0044b120` (sets it to 9).
- **Evidence:** the counter is `+0x4a8` and is touched only at a clip boundary: when the frame
  `+0x494` reaches the clip's frame count it goes to 0 and the queue front becomes the clip
  `+0x434` (previous in `+0x438`); the front is popped only when the queue holds more than one
  entry, so the last entry repeats. Then: new clip == 0 → counter + 1 (and `+0x178`, `+0x160`,
  `+0x168` zeroed); any other clip → counter = 0. If counter > 10 (unsigned, i.e. the 11th
  consecutive start of clip 0): when slot 0x1f is loaded (`[+0x2dc]+0x7c` non-zero) the queue
  is emptied and 0x1f, 0x20 are pushed (count 2); the counter is set to 0 either way. No
  rand(), no threshold variation, no 0x21: 0x21 is queued only by a request from 0x20 (E-0813).
  So the 11th idle cycle plays out, then 0x1f once (popped, counter 0), then 0x20 repeats
  forever until a request. The clip-start hook (`FUN_00425cc0`) is skipped when 0x20 follows
  0x20. Requests (`FUN_0041fde0`) never touch `+0x4a8`; request 5 sets clip 0 directly, so it
  does not count. Same code for every character (no player test); characters without slot
  0x1f just reset. A spawned character starts at 9: it fidgets after 2 idle cycles.
- **Method:** decompile (`notes/decomp/GRUMPA.EXE__FUN_00421a60.c`), grep of the dump for `0x4a8`.
- **Confidence:** proven

### E-1620 — The "talking flag" is the speaker's state slot 5; only conditions read it (Q-0401)
- **Binary/file:** CFXSound play `FUN_00448f70` / stop `FUN_00449040`; character speech queue:
  push `FUN_00425cc0` (op 0x48), pump `FUN_00425780` (last call of the character update
  `FUN_00421a60`), flush `FUN_00425980`, stop-all `FUN_00425950` (character op 0x60,
  `FUN_0041e0d0`); `FUN_00408ff0` returns `actor + 0x118` (the state-slot vector); sound
  is-playing `FUN_00449f80`.
- **Evidence:** the written address is `[slotvec.begin] + 0x67c` with begin = `actor+0x11c`
  (stride 0x118, value at +0x104, E-0201): 5 × 0x118 + 0x104 = 0x67c, so it is the value of
  **state slot 5** of the speaker character, not a mesh field (corrects E-0405's wording).
  A grep of the whole dump for `0x67c` finds only these four writers/one test (`FUN_00425cc0`
  tests it == 0 before starting a queued line); no animation, mesh, render or input code reads
  it. Play: if `[0x3ac]` speaker > 0 and the actor exists, `FUN_00425980(speaker)` runs (only
  when the speaker is not in the current scene, `+0x444 != +0x448`: stop the sound at the
  front of its speech queue `+0x3d0` and empty the queue), then slot 5 = 1. Stop
  (`FUN_00449040`, also used by op 0x60 on all 100 slots) sets slot 5 = 0 for a speaker > 0.
  Pump, each frame step of an active at-home character (after the 0.46 accumulator, E-1312):
  if the queue is non-empty and the front slot's sound has stopped (`FUN_00449f80` = 0: buffer
  not playing or `[0x1a0]` = 0), pop it, slot 5 = 0, and if another entry remains, play it
  and slot 5 = 1. Corpus (`tools/logic.py`): slot 5 is read by 31 conditions, all
  `c16 Sharlakanskraken[5]==0`, always together with `[4]==2`, on companion hint sounds
  (`so645 003_sch_beware_cannonbal`, `010_sch_snake`, ...) and walk-in proximity triggers
  660..673: a new companion line starts only when he is not already talking.
- **Method:** decompile, grep of `notes/decomp/all` for `0x67c`; corpus condition listing.
- **Confidence:** proven

### E-1400 — Combat stance (Ctrl) and the attack hit timer of actor 3
- **Binary/file:** actor 3 update `0x446f70` (`0x4470a9..0x447119`), `FUN_004473c0`,
  set cursor kind `FUN_004461a0`; floats `0x490640` 0.6.
- **Evidence:** each actor-3 animation tick (0.46 clock), after the steer angle: when the
  character's clip-start counter `+0x43c` (incremented by the character update each time a
  clip starts) differs from actor 3's copy `+0x2b0`: if the new clip `+0x434` is 0x12..0x14
  the hit timer `+0x2b4` = trunc(F × 0.6), F = the clip's frame count `+0x498`; if it is 0x17
  (hit) the timer = 0 (an attack interrupted by a hit never lands); the copy is updated.
  Then, if the timer > 0 it is decremented, and on reaching 0 the hit test `FUN_00446db0`
  runs (once per attack clip; the setting tick counts as the first). Ctrl (0x11) up →
  stance `+0x2c4` = 0 (cursor not touched); Ctrl down and the character has clip slot 0x12
  (`+0x2dc` table `+0x48`) → cursor kind 7 and stance = 1. Space jump needs stance 0. In
  stance, button events (`FUN_004473c0`) never walk: left held → random 0x12 + rand()%3
  only while the clip is 0 or 0x20; right held → request 0x15; no left and the clip is 2 or
  5 → request 2 (stop, run before the right-button test).
- **Method:** decompile; disassembly of the `__ftol` operand (`FILD [+0x498]`, `FMUL [0x490640]`).
- **Confidence:** proven

### E-1401 — The player's hit test `FUN_00446db0`: actors 91..94, 140 units, facing dot < −0.8
- **Binary/file:** `FUN_00446db0` (`0x446db0..0x446f6x`); `FUN_00430b40` (type 0x1c actor →
  its character id `+0x2a0`); floats `0x490644` 140.0, `0x490650` −0.8 (double), `0x49045c` 0.
- **Evidence:** for actors 91, 92, 93, 94 (table offsets 0x16c..0x178) that exist and whose
  character id is not −1 and exists: d = actor 3's copy of the player's position
  (`+0x150/+0x154/+0x158`) − the character's `+0x16c..+0x174`; if the **3D** length < 140:
  u = normalize(dx, 0, dz) (from the target towards the player), f = normalize(sin yaw, 0,
  cos yaw) with yaw = actor 3's copy `+0x148`; if u·f < −0.8 (the target within ≈ 36.9° of
  the player's forward) → `FUN_00425730(target char, attacker = actor 3's character id,
  damage = the player character's state slot 2 value)`. `+0x11c` is the state-slot array
  (stride 0x118, value at +0x104, E-1300), so `+0x21c/+0x334/+0x44c/+0x564` are slots
  1/2/3/4: damage is slot 2 (attack strength incl. the worn objects 1..4 bonus), not a clip
  or mesh value. Several targets can be hit by one swing; no sound here.
- **Method:** decompile; disassembly at `0x446e4d..0x446e9e` shows the y component stored 0.
- **Confidence:** proven

### E-1402 — Taking damage: `FUN_00425730`, score op 0x33, hit clip 0x17
- **Binary/file:** `FUN_00425730(target, attacker, damage)`; score DoCommand `FUN_004397a0`
  case 0x33.
- **Evidence:** `FUN_00425730` always stores the attacker id in the target's `+0x488` (the
  type 0x1c controller `FUN_0042ff50` reads it to pick whom to chase). Then, if the target's
  slot 1 (Life, `+0x21c`) >= 0 and n = damage − target slot 3 (defence, `+0x44c`) > 0 and
  actor 8 exists: actor 8 DoCommand(0x33, n, target id). Score 0x33 with a character id:
  that character's slot 1 −= n; if it is still > 0 the character gets request 0x17 (N2H2N,
  then idle); if the character is the current form the score's Life is reduced too (star 1,
  `SX_scare`, `docs/spec/score.md`). No invulnerability timer: every swing that passes the
  hit test and beats the defence costs n.
- **Method:** decompile.
- **Confidence:** proven

### E-1403 — Block and death in the character update `0x421a60`
- **Binary/file:** `notes/decomp/GRUMPA.EXE__FUN_00421a60.c` (clip-start block and the
  per-tick tail after the floor move).
- **Evidence:** at each clip start: new clip 0x15 → slot 3 (defence, `+0x11c → +0x44c`) += 5;
  previous clip `+0x438` was 0x15 → slot 3 −= 5 (so +5 defence exactly while N2D2N plays);
  new clip 0x17 → `+0x474` = 1 and `[DAT_004ba74c + 0xc] + 0x11c` = 0 (Q-1400). Each
  animation tick: if slot 1 (Life) < 1 and `+0x47c` == −1: `+0x4ac` (turn steps) = 0,
  request 4 (clips 8 N2D, 0xc D2D), and if clip slot 8 exists `+0x47c` = its F and `+0x480` =
  F + 20. `+0x47c` counts down per tick and at 0 runs `FUN_00425e30` (not read, Q-1400);
  `+0x480` counts down and at 0: active `+0x10c` = 0, visible `+0x110` = 0, home `+0x444` =
  −1, both timers −1, `+0x478` = 0; except characters 0x13, 0x38, 0x40, 0x45, 0x50: home =
  current scene `+0x448`, visible = 1, `+0x478` = 1 (the body stays). Roles 3/4/5 then
  message actors 0xb1..0xb3 (E-1224).
- **Method:** decompile.
- **Confidence:** proven for the order; `FUN_00425e30` and `+0x474/+0x478` meaning open.

### E-1700 — Worn attachments: the table's three u32, and how Draw places them
- **Binary/file:** `CFXCharacter::Draw` `FUN_004226a0` loop `0x422761..0x42295c`;
  `FUN_00421780` (SetWorn); Serialize `FUN_00422f80` (`0x4231f0` arm, attachment reads);
  lazy loader `FUN_0041f2b0` (attachment meshes `+0x34c` from names `+0x3ac` by
  `FUN_004157d0`, class ctor `FUN_00415140` sets frame `+0x11c = 0`; textures `+0x35c` from
  `+0x3bc`); mesh helpers `FUN_00415310` (copy vertex), `FUN_004166e0` (draw current frame),
  `FUN_00416680` (advance frame); matrix helpers `FUN_0043d990` (identity), `FUN_0043d8c0`
  (rotation from (pitch, yaw, roll) via `FUN_00473e71`), `FUN_0043d910` (translation),
  `FUN_0043d960` (rotation + translation), `FUN_0043d840` (4x4 product A·B); `FUN_0047c9f0`
  = `acos` (CRT `_CIacos`: `fpatan(sqrt(1-x²), x)`, error name "acos" at `0x4b61c0`);
  constant `0x49045c` = 0.0. `Actors/Characters.abi` record 10; `Meshes/*Grumpa*.ANB`.
- **Evidence:** per attachment entry the three u32 are `[0x36c][i]` = a **face index** of the
  body mesh, `[0x37c][i]` = the weapon bonus SetWorn adds to state slot 2 (`+0x334`),
  `[0x38c][i]` = the shield bonus added to slot 3 (`+0x44c`) (E-1300). Names go to the
  vectors `+0x3a8` (.ANB) and `+0x3b8` (.tga). Grumpa (id 10), from the corpus:
  0 `000_IO_Shield` (593, 0, 20), 1 `001_IO_FathersSword` (592, 10, 0), 2 `002_IO_Hammer`
  (592, 8, 0), 3 `003_IO_SwordOfMight` (592, 20, 0), 4 `004_IO_FathersSwordBroken`
  (592, 6, 0), 5 `005_IO_WoodenShield` (593, 0, 5); textures `00k_IT_<same>.tga`. All 26 of
  Grumpa's clips have 594 faces (592/593 are the last two). Draw, after building the
  character matrix (yaw-pitch-roll of `+0x160`, translation `(x, y + [0x178], z)` of
  `+0x16c`) and before the body, for each i with worn flag `[0x39c][i] == 1`: takes the
  current clip's mesh (`+0x2dc[+0x434]`), reads the index buffer's first index of face
  `[0x36c][i]` (ushort at `+0x10c + 6·face`, `0x42279f..0x4227ad`) and copies that vertex of
  the clip's **current frame** (`+0x108 + ((frame·nverts) + index)·0x20`; pos f32×3, normal
  f32×3 at +0xc). pitch = acos(ny), negated when nz < 0; yaw = 0, except for i = 0 or 5 (the
  shields): yaw = acos(ny), negated when ny < 0 (`0x4227f5..0x42281f`; it tests ny again, not
  nx). Local matrix = rotation (yaw, pitch, roll 0) with translation = the vertex position;
  world = local · character matrix (`0x4228a3`), `SetTransform(WORLD=1, ...)` (`0x4228c1`),
  texture `+0x35c[i]`, draws mesh `+0x34c[i]` at its frame `+0x11c`, which nothing but the
  constructor (0) ever sets (only `FUN_0041f2b0`, `FUN_0041fc20` and Draw touch `+0x34c`),
  so the attachment is static, frame 0. No clip, swim or boat test: any worn flag draws.
  The loader (`FUN_004157d0`, `0x41611a..0x416641`) builds one GPU vertex per UV slot: the
  index buffer holds the faces' UV indices (sections concatenated, offsets added), and each
  slot gets the position/normal of the position vertex its corners name (the last corner
  writing a slot wins), per frame.
  Worn flags start 0 (SetDevice zeroes `[0x39c]` with `[0x35c]`); only SetWorn and the
  status load (mode 4, E-1300) change them.
- **Method:** decompile + capstone disassembly of `0x42276b..0x42295c`; corpus run of
  `tools/parsers/abi.py` / `anb.py`.
- **Confidence:** proven for the rule; acos(ny) for the shield yaw looks like a slip for nx
  but is what the code does.

### E-1600 — Platforms: the 0x1a meshes `CFXFloor::Move` walks on (resolves Q-0810)
- **Binary/file:** `FUN_00433bb0` (Move, platform loop), `FUN_00433250` (face test on given
  arrays), `FUN_00433490` (height, platform branch), `FUN_004536e0` (0x1a → mesh `+0x1b0`),
  `FUN_00453990` (0x1a frame `+0x1c0`), `FUN_004157d0` (`.anb` load: `+0x108` vertex buffer,
  `+0x10c` indices, `+0x110` ΣB, `+0x114` ΣC), `FUN_00450f30` (0x1a DoCommand, opcode 0x17),
  `FUN_00432aa0` (vector push_back), `FUN_0040efa0` (broadcast loop), `FUN_00421a60` (call at
  `0x4220cb`), `FUN_00433010`, `FUN_0041fd70`, `FUN_004250a0`; `Meshes/*.anb`.
- **Evidence:** 1) The platform loop walks the floor's list `+0x148` by list index i; an entry
  counts when its actor exists and is **active** (`+0x10c` == 1); visibility (`+0x110`) is not
  tested. For each of the mesh's ΣC faces (`+0x114`, all sections together) it runs
  `0x433250` with the mesh's index array `+0x10c` (the face **uv-index** triples, offset by the
  section uv base) and its Direct3D vertex buffer `+0x108` (32-byte vertices, position first)
  with **no frame offset**: frame 0, raw model coordinates (no transform; the meshes are in
  world space). The point is pos + delta (x, z). `0x433250` is the floor's own face test
  (E-0800): inclusive x/z box, then edges (v1,v0), (v2,v1), (v0,v2) strictly > 0.0. The first
  hit (list order, then face order) stores the face in the floor's `+0x140` and in the
  caller's face, the **list index** i in the caller's platform, does pos += delta (all three
  axes), y = 0.4·y + 0.6·height, returns 1 (no wall slide on a platform). 2) The height on a
  platform is the y (byte 4) of buffer vertex `index[3·face + 0] + frame · ΣB`, frame = the
  0x1a's `+0x1c0` (current animation frame, unchecked against F): the face's first corner
  in the current frame, no blend. So the hit uses frame 0's footprint and the height follows
  the animation. 3) No hit: if a platform was set it becomes −1 and the face −1 (forcing the
  full face search of the static mesh). 4) The list: the 0x1a DoCommand on opcode 0x17 (the
  scene-entry broadcast, E-0202), when `+0x1d0` == 1 and actor 600 exists, pushes its own id
  (`+0x108`) onto `+0x148` (this corrects E-0803's "at device init"); the floor's own 0x17
  empties it. The broadcast walks the actor table from id 1 upward (`0x40efa0`), so the floor
  (600) clears before the 0x1a actors (711..715) add: after entry the list holds that scene's
  flagged 0x1a ids in ascending order. 5) The character (`0x421a60`) calls Move every update
  with platform `+0x454` and does nothing else with it but: the step check uses +80 instead of
  +20 when on a platform (y above old y + 80 → back to the old position and `0x4219f0(−2.0)`),
  and `0x433010` returns floor type 15 on a platform (≤ 18: never blocked; no other reader of
  15 there). No riding along in x/z: a moving platform only changes y (standing still, delta
  0 still runs the test and eases y toward the current frame's height). `0x41fd70` and
  `0x4250a0` (placement) reset face, platform and type to −1. Corpus: the 11 flagged meshes
  found (back1..3_hugg_IO, plattform, plattform_up, boardMesh, 117_Tunna_still_A..C,
  117_Walk_stigande_A..C) are one section each, and no uv index is shared by two vertices,
  so the uv-index triples equal the face vertex triples there.
- **Method:** decompile; corpus check with `tools/parsers/anb.py` (sections, faces, uv
  sharing); `ground.ANB`/`down.ANB` (scene 61) not found under `Meshes/` by those names.
- **Confidence:** proven

### E-1500 — Character opcodes 0x2e/0x2f/0x30/0x4b/0x54 are combat roles, not mounts
- **Binary/file:** `CFXCharacter::DoCommand` `FUN_0041e0d0` (cases 0x2e, 0x2f, 0x30, 0x4b,
  0x54), `FUN_00430960` (type 0x1c actors 91..95, take a character), `FUN_00447790`.
- **Evidence:** each needs its type 0x1c actor (0x2e → actor 91, 0x2f → 92, 0x30 → 93,
  0x4b → 94, 0x54 → 95; `DAT_004b9bc4 + 0x16c..0x17c`) and the character's slot 1 (life,
  mesh `+0x21c`) > 0. It calls `FUN_00430960(actor, own id, x)` with x = actor 3's character
  id (for 0x54: `arg1`), stores x in `+0x488` (the opponent), home `+0x444` = current scene,
  active = visible = 1, role `+0x564` = 3, 4, 5, 6, 7 respectively. `FUN_00430960`: if the
  actor already holds another character, that one gets queued op 1 and role 0; when the
  global fight counter `DAT_004c018c` goes 0 → 1 it broadcasts op 0x12d (301); counter += 1;
  actor `+0x2a0` = character, `+0x298` = opponent, actor active/visible = 1; then if actor 4
  holds a companion, actor 95 is inactive and the companion has clip slot 0x12 (attack),
  the companion is queued op 0x54 with `arg1` = this character (it fights it as role 7) and
  actor 4 lets go (`+0x290` = −1). Corpus: only 0x4b (75) occurs in scene data, sent to 34,
  35, 37, 38, 55 (rat leaders, hyena boss); 0x2e/0x2f/0x30/0x54 come from elsewhere (0x54
  from the code above). 0x2c also queues `(8, 0x55, own id)` to the score (E-0704).
- **Method:** decompile; corpus sweep with `tools/events.py` `scenes()`.
- **Confidence:** proven (which code sends 0x2e..0x30 not located: Q-1500)

### E-1501 — Opcode 0x46 splits a rider form into Grumpa and the mount
- **Binary/file:** `FUN_0041e0d0` arm at `0x41ea1f..0x41eaef`; `FUN_004219f0`,
  `FUN_00421940`, `FUN_00426580`, `FUN_004265e0`, `FUN_0041f2b0`, `FUN_004261c0`.
- **Evidence:** only if kind `+0x128` == 2 and both parts `+0x13c` (rider, Grumpa 10) and
  `+0x140` (mount) name existing actors. Order: the form's active = visible = 0 (home and
  role untouched); the mount, then Grumpa, get DoCommand 0x47 with `arg1` = the form's id
  (each: placed at the form's position, move delta `+0x294` = 30·(sin yaw, 0, cos yaw) with
  its own yaw, orientation `+0x160..+0x168` copied from the form, home = current scene,
  active = visible = 1, role 0); both LoadResources (`FUN_0041f2b0`); d = |min x| over the
  vertices (32-byte records, first float) of the mount's current clip mesh (`FUN_00426580`,
  start FLT_MAX) + |max x| of Grumpa's (`FUN_004265e0`, start FLT_MIN); Grumpa's move delta
  is overwritten with the local offset (d, 0, 0) turned by his yaw: (d·cos yaw, 0, −d·sin yaw)
  (`FUN_00421940`, only if his slot-0 clip exists): he steps sideways by the two half-widths,
  the mount keeps the 30-unit forward step (deltas go through the floor Move on the next
  tick, E-0814); then Grumpa gets DoCommand 0x2c (E-0816: the form, still held by actor 3,
  is queued op 1 and role 0; Grumpa becomes actor 3's character, role 1; score gets
  `(8, 0x55, 10)`: Life and icon switch to Grumpa); finally `FUN_004261c0(form)` walks the
  form's `+0x650` command list (copies only; effect opaque). Disassembly: mount = `ebx`
  first 0x47 at `0x41ea82`, Grumpa `edi` at `0x41ea93`, fabs/fadd at `0x41eaab..0x41eaba`,
  vector (d, 0, 0) at `0x41eac2..0x41eacd`, 0x2c at `0x41eade`.
- **Method:** decompile + capstone disassembly of `GRUMPA_NOCD.EXE`; floats `0x4904c4`
  3.4e38, `0x4904c8` 1.2e−38.
- **Confidence:** proven

### E-1502 — Mounting is scripted; the pair list `+0x12c` is only loaded and saved
- **Binary/file:** whole `.text` of `GRUMPA_NOCD.EXE` scanned (capstone) for `[reg+0x12c]`,
  `+0x130`, `+0x134`; Serialize `FUN_00422f80`, dtor `FUN_0041d320` (`0x41dab0`); scene data.
- **Evidence:** in the character class the vector `+0x12c` (first `+0x130`, last `+0x134`,
  8-byte entries) is touched only by the ctor (`0x41c9e7`), Serialize (`0x424160..0x424bbc`)
  and the destructor (`0x41dab0`); no other code compares kind `+0x128` (only DoCommand 0x46
  and actor 3's Backspace test). No proximity mount exists. Scenes mount by commands: scene
  20 `(3,0xc)(3,3)(12,0xb)(12,2)(12,0x2c)` (Grumpa off/hidden via actor 3, dragonfly rider 12
  on, shown, made the player), scene 40 the same with 10 and 13 (bear), scene 73 with 10 and
  88 (seahorse). Scene 101 dismounts by script: `(12,0xc)(12,3)(21,0xb)(21,2)(10,0xb)(10,2)
  (10,0x36,101)(21,0x36,101)(10,0x2c)` (no 0x46), the boat form 11 the same with 27. Op 0x46
  (70) in data only resets forms on scene entry: `(13,70)(13,0x36,s)(28,0x36,s)...` in many
  scenes (8, 10, 12, 16, 20, 21, 25, ...).
- **Method:** disassembly scan; `tools/events.py` corpus sweep.
- **Confidence:** proven for the code; the positions of a scripted mount come from the
  form's own state (scene data or Characters.abi), not from this code.

### E-1503 — Backspace in actor 3's update; mount movement uses the same code
- **Binary/file:** actor 3 update `0x446f70` (Backspace block after Shift), character update
  `0x421a60`, `FUN_0041fde0`; Characters.abi `[0x48c]`, `[0x490]`.
- **Evidence:** on each animation tick, if GetAsyncKeyState(8) is non-zero (no edge latch;
  any non-zero result) and actor 3 holds a character: if its kind `+0x128` == 2 it is sent
  0x46 at once (direct DoCommand, not queued), else, if actor 4 exists, actor 4 gets 0x37
  (release the companion, E-1222). So holding Backspace on a mount dismounts on the first
  tick and, Grumpa then being the held character, releases the companion on the next.
  Movement: neither `FUN_0041fde0` (request table, E-0813) nor the update reads `+0x128`;
  rider forms walk through the same requests, with clip slots from their own `.anb` list.
  The difference is data: mode `[0x48c]` 1 for boat 11 and boat 27 (only type-13 water
  faces walkable, y −0.5, E-0803), 2 for dragonfly 12 and 21, 0 for 10, 13, 28, 87, 88;
  radius group `[0x28c]/[0x5fc]` 50/250 (11), 30/150 (12, 13), 25/125 (10, 88), 90/450 (27);
  `[0x490]` 1 only for Grumpa 10.
- **Method:** decompile; Characters.abi read with `tools/parsers/abi.py` (offsets of `t_03`).
- **Confidence:** proven

### E-1430 — Actors 91..95 (type 0x1c) are `CFXFighter`: layout, vtable, Serialize, engage
- **Binary/file:** `CreateActor` case 0x1c (`operator new(0x2c4)`, ctor `FUN_0042f980`), vtable
  `0x490618`: [1] Serialize `0x430810` (error string `CFXFighter::Serialize`), [2] device
  `0x42fb20` (`CFXFighter::Initialize`), [4] Update `0x430790`, [6] DoCommand `0x42fcb0`. Engage
  `FUN_00430960`, release `FUN_00430a60`, held-character getter `FUN_00430b40`; character
  opcodes in `CFXCharacter::DoCommand` `FUN_0041e0d0` (cases 0x2e, 0x2f, 0x30, 0x4b, 0x54).
- **Evidence:** fields: type `+0x104` = 0x1c, active `+0x10c`, visible `+0x110`, orientation
  `+0x144` (yaw `+0x148`) and position `+0x150` copied from the character (`FUN_0042fb80`,
  `FUN_0042fbd0`), sphere block `+0x15c` (`FUN_0042fc20`, as the follower's), dist `+0x288`,
  target position `+0x28c..+0x294`, target character id `+0x298` (−1), clock `+0x29c`, held
  character `+0x2a0` (−1), scene `+0x2a4`, hit countdown `+0x2a8`, last seen clip-start count
  `+0x2b4`, companion flag `+0x2bc` (ctor 1; scene entry 1; follower release 0x37 sets 0, E-1222).
  Serialize mode 6 reads two integers (global2.atx `<28>`: id 91..95, character −1). Engagement
  is by character opcodes sent to the enemy character: **0x2e** → actor 91 role 3, **0x2f** →
  92 role 4, **0x30** → 93 role 5, **0x4b** → 94 role 6 (target = actor 3's held character,
  the player); **0x54 `arg1`** → actor 95 role 7 with target `arg1`. Each only if that actor
  exists and the character's life (state slot 1, `+0x11c → +0x21c`) > 0; then the character's
  last attacker `+0x488` = the target, home `+0x444` = current scene, active and visible = 1,
  role `+0x564` = 3..7. Engage (`0x430960`, no-op when already holding that character): a
  previously held character gets DoCommand 1 and role 0; if the global fighter count
  `DAT_004c018c` was 0, actor 301 gets DoCommand 0; count += 1; hold, target, active, visible
  set. Then if actor 4 holds a character, actor 95 is inactive and that character has clip slot
  0x12 (`+0x2dc` entry +0x48 non-null), the follower's character gets opcode 0x54 with the new
  enemy's id (it becomes actor 95, the fighting companion) and actor 4's `+0x290` = −1.
- **Method:** decompile (functions defined in a private copy of the project); vtable read from
  `GRUMPA.EXE`.
- **Confidence:** proven (which two fields mode 6 fills is inferred from the file).

### E-1431 — CFXFighter::Update: the enemy AI rule (approach, taunt, attack, separation)
- **Binary/file:** Update `0x430790`, rule `FUN_0042ff50`, hit test `FUN_00430680`; floats
  `0x4904a0` 0.46, `0x49034c` 1.0, `0x490614` π, `0x49064c` 280, `0x490648` 180, `0x490644`
  140, `0x49063c` 70, `0x490494` 4, `0x490640` 0.6 (at `0x4301e9`), `0x490650` double −0.8 (at
  `0x43073c`); acos `FUN_0047c9f0` of d.z (`0x430085`); rand `FUN_0047cce7`; sphere test
  `FUN_0044c6e0`; place `FUN_004250a0`.
- **Evidence:** Update: only when active and the held character exists; `+0x29c` += 0.46 and
  when > 1.0 it drops by 1.0, the character's position and orientation are copied and the rule
  runs. Rule, C = held character, T = `+0x298`: stop if either is −1 or C's life ≤ 0. If T's
  life > 0 and T visible: (a) if T is inactive and the player's character p (actor 3 `+0x298`)
  is valid, ≠ T and active: T = p, end. (b) T = C's last attacker `+0x488` (initially the
  player); P = T's position. d = (F.x−P.x, 0, F.z−P.z) normalised; heading = acos(d.z),
  negated when d.x < 0; turn = π + heading − yaw. dist = 3D |F−P| → `+0x288`. dist > 280:
  request 1 (run) with turn; 180 < dist ≤ 280: request 0 (walk); 140 < dist ≤ 180: request
  0x23/0x24/0x25 (`.anb` 35..37, S05..S07) by rand()%3. dist ≤ 140 and C has started a new
  clip since the last decision (C `+0x43c`, incremented at every clip start, ≠ `+0x2b4`): if
  C's current clip `+0x434` is an attack 0x12..0x14, `+0x2a8` = trunc(clip frames `+0x498` ×
  0.6); if it is 0x17 (hit), `+0x2a8` = 0; then rand()%6: 0 → request 2 (stop), 1 → 0x23,
  2 → 0x24, 3/4/5 → attack 0x12/0x13/0x14, all with turn; `+0x2b4` = C `+0x43c`. dist < 70:
  C is moved to F + 4·u (u = (F−P)/|F−P| 3D; x, z only, y kept). For each actor 91..95 other
  than itself holding a character whose sphere overlaps C's: C moved 4 units away from it the
  same way; the same against actor 4's character. Last, if `+0x2a8` > 0 it counts down and on
  reaching 0 the hit test runs: if dist < 140 and the horizontal unit vector (F−P) dotted with
  the fighter's forward (sin yaw, 0, cos yaw) < −0.8 (target within about 37° in front), the
  target takes a hit (E-1432) with attack = C's state slot 2 (`+0x11c → +0x334`). If T is dead
  or not visible: actors 91..94: T ≠ 10 → T = 10 and C `+0x488` = 10 (go for Grumpa), end;
  T = 10 → C request 2 (stop), T = −1. Actor 95: if the count > 1, T = the held character of
  the first active actor of 91..94 (also into C `+0x488`), end; none and T ≠ 10 → T = 10, end;
  else stop and T = −1.
- **Method:** decompile + disassembly (capstone) of the float operands.
- **Confidence:** proven

### E-1432 — Taking a hit: damage = attack − defence, sent as Life minus to the score
- **Binary/file:** `FUN_00425730(victim, attacker id, attack)`; callers `FUN_00430680` (enemy
  hits), `FUN_00446db0` (the player's hits, E-0811).
- **Evidence:** victim `+0x488` = attacker id (so a fighter's character re-targets whoever
  last hit it). If the victim's life (slot 1) ≥ 0 and damage = attack − victim's slot 3
  (`+0x11c → +0x44c`, defence; the player's block clip 0x15 adds 5 to it, E-0811) is > 0,
  actor 8 (score) gets DoCommand(0x33, damage, victim id): a Life minus on that character
  (E-1223, `docs/spec/score.md`). No clip is requested here (no hit-reaction request).
- **Method:** decompile.
- **Confidence:** proven

### E-1433 — Death of a fighter's character and the release; scene change and entry
- **Binary/file:** character update `0x421a60` (decompile lines 340..352), `FUN_00425e30`,
  release `FUN_00430a60`, fighter DoCommand `0x42fcb0` (cases 0x17, 0x19); 0x19 is broadcast
  by `FUN_0040e980` before the scene is changed (then `FUN_0040cb30` loads the new one).
- **Evidence:** character update: life ≤ 0 and `+0x47c` == −1 → turn steps `+0x4ac` = 0,
  request 4 (die: 8 then 0xc); if clip slot 8 is loaded, `+0x47c` = its frame count and
  `+0x480` = that + 20. `+0x47c` counts down each update; at 0 `FUN_00425e30` posts every
  command of the death list `+0x630` (ClassC records) and, for role 3..7, releases fighter
  91..95. `+0x480` reaching 0 resets `+0x47c/+0x480` to −1 and other state. Release: count −=
  1; hold, target = −1, active, visible = 0; count 0 → actor 301 DoCommand 1. If actor 95 is
  active and the count is now 1 (only the companion left): its character gets opcode 0x2d (back
  to follower, E-1223) when 95's `+0x2bc` == 1, else role 0 and the released actor's `+0x2bc`
  = 1; count = 0; actor 301 DoCommand 1 (actor 95 itself is not cleared). Fighter **0x19**
  (leaving the scene): actor 301 DoCommand 1; actor 95 active: same 0x2d/role-0 hand-back,
  then cleared; actor 94 active: character request 5, role 0, fighter cleared; 91..93 holding:
  character request 5, active = 0, visible = 0, home −1 (`FUN_004250e0`), role 0, fighter
  cleared; count = 0. **0x17** (entry, `arg1` scene): `+0x2bc` = 1, actor 301 DoCommand 1,
  `+0x2a4` = scene; 91..93 holding: request 5, inactive, home −1, fighter cleared. 0..3,
  0xb..0xd, 0x32..0x36, 500, 501 go to the held character's DoCommand; others are ignored.
- **Method:** decompile.
- **Confidence:** proven

### E-1720 — The cursor's pictures: kind = picture slot; load, draw, colour key, top-left hotspot (resolves Q-0900)
- **Binary/file:** CFXMouse (factory type 2, ctor `FUN_00444930`, vtable `0x490820`: load
  `0x444b60`, draw `0x445570`, update `0x445440`, message `0x446210`); CFXSprite (vtable
  `0x4908ec`, ctor `0x44c800`, create-from-file `0x44ed90`, position `0x44da00`/`0x44e0d0`,
  size `0x44dfd0`, colour key `0x44e1a0`/`0x44e100`/`0x44e1b0`); constants `0x490848` = 2.6,
  `0x490844` = 0.3925, `0x49081c` = π; `UI/002_Cursor/002_Cursor.atx`.
- **Evidence:** the mouse owns an array of 25 sprites (`+0x12c`, stride 0x318), indexed by
  the kind `+0x130`. Load reads four ints (`2 1 1 9` in the file), then the nine names into
  slots 1..8 and, for the ninth (`arrow1_.tga`), the name cut at its first `'1'` and
  formatted `%s%s%d_.tga` for 1..16 into slots 9..24 (loop `0x1bd8..0x4d58`). Slot 0 is
  unused. Each picture: CreateFromFile loads `<base>0000.<ext>`, `0001`, … while files exist
  (up to 100 frames); colour key COLORREF −1 = the colour of pixel (0,0) of the first frame,
  set as the source colour key on every frame; slots 1..8 also get `+0x10c` = 1 (arrows only
  `+0x110`). Kinds: 1 default, 2 grabing, 3 pointpush, 4 pull, 5 push, 6 stop, 7 attack,
  8 itemglitter, 9..24 arrow1_..arrow16_. Draw (when `+0x110` visible): kind −1 nothing;
  kind 0 = the held item's (`+0x140`) icon sprite (item `+0x134`); else slot[kind]; placed
  with its top-left at the mouse point `+0x158/+0x15c` (dest rect = point .. point + size:
  the hotspot is the top-left corner). While `+0x14c` > 0 slot 8 (itemglitter) is drawn too,
  at mouse − (16,16); `FUN_00446330` sets it to 10, the update counts it down. Arrow kind
  each update (only while kind is 9..24 and actor 3 exists): 9 + trunc(angle × 2.6 −
  0.3925), angle = `+0x154` (E-0817) in 0..2π, so straight below the player = 9 + 7
  (arrow8_), above = arrow1_/arrow16_. No kind 25 exists; PlayerControl (`FUN_004473c0`)
  treats kinds 9..25 as "walk cursor" (an off-by-one bound, harmless).
- **Method:** decompile (dump + `def_and_decomp.py` for `0x444b60`, `0x446210`); constants
  read in PyGhidra.
- **Confidence:** proven (mapping, placement, key); the frame timing is Q-1710.

### E-1721 — Who sets the cursor kind
- **Binary/file:** `FUN_00446130` (set kind unless 0), `FUN_00446150` (hold item / −1),
  `FUN_004461a0` (hover kind), mouse update `0x445440`, message `0x446210`, call sites
  `0x447145`, `0x4591ec`, `0x45922e`, `0x438c00`, `0x43e0f1/0x43e101`, `0x43e19e/0x43e1ad`.
- **Evidence:** **Hold** (`FUN_00446150 n`): `+0x140` = n, hover timer 0; n = −1 → kind 9
  (walk arrow); else kind 0 (the item's icon) and the item gets State 6. **Hover**
  (`FUN_004461a0 k`, ignored while an item is held): on the first hover the current kind is
  saved (`+0x138`, flag `+0x134`), kind = k, timer `+0x160` = 8; the update counts the timer
  down and at 0 restores the saved kind. So a hover kind lasts while it is re-sent every
  update and reverts 8 updates after the mouse leaves. Senders: a type-0x19 trigger under
  the mouse → 2 (`0x4591ec`, `0x45922e`, constant push 2: triggers carry no cursor field);
  an item in reach → 2 (E-0900); the inventory panel: over the panel 1, over a filled slot
  2 (`0x438c00`); PlayerControl: Ctrl held (GetAsyncKeyState 0x11) and the character armed
  (`+0x48`) → 7 attack (`0x447145`). Panel open/close (`0x43e0a0`, `0x43e160`): hold −1
  then kind 1 (default pointer). Message 0x23: drop held, kind 9; 2/3 show/hide; 0x1a puts
  the system cursor on the player. A click while holding arms `+0x144` = 16 (`0x445660`);
  16 updates later, if no handler took it (`+0x148` 0), an item still in State 6 is dropped
  (`FUN_0043c340`) and kind = 9. No code found that sets kinds 3..6 (pointpush, pull, push,
  stop) by constant; `sword_*` and `attack_ready_*` files are not in the cursor's list.
  PlayerControl walks only while the kind is a walk arrow (9..25).
- **Method:** decompile; disassembly of the SafeDisc-broken call sites (PyGhidra).
- **Confidence:** proven for the listed setters; kinds 3..6 unused is a search result
  (call sites of the three setters), not a proof (Q-1710).

### E-1530 — Character opcodes 1, 0x37, 0x47, 500, 501; actor 3 starts holding Grumpa
- **Binary/file:** `CFXCharacter::DoCommand` `FUN_0041e0d0` (cases 1, 0x37, 0x47, 500, 501),
  actor 3 Serialize `FUN_004474e0` (case 6), `Actors/global2.atx` blocks `<22>`, `<23>`.
- **Evidence:** character **op 1** is the request 2 (stop, `FUN_0041fde0(this, 2, 0.0)`), not a
  deactivation (supersedes "op 1 (deactivate)" in E-0816, E-1222, E-1500, E-1501: a released
  or replaced character stops walking and stays active and visible). **501**: active =
  visible = 0, then the stop. **500**: active = visible = 1, the per-state slot flags cleared,
  request 5. **0x37**: sent on to actor 4 as (0x37, `arg1`) — the follower releases its
  character. **0x47 `arg1`**: placed at actor `arg1`'s position, a pending move of 30 along
  its own yaw (`FUN_004219f0`, applied by the next tick's floor Move), orientation copied from
  that actor, home = current scene, active = visible = 1, role 0 (supersedes the "position
  only" reading of E-0403). Actor 3 Serialize mode 6 reads two integers and, if `+0x298` then
  names a character, sets its role `+0x564` to 1, as the follower's (E-1220): `global2.atx`
  `<22>` holds 3, 10 and `<23>` holds 4, 16, so a game starts with actor 3 holding Grumpa 10
  (role 1) and actor 4 holding the Scharlakanskraken 16 (role 2); Characters.abi has 16
  active and visible at home in scene 1 (97, 35, 238), beside Grumpa (117, 35, 206). Actor 3's
  save (mode 4) writes its held character `+0x298` last (after `+0x280`), the follower's
  (E-1220) its `+0x290`.
- **Method:** decompile (dump `notes/decomp/GRUMPA.EXE__FUN_0041e0d0.c`, `_004474e0.c`);
  global2.atx read; Characters.abi through `parsers/abi.py`.
- **Confidence:** proven (the two mode-6 fields inferred from the file, as E-1220).

### E-1460 — Character reactions: storage, trigger test, once per approach, re-armed on scene entry
- **Binary/file:** `CFXCharacter::AddReactCharacter` `0x4254c0`, `CFXCharacter::FindReaction`
  `0x425300`, `CFXCharacter::PostReaction` `0x4250f0`, `CFXCharacter::GetReactionCommands`
  `0x4258f0`, `CFXCharacter::ResetReactions` `0x41fd70`, the update `0x421a60` (call at
  `0x421afa`), `FUN_0044c6e0` (sphere overlap), `FUN_00422670` (present), Serialize `0x422f80`.
- **Evidence:** AddReactCharacter appends a fresh command vector to `+0x614` (begin `+0x618`)
  and an 8-byte entry {u32 other id, u32 fired = 0} to `+0x608..+0x610`, same index; the
  file's CC-vec (E-0401) fills that vector. The update (only when active `+0x10c` and at home
  `+0x444 == +0x448`, and only on the frames where its `+0x4a4` accumulator passes 1.0, E-1307)
  calls `0x425300`; if it returns 1 with an id ≠ −1, `0x4250f0` looks up that id's vector
  (`0x4258f0`, first entry with the id) and pushes every command, in order, onto the global
  queue with its conditions (`0x408760` at `0x4252b4`, E-0617). `0x425300` returns 0 at once
  if the character's state slot 4 (role, `+0x11c → +0x564`) is 7, its life (slot 1,
  `+0x21c`) < 1, or a dying countdown `+0x480`/`+0x47c` is > 0. Otherwise it walks the entries
  in file order and returns the first that fires. For each: the other actor is
  `DAT_004b9bc4[id]`; if its type (`+0x104`) is 3 it must be present (`0x422670`: visible
  `+0x110 == 1` and at home `+0x444 == +0x448`); if 5 (item) its scene `+0x288` must equal this
  character's `+0x448` and its state (vtable +0x1c) be 4. Then the spheres must overlap
  (`0x44c6e0`: centre distance < r1 + r2): this one centred on its position `+0x16c` with y
  raised by `[0x290]`, the other on its position with y raised by `[0x600]` (Serialize copies
  `[0x290]` there, `0x422f80`), both radius `[0x5fc]` (the 2nd float of E-0401's
  `[0x28c],[0x5fc],[0x290]` group). `+0x624` is 1 from the constructor and never written
  again, so the "once" path always runs: an entry fires (fired = 1, id also stored in `+0x62c`)
  only when fired was 0; an entry whose other is absent, not overlapping or of another type
  gets fired = 0 (re-armed). `0x41fd70` (from DoCommand 0x17 scene change `0x41e6ff` and the
  follower's scene entry `0x4351cf`): when the character's home is the new scene and actor 600
  (walk mesh, `DAT_004b9bc4+0x960`) exists, it sets `+0x44c/+0x450/+0x454 = −1`, clears every
  fired flag and requests idle (5).
- **Corpus:** Characters.abi (script over `parsers/abi.py`): 40 reacts to 10, 13, 88 each with
  one command (−1, 40, 0x2f, 0, 0), radius 450; 44 to 10, 13, 88 with (−1, 44, 0x30, 0, 0),
  450; 82 to 10, 13, 88 with (−1, 82, 0x2f, 0, 0), 450. Also 39/41/43/81/83/85 (ops 0x2e..0x30,
  radius 450). Many others react with 0x48 (sound 61/65/66/67), 0x4b or 0x2d. Radii of the
  reacted-to: 10 → 125, 13 → 150, 88 → 125 (so 40 engages Grumpa 10 at < 575).
- **Method:** decompile (dump), disassembly of `0x4251f0..0x4252d0` (the push the decompiler
  dropped), byte scan for call sites, corpus script.
- **Confidence:** proven (static); not traced.

### E-1800 — Actor 2's State (slot 0) mirrors the cursor kind; `2[0]==2` = the grab hand
- **Binary/file:** CFXMouse update `0x445440` (the write, after the hover-timer restore and
  before the picture step), setters `FUN_00446150`, `FUN_004461a0` (E-1721).
- **Evidence:** every update (while `+0x10c` is set) the mouse copies its kind `+0x130` into
  its own slot 0 (`+0x11c` → value `+0x104`), except that the walk-arrow kinds 9..24 are
  written as 1. No other mouse function writes slot 0. So actor 2's State is: −1 before any
  kind is set, 0 an item held (its icon is the cursor), 1 the default pointer or a walk
  arrow, 2 the grab hand (hovering a type-0x19 trigger, an item in reach or a filled panel
  slot), 7 attack (Ctrl, armed character); 3..6 never set (Q-1710). Hover is ignored while
  an item is held, so State 2 implies no item on the cursor, and the 8-update hover timer
  keeps it at 2 across a click. The 16 corpus conditions `(2, 0, 2, 0, link)` therefore mean
  "clicked while the cursor shows the grab hand, nothing held" (e.g. a trigger click with
  bare hands), not a generic plain click. The value lags the kind by up to one update
  (the mouse, actor 2, updates first).
- **Method:** decompile (dump).
- **Confidence:** proven (static).

### E-1801 — Condition list: an absent actor is skipped without touching the running state
- **Binary/file:** `FUN_00408c30` (E-0201).
- **Evidence:** when `actor[id]` is null the entry is skipped entirely: the result, the
  previous result and the previous link stay as they were (refines E-0201's "unchanged").
  Two edge effects follow from the state starting at result 0 / previous result 0 /
  previous link 0: if the absent actor is entry 0, entry 1 is judged as an AND continuation
  of a false group (it can never be true on its own); and the actor id recorded for the
  "last tested is an item" step (E-0206) is set before the null check, so a list that comes
  out true with an absent actor as its last entry dereferences a null actor (`+0x104`) in
  the original.
- **Method:** decompile (dump).
- **Confidence:** proven (static); neither edge case checked in the corpus.

### E-1802 — Scene links: only walls in scenes 5, 7 and 21 gate an exit; scene 58's ship hotspot sits behind its walls
- **Binary/file:** `Scenes/Scene_*.scn` (walk mesh 0x08, links 0x14), `Scenes/Scene_058.abi`.
- **Evidence:** `engines/grumpa/tools/walkplan.py reach` floods each entry's walk-mesh region
  over shared edges with the closed wall types 19..21 left out, and tests the exit spheres. In
  all 110 scenes every exit is reached from every entry except: scene 5 (wall 19 between the
  exits to 6 and 212: the banana guard, trigger 664 `OPENWALL(0)`), scene 7 (wall 19 between
  the exit to 10 and those to 8/309: the roots, trigger 660), scene 21 (entry from 69 walled
  in until wall 19 opens). In scene 58 the nearest vertex of the open region to trigger 660's
  sphere `(538, 419, 504) r150` (the ship's hull, `GOTO 101`) is 238 units away with the walls
  closed and 40 with all open; the only `OPENWALL` reaching scene 58 is the Giant Octopus's
  death list (`Characters.abi` c80 list 2: `@58 600.6(0)`). The walkthrough's map rests on this.
  Player sphere radius taken as 60 (a guess).
- **Method:** corpus statistic (`walkplan.py reach`, `--selftest`).
- **Confidence:** proven for the mesh topology; the sphere radius is approximate.

### E-1803 — Grumpa's strength slot and the two "strength > 15" hotspots
- **Binary/file:** `Actors/Characters.abi` (c10), `Scenes/Scene_018.abi`, `Scene_109.abi`,
  `Scene_061.abi`, `Scene_009.abi`, `Actors/global.atx`.
- **Evidence:** c10's six state slots start `(32, 100, 5, 2, 1, 0)`; by the opcodes
  0x58/0x5a (slot 2 / 3 += arg1, characters.md) slot 2 is the one the cork (109 trigger 661)
  and the Sword of Might (61 trigger 663, 9 triggers 666/667) test with `c10[2] > 15`.
  Scene 18 trigger 665 (the Gauntlets of Power, a click) sends `c10.88(11)` and `c10.90(2)`:
  5 + 11 = 16 > 15. Scene 37 trigger 664 (the Belt) sends `88(11)` as well, the Grandfather
  (global 243) `88(20)`, and c10's own list with g223 JungleMixture `88(11)` (the potion).
  So one of them suffices for the cork; the gauntlets are the nearest (jungle island).
- **Method:** corpus (`tools/logic.py`).
- **Confidence:** proven from data; slot 2 = attack strength is a reading (combat Q-0806).

### E-1804 — The ending: Captain c69's death list, scene 96, and the ship's order
- **Binary/file:** `Actors/Characters.abi` (c69), `Scenes/Scene_102.abi`, `Scene_109.abi`,
  `Scene_096.abi`.
- **Evidence:** c69 (home 102, inactive, life 400) has list 2 `@96 940.56(1)`, `GOTO 96`;
  Grumpa's (c10) list 7 is `@96 941.56(1)`, `GOTO 96`. Scene 96's script 781 plays film 620
  `grumpa_outro.mpg` and `end_succesful_VS.wav` when flag 940 = 1, film 621
  `grumpa_death.mpg` and `096_end_VS.wav` when 941 = 1; its exit leads to scene 1. Scene 102
  walk-in trigger 660 (active in the file, sphere r615 around the deck entry) plays the
  captain's line, whose end activates and shows c69. Scene 109 trigger 661 (the cork) defers to
  102: trigger 660 on (11), the hold door 661 and the way back 662 off (13), and plays the
  cork mesh whose end list plays film 620 `unplug.mpg` of scene 119 and goes there. 102's sound
  642 (`102_ratbeard_final_VS.wav`, the same ending) is started by no command in the corpus.
- **Method:** corpus (`tools/logic.py`).
- **Confidence:** proven from data; whether 660, latched after its first firing, can be
  re-armed by the cork's 11 depends on the latch rule (events.md: only 52 clears it).

### E-1805 — In-scene films are type-0x07 actors in four scenes
- **Binary/file:** `Scenes/Scene_500.abi`, `Scene_096.abi`, `Scene_119.abi`.
- **Evidence:** the type-0x07 records' strings are the four `.mpg` films: scene 500 actor 620
  `grumpa_intro.mpg` (its list: `GOTO(1, -1)`), scene 96 actors 620 `grumpa_outro.mpg` and
  621 `grumpa_death.mpg` (lists: `1.60(1)`, the main menu), scene 119 actor 620 `unplug.mpg`
  (list: `player.2`). They are started by opcode 0 (scene 96 script 781, scene 109 cork mesh
  712's end list). No other record names a film.
- **Method:** corpus (`tools/logic.py`, 0x07 names).
- **Confidence:** proven from data.

### E-1404 — Requests from a clip with no row keep the queue; a dying character takes none (corrects E-0813)
- **Binary/file:** `FUN_0041fde0` (character request), the inner `default:` arms of requests 0,
  1 and 3 and the outer `default:`; guards before the switch.
- **Evidence:** for requests 0 (walk), 1 (run) and 3 (jump) the inner switch on the clip
  playing (`+0x434`) has `default: return` (to `0x420fc7`'s return label): from a clip with no
  row the queue `+0x404` is **not** cleared and nothing is pushed (E-0813's "every other request
  clears the queue" holds only for the rows). The outer `default` (requests outside 0..4,
  0x12..0x15, 0x17, 0x1f..0x28, e.g. 5) clears the queue and pushes 0. Before the turn aim and
  the switch (after the request-5 reset block): return when the character has no clip in slot
  0, and when its death timer `+0x47c` > 0 (dying characters take no request and no turn).
  Consequence: a fighter waking from S02 (0x20 → 0x21 queued) is not stuck re-clearing its
  queue by the run/walk requests it repeats every tick.
- **Method:** decompile.
- **Confidence:** proven

### E-1531 — The engine follows, mounts and splits (scenario `follow`)
- **Binary/file:** engine `character.cpp`, `events.cpp`, `score.cpp`, `walk.cpp` (branch
  grumpa-a2); scenario `engines/grumpa/tests/follow.toml`; scene data through `tools/events.py`.
- **Evidence:** scenario `follow` (-d1 `who`): scene 6 entered from 1, the companion 16 placed
  at (−95.4, −700.0), 20 behind Grumpa (−95.5, −677.1, yaw 0); after Grumpa walks to
  (−44.0, −536.8) it follows and stops 77 away (clip 0). Scene 40, trigger 661 (as the scene
  does: `(10,0xc)(10,3)(13,0xb)(13,2)(13,0x2c)`): 13 is the player (role 1) at its
  Characters.abi place, 10 inactive and hidden; Backspace: 13 inactive and hidden, the bear 28
  at (561.1, 1054.6) and Grumpa 10 at (638.2, 1072.8) beside it, Grumpa the player (role 1),
  the companion running to him. Commands to actor 3 now reach Grumpa, so scene data that stops
  him through actor 3 takes effect: scene 211's entry script 781 sends (3, 0xc) and (4, 0xc)
  and the end list of sound 656 (3, 0xb), (4, 0xb); scene 1's walk-in triggers 664/665 the
  same with sounds 644/646 (player control returns when the companion's line ends).
- **Method:** scripted dev runs; corpus sweep.
- **Confidence:** verified (engine)

### E-1640 — Character sound slots and the speech queue (ops 0x48, 0x60; completes E-1223, E-1620)
- **Binary/file:** `CFXCharacter::LoadResources` `FUN_0041f2b0` (sound loop after the clips),
  `CFXSound` ctor `FUN_004484d0`, load `FUN_00449900`, play `FUN_00448f70`, stop `FUN_00449040`;
  `QueueSound` `FUN_00425cc0`, `PumpSpeechQueue` `FUN_00425780`, `StopAllSounds`
  `FUN_00425950`, `FlushSpeechQueue` `FUN_00425980`; callers: update `FUN_00421a60` (clip-start
  hook, last call = pump), `DoCommand` `FUN_0041e0d0` (0x17 → flush, 0x48, 0x60);
  `Actors/Characters.abi` (the file the game loads, characters.md), `notes/logic.txt`.
- **Evidence:** LoadResources runs once (guard: clip slot 0 of `+0x2dc` empty) and puts each
  `.wav` of the list `+0x330`/`+0x338` at slot `atoi(name)` (`FUN_0047c0ce`) of the 100-slot
  table `+0x324`, like clips (E-0815): a new `CFXSound` (fresh ctor: speaker `[0x3ac]` = 0, loop
  `[0x1a4]` = 0, volume/pan flags 0, no command list), SetDevice, then loaded from
  `"%s%s"` = `<data>\Sounds\` + name; on load failure the slot stays 0. So a character sound has
  speaker 0: playing or stopping it never touches any slot 5; only the queue code writes the
  owner's slot 5. QueueSound(n): n outside 0..99 ignored; if slot n is empty, LoadResources
  (no-op once loaded); n already anywhere in the queue → ignored; n < 60 and n ≠ 32 → play slot n
  (if loaded) and return: no stop first, and play only sets `[0x10c]`/`[0x1a0]` and calls the
  DirectSound buffer's Play without rewinding, so a slot already playing just continues. Else n
  is appended to the `std::deque<uint>` at `+0x3d0` (count `+0x3fc`; no capacity limit, the
  deque grows) even when the slot is empty; if the count is now 1, the slot is loaded and the
  owner's slot 5 is 0, it plays and slot 5 = 1. Pump (end of the update, which returns earlier
  unless active `+0x10c` and home `+0x444` == current scene `+0x448` and the animation step is
  due): front slot loaded and not playing → pop, slot 5 = 0, play the new front if any (and
  loaded) with slot 5 = 1. An empty front slot is never popped. Flush (scene entry op 0x17 for
  every character, and play of a speaker-tagged scene sound): only when home ≠ current scene:
  stop the front's sound (no commands) and empty the queue; slot 5 is left as it was. Op 0x60:
  stop (no commands) each of the 100 slots; the queue is not touched, so the next pump pops the
  stopped front and starts the next line. Corpus: op 0x60 (96) is sent nowhere; op 0x48 (72) is
  sent 204 times (178 to characters, 26 via actors 3/4), every n ≥ 60 (so scripts always queue): to characters directly n 60..67, to
  actor 4/actor 3 (forwarded to the held character) n 63 (9) / 64 (17). Slots below 60 come
  from the clip-start hook (clip number n, the character's slot-4 value ≠ 0; else a global
  sound `DAT_004ba764[n]`): 001/004 walk, 018 attack, 023 hit, 032 tired (queued: n = 32).
  Pairs sent but with no file in `Actors/Characters.abi`: (16,61), (21,61), (28,60),
  (30..32,60): these entries sit at the queue front unplayed and block that character's queue
  until a flush. Example: scene 7 trigger 662 (walk-in, once, sphere (19,−57,495) r405) sends
  actor4.72(64), and player.72(64) when riding c12/c13: the companion's
  `064_CS_*_rightway_VO.wav`.
- **Method:** decompile (`notes/decomp/all/`), `tools/logic.py` + a list of the `.wav` names
  per record of both Characters.abi files.
- **Confidence:** proven

### E-1750 — Engine runs: worn attachments, cursor pictures, the fidget, save version 5
- **Binary/file:** engine `scene.cpp` (`drawAttachments`, `setCursorImage`,
  `updateHoverCursor`), `walk.cpp`, `character.cpp` (`wear`, `update`, `syncState`),
  `saveload.cpp`; scenarios `engines/grumpa/tests/items.toml`, `cursor.toml`, `fidget.toml`,
  `equip_save.toml`; `tools/savecompat.py`.
- **Evidence:** `items`/`equip_save`: the panel puts 100 (Father's Sword, broken) and 134
  (Wooden Shield) in the equipment slots: worn bits 0x30, slots 2/3 go 5 → 11 and 2 → 7
  (the bonuses 6 and 5 of E-1700); the shield is drawn on his left arm, the blade by his right
  hand, as the tutorial card shows him. Saved, a new game, loaded: the same position, worn
  0x30, slots 11/7, both drawn. `cursor`: with Grumpa at screen (555, 215) the mouse below
  gives `arrow8_`, right `arrow4_`, above `arrow1_`; the panel shown `default`; an item taken
  `*134` (its icon). `fidget`: idle in scene 1, Grumpa is in slot 0x20 (S02) looping by update
  320, and a hold walks him out (clip 2). `savecompat.py grumpa`: the four archived
  generations (versions 3 and 4) load.
- **Method:** scripted dev runs (`grumpa_vm`, `where`, `cursor`).
- **Confidence:** proven for the engine; the attachment placement against the original's
  pixels is not compared (no capture of the original).

### E-1806 — Type 0x07 is `CFXCutScene`: a full-screen DirectShow film that pauses the game; Space or the film's end stops it and runs its list
- **Binary/file:** factory `FUN_0040d2f0` case 7 (`new 0x25c`, ctor `0x429aa0`, vtable `0x4904f0`:
  [1] Serialize `0x429d40`, [2] SetDevice `0x429c40` (error `CFXCutScene::Initialize(IFXDire…`),
  [3]/[4] render/update empty `0x4761b0`, [6] DoCommand `0x429c70`); play `FUN_0042afc0`, stop
  `FUN_0042b2c0`, run list `FUN_0042b3e0`, surface-renderer graph `FUN_0042aae0`; window
  procedure `FUN_00410cb0` (`0x8001`/`0x8003`/`0x8004`, `WM_KEYDOWN` 0x20); factory tick
  `FUN_0040e980`; boot `FUN_00436aa0` (`"%s\Movies"` into `0x4b9edc`); `CFXView::DoCommand`
  `0x45ad40`; `CFXSound::DoCommand` `0x448a40`; `Scenes/Scene_{096,119,500}.abi`.
- **Evidence:** **Fields:** Serialize mode 1/2 reads id `+0x108`, `+0x10c`, `+0x110`, the
  condition vector, `+0x114`, the name (`+0x144`), `+0x13c`, then 19 u32 into a stack local
  (discarded), then the command list `+0x248` (0x128-byte entries); save mode 4 keeps `+0x10c`,
  `+0x110`, `+0x13c`, `+0x140`. `+0x114` and the 19 u32 are read by no method of the class.
  **DoCommand:** 0 play, 1 stop, 23 (scene entry) play when `+0x13c = 1`; all three only while
  `+0x140 = 0`; 13 sets `+0x140 = 1` (disabled), 52 clears it; others ignored. Corpus: `+0x13c`
  = 1 only for scene 500's `grumpa_intro.mpg`, 0 for the 96 and 119 films (so the intro starts
  on entering scene 500 and nothing needs to send it 0). **Play:** broadcasts opcode 96 to every
  actor and runs the immediate list (characters stop their voice slots, E-1640; `CFXSound`
  ignores 96); builds `<Movies dir>\<name>` with `"%s\%s"`, the Movies dir being
  `<HKLM\SOFTWARE\Idol FX\Grumpa DataPath>\Movies` (no language folder; `0x42b105`
  pushes `0x4b9edc`); `CLSID_FilterGraph` `RenderFile`, the video window owned by the game
  window, `WS_CHILD`, 800×600 at the origin; notify window message `0x8001` with
  `lParam = 0x10000 | id`; when the device reports bit 0 (`device vtable+0x58`) it first tries
  a graph with its own surface renderer (`0x42aae0`) and on success fills the window black.
  Either way the fade actor 185 is set to full brightness at once (`FUN_0042f290(185, 0)`, no
  fade-out before), actor 0's `+0x10c`/`+0x110` are set 0, message `0x8003` sets the
  film-playing flag `0x4ba724`, and the graph runs. While actor 0's `+0x10c = 0` the factory
  tick only `Sleep(1)`s: no update, no render, no timers. **Input** while the flag is set:
  mouse messages and Escape are ignored (every arm requires `0x4ba724 = 0`); **Space**
  (`WM_KEYDOWN` 0x20) calls stop. A graph event `EC_COMPLETE` (1) or `EC_USERABORT` (2) on
  `0x8001` calls stop too. **Stop** (only while a graph exists): `IMediaControl::Stop`, colour-
  fill the back surface black, message `0x8004` clears the flag, release the graph, actor 0
  `+0x10c`/`+0x110` = 1, push every command of `+0x248` with its conditions (`FUN_00408760`,
  run by the next update), send op 1 to actor 3 (stop the held character), and op 87 to actor
  602 (`CFXView`: `+0xdcc = 2`, full background redraw). So the list runs the same way whether
  the film ends or is skipped. Opcode 1 sent by a command is the same stop.
- **Method:** decompile (functions at `0x429aa0..0x429d40` are not defined in the project;
  created in a read-only headless session), disassembly at `0x42b0fa..0x42b110` and
  `0x42b578..0x42b58c`; corpus bytes after each film name.
- **Confidence:** proven (static); whether looping ambience stays audible over the film is open
  (Q-1802).

### E-1532 — The seahorse mount works end to end in scene 73 (scenario `seahorse`)
- **Binary/file:** engine `follower.cpp`, `character.cpp` (grumpa-a2); scenario
  `engines/grumpa/tests/seahorse.toml`; `Scenes/Scene_073.abi` trigger 660.
- **Evidence:** the role `+0x564` is the character's state slot 4 (value at `+0x104 + 4·0x118`,
  E-0407 stride), so 660's condition `c10[4] == 1` is "Grumpa is the player". Trigger 660:
  polygon (350,389)(205,372)(181,283)(231,224)(494,221)(504,286)(434,378), sphere (5.8, 3.9,
  −174.3) r 390; commands `(121,16,1)(710,13)(660,13)(10,0xc)(10,3)(88,0xb)(88,2)(88,0x2c)
  (8,79)(221,67)(220,67)`. Dev run: Grumpa walks from (579.7, −219.6) to (305.8, −59.8), the
  net (121) held, a click at (350, 300) fires 660: 88 is the player (role 1) at its
  Characters.abi place (81.9, −148.3), 10 inactive and hidden, the score shows the seahorse
  icon and no air bar; 88 rides to (−131.5, 307.3); Backspace: 87 at (−153.0, 343.0), Grumpa
  at (−89.7, 351.0), the player.
- **Method:** scripted dev run; `.abi` read through `tools/parsers/abi.py`.
- **Confidence:** verified (engine)

### E-1807 — 0x1a mesh: file order of the eight command lists (corrects E-0601)
- **Binary/file:** `CFXStaticCharacter` Serialize `FUN_00452100` (load case 1/2), advance
  `FUN_00453760`, contact tests `FUN_004539a0` (called from update `FUN_00450cc0`), list
  runners `FUN_004540c0`, `FUN_004543a0`, `FUN_004512a0`, `FUN_00451580`, `FUN_00451b40`,
  `FUN_00451860`, `FUN_00451e20`; corpus `notes/logic.txt`.
- **Evidence:** the load reads the eight lists (count, then 0x128-byte commands) in the field
  order `+0x12c`, `+0x13c`, `+0x14c`, `+0x15c`, `+0x17c`, `+0x18c`, `+0x19c`, `+0x16c`, so
  `+0x19c` is the 7th and `+0x16c` the 8th (E-0601's "8th +0x19c" is wrong). Runners: file
  1 `+0x12c` by `FUN_004540c0` (mode 0x10 forward end); 2 `+0x13c` by `FUN_004543a0` (mode
  0x10 backward end); 3 `+0x14c` by `FUN_004512a0` (bubble flag `+0x1bc` bit 1: actor 3,
  the player, touches); 4 `+0x15c` by `FUN_00451580` (bit 2: actor 4, or the character
  held by actor 95 via `FUN_00430b40`); 5 `+0x17c`: no reader found in the class (loaded
  only); 6 `+0x18c` by `FUN_00451860` (bit 8: the actor whose id is in `+0x228`); 7 `+0x19c`
  by `FUN_00451e20` (end of animation, modes 4/8/2 without loop); 8 `+0x16c` by
  `FUN_00451b40` (bit 0x10: any of the combat-role actors 91..94, `DAT_004b9bc4 +
  0x16c..0x178`, E-1500). Each contact test runs its list on entering contact, latched by
  `+0x1e4` and per-test flags `+0x234`/`+0x238`/`+0x23c`/`+0x240..`; op 14/15 `+0x1e0`
  gates all tests. Matches the corpus: L6 (7th) holds the end-of-animation scripts
  (Scene_211 lock_IO, Scene_109 Cork_Animated), L2 player damage/air, L7 enemy hits.
- **Confidence:** proven (static), agrees with corpus

### E-1660 — Water in code: floor types 12/13 with mode `[0x48c]`, the ripple, and no reader of types 1/2/3/8
- **Binary/file:** character update `0x421a60` (after the floor Move, `0x4220cb..0x42225x`),
  actor 3 update `0x446f70`, `CFXCharacter::Draw` `0x4226a0` (water branch `~0x422ab0..0x422c9f`),
  shared-mesh loader `FUN_00435a00`, `FUN_0041fd70`, `FUN_004250a0`; `.scn` corpus via
  `tools/walkplan.py` `load()`; `Meshes/*Grumpa*.ANB` listing.
- **Evidence:** after Move, in this order: face −1 / step limit as E-0803; floor type = the
  face's u16; **mode 1** (boat): y = −0.5 and the old y `+0x2a4` = 0; type > 18 and closed →
  back to old; **mode 1 and type ≠ 13** → back to the old position (y then 0): a boat moves on
  type 13 only; **type 13 and mode 2** (dragonfly): y = −0.5, old y = 0; then **on type 12 or
  13**: if the current clip `+0x434` is 0xf, 0x10 or 0x11 (N2J2N, W2J2N, R2J2N: the jumps, not
  swim clips) y = old y; on type 12 with mode 2 y = old y. Nothing else depends on 12/13 or
  the mode: no clip, request, root motion, turn or speed change (`FUN_0041fde0` reads neither
  `+0x450` nor `+0x48c`). Actor 3: Space (request 3, jump) is refused when the floor type is
  13; Shift, Ctrl and Backspace ignore the floor; types 0..4 select the view unless mode 1
  (E-0812). Draw (not dying, `+0x474` ≠ 1): on type 13, if y < −4.0 (`0x4904b4`) or mode 1, and
  the shared mesh 0 exists, it draws `Meshes/waterripple.ANB` at (x, 4.0, z) with uniform scale
  min(|y|·0.03 + 0.2, 1.0) (`0x4904b0`, `0x4904ac`, `0x49034c`), 1.5 for mode 1 (`0x4904a8`),
  its playback value `+0x13c` = 5 while the clip is 0 (idle), else 8; on any other type it
  draws the shadow (shared mesh 2, `Shadow.ANB`); type 13 with y ≥ −4 draws neither. Shared
  meshes (`FUN_00435a00`): 0 `waterripple.ANB`, 1 `watersplasch.ANB` (no user found in the
  dumps), 2 `Shadow.ANB`, 3 `effect.ANB`. Grumpa has no swim clip (none of its `.anb` names, slots 0..0x25,
  is one). Floor type readers: only `0x421a60` (12, 13, > 18, writes 15),
  `0x446f70` (0..4, 13), `0x4226a0` (13); `FUN_0041fd70`/`FUN_004250a0` only reset it to −1.
  So types 1, 2, 3 matter only as view numbers and **type 8 has no reader** (46 faces, scene 5,
  y 0.5..8.4). Corpus vertex y: type 13 −8179.7..67.2 (scenes 4, 12, 16, 17, 20, 30, 32, 35,
  50, 80..87, 100, 101), type 12 −606.6..233.9 (scenes 9, 114).
- **Method:** decompile (dumps `notes/decomp/`, `build/grumpa-anim-decomp/`); floats read from
  `GRUMPA_NOCD.EXE` with pefile; corpus script.
- **Confidence:** proven (static); `watersplasch` use and the ripple's `+0x13c` meaning open.

### E-1661 — Air and drowning are scripts; Life 0 kills in code
- **Binary/file:** `Actors/global.atx` timers 220 "Syretimer" and 221 "Slut Luft" (both 4,000
  ms); `Scenes/Characters.abi` char 88 (Grumpa on the seahorse); `notes/logic.txt`
  (`tools/logic.py`); score update `FUN_00439730`, DoCommand `FUN_004397a0`; `0x421a60`.
- **Evidence:** no code drains or refills Air: the score's update only animates its sprites
  and sounds, actor 3's update sends nothing to actor 8, and the character update tests only
  Life (slot 1 < 1 → request 4 die, E-1403). Scripts: char 88's list L1 (becoming the form)
  starts timer 220 and shows the air bar (score 78) unless Scene_ID is 12, 16, 20, 30, 50 or
  80; char 87's list L0 hides the bar (79) and stops 220 and 221. Timer 220 on expiry: Air
  > 0 → score 77 (Air −6) and restart 220; Air < 1 → stop 220, start 221. Timer 221 on expiry:
  Air < 1 → score 51 with (8, 0): Life −8 on the current form, restart 221; Air > 0 → restart
  220, stop 221. Refills are scene scripts: score 76 with 2, 10 or 100 (100 with 79 and stopping
  220 on surfacing). So underwater the seahorse loses 6 Air every 4 s (99 → 0 in 68 s), then 8
  Life every 4 s until Life < 1 runs the character's death (E-1403). Score ops: 76/77 Air ±,
  78/79 bar shown/hidden (E-0703).
- **Method:** corpus (`logic.py` dump, `global.atx` text); decompile of the score functions.
- **Confidence:** proven

### E-1680 — Which scenes run the air timer: entry scripts start, stop and refill it
- **Binary/file:** `Scenes/Scene_*.abi` scripts 780..782 (type 0x21, run on the entry broadcast
  23, E-0204); `Scenes/Characters.abi` c10 list 7, c87 list 0, c88 list 1; `notes/logic.txt`.
- **Evidence:** **start** (`220.66`, score 78 shows the air bar): 51, 53, 55, 56, 57, 58,
  70..74, 117, 118, 119. **Surface** (`220.67`, score 76(100), 79 hides the bar, `221.67`):
  12, 16 (script 781), 20, 80, 101, 114; the same **without `221.67`**: 30, 32 (782), 50,
  54 (782). **Stop only** (79, 221.67, 220.67, no refill): 1 (782), and 96 (220/221.67). No
  air command in 14, 301, 17 (the piranha pool is bites, `hud.51(4)`), nor in any other scene.
  Scene 73 trigger 660 (mounting the seahorse) and c87 list 0 hide the bar and stop 220/221
  without a refill. Conditions are evaluated when a command is pushed (E-0200), so a firing
  of 220 or 221 tests Air as it was before that firing's 77/51 is delivered: 220 at Air 6
  subtracts to 0 and restarts itself; the next firing (Air 0) stops 220 and starts 221. With
  Air 99: 17 firings of 220 (68 s) to Air 0, 4 s more to the first `Life −8`. Grumpa's death
  (c10 list 7) defers `941.56(1)` to scene 96 and goes there (E-1804: `grumpa_death.mpg`).
  Consequence of the four surface scripts without `221.67` (30, 32, 50, 54; 50 is entered
  from underwater 70, 54 from 53): entering one while drowning refills Air to 100 but leaves
  221 running; its next firing sees Air > 0 and restarts 220, so Air drains on dry land with
  the bar hidden (Q-1680).
- **Method:** corpus (`tools/logic.py` over all scenes, filtered on g220/g221/hud 76..79/51).
- **Confidence:** proven from data

### E-1681 — Air bubbles are 0x1a meshes whose contact spheres ride a vertex; player contact runs file list 3
- **Binary/file:** `CFXStaticCharacter` contact test `FUN_004539a0`, `CFXSphere::Overlaps`
  `FUN_0044c6e0`, ctor `FUN_0044fc60`; `Scenes/Scene_{051,055..058,071,118}.abi` (parsed by
  `tools/parsers/abi.py` `t_1a`).
- **Evidence:** the `+0x25c` vector the file stores as `count × (u32, u32)` holds the contact
  spheres (0x118 bytes each in memory): first u32 = vertex index (`+0x114`), second = radius
  as a float (`+0x110`; the corpus values 0x41500000/0x41a00000/0x41d80000 = 13, 20, 27).
  Every update the test sets each sphere's centre (`+0x104..+0x10c`) to that vertex of the
  mesh's current frame (32-byte vertices, x y z first) when the vertex and frame are in range;
  then, if `+0x1e0` = 1 (the ctor sets it to 1, ops 14/15 set/clear it), for flag bit 1
  (`+0x1bc`) it tests the player's sphere (actor 3's character, E-0705) against each sphere
  with the centre-distance-below-sum-of-radii test; on a hit, unless `+0x220` ≠ −1 and the held
  character differs, it runs file list 3 (`+0x14c`), once per contact when `+0x1e4` = 1
  (latch `+0x234`, cleared when not touching), and stops testing for that update. All 19
  bubble meshes (bubbla51_1..3, 55_1..3, 56_1..3, 58_1..3, 71_1..3, 118_1..3, bubblor_IO in 57)
  have flags 1, `+0x1e4` 1, `+0x220` −1, one sphere on vertex 0 (bubblor_IO: vertices 8 r13
  and 64 r20), and list 3 = `hud.76(n)`: +10 (51: +2; 71_3: +2). The bubble scenes 119 and
  117 have none; 53, 70, 72, 73, 74 none either.
- **Method:** decompile (dump `notes/decomp/all/004539a0_*.c`, `0044c6e0`, `0044fc60` line
  `[0x78] = 1`); corpus script over `t_1a`.
- **Confidence:** proven (static + corpus)

### E-1682 — Actor 601's slot 1 is "Scene ID", set by the entry broadcast
- **Binary/file:** `CFXToScene` ctor `FUN_00447920` (adds a slot named `"Scene ID"`,
  `s_Scene_ID_0049e604`), DoCommand `FUN_00447ba0`.
- **Evidence:** DoCommand handles only 0x17 and writes `arg1` to the value of state slot 1
  (`[+0x11c] + 0x21c` = `0x104 + 1·0x118`, the E-1532 slot stride). 0x17 = 23 is the scene
  entry broadcast with `arg1` = the scene number (events.md), so `601[1]` is the current scene.
  c88 list 1's conditions `601[1] != 12, 16, 20, 30, 50, 80` mean "not a surface scene".
- **Method:** decompile.
- **Confidence:** proven

### E-1533 — The follower's step ignores the walk mesh; gate bit 2 in the engine
- **Binary/file:** follower rule `FUN_00434dd0`, update `FUN_00435080`, position setter
  `FUN_004250a0` (decompiled read-only into a private folder); floats `0x4906f0` = 1.0
  (scale on 170/100/70), `0x490718` 170, `0x4904a4` 100, `0x49063c` 70, `0x490494` 4;
  `Scenes/Scene_211.scn`, `.abi` triggers 669..675; engine `follower.cpp`, `events.cpp`;
  scenario `engines/grumpa/tests/companion_gate.toml`.
- **Evidence:** the update runs the rule whenever actor 4 holds an existing character; nothing
  tests the character's active flag. The setter stores the position and sets face `+0x44c`,
  platform `+0x454` and floor type `+0x450` to −1, no floor test. Scene 211's entry script
  stops the companion (op 0xc through actor 4) for its opening line; the rule keeps stepping it
  4 away while it is within 70 of Grumpa: placed at (1028.0, 1735.1) (face 331), it ends at
  (1021.0, 1782.5), off the mesh (no face by the E-0800 test, `scn.py` vertices). The floor
  result face −1 is undone (E-0803), so from there every move is undone: the companion runs in
  place for good (engine run before the fix). Gate bit 2 (E-0705): corpus `+0x188` bit 2 on 19
  triggers (`+0x14c` = 16 on 17: the companion's hint triggers, conditions `c16[4] == 2 &
  c16[5] == 0`). Engine run after the fix: the companion stays on the mesh, follows Grumpa west
  across the plaza and walks into trigger 675 ((881, 8, 1377) r 165): "walk-in trigger 675
  fired", its hint sound starts (c16[5] = 1).
- **Method:** decompile; corpus; scripted dev run.
- **Confidence:** proven (code); the stuck companion is the engine running the original's
  rule, not observed in the original.

### E-1534 — Scene 100 is open sea: mounts at the surface reach 101, Grumpa on foot sinks to 58
- **Binary/file:** `Scenes/Scene_100.scn` (`tools/parsers/scn.py`); E-1660 (mode `[0x48c]`),
  E-1503 (modes per form), E-0802 (height blend), E-0804 (exit spheres).
- **Evidence:** scene 100's walk mesh is 8 faces, 9 vertices, every face type 13 (water),
  every vertex at y −8179.7, x −11958..4485, z −8743..5138, all one connected region. Exits
  (centre, r): 101 (−336.8, 0, −261.6) r 1767.4; 58 (−3382.6, −23098.1, −3394.3) r 18091.8;
  82 r 72521.7, 81 r 11147.8, 83 r 4472.1, 84 r 10007.8, all at y 0. Entries at y 41.1..54.2
  (from 101: (−2432.2, 54.2, −1308.8)). On foot (mode 0) Move blends y toward the floor
  (0.4·y + 0.6·height each tick, E-0802), so Grumpa sinks toward −8180: the exits at y 0 (101
  among them) fall out of reach, while 58's sphere (bottom at y −41190, top at −5006) catches
  him: the underwater route. The boat (mode 1) is held at y −0.5 on every tick and the
  dragonfly (mode 2) on type 13 too (E-1660), so both stay at the surface and touch exit 101
  when within about 1767 + their sphere radius (30) of (−337, −262) horizontally; the region
  covers that point (face 2 / 5 around the origin). So mounts cross 100 to 101 by sailing or
  flying toward the scene centre; `walkplan.py reach 100` lists only 58/82 because it tests
  the exits at the floor's height.
- **Method:** corpus (scn.py); arithmetic from the cited rules.
- **Confidence:** proven from data and code rules; not run (the engine has no modes yet).

### E-1760 — A sound saved while playing restarts from its start on the next entry; its end list then runs
- **Binary/file:** CFXSound Serialize `FUN_004492d0` mode 4 (`case 4`, reads) / mode 5 (writes);
  DoCommand `FUN_00448a40` (disassembly `0x448a40..0x448b7c`); Update `FUN_00448db0`; Play
  `FUN_00449200`/`FUN_00448f70`; Stop `FUN_00449280`; ctor `FUN_004484d0`; entry sequence E-0202.
- **Evidence:** the scene status of a sound is `active +0x10c`, `visible +0x110`, its state
  slots, then `+0x1a0` (playing) and `+0x1b4` (the latch: opcode 0xd sets it, 0x34 clears it,
  while set every other opcode is ignored). The play position and the remaining time `+0x1a8`
  are not kept. DoCommand has no arm for 25 (scene exit): leaving a scene, saving or loading
  does not stop a playing sound or run its list; the actor is just written with playing = 1
  and deleted. On entry the actor is rebuilt from the data (ctor: `+0x1a8 = 0`, no buffer
  `+0x13c = 0`), the status read sets playing = 1, then broadcast 23 (0x17 arm `0x448b0a`):
  playing == 1 and no buffer → deferred play `+0x1b8 = 1` (E-0406); broadcast 86 (0x56) only
  loads the file. The first Update (`+0x10c` != 0) sees `+0x1b8`, calls `FUN_00449200`
  (stop-raw, then Play: `+0x1a8` = the file's length `+0x17c`, buffer from the start) and
  returns, so the timer branch cannot fire on the zeroed `+0x1a8`. When the restarted line's
  timer runs out, Stop (`FUN_00449280`) queues its command list (`FUN_00448bb0`). The only
  other ways to the list are opcode 0x1f5 (`0x448b66..0x448b75`) and the looping branch.
  So in scene 211 a save in the middle of voice 656 loads with the player still off (actor 3's
  `active` 0 is in its status, E-1300), the line plays again in full from its start, and its
  end list's `(3, 0xb)` gives control back: no softlock. The command queue (`remote.abi`)
  does not hold the end list while the line plays, so it plays no part.
- **Method:** decompile (dump) and PyGhidra disassembly of the DoCommand (not in the dump).
- **Confidence:** proven statically; not traced.

### E-1808 — The ship's enemies outmatch Grumpa's base strength; what makes the fights winnable
- **Binary/file:** `Actors/Characters.abi` (six state slots: State, Life, slot 2 attack, slot 3
  defence, role, hints), `Actors/global.atx` (timer 223), `Scenes/Scene_018.abi`,
  `Scene_037.abi`, `Scene_026.abi`; the damage rule `combat.md` (E-1402: n = attack −
  defence, only when > 0); scenario `path5_ship`.
- **Evidence:** Grumpa c10 starts at Life 100, attack 5, defence 2. The ship's fighters: rat
  leaders c37/c38 Life 150, attack 47, defence 18; Captain c69 Life 400, attack 40, defence 18;
  the Giant Octopus c80 Life 140, attack 31, defence 7. So base Grumpa does no damage to any of
  them, and needs attack > 7 for the octopus and > 18 for the rats and the captain. The data's
  raises of c10's slot 2 (opcode 0x58) and slot 3 (0x5a): the gauntlets (18 trigger 665) +11/+2,
  the Belt of Strength (37 trigger 664) +11, the Grandfather (global 243, needs both) +20/+20,
  the Ape King's Jungle Mixture (Grumpa's list, timer g223) +11/+2 for 180 000 ms, after which
  the timer sends (8, 89, 11) and (8, 91, 2) back. No weapon or item record changes the slots.
  So the ship needs the gauntlets plus the belt (attack 27), or the gauntlets plus the timed
  mixture. `path5_ship` (grumpa-dev b02e6ba0): on first boarding 102's trigger 660 activates
  c69, who hits Grumpa for 38 (40 − 2) three times; Grumpa dies and the game goes to scene 96.
- **Method:** corpus (`tools/logic.py`, the character slots), scenario run.
- **Confidence:** proven from data under the combat spec's damage rule; whether equipped
  weapons add attack in the code is asked of combat (Q-1800 update).

### E-1535 — The companion fights and comes back (scenario `companion_fight`)
- **Binary/file:** engine `combat.cpp`, `follower.cpp`, `character.cpp` (grumpa-a2); scenario
  `engines/grumpa/tests/companion_fight.toml`; Characters.abi `.anb` lists (`parsers/abi.py`).
- **Evidence:** the Scharlakanskraken 16 has no attack clip (slots 0..7, 0x1f..0x21), so it never
  joins a fight (E-1430's clip-0x12 test); the golem 22 has. Dev run: Kraken let go (4, 0x37),
  golem made the follower (22, 0x2d), scene 12: rat 35 engaged as 94 → "22 fights as 95 against
  35" (role 7, actor 4 holds none), the golem hits the rat four times (24 each) until it dies;
  the count drops to 1, fighter 95's flag is 1: the golem gets 0x2d (role 2, actor 4's again)
  and follows Grumpa. Two engine choices marked as original bugs: (1) fighter 95 keeps its
  character after the hand-back (E-1433) and its rule (E-1431: T dead → T = 10, then T = the
  character's last attacker, the dead enemy) keeps it swinging at nothing until the scene
  changes; the engine leaves 95 holding it (so it still joins no later fight in that scene, as
  in the original) but runs the rule only while the character's role is 7. (2) Fights are not
  saved (E-1300): a companion saved while fighting (role 7, actor 4 holding none) is held by no
  one after a load; the engine gives it 0x2d on load. Dev run: saved mid-fight, loaded: the
  golem is actor 4's (role 2) and follows.
- **Method:** scripted dev runs; corpus.
- **Confidence:** verified (engine); the two original-bug readings follow from the cited code,
  not observed in the original.

### E-1808 — The ship's enemies outmatch Grumpa's base strength; what makes the fights winnable
- **Binary/file:** `Actors/Characters.abi` (six state slots: State, Life, slot 2 attack, slot 3
  defence, role, hints), `Actors/global.atx` (timer 223), `Scenes/Scene_018.abi`,
  `Scene_037.abi`, `Scene_026.abi`; the damage rule `combat.md` (E-1402: n = attack −
  defence, only when > 0); scenario `path5_ship`.
- **Evidence:** Grumpa c10 starts at Life 100, attack 5, defence 2. The ship's fighters: rat
  leaders c37/c38 Life 150, attack 47, defence 18; Captain c69 Life 400, attack 40, defence 18;
  the Giant Octopus c80 Life 140, attack 31, defence 7. So base Grumpa does no damage to any of
  them, and needs attack > 7 for the octopus and > 18 for the rats and the captain. The data's
  raises of c10's slot 2 (opcode 0x58) and slot 3 (0x5a): the gauntlets (18 trigger 665) +11/+2,
  the Belt of Strength (37 trigger 664) +11, the Grandfather (global 243, needs both) +20/+20,
  the Ape King's Jungle Mixture (Grumpa's list, timer g223) +11/+2 for 180 000 ms, after which
  the timer sends (8, 89, 11) and (8, 91, 2) back. No weapon or item record changes the slots.
  So the ship needs the gauntlets plus the belt (attack 27), or the gauntlets plus the timed
  mixture. `path5_ship` (grumpa-dev b02e6ba0): on first boarding 102's trigger 660 activates
  c69, who hits Grumpa for 38 (40 − 2) three times; Grumpa dies and the game goes to scene 96.
- **Method:** corpus (`tools/logic.py`, the character slots), scenario run.
- **Confidence:** proven from data under the combat spec's damage rule; whether equipped
  weapons add attack in the code is asked of combat (Q-1800 update).

### E-1535 — The companion fights and comes back (scenario `companion_fight`)
- **Binary/file:** engine `combat.cpp`, `follower.cpp`, `character.cpp` (grumpa-a2); scenario
  `engines/grumpa/tests/companion_fight.toml`; Characters.abi `.anb` lists (`parsers/abi.py`).
- **Evidence:** the Scharlakanskraken 16 has no attack clip (slots 0..7, 0x1f..0x21), so it never
  joins a fight (E-1430's clip-0x12 test); the golem 22 has. Dev run: Kraken let go (4, 0x37),
  golem made the follower (22, 0x2d), scene 12: rat 35 engaged as 94 → "22 fights as 95 against
  35" (role 7, actor 4 holds none), the golem hits the rat four times (24 each) until it dies;
  the count drops to 1, fighter 95's flag is 1: the golem gets 0x2d (role 2, actor 4's again)
  and follows Grumpa. Two engine choices marked as original bugs: (1) fighter 95 keeps its
  character after the hand-back (E-1433) and its rule (E-1431: T dead → T = 10, then T = the
  character's last attacker, the dead enemy) keeps it swinging at nothing until the scene
  changes; the engine leaves 95 holding it (so it still joins no later fight in that scene, as
  in the original) but runs the rule only while the character's role is 7. (2) Fights are not
  saved (E-1300): a companion saved while fighting (role 7, actor 4 holding none) is held by no
  one after a load; the engine gives it 0x2d on load. Dev run: saved mid-fight, loaded: the
  golem is actor 4's (role 2) and follows.
- **Method:** scripted dev runs; corpus.
- **Confidence:** verified (engine); the two original-bug readings follow from the cited code,
  not observed in the original.

### E-1770 — The language's folders: texts, voices, the intro
- **Binary/file:** `games/grumpa/discs/cab/Local_*`, `Sounds_*`, `Movies_*`, `UI/001_Menu/`,
  `discs/cd/Movies/`; engine `menu.cpp`, `dialogue.cpp`, `movie.cpp`, `detection_tables.h`;
  scenarios `engines/grumpa/tests/lang_{sv,da,fi,nb}.toml`.
- **Evidence:** `UI/001_Menu/Text.txt` has the md5 of `Local_Swedish/Text.txt`
  (987d2174...), the other three differ (Danish ba1105e6..., Finnish 79220604...,
  Norwegian 596c780d...), so the menu folder holds the default language's copies. Each
  `Sounds_<language>` has the Swedish voice names but four (`014_pirateboss_yell`,
  `065_CS_kraken_spawnpoint_VO`, `CS_challenge_follower_VO`, `Fatbastard_Heavy_Breathing`),
  all four also in `Sounds_`. `Movies_Danish|Finnish|Norwegian` hold only
  `grumpa_intro.mpg`. Engine runs: `--detect` on the CD lists Grumpa in Swedish, Danish,
  Finnish and Norwegian; the menu with `language` sv/da/fi/nb shows "Nytt Spel", "Nyt
  Spil", "Uusi peli", "Nytt Spill" (Grumpa.TTF draws all four).
- **Method:** file comparison; scripted dev runs.
- **Confidence:** proven for the files; where the installer copies `Local_*` (presumably
  over `UI/001_Menu/`) is not read from the setup script.

### E-1610 — CFXCharacter command lists: what runs each one, and their contents in the loaded file
- **Binary/file:** `GRUMPA.EXE` dump (`build/grumpa-import`); Serialize `0x422f80` (E-0401);
  rules `0x4263c0` (hover) and `0x426490` (click), DoCommand `0x41e0d0` (case 0x12 → `0x426490`
  at `0x41e7e9`; case 0x19 → `0x425e30` at `0x41e727`; case 0x46 tail → `0x4261c0` at
  `0x41eae3`), update `0x421a60` (`0x4263c0` at `0x421b38`; death timer → `0x425e30` at
  `0x4222e3`), follower DoCommand `0x434c50` (0x37 → `0x425fc0` at `0x434d2a`), character
  vtable[4] `0x421a50` (pointer at `0x49047c`); `Actors/Characters.abi`.
- **Evidence:** call targets by an E8 scan of the dump: `0x425fc0` and `0x4261c0` have exactly
  one caller each, `0x425e30` two, `0x4263c0`/`0x426490` one each; the latch `0x4ba77c` is
  written only at `0x421a50` (= 0) and `0x42656a` (= 1). The lists, in file order:
  **rules** `+0x660` (n × {EC conditions at +0x104, CC commands at +0x114}, 0x124 B each):
  on op 0x12 (left button down broadcast), if the character is active, at home and the mouse
  point is in its screen rect `+0x148`, and the latch is 0: the first rule whose conditions
  hold (`0x408c30`) while the player's character (actor 3 `+0x298`) has its reaction sphere
  (`0x424ed0`) overlapping this one's (`0x44c6e0`) has its commands pushed (`0x408960`) and
  the latch is set; no further rule or character fires until the latch is cleared by any
  character's vtable[4] at the start of the next update (E-0202 order). Every update
  `0x4263c0` runs the same test without pushing and, if the latch is 0, arms the mouse glitter
  (`0x446330`, E-1720) and stops. **`+0x640`**: pushed when the follower lets the character go
  (op 0x37 to actor 4, after op 1 and role 0). **`+0x650`**: pushed on the rider form itself
  at the end of op 0x46 (the split, after 0x47/0x47/0x2c). **messages** `+0x674/+0x684`: none
  in the data. **death** `+0x630`: pushed when the death timer reaches 0 (E-1433), or on op 0x19
  (leaving the scene) while the death timer is still > 0 (then hidden, inactive, home −1).
  **reactions**: E-1460. Every push copies the command and its conditions to `0x408760`
  (conditions tested at push, `when` honoured, E-0617); there is no self-id substitution.
  Census of `Actors/Characters.abi` (44 records): rules on c10 (5: item use on Grumpa: jungle
  mixture, honey, potions/flea/…, branches, water), c13 (honey), c16 (blood orange: Hulk),
  c21/c28/c87 (mount: `2[0]==1 & c10[4]==1`; form 12/13/88 becomes the player, both parts
  hidden; c87 also hides the air bar 79 and stops 220/221), c23 (parrot, no conditions:
  scene 36 sets 940), c27 (boat: Oars held), c28 rule 1 (honey to the bear), c42 (banana);
  `+0x640` on c16, 20, 22, 23, 25, 26, 42 (each only a voice 0x48(60)); `+0x650` on c11
  (Oars back to inventory 42/43), c12 (voice, stop Dragon-Time 222), c13 (voice), c88 (voice;
  start 220 and show the air bar unless scene 12/16/20/30/50/80); death lists on 27 records
  (enemies add Globalcounters 201/202; c10: inventory op 0xc, `@96 941=1`, `@96 940=0`, GOTO
  96; c11/c12/c13/c88: Grumpa placed at the form and made the player, form and mount
  disabled; c69: `@102` sound 642). `Scenes/Characters.abi` (not loaded, E-0402) differs:
  there c69's death sets 940 and goes to 96 and c10's lacks 0xc and `940=0`; E-1804 cited
  that file. E-1661's "c88 L1 (becoming the form)" is the `+0x650` split list: the air timer
  starts when Grumpa gets off the seahorse; "c87 L0" is c87's rule 0 (mounting).
- **Method:** decompile dump + capstone/E8 scan of the dump; corpus walk of both character
  files with `abi.py`'s t_03 grammar, lists tagged by field.
- **Confidence:** proven (code paths and data); the rect `+0x148` is assumed to be the drawn
  screen bounds (not read here).

### E-1809 — Worn weapons and shields add attack and defence (supersedes E-1808's "no weapon")
- **Binary/file:** `Actors/Characters.abi` c10 attachments (`[0x37c]` weapon bonus to slot 2,
  `[0x38c]` shield bonus to slot 3, E-1700); engine `Characters::wear`.
- **Evidence:** c10's six attachments: 0 Shield (of Protection) defence +20, 1 Father's Sword
  attack +10, 2 Hammer +8, 3 Sword of Might +20, 4 Father's Sword Broken +6, 5 the wooden
  Shield defence +5. Worn, they add to slots 2/3, which the damage rule and the cork's
  `c10[2] > 15` read. So base Grumpa with the broken sword has attack 11 (beats the Octopus'
  defence 7), with the gauntlets too 22 (beats the rats' and the Captain's 18; the cork needs
  > 15). Defence: 2, +5 wooden shield, +2 gauntlets = 9; the Octopus (31) then hits for 22,
  the rats (47) 38, the Captain (40) 31. `path6_sea` (attack 22, defence 2): the Octopus kills
  Grumpa in four hits after one hit of his; the fights need the shield, blocks or more Life.
- **Method:** corpus, scenario run.
- **Confidence:** proven from data and E-1700.

### E-1405 — A character's body sphere: radius `[0x28c]`, centre `[0x290]` above the position (corrects E-0705)
- **Binary/file:** `FUN_00424e90` (`CFXCharacter::GetBodySphere`), the sphere layout of
  `FUN_0045a0b0` (E-0705: centre at sphere `+0x104..+0x10c`, radius at sphere `+0x110`),
  `FUN_0044c6e0` (overlap); `Actors/Characters.abi`.
- **Evidence:** `0x424e90` copies the position `+0x16c..+0x174` into `+0x280..+0x288`, adds
  `[0x290]` to the y `+0x284` and returns `this + 0x17c`, a sphere object: its centre is
  `0x17c + 0x104 = +0x280` and its radius `0x17c + 0x110 = +0x28c`. So the body sphere's
  radius is `[0x28c]` (Grumpa 25, the same field the walk mesh keeps off the walls) and
  `[0x290]` (30 for every character) only raises the centre. E-0705 read `[0x290]` as both.
  Used by the proximity gate, the scene exits, the fighters' and the follower's push-apart.
- **Method:** decompile (one function) against the sphere layout of E-0705.
- **Confidence:** proven

### E-1536 — The engine mounts the boat by its click rule and sails scene 100 (scenario `sea100`)
- **Binary/file:** engine `follower.cpp` (`Characters::clickRules`), `scene.cpp`, `walk.cpp`
  (grumpa-a2); scenario `engines/grumpa/tests/sea100.toml`; Characters.abi boat 27 rule 0.
- **Evidence:** boat 27's rule 0: conditions `c10[4] == 1` and `i111[0] == 6` (the Oars held);
  commands (11, 0x47, 27), (11, 0x2c), 27 and 10 off and hidden, voice 60, (4, 0x37), …; its
  reaction to 10 only plays voice 61 (the hint). Dev run: Grumpa walked to the shore, the
  reaction plays, the Oars held, a press on the boat (its bounds (400,426)–(559,501)): "character
  27 rule 0", 11 the player at the boat. `go 100` (first entry, y 41): the boat stays at
  y −0.5 (mode 1, E-1660) and sails from (−6058.9, −4355.8) to (−2233.5, −1906.5), then "exit
  to scene 101" (E-1534 confirmed). Backspace in 101 splits the form; Grumpa on foot sinks
  (101 is water too) and leaves for 58; in 100 on foot he sinks from y 54 to −6862 in 5 updates
  and −8179.5 in 25, and exit 58 fires.
- **Method:** scripted dev run.
- **Confidence:** verified (engine)

### E-1771 — Worn weapons and shields count in combat: their bonus is in slots 2 and 3
- **Binary/file:** `FUN_00421780` (E-1300, E-1700), damage `0x425730` (E-1432); engine
  `character.cpp` `wear`, `combat.cpp` `hit`; dev run `grumpa_vm` with `slot 10 2`.
- **Evidence:** wearing attachment k adds its attack bonus `[0x37c]` to state slot 2 (weapons)
  or its defence bonus `[0x38c]` to slot 3 (shields), taking it off subtracts it; the damage
  rule reads the attacker's slot 2 and the victim's slot 3. So equipment counts, through the
  slots, though no data record sends 0x58/0x5a for it (E-1808's "no item record"). Grumpa's
  attack with each weapon: Father's Sword broken 5+6 = 11, Father's Sword 15, Hammer 13, Sword
  of Might 25; defence with the Wooden Shield 7, the Shield of Protection 22. Engine run
  (grumpa-dev 8a1efaeb): the Sword of Might (110) put in the weapon slot takes c10's slot 2
  from 5 to 25. So of the weapons only the Sword of Might alone beats the ship's defence 18;
  the Father's Sword (15) needs the gauntlets (+11) or the mixture.
- **Method:** disassembly (E-1300, E-1700); scripted dev run.
- **Confidence:** proven

### E-1810 — The game's character database is `Actors/Characters.abi`; the real death lists (supersedes E-1804's ending chain)
- **Binary/file:** `Actors/Characters.abi` (loaded, E-0402) vs `Scenes/Characters.abi` (never
  opened, a different older copy: the files differ from byte 29); `tools/logic.py`, which read
  the latter until 2026-10-06 (fixed; `notes/logic.txt` regenerated); scenario `boss_captain`.
- **Evidence:** in the loaded database the Captain c69's death list (`+0x630`) is
  `@102 642.0`: it starts his last line `102_ratbeard_final_VS.wav`, whose end list sets scene
  96's flag 940 and goes to 96 (the outro). So sound 642 is the ending's trigger, not unused,
  and the `@96 940` / `GOTO 96` pair E-1804 gave to c69 belonged to the stale file. Grumpa's
  death (c10 list 7) sets 941 and goes to 96 (the death film). The bosses' death lists do not
  clear the islands' spawners (that was the stale file too): Turtle c36 opens its chest (14:
  sound 648, the Seed Star), Crocodile c47 and Hyena c55 their chests (+5 coins, `hud.9(5)`),
  Octopus c80 opens scene 58's walls and arms 660; every boss adds to globals 201/202 (kills).
  `boss_captain` (attack 67, defence 44 by op): c69 falls after 9 hits of 49, the line plays,
  96 shows `grumpa_outro.mpg` (669 frames). With attack 22, defence 9 he takes 4 a hit and
  Grumpa dies after three of his (31 each).
- **Method:** corpus, scenario runs.
- **Confidence:** proven.

### E-1772 — Cursor kind: the complete writer list; start kind 9 from the ATX; kinds 3..6 never set (Q-1710)
- **Binary/file:** `GRUMPA_NOCD.EXE` (`build/grumpa-import`); mouse Load `0x444b60`
  (`0x444b89`..`0x444bbd`), SetKind `0x446130`, Hold `0x446150`, Hover `0x4461a0`, update
  `0x445440`, message `0x446210`; `UI/002_Cursor/002_Cursor.atx`; `notes/logic.txt`.
- **Evidence:** a byte scan of `.text` for every `mov [reg+0x130], imm/reg` finds, in the mouse
  class (`0x444930`..`0x446340`), only: ctor `0x44494e` (−1), update `0x44547b` (hover restore)
  and `0x445559` (9, auto-drop), SetKind `0x446138`, Hold `0x446167` (9) / `0x446174`, Hover
  `0x4461d7`, message `0x44623d` (9); every other hit lies in other classes. An E8 scan for
  calls: SetKind from Load `0x444bbd` (the ATX value), the walk-arrow step `0x445430`
  (9 + angle term) and the panel `0x43e101`/`0x43e1ad` (1); Hover from `0x438c76` (panel),
  `0x438cad`, `0x43baa3`, `0x4591ec`, `0x45922e` (all push 2) and `0x447145` (7); Hold from
  20 sites (item numbers or −1). So no code path sets kinds 3, 4, 5, 6, or 8: `pointpush`,
  `pull`, `push`, `stop` are loaded and never shown. The four ATX ints are read in order into
  `+0x108` (2, the actor id), `+0x10c` (1, active: the update gate of E-1800), `+0x110`
  (1, visible: the draw gate of E-1720) and `+0x130` (9, the kind), and Load then calls
  SetKind(9): **the cursor starts as a walk arrow**, the ctor's −1 never survives a Load.
  Corpus: `logic.txt` (characters, items, globals, scenes) has no command whose target is
  actor 2 and no broadcast of ops 2, 3, 0x1a or 0x23; only conditions read `2[0]` (E-1800).
- **Method:** pefile + capstone scans of the dump; decompile dump; grep of `logic.txt`.
- **Confidence:** proven (static, complete scan of direct writes and direct calls).

### E-1773 — Cursor pictures animate: 10 fps, loop + ping-pong, only the shown picture steps
- **Binary/file:** mouse init `0x444ae6`..`0x444b3b` (40 sprites, stride 0x318), CFXSprite
  DoCommand `0x44e2c0` (jump table `0x44e3b0`/`0x44e3d0`), Play `0x44ed10`, Stop `0x44ed80`,
  update `0x44da50`, frame step `0x44dd80`, mouse update `0x445440`.
- **Evidence:** for each of its 40 sprites the mouse init sets the clock object, loop mode
  3 (`0x444b04`, `0x44da40`), rate 10 (`0x444b13`, `0x44d9f0`) and sends sprite op 0 (play,
  `0x444b2c` vtable+0x18 → `0x44e360` → Play). Sprite ops (`0x44e2c0`): 0 play, 1 stop,
  2/3 show/hide, 0xb/0xc active on/off, 0xd off, 0x17 play if autoplay, 0x34 revive, 500
  show+active+play, 501 hide+inactive+stop. Sprite update steps only while its `+0x10c` is
  set (E-1720: slots 1..8 yes, arrow slots 9..24 no, so arrows never animate). Mode 3 =
  bit 1 loop + bit 2 ping-pong: frames 0,1,..,n−1,n−2,..,1,0,1,.. one step every 50/10 = 5
  updates (0.1 s, E-0701 rule). Mouse update steps only slot[kind] (when kind ≠ 0) and slot 8
  while the glitter counter is > 0; other pictures keep their frame while not shown. Frame
  counts on disc: default 2, grabing 4, pointpush/pull/push/stop 4, attack 2, itemglitter 5.
- **Method:** capstone disassembly of the dump; decompile dump (`0x44da50`, `0x44dd80`,
  `0x44ed10`).
- **Confidence:** proven (static). Play's branch on the sprite's `+0x128` media object
  (`0x45c4b0`, its `+0x108`) is assumed 0 for picture sprites (Q-1711).

### E-1774 — The glitter arm `0x4263c0`: a character under the mouse that can be clicked now
- **Binary/file:** character update `0x421a60` (`0x421aff`..`0x421b4b`), `0x4263c0`,
  PtInRect import `0x4901d0`, mouse point getter `0x4461e0`.
- **Evidence:** each update, for each character: if the inventory panel (actor 90) is not
  visible (`+0x110` == 0) and the mouse exists and the mouse point (`+0x158`) is in the
  character's screen rect `+0x148`, `0x4263c0` runs and `+0x2d0` = 1 (else `+0x2d0` = 0).
  `0x4263c0` walks the character's click rules (`+0x660`, E-1610): the first rule whose
  conditions hold while the player's reaction sphere overlaps this character's arms the
  glitter (10 updates, E-1720) if the click latch `0x4ba77c` is 0. Other Glitter callers:
  `0x438d0b` (panel) and `0x4591fc` (trigger). So the glitter means "a click here now does
  something".
- **Method:** capstone disassembly (the caller is SafeDisc-broken in the decompile); dump.
- **Confidence:** proven (static).

### E-1612 — How CFXCharacter::Draw draws the water ripple and the shadow (resolves Q-1660)
- **Binary/file:** `CFXCharacter::Draw` `0x4226a0` (disassembly `0x422a4b..0x422da3`),
  `CFXCharacter::LoadSharedMeshes` `0x435a00` (textures table `0x4ba73c`), texture bind
  `0x456920` / unbind `0x4569f0`, texture load `0x455ff0` → `0x456400` (`+0x154`),
  `CFXAMesh::Advance` `0x416680`, matrix scale `0x43d8e0`; texture reload `0x435690` (from
  message 0x8002 in `0x4378c0`); corpus `Bitmaps/Virvel.tga`, `Shadow.tga`, `Splasch.tga`.
- **Evidence:** the device behind `[+0x144]` vtable `0x38` is a Direct3D 7 device (slots
  `0x2c` SetTransform, `0x40` SetMaterial, `0x50` SetRenderState, `0x8c` SetTexture, `0x94`
  SetTextureStageState). Textures parallel the meshes: 0 `Virvel.tga`, 1 `Splasch.tga`, 2
  `Shadow.tga`, 3 `effect.tga` (`0x435a00`); a `<name>.tma` beside it supplies the
  D3DMATERIAL7 (`+0x110..+0x150`; only `effect.tma`, `effect_item.tma` exist). The bind
  `0x456920`: SetMaterial, and if `+0x154` (set by `0x456400` when the image is 32-bit)
  ALPHABLENDENABLE 1, SRCBLEND SRCALPHA, DESTBLEND INVSRCALPHA, stage 0 ALPHAOP SELECTARG1,
  ALPHAARG1 TEXTURE; then SetTexture(0). Unbind: ALPHABLENDENABLE 0 if `+0x154`, SetTexture(0,
  null). Virvel.tga 256×256 and Shadow.tga 64×64 are 32-bit with 8 alpha bits; Splasch.tga is
  16-bit. Draw order (gated as E-1700): worn attachments, then ripple or shadow, then the
  body clip mesh (world = `[+0x400]` again, at `0x422d9c`). Both effects only when `+0x474` ≠ 1.
  **Ripple** (type 13, y < −4 or mode 1, mesh 0 loaded): a fresh matrix = identity, diagonal
  = s (`0x43d8e0`), translation row (x, 4.0, z) (`0x40800000` at `0x422b19`): no rotation;
  SetTransform(WORLD); LIGHTING 0, ALPHABLENDENABLE 1, SRCBLEND ONE, DESTBLEND ONE; then the
  bind overrides the blend to SRCALPHA/INVSRCALPHA (Virvel is 32-bit), so the drawn result is
  ordinary alpha blending by the texture's alpha; z-test and z-write untouched (on). `+0x13c`
  (5 if clip `+0x434` = 0, else 8) is the mesh's frames per second: Advance increments
  `+0x120` and when it reaches R / `+0x13c` (R = 50, E-0701; unsigned) steps frame `+0x11c`,
  wrapping to 0 at the frame count `+0x118` (always loops), counter 0. Advance runs once per
  rippled character's Draw on the one shared mesh, so two rippled characters double its rate.
  After: ALPHABLENDENABLE 0, LIGHTING 1. **Shadow** (type ≠ 13, mesh 2 loaded): world = the
  character's own matrix `[+0x400]` (orientation `+0x160`, position + (0, `+0x178`, 0), no
  scale; E-1700), so Shadow.ANB is drawn in the character's local space at its own size,
  turning with it; LIGHTING 0, ZBIAS 16 (`0x2f`), ZWRITEENABLE 0 (`0xe`); bind (alpha blend);
  draw; no Advance call, so the frame stays 0; after: LIGHTING 1, ZBIAS 0, ZWRITE 1. Cull
  mode is never touched. No radius `[0x28c]` is read. Mesh 1 / `Splasch.tga`: no reader in
  Draw or elsewhere (the only users of `0x4ba74c` / `0x4ba73c` are `0x435a00`, `0x435690`,
  the clears `0x41c8c0`/`0x41c940`, and Draw's slots 0, 2, 3). Every character that passes
  Draw's gate gets the shadow or ripple; no per-character flag. Side note: the reload
  `0x435690` names `Bitmaps\Spalsch.tga` (missing), so its chain stops there and slots 2 and
  3 (Shadow, effect) are not reloaded on message 0x8002.
- **Method:** PyGhidra disassembly (`disasm_range`), decompiles, TGA headers.
- **Confidence:** proven (static); the device identity is by vtable layout and state values.

### E-1540 — Walk-mesh wall flags survive leaving a scene and a save/load (CFXFloor mode 4/5)
- **Binary/file:** CFXFloor Serialize `0x432880` (no Ghidra function; defined read-only),
  ctor `0x432600`, SaveGameStatus `0x410390`, LoadScene `0x40cb30(scene, saveOld)`, load
  slot `0x442d40`; `games/grumpa/discs/cab/Save/Current/{001,211,307,500}_status.abi`.
- **Evidence:** Serialize mode 5 writes id `+0x108`, active `+0x10c`, visible `+0x110`, then
  0x71 (113) bytes from `+0x3048`; mode 4 reads the same minus the id. 113 bytes = the 28
  dword flags of indices 0..27 plus the low byte of index 28 (values are only 0/1, ctor
  sets all 29 dwords to 1, so nothing is lost). SaveGameStatus loops ids from 600 to the end
  of the actor table, so the floor (id 600) is the first record of every status file
  (shipped files: id 600, then the next id at offset 125 = 4+4+4+113; 001/307/500 have all
  flags 1, 211 all 0). LoadScene: if `saveOld` == 1 write the old scene's status, delete
  ids 600..979 (`0x40ef40(600, 0x3d4)`), load `.scn` (new floor, flags all 1 from the ctor)
  and `.abi`, then `0x410bf0` reads `<n>_status.abi` back if present (mode 4 overwrites the
  flags) before broadcast 23 (the floor's op 23 only clears the platform list, E-0803).
  Load slot copies `Player<n>\*` into `Current\` and calls LoadScene(scene, 0), so the old
  scene is not written over the loaded file; save writes the current scene's status first
  (E-0502). So walls opened by op 6 (e.g. scene 34's diamond lock) stay open on revisit and
  after a save/load; walls reset to closed only for a scene with no status file yet.
- **Method:** PyGhidra decompile (`define_and_decompile.py`, `-readOnly`); hex of the
  shipped status files.
- **Confidence:** proven (static + corpus).

### E-1406 — A jump's height is cosmetic: `+0x178` is a draw-only y offset that sums to 0
- **Binary/file:** character update `0x421a60` (clip-start block; root-motion tail before the
  Move call at `0x4220cb`), `CFXCharacter::Draw`-side transform `FUN_00424f20`,
  `FUN_00421940`, init `FUN_0041c9b0`; `Meshes/015_N2J2N_Grumpa.amb`, `016_W2J2N`, `017_R2J2N`.
- **Evidence:** each animation tick the clip's `.amb` y of the current frame is **added** to
  `+0x178` (accumulated; 0.0 `0x49045c` when the clip has no table). It is reset to 0 only when
  a clip **0** (idle) starts (with `+0x160`, `+0x168`) and at init (`0x41c9b0`). The only
  reader is `0x424f20`, which builds the draw transform at (x, y + `+0x178`, z): it never
  enters the Move, the step check or the position. Corpus: the cumulative y of all three jump
  clips returns to exactly 0.0 at the last frame (N2J2N/W2J2N 19 frames, peak 17.6 at frame 5,
  dip −10.0 at frame 13; R2J2N 25 frames, peak 21.7 at frame 10); horizontal travel z 124.6
  (N/W, x ≈ 0..1.4) and 208.1 (R). So the arc is a visual bob; the body's y comes only from
  the floor.
- **Method:** decompile dump grep (`[0x5e]`/`+ 0x178` across `notes/decomp/all`, only
  `0x421940`, `0x421a60`, `0x424f20`, `0x41c9b0` touch a character's `+0x178`); `.amb` script.
- **Confidence:** proven

### E-1407 — No jump branch in the step check; scene 17's stones are static faces crossed only from the east shore
- **Binary/file:** `0x421a60` after `0x4220cb`; floats read from `build/grumpa/Grumpa.dump.exe`
  (`0x490460` = 1.0, `0x49049c` = 20.0, `0x490498` = 80.0, `0x4906c4` = 0.4, `0x490640` = 0.6);
  `Scenes/Scene_017.scn` via `tools/walkplan.py load()`.
- **Evidence:** the order after Move is unconditional on the clip: face −1 → old pos; new y
  (= 0.4·old + 0.6·h from Move) > old y + 20 (+80 on a platform) → old x/y/z and
  `0x4219f0(−2.0)`; then floor type; and only afterwards, on types 12/13, clips 0xf/0x10/0x11
  set y = old y (E-1660). No airborne flag, no use of `+0x178`, no Space-held or run scaling:
  the run jump goes further only because R2J2N's `.amb` does (E-1406). Scene 17 has no
  platform: the 11 flagged 0x1a meshes (E-1600) are other scenes'; stone A (faces 1466..1485,
  y 22.0..43.5) and B (1514..1529, y 25.5..45.0) are type-1 faces of the static mesh, water is
  type 13. A landing tick passes only if h − y ≤ 33.3. Simulating the rules (E-0801 height,
  x/z face lookup, no wall slide or radius) for N2J2N and R2J2N from every shore face within
  260 of stone A, 5 yaws each: 11/380 land, all from the east shore (faces 541..558, 739..744,
  x 502..550, z −1814..−1858, y −0.4..2.1) heading ≈ −1.1..−1.2 rad (toward −x), ending at
  y 27..30 on A's low east part; from the south shore the rim is 40..44 above y ≈ 0 and the
  tick is undone each time, so the body stays over the water at y ≈ 0 (kept by the type-13
  rule) and sinks once the clip ends. A → B: 20/40 land (Δ ≈ 10..15).
- **Method:** decompile; `/tmp/jump17.py` (corpus simulation, not committed).
- **Confidence:** proven for the code; the crossing geometry is a simulation without wall
  slide (Q-1401).

### E-1541 — The desert prerequisites (walkthrough 9a–9d) play in the engine; walls kept
- **Binary/file:** engine (grumpa-a2: `Characters::loadFloor`, wall records in saves, E-1540);
  scenarios `engines/grumpa/tests/path9a_snake.toml` .. `path9d_belt.toml` (chained from
  path3's slot 3 to slot 9), `sea100.toml`; scene data through `tools/logic.py`.
- **Evidence:** dev runs (`walkto` legs from `walkplan.py`, items taken from the panel):
  9a scene 7's roots block 10 (type-19 walls) until trigger 660 with the Wood Splinter On Fire
  (133) or the Bottle of Rum; opening 10's door (663) lets the snake bite (Life −11) and its
  end list sets global 269. 9b: 73, 58, 72, 30 on foot, Life 88 → 72 from the air timer. 9c:
  the pond in 35 (664) fills the Empty Jar; scene 34's parrot area lies behind type-19 walls
  that only the diamond lock (663: Lock Shaped Diamond, Lock Shaped Stone or Bottle of Rum,
  mesh 713's end OPENWALL(0)) opens; walk-in 662 switches to the parrot camera (view 4) until
  sound 643 ends (VIEW 2); the parrot's gate line 642 must end before 665 takes the water; then
  c23 is the follower. 9d: in 36 a click on the parrot runs its rule 0 (Scene ID 36, 940 = 0);
  the gate sound 641's end opens the walls and 661 goes to 37; the diamond on the scorpion
  (660) and the pedestal (664): attack 5 → 16. Saving in 34 after the lock and loading kept
  the walls open (needed by 9d's start) only with E-1540 implemented. Scene 9 → 61 and 30 → 34
  defer floor opcodes to the next scene; they now reach the new floor (loaded before the
  deferred commands).
- **Method:** scripted dev runs; corpus.
- **Confidence:** verified (engine)

### E-0408 — Spawner (0x1d): spawns on scene entry, min..max distinct points, restores Life (completes E-0404)
- **Binary/file:** vtable `0x4908c0` (slot 1 Serialize `0x44a250`, slot 2 `0x44a1c0` stores the
  factory at `+0x130`, slot 5 update `0x4080a0` = `ret`, slot 6 DoCommand `0x44a1f0`); spawn
  round `0x44b560` (only caller of it: `0x44a22d`); point spawn `0x44b120` (only caller:
  `0x44b83d`); point Serialize `0x401c00`; character load `0x423303..0x423316`.
- **Evidence:** DoCommand `0x44a1f0`: op 0x34 → latch `+0x12c` = 0; while the latch is set every
  other op is ignored; op 0xd → latch = 1; op 0x17 → `+0x128` = arg1 (the new scene), then the
  spawn round, unless the global `0x4c04cc` == 1 (in .bss; its only reference in the binary is
  this read, so it is always 0). No other op (no 0x19, no 0x56) does anything; the update is
  empty. Spawn round `0x44b560`: nothing if max `+0x158` == 0; count = min `+0x154` +
  rand() % (max − min + 1), capped at the number of points; first every id of every point
  gets DoCommand 501 (inactive, invisible, stop; home untouched); then `count` times: a random
  point index rand() % npoints, re-drawn while it equals one already used this round (a
  local list); more than 10 comparisons in one draw abandons the rest of the round; then
  `0x44b120(index)`. Point spawn `0x44b120`: random id from the point's list, re-drawn while
  it is in the spawner's `+0x148` list (more than 60 comparisons → that point spawns
  nothing); id not loaded → log `"*** ERROR! Character not loaded ***"`, nothing; else
  `SetPosition(point +0x104)`, orientation `+0x160..+0x168` = point `+0x110` (vec3), active =
  visible = 1, DoCommand(2), home `+0x444` = `+0x128` (`0x4250e0`), Life (slot 1, `[+0x11c]
  +0x21c`) = `+0x484`, Request(5, 0.0) (`0x41fde0`), `+0x478` = 1, role (slot 4,
  `+0x564`) = 0, clip counter `+0x4a8` = 9, draw height `+0x178` = 0, update (vtable
  +0x14) called twice, id appended to `+0x148`. `+0x484` is written only at `0x423316`, from
  slot 1 just after the character's load: the Life it was loaded with. Status (Serialize
  mode 4, `0x44a286`): active, visible, the slots and the latch `+0x12c` only; `+0x148` is
  not kept, not loaded and never cleared, but the spawner is rebuilt from the `.abi` on each
  entry. File layout (mode 1/2, `0x44a3b0`): `+0x108`, active, visible, slot vector, min, max,
  `u32 n` points, each = point Serialize (`0x401c00`: position vec3 `+0x104`, orientation
  vec3 `+0x110`, 24 bytes) + `u32 k` + `k` character ids (`+0x120`).
- **Corpus:** 47 spawners (all id 760); (min, max) from (0,0) (scene 57: never spawns) to
  (3,3); 1..6 points; ids 30, 31, 32 in most scenes, 39..41 (scene 71), 43/44/81..85 (scenes
  51, 57, 58, 70, 72).
- **Method:** disassembly (capstone over the decrypted dump; `0x44a1f0`, `0x44a250` are not
  Ghidra functions), decompile dump of `0x44b120`, `0x44b560`; corpus via `abi.py`.
- **Confidence:** proven; the meaning of `+0x478` is open (E-1433's death writes it 0).

### E-1683 — A contact sphere's vertex is a GPU vertex (one per uv index), not a position vertex (refines E-1681)
- **Binary/file:** contact test `FUN_004539a0` (E-1681: "32-byte vertices" of the current
  frame, the mesh's vertex buffer); `Scenes/Scene_090.abi` meshes 710..712 (`rolling_stone_01/02`,
  `primus_rolling_stone_03`, 51 frames, one section of 54 position vertices and 312 uv indices).
- **Evidence:** the buffer the test reads is the one the renderer draws from, one 32-byte
  vertex per uv index carrying the position of the vertex that corner names (E-0600: each face
  corner on the vertex its uv index holds). The rolling stones' spheres name vertices
  (0, 42, 166, 203), (0, 161, 281, 140), (0, 31, 21, 260): beyond 54, so they are uv indices;
  the bubbles' vertex 0 is the same either way. Mapping uv index → its corner's position vertex
  puts the four spheres around the stone's surface; reading them as position vertices drops
  all but vertex 0. Geometry (stone 02 against Grumpa's sphere, radius 25 at +30, standing at
  (1945, 266, 1212) on its path): the nearest sphere overlaps by 38 units at frame 37 with the
  uv mapping, while vertex 0 alone passes 33 units clear.
- **Method:** corpus (`tools/parsers/anb.py`, `abi.py`), engine run (scenario `boulder`: two
  rolls, Life 99 → 77 → 55, hud 51(22) from each stone's third list).
- **Confidence:** proven for the index space (indices above the position count exist); the
  hit verified in the engine.

### E-1684 — The 0x1a contact test's four kinds (bits 1, 2, 8, 0x10), their lists and latches; ops 14/15 on a character do nothing
- **Binary/file:** contact test `FUN_004539a0` (dump `notes/decomp/all/004539a0_*.c`),
  mesh DoCommand `0x450f30` (vtable `0x490910` slot +0x18; no Ghidra function, read from the
  disassembly of `build/grumpa-import/GRUMPA_NOCD.EXE`, jump table `0x4511e4`), Serialize
  `FUN_00452100` (u32 run `+0x1b4,+0x1b8,+0x1bc,+0x1e4,+0x21c,+0x228,+0x1d0,…`), ctor
  `FUN_0044fc60` (`+0x220 = +0x224 = −1`), `FUN_004546f0`, `FUN_00446a00/446b10`,
  `FUN_004354d0`, `FUN_0042fb50/42fc20`, `CFXCharacter::DoCommand` `0x41e0d0`; corpus
  sweep of every `t_1a` record (`Scenes/*.abi`, `Actors/*.abi`).
- **Evidence:** with `+0x1e0` = 1, for each sphere in order, the test tries bit 1, 2, 8, 0x10;
  the first hit that runs a list ends the update (returns 1). A hit whose latch is already 1
  falls through to the next kind; a miss clears that latch (only when `once` `+0x1e4` = 1;
  with `once` = 0 a hit runs its list every update). Latches are per mesh, not per sphere.
  - bit 1: actor 3's held character (present) body sphere → list 3 `+0x14c`, latch `+0x234`,
    filter `+0x220` (player's held id must equal it; never loaded, −1 = none).
  - bit 2: actor 4's held character (`+0x290`), or when actor 4 is absent actor 95's
    (`FUN_00430b40`) → body sphere → list 4 `+0x15c`, latch `+0x238`, filter `+0x224`
    (never loaded, −1).
  - bit 4: not tested anywhere in the function.
  - bit 8: the actor whose id is `+0x228` (file field 6), a 0x1a mesh that must be active
    (`+0x10c` = 1); each of *its* spheres (none when its own `+0x1e0` ≠ 1) against this one →
    list 6 `+0x18c`, latch `+0x23c`, `+0x254` = index of the other's sphere that hit (a miss
    by that index clears the latch).
  - bit 0x10: the held characters of fighters 91, 92, 93, 94 (`DAT_004b9bc4 +0x16c..+0x178`,
    each present) body spheres, in that order, no id filter → list 8 `+0x16c`, latches
    `+0x240/+0x244/+0x248/+0x24c` one per fighter.
  Mesh DoCommand: 0x34 clears latch `+0x250`; while latched all else is ignored; 0/1, 2/3
  `+0x110`, 0xb/0xc `+0x10c`, 0xd inactive+invisible+latch, **0xe `+0x1e0` = 1, 0xf
  `+0x1e0` = 0**, 0x17 entry, 0x56, 0x5c, 500, 501. `CFXCharacter::DoCommand`'s switch below
  0x38 has no case 0xe or 0xf and no default: **ops 14 and 15 sent to a character do
  nothing** (scene 27's `c47.15` and timer 920's `c47.14` are no-ops).
  Corpus (`+0x1bc` of 260 meshes): 1 ×232 (47 with spheres: bubbles 51/55/56/57/58/71/118,
  4 back*_hugg, 9 snake2CCW, 10 Snake_A, 31 worm_A..G, 50 charkfen01, 81/82/83 hajfena, 90
  rolling stones, 100 SA..SH (once 0), 102 ratbeard_wait; 185 without spheres), 0x11 ×12
  (27 myra 712..720: lists 3 (2 cmds) and 8 (5); 105 tunna_A..C: lists 3 and 8), 3 ×6 (1, 3,
  211: no spheres, never fire), 8 ×3 (9 boulderB_fall → 716, 13 banan_1/2 → 713), 0x10 ×1 (33
  Stone_Falling, 10 spheres, lists 3, 4, 7, 8 filled), 0 ×6.
- **Method:** decompile + disassembly; corpus sweep (`t_1a` fields, 18-u32 block index 2 =
  `+0x1bc`, 3 = `+0x1e4`, 5 = `+0x228`).
- **Confidence:** proven (static + corpus)
