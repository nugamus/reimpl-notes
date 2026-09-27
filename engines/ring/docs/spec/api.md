# The game API (Ring, DVD edition)

The zone code declares its world through a fixed set of `aApplication` methods, called
with constant arguments (`engines/ring/notes/calls/*_setup.jsonl`, extracted by
`tools/ghidra/scripts/ring_calls.py`). This file says what each call builds. Evidence:
E-0031. Addresses are `RING_DVD.EXE`; names in `aApplication::` come from the error
strings (E-0013) or, for the unnamed wrappers, from the method they delegate to (E-0031).
Argument types: `int` 32-bit, `u8` a byte pushed as a dword, `f32` a float's bits pushed
as a dword (e.g. 0x41480000 = 12.5), `str` a pointer to a constant string.

Ids are integers chosen by the game (e.g. 80001); each kind (object, puzzle, rotation,
sound, variable) has its own list and a second declaration with the same id is refused
("ID already exists").

## Model

- **Puzzle** (`aPuzzle`, ctor 0x41b740): a fixed 640×448 screen. Fields: id, background
  image, and lists of movabilities (+8), accessibilities (+0xc), presentation images
  (+0x10), presentation animations (+0x14), texts (+0x18), ambient sounds (+0x1c), 3D sounds
  (+0x20); +0x24 = 1, +0x28, +0x29 = 0 at creation.
- **Rotation** (`aRotation`, ctor 0x41da10): a panorama node (`.aqc`, formats README) with
  lists of movabilities, accessibilities, sounds and `layers` animation layers (+0x1c,
  one 0x69-byte layer per section of the `.aqc`).
- **Object** (`aObject`, ctor 0x41f940): id, name, icon name, a flag byte; a list of
  accessibilities (+0xd) and of presentations (+0x11); four cursor definitions (passive
  +0x15, active +0x32, passive-drag +0x4f, active-drag +0x6c, each ending in a load-from
  byte initialised to `'e'`).
- **Accessibility** (`aAccesibility`, 8 bytes): its object and a hot spot. Lives in the
  puzzle's or rotation's accessibility list and in the object's.
- **Movability** (`aMovability`, 0x35 bytes): a hot spot that moves the player. Fields:
  +4 owner, +0xc target id, +0x10 "ride name" (a video, `str`), +0x14 kind (0 rotation →
  rotation, 1 rotation → puzzle, 2 puzzle → rotation, 3 puzzle → puzzle), +0x18..+0x31 the
  transition (below).
- **Hot spot** (0x21 bytes, ctor 0x423770): rectangle x1, y1, x2, y2 (int), enabled
  (u8), kind (1 accessibility, 2 movability), cursor id, `unk_19` (int), +0x1d key
  (initialised -1; `ObjSetPuzAccKey` sets it).
- **Transition** of a movability (0x423730, 8 values at +0x18): `f32 alpha1, f32 beta1,
  f32 ran1, int unk_24, u8 kind, f32 alpha2, f32 beta2, f32 ran2`; the constructor sets
  `0, 0, 85.0, 0, 2, 0, 0, 85.0`.

Rotation angles, "ran" and the transition kind byte are specified with the renderer
(`spec/rotation.md`); sounds, ambient and 3D sounds in `spec/sound.md`.

## Declarations

| Call | Address | Arguments | Builds |
|---|---|---|---|
| `SetZone` | 0x402210 | u8 zone | current zone (folder string at app+0x6b, id at app+0x6e); zones 1 and 7 call 0x417cf0 on app+0x8d, others 0x417cc0 |
| `AddPuz` | 0x404240 | int id | a puzzle (0x2d bytes) |
| `PuzAddBgrImg` | 0x4043c0 | int puzzle, str file, int x, int y, u8 unk_active | the background image (`aPuzzle::SetBgrImg` 0x41bce0; loaded from the zone's archive or disk per `GetreadFrom`) |
| `AddRot` | 0x404dc0 | int id, str name, u8 unk_3, int layers | a rotation whose node file is `<zone>\NODE\<name>.aqc` (formats README) |
| `SetComBufLen` | 0x405fc0 | int rotation, int bytes | the rotation's decompression buffer size |
| `AddObj` | 0x402900 | int id, str name, str icon, u8 unk_flag | an object; name and icon come from `aObj.ini` by id when present (0x402c00, 0x402c20), else from the arguments |
| `ObjAddPuzAcc` | 0x402c40 | int object, int puzzle, int x1, y1, x2, y2, u8 enabled, int cursor, int unk_9 | an accessibility of the object on the puzzle |
| `ObjAddRotAcc` | 0x402da0 | int object, int rotation, int x1, y1, x2, y2, u8 enabled, int cursor, int unk_9 | the same on a rotation, in tenths of a degree (x 0..3600, y negative above the horizon; `spec/rotation.md`) |
| `ObjSetPuzAccKey` | 0x402d60 | int object, int index, int key | the key of the object's index-th accessibility (0x423940) |
| `ObjSetAccOff` | 0x403090 | int object, int from, int to | `ObjSetAccOnOrOff(object, 0, from, to)`: disables accessibilities from..to |
| `ObjAddPre` | 0x4032f0 | int object | appends a presentation to the object |
| `ObjPreAddImgToPuz` | 0x403370 | int object, int presentation, int puzzle, str file, int x, int y, u8 active, u8 draw_type, int priority | an image of the presentation on the puzzle (`aObject::addObjectImageToPuz` 0x4205d0 → 0x42d320; `spec/drawing.md`) |
| `ObjPreAddAniToPuz` | 0x403460 | int object, int presentation, int puzzle, str name, int unk_5, int unk_6, int unk_7, u8 unk_8, int unk_9, int unk_10, f32 unk_11, u8 unk_12 | an animation on the puzzle (`aObject::addAnimationToPuz` 0x420650 → `aAnimationImage::Init` 0x4219f0); bit 2 of unk_12 clear = the animation starts stopped (0x42e480). Observed: unk_10 13..25, unk_11 12.5 |
| `ObjPreAddImgToRot` | 0x403560 | int object, int presentation, int rotation, int layer | the rotation layer's image as a presentation (`aObject::addImageToRot` 0x4206e0; layer < the rotation's layer count) |
| `ObjPreAddAniToRot` | 0x403660 | int object, int presentation, int rotation, int layer, int unk_5, f32 unk_6, u8 unk_7 | the layer as an animation (`aObject::addAnimationToRot` 0x420750); layer < the rotation's layer count |
| `ObjPreSetAniIdeOnPuz` / `…OnRot` | 0x4038d0 / 0x403920 | int object, int presentation, int unk_3, int unk_4 | `aObject::ObjPreSetAniIdeOnPuz`/`OnRot` (0x420eb0 / 0x420f20); unk_4 is an id of the same range as puzzles/rotations |
| `ObjPreAniSetStaFra` | 0x403970 | int object, int presentation, int frame | start frame |
| `ObjPreSetAniCooOnPuz` | 0x4039f0 | int object, int presentation, int x, int y | animation position |
| `ObjPrePauAni` | 0x403a40 | int object, int presentation | pauses the animation |
| `ObjPreAddTxtToPuz` | 0x403b10 | int object, int presentation, int puzzle, str text, then 9 arguments passed to `aText::Init` | a text on the puzzle (`aObjectPresentation::ObjPreAddTxtToPuz` 0x42f270) |
| `ObjPreSetTxtToPuz` | 0x403ba0 | int object, int presentation, int index, str text | sets the presentation's `index`-th text (`spec/text.md`) |
| `ObjPreSetTxtCooToPuz` | 0x403bf0 | int object, int presentation, int index, int x, int y | moves it |
| `ObjPreSho` | 0x403c80 / 0x403e00 | int object, int presentation / int object | shows one presentation / all of them (`aObject::ShowPresentation`) |
| `ObjPreHid` | 0x403d00 / 0x403e80 | the same | hides one / all (`aObject::HidePresentation`) |
| `ObjPreHidDeaPuz` | 0x403d80 / 0x403f00 | the same | hides one / all and frees their pictures (`aObjectPresentation::HideWithDeallocPuzzle`) |
| `ObjSetPasCur`, `ObjSetActCur`, `ObjSetPasDraCur`, `ObjSetActDraCur` | 0x403f80, 0x404030, 0x4040e0, 0x404190 | int object, then 7 dwords unk_2..unk_8 | the object's cursors, stored verbatim at +0x15/+0x32/+0x4f/+0x6c (0x420b70 …) with the load-from byte from `ART_BAG`. Observed: `22, 22, 20, 4, 12.5, 4, 4` (active), `22, 22, 0, 3, 0, 0, 3` (passive) |
| `ObjAddBagAni` | 0x402ed0 | int object, int unk_2, u8 unk_3, int unk_4, f32 unk_5, u8 unk_6 | the object's inventory animation (`aAnimationImage::Init` with the object's icon name 0x426cb0, from the bag archive per `ART_BAG`) |
| `PuzAddMovToRot` | 0x404450 | int puzzle, int rotation, str ride, int x1, y1, x2, y2, u8 enabled, int cursor, int unk_10 | a movability of kind 2 |
| `PuzAddMovToPuz` | 0x4046c0 | int puzzle, int puzzle, str ride, x1, y1, x2, y2, u8 enabled, int cursor, int unk_10 | kind 3 |
| `RotAddMovToRot` | 0x4050f0 | int rotation, int rotation, str ride, x1, y1, x2, y2, u8 enabled, int cursor, int unk_10 | kind 0 |
| `RotAddMovToPuz` | 0x405360 | int rotation, int puzzle, str ride, x1, y1, x2, y2, u8 enabled, int cursor, int unk_10 | kind 1 |
| `PuzSetMovToRot` | 0x4045c0 | int puzzle, int index, f32 alpha, f32 beta, f32 ran | transition `0, 0, 85.0, 0, 2, alpha, beta, ran` |
| `RotSetMovToPuz` | 0x4054b0 | int rotation, int index, f32 alpha, f32 beta, f32 ran, int unk_24, u8 kind | transition `alpha, beta, ran, unk_24, kind, 0, 0, 85.0` |
| `RotSetMovToRot` | 0x405250 | int rotation, int index, f32 alpha1, f32 beta1, f32 ran1, int unk_24, u8 kind, f32 alpha2, f32 beta2, f32 ran2 | the whole transition |
| `RotSetMovOff` | 0x405850 | int rotation, int from, int to | `RotSetMovOnOrOff(rotation, 0, from, to)` |
| `RotSetJugOn` | 0x405c70 | int rotation, f32 unk_2, f32 unk_3 | `RotSetJugOn` (the renderer's spec) |
| `SouAdd` | 0x406970 (4 arguments), 0x406ba0 (6) | int id, int type, str file, … | a sound in the global sound list (0x4683c0; when the 5th argument ≠ 1 the sound object is the larger class with an event, vtable 0x47e86c, else vtable 0x47e844) |
| `PuzAddAmbSou` / `RotAddAmbSou` | 0x404b00 / 0x405d50 | int owner, int sound, int volume, int pan, int same_mode, int leave_mode, int fade | an ambient sound of the puzzle/rotation (`aSoundItem::Init` 0x41a150: fade > 1 required, stored as fade − 1; the sound must be of the ambient-music type) |
| `PuzAdd3DSou` / `RotAdd3DSou` | 0x404c30 / 0x405e80 | int owner, int sound, int same_mode, int leave_mode, int fade, int volume, f32 angle, int amplitude | a 3D sound (`aRotation::Add3DSound` / `aPuzzle::Add3DSound`; the sound must be of the ambient-effect type) |
| `PuzSetAmbSouOff`, `PuzSet3DSouOff`, `RotSetAmbSouOff`, `RotSet3DSouOff` | 0x404be0, 0x404d20, 0x405e30, 0x405f70 | int owner, int sound | switches a sound off |
| `SouSet_406e20` | 0x406e20 | int sound, int volume | the sound's own volume (`spec/sound.md`) |
| `VarDefByte`, `VarDefWord`, `VarDefDwrd`, `VarDefFloa`, `VarDefStrg` | 0x406080, 0x406100, 0x406180, 0x406200, 0x406280 | int id, value | a game variable (`aVar`, app+0x95) with its initial value |
| `VarSetByte` | 0x4060b0 | int id, u8 value | sets a byte variable |
| `VisAddLisToPuz` | 0x406f90 | int id, int puzzle, … (57 arguments) | the inventory list widget of a puzzle (SY zone) |
| `VisAddShoToPuz` | 0x4074f0 | int id, int puzzle, … (10) | a "show" widget of a puzzle |

The wrappers look the owner up by id in the app's lists (objects app+0x79, puzzles
app+0x7d, rotations app+0x85) and report an error when it is missing. The remaining `u8`
and `unk_*` arguments are stored but not yet traced to their use; they stay opaque until
the code that reads them is specified.
