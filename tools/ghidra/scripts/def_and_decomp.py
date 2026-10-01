# Create a function at each address if missing, then decompile to notes dir. @category Grumpa
from ghidra.app.decompiler import DecompInterface
args = getScriptArgs()
outdir = args[0]
di = DecompInterface(); di.openProgram(currentProgram)
fm = currentProgram.getFunctionManager()
import os
for a in args[1:]:
    addr = currentProgram.getAddressFactory().getAddress(a)
    f = fm.getFunctionAt(addr)
    if not f:
        createFunction(addr, None); f = fm.getFunctionAt(addr)
    if not f:
        print("could not create function at", a); continue
    res = di.decompileFunction(f, 60, None)
    if res and res.decompileCompleted():
        txt = res.getDecompiledFunction().getC()
        p = os.path.join(outdir, "GRUMPA.EXE__%s.c" % f.getName())
        open(p, "w").write(txt)
        print("wrote", p, len(txt), "bytes; callees:", [c.getName() for c in f.getCalledFunctions(None)][:12])
    else:
        print("decompile failed for", a)
