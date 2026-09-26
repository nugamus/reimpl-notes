# Formats (Peintre engine, Mission Sunlight)

One row per recovered format: status here, the Kaitai spec next to it (`<fmt>.ksy`), the
validator in `engines/peintre/tools/parsers/<fmt>.py` (with `--selftest`), the proof in
`EVIDENCE.md`. A format is done only when its validator passes 100% of that type in
`games/mission-sunlight/discs/cd`, every byte consumed.

| Format | Files | Validator | Spec | Evidence | Status |
|---|---:|---|---|---|---|
| `.BFG` scene bundle | 15 (594 entries: 15 `.3DC`, 504 `.3DM`, 48 `.3DA`, 27 `.3DI`) | `bfg.py` | `bfg.ksy` | E-0013 | done (container and packing; entry payloads below) |

## `.BFG` — scene bundle (E-0013)

`u32 count`, 100 directory slots of `{char name[28]; u32 offset; u32 size}`, 4 zero
bytes, then the packed entries from 0xE18. The engine reads the whole file
(`LoadSceneFile` 0x42e85c), finds an entry by exact name among the first `count` slots and
unpacks it into the 3D heap (0x42e6e0 → 0x466bc3). Packing: byte 0 = 1 stored, else LZ
(12-bit distance, 4-bit length + 1, 16 flags per u16, LSB first). All 594 entries in the
corpus are LZ. Every unpacked entry starts with the 20-byte engine object header whose
only meaningful field is `type` (1 `.3DC`, 3 `.3DM`, 4 `.3DA`, 5 `.3DI`; the loader
accepts 0..6, CheckHeader 0x4348c0). Names after their NUL and unused slots hold leftover
memory of the authoring tool (unused slots in 5 files), as do the other header fields
(e.g. `0xCDCDCD` debug-heap fill in the packed entries' unused bytes).
