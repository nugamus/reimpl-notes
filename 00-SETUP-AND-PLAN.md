# Monet: The Mystery of the Orangery — reimplementation plan

A ScummVM-style reimplementation project, set up so that a Claude Code agent does the
bulk of the mechanical work and you do the judgement calls.

---

## 0. What the binaries actually are

Findings from `MissionMonet.exe` and `MissionD.exe`, verified from the PE headers:

| | MissionMonet.exe | MissionD.exe |
|---|---|---|
| Size | 339,968 B | 618,543 B |
| Built | 2000-10-02 16:28 UTC | 2000-10-09 15:16 UTC |
| Linker | MSVC 6.0 | MSVC 6.0 |
| CRT | **MSVCRTD** (debug) | **MSVCRTD** (debug) |
| Sections | 4 | 6 |
| Extra imports | — | DINPUT.dll |
| PDB path | — | `D:\MissionD\Debug\MissionD.pdb` |
| Packed? | No (entropy 4.4–6.2) | No |

Version resources on both: `CompanyName = Index+`, `ProductName = Mission Monet`,
`InternalName = MissionD`, `Copyright © 1999`.

**This is not Virtools/CK2.** The engine is **X3D by 4X Technologies S.A.**, with the
game linking `x3d.dll` (87 exports), `h3d.dll` (Direct3D wrapper, 7 exports),
`4xvideo.dll` and `AVIPLAY.dll`. Your project notes said Virtools/CK2 — that's worth
reconciling before the agent starts, because the whole format-analysis plan hinges on
it. (Possible the CK2 work belonged to *Road to India*, which genuinely is Virtools.)

### Why this is an unusually favourable target

1. **Both shipped EXEs are debug builds.** MSVCRTD means `assert()` is live, so the
   binary contains the original source filename for every assert site, e.g.
   `D:\MissionD\Source\XScene.cpp`, `D:\MissionD\Source\FrameWork Sources\LSound.cpp`.
   Cross-referencing those strings lets you attribute most functions to their original
   source file automatically. Debug builds are also unoptimised — no inlining, no
   register-allocation soup, textbook prologues — so Ghidra's decompiler output will be
   close to readable C++.
2. **Recovered source-tree layout** (from assert strings):
   - `Source/FrameWork Sources/` — `LArray`, `LBitmapReader`, `LClassCreator`,
     `LFrameReader`, `LKeyState`, `LMouseState`, `LMultipleMediaObject`,
     `LOptionScreen`, `LSharedMediaObject`, `LSimpleMediaObject`, `LSound`,
     `LSoundManager`, `LUser`, `MessageToUser.h`
   - `Source/` — `XAction`, `XAnimation`, `XCursor`, `XGameList`, `XObject3D`,
     `XScene`, `XSceneAnim`, `file.cpp`, `load.cpp`, `U00`, `U03`, `U04`, `U99`
   - `Source/Sound/` — `XSndStream`, `XTimer`, `XWaveFile`
   - `Source/Tools/` — `CaptureWnd` (dev capture tool, MissionD.exe only)
   So `L*` = reusable framework layer, `X*` = game layer, `U##` = per-chapter/unit
   scene logic. That's your module map, for free.
3. **The engine boundary is a named C API.** All 87 `X3d_*` entry points are exported
   by name (see `x3d-api-surface.md`). The game↔engine contract is already documented
   by the linker. This makes the *proxy-DLL tracing* technique below extremely powerful.
4. **MissionD.exe is a developer build** — bigger, has DirectInput, `U99.cpp`,
   `XAction.cpp`, and a screen-capture tool. Diff it against MissionMonet.exe; it may
   contain debug menus, level jumps, or logging that shipped disabled.

### Data layout (from format strings)

Root is `<drive>:/Data/`. Observed:

```
APP.BIN                  SCENE.BIN
U00.X3D  U01.X3D  ...    (scene files, "U%s.x3d")
<scene>/Info.bin         <scene>/InfoPara.bin
Anim/<unit>/*.A3D        (animations: parle.A3D, ouvre01.A3D, reveil.A3D, ...)
Anim/<unit>/*.O3D        (objects/meshes: ERNST2.O3D, U03_02.O3D)
Sound/<name>.WAV         Sound/<name>.bin
2dbit/Intro1.bmp
```

Loader entry points confirm five sub-format families:
`X3d_Load_Sdk_o3d` (objects), `_a3d` (animation), `_s3d`, `_l3d`, `_c3d` (scene, lights,
cameras). No public spec exists for any of these — this is original RE work.

---

## 1. Software YOU must install (the agent can't)

Install these on the Windows box (or Linux host — notes where it matters) before
starting the agent.

### Required

| Tool | Why | Notes |
|---|---|---|
| **JDK 21+** (Temurin) | Ghidra runtime | Set `JAVA_HOME` |
| **Ghidra 12.x** | Decompiler | Run it once, accept the EULA, create a project — the MCP servers attach to an existing project |
| **Maven** | Builds the Ghidra MCP extension | `mvn -v` must work |
| **Python 3.11+** and **uv** | MCP bridge | `uv` from astral.sh |
| **Node.js 20+** | Claude Code | |
| **Claude Code** | The agent | `npm i -g @anthropic-ai/claude-code` |
| **Git** | Version control + agent checkpoints | |
| **The game, installed, with data** | Corpus to validate against | `E:\Data` per your notes |
| **`x3d.dll`, `h3d.dll`, `4xvideo.dll`, `AVIPLAY.dll`** | The actual engine — the EXEs are thin clients | Copy them next to the EXEs for Ghidra import |

### Strongly recommended

| Tool | Why |
|---|---|
| **Visual Studio Build Tools 2022** (or **MinGW-w64 i686**) | You need a **32-bit x86** compiler to build the proxy/logging DLL described in §3. This is the single highest-value technique in the plan. |
| **dgVoodoo2** | D3D5-era wrapper → D3D11/12; makes the original runnable for reference capture |
| **x32dbg** (x64dbg's 32-bit build) | Live debugging, breakpoints on the X3D calls |
| **PE-bear** or **CFF Explorer** | Fast PE inspection without Ghidra |
| **ImHex** or **010 Editor** | Hex editing with binary templates while formats are being worked out |
| **Kaitai Struct compiler** | Turns format specs into parsers in many languages at once — ideal AI output target |
| **Blender** | Eyeball validation of extracted meshes/animations |
| **ffmpeg** | Inspect the AVI/`4xvideo` streams |

### Optional

- **RenderDoc** — you evaluated this already; with dgVoodoo2 in front it gives you
  ground-truth draw calls per frame.
- **Wine** (Linux) — surprisingly good for a D3D5-era title, and makes automated
  headless runs of the original scriptable.
- **ScummVM source tree** — only if you commit to that target (see §5).

---

## 2. AI tooling

### Ghidra MCP (pick one)

- **`bethington/ghidra-mcp`** — the fullest option as of mid-2026: ~200 MCP tools, a GUI
  plugin *and* a headless server, batch operations, lazy tool loading, Docker
  deployment. Requires Ghidra 12.x + JDK 21 + Maven + Python + uv. Its setup script
  builds and installs the extension and writes a `.mcp.json` that Claude Code picks up
  automatically. **Use `--no-lazy` / load all tool groups** — Claude Code needs the full
  tool list up front.
- **`LaurieWired/GhidraMCP`** — the original, simpler, fewer tools, easiest to get
  running. Good fallback if the above misbehaves.

Both work the same way: Ghidra holds the project, the MCP bridge exposes
decompile/rename/xref/comment/struct tools, and the agent drives it. **Prefer the
headless mode** for long autonomous runs — GUI-attached mode dies with the GUI and
serialises everything through one "current program".

### Also worth wiring up

- **PyGhidra** (bundled since Ghidra 11.3) — for anything the MCP tools don't cover,
  the agent can write a Python Ghidra script and run it headless. Batch jobs (like the
  assert-string auto-namer in §3) belong here, not in MCP round-trips.
- **Plain bash + `pefile` + `capstone`** — Claude Code can already do a lot without
  Ghidra. Don't route everything through MCP.
- A **repo-local `CLAUDE.md`** (provided alongside this doc) — the agent reads it on
  every session; it's where the invariants live.

### The token-economy problem

Decompiler output is enormous. An unmanaged agent will burn its context dumping
functions it will never use. Enforce in `CLAUDE.md`:
- fetch **one function at a time**, never `list_functions` + decompile-everything;
- immediately write findings to `notes/<module>.md` and drop the raw listing;
- run **batch** work (mass renaming, string xrefs) as a headless PyGhidra script, so
  results land on disk instead of in context;
- use subagents for anything exploratory so the raw output stays out of the main thread.

---

## 3. The two techniques that make this tractable

### 3.1 Assert-string auto-naming (do this first, it's cheap)

Every `assert()` in a debug build compiles to a call with the source filename and line
number as arguments. Write one PyGhidra script that:

1. Finds all strings matching `D:\MissionD\Source\...\*.cpp`.
2. For each, walks xrefs to the referencing functions.
3. Tags each function with the source file (namespace or a `SRC:` comment), and records
   the line number argument.
4. Emits `notes/function-map.csv`: address, source file, line, current name.

Result: several hundred functions instantly attributed to `XScene.cpp`, `LSound.cpp`,
`U04.cpp`, etc., plus a line-number ordering that reconstructs the *original layout of
each source file*. Functions sharing a file are almost always one class. This is the
skeleton everything else hangs off — and it is pure automation, no LLM judgement needed.

### 3.2 The x3d.dll proxy — behavioural ground truth

Because the engine boundary is 87 named exports, you can build a **shim `x3d.dll`** that
exports the same names, forwards each to the real DLL (renamed `x3d_real.dll`), and logs
every call with decoded arguments. Same for `h3d.dll` (7 exports).

Run the original game with the shim in place and you get a complete, timestamped trace
of everything the game asks the engine to do: every scene load, object lookup, camera
polar coordinate, animation transition, pick test, render state change.

That trace is worth more than any amount of static analysis, because:
- it tells you **which** of the 87 calls actually matter (probably ~30);
- it gives you a **golden log** for differential testing — your reimplementation replays
  the same input and must produce the same call sequence;
- it resolves argument semantics empirically (what units are the polar coordinates? what
  does `X3d_Object_Set_Camera_Type` take?) without decompiling the DLL at all.

Have the agent generate the shim: it's 87 mechanical `__declspec(dllexport)` stubs plus a
`.def` file, generated from `x3d-api-surface.md`. Build 32-bit. This is a perfect
agent task — tedious, deterministic, verifiable.

---

## 4. Phases

Each phase ends in a git tag and a written artefact. Don't let the agent start phase N+1
until phase N's validator passes.

**Phase 0 — Ingest.** Import all four DLLs + both EXEs into one Ghidra project. Run
auto-analysis. Run the assert-namer. Produce `notes/function-map.csv`,
`notes/module-map.md`. Inventory `E:\Data`: file counts, extensions, size histograms,
magic bytes per extension into `notes/corpus-inventory.md`.

**Phase 1 — Proxy tracing.** Build and validate the `x3d.dll`/`h3d.dll` shims. Capture
traces of: intro, one scene load, one dialogue, one puzzle, one scene transition. Store
under `traces/`. Write `notes/x3d-api-semantics.md` — one section per export, arguments
observed, call frequency, call-site source file.

**Phase 2 — File formats.** For each of O3D, A3D, X3D, S3D/L3D/C3D, `APP.BIN`,
`SCENE.BIN`, `Info.bin`, `InfoPara.bin`, `Sound/*.bin`: decompile the corresponding
`X3d_Load_Sdk_*` loader, derive the struct layout, write a **Kaitai Struct `.ksy` spec**
plus a Python validator. **Hard rule: a format is not "done" until the validator parses
100% of the files of that type in the corpus with zero leftover bytes and zero
out-of-range indices.** Meshes get exported to glTF and eyeballed in Blender (you already
have an inspector for this).

**Phase 3 — Game logic.** Decompile the `X*` and `U##` modules into documented
pseudocode: scene graph handling, the action/verb system (`XAction`), cursor and hotspot
logic (`XCursor`, `X3d_Scene_Pick_Object`), animation sequencing (`XSceneAnim`), save
format (`load.cpp`, `file.cpp`), the option screen, sound manager. Output:
`docs/engine-spec/*.md` — prose + pseudocode, no verbatim decompiler dumps.

**Phase 4 — Reimplementation.** Build from the specs, not from the decompiler output
(see §6). Order: file loaders → scene graph + camera → static rendering → picking →
animation → audio → game state machine → save/load → video playback.

**Phase 5 — Validation.** Replay the golden traces. Screenshot-compare against the
original under dgVoodoo2 at 640×480. Playthrough parity: same items, same flags, same
scene transitions.

---

## 5. Choosing a target — decide this before Phase 4

Three real options, and the agent should not pick for you:

- **ScummVM engine plugin (C++).** Your stated inspiration. You get their audio, input,
  save, scaler, and platform layers for free, plus a real user base. Costs: C++98-ish
  house style, their review process, and their requirement that the engine be clearly
  documented and not derived from copied code. This is the highest-effort, highest-payoff
  path, and their PhoenixVR work (Dracula Resurrection, The Last Sanctuary,
  Necronomicon) is a close structural precedent — same era, same "3D adventure with a
  proprietary in-house engine" shape.
- **Standalone native engine (Rust or modern C++ + SDL3 + wgpu/OpenGL).** Full freedom,
  easiest for an AI agent to write and test, no upstream politics. Best if the goal is
  "runs great on modern hardware with enhancements".
- **Web/TypeScript + WebGL/Three.js.** You already have a Three.js inspector and prior
  web-port work, so the on-ramp is short and the demo value is high. Weakest for audio
  timing and for anything ScummVM-shaped.

A sane hedge: write the **file loaders and the game-state machine as a portable core**
(Rust with C ABI, or plain C++ with no platform deps) and keep the renderer/platform
layer thin. Then the ScummVM-vs-standalone-vs-web decision is a swap of the outer layer,
not a rewrite.

---

## 6. Guardrails for the agent

Put these in `CLAUDE.md` and enforce them:

1. **No claim without evidence.** Every documented struct field, function name, or
   behaviour cites either a Ghidra address, an assert source file, or a trace line. The
   agent writes `EVIDENCE.md` entries, not assertions.
2. **No format spec without a passing validator over the full corpus.** LLMs are very
   good at producing plausible struct layouts that are wrong in the third field.
   Exhaustive parse + zero trailing bytes is the test that catches it.
3. **Specs, then code.** The reimplementation is written from `docs/engine-spec/`, not by
   transcribing decompiler output. This matters for correctness (decompiler artefacts
   propagate) and for the licence story if you ever upstream to ScummVM.
4. **One function at a time; findings to disk immediately.** See §2.
5. **Never modify anything under the game data directory.** Mount it read-only if you can.
6. **Commit per unit of work, tag per phase.** You want to be able to throw away a bad
   agent run cheaply.
7. **Escalate, don't guess.** If a format field's meaning is ambiguous after decompiling
   the loader *and* checking the corpus *and* checking the trace, the agent writes an
   open question into `docs/OPEN-QUESTIONS.md` and moves on. Silent guessing is what
   turns a 3-week project into a 6-month debugging project.

---

## 7. Legal, briefly

Reverse-engineering for interoperability and preservation is well-trodden ground and is
exactly what ScummVM does. Two practical rules: **the reimplementation ships no game
assets** (users supply their own copy), and **no verbatim decompiler output** goes into
the source tree. Keep the RE notes in a separate directory from the engine source if you
ever plan to upstream; some projects want that separation.

---

## 8. Suggested repo layout

```
monet-re/
├── CLAUDE.md                  # agent invariants (provided)
├── docs/
│   ├── engine-spec/           # phase 3 output — the actual deliverable
│   ├── formats/               # .ksy specs + prose
│   ├── OPEN-QUESTIONS.md
│   └── EVIDENCE.md
├── notes/                     # raw RE notes, function-map.csv, module-map.md
├── tools/
│   ├── ghidra_scripts/        # PyGhidra batch jobs
│   ├── proxy/                 # x3d.dll / h3d.dll logging shims
│   ├── parsers/               # python validators for each format
│   └── export/                # glTF exporters
├── traces/                    # golden logs from the proxy DLL
├── engine/                    # the reimplementation (phase 4+)
└── tests/                     # corpus validators + trace replay
```
