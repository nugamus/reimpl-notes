# Grumpa: the critical path, from the data

The game's own logic, read from the scene graphs (`Scenes/Scene_*.abi`, `.scn`), the character
database (`Actors/Characters.abi`), the items (`Actors/Items.abi`) and the globals
(`Actors/global.atx`). Each step cites the trigger or record that does it. Sources:

- `engines/grumpa/tools/logic.py` → `engines/grumpa/notes/logic.txt`: every scene's records
  and command lists, with targets named (`tr663` trigger, `i104` item, `c69` character,
  `g269` global, `fade.GOTO(n)` the scene change), each trigger's click point and sphere.
- `engines/grumpa/tools/walkplan.py reach`: which exits each entry's walk-mesh region touches,
  and which wall type gates them (E-1802). `walkplan.py plan` writes a scenario's walking legs.

Facts this rests on: E-1802 (walls and exits), E-1803 (strength), E-1804 (the ending), E-1805
(the films), E-1800/E-1801 (the cursor's State in conditions). Open: Q-1800, Q-1801.

## The world

One map, mostly open: almost every scene link is a walk-in exit sphere (`.scn` record 601),
and only three scenes gate an exit with a closed wall (E-1802): scene 5 (the monkey guard),
7 (the roots), 21 (Nosferatu's door). The rest of the progress is gated by click triggers
with item or flag conditions, by enemies whose death lists open walls or drop keys, and by how
Grumpa travels (on foot, swimming with the air timer, or on a mount).

| Area | Scenes | Boss (death list) |
|---|---|---|
| Jungle island (start) | 1, 211, 3, 5..18, 61, 90, 40, 212, 300..310 | Turtle c36 (scene 14): clears the spawners, drops the Seed Star |
| Swamp island | 20..27, 39, 60, 63..69, 75, 320..326 | Crocodile c47 (27): Seed Cube |
| Desert island | 30..37, 41, 80, 81, 330..338 | Hyena c55 (33): Seed Triangle; Scorpion c56 (37) |
| Sea, surface | 4, 50, 82..87, 100, 101 | |
| Sea, underwater (air timer) | 51, 53..58, 70..74 | Octopus c80 (58): opens the way into the ship; Skeleton c78 (56): the Oars |
| Pirate ship | 102, 104..109, 114, 117..119 | rat leaders c38 (104, Key Red), c37 (108, Key Blue); Captain c69 (102): the ending |
| End | 96 (outro or death film), 500 (intro) | |

## The critical path

The shortest route the data allows to the good ending, in the designed order: from the jungle,
under the sea to the ship. 23 steps through 31 scenes. Mechanics: **walk** walking, **run**,
**jump**, **fight** combat, **plat** platform, **follow** follower, **mount**, **swim**
swimming (water floors, the air timer g220), **use** an item held on the cursor clicked on a
hotspot, **take** picking an item up, **film** an in-scene film (type 0x07), **talk** voice
lines, **view** view change, **timer**.

| # | Scene(s) | What the player does | Trigger / condition (data) | Mechanics |
|---:|---|---|---|---|
| 1 | 1 | Take the broken sword, the shield (both used in fights) and the flying dust; click the door | items 100, 134, 105 lie here; `tr663` → `GOTO 211` | walk, take |
| 2 | 211 | Take the Gate Key; at the gate (view 3) hold it and click the lock | i104 lies at (834, 1, −65); `tr663 IF 2[0]==2 OR i104==6`: lock mesh 712, its end list `OPENWALL(0)`, `GOTO 307` | walk, view, take, use |
| 3 | 307, 3 | Walk through 307 to 3 | exits; 3's walk-in `tr660` starts the cannonball (timer 920) that frees the Wood Splinters (optional) | walk, timer |
| 4 | 3, 308, 212, 309, 7, 8, 12 | Walk on to scene 12; the roots in 7 only block the way to 10 | E-1802: from 309, scene 7 reaches 8 | walk |
| 5 | 12 | Take the Fishing Net (and the Empty Jar); the Sleepy Rat c35 wakes on `tr660` | i121 at (−559, 39, −193) | walk, take, fight (avoidable) |
| 6 | 12 → 8 → 7 → 309 → 212 → 308 → 3 → 303 → 14 | Walk back across the island to the turtle's beach | exits only | walk |
| 7 | 14 | The Turtle pirate boss talks (`tr660`), then fights; the exits are not walled | `so640` end: c36 on, `OPENWALL(21)` | talk, fight (avoidable) |
| 8 | 14 → 301 → 17 | Cross the piranha pool (bites `tr662/665..667`, life −4) and walk up into the cave | `tr663` (on foot) → `GOTO 18`; floor type 13 | walk, swim, timer |
| 9 | 18 | Click the Gauntlets of Power: strength 5 → 16 (E-1803) | `tr665`: g240, `c10.88(11)`, `c10.90(2)` | take |
| 10 | 18 → 17 → 300 → 16 | Walk to the beach and into the water | 16 `tr665` (not in boat/on dragonfly) → `GOTO 73` | walk, swim |
| 11 | 73 | Hold the Fishing Net and click the seahorse: Grumpa rides it, the air timer stops | `tr660 IF c10[4]==1 & i121==6`: i121 used, c88 `44` | use, mount, swim |
| 12 | 73 → 58 | Ride to the ship's hull and kill the Giant Octopus | c80 (home 58) list 2: `@58 OPENWALL(0)` (E-1802) | swim, mount, fight |
| 13 | 58 | Leave the seahorse (Backspace), click the hull | `tr660 IF c10[4]==1` (view 1): `GOTO 101` | mount, swim, view |
| 14 | 101 | Click the ship's side: Grumpa climbs on deck | `tr660`: mesh 710's end list `GOTO 102` | walk |
| 15 | 102 | The captain speaks (walk-in `tr660`, active from the start: Q-1800); click the hold door | `so640` end: c69 on; `tr661` → `GOTO 104` | talk |
| 16 | 104 | Kill the red rat leader (taunt `tr674`) for the Key Red; cross the seesaw board; use the key (or the Bottle of Rum) on the hatch; climb down | c38 list 2: i127 at the rat; `tr660..665` board; `tr667 IF i103==6 OR i127==6`, `so641` end `tr668` on → `GOTO 105` | fight, take, plat, use, view |
| 17 | 105, 106 | Dodge the rolling barrels (life −10); down through 106 | `tr660` → 106; exit → 107 | walk |
| 18 | 107 | Cross the trapdoor floor: each tile opens the trap under another (falls: back to the start, life −11) | `tr661..669`, falls `tr670..679`; `tr660` → `GOTO 108` | walk, timer |
| 19 | 108 | Kill the second rat leader (`tr663`) for the Key Blue; open the door; go in | c37 list 2: i129; `tr661 IF i103==6 OR i129==6` → `tr662` → `GOTO 109` | fight, take, use |
| 20 | 109 | Pull the cork (strength > 15): the ship floods | `tr661 IF c10[2]>15`; cork mesh 712 end: film `unplug.mpg` (119 actor 620), `GOTO 119`; @102 door and way back closed (E-1804) | film |
| 21 | 119 → 118 → 117 | Swim up through the flooded hull (air bubbles refill) | 119 `tr660`; 118 `tr662` (no key needed) | swim, timer |
| 22 | 117 → 114 → 102 | Step onto a rising barrel to the flooded deck, then click back up | 117 `tr660..662` → 114 entries 750..752; 114 `tr660` → `GOTO 102` | plat, swim |
| 23 | 102 → 96 | Kill Captain Ratbeard: the outro film and the end | c69 list 2: `@96 940.56(1)`, `GOTO 96`; 96 script 781: `grumpa_outro.mpg`, `end_succesful_VS.wav`; then the main menu (E-1804, E-1805) | fight, film |

Losing all life takes the other branch of the same scene: Grumpa's list 7 sets 96's flag 941
and goes there: `grumpa_death.mpg` (E-1804).

## Choices and alternatives on the way

- **Key Red / Key Blue**: the Bottle of Rum opens either lock instead (104 `tr667`, 108
  `tr661`); there is one bottle (scene 6: the Ape King cooks it from a banana, flag 940 once).
  So at least one rat leader must be beaten.
- **Strength > 15** (step 20, and the Sword of Might in 61/9): the gauntlets (18), the Belt of
  Strength (37) or the Ape King's Jungle Mixture (honey, scene 6; a timed +11, g223) (E-1803).
- **The surface route**: the boat (c27 at scene 12, rowed with the Oars from the Skeleton
  Captain's chest in 56) or the dragonfly (scene 20, the flying dust) to 100 and 101, under
  scene 100's cannons. Whether mounts cross 100's mesh to 101 is Q-1801.
- **Without the seahorse**: Grumpa can swim 16 → 73 → 58 on foot, against the air timer
  (bubbles in 58 refill 10).
- **The captain on the first visit**: by the data he is already up when Grumpa first boards
  (Q-1800); the hold and the cork are the designed way.

Not needed for the ending, by the data: the three island bosses (they only clear their
islands' enemy spawners and drop the seeds), the Ape King's son, the seeds and fruits, the
witch's Ancestor Fruitpunch and the Grandfather form (26), the golems, the parrot, the bear
and the Monkey Champion followers, the Lock Shaped Stone and Diamond. No ship trigger tests a
flag or item from the islands.

## Side quests (one line each, for later scenarios)

- Jungle: bananas from the stuck rat (13, burning splinter) or the ladder (16 → 13); the monkey
  guard (5, a banana, opens wall 19 to 6); the Ape King's cauldron (6: fire, then banana → Rum,
  coconut → Antidote, honey → Jungle Mixture; the son → the Monkey Champion follows); the roots
  (7, fire or Rum); the snake and the Sword of Might (10/61 and 11/9 by the rope); honey and bees
  (309 flowers, 15); the bear mount (40, honey); boulders and the golem (90).
- Swamp: the witch (22: the father's sword repaired for 4 coins, a shop, the Fruitpunch from
  the three fruits), the three seed doors (24 → 63/65/66), the crocodile boss and the ants (27),
  the tomb (25 → 26, the Grandfather form), termites (23), Nosferatu (21/69), the dragonfly (20).
- Desert: the crab, the tired elephant and water (30/34/35), the parrot follower (34), the
  hyena boss and the falling pillar (33), the worm and the Ape King's son (31/32), the gate (36,
  g269 Snake Dead), the scorpion and the belt (37), the Octagon Diamond (41).
- Sea: the shark's belly and the son (53/54), FoxyLady and the chest (50), the Skeleton
  Captain (56).

## Water, air and drowning

All of it is data (E-1661, E-1680..E-1682); the code only draws the ripple and limits boats
on floor type 13 (E-1660).

- **Air timer** `g220` (4 s): each firing, Air > 0 → Air −6 and again; Air 0 → it stops and
  `g221` (4 s) starts: Life −8 each firing while Air is 0; once Air > 0, 221 stops and 220
  restarts. Full air (99) lasts 68 s, then 8 Life every 4 s; Life < 1 kills Grumpa (death
  film, scene 96). Conditions are tested when the command is queued, before its effect.
- **Underwater scenes** (entry script: start 220, show the bar): 51, 53, 55..58, 70..74,
  117..119. **Surfacing** (220 and 221 stop, Air +100, bar hidden): 12, 16, 20, 80, 101, 114;
  30, 32, 50, 54 forget to stop 221 (Q-1680). The seahorse (73 trigger 660, c87) stops both
  timers and hides the bar; leaving it (c88 list 1) starts 220 again unless the scene is
  12, 16, 20, 30, 50 or 80.
- **Bubbles**: animated meshes in 51, 55..58, 71, 118 with a contact sphere (r 13..27) on
  one vertex; touching one gives Air +10 (+2 in 51 and 71's third), once per touch.
- **Water floors** (type 13, Grumpa wades with a ripple; type 12 in 114): 12, 16, 17, 50 and
  the other surface scenes; the underwater scenes are ordinary floor (type 0..3). Step 8
  (14 → 301 → 17) has no air: the danger is the piranha bites. Step 10 (16 `tr665`, a walk-in
  sphere r 765 when not in the boat or on the dragonfly) → 73, where the timer starts. Step 21
  (119 → 118 → 117): air drains from 119 on, 118's bubbles refill; 117 → 114 refills to 100.

## Engine gaps on the critical path

What the `grumpa` engine has (engine `CLAUDE.md` Status, 2026-10-06) against what the 23
steps need. "Steps" counts the steps that cannot be played without it.

| Mechanic | Engine | Steps blocked | Evidence |
|---|---|---:|---|
| Combat (attacks, damage, death lists) | missing (in progress) | 4: 12, 16, 19, 23 (5 and 7 can be fled) | Q-0806, E-1404 |
| Swimming (floor types 12/13, mode `[0x48c]`, the air timer and bubbles) | missing | 7: 8, 10..13, 21, 22 | Q-0800, E-0703 |
| Cursor State in conditions (actor 2 slot 0 = cursor kind) | missing | 1: step 2, so everything after it | E-1800, E-1801 |
| Mounts (form change op 0x2c/44, dismount) | specced, not built | 2: 11, 13 | E-1530, Q-0403 |
| In-scene films (type 0x07: `unplug.mpg`, the outro, the death film) | done (branch grumpa-a5; scenario `film`) | 0 | E-1805, E-1806 |
| Mesh animation end lists (the 7th list: lock, cork, ...) | fixed (grumpa-a5) | 0 (2 and 20 need it) | E-1807 |
| Platforms (moving 0x1a floors) | done | 0 (16, 22 rely on it) | E-1600 |
| Walking, running, exits, views | done | 0 | E-0810..E-0818 |
| Items: take, panel, use by condition | done (reach Q-0202 restored) | 0 | E-0900, E-0901 |
| Voice lines, timers, fades, HUD life/air | done | 0 | E-0405, E-0204, E-0700, E-0703 |
| Jump | missing | 0 on this path (swamp entry from 4, desert 41) | Q-0806 |
| Followers | specced | 0 on this path | E-1530 |

Ranked by steps blocked: swimming (7), combat (4), mounts (2), the cursor State (1, but it
is step 2 and stops everything).

## Scenarios

The chain plays the path from a new game, each scenario starting from the previous one's save
(`saves_from`; run them in order):

| Scenario | Steps | Ends |
|---|---|---|
| `path1_hut` | 1 | in 211, saved in slot 1 |
| `path2_gatekey` | 2 | at the gate with the key held: the lock click does not fire (cursor State, E-1800) |
| `film` (not chained) | 20 | the cork pulled in 109 (strength given by op), `unplug.mpg` plays, the flooded hull 119 runs on |
