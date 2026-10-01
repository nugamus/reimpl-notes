# Scan all initialized memory for 4-byte little-endian pointer values given as args.
# Prints every address whose dword equals one of the targets (finds vtable slots / tables).
# @category Grumpa
from ghidra.program.model.address import AddressSet
args = getScriptArgs()
targets = set(int(a, 16) for a in args)
mem = currentProgram.getMemory()
for block in mem.getBlocks():
    if not block.isInitialized():
        continue
    start = block.getStart(); size = block.getSize()
    data = bytearray(size)
    mem.getBytes(start, data)
    for i in range(0, size - 3):
        v = data[i] | (data[i+1] << 8) | (data[i+2] << 16) | (data[i+3] << 24)
        if v in targets:
            print("0x%08x -> 0x%08x (block %s)" % (start.getOffset() + i, v, block.getName()))
