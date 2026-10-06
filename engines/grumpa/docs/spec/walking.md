# Walking (engine behaviour)

How the player's character moves: the mouse steering of actor 3, the character's clip queue
and root motion, the walk mesh (`CFXFloor`), the scene links (`CFXToScene`) and the proximity
gate. Format: `docs/formats/README.md` (`.scn`, `.amb`). Evidence: E-0705, E-0800..E-0804,
E-0810..E-0818, E-0830, E-0831. Open: Q-0800, Q-0805..Q-0807, Q-0810, Q-0811. Engine: `walk.cpp`, `character.cpp`.

## Controls (E-0810, E-0811)

There is no click-to-walk, no path finding and no keyboard steering. The mouse actor 2 turns
button messages into broadcasts (0x12 left down, 0x14 left up, 0x13/0x15 right, 0x16 move;
cursor packed `x | y << 16`; to actor 90 only while the panel is open). Actor 3 (type 0x16) is
the player controller and holds the player's character (`+0x298`):

- **Left button held**: walk towards the cursor. A press whose cursor is not a walking arrow
  (kind outside 9..25: over a hotspot, an item, the panel) does not walk.
- **Release**: stop.
- **Shift** with the left button held: run. **Space**: jump. **Ctrl**: combat stance (left a
  random attack, right the block). **Backspace**: leave a mount. (Jump and combat: `combat.md`;
  a walk, run or jump request from a clip with no row keeps the queue, E-1404.)

## Actor 3's update (E-0812)

Each update the steer angle is computed and the buttons' requests are made (on 0x12 a walk
request with the turn, on 0x14 a stop). On its own animation clock (0.46 an update, as the
characters', E-0603), in order:

1. The character's floor type 0..4 is a **view number**: the first time after entry it selects
   that view at once; a later change sends (185, 30, type), the faded view change.
2. **Turn**: `turn = mouse angle − (yaw − view yaw) − π`, where the mouse angle is the angle of
   the screen vector from the character's screen point to the cursor (`π ± acos` of one of its
   normalized components, negated when the cursor is to the right; Q-0805) and the view yaw is
   the yaw of the view matrix's forward vector. Read geometrically: the character heads where
   the cursor lies on screen, "up" being the camera's forward direction on the floor. Where
   the character's screen point is computed is not read (Q-0805). The 16 walking-arrow
   cursors (kinds 9..24) follow the angle.
3. Shift with the left button held: a run request.
4. When the cursor is more than 20 px from the character's screen point: a turn-only request
   (−1). So a standing character turns to face the cursor too.

## Requests and the clip queue (E-0813, E-0815)

A character's clips sit in a 44-slot table; an `.anb` goes to the slot its name's number
gives (`004_W2R_Grumpa.anb` is slot 4). Grumpa: 0 idle, 1 N2W, 2 W2W walk loop, 3 W2N, 4 W2R,
5 R2R run loop, 6 R2W, 7 R2N, 0x1f..0x21 S01..S03. The clip playing at load is `[0x434]` from
Characters.abi.

Every request aims the yaw: yaw and turn are wrapped to [−π, π] and the next 10 animation
ticks each add `turn × 0.1` (re-aimed by every request, so steering closes 10 % of the error a
tick). Request −1 stops there; any other clears the queue and pushes, by the clip playing
("cut" = the clip ends at the next tick):

| request | from | queue |
|---|---|---|
| 0 walk | 0, 0xb, 0xd | cut, 1, 2 |
| | 1, 2, 3 | 2 |
| | 0x20 | cut, 0x21, 1, 2 |
| 1 run | 0, 0xb, 3 | 1, 4, 5, 6, 2 |
| | 1, 2 | 4, 5, 6, 2 |
| | 5 | 5, 6, 2 |
| | 0x20 | 0x21, 1, 4, 5, 6, 2 |
| 2 stop | 1, 2 | 3, 0 |
| | 5 | 7, 0 |
| | others | 0 |
| 5 reset | any | clip 0 at frame 0, queue empty, clock 0.6 |

## The character's animation tick (E-0603, E-0814, E-0802, E-0803)

1. The frame steps; past the clip's last frame it is 0 and the queue's next slot plays (an
   empty queue loops the clip).
   **Idle fidget (E-1740)**: the front is popped only when the queue holds more than one slot,
   so the last one repeats. At each clip start, a counter `[0x4a8]` goes +1 if the new clip is
   0 and to 0 otherwise. When it passes 10 (the 11th idle start in a row) it goes back to 0 and,
   if slot 0x1f is loaded, the queue becomes 0x1f, 0x20: the current idle plays out, S01 plays
   once, then S02 (0x20) loops until a request (walk or run from 0x20 plays 0x21 first). No
   randomness; every character, not only the player. Requests leave the counter alone
   (request 5 doesn't count as a start); a spawned character starts at 9, a new one at 0.
2. One yaw step, except in clips 8, 0xc and 0x12..0x14.
3. **Root motion**: unless the clip is 0, the clip's `.amb` record for the frame `(x, y, z)` is
   the move: `dx = z·sin(yaw) + x·cos(yaw)`, `dz = z·cos(yaw) − x·sin(yaw)` (local +z forward;
   y goes to a vertical offset, not the position). There is no speed constant: Grumpa's W2W
   moves about 5.1 units a tick, R2R 8.5..9.7.
4. **Floor**: the move goes through `CFXFloor::Move` with the character's radius `[0x28c]`.
   This runs every animation tick, idle too (a zero move still pushes off the walls and
   settles y, E-0830). The result is undone (the old position kept) when it leaves the mesh, climbs more than 20
   (80 on a platform), or lands on a floor type above 18 whose blocking flag is set.

## The walk mesh, `CFXFloor` (E-0800..E-0803)

The `.scn`'s record 8 (id 600): vertices (only x, y, z are read), triangles, a floor type per
face, and the neighbour across each edge (built at load from shared edges).

- **Face under (x, z)**: the triangle's x/z box (inclusive), then the edge functions of
  (v1, v0), (v2, v1), (v0, v2) all strictly positive. Searched from a hint face, its three
  neighbours, then every face.
- **Height**: per edge, the point projected in x/z on the edge's line (unclamped) gives a
  height; the three are blended by inverse x/z distance (weight 1e15 under 1e−7).
- **Move**: (platforms first, below) up to 100 times: the face under the target (none: move,
  face −1); collect the boundary edges within `radius` of the target by flooding the faces
  whose edges are within `radius`; push the target out from the nearest to exactly `radius`.
  Then move and set `y = 0.4·y + 0.6·height`.
- **Floor types**: 0..4 view numbers (above), 12/13 water (below, E-1660), 15 a platform, 19..21 walls closed until the floor's opcode 6 opens them (opcode 5
  closes; both take type + 1, 0 = all); opcode 23 empties the platform list.

**Platforms (E-1600).** On the scene-entry broadcast (23, ids ascending) the floor (600)
empties its platform list, then every 0x1a mesh actor with `+0x1d0` = 1 appends its id. Move
first walks that list: for each **active** entry (visibility not tested), every face of its
mesh (all sections, corners by the uv-index triples into the vertex buffer, **frame 0**,
model = world coordinates) gets the floor's face test at pos + delta. The first hit sets the
character's face and platform (the list index), moves by delta, sets y = 0.4·y + 0.6·h with
h = y of the face's first corner in the actor's **current** frame (`+0x1c0`), floor type 15,
and skips the wall slide. No hit clears platform and face (full static search). Nothing
carries the character in x/z; a rising platform lifts him only through h, every update.
The character's step limit is +80 on a platform (+20 otherwise).

## Water and swimming (E-1660, E-1661)

There is no swimming state: no swim clip, request, speed, turn or root-motion change. Water is
two floor types read after the floor Move, in this order (mode = Characters.abi `[0x48c]`):

1. Mode 1 (boat): y = −0.5 and the remembered old y = 0. If the face's type is not 13, the
   character goes back to its old x/z (y 0): a boat moves only on type-13 faces.
2. Type 13 with mode 2 (dragonfly): y = −0.5, old y = 0.
3. On type 12 or 13, while the clip is a jump (0xf, 0x10, 0x11) y stays the old y (the floor
   height is not followed); on type 12 with mode 2 y always stays the old y.

Anything else on 12/13 follows the floor like ground (type-13 faces go down to y −8180, so a
walker wades or sinks with the mesh). Actor 3 refuses Space (jump) on type 13; Shift, Ctrl and
Backspace do not look at the floor. Draw: on type 13, when y < −4 or in mode 1, the shared
`Meshes/waterripple.ANB` is drawn at (x, 4, z), uniform scale min(|y|·0.03 + 0.2, 1) (1.5 in
mode 1), playback value 5 while idle (clip 0) else 8; on every other type the shared
`Shadow.ANB`; on type 13 above −4 neither. Floor types 1..3 are only view numbers, 8 is never
read.

How they are drawn (E-1612), only while the character is not dying (`+0x474` ≠ 1), after the
worn attachments and before the body mesh:

- **Ripple**: `waterripple.ANB` textured with `Bitmaps/Virvel.tga`; world = scale s then
  translate (x, 4, z), no rotation. Lighting off; blending by the texture's alpha
  (SRCALPHA / INVSRCALPHA; Draw first asks for ONE/ONE but the 32-bit texture's bind
  overrides it); z-test and z-write stay on. Each draw advances the shared mesh: one frame
  every 50 / fps draws (fps 5 idle, 8 otherwise, integer division: every 10 or 6 draws),
  looping. The counter is shared, so every rippled character advances it.
- **Shadow**: `Shadow.ANB` textured with `Bitmaps/Shadow.tga`; world = the character's own
  matrix (orientation, position + (0, `+0x178`, 0), no scale), so it turns with the
  character at the mesh's own size. Lighting off, z-bias 16, z-write off, alpha blending by
  the texture's alpha; frame 0 always. Every drawn character gets it on non-water floors.
- `watersplasch.ANB` / `Splasch.tga` are loaded but never drawn.

**Air** is scripts only (E-1661): becoming Grumpa-on-seahorse (88) starts timer 220 and shows
the air bar unless the scene is 12, 16, 20, 30, 50 or 80. Every 4 s: Air > 0 → Air −6;
Air 0 → timer 221, which takes 8 Life every 4 s until Air comes back (score 76 refills of 2,
10, 100 in scene scripts). Life < 1 runs the character's death (E-1403).

## Scene links, `CFXToScene` (E-0804)

The `.scn`'s record 0x14 (id 601):

- **Exits** `(x, y, z, r, scene)`: each update, after the characters have updated (actor 601 after 10..88, E-0202, so a player placed at an entry is first settled on the floor), the player's sphere is tested against every
  exit sphere. A touched exit becomes the remembered one and, unless the latch is set, sends
  (185, 31, scene): the faded scene change; then the latch is set. An untouched exit that is
  the remembered one clears the latch. Every scene starts latched (remembered 0) and clears
  the latch on its first update that touches no exit (E-0818), so a player placed inside an
  exit on arrival must leave it before it fires.
- **Entries** `(x, y, z, rx, ry, rz, scene)`: on entry the player takes the position and
  rotation of the entry whose scene is the scene left; else, if an entry names scene −2, stays
  where it is; else takes the first entry. Not on the first entry after a new game or a load.
  Then, every entry: the request 5 (back to the idle, whatever `[0x434]` started), and the
  held character's home becomes the scene when it is active (E-0816, E-0830).

## The proximity gate (E-0207, E-0705)

A character's sphere is centred `[0x290]` above its position, of radius `[0x28c]` (E-1405); a trigger's is the four floats after its polygon. Two spheres touch when the centre
distance is below the radii's sum. A proximity-gated trigger (`+0x17c` = 1, `+0x154` = 1)
passes, for bit 1 of `+0x188`, when the player's character is present, is the required one
(`+0x150`, −1 any) and touches; with `+0x170` = 1 only once per stay inside. A click trigger
needs the gate when clicked; a walk-in trigger (`+0x178` = 0) fires on every update the gate
passes. Bit 2 is the same test for actor 4's character (the companion) against the id
`+0x14c` (−1 any), with its own once-latch; bit 4 the fighters' characters (combat). Each
source passes on its own (E-0705, E-1533).
