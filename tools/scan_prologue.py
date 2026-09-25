#!/usr/bin/env python3
"""Scan backward from a target VA for the nearest standard function prologue."""
import struct
import sys

EXE = "Original Game Files/INSTALL/02_PR/MissionMonet.exe"
IMAGE_BASE = 0x400000
TEXT_VA = 0x1000  # both raw_offset and vaddr of .text

def va_to_file(va):
    return va - IMAGE_BASE

with open(EXE, "rb") as f:
    data = f.read()

target_va = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0x41d347
target_off = va_to_file(target_va)

print(f"Target VA=0x{target_va:08x} file_off=0x{target_off:08x}")

# Scan backwards up to 0x2000 bytes for various prologues
candidates = []
for off in range(target_off - 1, max(target_off - 0x2000, TEXT_VA), -1):
    if data[off] == 0x55 and data[off+1] == 0x8b and data[off+2] == 0xec:
        candidates.append(("push ebp; mov ebp, esp", off))
    if data[off] == 0x55 and data[off+1] == 0x8b and data[off+2] == 0xec and data[off+3] == 0x83:
        candidates.append(("push ebp; mov ebp, esp; sub esp, ?", off))
    if data[off] == 0x83 and data[off+1] == 0xec:  # sub esp, ?
        pass
    if data[off] == 0x64 and data[off+1] == 0xa1 and data[off+6] == 0x6a:  # mov eax, fs:[0]; push -1
        candidates.append(("SEH prologue (fs:[0]; push -1)", off))
    if data[off] == 0xa1 and data[off+5] == 0x64:  # mov eax, [global]; mov fs:[0],esp
        candidates.append(("mov eax, [global]; mov fs:[0], esp", off))
    # ret followed by padding
    if data[off] == 0xc3 and data[off+1] in (0xcc, 0x90):
        candidates.append(("ret+pad", off))

# Show top 20 most recent
for kind, off in candidates[:30]:
    va = off + IMAGE_BASE
    print(f"  VA=0x{va:08x} file=0x{off:08x}  {kind}")
print(f"...total candidates: {len(candidates)}")
