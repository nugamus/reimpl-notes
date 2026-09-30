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

### Q-0004 — The `.fxi` block codec's per-mode pixel maths
- **Context:** E-0009. The container and byte layout are proven (`fxi.py`, 316/316); what
  remains is how each sub-block mode fills the 8×8 block from its mask + colours: mode 1
  (1bpp, 2 colours), mode 2 (2bpp, 4 colours), mode 3 (raw 8×4 ×2), and how the low- and
  high-nibble sub-blocks combine into the block. `FUN_00418de0`'s write branches are elided
  in the decompiler output; they need the assembly.
- **What we checked:** `FUN_00418de0` structure and byte reads; the surface fill loop in
  `FUN_004555c0`.
- **Blocks:** actually rendering `.fxi` (backgrounds, textures); a round-trip test.
- **Status:** open (read `FUN_00418de0`'s pixel writes in the disassembly)

### Q-0005 — `.scn` scene record layout
- **Context:** 110 files; header `08 00 00 00`, `58 02 00 00` (600), then a float stream
  (positions with a near-constant Y). Body length is not a whole number of 4-byte floats,
  so the header/record size is not yet right.
- **What we checked:** the corpus; not yet the `CFXScene` loader.
- **Blocks:** scene geometry / collision.
- **Status:** open

### Q-0006 — `.abi` actor-instance and save-status layout
- **Context:** 118 files; `Actors/Characters.abi`/`Items.abi` are actor tables,
  `Save/**/<id>_status.abi` are per-actor save state. Read by
  `CFXActorFactory::CreateFromABIFile` / `Load*GameStatus`.
- **What we checked:** the corpus; not yet the loader.
- **Blocks:** actor instancing and save/load.
- **Status:** open

### Q-0007 — `.anb` / `.amb` mesh and animation layout
- **Context:** 939 `.anb` + 588 `.amb`; `CFXAMesh`/`CFXAMeshEx::CreateFromFile`. Binary
  vertex/animation data.
- **What we checked:** the corpus; not yet the loader.
- **Blocks:** the 3D characters and items.
- **Status:** open
