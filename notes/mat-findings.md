# `.MAT` — what the corpus proves

Working notes, not a spec. `docs/formats/mat.ksy` is the canonical artefact once a
validator consumes every byte of every file (CLAUDE.md rule 2).

Corpus: 5 `.MAT` files, 4,858 bytes, no magic (plain ASCII).

## Proven

`.MAT` is a plain ASCII material script. No magic, no binary primitives, no per-record
signatures — every line is a literal key=value pair. The 03-HANDOFF-PHASE-2.md §2
loader-list note records that `.MAT` is plain ASCII beginning with `;-------...`; the
loader decompile step is skipped per that note and the layout is taken directly off
the sample bytes.

Structure (lines are zero-indexed, post-`splitlines`):

| Lines | Content |
|---:|---|
| 0 | `;-------...` (banner; `;` + 47 dashes, verified length-48) |
| 1 | `; <path>` (source authoring path comment; not a runtime path) |
| 2 | `;-------...` (banner) |
| 3.. | zero or more material blocks separated by optional banner lines |

Per material block, exactly 16 lines in fixed order:

| Line | Key | Shape |
|---:|---|---|
| 0 | `MATERIAL` | `="<name>"` |
| 1 | `TYPE` | `=<type>` (`MATERIAL_GOURAUD_RGB`, `MATERIAL_SELF_ILLUM`) |
| 2..5 | `AMBIENT`, `DIFFUSE`, `SPECULAR`, `LIGHT_COLOR` | `=<r>,<g>,<b>` |
| 6..7 | `SHININESS`, `SHININESS_STRENGTH` | `=<int>` |
| 8..11 | `TRANSPARENCY`, `BINARY_OPACITY`, `TWO_SIDED`, `TILING` | `=<int>` |
| 12 | `TEXTURE_MAP` | `="<path>"` |
| 13 | `REFLECTION` | `=<int>` |
| 14 | `LIGHT_MAP` | `="<path>"` (empty `""` allowed) |
| 15 | `REFLECTION` | `=<int>` (note: duplicated) |

The duplicated trailing `REFLECTION=` line is a stable artefact of every corpus sample
— every one has both, and both are non-negative integers. The parser captures both
into the `ints` list under the repeated `REFLECTION` key.

## Refuted

None — the first-try layout parsed all five corpus files, including the empty
`U02_03LOD.MAT` (144 bytes, header only, no materials).

## Observed

| File | Bytes | Materials | Notes |
|---|---:|---:|---|
| `U02/anim/U02_02/U02_02.MAT` | 1,879 | 5 | path `D:\U02\ANIM\U02_02\U02_02.MAT`, mix of types |
| `U02/anim/U02_03/U02_03LOD.MAT` | 144 | 0 | header-only; no materials |
| `U02/anim/U02_05/U02_06.MAT` | 484 | 1 | single material, GOURAUD |
| `U04/Anim/U04_02/OUVRE02.MAT` | 1,863 | 5 | mix of GOURAUD and SELF_ILLUM |
| `U05/anim/U05_05/ACTION01.MAT` | 488 | 1 | single material, GOURAUD |

`TYPE` is observed only as `MATERIAL_GOURAUD_RGB` or `MATERIAL_SELF_ILLUM`. The path
comments inside `.MAT` files reference source authoring paths under `D:\U02\...`,
`D:\U02GARE\...`, `D:\U04\...` — never the shipped `Data\` location. None are
runtime-meaningful; they are authoring-time breadcrumbs.

`LIGHT_MAP=""` is always empty in the corpus. `TEXTURE_MAP` is always non-empty and
always ends in `.TGA`, matching Q-0011 (the `.O3D` family references `.TGA` textures
that the corpus does not carry).

## Why no loader decompile

The handoff §2 explicitly waives the loader-decompile step for `.MAT` because the
sample bytes uniquely determine the layout — every material block is 16 fixed lines in
documented order, with no flags or variable-length sections. The format is provable
from sample bytes alone; decompiling the loader would not strengthen the spec and could
only re-derive what the corpus already shows. The EVIDENCE entry for this format
cites the handoff and the per-file sample structures, not a Ghidra address.

## Next step

Move on to `.DMF` — 518 files / 48.4 M / 8 distinct magics, the biggest remaining
engine format. The handoff recommends doing `.DMF` last among the engine formats so
the family claim is locked in across the smaller ones; that order is preserved here.