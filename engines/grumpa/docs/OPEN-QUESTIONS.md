# Open questions (Grumpa engine)

Things we could not determine after checking the original code (Ghidra), the corpus and
traces. An unresolved field goes here and stays opaque (`unk_*`) in the format spec. It
does not get a guessed meaning.

Append only. When a question is answered, keep the entry, mark it `RESOLVED`, and link the
`EVIDENCE.md` entry that resolved it. Ranges follow EVIDENCE.md (Q-0001.. survey, disc and
protection).

## Entry format

```
### Q-0001 — <one-line question>
- **Context:** where it came from (format + offset, function address, trace line).
- **What we checked:** the original code, the corpus, traces.
- **Observed range:** for a data field, the set of values seen across the corpus.
- **Blocks:** what work is stalled or degraded by not knowing this.
- **Status:** open | RESOLVED (see E-nnnn)
```

## Questions

### Q-0001 — How do we obtain a decrypted `Grumpa.exe` to read?
- **Context:** E-0003: SafeDisc 2.60.052 encrypts `.text` and `.data`; the key comes from
  SafeDisc's run-time check (its DLLs unpacked from the stub, the `secdrv.sys` driver, the
  disc signature of E-0004). Windows 10/11 no longer load `secdrv.sys`.
- **What we checked:** the static bytes (no readable code or strings); nckstwrt's
  SafeDiscLoader2 (GPL-3.0, github.com/nckstwrt/SafeDiscLoader2): it emulates `secdrv`
  and patches the check inside the running game, calling SafeDisc's own decryption, so
  it is a run-time route, not a static decryptor. The classic Safedisc2Cleaner (closed
  freeware) unwraps versions below 2.7 to a file, also by running the stub.
- **Blocks:** Ghidra on the game code: every spec (boot, rendering, scenes, actors) and the
  meaning of every format field.
- **Status:** open

### Q-0002 — Is the engine Idol FX's own and used by this game only (engine name `grumpa`)?
- **Context:** the engine is named after the game, as for Gilbert, until the code shows
  otherwise. The credits name a "FXSTRUCTOR" (E-0002), maybe Idol FX's editor.
- **What we checked:** the corpus only; the EXE's strings are encrypted (E-0003).
- **Blocks:** nothing now; the name of `../scummvm/engines/<engine>`.
- **Status:** open

### Q-0003 — Where does the installer put each file group?
- **Context:** the cabinet is unpacked by file group (E-0001); the installed layout (which
  folder `Grumpa.exe` reads `Scenes/`, `Meshes/`, … from, which language's files it
  takes) is set by the InstallScript `setup.inx` and by the EXE's paths.
- **What we checked:** file-group names only.
- **Blocks:** the run folder for the original and the engine's data paths.
- **Status:** open

### Q-0004 — The `.fxi` block codec's per-mode pixel maths — RESOLVED (see E-0009)
- **Context:** E-0009. The container and byte layout are proven (`fxi.py`, 316/316); what
  remains is how each sub-block mode fills the 8×8 block from its mask + colours: mode 1
  (1bpp, 2 colours), mode 2 (2bpp, 4 colours), mode 3 (raw 8×4 ×2), and how the low- and
  high-nibble sub-blocks combine into the block. `FUN_00418de0`'s write branches are elided
  in the decompiler output; they need the assembly.
- **What we checked:** `FUN_00418de0` structure and byte reads; the surface fill loop in
  `FUN_004555c0`.
- **Blocks:** actually rendering `.fxi` (backgrounds, textures); a round-trip test.
- **Status:** RESOLVED (E-0009). Each control byte's low nibble codes the high
  byte of the block's pixels, its high nibble the low byte; per plane, mode 0 solid, 1
  1bpp/2 values, 2 2bpp/4 values, 3 raw. `fxi.py` decodes 316/316. From the blit at
  `0x00419f7a` and the mode writes at `0x004198c0`+.

### Q-0005 — `.scn` scene record layout
- **Context:** 110 files; header `08 00 00 00`, `58 02 00 00` (600), then a float stream
  (positions with a near-constant Y). Body length is not a whole number of 4-byte floats,
  so the header/record size is not yet right.
- **What we checked:** the corpus; not yet the `CFXScene` loader.
- **Blocks:** scene geometry / collision.
- **Status:** open

### Q-0006 — `.abi` per-class actor serialize bodies
- **Context:** E-0012. The record framing is known (`u32 type, u32 id, class data`, looped
  to EOF) and the 34 actor types with their object sizes
  (`engines/grumpa/notes/actor-types.txt`). What remains for a byte-exact validator is each
  class's serialize (vtable+4): the fields each actor type reads from the stream. The
  common base (id, position, state) is shared; subclasses add their own.
- **What we checked:** `CreateFromABIFile`, `CreateActor`; not yet each serialize.
- **Blocks:** a 100% `.abi` validator; save/load; actor state.
- **Status:** open (decompile the per-type serialize methods)

### Q-0007 — The `.anb` trailing-frame count: F vs F-1
- **Context:** E-0014. `.anb` geometry, UVs and the animation block are decoded (938/939
  parse). The trailing animation block is `K*(ΣA)*24` bytes: K = F-1 frames for most meshes
  but K = F for the `X2Y` transition-animation clips (their names carry the state pair). The
  discriminator here is the file name, not yet a field found inside the file; and
  `012_D2D_Grumpa_In_Boat.ANB` has 4,456 unexplained trailing bytes.
- **What we checked:** `FUN_004157d0` (the final read is `(F-1)*ΣA*24`, yet the X2Y files
  hold one more frame); a name/prefix census of all 939 files.
- **Blocks:** knowing which stored frame is the rest pose; nothing for a static render.
- **Status:** open (find the in-file flag; the parser accepts K in {F-1, F})

### Q-0008 — The per-view camera (to composite actors into pre-rendered scenes)
- **Context:** E-0016. Each scene view is a pre-rendered 800×600 background + `.fxi` depth
  (E-0011); actors are placed in world 3D and projected with the camera the view was
  rendered at, then depth-tested against the `.fxi`. The engine's rasteriser works
  (E-0016) but needs that camera (eye position, look direction, vertical FOV, near/far) per
  view, and the mapping from `.fxi` depth values to world Z, to place and occlude actors
  correctly.
- **What we checked:** the device init (`FUN_00436aa0`, 800×600×16, no projection there);
  the `.scn` load path (`FUN_0040cb30` opens `Scene_N.scn` but does not parse camera data in
  that function); the mesh upload (`FUN_004154b0`). The camera is set during the scene
  render tick, from scene data whose location is not yet found.
- **Blocks:** scene-accurate actor rendering and occlusion; picking/hotspots.
- **Status:** open. Plan: boot into a scene with `startScene.txt` (E-0017) through
  SafeDiscLoader2 (as `sddump.py` does), then read the live view/projection matrix from the
  decrypted process — the fastest ground truth for the camera, near/far and scale. The
  static alternative is to trace the scene render tick to the device `SetTransform`.
  Runtime prerequisites found: the original resolves its data via the registry key
  `SOFTWARE\Idol FX\Grumpa` value `DataPath` (`FUN_00447840`/`FUN_00436aa0`; the read is
  behind a SafeDisc stub) and errors "Cant Find Registry Key, Fatal Error" if absent — so a
  runtime run needs that key set to the `cab` data folder, plus `startScene.txt` with a scene
  number, launched through SafeDiscLoader2. Then dump the decrypted process (as `sddump.py`
  does) and locate the perspective projection matrix (recognisable: 1/tan(fov) diagonal, a
  ±1 in the w column) and the per-view world matrix near the device object.
  The exact registry key is `HKLM\Software\Idol FX\Grumpa` value `DataPath` (the
  InstallShield template `Software\COMPANY_NAME\TITLE_MAIN` in `data1.hdr`; for the 32-bit
  game, `HKLM\Software\WOW6432Node\Idol FX\Grumpa`). Setting it needs admin, which this
  session lacks (HKCU is ignored by the game), so the runtime route is blocked here — it
  needs the user to run once (elevated):
  `reg add "HKLM\Software\WOW6432Node\Idol FX\Grumpa" /v DataPath /t REG_SZ /d "<cab path>" /f`.
  The on-disk EXE is SafeDisc-encrypted so it cannot be patched to read HKCU instead.
