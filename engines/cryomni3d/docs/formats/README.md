# Formats (CryOmni3D engine)

One row per recovered format: status here, the validator in
`engines/cryomni3d/tools/parsers/<fmt>.py` (with `--selftest`), the proof in `EVIDENCE.md`.
A format is done only when its validator passes 100% of that type in every game's reference
edition (`games/<game>/discs/<version>/`), every byte accounted for. Formats upstream
`cryomni3d` already reads (HLZ, HNM, WAM, the Versailles `.dat` files) still get a row and a
validator run over the other games, since their variants may differ.

| Format | Games | Files | Validator | Evidence | Status |
|---|---|---:|---|---|---|
| HNM6 (`.HNM`, `.HNS`; `hnm.ksy`) | China | 764 | `hnm.py` | E-0100, E-0101 | China 764/764, every byte; other games not run |
| SPR (`spr.ksy`) | China | 448 | `spr.py` | E-0102 | China 448/448, every byte; unk_16/unk_1a (Q-0100) |
| TGA (`tga.ksy`) | China | 151 | `tga.py` | E-0103 | China 151/151, every byte |
| WAV (`wav.ksy`) | China | 763 | `wav.py` | E-0104 | China 763/763, every byte; game reader Q-0101 |
| RAW puzzle mask (`raw.ksy`) | China | 2 | `raw.py` | E-0106 | China 2/2, every byte |
| CRF font (`crf.ksy`) | China | 11 | `crf.py` | E-0105 | China 11/11, every byte |
| LOC text files (`DIAL LABELS LISTE MINUTES Fichetxt CREDITS`) | China | 6 | `loctext.py` | E-0200..E-0205 | China 6/6, every byte; display of index rows Q-0202 |
| ZIK music (`zik.ksy`) | China | 6 | `zik.py` | E-0206 | China 6/6, every byte |
| `chine.cfg` (`china_cfg.ksy`) | China | 1 | `cfg.py` | E-0501, E-0207 | China 1/1, every byte |
| Save game (`china_sav.ksy`) | China | 0 | `sav.py` | E-0208 | specced from code only (no saves in the corpus); Q-0200, Q-0201 |

`uv run tools/ksy_check.py cryomni3d --max 0` runs these specs over every game's corpus:
all China files parse to the end; files of other games that fail are their own variants,
not yet covered (Aztec and Egypt II `Data/Font/*.crf`, 12; Egypt II `Data/FMV/*.hnm`, 9,
which end without the terminator; Versailles `DATAS_V/MUSIC/6AMB3.WAV`).

### HNM6 (China)

64-byte header, then `frame_count` superchunks of 4-aligned chunks and a zero u32, the
same as Mission Sunlight's HNM6 (`engines/peintre/docs/formats/hnm.ksy`). Chunks: IX
video, IW warp picture, AA/BB sound (CRYO_APC header + IMA ADPCM). Per folder: IMAGES,
INTERF, LOC, `Cd.hnm` are 640x480 one-frame IX stills; SYNC 384 files of 7 IX frames, no
sound; HNM 44 `.HNS` videos 640x480 with sound (0xA1 22050 Hz stereo 37, 0x21 22050 mono
5, 0xC1 44100 stereo 2; all 15 frames/s of sound); WARP 191 panoramas 2048x768, one IW
frame. Warps differ from everything else: `unk_1a` 1 (else 2), `file_size` = length - 4
(else = length), `max_frame_size` 0x300000, and the IW payload header is 24 bytes (no
`unk_18`), quality 85 in all. ScummVM already reads all of it: `video/hnm_decoder.cpp`
(videos, IX and IW) and `engines/cryomni3d/image/hnm.cpp` with `image/codecs/hnm.cpp`
(stills and warps, warp mode chosen by the IW tag).

### SPR (China)

Not Mission Sunlight's RLE bank: one picture in a TGA container. 18-byte TGA header
(id_length 12, type 2, depth 15, descriptor 0x20 = top row first), a 12-byte image ID
(u32 key colour, s32 `unk_16`, s32 `unk_1a`), then width*height X1R5G5B5 pixels.
Loader 0x41f760 (accepts depth 15 or 16). 27 key colours (0x001F in 184 files). No
ScummVM code reads it yet; a TGA decoder with the ID read would.

### TGA (China)

Plain uncompressed true colour: 150 files 16-bit X1R5G5B5 (as Mission Sunlight), one
24-bit (`SPRITES/LOAD/FOND.TGA`); descriptor 0 or 1 (bottom row first); a TGA 2.0 footer
in 40. Loader 0x416510 handles depth 16 and 24 only. ScummVM's `image/tga.cpp` reads both.

### WAV (China)

RIFF PCM 16-bit mono, 22050 Hz (762) or 44100 Hz (`SOUND/BOITE32A.WAV`); chunks `fmt `,
`data`, then `LIST`/`cue ` in 443. ScummVM's `Audio::makeWAVStream` reads them. The
game's own reader is not traced (Q-0101).

### RAW puzzle masks (China)

`PUZZLES/PUZZLE4/MASK.RAW` and `PUZZLES/HORLOGE/MASK.RAW`: 640x480 bytes, no header, the
byte under the mouse is the zone. PUZZLE4: 0xE7..0xFE zones 0..23, 0xFF none. HORLOGE:
0 none, 1..54 zones.

### CRF fonts (China)

The layout upstream `engines/cryomni3d/fonts/cryofont.cpp` reads for Versailles (BE:
"CRYOFONT", three u16, s16 height, 32-byte comment, glyphs of u16 h, u16 w, s16 off_x,
s16 off_y, u16 advance, w*h bytes). China's 11 files parse with it unchanged; each holds
224 glyphs (0x20..0xFF, as Versailles' do), ScummVM reads 223 and ignores 0xFF. Bitmaps
are 0/255; comment is 32 '?'.

### LOC text files (China)

`DATA/LOC/`: Windows-1252, CR LF, read whole (0x413200) and parsed in memory; each file
has its own reader (E-0200..E-0205). Ids are matched case-insensitively (lowercased).
DIAL.TXT has one byte 0x82 (code page 850's é in "Douairière", a slip in the data).
Except in DIAL and LABELS, the readers first turn every CR outside `<...>` and the byte
after it into NUL (0x40a5b0), then scan for delimiters.

- **DIAL.TXT** (dialogue lines, 694; max 700): `#id#` `<text>` `GOTO next` repeated, in
  that order only; id and text on one line; `next` is a block id or `fin` (end), all must
  resolve at load. Whitespace and `/`-to-line-end comments between tokens. Ids match the
  voice files `VOICES/<id>.WAV` (E-0006).
- **LABELS.TXT** (interface strings, 415; max 450): `#id#` `<text>` pairs, text may span
  lines; `/` comments; `#id#<text>` with nothing between them is rejected.
- **MINUTES.TXT** (the inquiry notes, 45; 50 slots): `#id#` `<text>` found by scanning,
  text may span lines; no comments.
- **LISTE.TXT** (documentation index, 119 entries): `##C` starts the group of letter C
  (row `-C-`); `#id#` `<text>` gives row `text/id` (id = a Fichetxt fiche label; E-1301); a
  `##name##` + `<title>` line is skipped and the group after it gets the header `-`;
  `<text>` with no id is ignored (one in the corpus).
- **Fichetxt.txt** (documentation, 8 themes, 122 fiches): `##theme##` `<title>`, fiches,
  `###`. Fiche: `#label#` `<title>` `!tga!`; with a picture `<caption>` `<text>` and as
  many `$link$` as the text holds `$word$` (at most 10); with `!!` a table of rows `<a>`
  `<b>` (`<>` = empty; at most 20), each with links; then `##`. Stray bytes between tokens
  are passed over (7 in the corpus).
- **CREDITS.TXT** (22 pages): lines; `#` starts a heading line (drawn in another colour);
  a line with `/` as first or second byte ends the page (blank lines after it are
  dropped); at most 30 lines a page, one page every 5 s, centred. The final `##` line is
  an empty heading; the credits end at the end of the file.

### ZIK music (China)

No header: the whole file is signed 16-bit little-endian stereo PCM at 22050 Hz, and it
loops from byte 0 (no loop points). The game streams it through a 512 KiB DirectSound
buffer and fades the volume (0..127) in and out. The track is chosen by the first three
letters of the place name (E-0206). ScummVM's `Audio::makeRawStream` (FLAG_16BITS |
FLAG_STEREO | FLAG_LITTLE_ENDIAN) inside a `LoopingAudioStream` plays it. Not APC.

### chine.cfg (China)

16 bytes, four LE u32 (E-0501, E-0207): navigation speed 0..4 (very slow .. very rapid,
default 2), subtitles 0/1 (default 1), music 0/1 (default 1), save mode (1 = automatic:
one save per player emblem, rewritten on every place change; 0 = manual named saves).
The corpus file: 2, 1, 1, 0. In ScummVM these become game options, not a file.

### Save games (China; specced from code only)

No save is in the corpus; the layout comes from the reading and writing routines alone
(E-0208) and is not checked against a real file. Files: automatic mode
`Data\Saved\_game<1..12>.sav` (one per emblem slot), manual mode `Data\Saved\<NAME>.sav`
(A-Z, 0-9, space). Little-endian, in order:

| Offset | Size | Field |
|---:|---:|---|
| 0 | 227 x u32 | game variables in table order (220 named, 5 unnamed, terminator, 1 padding dword) |
| 908 | 36 x (u32, s32) | object table entries' first two fields (35 objects + 8 bytes past the table; meaning Q-0200) |
| 1196 | 256 | current place name, NUL-terminated (the rest is stack garbage) |
| 1452 | f32, f32 | view angles (Q-0201) |
| 1460 | u32 | number of minutes held (50 slots, unchecked) |
| 1464 | per minute | u32 length, then the MINUTES.TXT id without NUL (14 bytes at most) |

Loading a save restores all of this and then enters the saved place. `sav.py --tables`
lists the variable and object names from CHINE.EXE.
