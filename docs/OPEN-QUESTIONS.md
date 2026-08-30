# Open questions

Things we could not determine after checking the loader, the corpus, and the traces.
Per CLAUDE.md rule 5: an unresolved field goes here and gets marked as an opaque blob in
the format spec. It does not get a guessed meaning.

Append only. When a question is answered, keep the entry, mark it `RESOLVED`, and link the
`docs/EVIDENCE.md` entry that resolved it.

## Entry format

```
### Q-0001 — <one-line question>
- **Context:** where it came from (format + offset, function address, trace line).
- **What we checked:** the three required avenues — loader decompilation, corpus survey,
  proxy traces — and what each returned.
- **Observed range:** for a data field, the set of values seen across the corpus.
- **Blocks:** what work is stalled or degraded by not knowing this.
- **Status:** open | RESOLVED (see E-nnnn)
```

## Questions

### Q-0001 — What are `x3dmp5.dll`, `x3dmp6.dll`, `x3dmp6k.dll`, `xd3d.dll`, `xs3d.dll` for?
- **Context:** present in `Original Game Files/INSTALL/02_PR/` but not named in the project
  ground truth, which lists only `x3d.dll`, `h3d.dll`, `4xvideo.dll`, `AVIPLAY.dll`.
- **What we checked:** nothing yet — noted at bootstrap, before any analysis.
- **Blocks:** the Phase 1 proxy plan assumes `x3d.dll` and `h3d.dll` are the whole engine
  surface. If the game loads any of these at runtime, the proxy misses those calls.
- **Status:** open

### Q-0002 — Which data root does the shipping build actually use?
- **Context:** CLAUDE.md says `<drive>:/Data/`. The repo has an extracted CD image at
  `Original Game Files/Data/`, which may differ from an installed game's `Data` directory
  (installers commonly copy a subset, or decompress packed files).
- **What we checked:** nothing yet — noted at bootstrap.
- **Blocks:** corpus completeness. A format validator that passes 100% of the CD corpus
  proves nothing if the game reads different files at runtime.
- **Status:** open

### Q-0003 — Is `flc.dll` / `SMACKW32.DLL` used, or dead weight from a middleware bundle?
- **Context:** both present in the install payload. Smacker and Autodesk FLIC are video
  formats; the project ground truth names `4xvideo.dll` and `AVIPLAY.dll` for video.
- **What we checked:** nothing yet.
- **Blocks:** video/cutscene work, later.
- **Status:** open
