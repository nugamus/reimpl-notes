# Possible bugs

Behaviour an agent is not sure is a bug: it might be what the game's makers intended. Each
entry gives the reasoning on both sides, so the user can decide by reading it. The user
answers by changing **Verdict**; agents act on it:

- `bug` → becomes a GitHub issue and gets fixed, even if the original has the same bug
  (ScummVM fixes the originals' bugs; a fix that would change how the game plays becomes an
  option in ENHANCEMENTS.md instead).
- `intended` → kept as the original does it; the entry stays as a record.
- `option` → moved to ENHANCEMENTS.md.

Before writing an entry, settle what can be settled (the `fix-issue` skill, step 1): what
the original's code does, and the signs below. Only what is still unclear comes here.

**Signs of a bug:** a crash, hang or softlock; state lost, corrupted or leaking between
places it shouldn't (saves, profiles, rooms); a visual that contradicts its surroundings
(clipping, wrong height or scale, flicker); behaviour that contradicts the game's own text,
manual or interface; the same action behaving differently in two places; data that looks
like a slip (an off-by-one coordinate, a missing case, a copy-pasted value).
**Signs of intent:** a deliberate code path with data written for it; the manual or the
interface describing it; the same design applied consistently across the game; the other
editions of the game doing the same.

Entry format:

```
### P-X3D-001: Short description
- **Seen:** what happens, where, how to reproduce (scenario or save).
- **Original:** what the original's code or a run shows (evidence ids).
- **For a bug:** the signs pointing that way.
- **For intended:** the signs pointing that way.
- **If it is a bug, the fix:** in a sentence, and whether it changes play.
- **Verdict:** open | bug | intended | option
```

## Monet (x3d)

### P-X3D-001: Every profile lists the same saves
- **Seen:** the save and load screens show the same saves whichever profile is selected
  (reported by the user, first filed as issue #1).
- **Original:** not checked yet. Next step: how the original names and filters its save
  files per profile (re-analyst), then one run of the original with two profiles.
- **For a bug:** profiles exist to separate players; a shared save list lets one profile
  overwrite another's game.
- **For intended:** the original may keep profiles only for names and settings, with one
  save list for the machine; our engine maps saves to ScummVM's per-game save slots, which
  have no notion of a profile.
- **If it is a bug, the fix:** save names carry the profile and the screens list only the
  current profile's saves (needs a save-format version bump; old saves stay visible to
  every profile).
- **Verdict:** open

## Mission Sunlight (peintre)

## Ring (ring)

## Gilbert (gilbert)

## Grumpa (grumpa)
