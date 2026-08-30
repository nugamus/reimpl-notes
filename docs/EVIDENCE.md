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

### E-0009 — Assert sites push the line number immediately before the `__FILE__` pointer
- **Binary/file:** `MissionMonet.exe`
- **Evidence:** three sites referencing `D:\MissionD\Source\XScene.cpp` (string at
  `0x00441788`): `0x0041a9c6` `PUSH 0x46` / `0x0041a9c8` `PUSH 0x441788` / `0x0041a9cd`
  `PUSH 0x3ed` / `CALL 0x0042a200`; likewise `0x0041ad64` (`PUSH 0x7c`, line 124) and
  `0x0041bcbc` (`PUSH 0x261`, line 609). All 166 assert sites across the two EXEs match
  this shape — `tools/ghidra_scripts/assert_namer.py` records a null line when it does
  not match, and produced none.
- **Method:** `get_assembly_context` over the string's xrefs, then the full scan.
- **Confidence:** proven

### E-0010 — 119 functions attributed to 31 distinct source files across the two EXEs
- **Binary/file:** `MissionMonet.exe`, `MissionD.exe`
- **Evidence:** `notes/function-map.csv`, `notes/module-map.md`. `MissionMonet.exe` 44 of
  1476 functions (3.0%), 20 source files, 20,001 bytes; `MissionD.exe` 75 of 3055 (2.5%),
  31 source files, 41,131 bytes. `notes/function-map-multi.csv` is empty: no function
  references more than one source path. The original tree had at least `Source\`,
  `Source\FrameWork Sources\`, `Source\Sound\` and `Source\Tools\`.
- **Method:** `tools/ghidra_scripts/assert_namer.py` run headless through
  `python -m pyghidra.ghidra_launch ... AnalyzeHeadless -process <binary> -noanalysis`.
  The stock `analyzeHeadless.bat` cannot run Python scripts — "Ghidra was not started
  with PyGhidra" — so the PyGhidra launcher is required for every script run.
- **Confidence:** proven for the attribution; the *absence* of a source file proves only
  that no assert names it, not that its code is absent.

### E-0011 — `x3d.dll`, `h3d.dll` and `x3dsdk.dll` contain no source-path strings
- **Binary/file:** `x3d.dll`, `h3d.dll`, `x3dsdk.dll`
- **Evidence:** the same scan reports `0 source-path strings, 0 single-file functions,
  0 multi-file functions` for all three. Consistent with release builds from a different
  vendor (4X Technologies).
- **Method:** `assert_namer.py`, identical invocation.
- **Confidence:** proven
- **Consequence:** assert-based attribution yields nothing for the 1,077 functions in
  those three DLLs. Their semantics must come from export names, Phase 1 traces and
  decompilation.

### E-0012 — The developer build is a strict superset; the shipping build has nothing unique
- **Binary/file:** `MissionD.exe` vs `MissionMonet.exe`
- **Evidence:** three independent diffs, none showing a shipping-only item.
  *Source paths:* 22 shared, 9 only in `MissionD.exe` (`Tools\CaptureWnd.cpp`, `U99.cpp`,
  `LKeyState.cpp`, `LMouseState.cpp`, `Sound\XSndStream.cpp`, `Sound\XTimer.cpp`,
  `Sound\XWaveFile.cpp`, `LArray.cpp`, `XAction.cpp`), 0 only in `MissionMonet.exe`.
  *Imports:* 67 symbols only in `MissionD.exe`, including three DLLs the shipping build
  does not link — `dinput.dll` (`DirectInputCreateA`), `comdlg32.dll`
  (`GetOpenFileNameA`, `GetSaveFileNameA`) and `ole32.dll` — plus `gdi32.dll` `BitBlt` /
  `CreateCompatibleBitmap` / `GetDIBits` and `kernel32.dll` `GetLogicalDriveStringsA`.
  0 imports only in `MissionMonet.exe`. *Strings:* 1,002 only in `MissionD.exe`
  (`Begin capture`, `Stop capture`, `D:/Capture/`, `*********SET_CRT_DEBUG_FIELD*`,
  `D:\MissionD\Debug\MissionD.pdb`), 363 only in `MissionMonet.exe`.
  Anchors: `LKeyState.cpp` at `0x00458911` line 41, `LMouseState.cpp` at `0x0045bde8`
  line 52, `CaptureWnd.cpp` at `0x00428d11` line 132 and `0x00428f03` line 183.
- **Method:** set diffs over `notes/_assert_scan/*.json`, `pefile`
  `DIRECTORY_ENTRY_IMPORT`, and a `[\x20-\x7e]{5,}` string sweep of both PEs.
- **Confidence:** proven for the import and string diffs; the source-path diff is strong
  only as positive evidence — `XAction.cpp` is surely present in both builds.

### E-0013 — `MessageToUser` shipped enabled; only the CRT debug layer was compiled out
- **Binary/file:** `MissionMonet.exe`, `MissionD.exe`
- **Evidence:** the `MessageToUser` sink at `0x0042a200` in `MissionMonet.exe` is reached
  from 5 attributed functions totalling 3,073 bytes, and all 22 source-path strings in
  the shipping build have at least one reference (zero orphans). Conversely
  `msvcrtd.dll!_CrtSetDbgFlag` and `msvcrtd.dll!_CrtDbgReport` are imported by
  `MissionD.exe` only, though both builds link `MSVCRTD.DLL` (E-0002).
- **Method:** xref counts from the `assert_namer.py` scan; `pefile` import diff.
- **Confidence:** proven

### E-0014 — The two EXEs import 80 distinct `x3d.dll` exports, not 87
- **Binary/file:** `MissionMonet.exe`, `MissionD.exe`, `x3d.dll`, `h3d.dll`
- **Evidence:** `notes/import-map.md`. `MissionMonet.exe` imports 70 `x3d.dll` symbols,
  `MissionD.exe` 80; the union is 80 and the intersection 70, so the shipping build's set
  is a subset. Both import 7 from `h3d.dll`, 5 from `AviPlay.dll`, 1 from `4xvideo.dll`.
  The 87 of E-0003 is `MissionD.exe`'s 80 `x3d.dll` plus 7 `h3d.dll` imports. The ten
  developer-only `x3d.dll` imports are all lighting, camera and animation enumeration:
  `X3d_Scene_Create_Light`, `X3d_Scene_Create_Spot_Light`, `X3d_Light_Set_Color`,
  `X3d_Light_Set_Multiplier`, `X3d_Light_Set_Name`, `X3d_Light_Include_Scene_All_Object`,
  `X3d_Camera_Release`, `X3d_Camera_Set_Target`, `X3d_Scene_Find_First_Animation`,
  `X3d_Scene_Find_Next_Animation`.
- **Method:** `tools/ghidra_scripts/import_map.py`, which walks each external function's
  entry and thunk addresses and takes the containing function of every reference, then
  joins those addresses against `notes/function-map.csv`.
- **Confidence:** proven
- **Consequence:** does not change E-0003's conclusion. The Phase 1 proxy `.def` still
  needs all 278 `x3d.dll` exports.
