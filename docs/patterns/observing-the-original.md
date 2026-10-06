# Observing the running original

For one precise question the code can't settle (rule 7). Run the original from a patched
run folder (`C:\<Game>Run`), never the disc folder, and kill only its process.

| Question | Tool |
|---|---|
| Which functions run, with which arguments and results | `uv run tools/trace/trace.py --spawn <exe> --hook <module>!0x<rva>=<label>` (Frida, to a file) |
| Which Win32 calls (files opened, registry, timers, sound) | `third_party/drmemory/DrMemory-Windows-2.6.20434/bin/drltrace.exe -only_from_app -logdir <dir> -- <exe>` (bin64 for 64-bit) logs every library call the game itself makes; without `-only_from_app` even a tiny program logs tens of thousands of lines |
| Which DirectDraw / Direct3D 7..9 calls it makes (modes, surfaces, blits) | `third_party/apitrace32/apitrace-14.0-win32/bin/apitrace.exe trace -m -a d3d7 -o 'C:\tmp\x.trace' 'C:\<Game>Run\<game>.exe'` (absolute Windows paths; close the game normally, not with /F, or the trace stays empty), then `apitrace dump <trace>`. Behind dgVoodoo the calls are logged but frames are not (it builds its Direct3D 11 device out of apitrace's reach, and a game may refuse its fullscreen mode under the trace): take frames with snap.ps1 instead |
| What the screen shows at a moment | `engines/x3d/tools/proxy/snap.ps1 out.png <process>` |
| A value at an address, stepping | the Ghidra MCP `debugger_*` tools (dbgeng): attach, break, read |
| What a scene looks like without running anything | `uv run tools/longplay.py <video url> <timestamps>`: frames from a recorded playthrough |

Old games on new Windows: dgVoodoo2 (`third_party/dgVoodoo2_87_3`) wraps DirectDraw and
Direct3D up to 7 so they run windowed (`FullScreenMode = false` in the folder's
`dgVoodoo.conf`, as `C:\GrumpaNoCD`); Monet's run folder uses it
(`engines/x3d/tools/proxy/setup_run.sh`). Proxy DLLs placed next to the EXE (x3d's
`tools/proxy`) can log or change calls into a specific library.

Write what you learned to EVIDENCE.md and the trace's line to `traces/INDEX.md`; the
captures themselves stay local.
