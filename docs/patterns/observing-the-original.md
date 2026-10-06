# Observing the running original

For one precise question the code can't settle (rule 7). Run the original from a patched
run folder (`C:\<Game>Run`), never the disc folder, and kill only its process.

| Question | Tool |
|---|---|
| Which functions run, with which arguments and results | `uv run tools/trace/trace.py --spawn <exe> --hook <module>!0x<rva>=<label>` (Frida, to a file) |
| Which Win32 calls (files opened, registry, timers, sound) | `third_party/drmemory/.../bin/drltrace.exe -logdir <dir> -- <exe>` logs every library call with arguments |
| What each frame draws (DirectDraw / Direct3D 7..9) | `third_party/apitrace32/.../bin/apitrace.exe trace -a <api> <exe>`, then `apitrace dump-images` or `qapitrace` to step frames and calls |
| What the screen shows at a moment | `engines/x3d/tools/proxy/snap.ps1 out.png <process>` |
| A value at an address, stepping | the Ghidra MCP `debugger_*` tools (dbgeng): attach, break, read |
| What a scene looks like without running anything | `uv run tools/longplay.py <video url> <timestamps>`: frames from a recorded playthrough |

Old games on new Windows: dgVoodoo2 (`third_party/dgVoodoo2_87_3`) wraps DirectDraw and
Direct3D up to 7 so they run windowed; Monet's run folder uses it
(`engines/x3d/tools/proxy/setup_run.sh`). Proxy DLLs placed next to the EXE (x3d's
`tools/proxy`) can log or change calls into a specific library.

Write what you learned to EVIDENCE.md and the trace's line to `traces/INDEX.md`; the
captures themselves stay local.
