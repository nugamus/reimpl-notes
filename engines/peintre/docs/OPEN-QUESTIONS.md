# Open questions (Peintre engine, Mission Sunlight)

Things we could not determine after checking the original code (Ghidra), the corpus and
traces. An unresolved field goes here and stays opaque (`unk_*`) in the format spec. It does
not get a guessed meaning.

Append only. When a question is answered, keep the entry, mark it `RESOLVED`, and link the
`EVIDENCE.md` entry that resolved it.

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

### Q-0001 — Does any other title share the PEINTRE 3D code?
- **Context:** E-0008 names the engine `peintre` after the program. Cryo and index+
  published other 3D titles in 1998–2000; if one of them runs the same code (same
  `.BFG/.3DC/.3DM` formats, `C_Monde`), the engine may need a broader name.
- **What we checked:** only this CD is in the corpus. X3D (Monet, 2000) is a different
  engine by 4X Technologies with Direct3D (engines/x3d), not this software renderer.
- **Blocks:** nothing now; a rename before upstreaming if a second game turns up.
- **Status:** open

### Q-0002 — What is the assembly at 0x455470–0x465bcf, and how is it entered?
- **Context:** E-0012. No function starts there after Ghidra's analysis.
- **What we checked:** raw disassembly of a few addresses only.
- **Blocks:** the rasteriser spec (texture mapping, shading) if it lives there.
- **Status:** open

### Q-0003 — How do the drawers address texels of the four odd-sized textures?
- **Context:** E-0015: jardin `salon.3DM` has 512 texel bytes more than 256x256, musee
  `plafond.3DM`, `plafond2.3DM`, `plafond3.3DM` 256 fewer.
- **What we checked:** sizes only. The drawers (0x43c780, 0x444e20, …) are not read yet.
- **Blocks:** nothing if texel addressing is masked to 256x256 (the engine can pad or
  crop); the last row of the three short ones then reads the next heap object.
- **Status:** open

### Q-0004 — .3DA: component order of rotation keys, meaning of track word 0 and key time units
- **Context:** E-0016.
- **What we checked:** data only (unit-length keys, times 0..30, word 0 = 30 in portev).
- **Blocks:** animation playback spec.
- **Status:** open

### Q-0100 — What do the constant fields of the TGP "LZWCRYO" header mean?
- **Context:** `.TGP` single body (E-0100): `u32 0x24` at 8, two zero u32 at 0x14, `256`
  at 0x1C, `1` at 0x20, unpacked size at 0x24. `Tgp_Load2` (0x414779) reads them and
  uses only the packed size at 0x28.
- **What we checked:** the loader; all 110 files (the values never vary).
- **Observed range:** 0x24, 0, 0, 256, 1, 614400 in every file.
- **Blocks:** nothing (the engine ignores them); they stay `unk_*` in `tgp.ksy`.
- **Status:** open
