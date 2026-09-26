# Boot

From process start to the first interactive screen, and the program's top-level modes.
Addresses are in `/MISSION.EXE`; paths are relative to the data root (below). The 3D world
(scene loading, movement, the 3D main loop) and the renderer have their own specs; this
one only names their entry points.

## Data root and files (E-0401, E-0404)

- `HKLM\SOFTWARE\Cryo\Mission Sunlight`, subkey `Path`: value `Target` (the install
  directory, a `\` is appended) and value `CD` (the CD's root); subkey `Language`, DWORD
  `LOC`; subkey `Install Level`, DWORD `IL` (`Registry_Read` 0x418416). Any missing value is
  fatal ("Could not retrieve registry informations...").
- `Target` + `DATA\...` holds everything the 2D side loads (`DATA\SPRITES`, `GFX`,
  `MOVIES`, `SOUND`, `FONTS`, `GRAPHS_2D`) and `Target` + `SAVE\` the saves.
  `CD` + `DATA\SCENES_3D\` holds the 3D bundles. On a full install both are the same tree;
  an engine reads everything from the one `Data/` tree of the CD.
- `PEINTRE.INI` is not read: `ReadPeintreIni` 0x41ed13 has no caller, and the path it
  would fill (0x502880) stays empty, so that path is just `\DATA\` and `\DATA\SCENES\`.

## Sequence (E-0400)

1. **Registry and players** (`App_Init` 0x4180c0): read the registry; read
   `SAVE\USERS.BIN` (`save.md`); discard every player whose `GGAME<n>.BIN` is missing
   (`Users_CheckSessions`, `save.md` "Integrity check"). Fatal errors end the program.
2. **Player-name screen** (`ui.md` "Player-name screen"): a popup window covering the
   screen, class `WC_MS_ACCUEIL`, title "Mission Sunlight", icon `GAME_ICON`, drawn with
   the EXE's bitmap resources. It ends by posting message 0x502 with the player index
   (wParam) and 1 = known player / 0 = new player (lParam). Closing it ends the program.
3. For a new player, delete the player's `GGAME<n>.BIN` and `GAME<n><00..34>.BIN`
   (0x4187ba); then rewrite `USERS.BIN` (0x418966).
4. **DirectInput**: mouse (relative) and keyboard devices (`ui.md` "Input").
5. The same window becomes the game window: the Cryo memory manager gets 16 MB
   (0x470970), the window procedure is replaced by 0x42fbd6 (below), and
   `App3D_InitPaths` 0x42eb21 builds the paths, opens DirectDraw at 640×480×16, reads the
   surface's pixel format (0x472240: 1 = RGB555, else RGB565; E-0100 converts images for
   555), initialises the 2D shell (0x40fb60), DirectSound (`Snd_Init`, volume from the
   player record) and clears both pages to black.
6. **Resume state**: a known player's `GGAME<n>.BIN` is read (`Load3DGGame` 0x42f111,
   `save.md`); a new player starts with 35 zero object flags.
7. If the resume state is not "inside a 2D zone" (GGAME's first u32 = 0, or new player):
   show `GRAPHS_2D\loading.tga` full screen (`LoadTga2`) and start the 3D world
   (0x41fda9, world spec) behind it.
8. **Intro**: mode 2, movie `MOVIES\intro.hnm` full screen. A left click skips it.
9. When the movie ends or is skipped (mode 2 handler, 0x42fbd6):
   - resume inside a 2D zone (GGAME first u32 = 1): mode 1, `Entry2D` with the saved zone
     (`ui.md`);
   - otherwise: mode 0, start the 3D world again (0x41fda9), start the 3D timer
     (`Timer3D_Begin` 0x42fb5e): the player is in 3D.

After that the program only reacts to window messages (`GetMessage` loop in WinMain); every
frame is a timer message.

## Program modes (E-0405)

The byte at 0x598cb0 selects what the window procedure 0x42fbd6 does:

| Mode | Handler | Entered by |
|---|---|---|
| 0, 4 | 3D (0x42f988, world spec) | end of the intro, return from 2D |
| 1, 3 | 2D shell `MainWndProc` 0x4122bb, or, while 0x4b0058 is set, `Entry2D` from the 3D state (0x42f755) | 3D asks for a 2D zone; loading a game; credits; 3D option menu (mode 3) |
| 2 | movie: on each 0x500 poll the mouse; a left click or the end of the stream closes the movie, then the branch below | intro, end movies |

Messages: 0x500 = one tick of the active timer; 0x501/0x502 = movie frame / movie end in
the 2D shell (media spec); 0x503 = tick of the option menu opened from 3D; 0x504 = tick of
the credits. The 2D timer is a 40 ms multimedia timer (25 ticks per second) that posts
0x500, 0x503 or 0x504 unless the shell's busy flag (0x4e22fc) is set (0x41224c,
0x412271, 0x412296).

## End of the game (E-0405, E-0414, E-0418)

Leaving zone 21 (`games/mission-sunlight/docs/a14.md`) returns to 3D with zone 21, which
plays `MOVIES\cinefin.hnm` (mode 2), then `cinefin2.hnm`, then switches to mode 1 with the
credits timer (`Timer_Begin` 0x40fbe9: frame buffers, `Curseurs`, font `topaz8`). The
credits (`ui.md` "Credits") end with `PostQuitMessage`.
