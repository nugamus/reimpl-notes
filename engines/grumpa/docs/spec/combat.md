# Combat and jumping (engine behaviour)

The player's jump, stance, attacks and block; the enemies (`CFXFighter`, actors 91..95), how
they start fighting (reactions), hit, take damage and die. Controls and the request table's
walking part: `walking.md`. Evidence: E-0813, E-1400..E-1404, E-1430..E-1433, E-1460. Open:
Q-1400, Q-1420, Q-1440. Engine: `combat.cpp`, `character.cpp`, `walk.cpp`, `score.cpp`.

## The other requests (E-0813)

Beside walk, run, stop and reset (`walking.md`), a request clears the queue and pushes, by the
clip playing:

| request | from | queue |
|---|---|---|
| 3 jump (needs slot 0x10) | 0, 0xb | 0xf, 0 |
| | 1, 3 | 0x10, 0 |
| | 2 | now 0x10 at frame 0, then 0 |
| | 5 | now 0x11 at frame 0, then 0 |
| | 0x20 | 0x21, 0xf, 0 |
| 4 die | any | 8, 0xc |
| 0x12..0x15, 0x17, 0x1f..0x28 | any | that slot, 0 |

Slots: 0xf N2J2N, 0x10 W2J2N, 0x11 R2J2N, 0x12..0x14 attacks, 0x15 N2D2N (block), 0x17 N2H2N
(hit), 8 N2D, 0xc D2D (dead, looping), 0x23..0x25 S05..S07 (fighters' taunts, by name only).
A walk, run or jump request from a clip with no row changes nothing, the queue included
(E-1404, which corrects `walking.md`'s "clears the queue" for those); a request outside the
tables clears the queue and pushes 0; a dying character (death timer running) takes no
request and no turn. A character counts every clip start; the stance and the fighters watch
that count.

## The player (actor 3, E-0810, E-1400)

On actor 3's animation tick (0.46 an update), after the steer angle:

1. **Hit timer**: when the character has started a clip since the last tick: an attack
   0x12..0x14 sets the timer to trunc(F × 0.6) (F its frame count), the hit 0x17 sets it to 0.
   Then a timer above 0 counts down and on reaching 0 the **hit test** runs: once a swing, at
   about 60 % of the clip.
2. **Ctrl** up: stance off. Ctrl down, and the character has slot 0x12: stance on (cursor
   kind 7).
3. **Space**, not in stance, floor type not 13: request 3 (held: again every tick).

The mouse buttons' events (press or release of either button) make the request: in stance,
left held → a random attack 0x12 + rand() % 3, only while the clip is 0 or 0x20; else, with
the clip 2 or 5, stop; right held → 0x15 (block). Out of stance as `walking.md`. Right
**down** without Ctrl toggles the inventory panel; with Ctrl it does not.

**Hit test** (E-1401): for each fighter 91..94 holding a character: the 3D distance from the
player's position below 140, and u · f < −0.8, u the horizontal unit vector from the target to
the player, f = (sin yaw, 0, cos yaw) the player's forward (the target within about 37° in
front): the target takes a hit with the player's state slot 2 (strength). One swing can hit
several.

## Taking a hit (E-1402, E-1432)

The victim's last attacker becomes the hitter. If the victim's Life (slot 1) ≥ 0 and
n = attack − the victim's slot 3 (defence) > 0, the score (actor 8) gets (0x33, n, victim): the
victim's Life −= n; still above 0, it gets request 0x17; when it is the current form, the HUD
Life drops too (`score.md`). No invulnerability. While N2D2N (0x15) plays the character's
defence is 5 higher (added at that clip's start, removed at the next clip's start, E-1403).

## Death (E-1403, E-1433)

On a character's animation tick, when Life < 1 and no death is running: its turn stops,
request 4, and with a slot 8 the death timer = F(8), the hide timer = F(8) + 20, both counted
down a tick. The death timer reaching 0 posts the character's **death list** (the record's
`+0x630` commands, E-0401) and releases its fighter. The hide timer reaching 0: inactive,
invisible, home −1; characters 0x13, 0x38, 0x40, 0x45 and 0x50 keep their body (visible, at
home in the current scene).

## Reactions (E-1460)

A character's reaction list holds (other character, commands). On each of its animation ticks
while active and at home, unless its role (slot 4) is 7, its Life is below 1 or it is dying:
the entries in order; an entry whose character is visible and at home here and whose sphere
touches this one's (centres at position + `[0x290]` up, radii `[0x5fc]` each) fires once:
its commands are pushed (conditions apply), and no later entry is looked at this tick. An entry
not touching re-arms; every scene entry re-arms the characters at home there. This is how the
enemies start fighting (39..44, 81..85 engage with 0x2e..0x30 when Grumpa 10, 13 or 88 comes
near).

## Fighters, actors 91..95 (E-1430..E-1433)

Each holds one character and a target. A character opcode engages it, if the character's Life
is above 0: **0x2e** → 91 (role 3), **0x2f** → 92 (4), **0x30** → 93 (5), **0x4b** → 94 (6),
target the player's character; **0x54** `arg1` → 95 (7), target `arg1` (the fighting
companion). The character's last attacker = the target, home = the current scene, active,
visible, role (slot 4) as given. A fighter already holding another character gives it op 1 and
role 0. The first engaged fighter sends 0 to actor 301, the last released 1 (Q-1420). Commands
to a fighter (0..3, 0xb..0xd, 0x32..0x36, 500, 501) go to its character.

**Update**, on its own 0.46 clock, C its character, T its target, F, P their positions:

1. Nothing when C or T is none, or C's Life ≤ 0.
2. T alive and visible: if T is inactive and the player's character is another, active one, T
   becomes the player and the tick ends. Else T = C's last attacker.
   - turn = π + h − yaw, h = acos(d.z) of d = normalized (F − P) in x/z, negated if d.x < 0.
   - dist = |F − P| (3D): above 280 run; 180..280 walk; 140..180 one of 0x23..0x25 at random.
   - dist ≤ 140, and C started a clip since the last decision: an attack sets the hit timer to
     trunc(F × 0.6), 0x17 to 0; then rand() % 6: 0 stop, 1 0x23, 2 0x24, 3..5 attack
     0x12..0x14; all with the turn.
   - dist < 70: C moves 4 units away from T (x, z). C moves 4 units away from every other
     fighter's character (and the follower's) whose sphere overlaps.
   - A hit timer above 0 counts down; at 0, with dist < 140 and d · (sin yaw, 0, cos yaw) <
     −0.8, T takes a hit with C's slot 2.
3. T dead or invisible: 91..94 go for Grumpa (10), or, if T already is 10, stop and drop the
   target. 95 takes the first active enemy's character while more than one fighter is engaged,
   else Grumpa, else stops.

**Release** (the death timer, E-1433): count − 1, the fighter empty. When only the companion
(95) is left, its character goes back to the follower (0x2d) or role 0, and the count is 0.
**Leaving a scene** (0x19): 91..93's characters reset to idle, hidden, inactive, home −1; 94's
reset to idle; 95 handed back; every fighter emptied, count 0. **Entering** (0x17): 91..93
emptied the same way.
