# Open questions

Things we could not determine after checking the loader, the corpus, and the traces.
Per CLAUDE.md rule 5: an unresolved field goes here and gets marked as an opaque blob in
the format spec. It does not get a guessed meaning.

Append only. When a question is answered, keep the entry, mark it `RESOLVED`, and link the
`docs/EVIDENCE.md` entry that resolved it.

## Entry format

```
### Q-0001 — <one-line question>
- **Context:** where it came from (format + offset, function address, trace line).
- **What we checked:** the three required avenues — loader decompilation, corpus survey,
  proxy traces — and what each returned.
- **Observed range:** for a data field, the set of values seen across the corpus.
- **Blocks:** what work is stalled or degraded by not knowing this.
- **Status:** open | RESOLVED (see E-nnnn)
```

## Questions

### Q-0001 — What are `x3dmp5.dll`, `x3dmp6.dll`, `x3dmp6k.dll`, `xd3d.dll`, `xs3d.dll` for?
- **Context:** present in `Original Game Files/INSTALL/02_PR/` but not named in the project
  ground truth, which lists only `x3d.dll`, `h3d.dll`, `4xvideo.dll`, `AVIPLAY.dll`.
- **What we checked:** nothing yet — noted at bootstrap, before any analysis.
- **Blocks:** the Phase 1 proxy plan assumes `x3d.dll` and `h3d.dll` are the whole engine
  surface. If the game loads any of these at runtime, the proxy misses those calls.
- **Status:** partly answered (E-0028). `x3d.dll` loads a rasteriser (`xd3d`/`xs3d`) and a
  math DLL (`x3dmp*`) by name at runtime. `xd3d` calls into `h3d.dll`, so the h3d proxy
  sees its calls. Open: which variants are picked on a modern machine. Check the loaded
  modules while tracing (tools/proxy/README.md).

### Q-0002 — Which data root does the shipping build actually use?
- **Context:** CLAUDE.md says `<drive>:/Data/`. The repo has an extracted CD image at
  `Original Game Files/Data/`, which may differ from an installed game's `Data` directory
  (installers commonly copy a subset, or decompress packed files).
- **What we checked:** nothing yet — noted at bootstrap.
- **Blocks:** corpus completeness. A format validator that passes 100% of the CD corpus
  proves nothing if the game reads different files at runtime.
- **Status:** mostly answered (E-0027). The root is `<exe dir>\Data\` when `APP.BIN` exists
  there, otherwise `<drive>:/Data/` on the drive whose volume label matches app `+0x108`.
  The installer copies only binaries, so an installed game reads the CD, and the CD copy is
  the corpus. Open: the expected label string.

### Q-0003 — Is `flc.dll` / `SMACKW32.DLL` used, or dead weight from a middleware bundle?
- **Context:** both present in the install payload. Smacker and Autodesk FLIC are video
  formats; the project ground truth names `4xvideo.dll` and `AVIPLAY.dll` for video.
- **What we checked:** nothing yet.
- **Blocks:** video/cutscene work, later.
- **Status:** open

### Q-0004 — Does `.X3D` cover two container formats, or one with two record kinds?
- **Context:** corpus inventory (E-0008). 24 `.X3D` files, two distinct 4-byte prefixes:
  21 files begin `3b 53 43 52` (`;SCR`, i.e. an ASCII `;` comment line) and 3 begin
  `4f 42 4a 45` (`OBJE`). Both look textual, not binary magic.
- **What we checked:** corpus survey only. Loader not yet decompiled; no traces exist.
- **Observed range:** two prefixes across 24 files, 44 B to 7.7 K.
- **Blocks:** Phase 2 scoping. If these are two grammars, `.X3D` needs two specs and two
  validators, and the scene-file spec cannot claim 100% corpus coverage with one parser.
- **Status:** RESOLVED (E-0036: one keyword grammar)

### Q-0005 — What discriminates `.DMF` variants at offset 2?
- **Context:** corpus inventory (E-0008). All 518 `.DMF` files begin `00 fb`; bytes 2-3
  take 8 distinct values (`22 00`, `32 04`, `28 04`, `2c 00`, `32 84`, `36 00`, `32 14`,
  `32 08`). Consistent with one container plus a version/flags/type field at offset 2 —
  but which of those it is, is unknown.
- **What we checked:** corpus survey only.
- **Observed range:** the 8 values above; `22 00` (215 files) and `32 04` (154) dominate.
- **Blocks:** the `.DMF` spec. 48.4 M across 518 files makes this the largest
  engine-specific format in the corpus after the media files.
- **Status:** RESOLVED (E-0038: bytes 2-5 are the u32 file size)

### Q-0006 — `.BIN`, `.FRA`, `.CFG` have no magic at all — what identifies them?
- **Context:** corpus inventory (E-0008). `.BIN` shows 80 distinct 4-byte prefixes over
  109 files, nearly all of shape `xx 00 00 00` — consistent with a leading little-endian
  count rather than a magic. `.FRA` (25 files, 8 prefixes) has the same shape, values
  1-23. `.CFG` (38 files, 3 prefixes) begins with what decodes as an IEEE-754 float
  (`cd cc cc 3e` = 0.4, `00 00 80 3f` = 1.0, `cd cc cc 3d` = 0.1).
- **What we checked:** corpus survey only.
- **Blocks:** any parser for these must be driven by the loader's expected layout, since
  the file itself carries no self-identification. Decompile the loader before speccing.
- **Status:** open

### Q-0007 — `.BMP` magic spread is a tool artefact, not a format question
- **Context:** the inventory reports 111 distinct magics for `.BMP`. Every one begins
  `42 4d` (`BM`); bytes 2-3 are the low half of the BMP header's little-endian file-size
  field, so the count tracks file sizes, not formats.
- **What we checked:** corpus survey. All 381 files share the 2-byte `BM` signature.
- **Blocks:** nothing. Recorded so a later reader does not re-open it. The general lesson
  applies to `.DMF`/`.FRA`/`.BIN` too: `tools/inventory.py` groups on a fixed 4 bytes, so
  a distinct-magic count above 1 is a prompt to look, not a verdict.
- **Status:** RESOLVED (see E-0008)

### Q-0008 — Is `U99.cpp` a developer test scene, and is there any scene-jump mechanism?
- **Context:** `D:\MissionD\Source\U99.cpp` appears only in `MissionD.exe`. Its one
  attributed function, `0x00464ead` (line 248, 793 bytes), calls `X3d_Load_Sdk_o3d`,
  `X3d_Camera_Get_Position`, `X3d_Scene_All_Light_Include_Object`, `X3d_Object_Release`
  and `X3d_Animation_Release` — load a model, place a camera, light it — with no gameplay
  imports. The shipped units are `U00`-`U04`.
- **What we checked:** the string diff (no developer-only string names a scene or a jump
  command; `U##` data-path strings are 252 in `MissionD.exe` vs 250 in `MissionMonet.exe`,
  near-identical), the import diff (the ten developer-only `x3d.dll` imports are all
  lighting/camera/animation-enumeration, E-0014), and the function map. No traces exist
  yet, and `0x00464ead` has not been decompiled.
- **Blocks:** nothing immediately. It matters for Phase 1 scenario selection: a working
  scene-jump in the developer build would make trace capture far cheaper than playing
  through the game.
- **Status:** open

### Q-0009 — Two source strings in `MissionMonet.exe` are referenced from outside any function
- **Context:** `D:\MissionD\Source\U00.cpp` and `D:\MissionD\Source\file.cpp` both have
  references, but `getFunctionContaining` returns nothing for those addresses, so neither
  contributes to `notes/function-map.csv`. Every other referenced source string in both
  EXEs lands inside a defined function.
- **What we checked:** the scan output in `notes/_assert_scan/MissionMonet.exe.json` —
  zero strings have zero xrefs, and the two files appear in `strings` but not in `single`.
- **Blocks:** two source files' worth of attribution, and it hints that Ghidra's
  auto-analysis missed a function boundary in the shipping build. Worth resolving before
  anyone trusts the 1,476 function count as complete.
- **Status:** open

### Q-0010 — What is the `.O3D` body layout after the 36-byte header?
- **Context:** the header is proven (E-0016), the body is not. Two fixed-stride readings
  were tested and refuted: 112-byte material records (541 of 2,133 candidate records have
  a malformed name field) and 192-byte object records (18,259 malformed name fields
  across 10,253 candidate slots). Both had passed a length check first.
- **What we checked:** the corpus, exhaustively, at field level. The loader has not been
  decompiled and no trace exists.
- **Observed range:** u32 at offset 32 is 0-87; the plausible object count that follows a
  112-byte-stride material array is 0-309.
- **Blocks:** the `.O3D` spec, hence 596 files / 14.0 M of the corpus, hence any Phase 3
  work on scene geometry.
- **Status:** RESOLVED (see E-0017, E-0018). `X3d_Load_Sdk_o3d` at `x3d.dll` `0x10001302`
  showed the file is a sequential stream with no fixed-offset records, which is why both
  stride hypotheses failed. `docs/formats/o3d.ksy` plus `tools/parsers/o3d.py` now parse
  596/596 files consuming every byte. Two fields remain opaque and are named `unknown`
  rather than guessed: five u32 per material, and one u32 per object.

### Q-0012 — Does the 1.00 `.O3D` LOD block ever occur?
- **Context:** `FUN_10012920` reads a per-object LOD block — u32 count, then that many
  full object records each followed by an f32 switch distance — but only when
  `DAT_1002d224` is set, which happens only for the `1.00` signature. All 596 corpus
  files are 0.95 (E-0018), and LOD geometry ships as separate `*LOD.O3D` files instead.
- **What we checked:** the loader and the whole corpus. No trace exists.
- **Blocks:** nothing today. `tools/parsers/o3d.py` raises on a 1.00 file rather than
  guessing, so a stray one would be loud rather than silently mis-parsed.
- **Status:** open

### Q-0011 — `.O3D` files reference `.TGA` textures, but the corpus has no `.TGA` files
- **Context:** 1,476 NUL-terminated strings in the `.O3D` bodies end in `.TGA` and none
  in any other extension (E-0016). The corpus holds 381 `.BMP` and no other image format
  (E-0008).
- **What we checked:** the corpus inventory and a sweep of the `.O3D` bodies. The loader
  has not been decompiled.
- **Blocks:** texture resolution, and any claim that the `.BMP` set is the complete
  texture set. Either the loader rewrites the extension at load time, or these are
  authoring-time paths that never resolve at runtime.
- **Status:** RESOLVED (E-0038: `X3d_Map_Init` rewrites the extension to `.dmf`)

### Q-0013 — What do the `.L3D` "extra" slots and the spot branch carry?
- **Context:** `tools/parsers/l3d.py` reads the per-light record but two slots — three f32
  (`extra_floats`) and two u32 (`extra_u32s`) — are not named, only sized. Every corpus
  file has `is_spot == 0`, so the spot branch (3 f32 target + 2 f32 angles) is parsed but
  has no corpus sample. The `X3d_Light_Set_Multiplier` export covers the multiplier
  surface, plausibly tying one of the three f32s to that, but the others are opaque.
- **What we checked:** the loader (`FUN_10014d50` at `x3d.dll` `0x10014d50`); all 5
  corpus files. Across them `extra_floats` is almost always `(104.8, 125.2, ±1.0)` and
  `extra_u32s` is `(0, 1)`, but no engine-side consumer reads the slots in the decompiled
  surface so the meanings cannot be proved from the binary alone.
- **Blocks:** nothing immediately — the record layout is fully recovered and the format
  spec stands. Matters only when an engine implementation needs to *write* a `.L3D`
  rather than read one, or when a Phase 1 trace reaches a light with non-default values.
- **Status:** open

### Q-0014 — What do the 10 f32s of a `.C3D` camera record mean?
- **Context:** `tools/parsers/c3d.py` reads the per-camera record but the 10 f32s are
  not named, only sized. They land at camera-struct offsets `+0x2C, +0x30, +0x34,
  +0x3C, +0x40, +0x44, +0x54, +0x58, +0x4C, +0x50` (non-monotonic in file order).
  The most plausible split is three triples at `+0x2C`, `+0x3C`, `+0x4C` — likely
  position / target / up, matching every other engine's camera slot — but no
  engine-side consumer reads the slots in the decompiled surface so the meanings
  cannot be proved from the binary alone.
- **What we checked:** the loader (`FUN_100148e0` at `x3d.dll` `0x100148e0`); all 6
  corpus files.
- **Observed range:** all 6 corpus cameras have plausible position values in the first
  triple (e.g. `Camera03` at `(176.08, 84.75, 57.98)`) and plausible target values in
  the second triple — consistent with the hypothesis but not evidence of it. The third
  triple is in the small-magnitude range typical of an up vector (`(-0.11, 1.65, 0.0,
  0.69)` for `Camera03`).
- **Blocks:** nothing immediately — the record layout is fully recovered and the format
  spec stands. Matters only when an engine implementation needs to *write* a `.C3D`
  rather than read one, or when a Phase 1 trace reaches a camera with non-default
  values.
- **Status:** open

### Q-0015 — What reads `.DMF` files at runtime?
- **Context:** 518 `.DMF` files / 48.4 M / 8 distinct magics in the corpus (E-0008).
  The string literals `tete.dmf` and `teteBA.dmf` are present in both
  `MissionMonet.exe` (at `0x000404d8` and `0x000404e4`) and `MissionD.exe` (at
  `0x000747c0` and `0x000747cc`), but no function in either binary references them
  via a direct `PUSH imm32` or `MOV reg, [imm32]` — they must be loaded through an
  indirect pointer table that the Ghidra function map does not yet attribute.
- **What we checked:** the entire engine SDK surface — `x3d.dll` exports 278
  `X3d_*` symbols, none of them a DMF loader; `x3dsdk.dll` 63 `X3dsdk_*` symbols,
  only `X3dsdk_Load_3ds` matches a file extension in the corpus, no DMF loader
  there; `xd3d.dll`/`xs3d.dll` carry `X3d_Add_Map_Dll` / `X3d_Update_Map_Dll` —
  the `*_Dll` suffix marks them as engine back-end helpers, not file readers. The
  only `X3d_Scene_Construct_Map` (`x3d.dll` `0x100016e0`) is a 5-byte thunk that
  delegates to `FUN_100105f0`, a 289-byte **buffer allocator** — it takes
  width/height/bpp arguments and never reads a file. So `.DMF` files are loaded by
  the EXE itself, not by any DLL whose loader we have decompiled.
- **Observed range:** the file header is `00 fb <byte2> <byte3>` where `<byte2>:
  <byte3>` takes 8 distinct values across the corpus — `22 00`, `32 04`, `28 04`,
  `2c 00`, `32 84`, `36 00`, `2c 14`, `32 08` (Q-0005). The header is followed by
  a structured body whose meaning is opaque without a parser.
- **Blocks:** a `.DMF` parser for 518 files / 48.4 M of the corpus, and any
  Phase 3 work that depends on scene maps. Until a DMF reader is located (likely
  in `MissionMonet.exe` itself, decompiling the function that owns the indirect
  pointer to `tete.dmf`), the format cannot be recovered.
- **Status:** RESOLVED (E-0038: `x3d.dll` `FUN_10016020`, through the host file callbacks)

### Q-0016 — What reads `.BIN`, `.FRA`, and `.CFG` files at runtime?
- **Context:** 109 `.BIN` / 25 `.FRA` / 38 `.CFG` files in the corpus. Each
  extension covers multiple distinct sub-formats — `.BIN` shows at least seven
  distinct layouts across the corpus (App-style ASCII banner `Mission Monet`,
  per-unit INFOACT/INFOOBJ u32-count records, SCENE with RGB header, dialogue
  D1_xx.BIN with 6-byte records, etc.). `.FRA` shows 8 distinct 4-byte prefixes,
  `.CFG` shows 3 distinct prefixes that decode as IEEE-754 floats (`0.4`, `1.0`,
  `0.1`).
- **What we checked:** the full engine SDK surface — every export of `x3d.dll`
  (278), `x3dsdk.dll` (63), `h3d.dll` (52), `xd3d.dll` (29), `xs3d.dll` (28),
  `x3dmp5/6/6k.dll` (31 each), `4xvideo.dll` (1), `AviPlay.dll` (5), `flc.dll`
  (1). No symbol mentions `.bin`, `.fra`, or `.cfg` — and no string literal in
  any DLL references those extensions at all. The handoff's plan of "load via the
  loader too, not via corpus guesswork" cannot be applied because no such loader
  exists in the decompiled DLL surface.
- **Observed range:** `.BIN` spans 92 B (`SCENE.BIN`) to 28,324 B
  (`U01/INFOACT.BIN`), 80 distinct 4-byte prefixes per E-0008. `.FRA` 25 files /
  8 prefixes, values 1–23 (small u32 count shape). `.CFG` 38 files / 3 prefixes,
  values 0.4 / 1.0 / 0.1 (IEEE-754 floats).
- **Blocks:** 172 files / the corpus' last-mile data — these are exactly the
  "load via the loader" formats the handoff warns against parsing from corpus
  guesswork. The next agent must locate the readers in `MissionMonet.exe` /
  `MissionD.exe` (decompiling the function(s) that own the indirect pointer
  table to `App.bin`, `SCENE.BIN`, `INFOACT.BIN`, `INFOOBJ.BIN`, etc.) before
  any of these three formats can be parsed.
- **Status:** `.BIN` resolved at the container layer (E-0025): the reader is
  `FUN_00415420` / `FUN_00415190` in `MissionMonet.exe`, and all 109 files share one
  chunk container. Per-chunk payloads (`#INDEX#`, `#ACTIONS#`, `#SCENE#`, `#CAMERA#`,
  `#APP#`, `#GAME#`) and `.FRA` / `.CFG` remain open. `.FRA` resolved (E-0100: read by
  `LFrameReader` in `MissionMonet.exe`, 25/25 parse); `.CFG` resolved (E-0103: read by
  nothing shipped, 38/38 parse).

### Q-0017 — Can the original game run unfocused, behind other windows, for unattended tracing?
- **Context:** the user wants traces captured while they keep using the PC.
- **What we checked:** the game's window procedure (`0x00416650`) clears its active flag
  `0x0046ec08` on `WM_ACTIVATE` inactive / `WM_ACTIVATEAPP` false, and the main loop spins
  until it is set again. It offers every message to `H3d_WindowProc` first (`0x004166d5`) and
  skips its own handling if that reports it handled. The h3d proxy's `MONET_BACKGROUND=1`
  swallows those messages, and the game then keeps running, but under dgVoodoo2 2.87.3
  (windowed) its surfaces are lost once it is not the active window:
  `DDERR_SURFACELOST` (`0x887601C2`) reloading `UserFond.bmp`, then hundreds of failing
  `H3d_Lock_BackBuffer` calls and an access violation. Clicking the startup dialog's OK
  while the game is in the background also crashes dgVoodoo's `DDraw.dll` (`c000041d`).
- **Next to try:** run the game on its own desktop (`CreateDesktop`) or in a VM, or find the
  dgVoodoo or h3d path that reports loss while inactive.
- **Status:** resolved (E-0029, E-0030, E-0031). Surface loss came from fullscreen-exclusive
  mode, and 4xvideo still honours its hidden "Window" command. `tools/proxy/run.ps1` selects
  windowed mode, `patch_exe.py` skips the 16-bit desktop check and the activating
  `ShowWindow`, the launcher drops inherited foreground rights (`LockSetForegroundWindow`),
  and background mode keeps the active flag set.

### Q-0018 — What runs between the `OptionUser` players screen and the first U01 frame?
- **Context:** boot (E-0032..E-0035). U00 opens `OptionUser` in app mode 2; U01 plays the
  prologue when started with flag 1.
- **What we checked:** WinMain, `LoadUnitScene`, `U00_Start`, `U01_Start`. Not yet: the
  frame manager (`DAT_0046ec1c`, vtable `+0x90`), the `OptionUser` button handlers, who
  calls `LoadUnitScene` with `U01`, and what `0x0046ed88` (skips the players screen) is.
- **Blocks:** the engine's path from boot to U01. Until answered the engine goes from the
  intro bitmaps straight to U01 with flag 1 (documented in `docs/engine-spec/boot.md`).
- **Next to try:** xrefs to `LoadUnitScene` and to the scene-name slot game `+0x14c`; a
  trace of entering a name and pressing OK.
- **Status:** RESOLVED (E-0105, `docs/engine-spec/ui.md` "Boot to U01"). `0x0046ed88` is
  the practice flag set by the Option menu's Practice item.

### Q-0019 — How does X3D light a face?
- **Context:** `docs/engine-spec/scene.md`. `#SCENE#` sets an ambient colour, `.L3D` adds
  omni/spot lights, materials carry four RGB triples (`.O3D`), and objects list the lights
  that include them.
- **What we checked:** where ambient is stored (`X3d_Scene_Set_Ambient_Light`, scene
  `+0x40..0x43`). Not the per-vertex or per-face shading code in `x3d.dll` / `xd3d.dll`.
- **Blocks:** faithful brightness. The static view uses texture × ambient / 255.
- **Next to try:** the render callback installed by `X3d_Scene_Init_Render`; compare a
  dark unit (U06, ambient 90) against the original.
- **Status:** RESOLVED (E-0140..E-0145, `docs/engine-spec/lighting.md`)

### Q-0020 — How are "weld" objects (faces indexing a parent's vertices) posed?
- **Context:** 5,193 `.O3D` objects have `vertex_flag` set, no vertices of their own and
  faces that index their parent's vertices; in U01 they are the characters (`U01_01`,
  `U01_02`, `U01ernest/U01_E`). `X3d_Object_Get_Number_Weld` exists.
- **What we checked:** the loader (E-0042) only; not the render path or `.A3D` playback.
- **Blocks:** correct character shapes. The static view draws those faces with the
  vertex owner's matrix (bind pose).
- **Next to try:** `X3d_Object_Get_Number_Weld` and the per-object transform in the render
  callback; render comparison of a character.
- **Status:** open
- **Status (2026-09-25):** resolved by E-0054: each welded object transforms its own range
  of the hierarchy top's vertex array with its own world matrix
  (`docs/engine-spec/animation.md`).

### Q-0021 — Why do U01's distant buildings look faint and its boats missing in the original?
- **Context:** E-0044. Candidates: LOD switching (`X3d_Object_Add_Lod`; the renderer asks
  the object class `+0x6c` vtable `+0x14` which object to draw, `xd3d.dll` `FUN_10020720`),
  camera-facing objects (E-0045), material fields.
- **What we checked:** material reader `FUN_10011450`: the five `unk` u32s go to material
  `+0x44`, `+0x48`, `+0x4c`, `+0x50`, `+0x58`; `X3d_Material_Init` sets `+0x6c`→`+8` to
  `31 − (+0x4c)·31/100`, so `+0x4c` is a transparency percentage (smoke materials
  `fum*trans` have 72). The faint buildings' materials have `+0x4c` = 0 and `+0x50` = 1, as
  do `barques` and `soleil`. Drawing every `lod=` file instead of its base object blanks
  the sky, so a LOD replaces single objects, not the whole file.
- **Also checked (2026-09-25):** LOD pick is specified (E-0052) and does not change this
  shot. `xd3d.dll` `FUN_1001e530` turns material `+0x50` into render-state bits (1 or 3 →
  `0x2`, 2 → `0x40`, 10 → `0x100`, 11 → `0x200`; texture → `0x1`, transparency → `0x8`);
  state 3 (texture + mode 1) selects a face drawer (`FUN_1000b840`) that differs from
  state 1 only by setting `D3DRENDERSTATE_COLORKEYENABLE` and flat shading, with vertex
  diffuse `0x00FFFFFF` (alpha 0). Material `+0x50` = 1 is on the boats (`barques`), the
  buildings (`immgch`/`immdrt`) and the sun (`soleil`). The distant "trees" in the engine
  are the `BARQUES` texture on `$Z$barque*` objects. Camera types (E-0045) are applied in
  `x3d.dll` `FUN_10019730` (object class `+0x6c` → `+0x10`): types 1–3 build the view
  rotation from fixed angles instead of the camera's; which angle type 2 keeps is
  ambiguous in the x87 decompile. A 50% blend on `+0x50` = 1 looked close but has no
  support in the code and was dropped.
- **Blocks:** matching the original's distant view.
- **Next to try:** whether the global alpha-blend state is on while state-3 faces draw
  (vertex alpha 0); disassemble `FUN_10019730` case 2 by hand for the angle.
- **Also checked (2026-09-25):** E-0058: type 2 keeps the camera's pitch and fixes the yaw
  at π/2; the object's true view-space origin goes to transform `+0x164`. Not yet read:
  how `xd3d.dll` uses `+0x164` to place the object.
- **Also checked (2026-09-25, lighting):** not lighting. The faint objects are beyond
  every U01 light and the ambient is white, so X3D draws them at texture colour
  (E-0145). They are class-2 colour-keyed faces (`xd3d.dll` `FUN_100039c0`: Gouraud,
  COLORKEYENABLE, no alpha blend, no fog; E-0143) with clamped texture coordinates.
- **Also checked (additive lead, 2026-09-25):** `xd3d.dll` has no fog render states
  (capstone scan of every `SetRenderState` call: no FOGENABLE/FOGCOLOR/FOGTABLE*). A face
  drawer just before `FUN_1000b840` (around `0x1000b604`..`0x1000b72x`) sets
  COLORKEYENABLE and alpha blending ONE/ONE (ONE/INVSRCALPHA when device `+0x1d7a0` →
  `+0x198` is set). Drawing material `+0x50` = 1 faces additively in the engine turns the
  silhouettes white over the sky, far brighter than the original: that drawer is not the
  one used for them, and state 3's drawer (`FUN_1000b840`) draws opaque with the colour
  key. The faint look is still unexplained; lighting (Q-0019) is the next suspect, since
  the drawers modulate the texture by the vertex colour.
- **Answer (2026-09-26):** the faint silhouettes are not `immgch`/`immdrt` but the haze
  planes `Box139..Box146` (`fumgchtrans`/`fumgdrttrans`, `+0x4c` = 72). Transparent faces
  are queued and drawn after all objects, back to front, depth write off, SRCALPHA/
  INVSRCALPHA with vertex alpha trunc(255 − 2.55·t) = 71 (E-0482, E-0483; the capture
  fits). The boats are back faces in this shot (E-0483, E-0205). The engine's black
  "birds" are key-coloured texels of mode-0 sky and reflection maps, which the original
  does not colour-key (E-0481). Rule in `scene.md`, "Drawing order and blending". Left
  open: which device caps bit selects 4444 textures and ONE/INVSRCALPHA for mode 2
  (E-0482); it does not change U01 on the capture setup.
- **Status:** RESOLVED (E-0481..E-0483)

### Q-0022 — What frame rate did the original run at, so what are its turn and pitch rates per second?
- **Context:** E-0046: turning and pitching step 0.06 rad per rendered frame; nothing in the
  EXE caps the frame rate (only the flip in `h3d.dll` or the driver can).
- **What we checked:** the main loop and `Scene_RenderFrame` (no Sleep, no timer wait); no
  traces yet.
- **Blocks:** a faithful per-second turn rate in the engine (it uses a provisional tick).
- **Next to try:** in the original, hold Right for 10 s in U01 and count full turns
  (dgVoodoo caps at 60 fps, `traces/INDEX.md`); read `H3d_Show_BackBuffer`'s flip flags.
- **Status:** RESOLVED (E-0541): fullscreen presents with a vsync'd Flip, so one frame and
  one 0.06-rad turn step per display refresh: 3.6 rad/s at 60 Hz.

### Q-0023 — Which side of a face is its front for collision?
- **Context:** E-0048: sphere and segment tests use face `+0x40` (`+8` plane normal, `+4`
  edge normals) and are one-sided.
- **What we checked:** the collision exports only, not where `x3d.dll` builds `+0x40`.
- **Blocks:** correct wall, floor and ceiling tests (the engine must derive the normal from
  the `.O3D` vertex order).
- **Next to try:** the `.O3D` loader's face setup in `x3d.dll`; check against U01 floor faces
  (their normals must point up for the ground ray to hit).
- **Status:** RESOLVED (E-0543): the stored face normal (rotated by the object's matrix),
  which points along (v2 − v1) × (v0 − v1); edge normals are (v[i] − v[i+1]) × n.

### Q-0024 — How does `X3d_Scene_Pick_Object` pick, and where do hotspots and actions come from?
- **Context:** E-0051: the pick goes through the renderer's vtable `+0xc`; hotspots are named
  after `$` in object names and looked up in scene `+0x1a0`; actions are queued and
  dispatched by name.
- **What we checked:** the EXE side of hover and click only.
- **Blocks:** mouse interaction in U01, including the `TakeCard` click that starts free
  movement (E-0050).
- **Next to try:** the pick method in `xd3d.dll`; the hotspot list's loader (scene `+0x1a0`)
  and `FUN_0041b700`'s queue (scene `+0x198`).
- **Status:** RESOLVED (see E-0070, E-0071, E-0072, E-0073, E-0074; spec in
  `docs/engine-spec/interaction.md`)

### Q-0025 — Minor camera and collision fields
- **Context:** `Camera_DistanceAhead` also skips objects with object `+0x40` ≠ 0; each walk or
  turn step sets camera `+0x50` and calls `FUN_004147a0(cursor, 1, 0)` and `FUN_0041bf30`
  (3D sound update); which units enable run (`+0x48`) and jump (`+0x4c`), E-0047.
- **What we checked:** the call sites only.
- **Blocks:** nothing in U01 beyond the halved speed near walls and the cursor while moving.
- **Status:** open

### Q-0026 — What else the animation tick drives, and what pauses `*U01_03` before `U01_Start`
- **Context:** E-0056/E-0057. Every `animation=` node starts running and looping, yet
  `U01_Start` "starts" `*U01_03` by unpausing it; the tick also runs scene `+0x168`
  (`FUN_00421b90`, probably the `TRAJCAM` camera path) and `FUN_00420e00` (list `+0x1a0`,
  a stored matrix multiplied into an object's local matrix every frame).
- **What we checked:** the node constructor, the tick, `U01_Start`'s calls.
- **Blocks:** whether U01's crank (`U01_03`) turns before the hand-over; any per-frame
  object spin from the `+0x1a0` list; the camera animation `U01_Start` waits for.
- **Next to try:** callers of `FUN_00420060`/`FUN_00420100` during U01 load
  (`FUN_0041e500`, the U01 constructor); decompile `FUN_00421b90` and what fills
  `+0x1a0` entries' `+0x6c`/`+0x88`.
- **Status:** RESOLVED (E-0542): INFOOBJ pauses `*U01_03` at frame 1; `+0x168` is the
  talker (E-0125), `+0x1a0` the stored-matrix hotspots (E-0391).

### Q-0040 — Which face test does the pick install, and what is face `+0x38`?
- **Context:** E-0070. The face class `+0` is `FUN_1000b040` or `FUN_1000b180`
  depending on `FUN_1000b690`'s argument; both return "not pickable" when face `+0x38` ≠ 0.
- **What we checked:** the two functions and their installer; not the caller's argument,
  not the O3D field that fills `+0x38`.
- **Blocks:** nothing in U01 as long as the engine picks front faces only; would matter if
  some faces are double-sided or flagged unpickable.
- **Next to try:** callers of `FUN_1000b690`; writers of face `+0x38` in `x3d.dll`'s O3D
  reader.
- **Status:** open

### Q-0041 — Where does the held-item cursor image come from, and what is the inventory UI?
- **Context:** E-0073/E-0074: a take step sets the cursor item to `<name>C` through the
  cursor manager `DAT_0046edc8` vtable `+0x18`; `Data/2dbit/<name>C.BMP` (32×32) and
  `<name>P.BMP` (50×50) exist for every U01 take target. Steps 2 and 3 also call
  `DAT_0046ec1c` vtable `+0xb8` → `+0x94` / `+0x98` (inventory add/remove, by the look).
- **What we checked:** file names and sizes only.
- **Blocks:** the exact file path and colour key of the item cursor; the inventory screen.
- **Status:** mostly RESOLVED (E-0104, `docs/engine-spec/ui.md`): `+0xb8` is the inventory
  bar `PorteF`, `+0x94`/`+0x98` show/hide it; item images are `Data/2DBIT/<name>.bmp`
  through the frame media manager (`.bmp` appended). The item cursor's colour key is not
  read.

### Q-0042 — What is the action queue's `+0x460` flag in U01's click handler?
- **Context:** `U01_DispatchClickActions` (`0x00401d30`) ends by running `MonterSurToit`
  when queue object `+0x460` ≠ 0, the hovered hotspot is `*U01_09` and camera `+0x1c`
  (z) < 100.
- **What we checked:** the handler only.
- **Blocks:** one alternate way onto U01's roof.
- **Status:** resolved by E-0084 (`+0x460` is action 20's exhausted flag)

### Q-0070 — Why do the lip tables not match their voices' lengths?
- **Context:** E-0126: 28 of 81 tables run past the `.wav`, others stop seconds early.
  Talk ends at whichever comes first, so the mouth may stop mid-sentence.
- **What we checked:** durations only; not whether the tables fit another language's
  recording or a different time scale.
- **Blocks:** nothing (the engine follows the original rule); it decides whether an
  improved lip sync is worth doing.
- **Next to try:** a capture of `U01_02` saying `d1_02` against the table; compare the
  tables with the `.wav` envelopes.
- **Status:** open

### Q-0071 — Does the early "not playing" of streamed voices show in play?
- **Context:** E-0123: for sounds of more than 166,666 data bytes, "group playing" turns
  false up to 83,333 data bytes before the sound ends; scripted waits and lip sync end
  then.
- **What we checked:** the code path only.
- **Blocks:** exact timing of U01's hand-over (`d1_01`, 23.4 s) and of talk animations.
- **Next to try:** a trace of the hand-over: when the camera resumes vs. the end of
  `d1_01`.
- **Status:** open

### Q-0072 — In which order do mouth nodes and the body animation pose the face?
- **Context:** E-0125: the mouth clips are nodes appended to scene `+0x158` after the
  character's nodes and drive the face dummy the body animation also drives; closing
  leaves slot 8 enabled while another slot may be enabled later.
- **What we checked:** the append call, not the list's insertion order or the tick's
  traversal order.
- **Blocks:** whether the mouth pose wins over the body idle; which of two enabled slots
  shows.
- **Next to try:** `FUN_0041fe90`'s traversal and the list's `+4` method; a capture of a
  talking character.
- **Status:** open

### Q-0073 — Which U01 code plays `d1_04`, `d1_05`, `telgrisi2`, `s1_11`, `S1_10`?
- **Context:** E-0127: `d1_04`/`d1_05` are in U01's string area (`0x0043f238`,
  `0x0043f230`); `s1_11` and `S1_10` are played at `0x0040188f` / `0x004017f3`;
  `telgrisi2.wav` has no reference found. Their triggers were not followed.
- **Blocks:** U01's sound completeness, not the sound system.
- **Next to try:** xrefs to those strings; the handlers owning `0x004017f3`, `0x0040188f`.
- **Status:** open

### Q-0045 — Which U01 objects become `Box203` and `*U01_21`?
- **Context:** E-0080. The renames depend on the order of X3D's top-level object list
  (newest first). If every `.O3D` root enters that list once, `Box203` is INTCAB's `Box20`
  and the renamed `Box31` is `U01_21.O3D`'s (the switch); `u01.md` assumes that.
- **What we checked:** `X3d_Scene_Get_Object`, `X3d_Object_Get_Son`,
  `X3d_Scene_Add_Object`; not how `X3d_Load_Sdk_o3d` adds a file's objects.
- **Blocks:** which object U01 hides and which one is the switch hotspot.
- **Next to try:** trace `X3d_Scene_Get_Object` return values at U01 load and read the
  names at those addresses.
- **Status:** RESOLVED (E-0530): only a file's root enters the list, prepended; `Box203`
  is INTCAB's `Box20`, the switch `Box31` is `U01_21.o3d`'s, as `u01.md` assumed.

### Q-0046 — What do the frame manager's `+0xb8` → `+0x90` / `+0xa8` do with `U02_01P`?
- **Context:** E-0081: U01's entry calls `+0x90("U02_01P")` and, when it returns 0,
  `+0xa8("U02_01P")`. `Data/2dbit/U02_01P.BMP` exists; `*P` bitmaps are inventory
  pictures (Q-0041).
- **What we checked:** the call site only.
- **Blocks:** the starting inventory (probably "add the item if missing").
- **Next to try:** decompile the object returned by `0x00426a40` and its `+0x90`, `+0xa8`.
- **Status:** RESOLVED (E-0104): `+0x90` = the bar has the item, `+0xa8` = add it; U01's
  entry gives `U02_01P` once.

### Q-0060 — Frame event 7, and what the scene does when a frame consumes input
- **Context:** E-0101/E-0102. `@HIL` redraws on event 7; the window procedure calls scene
  `+0x3c` and sets app `+0x48c` = 2 when the frame manager consumed a message in app mode 0.
- **What we checked:** the property handlers and the window procedure.
- **Blocks:** nothing for U01 as long as highlights are drawn every frame while hovered and
  clicks on the bar do not reach the scene.
- **Next to try:** callers of view `+0xc` with 7; scene vtable `+0x3c` (`0x0041b760`).
- **Status:** open

### Q-0061 — How do the list views (`cSU#`, `AOL#`, `VAS#`) draw and scroll?
- **Context:** `fra.ksy` `scroll`: three names (`UserASC`, `UserBoule`, `SCR.BitmapScroll`),
  two s32 (33, 33) and one s32 (32 or 20). The players list on `OptionUser` is one.
- **What we checked:** the constructor `0x004325d0` only.
- **Blocks:** drawing the players list and the save/load lists; selecting an existing
  player by clicking the list.
- **Next to try:** the `#SCR` vtable `0x0043b340` draw and event methods; `XGameList`
  (`DAT_0046ec10`, `%sUser_%i` folders).
- **Status:** open

### Q-0062 — Are inventory items outside the strip clipped?
- **Context:** E-0104: items sit at 86 + 70·i and scroll by 70; with more than 7 items some
  lie beyond the strip's 535 px.
- **What we checked:** layout and scroll code; not the item draw clip.
- **Blocks:** nothing in U01 (at most a few items).
- **Next to try:** the strip's draw (`vop#` vtable `0x0043b058`) and the manager `+0x7c`.
- **Status:** open

### Q-0063 — Does a greyed Option item (Load, Gallery) still react to clicks?
- **Context:** E-0106: greying swaps the bitmap of views 3 and 6; their `RCS@` stays.
- **What we checked:** the greying code only.
- **Blocks:** menu fidelity, not U01.
- **Next to try:** `OptionLoad` / `OptionGalerie` handlers with an empty list; a live click.
- **Status:** RESOLVED (E-0456: both still open their screens)

### Q-0047 — How does the player get from the booth roof onto the handcar?
- **Context:** u01.md says the climb (`MonterSurToit`) leaves the player "on the train
  roof", but the climb's last position (485.775, −44.9, 139) is over the booth roof
  (`int05fen01`), and the handcar `*U01_20`, paused at frame 20, is about 440 units away
  at (320, 381) in the engine (E-0090).
- **What we checked:** the engine's pose of `*U01_20` at frame 20 and an overhead view;
  not the original after the climb.
- **Blocks:** playing U01 to its end without teleporting.
- **Next to try:** run the original through the climb (`to_u01.sh`, then the chain of
  E-0090 with `send.ps1` clicks) and read `camera.ps1` and the ground object after it;
  check whether walking across the roofs reaches the car.
- **Also checked (2026-09-26, static):** E-0544: the booth roof joins the long roof
  `toit01`, which ends about 175 units short of the car; the car stands on the rails,
  11 units above them. Open: whether the original lets the player drop from `toit01` and
  walk to the car (collision, falls), which needs a live run.
- **Status:** open

### Q-0110 — Do U00's gauge labels (`deplace`, `Tourner`, `Sauter`, `Take`, `Take2`) show anything?
- **Context:** `FUN_0041a560` copies a label to gauge `+0x12`; U00 always starts the gauge
  invisible (E-0201). `u00.md` treats the labels as inert.
- **What we checked:** the gauge's start, check, stop and draw functions; not the save
  chunk `JAUGE` or other readers of `+0x12`.
- **Blocks:** nothing for play.
- **Next to try:** xrefs to reads of gauge `+0x12` (`FUN_0041a820`/`FUN_0041a790`).
- **Status:** open

### Q-0111 — Why did posted arrow keys not move the camera in U00's tutorial?
- **Context:** E-0203: after a new name, posted Down/Right key messages left the view
  unchanged for over a minute, so the tutorial's states past the first line are specified
  from code only (E-0201).
- **What we checked:** one run; keys posted with `send.ps1` (scan code, extended bit).
- **Blocks:** runtime confirmation of `u00.md`'s state machine.
- **Next to try:** the same run with `camera.ps1` reading the eye before and after a long
  Up hold; check whether a Say was blocking (keys released during a Say are lost), or
  whether collision with Monet blocks the first step; or the user plays it by hand.
- **Status:** RESOLVED (E-0213) the blocking `sb03` never ended because the sound buffers lack `DSBCAPS_GLOBALFOCUS` and the window was never focused; `patch_exe.py` now sets the flag in the run copy.

### Q-0112 — Who restarts U00's gauge in state 8 after the ending?
- **Context:** E-0215: after `DonnerLunettes` opened the Option menu, the hidden gauge read
  state 8 with a fresh start time while `spaceSeen` (`+0x700`) was 1. The only `Start(8)`
  sites (`0x00409a6b` frame hook, `0x00409cfd` near Monet) both require `+0x700` = 0.
- **What we checked:** every `call 0x0041a560` in U00's code; one live reading.
- **Blocks:** nothing (U00 is left through the menu; the gauge is invisible).
- **Next to try:** a watchpoint on gauge `+0x10` during the ending.
- **Status:** open

### Q-0120 — What do U00's tutorial lines say?
- **Context:** E-0232: the code fixes when each of `sb03`..`sb14` plays, not what it asks
  for. The designed path in `u00.md` (store the glasses with a strip click, `sb10` near
  Monet, `sb11` until Space) is read from the conditions alone.
- **What we checked:** EXE strings (no subtitles), the WAV list.
- **Blocks:** nothing for play; confirms the reading of `sb05`/`sb06`/`sb07`/`sb09`/`sb10`/`sb11`.
- **Next to try:** the user listens to `Data/U00/Sound/sb*.wav` and notes one line each.
- **Status:** open

### Q-0121 — Does the original step back onto the boat after the Shift jump, and where is the step-on reachable?
- **Context:** E-0231: the step-on needs the walking ground cast's highest hit to be
  `*U04_32` itself (not a child such as `*U04_30` or `Line07`). The jump lands at
  (149.87, 60.56, −9.0), about 10.6 units from the boat's origin, with the ground object
  cleared; the first step's cast may hit the boat again.
- **What we checked:** static code and object positions only.
- **Blocks:** confirming that the tutorial can be left by walking after the jump.
- **Next to try:** in the original, walk onto the boat, Shift, then Up; read
  `camera.ps1` before and after and see whether the view snaps back onto the boat.
- **Status:** RESOLVED (E-0215) yes; walking from the jump-off pose toward (172, 70) put the eye back on the boat with the step-on pose. The step-on is reached from the path spur at about (166, 54).

### Q-0090 — Which duplicate objects do U02's renames hit?
- **Context:** E-0160. `*U02_01` exists in the clerk's and the seller's `.O3D`, `*U02_07`
  in `Static/U02.O3d` and `Static/U02_07.o3d`; the renames take the first found. With a
  newest-first list (Q-0045), the seller's becomes `*U02_06` (the chestnut bag) and
  `U02.O3d`'s becomes `*U02_07a` (the bridge plank, hidden); `u02.md` assumes that.
- **What we checked:** load order in `U02.X3D`, the rename code; not X3D's list at runtime.
- **Blocks:** which objects are the bag, the counter coin and the two planks.
- **Next to try:** answered together with Q-0045 (trace `X3d_Scene_Get_Object` at load).
- **Status:** RESOLVED (E-0530): the seller's `*U02_01` becomes `*U02_06`; `U02_07.o3d`
  keeps `*U02_07`, `U02.O3d`'s becomes `*U02_07a`, as `u02.md` assumed.

### Q-0091 — Does a save restored between `MarronToPie` and `Sonner` keep the clerk's `Sleep` clip?
- **Context:** E-0163/E-0164. `Sonner` reads the clerk's slot 1 (`Sleep`) without a null
  check; `Sleep` is added only by `MarronToPie`. On a restore `U02_StartUnit` plays the
  snore on the effects emitter instead of the group-4 emitter and adds no clip.
- **What we checked:** U02's restore path; not the generic save/restore of node slots
  (`FUN_0041d490` / `FUN_0041d650`).
- **Blocks:** restore fidelity in U02 only.
- **Next to try:** decompile `FUN_0041d490` for node slot data; or save after the magpie
  in the original, reload, ring the bell.
- **Status:** RESOLVED (E-0535): yes; `Sleep` is slot 1 of the clerk's `*U02_04` node, so
  `ANIMATIONS` re-creates it with its overridden range 85..86 and the backup; `Sonner`
  finds it.

### Q-0092 — What happens to the seller's call timer after a restore?
- **Context:** E-0160. Chunk `TIMEVENDEUSE` stores `callStart` as a raw `timeGetTime`
  value; after a restore in a new session `now − callStart` is arbitrary (unsigned), so
  the first call may come at once or much later.
- **What we checked:** the chunk reader/writer; no live restore.
- **Blocks:** nothing (the engine saves a relative time).
- **Next to try:** restore a U02 save after a reboot in the original and time the first call.
- **Status:** open

### Q-0100 — Do the dimmed `OptionSave` buttons (Back, Main menu, Quit) react before the first save?
- **Context:** E-0184. They start with their `…D` bitmaps and switch to `…N` after a save;
  their `RCS@` commands are registered either way.
- **What we checked:** the OK handler; the frame file; a run that saved before using them.
- **Blocks:** menu fidelity only.
- **Next to try:** open the save screen and click Back before saving; look for code that
  disables `RCS@` on those views (`0x004323a0` "enabled").
- **Status:** RESOLVED (E-0545): yes; dimming only swaps the bitmap, and nothing disables
  the `RCS@` command.

### Q-0101 — Which animation nodes does `ANIMATIONS` cover, and what are node `+0x1cc`/`+0x1d0`?
- **Context:** E-0183. The writer recurses through node `+0x50` only (E-0056 calls it the
  child link; the tick also walks `+0x5c`), so nodes reachable only as siblings may be
  missing. The reader does not skip an entry whose node is not found, so the rest of the
  chunk would be misread. Two saved u32 per slot are unnamed (0xCD in the sample).
- **What we checked:** the reader and writer; one sample with a single node.
- **Blocks:** restore of scripted clips in units with several `*` nodes.
- **Next to try:** a save in U02 after the magpie or clerk clips; `FUN_0041fe90` for the
  tree walk; writers of node `+0x1cc`.
- **Status:** RESOLVED (E-0535): every node of the `+0x50` chain (the list's next link,
  not a child link) whose name starts `*` and that has slot clips; `+0x1cc`/`+0x1d0` back
  up the animation's first/last frame while a range override is active.

### Q-0102 — What does a player's saved unit number drive, and which number labels a players-list row?
- **Context:** E-0181, E-0185. `USERINFO`'s u16 is read only by `0x00425c10` (via
  `FUN_00414150`); the players list prints a counter before each name.
- **What we checked:** the writer and the one reader's call site.
- **Blocks:** nothing for U01; the gallery (if that is the reader) and list fidelity.
- **Next to try:** decompile `0x00425c10`; snap `OptionUser` with two players, one with a
  gap in the `User_<i>` indices.
- **Status:** partly answered (E-0452: it drives the gallery's unlocked paintings); the list
  label is open

### Q-0103 — What do U04's `PARAMS` and U07's `PLANCHE` save?
- **Context:** E-0182: U04 unit `+0x6ec`, `+0x6e8`, `+0x6e4`; U07 unit `+0x6c8`.
- **What we checked:** the chunk reader/writer only.
- **Blocks:** saves in U04 and U07.
- **Next to try:** writers of those unit fields in U04's and U07's code.
- **U07 answered:** `PLANCHE` is the plank-tipped flag (E-0395).
- **U04 answered (E-0332):** `+0x6ec` on the boat, `+0x6e8` face map swapped (never
  read), `+0x6e4` Monet finished painting (`u04.md`).
- **Status:** RESOLVED (E-0332, E-0395)

### Q-0130 — From where on the platform does the original let the player click the whistle cord?
- **Context:** E-0273. Geometry puts the cord in the locomotive's cab, visible and within
  the 160 pick limit only from the platform's east end (x ≈ 2780..2870, y ≈ 60..103).
- **What we checked:** world transforms, ray tests against the static meshes, collision
  walls and ground casts; the camera-facing draw and pick (E-0270). No live run.
- **Blocks:** confirming the engine's bell against the original (visibility through the
  cab, hover cursor 2 after `MarronToPie`).
- **Next to try:** in the original after `MarronToPie`, walk to about (2830, 90) facing +y
  (`camera.ps1`), hover the cord, snap; compare with the engine at the same `start_camera`.
- **Status:** open

### Q-0160 — What does a U05 restore bring back of the dog's and Mazout's clips?
- **Context:** E-0361. `U05_StartUnit` adds `ChienTourne` and `MazoutAttente` only on a
  new entry; later clips (`ChienAttente`, `Attente2`, `Action3`, `MazoutA01`) are added
  by the frame hook and handlers. U05 saves no chunk of its own, and its timers restart.
- **What we checked:** U05's start and frame hook; not the generic `ANIMATIONS` restore of
  node slots (`FUN_0041d490`, Q-0101).
- **Blocks:** restore fidelity in U05 (e.g. the dog routine reading a slot that a restore
  did not create).
- **Next to try:** answered with Q-0101; or save in the original after the dog sits and
  reload.
- **Status:** RESOLVED (E-0535): `ANIMATIONS` re-creates every slot clip of `*U05_05` and
  `*U04_04` with its frame, flags, fps and the active slot; the unit's timers still
  restart.

### Q-0161 — What does the `TableauJeu` frame show, and how does it close?
- **Context:** E-0364. U05's `DoTableauA`/`B` open frame `TableauJeu` for paintings
  `U14_02` / `U14_05` in app mode 2 with Escape off.
- **What we checked:** the opener `0x00426780`; not the frame class, its `+0x114`, or
  `TableauJeu.fra`.
- **Blocks:** the painting clicks in U05 (and any other unit's `DoTableau*`).
  Also U04's `ScrollTableau` (E-0334): `U13_01`, `U13_99`, `U13_04`, `U13_06`, `U16_02`,
  `U16_01`, `U14_01`, `U13_11`.
- **Next to try:** decompile the class created for `TableauJeu` and its `+0x114`; parse
  `2DFRA/TableauJeu.fra` with `fra.py`; spec it in `ui.md`.
- **Status:** RESOLVED (E-0457): full-screen `<name>.bmp`, cursor 2, a click
  (`FinTableauJeu`) closes it; `ui.md` "Other frames".

### Q-0140 — What does the original do on a U03 restore made after the clown's trick?
- **Context:** `u03.md`, E-0301, E-0303. U03 writes no unit chunk. On restore with M10
  exhausted, `U03::StartUnit` only stops the path follow and skips the clown emitter: the
  juggler model is loaded again (not `U03_02.O3D`), the `AttenteHorloge` clip is not
  created, and M20's condition comes from the save. `FlicSalut` and `DoCinematiqueFlic`
  then call `FUN_00420360(node, "AttenteHorloge", 1)` and write `+0x68` of the result
  without a null check.
- **What we checked:** the start and both handlers (capstone); `save.md` (no U03 chunk;
  `OBJECTS` restores hotspot visibility, `ANIMATIONS` covers nodes, Q-0101). No trace.
- **Blocks:** faithful restore of U03 mid-chain; the engine should rebuild the post-trick
  state from M10 rather than crash.
- **Next to try:** in the original, save after the trick, reload, click the policeman.
- **Status:** RESOLVED (E-0537): `ANIMATIONS` re-creates `AttenteHorloge` (and any later
  policeman clip), so nothing crashes; the policeman stands at his clip's own pose as in
  live play.

### Q-0141 — Can the clown's line end before `magie` passes frame 48, so that no postcard is given?
- **Context:** `AnimeSpeakClown` gives `U03_06P` only inside a loop that runs while the
  voice group plays (E-0303). `U03_01_04B` is 27.7 s and the frame is reached about 12 s in,
  but if Enter stops the voice (generic talk skip) the loop may end without the card.
- **What we checked:** capstone of `0x00405942..0x0040599c`; whether Enter stops the voice
  there depends on the talk system's skip, not read for this.
- **Blocks:** whether the engine must guard against a soft lock (U04 needs `U03_06`).
- **Next to try:** in the original, hold Enter through the clown's second line and check
  the inventory.
- **Status:** RESOLVED (E-0538): Enter gives the card at once, and the voice outlasts
  frame 48 by over 11 s; the card is missed only when the voice never plays.

### Q-0142 — Which child of Coordcam's root does `+0x24` return: `*Target` or `*camera`?
- **Context:** the cutscene aims at (`*camera` `+0x20`) `+0x24` (E-0305). `Coordcam.o3d`'s
  root `$$$DUMMY.Dummy01` has children `*Target` then `*camera` in file order. Aiming at
  `*camera` from `*camera` would be degenerate at every cut, so `u03.md` assumes `*Target`.
- **What we checked:** `o3d.py` file order; the child-list order of `X3d_Load_Sdk_o3d`
  (prepend or append) not read.
- **Blocks:** nothing if the assumption holds; the cutscene's framing if not.
- **Next to try:** decompile the child linking in `x3d.dll`'s o3d loader.
- **Status:** RESOLVED (E-0530): children keep file order, so `+0x24` is `*Target`, as
  `u03.md` assumed.

### Q-0143 — How does `X3d_Object_Animate_Transition` blend rotation, scale and visibility?
- **Context:** E-0305: translation is a linear mix; three more per-track functions and a
  t < 0.5 branch (`FUN_10004860` on both clips) are unread.
- **What we checked:** `x3d.dll` `0x10001032` and `FUN_10004d70` only.
- **Blocks:** exact poses during U03's 10-frame transitions (the clown's walk-off, the
  policeman's salute and reflection).
- **Next to try:** decompile `FUN_10005550`, `FUN_10005cf0`, `FUN_100069a0`,
  `FUN_10004860` in `x3d.dll`.
- **Status:** answered by E-0500 (scale and morph lerp, rotation slerp of the two slerped
  clip poses, hide B-over-A only for t < 0.5, lerped pivot) and E-0501 (in U03 the blended
  pose is overwritten by the next tick before rendering); `animation.md` "Transitions".

### Q-0170 — What does U06's clown look like after he first turns?
- **Context:** E-0391. `Hotspot_TurnToYaw` builds M = (local matrix at hotspot creation) ·
  Rz(yaw_old − yaw) and every tick sets local := posed local · M, so the load-time local
  matrix is applied on top of the animation's pose. If that matrix is not the identity,
  the clown jumps on his first turn; the sign convention of `X3d_Make_Rotation_Matrice_Z`
  and `X3d_Matrice_Mult` decides which way he turns.
- **What we checked:** the EXE side (decompile); not the x3d.dll matrix routines, not the
  local matrix of `*U03_02` in `TIRE.O3D`, no trace.
- **Blocks:** a faithful clown in U06 (he must face the player).
- **Next to try:** read `*U03_02`'s local transform with `o3d.py`; decompile
  `X3d_Make_Rotation_Matrice_Z` / `X3d_Matrice_Mult` in x3d.dll; a live run walking
  around the clown.
- **Status:** RESOLVED (E-0533): the stored matrix is `TIRE.O3D`'s identity rotation, so
  the clown turns in place by Rz(3π/2 − yaw) on his posed rotation, with no jump.

### Q-0171 — What is U06's `shooting` flag before its first write?
- **Context:** E-0390. Neither the constructor nor `U06_StartUnit` writes unit `+0x6d0`;
  the debug CRT fills new blocks with 0xCD, so it would read non-zero. From the new-game
  start (y = 475, safe) the first frame's stop clears it and runs the clown to frame 49.
  After a restore inside the danger zone, `shots` counts up from 0 but `shooting` starts
  true, so the first shot comes when the paused clip is seen, at once.
- **What we checked:** constructor `0x00410940`, base constructor `0x0041a890`, start.
- **Blocks:** exact behaviour right after a restore near the clown (minor).
- **Next to try:** `operator new` in `MSVCRTD.DLL` / a memory read of a fresh U06 object.
- **Status:** RESOLVED (E-0534): 0xCDCDCDCD (true); the first frame's stop runs the clown
  to frame 49 and clears it.

### Q-0172 — After a restore with `PLANCHE` = 1, what state is U07's plank in?
- **Context:** E-0395. The tip loads `planche.A3D` at run time and binds a new node; a
  restore reads only the flag and never re-creates the node, so the plank would be in its
  untipped pose while the tip can no longer fire.
- **What we checked:** the chunk reader and writer, the start, the input hook.
- **Blocks:** saves made in U07 after the tip.
- **Next to try:** whether the generic `ANIMATIONS` chunk (Q-0101) restores nodes added at
  run time; a live save/restore after the tip.
- **Status:** RESOLVED (E-0536): the plank shows its load (untipped) pose and cannot tip
  again.

### Q-0173 — Whose cursor does U07's use-up on the hotspot list head clear?
- **Context:** E-0396. `Open2Secret` and `CouperDynamite` call `FUN_004212b0` with the
  list head at scene `+0x1a0` instead of a hotspot. If the head is the object-less hotspot
  of `FUN_00420a90` (`+0x60` = 0), the cursor write is skipped and only the item is used
  up.
- **What we checked:** `FUN_004212b0`, `FUN_00421300` (skips a null object),
  `FUN_00420a90`; not who creates the head.
- **Blocks:** nothing visible if the head has no object.
- **Next to try:** xrefs to `FUN_00420a90` and the writer of scene `+0x1a0`.
- **Status:** RESOLVED (E-0539): the head is the object-less hotspot `Root`; only the item
  is used up.

### Q-0174 — Which `Object04` is U07's dynamite?
- **Context:** E-0394. The first `Object04` found is renamed `*U06_260`, the second
  `*U06_26` (the hotspot). With the newest-first object list that is `Cave2.O3d`'s.
- **What we checked:** the rename loop; the files that hold `Object04` (E-0398).
- **Blocks:** which object `CouperDynamite` hides and the fuse's position.
- **Next to try:** the engine's object order compared with `X3d_Scene_Get_Object`; a live
  hover over the dynamite.
- **Status:** RESOLVED (E-0530): the first `Object04` found is `Chambre1.O3d`'s
  (`*U06_260`), the second `Cave2.O3d`'s (`*U06_26`, the dynamite).

### Q-0150 — Where do the key, the boat's trajectory and the banks lie in U04's pond?
- **Context:** E-0338. The key `*U04_36` is fishable only from the boat (M29 is TRUE while
  aboard); the pick depth there is 4·s = 80. Jumping off works only when the boat clip's
  frame is < 60 or > last − 60, and always lands at (149.87, 60.56, −9).
- **What we checked:** code only.
- **Blocks:** confirming that the key is reachable with two oars and whether one oar
  (`BARKE_TOURNEROND`) can reach it.
- **Next to try:** `o3d.py`/`a3d.py` over `Static/U04.o3d`, `BARKE_TRAJECTOIRE1.A3D`,
  `BARKE_TOURNEROND.A3D`: the key's position against the path; then a live row.
- **Status:** RESOLVED (E-0540): with both oars the boat passes over the key, within 80
  units for Traj frames 296..713; the one-oar circle never gets closer than 153. Water
  occluding the pick is not checked.

### Q-0180 — Which duplicates do U33's renames hit (`GeoSphere0/1`, `pedalegch`, `pedaledrt`)?
- **Context:** E-0421. `X3d_Scene_Get_Object` takes the first match in X3D's list:
  `GeoSphere0`/`GeoSphere1` exist in `anim/balles.o3d` (the juggling balls, nodes
  `*U03_30`/`*U03_31`) and `anim/coffre.o3d` (inside the trunk); `pedalegch`/`pedaledrt`
  in `static/U03_35.o3d` (the policeman's bike) and `static/u03.o3d`. With a newest-first
  list (Q-0045) the later file wins: `coffre.o3d`'s spheres become the `*U03_30`/`*U03_31`
  hotspots' objects and `u03.o3d`'s pedals become `Zpedale`/`ZZpedale`. The nodes are
  renamed separately and are `balles.a3d`'s either way.
- **What we checked:** the rename code and `U33.x3d`'s load order; not X3D's list at
  runtime.
- **Blocks:** which objects the hotspots `*U03_30`/`*U03_31` pick; nothing in INFOACT
  uses them (cursor 0), so only hover is affected.
- **Next to try:** answered with Q-0045 (trace `X3d_Scene_Get_Object` at load).
- **Status:** RESOLVED (E-0530): `coffre.o3d`'s spheres and `u03.o3d`'s pedals, as E-0421
  assumed.

### Q-0181 — Is a root object's next-sibling link (`+0x28`) always null?
- **Context:** E-0421. `U33::SetNoCollisionTree(obj, 1)` sets `+0x118` on the object, its
  descendants and every later sibling (`+0x28`) with theirs. `*U03_02` and `*Ernest` are
  file roots: X3D links roots through `+0x2c` (E-0080) and fills `+0x24`/`+0x28` only
  from parent links (E-0052), so the call should cover the two characters' subtrees
  only; `u33.md` assumes that.
- **What we checked:** the recursion and both link fields; not that object creation
  zeroes `+0x28`.
- **Blocks:** whether other top-level objects (the `COL*` meshes) lose collision in U33.
- **Next to try:** decompile the object constructor in `x3d.dll` (`FUN_10011ea0`'s
  allocation) for `+0x28`.
- **Status:** RESOLVED (E-0530): yes; objects are calloc'd and only children get `+0x28`
  written.

### Q-0190 — Does the Settings music slider have any lasting effect?
- **Context:** E-0450. The slider reads group 1, which `SetAppMode(2)` has set to 0 in the
  Option menu, and OK's value is replaced by 85 at the next mode change out of the menu.
- **What we checked:** the slider, OK handler and `SetAppMode` statically.
- **Blocks:** Settings fidelity (whether the engine should keep the music value at all).
- **Next to try:** in the original, open Settings from the menu, snap the music knob, move
  it, OK, start a game and compare U01's ambient loudness with a default run.
- **Status:** open

### Q-0191 — Who enables the gallery thumbnails' `GIH@` captions (`<p>IndexA`, drawn at +49, +292)?
- **Context:** E-0453. Every `Galerie.fra` thumbnail has a `GIH@` (starts disabled) with
  `<p>IndexA` (194×111) at (49, 292) from the view, besides its `LIH@` hover `<p>IndexC`.
- **What we checked:** the gallery's methods and the commands; none enables a highlight.
- **Blocks:** the gallery's hover look.
- **Next to try:** xrefs to the `@HIG` enabled field (`@HIL` `+0x24` family, E-0102); a
  live hover over an unlocked thumbnail.
- **Status:** open

### Q-0192 — What does unit class 50 do with a painting's `U##D.X3D` scene?
- **Context:** E-0455. `GotoScene3D` loads `U01D`..`U06D`, `U33D` with
  `CreateUnitScene(0x32)` (`0x004123c0`, E-0075) and game `+0x174` = the painting.
- **What we checked:** the loader and the Escape path back to the painting.
- **Blocks:** the gallery's "3D" button.
- **Next to try:** decompile the class-50 vtable (`0x004123c0`): start, input, camera, and
  whether it shows the painting's viewpoint.
- **Status:** answered by E-0502: ambient, per-unit fix-ups, a camera cut from an 18-row
  pose table, free keyboard movement, mouse ignored; `ui.md` "3D view".

### Q-0193 — Which saved unit numbers can reach the gallery's case 33?
- **Context:** E-0452 unlocks 5 paintings for unit 33, but loading `U33.X3D` sets game
  `+0x160` = 3 (E-0087), which unlocks 4.
- **What we checked:** `Gallery_ComputeUnlocked`, `Game_WriteSave`'s argument.
- **Blocks:** the exact unlock count after a save in U33.
- **Next to try:** every write of game `+0x160`; a save in U33 in the original and the
  `USERINFO` u16 it writes (`savegame.py`).
- **Status:** RESOLVED (E-0532): `LoadUnitScene` sets `+0x160` = 33 after `U33.x3D` loads,
  so a save in U33 unlocks 5.

### Q-0144 — What hides U03's route plane `0000aaaaaa`?
- **Context:** `u03.md` Entry step 7 hides the `*path` object and takes the path model out
  of collision. `Anim/U03_09/path.o3d` also holds `0000aaaaaa` (56 faces, untextured
  `DEFAULT` material, white), a sibling of `*path` under `$$$DUMMY.Dummy01`, spread over
  the square. Hiding only `*path` leaves a white plane over the whole street in the engine,
  which the original cannot show (engine capture, 2026-09-26).
- **Engine for now:** the whole path model is hidden (not drawn, not picked, still
  animated) and out of collision.
- **Next to try:** read `U03::StartUnit` (`0x00404f70`) around the hide call: whether it
  hides the model's root with its subtree (`X3d_Object_Hide(root, 1)`), or the plane is
  hidden elsewhere.

### Q-0194 — Do U04 `fenetremais` and U05 `COKE.O3D` `Material #170` really show their key colour?
- **Context:** E-0484: after name sharing, these two mode-0 materials still map keyed
  texels onto their faces (27 % of `ARBREGR1`'s UV area, 26 % of `BAT02`'s). By E-0481 and
  E-0485 the original draws those texels in the key colour.
- **What we checked:** every `SetRenderState` site (no colour key, alpha test or blend in
  the mode-0 drawers), `H3d_Add_Texture`/`H3d_Set_Color_Key` (a DirectDraw source key on
  the surface, used only under COLORKEYENABLE), the palette conversion `FUN_1001df20` (no
  alpha), the EXE's render-state calls (filtering, dither, render class only).
- **Blocks:** nothing known; engine follows the rule.
- **Next to try:** a capture of those faces in the original (U04 house window, U05 coke
  building).
- **Status:** open
