# Dialogue: voice lines (engine behaviour)

Grumpa has no dialogue screens, choices or subtitles. Characters talk through voice lines:
`CFXSound` actors (types 0x18 and 0x2a) in the scene files, started by commands and chained by
the commands they run when they end. Evidence: E-0405. Open: Q-0400, Q-0401.

## The sound actor

After the common header (`id, active, visible, n × u32`, E-0400) a sound record holds:

| field | meaning |
|---|---|
| volume flag, volume | if the flag is 1, the volume in hundredths of a dB (0 = full, −10000 = silent) |
| pan flag, pan | if the flag is 1, the pan in hundredths of a dB (−10000 left .. 10000 right) |
| frequency flag, frequency | if the flag is 1, the playback rate in Hz |
| loop | 1 = loop until stopped |
| playing | 1 = playing when saved |
| on entry | 1 = start when the scene is entered |
| speaker | the id of the character who says the line; 0 = not speech |
| name | the `.wav` file |
| commands | a CC list run when the sound ends (`events.md`) |

## Files

The original opens `<data>\Sounds\<name>`. The disc's cabinet splits that folder into
`Sounds_` (language-independent effects and music) and `Sounds_<language>` (the voices); a name
in both is the language's voice (Q-0400). The engine looks in `Sounds_<language>` first, then
`Sounds_`. Names with non-ASCII letters (`Släpp_Lås_mig_SV.wav`) were extracted with `_` in
their place (`Sl_pp_L_s_mig_SV.wav`); the engine tries that spelling too.

## Commands

| opcode | effect |
|---:|---|
| 0, 500 | play (`active = 1`) |
| 1, 501 | stop and run the command list (501 also `active = 0`) |
| 0xb / 0xc | `active = 1 / 0` |
| 0xd | stop without running the command list, `active = visible = 0`, latched (one-shot) |
| 0x17 | scene entry: play if `on entry` is set |

Playing marks the speaker as talking (Q-0401) until the sound stops. A sound that is not
looping stops by itself at its end; **stopping runs the sound's command list**, which is how a
conversation goes on: the end of one line starts the next (or opens a door, moves a character).

## Messages

A character's message list (`characters.md`) would be shown as a fading caption by opcode
0x44 (through the scene manager, 185). Every list is empty in this edition: there is no
on-screen text besides the menus, help and credits (`Local_<language>`).
