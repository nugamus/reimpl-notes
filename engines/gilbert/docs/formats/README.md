# Formats (Gilbert engine)

One row per recovered format: status here, the Kaitai spec next to it (`<fmt>.ksy`), the
validator in `engines/gilbert/tools/parsers/<fmt>.py` (with `--selftest`), the proof in
`EVIDENCE.md`. A format is done only when its validator passes 100% of that type in
`games/gilbert/discs/cd`, every byte consumed.

| Format | Files | Validator | Spec | Evidence | Status |
|---|---:|---|---|---|---|
| `.wxi` picture collection | 234 (2,482 pictures) | `wxi.py` | `wxi.ksy` | E-0010 | done |
| `.wxs` / `.dxw` wave collection | 4 + 4 (identical pairs; 58 waves) | `wxi.py` | `wxi.ksy` | E-0010 | done (tail byte Q-0001) |
| `ctrl<room>.map` control map | 39 | `ctrlmap.py` | `ctrlmap.ksy` | E-0011 | done (cell meaning Q-0002) |
| `.mpg` film | 42 | ffprobe (standard format) | ISO 11172 | E-0007 | standard MPEG-1 system stream |
| `.wav` sound | 629 | none yet | RIFF | E-0001 | standard |
| `default.dat` game database | 1 | | | E-0005 | in progress (MFC CArchive) |

## `.wxi`, `.wxs`, `.dxw` — DelphiX collections (E-0010)

A 16-bit Windows resource entry around a Delphi component stream:

```
u8  0xFF, u16 10            resource type RCDATA by ordinal
char name[]\0               WDXPICTURECOLLECTION | DELPHIXPICTURECOLLECTION | DELPHIXWAVECOLLECTION
u16 flags                   0x1030
u32 size                    = rest of the file
"TPF0" sstr class, sstr name ("")      class TPictureCollectionComponent | TWaveCollectionComponent
property "List" = collection (0x0E), items each 0x01 + properties + 0x00, then 0x00
0x00 (end of properties), 0x00 (no child components)
```

Delphi stream values used: 0x02 int8, 0x03 int16, 0x04 int32, 0x06 short string,
0x07 identifier, 0x08 false, 0x09 true, 0x0A binary (u32 length + bytes), 0x0B set,
0x0E collection. `sstr` is a length byte + Latin-1 text.

Picture items: `Name` (string), `x`, `y` (ints, `WDX…` files only), `PatternHeight`,
`PatternWidth` (ints; 64×64 on the room backgrounds, 0 = the whole picture),
`Picture.Data` (binary), `SystemMemory`, `Transparent` (booleans), `TransparentColor`
(identifier: `clFuchsia`, `clBlack`, …), optional `Hint` (string). 52 items have no
`Picture.Data`. `Picture.Data` = sstr `TDIB` + BITMAPINFOHEADER (40 bytes, `biCompression`
0, positive height = bottom-up) + `biClrUsed` or 2^bpp RGBQUADs for ≤ 8 bpp + pixel rows
padded to 4 bytes. Nothing follows the pixels.

Wave items: `Name`, optional `Looped` (boolean), `Wave.WAVE` (binary) = `RIFF` u32
riff_size `WAVE` `fmt ` u32 16 + PCMWAVEFORMAT + `data` u32 n + n bytes + u8 unk_tail.
riff_size = blob length + 2 in all 58 (Q-0001). Seen: PCM mono 11,025/22,050/44,100 Hz and
stereo 22,050 Hz, 8 and 16 bit.

## `ctrl<room>.map` — control map (E-0011)

wDx `TDxMaps` stream (`TDxMaps.ReadData` 0x44f50c):

```
"ML01"            magic (not checked by the loader)
s32 high          number of maps - 1 (0 in the corpus)
per map:
  u8  name_len, char name[15]   Delphi string[15]: "Map", rest uninitialised
  u32 width, u32 height         in 16×16-pixel cells
  u32 size                      width * height * 10
  u32 unk_ptr                   the editor's buffer pointer, meaningless on disk
  u32 cells[width * height]     row-major, values 0..29 (Q-0002)
  u8  unk_tail[6 * width * height]   zero (4 stray bytes in 5 files)
```

Rooms and their grids: 80×60 (1280×960), 64×48, 60×40, 56×48, 52×40, 48×40, 48×36,
44×28, 40×36. The room picture `w<room>.wxi` is the grid size × 16.

## `.mpg` — films (E-0007)

Plain MPEG-1 system streams: one 384×288 MPEG-1 video stream, one MPEG-1 layer II audio
stream (44.1 kHz). Played by `gempeg.dll` through DirectShow (E-0006). In ScummVM:
`Video::MPEGPSDecoder` (needs libmpeg2 for video and libmad for layer II audio).
