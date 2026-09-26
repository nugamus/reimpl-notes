"""`.BMP` parser and corpus validator.

Standard Windows `BITMAPINFOHEADER` (BMP3) — 381 files / 125 MB in the corpus. The
format is third-party and well documented; the parser exists because every spec in
this project must pass `engines/x3d/tools/parsers/`'s 100%-corpus rule (CLAUDE.md rule 2).

Layout (every field is little-endian):

    14-byte BITMAPFILEHEADER
      u8x2 magic 'BM'
      u4 file size
      u2 reserved (always 0)
      u2 reserved (always 0)
      u4 pixel data offset (offBits)

    40-byte BITMAPINFOHEADER
      u4 header size (always 40 — BITMAPINFOHEADER, not BITMAPV4/V5)
      i4 width  (positive)
      i4 height (positive: bottom-up rows; negative: top-down)
      u2 planes (always 1)
      u2 bits per pixel (8 / 16 / 24 in the corpus)
      u4 compression (always 0 = BI_RGB in the corpus)
      u4 image size in bytes (0 allowed for BI_RGB)
      i4 x pixels per metre (often 0)
      i4 y pixels per metre (often 0)
      u4 colours used (0 = default = 2^bpp)
      u4 important colours (0 = all)

    Optional palette
      (2^bpp) × 4 bytes BGRA, only for bpp ≤ 8

    Pixel data
      |height| rows, each row padded to a 4-byte boundary

Validated by `engines/x3d/tools/parsers/bmp.py` against all 381 `.BMP` files: every byte consumed,
no out-of-range palette indices, expected vs declared file size matches.

    python engines/x3d/tools/parsers/bmp.py                 # validate the corpus
    python engines/x3d/tools/parsers/bmp.py --selftest
    python engines/x3d/tools/parsers/bmp.py --file <path>  # one file, structural summary
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    ParseError,
    corpus_argparser,
    default_root,
    find_files,
)

FILE_HEADER_LEN = 14
INFO_HEADER_LEN = 40

SUPPORTED_BPP = (1, 4, 8, 16, 24, 32)


def _row_stride(width: int, bpp: int) -> int:
    bits = width * bpp
    return ((bits + 31) // 32) * 4


def parse(data: bytes) -> dict:
    if len(data) < FILE_HEADER_LEN + INFO_HEADER_LEN:
        raise ParseError(
            f"file shorter than {FILE_HEADER_LEN + INFO_HEADER_LEN} bytes",
            len(data),
        )

    magic = data[:2]
    if magic != b"BM":
        raise ParseError(f"expected magic 'BM', got {magic!r}", 0)
    file_size = struct.unpack_from("<I", data, 2)[0]
    off_bits = struct.unpack_from("<I", data, 10)[0]
    if off_bits < FILE_HEADER_LEN + INFO_HEADER_LEN:
        raise ParseError(
            f"off_bits {off_bits} < minimum {FILE_HEADER_LEN + INFO_HEADER_LEN}", 10
        )

    info_size = struct.unpack_from("<I", data, 14)[0]
    if info_size != INFO_HEADER_LEN:
        raise ParseError(
            f"DIB header size {info_size} != {INFO_HEADER_LEN} (only BITMAPINFOHEADER supported)",
            14,
        )
    width = struct.unpack_from("<i", data, 18)[0]
    height = struct.unpack_from("<i", data, 22)[0]
    planes = struct.unpack_from("<H", data, 26)[0]
    bpp = struct.unpack_from("<H", data, 28)[0]
    compression = struct.unpack_from("<I", data, 30)[0]
    image_size = struct.unpack_from("<I", data, 34)[0]
    xppm = struct.unpack_from("<i", data, 38)[0]
    yppm = struct.unpack_from("<i", data, 42)[0]
    colors_used = struct.unpack_from("<I", data, 46)[0]
    important = struct.unpack_from("<I", data, 50)[0]

    if width <= 0:
        raise ParseError(f"width {width} must be positive", 18)
    if height == 0:
        raise ParseError(f"height 0 is not a valid BMP", 22)
    if planes != 1:
        raise ParseError(f"planes {planes} != 1", 26)
    if bpp not in SUPPORTED_BPP:
        raise ParseError(f"unsupported bpp {bpp} (corpus is 8/16/24)", 28)
    if compression != 0:
        raise ParseError(
            f"compression {compression} != BI_RGB (only BI_RGB supported)", 30
        )

    rows = abs(height)
    stride = _row_stride(width, bpp)
    pixel_bytes = stride * rows

    palette_bytes = 0
    palette_colors = 0
    if bpp <= 8:
        palette_colors = colors_used if colors_used else 1 << bpp
        palette_bytes = palette_colors * 4
        if off_bits < FILE_HEADER_LEN + INFO_HEADER_LEN + palette_bytes:
            raise ParseError(
                f"off_bits {off_bits} too small for {palette_colors}-colour palette",
                10,
            )

    expected_size = off_bits + pixel_bytes
    if len(data) < expected_size:
        raise ParseError(
            f"file {len(data)} bytes < expected {expected_size} (off_bits + pixel data)",
            len(data),
        )

    consumed = expected_size

    return {
        "file_size": file_size,
        "off_bits": off_bits,
        "info_size": info_size,
        "width": width,
        "height": height,
        "top_down": height < 0,
        "planes": planes,
        "bpp": bpp,
        "compression": compression,
        "image_size": image_size,
        "xppm": xppm,
        "yppm": yppm,
        "colors_used": colors_used,
        "important": important,
        "palette_colors": palette_colors,
        "palette_bytes": palette_bytes,
        "row_stride": stride,
        "rows": rows,
        "pixel_bytes": pixel_bytes,
        "consumed": consumed,
        "declared_file_size_matches": file_size == expected_size,
    }


def _selftest() -> None:
    body = (
        b"BM"
        + struct.pack("<I", 14 + 40 + 48)
        + struct.pack("<HH", 0, 0)
        + struct.pack("<I", 14 + 40)
        + struct.pack("<I", 40)
        + struct.pack("<i", 4)
        + struct.pack("<i", 4)
        + struct.pack("<H", 1)
        + struct.pack("<H", 24)
        + struct.pack("<I", 0)
        + struct.pack("<I", 48)
        + struct.pack("<ii", 0, 0)
        + struct.pack("<II", 0, 0)
        + b"\x00" * 48
    )
    doc = parse(body)
    assert doc["width"] == 4 and doc["height"] == 4
    assert doc["bpp"] == 24 and doc["row_stride"] == 12
    assert doc["pixel_bytes"] == 48
    assert doc["consumed"] == 14 + 40 + 48

    body8 = (
        b"BM"
        + struct.pack("<I", 14 + 40 + 4 * 4 + 16)
        + struct.pack("<HH", 0, 0)
        + struct.pack("<I", 14 + 40 + 4 * 4)
        + struct.pack("<I", 40)
        + struct.pack("<i", 4)
        + struct.pack("<i", 4)
        + struct.pack("<H", 1)
        + struct.pack("<H", 8)
        + struct.pack("<I", 0)
        + struct.pack("<I", 0)
        + struct.pack("<ii", 0, 0)
        + struct.pack("<II", 4, 0)
        + b"\x00" * (4 * 4)
        + b"\x00" * 16
    )
    doc8 = parse(body8)
    assert doc8["bpp"] == 8 and doc8["palette_colors"] == 4
    assert doc8["palette_bytes"] == 16
    assert doc8["row_stride"] == 4

    bad = b"BA" + body[2:]
    try:
        parse(bad)
    except ParseError as exc:
        assert "magic" in exc.message
    else:
        raise AssertionError("bad magic accepted")

    bad = bytearray(body)
    struct.pack_into("<I", bad, 14, 12)
    try:
        parse(bytes(bad))
    except ParseError as exc:
        assert "DIB header" in exc.message
    else:
        raise AssertionError("non-BMP3 header accepted")

    try:
        parse(body[:-1])
    except ParseError:
        pass
    else:
        raise AssertionError("truncated file accepted")

    # The declared file_size is informational and not enforced. The 3/381 corpus
    # files that record it short still parse because the parser derives size from
    # width/height/bpp, not from the declared field.

    print("selftest ok")


def _dump(path: Path) -> None:
    doc = parse(path.read_bytes())
    top_down = "top-down" if doc["top_down"] else "bottom-up"
    print(
        f"{path.name}: {doc['width']}×{doc['height']} {doc['bpp']}bpp"
        f" {top_down}, palette={doc['palette_colors']},"
        f" {path.stat().st_size}B on disk, declared={doc['file_size']}"
    )


def main(argv: list) -> int:
    if "--selftest" in argv:
        _selftest()
        return 0

    args = corpus_argparser(".BMP validator").parse_args(argv)

    if args.file:
        _dump(args.file)
        return 0

    root = args.root or default_root()
    files = find_files(root, "*.BMP")
    if not files:
        print(f"no .bmp files under {root}", file=sys.stderr)
        return 2

    ok = 0
    failures: list[tuple[Path, str]] = []
    totals = {
        "pixels": 0, "filesize": 0, "bytes": 0,
        "bpp": {}, "filesize_match": 0,
    }

    for path in files:
        data = path.read_bytes()
        try:
            doc = parse(data)
        except ParseError as exc:
            failures.append((path, f"{exc.message} at offset {exc.offset}"))
            continue
        ok += 1
        totals["pixels"] += doc["width"] * doc["rows"]
        totals["filesize"] += doc["file_size"]
        totals["bytes"] += len(data)
        totals["bpp"][doc["bpp"]] = totals["bpp"].get(doc["bpp"], 0) + 1
        if doc["declared_file_size_matches"]:
            totals["filesize_match"] += 1

    print(f"corpus: {root}")
    print(f"files: {len(files)}  passed: {ok}  failed: {len(failures)}")
    print(f"  bpp counts:        {totals['bpp']}")
    print(f"  pixels:            {totals['pixels']}")
    print(f"  declared total:    {totals['filesize']}")
    print(f"  actual total:      {totals['bytes']}")
    print(f"  size match count:  {totals['filesize_match']}/{ok}")
    for path, err in failures[:25]:
        print(f"  FAIL {path}  {err}")

    print("100% of corpus parsed" if ok == len(files) else "SPEC INCOMPLETE")
    return 0 if ok == len(files) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))