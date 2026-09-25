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
- **Status:** open

### Q-0005 — What discriminates `.DMF` variants at offset 2?
- **Context:** corpus inventory (E-0008). All 518 `.DMF` files begin `00 fb`; bytes 2-3
  take 8 distinct values (`22 00`, `32 04`, `28 04`, `2c 00`, `32 84`, `36 00`, `32 14`,
  `32 08`). Consistent with one container plus a version/flags/type field at offset 2 —
  but which of those it is, is unknown.
- **What we checked:** corpus survey only.
- **Observed range:** the 8 values above; `22 00` (215 files) and `32 04` (154) dominate.
- **Blocks:** the `.DMF` spec. 48.4 M across 518 files makes this the largest
  engine-specific format in the corpus after the media files.
- **Status:** open

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
- **Status:** open

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
- **Status:** open

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
  `#APP#`, `#GAME#`) and `.FRA` / `.CFG` remain open.

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
- **Status:** open. Until then traces are captured in the foreground (tools/proxy/README.md).
