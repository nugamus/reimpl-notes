# List functions that reference defined strings containing any given substring.
# @category Grumpa
args = getScriptArgs()
needles = [a.lower() for a in args]
fm = currentProgram.getFunctionManager()
refmgr = currentProgram.getReferenceManager()
data_it = currentProgram.getListing().getDefinedData(True)
out = {}
for data in data_it:
    v = data.getValue()
    if v is None:
        continue
    s = str(v)
    low = s.lower()
    if not any(n in low for n in needles):
        continue
    for ref in refmgr.getReferencesTo(data.getAddress()):
        f = fm.getFunctionContaining(ref.getFromAddress())
        if f:
            out.setdefault(f.getEntryPoint().toString(), (f.getName(), set()))[1].add(s[:64])
for ep, (name, strs) in sorted(out.items()):
    print("FUNC %s  %s" % (ep, name))
    for s in sorted(strs):
        print("   | %s" % s)
