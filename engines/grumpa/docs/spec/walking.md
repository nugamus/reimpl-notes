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
  random attack, right the block). **Backspace**: leave a mount. (Jump, combat and mounts are
  not in this spec yet: Q-0806.)

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
- **Move**: (platforms first, Q-0810) up to 100 times: the face under the target (none: move,
  face −1); collect the boundary edges within `radius` of the target by flooding the faces
  whose edges are within `radius`; push the target out from the nearest to exactly `radius`.
  Then move and set `y = 0.4·y + 0.6·height`.
- **Floor types**: 0..4 view numbers (above), 12/13 water cases (with the mode `[0x48c]`,
  Q-0800), 15 a platform, 19..21 walls closed until the floor's opcode 6 opens them (opcode 5
  closes; both take type + 1, 0 = all); opcode 23 empties the platform list.

## Scene links, `CFXToScene` (E-0804)

The `.scn`'s record 0x14 (id 601):

- **Exits** `(x, y, z, r, scene)`: each update the player's sphere is tested against every
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

A character's sphere is centred on its position raised by its radius `[0x290]`, of that
radius; a trigger's is the four floats after its polygon. Two spheres touch when the centre
distance is below the radii's sum. A proximity-gated trigger (`+0x17c` = 1, `+0x154` = 1)
passes, for bit 1 of `+0x188`, when the player's character is present, is the required one
(`+0x150`, −1 any) and touches; with `+0x170` = 1 only once per stay inside. A click trigger
needs the gate when clicked; a walk-in trigger (`+0x178` = 0) fires on every update the gate
passes. Bits 2 and 4 (actor 4's character, actors 91..94) are Q-0811.
