# `.S3D` — what the corpus proves

Working notes, not a spec. `docs/formats/s3d.ksy` is the canonical artefact once a
validator consumes every byte of every file (CLAUDE.md rule 2).

Corpus: 1 `.S3D` file (`U02/anim/U02_02/U02_02.S3D`), 73,916 bytes, version 0.95.

## Proven

`.S3D` is **not** a new format — it is a super-container that sequences the four
already-recovered per-format record readers against a single shared file cursor. The
loader at `x3d.dll` `0x100010e1` opens the file, reads 32-byte signature
`(c) 1998 4X Tech. 0.95 (S)`, then calls, in order:

| Loader function | Section shape | Equivalent standalone format |
|---|---|---|
| `thunk_FUN_100148e0` (`0x100148e0`) | camera records | `.C3D` body |
| `thunk_FUN_10014d50` (`0x10014d50`) | light records | `.L3D` body |
| `thunk_FUN_10011450` (`0x10011450`) | material records | `.O3D` body |
| `thunk_FUN_10012920` (`0x10012920`) | object records | `.O3D` body |
| `thunk_FUN_10012ee0` (`0x10012ee0`) | animation records | `.A3D` body |

Each section starts with a u32 count, then that many records. No per-section signature
— the cursor advances straight from one section into the next. This is why the engine
can write a complete scene out as a single `.S3D` instead of carrying five separate
files; the on-disk shapes are byte-for-byte the same as the standalone formats.

`X3d_Load_Sdk_s3d` then loops over each populated section and calls
`X3d_Scene_Add_*` (`Add_Camera`, `Add_Light`, `Add_Object`, `Add_Animation`) to attach
every record to the scene. The materials array is passed into the object reader so face
material indices can be resolved, and the lights array is also passed through.

## Refuted

None — the parser is a thin wrapper that reuses the already-validated per-format
record readers, and the layout matches the loader decomp exactly on first try.

## Observed

| File | Version | Bytes | Cams | Lights | Mats | Objects | Anims |
|---|---|---:|---:|---:|---:|---:|---:|
| `U02/anim/U02_02/U02_02.S3D` | 0.95 | 73,916 | 0 | 0 | 5 | 53 | 53 |

The 1-to-1 match between object count and animation count is consistent with the
animation file structure: each object has its own paired animation that animates the
same vertices. No cameras and no lights in this scene — those live in `.C3D`/`.L3D`
files alongside.

## Why this matters for the family claim

E-0020 said `.O3D/.A3D/.L3D` form the family. Adding `.C3D` (E-0021) made it four.
Adding `.S3D` makes it five, but `.S3D` is a meta-format: it is the engine's own
mechanism for combining the others. The "one container family" claim is now
strengthened: the engine ships its own multiplex of the per-format record shapes.

## Next step

Move on to `.MAT` — plain ASCII per the loader-list note; the loader decompile can be
skipped and the format parsed directly off the sample bytes. Then `.DMF` (the biggest
remaining engine format, 518 files / 48.4 M / 8 magics). `.BMP`, `.BIN`, `.FRA`,
`.CFG` follow.