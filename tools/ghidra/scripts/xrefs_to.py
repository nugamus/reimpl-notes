# List callers of the given function addresses. @category Grumpa
args = getScriptArgs()
af = currentProgram.getAddressFactory()
fm = currentProgram.getFunctionManager()
refmgr = currentProgram.getReferenceManager()
for a in args:
    addr = af.getAddress(a)
    f = fm.getFunctionAt(addr)
    print("== callers of %s (%s) ==" % (a, f.getName() if f else "?"))
    seen = set()
    for ref in refmgr.getReferencesTo(addr):
        cf = fm.getFunctionContaining(ref.getFromAddress())
        if cf and cf.getEntryPoint().toString() not in seen:
            seen.add(cf.getEntryPoint().toString())
            print("   %s  %s" % (cf.getEntryPoint(), cf.getName()))
