# Characters (engine behaviour)

The character database, how a character comes to be in a scene, and the commands it takes.
Format: `docs/formats/README.md` (`.abi`, type 0x03) and `tools/parsers/abi.py` `t_03`.
Evidence: E-0400..E-0404. Open: Q-0402, Q-0403.

## The database (E-0401, E-0402)

At boot the game loads `Actors/Characters.abi` (then `Actors/Items.abi`) into the global actor
table; `Scenes/Characters.abi` is never opened. Each record is one `CFXCharacter`, indexed by
its id, and stays loaded for the whole game: scenes do not create characters, they send them
commands. One record per *form*: Grumpa is 10, Grumpa in the boat 11, on the dragonfly 12, on
the bear 13, on the seahorse 88.

Per character the engine needs:

| field | meaning |
|---|---|
| `active`, `visible` | the Update and Draw gates |
| `home` (`+0x444`) | the scene the character is in; −1 = none (a spawner places it) |
| `position` (`+0x16c`), `yaw` (`+0x160`.y) | world placement, radians |
| `anims` (`+0x2e8`) | `.anb` names under `Meshes/`; entry 0 is the idle (`N2N`) |
| `sounds` (`+0x330`) | `.wav` names the character plays itself (attacks, hits, idle calls) |
| `textures` (`+0x30c`), `texture` (`+0x440`) | `.tga` names under `Bitmaps/`; the one in use |
| `attachments` (`+0x344`) | carried objects: `.ANB` mesh + `.tga` (Grumpa's shields and swords) |
| `kind` (`+0x128`), `parts` (`+0x13c`, `+0x140`) | 0 creature, 1 mount, 2 rider form made of two parts |
| `pairs` (`+0x12c`) | (other id, form id): which form two characters make together |

The rule, reaction and message lists are kept but not run yet (Q-0403); the message lists are
empty in the data.

## Presence (E-0403)

The game keeps one current scene number per character (`+0x448`). On every scene entry the
scene manager broadcasts opcode 0x17 with the new scene number, which every character stores.
A character is **drawn** when `visible` and `home == current scene`, and **updated** when
`active` and `home == current scene`. So a character shows up in a scene when its home scene
is that scene, or when a command brings it there:

| opcode | effect |
|---:|---|
| 2 | show: `visible = 1`, `home = current scene` |
| 3 | hide: `visible = 0` |
| 0xb / 0xc | `active = 1 / 0` |
| 0xd | disable: `active = visible = 0`, `home = −1`, latched until 0x34 |
| 0x17 | scene entry: current scene = `arg1` |
| 0x29 | place at another actor's position and orientation, show, `home = current scene` |
| 0x35 | texture index = `arg1` (clamped to the texture count) |
| 0x36 | `home = arg1` |
| 0x44 | show message `arg1` (none in the data; `dialogue.md`) |
| 0x47 | place at actor `arg1`'s position |

Roles (0x2c..0x30, 0x54: player control, follower, mount) are Q-0403.

## Spawners (type 0x1d, E-0404)

A spawner holds spawn points, each a position, an orientation and a list of character ids.
Spawning a point picks a random id from its list that is not already spawned (up to 60 draws),
moves that character to the point, turns it, sets `active = visible = 1` and sends it opcode 2
(so its home becomes the current scene).

## Drawing

A present character draws its current animation's mesh (`Meshes/<anim>`) with its texture at
`position`, turned by `yaw` about +Y, through the view camera against the `_IZ.fxi` depth, like
a type-0x1a mesh actor (`scene.md`). Until the animation state machine is specced (Q-0403) the
engine shows entry 0, the idle.
