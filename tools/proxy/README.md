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

## Deploy

**Never modify the original binaries or the CD (CLAUDE.md rule 7).** Work on a copy of an
installed game directory.

1. Install the game, then copy the whole install directory somewhere writable.
2. In the copy, rename `x3d.dll` to `x3d_orig.dll`, and `h3d.dll` to `h3d_orig.dll`.
3. Copy `build/proxy/Release/x3d.dll` and `h3d.dll` into the copy.
4. Run the game from that directory.

The proxy resolves `x3d_orig.dll` from its own directory, not by search order — it shares
a name with the DLL it replaces, so a plain `LoadLibrary` would risk finding itself.

## Traces

One line per call:

```
# monet proxy trace: x3d.dll, 278 exports
1 x3d.dll!X3d_Init ret=0x004012a7
2 x3d.dll!X3d_Scene_Create ret=0x00415b30
# 2 calls
```

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
