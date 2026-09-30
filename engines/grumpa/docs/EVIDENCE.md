# Evidence log (Grumpa engine)

Every factual claim in `engines/grumpa/docs/` and `games/grumpa/docs/` must have an entry
here that names the thing that proved it. Claims without evidence are bugs, not shortcuts.

Append only. Do not rewrite history; if a claim turns out to be wrong, add a new entry
that supersedes it and mark the old one `SUPERSEDED by E-nnnn`.

Ranges: survey, disc and protection E-0001..; later areas take the next free hundred.

## Entry format

```
### E-0001 — <one-line claim>
- **Binary/file:** games/grumpa/discs/cab/Profileshell/Grumpa.exe | .../Scenes/Scene_001.scn
- **Evidence:** Ghidra address, trace line, or corpus statistic.
- **Method:** how it was obtained.
- **Confidence:** proven | strong | tentative
```

An entry at `tentative` confidence must also have a matching line in `OPEN-QUESTIONS.md`.

## Entries

### E-0001 — The corpus: one CD image; 32 files on the ISO, 6,111 in its InstallShield cabinet
- **Binary/file:** `games/grumpa/images/Grumpa.bin` (788,891,376 B, MD5 `d71ad24b…`) with
  `Grumpa.cue` (one track, `MODE1/2352`); converted to `Grumpa.iso` (335,413 sectors,
  MD5 `2130011020…`), volume `Grumpa`, created 2002-03-12 09:16:48
- **Evidence:** `engines/grumpa/notes/corpus-inventory.md`: `games/grumpa/discs/cd` 32
  files, 340,577,965 B (9 in `DIRECTX8/`); `games/grumpa/discs/cab` 6,111 files,
  439,633,841 B in 78 file groups (56 files are the MFC runtime and InstallShield's own
  engine and support files). Game data by file group: `Bitmaps` 2,262, `Meshes` 1,638,
  `Scenes` 221, `Actors` 4, `UI` 125, `Sounds_` 550 plus `Sounds_<Language>` 241..280,
  `Local_<Language>` 4 each, `Shell_<Language>` 33 each, `Movies_<Language>` 1 each (the
  Swedish films are the ISO's `Movies/`), `Save` 20, `Profileshell` 36 (the programs).
  Every file's MD5 in `engines/grumpa/notes/corpus-md5.tsv`.
- **Method:** `python tools/disc/bin2iso.py`; 7-Zip extraction of the ISO; unshield 1.6.2
  (`third_party/unshield`, built statically with MSYS2 gcc into `build-mingw/`):
  `unshield -d games/grumpa/discs/cab x games/grumpa/discs/cd/data1.hdr` (6,111 files, no
  errors; log `logs/grumpa-unshield.log`); `python engines/grumpa/tools/survey.py`.
- **Confidence:** proven

### E-0002 — Idol FX's "Grumpa", a Nordic edition (Danish, Finnish, Norwegian, Swedish), published by Vision Park
- **Binary/file:** `cd/Setup.ini`, `cd/fxroute.ini`, `cd/Autorun.inf`,
  `cab/Local_Swedish/Credits.txt`, `cab/Profileshell/shellmedia/grumpa.shl`
- **Evidence:** `Setup.ini`: `AppName=Grumpa`, `[Languages] Default=0x001d count=4 key0=0x0006
  key1=0x000b key2=0x0014 key3=0x001d` (Windows primary language IDs: Danish, Finnish,
  Norwegian, Swedish; Swedish the default). `fxroute.ini`: `company = "Idol FX"`,
  `product = "Grumpa"`, `first = "setup.exe"`, `second = "FXProfileShell.exe"`.
  `Autorun.inf` opens `FXRoute.exe`. The credits (Swedish) list programmers Anders
  Åkerfeldt, Andreas Thorsén, Martin Eklund, a "FXSTRUCTOR" credit (Jörgen Strömbro) and a
  producer at Vision Park. `grumpa.shl` plays `vpark.avi` and `idolfx.avi`. Each language
  has its own `Local_*` texts, `Sounds_*` voices, `Shell_*` launcher files and intro film.
- **Method:** reading the files.
- **Confidence:** proven

### E-0003 — `Grumpa.exe` is an MSVC 6 program wrapped in SafeDisc 2.60.052: its code and data are encrypted on disc
- **Binary/file:** `cab/Profileshell/Grumpa.exe` (2,095,817 B, MD5 `4ff56a31…`, PE timestamp
  2002-01-28 10:09:13 UTC)
- **Evidence:** `engines/grumpa/notes/binaries.md`: linker 6.0, Rich header of Visual
  C++ 6 tools; imports only KERNEL32, USER32, GDI32, ADVAPI32, ole32, DDRAW, DSOUND, WINMM;
  sections `.text` (entropy 7.99) `.rdata` (4.46) `.data` (7.68) `.rsrc` `stxt774`
  `stxt371`; SafeDisc's marker `BoG_ *90.0&!!  Yy>` at file offset 0xfd4 followed by the
  version 2, 60, 52. `.text` and `.data` are ciphertext, and `.rdata` holds no readable
  strings either (no file names, no messages), so nothing of the game can be read
  statically. The disc carries SafeDisc's companions: `drvmgt.dll`, `secdrv.sys`,
  `00000001.TMP` (2,048 B), `00000000.016`/`.256` (800×600 splash bitmaps, 4 and 8 bit).
  The other programs are plain MSVC 6 (linker 6.0): `FXRoute.exe` (autorun menu),
  `FXProfileShell.exe` (the launcher, MFC), `GrumpaConfig.exe` (settings, MFC).
- **Method:** `python engines/grumpa/tools/survey.py`; a printable-string scan of
  `Grumpa.exe`.
- **Confidence:** proven

### E-0004 — The image keeps SafeDisc's signature: 598 sectors with bad EDC between two files
- **Binary/file:** `games/grumpa/images/Grumpa.bin`
- **Evidence:** `build/edcscan.exe games/grumpa/images/Grumpa.bin` → `sectors 335413 mode2 0
  bad-edc 598 runs 537 first 10761 last 20290`. The ISO directory places `00000001.TMP` at
  LBA 10314 and `SECDRV.SYS` at 20315..20329: the bad sectors lie in the unallocated gap
  between them (no file covers LBA 10315..20314). A plain `.iso` drops the EDC, so only
  the `.bin` can reproduce the disc check.
- **Method:** `tools/disc/edcscan.c` (EDC = CRC-32, reflected polynomial 0xD8018001, over
  bytes 0..0x80F of each mode-1 sector); ISO 9660 directory walk of `Grumpa.iso`.
- **Confidence:** proven
