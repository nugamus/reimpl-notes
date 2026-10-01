# Print the u32 (little-endian) stored at each given address. @category Grumpa
args = getScriptArgs()
af = currentProgram.getAddressFactory()
mem = currentProgram.getMemory()
for a in args:
    addr = af.getAddress(a)
    v = mem.getInt(addr) & 0xffffffff
    print("%s -> 0x%08x" % (a, v))
