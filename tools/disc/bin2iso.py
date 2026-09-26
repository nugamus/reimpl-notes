"""Raw CD image (.bin, 2352-byte sectors, MODE1 or MODE2 form 1) to a plain .iso.

    python tools/disc/bin2iso.py image.bin out.iso
    python tools/disc/bin2iso.py --selftest

Each raw sector is 12 sync bytes, a 4-byte header (minutes, seconds, frames, mode), then
the user data: 2048 bytes at offset 16 in mode 1, or 8 subheader bytes and 2048 bytes at
offset 24 in mode 2 form 1. Only the user data goes into the .iso, which 7-Zip or any OS
can then open.
"""
import sys

SYNC = b"\x00" + b"\xff" * 10 + b"\x00"


def convert(src, dst):
    sectors = 0
    with open(src, "rb") as f, open(dst, "wb") as out:
        while True:
            s = f.read(2352)
            if len(s) < 2352:
                break
            if s[:12] != SYNC:
                raise ValueError(f"sector {sectors}: no sync pattern (not a raw data track?)")
            out.write(s[16:2064] if s[15] == 1 else s[24:2072])
            sectors += 1
    return sectors


def _selftest():
    import os, tempfile
    d = tempfile.mkdtemp()
    raw = bytearray()
    for mode, fill in ((1, 0x41), (2, 0x42)):
        sec = bytearray(SYNC + bytes([0, 2, 0, mode]))
        if mode == 2:
            sec += b"\x00" * 8
        sec += bytes([fill]) * 2048
        sec += b"\x00" * (2352 - len(sec))
        raw += sec
    src, dst = os.path.join(d, "a.bin"), os.path.join(d, "a.iso")
    open(src, "wb").write(raw)
    assert convert(src, dst) == 2
    data = open(dst, "rb").read()
    assert data == b"A" * 2048 + b"B" * 2048, "user data"
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        _selftest()
    else:
        print(convert(sys.argv[1], sys.argv[2]), "sectors")
