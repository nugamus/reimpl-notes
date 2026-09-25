"""Find code/data references to a string literal in a PE, including indirect ones.

Ghidra's xref list only covers direct `PUSH imm32` / `MOV reg,[imm32]` operands.
Filenames handed to a loader through a pointer table never show up there. This
scans the whole image for the 4-byte little-endian VA of each target string,
reports which section each hit lands in, and then scans again for the VA of each
hit (one more indirection level) so a pointer-table entry can be traced back to
whatever references the table.

Usage: python tools/ptr_scan.py <pe> <needle> [needle ...]
"""

import struct
import sys

import pefile


def sections(pe):
    for s in pe.sections:
        name = s.Name.rstrip(b"\0").decode("latin-1")
        data = s.get_data()
        va = pe.OPTIONAL_HEADER.ImageBase + s.VirtualAddress
        yield name, va, data


def find_strings(pe, needle):
    """VAs of every occurrence of `needle` as an ASCII literal."""
    raw = needle.encode("latin-1")
    for name, va, data in sections(pe):
        start = 0
        while True:
            i = data.find(raw, start)
            if i < 0:
                break
            start = i + 1
            # only report a hit at a plausible literal start (preceded by NUL/pad)
            if i == 0 or data[i - 1] in (0, 0x20):
                yield name, va + i


def find_ptrs(pe, target_va):
    """VAs of every 4-byte little-endian slot holding `target_va`."""
    pat = struct.pack("<I", target_va)
    for name, va, data in sections(pe):
        start = 0
        while True:
            i = data.find(pat, start)
            if i < 0:
                break
            start = i + 1
            yield name, va + i


def main():
    path, needles = sys.argv[1], sys.argv[2:]
    pe = pefile.PE(path, fast_load=True)
    for needle in needles:
        print(f"\n=== {needle} ===")
        hits = list(find_strings(pe, needle))
        if not hits:
            print("  (string not found)")
            continue
        for sec, sva in hits:
            print(f"  string @ {sva:#010x} [{sec}]")
            lvl1 = list(find_ptrs(pe, sva))
            if not lvl1:
                print("    no 32-bit reference anywhere in the image")
            for psec, pva in lvl1:
                print(f"    ref @ {pva:#010x} [{psec}]")
                for qsec, qva in find_ptrs(pe, pva):
                    print(f"      ref-to-ref @ {qva:#010x} [{qsec}]")


if __name__ == "__main__":
    main()
