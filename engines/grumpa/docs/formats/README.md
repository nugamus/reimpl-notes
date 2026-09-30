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
| `.fxi` | 316 | binary image | `CFXSurface` / `CFXTexture` / `CFXZBuffer` | — | Q-0004 | 800×600 surface, **compressed body** (codec TBD) |
| `.scn` | 110 | binary | `CFXScene` | — | Q-0005 | header `08 00 00 00`, `0258`; float stream (layout TBD) |
| `.abi` | 118 | binary | `CFXActorFactory::CreateFromABIFile` / status saves | — | Q-0006 | actor instances and save status (layout TBD) |
| `.anb` `.amb` | 939 + 588 | binary mesh | `CFXAMesh` / `CFXAMeshEx` | — | Q-0007 | vertex/anim data (layout TBD) |

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

## Standard media (E-0007)

`.jpg` (JFIF), `.tga` (Targa, magic `00 00 02 00`), `.bmp` (Windows BMP), `.wav`
(RIFF/WAVE), `.avi` (RIFF/AVI), `.mpg` (MPEG-1). Read with off-the-shelf decoders; the
game's own `CFXBitmap`/`CFXSound` wrap them. Not re-specced here.

## Binary formats pending the loader

`.fxi`, `.scn`, `.abi`, `.anb`/`.amb` are compiled binary (arrays of records / a
compressed surface). Their field layouts and the `.fxi` codec are read from the loader
methods in the decrypted `Grumpa.exe` (`CFXSurface::CreateFromFile`,
`CFXScene`, `CFXAMesh::Serialize`, ...), which needs the Ghidra project; tracked as
Q-0004..Q-0007 until specced from that code.
