# For each "type:ctorAddr", create the function if needed, find the vtable it installs
# (MOV [reg], imm where imm in .rdata and *(imm+4) is code), report vtable[1] = Serialize.
# Follows up to 2 called sub-ctors (base classes set the vtable first). @category Grumpa
from ghidra.program.model.symbol import SourceType
args = getScriptArgs()
af = currentProgram.getAddressFactory(); mem = currentProgram.getMemory()
fm = currentProgram.getFunctionManager(); listing = currentProgram.getListing()

def u32(v):
    return mem.getInt(af.getAddress(hex(v))) & 0xffffffff

def ensure(addr):
    f = fm.getFunctionAt(addr)
    if not f:
        try:
            createFunction(addr, None)
        except:
            pass

def find_vtable(addr, depth=0):
    # The derived class installs its own vtable LAST in its ctor; take the last valid one.
    ensure(addr)
    inst = listing.getInstructionAt(addr)
    n = 0; last = None
    while inst is not None and n < 300:
        m = inst.getMnemonicString()
        if m == "RET":
            break
        if m == "MOV" and "dword ptr" in inst.toString() and inst.getNumOperands() >= 2:
            for obj in inst.getOpObjects(1):
                try:
                    val = obj.getValue()
                except:
                    val = None
                if val and 0x490000 <= val < 0x4b0000:
                    try:
                        ser = u32(val + 4)
                        if 0x401000 <= ser < 0x490000:
                            last = (val, ser)
                    except:
                        pass
        inst = inst.getNext(); n += 1
    return last

for pair in args:
    t, c = pair.split(":")
    r = find_vtable(af.getAddress(c))
    if r:
        print("type %s ctor %s vtable 0x%08x serialize 0x%08x" % (t, c, r[0], r[1]))
    else:
        print("type %s ctor %s ?" % (t, c))
