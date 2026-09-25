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

### E-0089 — The engine's scripted U01 entry ends in the original's hand-over state
- **Binary/file:** engine `x3d` at "X3D: Run U01's unit code"; `MissionMonet.exe` (E-0053).
- **Evidence:** run from the first shot through u01.md's entry (posted Enter cutting some
  voice waits), the engine's camera log at the end reads −466.36, −452.495, 30.48, yaw
  4.7, pitch 1.5708, the same values `camera.ps1` reads from the original at its
  hand-over; the mayor holds out the card (GiveCard) and the frame matches the original's
  (`traces/u01-entry-handover-compare.png`, local). The intermediate shots (the boatman,
  the mayor at FOV 45) match the original's intro captures by eye.
- **Method:** engine `-d1` log and snap.ps1; original captures from `to_u01.sh`.
- **Confidence:** proven for the end state; the timing of the intermediate moves is not
  compared frame by frame.

### E-0090 — U01's click chain and ride run in the engine through to U02
- **Binary/file:** engine `x3d` at "X3D: Ride U01's train through the siding into U02"; data
  `Data/U01/INFOACT.BIN`, `INFOOBJ.BIN`.
- **Evidence:** with `dev_handover` and scheduled console commands, the engine ran INFOACT
  M02 (card), M21 (points), M23 (barrel slides away, revealing the key), M18 (clock
  card), M15/M16 (fuse box, lever; the rod given with `hold`), M10 + M24 (the phone call:
  handset lifted, `D1_10`, camera moves, door closed, gauge), M19 (ladder) and M20 (the
  climb, ending over the booth roof `int05fen01`), and, from on top of the handcar, the
  ride: holding Up moves the car along `U01_20.A3D`, the points send it onto
  `U01_20A.A3D` near frame 90, and at its last frame the fade and the load of `U02.x3d`
  follow (`traces/u01-ride-to-u02.png`, local). The siding clip must drive the train's
  parent dummy (its root animation); bound to the train object itself the car leaves
  the rails. The key (M07), door (M08) and rod (M14) clicks missed from the viewpoints
  tried (occluded or too far), not a handler failure.
- **Method:** `dev_commands` runs with `-d1` logs and snapshots; posted Up/Enter.
- **Confidence:** proven that the handlers and the ride work as specified; not compared
  against the original frame by frame.

### E-0200 — U00 load and start: U04 assets, U00 info/voices, `*Lunettes0` renames, sphere 3/1, talker `U04_03`, `sb01` then `OptionUser`
- **Binary/file:** `MissionMonet.exe`; `Data/U00/{SCENE.BIN,Infoobj.bin,Infoact.bin,Sound/*}`.
- **Evidence:** `U00_Load` (`0x0040a070`, `U00.cpp:0xf5`): maps `%sU04/Maps/`, script path
  `%s%s` (unit root + name), root `%sU04/`, vtable `+0x4c("s3_01", 1)` (unit ambient).
  `U00_Start` (`0x0040a1e0`, disassembly): `X3d_Scene_Get_Object("*Lunettes0")` → copy
  `*U04_81`, `+0x5c` = 1 (the `X3d_Object_Hide` flag, E-0048), kept at unit `+0x6dc`; again
  `*Lunettes0` → `*U04_80`; `+0x5c` = 1 on `*U04_63`, `*U04_31`, `*U04_44`, `*U04_05`,
  `*U04_53` (`0x0043ff0c..0x0043ff44`); root `%sU00/`, vtable `+8` (INFOOBJ/INFOACT,
  E-0072), root `%sU04/`, vtable `+0x2c`; camera `FUN_00419ce0(3.0)` (sphere radius `+0x64`)
  and `FUN_00419d00(1.0)` (Z offset); `+0x6c8`/`+0x6cc` hotspot/node `*U04_03`,
  `+0x6d0`/`+0x6d4` `*U04_32`; node paused, vtable `+0x28("U04_03", "", "$$$DUMMY.*visage",
  0, 8, "%sAnim/U04_03_Lunettes/")`, node running; camera (81.1334, 265.81, 15.0), yaw/pitch
  `0x409570a4`/`0x3fbc28f6` = 4.67/1.47; if `0x0046ed88` = 0: `RunFor(0)`,
  `U00_SayMonet("sb01", 0, 0)`, `SetAppMode(2)`, frame `OptionUser`. `U00_SayMonet`
  (`0x0040a5c0`): third argument ≠ 0 → root `%sU00/`, vtable `+0x54(line, 0, 100)` (op 101's
  player, group 2) and return; else, second argument ≠ 0 → save camera position, yaw, pitch,
  FOV and set (81.1334, 265.81, 15), 4.67, 1.47, FOV 90 (`0x42b40000`); node running;
  `Talkers_Say("U04_03", line)` (`0x004215f0`); `RunFor(0)` while `FUN_00414ed0(+0x178)`;
  restore. U00 overrides vtable `+0x48` (`U00_PlayVoiceFile`, `0x0040a4a0`, `U00.cpp:0x147`)
  with `%sU00/Sound/%s.wav`. Corpus: `U00/SCENE.BIN` ambient (255, 255, 255), scale 10.0,
  `#CAMERA#` FOV 90, 20, 40, 7; INFOOBJ 5 entries (`*U04_03` type 6, `*U04_32` 5,
  `*U04_36` 4 hidden, `*U04_43` 4, `*U04_80` 4 cursor 4); INFOACT M01 (trigger 8 on
  `*U04_80`: op 2, op 10 `TakeLunettes`, max 1), M02 (trigger 7 item `U04_80` on `*U04_03`:
  op 10 `DonnerLunettes`, max 2); `U00/Sound` holds 18 WAVs and no `.bin`; the EXE and
  `MissionD.exe` name only sb01, sb03, sb03_bis, sb04..sb11, sb14.
- **Method:** MCP decompile and disassembly; strings and floats with `pefile`/Python;
  `infoobj.py`, `infoact.py`, Python `wave`. Functions renamed in Ghidra.
- **Confidence:** proven.

### E-0201 — U00's tutorial: a hidden 10-s gauge carries the hint state; the frame hook replays lines, the input hook advances states
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `U00_UpdateFrame` (`0x00409850`, vtable `+0x1c`): `Scene_RenderFrame`; if
  `+0x704` = 0: set it, `U00_SayMonet(0x0046ed88 ? "sb03_bis" : "sb03", 0, 0)`,
  `FUN_0041a560(gauge, 10.0, 0, "deplace", 1)`, camera to the start pose, FOV 90. Else if
  gauge `+4` ≠ 0 and `FUN_0041a6c0(gauge, 0)` (fires without stopping: elapsed `+0xc` is
  not reset, E-0082), switch on gauge `+0x10`: 1 `sb04` (1, 0) → 1 `deplace`; 2/3/4/5 need
  `+0x6d8`: `sb06`/`sb05`/`sb07`/`sb08` with (1, 1) → 2 `Sauter` / 3 `Sauter` / 5 `Take2`
  (and `+0x6f0` = 1) / 5 `Take2`; 7: cursor mode (`DAT_0046ec14 +4`) = 1 → `sb09` (1, 1),
  7 `""`; else if `+0x6fc` = 0: `+0x6fc` = 1, stop (`FUN_0041a680`), if `+0x6d8` → 3 `""`;
  8: if `+0x700` = 0, `sb11` (0, 0) → 8 `""`. Restart is `FUN_0041a560(10.0, 0, label, n)`.
  `U00_ProcessTutorialKeys` (`0x00409b40`, vtable `+0x40`), key table `0x0046e7e0 + vk·4`:
  state 1 and Up/Down (`0x46e878`/`0x46e880`) → stop, `+0x6e4` = 1; state 2 and
  Left/Right/PgUp/PgDn (`0x46e874`, `0x46e87c`, `0x46e864`, `0x46e868`) → stop, `+0x6e8`
  = 1; `+0x6d8` and `+0x6e8` and not `+0x6f0` and state ≠ 4 → start 4 `Take`; Shift
  (`0x46e820`) and `+0x6d8` → `U00_JumpOffStone` and return; Space (`0x46e860`) →
  `+0x700` = 1, stop if state 8; `Scene_HandleInput`; not `+0x6d8` and `_stricmp(camera
  +0x3c name, "*U04_32")` = 0 → `U00_StepOntoStone`; `+0x6f0`, not `+0x700`, state ≠ 8 and
  `FUN_00415e40(Monet hotspot +0x70, eye)` < 2·scale → `FUN_00419bc0(1000, Monet object)`,
  `+0x6fc` = 1, `sb10` (0, 0), start 8 `""`. `U00_StepOntoStone` (`0x00409d10`): `+0x6d8`
  = 1; eye := stone hotspot `+0x70..+0x78` + (0, 0, 10.0); camera `+0x40` (can move) = 0,
  `+0x70` (collision) = 0; `FUN_00419bc0(0, "*U04_43")`; `+0x6ec` = 1; if not `+0x6e8`:
  start 2 `Tourner`. Hotspot `+0x70` is `X3d_Object_Get_Global_Position` at hotspot
  creation (`FUN_00420b40`). `U00_JumpOffStone` (`0x00409dc0`): `+0x6d8` = 0;
  `Camera_MoveTo(2000, (149.87, 60.56, −9.0), 0.427, π/2, keep)`; `+0x40` = `+0x70` = 1,
  `+0x3c` = 0; stop if state 2. No store to app `+0x484` between `0x004097e0` and
  `0x0040a720` (capstone scan of all `+0x484` stores). `OptionEntrenement` calls game
  `+4(0)` and sets `0x0046ed88` = 1 (E-0105's handler list).
- **Method:** MCP decompile; key slots decoded from the table base; floats with Python.
- **Confidence:** proven for the logic; the gauge labels' use is open (Q-0110).

### E-0202 — `TakeLunettes` starts state 7; `DonnerLunettes` plays `prend`/`MET`, `sb14`, then opens the Option menu
- **Binary/file:** `MissionMonet.exe`; `Data/U04/Anim/U04_03_Lunettes/`.
- **Evidence:** U00 vtable `+0x30` (`U00_DispatchClickActions`, `0x00409aa0`, created):
  after `FUN_0041b700`, drains the queue `+0x198`: `DonnerLunettes` → `0x00409e90`,
  `TakeLunettes` → `0x00409e50`. `U00_TakeLunettes`: stop, start 7 `""`, `+0x6f0` = 1.
  `U00_DonnerLunettes`: `FUN_004144b0(cursor, 0, 0, 0)`, `FUN_00414820(cursor, 0, 0)`,
  `+0x700` = 1, stop; `FUN_00420220(Monet node, "%sANIM/U04_03_Lunettes/prend.A3D",
  "monet", 1, 1)`, slot loop `+0x68` = 0; `Camera_MoveTo(1000, start pose, 4.67, 1.47,
  90)`; `RunFor(0)` until slot `+0x60`; `*U04_81` `+0x5c` = 0; same with `MET.A3D`;
  `U00_SayMonet("sb14", 0, 0)`; `RunFor(0)` until slot frame `+0x74` ≥ 50.0; `*U04_81`
  `+0x5c` = 0; until `+0x60`; `RunFor(2000)`; frame manager `+0xc0(0)` (Option, E-0105);
  `FUN_00414820(cursor, 1, 0)`.
- **Method:** function created and decompiled over MCP.
- **Confidence:** proven.

### E-0203 — Live: a new player lands at the start pose facing Monet; posted arrows did not move the camera
- **Binary/file:** `C:\MonetRun` (`run.ps1`, `send.ps1`, `snap.ps1`).
- **Evidence:** launch, 14 s, a new random name + Enter; snaps at +5 s and +25 s show the
  garden from the start pose with Monet centred in front of the terrace (identical frames).
  Right 0.8 s and Down 1.5 s (about +38 s), then six Down taps of 1 s every 3 s, with snaps
  after each batch and 25–30 s later: the view never changed.
- **Method:** one live run; `MissionMonet.exe` killed afterwards.
- **Confidence:** proven for the start pose; the keys' effect is unresolved (Q-0111).

### E-0160 — U02's vtable, load hook and start: ambient `s1_15`, six renames, three talkers, camera cut and an autosave
- **Binary/file:** `MissionMonet.exe`; `Data/U02/**`, `INSTALL/02_PR/Message.txt`.
- **Evidence:** constructor `0x00402af0`: vtable `0x00439468`, `+0x6e8` = `+0x6f0` =
  `+0x6fc` = `+0x6c8` = 0, `+0x6ec` = 10000. Vtable: `+8` `0x00404ad0` / `+0xc`
  `0x00404b50` read / write chunk `TIMEVENDEUSE` (`0x0043f730`: u32 `+0x6e8`, `+0x6ec`,
  `+0x6f0`, `+0x6fc`; `+0xc` is what the game save `0x00412e40` calls), `+0x10`
  `U02_OnLoadRenames` (`0x00402b60`, function created), `+0x14` `U02_StartUnit`
  (`0x00402d30`, created), `+0x1c` `U02_UpdateFrameLogic`, `+0x30`
  `U02_DispatchClickActions`, `+0x40` `0x0041b7f0` (`Scene_HandleInput`: no U02 input
  hook). `0x00402b60`: vtable `+0x4c("s1_15", 1)`, `XScene_124`, then
  `X3d_Scene_Get_Object` + strcpy: `*U02_01` → `*U02_06`, `lourde05` → `*U02_12` (object,
  and node list `+0x14("lourde05", 1)` name at node `+0xc`), `*U02_07` → `*U02_07b`, next
  `*U02_07` → `*U02_07a`, the first → `*U02_07`, `*ZonePlanc` → `*U02_13`, `*colplanch` →
  `*U02_14`. `0x00402d30`: `FUN_0041ae10`; vtable `+0x28` talkers ("U02_02", "",
  "$$$DUMMY.*U02Parle", 0, 8, 0), ("U02_03", …, "$$$DUMMY.*U_03Parle"), ("U02_04", …,
  "$$$DUMMY.*visage"); node/hotspot pairs `+0x6d0/+0x6d4` `*U02_02`, `+0x6e0/+0x6e4`
  `*U02_03`, `+0x6cc/+0x6f4` `*U02_05`, `+0x6d8/+0x6dc` `*U02_04`; actions `+0x430`
  (M08 exhausted) and not `+0x440` (M12) → `+0x50("d1_25", hotspot +0x70, 1)`; hotspot
  `*U02_01` object `+0x5c` ≠ 0 → `+0x114` = 1; if `a`: `FUN_00419520(122.626, 67.0605,
  52.529)`, `FUN_00419550(0.1, π/2)`, inventory `+0x90`/`+0xa8("U02_01P")`, game vtable
  `+0x10(FUN_0042a3c0(0x3eb), 0)`. `FUN_0042a3c0(n)` reads `Message.txt` beside the EXE
  and returns line `n`'s text up to `;` (1003 = "Automatic save"); game `+0x10`
  (`0x00412e40`) writes `%sGamesave%i` for slot 0 with that name. Corpus (`o3d.py` over
  `U02.X3D`'s `OBJECT=` files): `*U02_01` in `anim/U02_04/U02_04.o3d` and
  `anim/U02_03/U02_03.O3D` (loaded later), `*U02_07` in `Static/U02.O3d` and
  `Static/U02_07.o3d` (later), `*U02_08` in `Static/ruisseau.O3d`, `plncher01` in
  `Static/repo.o3d`, `lourde05` in `anim/porte.O3D`.
- **Method:** MCP decompile and capstone (strings and floats resolved); PE import table;
  `o3d.py`, `infoobj.py`.
- **Confidence:** proven for the calls; which duplicate gets renamed follows from the list
  order (Q-0090).

### E-0161 — U02's frame hook: stream fall, the seller's call timer, the magpie trigger, the gauge warning and expiry
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `U02_UpdateFrameLogic` (`0x00402f70`): after `Scene_RenderFrame`,
  `_stricmp(camera +0x3c name, "*U02_08")` = 0 → `U02_FallInStream` (`0x00404bd0`);
  `+0x6f0` = 0, `timeGetTime − +0x6e8 > +0x6ec` (unsigned) and voice `+0x178` silent →
  `+0x6e8` = now, `rand·3/0x7fff` 1 → `d1_12`, 2 → `d1_13`, else `d1_14`,
  `Talkers_Say("U02_03", …)` (a vector (1818, 70, 83) is built and unused); `+0x6fc` = 1
  and `FUN_00415e40((1280, −564, −7.15), eye) < 240` (`0x004394c4`) → suspend, `+0x6fc` =
  2, `+0x6c8` ?= `FUN_00420360(+0x6cc, "PieVoleur", 1)` (slot by name), `FUN_00420060(0)`,
  `FUN_00419bc0(400, clip +0x80)`, direction `X3d_Convert_From_Polar` of the X3D camera
  `+0x54/+0x58` normalised, target eye + 150·(d.x, d.y) (`0x004394c0`) with eye z,
  `FUN_00419620(eye, target, yaw, yaw, pitch, pitch, 1000, 0x00402f50)`, `+0x50("S1_17",
  eye)`, `FUN_00419bc0(0, …)` while clip `+0x74` < 240, `FUN_00421300(+0x6f4, 5)`, resume.
  `FUN_00419620`: N = ftol(ms · scene `+0x144` (fps) · 0.001), min 1; per step position
  += Δ/N, yaw/pitch += Δ/N, callback, tick, render, emitter volumes; final snap.
  `0x00402f50` = `Camera_FollowGround(eye)`. Gauge `+0x148` running: `DAT_0044261c` = 0
  and duration − 20000 < elapsed < duration − 10000 → flag = 1, `Say("U02_02", "d1_26")`;
  `FUN_0041a6c0(1)` → suspend twice, `+0x50("s1_22", eye)`, `Say("U02_02", "d1_27")`,
  `RunFor(0)` while `+0x178` or `+0x174` plays, game vtable `+0x14` (`FUN_004135b0`,
  E-0082). `DAT_0044261c` has no other writer. `0x00404bd0`: suspend, `+0x50("s1_19",
  eye)`, N = ftol(`+0x144`), per step channel `+0x16c..+0x16e` −= (c₀ − 0x5a)/N if ≥ 0
  else 0, `FUN_0041b2f0`, `RunFor(10)`; d = normalise(polar(camera `+0x34`, `+0x38`)),
  P = (eye.x + s·d.x, eye.y + s·d.y, eye.z − (camera `+0x5c` − 30.0)), camera `+0x70` =
  0, `Camera_Fall(eye, P)` (drops z by `FUN_00415e40(eye, P)`, 3-D), `Camera_MoveTo(800,
  P, 100, 0.5, 40)`, twice `Camera_MoveTo(600, none, yaw + 3.0, 100, 100)`,
  `FUN_0041bfd0(2000)`, game `+0x14`. Corpus: `SCENE.BIN` `#SCENE#` 255/255/255,
  scale 40.0; `s1_19.wav` 10.12 s.
- **Method:** capstone of `0x00402f70..0x00403337` and `0x00404bd0..0x00404e6f`; MCP
  decompile of `FUN_00419620`, `Camera_Fall`, `FUN_00420360`, `FUN_00420060`.
- **Confidence:** proven.

### E-0162 — U02 dispatcher and the clerk / inspector / seller / door / plank handlers
- **Binary/file:** `MissionMonet.exe`; `Data/U02/INFOACT.BIN`.
- **Evidence:** `0x00403340`: `FUN_0041b700`, then while `+0x1a4` drains the queue
  comparing, in order, `ClickControleur` `0x00403560`, `ClickGuichetier` `0x004035f0`,
  `Donner100FrsAGuichetier` `0x00403850`, `ReTake100Frs` `0x004039a0`, `ClickVendeuse`
  `0x00403b30`, `AcheterMarron` `0x00403bc0`, `PieVoleur` `0x00403d70`, `ClicDoor`
  `0x00404010`, `TakePlanche` `0x00404380`, `PoserPlanche` `0x004043b0`, `MarronToPie`
  `0x00404060`, `ClickRonfle` `0x00403790`, `Sonner` `0x00404440`, `AcheterTicket`
  `0x004046a0`, `TakeTicket` `0x00404800`, `MonterDansTrain` `0x00404890` (all renamed
  `U02_*`); nothing after the loop. `0x00403560`: actions `+0x814` (M01 count) = 1 →
  `Say("U02_02", "d1_15")`, cursor 5 on `+0x6d4`; else `rand·2/0x7fff` = 1 → `d1_15`,
  else `d1_16`. `0x004035f0`: `+0x818` = 1 → `d1_17` and cursor 5 on `+0x6dc`; = 2 →
  `d1_18`; else random 1 → `d1_17`, else `d1_18`; `Say("U02_04")`; `+0x6ec` = 15000,
  `+0x6e8` = now. `0x00403850`: suspend, `FUN_00420220(+0x6d8,
  "%sAnim/U02_04/RendreArgent.A3D", "RendreArgent", 3, 1)` (slot 3, active; `+0x68` = 0),
  hotspot `*U02_01`: `FUN_004212b0`, cursor 4, `+0x28("*U02_01", 1, 1)`, object `+0x114`
  = 0; `Say("U02_04", "d1_19")`; `+0x6e8` = now; cursor 0 on `+0x6dc`; `MoveTo(800,
  (2339.33, −116.49, 78), 1.62)`; camera `+0x44` = `+0x40` = 0; `FUN_0041e2a0(M16, 1)`;
  resume. `0x004039a0`: `FUN_0041e2a0(M16, 0)`, `FUN_004211d0("*U02_01")`, slot
  `RendreArgent` (or load it) `+0x70` = 1, running, camera `+0x44` = `+0x40` = 1, cursor 3
  on `+0x6dc`, `*U02_01` object `+0x114` = 1. `0x00403b30`: `+0x6ec` = 20000; if `+0x430`
  and not `+0x440` and `+0x860` > 0: `DAT_00442620` (no writer anywhere) → `d1_28`, else
  random 1 → `d1_29`, else `d1_30`, `Say("U02_03")`, `+0x6e8` = now. `0x00404010`: node
  `*U02_12` frame < 2.0 → `+0x70` = 0, `FUN_00420100(50.0, 1)`; else `+0x70` = 1, run to
  1.0. `0x00404380`: `_stricmp(camera +0x3c name, "plncher01")` ≠ 0 →
  `FUN_004211d0("*U02_07")`. `0x004043b0`: `+0x28("*U02_07a", 1, 0)`, `FUN_004212b0`,
  cursor 0 on `*U02_13` and `*U02_07a` by name, `X3d_Scene_Get_Object("*U02_14")`
  `+0x118` = 0 (a `*U02_08` lookup before it is unused). `0x00403790`: `+0x860` (M20
  count) = 1 → cursor 3 on `+0x6e4`; = 3 → cursor 0 on `+0x6dc`; `+0x50("d1_25_2",
  hotspot +0x70)`; loop `RunFor(0)` + vtable `+0x40` while `+0x174` plays and
  `strstr(emitter +0x18, "d1_25_2")`; `0x004036d0`: `+0x184` = `FUN_00414c80(4, s·50)`,
  `SoundEmitter_Play("%sSound/d1_25.wav", +0x6dc +0x70, 1)`. `FUN_00420220(node, path,
  name, slot, active)` puts the clip in that slot (`FUN_004202f0`), inheriting the node's
  fps `+0x78`, loop `+0x68` and paused `+0x60`; `FUN_00416180(a, b, exact)` is
  case-insensitive equality or (exact 0) "a contains b".
- **Method:** capstone of `0x00403340..0x004047f2` (strings, floats); MCP decompile of
  `FUN_00420220`, `FUN_004202f0`, `FUN_004211d0`, `FUN_004212b0`, `FUN_00421300`,
  `FUN_00416180`; `infoact.py --file`.
- **Confidence:** proven.

### E-0163 — `AcheterMarron`, `PieVoleur`, `MarronToPie`: the seller's change, the magpie, the 180-s gauge and the clerk's sleep
- **Binary/file:** `MissionMonet.exe`; `Data/U02/Anim/U02_03`, `U02_04`, `U02_05`.
- **Evidence:** `0x00403bc0`: suspend, `+0x6ec` = 30000, `+0x6f0` = 1, camera `+0x40` =
  `+0x44` = 0, `MoveTo(1000, (1859.8, 73.65, 78.929), 3.1)`, cursor 4 on `*U02_06`,
  `+0x6f8` = `FUN_00420220(+0x6e0, "…U02_03/ACTION01.A3D", "DonnerMarron", 1, 1)`, its
  `+0x7c` := `FUN_0041c380(+0x7c, "*U02_03")` (sub-animation by name, depth first),
  `+0x68` = 0, `+0x78` = 8.0, running; `Say("U02_03", "d1_22")`; `+0x6e8` = now;
  `RunFor(0)` until `+0x60`; `FUN_0041e2a0(M06, 1)`; resume. `0x00403d70`: node `+0x6cc`
  `FUN_004200c0(30.0)`, `X3d_Object_Unhide(obj, 1)`, `FUN_00420080(1)`, running, `+0x78`
  = 40.0; `DonnerMonnaie` = `ACTION02.A3D` slot 2, sub-animation `*U02_03`, `+0x68` = 0,
  `+0x78` = 50.0, frame 1.0, running; yaw/pitch saved; camera `+0x70` = 0; loop
  `RunFor(0)` until magpie `+0x74` > 145.0 (`0x004394c8`), saying `d1_23_1` once when the
  clip's frame > 60.0; `+0x50("S1_17", eye)`, `Say("U02_03", "d1_23_2")`; `LookAt(0)`
  while < 240.0; camera `+0x70` = 1; `MoveTo(300, none, yaw, pitch, 100)`; `+0x6e8` =
  now; clip `+0x78` = 80.0, `RunFor(0)` until paused; `FUN_00420080(+0x6e0, 1)`; camera
  `+0x40` = `+0x44` = 1; `+0x6c8` = `FUN_00420220(+0x6cc, "…U02_05/Action02.A3D",
  "PieVoleur", 1, 1)`, `+0x68` = 0, `+0x78` = 30.0, `FUN_00420060(1)` (paused), frame
  (anim `+0x38` first frame) + 10.0; `+0x6fc` = 1; `+0x6f0` = 0. `0x00404060`: `+0x6ec` =
  60000, suspend, `FUN_004212b0(+0x6f4)`, `+0x28("*U02_06a", 1, 1)`, node running,
  `RunFor(300)`, `OnBarriere` = `ACTION03.A3D` slot 1 (`DAT_00442624`), `+0x68` = 1,
  `+0x78` = 20.0, `LookAt(500)`, `RunFor(500)`, `+0x28("*U02_09a", 1, 1)`, node running,
  `+0x68` = 0, `S'envoler` = `ACTION04.A3D` slot 1, `RunFor(0)` while frame < 29.0,
  `+0x28("*U02_06a", 0, 1)`, while frame < last − 30: `LookAt(0)`, once frame > 80.0
  `+0x50("s1_17", eye)`; `+0x6e8` = now; resume; P = eye − (0, 0, 5·s); app `+0x484` =
  0; `RunFor(0)` + `+0x40` for 2000 ms of `timeGetTime`; `+0x48("d1_24", P)`;
  `FUN_0041a560(180.0, 1, "", 0)`; `RunFor(0)` + `+0x40` while `+0x174` plays; app
  `+0x484` = 1; `0x00403a70`: `Sleep` = `U02_04/ACTION01.A3D` slot 1, running, `+0x6c` =
  1, `+0x68` = 0, frame 85.0, `FUN_00420140(0x55, 0x56)`, `+0x78` = 1.0,
  `U02_StartSnoreEmitter`, cursor 2 on `+0x6dc` and `*U02_10`. `FUN_004200c0` clamps to
  anim `+0x38`/`+0x3c` (first/last); `FUN_00420080` on a base node sets enabled and
  active slot 0. Corpus (`a3d.py`): `U02_03/ACTION01` 1..20, `ACTION02` 1..370,
  `U02_05/ACTION01` 1..370, `ACTION02` 1..700, `ACTION03` 642..830, `ACTION04` 1..250,
  `U02_04/ACTION01` 0..171; INFOOBJ `*U02_05` hidden, paused, 30 fps, not looping.
- **Method:** capstone; MCP decompile of `FUN_0041c380`, `FUN_00420080`, `FUN_004200c0`,
  `FUN_00420140`, `FUN_00420100`.
- **Confidence:** proven.

### E-0164 — `Sonner`, `AcheterTicket`, `TakeTicket`, `MonterDansTrain`: U02 ends with `LeHavRou.AVI` and unit 3
- **Binary/file:** `MissionMonet.exe`; `Data/Video/LeHavRou.avi`, `S6_1.wav`.
- **Evidence:** `0x00404440`: suspend; node list `+0x14("*U02_10", 0)` (contains-match;
  the node is `$Z$*U02_10`) running; cursor 5 on `+0x6dc`; eye, yaw, pitch, FOV (camera
  `+0x10`) saved; `LookAt(500, bell)`; `FUN_00414dc0(+0x184)`, delete, `+0x184` = 0;
  `+0x50("SIREN", eye)`; `MoveTo(2000, none, 100, 100, 60)`; `RunFor(0)` until the bell
  `+0x60`; clerk slot 1 (`+0x6d8 +0x18c`) `FUN_00420170` (restore range), `+0x6c` =
  `+0x68` = 0, `+0x78` = 80.0; `FUN_00419600(saved FOV)`; `FUN_004194f0((2334.25, −100,
  78.9))`, `FUN_00419550(1.54, π/2)`; `MoveTo(1000, none, 100, 100, 60)`; `RunFor(0)`
  until slot 1 pauses; `FUN_00420080(+0x6d8, 1)`; `Say("U02_04", "D1_31")`; `RunFor(0)`
  while `+0x178`; `FUN_004194f0(saved eye)`, `FUN_00419550(saved yaw, pitch)`; `+0x6e8` =
  now; cursor 0 on `+0x6e4`; resume. `0x004046a0`: suspend, `MoveTo(1400, (2362.52,
  −93.43, 78.9), 1.94, π/2)`, `Say("U02_04", "d1_32")`, `+0x6e8` = now, `DonnerTicket` =
  `U02_04/ACTION02.A3D` slot 2, `+0x78` = 30.0, `+0x68` = 0, frame 15.0, `FUN_004212b0`,
  cursor 0 on `+0x6dc`, `RunFor(0)` while frame < 100.0, `+0x50("s1_20", eye)`,
  `+0x28("*U02_11", 1, 1)`, resume. `0x00404800`: slot 3 (`+0x194`) or load
  `RendreArgent` into it; frame := anim `+0x3c`, `+0x68` = 0, `+0x70` = 1,
  `FUN_004201c0(node, 3, 1)`. `0x00404890`: suspend, `FUN_0041e2a0(M01, 0)`,
  `FUN_0041a680(gauge)`, `FUN_004212b0`, `LaisserEntrer` = `U02_02/ACTION02.A3D` slot 1,
  `+0x68` = 0, `+0x78` = 30.0, `Say("U02_02", "d1_33")`, `+0x6e8` = now, `RunFor(0)`
  until `+0x60` or `GetAsyncKeyState(VK_RETURN)`, `MoveTo(2000, (1413.16, 219.05, 78.93),
  4.55)`, twice z += 5.0 with `MoveTo(1000, …, 4.55)` + `RunFor(200)`, `MoveTo(2000,
  (1404, 293, 88.036), −1.62)`, `+0x50("s1_22", eye)`, `RunFor(0)` while `+0x178` or
  `+0x174`, `PlayVideo("LeHavRou", "s6_1", 0, 1)`, game vtable `+4(3)`. `PlayVideo`
  (`0x00417030`) takes four cdecl arguments: AVI name, WAV name (`[esp+0x210]`, used by
  `%sVideo/%s.wav` when non-empty), redraw (`[esp+0x214]`: call scene `+0x1c` after),
  stop group 2 (`[esp+0x218]`); U01 passes `("Prologue", "Prologue", 0, 1)` (refines
  E-0035's three-argument reading). Corpus: `LeHavRou.avi` IV41, 640×480, 66,667 µs/frame,
  496 frames (33.07 s); `S6_1.wav` 22,050 Hz mono 8-bit, 33.0 s.
- **Method:** capstone; MCP decompile of `FUN_00420170`, `FUN_00419600`, `FUN_004194f0`,
  `FUN_004201c0`, `FUN_004163b0`, `FUN_00414dc0`, `Camera_MoveTo`; AVI header and
  Python `wave`.
- **Confidence:** proven.

### E-0165 — U02 corpus: INFOACT ids and conditions, INFOOBJ, clips and sounds used by U02.cpp
- **Binary/file:** `Data/U02/INFOACT.BIN`, `INFOOBJ.BIN`, `SCENE.BIN`, `U02.X3D`,
  `Anim/**`, `Sound/*.wav`.
- **Evidence:** `infoact.py --file`: ids 1..8, 12..21; conditions M02 `!M12`, M03/M04
  `!M05`, M06/M19 `FALSE`, M12 `M08`, M13 `M12`, M14 `M13`, M20 `M08 & !M12`, others
  `TRUE`; max 1 for M05, M06, M08, M12, M13, M14, M18, max 3 for M20. `infoobj.py`: 17
  hotspots `*U02_01`..`*U02_14`, `*U02_06a`, `*U02_07a`, `*U02_09a`; types 6 for
  `*U02_02..04`, 5 for `*U02_05`, `*U02_06a`, `*U02_09a`, `*U02_10`, `*U02_12`; hidden
  at start `*U02_01`, `*U02_05`, `*U02_06a`, `*U02_07a`, `*U02_09`, `*U02_09a`, `*U02_11`,
  `*U02_14`. `U02.X3D`: characters `U02_04` (clerk, `attente.a3d`), `U02_02`
  (inspector), `U02_03` (seller), `U02_05` (magpie, `ACTION01.a3d`), `porte`, `U02_10`,
  `U02_06a`, `U02_09a`. `SCENE.BIN`: scale 40.0, `#CAMERA#` FOV 90, radius 20, Z offset
  40. Sounds (Python `wave`): `s1_15` 28.11 s, `d1_25` 8.22 s, `d1_25_2` 6.82 s, `SIREN`
  2.52 s, `s1_17` 2.65 s, `s1_18` 1.79 s, `s1_19` 10.12 s, `s1_20` 0.13 s, `s1_22` 6.77 s,
  `d1_12`..`d1_33` 1.1–8.7 s (lip `.BIN` for all but `d1_25`, `d1_25_2`).
- **Method:** the parsers named; Python `wave`.
- **Confidence:** proven.

### E-0180 — Save files are the `.BIN` chunk container, written by a mirror of the reader
- **Binary/file:** `MissionMonet.exe`; `Save/` samples of two runs (`traces/save/run0`,
  `run1`, local).
- **Evidence:** the stream object (`FUN_00414f10`, 0x694 bytes) opens with mode `rb`/`wb`
  (`FUN_00414f70`, `0x004411b8` / `0x00441378`); writing: `FUN_00415090` begins a chunk
  (`sprintf("#%s#")`, `0x0044137c`, copied with its NUL into a 20-byte table name, offset =
  `ftell`, size 0; refuses a second begin before the end), `FUN_00415340` `fwrite`s and adds
  to the chunk size, `FUN_00415180` ends it, `FUN_00415000` appends the table (count · 0x1c
  bytes from `+0x114`) and the u32 count. The table buffer holds (0x68c − 0x114) / 0x1c =
  50 entries. Reads (`FUN_004153a0`) fail past the current chunk's end, which the
  variable-length readers use as their loop end. `savegame.py`: 2/2 `Gamesave.*` and 7/7
  `*.bin` samples parse through `binchunk.parse`, every payload consumed; `--selftest`.
- **Method:** MCP decompile; validator over the samples.
- **Confidence:** proven.

### E-0181 — Players and settings: `Info.bin` `CURRENT`, `User_<i>/Info.bin` `USERINFO`, `InfoPara.bin` `FILTER`
- **Binary/file:** `MissionMonet.exe`; samples as E-0180.
- **Evidence:** player list `DAT_0046ec10`: `FUN_00413910` reads `CURRENT` (u16, via
  `FUN_00413ee0`, `%s/Info.bin` `0x004411f4` in the save root app `+0x36e`), scans
  `%sUser_*` (`0x004411e8`) folders, index = `atoi` after the last `_`, reads `USERINFO`
  (`0x004411cc`) name[64] into `+0xce + 64·i` and u16 into `+0x198e + 2·i`, counts in
  `+6`, then selects `CURRENT` (`FUN_004140b0`: stores the index, rewrites `CURRENT`
  with `FUN_00413fd0`, rebuilds the save list `XGameList` for `%sUser_%i//`).
  `FUN_00413b40` (new player) `_mkdir`s `%sUser_%i` (`0x00441228`), logs `File Copy: %s\*.*`
  to `%sInstall.log` when present, writes `USERINFO` (name, u16 0); `LUser_SelectUser`
  passes the player count as the index. `Game_WriteSave` ends with `FUN_00413d70`, which
  rewrites `USERINFO` with the game's unit number (`+0x160`); its only reader is
  `FUN_00414150`, called from `0x00425c24` (in `0x00425c10`). `InfoPara.bin`
  (`0x004415c8`): startup (`0x004174a0`, `MessageToUser.h:34`) writes `FILTER` from
  `DAT_0046ec00 +0x20` when missing, else reads it and on change sets D3D render states
  0x11 and 0x12 to 1 (value 0) or 2; exit (`0x004172a0`) rewrites it when it changed.
  Samples: `CURRENT` 0 and 1; `FILTER` 1; `USERINFO` `Player's nameName` with 0, and 1
  after a save in U01.
- **Method:** MCP decompile; samples.
- **Confidence:** proven.

### E-0182 — Save and load: `Gamesave.<slot>`, chunk order, restore through `LoadUnitScene(name, 0, stream)`
- **Binary/file:** `MissionMonet.exe`; `traces/save/run1/User_0/Gamesave.1`, `.3` (local).
- **Evidence:** game vtable `0x00439894`: `+0xc` `Game_LoadSave` (`0x00412d00`), `+0x10`
  `Game_WriteSave` (`0x00412e40`). Write: slot > 99 → 0, path `%sGamesave.%i`
  (`0x0044110c`) in the save list's `+0x1a5c`; chunk `GAME` (`0x004410f8`): name 0x40
  (game `+8`), u16 `+0x160`, scene 0x14 (`+0x14c`); scene vtable `+0xc`; `PorteF` `+0x9c`
  (strip view 200, `+0x11c` = `0x00431fc0`, chunk `PORTEF`); close; `FUN_00413d70`. Load:
  name `Game%i`, open, `GAME` into the same fields, `PorteF +0xa0` (strip `+0x120` =
  `0x00432070`: clear, then add names), `LoadUnitScene(+0x14c, 0, stream)` (pushes at
  `0x00412dfe..0x00412e07`), close. `LoadUnitScene` then sets game `+0x164` = 0, `+0x168` =
  1, `+0x160` = unit, app `+0x488` = 1. Scene vtables (`+8` restore / `+0xc` write): base
  `0x00439934` `Scene_RestoreState` `0x0041d490` / `Scene_WriteState` `0x0041d650`; U01
  `0x00402a30`/`0x00402a90` (`TRAIN_CHANGED`), U02 `0x00404ad0`/`0x00404b50`
  (`TIMEVENDEUSE`), U04 `0x0040b2c0`/`0x0040b330` (`PARAMS` `0x004400e0`: `+0x6ec`,
  `+0x6e8`, `+0x6e4`), U06 `0x00410cf0`/`0x00410d10` (base only), U07
  `0x004117b0`/`0x00411800` (`PLANCHE` `0x00440c74`: `+0x6c8`); U00, U03, U05, U33, U50
  use the base. Base start `0x0041ae10` calls `+8(stream)` then `+0x2c`; `U01_Start`
  with a = 0 calls `+0x4c("U01", 1)` instead of the prologue, then sets the sphere offset
  and calls `0x0041ae10`. Writer order in `Scene_WriteState`: `SCENE`, cursor
  (`FUN_00414c20`), actions (`FUN_0041eb20`), camera (`FUN_00418890`), `OBJECTS`
  (`FUN_0041d6f0`), `ANIMATIONS` (`FUN_00420760`), gauge (`FUN_0041a820`); restore order in
  `Scene_RestoreState`: `SCENE` (`FUN_0041b2f0`), cursor (`FUN_00414bc0`), camera
  (`FUN_004187b0`), `Scene_LoadObjectInfo(stream)`, `ANIMATIONS` (`FUN_00420410`), gauge
  (`FUN_0041a790`), `FUN_00414960(cursor, 0)`, `Scene_LoadActions`, actions
  (`FUN_0041ea90`). Runtime: saving on the first row wrote `Gamesave.1` (10,552 bytes,
  chunks `GAME SCENE CURSOR ACTIONS CAMERA OBJECTS ANIMATIONS TRAIN_CHANGED PORTEF`);
  loading it from `OptionLoad` put the camera back at −466.36, −452.495, 30.48, 4.7,
  1.5708 (`camera.ps1`) with the mayor holding out the card (`traces/save/s7-loaded.png`).
- **Method:** MCP decompile; capstone; one live run (`to_u01.sh`, Escape, Yes, OK, a second
  save, Main menu, Load, OK).
- **Confidence:** proven.

### E-0183 — Scene chunk payloads: cursor, action tables, camera, hotspots, animation slots, gauge, inventory
- **Binary/file:** `MissionMonet.exe`; `Gamesave.1`.
- **Evidence:** `SCENE`: scene `+0x16c`, 4 bytes (r, g, b to the ambient). `CURSOR`
  (`0x00441358`): cursor `+0x4d8` (30), `+0x4d4`, `+0x4d0`; `FUN_00414910` (from
  `SetAppMode` and two others) sets them to image `+0x2c`, 1, 1 when mode `+4` = 1;
  `FUN_00414960` restores (`FUN_00414540(mode, image)`) and clears `+0x4d0`. `ACTIONS`
  (`0x00441c14`): manager (scene `+0x198`) `+0x410` (0x400), `+0x810` (0x400), then for
  each non-null `+0x10[id]`, id 0..255, action `+0x368` (0x100, the condition, set by
  `FUN_0041e020` from record `+0x22`); `FUN_0041e2e0` treats `+0x410[id]` ≠ 0 as not
  runnable and passes `+0x410` to `EvalActionCondition`; `FUN_0041e320` increments action
  `+0x364` and stores it in `+0x810[id]`, `FUN_0041e3a0` sets `+0x410[id]` = 1 at
  `max_runs`; `Scene_LoadActions` copies the tables into `+0x360/+0x364` only when
  `+0x810[id]` > 0, and it runs before the chunk is read. `CAMERA` (`0x00441668`): camera
  `+0x14` (16 bytes), `+0x34`, `+0x38`, `+0x64`, `+0x68`, `+0x40`, `+0x44`, `+0x70`,
  `+0x5c`; the reader then calls `FUN_00419520`, `FUN_00419550` and
  `X3d_Sphere_Set_Position`. `OBJECTS`: `FUN_0041d6f0` reloads `INFOOBJ.BIN` and per
  record `FUN_00421170` writes object cursor (`+0x128`), `+0x5c` == 0 and, for the node of
  that name, `+0x74`, `+0x60`, `+0x68`. `ANIMATIONS` (`0x00441b94`): per node reachable
  through `+0x50` with `+0x7c` set, name starting `*` and `+0x1c8` ≠ 0: name `+0xc` (64),
  `+0x1c8`, `+0x1ca`, then per non-null slot 1..15 of `+0x188`: u16 slot, `+0x84` (260),
  `+0xc` (64), `+0x64`, `+0x60`, `+0x68`, `+0x6c`, `+0x70`, `+0x74`, `+0x78`, anim
  `+0x38`, `+0x3c`, `+0x1cc`, `+0x1d0`; the reader finds the node by name (list `+0x14`),
  cuts the path after `Data` (`0x00441610`) + 1 and prefixes the data root (app
  `+0x26a`), `FUN_00420220(path, name, slot, +0x64 value)`, then the remaining fields, and
  the active slot. `JAUGE` (`0x00441760`): gauge `+0x12` (30), `+0x34`, `+8`, `+0xc`,
  written only while `+4` ≠ 0; reading sets `+4` = `timeGetTime` when `+0xc` > 0.
  `PORTEF` (`0x00442584`): strip `+0x34` (last index, −1 without a list, `0x004348b0`),
  then each item's name (30). Sample values: ambient 255, 255, 255; exhausted[1] = 1; 23
  condition blocks (U01 `INFOACT.BIN` has 26 records); camera can move 0, can turn 0,
  collide 1, eye height 60, sphere 20 / 37; 25 hotspots; one node `*U01_02` with slot 1
  `GiveCard` (`…/U01_02/Action03.A3D`, paused, frame 25, fps 15, frames 1..25); no gauge;
  `PORTEF` `U02_01P`. Bears on Q-0091 (slot clips survive a save when their node is a
  `*` node).
- **Method:** MCP decompile; capstone; `savegame.py --dump`.
- **Confidence:** proven for layout and order; `unk_1cc`/`unk_1d0` and the traversal limit
  are Q-0101.

### E-0184 — `OptionSave` / `OptionLoad`: slot lists, name edit, OK handlers
- **Binary/file:** `MissionMonet.exe`; `Data/2DFRA/OptionSave.fra`, `OptionLoad.fra`;
  `INSTALL/02_PR/Message.txt`.
- **Evidence:** `RegisterFrameCommands` pushes `OptionSelectSave` → `0x0042b200` (option
  screen `+0x40` = `0x00427470`), `OptionSelectGame` → `0x0042b1e0` (`+0x3c` =
  `0x00427280`), `OptionSave3D` → `+0x44` (`0x004275b0`: close, `+0xc4`),
  `OptionSaveSommaire` and `OptionScreen` → `0x0042b490` (`+0x38`, the Option menu),
  `SaveQuit` → `0x0042b160` (`+0x20`, `OptionQuitter`). `0x00427470`: slot = save list
  (`DAT_0046ec74`) `+0x12c` (= `+0x11c`), name = view 11 text, `Game_WriteSave`,
  `XGameList_59`, list refresh, then views 2, 3, 5: the bitmap name's character 5 before
  the end (`…D.BMP`) := `N`. `0x00427280`: slot = load list (`DAT_0046ec70`) `+0x13c`
  (`0x004280f0`: the `+0x11c`-th used slot), −1 → nothing, else `Game_LoadSave`, close,
  `+0xc4`. `XGameList_59` (`0x004136b0`, `XGameList.cpp:59`): clears 99 used flags
  (`+0x10`) and names (`+0x19c`), scans `%sGamesave.*`, slot = `atoi` after the last `.`,
  `fread` 0x40 bytes from offset 0 as the name, newest by `ftLastWriteTime.dwLowDateTime`
  into `+8` (default 1), count `+0xc`. Save list `#SAV` (`0x004282b0`): 98 rows
  (`+0x8c` = 32 · 0x62); iterator `0x004283f0` steps the slot and turns 0 into 1; initial
  selection `0x00428450` = first free slot from 1 (< 98), scrolled into view. Load list
  `#LOA` (`0x00428010`): iterator `0x004280b0` skips unused slots; rows = count.
  Row drawing `0x00427b60`: rows 32 px (`DAT_004421d0`), width `+0x1c` − 38
  (`DAT_004421d4`), `sprintf("%i", slot + 1)` + `" - "` (`0x00442258`) + name, or message 1
  (`FUN_0042a3c0(1)`, `Message.txt` beside the EXE: `Empty`); `SetTextColor` 0x5ac4f7 for
  the selected row else 0xebba87, `DrawTextA` flags 0x925; surface colour key 0x502020
  (`LOptionScreen.cpp:588`). `Message.txt`: 300 `Save without name`, 301 `Player's name`.
  Runtime (`traces/save/s2`..`s7`, local): the save screen showed rows `2 - Empty` …
  `10 - Empty`, the first highlighted, edit `Save without name`, Back/Main menu/Quit dim;
  typing ` A` and OK wrote `Gamesave.1` named `Save without name A` and brightened the
  three buttons; clicking the third row and typing `B` wrote `Gamesave.3` named
  `Save without name AB`; the load screen listed `2 - Save without name A` and
  `4 - Save without name AB`, none selected, OK dim until a row was clicked.
- **Method:** MCP decompile; capstone; `fra.py`; one live run (the one of E-0182).
- **Confidence:** proven.

### E-0185 — The players list: rows as the save lists; a click copies the name into the edit
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `#USc` (`0x00429510`, list `DAT_0046ec78`, vtable `0x0043a784`): iterator
  `0x00429eb0` skips indices whose used flag (player list `+8 + 2·i`) is 0; draw
  `0x00429bf0` uses row height `0x00442268` = 32, width − 38 (`0x0044226c`), `"%i"` +
  `" - "` + name, the same two text colours, `DrawTextA` 0x925, colour key 0x502020. Click
  `0x00429f10`: row → `+0x11c`, redraw, `+0x140` = `0x0042a050`: walk to the row-th used
  player and set view 11's text to its name, then `+0x144` = `0x0042a0e0` (edit changed):
  empty text → OK view (id 2) bitmap `…N`, no selection; else `…M`, select the row whose
  name matches (`+0x138`) and scroll to it. `LUser_SelectUser` is reached only through the
  `SelectUser` command.
- **Method:** capstone of the methods named.
- **Confidence:** proven for the logic; the number printed before the name (the counter
  passed to `sprintf` at `0x00429d72`) is not traced (Q-0102). Answers Q-0061 except the
  scroll bar.

### E-0204 — The take step's item is six characters of the hotspot name after its first
- **Binary/file:** `MissionMonet.exe`; `Data/U02/INFOACT.BIN`.
- **Evidence:** the take routine `FUN_004211d0` (called by INFOACT op 2 at `0x00421270`)
  looks the hotspot up by name (vtable `+0x14`), hides it (`+0x28`), then
  `FUN_00416140(hotspot + 0xc, 1, 6, buf)` copies 6 characters of the hotspot's name from
  index 1 and appends the string at `0x004414cc` before setting the cursor
  (`FUN_00414540`). U02's M18 takes from `*U02_09a` (op 2 arg `U02_09`) and M13 then
  expects item `U02_09`; the engine, using the whole name, looked for a cursor image
  `U02_09a` that the EXE resources lack. Every other op 2 in the corpus has a
  7-character hotspot name, so the truncation only shows here.
- **Method:** Ghidra decompile and disassembly of `0x004211d0`; engine run.
- **Confidence:** proven for the substring; the appended suffix is the cursor-image `C`
  of `interaction.md` (not re-read here).

### E-0250 — Action run counts and exhausted flags are per id, so U01's second `M20` record and `M11`/`M22`-on-`*U01_01` never run; the climb repeat is the click handler's post-queue check
- **Binary/file:** `MissionMonet.exe`; `Data/U01/INFOACT.BIN`.
- **Evidence:** `FUN_0041e2e0` (runnable) reads the exhausted flag at action manager
  `+0x410 + id·4` (`id` = record `+8`) before `EvalActionCondition`; `FUN_0041e320` counts
  at `+0x810 + id·4` (E-0073). U01's INFOACT has two records with id 20 and two with id 22
  (`infoact.py --file Data/U01/INFOACT.BIN`). The first `M20` (trigger 7, `max_runs` 1)
  exhausts id 20, which also blocks the second `M20` (trigger 8 on `*U01_09`, condition
  `M20`). `M11` needs `M10` exhausted, but `M10` has `max_runs` 100 (never exhausted);
  `M22` on `*U01_01` needs `M11`. U01 vtable `+0x30` is `U01_DispatchClickActions`
  (`0x00401d30`), the click handler: `FUN_0041b700` (hover, then trigger when scene
  `+0x13c` ≠ 0), drain the queue, then with a hovered hotspot the check of E-0084
  (id 20 exhausted, hovered `*U01_09`, camera `+0x1c` < 100) → `MonterSurToit`. So the
  check runs on every click on `*U01_09`, whatever the click triggered; after the first
  climb the eye is at z 139, so it does not repeat at once. Vtable `+0x34` is
  `FUN_00412aa0` (returns 1) and `+0x44` the generic `Scene_PickHover` (`0x0041b540`): U01
  has no hover hook of its own.
- **Method:** MCP decompile of the functions named; `infoact.py`.
- **Confidence:** proven.

### E-0251 — A held item goes back to the bar on a unit change and on the load screen; a click with no matching action keeps it; cursor kind 0 does not stop a click
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `FUN_004149e0` (cursor mode 1 or 2: stop the blink, strip `+0xa8(cursor
  +0x4a)` = add the `…P` name, cursor mode 0 kind 0) is called from `App_OnEscape`
  (`0x00416559`), from game vtable `+4` "go to unit n" (`0x00412ffa`, after the
  load-pending test at `0x00412fd4`) and from game vtable `+0x14` `FUN_004135b0`
  (`0x004135c6`, the "caught" exit to `OptionLoad`, E-0082), which then sets game `+0x168`
  = 0, cursor kind 0 and resumes if cursor `+0x448` = 0. `Actions_TriggerForHotspot`
  (`0x0041e3f0`) does nothing when `FUN_0041e180` finds no runnable action: the cursor and
  a held item stay as they are. Neither it nor `FUN_0041b700` reads the hotspot's cursor
  kind: a hotspot with kind 0 (e.g. `*U01_18`, `*U01_01` after the first phone call)
  still triggers its actions. `FUN_0041e900` chains records with the same hotspot type
  and hotspot (by `FUN_0041e240`, name equal or contained) in file order.
- **Method:** MCP decompile and disassembly of the functions named.
- **Confidence:** proven.

### E-0252 — The take step hides its target without collision; take and use-up act on the action's target
- **Binary/file:** `MissionMonet.exe`; `Data/U01/INFOACT.BIN`.
- **Evidence:** `Action_RunStep` case 2 calls `FUN_004211d0(action +0xb0, "")` and case 3
  `FUN_004212b0(action +0xb0)`; `+0xb0` is the target hotspot (`+0xac` the hotspot,
  used for positions by ops 1 and 13). `FUN_004211d0`: cursor kind 0 (`FUN_00421300`),
  hotspot vtable `+0x28("", 0, 1)` = `0x00421050` hide with `+0x118` = 1 (no collision,
  E-0088), cursor mode 1 with the item name (E-0204), manager `+0xb8()` `+0x94` (show the
  bar). `FUN_004212b0`: stop the blink (`FUN_00414ba0`), cursor mode 0 kind 0 (the item
  is gone, not stored), target cursor kind 0, hide the bar (`+0x98`). In U01 only `M20`
  has a target other than its hotspot: use-up clears `*U01_10`'s kind, `*U01_09` keeps 5.
- **Method:** MCP decompile; `infoact.py`.
- **Confidence:** proven.

### E-0253 — U01's items: three are used up in U01, three leave for later units
- **Binary/file:** `Data/U0*/INFOACT.BIN`, `Data/2dbit`.
- **Evidence:** `infoact.py` over every unit: U01 takes (op 2) `*U01_04` (M02), `*U01_05`
  (M07), `*U01_12` (M14), `*U01_19` (M18), `*U01_08` (M19). Trigger-7 actions with these
  items: `U01_05` U01 M08 (door), `U01_12` U01 M15 (fuse box), `U01_08` U01 M20 (climb),
  each with op 3; `U01_19` U03 M30 (`*U03_09`), `U01_04` U04 M03 (`*U04_03`); the
  banknote `U02_01` U02 M03 / M05. `2dbit` has `…C` and `…P` images for all six.
- **Method:** `infoact.py --file` on each unit; directory listing.
- **Confidence:** proven.

### E-0230 — `U00_Start` first runs U04's name fix-ups (`U04_FixObjectNames`): renames, hides, no-pick and no-collision boxes
- **Binary/file:** `MissionMonet.exe`; `Data/U00/U00.x3d`, the `Data/U04/**/*.o3d` it loads.
- **Evidence:** `U00_Start` (`0x0040a1e0`) calls `0x0040e720` (renamed
  `U04_FixObjectNames`) with the X3D scene before its own renames. Other callers:
  `0x0040a7c6` (the unit whose constructor `0x0040a720` installs vtable `0x00439630`) and
  `FUN_004129a0`. Body, in order, each by `X3d_Scene_Get_Object` (newest-first lookup,
  u01.md): `*U04_37` → `*U04_44`, then the next `*U04_37` → `*U04_63`; `*U04_26`
  animation + object → `FUN_0041c280(scene, anim, obj, "")`; `*U04_05t` → `*U04_05`;
  `*pot confi` → `*U04_53`; `*U04_27` → `*U04_61`; `*U04_28` → `*U04_62`; `*U04_16t` →
  `*U04_16`; `$$$DUMMY.*dummycann` → `*U04_29`; `Cylinder38`, `Box1448`, `Box1449`,
  `Box1450`, `Box1447` → `*U04_51`; child of `*U04_03` matching `PALETTE`
  (`FUN_0041b4c0(obj, "PALETTE", 1)`) → `*U04_50`; `* face ech` → `*U04_52` and `+0x5c` = 1
  (hidden); while `Box36` exists: rename `Box36_%i` (i = 0, 1, …; format `0x0044078c`) and
  `+0x114` = 1 (not pickable, E-0070); `Box1162` `+0x114` = 1; `+0x118` = 1 (out of
  collision and ground casts, E-0059) on `Box368`, `Box366`, `Box373`, `Box430`, `Box431`,
  `Box435`, `Box436`, `Box437`, `Box682`, `Box686`, `Box687`, `Box690`, `Box691`, `Box708`,
  `Box198`, `Box199`, `Box429`, `Box619`, `Box620`, `Box212`, `Box214`, `Box218`, `Box713`,
  `Box822`. Strings at `0x004406c4..0x00440858`, `0x0043ff0c..0x0043ff2c`, `0x00440204`.
  Corpus (o3d.py over U00.x3d's `Object=` files): present in U00 are `*U04_37` twice
  (`static/u04.o3d`, `static/U04_37.o3d`), `*U04_05t`, `*pot confi`, `* face ech`,
  `*U04_31` (u04.o3d), `*U04_27`/`*U04_28` (children of `*U04_32`, `Anim/barke_placement.o3d`),
  `Cylinder38` and `Box1447..1450` (`static/potabeille.o3d`), `Box36` seven times (u04,
  bosketjone1, parterrehaut, barreba1, barrecote1, barreho2, pontsous), `Box1162`, and of
  the collision list all but `Box431`, `Box435`, `Box436`, `Box686`, `Box687`, `Box619`,
  `Box620`, `Box429`; absent: `*U04_26` (no object or A3D node of that name), `*U04_16t`,
  the dummy, any `PALETTE` object. So U00_Start's hides of `*U04_44`, `*U04_63`, `*U04_05`,
  `*U04_53` only find their objects through these renames.
- **Method:** MCP decompile of `0x0040e720` and `U00_Start`; xrefs; `pefile` strings;
  `o3d.py` / `a3d.py` over U00's object list. Function renamed in Ghidra.
- **Confidence:** proven.

### E-0231 — U00's ground object is the object whose face the walking ground cast hit; the boat is `*U04_32`
- **Binary/file:** `MissionMonet.exe`; `Data/U04/Anim/barke_placement.o3d`, `static/lunette.o3d`.
- **Evidence:** `Camera_FollowGround` (`0x0041a270`) walks every object
  (`X3d_Scene_Find_First/Next_Object(scene, 1)`), skips `+0x118` ≠ 0, tests each face with
  `X3d_Line_Face_Collision` and stores the object of the highest hit in camera `+0x3c`
  (0 if none); it runs only in the walking ground step (movement.md). U00's other writer
  is `U00_JumpOffStone` (`+0x3c` = 0, `0x00409e2d`); U01's is the train (`0x00401368`).
  `U00_ProcessTutorialKeys` compares `_stricmp(*(char **)(camera + 0x3c), "*U04_32")`, the
  hit object's own name, with no parent walk. `barke_placement.o3d` ("barque", a boat):
  top object `*U04_32` (109 faces, local position (141.39, 66.87, −21.82)) with children
  `Box02`, `Box01`, `*U04_30`, `*U04_40`, `*U04_39`, `*U04_28`, `*U04_27`, `*U04_43`,
  `Line07`, none welded. The ground glasses `*Lunettes0` (`static/lunette.o3d`, top level,
  22 faces) are at (141.37, 70.74, −20.33); Monet's own `*Lunettes0` is a child of
  `montur` in `anim/U04_03_Lunettes/U04_03_LUNETTES.O3D`, the last file U00.x3d loads, so
  newest-first lookup finds it first (→ `*U04_81`). Near-Monet distance `FUN_00415e40` is
  the 3D Euclidean distance between Monet's hotspot `+0x70` and the eye (camera `+0x14`).
  `U00_SayMonet` with a non-zero third argument never touches the talker, so Remarks do
  not animate Monet. The U00 unit's constructor (`0x004097e0`) zeroes `+0x6d8`,
  `+0x6e0..+0x703` and `+0x704`; of the flags `+0x6e4` (moved) is written and never read,
  `+0x6ec` is read only to set itself (capstone scan of `0x00409820..0x0040a770`).
- **Method:** MCP decompile; capstone scans for `+0x3c` stores and U00 field accesses;
  `o3d.py`.
- **Confidence:** proven.

### E-0232 — U00's interactables are two actions on five hotspots; the designed path stores the glasses through the bar the take step raised
- **Binary/file:** `Data/U00/Infoobj.bin`, `Infoact.bin`; `MissionMonet.exe`.
- **Evidence:** full parse (`infoobj.py`, `infoact.py`): hotspots `*U04_03` (type 6, cursor
  0, anim running looping), `*U04_32` (5, cursor 0, paused), `*U04_36` (4, hidden),
  `*U04_43` (4, cursor 0), `*U04_80` (4, cursor 4). Actions: only M01 (trigger 8 on
  `*U04_80`, TRUE, steps op 2 `U04_80`, op 10 `TakeLunettes`, max 1) and M02 (trigger 7,
  item `U04_80` on `*U04_03`, TRUE, op 10 `DonnerLunettes`, max 2). No action names
  `*U04_32`, `*U04_36` or `*U04_43`, so clicks on them, and plain clicks on Monet, run
  nothing. U00's vtable (`0x004395d8`, 22 slots up to `+0x54`) overrides only `+0`
  (destructor `0x00409820`), `+0x10` Load, `+0x14` Start, `+0x1c` frame, `+0x30` dispatch,
  `+0x40` input and `+0x48` voice path; the dispatcher knows only `DonnerLunettes` and
  `TakeLunettes`; the other slots are the base scene's (same addresses as U01's
  `0x004393d0` and U02's `0x00439468` at `+4`, `+0x18`, `+0x20..+0x2c`, `+0x34..+0x3c`,
  `+0x44`, `+0x4c..+0x54`; `+8`/`+0xc` are `0x0041d490`/`0x0041d650`, which U01 and U02
  override). Op 2
  shows the bar (E-0104), so a take leaves the bar up and one strip click stores the
  glasses without Space; `spaceSeen` (`+0x700`) is set only by Space (and
  `DonnerLunettes`), and the near-Monet line `sb10` needs it clear.
- **Method:** parsers; vtable dump with `pefile`; E-0201/E-0202 functions.
- **Confidence:** proven for the data and code; what the lines say is not checked (Q-0120).

### E-0270 — Camera-facing objects: `+0x164` is row 3 of the object's model-view, and every welded object gets its own camera type's model-view
- **Binary/file:** `x3d.dll`, `xd3d.dll`.
- **Evidence:** `FUN_10019730` (x3d) builds the model-view at transform `+0x134` (a 4×4,
  row 3 at `+0x134 + 0x30` = `+0x164`). Case 2: `+0x134` = global `+0xf4` ×
  Tr(−camera position `+0x2c..+0x34`) × R(yaw π/2, camera pitch `+0x58`) × roll ×
  projection; then `auStack_10c` = global × the true view (camera `+0x5c` `+0x80`), and
  its row 3 (`uStack_dc..d4`) is written to `+0x164..+0x16c`, i.e. over the model-view's
  translation row. So a vertex v is drawn at v · (global rotation) · R(π/2, e) · P plus the
  object origin projected by the true view: the offsets turn, the origin stays. Nothing
  else reads `+0x164` in `x3d.dll` or `xd3d.dll` (instruction search for `+ 0x164]`: only
  stack locals and this store). `FUN_1001d440` (the `+0x24` transform) runs
  `X3d_Vertex_Transformation` over the object's own range (`+0x48`, `+0x44`) with that
  object's `+0x134`. The renderer `FUN_10020720` (xd3d) and the pick `FUN_100213f0`
  (xd3d, E-0070) both call class `+0x10` with the object's own `+0x108` for the object
  and for each weld child (`+0` = 0, `+0x40` ≠ 0) before `+0x24`, so a welded `$Z$`
  object's range is camera-facing about its own origin, drawn and picked alike. The
  global `+0xf4` chain does not involve the camera type: a `$Z$` parent does not move its
  children's origins.
- **Method:** MCP decompile of `FUN_10019730`, `FUN_1001d440`, `FUN_10020720`,
  `FUN_100213f0`; MCP instruction search.
- **Confidence:** proven. Resolves the "how the renderer uses `+0x164`" part of E-0058 and
  E-0062 (the engine's origin-plus-rotated-offsets drawing was right).

### E-0271 — After loading, names with a camera prefix are cut to start at their `*`; animation nodes keep the `.A3D` names
- **Binary/file:** `MissionMonet.exe`; `Data/U02/anim/U02_10.O3D`, `U02_10.A3D`.
- **Evidence:** `FUN_0041b010` (called from `XScene_124`, the generic load, and
  `U00_Load`): for each scene object, after setting camera type 1/2/3 for `$XYZ$`/`$Z$`/
  `$XZ$` (E-0045), `strstr(name, 0x004417b8)` with `0x004417b8` = `"*"` (bytes
  `2a 00`); if found, the name is overwritten with the text from the `*` on. Only objects
  are renamed; node lookups by `*U02_10` use the node list's contains-match
  (`FUN_00416180(…, 0)`, E-0072, E-0164), whose node keeps `$Z$*U02_10`. `U02_10.O3D`:
  `$$$DUMMY.Dummy01` (root, no own vertices, weld array of 10, rotation −90° about x),
  `$Z$*U02_10` (welded, vertices 0..3), `$Z$chaine` (welded, 4..9, parent `$Z$*U02_10`);
  so after load the objects are `$$$DUMMY.Dummy01`, `*U02_10`, `$Z$chaine`, both lower
  ones camera type 2. INFOOBJ's hotspot `*U02_10` binds to the object by exact name
  (E-0072), which exists only after this cut; its node state (frame 1, paused, 15 fps, not
  looping) reaches node `$Z$*U02_10` through the contains-match (`FUN_004210d0`, list
  `+0x158` vtable `+0x14(name, 0)`).
- **Method:** MCP decompile of `FUN_0041b010`; `0x004417b8` read; xrefs; `o3d.py`/`a3d.py`
  over the two files.
- **Confidence:** proven.

### E-0272 — INFOOBJ's hidden hotspots also leave collision; a script "show" puts them back
- **Binary/file:** `MissionMonet.exe`; `Data/U02/INFOOBJ.BIN`, `Static/U02.O3d`.
- **Evidence:** `FUN_004210d0` (applies an INFOOBJ entry) with visible (`+0x30`) = 0 calls
  hotspot vtable `+0x28("", 0, 1)` (`0x0042110d..0x0042111a`). `+0x28` = `0x00421050`:
  show → `X3d_Object_Unhide(obj, 1)` and object `+0x118` = 0; hide →
  `X3d_Object_Hide(obj, 1)` and `+0x118` = third argument. `+0x118` (no collision, E-0048)
  is set on the hotspot's object only, not its children. So every hotspot hidden at load is
  out of collision until shown through `+0x28`; `X3d_Object_Unhide` alone (the magpie in
  `PieVoleur`, E-0163) leaves it out. U02: hidden at start `*U02_01`, `*U02_05`,
  `*U02_06a`, `*U02_07a`, `*U02_09`, `*U02_09a`, `*U02_11`, `*U02_14` (E-0165). In
  `Static/U02.O3d` (world transforms per `scene.md`) `*colplanch` (→ `*U02_14`) is two
  faces at z −6..−2 over x 416..440, y −993..−846, and `*U02_07` (→ `*U02_07a`, the laid
  plank) spans x 424..432, y −993..−846, z −9..−2: both lie across `ruisseau.O3d`'s stream
  `*U02_08` (x −480..2159, y −1675..−668). Hidden and without collision they are no floor,
  so the stream cannot be crossed until `PoserPlanche` shows `*U02_07a` (`+0x28`, 1) and
  clears `*U02_14`'s `+0x118` (E-0162).
- **Method:** capstone of `0x004210d0..0x0042116d` and `0x00421050..0x004210c3`; Python
  over `o3d.py` output.
- **Confidence:** proven.

### E-0273 — The "bell" is the locomotive's whistle cord, in the cab; the player clicks it from the platform's east end
- **Binary/file:** `Data/U02/anim/U02_10.O3D`, `U02_10.A3D`, `Static/nloco2.o3d`,
  `Static/colTotal.o3d`, `Static/U02.O3d`; `MissionMonet.exe`.
- **Evidence:** World transforms (`scene.md`, row vectors): Dummy01 at (2842.8, 0,
  −113.0), rotation (x, y, z) → (x, −z, y); `*U02_10`'s origin (row 3) = (2832.2, 215.7,
  101.4) and `$Z$chaine`'s origin is the same point (−pivot + parent pivot + position =
  0). Local y becomes world z: the cord (x width 1.8) spans z 118.5..128.5 (`*U02_10`) and
  91.8..118.5 (`$Z$chaine`, a 3.7-wide handle at z ≈ 92). `U02_10.A3D` (1..38) moves
  only `$Z$chaine` (19 translation keys, y −9.93 → −10.7 and back): a pull. `Sonner`
  plays `SIREN` (E-0164). Stored normals are local (0, 0, −1) → world +y, so with camera
  type 2 (drawn as seen from yaw π/2, i.e. looking −y, E-0058/E-0270) its faces are always
  front faces; drawn without it, from the platform (y < 215.7, looking +y) they are back
  faces and the pick (E-0070) skips them (checked with E-0070's test in camera space).
  `nloco2.o3d` `loco02` spans x 2540..2967, y 122..238, z −9..168: the cord hangs inside
  the locomotive. `colTotal.o3d` `Colision04` walls the platform off: faces
  (2392, 110)→(2874, 124) with normal −y and (2826, −118)→(2874, 124) with normal −x
  (ground there z ≈ 10, eye ≈ 70), so the cab is out of reach. Ray tests from eyes at
  z 78 to cord points z 95..125 against `nloco2`, `U02`, `DIVERS`, `deco` front faces:
  clear from x ≈ 2780..2870 over y −40..110 (except a pillar at x ≈ 2830), blocked west
  of x ≈ 2770. Pick depth limit 4 · s = 160 (E-0051): from (2830, 100, 70) the handle is
  ≈ 116 away, so the player clicks it standing at the wall, x ≈ 2780..2870, y ≈ 60..103,
  facing +y (yaw ≈ −π/2).
- **Method:** Python over `o3d.py`/`a3d.py` output (world transforms, Möller–Trumbore ray
  tests, ground casts); no live run.
- **Confidence:** strong (geometry; the live check is Q-0130).

### E-0274 — U02's magpie and barrier: where the player stands
- **Binary/file:** `Data/U02/anim/U02_05/*.A3D`, `U02_06A.*`, `U02_09A.*`,
  `Static/colTotal.o3d`, `Static/U02.O3d`, `Static/ruisseau.O3d`.
- **Evidence:** magpie root translation keys: `ACTION01` 1..370 from (1848, 604, 341) to
  (1278.1, −563.6, −4.3) at 369; `Action02` holds (1278.1, −563.6, −4.3) to key 11
  (the paused `PieVoleur` frame, E-0163), then flies to (461.9, −1113.2, 70.5) (key 606;
  `ACTION03` holds (462.3, −1112.7, 70.5)). The frame hook's trigger (1280, −564, −7.15),
  radius 240 (E-0161), is that perch; ground there z ≈ −10, eye ≈ 50, so the player comes
  within about 233 horizontally. `U02_06A`/`U02_09A`: `$$$DUMMY.#SCENE` identity at
  (1173.7, −103.2, −1172.3), so the chestnut and the coin end at (462.4, −1102, 15.6) and
  (462.5, −1102.1, 14.8), on the barrier below the magpie. `Colision01` (y −1040, x
  174..669, normal +y) keeps the player at y ≳ −1020; ground (462, −1020) z −2. From
  there magpie and coin are ≈ 97 away (pick limit 160). That bank lies across the stream
  (`*U02_08` y −1675..−668; the plank `*U02_07a` bridges y −846..−993 at x ≈ 428, E-0272),
  so feeding the magpie and taking `U02_09` need the plank. `*U02_13` (`*ZonePlanc`),
  where the plank is laid: x 360..480, y −867..−793, z −7.
- **Method:** Python over `a3d.py`/`o3d.py` output; ground casts.
- **Confidence:** strong (key values, not the TCB-interpolated path).

### E-0275 — `U02_FallInStream` dims in float steps truncated each step: the light ends near 75, not 90
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `0x00404bfd..0x00404d3a`: N = `_ftol`(scene `+0x144`, fps) (import
  `0x00439160` = MSVCRTD `_ftol`); per channel step = (float)(c₀ − 0x5a) / N; each of N
  iterations: c = `_ftol`((float)c − step), or 0 when below 0.0 (`0x0043943c` = 0.0),
  stored as a byte, then `FUN_0041b2f0(c)` and `RunFor(10)`. Truncation after every step
  removes ⌈step⌉ each time when step is not whole: from 255, 255 − N·⌈165/N⌉ (N = 60 or
  30: 75; 25: 80; exactly 90 only when N divides 165).
- **Method:** capstone; PE import table.
- **Confidence:** proven. Refines E-0161's "(c₀ − 90)/N" (`u02.md` said "toward 90").

### E-0210 — Every path that stores, keeps or drops the held item
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** cursor `DAT_0046ec14`: `+4` mode (0 normal, 1 holding, 2 blinking), `+0x2c`
  image, `+0x4a` bar name, stash `+0x4d0`/`+0x4d4`/`+0x4d8` (E-0183). The cursor setter
  `FUN_00414540(mode, name, redraw)` (`ret 0xc`) has three callers: the take routine
  `FUN_004211d0`, the bar item press `0x004321e0` and the stash restore `FUN_00414960`.
  **Store** = `FUN_004149e0`: if mode is 1 or 2 (2 first stops the blink,
  `FUN_00414ba0`), bar `+0xa8(cursor +0x4a)` (add), cursor normal (`FUN_004144b0(0,0,0)`).
  Its callers: `App_OnEscape` (`0x00416400`) only on the in-game branch (game `+0x160` ≠ 0
  and help panel `+0x170` = 0; the U00 branch, `+0x160` = 0, stops group 1 and opens the
  menu without it); `FUN_004135b0` (game vtable `+0x14`, caught → `OptionLoad`); and the
  unit switch, game vtable `+4` (`0x00412fb0`, call at `0x00412ffa`, before `+0x160` and
  the script name are set; Ghidra has no function there, so its xref list misses it). The
  strip press `0x00431cb0` adds `+0x4a` when mode = 1 and hides the bar; the item press
  first forwards to it (swap). **Kept:** `App_OnLButtonDown` (`0x00417c10`, app mode 0,
  cursor shown, rate limit) → scene `+0x30` → `FUN_0041b700`: hover, then
  `Actions_TriggerForHotspot` only if a hotspot is under the cursor; no match ends in
  `FUN_00412a90` (empty). WndProc (`0x00416650`) jump table `0x00416978`: 0x201 →
  `App_OnLButtonDown`; 0x202, 0x203, 0x204, 0x205 → `0x00412aa0` (`mov eax, 1; ret 8`), so
  right clicks do nothing. `PorteF_OnKeyDown` (`0x00431800`) only slides the bar.
  `Scene_PickHover` resets the cursor only when mode is neither 1 nor 2. **Frames:**
  `SetAppMode(2)` (`0x00417ce0`) stashes a holding cursor (`FUN_00414910`: `+0x4d0` = 1,
  `+0x4d4` = 1, image) and sets it normal, but the app-mode-2 branch of the main loop
  (`0x00416de1`..`0x00416e2f`) calls `FUN_00414800(1)` → `FUN_00414960(1)` every pass,
  which restores the stash (`FUN_00414540(1, image)`) and clears `+0x4d0`: the item stays
  on the cursor over every frame. Leaving mode 2 runs `FUN_00414960(0)`, the same restore.
  **Dropped** (normal cursor, nothing added): `LoadUnitScene` (`0x004130b0`: `+0x4d0` = 0,
  `FUN_004144b0(0, 1, 1)`), the base unit start `FUN_0041ae10`, op 3 (`0x004212b0`),
  `U00_DonnerLunettes`, `Scene_RestoreState` without a save; `Game_NewGame`
  (`0x00412b80`) calls `SetAppMode` and then clears the strip (bar vtable `+0xa4` =
  `0x00431b30`, call at `0x00412ccb`).
- **Method:** MCP decompile; capstone of the WndProc, the main loop and `0x00412fb0`;
  vtable reads with `pefile`.
- **Confidence:** proven. Live checks: E-0211, E-0212.

### E-0211 — Live: a take puts the item on the cursor and raises the bar; only a strip click stores it
- **Binary/file:** `C:\MonetRun` (sound patch of E-0213); `tools/proxy/cursor.ps1` reads the
  cursor fields of E-0210; snaps in `traces/inv/` (local).
- **Evidence:** U00 on the boat, click at game (312, 434) on the glasses: mode 1, image
  `U04_80C.bmp`, bar name `U04_80P.bmp`; the glasses vanish from the seat and within about
  0.6 s the bar is fully up (y = 420) with the glasses image drawn centred on the cursor
  (`d03`..`d05`). Nothing more happens by itself: 30 s later mode is still 1 and the strip
  empty. With the item held: left click on empty water (100, 200) → mode 1; right click
  (500, 150) → mode 1; Space → the bar slides up, mode 1, strip empty (`b11`). Click on
  the strip (330, 450) → mode 0, bar hides; Space → the glasses in slot 0 (`b13`). Click
  slot 0 (111, 450) → mode 1 again, bar hides, strip empty. Holding the glasses, a click on
  the table (200, 300) keeps mode 1. In the first run the click right after the take
  landed at y = 428, inside the risen bar, and stored the glasses at once (`b04`..`b07`).
- **Method:** two live runs, 2026-09-26; `send.ps1` (new `-Right`), `snap.ps1`.
- **Confidence:** proven.

### E-0212 — Live: Escape in U00 keeps the item on the cursor over the menu; Practice stores it, New game loses it
- **Binary/file:** `C:\MonetRun`; `traces/inv/` (local).
- **Evidence:** holding the glasses in U00 (no game), Escape: app mode 2, the Option menu
  with the glasses image still drawn at the cursor (`b14`); cursor mode 1, stash image
  `U04_80C.bmp` with `+0x4d0` = 0 (restored, E-0210). Practice from there: mode 0, and
  after `sb03_bis` Space shows the glasses in slot 0 (`b16`): the unit switch stored them.
  Same again, then New game: mode 0 at once; at U01's hand-over (`camera.ps1` = the
  free-roam pose) Space shows only the banknote `U02_01P` (`c01`).
- **Method:** live run, 2026-09-26.
- **Confidence:** proven.

### E-0213 — Voices of an unfocused original never end: no `DSBCAPS_GLOBALFOCUS` (answers Q-0111)
- **Binary/file:** `MissionMonet.exe` `0x00421fc6`/`0x00421fd0`; `C:\MonetRun`.
- **Evidence:** `LSound_72` builds the caps as `0x10080` or `0x100c0` (+2 static, E-0120),
  never with `0x8000` (global focus), so DirectSound keeps a background application's
  buffers silent and not advancing. Live, window never focused: after a new name the
  read-out shows `started` = 1 and the gauge stopped for over a minute (U00 is inside the
  blocking `sb03` Say), the camera fixed at the start pose, Up and Enter ignored (as
  E-0203). With `patch_exe.py`'s two new patches (caps `0x18080`/`0x180c0` in the copy),
  `sb03` returns after about 12 s (gauge state 1 at +13 s) and Up moves the eye.
- **Method:** capstone; two live runs, 2026-09-26.
- **Confidence:** proven. Nothing for the engine (its mixer does not depend on focus).

### E-0214 — Space never reaches U00's key table while the bar exists: `spaceSeen` is set only by the ending
- **Binary/file:** `MissionMonet.exe`; `C:\MonetRun`.
- **Evidence:** WndProc (`0x00416650`) first hands every message to the frame manager
  (`DAT_0046ec1c`, vtable `0x00439e5c`, `+0x68` = `0x0042bc00` → `+0x6c` = `0x0042bcc0`) and
  returns at once when it answers non-zero. For 0x100 (jump table byte `0x0042bf30`,
  target `0x0042bcf7`) it calls each active frame's `+0x1c`; `PorteF`'s (`0x0043ae9c` +
  `0x1c` = `PorteF_OnKeyDown`, `0x00431800`) returns 1 for Space whenever app `+0x488` is
  set. So Space's key-table slot `0x0046e860` is never written and
  `U00_ProcessTutorialKeys` never sets `+0x700`; only `U00_DonnerLunettes` does. Live: near
  Monet in state 8, Space (80 ms) then Space (400 ms): the bar toggled each time, `+0x700`
  stayed 0 and the gauge stayed in state 8 (`sb11` keeps coming back); after the glasses
  were given it read 1.
- **Method:** capstone; vtable reads; live run, 2026-09-26.
- **Confidence:** proven. Supersedes E-0232's "set only by Space (and `DonnerLunettes`)"
  and E-0201's Space step as far as its effect goes (the code is there, the key never
  arrives while `PorteF` is open with inventory allowed).

### E-0215 — Live: U00's tutorial played end to end
- **Binary/file:** `C:\MonetRun`; `tools/proxy/cursor.ps1`, `camera.ps1`; `traces/inv/`
  (local).
- **Evidence:** new player, 2026-09-26 (times after Enter): `sb03` ends at ≈12 s, gauge
  state 1; Up during `sb04` does nothing, after it Up sets `moved` and stops the gauge
  (state 0). Route (collision `static/Collision.o3d` placed with E-0042's matrices): the
  courtyard west to (41, 253), south down the steps (z 15 → −3.6) to (54, 209), the ring
  path east (105, 160) → (150, 145) → (174, 134) → (196, 72) → spur (166, 54); walking west
  onto the boat puts the eye at (141.389, 66.874, −11.818), yaw 1.5508, pitch 0.9491
  (looking at `*U04_43`), `onStone` = 1, state 2. On the boat Up does not move. Right
  0.85 s: yaw 4.6708, `turned` = 1, state 4 at once; 10 s later `glassesTaken` = 1,
  state 5. Take: state 7; strip click: the next fire sets `nearMonet` = 1 and state 3.
  Shift: eye (149.87, 60.56, −9.26), yaw 6.7102 (0.427 + 2π, not reduced), pitch π/2,
  `onStone` = 0, state stays 3. Walking from there toward (172, 70) stepped back onto the
  boat (`onStone` = 1 again, same pose; answers Q-0121). At the terrace, at (68.9, 265.1),
  the view turned to Monet (yaw 5.0204, pitch 1.2116), state 8. Glasses from the bar onto
  Monet at (471, 262): cursor normal, `spaceSeen` = 1, state 0, the view back at the start
  pose; Monet wears the glasses (`e2`); the Option menu about 18 s after the click, "Load a
  game" and "Gallery" dimmed (`e4`). Practice then: unit flags fresh, `sb03_bis` ≈11 s,
  state 1, strip unchanged (empty here; in E-0212 it kept the glasses). Hover on Monet
  gives cursor kind 0, as his INFOOBJ entry. After the ending the hidden gauge read state
  8 with a new start time although `spaceSeen` = 1 (Q-0112).
- **Method:** live run, 2026-09-26; `cursor.ps1` sampled every 2–4 s.
- **Confidence:** proven for the listed readings.

### E-0205 — The renderer culls back faces: xd3d never sets a cull mode, so D3D's default CCW culling applies
- **Binary/file:** `xd3d.dll`; `traces/u01-start-original.png`.
- **Evidence:** capstone scan of every `IDirect3DDevice2::SetRenderState` call (vtable
  `+0x5c`, 257 sites) in `xd3d.dll`: the immediate states set are 1 (texture handle), 9
  (shade mode), 0xe (Z write), 0x13/0x14 (blend factors), 0x1b (alpha blend), 0x1d
  (specular), 0x29 (colour key), 0x2c/0x2d (texture address); never 0x16
  (`D3DRENDERSTATE_CULLMODE`). D3D's default is `D3DCULL_CCW`, so faces wound
  counter-clockwise on screen are not drawn, matching the pick's back-face test (E-0070).
  Engine check: with back faces culled (OpenGL `glFrontFace(GL_CCW)` in its projection)
  U01's first shot loses the dark boat in front of the harbour, as in the original
  capture; with the other winding the whole scene vanishes.
- **Method:** Python capstone over `.text` of `xd3d.dll`; engine render compared with the
  capture.
- **Confidence:** proven for the state scan; the U01 comparison is visual. Q-0021's faint
  buildings and the engine's birds remain unexplained.

### E-0360 — U05's vtable and state: no load hook, no input hook, no save chunk; three timers/flags
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** constructor `0x0040ece0` (`U05_ConstructUnitScene`): `FUN_0041a890`, vtable
  `0x004396d4`, `+0x6e0` = `+0x6e4` = `+0x6cc` = `+0x6c8` = 0. Vtable: `+8` `0x0041d490`,
  `+0xc` `0x0041d650`, `+0x10` `0x0041acf0` (all generic), `+0x14` `U05_StartUnit`
  (`0x0040ed40`, function created), `+0x1c` `U05_UpdateFrameLogic` (`0x0040f160`,
  created), `+0x24` `0x0041c350` (talkers, nodes, hotspots tick), `+0x30`
  `U05_DispatchClickActions` (`0x0040f3a0`, created), `+0x40` `0x0041b7f0`
  (`Scene_HandleInput`). U05 code reads/writes `+0x6e0` (dog wait, then chatter clock),
  `+0x6e4` (bark time), `+0x6c8` (exit latch); `+0x6d0` is written once
  (`X3d_Camera_Get_Position` at the end of the start) and never read.
- **Method:** MCP decompile, vtable bytes, capstone of `0x0040ece0..0x00410940`.
- **Confidence:** proven.

### E-0361 — `U05_StartUnit`: renames, collision and pick fix-ups, two talkers, the dog's and Mazout's start clips, camera cut, autosave, ambient `s4_01a`
- **Binary/file:** `MissionMonet.exe`; `Data/U05/U05.x3d`, `anim/*.A3D`.
- **Evidence:** `0x0040ed40`: `X3d_Scene_Get_Object("fil")` → strcpy `*Fil`,
  `Object_SetNoCollisionTree(obj, 1)` (`0x00421020`: `+0x118` := v, recurse `+0x24`, loop
  `+0x28`); node list `+0x158` `+0x14("fil", 1)` name `+0xc` := `*Fil`;
  `+0x14("Object02", 1)` → `*U05_10`; `FUN_0041b440(name, 0)` (exact, then contains)
  `battant02`, `battant`, `col103` → `+0x118` = 1; `FUN_0041ae10(a, stream)`; camera
  `FUN_00419ce0(32.0)`, `FUN_00419d00(0.0)`; hotspots `+0x1a0` `*U05_05`, `*U04_04` →
  `0x00421020(hotspot +0x60, 1)`; `Box17` `+0x114` = 1; vtable `+0x28("U05_02", "",
  "$$$DUMMY.*visage", 0, 8, 0)` and `("U04_04", …)`; actions `+0x434` (M09) →
  `ColPorte2` `+0x118` = 1, `+0x43c` (M11) → `ColPorte1`; if `a`: node `*U05_05`
  `FUN_00420080(0)`, `FUN_00420220(node, "…Anim/U05_05/Attente.A3D", "ChienTourne", 1,
  1)`, slot `+0x68` = 1, `+0x78` = 15.0, `FUN_00420060(1)`, `FUN_004200c0(245.0)`; node
  `*U04_04` `MazoutAttente` (`Anim/U04_04/Attente.A3D`) slot 1, `+0x68` = 1, 15.0,
  `FUN_00420060(0)`; `FUN_00419520(0xc23e6666, 0x429a8a3d, 0x42378f5c)` (−47.6, 77.27,
  45.89), `FUN_00419550(0xc0c9eb85, π/2)` (−6.31); game `+0x10(FUN_0042a3c0(0x3eb), 0)`;
  always `X3d_Camera_Get_Position(→ +0x6d0)`, `+0x4c("s4_01a", 1)`. Corpus (`o3d.py`,
  `a3d.py`): `fil` and `*U05_08` in `anim/Lampes.O3D`, animation `fil` in `lustre.A3D`
  (1..100); no animation named `Object02` in any U05 `.A3D`; `battant`, `battant02`,
  `Box17` in `static/st-laz.o3d`, `col103` in `colTotal.O3D`, `ColPorte1/2` in
  `colPorte.O3D`; `U05_05/Attente.A3D` 1..356, `U04_04/Attente.A3D` 1..100.
  `X3d_Object_Hide(obj, 0)` sets only the object's `+0x5c`; with 1 also its subtree
  (`x3d.dll`); `Unhide` mirrors it.
- **Method:** capstone (strings, floats), MCP decompile of `0x00421020`, `0x0041b440`,
  `0x00420080`, `0x00420060`, `X3d_Object_Hide`/`Unhide`.
- **Confidence:** proven.

### E-0362 — U05's frame hook: the dog's three steps, Mazout, the 15-s gauge, M23, chatter, the exit, and a dead bark timer
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `0x0040f160` (actions `+0x198`: exhausted `+0x410[id]`, records
  `+0x10[id]`): `+0x414` ∧ ¬`+0x428` → `+0x6e0` ?= GetTickCount; ¬`+0x420`: now >
  `+0x6e0` + 4000 ∧ `U05_DogBarkThenSit` (`0x004101f0`) → `FUN_0041e3a0(M04)`; else
  ¬`+0x424`: `U05_DogWaitLoop` (`0x004102e0`) → exhaust M05; else `U05_ChefNoticesDog`
  (`0x004103c0`) → `FUN_0041e4b0(M06)`, inventory `+0x90`/`+0xa8("U04_44P")`. `+0x43c` ∧
  ¬`+0x440` → `U05_MazoutConfronts` (`0x0040fc40`) → exhaust M12; `+0x444` ∧ ¬`+0x448` →
  `U05_MazoutGaugeExpired` (`0x0040fa60`); `+0x45c` ∧ ¬`+0x46c` → `U05_ChefCallsNear`
  (`0x0040f660`: distance(eye, `*U05_02` local) ≤ 220 → run M23); `+0x470` ∧ ¬`+0x474` →
  `U05_ChefChatter` (`0x0040f560`: timer init, voice group 2 silent, now ≥ `+0x6e0` +
  20000, ≤ 220 → `+0x6e0` = now, `fmod(rand, 2.0)` = 1.0 → run M26 else M27); `+0x470` ∧
  `+0x6c8` = 0 → `U05_ExitToU06` (`0x004106f0`); `+0x438` (M10) → `+0x6e4` ?= now +
  28000, now > it → run M82, `+0x6e4` = rand·40000/0x7fff + now; last
  `Scene_RenderFrame`. `0x004101f0`: node `*U05_05` active slot (`+0x188[+0x1ca]`)
  `+0x68` = 0, `+0x60` = 0 → return 0; run M82, `ChienAttente`
  (`Anim/U05_05/ACTION01.A3D`) slot 2, `+0x68` = 0, 15.0, running. `0x004102e0`: same
  test, `Attente2` (`ATTENTE02.A3D`) slot 3, `+0x68` = 1, 15.0, running. `0x004103c0`:
  `LSoundManager_IsGroupPlaying(2)` → 0; distance > 220 → 0; run M06,
  `FUN_0041e2a0(M07, 1)`, `FUN_0041e2a0(M09, 1)`. `0x0040fc40`: eye.x ≥ 1425 → 0;
  `FUN_00414820(0, 0)`; `FUN_00419620(eye, (1306.35, −945.6, eye.z), cam yaw,
  polar(normalise(obj − target)) yaw, cam pitch, π/2, 4000, 0)`; `MazoutA01`
  (`Anim/U04_04/Action01.A3D`) slot 2, `+0x68` = 0, 15.0, running; run M13;
  `Scene_RunFor(0)` while group 2 plays and not `FUN_004163b0(0xd)`;
  `FUN_00414dc0(+0x178)`; `FUN_0041a560(15.0, 1, "", 0)`; `+0x6e0` = 0;
  `FUN_00414820(1, 1)`. `0x0040fa60`: `FUN_0041a6c0(gauge, 1)` = 0 → return; `MazoutA03`
  (`Anim/U04_04/Action02.A3D`) slot 3, not looping, 15.0, running; `X3d_Object_Hide(o, 1)`
  over `X3d_Scene_Find_First/Next_Object(…, 1)`; `X3d_Object_Unhide(*U04_04, 1)`;
  `FUN_00419520(1310, −986, eye.z)`; `FUN_00419580(that, obj local + (0, 0, 30))`;
  `+0x50("s4_04.wav", P, 0)`; `RunFor(0)` until slot `+0x60`; `FUN_0041bfd0(2000)`; game
  `+0x14(1)`. `0x004106f0`: eye.y > 928.0 → suspend; `*U05_13` local; dir = (170, 129,
  obj.z − eye.z) = (1266, 1302) − (1096, 1173); `FUN_00419620(eye, (1096, 1173, eye.z),
  cam yaw, dir yaw, cam pitch, π/2, 7000, 0)`; `+0x6c8` = 1; `FUN_0041bfd0(2000)`; game
  `+4(6)`. `Talkers_Say` (`0x004215f0`) stops the current talker (`FUN_00421730`) before
  playing, so M06's second run restarts `U05_04`. WalkPath argument order (eye, target,
  yaw₀, yaw₁, pitch₀, pitch₁, ms, callback) from the stack offsets of
  `X3d_Camera_Get_Polar(cam, &yaw, &pitch)` and `X3d_Convert_To_Polar(v, &yaw, &pitch)`,
  as E-0161.
- **Method:** capstone with stack-offset tracking; MCP decompile of each function named.
- **Confidence:** proven.

### E-0363 — U05's dispatcher, `TestSpeakChef` and `ChienVersPorte`
- **Binary/file:** `MissionMonet.exe`; `Data/U05/Anim/U05_05/ACTION03.A3D`.
- **Evidence:** `0x0040f3a0`: `FUN_0041b700`, then while `+0x1a4` the queue is compared
  in order with `TestSpeakChef` `0x00410060`, `ChienVersPorte` `0x00410470`,
  `MaskGrille` `0x0040fea0`, `LampeTombe` `0x0040f7e0`, `OuvrePorteConsigne`
  `0x0040f790`, `OuvrePorteSalle` `0x0040f6d0`, `AfficheChefEtChiot` `0x00410020`,
  `AfficheCariolle` `0x00410850`, `FermePorteConsigne` `0x0040f750`, `DoTableauA`
  `0x0040f520`, `DoTableauB` `0x0040f540` (all renamed `U05_*`); nothing after the loop.
  `0x00410060`: suspend; `FUN_00419620(eye, (1493, −532, eye.z), cam yaw, yaw toward
  `*U05_02`, cam pitch, 1.45 (`0x3fb9999a`), 10000, 0)`; while group 2 plays: vtable
  `+0x24`, `Scene_RenderFrame`; resume; dog node slot 1 (`+0x18c`) `FUN_00420060(0)`,
  `X3d_Object_Unhide(slot +0x80, 1)`. `0x00410470`: suspend; `FUN_0041e2a0(M07, 0)`;
  cursor 0 on hotspots `*U05_02`, `*U05_05`; nodes `*U05_05`, `*U05_01`; `Action3`
  (`ACTION03.A3D`) slot 4, `+0x68` = 0, 15.0, running; `+0x48("U05_06A", camera +0x14)`;
  loop while slot `+0x60` = 0: 97.0 < frame < 99.0 ∧ door `+0x60` → door `+0x68` = 0,
  15.0, running; frame > 102.0 ∧ door `+0x60` → door `+0x70` = 1, 15.0, running,
  `+0x48("U05_06B", eye)`, exit loop; else `+0x24`, `U05_TurnCameraToObject(slot +0x80)`
  (`0x00410870`: `FUN_00419550` with the polar of normalise(object local − eye)),
  `Scene_RenderFrame`, `FUN_00416990` (message pump). After: node `*U05_06`
  `FUN_00420060(1)`, frame 20.0; node `*U05_12` running, 15.0, `+0x68` = 0, `+0x70` = 1;
  resume; `ColPorte2` `+0x118` = 1. Corpus: `ACTION03.A3D` 1..673, `PORTES.A3D` 0..25.
- **Method:** capstone; MCP decompile.
- **Confidence:** proven.

### E-0364 — `MaskGrille`, `LampeTombe`, the doors, `Affiche*`, `DoTableau*`
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `0x0040fea0`: suspend; `X3d_Object_Hide(*U05_07, 1)`; `FUN_00419620(eye,
  (1489.92, −1189.56, 0.65), yaw, yaw, pitch, pitch, 4000, 0)`; then `FUN_00415ed0(v,
  1489.92, −1134.35, z saved before)`, `FUN_00419620(eye, v, yaw, −1.55, pitch, pitch,
  1500, 0)`; hide `*U05_02`, `*U05_05` (1); resume; `ColPorte1` `+0x118` = 1.
  `0x0040f7e0`: suspend; `FUN_0041a680(gauge)`; `MazoutA03` (`Anim/U04_04/Action03.A3D`)
  slot 4, not looping, 15.0, running; `X3d_Object_Hide(*U05_08, 0)`; node `*Fil` `+0x68`
  = 0, 15.0, running; `+0x50("s4_0809.wav", eye, 0)`; `FUN_00419620(eye, (1306.35,
  −945.6, eye.z), cam yaw, yaw toward Mazout, cam pitch, π/2, 1000, 0)`; tick and render
  while group 2 plays; `X3d_Object_Unhide(*U05_09, 1)`; `FUN_0041e3a0(M14)`; resume.
  `0x0040f790`: node `*U05_10` `+0x68` = 0, 15.0, running; `FUN_00421300(hotspots, 0,
  "*U05_10", 1)`. `0x0040f750`: same node, running, then `+0x70` = 1. `0x0040f6d0`:
  `*U05_01` and `*U05_12` `+0x68` = 0, 15.0, running, `+0x70` = 0; `FUN_0041e2a0(M83, 0)`;
  run M84. `0x00410020`: `X3d_Object_Unhide` `*U05_02`, `*U05_05` (1). `0x00410850`:
  unhide `*U05_13`. `0x0040f520`/`0x0040f540`: frame manager (`DAT_0046edb0`) vtable
  `+0xc8` = `FrameManager_OpenTableauJeu` (`0x00426780`) with `"U14_02"` / `"U14_05"`:
  frame `+0x90("TableauJeu")`, kept at `+0x188`, then its `+4`, `+0x38(1)`,
  `+0x114(name)`; app `+0x47c` = 2, `+0x484` = 0.
- **Method:** capstone; MCP decompile.
- **Confidence:** proven for the calls; the `TableauJeu` frame itself is not analysed
  (Q-0161).

### E-0365 — U05 corpus: INFOACT, INFOOBJ, the dummy item `U04_111`, dead M10
- **Binary/file:** `Data/U05/Infoact.bin`, `Infoobj.bin`, `Data/*/INFOACT.BIN`,
  `MissionMonet.exe`.
- **Evidence:** `infoact.py --file`: 32 records, ids 1..17, 19..27, 80..85; steps and
  conditions as listed in `u05.md`. `U04_111` occurs only in `U05/Infoact.bin` (every
  unit's INFOACT scanned; no take step yields it). No U05 code runs or exhausts M10
  (record `+0x38`; the only `FUN_0041e4b0`/`FUN_0041e3a0` targets are M04, M05, M06,
  M12, M13, M14, M23, M26, M27, M82, M84), and op 14 targets only M08, M20, M21, M80,
  M85. `U04_44` is taken in U04 (M32, op 2 on `*U04_44`). `infoobj.py`: 15 entries as
  listed. Sounds (Python `wave`): `U05_01` 11.80 s, `U05_02` 14.44, `U05_03` 26.29,
  `U05_04` 5.29, `U05_05` 5.30, `U05_06A` 4.78, `U05_06B` 4.48, `U05_07` 34.50, `U05_08`
  6.27, `U05_09` 14.48, `U05_10` 2.68, `U05_11` 2.32, `d4_12` 2.59, `s4_01a` 34.26,
  `s4_02` 2.81, `s4_04` 2.19, `s4_06` 0.40, `s4_08` 1.69, `s4_0809` 4.64, `s4_10` 2.45;
  no string in the EXE or INFOACT names `U05_10b`, `U05_11b`, `s4_03`, `s4_06chaise`,
  and `U05_12`, `U05_13` occur only as hotspot names.
- **Method:** the parsers; grep of every INFOACT dump; capstone of the action-record loads.
- **Confidence:** proven.

### E-0366 — U05's `SCENE.BIN`: scale 46, FOV 90, sphere 20 / 40 (overridden to 32 / 0)
- **Binary/file:** `Data/U05/SCENE.BIN`.
- **Evidence:** payload bytes: ambient 255, 255, 255; scale `0x42380000` = 46.0;
  `#CAMERA#` FOV 90.0, radius 20.0, Z offset 40.0, speed 20.0 (overwritten, E-0039).
  `U05_StartUnit` then sets radius 32 and Z offset 0 (E-0361).
- **Method:** Python `struct` over the file.
- **Confidence:** proven.

### E-0390 — U06's vtable and start: ambient `s4_11`, talker `U06_18`, `lourde` paused, clown yaw 3π/2, sphere offset 5, camera cut and autosave
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `CreateUnitScene` case 6 → `0x00410940`: base constructor, vtable
  `0x00439760` (nothing else initialised). Vtable: `+8` `0x00410cf0` / `+0xc` `0x00410d10`
  only call `Scene_RestoreState` / `Scene_WriteState` (no unit chunk), `+0x10` the generic
  `0x0041acf0`, `+0x14` `U06_StartUnit` (`0x00410990`), `+0x18` generic, `+0x1c`
  `U06_UpdateFrameLogic` (`0x00410ab0`), `+0x30` `U06_DispatchClickActions` (`0x00410da0`,
  created), `+0x34` `0x00412aa0` (returns 1), `+0x40` `U06_HandleInput` (`0x00410d30`,
  created). `U06_StartUnit`: `+0x4c("s4_11", 1)`; `FUN_0041ae10(a, b)`; `+0x28("U06_18",
  "", "$$$DUMMY.*visage", 0, 8, 0)`; node list `+0x14("lourde", 1)` → if found
  `FUN_00420060(1)` (paused); `+0x6d4` = 0; `+0x6c8` = node `*U03_02`, its `+0x68` = 0;
  `+0x6cc` = hotspot `*U03_02`, its `+0x80` = `0x4096cbe4` (4.712389 = 3π/2);
  `FUN_00419d00(camera, 5.0)` (sphere Z offset `+0x68`); if `a`: `FUN_00419520(−673.3,
  475, 25.4)`, `FUN_00419550(2.16, π/2)`, game `+0x10(FUN_0042a3c0(0x3eb), 0)`
  (autosave). `+0x6d0` has no writer outside the frame hook's helpers.
- **Method:** capstone of `0x00410990..0x00410aa4` with strings and floats resolved; MCP
  decompile; vtable read with `pefile`.
- **Confidence:** proven.

### E-0391 — U06's clown: a safe rectangle, a 330 range, three `Tir` shots, and a hotspot turned toward the walking player
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `U06_UpdateFrameLogic`: `Scene_RenderFrame`; `U06_IsSafeFromClown`
  (`0x00410b80`): eye y (camera `+0x18`) > 280.0 → 1, else `FUN_00416030(eye, −800,
  −100000, 100000, 230)` (strict bounds on x and y); not safe → `FUN_00415e40(eye,
  hotspot +0x70)` compared with 330.0 (`0x004397b8`): `+0x6d0` = 0 and ≤ 330 →
  `U06_ClownStartShooting` (`0x00410bc0`: node running, `+0x6d0` = 1); `+0x6d0` ≠ 0 and
  > 330, or safe → `U06_ClownStopShooting` (`0x00410be0`: if `+0x6d0`,
  `FUN_00420100(49.0, 1)`, `+0x6d0` = `+0x6d4` = 0). Then `+0x6d0` and node `+0x60` →
  `FUN_004200c0(1.0)`, `FUN_00420060(0)`, `+0x50("Tir", eye, 0)`, `++(+0x6d4)` > 2
  (signed) → `U06_ShotDown` (`0x00410c20`): `FUN_00414820(0, 0)`, `RunFor(800)`,
  `MoveTo(800, none, 100, 2.0, 100)`, `MoveTo(1200, none, yaw + 0.5, 2.76, 100)`,
  `MoveTo(1400, none, yaw + π, 100, 100)`, `+0x6d4` = 0, `FUN_0041bfd0(600)`,
  `RunFor(1000)`, game `+0x14(1)`. `U06_HandleInput`: `Scene_HandleInput`, then if
  `0x0046e878` (Up) or `0x0046e880` (Down): `FUN_00415ef0(hotspot +0x70, eye, &yaw,
  &pitch)` (normalise(eye − hotspot), `X3d_Convert_To_Polar`), hotspot vtable
  `+0x20("*U03_02", yaw, pitch, 0)`. Hotspot vtable `0x00439a20` `+0x20` =
  `Hotspot_TurnToYaw` (`0x00420f00`, created): with the last argument 0 it acts on itself:
  `X3d_Make_Rotation_Matrice_Z(R, +0x80 − yaw)`, `X3d_Matrice_Mult(T, +0x88, R)`, `+0x88`
  := T, `+0x80` = yaw, `+0x84` = pitch, `+0x6c` = 1 (else match by object name and recurse
  on `+0x50`). `FUN_00420b40` (hotspot with an object) sets `+0x80` = 0, `+0x84` = π/2,
  `+0x88` = `X3d_Object_Get_Local_Matrice`. The tick `FUN_0041c350`: `Talker_Tick`, node
  tick `FUN_0041fe90`, then `Hotspots_ApplyStoredMatrices` (`0x00420e00`): for each
  hotspot with `+0x6c`, local := `X3d_Matrice_Mult(local, +0x88)`. Answers the
  `FUN_00420e00` part of Q-0026. Corpus: `Anim/U03_02/TIRE.A3D` 1..50; INFOOBJ `*U03_02`
  20 fps, paused.
- **Method:** capstone of `0x00410ab0..0x00410d98`; MCP decompile of the functions named.
- **Confidence:** proven for the logic; the visual result of the matrix product is Q-0170.

### E-0392 — U06 handlers: `OpenDoor`, `UseArrosoir` (the camera rides the watering can, the man wakes and talks), `UseBiche` (down the drain to unit 7)
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `U06_DispatchClickActions`: `FUN_0041b700`, then the queue compared with
  `OpenDoor` `0x00410e50`, `UseArrosoir` `0x00410ea0`, else `UseBiche` `0x00411140`.
  `U06_OpenDoor`: node `*U06_16` `FUN_00420060(0)`, `+0x50("s1_04", eye, 0)`,
  `FUN_00421300(list, 0, "*U06_16", 1)`. `U06_UseArrosoir`: `FUN_00414820(0, 0)`; hotspot
  `*U06_17` `+0x28("", 1, 1)` (`Hotspot_ShowOrHide` `0x00421050`: "" = itself; show =
  `X3d_Object_Unhide` and `+0x118` = 0; hide = `X3d_Object_Hide` and `+0x118` = arg 3);
  node `*U06_17` `FUN_004200c0(1.0)`, running; `FUN_00420220(node *U06_18,
  "%sAnim/U06_18/reveil.A3D", "reveil", 1, 0)`, `+0x68` = 0; half = (anim `+0x3c` −
  `+0x38`) · 0.5; loop while node `+0x60` = 0 and not `FUN_004163b0(VK_RETURN)`:
  `X3d_Object_Get_Global_Position(can)`, `FUN_00419520(G.x − 3.09, G.y − 8.542, eye z)`,
  `FUN_00419c00(0, (−1058.87, 406.222, 15.2054))` (ms 0: face the point with
  `FUN_00419580`, then `RunFor(0)`), once frame > half − 15 → `+0x50("s4_13")`, frame >
  half → `FUN_00420080(clip, 1)` (a type-0x32 slot: `FUN_004201c0(node, slot, 1)`); then
  `RunFor(0)` while the clip runs and not Enter; `Talkers_Say("U06_18", "d4_12")`;
  `MoveTo(4000, (−1049.73, 395.246, 25.41), −2.8, 0.77)`; `RunFor(0)` while scene
  `+0x168`; `MoveTo(1000, same, −5.2, 1.33)`; list `+0x28("*U06_18", 0, 1)`;
  `FUN_00414820(1, 1)`. `U06_UseBiche`: suspend; node `*U06_21` `+0x68` = 0, running;
  `+0x50("s4_15")`; wait `+0x60`; `MoveTo(1000, (−685.55, −1224.05, 25))`; `MoveTo(1000,
  (−685.295, −1224.03, −7.15), 4.28)`; `RunFor(1000)`; `MoveTo(800, none, 4.11, 2.777)`;
  `+0x70` = 1, running; `+0x50("s4_15")`; wait `+0x60`; game `+4(7)`.
- **Method:** capstone of `0x00410e50..0x004112a7`; MCP decompile.
- **Confidence:** proven.

### E-0393 — U06 corpus: scale 12, INFOACT, INFOOBJ, the clown's `Tire`, the shed, the watering can and the drain cover
- **Binary/file:** `Data/U06/SCENE.BIN`, `INFOACT.BIN`, `INFOOBJ.BIN`, `U06.X3D`, `Anim/**`,
  `Static/**`, `Sound/*.wav`.
- **Evidence:** `SCENE.BIN`: ambient (90, 90, 90), floats 12.0, 90.0, 20.0, 40.0, 7.0.
  `infoact.py --file`: M01 trig 8 `*U06_16` → op 10 `OpenDoor`; M02 take `U06_17`; M03
  trig 7 `U06_17` on `*U06_18` → op 3, `UseArrosoir`; M04 take `U06_19`; M06 take
  `U06_20`; M07 trig 7 `U06_20` on `*U06_21` → op 3, `UseBiche`; all `TRUE`, max 1.
  `infoobj.py`: `*U06_15` t5 c2, `*U03_02` t6 c0 20 fps paused, `*U06_16` t5 c2 7 fps no
  loop, `*U06_17` t5 c4 running no loop, `*U06_18` t6 c5, `*U06_19..21` t4 c4/4/5, all
  visible. Objects (`o3d.py`): `*U03_02` root of `Anim/U03_02/TIRE.O3D` (a clown:
  `TETEclown`), `lourde` → `*U06_15` in `Anim/ORANGE.O3D`, `*U06_16` in `CABANEXT.O3D`,
  `*U06_17` (children `eau02..05`) in `U06_17.O3D`, `*U06_19` in `Static/CABANE.O3D`,
  `*U06_20` in `Static/U06_20.O3D`, `*U06_21` in `u06_21.O3D`. Ranges (`a3d.py`): `TIRE`
  1..50, `CABANEXT` 1..40, `ORANGE` 0..50, `U06_17` 1..150, `U06_21` 1..30,
  `U06_18/REVEIL` 1..40. Sounds: `Tir` 1.34 s, `d4_12` 26.15, `s1_04` 4.62, `s4_11`
  21.02, `s4_12` 4.67, `s4_13` 1.74, `s4_15` 1.54. `s4_12` occurs in no `.BIN` and not in
  `MissionMonet.exe`.
- **Method:** the parsers named; Python `wave`; byte search.
- **Confidence:** proven.

### E-0394 — U07's vtable, renames and start: `Object04` → `*U06_26…`, `secretpioc`, halos out of collision, two positional loops, sphere s/4, shaft camera with walking off
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** case 7 → `0x004112b0`: vtable `0x004397d0`, `+0x6c8` = 0. Vtable: `+8`
  `U07_ReadPlancheChunk` (`0x004117b0`), `+0xc` `U07_WritePlancheChunk` (`0x00411800`),
  `+0x10` `U07_OnLoadRenames` (`0x00411300`, created), `+0x14` `U07_StartUnit`
  (`0x00411470`, created), `+0x18` `U07_DeleteEmittersAndUnload` (`0x00411740`: deletes
  `+0x184`, `+0x188`, then `0x0041ae40`), `+0x1c` `U07_UpdateFrameLogic` (`0x00411780`),
  `+0x30` `U07_DispatchClickActions` (`0x004119d0`, created), `+0x40`
  `U07_HandleLadderAndGround` (`0x00411850`, created). `U07_OnLoadRenames`: `XScene_124`;
  loop `X3d_Scene_Get_Object("Object04")` → `sprintf(name, i = 1 ? "%s" : "%s%i",
  "*U06_26", i)` from i = 0; `"secretpioc"` → strcpy `"*U06_28"`; `"*U06_27"` →
  `"*U06_29"`; `X3d_Scene_Find_First/Next_Object(…, 1)` with `strncmp(obj, "halo", 4)` = 0
  → `+0x118` = 1; object `"planche"`: strcpy into `[obj +0x20]` (its parent) `"*U06_30"`.
  `U07_StartUnit`: `+0x4c("s4_16", 1)`; camera `+0x58` = 0; `FUN_0041ae10`; actions
  `+0x42c` (M07 exhausted; the flags are at `+0x410 + 4·id`, as U02's `+0x430` = M08) = 0
  → `+0x184` = `FUN_00414c80(4, s·50)`, `SoundEmitter_Play("%sSound/s4_22.wav", (1299,
  −143, 473), 1)`; `+0x188` = `FUN_00414c80(5, s·50)`, `s4_19.wav` at (1536, 363, 374),
  loop; `FUN_00419ce0(s · 0.25)` (camera `+0x64`, `+0x6c`, sphere object `+0x10`);
  `FUN_00419d00(camera +0x5c · 0.4)`; camera `+0x3c` = hotspot `*U06_30` `+0x60`;
  `+0x420` (M04) → `X3d_Scene_Get_Object("ColGrille")` `+0x118` = 1; if `a`:
  `FUN_00419520(1454.67, 1912.72, 570.605)`, `FUN_00419550(1.04, 2.77)`, camera `+0x40` =
  0, `+0x70` = 0; inventory `+0xb8()` `+0x90("U06_19P.bmp")` → list `+0x28("*U06_19", 0,
  1)`; autosave (`0x3eb`).
- **Method:** capstone of `0x00411300..0x00411840` (strings, floats, IAT names via
  `pefile`); MCP decompile.
- **Confidence:** proven.

### E-0395 — U07's `PLANCHE` chunk is the plank-tipped flag; the input hook is a 20-unit ladder before the switch, then the plank and the water checks
- **Binary/file:** `MissionMonet.exe`; `Data/U07/Anim/PLANCHE.*`.
- **Evidence:** `U07_ReadPlancheChunk`: `FUN_0041d490(stream)`, then chunk `"PLANCHE"`
  (`FUN_00415190`) → 4 bytes into `+0x6c8`; the writer mirrors it after `FUN_0041d650`.
  The only other writer of `+0x6c8` is `U07_TipPlank` (`0x00412210`), which sets 1.
  `U07_HandleLadderAndGround`: `Scene_HandleInput`; actions `+0x414` (M01 exhausted) = 0:
  Up flag `0x0046e878` → p = eye + (0, 0, 20.0), `HasHeadroom(p)` → `MoveTo(1200, p,
  100, 100, 100)`, flag := 0; Down flag `0x0046e880` → p = eye − 20, `FUN_00416000(p)`
  (p.z − `FindGroundBelow`) ≥ camera `+0x5c` → `MoveTo(1200, p)`, flag := 0. Else:
  `+0x6c8` = 0 and `_stricmp(camera +0x3c name, "Planch01")` = 0 → `U07_TipPlank`;
  camera `+0x3c` null or `strncmp(name, "*eau", 4)` = 0 → `U07_FallInWater`
  (`0x004120a0`). `U07_TipPlank`: suspend, `+0x6c8` = 1, `MoveTo(800, (1034.62, 287.2,
  374), 7.863, 1.0108)`, `MoveTo(1000, (1034.55, 284.2, 374.3), 4.743, 0.85)`,
  `X3d_Load_Sdk_a3d(scene, "%s/Anim/planche.A3D", &root)`, strcpy root name `"*U06_30"`,
  `FUN_0041c280(root, hotspot *U06_30 +0x60, path, 30.0)`, node `*U06_30`
  `FUN_00420080(1)`, `+0x68` = 0, `+0x50("planche", eye, 0)`, `RunFor(0)` until `+0x60`,
  `MoveTo(1000, none, 100, π/2)`, resume. `U07_FallInWater`: suspend, `+0x50("eau",
  eye)`, d = normalise(`X3d_Convert_From_Polar(yaw, pitch)`), P = eye + s·(d.x, d.y),
  P.z = eye.z − `+0x5c` + 10.0, camera `+0x70` = 0, `Camera_Fall(eye, P)`, `MoveTo(800,
  P, 100, 0.5, 40)`, two `MoveTo(600, none, yaw + 3.0)`, `FUN_0041bfd0(2000)`, game
  `+0x14(1)`. Corpus: `PLANCHE.O3D` root `$$$DUMMY.Dummy02` with `planche` → `Planch01`;
  `PLANCHE.A3D` 1..50 (commented out in `U07.X3D`).
- **Method:** capstone of `0x004117b0..0x004119c0` and `0x004120a0..0x004123b8`; MCP
  decompile.
- **Confidence:** proven. Answers the U07 half of Q-0103.

### E-0396 — U07 handlers: the switch starts a 270-s gauge and lowers the player; two secret walls, the grille; `CouperDynamite` plays `Epilogue` and opens the Option menu
- **Binary/file:** `MissionMonet.exe`; `Data/Video/Epilogue.avi`, `epilogue.wav`.
- **Evidence:** `U07_DispatchClickActions`: `FUN_0041b700`; queue names in order
  `DoInterrupteur` (`0x00411ac0`), `Open1Secret` (`0x00411d70`), `Open2Secret`
  (`0x00411de0`), `CouperDynamite` (`0x00411e60`), `OpenGrille` (`0x00411d50`).
  `U07_DoInterrupteur`: suspend; node `*U06_22` running; `+0x50("s1_08bis", eye)`;
  `RunFor(0)` while `FUN_00414ed0(+0x174)`; node `*Eteint01` running; `+0x50("s4_20")`;
  `MoveTo(1000, none, 4.64, 0.3)`; wait `*Eteint01` `+0x60`; `FUN_0041a560(gauge, 270.0,
  1, "", 0)`; `MoveTo(1000, none, 1.54286, 0.530796)`; Q = eye; loop { Q.z = eye.z −
  s·0.6; `MoveTo(1000, Q)`; `RunFor(300)` } while `FUN_00416000(eye)` ≥ `+0x5c`·1.8
  (double `0x00439830`); `Camera_FollowGround(eye)`; `sprintf("%s/SAUT.WAV", app
  +0x26a)`, `FUN_00416370` (file exists) → `SoundEmitter_Play(+0x174, path, eye, 0)`;
  `MoveTo(800, none, 100, π/2)`; `MoveTo(1500, (1453.19, 1912.76, 362.294), 2.663)`;
  camera `+0x70` = 1, `+0x40` = 1; resume. `U07_OpenGrille`: `ColGrille` `+0x118` = 1.
  `U07_Open1Secret`: `+0x50("s4_21", eye, 0)`, hotspot `*U06_28` `+0x28("*U06_28", 0,
  1)`, `mursecret` `+0x118` = 1. `U07_Open2Secret`: same with `*U06_29`, then
  `FUN_004212b0` with ecx = list `+0x1a0` (a stray `""` push), `mursecreth` `+0x118` = 1.
  `U07_CouperDynamite`: `FUN_0041a680(gauge)`, `FUN_004212b0(list +0x1a0)`, hotspot
  `*U06_26` `+0x28("", 0, 1)`, `FUN_00414dc0(+0x184)`, delete, `+0x184` = 0,
  `RunFor(3000)`, `PlayVideo("Epilogue", "Epilogue", 0, 1)`, frame manager
  (`DAT_0046ec1c`) `+0xc0(0)` (the Option screen, E-0105). No suspend and no game `+4` in
  `CouperDynamite`. Corpus: `Epilogue.avi` IV50, 640×480, 100,000 µs/frame, 362 frames
  (36.2 s); `epilogue.wav` 22,050 Hz mono 8-bit, 36.97 s.
- **Method:** capstone of `0x004119d0..0x00411ef8`; MCP decompile; AVI header, `wave`.
- **Confidence:** proven.

### E-0397 — U07's gauge expiry: the explosion flickers FOV and ambient for 2 s, then game over
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `U07_UpdateFrameLogic`: `Scene_RenderFrame` (`0x0041b130`), then
  `FUN_0041a6c0(gauge, 1)` → `U07_DynamiteExplodes` (`0x00411f00`): suspend;
  `FUN_00414dc0(+0x184)`, delete; `FUN_00419550(9.16, π/2)`; `FUN_00419520(1390.44,
  −120.8, 487.27)`; `+0x50("Explosion", eye, 0)`; t0 = `timeGetTime`, last = 0; while
  now − t0 < 2000: `Camera_MoveTo(100, none, 100, 100, flag ? 70 : 90)` (flag starts 1,
  toggles); now − last > 100 → last = now, `rand()·5/0x7fff` via table `0x00412084`:
  1 → `FUN_0041b2f0(255, 0, 0)`, 2 → (128, 0, 255), 3 → (128, 255, 0), 4 → (255, 255,
  255), else (0, 0, 0); vtable `+0x1c()`; then `FUN_0041bfd0(2000)`, game `+0x14(1)`.
- **Method:** capstone of `0x00411f00..0x0041207f`; MCP decompile.
- **Confidence:** proven.

### E-0398 — U07 corpus: scale 35, INFOACT with a dead `xxx`, INFOOBJ, duplicate `Object04` / `*U06_27`, planks, water and sounds
- **Binary/file:** `Data/U07/**`.
- **Evidence:** `SCENE.BIN`: ambient (255, 255, 255), floats 35.0, 90.0, 20.0, 40.0, 7.0.
  `infoact.py --file`: ids 1..8, all `TRUE`, max 1; M01 trig 8 `*U06_22` →
  `DoInterrupteur`; M02 trig 0 → `xxx`; M03 take `U06_24`; M04 trig 8 `*U06_27` → op 4
  `*U06_27`, op 13 `s4_20`, `OpenGrille`; M05 / M06 trig 7 `U06_24` on `*U06_28` /
  `*U06_29` → `Open1Secret` / `Open2Secret`; M07 trig 7 `U06_19` on `*U06_26` →
  `CouperDynamite`; M08 take `U06_19`. `infoobj.py`: 11 hotspots, all visible;
  `*Eteint01` frame 8, 1 fps, paused, no loop. `U07.X3D` loads `Static/U07`, `ColTotal`,
  `Col`, `Anim/Lum`, `Rat`, `Rat2` ×3, `Rat3`, `boutanche`, `U06_22`, `Planche` (no
  animation), `U06_27`, then `Static/Taches`, `Cave2`, `Escalier`, `Chambre1`, `Entrez`,
  `U06_24`, `Plaque`. Objects (`o3d.py`): `Object04` in `CAVE2.O3D` and `CHAMBRE1.O3D`
  (also the unloaded `AMPOULES.O3D`); `secretpioc` in `CHAMBRE1.O3D` (and the unloaded
  `CAVE.O3D`); `*U06_27` in `Anim/U06_27.O3D` and `Static/CAVE2.O3D`; `*U06_19` in
  `CHAMBRE1.O3D`; `ColGrille` in `COL.O3D`; `mursecret`, `mursecreth` in `COLTOTAL.O3D`;
  `*eau`, `*eau0..16` in `TACHES.O3D`; `halo469..582` in `LUM.O3D`. Ranges: `U06_22`
  1..10, `U06_27` 1..70, `PLANCHE` 1..50, `LUM` 1..7. Sounds: `Couper` 0.68 s (named by
  no code), `Explosion` 4.95, `Planche` 4.10, `eau` 5.62, `s1_08bis` 1.60, `s4_16` 14.87,
  `s4_19` 6.13, `s4_20` 3.40, `s4_21` 4.34, `s4_22` 2.32.
- **Method:** the parsers named; Python `wave`.
- **Confidence:** proven.

### E-0399 — Units chain by `Game_GoToUnit`; U07 has no successor: the game ends with `Epilogue` and the Option menu; unit 50 is the gallery viewer
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** game vtable `0x00439894` `+4` = `Game_GoToUnit` (`0x00412fb0`, created):
  unit 8 → `+0x160` = 3 and scene `"U33.x3D"` (`0x0044112c`), else `+0x160` = n and
  `"U%s.x3d"` with the two-digit number. Call sites `push n; call [vtable+4]`: U01
  `0x00401c7e` (2), U02 `0x00404ab5` (3), U33 range `0x00407ebf` (4), U04 `0x0040b283`
  (5), U05 `0x00410840` (6), U06 `0x0041129f` (7); `Scene_HandleInput`
  `0x0041b8ca..0x0041b938` goes to 1..8 while Tab (`0x0046e804`) and Numpad 1..8
  (`0x0046e964..0x0046e980`) are held. No immediate argument of 8 or more appears, and U07's
  code does not call it. Unit 50 (`0x004123c0`, vtable `0x0043983c`) is created only by
  `Game_OpenGalleryView` (`0x004131e0`): a 6-character picture name (`U11_01` … `U14_07`)
  picks a scene `U01D.X3D`, `U02D`, `U03D`, `U33D`, `U04D`, `U05D` or `U06D.X3D`, stored
  at game `+0x174`; `CreateUnitScene(0x32)`, load, `SetAppMode(0)`, `+0x10`, `+0x14(1, 0)`,
  game `+0x168` = 1, `+0x170` = 1. `U50_OnLoadGalleryAmbient` (`0x00412410`) and
  `U50_StartGalleryView` (`0x00412530`) look the name up in the 18-entry table
  `0x00440d48` with unit numbers (`0x00440d90`: 1, 2, 2, 3, 33, 4 ×9, 5, 5, 6, 6) and
  camera poses (`0x00440db4`, 20 bytes each: x, y, z, yaw, pitch), start that unit's
  ambient, run its fix-ups and cut the camera; vtable `+0x30..+0x38` return 1 (no
  clicks), `+0x44` (`0x00412ab0`) stores a pick. `Data/` has no `U50` directory.
- **Method:** capstone scan of `.text` for `push imm; call [reg+4]`; MCP decompile;
  `pefile` table dumps.
- **Confidence:** proven for the chain and the end; the gallery's behaviour is not
  specified here.

### E-0300 — U03's vtable `0x004394e4`: start, frame hook and dispatcher overridden; no load hook, no save chunk; the file is `U03.cpp`
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `CreateUnitScene` case 3 → `U03::Construct` (`0x00404e70`, was
  `FUN_00404e70`): `FUN_0041a890`, vtable `0x004394e4`, `+0x6e4` (follow) = 1, `+0x6fc`,
  `+0x700`, `+0x704`, `+0x708` (cinematic objects / nodes), `+0x6e8`, `+0x6c8`, `+0x6cc`
  (emitters) = 0, `DAT_0044262c` = this. Vtable (MCP memory read): `+0` `0x00404ec0`
  (deleting destructor → `U03::Destruct` `0x00404ee0`: stop and delete both emitters,
  `U03::ReleaseCinematique`), `+8` `0x0041d490`, `+0xc` `0x0041d650`, `+0x10`
  `0x0041acf0` (all generic), `+0x14` `U03::StartUnit` (`0x00404f70`, function created),
  `+0x1c` `U03::UpdateFrameLogic` (`0x00405480`), `+0x30` `U03::DispatchClickActions`
  (`0x004054e0`, created), `+0x40` `0x0041b7f0` (`Scene_HandleInput`). `0x00406a80`
  carries the assert `D:\MissionD\Source\U03.cpp` line 0x2fa (762); renamed
  `U03::LoadCinematique`. The other U03 functions (`0x00405580`..`0x00407050`) are renamed
  after what they do (`u03.md`).
- **Method:** MCP decompile and memory read; capstone with strings resolved.
- **Confidence:** proven.

### E-0301 — `U03::StartUnit`: renames and hides before the generic start, sphere 30.5/10.5, emitters on groups 5 and 6, three talkers, M01, camera, autosave, `U01_19P`, `s2_01`
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** capstone `0x00404f70..0x0040546f`: `X3d_Scene_Get_Object` (case-sensitive,
  E-0080) of `$$$DUMMY.Dummycolis` → `X3d_Object_Hide(1)`; strcpy renames `Box121` →
  `*U03_22`, `*U03_18` → `Quille tete`, `u03_18` → `*U03_18`; `*U03_03` `+0x5c` = 1;
  `pedaledrt` `+0x118` = `+0x5c` = 1; then `FUN_0041ae10` (generic start); camera
  `FUN_00419ce0(30.5)`, `FUN_00419d00(10.5)`; hotspot list `+0x14("*U03_02", 1)` → `+0x6d0`,
  node list → `+0x6d4`; node `*U03_08` `FUN_00420060(1)`; node `*U03_09` → `+0x6dc`,
  `+0x78` = 15.0; node `*path` → `+0x6e0`, `+0x6c` = `+0x68` = 0, `+0x78` = 4.0; object
  `*path` hidden and `U03::DisableCollisionTree(its parent)` (`0x00406f60`: `+0x118` = 1 on
  the object, recursing over `+0x24` and `+0x28`); actions `+0x438` (M10 exhausted) = 0 →
  `FUN_00421330(*U03_09, 1)` else `FUN_00421330(ColClown, 1)`; `FUN_00414c80(5, 1000.0)` →
  `+0x6cc`, `SoundEmitter_Play("%sSound/s2_03.wav", global position of *U03_01, loop 1)`;
  M10 not exhausted: `FUN_00414c80(6, 1000.0)` → `+0x6c8`, `s2_04.wav` at `*U03_02`, else
  `+0x6e4` = 0; vtable `+0x28` talkers (`U03_01`, `$$$DUMMY.*visage`), (`U03_02`,
  `$$$DUMMY.visage`), (`U03_09`, `$$$DUMMY.visage`), each (…, 0, 8, 0); if `a`:
  `FUN_0041e4b0(actions +0x14)` (M01), `FUN_00415ed0(−132.19, −463.89, 70)`,
  `U03::SnapToGround` (`0x00407050`: `FindGroundBelow`, z = hit z + camera `+0x5c`),
  `FUN_00419520`, `FUN_00419550(−1.28, π/2)`, game `+0x10(message 1003, 0)`; then on both
  paths (`0x0040540d`) inventory `+0x90`/`+0xa8("U01_19P")`, vtable `+0x4c("s2_01", 1)`.
  `FUN_00414c80(group, range)` only stores them: these emitters are not in the scene's
  emitter list (`Scene_UpdateEmitterVolumes`). Supersedes `sound.md`'s "U03's code plays on
  4": U03 uses groups 5 and 6.
- **Method:** capstone (strings and float immediates resolved), MCP decompile of
  `FUN_00414c80`, `FUN_00414e00`, `FUN_00406f60`, `FUN_00407050`.
- **Confidence:** proven.

### E-0302 — U03's frame hook: the policeman takes `*path`'s transform turned by π; the two emitters are refreshed every frame
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `U03::UpdateFrameLogic` (`0x00405480`): if app `+0x47c` ≠ 1: `+0x6e4` ≠ 0
  → `U03::FlicFollowPath` (`0x00405580`); `FUN_00414e00(+0x6c8)`, `FUN_00414e00(+0x6cc)`
  (volume from distance when the group plays and a handle is held); `Scene_RenderFrame`.
  `0x00405580`: if node `+0x6dc` `+0x60` = 0: `X3d_Object_Get_Local_Matrice(path obj)`,
  `X3d_Make_Rotation_Matrice_Z(π)`, `X3d_Matrice_Mult(A, Rz, pathLocal)`,
  `X3d_Matrice_Mult(B, flicLocal, A)`, `X3d_Object_Set_Local_Matrice(flic, B)`, then
  `X3d_Object_Set_Global_Position(flic, global position of the path object)`. The main
  loop runs the tick (`+0x24`) before `+0x1c` (E-0046), so the pose composed is the one
  just sampled. `Matrice_Mult(dst, a, b)` = a·b (E-0042).
- **Method:** MCP decompile.
- **Confidence:** proven.

### E-0303 — `AnimeSpeakClown`: walk, two lines, the clown's model swapped for `U03_02.O3D` + `magie.A3D`, the postcard `U03_06P`, the policeman stops, the clown walks off
- **Binary/file:** `MissionMonet.exe`; `Data/U03/Anim/**`.
- **Evidence:** `0x00405670`: `FUN_00414820(0, 0)`; `FUN_00421330(*U03_09, 0)`,
  `(ColClown, 1)`; `Talkers_Say("U03_02", "U03_01_04")`; `FUN_00421300(+0x6d0, 0)`; clown
  local position, `FUN_00415ed0(−126, −581, eye z)`, direction normalised → polar;
  `FUN_00419620(eye, target, yaw, dirYaw, pitch, π/2, 6000, 0)` (arguments traced through
  the stack, `0x004057b4..0x004057d3`; the function's full signature and yaw wrap from its
  decompile); `RunFor(0)` while `+0x178` plays and not `FUN_004163b0(0x0d)`;
  `Camera_MoveTo(3000, (−118, −644, 71), 1.62, 1.6, 43.0)`; scene `+0x1a4` = 0;
  `U03::SwapClownModel` (`0x00405b60`: free the object's `+0x128`, `X3d_Object_Release`,
  `FUN_00420080(old node, 0)`, `X3d_Animation_Release`, node name `ClownDeleted`,
  `XObject3D_60("%sANIM/U03_02/U03_02.O3D")`, cursor `[+0x128]` = 0, `+0x1a8` = 0,
  `+0x1a4` = hotspot, `GetCursorPos`/`ScreenToClient`/vtable `+0x44`, vtable
  `+0x20("%sANIM/U03_02/magie.A3D", obj, 15.0)` → `+0x6d4`, `FUN_004200c0(1.0)`, paused,
  `+0x68` = 0, talker `U03_02` renamed `Deleted`, vtable `+0x28("U03_02", "",
  "$$$DUMMY.visage", 0, 8, 0)`, eye x += 3.5 (`0x00439540`), z += 5 (`0x004394cc`),
  `FUN_004194f0`, stop and delete `+0x6c8`); `Say("U03_02", "U03_01_04B")`, `timeGetTime`;
  `Camera_MoveTo(3000, saved eye, yaw, pitch, 90.0)`; loop: > 9000 ms or Enter → node
  enable + run; node run; loop while the voice plays: frame > 48.0 (`0x0043953c`) or Enter
  → `U03::GiveCartePostale` (`0x00405b00`: `*U03_03` `+0x5c` = 1, inventory
  `+0x90`/`+0xa8("U03_06P")`); `U03::FlicAttenteHorloge` (`0x00405db0`:
  `FUN_00420220(*U03_09 node, "Anim/U03_09/PARLENBOUCLE.A3D", "AttenteHorloge", 1, 1)`,
  `+0x68` = 1, `+0x78` = 20.0, running, `+0x6e4` = 0, `FUN_00421300(list, 3, "*U03_09")`,
  `FUN_0041e2a0(actions +0x60 = M20, 1)`); tick while node `+0x60` = 0 and not
  `FUN_00419c70(1)`; pause; voice playing → `RunFor(7000)`; `FUN_00420220(+0x6d4,
  "Anim/U03_02/marche.A3D", "marche", 1, 1)`, `+0x68` = 0, `+0x78` = 15.0, paused,
  `U03::AnimateTransition(+0x6d4, clip, 10, node frame, clip frame)`, running, frame += 1.0
  per `RunFor(0)` until paused; hotspot vtable `+0x28("", 0, 1)` (`0x00421050`, E-0272;
  vtable read at `0x00439a20`); `FUN_00414820(1, 1)`. `FUN_00420220(parent, path, name,
  slot, active)`, `FUN_00420360(parent, name, exact)` returns the slot or 0 (MCP decompile).
- **Method:** capstone and MCP decompile.
- **Confidence:** proven.

### E-0304 — `FlicSalut`: walk to (−489, −464) on the ground, `salut` in slot 2 with transitions both ways
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `0x00405e90`: suspend; `FUN_0041b440("*U03_09", 0)` local position;
  target (−489, −464, eye z) through `U03::SnapToGround` (the 4.72 stored in the next slot
  is overwritten by the polar yaw; stack traced `0x00405efd..0x00405fc7`);
  `FUN_00420360(node, "AttenteHorloge", 1)` `+0x68` = 0; `FUN_00419620(eye, target, yaw,
  dirYaw, pitch, π/2, 2000, 0)`; `FUN_00420220(node, "Anim/U03_09/salut.A3D", "salut", 2,
  0)`; `U03::AnimateTransition(Attente, salut, 10, its frame, salut frame)`;
  `FUN_00420080(salut, 1)` (type-0x32 node: `FUN_004201c0(parent, slot, 1)`), `+0x68` =
  0, `+0x78` = 15.0, running; `RunFor(0)` until frame ≥ last − 10; transition back with
  (−1, −1); Attente active, running, `+0x68` = 1; `RunFor(0)` while
  `LSoundManager_IsGroupPlaying(2)`; resume.
- **Method:** capstone.
- **Confidence:** proven.

### E-0305 — `DoCinematiqueFlic`: the Coordcam/Cine01 cutscene with cuts on Coordcam frames, then `U33.X3D`; `AnimateTransition` lerps translations
- **Binary/file:** `MissionMonet.exe`, `x3d.dll`; `Data/U03/cinematiques/*`.
- **Evidence:** `0x00406250`: suspend; `FUN_0041e2a0(actions +0x74 = M25, 0)`;
  `FUN_00421300(list, 0, "*U03_08")`; inventory `+0x98` (hide the bar, E-0252);
  `U03::LoadCinematique` (`X3d_Load_Sdk_o3d` `cinematiques/Coordcam.o3d` → `+0x6fc`,
  `Cine01.o3d` → `+0x700`; `X3d_Load_Sdk_a3d` of each `.a3d`, `FUN_0041fc20(type 1)`,
  `FUN_0041fe60(node, anim, obj, 15.0, loop 0, paused 1)`, frame 1.0, paused → `+0x708`
  (Coordcam), `+0x704` (Cine01), appended at the end of node list `+0x158` via `+0x50`,
  vtable `+0x24`, both objects hidden); the walk of `FlicSalut` with 800 ms; run `"M31"`
  (`FUN_0041dea0(actions +4, "M31", 1)`, `FUN_0041e4b0`); `FUN_00420220(node,
  "Anim/U03_09/REFLECTION.A3D", "refelction", 3, 1)`, transition (−1, −1), 15 fps, tick +
  `Scene_RenderFrame` until frame ≥ last − 47, pause; `FUN_00419620(eye, eye, yaw, 3.17
  (`0x004394e0`), pitch, π/2, 2000, 0)`; `RunFor(4500)`; `FUN_00420220(node,
  "Anim/U03_09/GOTOHORLOGE.A3D", "vers horloger", 4, 1)`, loop 0, 15 fps, paused,
  `DAT_00442628` = it; `U03::FindObjectInTree(+0x6fc, "*camera")`; both nodes frame 1.0 and
  `FUN_0041fe90`; hide the clip's object (the policeman); duration = last / fps;
  `FUN_00419620(eye, (−871.48, −584.464, *camera z), yaw, yaw, pitch, π/2,
  ftol(duration)·1000, U03::CinematiqueWalkCallback)`. Callback `0x00406120`: step = 8 →
  `X3d_Object_Unhide`, run; `DAT_00442628` set and last − 45 < frame → `FUN_0041e4b0(actions
  +0x94 = M33)`, clear; aim at the global position of (`*camera` `+0x20`) `+0x24` via
  `FUN_00419550`. After the walk: pending → M33; callback(…, 100, 100); tick + render
  until the clip pauses; unhide `+0x700`, hide the policeman, run `+0x704`, `+0x708`;
  node `*U03_08` running, `+0x68` = 0; d = (50.0 − X3D camera `+0x50`) · 0.05; loop while
  `+0x704` runs: cuts at Coordcam `+0x74` > 1/132/186/278 for k = 0/2/3/5
  (`0x00439460`, `0x00439554`, `0x00439550`, `0x0043954c`): `FUN_00419520(*camera global)`,
  `FUN_00419580(camera, target)` (yaw/pitch of target − camera), k++, break at 6; > 240
  (`0x004394c4`) and k = 4 → run `"M35"`, k = 5; > 20 and k = 1 → k = 2; `RunFor(0)`;
  camera `+0x10` > 50 → `+0x10` and X3D `+0x50` += d. Then pause both, `RunFor(7000)`, run
  both; `RunFor(0)` until frame ≥ 420 (`0x00439548`), one cut at > 360 (`0x00439544`)
  with k = 6; wait for the voice group; strcpy `"U33.X3D"` (`0x0043f940`) to game `+0x14c`,
  `SetAppMode(1)`, `U03::ReleaseCinematique`, `FUN_00414820(1, 0)`.
  `U03::AnimateTransition` (`0x00406f90`): for i = 1..n: vtable `+0x24`,
  `X3d_Object_Animate_Transition(obj, animA, fa, animB, fb, i/n, 1, 1)`, `RunFor(0)`.
  In `x3d.dll` (`0x10001032`) it calls four per-track functions and, for t < 0.5,
  `FUN_10004860` on both; the first (`FUN_10004d70`) samples each clip's translation keys
  linearly between the bracketing keys and writes pa + t·(pb − pa) to the object's local
  translation, recursing over children (last argument).
- **Method:** capstone (stack traced by hand for the `FUN_00419620` arguments), MCP
  decompile in both programs; `o3d.py`/`a3d.py` over the cinematic files (`Coordcam`:
  `$$$DUMMY.Dummy01` with children `*Target`, `*camera`, 450 frames; `Cine01` 600 frames).
- **Confidence:** proven for the flow; which child `+0x24` is: Q-0142; the other tracks of
  the transition: Q-0143.

### E-0306 — U03 corpus: INFOACT, INFOOBJ, objects, clips and sounds
- **Binary/file:** `Data/U03/**`, `Data/U04/INFOACT.BIN`, `MissionMonet.exe`.
- **Evidence:** `SCENE.BIN` (`binchunk.parse`): ambient 255/255/255, scale 45.0; camera FOV
  90, radius 20, Z offset 40, speed 7. `infoact.py --file Data/U03/INFOACT.BIN`: ids 1, 2,
  10, 20, 25, 30, 31, 33, 34, 35, 40, 45, 50, 51 with the steps and conditions tabled in
  `u03.md`; M34 and M50 have trigger 0 and nothing runs them (no `M34`/`M50` string in the
  EXE, no read of actions `+0x98`/`+0xd8` in U03's code, no op 14 naming them).
  `infoobj.py`: 26 hotspots, hidden `*U03_06`, `*U03_24`, `*U03_26`, `*U03_29`. `o3d.py`
  over `U03.x3d`'s `OBject=` files: no object for `*U03_07`, `17`, `18` (after the rename),
  `19`, `21`, `25`..`29`, nor for `$$$DUMMY.Dummycolis` or `u03_18`; `*U03_06` only in
  `Anim/U03_02/MAGIE.O3D` (loaded by no code or script); clown root `*U03_02` at
  (−115.7, −667.4, 47.5), `*U03_01` at (645.7, 22.1, 41.4), `*U03_09` at
  (−490.8, −421.9, 50.1), door `*u03_08` at (−859.5, −447.2, 59.5). `a3d.py` frames:
  PARLENBOUCLE 1..200, salut 1..90, REFLECTION 1..170, GOTOHORLOGE 1..155, U03_09 marche
  1..62, path 1..3000, magie 1..130, U03_02 marche 1..38, Jongleur 1..70, attente 1..250,
  portehorl 0..100. Sounds (Python `wave`): `U03_01_01` 12.45 s, `_03` 14.02, `_04` 17.93,
  `_04B` 27.68, `_05` 2.86, `_06` 3.81, `_07` 2.69, `_08A` 21.92, `_08C` 19.57, `_08D`
  18.74, `_08E` 16.16, `_09` 2.06, `s2_01` 35.57, `s2_03` 21.26 (16-bit), `s2_04` 5.32,
  `s2_05` 2.15. No EXE or INFOACT reference to `U03_01_02`, `U03_01_0506`, `s2_06`.
  `U03_06` is used in U04 (M17, `UseCartePostale`). `U03D.X3D` is referenced only from
  `Game_OpenGalleryView` (`0x0041346a`).
- **Method:** the parsers named; byte search of the EXE; MCP xrefs.
- **Confidence:** proven.

### E-0330 — U04's unit class: vtable `0x00439630`; `U04.x3d` is the unit scene, `U04D.X3D` a gallery backdrop, `U04Cpl.x3d` unused
- **Binary/file:** `MissionMonet.exe`; `Data/U04/U04.x3d`, `U04D.x3d`, `U04Cpl.x3d`.
- **Evidence:** `CreateUnitScene` case 4 → `0x0040a720` stores vtable `0x00439630` and zeroes
  unit `+0x6e8`, `+0x6ec`, scene `+0x184`, `+0x6d4..+0x6e4`, `+0x6d0`. Vtable: `+8`
  `U04_ReadParamsChunk` (`0x0040b2c0`), `+0xc` `U04_WriteParamsChunk` (`0x0040b330`),
  `+0x10` generic `0x0041acf0`, `+0x14` `U04_StartUnit` (`0x0040a7a0`), `+0x1c`
  `U04_UpdateFrameLogic` (`0x0040aac0`), `+0x30` `U04_DispatchClickActions`
  (`0x0040adb0`), `+0x40` `U04_HandleInput` (`0x0040afd0`), `+0x44`
  `U04_PickHoverHiddenTargets` (`0x0040b3a0`), the rest generic (`+0x34` `0x00412aa0`,
  `+0x48..+0x54` sound). `U04D.X3D` (`0x0044114c`) is referenced only by `FUN_004131e0`
  for `U13_01`, `U13_03`, `U13_04`, `U13_05`, `U13_06`, `U13_11`, `U13_12`, `U13_13`,
  `U13_14` (unit class `0x32`, E-0037). No string `Cpl` in either EXE or any DLL of
  `02_PR`. `diff` of the scripts (CR stripped): `U04Cpl.x3d` = `U04.x3d` with the
  `irisdevant`, `arbrefond`, `arbustefond`, `plantelac1..6`, `plante1..4`,
  `plantelacdevant1`, `chevaletpetit` lines uncommented and without
  `static\ColTable04.o3d`; `U04D.x3d` has `COLBARQUE.O3D` for `CANNAPECHE.O3D`, pots
  `potbas1/2`, `pothaut2/3` on, and `tubepeinture`, `morceauverre`, `coffre`, `abeille`,
  `BARKE_PLACEMENT`, `rondbarke`, `Salon`, `Chaise`, `U04_37`, `PinssoPalette`,
  `ColTable04`, the `tablo3`/`porche` animations, `U04_02\Ouvre01.a3d` and Monet
  (`anim\U04_03\U04_03.o3d`, `peint.a3d`) off.
- **Method:** MCP decompile and memory read; `diff`; Python byte search of `02_PR`.
- **Confidence:** proven.

### E-0331 — `U04_StartUnit`: fix-ups, sphere 5/0, emitters by state, boat restore, talker, face, autosave
- **Binary/file:** `MissionMonet.exe`; `Data/U04/SCENE.BIN`, `Anim/**`, `maps/tete*.dmf`.
- **Evidence:** `0x0040a7a0` (EBX = first argument `a`): game `+0x160` = 4; vtable
  `+0x4c("s3_01", 1)`; `U04_FixObjectNames` (`0x0040e720`); `+0x6f8` =
  `X3d_Scene_Get_Object("Box70")`; `FUN_0041ae10(a, b)`; `FUN_00419ce0(5.0)`,
  `FUN_00419d00(0.0)`; `+0x6c8`/`+0x6cc` hotspot/node `*U04_03`, `+0x6f0`/`+0x6f4`
  `*U04_32`; action manager `+0x488` (id 30) = 0 → `+0x6d4` = `*U04_43`'s hotspot object;
  `+0x4a8` (id 38) = 0 → `+0x6d8` = `*U04_52`'s; `+0x41c` (id 3) and not `+0x454` (id 17)
  → `U04_StartStudioEmitter` (`0x0040b9e0`: new emitter `FUN_00414c80(5, s·50.0)` at
  scene `+0x188`, `SoundEmitter_Play("%sSound/s3_07.wav", (165.82, 332.92, 15), 1)`); id 3
  and not `+0x424` (id 5) → `U04_StartBeeEmitter` (`0x0040bab0`: group 4, `+0x184`,
  `s3_05.wav` at `*U04_06` hotspot `+0x70`, looping); `+0x6ec` ≠ 0 →
  `FUN_00419520(x, y, boat hotspot z + 10.0)`, scene `+0x138` = 20.0; vtable
  `+0x28("U04_03", "", "$$$DUMMY.*visage", 0, 8, 0)`; id 18 (`+0x458`) and not id 20
  (`+0x460`) → `U04_SetMonetFaceMap(1)`; `+0x6e4` → `pain_Sot01` `+0x5c` = 1; id 18 →
  `kokliko01` `+0x5c` = 1 if found; `a` ≠ 0 → inventory `+0x90`/`+0xa8` `U01_04P`,
  `U03_06P`; `FUN_00419520(−33.566, 352.43, 15.0)`, `FUN_00419550(1.36, π/2)`; game
  `+0x10(FUN_0042a3c0(0x3eb), 0)`. `U04_SetMonetFaceMap` (`0x0040d630`): `TETE` of Monet's
  object (`FUN_0041b4c0`, exact = 1), first material's map, `X3d_Map_Create`, name
  `tete.dmf` (`0x004404d8`, arg 0) or `teteBA.dmf` (`0x004404e4`, arg 1), `X3d_Map_Init`,
  `X3d_Scene_Add_Map`, `X3d_Material_Update`, `+0x6e8` = 1. `U04/maps` holds `tete.dmf`
  and `teteBa.dmf`; `U04/Sound` has no `.bin`. `U04/SCENE.BIN`: ambient 255/255/255,
  f32 10.0, 90, 20, 40, 7.
- **Method:** MCP decompile; capstone with strings and floats resolved; directory lists.
- **Confidence:** proven.

### E-0332 — U04's `PARAMS`: on the boat, face swapped (never read), painting done
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `U04_ReadParamsChunk`/`U04_WriteParamsChunk` (E-0182) move `+0x6ec`,
  `+0x6e8`, `+0x6e4` (4 bytes each). Every access in `0x0040a720..0x0040ece0` (capstone
  scan): `+0x6ec` written by the constructor, `U04_StepOntoBoat` (1) and
  `U04_JumpOffBoat` (0), read by start, the frame hook and the input hook; `+0x6e8`
  written by the constructor and `U04_SetMonetFaceMap` only, read by nothing but the
  chunk writer; `+0x6e4` written by the constructor and `U04_MonetFinishesPainting` (1),
  read by start and `U04_ScrollTableau`. Answers Q-0103 for U04.
- **Method:** capstone scan of the U04 range for `+0x6d0..+0x6f8`; MCP decompile.
- **Confidence:** proven.

### E-0333 — U04's frame, input and hover hooks
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `U04_UpdateFrameLogic` (`0x0040aac0`): `Scene_RenderFrame`; gauge `+4` ≠ 0:
  (not id 3, label `Door` `0x0043ffd8`, `FUN_0041a6c0(gauge, 1)`) → Monet slot 1 `+0x70`
  = 1, running, `+0x78` = 10.0, door node `+0x70` = 1, running, loop `RunFor(0)` + vtable
  `+0x40` until door `+0x60`, camera `+0x40` = 1, `FUN_0041e2a0(M02, 1)`; (not id 17,
  camera x > 180, y > 275, label `Paint`, fired: the fire test is the last operand) →
  `U04_MonetFinishesPainting`; (`+0x6ec`, `ecroule`, fired) → `U04_BoatSinks`
  (`0x0040d4e0`); (`PlusVite`, fired) → `+0x48("d3_20", eye − (s·10, 0, 0))`. Then id 17
  and not id 18 and y < 40 → `U04_AuSecours` (`0x0040d720`); id 18, not id 20, not id 40
  (`+0x4b0`), distance to (213.47, 296.4, 15) < 2·s → `U04_ErnestLocksStudio`; not
  `+0x6ec` and `_stricmp(camera +0x3c, "*U04_32")` = 0 → `U04_StepOntoBoat`.
  `U04_HandleInput`: not on boat: id 24 (`+0x470`), Shift (`0x46e820`), distance to
  (191, 240.8, 15) < s·0.5, yaw := `FUN_00416080` (fmod into [0, 2π)), |yaw − 1.54| < 1.5
  → `U04_ClimbOutOfWindow` (`0x0040dde0`); id 32 (`+0x490`), id 39 (`+0x4ac`), Up
  (`0x46e878`), x < −22, y > 307, |yaw − 4.9| < 1.5 → suspend, `Camera_MoveTo(2000,
  (−28.948, 358.7, 15), 4.6, π/2, 90)`, `FUN_0041bfd0(2000)`, `PlayVideo("GivParis",
  "s6_1", 0, 1)`, game `+4(5)`. On boat: Up → `U04_RowBoat(0, 1)`, Down (`0x46e880`) →
  `(0, 0)`; Shift → slot = boat node `+0x18c` or the node; frame `+0x74` < 60 or > anim
  last − 60 → `U04_JumpOffBoat`, `FUN_004200c0(1.0)`; no slot → `U04_JumpOffBoat`. Then
  camera `+0x3c` == `+0x6f8` → climb out; `Scene_HandleInput`.
  `U04_PickHoverHiddenTargets`: `+0x5c` = 0 on the four `+0x6d4` objects,
  `Scene_PickHover`, `+0x5c` = 1.
- **Method:** MCP decompile; capstone for strings, floats and the Say arguments.
- **Confidence:** proven.

### E-0334 — U04's door, studio, pot, tube, painting-finished and painting-view handlers
- **Binary/file:** `MissionMonet.exe`; `Data/2dbit/U13_*`, `U14_01*`, `U16_0*`.
- **Evidence:** dispatcher `0x0040adb0`, order as in `u04.md`. `U04_MonetOpenDoor`
  (`0x0040b400`): run count `+0x818` (M02) = 1 → `FUN_00420220(Monet, ouvre01.A3D,
  "OpenDoor", 1, 1)`; door anim `+0x3c` = 0x19; `+0x50("s3_13", eye)`; `d3_01`
  (`0x004400f0`) / `d3_02` (`0x004400e8`); `FUN_0041a560(12.0, 0, "Door", 0)`.
  `U04_EntrerDansAtelier` (`0x0040b630`): moves of 1000/1500/1000/9000/3000 ms as
  specified, `d3_03`, clips `ouvre02`, `change`, door `ouvre02` frame := anim `+0x3c`; M07
  (`+0x2c`) FALSE, loop while the voice plays and id 7 is not exhausted, TRUE; app
  `+0x484` 0/1. `U04_UsePot` (`0x0040bb80`): `FUN_00420080(*U04_06 node, 0)`, hide
  `*U04_06`, show `*U04_53`, `FUN_00414dc0(+0x184)`, `s3_06`, `*U04_07` cursor 4.
  `U04_UseTube` (`0x0040bc20`): `FUN_0041a560(80.0, 0, "Paint", 0)`, `Recharge.A3D` in
  slot 2, `FUN_004203c0(2)` deletes slot 2 (`+0x188[2]`, count −1).
  `U04_MonetFinishesPainting` (`0x0040bd50`): `far` = y > 308 (`fcomp`, `test ah, 0x41`
  at `0x0040bd87`), clips and lines `d3_14` (`0x0044029c`), `d3_17` (`0x00440254`), Enter
  = `FUN_004163b0(0xd)`, `+0x6e4` = 1, Monet cursor 5, hide `*U04_50`, `range.A3D`, M17
  (`+0x54`) TRUE, `FUN_0041a680`. `U04_EnablePaintingActions` / `Disable`
  (`0x0040c3f0` / `0x0040c440`): manager `+0x30..+0x50` (ids 8..16), `FUN_0041e2a0(1/0)`,
  cursor 2/0 on each action's hotspot `+0xac`. `U04_ScrollTableau` (`0x0040c240`):
  current action (`+0xc`) id `+8`, switch 8..16 → frame manager (`DAT_0046edb0`) `+0xc8`
  (`0x00426780`: frame `TableauJeu` via `+0x90`, `+0x114(id)`, app `+0x47c` = 2,
  `+0x484` = 0); the guard `strstr("d3_14"/"d3_03", voice emitter +0x18)` looks for the
  stored full path (`FUN_0041baf0` builds `%sSound/%s.WAV`; `SoundEmitter_Play` copies it
  to `+0x18`) inside the short literal, so it never matches; then id 7 and not `+0x6e4` →
  `FUN_0041a560(30.0, 0, "Paint", 0)`.
- **Method:** MCP decompile; capstone.
- **Confidence:** proven.

### E-0335 — `UseCartePostale` (Mazout) and `U04_AuSecours` (the kidnapping)
- **Binary/file:** `MissionMonet.exe`; `Data/U04/Anim/U04_04/`, `Sound/`.
- **Evidence:** `0x0040c490`: `Camera_MoveTo(4000, (201.19, 300.77, 15), 6.24, π/2)`,
  `replace.A3D`, `parle02.A3D`, `FUN_00414dc0(voice)`; `FUN_00420a90(new, 6, 0,
  "*U04_04", 0)`, `XObject3D_60("%sANIM/U04_04/U04_04.o3d")`, hotspot list `+4`, vtable
  `+0x20(invite.a3d)`, `+0x28("U04_04", "", "$$$DUMMY.*visage", 0, 8, 0)`; `ZIVAT.A3D`
  until frame 50 (`0x00439448`); P = Monet position + (s, −s·0.5) (cdecl
  `X3d_Object_Get_Global_Position`, `0x0040c816..0x0040c83e`), `FindGroundBelow`
  (`0x00415f40`) + camera `+0x5c`, `Camera_MoveTo(800, P, 3.14, π/2)`, until frame 300
  `FUN_004194f0(P)`; `Camera_MoveTo(2000, (78.51, 272.95, 15), 3.4, 1.5)`; `Say(U04_03,
  "d3_18b")`; `Presente.A3D`; `+0x50("ArbreCraque", eye − (10, 0, 0))`, `RunFor(1500)`;
  `Say(U04_04, "d3_19")` with a 1000 ms `timeGetTime` cap; `Course.A3D` "Mazout", first
  frame > 50 → `+0x50("s3_08_pas", the same point)`, frame > 100 → `FUN_00419bc0(0,
  Mazout's object)`; `Camera_MoveTo(1000, (75.9, 261.43, 15), 2.071)`; hide `*U04_04`,
  show `*U04_44`; release; `parle04.A3D` 5 fps. `U04_AuSecours` (`0x0040d720`): manager
  `+0x458` = 1; `+0x48("d3_21", eye − (s·8, 0, 0))`; `evanoui.A3D` looping; hide
  `*U04_08`; `U04_SetMonetFaceMap(1)`; door `SENVAT.A3D` slot 1 paused at frame 1;
  `FUN_0041a560(6.0, 0, "PlusVite", 0)`; hide `kokliko01`.
- **Method:** MCP decompile; capstone.
- **Confidence:** proven.

### E-0336 — `U04.cpp:1066` is Ernest locking the studio
- **Binary/file:** `MissionMonet.exe`; `Data/U04/Anim/Ernest/`.
- **Evidence:** `0x0040d8a0` (renamed `U04_ErnestLocksStudio`; its error call passes line
  `0x42a` = 1066 and `D:\MissionD\Source\U04.cpp`): suspend; `FUN_0041e3a0(M40)`
  (exhausted); `FUN_00419bc0(800, Monet's object)`; `+0x48("d3_23", eye)`; `timeGetTime`;
  `X3d_Load_Sdk_o3d("%sANIM/Ernest/ERNST2.O3D")`, `X3d_Scene_All_Light_Include_Object`;
  vtable `+0x20(respect.A3D, obj, 15.0)`; `FUN_00419bc0(1000, door object)`; wait while
  the voice plays, < 28000 ms, Enter up; `SENVAT.A3D` "senvat"; door slot running; frame
  ≥ 70 (`0x004396cc`); `s3_09a`; door paused; `RunFor(2000)`; `X3d_Animation_Release`
  ×2, `X3d_Object_Release`; show `*U04_36`; door cursor 5; Monet cursor 2; M20 (`+0x60`)
  TRUE; stop the effects group; resume; `RunFor(2000)`; `s3_09b`.
- **Method:** MCP decompile; capstone.
- **Confidence:** proven.

### E-0337 — U04's ungagging, hints, window and ladder handlers
- **Binary/file:** `MissionMonet.exe`.
- **Evidence:** `U04_EnleverBaillon` (`0x0040dc20`): `U04_SetMonetFaceMap(0)`,
  `reveil.A3D`, `Talkers_Say("*U04_03", "d3_24")` (`0x0040dc8c..0x0040dc96`), Monet cursor
  3, `parle03.A3D`, `*U04_22` cursor 2, `*U04_23` cursor 4, app `+0x484` 0/1 around a
  voice loop with vtable `+0x40`, 6 fps. `U04_MonetTalkAfterBaillon` (`0x0040e5c0`): id
  29 (`+0x484`) or id 24 exhausted → nothing; count `+0x8b4` 1 → `d3_25`, 2 → `d3_26`,
  else ⌊rand·2/32767⌋ = 1 → `d3_25`, else `d3_26`. `U04_MonetTalkAfterMarteau`
  (`0x0040e640`): count `+0x8b8`: 1 → id 29 ? `d3_29` : `d3_28`; 2 → `d3_29`; 3 → id 29 ?
  `d3_29` : `d3_30`; else r = ⌊rand·3/32767⌋: id 29 or r = 2 → `d3_29`, r = 1 → `d3_28`,
  else `d3_30`. `U04_BriserVitre` (`0x0040cd50`): `+0x50("Vitre", eye)`, show `*U04_41`,
  wait for the effects group, climb out. `U04_ClimbOutOfWindow` (`0x0040dde0`):
  `Camera_MoveTo(1000, (194, 246, 21), 1.707, 1.57)`, `(1000, (186, 220.26, 21), keep)`,
  `Camera_ApplyVelocity(1)`, `s3_12`. `U04_MonterSurEchelle` (`0x0040ded0`): y < 240 →
  `(187.89, 234, 24)` 4.9 / 1.57, `(189.43, 244, 24)`, step, `s3_12`; else climb out.
  `U04_UseEchelle` (`0x0040deb0`): `+0x6d8` = 0, `*U04_63` cursor 2.
- **Method:** capstone (Say arguments; the decompiler drops them); MCP decompile.
- **Confidence:** proven.

### E-0338 — U04's boat: step on and off, rowing, sinking, cork, oars
- **Binary/file:** `MissionMonet.exe`; `Data/U04/Anim/BARKE_*.A3D`.
- **Evidence:** `U04_StepOntoBoat` (`0x0040cdf0`): `+0x6ec` = 1, `+0x138` = 20.0, eye =
  the boat hotspot's position + 10 z, camera `+0x40` = `+0x70` = 0, `FUN_00419bc0(0,
  *U04_43)`; run count `+0x888` (M30) = 0 → if gauge `+4`: a `FUN_0041a510` copy of its 15
  dwords at `+0x6d0`; `FUN_0041a560(20.0, 1, "ecroule", 0)`, `+0x50("s3_15", eye)`;
  `*U04_36` cursor 5; M29 (`+0x84`) TRUE. `U04_JumpOffBoat` (`0x0040cfa0`): `+0x138` =
  10.0, `+0x6ec` = 0, `Camera_MoveTo(2000, (149.87, 60.56, −9.0), 0.427, π/2)`, camera
  `+0x40` = `+0x70` = 1, `+0x3c` = 0; label `ecroule` → stop the gauge, stop `+0x174`,
  copy back and free `+0x6d0`; `*U04_36` cursor 0; M29 FALSE. `U04_RowBoat`
  (`0x0040d0b0`): right = `+0x494` | `+0x498`, left = `+0x49c` | `+0x4a0`; clip names
  `Rond` (`0x00440484`), `Traj` (`0x004404ac`), loaded with loop 1, paused, 30 fps;
  direction `+0x70` as in `u04.md`; `s3_14`; `FUN_0041ff20(slot)`; boat position, eye +
  10; `FUN_00415ef0(eye, *U04_43 position, &yaw, &pitch)`, `+6.283` while < 0
  (`0x0040d414..0x0040d45f`); |ftol(camera yaw − yaw)| + |ftol(camera pitch − pitch)| >
  0.6 → `FUN_00419c00(1000, position)`, else `FUN_00419550` (`0x0040d463..0x0040d4cd`).
  `U04_BoatSinks` (`0x0040d4e0`): `BARKE_PLACEMENT_COULE1.A3D` "deplacement", 30 fps,
  `s3_15`, the eye follows, `FUN_0041bfd0(2000)`, game `+0x14(1)`. `U04_UseBouchon`
  (`0x0040dfd0`): `+0x6d4` = 0, stop the gauge and `+0x174`, restore `+0x6d0`.
  `U04_RameToGauche` / `Droite` (`0x0040cdb0` / `0x0040cdd0`): cursor 0 on `*U04_40` /
  `*U04_39`.
- **Method:** MCP decompile; capstone.
- **Confidence:** proven.

### E-0339 — `UseCle`, the exit to U05, and U04's item path
- **Binary/file:** `MissionMonet.exe`; `Data/U05/INFOACT.BIN`; `Data/Video/GivParis.avi`.
- **Evidence:** `U04_UseCle` (`0x0040e030`): Monet cursor 0; M43 (`+0xbc`) FALSE; x ≤ 156
  → `(135.25, 280.78, 15)` yaw 0.5, else `(169.9, 269.81, 15)` 3.64; `s3_18`;
  `RunFor(400)`; door slot `FUN_00420080(1)`, `+0x70` = 1, 15 fps, loop 0; `RunFor(1000)`;
  `d3_31B`; `RACOMPAGNE.A3D` to half, `FUN_00419bc0(1000, TETE)`, to last − 30;
  `Camera_MoveTo(5000, (80.5, 259.2, 15), 5.042)`; `+0x490` (id 32) = 0 → `d3_31_3`,
  `TROUVLEGANT.A3D`, look at `*U04_44`, camera `+0x40` = `+0x44` = 0, loop until id 32,
  `d3_35` (`0x0040e45c..0x0040e48a`); `ASSOIT.A3D`, `parle04.A3D` 5 fps; id 32 → `d3_35`
  (`0x0040e576..0x0040e58e`). Exit: E-0333. `infoact.py` on U05: M09 uses `U04_44` on
  `*U05_05` (use up). E-0253: `U01_04` is U04's M03.
- **Method:** MCP decompile; capstone; `infoact.py --file`.
- **Confidence:** proven.

### E-0340 — U04's INFOACT/INFOOBJ, and `Say("*U04_03")` finds no talker
- **Binary/file:** `MissionMonet.exe`; `Data/U04/INFOACT.BIN`, `INFOOBJ.BIN`.
- **Evidence:** `infoact.py --file Data/U04/INFOACT.BIN`: 42 records, ids 1..43 without
  16, steps and conditions as in `u04.md`; M18 and M40 have trigger 0. `infoobj.py`: 48
  entries as tabled. Talkers: `XSceneAnim_157` (`0x0041c400`) creates the talker with
  `FUN_00421360(this, character, face)` (`0x0041c57e..0x0041c590`), whose name `+0xc` is
  the character (`FUN_0041dd90(6, 0, name)`); `Talkers_Say` looks it up with vtable
  `+0x14(name, 0)` = `FUN_0041dea0` → `FUN_00416180(talker name, query, 0)`: `_stricmp`,
  else `strstr` of the upper-cased query in the upper-cased name. `U04_03` does not
  contain `*U04_03`, so `Talkers_Say` takes its no-talker branch (voice at the eye).
- **Method:** parsers; MCP decompile; capstone.
- **Confidence:** proven.
