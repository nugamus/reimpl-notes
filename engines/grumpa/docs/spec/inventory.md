# Items, the cursor and the inventory (engine behaviour)

How Grumpa carries and uses objects. Formats: `docs/formats/README.md` (`.abi`, `.atx`).
Evidence: E-0503, E-0504; command routing and conditions: `events.md` (E-0200, E-0201).

## Items (E-0503)

The 66 items are global actors, ids 100..179, loaded once per game from `Actors/Items.abi`
(type 5, CFXItem). Each item has:

| field | meaning |
|---|---|
| `State` (state slot 0) | 1 gone, 3 in the inventory, 4 lying in a scene, 6 on the cursor |
| scene | the scene it lies in when State is 4 (−1 none) |
| position, rotation | where it lies (world space, drawn with the view camera) |
| `IO_<name>.ANB`, `IT_<name>.tga` | its 3D mesh and texture in the world |
| `IC_<name>.tga` | its 32×32 inventory icon (`Bitmaps/`) |
| `IS_<name>.wav` | its spoken name |
| latch | set by 13; while set only 52 is obeyed |

An item lying in the current scene (State 4) is drawn as a 3D actor. Clicking inside its
screen rectangle (widened to 60 px if narrower than 40) with nothing on the cursor adds it
to the inventory and plays the pick-up sound.

Commands to an item (`DoCommand`):

| op | effect |
|---:|---|
| 0 / 1 | play / stop its spoken name |
| 13 | disable: off the cursor, State 1, scene −1, latch |
| 16 `s` | State = `s`; unless `s` is 6, take it off the cursor if it is there |
| 23 `n` | the current scene is `n` (broadcast on scene entry) |
| 42 | add to the inventory (State 3); full → drop beside Grumpa (State 4) |
| 43 | reload its mesh |
| 52 | clear the latch |
| 54 `n` | put it in scene `n` (State 4) |
| 71 `a` | put it where actor `a` stands (State 4) |
| 86 | load if it lies in the current scene, else unload |

Adding 174 (Water Drop) sends `(8, 50, 100)` and adding 177..179 (the coins) sends
`(8, 9, 1)` to actor 8, and the item goes to State 1: these are counted, not carried.

## The cursor (actor 2)

The cursor holds at most one item id (−1 none). Taking an item onto the cursor sets its
State to 6 and draws its icon as the cursor; putting it back clears it.

**Using an item** is not a separate mechanism: a hotspot's commands carry conditions
`(item, 0, 6, mode, link)` — "item's State == 6", i.e. the player is holding it — so a
left click on the hotspot while holding the right item runs the guarded commands (E-0201,
209 such conditions in the corpus). Those commands then consume it (16 → 1), swap it
(42 to another item) or keep it. Help.txt: clicking where nothing reacts drops the held
item beside Grumpa (needs a player character; Q-0202).

## The inventory panel (actor 90, E-0504)

From the first block of `UI/090_Inventory/090_Inventory.atx`: hidden and inactive at start,
at (480, 170); panel `Inventory.jpg` (307×139); slot frame `InventorySlot_####.jpg` (96×96,
frame 0 empty, 1 filled); voice `InventoryIsFull_VS.wav`.

Layout from the panel's top-left (x, y) and its size (W, H):

| element | rectangle |
|---|---|
| weapon slot (left of Grumpa) | x, y, 96×96 |
| shield slot (right of Grumpa) | x+210, y, 96×96 |
| slot i (0..8), row r = i/3, column c = i%3 | x + (W−258)/2 + 86c, y + H + 86r, 86×86 |
| button "saved games" (diskette) | x+70..x+100, y+96..y+132 |
| button "main menu" (door) | x+200..x+232, y+96..y+132 |

Drawing (when shown): the panel at (x, y); for each slot the slot frame at its occupied flag
at the slot's top-left, then the item icon at slot + (32, 32); then the equipment slots'
icons at slot + (32, 32).

Commands: 19 toggles shown/hidden (and active), ignored while Ctrl is down or while
locked; 12 locks (and hides), 11 unlocks; 2 / 3 show / hide. A right click sends 19
(Help.txt: "right click shows the inventory").

A left click on a slot:

- nothing on the cursor, an item in the slot → the item goes on the cursor (State 6, its
  name is spoken); the slot empties;
- an item on the cursor, the slot empty → the item goes in that slot (State 3);
- an item on the cursor and in the slot → the held item goes to the first free slot.

Adding an item (op 42, a pick-up, or the case above): an item already in a slot is not added
again; otherwise the first empty slot takes it (State 3). With all nine full, the "inventory
full" voice plays and the item drops beside Grumpa.

The shield slot takes only 134 (Shield) and 138 (Shield of Protection) and tells actor 10 to
wear it. The weapon slot and the two buttons are Q-0502; the engine leaves both buttons to
ScummVM's own save/load and menu.

## Persisted state

Items and the panel are global actors: their state (`active`, `visible`, State, scene,
position, rotation, latch; the panel's 9 flags + 9 ids and the 2 equipment slots) is saved
with the game (`save.md`).
