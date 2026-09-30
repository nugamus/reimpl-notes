"""Name Gilbert.exe's Delphi methods from the class VMTs (published methods and virtuals).

Delphi 4/5 VMT, offsets from the VMT pointer: -76 self pointer, -52 published method
table, -44 class name, -40 instance size, -36 parent (pointer to the parent's VMT
pointer), -32..-4 the eight TObject virtuals, 0.. the class's own virtuals. A published
method table is u16 count, then per method: u16 entry size, u32 code address, name.

Writes engines/gilbert/notes/names/GILBERT.EXE-vmt.csv (address,name,evidence) for
tools/ghidra/scripts/apply_names.py, and notes/delphi-classes.md (class tree).

    python engines/gilbert/tools/delphi_vmt.py
    python engines/gilbert/tools/delphi_vmt.py --selftest
"""

from __future__ import annotations

import csv
import struct
import sys
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[3]
EXE = REPO / "games/gilbert/discs/cd/Program/Gilbert.exe"
NOTES = REPO / "engines/gilbert/notes"
TOBJECT_VIRTUALS = ["SafeCallException", "AfterConstruction", "BeforeDestruction", "Dispatch",
                    "DefaultHandler", "NewInstance", "FreeInstance", "Destroy"]


class Image:
    def __init__(self, blob: bytes, base: int, sections: list[tuple[int, int, int]]):
        self.blob, self.base, self.sections = blob, base, sections  # (va, size, file offset)

    def off(self, va: int) -> int | None:
        for s_va, size, raw in self.sections:
            if s_va <= va < s_va + size:
                return raw + va - s_va
        return None

    def u32(self, va: int) -> int | None:
        o = self.off(va)
        return None if o is None or o + 4 > len(self.blob) else struct.unpack_from("<I", self.blob, o)[0]

    def sstr(self, va: int) -> str | None:
        o = self.off(va)
        if o is None:
            return None
        n = self.blob[o]
        s = self.blob[o + 1:o + 1 + n]
        return s.decode("latin1") if n and all(32 < c < 127 for c in s) else None

    def is_code(self, va: int) -> bool:
        return va is not None and self.off(va) is not None and va < self.code_end


def find_vmts(img: Image) -> dict[int, dict]:
    vmts = {}
    for s_va, size, raw in img.sections:
        for va in range(s_va + 76, s_va + size - 4, 4):
            if img.u32(va - 76) != va:
                continue
            name = img.sstr(img.u32(va - 44) or 0)
            if name is None:
                continue
            parent_pp = img.u32(va - 36)
            parent = img.u32(parent_pp) if parent_pp else None
            vmts[va] = {"name": name, "parent": parent, "methods": img.u32(va - 52),
                        "size": img.u32(va - 40)}
    return vmts


def published(img: Image, table: int) -> list[tuple[int, str]]:
    if not table:
        return []
    o = img.off(table)
    count = struct.unpack_from("<H", img.blob, o)[0]
    out, p = [], o + 2
    for _ in range(count):
        size, addr = struct.unpack_from("<HI", img.blob, p)
        n = img.blob[p + 6]
        out.append((addr, img.blob[p + 7:p + 7 + n].decode("latin1")))
        p += size
    return out


def virtuals(img: Image, vmt: int, vmts: dict[int, dict]) -> list[tuple[int, int]]:
    """(slot, address) of the class's own virtual slots, up to the next VMT or a non-code word."""
    ends = [v - 76 for v in vmts if v > vmt]
    limit = min(ends) if ends else vmt + 4 * 256
    out, slot = [], 0
    while vmt + 4 * slot < limit:
        a = img.u32(vmt + 4 * slot)
        if not img.is_code(a):
            break
        out.append((slot, a))
        slot += 1
    return out


def load() -> Image:
    pe = pefile.PE(str(EXE))
    base = pe.OPTIONAL_HEADER.ImageBase
    secs = [(base + s.VirtualAddress, max(s.Misc_VirtualSize, s.SizeOfRawData), s.PointerToRawData)
            for s in pe.sections if s.SizeOfRawData]
    img = Image(EXE.read_bytes(), base, secs)
    code = pe.sections[0]
    img.code_end = base + code.VirtualAddress + code.Misc_VirtualSize
    return img


def main() -> None:
    img = load()
    vmts = find_vmts(img)
    names: dict[int, tuple[str, str]] = {}
    for va, v in sorted(vmts.items()):
        for addr, m in published(img, v["methods"]):
            names.setdefault(addr, (f"{v['name']}::{m}", f"published method of {v['name']} (VMT 0x{va:x})"))
    # Virtuals: name a slot after the first (root-most) class that introduces its address.
    for va, v in sorted(vmts.items()):
        for i, (slot_off, name) in enumerate(zip(range(-32, 0, 4), TOBJECT_VIRTUALS)):
            a = img.u32(va + slot_off)
            parent = v["parent"]
            if parent and img.u32(parent + slot_off) == a:
                continue  # inherited
            names.setdefault(a, (f"{v['name']}::{name}", f"TObject virtual slot {slot_off} of {v['name']}"))
        for slot, a in virtuals(img, va, vmts):
            parent = v["parent"]
            if parent and parent in vmts and img.u32(parent + 4 * slot) == a:
                continue
            names.setdefault(a, (f"{v['name']}::virtual_{slot * 4:03x}",
                                 f"virtual slot +0x{slot * 4:x} of {v['name']} (VMT 0x{va:x})"))
    (NOTES / "names").mkdir(parents=True, exist_ok=True)
    with (NOTES / "names/GILBERT.EXE-vmt.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["address", "name", "evidence"])
        for a, (n, ev) in sorted(names.items()):
            w.writerow([f"{a:08x}", n, ev])
    lines = ["# Gilbert.exe: Delphi classes (from the VMTs)", "",
             "Generated by `engines/gilbert/tools/delphi_vmt.py`. Class, VMT, instance size, parent.", ""]
    for va, v in sorted(vmts.items(), key=lambda kv: kv[1]["name"].lower()):
        par = vmts.get(v["parent"], {}).get("name", "-")
        pub = published(img, v["methods"])
        lines.append(f"- `{v['name']}` VMT 0x{va:x}, {v['size']} B, parent `{par}`"
                     + (f"; published: {', '.join(m for _, m in pub)}" if pub else ""))
    (NOTES / "delphi-classes.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(vmts)} classes, {len(names)} names")


def selftest() -> None:
    # One fake VMT at 0x1000+76 in a single section; class name at 0x1100.
    blob = bytearray(0x200)
    vmt = 0x1000 + 76
    struct.pack_into("<I", blob, 0, vmt)
    struct.pack_into("<I", blob, 76 - 44, 0x1100)
    struct.pack_into("<I", blob, 76 - 52, 0x1120)
    blob[0x100:0x106] = b"\x05TTest"
    struct.pack_into("<HHI", blob, 0x120, 1, 11, 0x1180)
    blob[0x128:0x12d] = b"\x04Go!!"
    img = Image(bytes(blob), 0, [(0x1000, 0x200, 0)])
    img.code_end = 0x1200
    v = find_vmts(img)
    assert list(v) == [vmt] and v[vmt]["name"] == "TTest"
    assert published(img, 0x1120) == [(0x1180, "Go!!")]
    print("selftest ok")


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
