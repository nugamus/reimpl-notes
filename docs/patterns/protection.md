# Copy protection and packed executables

Signs: Detect It Easy names a protector; sections with entropy near 8; `.text` that
disassembles to garbage; strings missing from `.rdata`; extra sections (`stxt774`,
`.cms_t`/`.cms_d`); an import table of a few stubs.

- **A decrypted executable may already exist.** A community no-CD build of the game's EXE
  usually has the protection removed and every import resolved, which beats any dump of
  our own: Grumpa's Ghidra work moved to `GRUMPA_NOCD.EXE` for that reason (Q-0002/Q-0003
  history in its OPEN-QUESTIONS.md). Use it locally as Ghidra input and in run folders;
  never commit it or anything from it.
- **SafeDisc (1.x, 2.x)**, when no such build exists: run the game once through SafeDiscLoader2
  (`third_party/SafeDiscLoader2`, built with MSBuild; it emulates `secdrv.sys`, so it works
  on modern Windows) in a run folder, and dump the decrypted image when it reaches its
  entry point. Grumpa's `engines/grumpa/tools/sddump.py` does this: it rebuilds the import
  table; the SafeDisc stub slots stay unnamed and are named from their use. Import the
  dump into Ghidra, not the disc EXE.
- **Disc checks** without encryption: patch a *copy* in a run folder, through a script
  that byte-checks every patch (rule 5).
- **Unknown layers** (Prophet's `.cms_t`/`.cms_d`): identify the protector with DIE and
  `tools/ref.py <section names>`, then dump at the original entry point after the layer
  ran (trace.py or the MCP debugger: break on the first call into the game's own code).
- **The disc signature** (bad-EDC sectors and the like) survives only in a raw `.bin`, not
  in an ISO; `tools/disc/edcscan.c` reads it. Keep the original image.

Dumps are the original's code: they stay in `build/` (gitignored), never published.
