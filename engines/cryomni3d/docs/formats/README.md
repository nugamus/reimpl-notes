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
