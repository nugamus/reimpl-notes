# Print ASCII at each given address (for extension strings). @category Grumpa
args = getScriptArgs()
from ghidra.program.model.address import AddressSet
af = currentProgram.getAddressFactory()
mem = currentProgram.getMemory()
for a in args:
    addr = af.getAddress(a)
    bs = bytearray()
    for i in range(8):
        b = mem.getByte(addr.add(i)) & 0xff
        if b == 0: break
        bs.append(b)
    print("%s  %r" % (a, bytes(bs)))
