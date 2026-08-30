# Phase 0 summary

What the assert strings in the two MSVC 6 debug builds prove about the original source
layout, and what the developer build carries that the shipping build does not. No
function body was decompiled to produce any of this.

Backing data: `function-map.csv`, `function-map-multi.csv`, `module-map.md`,
`import-map.md`, and the raw per-program scans in `_assert_scan/`. Regenerate with
`tools/ghidra_scripts/assert_namer.py` and `tools/ghidra_scripts/import_map.py`.

## Method, and what it does not cover

`assert_namer.py` walks every defined string that looks like an MSVC `__FILE__` path,
follows each reference, and reads the line number from the `PUSH` immediately preceding
the `PUSH` of the path pointer. That shape was verified against real sites before the
script was written — e.g. `MissionMonet.exe` `0x0041a9c6`:

    PUSH 0x46          ; line 70
    PUSH 0x441788      ; -> "D:\MissionD\Source\XScene.cpp"
    PUSH 0x3ed         ; message id
    MOV  ECX,EAX
    CALL 0x0042a200    ; MessageToUser

Every one of the 166 assert sites found across the two EXEs matched it. None fell back to
an unknown line number, and no function referenced more than one source file, so
`function-map-multi.csv` is empty — there is no evidence of inlined or shared assert
helpers.

**Coverage is low and that is inherent to the method.** Only functions that contain an
assert get attributed:

| Program | Functions | Attributed | Coverage | Source files | Attributed bytes |
|---|---:|---:|---:|---:|---:|
| `MissionMonet.exe` | 1,476 | 44 | 3.0% | 20 | 20,001 |
| `MissionD.exe` | 3,055 | 75 | 2.5% | 31 | 41,131 |

A source file's absence from this map is not evidence that its code is absent from the
binary — only that no surviving assert names it. `XAction.cpp` appears in `MissionD.exe`
and not in `MissionMonet.exe`, but the shipping game plainly runs actions; the assert
simply did not survive. Treat every "only in D" claim below accordingly, and prefer the
import and string diffs, which are positive evidence.

## Functions attributed per source file

Full per-file listings with line numbers and sizes are in `module-map.md`. Top of each
binary by attributed code size:

| `MissionMonet.exe` | Fns | Bytes | | `MissionD.exe` | Fns | Bytes |
|---|---:|---:|---|---|---:|---:|
| `LSound.cpp` | 9 | 3,697 | | `LSound.cpp` | 11 | 5,661 |
| `MessageToUser.h` | 5 | 3,073 | | `MessageToUser.h` | 6 | 4,499 |
| `LSoundManager.cpp` | 4 | 1,492 | | `XScene.cpp` | 6 | 3,084 |
| `XScene.cpp` | 3 | 1,396 | | `LSoundManager.cpp` | 5 | 2,533 |
| `LMultipleMediaObject.cpp` | 2 | 1,308 | | `LBitmapReader.cpp` | 2 | 2,306 |
| `LOptionScreen.cpp` | 3 | 1,250 | | `XSndStream.cpp` | 6 | 2,214 |
| `U03.cpp` | 1 | 1,017 | | `LOptionScreen.cpp` | 4 | 2,012 |
| `load.cpp` | 2 | 999 | | `LMultipleMediaObject.cpp` | 2 | 1,546 |
| `U04.cpp` | 1 | 882 | | `load.cpp` | 2 | 1,372 |
| `LSharedMediaObject.cpp` | 2 | 870 | | `U04.cpp` | 1 | 1,222 |

Line spans are informative beyond the sizes: `LSound.cpp` asserts run from line 72 to
696 and `LOptionScreen.cpp` from 566 to 1144, so those files are at least ~700 and
~1150 lines. `XScene.cpp` spans 70 to 651.

`MessageToUser.h` ranks second in both builds, which is an artefact — it is the assert
macro's own header, so a function that inlines the macro's failure path gets attributed
to it rather than to the caller's `.cpp`. Those entries are the least useful in the map.

## Which source files are largest — and the caveat that matters

**This ranking measures asserted code, not total code.** `LSound.cpp` tops both builds
because sound code checks its preconditions constantly, not necessarily because it is the
biggest file. 20 KB of `MissionMonet.exe`'s 340 KB image is attributed; the other 94% is
unranked. Do not use this table alone to schedule Phase 3.

What it does support: the framework layer (`L*`) dominates the attributed set —
`LSound`, `LSoundManager`, `LBitmapReader`, `LOptionScreen` and the three
`L*MediaObject` files together account for 8,986 bytes in the shipping build against
4,124 for the game layer (`X*` plus `U##`). Audio and media-object lifetime management
are where the original authors spent their assertions, which is a reasonable proxy for
where the invariants live.

## What `MissionD.exe` has that `MissionMonet.exe` does not

Three independent diffs agree: the developer build is a superset. Zero source files, zero
imports and zero `x3d.dll` exports are unique to the shipping build.

### Source files (assert evidence, weak — see the coverage caveat)

22 source paths appear in both. Nine appear only in `MissionD.exe`:

| Source file | Signal |
|---|---|
| `Source\Tools\CaptureWnd.cpp` | the screen-capture tool |
| `Source\U99.cpp` | a unit/chapter scene numbered far past the shipped `U00`-`U04` |
| `FrameWork Sources\LKeyState.cpp` | keyboard state |
| `FrameWork Sources\LMouseState.cpp` | mouse state |
| `Source\Sound\XSndStream.cpp` | streaming audio |
| `Source\Sound\XTimer.cpp`, `XWaveFile.cpp` | the same `Sound\` subdirectory |
| `FrameWork Sources\LArray.cpp` | container |
| `Source\XAction.cpp` | almost certainly in both; the assert did not survive |

The `Source\Sound\` subdirectory is a structural finding: `XSndStream`, `XTimer` and
`XWaveFile` sit one level deeper than every other `X*` file, so the original tree had at
least `Source\`, `Source\FrameWork Sources\`, `Source\Sound\` and `Source\Tools\`.

### Imports (positive evidence, strong)

`MissionD.exe` imports 67 symbols the shipping build does not, including three DLLs the
shipping build does not link at all:

- **`dinput.dll`** — `DirectInputCreateA`. Matches `LKeyState.cpp` (`0x00458911`, line 41,
  758 bytes) and `LMouseState.cpp` (`0x0045bde8`, line 52, 681 bytes).
- **`comdlg32.dll`** — `GetOpenFileNameA`, `GetSaveFileNameA`. File pickers.
- **`ole32.dll`**.
- **`gdi32.dll`** — `BitBlt`, `CreateCompatibleBitmap`, `GetDIBits`, alongside
  `SetCapture` / `ReleaseCapture` / `ClientToScreen`. The screen grabber, matching
  `CaptureWnd.cpp` (`0x00428d11` line 132, `0x00428f03` line 183).
- **`kernel32.dll`** — `GetLogicalDriveStringsA`, `GetDriveTypeA`, `FindResourceA`,
  `LoadResource`, `WriteFile`, `_lopen`/`_lread`/`_lwrite`/`_lclose`,
  `GetPrivateProfileStringA`.
- **`msvcrtd.dll`** — `_CrtSetDbgFlag`, `_CrtDbgReport`, `_strdate`, `_strtime`.

### Strings

`MissionD.exe` has 1,002 printable strings the shipping build lacks; `MissionMonet.exe`
has 363 the developer build lacks. The developer-only set includes `Begin capture`,
`Stop capture`, `D:/Capture/`, `d:\Capture\image`, `ALa capture est limit`,
`Error to use GetLogicalDriveStrings`, `*********SET_CRT_DEBUG_FIELD*` and
`D:\MissionD\Debug\MissionD.pdb` — confirming the build configuration was literally named
`Debug`.

### The three specific questions

- **Debug menus:** no evidence found. No menu-resource or command-name strings appear in
  the developer-only set. What exists is a capture dialog (`EndDialog`,
  `SetCapture`/`ReleaseCapture`, a `comdlg32` save dialog), not a debug menu.
- **Scene-jump commands:** no direct evidence. No developer-only string names a scene or a
  jump command, and the `U##` data-path strings are near-identical between the builds
  (252 vs 250). The candidate is `U99.cpp`, whose single attributed function `0x00464ead`
  (line 248, 793 bytes) calls `X3d_Load_Sdk_o3d`, `X3d_Camera_Get_Position`,
  `X3d_Scene_All_Light_Include_Object`, `X3d_Object_Release` and `X3d_Animation_Release`
  — load a model, place a camera, light it, with no gameplay imports. Consistent with a
  test or viewer scene, but "consistent with" is not proof. Logged as **Q-0008**.
- **Logging that shipped disabled:** the `MessageToUser` path did **not** ship disabled. It
  is present and referenced in `MissionMonet.exe` (5 attributed functions, 3,073 bytes,
  sink at `0x0042a200`), and all 22 source-path strings in the shipping build have at
  least one reference — none is orphaned. What is developer-only is the *CRT* debug layer:
  `_CrtSetDbgFlag` and `_CrtDbgReport` are imported by `MissionD.exe` alone, even though
  both builds link `MSVCRTD.DLL`. So the game's own assert reporting shipped **enabled**;
  CRT heap-debug reporting was compiled out of the shipping build.

## Which `x3d.dll` exports are called from which source files

Full table in `import-map.md`. Counts:

| Library | `MissionMonet.exe` | `MissionD.exe` | Union |
|---|---:|---:|---:|
| `x3d.dll` | 70 | 80 | 80 |
| `h3d.dll` | 7 | 7 | 7 |
| `AviPlay.dll` | 5 | 5 | 5 |
| `4xvideo.dll` | 1 | 1 | 1 |

Every one of those imports has an identified calling function except one `h3d.dll` import
in `MissionD.exe`. Source-file attribution reaches far fewer: 21 of the shipping build's
70 `x3d.dll` exports and 22 of the developer build's 80 — a direct consequence of the 3%
function coverage, not of anything about the imports themselves.

The 80-export union sharpens E-0003: the "87 imported symbols" figure is `MissionD.exe`'s
80 `x3d.dll` imports plus its 7 `h3d.dll` imports. `MissionMonet.exe` imports only 70
`x3d.dll` symbols. The Phase 1 proxy still needs all **278** exports.

Attributed exports per source file, shipping build:

| Source file | `x3d.dll` exports reached |
|---|---:|
| `MessageToUser.h` | 13 |
| `XObject3D.cpp` | 5 |
| `U04.cpp` | 4 |
| `U03.cpp` | 4 |
| `load.cpp` | 3 |
| `XScene.cpp` | 3 |
| `XSceneAnim.cpp` | 1 |
| `XAnimation.cpp` | 1 |

The ten `x3d.dll` exports imported by `MissionD.exe` alone are all lighting, camera and
animation-enumeration calls: `X3d_Scene_Create_Light`, `X3d_Scene_Create_Spot_Light`,
`X3d_Light_Set_Color`, `X3d_Light_Set_Multiplier`, `X3d_Light_Set_Name`,
`X3d_Light_Include_Scene_All_Object`, `X3d_Camera_Release`, `X3d_Camera_Set_Target`,
`X3d_Scene_Find_First_Animation`, `X3d_Scene_Find_Next_Animation`. The shipping build
loads scenes with their lights already authored; the developer build can create and
enumerate them at runtime. That reinforces the `U99.cpp`-as-test-scene reading without
settling it.

## The engine DLLs have no assert strings at all

`x3d.dll`, `h3d.dll` and `x3dsdk.dll` were scanned with the same script and yielded zero
source-path strings and zero attributed functions. They are release builds from a
different vendor (4X Technologies), and this technique gives nothing there. Everything
learned about those 1,077 functions will have to come from the export names, the Phase 1
proxy traces, and decompilation.
