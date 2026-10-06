# Patterns

Techniques that came up in more than one game, written once so the next game starts from
them instead of rediscovering them. Each page says what the problem looks like, what to
do, and where we did it. They are indexed by `tools/ref.py` (source `ours`).

| Page | When |
|---|---|
| [identifying.md](identifying.md) | A new disc, an unknown file or executable |
| [protection.md](protection.md) | The EXE is encrypted, packed or checks the disc |
| [naming-code.md](naming-code.md) | Ghidra shows thousands of `FUN_` and you need names |
| [emulating-original-code.md](emulating-original-code.md) | A format's grammar is buried in a long loader |
| [observing-the-original.md](observing-the-original.md) | You need what the running original actually does |
| [scummvm-reuse.md](scummvm-reuse.md) | Before writing a decoder, a renderer or a UI piece |
| [directdraw-to-scummvm.md](directdraw-to-scummvm.md) | Porting a DirectDraw game's screen, blits, colour keys and timing |
| [software-3d-parity.md](software-3d-parity.md) | Matching the original's 3D (Direct3D 7 or a software rasteriser) |

Add a page (or a section) when you solve something a different game would hit too. Keep
it to the technique and our tools; game specifics stay in the engine's docs.
