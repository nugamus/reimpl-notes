# `.L3D` — what the corpus proves

Working notes, not a spec. `docs/formats/l3d.ksy` is the canonical artefact once a validator
consumes every byte of every file (CLAUDE.md rule 2).

Corpus: 5 `.L3D` files, 5,718 bytes, one distinct signature.

## Proven

`.L3D` shares the engine's `(c) 1998 4X Tech.` 32-byte signature with `.O3D` and `.A3D`,
with `(L)` in place of `(O)` or `(A)`. Same stream-read primitives inside `x3d.dll`
(`FUN_1000ba90` u32, `FUN_1000baf0` u8, `FUN_1000bb20` f32, `FUN_1000bb50` n-bytes). One
container family, three visible extensions — adding `.L3D` confirms the pattern is across
the whole engine, not a one-off.

`X3d_Load_Sdk_l3d` (`x3d.dll` `0x100012fd`) is a thin wrapper that opens the file, reads
32 bytes, compares the signature against both the `0.95 (L)` and `1.00 (L)` strings, sets
the loader-global `DAT_1002d224` accordingly, then calls the real per-record reader at
`FUN_10014d50` (`x3d.dll` `0x10014d50`). That function reads the rest.

The per-light record layout is taken straight off the read sequence in `FUN_10014d50`:

| Bytes | Field |
|---:|---|
| 32 | name (NUL-padded) |
| 12 | position (3×f32) |
| 3 | color (3×u8 RGB) |
| 12 | extra_floats (3×f32, opaque) |
| 8 | extra_u32s (2×u32, opaque) |
| 4 | is_spot |
| _20_ | _[if `is_spot != 0`]: spot_target (3×f32), spot_angles (2×f32)_ |

Per-light fixed size: 71 bytes omni, 91 bytes spot.

`FUN_10014d50` then calls either `X3d_Light_Create` (`0x10001078`) — omni — or, after the
spot branch, `X3d_Spot_Light_Create` (`0x10001253`). The original `param_2` it receives
from `X3d_Load_Sdk_l3d` is the count, and `piStack_2c` becomes the array of created light
pointers that `X3d_Scene_Add_Light` then registers.

## Refuted

None — the first-try layout parsed all five corpus files. Because the per-light record has
no flags inside it (the conditional is just `is_spot`, which expands a fixed-size suffix),
this is a simpler shape than `.O3D` and the "stride hypothesis" trap doesn't apply.

## Observed

| File | Version | Lights | Spot | Notes |
|---|---|---:|---:|---|
| `U01/static/LIGHTS.L3D` | 0.95 | 5 | 0 | one per `Omni01..05`, RGB white-ish |
| `U03/Static/LIGHT.L3D` | 0.95 | 23 | 0 | 23 omni |
| `U03/Static/LUMIERE.L3D` | 0.95 | 23 | 0 | duplicate, French name |
| `U06/Static/LIGHT.L3D` | 0.95 | 4 | 0 | 4 omni |
| `U33/Static/LIGHT.L3D` | 0.95 | 23 | 0 | same 23 |

The `extra_floats` slot is almost always `(104.8, 125.2, ±1.0)` — three values, the third
nearing `±1`. Consistent with one being intensity (the `X3d_Light_Set_Multiplier` export
covers that), the others not named. The `extra_u32s` slot is almost always `(0, 1)`. Both
slots are flagged `extra_*` in `tools/parsers/l3d.py` per CLAUDE.md rule 5.

## Spot branch — no corpus sample

Every `.L3D` in the corpus has `is_spot == 0`. The spot branch is parsed (3 f32 target + 2
f32 angles) and the test exercises it, but the validator has no sample to cross-check the
branch against. Recorded as Q-0013.

## Next step

Move on. `.C3D` and `.S3D` share the same `(X)` signature scheme and use the same four
stream primitives — same shape of loader, same decompile-then-parse loop, the only change
is the per-record function (`FUN_10014d50` for lights, an analogous `FUN_1001xxxx` for the
next format). `.C3D` is the natural next pick: 6 files, 648 bytes, smallest corpus next
after `.L3D`.
