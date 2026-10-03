# Items, the cursor and the inventory (engine behaviour)

How Grumpa carries and uses objects. Formats: `docs/formats/README.md` (`.abi`, `.atx`).
Evidence: E-0503, E-0504, E-0900, E-0901; command routing and conditions: `events.md` (E-0200, E-0201).

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

## Items in the world (E-0900)

An item lies in a scene when its State is 4 and its scene is the current one.

- **Drawn** (when visible; layer 3, with the mesh actors): its `IO_*.ANB` frame 0 with
  `IT_*.tga`, lit, textured and depth-tested like a 0x1a mesh (`scene.md`), placed by
  world = rotation (roll `rot.z` about Z, then pitch `rot.x` about X, then yaw `rot.y`
  about Y, Direct3D's yaw-pitch-roll) then translation to `position`.
- **Spinning** (when active): every 2 updates `rot.y` += 0.05 rad, wrapping at 2π.
- **Screen rectangle**: the bounding rectangle of the 8 projected corners of the mesh's
  bounding box under the same matrices, recomputed each draw; for hovering and clicking each
  dimension narrower than 40 px becomes centre ± 30 px.
- **Hovering** (when active, the panel hidden): the mouse in the rectangle and the player's
  character within 160 units of the item → the hotspot cursor, and the item says its name
  (`IS_*.wav`) once each time the mouse comes onto it.
- **Picking up** (a left click): a hovered item under the click with nothing on the cursor
  goes into the inventory (State 3; full: dropped beside Grumpa) and `Sounds\effect_item.wav`
  plays.
- **Placed** by op 71 `a` (at actor `a`, 30 units higher, turned as it) or dropped beside
  Grumpa (at the player's character, 20 higher, 30 units ahead on the walk mesh, else 30
  behind, else on the spot): State 4 in the current scene, shown, `effect_item.wav`, and a
  short glow: `Meshes\effect_item.ANB` with `Bitmaps\effect_item.tga` drawn over it (no z
  writes), one frame every 2 updates for 10 frames.

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

The panel tests a click in this order: the door button, the diskette button, the nine
slots, the shield slot, the weapon slot (E-0901). The buttons work only with the plain
cursor: the door sends `(1, 60)` (the main menu), the diskette `(1, 61)` (the saved games).

Adding an item (op 42, a pick-up, or the case above): an item already in a slot is not added
again; otherwise the first empty slot takes it (State 3). With all nine full, the "inventory
full" voice plays and the item drops beside Grumpa.

The two equipment slots (E-0901): with nothing on the cursor, the item in the slot goes on
the cursor, says its name, and Grumpa (actor 10) stops wearing it; with an item on the
cursor that fits the slot, the slot's old item goes back to the inventory, the held one goes
in (State 3) and Grumpa wears it; any other held item goes to the inventory. The weapon slot
(left) takes 100, 101, 110 and 113 (Father's Sword broken / whole, Sword of Might, Hammer;
attachments 4, 1, 3, 2), the shield slot (right) 138 and 134 (attachments 0 and 5). The
engine maps the door to its main menu and the diskette to ScummVM's save dialog.

## Persisted state

Items and the panel are global actors: their state (`active`, `visible`, State, scene,
position, rotation, latch; the panel's 9 flags + 9 ids and the 2 equipment slots) is saved
with the game (`save.md`).
