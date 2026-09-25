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
  subject of the Phase 0 diff (git history: notes/phase0-summary.md).

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

### E-0015 — The tracing proxy is transparent across calling conventions
- **Binary/file:** `tools/proxy/generated/x3d_proxy.c`, `build/proxy/Release/x3d.dll`
- **Evidence:** the built proxies export 278 (`x3d.dll`) and 52 (`h3d.dll`) symbols whose
  name-and-ordinal sets are identical to the originals', `Machine = 0x14c`.
  `proxy_selftest.exe` calls through the real proxy into a stand-in DLL and passes 8 of 8
  checks: `__cdecl` with 4 arguments, `__stdcall` with 4 and with 8 arguments, a `double`
  argument returned in ST(0), the caller's stack frame intact after `__stdcall` cleanup,
  one trace line per call, and each call logged under its own export name.
- **Method:** `pefile` export comparison; `cmake --build build/proxy --config Release`
  then `build/proxy/Release/proxy_selftest.exe` (exit 0).
- **Confidence:** proven for the four exercised shapes. Not proven for `__fastcall` or
  for callees that read undefined registers on entry; no engine export has been observed
  to do either, because no trace exists yet.

### E-0016 — All 596 `.O3D` files share a 36-byte fixed header
- **Binary/file:** `Original Game Files/Data/**/*.O3D`
- **Evidence:** every file begins with the 27-byte `(c) 1998 4X Tech. 0.95 (O)\0`. Bytes
  27, 29, 30 and 31 are constant across all 596 (`0x78`, `0xa1`, `0x63`, `0x00`); byte 28
  takes 41 distinct values, all within `0xb7`-`0xc6`. The little-endian u32 at offset 32
  ranges 0-87, and is 0 in 171 files. 1,476 NUL-terminated strings recovered from the
  body end in `.TGA` and none in any other extension, although the corpus holds no `.TGA`
  file (E-0008).
- **Method:** `pathlib.Path.rglob` over the corpus with `struct.unpack_from`; counts in
  `docs/formats/README.md`.
- **Confidence:** proven for the header; the body layout is **not** established — two
  fixed-stride hypotheses (112-byte materials, 192-byte objects) passed a length check
  and were then refuted by a field-level check, 541 and 18,259 failures respectively.
- **Superseded in part by E-0018:** the body layout is now established, and the reason
  the fixed strides failed is that `.O3D` has no fixed-offset records at all. The header
  facts stand, but "byte 28 varies over 41 values" is explained by E-0018, not meaningful.

### E-0017 — `.O3D` is a sequential stream, not a record array
- **Binary/file:** `x3d.dll`
- **Evidence:** `X3d_Load_Sdk_o3d` at `0x10001302` reads a 32-byte signature, `strcmp`s it
  against `(c) 1998 4X Tech. 0.95 (O)` and `(c) 1998 4X Tech. 1.00 (O)`, sets the global
  `DAT_1002d224` to 0 or 1, then calls `FUN_10011450` (materials) and `FUN_10012920`
  (objects), the latter calling `FUN_10011ea0` per object. Every read goes through one of
  four cursor primitives, each of which advances a shared offset:
  `FUN_1000ba90` (u32, +4), `FUN_1000baf0` (u8, +1), `FUN_1000bb20` (f32, +4),
  `FUN_1000bb50` (n bytes, +n). Decompiler output in `notes/decomp/`.
- **Method:** `tools/ghidra_scripts/decompile_one.py`, one function at a time.
- **Confidence:** proven
- **Consequence:** the signature field is 32 bytes, not the 27 of E-0016; bytes 27-31 lie
  *inside* it, past the NUL, and are uninitialised writer memory. That is why byte 28
  takes 41 values and why every fixed-stride reading of the body failed.

### E-0018 — The `.O3D` spec parses 100% of the corpus, consuming every byte
- **Binary/file:** `Original Game Files/Data/**/*.O3D`, `docs/formats/o3d.ksy`
- **Evidence:** `python tools/parsers/o3d.py` reports 596/596 files parsed with the cursor
  landing exactly on end-of-file and no out-of-range vertex or material index. Totals:
  2,133 materials, 13,950 objects, 130,797 faces, 140,129 vertices, 14,700,676 bytes —
  matching the 14.0 M `.O3D` figure in E-0008. All 596 are version 0.95.
  5,613 objects set the shared-geometry flag; 5,193 objects hold zero vertices of their
  own yet carry faces, and **every one of those 5,193 names a parent** whose vertex array
  its faces index — no exceptions, so the validator resolves indices up the parent chain.
- **Method:** parser written from the loader (E-0017), never from corpus guesswork; its
  `--selftest` also asserts that a trailing byte, a truncated file, an unknown signature
  and an out-of-range index are each rejected.
- **Confidence:** proven for version 0.95. The 1.00 LOD block in `FUN_10012920` is
  described in the `.ksy` but unimplemented and unexercised — no 1.00 file exists in the
  corpus, and the parser raises rather than guessing.

### E-0019 — `.L3D` is the X3D engine's light container; 5/5 corpus files parse
- **Binary/file:** `x3d.dll`, `Original Game Files/Data/U0[1-7]*/Static/*.L3D` (5 files,
  5,718 bytes total).
- **Evidence:** signature `(c) 1998 4X Tech. 0.95 (L)` (matching the engine family) on all
  five. `python tools/parsers/l3d.py` reports 5/5 files parsed with the cursor landing
  exactly on end-of-file. Totals: 78 lights, 0 spot, 5,718 bytes — matches the 5.6 K
  `.L3D` figure in E-0008.
- **Method:** `X3d_Load_Sdk_l3d` at `x3d.dll` `0x100012fd` decompiled with
  `tools/ghidra_scripts/decompile_one.py`; per-light layout taken from the read sequence
  in `FUN_10014d50` (`x3d.dll` `0x10014d50`) — `FUN_1000bb50` 32-byte name, three
  `FUN_1000bb20` for position, three `FUN_1000baf0` for RGB, three more `FUN_1000bb20`,
  two `FUN_1000ba90`, one `FUN_1000ba90` `is_spot`, plus a spot branch (3+2 f32) only
  when set. Per-light size is 71 bytes omni / 91 bytes spot, fixed regardless of other
  fields. `X3d_Light_Create` (`0x10001078`) called per omni light; `X3d_Spot_Light_Create`
  (`0x10001253`) called per spot.
- **Confidence:** proven for omni. The spot branch is parsed (test exercises it) but no
  1.00 or spot-`.L3D` file exists in the corpus; that path is unexercised and logged as
  Q-0013.

### E-0020 — The `(c) 1998 4X Tech. 0.95 (X)` family spans at least `.O3D`, `.A3D`, `.L3D`
- **Binary/file:** `x3d.dll`, corpus `.O3D` (596), `.A3D` (429), `.L3D` (5) files.
- **Evidence:** all three extensions carry the engine's 27-byte `(c) 1998 4X Tech. 0.95`
  signature with the suffix letter — `(O)`, `(A)`, `(L)` — in place, followed by an
  `x3d.dll` global `DAT_1002d224` selector. The same four stream-read primitives
  (`FUN_1000ba90` u32, `FUN_1000baf0` u8, `FUN_1000bb20` f32, `FUN_1000bb50` n-bytes) are
  the only file-reading primitives any of the loaders touch. Per-format work differs only
  in the per-record reader the top-level loader dispatches to (`FUN_10012920` for `.O3D`,
  `FUN_10012ee0` for `.A3D`, `FUN_10014d50` for `.L3D`).
- **Method:** decompiled `X3d_Load_Sdk_o3d`, `X3d_Load_Sdk_a3d`, `X3d_Load_Sdk_l3d` and
  their per-format callees; confirmed the four primitives are the only file reads in each
  via callee lists emitted by `tools/ghidra_scripts/decompile_one.py`.
- **Confidence:** strong. `.S3D` and `.C3D` have not been recovered yet but the same
  signature scheme and same primitive set are visible in `X3d_Load_Sdk_s3d` and
  `X3d_Load_Sdk_c3d` exports, so the family claim is likely to extend to them once
  their layouts are recovered.

### E-0021 — `.C3D` is the X3D engine's camera container; 6/6 corpus files parse
- **Binary/file:** `x3d.dll`, `Original Game Files/Data/U0[2-7]*/Static/CAMERA.C3D` and
  `Data/U04/Anim/U04_03_Lunettes/CAMERA.C3D` (6 files, 648 bytes total).
- **Evidence:** signature `(c) 1998 4X Tech. 0.95 (C)` on all six. `python
  tools/parsers/c3d.py` reports 6/6 files parsed with the cursor landing exactly on
  end-of-file. Totals: 6 cameras, 648 bytes — matches the 648 B figure in E-0008.
- **Method:** `X3d_Load_Sdk_c3d` at `x3d.dll` `0x1000124e` decompiled with
  `tools/ghidra_scripts/decompile_one.py`; per-camera layout taken from the read
  sequence in `FUN_100148e0` (`x3d.dll` `0x100148e0`) — `FUN_1000bb50` 32-byte name
  into camera-struct offset `+0x0C`, then ten `FUN_1000bb20` f32s into camera-struct
  offsets `+0x2C, +0x30, +0x34, +0x3C, +0x40, +0x44, +0x54, +0x58, +0x4C, +0x50`
  (non-monotonic in file order — the parser tracks file order). `X3d_Camera_Create`
  (`0x10001406`) called per camera. Per-camera size is 72 bytes, fixed regardless of
  field semantics.
- **Confidence:** proven for the layout (6/6 corpus, every byte consumed). The 10 f32s
  carry no names; the split into three plausible vec3s at `+0x2C, +0x3C, +0x4C`
  (position / target / up) is Q-0014, unproven. No 1.00 `.C3D` file exists in the
  corpus.

### E-0022 — `.S3D` is the X3D engine's scene super-container; 1/1 corpus file parses
- **Binary/file:** `x3d.dll`, `Original Game Files/Data/U02/anim/U02_02/U02_02.S3D`
  (73,916 bytes).
- **Evidence:** signature `(c) 1998 4X Tech. 0.95 (S)`. `python tools/parsers/s3d.py`
  reports 1/1 file parsed with the cursor landing exactly on end-of-file. Totals: 0
  cameras, 0 lights, 5 materials, 53 objects, 53 animations, 73,916 bytes — matches
  the 72 K `.S3D` figure in E-0008.
- **Method:** `X3d_Load_Sdk_s3d` at `x3d.dll` `0x100010e1` decompiled with
  `tools/ghidra_scripts/decompile_one.py`. The loader is a sequencer that dispatches
  to five per-format record readers — `thunk_FUN_100148e0` (cameras, same as `.C3D`),
  `thunk_FUN_10014d50` (lights, same as `.L3D`), `thunk_FUN_10011450` (materials, from
  the `.O3D` chain), `thunk_FUN_10012920` (objects, from the `.O3D` chain),
  `thunk_FUN_10012ee0` (animations, same as `.A3D`). Each section starts with a u32
  count, then that many records; no per-section signature. The parser is a thin wrapper
  around the existing per-format record readers (`c3d._parse_camera`, `l3d._parse_light`,
  `o3d.read_material`, `o3d.read_object`, `a3d.read_animation`) wired through a
  `_O3dReaderAdapter` that bridges the `o3d.Reader` API onto the `common.Reader`
  cursor.
- **Confidence:** proven for the layout (1/1 corpus, every byte consumed). No 1.00
  `.S3D` file exists in the corpus. Adding `.S3D` to the family claim (E-0020)
  strengthens it: `.S3D` is the engine's own multiplex of the per-format record
  shapes, not a new format.

### E-0023 — `.MAT` is the X3D engine's plain-ASCII material script; 5/5 corpus files parse
- **Binary/file:** `Original Game Files/Data/U02/anim/U02_02/U02_02.MAT` (1,879 B),
  `Data/U02/anim/U02_03/U02_03LOD.MAT` (144 B), `Data/U02/anim/U02_05/U02_06.MAT`
  (484 B), `Data/U04/Anim/U04_02/OUVRE02.MAT` (1,863 B),
  `Data/U05/anim/U05_05/ACTION01.MAT` (488 B).
- **Evidence:** no magic. Each file is latin1 text. `python tools/parsers/mat.py`
  reports 5/5 files parsed, every line consumed. Totals: 12 materials, 4,858 bytes —
  matches the 4.7 K `.MAT` figure in E-0008. Empty material list accepted
  (`U02_03LOD.MAT`).
- **Method:** layout derived directly from the sample bytes per the handoff
  (`03-HANDOFF-PHASE-2.md` §2) — "`.MAT` is plain ASCII (line 1 is `;-------...`),
  so the loader skip applies — parse it directly off the sample bytes, no decompile
  needed". The format is provable from sample bytes alone because every material block
  is exactly 16 fixed lines in documented order with no flags or variable-length
  sections. Decompiling the loader would only re-derive what the corpus already shows.
- **Structure:** three-line header (banner `;` + 47 dashes, `; <path>`, banner), then
  zero or more 16-line material blocks separated by banner lines. Per-block key order:
  `MATERIAL`, `TYPE`, `AMBIENT`, `DIFFUSE`, `SPECULAR`, `LIGHT_COLOR`, `SHININESS`,
  `SHININESS_STRENGTH`, `TRANSPARENCY`, `BINARY_OPACITY`, `TWO_SIDED`, `TILING`,
  `TEXTURE_MAP`, `REFLECTION`, `LIGHT_MAP`, `REFLECTION`. The duplicated trailing
  `REFLECTION=` is a stable writer artefact across all 5 files.
- **Confidence:** proven. No `.MAT` loader decompile was performed; the handoff's
  loader-skip note is the citation for this exception to the default rule.

### E-0024 — `.BMP` files are standard Windows BITMAPINFOHEADER (BMP3); 381/381 corpus files parse
- **Binary/file:** `Original Game Files/Data/**/*.BMP` (381 files, 131,324,774 bytes
  on disk).
- **Evidence:** all 381 files begin `BM`, all carry a 40-byte DIB header
  (`0x00000028` at offset 14), all have `compression = BI_RGB (0)`. BPP counts:
  24 bpp × 340 files, 16 bpp × 40 files, 8 bpp × 1 file. Total pixels 46,347,716.
  `python tools/parsers/bmp.py` reports 381/381 files parsed; expected file size
  (`off_bits + row_stride × |height|`) matches on-disk size for 136/381 — the
  remaining 245 have a wrong-but-close declared `file_size` field (3 of them
  short by 17–100 bytes — `SaveRetourD.BMP`, `SaveSommaireD.BMP`, `U01_04P.BMP`).
  These are still valid BMPs because the writer flushed the header before the
  trailing pixel rows; width/height/bpp stay self-consistent.
- **Method:** layout derived from Microsoft's published BMP3 spec, no decompile
  required. The validator derives size from `off_bits + row_stride × |height|`,
  not from the declared field. `--selftest` exercises trailing bytes, magic,
  DIB-header mismatch, truncation, palette handling, declared-size drift.
- **Confidence:** proven for the corpus (381/381 parse). No `BITMAPV4`/`V5`,
  `BI_BITFIELDS`, `BI_RLE4`/`8`, `BI_JPEG`, `BI_PNG` exist in the corpus.

### E-0025 — Every `.BIN` is one chunk container: trailing `#NAME#` table + `u32 count`; 109/109 parse
- **Binary/file:** `MissionMonet.exe`; `Original Game Files/Data/**/*.BIN` (109 files).
- **Evidence:** `FUN_00415420` (`0x00415420`) does `fseek(f, -4, SEEK_END)` for the count,
  then `fseek(f, -(count*0x1c + 4), SEEK_END)` for the table
  (`notes/decomp/MissionMonet.exe__FUN_00415420.c:21,29-30`). `FUN_00415190` finds a chunk
  by name via `sprintf` of the tag (`notes/decomp/MissionMonet.exe__FUN_00415190.c:26`).
  Table entry = `char name[20]`, `u32 offset`, `u32 size`. In all 109 files the chunks
  tile `[0, table)` exactly, no gaps, no overlap. Chunk names seen: `#INDEX#` ×81,
  `#ACTIONS#`/`#OBJECTS#`/`#SCENE#`/`#CAMERA#` ×9, `#APP#`/`#GAME#` ×1.
- **Method:** `python tools/parsers/binchunk.py` → 109/109, `--selftest` covers truncation,
  bad names, trailing bytes, zero count.
- **Confidence:** proven for the container layer. Payloads per chunk name are separate
  specs. Supersedes the "at least seven distinct layouts" reading in Q-0016 and the
  "terminator" reading in `docs/formats/README.md` (that 32-byte block is the table).

### E-0026 — `#OBJECTS#` payload is `u32 count` + `count` × 68-byte entries; 9/9 INFOOBJ.BIN parse
- **Binary/file:** `MissionMonet.exe`; `Data/U##/INFOOBJ.BIN` (9 files, 183 entries).
- **Evidence:** `FUN_0041d6f0` (`0x0041d6f0`) seeks `OBJECTS`, reads a `u32` count, then
  `count * 0x44` bytes in one read (`notes/decomp/MissionMonet.exe__FUN_0041d6f0.c:64-79`).
- **Method:** `python tools/parsers/infoobj.py` → 9/9, every byte consumed.
- **Confidence:** proven for layout; the seven numeric fields per entry are opaque until
  `FUN_0041b440` (per-entry consumer) is decompiled.

### E-0027 — The game reads `<exe dir>\Data\` if `APP.BIN` is there, and only otherwise searches for the CD
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `resolveDataPaths` (`0x004179b0`, was `FUN_004179b0`) takes the exe
  directory from `GetModuleFileNameA`, builds `<dir>\Data\` (data root, app `+0x26a`) and
  `<dir>\Save\` (app `+0x36e`, also where `DbgInfo.txt` is written), then calls
  `fileExists` (`0x00416370`, `CreateFileA` probe) on `<dir>\Data\APP.BIN`. Only if that
  fails does it set app `+0x474 = 1`. The startup function at `0x00416b40` (auto-named
  `MessageToUser_34`, is the WinMain body) calls `findCdDriveByVolumeLabel` (`0x00417b30`)
  only when that flag is set. That function walks drives `C:`..`Z:`, reads each volume label
  with `getDriveVolumeLabel` (`0x004160b0`, `GetVolumeInformationA`), compares the first 8
  chars case-insensitively (`_strnicmp`) against a string at app `+0x108`, and on a match
  sets the data root to `%s:/Data/` (`0x00441628`). No match → message box `0x3b8`, exit.
- **Method:** MCP decompile of the four functions; string bytes read with `pefile`.
- **Confidence:** proven for the control flow. The expected label at app `+0x108` is not
  traced (Q-0002). Practical consequence: a folder holding the `02_PR` binaries plus a
  copy of `Data/` runs without a CD or the installer.

### E-0028 — `x3d.dll` names the rasteriser and math DLLs as strings, so it loads them itself
- **Binary/file:** `x3d.dll`, `xd3d.dll`, `4xvideo.dll`.
- **Evidence:** `x3d.dll` imports only `KERNEL32`/`MSVCRT`, yet contains the strings
  `xd3d.dll`, `xs3d.dll`, `xf3d.dll`, `xvr3d.dll`, `x3dmp5.dll`, `x3dmp6.dll`,
  `x3dmp6k.dll`. `xd3d.dll` and `4xvideo.dll` statically import `h3d.dll`; `h3d.dll`
  imports `DDRAW.dll`.
- **Method:** `pefile` import tables plus a byte scan for `*.dll` strings.
- **Confidence:** strong. It shows the names exist, not which one is picked at runtime (Q-0001).
  `xf3d.dll` and `xvr3d.dll` are not in the install payload.

### E-0029 — The startup dialog is 4xvideo's device dialog; its hidden "Window" command selects h3d's windowed mode
- **Binary/file:** `4xvideo.dll`, `h3d.dll`.
- **Evidence:** `Video4x_Init` (`4xvideo.dll` `0x10001005`) runs `DialogBoxParamA(hinst, 0x65,
  hwnd, 0x10001a20)` using the *game's* module handle, so the game's own dialog resource
  (portrait, OK/Exit) is shown. The dialog procedure (`0x10001a20`) sets the fullscreen flag
  `DAT_10005548 = 1` on `WM_INITDIALOG`, sets it to 1/0 on commands `0x3f6`/`0x3f7`, and ends
  the dialog on `0x3f3` (OK). Monet's dialog has no `0x3f6`/`0x3f7` controls, but the
  procedure still honours the commands. `FUN_10001290` then calls
  `H3d_DDDriver_Init_D3DDriver_And_Video_Mode(ctx, driver, mode, DAT_10005548, 1)`. In
  `h3d.dll` a zero fourth argument sets `ctx[0x8d36] = 0`, sizes the window to the mode with
  `AdjustWindowRectEx`/`SetWindowPos` and calls `SetCooperativeLevel(hwnd, 0x808)`
  (`DDSCL_NORMAL | DDSCL_FPUSETUP`). Nonzero calls `SetCooperativeLevel(hwnd, 0x811)`
  (exclusive, fullscreen) and `SetDisplayMode`. In windowed mode `H3d_WindowProc` blits the
  back buffer to the client rectangle on `WM_PAINT`.
- **Method:** MCP decompile of `Video4x_Init`, `FUN_10001290`, `0x10001a20`,
  `H3d_DDDriver_Init_D3DDriver_And_Video_Mode`, `H3d_WindowProc`. Confirmed at runtime:
  posting `WM_COMMAND 0x3f7` then `0x3f3` gives a 640×480 window that renders 3D.
- **Confidence:** proven.

### E-0030 — In windowed mode the game refuses any desktop colour depth but 16 bpp
- **Binary/file:** `MissionMonet.exe`, `MissionD.exe`.
- **Evidence:** `MissionMonet.exe` `0x00417683` calls `GetDeviceCaps(GetDC(hwnd), BITSPIXEL)`
  when `0x004667a4` (fullscreen flag returned by `Video4x_Init`) is 0; `cmp eax, 0x10` /
  `je 0x004176c3` at `0x00417689`/`0x0041768c` skips message 951 "Please set your screen to 16
  bits colour mode." `MissionD.exe` has the same check at `0x0042cd62`/`0x0042cd6b`.
- **Method:** capstone disassembly at the `push 0x3b7` site. Seen at runtime on a 32-bit
  desktop. `tools/proxy/patch_exe.py` turns the `je` into `jmp` in the run-folder copy.
- **Confidence:** proven.

### E-0031 — The game stalls its main loop while inactive, and lets `H3d_WindowProc` pre-empt every message
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** window procedure at `0x00416650`: every message goes first to
  `H3d_WindowProc(ctx, hwnd, msg, wp, lp, &handled, &result)` (`0x004166d5`, cdecl, 7 args).
  If `handled` is set it returns `result` immediately. Otherwise `WM_ACTIVATE`
  (`0x00416738`) sets the active flag `0x0046ec08` to 1 only if `LOWORD(wp) != WA_INACTIVE`
  and `HIWORD(wp) == 0`, else 0. `WM_ACTIVATEAPP` (`0x0041678f`) sets it to 1 for `wp` 1 or 2,
  else 0. Both clear the 1020-byte key-state array at `0x0046e7e0`. WinMain's loop at
  `0x00416b40` spins `FUN_00416990` while `0x0046ec08 == 0`.
- **Method:** capstone disassembly; runtime confirmation: with the h3d proxy's
  `MONET_BACKGROUND=1` swallowing focus-loss messages, the game keeps rendering unfocused.
- **Confidence:** proven.

### E-0032 — WinMain shows `Intro1.bmp` for 3000 ms and `Intro2.bmp` for 2000 ms, busy-waiting on `timeGetTime`
- **Binary/file:** `MissionMonet.exe`; `Data/2dbit/Intro1.bmp`, `Intro2.bmp`.
- **Evidence:** WinMain (`0x00416b40`, renamed `WinMain_Boot`; the assert namer had
  mislabelled it `MessageToUser_34`) formats `%s2dbit/Intro1.bmp` (`0x00441588`) with the
  data root (app `+0x26a`, E-0027), calls `ShowFullscreenBitmap` (`0x00416fc0`), then
  `WaitMilliseconds(3000)` (`0x004163d0`); then `%s2dbit/Intro2.bmp` (`0x00441574`),
  `WaitMilliseconds(2000)`, and `ShowFullscreenBitmap` on Intro2 a second time.
  `WaitMilliseconds` reads `timeGetTime` once and spins until the difference reaches the
  argument: no message pump, no sleep, no input check. `ShowFullscreenBitmap` loads the
  file into a surface (`FUN_004156a0`), `SetRect(0,0,0x280,0x1e0)`, blits it to (0,0) with
  flags `0x10` (`DDBLTFAST_WAIT`) and calls `H3d_Show_BackBuffer`. Both files are
  640×480 24-bit (921,656 bytes).
- **Method:** MCP decompile of the three functions; runtime (`run.ps1`, which confirms the
  startup dialog first): `snap.ps1` 3 s after launch shows Intro2, 6 s shows U00's 3D
  garden with Monet, 9 s the players screen (E-0034).
- **Confidence:** proven.

### E-0033 — After the intro the app enters mode 1 with scene `U00.X3D`, and `LoadUnitScene` picks the unit class from the name's digits
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** WinMain copies `U00.X3D` (`0x0044156c`) to game `+0x14c` and calls
  `SetAppMode(app, 1)` (`0x00417ce0`, stores app `+0x47c`). The main loop switches on that
  mode: 1 calls `LoadUnitScene(game+0x14c, 1, 0)` (`0x004130b0`, thiscall on game); 2 renders the paused scene
  plus the 2D frame (`FUN_00414800`/`FUN_00414630`, `H3d_Show_BackBuffer`); 0 calls the
  scene's vtable `+0x24` and `+0x1c` each iteration. `LoadUnitScene` destroys the current
  scene, takes 2 characters from index 1 of the name (`FUN_00416140(name,1,2)`), `atoi`s
  them, and calls `CreateUnitScene(n)` (`0x00417f10`): 0 → `FUN_004097e0` (U00), 1 →
  `FUN_00401000`, 2 → `FUN_00402af0`, 3 → `FUN_00404e70`, 4 → `FUN_0040a720`, 5 →
  `FUN_0040ece0`, 6 → `FUN_00410940`, 7 → `FUN_004112b0`, 0x21 → `FUN_00407090`, 0x32 →
  `FUN_004123c0`, other → base `FUN_0041a890`. It then calls `XScene_70(scene, name)`,
  `SetAppMode(app, 0)`, vtable `+0x10(name)` and vtable `+0x14(a, b)`, where `a`, `b` are
  its second and third arguments (`ret 0xc`; pushes at `0x00413157`..`0x00413169`). It has
  two callers: the loop's mode-1 branch (`0x00416e5a`) passes `(game+0x14c, 1, 0)`, so every
  scene switch goes through "write name to game `+0x14c`, set mode 1"; `0x00412d00` (reads
  the scene name from a `.BIN`-chunked save stream, `FUN_004153a0(+0x14c, 0x14)`) passes
  `(name, 0, stream)`. So `a == 1` means "entered normally", `a == 0` "restored from a save".
- **Method:** MCP decompile of WinMain, `SetAppMode`, `LoadUnitScene`, `CreateUnitScene`.
- **Confidence:** proven for the control flow; the meaning of vtable `+0x10`/`+0x14` is
  read from the U00 and U01 overrides (E-0034, E-0035).

### E-0034 — U00 is the menu scene: U04's garden with Monet, under the `OptionUser` frame ("The players")
- **Binary/file:** `MissionMonet.exe`; `Data/U00/U00.x3d`.
- **Evidence:** U00 vtable `0x004395d8`: `+0x10` = `0x0040a070` (created as `U00_Load`),
  `+0x14` = `0x0040a1e0` (`U00_Start`). `U00_Load` asserts `D:\MissionD\Source\U00.cpp`
  line `0xf5`, sets the map directory `%sU04/Maps/` (`0x0043feb8`) and the asset root
  `%sU04/` (`0x0043fea8`); `U00.x3d` is a text script (`;SCRIPT`, `Object="static\u04.o3d"`,
  `Lod="…,800"`, `Animation="Anim\porche.a3d"`) that names only U04 assets. `U00_Start`
  loads animation `U04_03_Lunettes` for object `U04_03`, positions the camera
  (`FUN_00419520(cam, 81.1334, 265.8100, 15.0)`, floats `0x42a2449c 0x4384e7ae 0x41700000`),
  and, when `0x0046ed88 == 0`, calls `SetAppMode(app, 2)` and opens the 2D frame
  `OptionUser` (`0x0043fec4`) through the frame manager's vtable `+0x90`.
- **Method:** vtable read with `pefile`; functions created and decompiled over MCP.
  Runtime: `snap.ps1` 9–50 s after launch shows a static screen titled "The players",
  "New players : Player's name", a list box and OK; nothing else happens without input.
- **Confidence:** proven for the sequence; the frame contents come from
  `Data/2DFRA/OptionUser.fra` by name only (`.FRA` is still open, Q-0016).

### E-0035 — U01 entered with flag 1 plays `Video/Prologue.AVI` with `Video/Prologue.wav`
- **Binary/file:** `MissionMonet.exe`; `Data/Video/Prologue.avi`, `prologue.wav`.
- **Evidence:** `0x00401230` (created as `U01_Start`; U01's constructor `0x00401000` installs
  vtable `0x004393d0`, whose `+0x14` is `0x00401230`, so `LoadUnitScene` reaches it): if its first argument is nonzero it calls
  `PlayVideo("Prologue", 0, 1)` (`0x00417030`), else vtable `+0x4c("U01", 1)` (`0x0043f124`). `PlayVideo`
  sets app mode 3, opens `%sVideo/%s.AVI` (`0x0043fcb4`) with `AviOpenFile`, plays it at
  (0,0) with `AviPlayMovie(0,0)`, then starts `%sVideo/%s.wav` (`0x0044159c`) through
  `LSoundManager_290` when the name is non-empty. It loops pumping messages until key
  `0x0d` (Enter) or `0x1b` (Escape) is down (`FUN_004163b0`) or `AviGetStatus() == 4`,
  then `AviClose`, stops sound channel 2 when the third argument is set, and returns to
  mode 0. `Prologue.avi`: one stream, IV50, 640×480, 100,000 µs/frame, 652 frames
  (65.2 s). `prologue.wav`: PCM mono 8-bit 22,050 Hz, 63.3 s.
- **Method:** capstone disassembly at `0x00401230`, MCP decompile of `PlayVideo`; AVI
  `avih`/`strh` and WAV headers read with Python.
- **Confidence:** proven: U01 entered normally (not from a save, E-0033) plays the prologue
  first. The path from `OptionUser` to U01 is still Q-0018.

### E-0036 — `.X3D` is a keyword script read by `load.cpp`; 24/24 parse
- **Binary/file:** `MissionMonet.exe`; `Data/**/*.X3D` (24 files).
- **Evidence:** `FUN_0041fb30` dispatches on the lower-cased name: `.s3d` →
  `X3d_Load_Sdk_s3d`, `.o3d` → `X3d_Load_Sdk_o3d`, `.x3d` → read the whole file and call
  `load::load_262` (`0x0041f8c0`, assert `D:\MissionD\Source\load.cpp`). That loop skips
  space/tab/CR/LF (`FUN_0041f1e0`), skips `;` lines (`FUN_0041f220`), and matches a keyword
  with `_strnicmp` against the table at `0x00441d94`: `scene=` `object=` `animation=`
  `camera=` `light=` `lod=` (indices 0..5); no match asserts (load.cpp `0xea`). Each takes
  a `"`-quoted field read by `FUN_0041f260` (stops at `"`, CR or `,`; 255 chars max).
  Handlers: `scene=` → `X3d_Load_Sdk_s3d`; `object=` (`FUN_0041f3f0`) →
  `X3d_Load_Sdk_o3d`, remembers the object in `0x0046ec44`, and hides it
  (`X3d_Object_Hide(obj,1)`) when the lower-cased path starts `static\col` (`0x00441df4`);
  `animation=` (`FUN_0041f500`) takes an optional `,fps` (default 30.0) and calls the
  scene's vtable `+0x20(path, lastObject, fps)`; `camera=` → `X3d_Load_Sdk_c3d`; `light=`
  → `X3d_Load_Sdk_l3d` then `X3d_Scene_All_Light_Include_Scene_All_Object(scene,1)`;
  `lod=` (`load::load_185`, `0x0041f620`) takes a mandatory `,distance`, loads the `.O3D` and calls
  `X3d_Object_Add_Lod(lastObject, lod, scene, distance)` and
  `X3d_Scene_All_Light_Include_Object`. Every path is prefixed with the scene's asset
  directory (`"%s%s"`, `0x0043feb0`, scene `+8`).
- **Method:** MCP decompile of the functions named; strings read with `pefile`;
  `python tools/parsers/x3d.py` → 24/24 (`--selftest` passes). Corpus totals: object 619,
  lod 406, animation 169, light 4, camera 4, no `scene=`. Every file referenced by the 18
  scene scripts in `Data/Uxx/` exists; the 6 scripts under `Anim/`/`Capt/` are authoring
  leftovers with 45 dangling references between them.
- **Confidence:** proven. Resolves Q-0004 (one grammar; the `OBJE` prefix is a script
  without the `;SCRIPT` comment line).

### E-0037 — A new game starts at the scene named in `App.bin` `#GAME#` (`U01.X3D`); `U##D.X3D` belong to the gallery
- **Binary/file:** `MissionMonet.exe`; `Data/App.bin`.
- **Evidence:** `FUN_00412b80` opens `%sAPP.BIN` (`0x00441100`), seeks chunk `GAME`
  (`0x004410f8`) and reads 0x1e bytes into game `+0x14c` (the next-scene slot, E-0033);
  if that fails it copies `U01.X3D` (`0x004410f0`). It then names the player `NoName`
  (`0x004410e8`) and calls `SetAppMode(app, 1)`. `App.bin` `#GAME#` is at offset 0x15e,
  size 0x1e: `U01.X3D\0` followed by filler. `FUN_004131e0` maps painting ids (`U11_01`
  → `U01D.X3D`, `U11_02`/`U11_03` → `U02D.X3D`, … `U14_07` → `U06D.X3D`) and loads them
  with `CreateUnitScene(0x32)`: the `D` scripts are the painting view's backdrops.
- **Method:** MCP decompile; `App.bin` bytes read with `xxd`.
- **Confidence:** proven for what `FUN_00412b80` does; which UI button calls it is part of
  Q-0018.

### E-0038 — `.DMF` is the texture format; `x3d.dll` reads it for every `.TGA` map name; 518/518 parse
- **Binary/file:** `x3d.dll`; `Data/**/*.DMF` (518 files).
- **Evidence:** `X3d_Map_Init` (`0x10001618`) overwrites a map name from its first `.`
  with the 5 bytes at `0x10027c14` (`.dmf\0`). `FUN_10016020` opens that file through the
  host's file callbacks, `FUN_10010ba0` requires `u16 0xfb00` (`cmp word [esp+6], 0xfb00`,
  `0x10010bc5`) and a `u32` total size, then loops `FUN_100108a0` over chunks
  `u16 id, u32 size` (size includes the 6-byte header) until the cursor equals the total:
  `0xfb10` u16 bpp, u16 width, u16 height (`FUN_100105f0` allocates; bpp 8 also gets a
  0x600-byte palette buffer); `0xfb20` 0x400 palette bytes; `0xfb21` 4 bytes colour key
  (first three R, G, B; sets map `+0x2c = 1`); `0xfb22` u32 to map `+0x28`; `0xfb23` u32
  to the map's animation block `+8` and sets its `+4 = 1`; `0xfb30` raw pixels (w·h bytes
  at bpp 8, else w·h u16); `0xfb31` 2×2 vector quantisation (`FUN_10010770`: 0x800-byte
  codebook of 256 × 4 u16, then (w/2)(h/2) index bytes); other ids skipped by size.
  After loading, a bpp-15 map is converted to 565 when the display is 16-bit.
- **Method:** capstone scan of `x3d.dll` for the chunk ids, MCP decompile of the four
  functions; `python tools/parsers/dmf.py` → 518/518, every byte consumed (`--selftest`
  passes). Corpus: bpp 15 × 251, bpp 8 × 267; chunk layouts `10 22 30` × 215,
  `10 20 21 22 30` × 162, `10 20 22 30` × 105, `10 21 22 30` × 33, `10 21 23 22 30` × 3;
  no `0xfb31`. Palette entries are B, G, R, 0: decoding U01's `MonetTet.dmf`,
  `Costard.dmf` and `Palette.dmf` in that order gives skin tones and wood, R, G, B order
  gives blue skin. bpp 15 is 555 (U01 `djeul.dmf`, a face, decodes correctly).
- **Confidence:** proven for the layout and the pixel formats; `unk_fb22`/`unk_fb23` stay
  opaque. Resolves Q-0005 (the header bytes are the file size), Q-0011 (the `.TGA` names
  are rewritten to `.dmf`) and Q-0015 (the reader is in `x3d.dll`, behind the host file
  callbacks, which is why no string or import pointed at it).

### E-0039 — `SCENE.BIN` `#SCENE#` is ambient RGB + a scene scale; `#CAMERA#` is FOV, collision sphere and speed
- **Binary/file:** `MissionMonet.exe`; `Data/U*/SCENE.BIN` (9 files).
- **Evidence:** the scene's vtable `+4` (`FUN_0041d340`) reads `#SCENE#` (`0x00441b74`) as
  u32 r, g, b and f32 into scene `+0x138`, then calls `FUN_0041b2f0(scene, r, g, b)`, which
  calls `X3d_Scene_Set_Ambient_Light` (trace call site `0x0041b31f`). The camera init
  (`0x00418560`) reads `#CAMERA#` (`0x00441668`) as four f32: camera `+0x10` (passed to
  `X3d_Camera_Set_Fov`), `+0x64` (sphere radius), `+0x68` (sphere Z offset), `+8`. It
  then overwrites `+8` with 2.0, sets the eye height `+0x5c = scale · 1.5`, the position
  (0, 0, eye height), angles (0, π/2), creates the collision sphere with radius
  `scale · 0.5` and Z offset `eye height − 2 · radius`. Values: U01 `#SCENE#` (255, 255,
  255, 40.0), `#CAMERA#` (90, 20, 40, 2); all nine files have FOV 90.
- **Method:** MCP decompile of `FUN_0041d340` and `0x00418560`; payloads read with Python
  (E-0025 container).
- **Confidence:** proven for the layout and where the values go. The meaning of scene
  `+0x138` beyond "unit length" (eye height and sphere derive from it) is inferred.

### E-0040 — The X3D view: horizontal FOV in degrees, yaw/pitch angles, a 4:3 frame at any resolution
- **Binary/file:** `x3d.dll`, `MissionMonet.exe`.
- **Evidence:** `X3d_Camera_Set_Fov` stores camera `+0x50`, `X3d_Camera_Set_Polar`
  `+0x54`/`+0x58`, `X3d_Camera_Set_Position` `+0x2c..0x34`. `FUN_10007dd0` (`x3d.dll`)
  builds the view: translation by −position; a rotation R with rows
  (−sin a, cos e·cos a, sin e·cos a), (−cos a, −cos e·sin a, −sin e·sin a), (0, sin e, −cos e)
  for a = `+0x54`, e = `+0x58` (row vectors, v·T·R); a roll by `+0x4c` degrees; and a
  scale of x by `1/tan(fov·π/360)` and y by `1/tan(fov·π/360) · (w/2) / ((h/2) · k)`.
  `X3d_Scene_Init_Resolution` stores w/2, h/2 at viewport `+0x10`/`+0x14` and `k` at scene
  `+0x34`; the EXE (`0x0041af4e`..`0x0041af88`) passes origin (0,0), the video mode's
  width and height, `k` = video `+0x14`, near 0.1 (`0x3dcccccd`), far 1,000,000
  (`0x49742400`). `FUN_00418350` sets video `+0x14 = (w/h) · 0.75`, so the y scale is
  always `4/3 · x scale`: the picture is framed for 4:3 whatever the mode.
- **Method:** MCP decompile of the four `x3d.dll` functions and `FUN_00418350`; capstone
  disassembly of the `X3d_Scene_Init_Resolution` call.
- **Confidence:** proven for the matrices. With e = π/2 the camera looks along
  (cos a, −sin a, 0) with world +Z up; the screen-space sign of y is taken from render
  comparison (docs/engine-spec/scene.md).

### E-0041 — U01's normal entry puts the camera at (−258.44, −508.20, 29.55), angles (1.31, π/2)
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `U01_Start` (`0x00401230`), after the prologue, builds a vec3 with
  `FUN_00415ed0(v, 0xc3813852, 0xc3fe199a, 0x41ec5e35)` and passes it to `FUN_004194f0`
  (camera: copy to `+0x14`, `X3d_Camera_Set_Position`), then `FUN_00419550(cam,
  0x3fa7ae14, 0x3fc90fd8)` (angles to camera `+0x34`/`+0x38` and X3D camera
  `+0x54`/`+0x58`), then runs the scene for 1500 (`0x5dc`) through `FUN_0041bf70` before
  scripted camera moves (`FUN_00419860`) and handing over control.
- **Method:** MCP decompile of `U01_Start` and the camera setters; floats decoded with
  Python.
- **Confidence:** proven for the values. The following camera moves and what
  `FUN_0041bf70`'s argument measures belong to the main-loop spec (next milestone).

### E-0042 — An `.O3D` object's world matrix is Tr(−pivot)·Scale·M·Tr(parent pivot + position)·parent; its vertices are local
- **Binary/file:** `x3d.dll`, `x3dmp5.dll`; `Data/U01/**/*.O3D`.
- **Evidence:** `FUN_10011ea0` (`x3d.dll`) reads the three vec3s after the object's light
  list into transform block (object `+0xfc`) `+0x14`, `+0x44`, `+0x64` and the 16 floats
  into `+0xb4`, copied to `+0x74` (`X3d_Matrice_Copy`). The getters name them:
  `X3d_Object_Get_Init_Pivot_Position` reads `+0x14`, `X3d_Object_Get_Local_Init_Position`
  `+0x44`, `X3d_Object_Get_Local_Init_Scale` `+0x64`, `X3d_Object_Get_Local_Init_Matrice`
  `+0xb4`. So the `.ksy` names `position`/`scale`/`rotation` were off by one slot: they are
  pivot, local position, local scale (supersedes those three names in `o3d.ksy`). The
  parent name is resolved to an object loaded earlier in the same file and stored at
  object `+0x20`. `FUN_1001dd30` (called via `X3d_Object_Get_Global_Matrice` /
  `_Position`, parents first through `FUN_1001dd00`) builds the global matrix `+0xf4` as
  `Tr(−pivot) · diag(scale) · M · Tr(position + user)` for a root and
  `Tr(−pivot) · diag(scale) · M · Tr(parent pivot) · Tr(position + user) · parent global`
  for a child, where `user` is `+0x24` (zero at load). `X3d_Matrice_Mult(dst, a, b)`
  (`x3dmp5.dll` `0x10001087`) computes dst = a·b; `X3d_Vecteur_Array_Matrice_Mult`
  computes v·M with the translation in row 3 (elements 12..14), so vertices are row
  vectors. Corpus: `U01/static/PTITRAIN.O3D` object `A154` has vertices spanning
  ±124.8 / ±93.4 / ±38.4 around 0 and local position (1124.8, 930.1, −1309.9): vertices
  are object-local, which supersedes "used as stored" in `docs/engine-spec/scene.md`.
- **Method:** MCP decompile of `FUN_10011ea0`, the getters, `FUN_1001dd00`,
  `FUN_1001dd30`, and the two `x3dmp5.dll` functions.
- **Confidence:** proven for the load-time pose. Animation (`.A3D`) overrides and the
  "weld" objects whose faces index a parent's vertices (Q-0020) are not covered.

### E-0043 — Only Enter (and Escape for videos) skips, through `GetAsyncKeyState`; U00's talk is unskippable
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `PlayVideo` stops on `GetAsyncKeyState` of Enter or Escape
  (`0x0041713f`, `0x0041714d`) or `AviGetStatus() == 4` (`0x0041716a`); Space and clicks do
  not skip. Unit scripts run sequences as blocking loops around `FUN_0041bf70(scene, ms)`;
  a typical wait loops while the voice channel plays (`FUN_00414ed0(scene[0x5e])`) or the
  camera moves (`DAT_00442640 + 0x168`) and exits early when `FUN_004163b0(0x0D)`
  (`GetAsyncKeyState(vk) & 0x8000`) is down: `U01_Start` `0x0040158d`, `0x0040169c`;
  `FUN_00402380` `0x00402434`; `U04::U04_1066` `0x0040da31` (`U04.cpp:1066`). Enter ends only
  the current wait; fixed `Wait(ms)` calls and animation-frame waits are not skippable.
  U00's talk helper `FUN_0040a5c0` loops only while the voice plays (no key check).
  Escape in play goes through the main loop's key table (`0x0046e7e0 + vk*4`, set by
  WM_KEYDOWN in the window procedure `0x00416650`) to `FUN_00416400`, gated by
  `app+0x484` ("Escape allowed", cleared by `U01_Start` at `0x004014c2`, set again at
  `0x00401752`). Space (`0x00431800`, gated by `app+0x488`) toggles a 2D bar parked at
  y = 480.
- **Method:** capstone read of the window procedure; MCP decompile of the functions named
  (background agent, 2026-09-25).
- **Confidence:** proven for the checks and addresses; that Space's bar is the inventory
  is the user's observation.

### E-0044 — U01's first shot, original vs engine: transform, UV v and screen orientation confirmed
- **Binary/file:** `MissionMonet.exe` with the real `x3d.dll` (`X3D_PROXY=0`); ScummVM engine
  `x3d` at the commit that adds `scene.cpp`; `Data/U01/`.
- **Evidence:** `traces/u01-start-original.png` (snap.ps1 of the original ~64 s after New
  game, first U01 frame) and `traces/u01-start-engine.png` (engine, `start_scene=U01.X3D`,
  camera E-0041), side by side in `traces/u01-start-compare.png` (captures stay local,
  `.gitignore`). The sky dome's cloud bands, the sun disc, its reflection streak on the
  water and the horizon line fall on the same pixels in both. So: vertices transformed
  per E-0042 are right (the "used as stored" reading is superseded); `.DMF` rows uploaded
  in file order with UV v = 0 at the first stored row are right (a flip would turn the
  clouds upside down); camera "up" (world +Z at e = π/2) is screen up and x is not
  mirrored. Differences: the original draws the distant buildings (`Box*`, materials
  `immgch`/`immdrt`) faint, blended with the sky; the engine draws them opaque. The engine
  shows boats (`$Z$barque0/1`, `$Z$barques`) and dark specks the original does not show
  (Q-0021).
- **Method:** `tools/proxy/run.ps1` + `send.ps1` sequence in `tools/proxy/README.md`;
  `snap.ps1`; PIL side-by-side.
- **Confidence:** proven for the three orientation questions; the differences are open.

### E-0045 — Object names prefixed `$XYZ$`, `$Z$`, `$XZ$` get camera types 1, 2, 3
- **Binary/file:** `MissionMonet.exe`, `x3d.dll`, `xd3d.dll`.
- **Evidence:** `FUN_0041b010` walks the scene's objects (`X3d_Scene_Find_First_Object` /
  `_Next_Object`) and calls `X3d_Object_Set_Camera_Type(obj, 1)` for names containing
  `$XYZ$` (`0x004417c8`), `2` for `$Z$` (`0x004417c4`), `3` for `$XZ$` (`0x004417bc`), then
  rewrites the name from the next `$` string match (`0x004417b8`). The setter stores
  object `+0x108`, read only by `xd3d.dll` (`FUN_10020310`, `FUN_10020720`, …), which
  passes it to the object class's render method (`+0x6c` vtable `+0x10`). U01's sun and
  boats are `$Z$` objects.
- **Method:** byte search of the binaries, MCP xrefs and decompiles.
- **Confidence:** proven for the mapping; that the types are billboard modes (face the
  camera around all axes / Z / X and Z) is inferred from the names.

### E-0046 — One logic step per rendered frame; movement is scaled by a QueryPerformanceCounter frame rate, turning is not
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** the main loop in `WinMain_Boot` (`0x00416e64`..`0x00416ea3`, capstone) calls,
  per iteration after the message pump `FUN_00416990`, scene vtable `+0x24`, `+0x1c`, and,
  if app `+0x480` is 0, `+0x40`. U01's vtable is `0x00439468` (stored by the constructor at
  `0x00402afa`; `+4` is `FUN_0041d340`, E-0039): `+0x24` `FUN_0041c350` (animation and sound
  tick), `+0x1c` `U01_UpdateFrameLogic` (`0x00402f70`, calls `Scene_RenderFrame` first),
  `+0x40` `Scene_HandleInput` (`0x0041b7f0`, calls `Camera_HandleKeys`). `Scene_RenderFrame`
  (`0x0041b130`) renders (`X3d_Render`), then `QueryPerformanceCounter` into scene `+0x128`
  and sets scene `+0x144 = frequency / (counter − scene +0x120)` (frequency from
  `QueryPerformanceFrequency` at `+0x130`, set with the first counter in `XScene::XScene_124`
  `0x0041acf0`), copies the counter to `+0x120`, and presents (`H3d_Show_BackBuffer`). No
  `Sleep` or wait in the loop. `Camera_SetWalkVelocity` (`0x00418b60`) divides by
  `max(+0x144, 8.0)`; `FUN_00418d30`/`FUN_00418d00`/`FUN_00418d60`/`FUN_00418da0` add
  camera `+0xc · 0.06` per call with no time factor. `Scene_RunFor` (`0x0041bf70`): with
  ms = 0 one `FUN_0041c350` + `Scene_RenderFrame` + pump, otherwise repeated until
  `timeGetTime` has advanced ms.
- **Method:** MCP decompile; capstone disassembly of the loop; vtable read with `pefile`.
- **Confidence:** proven for the order and formulas. The real frame rate of the original
  is not known (Q-0022).

### E-0047 — Keyboard camera: key table, bindings, speeds, turn and pitch steps, head bob
- **Binary/file:** `MissionMonet.exe`, `x3dmp5.dll`.
- **Evidence:** the window procedure (`0x00416650`) sets `0x0046e7e0 + vk·4` to 1 on
  WM_KEYDOWN (`0x00416877`) and to 0 on WM_KEYUP (`0x00416860`). `Camera_HandleKeys`
  (`0x00418970`) reads, in order: `0x0046e824` (VK 0x11 Ctrl; with camera `+0x48` sets mode
  `+0x54` = 1), `0x0046e960` (0x60 Numpad 0 → `Camera_Crouch`), `0x0046e820` (0x10 Shift →
  `Camera_Jump`), `0x0046e878` Up → `FUN_00418c70`, `0x0046e880` Down → `FUN_00418cb0`,
  `0x0046e87c` Right → `FUN_00418d30`, `0x0046e874` Left → `FUN_00418d00`, `0x0046e864`
  PgUp → `FUN_00418d60` and `0x0046e868` PgDn → `FUN_00418da0` (both only without Ctrl).
  Up/Down need camera `+0x40`, set `+8` to 2.0 (`DAT_00441660`) / to half of it when equal,
  call `Camera_SetWalkVelocity` (1 / 0), `Camera_HeadBob` (`0x00418f60`) and
  `FUN_00418fd0`. Turns and pitches need `+0x44`; pitch is stepped only while
  `+0x38 < 2.7` (up) or `> 0.6` (down). `Camera_SetWalkVelocity`:
  `X3d_Convert_From_Polar(a, e)` (`x3dmp5.dll` `0x10001450`: (cos a·sin e, −sin a·sin e,
  −cos e)), normalised; step = `+8 · scene+0x138 / max(fps, 8)`, halved when
  `Camera_DistanceAhead` (`0x00419dc0`) < 2·`+0x64`; ×2 for mode 1, ×0.25 for modes 2 and
  4, ×0.5 for mode 3; writes only velocity x, y (`+0x24`, `+0x28`). The constructor
  `FUN_004184b0` sets `+0xc` = 1.0, `+0x10` = 90, `+0x40` = `+0x44` = 1, `+0x48` = `+0x4c`
  = 0, `+0x58` = 1, `+0x70` = 1. `Camera_HeadBob`: global roll `0x0046ec30 += 0x00441664 /
  fps` (1.0), clamped to ±0.4 with the rate's sign flipped at the clamp, stored as X3D
  camera `+0x4c` (roll, degrees, E-0040). `U01_Start` sets the sphere Z offset to 37.0
  (`FUN_00419d00`); the camera init runs earlier, from `XScene::XScene_124`. Camera `+0x48`
  and `+0x4c` are written only at `0x00407d43`, `0x00409575`, `0x0040957e`, `0x0040977f`,
  `0x00409788` (outside U01's code).
- **Method:** MCP decompile; capstone read of the window procedure and `x3dmp5.dll`;
  byte scan for camera-field writes after a load of scene `+0x14c`.
- **Confidence:** proven.

### E-0048 — Collision: sphere slide against every non-flagged object, then a downward ray snaps the eye to ground + eye height
- **Binary/file:** `MissionMonet.exe`, `x3d.dll`.
- **Evidence:** `Camera_HandleKeys` ends with position += velocity when camera `+0x70` is 0,
  else `Camera_ApplyVelocity(1)` (`0x00419d30`): `Camera_SlideSphere` (`0x00419f70`: centre
  = eye − (0,0,`+0x68`) + velocity → `Sphere_ResolveAgainstScene` `0x0041a050` → + offset),
  then `Camera_FollowGround` (`0x0041a270`): segment eye → eye − (0,0,10000) against every
  face, keeps the highest hit; ≤ 1.3·`+0x5c` below → z = hit + `+0x5c`, return 0; else
  `Camera_Fall` (`0x00419390`: z = z₀ − t²·scale·5.9 until the drop is covered, then
  `%s/SAUT.WAV` (`0x00440cc4`) if camera `+0x58` and drop > 1.5·scale), return 2 → slide
  again; no hit → 3. Velocity is zeroed after. `Sphere_ResolveAgainstScene` walks
  `X3d_Scene_Find_First_Object` / `_Next_Object(scene, 1)` (depth-first over children,
  `x3d.dll`), skips objects with `+0x118` ≠ 0 or failing `X3d_Object_Check_Sphere_Collision`
  (world bounding sphere vs sphere), and per face calls `X3d_Sphere_Face_Collision(…, 2)`:
  signed plane distance must be in (0, r); inside all edge planes → contact = projection,
  return 2; else nearest edge/vertex point, return 1 if closer than r. On 1 the push normal
  is normalize(centre − contact), on 2 `X3d_Face_Get_Collision_Normal` (face `+0x40` `+8`);
  if its z ≥ cos(π/4) or ≤ −cos(π/4) the function returns at once, else centre = contact +
  normal·r. `X3d_Line_Face_Collision(…, 2)`: the endpoints' plane distances must have
  opposite signs with the start ≥ 0, and the crossing point inside every edge plane.
  `X3d_Object_Hide` sets object `+0x5c`, not `+0x118`; `+0x118` is written only by unit
  code, e.g. U01 `0x00401175` on `X3d_Scene_Get_Object(scene, "Box203")` (also hidden),
  `0x0041000c` on `ColPorte1`.
- **Method:** MCP decompile of the EXE functions and the four `x3d.dll` exports; capstone
  scan for `+0x118` stores.
- **Confidence:** proven for the algorithm. Which side a face's normal points to (vertex
  winding) is open (Q-0023).

### E-0049 — Jump, crouch, headroom and the `XHELP` debug mode
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `Camera_Jump` (`0x00419000`, needs camera `+0x4c` and `+0x40`): mode
  `3 − (mode ≠ 1)`; Up/Down sampled once with `GetAsyncKeyState`; loop t += Δ`timeGetTime`
  / 1000, z = z₀ + scale·t − t·scale·t·0.5 (ends when negative), returns if eye z minus
  `FindGroundBelow` (`0x00415f40`, via `0x00416000`) < `+0x5c` or `HasHeadroom` fails,
  slides, sets the position, `Scene_RunFor(0)`; at the end clears velocity, mode and
  `+0x50` and sends WM_KEYUP. `Camera_Crouch` (`0x004191e0`): mode 4, offset
  `scale·0.5 + 3 − r − 1`, height `scale·0.5 + 3`, `Camera_MoveTo(1000)` down by the height
  difference; loop until Numpad 0 is up and `HasHeadroom`, then `Camera_MoveTo(2000)` up and
  restore. `HasHeadroom` (`0x0041a3f0`): segment eye → eye + (0,0,10000), lowest hit, true if
  ≥ 0.4·scale above. `CheckDebugCode` (`0x0041b780`), called on every WM_KEYUP, matches
  `XHELP` (`0x004417d0`) and sets game `+0x16c`, which gates Insert (`+0x70` toggle), the
  Ctrl debug keys in `Camera_HandleKeys` and the overlay `FUN_0041c690` in
  `Scene_RenderFrame`.
- **Method:** MCP decompile.
- **Confidence:** proven.

### E-0050 — Scripted camera moves are frame-counted lerps; U01 hands over with movement disabled until `TakeCard`
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `Camera_MoveTo` (`0x00419860`): 100.0 (`0x00439444`) means keep yaw
  (`+0x34`), pitch (`+0x38`), FOV (`+0x10`); N = ftol(ms · scene `+0x144` · 0.001
  (`0x00439908`)), minimum 1; angles `fmod`-reduced, +2π when negative, short way; per
  frame adds the deltas, `+0x24` tick, `Scene_RenderFrame`, `FUN_0041bf30`, pump; then sets
  the targets. `FUN_00419bc0` / `FUN_00419c00` turn toward an object's global position.
  `U01_Start` (`0x00401230`) after E-0041: `Scene_RunFor(1500)`, app `+0x484` = 0,
  look at `TETE` (`0x0043f0a8`) 1000 ms, `MoveTo(2500, (−405.67, −494.31, 29.5), 2.9)`,
  `MoveTo(800, (−468.4, −481.3, 29.5), 1.76)`, voice wait (Enter), `RunFor(1000)`,
  `_U01_03`, look at `TETE` 1000, `RunFor(400)`, `MoveTo(1400, (−466.36, −452.495, 30.48),
  4.7)`, `MoveTo(1800, same, 4.7, 1.4908, fov 45)`, camera-animation wait (Enter),
  `MoveTo(600, current, keep, π/2, saved fov)`, `GiveCard`, camera `+0x40` = `+0x44` = 0,
  app `+0x484` = 1. `0x00401d30` (referenced from `0x00439400`) on action `TakeCard`
  (`0x0043f224`) calls `0x00401fb0`, which waits for an animation and sets `+0x40` = `+0x44`
  = 1 (`0x00402020`, `0x0040202d`).
- **Method:** MCP decompile; floats decoded with Python.
- **Confidence:** proven for the sequence and constants; the animations' content is not
  covered.

### E-0051 — Hover picks through `X3d_Scene_Pick_Object` within 4 · scale; clicks are rate-limited and dispatched by action name
- **Binary/file:** `MissionMonet.exe`, `x3d.dll`.
- **Evidence:** WM_MOUSEMOVE → `App_OnMouseMove` (`0x00417ca0`) → scene `+0x38` → `+0x44`
  `Scene_PickHover` (`0x0041b540`); WM_KEYUP also calls `+0x44` at `GetCursorPos` /
  `ScreenToClient`. `Scene_PickHover`: `X3d_Scene_Pick_Object(scene, x, y, &obj, &dist)`
  (delegates to the renderer object's vtable `+0xc`, `x3d.dll` `0x100016c7`); no pick if
  dist > scene `+0x138 · 4`; `FUN_0041b6a0` walks parents (`+0x20`) to a name containing `$`
  and looks the rest up in the hotspot list (`+0x1a0` vtable `+0x14`); `FUN_0041b600` sets
  the cursor. WM_LBUTTONDOWN → `App_OnLButtonDown` (`0x00417c10`): needs app `+0x480` and
  `+0x47c` = 0 and ≥ 1000/fps + 10 ms since the last click (app `+0x490`), then scene
  `+0x30`; U01's is `U01_DispatchClickActions` (`0x00403340`): `FUN_0041b700` (hover, then
  queue the hotspot's action), then drain the queue comparing names (`ClickControleur`,
  `ClickGuichetier`, …, `MonterDansTrain`).
- **Method:** MCP decompile; capstone read of the window procedure.
- **Confidence:** proven for the flow; picking internals and hotspot data are open (Q-0024).

### E-0052 — LODs pair two object hierarchies child by child; the renderer picks by squared distance
- **Binary/file:** `x3d.dll`, `xd3d.dll`.
- **Evidence:** `X3d_Load_Sdk_o3d` (`0x10001302`) returns the file's first object (the
  `*param_3 = *piStack_38` after `X3d_Scene_Add_Object`). `FUN_10012920` appends each
  object to its parent's child list (`+0x24` first child, `+0x28` next sibling) in file
  order. `X3d_Object_Add_Lod(base, lod, scene, d)` squares d (negative → 0), and when the
  base's transform block `+0` is 0 walks both child lists in step, calling
  `FUN_100152c0(child, lodChild, scene, d²)` (recursing the same way, doing nothing when
  either is null), unlinks the LOD object from the scene and inserts it in the base's
  LOD chain `+0x3c`, sorted by its threshold `+0x38`. The object class method table
  (`FUN_1000b690` fills `0x1002d144`) has `+0x14` = `FUN_10015200`: with s = squared
  distance from the object's global position (`+0xfc` → `+0x124..0x12c`) to the camera
  position (camera `+0x2c..0x34`), it returns the chain entry with the largest threshold
  ≤ s, else the object itself. `xd3d.dll` `FUN_10020720` draws the returned object's
  faces.
- **Method:** MCP decompile of the functions named; functions created at `0x10015200`
  and `0x10019730`.
- **Confidence:** proven for pairing and selection. That the chosen LOD object uses its
  own world matrix is inferred (the draw call passes both objects).

### E-0053 — A second U01 viewpoint matches the original; the original's camera can be read live
- **Binary/file:** `MissionMonet.exe` (running, x3d proxy with the data-export fix); engine
  `x3d` with `start_camera`.
- **Evidence:** `tools/proxy/camera.ps1` reads `[0x00442640]` (current scene) → `+0x14c`
  (camera) → `+0x14` position, `+0x34`/`+0x38` angles (E-0041's setters). At the
  post-intro hand-over it prints `-466.36,-452.495,30.4799728,4.7,1.570796`, the free-roam
  state E-0050 derives statically. Rendering the engine from that camera gives the same
  wall, wire, sheds, barrels and red carpet on the same pixels as the original
  (`traces/u01-mayor-compare.png`, local). The mayor (a weld object with an animation) is
  garbled in the engine: Q-0020.
- **Method:** ReadProcessMemory from PowerShell; snap.ps1 of both windows.
- **Confidence:** proven for the static geometry and the camera reader.

### E-0054 — Welded objects: each owns a range of its hierarchy top's vertex array and transforms it with its own world matrix
- **Binary/file:** `x3d.dll`, `xd3d.dll`; `Data/**/*.O3D`.
- **Evidence:** `FUN_10011ea0` reads the object's first count into object `+0x44`, the
  flag into `+0x40`, and when the flag is set a u32 into `+0x48` and a count into transform
  block `+0`, which sizes `X3d_Object_Create_Vertex` (positions `+0x4c`, normals `+0x50`).
  `X3d_Object_Get_Number_Weld` returns transform block `+0`. `FUN_10012920`, after
  linking parents, gives every flagged object with a parent the `+0x4c`/`+0x50` arrays of
  `X3d_Object_Get_Great_Father` (its top ancestor). The object class methods (table
  `0x1002d144`, `FUN_1000b690`) `+0x1c` (`FUN_1001a280`, lighting) and `+0x24`
  (`FUN_1001d440`) process exactly vertices `+0x48 .. +0x48 + +0x44 − 1` of those arrays:
  `FUN_1001d440` calls `X3d_Vertex_Transformation` on them with the object's model-view
  (`+0xfc` → `+0x134` = global `+0xf4` × view, `FUN_10019730` case 0) into one
  screen-vertex buffer indexed by the same vertex numbers; `FUN_1001a280` transforms the
  same range with the global matrix and the normals with `X3d_Normal_Array_Matrice_Mult`.
  `xd3d.dll` `FUN_10020720` computes the matrices of an object's weld children
  (`+0` = 0 and `+0x40` ≠ 0) and recurses into them before drawing the object's faces,
  whose indices address the whole shared buffer. Corpus: `tools/parsers/o3d.py` now checks
  that in every hierarchy the ranges partition the top's array: 596/596 pass, 139
  hierarchies, 5,613 welded objects, and no welded object below the top has an array of
  its own. Geometry check on U01's characters (`U01_01`, `U01_02`, `U01_E`): transforming
  each vertex with its owner's load-time world matrix (E-0042) gives median / maximum face
  edge 2.6 / 14.1, 2.5 / 13.5, 2.6 / 17.8 units; with the top object's matrix for all (the
  static view's rule) 3.4 / 35.1, 4.4 / 40.6, 3.1 / 35.1. So stored vertices are local to
  their owning object.
- **Method:** MCP decompile of the functions named (functions created at `0x1001d440` and
  `0x1001a280`, the `+0x24`/`+0x1c` thunk targets); Python over `o3d.py` output.
- **Confidence:** proven. Resolves Q-0020; supersedes the "bind pose" rule for weld
  objects in `docs/engine-spec/scene.md` and the `vertex_*` names in `o3d.ksy` (now
  `own_vertex_count`, `welded`, `weld_first_vertex`, `weld_vertex_count`).

### E-0055 — `.A3D` tracks: TCB-spline or linear translation, linear scale, slerped absolute quaternions, written to the object's live transform
- **Binary/file:** `x3d.dll`, `x3dmp5.dll`; `Data/**/*.A3D`.
- **Evidence:** `FUN_10012ee0` reads, after name and parent, the pivot into animation
  `+0xb4..+0xbc` and three u32s into `+0x34`, `+0x38`, `+0x3c`, returned by
  `X3d_Animation_Get_Number_Frame`, `_Get_First_Frame`, `_Get_Last_Frame`. Tracks are
  count, flags, frame numbers, 5 f32 per key (stride `0x14`), values; allocation error
  strings name them "translation" (`+0x40`), "scale" (`+0x54`), "rotation" (`+0x68`),
  "Hide" (`+0xa0`, one u32 per key at `+0xb0`) and "morph" (`+0x7c`: inner count `+0x8c`,
  then per key positions `+0x90`, normals `+0x94`, 4 f32 at `+0x98` and 6 f32 expanded to
  8 box corners at `+0x9c`). Children are appended to their parent's `+0x24`/`+0x28` list
  in file order. `X3d_Object_Animate(obj, anim, frame, usePivot, recurse)` and
  `_Animate_Spline` run five samplers, then set the live pivot (transform `+4`) from the
  animation's pivot (usePivot ≠ 0) or the object's init pivot `+0x14`, and set the dirty
  flag `+0x174`. Translation → transform `+0x34` (linear `FUN_10003430`; spline
  `FUN_10002d90`: Hermite with tangents from `FUN_10002410` using key floats 0..2 as
  tension/continuity/bias, and an ease remap using key j's float 3 and key i's float 4).
  Scale → `+0x54` (linear `FUN_100038a0`, both variants). Rotation → `X3d_Quaternion_Slerp`
  then `X3d_Quaternion_To_Matrice` into `+0x74`, also copied to `+0xb4` (`FUN_10003ce0`,
  both variants). Hide → object `+0x5c` = key i's u32 (`FUN_10004860`). Morph lerps the
  object's own vertex range and bounds (`FUN_10004310`). Key lookup (`FUN_10002780`,
  `FUN_10002870`): before the first key → key 0; at or after the last → the last key
  unless flags & 3 and the last frame ≠ 0 (wrap); else binary search. Recursion
  (`FUN_100031d0`, `FUN_10002940`, …) pairs the object's first child with the animation's
  first child, and siblings with siblings, by position. `FUN_1001dd30` builds the global
  matrix from exactly these live fields (`+4`, `+0x54`, `+0x74`, `+0x34` + `+0x24`, parent
  `+4`). `x3dmp5.dll`: `X3d_Quaternion_Set` stores (cos θ/2, axis · sin θ/2), so w is
  first; `X3d_Quaternion_To_Matrice` and `_Slerp` are written out in
  `docs/engine-spec/animation.md`. Corpus (`tools/parsers/a3d.py`): every file has one
  (frames, first, last) header shared by all its animations; all track flags are 0; no
  hide or morph keys; of 555,288 keys only 19,046 have a non-zero parameter, always
  float 1. In U01's 14 animated `.O3D`/`.A3D` pairs the hierarchies pair name for name;
  key 0 of `U01_01/ATTENTE` reproduces the `.O3D` matrices exactly with this
  quaternion-to-matrix rule, and every animation pivot equals its object's pivot. All
  13,950 `.O3D` matrices have a zero translation row.
- **Method:** MCP decompile of the functions named; Python over the parser output.
- **Confidence:** proven. Supersedes the track D/E layouts of `a3d.ksy`/`a3d.py` (hide:
  one u32 per key, not two; morph: per-key blocks with 10 floats, not 7 once); the parser
  never met them because no corpus file has such keys.

### E-0056 — The EXE binds `animation=` by name, advances frame += seconds × fps per rendered frame, and samples with `X3d_Object_Animate_Spline`
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** Scene vtable `+0x20` is `XSceneAnim::XSceneAnim_22` (`0x0041c170`, assert
  `XSceneAnim.cpp:22`): `X3d_Load_Sdk_a3d` (first animation of the file), then if the
  root's name contains `*` (`0x004417b8` is `"*"`, not `"$"` as E-0045 says) one node for
  (root animation, the `object=` object); otherwise one node per direct child of the root,
  bound to the object found by `FUN_0041b4c0` (depth-first over the object's children and
  their siblings, `FUN_00416180` with exact = 1: `_stricmp`). `FUN_0041c280` creates the
  node (`FUN_0041fc20`: name = object name, `+0x64` = 1, `+0x68` = 1, `+0x78` = 30.0) and
  `FUN_0041fe60(node, anim, obj, fps, loop 1, paused 0)` sets frame `+0x74` = first frame.
  Tick `FUN_0041c350` (vtable `+0x24`) → `FUN_0041fe90` over the node tree (`+0x50`
  child, `+0x5c` next): for a node with an object and an animation, if sub-slot `+0x1ca`
  is set play that slot's node instead; else if `+0x64`: advance unless paused (`+0x60`,
  `FUN_0041ff20`), then `X3d_Object_Animate_Spline(obj, anim, frame, 0, 1)`.
  `FUN_0041ff20`: ping-pong `+0x6c` flips direction `+0x70` at the ends; frame ±=
  `DAT_0046ebe0 · fps`; not looping: clamp to [first, last], and without ping-pong set
  paused; looping (`+0x68`): above last → `fmod(frame, last) + first` (capstone
  `0x0041ff90..0x0041ffad`), below first → `last − (first − frame)`; stop target
  (`+0x1d8`/`+0x1d4`): within 2 · dt · fps → frame = target, paused. `Scene_RenderFrame`
  stores `DAT_0046ebe0` = (counter − previous) / frequency, the seconds between the last
  two presents (capstone `0x0041b285..0x0041b29a`, beside the fps of E-0046). Other
  entry points: `X3d_Object_Animate_Transition` has one caller (`FUN_00406f90`, not U01);
  the tick also runs `FUN_00421b90` (scene `+0x168`) and `FUN_00420e00` (list `+0x1a0`,
  multiplies an object's local matrix by a stored one when `+0x6c` is set).
- **Method:** MCP decompile; capstone reads of the x87 code.
- **Confidence:** proven for binding, clock and sampling call. What `+0x168` and the
  `FUN_00420e00` list animate is open (Q-0026).

### E-0057 — U01's scripted animations: `_U01_03` unpauses a node; `GiveCard` plays U01_02 `Action03` once in slot 1; `TakeCard` plays it back to frame 1
- **Binary/file:** `MissionMonet.exe`; `Data/U01/Anim/**`.
- **Evidence:** `U01_Start` (EBX = 0 from `0x00401240`): at `0x004015ca` finds the node
  named `*U01_03` (`0x0043f0a0`) through node list vtable `+0x14(name, 1)` and calls
  `FUN_00420060(node, 0)`: `+0x60` = 0 (running). At `0x00401708..0x0040172f`:
  `FUN_00420220(unit +0x6d0, "%sAnim/U01_02/Action03.A3D", "GiveCard", 1, 1)`, then that
  node's loop `+0x68` = 0. `FUN_00420220` makes a node (type `0x32`), loads the whole file
  with `XAnimation::XAnimation_55` (assert `XAnimation.cpp:55`) on the parent node's
  object with its fps, loop and paused values, and `FUN_004202f0` puts it in slot 1 of the
  parent (`+0x188[1]`; slot 0 = the parent itself; count `+0x1c8`), running, and makes it
  the active slot `+0x1ca`. `0x00401fb0` (TakeCard): slot 1's direction `+0x70` = 1,
  `FUN_00420100(slot1, 1.0, 1)` (running until frame 1.0), `Scene_RunFor(0)` until
  paused, then `FUN_004201c0(parent, 0, 1)` (active slot 0, running) and
  `FUN_004200c0(slot 0, 1.0)` (frame := 1.0 clamped to [first, last]), then enables
  movement (E-0050). Corpus: `U01_02/ACTION03.A3D` frames 1..25, keys 0..23;
  `U01_02/ATTENTE.A3D` 1..100, keys 0..90; `U01_01/ATTENTE.A3D` 1..10 with keys at 0 and
  1 only; `U01_03.A3D` 1..30.
- **Method:** MCP decompile and disassembly of the functions named; parser output.
- **Confidence:** proven for the calls. That unit `+0x6d0` is the node of `U01_02` is
  inferred from the file it plays; who pauses `*U01_03` before `U01_Start` is open
  (Q-0026).

### E-0058 — Camera type 2 (`$Z$`) keeps the camera's pitch and fixes its yaw at π/2
- **Binary/file:** `x3d.dll`.
- **Evidence:** `FUN_10019730`'s jump table (`0x10019e30`) sends type 2 to `0x10019975`.
  With camera `+0` = 0 (`0x100199d6..0x100199e0`), `0x100199e2..0x10019a4c` loads π/2
  (double at `0x10024098`) as the yaw and camera `+0x58` (the pitch e of E-0040) as the
  pitch, and fills the view rotation of E-0040 with them; with camera `+0` ≠ 0 the pitch
  comes from `X3d_Convert_To_Polar` of the normalised target − position. Roll (`+0x4c`)
  and projection follow as for the normal view; the object's origin in the true view
  (global × view, row 3) is stored at transform `+0x164..+0x16c`.
- **Method:** capstone disassembly by hand; MCP decompile.
- **Confidence:** proven for the angles. How the renderer places the object with
  `+0x164` is not read (Q-0021).
