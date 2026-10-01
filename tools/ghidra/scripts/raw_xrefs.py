# Print raw references to each address arg (from-address + type), no function filter.
# @category Grumpa
args = getScriptArgs()
af = currentProgram.getAddressFactory()
rm = currentProgram.getReferenceManager()
fm = currentProgram.getFunctionManager()
for a in args:
    addr = af.getAddress(a)
    print("== refs to %s ==" % a)
    n = 0
    for ref in rm.getReferencesTo(addr):
        fa = ref.getFromAddress()
        f = fm.getFunctionContaining(fa)
        print("   from %s  type=%s  in=%s" % (fa, ref.getReferenceType(), f.getName() if f else "<none>"))
        n += 1
    if n == 0:
        print("   (none)")
