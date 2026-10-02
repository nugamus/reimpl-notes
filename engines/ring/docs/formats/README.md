# Formats (Ring engine)

One row per recovered format: status here, the Kaitai spec next to it (`<fmt>.ksy`), the
validator in `engines/ring/tools/parsers/<fmt>.py` (with `--selftest`), the proof in
`EVIDENCE.md`. A format is done only when its validator passes 100% of that type across
every version in `games/ring/discs/` and `games/prophet-and-assassin/discs/`, every byte
consumed.

The corpus of a type is its loose files and the members of every archive of that type
(`parsers/common.py`); identical contents are parsed once. "Files" counts every instance,
"distinct" the contents parsed.

| Format | Files (distinct) | Validator | Spec | Evidence | Status |
|---|---:|---|---|---|---|
| `.at2` / `.at3` archive | 41 (23) | `at2.py` | `at2.ksy` | E-0016 | done |
| Packed image (BMA): loose `.bma`, `.bmp` members of `.at2` | 14,408 (4,895) + 6 misnamed text | `bma.py` | `bma.ksy` | E-0017 | done |
| Packed TGA (TGC): `.tga` members of `.at2` | 22,868 (1,501) | `tgc.py` | `tgc.ksy` | E-0018 | done |
| Plain BMP / TGA on disk | 53 (21) + 3 misnamed text | `bmp.py` | below | E-0019 | done |
| `.aqc` panorama node | 587 (351) | `aqc.py` | `aqc.ksy` | E-0020 | done (1 file with trailing bytes, Q-0003) |
| `.wac` / `.was` packed sound | 4,637 (2,638) + 53 damaged | `wac.py` (+ `wac_damaged.txt`) | `wac.ksy` | E-0021 | done (damaged DVD files: Q-0004) |
| `.wav` | 744 (210) | `wav.py` | below | E-0022 | done |
| `.dia` subtitles, `.dan` lip timing | 7,755 (4,498) | `dia.py` | below | E-0025 | done |
| Configuration: `fl.ini`, `aPre.ini`, `cd.ini`, `aObj.ini`, `aMes.ini`; `.aba` save lists | 38 (19) | `ini.py` | below | E-0026 | done (`.aba` records not specced: corpus has none) |
| Windows raster fonts: `arxrin.fon`, DVD `ARXRIN.GRE`/`.HEB`/`.SLO` | 7 (4) | `fon.py` | below | E-0043 | done |
| `.cnm` / `.ci2` video, `CNM UNR` images in `.at3` | 3,462 (2,780) + 1 damaged | `cnm.py` | `cnm.ksy` | E-0024, E-0028, E-0350..E-0357 | done: HBR (Ring DVD/CD) and UNR (Ring ISO, Prophet) decoded in full; the damaged ISO file plays 132 of its frames (E-0356) |

## Packed bit stream

Shared by the packed images, and per Templier's engine by panoramas and sound
(`RING_DVD.EXE` 0x4308e0, E-0017; `parsers/bitstream.py`, C build `parsers/ringdec.c`).
Arguments: a literal width `v`, an index width `i` (always 6 so far), a start and an end
bit. Bits are read MSB first (a big-endian dword at byte `pos >> 3`). A cache of 64
(value, stamp) slots starts zeroed, the replacement slot `r` and the last slot `l` at 0.

- `0` + `v` bits: literal; emitted, stored in slot `r`, `l = r` (no stamp).
- `10` + `i` bits: slot index `s`; its value is emitted, its stamp set to the bit position
  after the code, `l = s`; if `s == r`, `r` becomes the slot with the smallest stamp
  (lowest index on ties).
- `11`: the previous value again; slot `l` stamped; if `l == r`, `r` is recomputed.

Decoding runs while the position is below the end bit, so a stream may yield one extra
code from its padding bits.

## HBR video codec

(`RING_DVD.EXE` 0x42ce30, E-0028; C in `parsers/ringdec.c` `ring_hbr`.) A picture is a
raster of 4×1-pixel tiles (four RGB555 words), rows bottom-up. Each 'T' and 'S' chunk
carries a tile table (8 bytes per tile), a code stream and a run list (the chunk's last
`runs_size` bytes: entries of a byte count `c` then `c/2` u16 tile indices). The stream is
read in nibbles. At a byte boundary: a byte `< 0x80` starts a new 12-bit code (it and the
next byte's high nibble); a byte `>= 0x80` repeats ring slot `b - 0x80`. Mid-byte: a low
nibble `< 8` starts a new 11-bit code (it and the next byte); otherwise ring slot
`nibble·16 + next high nibble - 0x80`. New codes go into a 128-slot ring (write position
back to 0 every chunk, contents kept). A code `<= ntiles` emits one tile; `ntiles < code <
0x780` emits run number `code - ntiles` of the run list; `code >= 0x780` emits back-buffer
segment `code - 0x780`. Each emitted code's output is remembered for the rest of the chunk,
and a ring hit repeats it. A 'T' chunk decodes into the back buffer, whose segment lengths
(in tiles) precede its payload; an 'S' chunk decodes into the picture, which is kept
between frames: a short frame leaves the rest unchanged, and a stream may emit more than
the picture (up to the engine's 0x8cfff-byte check).

## UNR video codec

(E-0350..E-0357; C in `parsers/ringdec.c` `ring_unr_tiles`, `ring_unr1_frame`,
`ring_unr2_frame`, checked against the original code run in Unicorn on every picture,
`tools/unr_oracle.py`.) Two codecs share the "CNM UNR" container. The program picks one, not
the file: v1 in the Ring ISO EXE (`RING_ISO.EXE` SControl 0x42c680, picture 0x436440), v2
in Prophet's (`LEGEND.EXE` tiles 0x424240, picture 0x423630). In the corpus the header's
+0x0c tells them apart: 1250 in every Ring ISO file, 1500 or 2500 in every Prophet file.

The picture is 32-bit (bytes B, G, R, 0), rows bottom-up like HBR, kept between frames, and
built from 4×1-pixel tiles. Header byte +0x1a ("interlaced"; all 440 Ring ISO videos, one
Prophet video) decodes half the rows and stores tiles at half scale.

Chunks. 'S' and 'U' (0x2f-byte header): u32 size, u32 map_size, u16 ntiles, u16
tile_width (4 everywhere; the EXEs also have 2-pixel variants no file uses), u32 width,
u32 height, u32 unk_14, u32 unk_18 (= unk_14; 1250 Ring ISO, 1500 or 2500 Prophet videos,
0 in `.at3` pictures; Q-0110), 19 zero bytes; the payload is the picture stream (map_size
bytes), then a tile table if map_size < size. 'T' (v2; v1's TControl returns without reading):
u32 size, u16 ntiles, u16 tile_width, a tile table. 'U' and 'S' decode alike; Play skips
an 'S' when late, never a 'U'. Ring ISO: every picture is an 'S' with its own tiles;
Prophet videos: groups of a 'T', a 'U' and up to three 'S' (2,854 of 2,903 groups have
three), the pictures without tiles; `.at3` pictures: one 'S' with tiles.

Tile table (both). ntiles counts every tile: tile 0 is 16 raw bytes, each next tile is
the previous one plus deltas, a delta being followed by a sign bit when non-zero (1 =
subtract; bytes wrap). v1, bits MSB first: per tile 3 bits n, then 16 deltas of n + 1 bits
in byte order. v2, bits LSB first (read as little-endian 64-bit words): per byte lane
c = 0..3, 3 bits n; n = 7: four raw bytes (pixels 0..3 of lane c); otherwise four n-bit
deltas (n = 0: no bits). Both decoders run one tile further (tile ntiles) into the bytes
after the data; no index uses it. Interlaced: tiles 0..ntiles − 1 are then shifted left
one bit as u32.

v1 picture (interlaced only in the corpus; the EXE has plain variants). Bits MSB first,
from the first payload byte; tile rows = h/2 + 1, w/4 tiles each, "up" being the tile row
decoded before. Per tile: `0` + an index (10 bits if ntiles < 0x400, 11 if < 0x800, else
12): that tile; or `1` + a vector:
`1` up; `01` + 2 bits: (−1,0) (−1,−1) (1,−1) (0,−2); `00` + 4 bits: (−2,−3) (2,−3) (−1,−4)
(1,−4) (−1,−2) (1,−2) (0,−3) (0,−4) (−2,0) (−2,−1) (2,−1) (−2,−2) (2,−2) (−1,−3) (1,−3)
(0,−5) (in tiles, tile rows): copy the 4 pixels there, as already written (the buffer is
linear: left of column 0 is the end of a previous row). Tile row 0 goes to picture row 0
and codes only (−1,0) and (−2,0); tile rows r = 1..m go to picture row 2r, m = h/2 − 1
when h is even, else (h − 1)/2, and set row 2r − 1 to (new >> 1) + (row 2r − 2 >> 1) per
u32, or to the new value itself for `up`; an even h ends with one tile row on picture row
h − 1, where a vector's first tile row up is one picture row and each further one two.

v2 picture. Bits LSB first, from the first payload byte. First a map of u16 tile numbers,
w/4 per row, h rows (h/2 + 1 interlaced), in groups of 8 entries: `1` copies the 8 entries
one map row up; `0` codes 8 entries, each (bits in read order):
- `1`: the entry above;
- `000` + b bits (b = bit length of ntiles): that number;
- `001` + 4 bits d + sign: above + d + 1, or above − d − 1 when the sign is 1;
- `010`: one of the left, up-left, up-right and up-up entries, those that exist and differ
  from the entry above, each value once, in that order: one candidate takes no bit, two
  take 1 bit, three or four 2 bits;
- `011` + 4 bits k: slot k + 1 of the history of the entry above.

Every entry coded by `000`, `001` or `010` below the first row is pushed on the history of
the entry above it: 16 slots per tile number, written cyclically from slot 1, cleared each
picture. The map ends when `rows` row ends have been counted, a group counting at most one:
under 8 tiles a row the count runs past the map; those entries are never drawn and their
bits are not in the file. Then each entry draws its tile; 0 leaves the picture as it was.
Interlaced: map row r goes to picture row 2r and, for r ≥ 1, sets row 2r − 1 to (new +
row 2r − 2) per u32, the two u32 of a pixel pair then shifted right by one as one 64-bit
value (only where the entry is not 0); an even h ends with a plain row on h − 1.

Every stream ends in the last byte of its part (byte padding only); no picture reads a tile
past ntiles − 1 or a vector outside the picture, no v1 first row codes another vector, no
v2 `010` choice falls past its candidates (E-0355).

## Plain BMP / TGA

On disk only (`aImage::Load` with 'e'): BMP = 'BM', 40-byte info header, 24 bpp, BI_RGB,
rows padded to 4 bytes, bottom-up, optionally 2 zero bytes after the pixels that the
file-size field counts. TGA = type 2, 24 or 32 bpp, no id, no colour map, optional TGA 2.0
footer.

## Plain WAV

RIFF WAVE with even-padded chunks to the RIFF size; a PCM `fmt ` and a `data` chunk.

## Dialog text

`.dia` (`aDialog::ReadLyrics` 0x427090, `ParseLyricLine` 0x427550): the first 0x1000 bytes,
cut at each LF; the byte before each LF is blanked (the CR, or the last character of a line
in files with bare LFs); each complete line is spaces, a decimal time, optionally
`,digits:digits.digits`, spaces, the text; `#` splits the text into two parts. Bytes after
the last LF are never parsed. `.dan` (`aDialog::ReadDialogAnimation` 0x4271b0): `%d`, then
`%d %d %d` triples until the scan fails.

## Configuration files

Whitespace-token files read with `fscanf` (`fl.ini`: a count then that many `KEY: value`
pairs; `aPre.ini`: four integers; `cd.ini`: the disc number) and line files (`aObj.ini`: an
object id line followed by one `LAN<ws>#text#…` line per language, 10 in the DVD, 5 in the
CD and ISO versions, 7 in Prophet; `aMes.ini`: a message key followed by `LAN<ws>#title#text`
lines). The readers match a language by its first three characters (the CD/ISO `aMes.ini`
has a `TA` line no language matches). Details in `parsers/ini.py`.

## Not read by the game

`INSTALL/*.LAN`, `*.LIS`, `*.UNI` (installer), `aObj.BAK` (CD disc 6), `.pdf`/`.txt`/`.htm`
documents, and `ARXRIN.GRE`/`.HEB`/`.SLO`: no game EXE names them (they are fonts, below).

## Fonts

The EXEs add one font file each with `AddFontResourceA` (`arxrin.fon`, Prophet
`Legend.FON`). A standard Windows `.FON`: an NE executable whose resources are one FONTDIR
and FNT 2.0 raster fonts (118-byte header, a table of `width u16, offset u16` for
characters first..last plus a sentinel, column-major glyph bitmaps of ceil(width/8) × pixel
height bytes, the face name). `arxrin.fon` (identical in the three editions, MD5
`1005a256…`) holds "ARX Pilgrim L" at 8, 10, 12, 14, 18, 24 points, cell heights 13, 16,
20, 24, 29, 37, ascents 11, 13, 16, 19, 23, 29, characters 32..255, default character 128,
weight 400, charset 0. `ARXRIN.SLO` is the same six fonts (0xFF padding after one font's
dfSize); `ARXRIN.HEB` and `ARXRIN.GRE` are the same file: "ArxelHebrew" 9, 12, 16 points,
charset 2. Prophet's `Legend.FON` holds one font, "Arxel1" 8 points, characters 31..255.
`fon.py` accounts for every byte of every font resource.

## Not this type

`BOGUS.BMA`, `BOGUS2.BMA`, `BOGUS2.BMP` in `DATA/SY/IMAGE` of the DVD, CD disc 1 and ISO
disc 1 (MD5 `00a84375…`, 181 bytes) hold the text of a `.dia` subtitle file; no EXE names
them (E-0017). The validators report them as "not this type".

## Damaged in the corpus

53 `.wac` files of the DVD's added languages (SPA 18, ITA 13, HOL 11, SWE 11) are damaged
on the disc: 52 have a run of undecodable bytes (about 4 KB) after a chunk that crosses a
64 KiB file offset, one (`N2/SOUND/ITA/1437.WAC`) has no WAV header. `wac_damaged.txt`
lists them; `wac.py` reports them as excluded (E-0021, Q-0004). One ISO video
(`disc4/data/fo/Pla/fos03n02_s05n01.cnm`) has a damaged chunk at frame 132 (E-0024): the ISO
EXE reads chunks in order, so it plays frames 0..131 and ends the video there (E-0356).
