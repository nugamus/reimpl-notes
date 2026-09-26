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

### Q-0150 — What does the CVY mask colour (0x116A / 0x08AA) do after it is painted over a movie?
- **Context:** E-0205. Blit_CvyMask paints parts of the movie rectangle in one dark blue
  on the back buffer (0x6516a8) every frame.
- **What we checked:** the constants occur only at the four mask calls; no other code
  compares pixels with them (byte search of `.text`). Whether the colour is simply the
  interface background (masking the video to a non-rectangular window) or a key for a
  later pass (sprites, 3D) is not established.
- **Blocks:** nothing for decoding; the engine can paint the same colour. A capture of
  one masked movie (e.g. `A01_032A`) would settle what shows there.
- **Status:** open

### Q-0151 — Which movie does A13_052B.CVY belong to: A13_052B.HNM (94 frames) or the extensionless A13_052B (101)?
- **Context:** E-0204. The CVY has 101 masks; table entry `A13_052b` has has_cvy = 1 and
  the EXE opens `A13_052B.HNM` (94 frames), so masks 0..93 are used.
- **What we checked:** frame counts; the EXE never opens a file without `.HNM`.
- **Blocks:** whether masks line up with the 94-frame movie (a capture or a decoded frame
  comparison would show it).
- **Status:** open

### Q-0220 — chambreb: what starts the mirror track and the shoe track, and what are DAT_004abd60 / DAT_004abd70?
- **Context:** E-0332. `mirroir.3da` (on `mirroircas`) is only ever posed at its end or
  stopped by the 3D code; `chaussur.3da` has playing = 1 in .data and the entry clears it
  whenever the shoes are in the room. `DAT_004abd60` is set to 1 at entry when it and
  `DAT_004abd70` are 0 and `DAT_004abd14` = 1; nothing in the 3D code reads it.
- **What we checked:** every decompiled function of 0x419e50..0x42fbd6 (grep for the
  addresses). The 2D side receives the whole state block by pointer (E-0312) and may
  write these words by offset.
- **Blocks:** nothing in the 3D flow; possibly a mirror-breaking animation seen after
  zone 11.
- **Status:** open

### Q-0235 — Who sets DAT_004abc08 (mangeurs' cuckoo on entry)?
- **Context:** mangeurs' init `0x4298e5` sets `DAT_00599044` := (`DAT_004abc08` = 0); the
  frame plays `coucou` and clears `DAT_004abc08` when it was non-zero (E-0364).
- **What we checked:** all decompiled game3d functions; no other write. It lies in the saved
  block `0x4aba40` passed to the 2D side (E-0312), so a 2D zone may set it.
- **Blocks:** when the cuckoo sounds.
- **Status:** open

### Q-0236 — Are the never-started 3D tracks started elsewhere?
- **Context:** loaded tracks whose playing word no decompiled 3D function sets to 1:
  jardin `papiyon3.3da` (`0x4ad228`), maisonj `nuages.3da` (`0x4adba4`), mangeurs
  `buche.3da`, `chaise.3da`, `fagot.3da` (`0x4ae3ac`, `0x4ae424`, `0x4ae49c`) (E-0361,
  E-0363, E-0364).
- **What we checked:** the decompiled game3d functions (0x419f0e-0x42fbd5).
- **Blocks:** nothing for playback (they stay at their loaded pose); mangeurs' track ends
  hide the log/faggot and scroll `fire`, which would matter if they ran.
- **Status:** open

### Q-0237 — What leaves maisonj for hopiext (7 → 2)?
- **Context:** `0x41fda9` has an arrival for previous scene 7, target 2 (E-0308), but
  maisonj's frame `0x428e63` never sets `DAT_004e3144` := 2 (E-0363).
- **What we checked:** every write of `DAT_004e3144` in the decompiled 3D functions of batch B.
- **Blocks:** nothing; a missing exit would only drop an unused arrival.
- **Status:** open
