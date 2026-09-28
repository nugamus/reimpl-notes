# Mission Sunlight: playthrough

A short route through the whole game, for testing the engine. It is read from the scene
flows in [`../docs/`](../docs/) (each step links to the scene it happens in); nothing here
is new knowledge.

1. [Act 1: Holland](act1.md): the museum, the cottage, the potato eaters (zones 0–3)
2. [Act 2: Arles](act2.md): café, terrace, Yellow House, bedroom, bridge, hospital (zones 4–18)
3. [Act 3: Auvers](act3.md): garden, inn, wheat field, church, the ending (zones 19–24, 21)

## How every puzzle works

- **Take** an item: click it; the inventory bar opens (Space opens it any time).
- **A zone** (a 2D puzzle) opens when you click its object in 3D. Open the bar, drag each
  listed item onto its empty slot and play its mini-game ([`../docs/a*.md`](../docs/)).
- **Sunflower**: when every item of a zone is placed, click the sunflower and drag it onto
  the vase. Backspace or the corner arrow leaves a zone or a scene.
- **Carry**: some 3D objects are carried instead of taken (the cursor changes); click the
  target while carrying, anything else drops it back.
- **Acts** open in the museum: act 2's door after zones 1–3, act 3's after zones 4–18
  ([`musee.md`](../docs/musee.md) "Init").

## Faster testing

Dev ini game domain (`engines/peintre/tools/scummvm.ini`): `dev_scene=<n>` starts in a 3D
scene, `dev_zone=<n>` + `dev_held=all` in a zone with every item. Scene numbers are in
each act's table.
