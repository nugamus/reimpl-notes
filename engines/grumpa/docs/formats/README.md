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
| `.scn` | 110 | binary | `CFXScene` | — | Q-0005 | header `08 00 00 00`, `0258`; float stream (layout TBD) |
| `.abi` | 118 | binary | `CFXActorFactory::CreateFromABIFile` / status saves | — | E-0012 | record framing done (`u32 type,u32 id,class data`); per-class fields Q-0006 |
| `.amb` | 588 | binary mesh | `CFXAMeshEx::CreateFromFile` | `amb.py` | E-0013 | done (`u32 count` + count×(pos+normal)) |
| `.anb` | 939 | binary mesh | `FUN_004157d0` (faces/UV/anim) | — | E-0014 | sections mapped; fields Q-0007 |

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

The first field of a block is the actor id (`// Actor ID  FX_INVENTORY= 30`). A block
without a `<type><name>` header overrides the block before it (seen in
`090_Inventory.atx`). Header type = the CFX class; the corpus uses
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

## Binary formats still pending the loader

`.scn`, `.abi`, `.anb`/`.amb` are compiled binary (arrays of records). Their field layouts
are read from the loader methods in the decrypted `Grumpa.exe` (`CFXScene`,
`CFXActorFactory::CreateFromABIFile`, `CFXAMesh::Serialize`) in `ghidra_projects/Grumpa.gpr`;
tracked as Q-0005..Q-0007 until specced.
