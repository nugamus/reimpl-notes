"""List all functions near a target address; useful to find what got created."""
from __future__ import annotations

import sys

try:
    currentProgram  # noqa: F821
except NameError:
    print(__doc__)
    sys.exit(2)

addr_factory = currentProgram.getAddressFactory()
fn_mgr = currentProgram.getFunctionManager()
target_str = sys.argv[1] if len(sys.argv) > 1 else "0x41d340"
target = int(target_str, 16)

for f in fn_mgr.getFunctions(True):
    entry = int(str(f.getEntryPoint()), 16)
    if abs(entry - target) < 0x300:
        end = int(str(f.getBody().getMaxAddress()), 16)
        print(f"{f.getName()} entry=0x{entry:08x} end=0x{end:08x} size={f.getBody().getNumAddresses()}")
