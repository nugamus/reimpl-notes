# Formats (Peintre engine, Mission Sunlight)

One row per recovered format: status here, the Kaitai spec next to it (`<fmt>.ksy`), the
validator in `engines/peintre/tools/parsers/<fmt>.py` (with `--selftest`), the proof in
`EVIDENCE.md`. A format is done only when its validator passes 100% of that type in
`games/mission-sunlight/discs/cd`, every byte consumed.

| Format | Files | Validator | Spec | Evidence | Status |
|---|---:|---|---|---|---|
| `.BFG` scene bundle | 15 (594 entries: 15 `.3DC`, 504 `.3DM`, 48 `.3DA`, 27 `.3DI`) | `bfg.py` | `bfg.ksy` | E-0013 | done (container and packing; entry payloads below) |
| `.3DC` scene (in BFG) | 15 | `obj3d.py` | `obj3d.ksy` | E-0014 | layout done, every byte reached; field meanings partly open |
| `.3DM` texture (in BFG) | 504 | `obj3d.py` | `obj3d.ksy` | E-0015 | done (4 odd sizes, Q-0003) |
| `.3DA` animation (in BFG) | 48 | `obj3d.py` | `obj3d.ksy` | E-0016 | layout done; key meaning tentative (Q-0004) |
| `.3DI` boxes (in BFG) | 27 | `obj3d.py` | `obj3d.ksy` | E-0016 | layout done; face record fields open |
| `.TGP` full-screen / panorama image | 134 (110 single 640x480, 24 chunked panoramas) | `tgp.py` | `tgp.ksy` | E-0100, E-0101 | done |

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

## `.3DC` / `.3DM` / `.3DA` / `.3DI` — objects inside a BFG (E-0014..E-0016)

Memory images of the authoring tool's structures, relocated on load. `obj3d.py` follows
every pointer the loader relocates and requires the structures to cover each body
exactly once; 594/594 pass. Corpus totals: 560 nodes, 57,720 vertices, 39,073 polys in
1,235 face groups (types 3: 839, -6: 384, 1: 11, -4: 1), 500 materials; 504 textures;
2,016 animation tracks (4,967 rotation and 4,637 position keys); 27 box sets (6,421
vertices, 7,695 faces).

- **3DC**: node table (every node, the root first), materials (name, texture name), then
  the tree. Node: name[12], flags, parent/child/sibling, local position (s32) and
  rotation (3x3 Q15), world position and rotation (runtime), then counts and pointers of
  vertices (40 B: flags, xyz s32, runtime), UVs (16.16), vertex normals and face normals
  (Q15), face groups (per material: type, material name, polys) and vertex groups (per
  face-group type, runtime per-vertex items). A poly has three corners (vertex, vertex
  normal, vertex-group item), a face normal, and three UVs when the group is textured
  (poly size 0x44; 0x38 without UVs).
- **3DM**: a 32-level x 256-colour shade table of RGB565 (in the high half of u32s) and a
  256 x 256 8-bit texel map. The drawers read texels at `table + 0x8000`.
- **3DA**: tracks of rotation keys (time, 4 x Q15) and position keys (time, xyz).
- **3DI**: collision boxes (`BOX*.3DI`, loaded by `C_Monde::LoadScene` and
  `LoadBox<Scene>`): vertices, 0x60-byte faces that point at vertices, 12-byte items.

## `.TGP` — full-screen and panorama images (E-0100, E-0101)

`u32 width, u32 height`, then one of two bodies. The caller picks the loader, not the
file; the magic tells them apart. **Chunked** (`Tgp_Load` 0x40d9c0, 24 files, panoramas
of 1500 px on one side): `u32 count`, then `count` × `{u32 packed_size; u32
unpacked_size; HLZ stream}`, unpacked back to back into `width*height*2` bytes.
**Single** (`Tgp_Load2` 0x414779, 110 files, all 640×480): a 0x24-byte header from
offset 8 (`unk 0x24`, `"LZWCRYO\0"`, `unk 0, 0, 256, 1`, unpacked size, packed size) and
one HLZ stream to EOF; the engine uses only the packed size and unpacks straight into the
640×480 screen buffer. Pixels are **RGB565**, top row first; on RGB555 surfaces the
engine shifts red/green down (0x40b266). HLZ is Cryo's LZ (0x430700), bit for bit the
one ScummVM already has as `Image::HLZDecoder::decodeFrameInPlace` (`image/codecs/hlz.h`):
reuse it. Every stream ends with its end marker exactly at the end of its chunk.
