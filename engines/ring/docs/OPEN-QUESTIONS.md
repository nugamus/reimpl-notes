# Open questions (Ring engine)

Things we could not determine after checking the original code (Ghidra), the corpus and
traces. An unresolved field goes here and stays opaque (`unk_*`) in the format spec. It does
not get a guessed meaning, and it does not take Templier's meaning on trust either.

Append only. When a question is answered, keep the entry, mark it `RESOLVED`, and link the
`EVIDENCE.md` entry that resolved it.

## Entry format

```
### Q-0001 — <one-line question>
- **Context:** where it came from (format + offset, function address, trace line).
- **What we checked:** the original code, the corpus, traces, Templier's engine.
- **Observed range:** for a data field, the set of values seen across the corpus.
- **Blocks:** what work is stalled or degraded by not knowing this.
- **Status:** open | RESOLVED (see E-nnnn)
```

## Questions

### Q-0001 — Which protection wraps Prophet's Legend.ex_, and where do its import slots lead?
- **Context:** E-0004: sections `.cms_t`/`.cms_d`, entry point in `.cms_t`, import calls in
  `.text` go through slots in `.cms_d` (e.g. `[0x4e82f0]`) instead of the IAT.
- **What we checked:** section layout, entropy, byte diff against the crack (diff oracle
  only). No product string found in `.cms_t`/`.cms_d`.
- **Observed range:** 323 differing runs in `.text`, most of them 3-byte slot addresses.
- **Blocks:** naming the Win32 calls in Prophet's code during RE. A slot → import map can be
  built site by site from the diff (same call site, IAT slot in the crack) without using the
  crack's code.
- **Status:** open

### Q-0002 — Where does the engine convert RGB555 image data to the display's 16-bit layout?
- **Context:** E-0017: packed images decode to 16-bit pixels that look right as RGB555.
  `RING_DVD.EXE` 0x414410 (string `aVideoDeviceRaw::CalculateMask…`) sets channel masks
  for four display layouts (555, 565, 655, 556), so the engine adapts to the surface.
- **What we checked:** the Bma loader copies table entries without conversion.
- **Blocks:** nothing for ScummVM (we pick the pixel format), but the spec of image
  loading should name the conversion step.
- **Status:** open

### Q-0003 — Does Prophet read only 10 layers of A03S02N05R01.aqc?
- **Context:** E-0020: 18,289 bytes after the tenth section of this file do not form a
  section (they start with a copy of the last entry). The engine reads as many sections as
  the rotation has layers (`this+0x48`, from the game code).
- **What we checked:** the file; LEGEND.EXE strings (rotation names are not stored whole).
- **Blocks:** nothing if the layer count is 10; the validator keeps the bytes as
  `unk_trailing` for this file only.
- **Status:** open (answer from Prophet's zone a03 code: the AddRot call for this node)

### Q-0004 — What does the original do with the 53 damaged DVD voice files?
- **Context:** E-0021: 52 DVD `.wac` files (SPA/ITA/HOL/SWE) break at a 64 KiB offset,
  one has no WAV header. The mono decoder reads `size + 2` bytes per chunk, so after the
  break it reads garbage sizes; a failed read raises `aSecComSouMono::Decompress -> raed
  Error`.
- **What we checked:** the decoder and the files; the good chain resumes about 4 KB later.
- **Blocks:** how our engine plays these lines (stop at the break like a read error, skip
  to the resumed chain, or fall back to another language's file). One precise run of the
  original DVD in Spanish on `AS/SOUND/SPA/1104.WAC` would answer what the player hears.
- **Status:** open

### Q-0005 — How does the ISO version play fos03n02_s05n01.cnm with its damaged frame 132?
- **Context:** E-0024: the chunk at the table's frame-132 video offset is not a chunk.
  If Play reads sequentially, the chain breaks there ("Error in typeCinData"); if it seeks
  by the table, only that frame is lost.
- **What we checked:** the file; the ISO EXE's Play has not been read yet.
- **Blocks:** faithful playback of one ISO-version video (FO zone transition).
- **Status:** open

### Q-0006 — How does the DVD EXE resolve a data path (install dir vs CD path)?
- **Context:** spec/boot.md: paths are built from app+0x6b (0x402460), the string at
  app+0x14 (0x402470, the `CDPATH` value set by 0x40b4d0) and the one at app+0x18
  (0x402480), with formats like `%s%s\%s\%s\%s`.
- **What we checked:** the three getters; not yet the callers' choice between them.
- **Blocks:** nothing for ScummVM (everything is under one game directory), but the spec
  of file lookup should say which prefix each kind of file uses.
- **Status:** open
