"""DelphiX collections: `.wxi` pictures, `.wxs`/`.dxw` waves (engine `gilbert`).

A file is one 16-bit Windows resource entry (RCDATA) whose body is a Delphi binary form
stream (`TPF0`) of a DelphiX TPictureCollectionComponent or TWaveCollectionComponent.
See engines/gilbert/docs/formats/README.md.

    python engines/gilbert/tools/parsers/wxi.py            # validate the whole corpus
    python engines/gilbert/tools/parsers/wxi.py FILE...    # dump items
    python engines/gilbert/tools/parsers/wxi.py --selftest
"""

from __future__ import annotations

import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
DATA = REPO / "games/gilbert/discs/cd/Program/Data"
EXTS = {".wxi", ".wxs", ".dxw"}

# Delphi TValueType
VA_NULL, VA_LIST, VA_INT8, VA_INT16, VA_INT32, VA_EXT, VA_STRING, VA_IDENT, VA_FALSE, VA_TRUE, \
    VA_BINARY, VA_SET, VA_LSTRING, VA_NIL, VA_COLLECTION = range(15)


class Reader:
    def __init__(self, data: bytes, pos: int = 0):
        self.d, self.p = data, pos

    def u8(self) -> int:
        v = self.d[self.p]
        self.p += 1
        return v

    def unpack(self, fmt: str):
        v = struct.unpack_from("<" + fmt, self.d, self.p)
        self.p += struct.calcsize("<" + fmt)
        return v[0] if len(v) == 1 else v

    def take(self, n: int) -> bytes:
        if self.p + n > len(self.d):
            raise ValueError(f"read of {n} past end at 0x{self.p:x}")
        v = self.d[self.p:self.p + n]
        self.p += n
        return v

    def sstr(self) -> str:
        return self.take(self.u8()).decode("latin1")


def read_value(r: Reader):
    t = r.u8()
    if t == VA_INT8:
        return r.unpack("b")
    if t == VA_INT16:
        return r.unpack("h")
    if t == VA_INT32:
        return r.unpack("i")
    if t in (VA_STRING, VA_IDENT):
        return r.sstr()
    if t == VA_LSTRING:
        return r.take(r.unpack("I")).decode("latin1")
    if t == VA_FALSE:
        return False
    if t == VA_TRUE:
        return True
    if t in (VA_NULL, VA_NIL):
        return None
    if t == VA_BINARY:
        return r.take(r.unpack("I"))
    if t == VA_SET:
        members = []
        while (m := r.sstr()) != "":
            members.append(m)
        return set(members)
    if t == VA_EXT:
        return r.take(10)
    if t == VA_LIST:
        items = []
        while r.d[r.p] != VA_NULL:
            items.append(read_value(r))
        r.u8()
        return items
    if t == VA_COLLECTION:
        items = []
        while (k := r.d[r.p]) != VA_NULL:
            if k != VA_LIST:
                raise ValueError(f"collection item order value 0x{k:02x} at 0x{r.p:x}")
            r.u8()
            items.append(read_props(r))
        r.u8()
        return items
    raise ValueError(f"value type {t} at 0x{r.p - 1:x}")


def read_props(r: Reader) -> dict:
    props = {}
    while (name := r.sstr()) != "":
        props[name] = read_value(r)
    return props


def parse(data: bytes) -> dict:
    """Resource header, then the TPF0 stream. Consumes every byte or raises."""
    r = Reader(data)
    if r.u8() != 0xFF or r.unpack("H") != 10:
        raise ValueError("not an RCDATA resource entry")
    res_name = bytearray()
    while (c := r.u8()) != 0:
        res_name.append(c)
    flags, size = r.unpack("HI")
    if r.p + size != len(data):
        raise ValueError(f"resource size {size} != {len(data) - r.p} bytes left")
    if r.take(4) != b"TPF0":
        raise ValueError("no TPF0 signature")
    cls, name = r.sstr(), r.sstr()
    props = read_props(r)
    if r.sstr() != "":  # children list terminator
        raise ValueError("unexpected child component")
    if r.p != len(data):
        raise ValueError(f"{len(data) - r.p} trailing bytes")
    return {"resource": res_name.decode("latin1"), "flags": flags, "class": cls, "name": name,
            "items": props.get("List", []), "props": props}


def parse_dib(blob: bytes) -> dict:
    """Picture.Data of class TDIB: BITMAPINFOHEADER, palette, pixels; nothing else."""
    r = Reader(blob)
    cls = r.sstr()
    if cls != "TDIB":
        raise ValueError(f"picture class {cls}")
    hsize, w, h, planes, bpp, comp, isize, _, _, used, _ = r.unpack("IiiHHIIiiII")
    if hsize != 40 or planes != 1:
        raise ValueError(f"header size {hsize} planes {planes}")
    ncol = (used or (1 << bpp)) if bpp <= 8 else 0
    r.take(4 * ncol)
    stride = (w * bpp + 31) // 32 * 4
    want = stride * abs(h) if comp == 0 else isize
    r.take(want)
    if r.p != len(blob):
        raise ValueError(f"DIB: {len(blob) - r.p} bytes left after pixels ({w}x{h}x{bpp} comp {comp})")
    return {"w": w, "h": h, "bpp": bpp, "comp": comp, "colors": ncol}


def parse_wave(blob: bytes) -> dict:
    """Wave.WAVE: RIFF header, a 16-byte `fmt ` chunk, a `data` chunk, then one byte
    (unk_tail, 0 in the corpus). The RIFF size field is len(blob) + 2, not len - 8."""
    riff, riff_size, wave, fmt, fmt_size = struct.unpack_from("<4sI4s4sI", blob)
    if riff != b"RIFF" or wave != b"WAVE" or fmt != b"fmt " or fmt_size != 16:
        raise ValueError("not RIFF WAVE with a 16-byte fmt chunk")
    tag, ch, rate, _, align, bits = struct.unpack_from("<HHIIHH", blob, 20)
    data, data_size = struct.unpack_from("<4sI", blob, 36)
    if data != b"data" or 44 + data_size + 1 != len(blob):
        raise ValueError("data chunk does not end one byte before the blob")
    if riff_size != len(blob) + 2:
        raise ValueError(f"RIFF size {riff_size} for a {len(blob)}-byte blob")
    return {"tag": tag, "channels": ch, "rate": rate, "bits": bits, "unk_tail": blob[-1]}


def check(path: Path, stats: Counter) -> None:
    f = parse(path.read_bytes())
    stats[f"class {f['class']}"] += 1
    for it in f["items"]:
        keys = tuple(it)
        stats[f"item keys {keys}"] += 1
        if "Picture.Data" in it:
            d = parse_dib(it["Picture.Data"])
            stats[f"dib {d['bpp']}bpp comp {d['comp']} colors {d['colors']}"] += 1
            stats["dib bottom-up" if d["h"] > 0 else "dib top-down"] += 1
            if it.get("PatternWidth", 0) and d["w"] % it["PatternWidth"]:
                stats["pattern width not dividing picture"] += 1
        if "Wave.WAVE" in it:
            w = parse_wave(it["Wave.WAVE"])
            stats[f"wave tag {w['tag']} {w['channels']}ch {w['rate']} Hz {w['bits']} bit, tail {w['unk_tail']}"] += 1


def validate() -> int:
    files = sorted(p for p in DATA.rglob("*") if p.suffix.lower() in EXTS)
    stats, bad = Counter(), 0
    for p in files:
        try:
            check(p, stats)
        except (ValueError, struct.error, IndexError) as e:
            bad += 1
            print(f"FAIL {p.relative_to(DATA)}: {e}")
    by_ext = Counter(p.suffix.lower() for p in files)
    print(f"{len(files) - bad}/{len(files)} parsed, every byte consumed ({dict(by_ext)})")
    for k, v in sorted(stats.items()):
        print(f"  {v:6}  {k}")
    return 1 if bad else 0


def dump(path: Path) -> None:
    f = parse(path.read_bytes())
    print(f"{path.name}: resource {f['resource']} class {f['class']}, {len(f['items'])} items")
    for it in f["items"]:
        info = {k: v for k, v in it.items() if not isinstance(v, bytes)}
        if "Picture.Data" in it:
            info["dib"] = parse_dib(it["Picture.Data"])
        if "Wave.WAVE" in it:
            info["wave"] = len(it["Wave.WAVE"])
        print("  ", info)


def selftest() -> None:
    dib = b"\x04TDIB" + struct.pack("<IiiHHIIiiII", 40, 2, 2, 1, 8, 0, 8, 0, 0, 1, 0) + b"\0" * 4 + b"\0" * 8
    item = (b"\x04Name\x06\x01a" + b"\x0cPicture.Data\x0a" + struct.pack("<I", len(dib)) + dib + b"\x00")
    body = b"TPF0\x1bTPictureCollectionComponent\x00\x04List\x0e\x01" + item + b"\x00\x00\x00"
    data = b"\xff\x0a\x00X\x00" + struct.pack("<HI", 0x1030, len(body)) + body
    f = parse(data)
    assert f["class"] == "TPictureCollectionComponent" and f["items"][0]["Name"] == "a"
    assert parse_dib(f["items"][0]["Picture.Data"]) == {"w": 2, "h": 2, "bpp": 8, "comp": 0, "colors": 1}
    try:
        parse(data + b"\0")
        raise AssertionError("trailing byte accepted")
    except ValueError:
        pass
    print("selftest ok")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--selftest"]:
        selftest()
    elif args:
        for a in args:
            dump(Path(a))
    else:
        sys.exit(validate())
