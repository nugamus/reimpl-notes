# Enhancements

Improvements that are not bug fixes: things the original never did, offered as an option
the player can tick in ScummVM (Game options → Engine tab), off unless the entry says
otherwise. Agents propose them here; the user decides by changing **Decision**. Agents
implement entries marked `approved` without asking again, then mark them `done` with the
commit.

How to propose one (agents): add it under its game with the next id, fill every field,
**Decision:** `proposed`. Keep it to things a player would notice and want. Bug fixes do
not belong here (they go in issues, or in POSSIBLE-BUGS.md when unsure), unless fixing the
original's bug would change how the game plays; then the fix is an option here.

Entry format:

```
### OPT-X3D-001: Short name of the option
- **What:** what the player sees with the option on.
- **Why:** the annoyance or limitation in the original it removes.
- **Default:** off (original behaviour) | on (only for pure quality-of-life with no effect on play)
- **Cost:** a rough size (small / medium / large) and anything it touches (saves, timing).
- **Decision:** proposed | approved | rejected (reason) | done (engine commit)
```

Options already in the engines (each documented in ScummVM's `doc/docportal/settings/game.rst`
on the engine branch) are not repeated here.

## Monet (x3d)

## Mission Sunlight (peintre)

## Ring (ring)

## Gilbert (gilbert)

## Grumpa (grumpa)
