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
