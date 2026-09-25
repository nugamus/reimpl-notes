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

Commands are Git Bash from the repo root; `!` in front runs them from the Claude Code prompt.

### 1. Set up the run folder (once; already done on the capture machine)

```sh
bash tools/proxy/setup_run.sh            # builds C:\MonetRun
```

What it does, and why:

- **No CD, no installer.** The game reads `<exe folder>\Data\` whenever `Data\APP.BIN` is
  there and only otherwise hunts for the CD by volume label (E-0027). The script copies
  the `02_PR` binaries and `Data/`. The originals are never touched (rule 7).
- **dgVoodoo2** (32-bit `MS/x86` DLLs) runs the game's DirectDraw/Direct3D 5 on D3D11:
  windowed, `DesktopBitDepth = 16` (the game's windowed mode needs a 16-bit primary
  surface), `FPSLimit = 60` (windowed rendering is otherwise uncapped, ~200+ fps), no
  watermark.
- **Proxies** replace `x3d.dll`/`h3d.dll`; the real ones become `x3d_orig.dll`/`h3d_orig.dll`.
  Build them first (Build, above).
- **Two patches to the copied exe** (`tools/proxy/patch_exe.py`, byte-verified, E-0030/E-0031):
  skip the "set your screen to 16 bits" check, and show the game window without
  activating it.

### 2. Video codecs (Indeo 4 and 5) — installed on the capture machine 2026-09-25

The cutscene AVIs are video-only `IV50` and `IV41` (sound is separate WAVs). The two
decoders come from the game CD's own installer (`Indeo\iv5setup.exe`, Ligos), extracted with
unshield (`third_party/unshield`, built from source with `third_party/zlib`) into
`C:\MonetRun\codecs`. Windows Defender reported no threats. The install script checks their
SHA-256 hashes, copies them to `SysWOW64` and registers `vidc.iv41` / `vidc.iv50`. It needs one
UAC prompt:

```sh
powershell -Command "Start-Process powershell -Verb RunAs -Wait -ArgumentList '-ExecutionPolicy','Bypass','-File','<repo>	ools\proxy\install_indeo.ps1'"
```

`-Uninstall` removes them. Verified: all 8 AVIs in `Data/Video` decode a frame through
Video for Windows in a 32-bit process.

### 3. Launch

```sh
powershell -ExecutionPolicy Bypass -File tools/proxy/run.ps1            # MissionMonet.exe
powershell -ExecutionPolicy Bypass -File tools/proxy/run.ps1 -Exe MissionD.exe
```

The game opens as a normal 640×480 window **behind** whatever you are using. It does not
take focus, and it keeps running while you do other things. Click it when you are ready to
play; switching away does not pause it. How:

- The startup dialog (portrait, OK/Exit) is started minimised and never activated. The
  script sends it the stock 4X "Window" command and then OK. Monet's dialog hides the
  Fullscreen/Window radio buttons, but `4xvideo.dll` still honours the command (E-0029),
  which selects h3d's real windowed mode. Windowed mode has no exclusive DirectDraw
  surfaces to lose when focus changes.
- `MONET_BACKGROUND=1` makes the h3d proxy swallow focus-loss messages. Otherwise the
  game's window procedure clears its "active" flag and the main loop stalls (E-0031).
  It also makes posted key-downs visible to `GetAsyncKeyState`, so a driver can skip
  videos and voice lines. The trace header says `# background mode` when this is on.

To undo everything, delete `C:\MonetRun` and run step 1 again.

| Symptom | Fix |
|---|---|
| "needs Direct3D acceleration" (message 950) | dgVoodoo DLLs missing or the x64 ones; rerun step 1 |
| "insert CD" style box and exit | `Data\App.bin` is not next to the exe; rerun step 1 |
| "Please set your screen to 16 bits" | the exe copy is unpatched: `python tools/proxy/patch_exe.py` |
| `run.ps1` says no dialog confirmed | the game hit an error box; look at the window, then report it |
| crash ~1.5 s into U01 (EIP `0x40af518c`) | the x3d proxy; `X3D_PROXY=0 bash tools/proxy/setup_run.sh` installs the real `x3d.dll` (h3d tracing stays) |
| crash `c0000005` in ntdll (Application log) | seen once right after an agent typed a player name too early; not reproduced. Note it in `traces/INDEX.md` |

Agents can drive and watch the original without focusing it: `tools/proxy/send.ps1` posts
keys, text and clicks, and `tools/proxy/snap.ps1 out.png` captures the window even when it is
covered. The game stores player profiles in `C:\MonetRun\Save\` (`User_N/`, `Info.bin`);
delete that folder's contents for a fresh start.

Reaching U01 with posted messages only (E-0043): `run.ps1`; wait 12 s; `send.ps1 -Text Name
-Enter`; after 5 s `send.ps1 -Key 0x1B -HoldMs 70000` (Monet's tutorial polls Escape only
between lines, so hold it); the menu appears; `send.ps1 -ClickX 376 -ClickY 37` (New game);
after ~8 s `send.ps1 -Key 0x0D -HoldMs 1500` skips the prologue. Background mode redirects
the exe's `GetAsyncKeyState` so posted keys count as held (E-0043 lists what reads it):
posted Enter also cuts U01/U04 voice lines. The first U01 shot holds for 1.5 s, then the
camera moves. Never post Escape on the players
screen: it quits the game.

### 4. Play the scenarios

**One scenario per launch.** Launch (step 3), click the window when ready, do exactly the
scenario, quit through the game's menu. Quitting properly writes the final `# N calls` line; Alt+F4 or killing
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

### 5. Which engine DLLs actually load (Q-0001)

During any run, while the game is open, run this from a normal Command Prompt:

```
tasklist /m /fi "imagename eq MissionMonet.exe" > C:\MonetRun\modules.log
```

and copy `modules.log` into `traces/`. If it lists nothing useful, Sysinternals
Process Explorer (View, Lower Pane View, DLLs) shows the same thing. We want to know
which of `xd3d`/`xs3d` and `x3dmp5/6/6k` the game picked.

### 6. Optional: the developer build

Repeat scenario 02 with `MissionD.exe` from the same folder, named `02-idle-D-*.log`.
It is a superset of the shipping build (E-0012) and may log more.

### 7. Hand-off

`traces/*.log` stays on this machine (gitignored); commit only `traces/INDEX.md`. Tell
the next agent the traces are in, and it reads `traces/INDEX.md` first.

## Traces

```
# monet proxy trace: x3d.dll, 278 exports
# background mode: focus-loss messages swallowed      (h3d only, when on)
# mode: frames, boundary X3d_Render
1581 t=660369100.836 x3d.dll!X3d_Object_Animate_Spline ret=0x0041ff02 x32
1613 t=660369100.872 x3d.dll!X3d_Render ret=0x0041b18b
= x412
1614 t=660369114.795 x3d.dll!X3d_Object_Get_Global_Position ret=0x0042167f
...
# 38000 calls
```

Default is **frame mode**. A frame ends at the boundary export (`X3d_Render` for x3d,
`H3d_Show_BackBuffer` for h3d). Within a frame each (export, call site) pair is written
once, in order of its first call, with ` xN` for its count. The leading number and `t=`
belong to that first call. A frame whose list of pairs equals the previous frame's is not
written. Instead `= xN` counts how many such frames followed. The game runs per-face
collision loops every frame (`X3d_Object_Find_Next_Face` / `X3d_Line_Face_Collision`
alternating), which made per-call logging about 10 MB/s.

`MONET_TRACE_RAW=1` gives the full stream instead: one line per run of identical
consecutive calls (same export and call site), ` xN` for the run length.

`t=` is `QueryPerformanceCounter` in ms, a machine-wide clock, so the x3d and h3d files of
one run merge by time. The log is flushed at least once a second, so a killed game loses
at most the last second.

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
