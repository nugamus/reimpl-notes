# Sound, voices and lip sync

What the engine needs to play U01's sound: the channel model of the EXE's sound manager
(`LSoundManager.cpp` / `LSound.cpp`), the two positional emitters, character talk with
lip sync from `Sound/<name>.bin`, and the clocks behind them. `s` is the scene scale
(U01: 40). All sound code is in `MissionMonet.exe`; the X3D DLLs have none.

## Output and files (E-0120, E-0127)

- One DirectSound device, priority level, primary buffer **22,050 Hz, 8-bit, mono**.
  Every sound is mixed down to that, so the original never pans and never plays above
  22 kHz / 8 bit.
- Every file is PCM WAV, mono. Corpus: 244 files: 235 at 22,050 Hz 8-bit, 7 at
  44,100 Hz 16-bit (all in `U01/Sound`: `s1_03`, `s1_08b`, `s1_10`..`s1_13`, `u01`),
  1 at 22,050 Hz 16-bit (`U03/Sound/s2_03`), 1 at 11,025 Hz 8-bit (`U07/Sound/Couper`).
  76 carry a `LIST` chunk after `data` (ignore it).
- Paths: `<data root>/Uxx/Sound/<name>.WAV`, or `<data root>/Uxx/Sound/<name>` when the
  lower-cased name contains `.wav`. A missing file is skipped (the original logs it).
  The landing sound is `<data root>/SAUT.WAV`; video soundtracks are `Video/<name>.wav`
  (`boot.md`).

**Engine:** play the files at their own rate and depth; downmixing to 22 kHz 8-bit is not
reproduced.

## Groups and volume (E-0120, E-0121)

Every playing sound belongs to one of groups 1..6. A group has a volume G (0..100) and each
sound its own volume v (0..100). The sound plays at

    attenuation (dB) = (v · G − 10000) / 100          (0 dB = full, −100 dB = silent)

i.e. gain = 10^((v·G − 10000) / 2000). G starts at 100 for every group. Every app mode change (`boot.md`) to mode 0, 1 or 3
sets G₁ = 85, G₄ = 80, G₅ = 80; a change to mode 2 (2D frame over the scene) sets G₁ = G₄ = G₅ = 0 (silent). G₂ and G₃ are never changed, so
voice and effects keep playing under a frame. Changing G re-applies it to that group's
sounds at once.

| Group | Use in U01 | Start rule |
|---:|---|---|
| 1 | Ambient / music: step op 12, the unit's own loop `u01.wav` | op 12 starts another sound; nothing stops the group except the unit |
| 2 | Voice: the voice emitter (op 1, character talk), op 101, video soundtracks | the emitter and op 101 stop the whole group first |
| 3 | Effects: the effects emitter (op 13, `SAUT.WAV`, U01's door/phone/drawer/train sounds) | the emitter stops the whole group first |
| 4, 5 | not used by U01 (U03's code plays on 4) | |

A sound has: loop flag, volume v, group. **Looping** sounds restart from the start of the
data seamlessly and never end by themselves. A one-shot plays once and is then removed.

| Who plays | Group | v | Loop |
|---|---:|---:|---|
| Step op 12 `arg` | 1 | 85 | yes |
| Unit ambient (U01: `U01` → `Sound/U01.WAV`, after the prologue and after a save load) | 1 | 85 | yes |
| Step op 101 `arg` | 2 | 100 | no |
| Voice emitter (op 1, talk) | 2 | by distance | no |
| Effects emitter (op 13, `SAUT.WAV`) | 3 | by distance | caller (op 13: no) |
| Video soundtrack (stops **all** sounds first) | 2 | 100 | no |

So op 12 in U01's mode 0 plays at v·G = 85·85: −27.75 dB. (Op 12 is not in the corpus's
action tables; the unit ambient goes the same way.)

## Emitters: positional sound (E-0122)

The scene owns two emitters, created at scene load:

| Emitter | Group | Range D |
|---|---:|---|
| voice | 2 | 50 · s (U01: 2000) |
| effects | 3 | 60 · s (U01: 2400) |

**Play(file, position P, loop):** if the emitter's group is playing (below) and the file
name equals the emitter's last one (case-insensitive), do nothing and report "not
started". Otherwise store P, stop every sound of the group, start the file (v = 100),
remember its name, and set its volume from the distance.

**Volume from distance:** d = |P − eye| (the camera position, Euclidean, world units):

    v = trunc(100 · (D − d) / D)   for d < D,   else 0;   clamped to 0..100

Linear in v, so linear in dB: at the emitter 0 dB, at D/2 −50 dB, at D silent. There is no
panning (all pan values stay centred, and the output is mono anyway). P is fixed when the
sound starts; it does not follow a moving object.

**When the volume is recomputed:** at start, and after every camera movement step: each
walk step (Up/Down key frame, `movement.md`), each frame of a scripted `MoveTo`/`LookAt`
and of a camera path. Turning in place does not recompute (no pan, distance unchanged).
Only emitters whose group is playing and that still own a sound are updated. Op 101
detaches the voice emitter from the sound it plays, so op 101's sound keeps v = 100.

Positions used:
- op 1 on a non-character, op 13: the hotspot object's global position at click time;
- character talk: the global position of the character's face object (below);
- `SAUT.WAV`: the eye.

## "Playing" and the wait condition (E-0123)

A group **is playing** when it holds a sound that has not hit the end of its data. That is
the wait condition of scripted sequences ("wait while the voice plays" = group 2 playing,
`movement.md`'s U01 hand-over) and what ends a character's talk.

The original decides it differently for short and long sounds, and the difference is
audible in timing:

- A sound whose data is smaller than the 166,666-byte streaming buffer (1,000,000 / 6,
  rounded down to whole samples; 7.56 s at 22 kHz 8-bit, 1.89 s at 44.1 kHz 16-bit) is
  loaded whole. A one-shot stays "playing"
  until the sound thread (every 500 ms) sees DirectSound report it stopped and removes it:
  0..500 ms after the audible end.
- A longer sound streams through two halves of that buffer, refilled by the same 500 ms
  thread. Its end flag is set by the first refill that finds no data left, which happens as
  playback enters the half holding the last data: "playing" ends **up to one half buffer
  (83,333 bytes of the file's data: 3.78 s at 22 kHz 8-bit, 0.94 s at 44.1 kHz 16-bit)
  before the audible end**. The tail still plays out. In U01 this applies to `d1_01`
  (23.4 s), `d1_02`, `d1_03`, `d1_04`, `d1_08`, `d1_10`, `Marsaillaise`, `s1_03`, `s1_10`,
  `s1_11`, `s1_12`, `s1_13` and `u01`.

**Engine:** model "playing" as "audio still sounding" with a per-sound early-end offset:
0 for sounds ≤ 166,666 bytes of data, else the position where the last partial half begins.
The simpler "sound still audible" is acceptable if traces show the early end does not
matter (Q-0071).

## Character talk and lip sync (E-0124, E-0125)

### Talkers

A unit declares its speaking characters in its start hook (`U01_Start`): character
`U01_01` with face object `$$$DUMMY.*01SParle`, and `U01_02` with `$$$DUMMY.*02SParle`.
A talker is a type-6 hotspot bound to the character's animation node. For each talker,
from `<data root>/Uxx/Anim/<character>/`, load these clips into mouth slots:

| Slot | File | Slot | File |
|---:|---|---:|---|
| 1 | `Yeux.A3D` | 5 | `E.A3D` |
| 2 | `Ch.A3D` | 6 | `F.A3D` |
| 3 | `Ch_yeux.A3D` | 7 | `O.A3D` |
| 4 | `B.A3D` | 8 | `A.A3D` |

Each clip is a whole-body `.A3D` (frames 0..1); only the sub-animation named after the face
object is used. It becomes an animation node bound to the face object (so it poses the
face dummy and, by `animation.md`'s recursive Animate, the mouth, cheeks, brows and eyes
under it), at 15 fps, looping, **disabled** (not ticked) and paused. Missing files leave
their slot empty; empty slots 1..8 and slot 0 then point to the lowest-numbered loaded
clip. These nodes are added to the scene's node list after the character's own nodes, so
when enabled they override the body animation's pose of the face subtree (inferred from the
list order, Q-0072).

### Say(character, name)

Step op 1 whose target is a type-6 hotspot, and unit code (U01: `U01_01` says `d1_01` at
the hand-over), call Say:

1. If another talker is talking, stop it (below).
2. Play `Sound/<name>` on the voice emitter at the face object's global position. If the
   emitter did not start it (same file still playing), stop here.
3. This talker becomes the scene's current talker. If `Sound/<name>.bin` exists, load its
   lip table (`docs/formats/lip.ksy`) and use lip mode; else random mode.
4. Talk start time T₀ = now (ms). Talking = on.

If the target names no talker, the voice plays on the voice emitter at the eye instead
(no lip sync).

### Per frame (the animation tick, before rendering)

For the current talker only:

- If the voice group is not playing: **stop** (all 9 slot nodes disabled, lip table freed,
  talking off, no current talker). The face returns to the body animation's pose.
- **Lip mode**, t = now − T₀ (ms). Look up the shape: the last record with time ≤ t
  (records before the first: shape 1). If t ≥ every record's time, **stop** as above
  even if the voice is still playing. Then, with L = the time of the last mouth change
  (reset to 0 by shape 1):
  - shape 1 (closed): if a slot is selected, disable it and pause it, deselect, and put
    slot 8 (`A`) enabled, paused at frame 0.
  - shape 2 or 3: if t − L ≥ 200, select that slot, L = t.
  - shape 4..8: if t − L ≥ 200: L = t; r = 4 + ⌊rand · 4 / 32767⌋; if r is the selected
    slot, draw r = 1 + ⌊rand · 4 / 32767⌋ until it is not; select r; set r's fps to
    ⌊rand · 2 / 32767⌋ + 1.
- **Random mode** (no `.bin`), every 200 ms of wall clock: r = 1 + ⌊rand · 9 / 32767⌋;
  r = 9: disable and pause the selected slot (it stays selected); else select r. Then set
  the selected slot's fps to ⌊rand · 4 / 32767⌋ (0 freezes it).

`rand` is 0..32767 (MSVC `rand`). **Select n** (n ≠ current): disable the current slot,
enable n and set it running (not paused). The clips loop over frames 0..1 at their fps,
so the mouth flaps between frame 0 (rest) and frame 1 (the shape).

So the data's shapes 4..8 all mean "open": the original picks among `B`/`E`/`F`/`O`
(rarely `A`) at random, and only 1 (closed), 2 (`Ch`) and 3 (`Ch_yeux`) are used as given.

### Lip data vs. voice length (E-0126)

81 `.bin` files, all with a `.wav` of the same name. In 28 the last record lies past the
end of the `.wav` (up to 8.6 s, `U05_06`); in the others it ends early. The records are
~46 ms apart (min 44, median 46). Talk ends at the earlier of "voice group not playing"
and "past the last record", so the mouth can stop before the voice (Q-0070).

## U01 inventory (E-0127)

`Data/U01/Sound`: 23 `.wav`, 8 `.BIN` (lip data for `d1_02`..`d1_09`).

| Sound | Played by | Channel |
|---|---|---|
| `u01` (24.5 s, 44.1 kHz 16-bit) | U01 start, after the prologue / on save load | group 1, looping |
| `d1_01` | U01 hand-over, `U01_01` says it (no `.bin`: random mouth) | voice |
| `d1_02`, `D1_03`, `D1_06`..`D1_10` | step op 1 of actions M01..M22 on `U01_01`/`U01_02` | voice (talk) |
| `Marsaillaise`, `s1_03`, `s1_07`, `s1_08b` | step op 13 | effects |
| `OpenDoor`, `CloseDoor`, `TelGrisi`, `s1_05`, `s1_13`, `S1_10` | U01's action handlers (`interaction.md`) | effects |
| `s1_11` | U01 code, at a position | voice emitter |
| `s1_12` | the train departure (below) | effects, looping |
| `d1_04`, `d1_05`, `telgrisi2` | U01 code paths not traced here (Q-0073) | |

**Train departure** (`0x00401b90`, when the `Train2` clip of `Anim/U01_20A.A3D` reaches
its last frame): play `s1_12` looping on the effects emitter at the eye, stop group 1 (the
ambient), then fade: for d = 10, 20, … while d < 60 · s: set the emitter's distance to d,
`RunFor(20)`. In U01 that is 240 steps, about 4.8 s from full to silent; then it calls
the app object (`0x0046ec18` vtable `+4`, argument 2; not traced here).

## Timing (E-0123, E-0125)

| What | Clock | Rate |
|---|---|---|
| Lip sync, random mouth | `timeGetTime` ms since talk start / absolute | every animation tick (each frame and each `RunFor`/`MoveTo` step); changes at most every 200 ms |
| Mouth clip playback | the node tick: seconds between presents × fps | per frame (`animation.md`) |
| Stream refill, end detection, one-shot removal | multimedia timer thread | every 500 ms |
| Emitter volume | none: event-driven by camera movement | per camera step |

**Engine model:** in the fixed logic tick, t = logic time since the talk started (ms);
apply the lip rules each tick. Recompute emitter volumes each tick the camera moved (or
simply every tick; distance is unchanged otherwise). Use the mixer's own end-of-stream
for "playing", adjusted per the rule above. Seed an engine RNG for `rand`; exact MSVC
sequences are not needed (the draws depend on frame timing in the original anyway).
