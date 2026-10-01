# The event system (engine behaviour)

How Grumpa runs scene logic — navigation, puzzles, interactions. Evidence: E-0109..E-0111.

## Model

- **Actors by id.** Every `.abi` record becomes an actor stored in a flat global table indexed
  by its record id (`DAT_004b9bc4[id]`, `FUN_0040d270`); the id is also written to `actor+0x108`.
  So a command targets an actor by a direct array index.
- **Command queue.** A global doubly linked list (`DAT_004b9b9c`, pending count `DAT_004b9ba0`)
  holds queued commands. A command is five ints: `(when, targetId, opcode, arg1, arg2)`.
- **Dispatcher** (`FUN_0040efa0`, run per tick): for each queued command whose `when` equals
  the factory's current time (`factory+0x130`), call the target's `DoCommand`
  (`actor->vtable[6](opcode, arg1, arg2)`); `targetId == -1` broadcasts to every actor. The
  command is then removed. `SaveSceneCommand`/`LoadSceneCommand` (`FUN_0040f4c0`/`FUN_0040f7b0`)
  persist the queue.
- **Triggers enqueue.** Each actor carries a `CC` command list (E-0109); a trigger (0x19) has a
  screen polygon (E-0108). Clicking inside the polygon enqueues that trigger's command
  templates (with `when = now`), which the dispatcher then routes to the targets.

## Opcodes (`DoCommand`, shared vocabulary; E-0111)

Each actor keeps an `active` flag (`+0x10c`, updated/animated) and a `visible` flag
(`+0x110`, drawn), plus a one-shot "latch" (`+0x210` sprite / `+0x184` trigger).

| opcode | effect |
|---:|---|
| 0 / 1 | play / stop |
| 2 / 3 | show / hide (`visible` = 1 / 0) |
| 11 / 12 | activate / deactivate (`active` = 1 / 0) |
| 13 | disable: `active=visible=0`, set latch (one-shot; ignores further commands until 52) |
| 52 | clear the latch (re-enable) — the only opcode honoured while latched |
| 86 | reset / init |
| 500 / 501 | full on (show+activate+play) / full off |

Trigger extras: 14/15 set/clear `+0x154`; 18 and 22 take an argument; 23 sets a global flag.

### Worked example (Scene_007 path trigger id 660)

Click enqueues: `burningroots`(730)→500, `roots_with_acid`(733)→500, `roots`(732)→13,
self(660)→13 (one-shot), trigger 663→11 — i.e. show the burning animation, hide the plain
roots, disable itself, arm the next trigger: the burn-the-roots puzzle step.

## Open (Q-0010)

The click→enqueue code path, actors' initial `active`/`visible` state at scene entry, scene
navigation (the go-to-scene opcode/class), and the remaining classes' opcodes (sound,
character, inventory, dialogue). These complete the playable loop.
