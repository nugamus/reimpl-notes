# Evidence log

Every factual claim made anywhere in `docs/` must have an entry here that names the thing
that proved it. Claims without evidence are bugs, not shortcuts.

Append only. Do not rewrite history; if a claim turns out to be wrong, add a new entry
that supersedes it and mark the old one `SUPERSEDED by E-nnnn`.

## Entry format

```
### E-0001 — <one-line claim>
- **Binary/file:** MissionMonet.exe | x3d.dll | Data/U01.X3D | traces/2026-08-30-intro.log
- **Evidence:** Ghidra address (`0x004ab120`), assert source path + line
  (`D:\MissionD\Source\XScene.cpp:412`), trace line number, or corpus statistic
  ("all 214 .O3D files have `4X3D` at offset 0").
- **Method:** how it was obtained (decompiled `FUN_004ab120`; ran
  `tools/parsers/o3d.py` over the corpus; proxy trace of the intro sequence).
- **Confidence:** proven | strong | tentative
```

An entry at `tentative` confidence must also have a matching line in
`docs/OPEN-QUESTIONS.md`.

## Entries

### E-0001 — Game binaries and engine DLLs ship in the installer payload, not preinstalled
- **Binary/file:** `Original Game Files/INSTALL/02_PR/`
- **Evidence:** directory listing contains `MissionMonet.exe`, `MissionD.exe`, `x3d.dll`,
  `h3d.dll`, `4xvideo.dll`, `AviPlay.dll`, `MSVCRTD.DLL`, plus previously unlisted
  `x3dmp5.dll`, `x3dmp6.dll`, `x3dmp6k.dll`, `x3dsdk.dll`, `xd3d.dll`, `xs3d.dll`,
  `flc.dll`, `SMACKW32.DLL`.
- **Method:** `find` over the extracted CD image at bootstrap.
- **Confidence:** proven

### E-0002 — `MSVCRTD.DLL` is redistributed alongside the game binaries
- **Binary/file:** `Original Game Files/INSTALL/02_PR/MSVCRTD.DLL`
- **Evidence:** file present in the shipping payload. Consistent with the CLAUDE.md ground
  truth that both EXEs are MSVC 6 debug builds — a release build would link `MSVCRT.DLL`.
- **Method:** directory listing.
- **Confidence:** strong

### E-0003 — "87 x3d.dll exports" is an import count; the DLL exports 278
- **Binary/file:** `INSTALL/02_PR/x3d.dll`, `h3d.dll`, and the other engine DLLs
- **Evidence:** PE export directories, read with `pefile`:
  `x3d.dll` 278 symbols, all prefixed `X3d_`; `h3d.dll` 52, all `H3d_`;
  `x3dsdk.dll` 63 `X3dsdk_`; `xd3d.dll` 29 and `xs3d.dll` 28, both exporting the same
  `X3d_*_Dll` names (`X3d_Add_Camera_Dll`, `X3d_Add_Face_Dll`, ...);
  `x3dmp5.dll` / `x3dmp6.dll` / `x3dmp6k.dll` 31 each, same names, all matrix and polar
  helpers (`X3d_Matrice_Inverse`, `X3d_Convert_To_Polar`);
  `4xvideo.dll` 1 (`Video4x_Init`); `AviPlay.dll` 5 named (`AviOpenFile`, `AviPlayMovie`,
  `AviSetWindow`, `AviGetStatus`, `AviClose`); `flc.dll` 1 (`Flc_Unpack`).
  `x3d-api-surface.md` says so in its own header — "x3d.dll (87 imported symbols)" — the
  87 is what the two EXEs import, not what the DLL exports.
- **Method:** `pefile.PE(...).DIRECTORY_ENTRY_EXPORT.symbols` over every DLL in
  `INSTALL/02_PR/`.
- **Confidence:** proven
- **Consequence:** the Phase 1 proxy `.def` needs all 278 `x3d.dll` names, not 87. A
  proxy that exports only what the EXEs import will fail to satisfy any other DLL that
  links against `x3d.dll`.

### E-0004 — `AviPlay.dll` exports by name, not by ordinal
- **Binary/file:** `INSTALL/02_PR/AviPlay.dll`
- **Evidence:** export table contains the five names listed in E-0003. CLAUDE.md
  previously described it as "ordinal-only".
- **Method:** same `pefile` sweep.
- **Confidence:** proven

### E-0005 — Both EXE build timestamps match the stated ground truth
- **Binary/file:** `MissionMonet.exe`, `MissionD.exe`
- **Evidence:** PE `FILE_HEADER.TimeDateStamp` = 2000-10-02 and 2000-10-09; sizes
  339,968 and 618,543 bytes; both `Machine = 0x14c` (x86-32).
- **Method:** `pefile` header read.
- **Confidence:** proven

### E-0006 — All 13 engine binaries import and auto-analyse cleanly in Ghidra 12.1.3
- **Binary/file:** `ghidra_projects/Monet.gpr`
- **Evidence:** headless run logged 13 × `REPORT: Analysis succeeded`, 0 errors, exit 0.
  Log at `logs/ghidra-import.log` (gitignored).
- **Method:** `analyzeHeadless ghidra_projects Monet -import <13 binaries>
  -analysisTimeoutPerFile 2400`, via the `C:\ghidra` junction (the stock `.bat` fails on
  the space in the repo path).
- **Confidence:** proven

### E-0007 — `MissionD.exe` has 2.07× the functions of `MissionMonet.exe`
- **Binary/file:** all 13 programs in `ghidra_projects/Monet.gpr`
- **Evidence:** Ghidra function counts after auto-analysis — `MissionD.exe` 3055,
  `MissionMonet.exe` 1476, `x3d.dll` 702, `xs3d.dll` 241, `x3dsdk.dll` 222, `xd3d.dll`
  181, `h3d.dll` 153, `AviPlay.dll` 111, `x3dmp5.dll` 74, `x3dmp6.dll` 74,
  `4xvideo.dll` 58, `x3dmp6k.dll` 42, `flc.dll` 19.
- **Method:** `get_function_count` over the Ghidra MCP bridge, one call per program with
  an explicit `program` selector.
- **Confidence:** proven
- **Consequence:** the developer build carries ~1579 functions the shipping build does
  not. Whether that is debug tooling, statically-linked CRT differences, or both is the
  subject of the `phase0-summary.md` diff.

### E-0008 — Corpus is 2,393 files / 343.3 M over 18 extensions; only `.X3D` shows two genuinely distinct container prefixes
- **Binary/file:** `Original Game Files/Data/`
- **Evidence:** `notes/corpus-inventory.md`. By total size: `.BMP` 381 files / 125.2 M,
  `.AVI` 8 / 77.8 M, `.WAV` 244 / 56.0 M, `.DMF` 518 / 48.4 M, `.A3D` 429 / 21.4 M,
  `.O3D` 596 / 14.0 M, then `.BIN` 109, `.S3D` 1, `.X3D` 24, `.FRA` 25, `.CFG` 38,
  `.3DS` 1, `.L3D` 5, `.MAT` 5, `.ARN` 1, `.TXT` 1, `.C3D` 6, `.VIT` 1.
  Single-magic extensions: `.AVI`, `.WAV`, `.A3D`, `.O3D`, `.S3D`, `.3DS`, `.L3D`,
  `.MAT`, `.ARN`, `.TXT`, `.C3D`, `.VIT`. Multi-prefix extensions inspected by hand:
  `.BMP` all `42 4d` (Q-0007), `.DMF` all `00 fb` (Q-0005), `.BIN`/`.FRA`/`.CFG` carry no
  signature (Q-0006), `.X3D` splits `;SCR` (21 files) vs `OBJE` (3) (Q-0004).
- **Method:** `python tools/inventory.py` over the user-confirmed data root, then a
  re-read of the per-extension magic tables it emitted.
- **Confidence:** proven for the counts; the "one container" readings of `.BMP` and
  `.DMF` are strong, not proven — no loader has been decompiled yet.
