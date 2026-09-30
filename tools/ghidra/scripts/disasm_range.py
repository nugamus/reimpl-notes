# Disassemble an address range (or a function by entry). @category Grumpa
# args: <start> [end]   ; if no end, disassemble the containing function.
args = getScriptArgs()
af = currentProgram.getAddressFactory()
listing = currentProgram.getListing()
fm = currentProgram.getFunctionManager()
start = af.getAddress(args[0])
if len(args) > 1:
    end = af.getAddress(args[1])
else:
    f = fm.getFunctionContaining(start)
    end = f.getBody().getMaxAddress()
inst = listing.getInstructionAt(start)
while inst is not None and inst.getAddress().compareTo(end) <= 0:
    a = inst.getAddress()
    # show any label at this address
    sym = currentProgram.getSymbolTable().getPrimarySymbol(a)
    if sym and sym.getSource().toString() != "DEFAULT":
        print("%s:" % sym.getName())
    print("  %s  %s" % (a, inst.toString()))
    inst = inst.getNext()
