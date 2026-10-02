# Formats (Grumpa engine)

One row per recovered format: status here, the validator in
`engines/grumpa/tools/parsers/<fmt>.py` (with `--selftest`), the proof in `EVIDENCE.md`.
A format is done only when its validator passes 100% of that type in
`games/grumpa/discs/cab`, every byte accounted for. Counts from
`engines/grumpa/notes/corpus-inventory.md`.

The class names below are the game's own, read from the strings in the decrypted
`Grumpa.exe` (`CFX*`, E-0003): the data is the serialised state of a C++ class tree rooted
at `CFXActorFactory`, which loads `.atx`/`.abi` actors, `.scn` scenes, `.fxi` surfaces,
`.anb`/`.amb` meshes and the standard media.

| Format | Files | Kind | Loader (CFX class) | Validator | Evidence | Status |
|---|---:|---|---|---|---|---|
| `.atx` | 114 | text | `CFXActorFactory::CreateFromATXFile` | `atx.py` | E-0005 | done (shape; field meaning per class TBD) |
| `.btn` `.shl` | 30 + 4 | text ini | FXProfileShell | — | E-0006 | `key = value`, standard |
| `.sts` | 7 | text | `CFXMenu::LoadPlayerInfo` | — | E-0006 | player name + counter, two lines |
| `.tma` | 2 | text | texture-matrix anim | — | E-0006 | tab-separated float rows |
| `.txt` | 19 | text | menu / credits / help | — | E-0006 | UI strings (cp1252) |
| `.jpg` `.tga` `.bmp` | 1745 + 317 + 65 | image | `CFXBitmap` etc. | — | E-0007 | standard JFIF / Targa / Windows BMP |
| `.wav` | 1612 | sound | `CFXSound` | — | E-0007 | standard RIFF/WAVE |
| `.avi` `.mpg` | 10 + 4 | video | `gempeg`-style / MPEG-1 | — | E-0007 | standard |
| `.fxi` | 316 | 16-bit Z-depth (also colour) | `CFXZBuffer` / `CFXSurface` | `fxi.py` | E-0009, E-0010 | done (316/316 parse + decode) |
| `.scn` | 110 | binary (3 actor records) | `CFXActorFactory::CreateFromABIFile` | `scn.py` | E-0500 | done (110/110; walk mesh, scene links, view list) |
| `.abi` | 118 | binary scene graph | `CFXActorFactory::CreateFromABIFile` | `abi.py` | E-0100..E-0103, E-0400, E-0401 | done: 113/113 byte-exact (scenes, items, both character databases), 15 types |
| `.amb` | 588 | binary mesh | `CFXAMeshEx::CreateFromFile` | `amb.py` | E-0013 | done (`u32 count` + count×(pos+normal)) |
| `.anb` | 939 | binary mesh | `CFXAMeshEx` / `FUN_004157d0` | `anb.py` | E-0014 | done (938/939: geometry, UVs, anim); frame-count Q-0007 |

## `.atx` — actor/object definitions (E-0005)

Text, read by `CFXActorFactory::CreateFromATXFile`. A file is a sequence of blocks:

```
<type><name>            optional header: decimal class code, actor name
{
    <field>             one field per line: a value, several whitespace-separated
                        values (colour triple, x/y/z position), or a file name that
                        may contain spaces; trailing comment from the first `/`
    ...
}
```

The first field of a block is the actor id (`// Actor ID  FX_INVENTORY= 30`). The reader
skips lines until one holds `<`, so a block without a `<type><name>` header is never read
(the second block of `090_Inventory.atx`, E-0504). Header type = the CFX class; the corpus uses
2, 3 (item, 42×), 4 (inventory), 5 (character, 65×), 6, 22, 23, 27, 28, 31, 37 (global
counter, 20×), 38, 39. The field list per class is game logic and not yet specced
(fields stay opaque). `atx.py` checks the shape: 114/114 parse, every byte in a block or
whitespace.

## Text configuration (E-0006)

- `.btn` / `.shl` — the InstallShield profile shell (`FXProfileShell.exe`): `key = value`
  lines. `.shl` names the window, background, movies and buttons; each `.btn` gives a
  button its two-state bitmaps, hit rectangle, hover/click sounds and `execute_cmd`
  (`grumpa.exe`, a URL, or the help file). `value.shl` in `_Support_*`/`_MFC_*` is
  InstallShield's, not the game's.
- `.sts` — a player slot's status: line 1 the player name, line 2 a counter.
- `.tma` — a texture-matrix animation: rows of tab-separated floats (`1.0 1.0 1.0 1.0`
  ...), used for the `effect`/`effect_item` materials.
- `.txt` — UI text in cp1252 (`Text.txt` menu labels, `Credits.txt`, `Help.txt`), one
  language per `Local_*` / `UI/001_Menu` copy.

## Scene views: colour + depth naming (E-0011)

A pre-rendered node is a colour background plus a depth buffer, paired by name in
`Bitmaps/`: `<scene>_<view>_IS.jpg` (Image Screen, 800×600 colour) and
`<scene>_<view>_IZ.fxi` (Image Z, 16-bit depth). 173 such pairs. Animated scene elements
instead have per-frame depth `<name>_Z####.fxi` (143 files: chest, pit trap, ...) with
matching colour frame sequences. The engine draws the colour view, then composites the 3D
actors against the depth buffer.

## Standard media (E-0007)

`.jpg` (JFIF), `.tga` (Targa, magic `00 00 02 00`), `.bmp` (Windows BMP), `.wav`
(RIFF/WAVE), `.avi` (RIFF/AVI), `.mpg` (MPEG-1). Read with off-the-shelf decoders; the
game's own `CFXBitmap`/`CFXSound` wrap them. Not re-specced here.

## `.fxi` — surface image (E-0009)

Loaded by `FUN_00418de0` (decrypted `Grumpa.exe`). 18-byte header (`u8 version`,
`u8 flag`, `u16 width`, `u16 height`, `u32`×3), a 16-bit surface. `flag == 0`: raw
`width*height*2` pixels (36 files). `flag != 0`: `(width/8)*(height/8)` control bytes, one
per 8×8 block; each block is two sub-blocks (the control byte's low nibble, then its high
nibble), each a mode — 0 solid (1 B), 1 two-colour (8-B 1bpp mask + 2×u16, 10 B), 2
four-colour (16-B 2bpp mask + 4×u16, 20 B), 3 raw (64 B) (280 files). `fxi.py` parses
316/316 with every byte consumed. Dimensions vary (173 are 800×600, down to 56×56). The
per-mode pixel maths (filling the 8×8 block from the masks/colours) is Q-0004.

## `.abi` — scene graph / actor database (E-0100..E-0103)

A serialized `CFXActorFactory` tree. `CFXActorFactory::CreateFromABIFile` (`FUN_0040cef0`)
reads records to end-of-file:

    record = u32 type, u32 id, <Serialize(mode 1)>

`CreateActor` (`FUN_0040d2f0`) maps `type` to a `CFX*` class; each class's `Serialize`
(vtable[1]) is called with mode 1. The read primitive `FUN_004026c0(archive, dst, n)` reads
`n` bytes; `FUN_00430c50` reads a pascal string (`u32 len` + `len` bytes). A trailing chunk
under 8 bytes (a `type` with no `id`) is ignored (e.g. `Scene_400.abi`, 4 padding bytes).

Three vector element classes recur (E-0101): `EC` (`FUN_00409920`, 5 u32 = 20 B), `ClassC`
(`FUN_00409150`, 5 u32 + `u32 n` + `n`×EC) and `ClassD` (`FUN_00409cf0`, an EC-vector then a
ClassC-vector, type 3 only). Each actor body is fixed u32 runs, EC/ClassC vectors, pascal
strings and inline embedded sub-objects; see `engines/grumpa/notes/actor-types.txt` and the
per-type functions in `abi.py`.

`abi.py` parses **111/111** scene + item files consuming every byte: **2004 records** over
14 types — 0x11 view, 0x18/0x2a `CFXSound`, 0x19 `CFXTrigger`/`CFXSprite`, 0x0d, 0x1a, 0x07,
0x1d, 0x1e, 0x20, 0x21, 0x22/0x25, 0x23/0x26, 0x24/0x27, 0x05 `CFXItem`. Two actors branch
on a value they read (0x19 reads a bubble array iff +0x1ac == 2; 0x0d reads two extra u32 iff
+0x20c == 1); 0x20's transform vector is pre-sized to 5 by its ctor.

**Per-view camera** (E-0103, resolves Q-0008): a 0x11 view ends with `u32 cam_id` + a
0x68-byte block of 26 floats, handed to the render device. Across the corpus only floats
`f1=1.0`, `f2∈[0.75,1.0]`, `f3∈[0.70,1.0]` (projection), `f13..f15` = camera position, `f19`
= range/far, `f21=1.0` are non-zero (the rotation fields are 0 — axis-aligned views).

**Actor header** (E-0400): the loader seeks back over the id, so every Serialize reads `id`
again, then `active`, `visible`, `u32 n` and `n` u32 (n = 1, element 0 in every scene record;
6 per character). The older per-type grammars in `abi.py` count `active, visible, n` as one
12-byte run and the element as an "EC count"; the byte totals are right, the meanings are the
ones here.

**Type 0x03 `CFXCharacter`** (`Actors/Characters.abi`, `Scenes/Characters.abi`; E-0401,
E-0402): 44 + 44 records, every byte consumed, the grammar taken from the original's own
Serialize run under Unicorn (`tools/abiemu.py`). After the header: home scene, position,
orientation, three floats and two u32; a ClassD rule vector; three CC vectors and a message
list (`pstr` + CC vector, empty in the corpus); a reaction list (character id + CC vector);
the `.anb` animation, `.wav` sound and `.tga` texture name lists (with the texture index between
the last two); the carried-object table (`.ANB`, `.tga`, 3 u32); kind and parts; a pair list.
Exact order in E-0401 and `abi.py` `t_03`.

## `.scn` — walk mesh, scene links and view list (E-0500)

Read by `LoadScene` through the same `CreateFromABIFile` as the `.abi` (`u32 type, u32 id,
Serialize(mode 1)` to EOF), just before `Scene_<n>.abi`. Exactly three records:

    type 0x08, id 600  walk mesh
        u16 nv, u16 nf
        nv * { f32 x, y, z; f32 unk[5] }        unk[0..2] always (0, 1.0, 0)
        nf * { u16 v0, v1, v2 }                 vertex indices (< nv)
        nf * u16 unk                            per-face value (0,1,2,3,12,13,19,20)
    type 0x14, id 601  scene links ("CFXToScene")
        u32 np, np * u32                         state slots (State, Scene_ID; 0 in the corpus)
        u32 n,  n * { f32 x, y, z; f32 unk_r; u32 scene }        exits
        u32 m,  m * { f32 x, y, z; f32 rx, ry, rz; u32 scene }   entries (arriving from scene)
    type 0x09, id 602  view list
        u32 n
        n * { u32 len, char colour[len]; u32 len, char depth[len] }   "<v>_IS.jpg", "<v>_IZ.fxi" (NUL included)
        n * f32 unk_m1[16]                       per view (rotation + translation)
        n * f32 unk_m2[16]                       per view (projection-shaped)

`scn.py` parses 110/110, every byte consumed. Open meanings: Q-0500, Q-0501.
