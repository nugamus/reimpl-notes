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

## Not this type

`BOGUS.BMA`, `BOGUS2.BMA`, `BOGUS2.BMP` in `DATA/SY/IMAGE` of the DVD, CD disc 1 and ISO
disc 1 (MD5 `00a84375…`, 181 bytes) hold the text of a `.dia` subtitle file; no EXE names
them (E-0017). The validators report them as "not this type".

## Damaged in the corpus

53 `.wac` files of the DVD's added languages (SPA 18, ITA 13, HOL 11, SWE 11) are damaged
on the disc: 52 have a run of undecodable bytes (about 4 KB) after a chunk that crosses a
64 KiB file offset, one (`N2/SOUND/ITA/1437.WAC`) has no WAV header. `wac_damaged.txt`
lists them; `wac.py` reports them as excluded (E-0021, Q-0004).
