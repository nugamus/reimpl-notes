# Evidence (CryOmni3D engine)

Append-only proof for every claim in this engine's specs (rule 1). Never edit an entry;
supersede it with a new one that names the old id.

Entry format:

```
### E-0001 — <one-line claim> (YYYY-MM-DD)
- **Source:** Ghidra `<program>!0x<address>` (`<name>`), an assert path, a trace line
  (`traces/INDEX.md` entry), or a corpus statistic (the script and its output).
- **Shows:** what that source says, in words (never pasted decompiler output, rule 3).
- **Used by:** the spec or format sections that rely on it.
```

Numbering: E-0001.. survey and binaries, E-0100.. the first format area, and so on in blocks
of 100 per area, so related entries stay together.

### E-0001 — upstream `cryomni3d` is built to take more games, one subengine each (2026-10-07)
- **Source:** ScummVM upstream master `da05d83f`, `engines/cryomni3d/`: `configure.engine`
  (`add_engine cryomni3d "Cryo Omni3D games" yes "versailles" "" "highres hnm"` and
  `add_engine versailles "Versailles 1685" yes`), `detection.h` (enum `CryOmni3DGameType`:
  `GType_VERSAILLES`, `GType_HNM_PLAYER`), `metaengine.cpp` (switch on the game type),
  `module.mk` (`ifdef ENABLE_VERSAILLES` adds `versailles/*.o`). 16,744 lines of `.cpp`.
- **Shows:** shared code at the top level (`omni3d`, `wam_parser`, `datstream`,
  `fixed_image`, `mouse_boxes`, `objects`, `sprites`, `font_manager`, `dialogs_manager`,
  `image/hlz`, `image/hnm`); per-game code in a subengine folder chosen by game type.
  A plain `--disable-all-engines --enable-engine=cryomni3d` leaves the subengine out; our
  build scripts now enable an engine's subengines from its `configure.engine`.
- **Used by:** CLAUDE.md Ground truth (engine structure).

### E-0002 — what the two WIP forks the wiki links contain (2026-10-07)
- **Source:** `reference/templier-scummvm-cryo` (github.com/Templier/scummvm, branch `cryo`,
  last commit 2013-11-27); `reference/elyosh-scummvm-cryo` (github.com/elyosh/scummvm-cryo).
- **Shows:** Templier's `engines/cryo/` is 3,106 lines: `data/graphics/{font,hnm,jp6,sprite,
  spw}`, `data/logic/{scenario,wam}`, `data/resource/bigfile`, `data/sound/{apc,spp,synchro,
  zik}`, `game/china/`, `game/{screen,warp}`; most files are class shells of about 30 lines,
  the largest parts are `hnm.cpp` (250) and `bigfile.cpp` (134). Its detection names 13
  games and has entries for three: Atlantis (GOG: `Atlantis.exe` md5 `f54b69b5…` 714,240 B
  and `BIGCD1..4.BIG`), China (`CHINE.EXE` `8850a946…` 573,952 B, `CD.HNM`), Egypt
  (`EGYPTE.EXE` `cce60d74…` 375,808 B). elyosh's engine is Dune only (`hsq`, `sentences`,
  `sprite`, `music`), not Omni3D.
- **Used by:** CLAUDE.md Ground truth (references). Format names are leads, not facts.

### E-0003 — the reference edition of each game and where it was extracted (2026-10-07)
- **Source:** extraction from `games/<game>/images/` with 7-Zip and a raw-sector converter
  (2352-byte and 2448-byte sector images, data track only; no image had audio tracks);
  listing of the extracted folders.
- **Shows:** one English edition per game in `games/<game>/discs/<version>/`:
  - `versailles/en-iso/{cd1,cd2}` (DOS: `DATAS_V/`, `DOS4GW.EXE`, `INSTALL.EXE`; no Windows
    executable; cd2 is only `DATAS_V/`).
  - `atlantis/en-us/cd1..4` (`ATLANTIS.EXE` 688,128 B, `CRYO.DLL` 488,960 B, `MSS32.DLL`,
    `BIGCD1.BIG`; cd2 and cd3 are a single `BIGCD2.BIG`/`BIGCD3.BIG` each; disc 1 is the
    Europe release, discs 2 to 4 USA/Europe).
  - `egypt/en-iso/cd1` (`EGYPTE.EXE` 380,928 B; folders `GAME HNM MUSIC REF SOUND SPRITE SYC
    WARP`).
  - `china/en-iso/cd1` (`CHINE/CHINE.EXE` 571,904 B).
  - `zero-zone/en/cd1` (`ZeroZone.exe` 536,576 B, `zzdatas.big`, `zzlocal_e.big`).
  - `aztec/en-iso/cd1` (`Aztec/Aztec.exe` 1,789,275 B, a 589,884 B `Aztec.exe` launcher at
    the root, `CM6_512.dll`, `CM6_640.dll`, `SPR_P5.DLL`, `SPR_P6.DLL`; see Q-0003).
  - `egypt-2/en/cd1..2` (`Eg2/Eg2.exe` 1,355,776 B with the same `Cm6_*`/`Spr_p*` DLLs).
  - `versailles-2/multi-dvd/dvd1` (`App/V2.exe` 2,674,688 B, `Spr_p5.dll`, `Spr_p6.dll`,
    `BigFile/`, `1.bf`..`5.bf`).
  - `atlantis-2/en-us/cd1..4`, `atlantis-3/en-us/cd1..3` (the US "Beyond Atlantis II"):
    InstallShield cabinets, no loose game executable yet (unshield needed).
  - `egypt-3/en-us/cd1..3`: `Install.exe` and `datas/`, no loose game executable.
  None of the executables' identities (compiler, protection) are established yet. The
  shared `CM6_*`/`Spr_p*` DLLs in Aztec, Egypt II and Versailles II are a first hint of one
  later engine generation (Q-0002).
- **Used by:** CLAUDE.md Ground truth (corpus).

### E-0004 — China's executable: MSVC 5, no protection, own source layout (2026-10-07)
- **Source:** `python tools/identify.py games/china/discs/en-iso/cd1/CHINE/CHINE.EXE`
  (Detect It Easy: PE32, Microsoft Linker 5.10, MSVC 11.00-13.10, DirectDraw, DirectInput,
  DirectSound; no packer or protector reported); Ghidra `CryOmni3D.gpr` program
  `/china/CHINE.EXE` (imported and analysed 2026-10-07: 838 functions); the assert scan
  `tools/ghidra/scripts/assert_namer.py` (`engines/cryomni3d/notes/china-module-map.md`).
- **Shows:** the error routine is passed `F:\Chine\Sources\<file>.cpp` and a line number
  (format string "Fatal error (%d) in File %s at Line %d" at file offset 0x5b864); 29 source
  paths name 48 functions. Sources, in link (alphabetical) order and their first attributed
  function: `carte` 0x401000, `credits` 0x403a50, `Dial` 0x403eb0, `Interface` 0x406de0,
  `Label` 0x410300, `load` 0x410900, `Minutes` 0x411ac0, `Music` 0x412680, `MyError`
  0x412d10, `MyFile` 0x412f10, `MyFont` 0x413300, `MyKeyb` 0x414b30, `MyMouse` 0x414d20,
  `MyScreen` 0x415570, `MySound` 0x415bb0, `MyTga` 0x416510, `MyTimer` 0x416bb0, `MyWarp`
  0x416ca0, `MyWind` 0x4176b0, `Object` 0x417a30, `Puzzle4` 0x417e90, `PuzzleBombe`
  0x4192c0, `PuzzleBoudha` 0x41a3b0, `PuzzleBoutons` 0x41a8f0, `PuzzleGO` 0x41b5d0,
  `PuzzleHorloge` 0x41bd30, `PuzzlePenjing` 0x41c520, `PuzzleSceaux` 0x41d020, `save`
  0x41dea0. Game code runs 0x401000..about 0x420000 (paths and data folders at 0x41f190..
  0x41ffb0), then a DirectDraw/DirectSound wrapper (0x420500..0x421e80, French error
  strings), then a Cryo library block (APC sound "CRYO_APC" 0x43750d.., a timer 0x438110,
  file I/O with "ERREUR FileOpen" 0x4388f1.., DirectInput keyboard and mouse 0x44102b..),
  then the MSVC runtime. No Cryo library DLL: everything is in the one executable.
- **Used by:** CLAUDE.md Ground truth (China); naming in Ghidra.

### E-0005 — China's data: one CD, folders and file types (2026-10-07)
- **Source:** listing of `games/china/discs/en-iso/cd1/CHINE` and `python tools/identify.py`
  on it (`engines/cryomni3d/notes/corpus-triage-china.md`); the disc images in
  `games/china/images/` (EN ISO is a single 614 MB `CHINE.mdf`; the DVD a single 3.7 GB
  `CHINE.iso`; the FR CD a single `CHINE.bin`).
- **Shows:** the game is one CD. `CHINE/` holds `CHINE.EXE`, `Cd.hnm`, `chine.cfg` (16 B:
  four LE uint32 2, 1, 1, 0), `readme.*`, and `DATA/` with: `FONTES` 11 `.CRF` (magic
  `CRYOFONT`, the format upstream's `fonts/cryofont` reads for Versailles); `HNM` 44 `.HNS`
  (640x480 HNM6 videos with sound); `IMAGES` 127 `.HNM` (640x480 HNM6 stills); `INTERF` 15
  `.HNM`, 50 `.SPR`, 119 `.TGA`; `INVENT` 19 `.SPR`, 2 `.TGA`; `LOC` 2 `.HNM`, six text
  files (`CREDITS DIAL Fichetxt LABELS LISTE MINUTES`), `VOICES/` 720 `.WAV` + 1;
  `MUSIC` 6 `.ZIK`; `PUZZLES/<8 puzzles>` 257 `.SPR`, 29 `.TGA`, 16 `.WAV`, 2 `.RAW`
  (307,200 B = 640x480 bytes); `SAVED` (empty); `SOUND` 25 `.WAV`; `SPRITES/{CURSEURS,LOAD,
  OBJETS}` 122 `.SPR`, 1 `.TGA`; `SYNC` 384 `.HNM` (640x480 HNM6); `WARP` 191 `.HNM` (HNM6,
  header width 2048, height 768 for the first two). `DISK1.DAT` is empty (0 B). TGAs are
  type-2 uncompressed 16-bit. Every HNM/HNS starts with `HNM6` and the string
  "Pascal URRO  R&D" at 0x20. There are no `.wam`, `.hlz`, `.hlw` or `.dat` level files as
  in Versailles: place links and game logic are not in the data folders.
- **Used by:** formats README (the format list); CLAUDE.md Ground truth.

### E-0006 — China's logic lives in the executable; text is in LOC (2026-10-07)
- **Source:** strings of `CHINE.EXE` (file offsets): object table names (`CLE_JARRE`,
  `MANDAT1..4`, `PINCEAU`, ... with `c_<x>`/`r_<x>`/`i_<x>` sprite stems, 0x5c680..0x5cb94),
  game variables and dialogue/sync ids (`VAR_LETTRE_REVELEE`, `VAR_Pieces`,
  `Venant_de_HORLOGE`, `CHAPITRE`, `MODE_VISITE`, `ANMI5111`, ... 0x5e364..), the debug line
  "%d i/s - Zone %d / Label : %s / Contexte : %s / Chap : %d" (0x5bdc4), save names
  "%s_game%d.sav" and "Data\Saved\"; `DATA/LOC/DIAL.TXT` (694 blocks `#<id>#`, a `<text>`
  line and one `GOTO <id>` line each).
- **Shows:** like Versailles (whose logic upstream reimplements in C++), China's places,
  objects, variables and scenario are compiled into the executable; data files hold only
  media and text. Dialogue text blocks are keyed by the same ids as the voice files
  (`LOC/VOICES/<id>.WAV`) and sync videos.
- **Used by:** the plan: game logic must be recovered from `CHINE.EXE` and specced in
  `games/china/docs/`.
