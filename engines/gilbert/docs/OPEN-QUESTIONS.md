# Open questions (Gilbert engine)

Things we could not determine after checking the original code (Ghidra), the corpus and
traces. An unresolved field goes here and stays opaque (`unk_*`) in the format spec. It
does not get a guessed meaning.

Append only. When a question is answered, keep the entry, mark it `RESOLVED`, and link the
`EVIDENCE.md` entry that resolved it. Ranges follow EVIDENCE.md (Q-0001.. survey and front
end, Q-0100.. `default.dat` and `ge.dll`).

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

### Q-0001 — What are the wave blobs' trailing byte and their RIFF size (length + 2)?
- **Context:** E-0010, `Wave.WAVE` in `.wxs`/`.dxw`.
- **What we checked:** the corpus only; DelphiX's TWave writer not yet located in
  Gilbert.exe (unit `wave`).
- **Observed range:** tail byte 0 in all 58 blobs; RIFF size field = blob length + 2 in all.
- **Blocks:** nothing for playback (the `fmt `/`data` chunks are consistent); matters only
  for writing the files back.
- **Status:** open

### Q-0002 — What do the control-map cell values mean?
- **Context:** E-0011, `ctrl<room>.map` grid, values 0..29.
- **What we checked:** the corpus: 0 and 1 dominate (walkable floor and walls by their
  shapes in the ASCII plots), 2..29 form small blocks at doorways and objects. The users of
  the grid (`GEPathNewPath`, `GEWalkmapAreaHit`, Gilbert.exe's room code) not yet read.
- **Observed range:** 0..29; at most 17 distinct values per room.
- **Blocks:** walking, room exits and hot spots.
- **Status:** open
