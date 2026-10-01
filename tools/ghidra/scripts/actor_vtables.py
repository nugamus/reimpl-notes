# For each actor constructor address, read the vtable it installs and vtable[1] (Serialize).
# @category Grumpa
# args: pairs "type:ctorAddr" ...
args = getScriptArgs()
af = currentProgram.getAddressFactory()
mem = currentProgram.getMemory()
fm = currentProgram.getFunctionManager()
listing = currentProgram.getListing()

def u32(a):
    return mem.getInt(a) & 0xffffffff

for pair in args:
    t, ctor = pair.split(":")
    caddr = af.getAddress(ctor)
    # scan the ctor for "MOV dword ptr [reg], imm" where imm is a vtable in .rdata
    inst = listing.getInstructionAt(caddr)
    vtab = None
    n = 0
    while inst is not None and n < 60:
        s = inst.toString()
        if inst.getMnemonicString() == "MOV" and "dword ptr" in s:
            # look for an immediate operand that points into memory with a function at [imm]
            for i in range(inst.getNumOperands()):
                for obj in inst.getOpObjects(i):
                    try:
                        val = obj.getValue() if hasattr(obj, "getValue") else None
                    except:
                        val = None
                    if val and 0x490000 <= val < 0x4b0000:
                        # candidate vtable; serialize = *(val+4)
                        try:
                            ser = u32(af.getAddress(hex(val + 4)))
                            if 0x401000 <= ser < 0x490000:
                                vtab = val
                                print("type %s ctor %s vtable 0x%08x serialize 0x%08x" % (t, ctor, val, ser))
                                raise StopIteration
                        except StopIteration:
                            raise
                        except:
                            pass
        inst = inst.getNext(); n += 1
        if vtab:
            break
    if not vtab:
        print("type %s ctor %s vtable ?" % (t, ctor))
