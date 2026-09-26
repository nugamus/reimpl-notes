# Formats

One file for every recovered format: status here, the Kaitai spec next to it
(`<fmt>.ksy`), the validator in `engines/x3d/tools/parsers/<fmt>.py`, the proof in `EVIDENCE.md`.
A format is done only when its validator passes 100% of the corpus, every byte consumed.

| Format | Files | Validator | Spec | Evidence | Status |
|---|---:|---|---|---|---|
| `.O3D` mesh | 596 | `o3d.py` | `o3d.ksy` | E-0016..18, E-0054 | done |
| `.A3D` animation | 429 | `a3d.py` | `a3d.ksy` | E-0020, E-0055 | done |
| `.L3D` lights | 5 | `l3d.py` | `l3d.ksy` | E-0019 | done |
| `.C3D` cameras | 6 | `c3d.py` | `c3d.ksy` | E-0021 | done (10 f32s opaque, Q-0014) |
| `.S3D` scene | 1 | `s3d.py` | `s3d.ksy` | E-0022 | done |
| `.MAT` material script | 5 | `mat.py` | `mat.ksy` | E-0023 | done |
| `.BMP` | 381 | `bmp.py` | `bmp.ksy` | E-0024 | done |
| `.BIN` chunk container | 109 | `binchunk.py` | — | E-0025 | container done; payloads below |
| `#OBJECTS#` (INFOOBJ.BIN) | 9 | `infoobj.py` | `infoobj.ksy` | E-0026, E-0072 | done |
| `#ACTIONS#` (INFOACT.BIN) | 9 | `infoact.py` | `infoact.ksy` | E-0071 | done |
| `#SCENE#` `#CAMERA#` (SCENE.BIN) | 9 | — | below | E-0039 | done |
| `#GAME#` (App.bin) | 1 | — | below | E-0037 | first 30 bytes read: start scene name |
| `#INDEX#` (Sound/*.bin lip sync) | 81 | `lip.py` | `lip.ksy` | E-0124 | done |
| `#APP#` (App.bin) | 1 | — | — | — | open |
| `.X3D` scene script | 24 | `x3d.py` | this file (text) | E-0036 | done |
| `.DMF` texture | 518 | `dmf.py` | `dmf.ksy` | E-0038 | done (`fb22`/`fb23` opaque) |
| `.FRA` 2D frame | 25 | `fra.py` | `fra.ksy` | E-0100 | done (view `unk_7`/`unk_8`, list fields opaque) |
| `.CFG` (`x3dcfg.cfg`) | 38 | `cfg.py` | `cfg.ksy` | E-0103 | done; not read by the game |
| `Media.txt` (2dbit multi-part images) | 1 | — | `ui.md` (Gallery, `Loupe`) | E-0454 | fields 1..4 read (name; id; cols,rows; file); trailing empty fields opaque; no validator |
| Save files (`Save/`, not corpus) | 9 samples | `savegame.py` | `savegame.ksy` | E-0180..E-0183 | done over the samples; `unk_*` fields open (Q-0101, Q-0103) |

Loader rule learned the hard way: the engine formats (`.O3D`/`.A3D`/`.L3D`/`.C3D`/`.S3D`,
and `.DMF` through the host's file callbacks, E-0038) are read by `x3d.dll`; the
game-specific ones (`.BIN`, `.X3D`, `.FRA`) by `MissionMonet.exe`.

## `.FRA` — 2D frame (E-0100)

`u32 count`, then per object: a 4-byte class tag, a 36-byte view (`id, x, y, w, h,
visible, parent, unk_7, unk_8`), a class body of fixed size, and properties (4-byte tag +
fixed body) up to a 0 tag. Tags are MSVC multi-character constants, so `'#BIT'` reads
`TIB#` in the file. Class and property sizes are the read lengths of their constructors in
`MissionMonet.exe`; see `fra.ksy`. Corpus: 106 objects, 196 properties (65 `ucg@`, 58
`RCS@`, 53 `LIH@`, 20 `GIH@`). `nCC#` / `nIC#` (7 video frames) are unknown to both EXEs.
Behaviour: `engines/x3d/docs/spec/ui.md`.

## `.CFG` — `x3dcfg.cfg` (E-0103)

Authoring-tool settings in `Anim/`, `Static/` and `cinematiques/` folders: 3 f32, 6 u32,
`u32 n`, `n` × 260-byte paths on the authors' machine (`D:\MissionD\Data\U01\maps`).
Nothing in the shipped binaries reads them; the engine ignores them.

## `.X3D` — scene script (E-0036)

Text, read whole and parsed by `load::load_262`. Whitespace (space, tab, CR, LF) is
skipped; `;` comments to end of line; otherwise one of these keywords, case-insensitive,
each followed by one `"`-quoted field (a field ends at `"`, CR or `,`):

| Keyword | Field | Effect |
|---|---|---|
| `scene=` | `"path.s3d"` | `X3d_Load_Sdk_s3d` (unused in the corpus) |
| `object=` | `"path.o3d"` | load; becomes the "last object"; hidden if the path starts `static\col` (collision meshes) |
| `lod=` | `"path.o3d,distance"` | load and attach to the last object as a level of detail at `distance` |
| `animation=` | `"path.a3d[,fps]"` | attach to the last object, fps default 30 |
| `light=` | `"path.l3d"` | load lights; every light includes every object |
| `camera=` | `"path.c3d"` | load cameras |

Paths are relative to `Data/<first three characters of the script name>/` (U00 uses
`U04/`), with `\` separators. No `.ksy`: Kaitai does not describe token grammars; the
validator is the spec's executable form.

## `.DMF` — texture (E-0038)

`u16 0xfb00`, `u32 file size`, then chunks `u16 id, u32 size` (size counts the 6-byte
header). See `dmf.ksy`. Palette entries are B, G, R, 0; 15-bit pixels are 555, 16-bit
565. Maps are referenced from `.O3D` materials by `.TGA` names, which the loader rewrites
to `.dmf`. The EXE registers `Data/<unit>/Maps\` as the scene's map search path
(`XScene_70` → `FUN_0041dd30`, a list at scene `+0x1b0`); that the host file callback
searches that list is inferred, not traced. Every map's width and height are powers of two (E-0611).

## `SCENE.BIN` payloads (E-0039)

`#SCENE#`: u32 r, u32 g, u32 b (ambient light), f32 scale (the unit that eye height and
collision sphere derive from). `#CAMERA#`: f32 fov (degrees, horizontal), f32 sphere
radius, f32 sphere Z offset, f32 `unk_speed` (read, then overwritten with 2.0).

## `.O3D` — what the corpus proves so far

Working notes, not a spec. `engines/x3d/docs/formats/` stays empty until a validator consumes every
byte of all 596 files (CLAUDE.md rule 2). Two structural hypotheses were tested here and
**refuted**; they are written down so nobody re-derives them.

Corpus: 596 `.O3D` files, 14.0 M, one distinct magic (E-0008).

### Proven

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

### Refuted

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

### Next step

Decompile the loader rather than guess further. `X3d_Load_Sdk_o3d` is the entry point — it
is imported by both EXEs and reached from `U99.cpp` `0x00464ead` in `MissionD.exe` (see
`import-map.md`). Its callee chain inside `x3d.dll` defines the record layout exactly, and
`x3d.dll` has no assert strings to shortcut with (E-0011).

## `.L3D` — what the corpus proves

Working notes, not a spec. `engines/x3d/docs/formats/l3d.ksy` is the canonical artefact once a validator
consumes every byte of every file (CLAUDE.md rule 2).

Corpus: 5 `.L3D` files, 5,718 bytes, one distinct signature.

### Proven

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

### Refuted

None — the first-try layout parsed all five corpus files. Because the per-light record has
no flags inside it (the conditional is just `is_spot`, which expands a fixed-size suffix),
this is a simpler shape than `.O3D` and the "stride hypothesis" trap doesn't apply.

### Observed

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
slots are flagged `extra_*` in `engines/x3d/tools/parsers/l3d.py` per CLAUDE.md rule 5.
E-0140 names them: inner and outer radius, multiplier, hidden, attenuate (`l3d.ksy`).

### Spot branch — no corpus sample

Every `.L3D` in the corpus has `is_spot == 0`. The spot branch is parsed (3 f32 target + 2
f32 angles) and the test exercises it, but the validator has no sample to cross-check the
branch against. Recorded as Q-0013.

### Next step

Move on. `.C3D` and `.S3D` share the same `(X)` signature scheme and use the same four
stream primitives — same shape of loader, same decompile-then-parse loop, the only change
is the per-record function (`FUN_10014d50` for lights, an analogous `FUN_1001xxxx` for the
next format). `.C3D` is the natural next pick: 6 files, 648 bytes, smallest corpus next
after `.L3D`.

## `.C3D` — what the corpus proves

Working notes, not a spec. `engines/x3d/docs/formats/c3d.ksy` is the canonical artefact once a
validator consumes every byte of every file (CLAUDE.md rule 2).

Corpus: 6 `.C3D` files, 648 bytes, one distinct signature.

### Proven

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

### Refuted

None — the first-try layout parsed all six corpus files. Because the per-camera
record has no flags inside it (every camera reads exactly 32 + 40 bytes), this is an
even simpler shape than `.L3D`.

### Observed

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

### Next step

Move on to `.S3D` — same family, same primitives, same decompile-then-parse loop.
`.MAT` is plain ASCII per the loader-list note; the loader decompile can be skipped
and the format parsed directly off the sample bytes. `.DMF` is the biggest remaining
engine format (518 files / 48.4 M / 8 distinct magics) and benefits from having the
family claim locked in across `.S3D`/`.MAT` first. `.BMP`, `.BIN`, `.FRA`, `.CFG`
follow.

## `.S3D` — what the corpus proves

Working notes, not a spec. `engines/x3d/docs/formats/s3d.ksy` is the canonical artefact once a
validator consumes every byte of every file (CLAUDE.md rule 2).

Corpus: 1 `.S3D` file (`U02/anim/U02_02/U02_02.S3D`), 73,916 bytes, version 0.95.

### Proven

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

### Refuted

None — the parser is a thin wrapper that reuses the already-validated per-format
record readers, and the layout matches the loader decomp exactly on first try.

### Observed

| File | Version | Bytes | Cams | Lights | Mats | Objects | Anims |
|---|---|---:|---:|---:|---:|---:|---:|
| `U02/anim/U02_02/U02_02.S3D` | 0.95 | 73,916 | 0 | 0 | 5 | 53 | 53 |

The 1-to-1 match between object count and animation count is consistent with the
animation file structure: each object has its own paired animation that animates the
same vertices. No cameras and no lights in this scene — those live in `.C3D`/`.L3D`
files alongside.

### Why this matters for the family claim

E-0020 said `.O3D/.A3D/.L3D` form the family. Adding `.C3D` (E-0021) made it four.
Adding `.S3D` makes it five, but `.S3D` is a meta-format: it is the engine's own
mechanism for combining the others. The "one container family" claim is now
strengthened: the engine ships its own multiplex of the per-format record shapes.

### Next step

Move on to `.MAT` — plain ASCII per the loader-list note; the loader decompile can be
skipped and the format parsed directly off the sample bytes. Then `.DMF` (the biggest
remaining engine format, 518 files / 48.4 M / 8 magics). `.BMP`, `.BIN`, `.FRA`,
`.CFG` follow.

## `.MAT` — what the corpus proves

Working notes, not a spec. `engines/x3d/docs/formats/mat.ksy` is the canonical artefact once a
validator consumes every byte of every file (CLAUDE.md rule 2).

Corpus: 5 `.MAT` files, 4,858 bytes, no magic (plain ASCII).

### Proven

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

### Refuted

None — the first-try layout parsed all five corpus files, including the empty
`U02_03LOD.MAT` (144 bytes, header only, no materials).

### Observed

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

### Why no loader decompile

The handoff §2 explicitly waives the loader-decompile step for `.MAT` because the
sample bytes uniquely determine the layout — every material block is 16 fixed lines in
documented order, with no flags or variable-length sections. The format is provable
from sample bytes alone; decompiling the loader would not strengthen the spec and could
only re-derive what the corpus already shows. The EVIDENCE entry for this format
cites the handoff and the per-file sample structures, not a Ghidra address.

### Next step

Move on to `.DMF` — 518 files / 48.4 M / 8 distinct magics, the biggest remaining
engine format. The handoff recommends doing `.DMF` last among the engine formats so
the family claim is locked in across the smaller ones; that order is preserved here.

## `.BMP` — what the corpus proves

Working notes, not a spec. `engines/x3d/docs/formats/bmp.ksy` is the canonical artefact once a
validator consumes every byte of every file (CLAUDE.md rule 2).

Corpus: 381 `.BMP` files, 131 MB, all `BM` magic, all BITMAPINFOHEADER (BMP3).

### Proven

Standard Windows `BITMAPINFOHEADER` (BMP3). Every file in the corpus is laid out
identically:

| Offset | Size | Field | Notes |
|---:|---:|---|---|
| 0 | 2 | `magic` | `'BM'` |
| 2 | 4 | `file_size` | declared on-disk size; informational (see below) |
| 6 | 2 | `reserved1` | always 0 |
| 8 | 2 | `reserved2` | always 0 |
| 10 | 4 | `off_bits` | byte offset of first pixel row |
| 14 | 4 | `info_size` | always 40 (BMP3, not V4/V5) |
| 18 | 4 | `width` | always positive |
| 22 | 4 | `height` | positive = bottom-up, negative = top-down |
| 26 | 2 | `planes` | always 1 |
| 28 | 2 | `bpp` | 8, 16 or 24 |
| 30 | 4 | `compression` | always 0 (BI_RGB) |
| 34 | 4 | `image_size` | may be 0 under BI_RGB |
| 38 | 4 | `xppm` | often 0 |
| 42 | 4 | `yppm` | often 0 |
| 46 | 4 | `colors_used` | 0 = default = `2^bpp` |
| 50 | 4 | `important` | often 0 |
| 54.. | variable | palette (≤8bpp) + pixel data | row stride `((width*bpp+31)//32)*4` |

Row stride = `((width * bpp + 31) // 32) * 4` (each row padded to 4-byte boundary).
Total pixel bytes = `stride × |height|`. Total expected file size =
`off_bits + pixel_bytes`. The parser derives size from this formula and does not
trust the declared `file_size`.

The corpus has no `BITMAPV4`/`BITMAPV5` headers (no 108/124-byte DIB), no
`BI_BITFIELDS`/`BI_RLE4`/`BI_RLE8`/`BI_JPEG`/`BI_PNG` compression. These would be
no-ops to add since they do not occur.

### Refuted

None — the first-try layout parsed 378/381 files on the run that enforced the
declared `file_size` invariant. The 3 failures showed the declared size is
*informational only*; the parser now derives size from width × height × stride and
passes 381/381.

### Observed

| bpp | files |
|---:|---:|
| 24 | 340 |
| 16 | 40 |
| 8 | 1 |

| Property | Value |
|---|---|
| Total pixels | 46,347,716 |
| Total bytes (on disk) | 131,324,774 |
| Declared total | 131,324,637 |
| Files where declared == actual | 136/381 |

The 3 files where declared is **wrong** are:

| File | Declared | Actual | Shortfall |
|---|---:|---:|---:|
| `2dbit/SaveRetourD.BMP` | 6,354 | 6,374 | 20 |
| `2dbit/SaveSommaireD.BMP` | 4,389 | 4,406 | 17 |
| `2dbit/U01_04P.BMP` | 7,554 | 7,654 | 100 |

These are scattered editor snapshots (two save dialog backgrounds and one
puzzle-piece panel). The writer must have flushed the file header before writing
the trailing pixel rows. The on-disk shape is still a valid BMP — width/height/
stride are self-consistent, so the parser reads every byte correctly.

### Why this matters for the corpus claim

BMP is a third-party format; CLAUDE.md rule 2 still applies (every format needs a
spec and a 100%-corpus validator), but the loader decompile step is unnecessary —
Microsoft's published format is sufficient. The EVIDENCE entry cites the parser run
and the sample-byte survey (all `BM`, all `BITMAPINFOHEADER`, all BI_RGB) rather than
a Ghidra address.

### Next step

Move on to `.BIN` — 109 files / 80 magics / no magic. Per the handoff, load via the
loader (`x3d.dll` must have a BIN reader). Then `.FRA` and `.CFG` follow.

## INFOOBJ.BIN format findings

### TL;DR

`Data/U##/INFOOBJ.BIN` is a per-unit object-info container: a fixed-width table of
68-byte entries preceded by a `u32 count` and terminated by a 32-byte `#OBJECTS#`
footer. The on-disk layout is fully pinned down. Every byte is consumed by
`engines/x3d/tools/parsers/infoobj.py` over all 9 corpus files (100% pass, 183 entries, 12,768
bytes total).

### Loader evidence

Two loaders in `MissionMonet.exe` reference `INFOOBJ.BIN`:

* `FUN_0041d490` (`0x0041d490`) — opens INFOOBJ.BIN standalone when called with a
  null reader (`engines/x3d/notes/decomp/MissionMonet.exe__FUN_0041d490.c:42-69`); also serves as
  the entry point for a generic reader that processes `SCENE` / `ANIMATIONS` /
  `OBJECTS` sections in `Scene.bin` when called with a non-null reader
  (`engines/x3d/notes/decomp/MissionMonet.exe__FUN_0041d490.c:70-91`).
* `FUN_0041d6f0` (`0x0041d6f0`) — the actual OBJECTS-sub-loader; reads the entries
  (`engines/x3d/notes/decomp/MissionMonet.exe__FUN_0041d6f0.c:64-79`).

The string `s_INFOOBJ_BIN_00441b88` lives at `MissionMonet.exe + 0x41b88` and
spells `INFOOBJ.BIN\0`. The OBJECTS-section string lives at `0x41bc0` (`OBJECTS\0`).
The path is built by `sprintf(buf, "Data/U%02d/INFOOBJ.BIN", DAT_00442640 + 8)`
(line 44/46 of the two decompiled files), where `DAT_00442640` is the unit-number
slot populated earlier in the engine.

`FUN_0041d6f0` reads:

```c
iVar1 = FUN_00415190(this_00, s_OBJECTS_00441bc0);   // find "OBJECTS" tag
if (iVar1 != 0) {
    FUN_004153a0(this_00, &local_118, 4);            // u32 count
    if (local_118 == 0) { ExceptionList = local_c; return 1; }
    local_114 = operator_new(local_118 * 0x44);
    FUN_004153a0(this_00, local_114, local_118 * 0x44);   // count * 68 bytes
    FUN_00415180((int)this_00);                      // close section
}
```

`FUN_00415190` is the seek-to-tag reader primitive. `FUN_004153a0` is a bulk-copy
read. `FUN_00415180` is the close-section primitive.

After the entries are in memory, the loader iterates them and calls
`FUN_0041b440` per entry (`engines/x3d/notes/decomp/MissionMonet.exe__FUN_0041d6f0.c:84-108`).
That sub-loader is what interprets each 68-byte blob; the raw fields are not parsed
inside `FUN_0041d6f0` itself.

### On-disk layout

The 9 corpus files all follow this exact layout (verified by `engines/x3d/tools/parsers/infoobj.py`):

```
+0x000  u32          count
+0x004  entry[0]     68 bytes
+0x048  entry[1]     68 bytes
...
+0x004 + count * 68  terminator  (32 bytes)
```

where each entry is:

```
+0x00  40 bytes    name (NUL-terminated, e.g. "*U04_03\0", then 0xCD garbage)
+0x28  4  bytes     u32 type          hotspot type; INFOACT actions match on it; 6 = character
+0x2C  4  bytes     u32 cursor        cursor kind (0 default, 2 click, 3 voice, 4 take, 5 use)
+0x30  4  bytes     u32 visible       0 = hidden at load
+0x34  4  bytes     f32 anim_frame    animation node frame
+0x38  4  bytes     u32 anim_paused   non-zero = paused at anim_frame
+0x3C  4  bytes     u32 anim_fps      animation node frame rate
+0x40  4  bytes     u32 anim_loop     animation node loop flag
```

Field meanings (E-0072, superseding the "field_a..g" and "reserved" readings below):
`Scene_LoadObjectInfo` (`0x0041d8e0`) creates one hotspot per entry and applies it with
`FUN_004210d0`; the savegame's `OBJECTS` chunk (`FUN_0041d6f0`, the writer, not a loader)
has the same layout. Behaviour: `engines/x3d/docs/spec/interaction.md`.

and the terminator is:

```
+0x00  10 bytes     "#OBJECTS#\0"
+0x0A  10 bytes     0xCD padding
+0x14  4  bytes     u32 = 0          (count of this OBJECTS section)
+0x18  4  bytes     u32 = offset_of_OBJECTS_tag
+0x1C  4  bytes     u32 = 1          (flag)
```

Correction (E-0025): the 32-byte "terminator" below is the `.BIN` chunk table,
one entry `#OBJECTS#` at offset 0 covering the payload. There is no rewind mystery.

### Corpus inventory

| File | Size | Entries | Names |
|---|---:|---:|---|
| `U00/Infoobj.bin` | 376 | 5 | `*U04_03 *U04_32 *U04_36 *U04_43 *U04_80` |
| `U01/INFOOBJ.BIN` | 1736 | 25 | `*U01_01 .. *U01_24, *Ernest` |
| `U02/INFOOBJ.BIN` | 1192 | 17 | `*U02_01 .. *U02_14, *U02_06a, *U02_07a, *U02_09a` |
| `U03/INFOOBJ.BIN` | 1804 | 26 | `*U03_01 .. *U03_29` (gaps) |
| `U04/INFOOBJ.BIN` | 3300 | 48 | `*U04_01 .. *U04_53` (gaps), `*Ernest`, `*U03_06` |
| `U05/Infoobj.bin` | 1056 | 15 | `*U05_01 .. *U05_13, *Fil, *U04_04` |
| `U06/INFOOBJ.BIN` | 580 | 8 | `*U06_15 .. *U06_21, *U03_02` |
| `U07/INFOOBJ.BIN` | 784 | 11 | `*U06_22 .. *U06_30, *Eteint01, *U06_19` |
| `U33/INFOOBJ.BIN` | 1940 | 28 | `*U03_01 .. *U03_37` (gaps) |

Entry names are not necessarily unique across files — `*U03_06` appears in both
`U04/INFOOBJ.BIN` and `U33/INFOOBJ.BIN`, `*Ernest` appears in both `U01` and `U04`,
`*U04_04` appears in both `U04` and `U05`. This is consistent with the engine
referencing scene objects by name across unit boundaries.

### Unexplained / opaque

* **`reserved` (entry offset `+0x08`, 32 bytes)**: every byte is `0xCD` across all 9
  files and 183 entries. This is MSVC's uninitialised-heap pattern, and the runtime
  loader overwrites the first 4 bytes of this region (entry offset `+0x2C`) with a
  pointer to the loaded object's handle (see `FUN_0041d6f0:88-96`). The remaining 28
  bytes presumably hold pointer-sized slots that get populated by `FUN_0041b440` (the
  per-entry sub-loader), but `FUN_0041b440` is not decompiled here. The slot
  semantically becomes 8 pointer fields at runtime, so the writer never bothered to
  serialise them. See OPEN-QUESTIONS for the full picture.

* **Seven numeric fields** (`field_a` .. `field_g`): values are stable per field
  across the corpus, suggesting well-defined semantics, but the meaning of each is
  unknown without decompiling `FUN_0041b440`. Empirical notes:
    * `field_a` (`+0x28`): mode 4 or 5, occasional 6.
    * `field_b` (`+0x2C`): on-disk values 0..5, but the runtime value is a pointer.
    * `field_c` (`+0x30`): almost always 1.
    * `field_d` (`+0x34`): almost always 1.0; one entry in U01 has 20.0.
    * `field_e` (`+0x38`): almost always 1.
    * `field_f` (`+0x3C`): strong mode at 15 (170/183), with 0, 2, 4, 50 outliers.
    * `field_g` (`+0x40`): mode 1 (139/183), rest 0.

* **Terminator `flag = 1`**: present in every corpus file; semantics unknown.

### Validator output

```
$ python engines/x3d/tools/parsers/infoobj.py
corpus: C:\...\games/monet/discs/cd\Data
files: 9  passed: 9  failed: 0
  objects: 183
  bytes:   12768
100% of corpus parsed
```

## `#ACTIONS#` (INFOACT.BIN, E-0071)

The only chunk of `Data/U##/INFOACT.BIN`: `u32 count`, then `count` records of 0x440
bytes, read by `Scene_LoadActions` (`0x0041da90`). Record: `u32 id`, `char name[30]`,
`char condition[258]`, `i32 max_runs`, `u32 trigger`, `char item[32]`,
`u32 hotspot_type`, `char hotspot[32]`, `u32 target_type`, `char target[32]`,
`u32 step_count` (≤ 10), then 10 steps of `u32 op` + `char arg[64]`. Field docs in
`infoact.ksy`, behaviour in `engines/x3d/docs/spec/interaction.md`.

`python engines/x3d/tools/parsers/infoact.py` → 9/9 files, 198 records, every byte consumed
(`--selftest`, `--file` dumps a unit). Corpus: trigger 8 ×115, 7 ×74, 0 ×9; `max_runs`
1 ×143, 100 ×52, 2, 3, 9 once each; ops 1, 2, 3, 4, 7, 9, 10, 13, 14, 15, 16, 101.

## `#INDEX#` (Sound/*.bin, lip sync, E-0124)

`u32 count`, then `count` records of `u32 time_ms, u16 shape, u16 unk_pad` (`lip.ksy`).
81 files, all under `Uxx/Sound/`, each beside a `.wav` of the same name; 10,373 records;
shapes 1..8 (1: 1,289, 2: 914, 3: 571, 4: 1,608, 5: 1,566, 6: 971, 7: 986, 8: 2,468);
`unk_pad` is 0xCDCD throughout; first time 0 in every file; steps 44 ms minimum, 46 ms
median. What the shapes do is `engines/x3d/docs/spec/sound.md`.
