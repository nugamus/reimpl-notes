# Characters (engine behaviour)

The character database, how a character comes to be in a scene, and the commands it takes.
Format: `docs/formats/README.md` (`.abi`, type 0x03) and `tools/parsers/abi.py` `t_03`.
Evidence: E-0400..E-0404, E-1220..E-1224, E-1500..E-1503, E-1530. Open: Q-0402, Q-0403, Q-1500.

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
| 0x32 / 0x33 | Life + / − `arg1`: passed to the score as `(op, arg1, own id)` (`score.md`, E-0704) |
| 0x44 | film `arg1` of the character's list after a fade out over 16 (E-0700); the lists are empty in the data |
| 0x58 / 0x59, 0x5a / 0x5b | slot 2 / slot 3 + / − `arg1` (floor 0) |
| 0x5d / 0x5e / 0x5f | slot 2 / 3 / 1 = `arg1` |
| 0x47 | placed at actor `arg1`'s position and orientation, then a pending move of 30 along its yaw (taken by the next tick's floor Move); home = current scene, active = visible = 1, role 0 (E-1530) |
| 1 | stop (request 2) (E-1530) |
| 500 / 501 | active = visible = 1 and request 5 / active = visible = 0 and stop |
| 0x2c / 0x2d | becomes the player's / the follower's character (Roles) |
| 0x37 | passed on to actor 4: the follower lets go |
| 0x46 | a rider form splits (Mounts) |

## Roles: the player and the follower (E-0816, E-1220..E-1224, E-1530)

A character's role (`+0x564`, which is its state slot 4, so conditions such as `c10[4] == 1`, "Grumpa is the player", read it): 0 none, 1 the player's, 2 the follower's, 3..7 a fighter's
(`combat`, E-1500). Two global actors hold one character each:

- **Actor 3**, the player controller (`walking.md`), holds the player's character. **0x2c** on
  a character: the character actor 3 held before gets op 1 (stop) and role 0; actor 3 holds
  this one; it becomes active and visible, home = current scene, role 1; the score gets
  (85, own id), so the form icon and Life follow (`score.md`).
- **Actor 4**, `CFXFollower`, holds the companion. **0x2d** on a character: only when actor 4
  holds none: actor 4 holds it; home = current scene, active = visible = 1, role 2.
- A new game starts with actor 3 holding Grumpa 10 and actor 4 holding the
  Scharlakanskraken 16 (`global2.atx` `<22>`, `<23>`).

Commands to actors 3 and 4: 0..3, 0xb..0xd, 0x32..0x36, 0x48, 500, 501 are passed on to the held
character (dropped when none). **0x37**: the held character gets op 1, role 0, and the actor
holds none; for actor 4 a fighting companion's flag on actor 95 clears too (combat). **0x23**
`arg1` ≠ 0: the next scene entry does no placement (once); 0: it does.

**Following** (actor 4's update, every second update): with F the companion's position, P the
player character's, d = (F.x − P.x, 0, F.z − P.z) normalised, heading = acos(d.z) (negated
when d.x < 0), turn = π + heading − companion yaw; while the freeze count is above 0 the turn
is 0 and the count drops by one. dist = |F − P| (3D):

| dist | request |
|---|---|
| > 170 | run (1) with the turn |
| 100 < dist ≤ 170 | walk (0) with the turn |
| ≤ 100 | stop (2) with the turn, only on the first update of this band |

Then, if dist < 70: the companion steps 4 units straight away from the player in x/z (no floor
test), gets walk (0) with turn + π/2, and the turn is frozen for 20 rule runs (so it walks
round out of the player's way).

**Scene entry** (actor 4 on 0x17): unless 0x23 asked otherwise, the companion takes the
player character's position and orientation and steps 20 back along that yaw (x −= 20·sin yaw,
z −= 20·cos yaw); else it keeps its own. It is placed there, gets request 5 (idle), its home
becomes the scene when it is active; the freeze count is reset.

**Shuffle aside** (the character update, E-1224): a role-0 character whose sphere overlaps the
player's or the companion's steps 4 units away from it horizontally, then gets walk with turn
π/2 and stop.

## Sound slots and the speech queue (E-1640, E-1620, E-1223)

Each `.wav` of a character's sound list is loaded once (with its clips) into slot
`atoi(name)` of a 100-slot table (`065_CS_Gulp_VO.wav` is slot 65), from `Sounds\<name>`; a
missing file leaves the slot empty. Character sounds have default volume and pan, no loop, no
speaker and no command list, so playing or stopping one never changes a talking flag by
itself. The character's **state slot 5** (talking) is written only by the queue below.

**Op 0x48** `arg1` = n: ignored outside 0..99 or when n is already in the queue. n < 60 and
n ≠ 32: play slot n now (no stop; a slot already playing just goes on). Otherwise append n to
the speech queue (unbounded, even if the slot is empty); if it is now the only entry, its slot
is loaded and slot 5 is 0, play it and set slot 5 = 1. Scripts send only n ≥ 60 (63/64 via
actors 3/4); slots below 60 and 32 (tired) come from the clip-start hook.

**Pump**, last step of the character update, so only for an active character at home in the
current scene, on its animation steps: if the front's slot is loaded and no longer playing,
pop it, slot 5 = 0, and play the next entry (if loaded) with slot 5 = 1. An entry whose slot is
empty is never popped and blocks the queue (data: (16,61), (21,61), (28,60), (30..32,60)).
**Flush**, on scene entry (op 0x17) and when a scene sound naming this speaker plays: only if
the character is away from the current scene, stop the front's sound and empty the queue
(slot 5 unchanged). A first line queued for an absent character therefore plays, but nothing
after it until the character is back. **Op 0x60**: stop all 100 slots without commands; the
queue stays, so the next pump moves on to the following line. No data sends 0x60.

## Mounts (E-1501..E-1503)

A rider form (kind 2) is Grumpa and a mount as one character: 11 the boat (10 + 27), 12 the
dragonfly (10 + 21), 13 the bear (10 + 28), 88 the seahorse (10 + 87). There is no automatic
mounting; scenes mount and dismount by commands: Grumpa off and hidden (through actor 3), the
form on, shown and made the player (0x2c), and the reverse. The form walks with the same
requests and update as Grumpa, on its own clips; only its data differ (radius, mode
`[0x48c]`: 1 boats, water faces only; 2 dragonflies).

**0x46** (split; only for kind 2 with both parts): the form becomes inactive and invisible;
the mount, then Grumpa, get 0x47 with the form's id (placed on the form, 30 forward, shown,
at home); Grumpa's pending move becomes (d·cos yaw, 0, −d·sin yaw) with d = |the mount's
current clip's least vertex x| + |Grumpa's greatest|, so he steps off sideways; Grumpa gets
0x2c (the form stops, Grumpa is the player, the score shows him).

**Backspace** (actor 3, each animation tick while held, no latch): if the player's character
is a rider form it gets 0x46; else actor 4 gets 0x37 (the companion is let go).


## Spawners (type 0x1d, E-0404)

A spawner holds spawn points, each a position, an orientation and a list of character ids.
Spawning a point picks a random id from its list that is not already spawned (up to 60 draws),
moves that character to the point, turns it, sets `active = visible = 1` and sends it opcode 2
(so its home becomes the current scene).

## Drawing

A present character draws its current animation's mesh (`Meshes/<anim>`) with its texture at
`position`, turned by `yaw` about +Y, through the view camera against the `_IZ.fxi` depth, like
a type-0x1a mesh actor (`scene.md`; the yaw sign is Q-0404). Until the animation state machine is specced (Q-0403) the
engine shows entry 0, the idle. The animation clock (E-0603): while the character is active
and at home, every update adds 0.46 to an accumulator; past 1.0 it loses 1.0 and the frame
steps; at the clip's last frame the frame goes to 0 and the next queued clip (if any) starts,
so the idle loops at 23 frames a second. The per-frame motion table the update also applies
is Q-0601.

## Attachments (E-1700, E-1300)

Each attachment entry is `{.ANB, .tga, face, attack bonus, defence bonus}`: `face` is a
face index of the body mesh, the bonuses go to state slots 2 and 3 while worn. A worn flag per
entry (start 0, saved in the status) is set by `wear(k, on)`: groups {0, 5} (shields) and
{1..4} (weapons) hold one worn entry each. Grumpa (10): 0 Shield (face 593, def 20),
1 Father's Sword (592, att 10), 2 Hammer (592, att 8), 3 Sword of Might (592, att 20),
4 Father's Sword broken (592, att 6), 5 Wooden Shield (593, def 5).

Drawing, before the body, for every worn entry k, in any clip:
- p, n = position and normal of the vertex the body's index buffer names first for face
  `face_k`, in the current clip at its current frame (the GPU vertex is the corner's UV slot,
  which carries the corner's position vertex, see E-1700).
- pitch = acos(n.y), negated if n.z < 0; yaw = 0, but for shields (k = 0, 5) yaw = acos(n.y),
  negated if n.y < 0; roll = 0.
- world = YawPitchRoll(yaw, pitch, 0) translated to p, then times the character matrix
  (its yaw-pitch-roll orientation, at position + (0, `+0x178`, 0)); row vectors, D3D order.
- draw the attachment `.ANB` at frame 0 (it never animates) with its `.tga`.
