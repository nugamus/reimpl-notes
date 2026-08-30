# `.O3D` — what the corpus proves so far

Working notes, not a spec. `docs/formats/` stays empty until a validator consumes every
byte of all 596 files (CLAUDE.md rule 2). Two structural hypotheses were tested here and
**refuted**; they are written down so nobody re-derives them.

Corpus: 596 `.O3D` files, 14.0 M, one distinct magic (E-0008).

## Proven

The first 36 bytes are uniform across all 596 files.

| Offset | Size | Content |
|---:|---:|---|
| 0 | 27 | `(c) 1998 4X Tech. 0.95 (O)\0` — byte-identical in all 596 files |
| 27 | 1 | always `0x78` |
| 28 | 1 | varies; 41 distinct values, all in `0xb7`-`0xc6` |
| 29 | 1 | always `0xa1` |
| 30 | 1 | always `0x63` |
| 31 | 1 | always `0x00` |
| 32 | 4 | little-endian count, range 0-87; 171 files hold 0 |

Bytes 27-30 read as a little-endian u32 give values clustered around 1,671,54x,xxx, all
differing only in the second byte. Consistent with a build stamp or an ID, inconsistent
with a 1998 Unix timestamp. Not resolved.

The signature ends `(O)`, matching the extension. Worth checking whether `.A3D`, `.S3D`,
`.L3D` and `.C3D` carry the same signature with a different letter — that would make one
container family rather than five formats.

Every NUL-terminated string recovered from the region that looks like texture references
ends in `.TGA` (1,476 occurrences, no other extension). The corpus contains no `.TGA`
files at all — 381 `.BMP` and nothing else image-shaped (E-0008) — so either the loader
rewrites the extension or these are authoring-time paths. Logged as Q-0011.

## Refuted

Two fixed-stride readings looked right on the first few files and both failed the corpus:

1. **"Materials are 112-byte records starting at offset 36."** The u32 at
   `36 + 112 * count` is a plausible small object count in all 596 files, which is why it
   survived first contact. But treating offsets +0 and +72 of each record as NUL-padded
   32-byte name fields fails for 541 of 2,133 candidate material records.
2. **"Objects are 192-byte records."** The stride never overruns end-of-file in any of the
   596 files — but that only constrains the total, and it is a weak constraint. Reading
   +0 and +36 of each record as name fields fails 18,259 times across 10,253 candidate
   object slots.

The lesson is the one CLAUDE.md rule 2 already states: "no overrun" is not evidence of a
correct layout. A field-level check refuted in minutes what a length check had endorsed.

## Next step

Decompile the loader rather than guess further. `X3d_Load_Sdk_o3d` is the entry point — it
is imported by both EXEs and reached from `U99.cpp` `0x00464ead` in `MissionD.exe` (see
`import-map.md`). Its callee chain inside `x3d.dll` defines the record layout exactly, and
`x3d.dll` has no assert strings to shortcut with (E-0011).
