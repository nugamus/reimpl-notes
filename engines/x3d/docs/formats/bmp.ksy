meta:
  id: bmp3
  title: Windows BITMAPINFOHEADER (BMP3)
  file-extension: bmp
  endian: le

doc: |
  Standard Windows 3.x `BITMAPINFOHEADER` BMP. The 381 `.BMP` files in the Monet corpus
  (131 MB total, all `BM` magic) are uniformly BMP3: 14-byte file header, 40-byte info
  header, no compression (`BI_RGB` only), bpp in {8, 16, 24}. Format is third-party and
  documented; this spec exists because every format in the project must ship with a
  `.ksy` and a validator that parses 100% of the corpus.

  The declared `file_size` field in the file header is informational. Three of 381
  corpus files (`SaveRetourD.BMP`, `SaveSommaireD.BMP`, `U01_04P.BMP`) record it short
  by 17–100 bytes without affecting on-disk size — the writer must have flushed the
  header before the trailing rows. The parser derives size from
  `off_bits + row_stride × |height|`, which is what the on-disk shape actually is.

  No `BITMAPV4`/`BITMAPV5` (108/124-byte DIB headers), no `BI_BITFIELDS` /
  `BI_RLE4` / `BI_RLE8` / `BI_JPEG` / `BI_PNG` compression — the corpus has none of
  these.

seq:
  - id: file_header
    type: file_header
  - id: info_header
    type: info_header
  - id: palette
    type: palette
    if: info_header.bpp <= 8
  - id: pixel_data
    type: pixel_data

types:
  file_header:
    doc: 14-byte BITMAPFILEHEADER.
    seq:
      - id: magic
        contents: 'BM'
      - id: file_size
        type: u4
        doc: |
          Declared on-disk size. Informational — the parser derives the actual shape
          from the info header instead.
      - id: reserved1
        type: u2
      - id: reserved2
        type: u2
      - id: off_bits
        type: u4
        doc: Byte offset of the first pixel row. Always 54 for 24/16bpp; `54 +
          palette_size` for 8bpp (palette is `4 × 2^bpp` bytes).

  info_header:
    doc: 40-byte BITMAPINFOHEADER (BMP3). The corpus contains only this DIB variant.
    seq:
      - id: info_size
        contents: [0x28, 0x00, 0x00, 0x00]
        doc: |
          DIB header size, always 40 (`0x00000028`) for BITMAPINFOHEADER.
      - id: width
        type: s4
        doc: Pixels. Must be positive.
      - id: height
        type: s4
        doc: |
          Pixels. Positive: bottom-up rows. Negative: top-down. Zero is invalid.
      - id: planes
        contents: [0x01, 0x00]
        doc: Always 1.
      - id: bpp
        type: u2
        doc: Bits per pixel. Corpus is 8, 16, 24.
      - id: compression
        contents: [0x00, 0x00, 0x00, 0x00]
        doc: |
          Always `BI_RGB` (0). The corpus has no `BI_BITFIELDS` (3), `BI_RLE4` (2),
          `BI_RLE8` (1), `BI_JPEG` (4) or `BI_PNG` (5).
      - id: image_size
        type: u4
        doc: Pixel data size in bytes; may be 0 under BI_RGB.
      - id: xppm
        type: s4
        doc: X pixels per metre; often 0.
      - id: yppm
        type: s4
        doc: Y pixels per metre; often 0.
      - id: colors_used
        type: u4
        doc: |
          Palette size in entries. `0` means the default `2^bpp`. Only meaningful
          when bpp ≤ 8; the corpus has exactly one 8bpp file, which uses the
          default 256-entry palette.
      - id: important
        type: u4
        doc: Required palette colours; 0 means all.

  palette:
    doc: |
      `BGRA` colour entries, `(2^bpp)` of them unless `colors_used` is non-zero.
      Only emitted when `bpp ≤ 8`.
    seq:
      - id: entries
        type: palette_entry
        repeat: expr
        repeat-expr: info_header.colors_used != 0 ? info_header.colors_used : (1 << info_header.bpp)

  palette_entry:
    seq:
      - id: blue
        type: u1
      - id: green
        type: u1
      - id: red
        type: u1
      - id: alpha
        type: u1

  pixel_data:
    doc: |
      Bottom-up (height > 0) or top-down (height < 0) rows of pixel data, each row
      padded to a 4-byte boundary. Total bytes
      `((width * bpp + 31) // 32) * 4 × |height|`.
    seq:
      - id: rows
        type: row
        repeat: expr
        repeat-expr: info_header.height < 0 ? -info_header.height : info_header.height

  row:
    seq:
      - id: pixels
        size-eos: true
        doc: |
          One row of pixels, left-to-right, padded to a 4-byte boundary. Parser does
          not interpret the per-pixel bit packing — only the row stride matters.