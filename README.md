# reimpl-notes

Research notes and tools behind my [ScummVM](https://www.scummvm.org) engines for a handful of late-90s
adventure games. The engines themselves live in my ScummVM fork,
[nugamus/scummvm](https://github.com/nugamus/scummvm); this repo is everything that went into figuring out how
the originals work.

| Engine | Game | Developer |
| --- | --- | --- |
| `x3d` | Monet: The Mystery of the Orangerie Museum | 4X Technologies |
| `peintre` | Mission Sunlight | |
| `ring` | Ring: The Legend of the Nibelungen | Arxel Tribe |
| `gilbert` | Gilbert og den kemystiske ø | |
| `grumpa` | Grumpa | |

## What's in here

```
engines/<engine>/
  docs/     specs and write-ups: file formats, scene logic, open questions, evidence logs
  notes/    working notes: function and address maps, call graphs, file checksums
  tools/    parsers, validators, tracing proxies and helper scripts
games/<game>/
  docs/         notes on the game itself (structure, puzzles, versions)
  playthrough/  routes used to test the engines end to end
tools/      shared tooling: Ghidra scripts, disc readers, launch helpers
```

File formats are described as [Kaitai Struct](https://kaitai.io) specs (`*.ksy`) where possible, and every parser
has a validator that has to account for every byte of every file before a format counts as understood.

## What's not in here

No game files, ever: no disc images, no extracted assets, no screenshots of the originals, no executables.
You need your own copy of a game to use any of the tools.

Decompiled or disassembled code from the original executables isn't included either. It was used as reference
during the analysis, but it's the publisher's code, so only the conclusions drawn from it are here: names,
addresses, behaviour and the formats themselves.

## Using the tools

Most of it is Python 3 with no unusual dependencies. The Ghidra scripts expect a local Ghidra install
(`tools/ghidra/`), and the tracing proxies under `engines/x3d/tools/proxy/` build with CMake and MSVC for 32-bit
Windows. Each tool folder has notes on how it's run.
