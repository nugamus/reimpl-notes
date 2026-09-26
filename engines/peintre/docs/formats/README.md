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
| `.TGP` full-screen / panorama image | 134 (110 single 640x480, 24 chunked panoramas) | `tgp.py` | `tgp.ksy` | E-0100, E-0101 | done (LZWCRYO constants open, Q-0100) |
| `.SPR` sprite bank | 289 (12 RLE, 115 band, 10 raw8, 152 raw16; 5,827 frames) | `spr.py` | `spr.ksy` | E-0102, E-0103 | done |
| `.TGA` 2D overlay / cursor | 104 (11 with TGA 2.0 footer) | `tga.py` | `tga.ksy` | E-0104 | done |
| `.HNM` movie (Cryo HNM6) | 95 (94 `.HNM` + extensionless `A13_052B`; 21,363 IX, 80 AA, 18,208 BB chunks) | `hnm.py` | `hnm.ksy` | E-0200..E-0203, E-0206 | done |
| `.CVY` movie mask | 37 (2,900 frames; 24 opened by the game, 13 never) | `cvy.py` | `cvy.ksy` | E-0204, E-0205 | done (colour meaning Q-0150) |
| `.AWF` bitmap font | 2 (1 fixed, 1 proportional) | `awf.py` | `awf.ksy` | E-0105 | done |

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

## `.SPR` — sprite banks (E-0102, E-0103)

`u32 head`: bit 31 = raw frames, bit 30 = band frames (only without bit 31), bits 0..29 =
palette end (4 = no palette, 772 = 256 RGB triples, 8 bits per channel; the engine keeps
the top 5/6/5 bits). From there to EOF is the bank: `u32 offsets[n]` (n = offsets[0] / 4,
relative to the bank; the last frame ends at EOF), then frames `{u16 a; u16 b; data}`,
each zero-padded to a multiple of 4. Four kinds:

| Kind | Files / frames | a, b | Data | Drawn at |
|---|---|---|---|---|
| rle (bits 00) | 12 / 124 (cursors, CURSOPT, LCAPS, portraits) | width, height | `b` RLE rows over palette indices | centred: `(x − a/2, y − b/2)` |
| band (bits 01) | 115 / 3,619 | first screen row, row count | `b` RLE rows, 640 px wide | `(0, a)`, x/y ignored; `a = b = 0` is empty |
| raw8 (bit 1, palette) | 10 / 146 | width, height | `a*b` palette indices | `(x, y)`, opaque |
| raw16 (bit 1, no palette) | 152 / 1,938 | width, height | `a*b` RGB565 | `(x, y)`, opaque |

RLE row: `0x80` ends the row; `c < 0x80` skips `c` pixels (transparent: the only
transparency in SPR); `c > 0x80` is followed by `c & 0x7F` palette indices. Band frames
are full-width strips drawn over a 640×480 background.
No ScummVM reader applies (cryomni3d's `SPRI` sprites are a different, big-endian format).

## `.TGA` — 2D overlays and cursors of the 3D part (E-0104)

Plain Truevision TGA, one variant: type 2, 16 bits, no id, no colour map, origin 0,
descriptor 0 or 1, pixels **X1R5G5B5 bottom row first**, then optionally (11 files) the
26-byte TGA 2.0 footer. The engine reads only width/height (offset 12) and the pixels
(offset 18), flips the rows and converts to RGB565 on 565 screens. The keyed blitter skips
**pure green** (0x03E0 in 555, 0x07C0 in 565). ScummVM's `Image::TGADecoder` parses it,
but treats the descriptor-1 files as ARGB1555 with bit 15 = 0, i.e. fully transparent:
convert its surface as RGB555 ignoring alpha (or read the 18-byte header directly).

## `.AWF` — bitmap fonts (E-0105)

A 38-byte header that the engine keeps as the font record (five u32 offsets into the data:
glyphs, glyph table, widths, spacing a, spacing b; then `u8 first_char, count, baseline,
unk_1f; u16 flags` (bit 0 = proportional)`, fixed_width, height`), then the data: `u32
glyph_table[count]` (offsets from the glyph base), 1-bpp glyphs (`height` rows of
`ceil(w/8)` bytes, MSB = leftmost, set bit = text colour, clear = untouched), and for a
proportional font three `count`-byte tables: width, spacing a (u8), spacing b (s8).
Text is drawn from `y − baseline`; the pen advances by `fixed_width`, or by
`width + spacing_a + spacing_b`; bytes below `first_char` draw nothing and do not advance.
A shadow variant also blacks the pixel one down and one right of each ink pixel. The
measure routine counts `fixed_width + 1` per char for a fixed font, one more than drawing.
TOPAZ8: fixed 8×8, chars 32..165. TROBO12: proportional, 17 rows, chars 32..122 (next to
it, `TROBO.TTF` is a TrueType font, not read by this loader). ScummVM's Cryo font reader
(`CRYOFONT`) is a different format.

## `.HNM` — movies, Cryo HNM6 (E-0200..E-0203, E-0206)

64-byte header (`HNM6`, audio flags, bpp 16, 640x480 (the EXE accepts nothing else),
file size, frame count, max video payload, author and copyright strings), then one
superchunk per frame (`u32 size | flags << 24`, flags 0 in the corpus) and a zero u32 at
the end. Chunks `{u32 size, char type[2], u16 flags}` are padded to 4 bytes. Three chunk
types occur: `IX` video in every frame (frame 0 always a key frame, `quality < 0`), `AA`
in frame 0 (a 32-byte `CRYO_APC 1.20` header, then the sound for the first 32 frames)
and `BB` in later frames (one frame of sound, exactly `AA`'s ADPCM size / 32 in every
file). Sound: 15 silent, 59 22050 Hz mono, 21 22050 Hz stereo. The `IX` payload has a
28-byte header (quality, five stream offsets, then `unk_18` = `end` again) whose `end`
equals the payload size in all 21,363 frames.

**ScummVM:** `Video::HNMDecoder` reads every file unchanged: it handles `IX`, `AA`, `BB`
(the EXE's walker also accepts `IV`, absent here; ScummVM's `IW` is absent too), its
24-byte frame header ends before `unk_18`, and its `(samples & 31) == 0` and equal-`BB`
asserts hold for all 80 sound files. What the engine must add: a silent movie's frame
delay is 80 ms in the EXE (ScummVM's HNM6 default is 66 ms; the constructor takes the
delay); with sound the EXE runs a `1000 / fps` ms timer (83 ms; 80 ms for `a03_05a`, 1,764
samples per frame) where ScummVM clocks frames by the samples (1,836 mono or 1,837
stereo per frame, 83.3 ms). Movies with a table entry are drawn into a rectangle with a
CVY mask on top (below).

## `.CVY` — per-frame movie masks (E-0204, E-0205)

`u32 frame_count, u32 buffer_size, u32 offsets[frame_count]`, then one Cryo HLZ stream
per movie frame (the TGP packing, E-0101), each padded to 4 bytes with leftover memory.
A frame unpacks to a run mask: a byte `1..0x7F` skips lines, `0` repeats the previous
line, `0x80 | n` starts a line of `n` run bytes (`0x80 | k` paints `k + 1` u32 = two
pixels each, else skips `k + 1` u32); every line's runs add up to 320 u32 (640 pixels),
counted from the movie rectangle's origin. 130 of the 2,900 masks paint nothing (`7F 7F
7F 63`, 480 lines skipped).

The game's movie table (0x4a7a08, 68 entries `{char name[12]; u32 has_cvy; u32 x, y, w,
h; u32 sound_on}`) says which movie has a mask: Movie_Open (0x414ace) plays the HNM
into the rectangle (the top-left `w x h` of the 640x480 frame is copied to `(x, y)`) and
paints mask `n` over frame `n` in colour 0x116A (5-6-5) or 0x08AA (5-5-5), the same dark
blue, RGB about (16, 44, 82). 24 table entries have a CVY and all 24 files exist; 13 CVY
files (`A03_023A`..`L`, `A14_032A`) belong to entries with `has_cvy = 0` and are never
opened. Frame counts equal the HNM's except in four files: `A13_052B.CVY` has 101 masks
for the 94-frame `A13_052B.HNM` (the extensionless `A13_052B` has 101 frames, Q-0151),
and three of the unused ones. For the 24 opened files every mask covers at least the
rectangle's height and paints nothing below it.

