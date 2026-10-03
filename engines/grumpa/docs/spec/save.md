# Game state, saving and loading (engine behaviour)

Evidence: E-0202, E-0203 (scene status), E-0501, E-0502.

## The original

The live game state is a folder, `Save\Current\`:

| file | content |
|---|---|
| `<nnn>_status.abi` | one per visited scene: `{u32 id, Serialize mode 4}` for each scene actor (id ≥ 600) |
| `global.abi` | the same for the global actors (ids < 600: items, characters, counters, flags, the inventory) |
| `remote.abi` | the command queue (`u32 count` + commands; empty = 4 zero bytes) |

Leaving a scene writes its status file; entering a scene reads it back if it exists, so a
revisited scene keeps its state (E-0202). Mode 4 keeps per actor `active`, `visible`, the
state slots and a few class fields (E-0203; items and the inventory E-0501).

- **New game:** empty `Current\`, reload the global actors from the data, load the start
  scene.
- **Save to slot n** (1..6): write `global.abi`, the current scene's status and the queue;
  copy `Current\*` to `Save\Player<n>\`; write `Player.sts` (player name, newline, current
  scene number) and `Player.tga` (a screenshot).
- **Load slot n:** empty `Current\`, copy `Save\Player<n>\*` into it, then enter the scene.

## The engine

ScummVM saves (`<target>.s##`, the metaengine's list, the launcher and the global menu),
not the original's folder: a save holds the same information as `Current\` after a save —
the global actors' state, every visited scene's actor states, the queue, the current scene
and view — plus ScummVM's header and thumbnail. The player name of `Player.sts` is the save
description. The panel's diskette and door buttons are not drawn as save/load (Q-0502):
ScummVM's menu (Ctrl+F5) and the launcher replace them.

Layout of the save stream (`Common::Serializer`, version 2, little-endian):

    u32 version, i32 current scene
    per item of Items.abi in file order:
        u8 active, u8 visible, u8 latch, i32 State, i32 scene, f32 pos[3], f32 rot[3]
    9 × i32 slot item id (−1 empty), 2 × i32 equipment item id, i32 held item,
    u8 panel shown, u8 panel locked
    the event VM's block (global actors, kept scene statuses, command lists; events.md)

Loading reloads the items from the data, applies the stream, and enters the saved scene.
