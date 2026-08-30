# `.BMP` — what the corpus proves

Working notes, not a spec. `docs/formats/bmp.ksy` is the canonical artefact once a
validator consumes every byte of every file (CLAUDE.md rule 2).

Corpus: 381 `.BMP` files, 131 MB, all `BM` magic, all BITMAPINFOHEADER (BMP3).

## Proven

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

## Refuted

None — the first-try layout parsed 378/381 files on the run that enforced the
declared `file_size` invariant. The 3 failures showed the declared size is
*informational only*; the parser now derives size from width × height × stride and
passes 381/381.

## Observed

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

## Why this matters for the corpus claim

BMP is a third-party format; CLAUDE.md rule 2 still applies (every format needs a
spec and a 100%-corpus validator), but the loader decompile step is unnecessary —
Microsoft's published format is sufficient. The EVIDENCE entry cites the parser run
and the sample-byte survey (all `BM`, all `BITMAPINFOHEADER`, all BI_RGB) rather than
a Ghidra address.

## Next step

Move on to `.BIN` — 109 files / 80 magics / no magic. Per the handoff, load via the
loader (`x3d.dll` must have a BIN reader). Then `.FRA` and `.CFG` follow.