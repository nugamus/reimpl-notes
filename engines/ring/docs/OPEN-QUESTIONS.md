# Open questions (Ring engine)

Things we could not determine after checking the original code (Ghidra), the corpus and
traces. An unresolved field goes here and stays opaque (`unk_*`) in the format spec. It does
not get a guessed meaning, and it does not take Templier's meaning on trust either.

Append only. When a question is answered, keep the entry, mark it `RESOLVED`, and link the
`EVIDENCE.md` entry that resolved it.

## Entry format

```
### Q-0001 — <one-line question>
- **Context:** where it came from (format + offset, function address, trace line).
- **What we checked:** the original code, the corpus, traces, Templier's engine.
- **Observed range:** for a data field, the set of values seen across the corpus.
- **Blocks:** what work is stalled or degraded by not knowing this.
- **Status:** open | RESOLVED (see E-nnnn)
```

## Questions

### Q-0001 — Which protection wraps Prophet's Legend.ex_, and where do its import slots lead?
- **Context:** E-0004: sections `.cms_t`/`.cms_d`, entry point in `.cms_t`, import calls in
  `.text` go through slots in `.cms_d` (e.g. `[0x4e82f0]`) instead of the IAT.
- **What we checked:** section layout, entropy, byte diff against the crack (diff oracle
  only). No product string found in `.cms_t`/`.cms_d`.
- **Observed range:** 323 differing runs in `.text`, most of them 3-byte slot addresses.
- **Blocks:** naming the Win32 calls in Prophet's code during RE. A slot → import map can be
  built site by site from the diff (same call site, IAT slot in the crack) without using the
  crack's code.
- **Status:** open
