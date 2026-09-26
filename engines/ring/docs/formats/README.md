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
| `.cnm` / `.ci2` video, `CNM UNR` images in `.at3` | 3,462 (2,780) + 1 damaged | `cnm.py` | `cnm.ksy` | E-0024 | container done; codec not yet decoded (Q-0005 for the damaged file) |

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
documents, and `ARXRIN.GRE`/`.HEB`/`.SLO`: no game EXE names them. The EXEs load one font
each (`arxrin.fon`, Prophet `Legend.FON`, via `AddFontResourceA`): a standard Windows
`.FON`, validator not written yet.

## Not this type

`BOGUS.BMA`, `BOGUS2.BMA`, `BOGUS2.BMP` in `DATA/SY/IMAGE` of the DVD, CD disc 1 and ISO
disc 1 (MD5 `00a84375…`, 181 bytes) hold the text of a `.dia` subtitle file; no EXE names
them (E-0017). The validators report them as "not this type".

## Damaged in the corpus

53 `.wac` files of the DVD's added languages (SPA 18, ITA 13, HOL 11, SWE 11) are damaged
on the disc: 52 have a run of undecodable bytes (about 4 KB) after a chunk that crosses a
64 KiB file offset, one (`N2/SOUND/ITA/1437.WAC`) has no WAV header. `wac_damaged.txt`
lists them; `wac.py` reports them as excluded (E-0021, Q-0004). One ISO video
(`disc4/data/fo/Pla/fos03n02_s05n01.cnm`) has a damaged chunk at frame 132 (E-0024, Q-0005).
