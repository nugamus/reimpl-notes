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

### E-0070 — `X3d_Scene_Pick_Object` is a screen-space polygon test over front faces of visible, in-frustum objects; the distance is camera-space depth
- **Binary/file:** `x3d.dll`, `xd3d.dll`.
- **Evidence:** `X3d_Scene_Pick_Object` (`x3d.dll` `0x100016c7`) returns 0 when the
  renderer table (scene `+0x4c`) has no `+0x70`, else calls its `+0xc`, the rasteriser's
  `X3d_Pick_Dll` (the name is among the `_Dll` strings `x3d.dll` resolves, `0x10028c24`).
  `X3d_Pick_Dll` (`xd3d.dll` `0x1000129e`): builds the camera matrix (camera `+100`
  method), sets *dist = scene `+0x30` (far; `X3d_Scene_Init_Resolution` stores near
  `+0x2c`, far `+0x30`, viewport centre `+0x3c`→`+8/+0xc` = origin + size/2, half size
  `+0x10/+0x14`), object = 0, and walks the top-level list (`+0x2c`) with `FUN_10021970`,
  recursing children `+0x24` and siblings `+0x28` (`FUN_10021760`) whatever the parent's
  outcome. An object is tested when object `+0x40` (weld flag, E-0054) and `+0x114` are 0;
  weld tops go through `FUN_100213f0`, which tests the top's faces (the shared weld mesh)
  and reports the top. Per object: class methods `+0x10` (camera type), `+0x14` (LOD,
  E-0052), `+0x18` = `FUN_1001a010`: `+0x60` = 0 when hidden (`+0x5c`), else 1 if any
  bounding-box corner (`+0x68`, `+0x7c..`) is inside all six planes (near, far, ±x ≤ z,
  ±y ≤ z) or the box straddles all of them; `+0x11c` forces 1. Only `+0x60` objects are
  tested. Per face: face class `+0` (`FUN_1000b040` / `FUN_1000b180`, x3d `0x1000118b` /
  `0x1000106e`) is 1 when face `+0x38` = 0 and n · v0 < −0.01 with
  n = (v0 − v1) × (v2 − v1) in camera space (the second variant retries later vertex
  triples). `FUN_1001efa0`: outcode AND/OR over the six planes rejects faces outside one
  plane; near/far clipping (`FUN_10010250`, `FUN_10010660`); projection
  sx = cx + fx · X/Z, sy = cy − fy · Y/Z; bounding-box test, then every edge
  (y − sy_i)(sx_{i+1} − sx_i) + (x − sx_i)(sy_i − sy_{i+1}) ≤ 0; depth
  d = (m · v0) / (m · ((x − cx)/fx, (cy − y)/fy, 1)), m the unit normal. The smallest d
  wins; the reported object is the base object, not its LOD. The EXE passes client pixel
  coordinates as floats (`Scene_PickHover`, `0x0041b540`).
- **Method:** MCP decompile of the functions named; `X3d_Scene_Init_Resolution` decompile.
- **Confidence:** proven for the traversal, tests and depth. Face `+0x38` and which face
  variant is installed are open (Q-0040).

### E-0071 — `#ACTIONS#` (INFOACT.BIN) is `u32 count` + 0x440-byte action records; 9/9 parse, 198 records
- **Binary/file:** `MissionMonet.exe`; `Data/U##/INFOACT.BIN` (9 files).
- **Evidence:** `Scene_LoadActions` (`0x0041da90`, was `FUN_0041da90`) opens
  `%s%s` of the unit path and `INFOACT.BIN` (`0x00441c1c`), seeks `ACTIONS`
  (`0x00441c14`), reads a u32 count and `count * 0x440` bytes, and per record (base r)
  looks up hotspots named at r + 0x150 and r + 0x174 in the list (scene `+0x1a0`, vtable
  `+0x14`), then `FUN_0041e020(10, id r+0, name r+4, trigger r+0x128, item r+0x12c,
  hotspot_type r+0x14c, hotspot, target_type r+0x170, target, condition r+0x22,
  max_runs r+0x124, step_count r+0x194, steps r+0x198)`; the constructor copies
  `step_count` steps of `u32` + string, stride 0x44. So 30 bytes of name, 258 of
  condition, 10 steps of 68 bytes (0x198 + 0x2a8 = 0x440).
- **Method:** MCP decompile; `python tools/parsers/infoact.py` → 9/9 files, 198 records,
  every byte consumed, `--selftest` (truncated chunk, step count 11 rejected).
- **Confidence:** proven for the layout. Resolves the `#ACTIONS#` part of the open
  `.BIN` payloads.

### E-0072 — INFOOBJ.BIN entries are the unit's hotspots: name[40], type, cursor, visible, animation frame/paused/fps/loop; the hover marker is `*`
- **Binary/file:** `MissionMonet.exe`; `Data/U##/INFOOBJ.BIN`.
- **Evidence:** the unit vtable `+8` (U01 `0x00402a30`) calls `FUN_0041d490`, which with
  no reader opens INFOOBJ.BIN, calls `Scene_LoadObjectInfo` (`0x0041d8e0`) and
  `Scene_LoadActions`. `Scene_LoadObjectInfo` reads `OBJECTS`, and per 0x44-byte entry
  finds the object named by the entry (`FUN_0041b440`, exact: `X3d_Scene_Get_Object`, then
  depth-first `_stricmp`), copies the entry name over the object name (a full C string,
  so the name field is 40 bytes up to `+0x28`), finds or creates the hotspot
  (`FUN_00420b40(type = entry +0x28, ++scene +0x19c, object)`, added to list `+0x1a0`;
  the only caller of `FUN_00420b40`), and applies the entry with `FUN_004210d0`:
  object `+0x128` → cursor kind = `+0x2c`; `+0x30` = 0 → hide (hotspot vtable `+0x28`);
  the animation node named like the hotspot (list scene `+0x158`): `+0x38` = 0 →
  `FUN_004200c0(frame +0x34)` (set frame, clamped to the animation's first/last), else
  `FUN_00420100(frame, 0)` (paused, frame); node `+0x78` = (float) `+0x3c`; node `+0x68` =
  `+0x40`. `FUN_0041d6f0` writes the same fields back into a save's `OBJECTS` chunk
  (`FUN_00421170`). Hover `Scene_FindHotspotForObject` (`0x0041b6a0`, was `FUN_0041b6a0`)
  walks parents (`+0x20`) to a name containing `0x004417b8` = `"*"` and looks up the
  substring from `*` with `(name, 0)`: the list's find (`FUN_0041dea0`) matches by
  `FUN_00416180(node name, key, 0)` = `_stricmp` equal or upper-cased `strstr`, walking
  `+0x50`/`+0x5c`; on no match it continues from the parent. Op 1 treats target type 6 as
  a character (`Action_RunStep`, case 1). Corpus: U01 `*U01_03` has anim_paused = 1,
  `*U01_10` and `*Ernest` visible = 0.
- **Method:** MCP decompile of the functions named; `python tools/parsers/infoobj.py`
  (9/9, 183 entries, field names updated).
- **Confidence:** proven for the fields. The meaning of types 4 and 5 is only observed
  (takeables / fixtures in U01). Supersedes E-0026's opaque fields and the "reserved
  32 bytes overwritten by a pointer" reading, and E-0051's `$` marker (it is `*`).

### E-0073 — A click triggers the hotspot's first runnable INFOACT action; steps are data, op 10 hands a name to the unit's C++
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `FUN_0041b700` (after hover) calls `Actions_TriggerForHotspot`
  (`0x0041e3f0`, was `FUN_0041e3f0`) when a hotspot is hovered and scene `+0x13c` ≠ 0
  (`U01_Start` writes 0 at `0x004014ac`, 1 at `0x00401767` right after the hand-over).
  Kind = 7 with the held item's name when the cursor mode is 1 or 2, else 8.
  `FUN_0041e180` → `FUN_0041e240` walks the action list (`+0x50`) for the first action with
  `+0x64` (hotspot_type) = hotspot `+4` and hotspot name equal to / containing the clicked
  one, then that action's `+0x5c` chain (same hotspot, appended in file order by
  `FUN_0041dfe0` via `FUN_0041e900`) for `+0x60` = kind, runnable (`FUN_0041e2e0`:
  exhausted flag table `+0x410[id]` = 0 and `EvalActionCondition` (`0x00415b80`) true)
  and, for 7, `_stricmp(item, held)` = 0. `FUN_0041e4b0` runs each step
  (`Action_RunStep`, `0x0041e500`) then `FUN_0041e320`: run count `+0x810[id]` += 1;
  if `max_runs` < 100 and count ≥ max_runs, `FUN_0041e3a0` sets exhausted `+0x410[id]` = 1.
  `EvalActionCondition` lower-cases; `t` → 1, `f` → 0, `m`/digits/`!m` read an index
  (`FUN_00415ad0`) into the exhausted table, `&`, `|`, `(`…`)` combine. Steps: 1 voice
  (`FUN_004215f0` for a type-6 target found in scene `+0x164`, else scene vtable `+0x48`
  at the hotspot position, `%sSound/%s.WAV` or `%sSound/%s` if the name has `.wav`); 2
  `FUN_004211d0` (cursor kind 0, hide, cursor item = name chars 1..6 + `C`,
  `FUN_00414540(cursor, 1, …)`); 3 `FUN_004212b0`; 4 node `FUN_00420060(node, 0)`;
  6 `Scene_RunFor(atoi)`; 7 `FUN_00421300` (cursor kind = atoi); 9 hotspot vtable
  `+0x28(…, atoi == 0, 1)`; 10 `FUN_0041ebb0` (queue slot, 10 max, message "Cannot to add
  action into queue"); 12 vtable `+0x4c` (`FUN_0041bc00`, sound channel 1, assert
  `XScene.cpp:609`); 13 vtable `+0x50` (`FUN_0041bcf0`, positional, `XScene.cpp:628`);
  14 find by name and run if runnable; 15/16 condition := `TRUE`/`FALSE`
  (`FUN_0041e2a0`); 101 vtable `+0x54` (`FUN_0041be00`, channel 2 after stopping it,
  `XScene.cpp:651`). The unit's click handler drains the queue and matches names with
  `FUN_0041e940` (`_stricmp` against each step argument).
- **Method:** MCP decompile; functions created at `0x0041baf0`, `0x0041bc00`,
  `0x0041bcf0`, `0x0041be00`, `0x0041dfe0`, `0x0041df60`; U01 action list from
  `infoact.py --file Data/U01/INFOACT.BIN`.
- **Confidence:** proven. Resolves Q-0024 with E-0070, E-0072, E-0074.

### E-0074 — Cursors are 20×20 bitmap resources of the EXE, white-keyed, with per-kind hotspots; held items blink over "use" hotspots
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `XCursor_LoadCursors` (`0x00414250`) calls `XCursor::XCursor_63`
  (assert `XCursor.cpp:63`) for kinds 0..13: `Cur_default.BMP` (0, 0), `CUR_WAIT` (9, 2),
  `CUR_CLIC` (9, 2), `CUR_VOICE` (10, 10), `CUR_TAKE` (10, 4), `CUR_USE` (10, 10), then
  `LOUPEB`, `LOUPED`, `LOUPEDB`, `LOUPEDH`, `LOUPEG`, `LOUPEGB`, `LOUPEGH`, `LOUPEH`
  (10, 10), stored at cursor `+0x84 + 0x30·i` with the pair at `+0xa4/+0xa8`. The loader
  `FUN_004156a0` uses `LoadImageA` on the EXE module first (file only as fallback), and
  `pefile` lists these names as `RT_BITMAP` resources (plus unused `CUR_DROP.BMP`), all
  20×20 24-bit. Surfaces get colour key 0xFFFFFF (`FUN_004159c0`); `FUN_00414670` draws
  mode 0 as a 20×20 color-keyed blit at (`+0x70`, `+0x74`) = cursor − pair
  (`FUN_00414890`), mode 1 a 32×32 item image at cursor − (16, 16). Hover
  (`FUN_0041b600`): mode 0 → kind = hotspot object `+0x128` or 0; mode 1 over a hotspot
  of kind 5 → two animation frames (item, none) at 6 per second (`FUN_00414a30`,
  `FUN_00414b60(…, 6)`, mode 2); mode 2 off such a hotspot → back to mode 1
  (`FUN_00414ba0`). Corpus: `Data/2dbit/` has `U01_04C/05C/08C/12C/19C.BMP` (32×32, white
  background) for U01's five take targets.
- **Method:** MCP decompile; `pefile` resource walk.
- **Confidence:** proven for the table, resources and drawing; the item image's loader
  (cursor manager `DAT_0046edc8` vtable `+0x18`) is not read (Q-0041).

### E-0075 — Unit classes come from a switch on the unit number; U01's vtable is `0x004393d0`, and `0x00403340` / `0x00402f70` belong to U02
- **Binary/file:** `MissionMonet.exe`; `Data/U02/INFOACT.BIN`.
- **Evidence:** `CreateUnitScene` (`0x00417f10`..) indexes byte table `0x004181d0` by the
  unit number (0..50) into jump table `0x004181a4`: 0 → `FUN_004097e0`, 1 →
  `FUN_00401000` (stores vtable `0x004393d0`), 2 → `FUN_00402af0` (vtable `0x00439468`),
  3 → `0x00404e70`, 4 → `0x0040a720`, 5 → `0x0040ece0`, 6 → `0x00410940`,
  7 → `0x004112b0`, 33 → `0x00407090`, 50 → `0x004123c0`, others `0x0041a890`.
  U01's vtable: `+0x8` `0x00402a30`, `+0x14` `U01_Start` (`0x00401230`), `+0x1c`
  `0x004017a0` (calls `Scene_RenderFrame` first), `+0x30` `U01_DispatchClickActions`
  (`0x00401d30`, function created), `+0x40` `0x00401940` (calls `Scene_HandleInput`
  `0x0041b7f0`), `+0x44` `Scene_PickHover`, `+0x48..+0x54` the sound methods of E-0073.
  `0x00401d30` compares `TakeCard`, `ClickMaire`, `OpenDoor`, `CloseDoor`,
  `TakeCarteHorloge`, `OpenBoitier`, `BaisserManette`, `ClicTel`, `OpenTiroir1`,
  `OpenTiroir2`, `MonterSurToit`, `DoInterrupteur` (the op-10 names of U01's INFOACT),
  while `0x00403340` compares `ClickControleur` … `MonterDansTrain`, the op-10 names of
  `U02/INFOACT.BIN`. Renamed `U02_DispatchClickActions` and `U02_UpdateFrameLogic`.
- **Method:** capstone of `CreateUnitScene`, MCP xrefs, `infoact.py --file`.
- **Confidence:** proven. Supersedes the U01 attribution of `0x00439468`, `0x00402f70` and
  `0x00403340` in E-0046 and E-0051; the loop structure they describe holds for U01 with
  the addresses above.

### E-0059 — Walking, the collision stop and the wall slide match the original to within key-timing jitter
- **Binary/file:** `MissionMonet.exe` (x3d/h3d proxies, background mode, dgVoodoo capped at
  60 fps); engine `x3d` at "X3D: Walk, turn and collide in U01" (60 logic steps/s).
- **Evidence:** from the hand-over state (−466.36, −452.495, 30.48, yaw 4.7) after
  `TakeCard`, the same posted key holds give, original vs engine
  (`tools/proxy/camera.ps1`; engine `-d1` log):
  Down 1 s → (−465.85, −493.37, 29.546) vs (−465.85, −493.45, 29.546);
  Down 2 s more, stopped by collision → (−464.859, −508.173) vs (−464.852, −508.168);
  Left 1 s → yaw 1.10 vs 0.92 (3.60 vs 3.78 rad: 60 vs 63 steps of 0.06; the posted hold
  lasts ~1.0–1.05 s); Up 2 s along a wall → Δy ≈ 0 in both, Δx = 36.75 vs 48.85, each
  = 40 units/s (half speed, face ahead within 2r) · 2 s · cos(yaw). The original turned
  0.06 rad per rendered frame at dgVoodoo's 60 fps cap. `traces/u01-walk-compare.png`
  (local).
- **Method:** `tools/proxy/to_u01.sh`, `send.ps1` click on the card (game coordinates
  (262, 338)), `send.ps1 -Key` holds on both programs.
- **Confidence:** proven for speeds, ground snap and the collision stop; the turn rate per
  second depends on the frame rate (Q-0022).

### E-0060 — U01's constructor hides `Box203` and `Cylinder07`
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** in the U01 constructor, `0x00401159` pushes `Box203` (`0x0043f044`) for a
  scene lookup whose result goes to `X3d_Object_Hide` at `0x00401181`; `0x0040118c` pushes
  `Cylinder07` (`0x0043f038`), hidden at `0x0040119e` (`push 1`). The trace of a U01 run
  shows `X3d_Object_Hide` from `0x00401183` and `0x004011a0` (return addresses).
- **Method:** capstone read with the pushed strings resolved; proxy trace.
- **Confidence:** proven. (`Box203` also loses collision, E-0048.)

### E-0061 — Welded skinning and `.A3D` playback reproduce the mayor's pose
- **Binary/file:** engine `x3d` at "X3D: Play .A3D animations and pose welded characters";
  the original after `TakeCard`.
- **Evidence:** at the hand-over camera the mayor's body, sash, arms and head fall on the
  same pixels in both (`traces/u01-mayor-posed-compare.png`, local); before skinning the
  same mesh was garbled (E-0053). A diagonal wire from the pole top, left of the mayor,
  is drawn by the engine only; it is neither `Box203` nor `Cylinder07` (Q-0021).
- **Method:** `snap.ps1` of both windows.
- **Confidence:** proven for the pose at that moment.

### E-0062 — Drawing `$Z$` objects as camera-facing about their origin leaves U01's first shot unchanged
- **Binary/file:** engine `x3d`, U01 first shot (E-0041).
- **Evidence:** with type-2 objects drawn per E-0058 (offsets from the object's origin
  rotated by the yaw-π/2 view instead of the camera's, the origin placed by the true
  view), the sun disc stays on the same pixels as the original and the boat hulls only
  widen slightly: the boats still show where the original shows none. So their absence in
  the original is not the camera type.
- **Method:** engine render with `start_camera=-258.44,-508.20,29.546,1.31,1.570796`
  beside `traces/u01-start-original.png`.
- **Confidence:** proven for this shot; how the renderer uses `+0x164` stays inferred.

### E-0076 — A pick on a welded object's face reports that object, not its hierarchy top
- **Binary/file:** `Data/U01/Anim/U01_02/U01_02.O3D`; `MissionMonet.exe` (running).
- **Evidence:** the mayor's card `*U01_04` is a welded child (`welded` 1, no own vertices,
  2 faces) of `mainG` under `*U01_02`, the hierarchy top holding the 426-vertex array
  (`tools/parsers/o3d.py`). Clicking the card in the original at game (262, 338) runs
  INFOACT M02 on hotspot `U01_04` (`TakeCard`, E-0059's run). If the pick reported the top
  (`*U01_02`, E-0070's reading), the hover walk would find hotspot `*U01_02` and M02 could
  never run. The engine, reporting the face's own object, picks `*U01_04` at depth 22.6
  there and the same action follows.
- **Method:** parser dump; engine `-d2` log with `dev_click=262,338,3000`.
- **Confidence:** strong (behavioural). Supersedes the "hit is reported for the top" clause
  of E-0070; the rest of E-0070 stands.

### E-0120 — The sound manager: one DirectSound device, 22,050 Hz 8-bit mono primary, groups 1..6, volume = v · G in hundredths of a dB
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** the manager constructor `FUN_00422d70` (called at `0x00426667` with
  1, 22050, 8, 1000000, 6) stores channels/rate/bits, sets the streaming buffer size
  `+0x2c` = 1000000 / 6 and zeroes the six group attenuations `+0x30..+0x44`; the global
  is `0x0046ec54`. `LSoundManager_99` (`0x00423020`, assert `LSoundManager.cpp:99..154`):
  `DirectSoundCreate`, `SetCooperativeLevel(hwnd, 2)` (priority), a primary buffer set to
  PCM 1 channel, `+0x1c` Hz, `+0x20` bits, played looping, and `timeSetEvent(500, 300,
  0x00423840, 0, periodic)`. `LSoundManager_290` (`0x004233a0`, `:290..311`): group ≤ 6
  (assert `:0x122`), new `LSound` (0x17c bytes), `LSound_72` with the group's attenuation
  `+0x2c + 4·group` and the buffer size. `LSound_72` (`0x00421e80`, `LSound.cpp:72`):
  `+0x118` = loop, `+0x11c` = remove-when-done, `+0x120` = pan capable, `+0x10c` = group,
  buffer = size rounded down to the block align, **static** (`+0x130` = 1, whole file)
  when the data is smaller, caps `0x10080` (+`0x40` with pan, +2 static); then volume
  `LSound_469`, pan `LSound_574` only if either pan value ≠ 100, and plays if asked.
  `LSound_469` (`0x004228c0`, `:469..483`): v in 0..100 (assert), DirectSound volume =
  −((−10000 − G) · 0.01 · v + 10000) (constants `0x00439a80` = 0.01, `0x00439a78` =
  10000.0, capstone). `LSoundManager_413` (`0x00423620`): group volume V in 0..100 →
  G = (V − 100) · 100 (`fsub 100.0` at `0x0042368e`, ×100 by `lea`), re-applied to every
  sound of that group (`FUN_004229b0`); `LSoundManager_397` reads it back as 100 + G/100
  (`0x00439ab0` = −0.01). Hence volume = v·V − 10000 hundredths of a dB. `LSound_574`
  (`0x00422a70`): pan = 100·(R − 100) when L = 100, else |100·(L − 100)|; every call site
  in the EXE passes 100, 100.
- **Method:** MCP decompile; capstone for the x87 constants; `pefile` reads of the doubles.
- **Confidence:** proven.

### E-0121 — Group assignments and per-call-site sound parameters
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `SetAppMode` (`0x00417ce0`): on a change to mode 2, `LSoundManager_413`
  groups 1, 4, 5 → 0; on any other change → 85, 80, 80. Call sites of
  `LSoundManager_290` (path, loop, remove, pan, group, play, v, 100, 100): scene vtable
  `+0x4c` `FUN_0041bc00` (step 12, `XScene.cpp:609`): (loop = caller, 0, 0, 1, 1, 85);
  `Action_RunStep` (`0x0041e500`) case 12 passes loop 1. `+0x54` `FUN_0041be00` (step 101,
  `XScene.cpp:651`): `LSoundManager_StopGroup(2)` (`0x00423360`), then (caller, 1, 1, 2,
  1, v = caller), and zeroes the voice emitter's sound pointer; case 101 passes (0, 100).
  `SoundEmitter_Play` (`0x00414ce0`): (loop = caller, 1, 1, emitter group, 1, 100).
  `PlayVideo` (`0x00417030`): `FUN_004232d0` (stop all) then (0, 1, 1, 2, 1, 100).
  U03's `FUN_00407b80`: group 4, v 85 and 90. `U01_Start` calls vtable `+0x4c("U01", 1)`
  at `0x004013ed` (a ≠ 0, after the prologue) and `0x0040126a` (save load).
- **Method:** MCP decompile; capstone scan of U01's vtable calls (`0x00401000..0x00403000`).
- **Confidence:** proven.

### E-0122 — Two positional emitters: voice (group 2, 50·s) and effects (group 3, 60·s); volume falls linearly with distance to the eye
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** scene load at `0x0041ac1e..0x0041accb`: two 0x128-byte emitters
  (`FUN_00414c80(group, range)`: `+0x120` group, `+0x124` range) with range = scene
  `+0x138` × 50.0 (`0x00439448`) for group 2 → scene `+0x178`, × 60.0 (`0x00439440`) for
  group 3 → scene `+0x174`; they are also listed at scene `+0x17c`, `+0x180`.
  `SoundEmitter_Play`: if `FUN_00414ed0` (group playing) and `_stricmp(last name, file)`
  = 0 return 0; copy the position to `+8`, stop the group, play, store the handle `+4` and
  the name `+0x18`, then `SoundEmitter_SetDistance` (`0x00414e40`) with `FUN_00415e40`
  (Euclidean distance) to camera `+0x14`. `SoundEmitter_SetDistance`: d < range →
  v = ftol(100 · (range − d) / range) (capstone `0x00414e60..0x00414e76`), else 0;
  clamped 0..100; `LSound_469`. `Scene_UpdateEmitterVolumes` (`0x0041bf30`) walks the
  (up to 7) emitters at scene `+0x17c` and, for those whose group plays and which hold a
  handle (`FUN_00414e00`), recomputes; it is called from `FUN_00418fd0` (after each walk
  key step, E-0047), `Camera_MoveTo` (each frame) and `FUN_00419620` (camera path, each
  frame). Scene vtable `+0x48` `FUN_0041baf0` (`XScene.cpp:0x250`) plays on the voice
  emitter, `+0x50` `FUN_0041bcf0` (`:628`) on the effects emitter; `Camera_Fall` plays
  `SAUT.WAV` through the effects emitter at camera `+0x14` (`0x004194d2`).
- **Method:** capstone of the scene loader; MCP decompile; float constants read with
  `pefile`.
- **Confidence:** proven.

### E-0123 — "Group playing" means a sound of the group without its end flag; streamed sounds raise it up to half a buffer early; a 500 ms thread polls
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `LSoundManager_IsGroupPlaying` (`0x00423310`): any listed sound with
  `+0x10c` = group and `+0x168` = 0. `LSound_185` (`0x00422090`, `LSound.cpp:185..254`)
  fills one half of the buffer (the whole buffer when static) from the file
  (`FUN_00423d70`); read 0 bytes → silence (0x80 for 8-bit, else 0) and `+0x168` = 1;
  a short read → loop set: seek to the data start (`FUN_00423d30`) and read the rest
  (capstone `0x00422257..0x004222e3`), else silence. `LSound_446` (`0x00422710`) is the
  per-sound poll: streaming → refill the half not playing once the cursor has left it, or
  stop (`LSound_378`) when `+0x168` is set; static → if not looping and remove-when-done,
  stop when DirectSound's status is 0. `LSound_378` with remove-when-done hands the sound
  to `FUN_00423540` (delete list). The timer callback `0x00423840` → `0x00423860` frees
  the delete list and calls each listed sound's poll. `LSound_317`: plays looping unless
  (not looping and static).
- **Method:** MCP decompile; capstone for the loop branch the decompiler dropped.
- **Confidence:** proven for the mechanism; the audible consequence is Q-0071.

### E-0124 — `Sound/<name>.bin` is a `#INDEX#` chunk of (u32 ms, u16 shape, u16 pad) records; 81/81 parse
- **Binary/file:** `MissionMonet.exe`; `Data/*/Sound/*.bin` (81).
- **Evidence:** `Talkers_Say` (`0x004215f0`) formats `%sSound/%s.bin` (`0x00441f5c`) and,
  if it exists, `Talker_LoadLipBin` (`0x00421960`): `FUN_00414f70` opens the container,
  `FUN_00415190(..., "INDEX")` (`0x00441fb8`), reads 4 bytes into talker `+0x220`
  (count; < 1 → done), allocates count·8 and reads them into `+0x224`. The lookup
  `FUN_00421a70` compares the elapsed ms with each record's first u32 and returns the
  previous record's second dword cast to a short. `tools/parsers/lip.py`: 81/81 files
  (all `Uxx/Sound/*.bin`), 10,373 records, every byte consumed, only `#INDEX#`; shapes
  1..8 (1 ×1,289, 2 ×914, 3 ×571, 4 ×1,608, 5 ×1,566, 6 ×971, 7 ×986, 8 ×2,468); pad
  0xCDCD in every record; first time 0 in all 81; time steps min 44, median 46 ms.
- **Method:** MCP decompile; validator.
- **Confidence:** proven.

### E-0125 — Talkers: eight mouth clips on the face dummy at 15 fps; lip mode follows the table with 200 ms spacing and random open shapes; random mode without a table
- **Binary/file:** `MissionMonet.exe`; `Data/U01/Anim/U01_01/*.A3D`.
- **Evidence:** `U01_Start` calls scene vtable `+0x28` (`XSceneAnim_157`, `0x0041c400`)
  at `0x004012a4` / `0x004012be` with `U01_01` / `$$$DUMMY.*01SParle` and `U01_02` /
  `$$$DUMMY.*02SParle`, count 8; it builds a talker (`FUN_00421360`: type-6 hotspot,
  face name `+0x174`, slots `+0x1b4`×9 = 0, current `+0x1dc` = 0) with anim dir
  `%sAnim/%s/` (`0x0043fee0`) and `FUN_00421480`: face object `+0x170` (under the
  character's object, else by scene name), then `FUN_004217b0` for `A` (slot 8), `B` 4,
  `Ch` 2, `Ch_yeux` 3, `E` 5, `F` 6, `O` 7, `Yeux` 1 (`0x00441f34..0x00441f58`): load
  `%s%s.A3D`, take the sub-animation named like the face (`FUN_0041c380`), make a node
  `<char>VISAGE` (`0x00441f6c`) bound to the face object at 15.0 fps (`0x41700000`),
  loop 1, running, then `+0x64` = 0, and append it to scene `+0x158`; empty slots and
  slot 0 get the first non-empty; `FUN_00421780` disables and pauses all. The A3D shows
  `$$$DUMMY.*01SParle` under `TETE` with the mouth, cheek, brow and eye objects below it.
  `Talkers_Say`: stop the current talker (`FUN_00421730`: all slots `+0x64` = 0, free the
  table, `+0x60` = 0, scene `+0x168` = 0); face global position → scene `+0x48`; if it
  started: scene `+0x168` = talker, load the table (`+0x1e4` = 1) or not, `+0x1e0` =
  `timeGetTime()`, `+0x60` = 1. `Action_RunStep` case 1 calls it for a type-6 target found
  in the talker list; `U01_Start` at `0x004014ce` for `U01_01` / `d1_01`. The animation
  tick (`FUN_0041c350`) runs `Talker_Tick` (`0x00421b90`) for scene `+0x168`: voice
  emitter's group not playing → `FUN_00421730`; table → `FUN_00421bd0`, else
  `FUN_00421d20`. `FUN_00421bd0`: t = `timeGetTime` − `+0x1e0`; `FUN_00421a70` past the
  last record → `FUN_00421730`; 1 → `FUN_00421b20` (current slot `+0x64` = 0, `+0x60` = 1,
  current = 0; slot 8: `FUN_00420080(1)` enabled, paused, frame 0.0), `DAT_0046ec48` = 0;
  2/3 → if t − `DAT_0046ec48` > 199 select it; other → if > 199: r = rand·4/0x7fff + 4,
  while r = current r = rand·4/0x7fff + 1; select; slot `+0x78` (fps) = rand·2/0x7fff + 1.
  `FUN_00421d20`: every > 199 ms of `timeGetTime` (`DAT_0046ec4c`): r = rand·9/0x7fff + 1;
  9 → current slot `+0x64` = 0, `+0x60` = 1; else select; current slot fps =
  rand·4/0x7fff. Select `FUN_00421ac0`: old slot `+0x64` = 0; new `+0x64` = 1, `+0x60` = 0.
  Node fields per E-0056: `+0x64` enabled, `+0x60` paused, `+0x78` fps.
- **Method:** MCP decompile; capstone around the talker declarations; `a3d.py` dump of
  `U01_01/A.A3D`.
- **Confidence:** proven for the rules; the override order against the body animation is
  Q-0072. Partly answers Q-0026 (scene `+0x168` is the current talker, not a camera path).

### E-0126 — Lip tables do not match their voice lengths
- **Binary/file:** `Data/*/Sound/*.bin`, `.wav`.
- **Evidence:** `lip.py -v`: every `.bin` has a `.wav` of the same name; the last record
  lies after the `.wav`'s end in 28 of 81 (`D1_02` 49.8 s vs 41.6 s; `U05_06` 14.4 s vs
  5.7 s) and well before it in others (`d1_08` 11.8 s vs 15.4 s).
- **Method:** validator statistics (Python `wave` durations).
- **Confidence:** corpus fact; the reason is Q-0070.

### E-0127 — WAV corpus formats and U01's sound users
- **Binary/file:** `Data/**/*.wav` (244); `MissionMonet.exe`.
- **Evidence:** all RIFF/WAVE PCM mono: 22,050 Hz 8-bit ×235, 44,100 Hz 16-bit ×7 (U01:
  `s1_03`, `s1_08b`, `s1_10`, `s1_11`, `s1_12`, `s1_13`, `u01`), 22,050 Hz 16-bit ×1
  (`U03/Sound/s2_03`), 11,025 Hz 8-bit ×1 (`U07/Sound/Couper`); chunks `fmt `+`data` ×168,
  plus a trailing `LIST` ×76. `Data/U01/Sound`: 23 `.wav`, 8 `.BIN`. INFOACT U01: op 1
  `d1_02`, `D1_03`, `D1_06`..`D1_10`; op 13 `Marsaillaise`, `s1_03`, `s1_07` ×2,
  `s1_08b`. U01 code (capstone scan of vtable `+0x48..+0x54` calls): `+0x50` `S1_10`
  (`0x004017f3`), `s1_12` (`0x00401ab2`, `0x00401c01`), `OpenDoor`, `CloseDoor.wav`,
  `TelGrisi` ×2, `CloseDoor`, `s1_05` ×2, `s1_13`; `+0x48` `s1_11` (`0x0040188f`);
  `+0x4c` `U01`. The train handler `0x00401b90`: `+0x50("s1_12", camera, 1)`,
  `LSoundManager_StopGroup(1)`, then d += 10 while d < scale·60: `SoundEmitter_SetDistance`
  on scene `+0x174`, `Scene_RunFor(20)`.
- **Method:** Python RIFF walk over the corpus; `infoact.py --file`; capstone.
- **Confidence:** proven.

### E-0080 — U01's load hook renames the switch, the `Box20` family, `tige` and `*U01_08P`; X3D's object list is newest first
- **Binary/file:** `MissionMonet.exe`, `x3d.dll`; `Data/U01/U01.X3D`, `Data/U01/**/*.O3D`.
- **Evidence:** U01 vtable `+0x10` (`0x00401050`, after `XScene_124`): the object found by
  `X3d_Scene_Get_Object("Box31")` gets the name `*U01_21` (`0x0040108a`), the node found as
  `Object07` in the node list (scene `+0x158` vtable `+0x14`) gets `*U01_21` at node `+0xc`;
  a loop (`0x004010f8..0x0040114b`) finds `Box20`, copies `sprintf("Box20%i", ++i)` over
  its name and looks `Box20` up again until none is left; `Box203` gets `+0x118` = `+0x114`
  = 1 and `X3d_Object_Hide`, `Cylinder07` is hidden (E-0060); `tige` is renamed `*U01_12`,
  `*U01_08P` `*U01_08`; unit `+0x6e4` = 0 (the constructor `0x00401000` also sets `+0x6e8`
  = 0). `X3d_Scene_Get_Object` walks the scene list (`+0x2c` next) and in each root
  `X3d_Object_Get_Son` (case-sensitive `strcmp`, self, then children `+0x24` and siblings
  `+0x28` depth first); `X3d_Scene_Add_Object` prepends. Corpus (`o3d.py`): `Box20` is in
  PTITRAIN, INTCAB, RAILS, PLDV (U01.X3D order), `Box31` in U01, PTITRAIN, RAILS,
  `U01_21.O3D`; no file has `Box203`. Unit vtable `+8` (`0x00402a30`) / `+0xc`
  (`0x00402a90`) read / write chunk `TRAIN_CHANGED` (`0x0043f2a4`): u32 `+0x6e4`, u32
  `+0x6e8`.
- **Method:** capstone with strings resolved; MCP decompile of the x3d.dll functions.
- **Confidence:** proven for the renames and list order; which object becomes `Box203`
  follows from the load order only if every root enters the list once (Q-0045).

### E-0081 — `U01_Start` in full: talkers, ambient, the `d1_01` / M01 talks; the wait E-0050 calls "camera animation" is the talk wait
- **Binary/file:** `MissionMonet.exe`; `Data/U01/INFOACT.BIN`, `Data/U01/Sound`.
- **Evidence:** `U01_Start` (`0x00401230`, capstone): `PlayVideo("Prologue")` or (restore)
  vtable `+0x4c("U01", 1)`; `FUN_00419d00(37.0)`; `FUN_0041ae10` (vtable `+8`, `+0x2c`);
  vtable `+0x28` = `XSceneAnim::XSceneAnim_157` twice with ("U01_01", "",
  "$$$DUMMY.*01SParle", 0, 8, 0) and ("U01_02", "", "$$$DUMMY.*02SParle", 0, 8, 0); unit
  `+0x6d0`/`+0x6d4` = node/hotspot `*U01_02`, `+0x6c8`/`+0x6cc` `*U01_01`, `+0x6dc` hotspot
  `*U01_20`, `+0x6d8` = `FUN_00420190(*U01_20)` (the node's active slot); if `+0x6e8`,
  camera `+0x3c` = the `*U01_20` object; `+0x6e0` = (`*U01_21` node frame ≥ 2.0,
  `0x00439428`); `FUN_00421330(*Ernest object, 1)` sets `+0x118` on it, its children and
  siblings recursively; `FUN_0041b440("Tapiroug*" match, 0)` → `+0x114` = 1. New game:
  `+0x4c("U01", 1)`; `FUN_00414820(cursor, 0, 0)` (app `+0x480` = 1, the suspend flag of
  E-0046/E-0051); `FUN_00421300` cursor 0 on `*U01_02`, `*U01_01`; `DAT_0046ec1c` vtable
  `+0xb8` → `+0x90("U02_01P")`, if 0 `+0xa8("U02_01P")`; camera E-0041; `RunFor(1500)`;
  scene `+0x13c` = 0, app `+0x484` = 0; `FUN_004215f0(talkers, "U01_01", "d1_01")`;
  `LookAt(1000, FUN_0041b4c0(*U01_01 object, "TETE", exact))`; two `MoveTo` (E-0050);
  voice-emitter wait (`+0x178`, Enter); `RunFor(1000)`; `FUN_0041e4b0(actions +0x14)`.
  The action manager (scene `+0x198`) keeps action pointers at `+0x10 + id·4`
  (`Scene_LoadActions` `0x0041dc9e`), so this runs M01 (`Marsaillaise` op 13, `d1_02` op 1
  on `U01_02`) and counts it (`FUN_0041e320`). Then `*U01_03` running; `LookAt(1000, TETE
  under *U01_02)`; `RunFor(400)`; FOV saved; two `MoveTo`; loop while
  `DAT_00442640 + 0x168` ≠ 0 and Enter up. `+0x168` is the current talker: `FUN_004215f0`
  stores it (`DAT_00442640[0x5a]`), `FUN_00421730` (talk stop) clears it, `FUN_0041c350`
  ticks it. Then stop `+0x178` and `+0x174`, pause `*U01_03`, `MoveTo(600, keep, keep, π/2,
  saved)`, `GiveCard`, camera `+0x40` = `+0x44` = 0, app `+0x484` = 1, `*U01_01` cursor 3,
  scene `+0x13c` = 1, `FUN_00414820(cursor, 1, 1)`. Corpus: `d1_01.WAV` 23.43 s (no
  `.BIN`), `d1_02.WAV` 41.60 s, `Marsaillaise.WAV` 9.0 s.
- **Method:** capstone of `0x00401230..0x0040178e` with strings and floats resolved; MCP
  decompile of the helpers named; `infoact.py --file`; Python `wave`.
- **Confidence:** proven. Supersedes E-0050's "camera-animation wait (Enter)" (it is the
  talk wait) and answers the `+0x168` part of Q-0026.

### E-0082 — U01's per-frame hook: a 20-second gauge started by the phone call; expiry plays "caught" and opens `OptionLoad`
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** U01 vtable `+0x1c` (`0x004017a0`) calls `Scene_RenderFrame`, then
  `FUN_0041a6c0(scene +0x148, 1)`: true once when gauge `+0x30` ≥ 1.0, resetting it
  (`FUN_0041a680`: `+4`, `+0x10`, `+0x30` = 0). The gauge (save chunk `JAUGE`,
  `0x00441760`; `FUN_0041a820`/`FUN_0041a790`): `FUN_0041a560(seconds, visible, name, id)`
  sets duration `+8` = ⌊seconds⌋·1000, start `+4` = `timeGetTime`, elapsed `+0xc` = 0;
  `Scene_RenderFrame` calls `FUN_0041a5d0` only while `+4` ≠ 0 (`0x0041b1bc`), which
  accumulates elapsed, sets `+0x30` = elapsed / duration and, below 1.0 and if visible,
  fills (`FUN_0041a700`, DirectDraw `Blt` colour fill of a RECT) (9, 9, 111, 21) with
  0x808080 and (10, 10, 110 − ftol(100·p), 20) with 0xFF. The only start in U01 is
  `0x004024ca` (`20.0`, visible 1); `MonterSurToit` resets it (`0x0040268c`). On expiry:
  `FUN_00414820(0, 0)`, app `+0x488` = 0, `+0x50("S1_10", eye)`, wait `+0x174`, hotspot
  list `+0x28("*Ernest", 1, 0)` (`0x00421050`: show, `+0x118` = 0), `LookAt(100, *U01_07
  object)`, door node `FUN_004200c0(2.0)`, `0x00402050` (OpenDoor), `+0x48("s1_11", eye)`,
  wait for the door node's `+0x60`, `MoveTo(1000, (486.059, −107.99, 24), 0.0831, 1.95)`,
  `MoveTo(2000, none, 0.1631, 2.19, 35)`, `FUN_0041bfd0(2000)` (N = ftol(ms · fps ·
  0.001) steps lowering ambient `+0x16c..+0x16e` by start/N via `FUN_0041b2f0`,
  `RunFor(10)` each, app `+0x488` = 0 then 1), then game object (`DAT_0046ec18`, vtable
  `0x00439894`) `+0x14` = `FUN_004135b0`: stop all sounds, frame manager
  (`DAT_0046ec1c`, vtable `0x00439e5c`) `+0xc0(2)` = `FUN_004266c0` → `FUN_00426ea0`
  loads frame `OptionLoad` and sets app mode 2.
- **Method:** capstone and MCP decompile of the functions named.
- **Confidence:** proven. The fill colour's channel order (red) is inferred.

### E-0083 — U01's input hook rides the train while the eye stands on `*U01_20`
- **Binary/file:** `MissionMonet.exe`; `Data/U01/Anim/U01_20*.A3D`, `INFOOBJ.BIN`.
- **Evidence:** U01 vtable `+0x40` (`0x00401940`): `+0x6e8` = (camera `+0x3c` ==
  `*U01_20` object); `Camera_FollowGround` (`0x0041a270`) stores the highest hit's object in
  camera `+0x3c`. If set: camera `+0x70` = 0; `GetAsyncKeyState(VK_UP)` → `0x00401a40`,
  else `Camera_HandleKeys`; `Camera_FollowGround` on a copy of the eye; camera `+0x70` = 1
  if the ground object changed. Always `Scene_HandleInput` (`0x0041b7f0`, which calls
  `Camera_HandleKeys` again); then if on the train and Up up, stop `+0x174`.
  `0x00401a40`: `FUN_0041ff20(+0x6d8)` (the frame advance, which does not test the paused
  flag; E-0056's tick does); global positions of the train object (P) and hotspot
  `*U01_23`'s object (Q); `+0x50("s1_12", eye, 1)` if `+0x174` is silent, else emitter
  `+8` := eye; Q.z += 10, P.z := Q.z(old) + 18 (`0x00401ad3..0x00401af6`);
  `FUN_00415e80` d = normalize(Q − P); `FUN_00419520(P.x − 40 d.x, P.y − 40 d.y,
  P.z − 20 d.z)` (`0x0043942c` = 40, `0x00439430` = 20); `FUN_00419580(P, Q)` (yaw/pitch
  by `X3d_Convert_To_Polar`); pitch := π/2; `0x00401b90`. `0x00401b90`: with `+0x6e4` = 0,
  `+0x6e0` set and |ftol(frame) − 90| ≤ 1: `+0x6e4` = 1,
  `FUN_00420220(node, "%sAnim/U01_20A.A3D", "Train2", 1, 1)`, `FUN_0041fe60(clip, own
  animation, train object +0x20, 10.0, 0, 1)`, frame 15.0, `+0x6d8` = the clip; with
  `+0x6e4` set and frame == (float) last frame: the exit (E-0087). Corpus (`a3d.py`):
  `U01_20.A3D` frames 1..270 with children `*U01_20` → `*U01_23`; `U01_20A.A3D` 0..120;
  INFOOBJ `*U01_20` frame 20, paused, 15 fps, looping.
- **Method:** capstone (stack offsets tracked by hand; the MCP decompile misreads them);
  MCP decompile of the callees.
- **Confidence:** proven.

### E-0084 — U01's click handlers (`0x00401d30` dispatch)
- **Binary/file:** `MissionMonet.exe`; `Data/U01/INFOACT.BIN`, `INFOOBJ.BIN`.
- **Evidence:** names at `0x00401d76..0x00401ead` →
  `TakeCard` `0x00401fb0` (E-0057; then `FUN_00421300(*U01_02 hotspot, 3)`);
  `ClickMaire` `0x00401f40`: static `0x0043f010` (initial 1) → `d1_04` and cleared, else
  `rand` scaled by 2/32767 (`imul 0x80010003`, `sar 0xe`) = 1 → `d1_04`, else `d1_05`,
  `FUN_004215f0("U01_02", …)`;
  `OpenDoor` `0x00402050`: node `*U01_07` `+0x70` = 0, `+0x78` = 2.5,
  `FUN_00420100(12.0, 1)`, `+0x50("OpenDoor", hotspot +0x70, 0)`;
  `CloseDoor` `0x004020b0`: `+0x50("CloseDoor.wav", hotspot +0x70, 0)`, `+0x70` = 1,
  `+0x78` = 4.0, `FUN_00420100(0.0, 1)`;
  `TakeCarteHorloge` `0x00402110`: `FUN_00421300(list, 2, "*U01_11", by name)`;
  `OpenBoitier` `0x00402510`: node `*U01_13` frame == 10.0 → `+0x70` = 1,
  `FUN_00420100(0, 1)`; else `+0x70` = 0, `FUN_00420100(10.0, 1)`;
  `BaisserManette` `0x00402570`: node `*U01_14` `FUN_00420100(10.0, 1)`;
  `OpenTiroir1`/`2` → `0x004025a0("*U01_15"/"*U01_16")`: `FUN_00420140(0, 10)` (animation
  first/last := 0/10, old values kept at node `+0x1cc/+0x1d0`); frame == 10 → stop
  `+0x174`, `+0x50("s1_05", eye)`, `+0x70` = 1, run to 0; else frame ≤ 1.0 → stop
  `+0x174`; `+0x50("s1_05", eye)`, run to 10, `+0x70` = 0;
  `DoInterrupteur` `0x00402840`: node `*U01_21` `+0x68` = 0, running, `+0x50("s1_13",
  eye)`, eye and angles saved, then the two branches on `+0x6e0` with `FUN_00419520` /
  `FUN_00419550` cuts to (667, 723.8, 94) 6.02/0.79 and (753.22, 662.18, 93.55) 6.26/π/2,
  `RunFor` 1200/1500 (or 600, 1500, 1200 with `FUN_00420100(100.0, 1)`), restore,
  `RunFor(0)`. After the queue: action manager `+0x460` (= exhausted flag of id 20,
  `+0x410 + id·4`), hovered hotspot `*U01_09` (`_stricmp`) and eye z < 100 →
  `MonterSurToit`. `Light255` and `EcouterConversation` are not compared.
- **Method:** capstone with strings and floats resolved; MCP decompile of the node API
  (`FUN_00420060`, `FUN_004200c0`, `FUN_00420100`, `FUN_00420140`, `FUN_004201c0`).
- **Confidence:** proven. Resolves Q-0042.

### E-0085 — `ClicTel`: M10's run count picks pick-up or hang-up; with the lever down the call starts the gauge
- **Binary/file:** `MissionMonet.exe`; `Data/U01/INFOACT.BIN`, `Anim/Combine.A3D`.
- **Evidence:** `0x00402130`: node and hotspot `*U01_11`; `fmod(actions +0x838, 2.0)`
  (`+0x810 + 10·4`: M10's count, already incremented since the steps and count run before
  the queue) == 0 → `+0x70` = 1, running, loop `RunFor(0)` + vtable `+0x40` until
  `+0x60`, stop and delete `+0x184`, `+0x50("TelGrisi", hotspot +0x70)`. Else `+0x70` = 0;
  actions `+0x450` (M16 exhausted) → `FUN_00421300(hotspot, 0)`, `FUN_0041e2a0(M10, 0)`
  (condition `FALSE`, `0x00441cc0`), `0x00402380`, running; otherwise `+0x50("TelGrisi")`,
  loop while `+0x174` plays, `+0x184` = new emitter `FUN_00414c80(4, s·50)`,
  `SoundEmitter_Play("%sSound/TelGrisi2.wav", hotspot +0x70, 1)`, running. Then count == 1
  → `FUN_0041e2a0(0)` on actions `+0x20`, `+0x24`, `+0x28` (M04, M05, M06) and cursor 0 on
  `*U01_01`. `0x00402380`: suspend, node forward running, if actions `+0x470` (M24
  exhausted) = 0: `FUN_0041e4b0(M24)`, `FUN_0041e2a0(M19, 1)` (`TRUE`, `0x00441cc8`),
  `MoveTo(1500, (433.788, −91.1468, 24.7812), 2.84318, 1.0708)`, wait `+0x178` (Enter),
  `MoveTo(1000, (421.145, −69.187, 24.78), 0.6431)`, `+0x50("CloseDoor", eye)`,
  `0x004020b0`, `FUN_0041a560(20.0, 1, "", 0)`, cursor 4 on `*U01_08`, resume. Corpus:
  M24 = op 1 `D1_10` on `U01_11` (type 5), `d1_10.wav` 48.24 s; `Combine.A3D` animates
  `*U01_11`, frames 0..62.
- **Method:** capstone; MCP decompile of `FUN_0041e2a0`, `FUN_0041e320`, `FUN_0041e4b0`,
  `SoundEmitter_Play`, `FUN_00414c80`; `Scene_LoadActions` for the id table.
- **Confidence:** proven.

### E-0086 — `MonterSurToit` climbs in five steps of D/7 and leaves the eye on the train roof
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `0x00402670`: `FUN_00414820(0, 0)`, `FUN_0041a680(gauge)`,
  `X3d_Object_Unhide(*U01_10, 1)`, `MoveTo(1000, (439.833, −50.66, 28.2052), 100, π/2)`,
  `MoveTo(800, eye, −0.45)`, `RunFor(500)`, D = `FUN_00415e40` (distance) from the eye to
  (439.833, −50.66, 100.637), five times `MoveTo(500, (439.833, −50.66, eye.z + D ·
  0.142857))` + `RunFor(200)`, `MoveTo(1500, (469.932, −40.2943, 110.637), 7.2731)`,
  `MoveTo(1200, (485.775, −44.9, 139))`, `FUN_00419d00(20.0)`, `FUN_00414820(1, 1)`.
- **Method:** capstone and MCP decompile.
- **Confidence:** proven.

### E-0087 — U01 ends when the siding clip reaches its last frame: fade, train sound fade, go to unit 2 (`U02.x3d`)
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `0x00401b90` (E-0083) with `+0x6e4` set and the clip at its last frame:
  `FUN_00414820(0, 0)`, `FUN_0041bfd0(2000)`, app `+0x488` = 0, `+0x50("s1_12", eye, 1)`,
  `FUN_00423360(sound manager, 1)`, d += 10 while d < scene `+0x138` · 60 with
  `FUN_00414e40(+0x174, d)` and `RunFor(20)`, then game vtable `+4(2)`. Game vtable
  `0x00439894` `+4` = `0x00412fb0`: returns if app mode is already 1; else mode 1,
  `n == 8` → name `U33.x3D` (`0x0044112c`, `+0x160` = 3), otherwise `sprintf("U%s.x3d",
  FUN_00416250(n, 2 digits))` into game `+0x14c`. The debug keys in `Scene_HandleInput`
  call the same method with 1..8.
- **Method:** MCP decompile and capstone.
- **Confidence:** proven for the call; U02's own entry is not covered.

### E-0088 — Step op 9 shows the target when its argument is `0` and hides it (no collision) otherwise
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `Action_RunStep` case 9 (`0x0041e526..0x0041e55b`): `atoi(arg)` (0 when the
  argument is empty), `sete bl`, then target hotspot vtable `+0x28(target name, atoi == 0,
  1)`. Hotspot vtable `0x00439a20` `+0x28` = `0x00421050(name, show, noCol)`: finds by
  name, `show` ≠ 0 → `X3d_Object_Unhide(obj, 1)` and `+0x118` = 0, else
  `X3d_Object_Hide(obj, 1)` and `+0x118` = `noCol`.
- **Method:** capstone.
- **Confidence:** proven. Supersedes the op-9 row of `interaction.md` ("show if `arg` ≠ 0"),
  which is inverted.

### E-0140 — `.L3D` light fields after the colour are inner, outer, multiplier, hidden, attenuate
- **Binary/file:** `x3d.dll`; `Data/U0[1,3,6]/Static/*.L3D`, `U33`.
- **Evidence:** `FUN_10014d50` stores the three f32 after the RGB at light `+0x38`, `+0x34`,
  `+0x3c` and the two u32 at `+0x40`, `+0x44`, then `+0x4c`→`+0x30` = (`+0x34`)² and
  `+0x34` = (`+0x38`)². The exports name the slots: `X3d_Light_Set_Inner` writes `+0x38`
  and the squared copy `+0x34`; `X3d_Light_Set_Outer` `+0x34` and `+0x30`;
  `X3d_Light_Set_Multiplier` `+0x3c`; `X3d_Light_Get_Hide_State` reads `+0x40`;
  `X3d_Light_Attenuate` sets `+0x44` = 1. Spot angles are stored as
  `cos(angle · π · 0.0027777)` = cos(angle / 2 in degrees) at spot `+0x40` (first) and
  `+0x44` (second). Light `+0x2f` = (r + g + b) / 3. Corpus: every light has inner ≤
  outer (e.g. U01 104.8 / 125.2, U06 32 / 80); multipliers −1, 0.3, 1, 4, 5 (U01: four
  at −1, Omni04 at +1); hidden always 0; attenuate 1 except U06 (0).
- **Method:** MCP decompile; `tools/parsers/l3d.py` dump of all five files.
- **Confidence:** proven.

### E-0141 — Material render class and slots: `+0` class 0/1/2, colours ambient/diffuse/specular/light, u32s shininess, strength, transparency, mode, tiling
- **Binary/file:** `x3d.dll`, `xd3d.dll`; corpus `.O3D` (2,133 materials).
- **Evidence:** `FUN_10011450` reads `flags` into material `+0`, which
  `X3d_Material_Get_Default_Render_Class` returns and `xd3d.dll` `FUN_1001df90` switches on
  (with the state bits of `FUN_1001e530`) to pick the drawer table. `x3d.dll` `FUN_1001e950`
  (adding a material to an object) increments transform `+0x1a0` for class 1 and `+0x1a4`
  for class 2 (`0x1001e9c6..0x1001e9e2`; `0x10018658..0x1001874f` redo it when the state
  changes). `X3d_Material_Set_Ambient` writes `+0x2c..0x2e`, `X3d_Material_Set_Light_Color`
  `+0x3e..0x40`. The untextured class-2 drawer (`xd3d.dll` `0x10001f76..0x10002060`)
  multiplies the lit colour by `+0x32..0x34` (diffuse) and indexes a table built from
  `+0x38..0x3a` (specular); `FUN_1001ddc0` builds that table from `+0x44` (shininess) and
  `+0x48` (strength). Every drawer sets `D3DRENDERSTATE_TEXTUREADDRESSU/V` (0x2c/0x2d) to 3
  (clamp) when material `+0x58` = 0, else 1 (wrap) (e.g. `0x100029db..0x10002a10`). Corpus:
  class 2: 1,537, class 0: 596, class 1: 0; all class-0 materials textured; `+0x58` = 1 on
  1,986, 0 on 147; `+0x50` ∈ {0, 1}. The order matches `.MAT`'s AMBIENT, DIFFUSE, SPECULAR,
  LIGHT_COLOR, SHININESS, SHININESS_STRENGTH, TRANSPARENCY.
- **Method:** MCP decompile, capstone sweep of both DLLs, `o3d.py` over the corpus.
- **Confidence:** proven for class, ambient, light colour, diffuse/specular use, tiling;
  the shininess names follow `.MAT` order and the table's use.

### E-0142 — X3D lights class-2 objects per vertex in RGB with an overflow term; `FUN_1001aea0`
- **Binary/file:** `x3d.dll`, `xd3d.dll`.
- **Evidence:** `FUN_1000b690` fills the object class (`0x1002d0d8` `+0x6c`): `+0x1c` =
  `0x10001668` → `FUN_1001a280`, `+0x20` = `0x10001064` → `FUN_1001aea0`. `xd3d.dll`
  `FUN_10020d10` / `FUN_10020720` call `+0x1c` when transform `+0x1a0` ≠ 0 and `+0x20` when
  `+0x1a4` ≠ 0, for the drawn (LOD-picked) object with the original object and the scene,
  after culling. `FUN_1001aea0`: transforms the drawn object's vertex range (`+0x48`,
  `+0x44`) and normals by the original's global matrix (`X3d_Normal_Array_Matrice_Mult`
  with transform `+0x178`) into `DAT_10028ec4` / `DAT_10028ed4`; sets diffuse
  `DAT_10028edc` to scene `+0x40..0x42` and specular `DAT_10028ee0` to 0; for each light of
  the original's list (`+0x64`) with `+0x40` = 0: omni without attenuation adds
  colour · multiplier · (L̂·N) when positive; with attenuation, rejects the light when
  |P − sphere centre|² ≥ (outer + radius)², else per vertex uses 1, or
  1 − (d² − inner²)/(outer² − inner²), or 0 by d²; spot uses (P−T)̂·N, then the cone on
  L̂·(P−T)̂. Clamp: > 255 moves the excess (capped 255) into specular and sets 255; < 0 → 0.
  `FUN_1001a280` does the same with the grey values `+0x2f` / scene `+0x43` into the w slot.
- **Method:** MCP decompile (function created at `0x1001aea0`), capstone for the thunks.
- **Confidence:** proven.

### E-0143 — Drawers: class 2 textured sends lit RGB as diffuse and the overflow as specular; class 0 sends white, flat
- **Binary/file:** `xd3d.dll`, `x3d.dll`.
- **Evidence:** `x3d.dll` `0x10020f4b` passes `0x10028ec0` to `X3d_Init_Render_Dll`, so
  `xd3d.dll`'s context `+0x1c` / `+0x20` are `DAT_10028edc` / `DAT_10028ee0`. Class 2
  state 1 (`FUN_10002420`) packs `_ftol` of `+0x1c` R, G, B into the D3DTLVERTEX colour
  (alpha 0) and of `+0x20` into specular (`0x10002933..0x10002996`), sets
  SPECULARENABLE 1, SHADEMODE 2 (Gouraud), draws a triangle fan (`IDirect3DDevice2`
  `+0x74`, type 6); class 2 state 3 (`FUN_100039c0`) does the same with COLORKEYENABLE.
  Class 0 state 1 (`FUN_1000a740`, created) writes 0x00FFFFFF and SHADEMODE 1 (flat), no
  specular; class 0 state 3 is `FUN_1000b840`. A sweep of every `SetRenderState` call site
  in `xd3d.dll` finds no state 21 (TEXTUREMAPBLEND) and no 28 (FOGENABLE).
- **Method:** MCP decompile, capstone sweep of `push` arguments before `call [reg+0x5c]`.
- **Confidence:** proven for the vertex data and states; that the blend is modulate is
  Direct3D 5's documented default.

### E-0144 — The per-object lit-colour cache is never enabled, so lighting runs every frame
- **Binary/file:** `x3d.dll`, `xd3d.dll`.
- **Evidence:** `FUN_1001aea0` / `FUN_1001a280` reuse byte copies (`+0x120`, `+0x124`) only
  when object `+0x10c` ≠ 0 (and call `FUN_1001c010` when `+0x110` ≠ 0). No instruction in
  either DLL writes `+0x10c` or `+0x110` (disassembly sweep: only the reads at
  `0x1001a290`, `0x1001aeb0`, `0x1001aeba`, `0x1001ba79`, `0x1001c020`, `0x1001ce0a`);
  `X3d_Object_Create` allocates the object zeroed.
- **Method:** capstone sweep.
- **Confidence:** strong (a write through a computed pointer in the EXE is not excluded).

### E-0145 — U01's distant buildings, boats and sun are beyond every light: lighting leaves them at texture colour
- **Binary/file:** `Data/U01/static/U01.o3d`, `LIGHTS.L3D`, `SCENE.BIN`.
- **Evidence:** ambient (255, 255, 255) (E-0039). World vertices (E-0042) of the objects
  using `immgch`, `immdrt`, `barques` (class 2) and `soleil` (class 0) are 595 to 3,498
  units from the nearest light; the largest `outer` is 164 and all U01 lights attenuate.
  So D = (255, 255, 255), S = 0: texture × 1. `immgch`/`immdrt`/`barques` have `+0x50` = 1,
  `+0x58` = 0 (clamp).
- **Method:** script over `o3d.py` / `l3d.py` output.
- **Confidence:** proven for the lighting result.

### E-0100 — `.FRA` is a tagged object list read by `LFrameReader` and built by `LClassCreator`; 25/25 parse
- **Binary/file:** `MissionMonet.exe`; `Data/2DFRA/*.fra`.
- **Evidence:** `LFrameReader::LFrameReader_97` (`0x0042d290`, assert `LFrameReader.cpp:97`)
  opens `<root>2DFRA/<name>` with `.fra` appended when the name has no `.` (`0x0042d250`;
  strings `2DFRA/` `0x004424a4`, `.fra` `0x004424ac`, set by the constructor `0x0042d130`),
  reads the whole file (size masked to 16 bits) and returns the first u32.
  `LClassCreator::LClassCreator_128` (`0x0042e4e0`) loops that many times: read a u32 tag
  (`0x0042d3f0`), construct the class registered for it (`0x0042e610`: tag → index →
  factory), call its `+0x24`, then read u32 tags until 0 (`0x0042d410`), constructing each
  as a property (`0x0042e6a0`) and calling its `+8`, then the object's `+0x108`.
  `RegisterFrameClassTags` (`0x0042aab0`) pairs tags with factories: `#VIE` (`0x23564945`)
  `0x004341b0`, `#BIT` `0x00423e40`, `#SCR` `0x00432570`, `@CUR` `0x0042e850`, `@ARF`
  `0x0042d010`, `@HIL` `0x0042ec30`, `@DRA` `0x0042e9d0`, `@SCR` `0x00432290`, `@ANI`
  `0x0042d490`, `@HIG` `0x0042ef30`, `#pov` `0x0042ad00`, `#pob` `0x0042aca0`, `#LOP`
  `0x0042f2b0`, `#LOA` `0x00427fb0`, `#SAV` `0x00428250`, `#Edi` `0x004284d0`, `#Vol`
  `0x00434cd0`, `#VoB` `0x00435340`, `#VoA` `0x00435200`, `#UEd` `0x00429290`, `#SEd`
  `0x00429100`, `#USc` `0x004294b0`, `@gcu` `0x00426a60`; and frame classes by name:
  `PorteF` `0x00431680`, `Tableau` `0x00426090`, `Loupe` `0x004262c0`, `Taille`
  `0x00426400`. Constructors read their body with `FUN_0042d3c0(reader, dst, n)`: view
  `0x004342f0` 0x24 (id → `+0x10`, rect → `+0x14..+0x20`, `+0x38`, parent id → attach to
  that view, `+0x3c`, `+0x40`); `#BIT` `0x00423ea0` +0x2c (two s32 → `+0x24/+0x28`, name →
  `+0x74`, s32 → `+0x70`); `#LOP` `0x0042f310` #BIT + 8; `#SCR` `0x004325d0` +0x6c (three
  names at `+0xb8/+0xd8/+0xf8`); `#Vol` `0x00434d30` +0x24; `#pov`, `#pob`, `#Edi` and its
  subclasses, `#LOA`/`#SAV` (through `0x004275e0` → `#SCR`) and `#USc` (→ `#SCR`) read
  nothing more. Properties (base `0x0042e210` reads nothing): `@gcu` 4, `@CUR` 4, `@DRA` 4,
  `@ARF` 0x20, `@SCR` 0x20, `@HIL` 0x28 (`@HIG` = the `@HIL` constructor + enabled = 0),
  `@ANI` 0x38. With these sizes `tools/parsers/fra.py` consumes every byte of 25/25 files
  (106 objects, 196 properties). `nCC#` / `nIC#` (7 files: `Prologue`, `Epilogue`,
  `GivParis`, `LeHavRou`, `RouGiv`, `V33_01/02`) are not registered and their bytes occur
  in neither EXE; their layout (view + u32 + name[32]) is from the corpus. Of 128
  bitmap-name fields all but `Intro`, `FondNoir` and three `SCR.BitmapScroll` exist in
  `Data/2dbit/`.
- **Method:** MCP decompile; capstone for the tag/factory pushes and constructor read
  sizes; `fra.py` over the corpus.
- **Confidence:** proven. Resolves the `.FRA` half of Q-0016.

### E-0101 — Frame manager: input first, hit test from the last view, a 50 ms timer, frames drawn after the 3D scene
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** the manager (constructor chain `0x00426540` → `0x0042b6e0`, vtable
  `0x00439e5c`; `DAT_0046ec1c` and `DAT_0046edb0` hold the same object) gets each window
  message first (window procedure `0x00416650`, call at `0x00416680` to `+0x68` =
  `0x0042bc00`, which forwards only while its open-frame list is non-empty).
  `FrameManager_OnMessage` (`0x0042bcc0`): `WM_KEYDOWN` → `+0xc(15, 0, &vk)`, then each
  open frame's `+0x1c` until one returns nonzero; `WM_CHAR` → frames' `+0x38`;
  `WM_MOUSEMOVE` (`0x0042c1c0`) → frames' `+0x14`; `WM_LBUTTONDOWN` (`0x0042c140`) →
  `+0xc(4)`, frames' `+0x18`; `WM_LBUTTONUP` (`0x0042c0d0`) → `+0x30`; `WM_RBUTTONDOWN`
  (`0x0042c050`); `WM_TIMER` → `+0x74`. Frame base: press (`0x0042cba0`) walks the view
  list from the last index to 0, needs the view's `+0x38` (`0x00426a00`) and `PtInRect`
  (`0x004349b0`), remembers the view (`+0x30`) and calls its `+0x50` (event 4,
  `0x00434a80`); release (`0x0042ced0`) calls the remembered view's `+0x64` (event 13,
  `0x00434bc0`); move (`0x0042cab0`) calls `+0x44` (event 1, `0x00434a10`) on the old
  view, `+0x48` (event 2) on the new, `+0x4c` (event 3) while inside. A view offers each
  event to its properties first (`+0xc`). When the manager consumed a message in app mode
  0 the window procedure calls scene `+0x3c` and sets app `+0x48c` = 2.
  `SetTimer(hwnd, 0, 50, NULL)` at `0x0042ba99`. Draw: in app mode 0 `Scene_RenderFrame`
  (`0x0041b130`) runs `X3d_Render`, manager `+0x70(1)` (`0x0042bc50`: `+0x7c`, `+0x84`),
  the cursor (`FUN_00414630`), the help panel (`FUN_0041a5d0`), then presents; in app mode
  2 the main loop (`0x00416de1`..`0x00416e2a`) restores under the cursor, calls
  `+0x70(1)`, draws the cursor and presents without rendering the scene. A view moves with
  its children (`+0xc0`, `0x00434670`).
- **Method:** MCP decompile; capstone.
- **Confidence:** proven for routing and order; event 7's sender and scene `+0x3c` are open
  (Q-0060).

### E-0102 — Properties: `@gcu` cursor kind on hover, `@HIL` hover bitmap, `@SCR` named command on press; 37 commands
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** property event handlers (vtable `+4`, called with event, view, data):
  `@gcu` `0x00426b70`: event 2 → `FUN_004144b0(cursor, 0, value, 0)` unless cursor mode
  (`DAT_0046ec14 +4`) is 1 or 2; event 1 → kind 0. `@HIL`/`@HIG` `0x0042ede0`: 1 →
  hovered = 0 and redraw, 2 → hovered = 1 and redraw, 7 → `+0x2c` while hovered; the draw
  (`0x0042ee50`) blits the named bitmap at view position + (dx, dy). `@SCR` `0x004323a0`:
  when enabled, look the name up in the command registry `DAT_0046edd0` (`0x00432540`) and
  call it with (event, view, data). `@ARF` `0x0042d110`: event 4 → manager `+0x88(name)`.
  `@CUR` `0x0042e9a0`: event 2 → `SetCursor`. `RegisterFrameCommands` (`0x0042ad60`) maps
  37 names to handlers `0x0042b070`..`0x0042b650`; all act on event 4 only, except
  `MoveCredit` (15 → leave the credits, 4 → next page) and `SaveOui`/`SaveNon` (also 15
  with Escape down → close `Save`). Handlers call the option screen `DAT_0046ec6c` (vtable
  `0x00439f7c`): `OptionNouvelleP` `+0x1c` (`0x00427110`), `OptionQuitter` `+0x20`,
  `OptionCredits` `+0x24`, `OptionLoad` `+0x2c`, `OptionSave` `+0x30`, `OptionScreen`
  `+0x38`, `OptionReglage` `+0x48`; `SelectUser` → `DAT_0046ec78 +0x134`
  (`LUser_SelectUser`, `0x00429600`); `QuitterOK` → `PostQuitMessage(0)`;
  `OptionEntrenement` (`0x0042b4d0`) closes the menu, destroys the option screen, calls
  game `+4(0)` and sets `0x0046ed88` = 1; gallery and magnifier commands go to
  `DAT_0046ec64`.
- **Method:** capstone of the handlers; MCP decompile.
- **Confidence:** proven. Corpus frames use only `ucg@`, `RCS@`, `LIH@`, `GIH@`.

### E-0103 — `x3dcfg.cfg` is authoring residue: no shipped binary reads it; 38/38 parse
- **Binary/file:** all of `INSTALL/02_PR`; `Data/**/x3dcfg.cfg`.
- **Evidence:** a case-insensitive byte search for `cfg` finds only `APP.CFG` in
  `MissionD.exe` (offset `0x75e80`), nothing in `MissionMonet.exe`, `x3d.dll` or
  `x3dsdk.dll`. All 38 files: 36 header bytes (3 f32, 6 u32), u32 n ∈ {0, 1, 2}, then
  n × 260 bytes of NUL-padded paths (`D:\MissionD\Data\U01\maps`); the sizes 40, 300 and
  560 match exactly. `tools/parsers/cfg.py`: 38/38.
- **Method:** Python byte search; parser.
- **Confidence:** proven for the layout; the header's meaning is unknown and not needed.
  Resolves the `.CFG` half of Q-0016.

### E-0104 — The inventory bar is the frame `PorteF`: 4 px per 50 ms tick, items at 86 + 70·i, `P`/`C` image names
- **Binary/file:** `MissionMonet.exe`; `Data/2DFRA/PorteF.fra`, `Data/2dbit/*P.BMP`.
- **Evidence:** `PorteF` constructor `0x004316e0` (frame base `0x0042c860`, vtable
  `0x0043ae9c`, slide timer at `+0x38` with vtable `0x0043ae88`). `PorteF_OnKeyDown`
  (`0x00431800`, vtable `+0x1c`): only key `0x20` and app `+0x488` ≠ 0; timer running →
  `+0x98` if shown (`+0x48`) else `+0x94`; otherwise `+0x94` when the root's y is `0x1e0`,
  else `+0x98`. Show (`0x00431990`): step `+0x44` = −4, count `+0x46` = (y − 420)/4, start
  the timer, shown = 1. Hide (`0x00431a50`): step 4, count (480 − y)/4, shown = 0. Tick
  (`0x004318c0`): move the root by (0, step), count − 1 and stop at 0, clamp to 420 / 480
  and stop. `+0x80(1)` (`0x00431a10`) stops and parks the root at (0, 480). Strip `vop#`
  (id 200): add `0x00431cf0` (item = bitmap view `0x004320e0`, 51×51 at
  x = `0x9c` + 70 · last index, y = strip y + strip h/2 − 25, cursor property kind 4
  (`0x00426b40`), bitmap = the given name; count + 1), remove `0x00431ed0` (`_stricmp`,
  later items `+0xc0(−70, 0)`), has `0x00431e70` (first 7 characters), scroll
  `0x00431f80`, save / load `0x00431fc0` / `0x00432070` (chunk `PORTEF`: u32 last index,
  30-byte names), clear `0x00432030`. Arrows `bop#` `+0x50` (`0x00431be0`): id 100 →
  scroll(−1), else scroll(1). Strip press (`0x00431cb0`): cursor mode 1 → add the name at
  cursor `+0x4a`, hide the bar. Item press (`0x004321e0`): forward to the strip, copy the
  item name, set byte 6 to `C` (`0x00432239`), cursor mode 1 with it (`FUN_00414540`,
  which keeps the name with byte 6 = `P` at cursor `+0x4a`), remove the item, hide the bar.
  INFOACT op 2 (`0x00421270`) shows the bar after setting the cursor; op 3 (`0x004212b0`)
  hides it; clearing app `+0x488` (`0x00417da0`) hides it; `FUN_004149e0` (on Escape)
  adds a held item back. `U01_Start` adds `U02_01P` (`0x0043f0b8`) when `+0x90` reports
  it absent (`0x00401429`..`0x00401459`). Runtime (2026-09-25, `snap.ps1`): after Space at
  the U01 hand-over the bar is at y = 420 with a banknote at x ≈ 86 and empty circles
  every 70 px; Space again hides it. `2dbit`: `…P` item images are 50×50, `PorteF.bmp`
  640×60.
- **Method:** capstone and MCP decompile; one live run.
- **Confidence:** proven for logic and layout. The 750 ms slide follows from the 50 ms
  timer (E-0101) but was not timed live (a capture takes longer than the slide). Answers
  Q-0046 and the inventory half of Q-0041.

### E-0105 — Players screen to U01: `SelectUser`, U00's tutorial, Escape → Option, New game reads `App.bin`
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `LUser_SelectUser` (`0x00429600`): text of view 11 (`+0x128`); empty →
  return; index = `+0x138(name)`, −1 → add to the player list `DAT_0046ec10`
  (`FUN_00413b40`); `PorteF` = manager `+0x94("PorteF", 100)`, kept at manager `+0x18c`,
  `+0x80(1)`; select (`FUN_004140b0`); close the current frame; new player →
  `SetAppMode(0)`, else manager `+0xc0(0)` (`0x004266c0`: create the option screen, which
  opens `Option`, `0x00426f90`). `App_OnEscape` (`0x00416400`), gated by app `+0x484`:
  held item back to the bar; mode 0: game `+0x170` ≠ 0 → gallery; game `+0x160` = 0 →
  stop sound group 1 and open the option screen; else manager `+0xd4` (`0x00426970`: open
  frame `Save` modal, app `+0x480` = 1); mode 2: last opened frame `OptionUser` →
  `SendMessage(WM_DESTROY)`, else if manager `+0xd0` ≠ 1 (not on `Option`) → reopen
  `Option`. The main loop calls it for Escape or F5 (key slots `0x0046e84c`,
  `0x0046e9b0`). `Game_NewGame` (`0x00412b80`, game vtable `0x00439894 +8`): chunk `GAME`
  of `%sAPP.BIN` (30 bytes) → game `+0x14c`, default `U01.X3D`; `+0x164` = 1, `+0x160` = 1,
  name `NoName`; `SetAppMode(1)`; `PorteF +0xa4` (clear the strip). Game `+4(n)`
  (`0x00412fb0`) sets `+0x160` = n and loads `U<nn>.x3d`. `U00_Start` (`0x0040a1e0`) opens
  `OptionUser` only when `0x0046ed88` = 0 (after line `sb01`); U00's frame logic
  (`0x00409850`) starts with line `sb03_bis` instead of its normal first line when it is
  1, then runs the tutorial steps (help names `deplace`, `Sauter`, `Take2`). Runtime: `to_u01.sh` (type a
  name, Enter, hold Escape ~70 s, click (376, 37)) reaches U01; snaps show "The players"
  with the edit text "Player's name" at (306, 91) and the Option menu with Load and
  Gallery dimmed; Escape at the U01 hand-over shows "Do you want to save?" over the scene.
- **Method:** MCP decompile; capstone; live run.
- **Confidence:** proven. Answers Q-0018.

### E-0106 — The Option menu: seven items over `SomFond`; Load and Gallery greyed by a bitmap swap
- **Binary/file:** `MissionMonet.exe`; `Data/2DFRA/Option.fra`.
- **Evidence:** `fra.py --file Option.fra`: ids 2, 3, 9, 6, 5, 7, 8 with the rects, hover
  bitmaps and commands listed in `ui.md`. `0x00426f90` / `0x00427210` open `Option` and,
  when `DAT_00442648 +0xc` = 0, set view 3's bitmap to `SomB2` (`+0x114`); when the
  gallery list (`DAT_0046ec64[6]`) is empty, view 6's to `SomE2`. Credits (`0x00427140`)
  stores the time and opens `Credits`; the option screen's tick (`0x00426e60`) calls its
  `MoveCredit` method after 6000 ms. Runtime snap: the seven labels at those rects, Load
  and Gallery dark.
- **Method:** parser dump; MCP decompile; live run.
- **Confidence:** proven.

### E-0107 — Frame text is GDI Arial 12 pt; labels are bitmaps
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** the edit class (`LOptionScreen::LOptionScreen_1144`, `0x00428a20`, assert
  `LOptionScreen.cpp:1144`) takes a DC from the manager (`+0x20`), builds a `LOGFONT` with
  height −`MulDiv(size, GetDeviceCaps(LOGPIXELSY), 72)` and face `Arial` (`0x00442260`),
  then `CreateFontIndirectA` and `SelectObject`; size `+0x28c` = 12 (`0x004285c2`). Max
  length `+0x290`: 40 for `#SEd` (`0x0042919e`), 30 for `#UEd` (`0x0042932f`). No font file
  is in the data; every menu label in the corpus frames is part of a bitmap.
- **Method:** MCP decompile; capstone.
- **Confidence:** proven for the edits; the lists' text drawing is not read (Q-0061).
