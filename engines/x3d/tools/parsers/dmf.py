r"""`.DMF` texture parser and corpus validator.

Reader: x3d.dll (E-0038). `X3d_Map_Init` (`0x10001618`) replaces a map name's extension
with `.dmf` (`0x10027c14`); `FUN_10016020` opens the file, `FUN_10010ba0` checks the header
and walks the chunks with `FUN_100108a0`:

    u16 magic = 0xfb00, u32 total_size (== file size), then chunks until offset == total:
    u16 id, u32 size (includes this 6-byte header)
      fb10  u16 bpp, u16 width, u16 height      bpp 8 (palette), 15 (555), 16 (565)
      fb20  256 x 4-byte palette entries
      fb21  4 x u8 colour key; the first three are R, G, B (packed to 16 bits at load)
      fb22  u32 unk_fb22
      fb23  u32 unk_fb23
      fb30  raw pixels: w*h bytes (bpp 8) or w*h u16 (bpp 15/16)
      fb31  vector-quantised 16-bit pixels (`FUN_10010770`): a 256-entry codebook of 2x2
            u16 blocks (top-left, top-right, bottom-left, bottom-right; 0x800 bytes), then
            (w/2)*(h/2) u8 block indices, row-major
      other ids are skipped by size

A 15-bit map is converted to 565 when the display is 16-bit (`FUN_10016020`).

    python engines/x3d/tools/parsers/dmf.py                 # validate the corpus
    python engines/x3d/tools/parsers/dmf.py --selftest
    python engines/x3d/tools/parsers/dmf.py --png <file.dmf> <out.png>
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ParseError, Reader, main_for  # noqa: E402

KNOWN = (0xFB10, 0xFB20, 0xFB21, 0xFB22, 0xFB23, 0xFB30, 0xFB31)


def parse(data: bytes) -> dict:
    r = Reader(data)
    if r.u16() != 0xFB00:
        raise ParseError("bad magic", 0)
    total = r.u32()
    r.check(total == len(data), f"total size {total} != file size {len(data)}", 2)
    out: dict = {"chunks": []}
    while r.pos < total:
        start = r.pos
        cid, size = r.u16(), r.u32()
        r.check(size >= 6 and start + size <= total, f"bad chunk size {size}", start)
        end = start + size
        out["chunks"].append(cid)
        if cid == 0xFB10:
            out["bpp"], out["width"], out["height"] = r.u16(), r.u16(), r.u16()
            r.check(out["bpp"] in (8, 15, 16), f"bpp {out['bpp']}", start)
        elif cid == 0xFB20:
            out["palette"] = r.bytes(0x400)
        elif cid == 0xFB21:
            out["key"] = r.bytes(4)
        elif cid == 0xFB22:
            out["unk_fb22"] = r.u32()
        elif cid == 0xFB23:
            out["unk_fb23"] = r.u32()
        elif cid == 0xFB30:
            n = out["width"] * out["height"] * (1 if out["bpp"] == 8 else 2)
            out["pixels"] = r.bytes(n)
        elif cid == 0xFB31:
            r.check(out["bpp"] != 8, "vq chunk in a paletted map", start)
            out["codebook"] = r.bytes(0x800)
            out["indices"] = r.bytes((out["width"] // 2) * (out["height"] // 2))
        else:
            r.skip(size - 6)
        r.check(r.pos == end, f"chunk {cid:#x} not fully consumed ({end - r.pos} left)", start)
    r.expect_eof()
    r.check("width" in out and ("pixels" in out or "indices" in out), "no image", 0)
    return out


def to_rgb(d: dict, palette_order: str = "rgb") -> tuple[int, int, bytes]:
    """RGB888 bytes, for inspection only."""
    w, h = d["width"], d["height"]
    px = []
    if d["bpp"] == 8:
        pal = d["palette"]
        o = (0, 1, 2) if palette_order == "rgb" else (2, 1, 0)
        for i in d["pixels"]:
            e = pal[i * 4:i * 4 + 4]
            px.append(bytes((e[o[0]], e[o[1]], e[o[2]])))
        return w, h, b"".join(px)
    if "pixels" in d:
        vals = struct.unpack(f"<{w * h}H", d["pixels"])
    else:
        cb = struct.unpack("<1024H", d["codebook"])
        vals = [0] * (w * h)
        for by in range(h // 2):
            for bx in range(w // 2):
                c = d["indices"][by * (w // 2) + bx] * 4
                y, x = by * 2, bx * 2
                vals[y * w + x], vals[y * w + x + 1] = cb[c], cb[c + 1]
                vals[(y + 1) * w + x], vals[(y + 1) * w + x + 1] = cb[c + 2], cb[c + 3]
    out = bytearray()
    for v in vals:
        if d["bpp"] == 15:
            out += bytes(((v >> 10 & 31) << 3, (v >> 5 & 31) << 3, (v & 31) << 3))
        else:
            out += bytes(((v >> 11 & 31) << 3, (v >> 5 & 63) << 2, (v & 31) << 3))
    return w, h, bytes(out)


def _selftest() -> None:
    img = struct.pack("<HIHHH", 0xFB10, 12, 8, 2, 2)
    img += struct.pack("<HI", 0xFB20, 0x406) + bytes(range(256)) * 4
    img += struct.pack("<HII", 0xFB22, 10, 7)
    img += struct.pack("<HI", 0xFB30, 10) + b"\x00\x01\x02\x03"
    data = struct.pack("<HI", 0xFB00, 6 + len(img)) + img
    d = parse(data)
    assert (d["bpp"], d["width"], d["height"], d["unk_fb22"]) == (8, 2, 2, 7)
    assert to_rgb(d)[2][3:6] == bytes((4, 5, 6))
    for bad in (data[:-1], data + b"\x00", b"\x00\xfa" + data[2:]):
        try:
            parse(bad)
        except ParseError:
            continue
        raise AssertionError("accepted a bad file")
    vq = struct.pack("<HIHHH", 0xFB10, 12, 16, 2, 2)
    vq += struct.pack("<HI", 0xFB31, 6 + 0x800 + 1) + struct.pack("<4H", 1, 2, 3, 4) + bytes(0x7F8) + b"\x00"
    d = parse(struct.pack("<HI", 0xFB00, 6 + len(vq)) + vq)
    assert len(to_rgb(d)[2]) == 12
    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    elif "--png" in sys.argv:
        from PIL import Image
        i = sys.argv.index("--png")
        order = "bgr" if "--bgr" in sys.argv else "rgb"
        w, h, rgb = to_rgb(parse(Path(sys.argv[i + 1]).read_bytes()), order)
        Image.frombytes("RGB", (w, h), rgb).save(sys.argv[i + 2])
    else:
        raise SystemExit(main_for(parse, "**/*.DMF", ".DMF validator"))
