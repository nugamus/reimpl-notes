# Identifying what a game is made of

First hour of a new game, before any decompiling.

1. **Extract the disc** to `games/<game>/discs/<version>/`: 7-Zip for ISOs,
   `tools/disc/bin2iso.py` for raw `.bin` tracks, unshield
   (`third_party/unshield/build-mingw/src/unshield.exe`) for InstallShield `data1.hdr`/
   `.cab` sets (unpack by file group, as Grumpa's `cab/`). Keep the images untouched.
2. **Corpus triage**: `python tools/identify.py games/<game>/discs/<version>` gives one row
   per extension (count, size, TrID's guess, magic bytes, entropy, best reference). Save it
   as `engines/<engine>/notes/corpus-triage.md`. Standard formats (WAV, JPEG, AVI, MPEG,
   Smacker, Bink, QuickTime) are ScummVM's job, not ours; the rest is the format work.
3. **Executables**: `python tools/identify.py <exe>` runs Detect It Easy: compiler and
   linker (MSVC 6, Borland C++, Delphi), libraries (MFC, DirectX, VfW), packers and
   protection (SafeDisc, SecuROM, see protection.md), installers. That decides the Ghidra
   set-up (compiler spec, see naming-code.md).
4. **Entropy**: above ~7.5 bits/byte means compressed or encrypted (JPEG and MPEG are, by
   nature); a proprietary format at that level has a compression layer to find first.
5. **Search before guessing**: `python tools/ref.py "<extension or magic or name>"` over the
   format wikis, ScummVM's wiki and source, and our own specs (ScummVM's wiki lists which
   engine family a game belongs to, which saved Ring a survey).

Where we did it: Grumpa's survey (`engines/grumpa/tools/survey.py`, E-0001..E-0004),
Ring's editions (E-0002..E-0007), Gilbert's Delphi front end (E-0008).
