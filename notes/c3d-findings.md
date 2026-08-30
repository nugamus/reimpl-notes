# `.C3D` — what the corpus proves

Working notes, not a spec. `docs/formats/c3d.ksy` is the canonical artefact once a
validator consumes every byte of every file (CLAUDE.md rule 2).

Corpus: 6 `.C3D` files, 648 bytes, one distinct signature.

## Proven

`.C3D` shares the engine's `(c) 1998 4X Tech.` 32-byte signature with `.O3D`, `.A3D`
and `.L3D`, with `(C)` in place of the others. Same stream-read primitives inside
`x3d.dll` (`FUN_1000ba90` u32, `FUN_1000baf0` u8, `FUN_1000bb20` f32, `FUN_1000bb50`
n-bytes). One container family, four visible extensions — adding `.C3D` confirms the
pattern is across the whole engine, not a one-off.

`X3d_Load_Sdk_c3d` (`x3d.dll` `0x1000124e`) is a thin wrapper that opens the file,
reads 32 bytes, compares the signature against both the `0.95 (C)` and `1.00 (C)`
strings, sets the loader-global `DAT_1002d224` accordingly, then calls the real
per-record reader at `FUN_100148e0` (`x3d.dll` `0x100148e0`). That function reads
the rest, allocating an array of `count` cameras via `X3d_Camera_Create`
(`0x10001406`) and filling each one's struct fields in the read sequence below.

The per-camera record layout is taken straight off the read sequence in
`FUN_100148e0`:

| Bytes | Field | Camera struct offset |
|---:|---|---|
| 32 | name (NUL-padded) | `+0x0C` |
| 4  | f32 | `+0x2C` |
| 4  | f32 | `+0x30` |
| 4  | f32 | `+0x34` |
| 4  | f32 | `+0x3C` |
| 4  | f32 | `+0x40` |
| 4  | f32 | `+0x44` |
| 4  | f32 | `+0x54` |
| 4  | f32 | `+0x58` |
| 4  | f32 | `+0x4C` |
| 4  | f32 | `+0x50` |

Per-camera fixed size: 72 bytes.

The struct offsets are non-monotonic in file order — `+0x54`/`+0x58` come before
`+0x4C`/`+0x50` — because `bb20` only advances the file cursor; the destination
offset is a fixed camera-object slot, not the next byte position. The parser tracks
file order, not struct order.

The loader also writes a u32 of `1` to the camera struct at `+0x08` before reading
the name — that field is not part of the file, so the parser does not see it.

## Refuted

None — the first-try layout parsed all six corpus files. Because the per-camera
record has no flags inside it (every camera reads exactly 32 + 40 bytes), this is an
even simpler shape than `.L3D`.

## Observed

| File | Version | Cameras | Notes |
|---|---|---:|---|
| `U02/static/CAMERA.C3D` | 0.95 | 1 | name `Camera03` |
| `U04/Static/CAMERA.C3D` | 0.95 | 1 | |
| `U04/Anim/U04_03_Lunettes/CAMERA.C3D` | 0.95 | 1 | |
| `U05/Static/CAMERA.C3D` | 0.95 | 1 | |
| `U06/Static/CAMERA.C3D` | 0.95 | 1 | |
| `U07/Static/CAMERA.C3D` | 0.95 | 1 | |

All six files are version 0.95; all carry exactly one camera; all are 108 bytes
(32-byte signature + u32 count + 72-byte record).

The 10 f32s are flagged `params` and given no semantic names per CLAUDE.md rule 5.
The plausible split into three vec3s at `+0x2C`, `+0x3C`, `+0x4C` (position, target,
up) is recorded as Q-0014 with no engine-side evidence yet.

## Next step

Move on to `.S3D` — same family, same primitives, same decompile-then-parse loop.
`.MAT` is plain ASCII per the loader-list note; the loader decompile can be skipped
and the format parsed directly off the sample bytes. `.DMF` is the biggest remaining
engine format (518 files / 48.4 M / 8 distinct magics) and benefits from having the
family claim locked in across `.S3D`/`.MAT` first. `.BMP`, `.BIN`, `.FRA`, `.CFG`
follow.