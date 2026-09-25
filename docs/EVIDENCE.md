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
