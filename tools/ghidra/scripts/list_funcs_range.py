# List functions in an address range with size and callee count. @category Grumpa
args = getScriptArgs()
lo = currentProgram.getAddressFactory().getAddress(args[0])
hi = currentProgram.getAddressFactory().getAddress(args[1])
fm = currentProgram.getFunctionManager()
it = fm.getFunctions(lo, True)
while it.hasNext():
    f = it.next()
    if f.getEntryPoint().compareTo(hi) > 0:
        break
    body = f.getBody().getNumAddresses()
    callees = len(list(f.getCalledFunctions(None)))
    print("%s  %-28s  %5d B  %2d callees" % (f.getEntryPoint(), f.getName(), body, callees))
