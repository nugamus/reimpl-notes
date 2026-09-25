# Engine-DLL tracing proxies

`x3d.dll` and `h3d.dll` replacements that log every call and forward it to the real
implementation. This is the behavioural oracle: when static analysis and a trace
disagree, the trace wins (CLAUDE.md).

## Build

```sh
python tools/proxy/gen_proxy.py
cmake -S tools/proxy -B build/proxy -A Win32
cmake --build build/proxy --config Release
build/proxy/Release/proxy_selftest.exe      # 8 checks, must print "proxy selftest ok"
```

32-bit is mandatory — the game is x86 and the thunks are x86 inline assembly. The
generated sources under `generated/` are checked in so a build does not need the game
binaries, but regenerate them if the corpus ever changes.

Run `proxy_selftest.exe` before trusting a trace. It calls through the real proxy into a
stand-in DLL under `__cdecl`, `__stdcall` with 4 and 8 arguments, and a `double` returned
in ST(0), then checks the caller's frame and the trace contents. If the thunks ever stop
being transparent, that is where it shows.

## Capturing traces: step-by-step

**Status on the capture machine (2026-09-25):** steps 1, 3, 4 and 5 are done. `C:\MonetRun`
has the binaries, `Data/`, dgVoodoo2 (windowed, 2x, no watermark) and the proxies. The
baseline ran, and the proxy was verified to trace. Indeo (step 2) is **not** installed.
Start at step 6.

Launch with the helper instead of double-clicking (foreground; see Q-0017 for why it cannot run behind other windows yet):

```sh
powershell -ExecutionPolicy Bypass -File tools/proxy/run.ps1            # MissionMonet.exe
powershell -ExecutionPolicy Bypass -File tools/proxy/run.ps1 -Exe MissionD.exe
```

Every launch shows a startup dialog (Monet portrait, **OK / Exit**). The script focuses it
and clicks OK. Two things it works around, both seen on this machine:

- the game **minimises itself and stops its loop when it loses focus**. Don't alt-tab
  during a scenario, because the pause ends up in the trace;
- if OK is clicked while the game is in the background, dgVoodoo's `DDraw.dll` crashes
  (`c000041d`, Windows Application log) during Direct3D setup.

This is the part only a human can do: play the game with the proxies in place. Budget
about two hours the first time. Commands are Git Bash; `!` in front runs them from the
Claude Code prompt.

### 1. Make a runnable copy (no CD, no installer)

The game reads `<exe folder>\Data\` whenever `Data\APP.BIN` exists there, and only
otherwise hunts for the CD by volume label (E-0027). So a plain folder works:

```sh
mkdir -p /c/MonetRun
cp -r "Original Game Files/INSTALL/02_PR/." /c/MonetRun/
cp -r "Original Game Files/Data" /c/MonetRun/Data        # 350 MB
ls /c/MonetRun/Data/App.bin /c/MonetRun/Save             # both must exist
```

Use a path without spaces, outside the repo and never inside `Original Game Files/`
(rule 7). Everything below happens in `C:\MonetRun`.

### 2. Video codec (Indeo 5)

Cutscenes are AVI files decoded by the system's Indeo 5 codec. Run
`Original Game Files\Indeo\iv5setup.exe` as administrator. If it refuses on Windows 11,
carry on and write "no Indeo" in `traces/INDEX.md`, because videos will then fail or show black.
Do **not** run the DirectX 7 installer; dgVoodoo2 replaces it.

### 3. dgVoodoo2 (Direct3D 5 on a modern GPU)

`h3d.dll` draws through DirectDraw/Direct3D. dgVoodoo2 replaces those with a D3D11
back end, so it runs correctly on Windows 11.

```sh
cp third_party/dgVoodoo2_87_3/MS/x86/DDraw.dll \
   third_party/dgVoodoo2_87_3/MS/x86/D3DImm.dll \
   third_party/dgVoodoo2_87_3/dgVoodoo.conf \
   third_party/dgVoodoo2_87_3/dgVoodooCpl.exe /c/MonetRun/
```

Use the `MS/x86` DLLs, not `x64`. The game is 32-bit. Then run
`C:\MonetRun\dgVoodooCpl.exe`, make sure the config folder at the top is `C:\MonetRun`, and set:

- **General:** Appearance *Windowed*; Scaling mode *Stretched, keep aspect ratio*.
- **DirectX:** Videocard *dgVoodoo Virtual 3D Accelerated Card*; VRAM 256 MB;
  untick *dgVoodoo Watermark*; Resolution *Unforced*.
- Apply, close.

Windowed mode makes it easy to watch the trace files and to quit cleanly.

### 4. Baseline run, without the proxy

Double-click `C:\MonetRun\MissionMonet.exe`. Get to the main menu, start a game, walk a
few steps, quit through the game's own menu. **Do not continue until this works.** A
crash here is a setup problem, not a proxy problem:

| Symptom | Fix |
|---|---|
| "needs Direct3D acceleration" (message 950) | dgVoodoo DLLs missing or the x64 ones; redo step 3 |
| "insert CD" style box and exit | `Data\App.bin` is not next to the exe; redo step 1 |
| `MSVCRTD.DLL` missing | it ships in `02_PR`; the copy in step 1 was incomplete |
| crash at start | right-click exe, Properties, Compatibility: *Windows XP (SP3)*, retry |
| black video, game continues | Indeo missing (step 2), note it and move on |

Write down any setting you had to change. It goes in the header of `traces/INDEX.md`.

### 5. Install the proxies

```sh
cd /c/MonetRun
mv x3d.dll x3d_orig.dll
mv h3d.dll h3d_orig.dll
cp "<repo>/build/proxy/Release/x3d.dll" "<repo>/build/proxy/Release/h3d.dll" .
```

Copy **only** those two. `build/proxy/Release/x3d_orig.dll` is the self-test stand-in,
not the game's DLL; copying it would break the game. If the build folder is missing,
run the Build section above first. To undo: delete the two proxies and rename the
`_orig` files back.

Leave `MONET_TRACE` unset. Each proxy then writes `monet-trace-<dll>-<pid>.log` into
`C:\MonetRun`, one file per DLL per run.

### 6. Play the scenarios

**One scenario per launch.** Start the game, do exactly the scenario, quit through the
game's menu. Quitting properly writes the final `# N calls` line; Alt+F4 or killing
the process loses it, although the trace is still usable. Go slowly and don't wander:
a short, clean trace is worth more than a long mixed one.

| # | Name | Do exactly this |
|---|---|---|
| 01 | `boot` | Launch, let the intro play without skipping, reach the main menu, wait 10 s, quit. |
| 02 | `idle` | New game. Touch nothing for 30 s. Quit. (One frame's worth of calls, repeated.) |
| 03 | `walk` | New game. Forward 5 s, turn left 3 s, turn right 3 s, back 3 s, walk into a wall and keep pushing 3 s. Quit. |
| 04 | `hover-click` | New game. Move the mouse over a few things, click one interactive object. Quit. |
| 05 | `inventory` | Pick up an item, open the inventory, select it, use or combine it if you can. Quit. |
| 06 | `dialogue` | Talk to a character through one full conversation. Quit. |
| 07 | `transition` | Walk through a door or passage until a new area loads. Walk 3 s. Quit. |
| 08 | `save-load` | Play briefly, save to a slot with a name, quit to the menu, load it, walk 3 s. Quit. |
| 09 | `options` | Open the options screen, change volume, go back to the game. Quit. |
| 10 | `cutscene` | Trigger any video other than the intro (skip this one if you can't reach one). |
| 11 | `skip` | Launch and skip the intro at every chance (Esc, click). Quit at the menu. |
| 12 | `long` | Optional: play normally for 10–15 minutes, noting what you did with rough times. |

For scenarios 04 onward it helps to keep one save in the right spot and load it
first. Say so in the notes, because loading is part of that trace.

After each run, from the repo root:

```sh
bash tools/proxy/collect.sh 03-walk
```

It moves the newest x3d/h3d traces to `traces/03-walk-x3d.log` / `-h3d.log`, copies the
game's `Save/DbgInfo.txt` as `-dbginfo.log`, and warns if a trace has no end marker.

Then add a row to `traces/INDEX.md` saying what you actually did, including any
deviations. The notes matter as much as the logs.

### 7. Which engine DLLs actually load (Q-0001)

During any run, while the game is open, run this from a normal Command Prompt:

```
tasklist /m /fi "imagename eq MissionMonet.exe" > C:\MonetRun\modules.log
```

and copy `modules.log` into `traces/`. If it lists nothing useful, Sysinternals
Process Explorer (View, Lower Pane View, DLLs) shows the same thing. We want to know
which of `xd3d`/`xs3d` and `x3dmp5/6/6k` the game picked.

### 8. Optional: the developer build

Repeat scenario 02 with `MissionD.exe` from the same folder, named `02-idle-D-*.log`.
It is a superset of the shipping build (E-0012) and may log more.

### 9. Hand-off

`traces/*.log` stays on this machine (gitignored); commit only `traces/INDEX.md`. Tell
the next agent the traces are in, and it reads `traces/INDEX.md` first.

## Traces

One line per run of calls:

```
# monet proxy trace: x3d.dll, 278 exports
1 t=658601400.285 x3d.dll!X3d_Init_Mathlib ret=0x004182cb
5 t=658601412.901 x3d.dll!X3d_Object_Animate_Spline ret=0x0041c2a0 x33
# 38 calls
```

The first number is the sequence number of the first call in the run. `t=` is
`QueryPerformanceCounter` in ms, a machine-wide clock, so the x3d and h3d files of one
run merge by time. ` xN` means N consecutive calls to the same export from the same call
site. Without it the game's uncapped render loop wrote about 130 MB a minute. The log is
flushed at least once a second, so a killed game loses at most the last second.

`ret` is the return address at the call site, which identifies the calling function and
joins straight back to `notes/function-map.csv`.

Set `MONET_TRACE` to choose the output path; it is read in `DllMain`, so it must be set
before the game starts. Without it the proxy writes `monet-trace-<dll>-<pid>.log` into
the working directory. Both proxies write their own file — point `MONET_TRACE` at a path
only when loading one of them, or they will overwrite each other.

Traces belong in `traces/`. `traces/*.log` is gitignored; a trace a test depends on gets
force-added as `traces/golden-*.log`.

## Limits

- Arguments and return values are not captured, only the call sequence and the call site.
  Recovering signatures needs per-export knowledge that does not exist yet; the sequence
  is what Phase 4 replay compares against.
- An export the real DLL does not provide is fatal and loud (message box, `ExitProcess`)
  rather than a wild jump through a null pointer. It should never fire — the export lists
  are generated from the real DLLs — but it would catch a mismatched drop-in.
- The other engine DLLs (`x3dsdk`, `xd3d`, `xs3d`, `x3dmp5/6/6k`, `4xvideo`, `AviPlay`,
  `flc`) are not proxied. See Q-0001: if any turns out to be loaded at runtime, add it to
  `TARGETS` in `gen_proxy.py` — the generator is not specific to `x3d`.
