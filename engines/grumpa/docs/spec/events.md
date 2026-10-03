# The event system (engine behaviour)

How Grumpa runs scene logic: navigation, puzzles, interactions. Evidence: E-0109..E-0117,
E-0200..E-0208, E-0700..E-0705.

## Actors

- **One table by id.** Every actor sits in a flat global table indexed by its id
  (`DAT_004b9bc4[id]`, `FUN_0040d270`; E-0110). Ids below 600 live for the whole game:
  0 the factory, 2 the mouse, 3/4 the player-character holders, 8..88 the characters,
  100..179 the items (`Items.abi`), 180 ambient sound, 185 the fade/scene manager, 186 a
  proxy, 200..279 the global counters, timers and flags of `Actors/global.atx` (E-0205).
  Ids 600..979 belong to the current scene (`Scene_<n>.scn`, `Scene_<n>.abi`) and are
  deleted when it is left (E-0202).
- **Common state** (E-0111, E-0201): `active` (`+0x10c`, updated), `visible` (`+0x110`,
  drawn), a latch (13 sets it, 52 clears it, nothing else is obeyed while set), and state
  slots: slot 0 "State" exists on every actor (value 0); `vtable[7]`/`[8]` get/set slot 0.

## Commands

A command is `(when, target, opcode, arg1, arg2)` plus a condition list (E-0109, E-0113).

- **Push** (E-0200): evaluate the conditions now; if false, drop the command. Then
  `when == -1` or `when ==` the current scene number → the **immediate** list; any other
  `when` (always another scene's number in the data) → the **deferred** list, kept across
  scenes until that scene is entered.
- **Run the immediate list** (E-0200): take the whole list, empty it, and deliver each
  command: `target == -1` broadcasts to every actor (ids ≥ 1), else the one actor. Commands
  pushed during the run wait for the next run.
- **Deliver** = the target class's `DoCommand(opcode, arg1, arg2)`; an id with no actor
  ignores it.
- **Conditions** (E-0201): `(id, slot, value, mode, link)`: `actor[id].slot[slot]` is
  `==` (0), `>` (1), `<` (2), `!=` (3) `value`. Conditions linked by `link = 0` form an AND
  group; `link = 1` ends a group; the list is true when any group is true; an empty list is
  true; an absent actor is skipped. If the list is true and the last tested actor is an
  item, actor 186 is pointed at that item.
- **"Run its commands"** (an actor firing one of its command lists) = push each command in
  order. Triggers and scripts skip a command that targets themselves with opcode 0.

## The loop (E-0202)

50 updates a second (0.02 s; timers add 20 ms per update). One update: run the immediate
list, then each actor's update in id order. Drawing follows.

**Leaving a scene:** broadcast 25 (`arg1` = the scene), run the immediate list, keep the
status of the scene's actors (E-0203: active, visible, state slots and the class extras).
**Entering scene n:** load its `.scn` and `.abi` (current scene = n), restore n's kept
status if any, deliver the deferred commands for n (removing them), broadcast 23
(`arg1 = n`) and run the immediate list, broadcast 86 and run it, push `(185, 33, 24)`.

## Classes

Opcodes shared by most classes: 0 play/run, 1 stop, 2/3 show/hide, 11/12 activate /
deactivate, 13 latch (and off), 52 unlatch, 86 reset, 500 on (active + visible + play),
501 off.

| class | opcodes and behaviour |
|---|---|
| 0x0d sprite (E-0208) | play 0/500 (and 23 if autoplay), stop 1/501, 2/3, 11/12, 13 (off, not playing), 52, 86. Update: while active and running, one frame every max(1, 50 / fps) updates (E-0701); mode bits 1 loop, 2 ping-pong, 4 forward, 8 backward, 0x10 forward-then-back. An animation that ends runs its end list; 0x10 runs its forward-end / backward-end lists. Frame count = the frames on disc. |
| 0x19 trigger (E-0207) | 0 activate + run, 1 deactivate, 2/3, 11/500 active + visible, 12/501 neither, 13 latch + off, 14/15 proximity on/off, 18 click `(x, y)`, 22 mouse position, 86. A click fires it when: active, view gate (`+0x174`) = current view or −1, click type (`+0x178 = 1`), inside the polygon, the proximity gate when `+0x17c = 1` (spheres below), its conditions when `+0x180 = 1`. Walk-in triggers (`+0x178 = 0`) fire from the update whenever the gate passes (the engine, without a moving player yet, fires them on a click: Q-0202). |
| 0x1a mesh (E-0601) | 0 play (always restarts), 1 stop, 2/3, 11/12, 13 latch + off, 14/15 bubble tests, 23 play if autoplay, 52, 86/92 reload, 500/501 (active + visible + play / neither + stop). Animation and its delay timer: `scene.md`. |
| 0x21 script (E-0204) | 0 run now; 23 run on the next update if unguarded or its conditions hold; 13/52. |
| 0x22/0x25 counter | 57 add (`arg1`, at least 1) below max → at max state = 1 and, with fire, run; 58 state 1 → 0, subtract, floor 0; 59 max = `arg1`; 62 count = state = 0; 13/52. |
| 0x23/0x26 timer | update: while active, elapsed += 20 ms; past the limit: stop, run. 64 start with limit `arg1`; 65 limit = `arg1`; 66 activate; 67 stop; 13/52. |
| 0x24/0x27 flag | 16/56: state = `arg1`; then state 1 with fire → run; 13/52. |
| 185 fade (E-0700) | 30 fade out over 20, then view `arg1`, broadcast 26 (`arg1` = view), fade in over 20; 31 fade out over 20 (`arg2 = −1`: black at once), then go to scene `arg1`; 32/33 fade out/in over `arg1` updates. See Fades. |
| 186 proxy (E-0206) | 63 target = `arg1`; anything else is delivered to the target. |
| 8 score, 180 ambience | `score.md` (E-0702, E-0703). |

## Fades (actor 185, E-0700)

A level L from 0 (black) to 255 (normal) scales every colour channel of the whole screen by
L/255. A fade has a step S and a hold H: each update while it runs, a held update (H > 0)
only counts H down; otherwise L += S, and it ends at L ≥ 255 (L = 255) or L ≤ 0 (L = 0).
Every start sets H = 4.

- fade out over n: L = 255, S = −255/n (integer division);
- fade in over n: L = 0, S = 255/n; over 0: L = 255 at once;
- 31 with `arg2 = −1`: L = 0 at once, S = −1 (it ends after the hold).

When a fade ends: a pending view (30) is shown, broadcast 26, and a fade in over 20 starts; a
pending scene (31) is requested and the scene changes on the next loop (E-0202), whose entry
pushes `(185, 33, 24)`: the new scene stays black for the hold, then fades in. L stays where
the fade left it, so a scene left black stays black until a fade in. Escape (opcode 60 to
every actor) is taken only while no fade runs and L ≠ 0; clicks are not blocked.

## The proximity gate (E-0705)

A trigger's sphere is the `x, y, z, r` after its polygon; a character's is its position
raised by its radius `[0x290]` (Characters.abi). Spheres overlap when the centre distance is
below the sum of the radii. With `+0x154 = 1` the gate passes for: bit 1 of `+0x188`, the
player's character (actor 3's, present in the scene, `+0x150` −1 or its id); bit 2, actor
4's character (`+0x14c` −1 or its id); bit 4, the characters of actors 91..94. With
`+0x170 = 1` each of them passes once per entry into the sphere. The engine has no moving
player character yet (Q-0202, Q-0403): a click stands in for walking there.

### Worked examples

- Scene_007 path trigger 660 (E-0111): `burningroots` 730 → 500, `roots_with_acid` 733 →
  500, `roots` 732 → 13, itself → 13, trigger 663 → 11: burn the roots and arm the next step.
- Scene_061 trigger 661 (a walk-in trigger of view 1, E-0112, E-0200): hide sprite 730 and
  deactivate itself now; the commands with `when = 10` wait for scene 10 (where exit 660
  leads) and act on scene 10's actors; those guarded by global flag 269 ("Snake Dead") are
  kept or dropped by its value at the moment 661 fires.

## Not covered here

Characters (type 0x03), items (type 5), sounds (0x18), the views' matrices (actor 602),
inventory, dialogue: their classes' opcodes belong to their own specs.
