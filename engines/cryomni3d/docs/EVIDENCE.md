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

### E-0600 — China's warp image is 2048x768, 16 bits per pixel, in one 3 MB buffer (2026-10-07)
- **Source:** Ghidra `CHINE.EXE!0x416ca0` (`MyWarp::init`): allocates 0x300000 bytes
  (3,145,728 = 2048 x 768 x 2) for the warp buffer. `0x416d60` (`MyWarp::loadWarp`): an
  HNM6 warp is read from file offset 0x44 (a 4-byte chunk size, then 4 skipped bytes, then
  size-8 bytes) and decoded in one call (`0x439004`, or `0x439019` when its second argument
  is set) into that buffer; a TGA fallback reads 15/16-bit or 24-bit pixels (24-bit
  converted to 15/16-bit over 0x180000 = 2048 x 768 pixels). Renderer `0x44205c` reads
  16-bit source pixels at index `(row << 11) | column` (row mask 0x1ff800, column from bits
  21+ of a 32-bit fixed-point x). Corpus: all 191 `DATA/WARP/*.HNM` have `HNM6` header
  width 2048, height 768 (python over the header u16 at offsets 8 and 10).
- **Shows:** one flat 2048-column x 768-row 16-bit image per warp (a cylinder-like strip,
  not cube faces). The display is 15-bit (555) or 16-bit (565) (global 0x48f270 = 15 or
  16) and the pixel conversion follows it.
- **Used by:** spec/china-warp.md (Warp image).

### E-0601 — China's projection tables equal upstream `Omni3DManager::init`, hfov 75.137 deg, vfov 50 deg (2026-10-07)
- **Source:** Ghidra `CHINE.EXE!0x441c90` (`Warp::init(hfovDeg, vfovDeg)`), called by
  `0x416ca0` and `0x417400` with 75.137 and 50.0 (the float 75.137 also at 0x450230).
  Double constants: pi = 4 x (a CRT inverse-trig call on sqrt(2) x 0.5) (0x450280,
  0x450288, 0x450298); 1/180 (0x4502a0); 0.8611111 = 155/180 (0x4502a8); 384.0
  (0x4502b0); 16.0 (0x4502b8); 1/320 (0x4502c0); 2^27 (0x4502c8); 65536.0 (0x4502d0).
  Disassembly read with capstone.
- **Shows:** hfov and vfov are kept in radians; hypV = 384 / sin(155 deg / 2);
  step = tan(hfov/2) x 16 / 320; scale = 2^27 / (2 pi). For 31 rows i: oppH = (i-15) x step,
  angleH[i] = atan2(oppH, 1), hypH[i] = sqrt(oppH^2 + 1); for 21 columns j:
  oppV[j] = (j-20) x step, coord[i][j] = hypV x hypH[i] / sqrt(oppV^2 + hypH[i]^2) x 65536.
  This is upstream `Omni3DManager::init` term for term, except the vertical field of view:
  China passes 50 deg directly, upstream derives it from hfov (52.31 deg for Versailles'
  75 deg). China keeps the tables as 32-bit floats.
- **Used by:** spec/china-warp.md (Projection tables).

### E-0602 — China's grid update equals upstream `updateImageCoords`; beta clamped to +-45 deg (2026-10-07)
- **Source:** Ghidra `CHINE.EXE!0x441df0` (`Warp::setView(alpha, beta)`), disassembly
  0x441df0..0x442058; constants 0.9 (0x4502d8), 384 x 65536 (0x4502e0).
- **Shows:** beta is clamped to +-0.9 x vfov (+-45 deg); alpha is wrapped by one 2 pi step
  (>= 2 pi: subtract; negative: add); both are stored back (globals 0x53485c alpha,
  0x534844 beta). Then for each of 31 rows: s = sin(angleH[i] + beta),
  c = cos(angleH[i] + beta) x hypH[i]; for 20 columns: a = atan2(oppV[j], c) x scale,
  x = (2^27 - alpha x scale) + a at the left point and - a at its mirror,
  y = 384 x 65536 - coord[i][j] x s; the centre column: x = 2^27 - (alpha - atan2(0, c)) x
  scale. Output: 31 rows x 82 ints (41 points x,y in 16.16 image pixels; the first two
  ints unused), upstream's `_imageCoords` layout. The base x term is rounded to a 32-bit
  float. Extra, not in upstream: it stores the image x (bits 16..26) of the two ends of the
  top grid row (beta > 0) or bottom grid row (beta <= 0) in 0x534858 and 0x534854.
- **Used by:** spec/china-warp.md (View angles, Grid).

### E-0603 — China's renderer is upstream's 16x16-block interpolation with different row deltas (2026-10-07)
- **Source:** Ghidra `CHINE.EXE!0x44205c` (`Warp::render(src, dst)`), disassembly
  0x44205c..0x442134; called by `0x417230`, `0x417400`, `0x417500`.
- **Shows:** 30 block rows x 40 block columns of 16x16 pixels = 640x480, destination
  stride 640 16-bit pixels. Per block, from its corners (TL, TR, BL, BR):
  x1 = (TR.x - TL.x) >> 4; dx1 = (((BR.x - BL.x) >> 4) - x1) >> 4;
  y1raw = (TR.y - TL.y) >> 4; dy1 = (((BR.y - BL.y) >> 4) - y1raw) >> 9; y1 = y1raw >> 5;
  dx2 = (BL.x - TL.x) >> 4; dy2 = (BL.y - TL.y) >> 9; x2 = (2 TL.x + dx2) >> 1;
  y2 = (2 (TL.y >> 5) + dy2) >> 1. Per pixel the column and row stepping is upstream's
  inner loop exactly (px starts (2 x2 + x1) x 16, steps x1 x 32, column px >> 21; py starts
  (2 y2 + y1) / 2, steps y1, row offset py & 0x1ff800). Upstream `getSurface` uses
  dx1 = (...) >> 10 and dy1 = (...) >> 15 where China has >> 4 and >> 9 (a 64 times
  smaller per-row change of the pixel step).
- **Used by:** spec/china-warp.md (Rendering).

### E-0604 — China's screen-to-image mapping equals upstream `mapMouseCoords`, y returned as 767 - y (2026-10-07)
- **Source:** Ghidra `CHINE.EXE!0x441b80` (`Warp::screenToImage`); caller `0x4153c0`
  (`MyWarp::hitTest`) takes the point from `0x415440` (`MyMouse::getHotPoint`) and passes
  the result to `0x420370` (linear search of the place's zones: 40-byte records, count at
  0x5305a8, test `0x420340`).
- **Shows:** cell = 82 x (y >> 4) + 2 x (x >> 4); the same bilinear blend as upstream;
  x = (blend & 0x7ff0000) >> 16 (0..2047); y = 0x2ff - (blend >> 16), i.e. 767 - image row
  (upstream's Versailles caller uses 768 - y). The hot point is the cursor's top-left plus
  the cursor sprite's hot-spot offset (sprite +0xc / +0x10) or, when that is 0, half the
  sprite's width / height.
- **Used by:** spec/china-warp.md (Hit testing).

### E-0605 — China turns the view by cursor position in edge bands, with 0.8 inertia (2026-10-07)
- **Source:** Ghidra `CHINE.EXE!0x4170a0` (`MyWarp::scrollByCursor`, called each frame
  from `0x406530`); float constants 100 (0x45021c), 380 (0x450220), 1250 (0x450224),
  1500 (0x450228), 0.8 (0x45022c); cursor kept by `0x414fb0` (`MyMouse::update`:
  DirectInput relative motion, clamped to 0..640 - cursor width and 0..480 - cursor height;
  starts at 320,240 in `0x414d20`); speed setting 0x48f258 (default 2 in `0x4056c0`; the
  options code `0x40e630` cycles it modulo 5).
- **Shows:** with the cursor centre (cx, cy): pushX = 100 - cx when cx < 100, 540 - cx when
  cx > 540, else 0; pushY = cy - 100 when cy < 100, cy - 380 when cy > 380, else 0.
  k = 5 - speed setting. Each frame: vAlpha += pushX / (k x 1250), vBeta += pushY /
  (k x 1500); if either velocity is non-zero: beta += vBeta, alpha += vAlpha,
  `Warp::setView`, then both velocities x 0.8. Per frame, no time base; no alpha limits on
  this path. Cursor left raises alpha (turns left); cursor up lowers beta (looks up).
  Upstream `updateCoords` (mouse deltas x 0.00025 / 0.0002, decay 0.4 / 0.6, WAM limits)
  is a different model.
- **Used by:** spec/china-warp.md (Turning).

### E-0606 — China's node-change transition: turn to the cursor, then zoom in by 1 deg per frame (2026-10-07)
- **Source:** Ghidra `CHINE.EXE!0x417500` (`MyWarp::turnToPoint(x, y)`), constants 416.0
  (0x450238), +-3.14159 / +-6.28318 (0x450240..0x450258), -0.2 (0x450260);
  `0x417400` (`MyWarp::zoomIn(frames)`), constant 1.0 (0x450234); both called by
  `0x41f430` for zone kinds 2..5 with the cursor top-left position (not the hot point).
- **Shows:** turnToPoint: target = (alpha + atan2(320 - x, 416), beta + atan2(y - 240, 416));
  each frame the remaining difference is wrapped to about (-pi, pi] and 20 % of it is
  applied, then setView, render, flip; 32 frames. 416 = 320 / tan(75.137 deg / 2), the
  focal length in pixels. zoomIn(n): n frames, each re-running `Warp::init(h, 50)` with h
  from 75.137 down by 1 per frame, setView, render, flip; then `Warp::init(75.137, 50)`.
- **Used by:** spec/china-warp.md (Transitions).

### E-0500 — China's WinMain and start-up order (2026-10-07)
- **Source:** Ghidra `/china/CHINE.EXE` (decompile dump `notes/decomp/all/`): CRT `entry`
  0x4456d0 calls 0x4118a0 (WinMain) with the module handle; 0x4118a0 calls 0x4053b0 (boot),
  then font load 0x413300, then the game 0x4064e0, then shutdown 0x405950; 0x4053b0 body.
- **Shows:** boot first creates a named 32-byte file mapping "Chine" (0x45c0a0); if it
  already exists (GetLastError 183) boot returns 4 and WinMain exits silently (one instance
  only). Otherwise, in order, each must return 0 or start-up stops: globals reset 0x4056c0,
  error module 0x412d10, keyboard 0x414b30, window 0x4176b0, screen 0x415570, warp 0x416ca0,
  file 0x412f10, CD check 0x41ff50(1), loading screen 0x405740, timer 0x416bb0, sound
  0x415bb0, mouse 0x414d20, objects 0x417a30, then game modules (0x4106a0, 0x410280,
  0x406d90, 0x40ec80, 0x404080 dialogue, carte 0x401000, 0x4119f0, music 0x412680), then
  `chine.cfg` 0x405870, then the pre-menu videos (E-0504), then menu music 0x4057b0.
  0x41f160 (several times in the chain) is an empty "return 0".
- **Used by:** spec/china-boot.md Start-up.

### E-0501 — `chine.cfg`: four LE uint32 options, written by the options screen (2026-10-07)
- **Source:** CHINE.EXE 0x405870 (read), 0x4059f0 (write), 0x4056c0 (defaults), 0x40e630
  (options screen: labels `omni3D`, `sous_titre`, `musique`, `save` 0x45c97c, `retour`;
  speed names `tres_lent` .. `tres_rapide`); corpus `CHINE/chine.cfg` = 2, 1, 1, 0 (E-0005).
- **Shows:** `chine.cfg` (current directory) is read only if it exists; fields in order:
  (1) panorama speed 0..4 (default 2; the options button steps it modulo 5), (2) subtitles
  on/off (default 1), (3) music on/off (default 1), (4) unk_save_mode (default 0); after
  reading, the in-memory flag "save mode" = (field 4 == 0). The options screen toggles the
  fourth button between the two values and keeps field 4 = !flag. Missing file: defaults.
- **Used by:** spec/china-boot.md Start-up; Q-0500.

### E-0502 — China's CD check: `disk%d.dat` on drives C..Z, `cd` prompt (2026-10-07)
- **Source:** CHINE.EXE 0x41ff50 (called with disk 1), 0x41ffb0, 0x420020, 0x41ff30;
  strings `%c:\Chine\Data\disk%d.dat` 0x45ee9c, `%c:\Chine\Data\` 0x45ee8c, `cd` 0x45eeb8;
  corpus `CHINE/DATA/DISK1.DAT` (0 bytes) and `CHINE/Cd.hnm`.
- **Shows:** the check opens `<L>:\Chine\Data\disk1.dat` for drive letters 'c'..'z' in
  order and keeps the first letter that opens; every later CD path is `<L>:\Chine\Data\...`.
  If none opens, 0x420020 shows the still image `cd` (found as `Cd.hnm` in the game
  folder, E-0510) and polls each frame: Escape aborts start-up (returns 3), Space waits 4 s
  and rescans; the loop repeats until a drive is found.
- **Used by:** spec/china-boot.md Start-up.

### E-0503 — China's screen is 640x480 16-bit; warp buffer 2048x768 (2026-10-07)
- **Source:** CHINE.EXE 0x415570 (MyScreen init: mode call with 0x280, 0x1e0, 0x10; pitch
  global 0x500), 0x416ca0 (MyWarp init), screen-sized copies of 0x25800 dwords (0x96000 B)
  in 0x407140 and 0x406de0.
- **Shows:** a 640x480 16-bit DirectDraw mode (pitch 1280); a pixel-format global (15 or
  16) selects 555 or 565 routines. Warp init calls the projection set-up 0x441c90 with the
  floats 75.137 and 50.0, zeroes the view angles (alpha 0x53485c, beta 0x534844) and
  allocates the warp buffer of 0x300000 bytes (= 2048 x 768 x 2, the WARP HNM size, E-0005).
- **Used by:** spec/china-boot.md Start-up; Q-0501.

### E-0504 — what plays before China's menu, and how it is skipped (2026-10-07)
- **Source:** CHINE.EXE 0x4053b0 tail; 0x41fd70 (`<L>:\Chine\Data\` + `Hnm\` 0x45ee58);
  0x4146c0 (HNS player); 0x403380 then 0x404710 (dialogue lip-sync player, `%s%s%d.hnm`,
  `%s%s.wav`, subtitles drawn only while the subtitle option is set); 0x4057b0, 0x41fcc0,
  0x41fd00 (`Data\Music\`, `Music\`, `Allee.zik`); 0x405740 (`Load`, "Chargement en
  cours..."); corpus `DATA/HNM/{LOGO,INTRO,ITB}.HNS`, `SYNC/P000ANJ0..3.HNM`,
  `P000EMP0..3.HNM`, `LOC/VOICES/ANJGEN41.WAV`, `LOC/DIAL.TXT` block `#ANJGEN41#`.
- **Shows:** during boot the loading screen shows image `Load` with the white text
  "Chargement en cours..." at (x 50, y 200), font 3. After `chine.cfg`: `logo.hns`, then
  `intro.hns` (both from `<L>:\Chine\Data\Hnm\`), then the dialogue `ANJGEN41` with the
  speaker stems `P000ANJ` and `P000EMP` (face loops `SYNC\<stem><0..3>.hnm`, voice
  `ANJGEN41.wav`) with subtitles forced off for it, then `itb.hns`, then music `Allee.zik`
  (local `Data\Music\` first, else the CD's `Music\`; started only if the music option is
  on). The HNS player sets a 10 ms multimedia timer, pre-buffers up to 2 s, then shows
  frames; it stops when Escape (DIK 1) is down or the left mouse button is clicked; each
  video is skipped separately (the result is ignored). The dialogue player also stops on
  Escape.
- **Used by:** spec/china-boot.md Before the menu.

### E-0505 — China's main menu: `fondtitr`, eight bullets, labels from LABELS.TXT (2026-10-07)
- **Source:** CHINE.EXE 0x406de0 (Interface: `fondtitr`, `roug_1..6.spr`, `blc_1..6.spr`;
  pushes at 0x406e43..0x407071), 0x407140 (menu screen), 0x41f760 (SPR loader), 0x420340
  (point-in-rect), 0x4136d0 (text draw: first coordinate y, second x), 0x406d20 (save
  slots); corpus `DATA/INTERF/ROUG_*.SPR`, `BLC_*.SPR` (header bytes 0x0c..0x1d, read by a
  script), `DATA/LOC/LABELS.TXT`.
- **Shows:** background `Interf\fondtitr` (`FONDTITR.HNM`), copied to a 640x480 back
  buffer. SPR file = 18-byte TGA-style header (width u16 @0x0c, height u16 @0x0e, bpp u8
  @0x10 must be 15 or 16), key colour u32 @0x12, x i32 @0x16, y i32 @0x1a, then w*h 16-bit
  pixels. All twelve bullets are 14x14, key 0x1f. Slots (normal sprite `roug_n`, hover
  `blc_n`; x, y): 0 `nouveau_jeu` "Start the game" (196,225); 1 `charge_jeu` "Load a game"
  (212,254); 2 `reprendre`/`reprendre2` "Resume the game"/"Resume the visit" (230,283);
  3 `sauve_jeu` "Save the game" (246,312); 4 `visite` "Visit the site" (264,341);
  5 `consulte_doc` "Consult the documentation" (280,370); 6 `options` "Options" and 7
  `quitter` "Leave the game" reuse `roug_6`/`blc_6` moved by (+20 x, +25 y) per step:
  (300,395), (320,420). Label at (x+20, y+1). Hit rectangle = bullet rectangle grown right
  by the label width and down by the label height; hovering draws `blc_n` and the label in
  0xffff, else `roug_n` and the label in 0x7020 (enabled) or 0x9a73 (disabled). Enabled:
  0 if fewer than 12 of `Data\Saved\<name>_game<1..12>.sav` exist; 1 if any exists or save
  mode is set; 2 if a game is running or variable 0 (visit) is set; 3 if save mode and a
  game is running; 4..7 always. A click on an enabled button returns a choice: 0 gives 1
  new game, 1 gives 2 load, 2 gives 3 resume, 3 gives 4 save, 4 gives 5 visit, 7 gives 6
  quit; 5 opens the documentation (0x4070a0, 0x4085d0) and 6 the options screen (0x40e630)
  inside the menu.
- **Used by:** spec/china-boot.md Main menu.

### E-0506 — menu choices and what "new game" sets up (2026-10-07)
- **Source:** CHINE.EXE 0x406360 (menu dispatcher), 0x403a30 (reset), 0x403440, 0x4033c0
  /0x4201d0/0x4201c0 (game variable table at 0x45eec8, 12-byte entries), 0x41f190 (set
  scene handler), 0x410900/0x410da0 (`CHOISISSEZ VOTRE EMBLEME:`), 0x41e930 (`Fondlod`,
  load), 0x41e090 (`Fondsvg`, save); pushes of 0x436db0 at 0x4063ee and 0x406481.
- **Shows:** choice 1 (new game): reset game state (0x403a30); if save mode is off, the
  emblem chooser runs first and Cancel returns to the menu; then game-running = 1, scene
  handler = 0x436db0 (`Script_Start`), object 0x1e set to state 2 unless already 1..3,
  variable 0 (visit) = 0. Choice 2 load (emblem loader or 0x41e930), 3 resume, 4 save
  (0x41e090), 5 visit: reset, variable 0 = 1, handler 0x436db0, game-running = 0. Choice 6
  quits: the game loop ends and the credits (0x403b10, `credits.txt`) run.
- **Used by:** spec/china-boot.md Main menu, New game; Q-0500.

### E-0507 — China's first place: `Script_Start` then `pne140`, alpha 4.7 (2026-10-07)
- **Source:** CHINE.EXE raw disassembly (capstone) at 0x436db0 and 0x431050 (the region
  0x421f00..0x436e20 has no Ghidra functions, Q-0503); 0x403a10, 0x402d50, 0x402dd0,
  0x416d60; strings `Script_Start` 0x4629c0, `MIN001` 0x4629b8, `pne140` 0x45be08,
  `lionne_pne`, `lion_pne`; corpus `DATA/WARP/PNE140.HNM`.
- **Shows:** a scene handler takes one int: 1 returns a data pointer, 2 its name, 3 runs on
  entry, 0 each frame. `Script_Start` on entry: clears 0x5305a8, sets variable 1 = 1, calls
  0x411d80("MIN001"), sets view alpha = 4.7f, beta = 0 (0x403a10 writes them straight to
  the warp angles), then switches to handler 0x431050. That handler (name `pne140`) on entry
  registers its zones (0x403060, 0x4031b0, 0x403100 with labels `lionne_pne`, `lion_pne`)
  and loads warp `pne140`: 0x402d50 builds `<L>:\Chine\Data\warp\pne140` (0x402dd0) and
  loads it with 0x416d60, stores the name, sets display mode 1 (warp) and the cross-fade
  flag. So the first panorama is `DATA/WARP/PNE140.HNM` at alpha 4.7, beta 0.
- **Used by:** spec/china-boot.md New game.

### E-0508 — China's game loop and per-frame order (2026-10-07)
- **Source:** CHINE.EXE 0x4064e0, 0x406530, 0x406880, 0x41f380, 0x415370, 0x4170a0,
  0x417230, 0x404e80; the debug line at 0x415a20.
- **Shows:** 0x4064e0 runs the menu, then frames until a frame asks for the menu (then the
  menu again) or quit is set (then credits). One frame: input/keys 0x406880 (frame rate,
  debug keys, Space or the interface trigger opens the interface screen 0x40efd0 whose
  result can return to the menu; Escape calls 0x4039f0); if the window is active: music
  tick 0x412740, mouse 0x414fb0, 0x415270, sound 0x403640, hotspot under the cursor
  0x415370, scene handler call 0x41f380 (entry call with 3 once, then 0); then draw by
  display mode: 2 = still image, 1 = warp: if the cross-fade flag is set, the old frame is
  cross-faded into the new view (0x404e80, 640x480) first; then view update 0x4170a0, warp
  render 0x417230, labels 0x4107c0, optional overlays (inventory debug 0x40fd60, debug text
  0x415a20, 0x420260), cursor 0x415340, then unlock 0x415860 and flip 0x415900.
- **Used by:** spec/china-boot.md Main loop.

### E-0509 — China's panorama scrolling by cursor near the edges (2026-10-07)
- **Source:** CHINE.EXE 0x4170a0; floats 0x45021c 100.0, 0x450220 380.0, 0x450224 1250.0,
  0x450228 1500.0, 0x45022c 0.8; 0x441df0 (set view, beta clamped to plus/minus 0.9 x a
  library limit, alpha wrapped by a period global).
- **Shows:** cursor point = cursor position + half the cursor size. dx = 100 - x if x < 100,
  540 - x if x > 540, else 0; dy = y - 100 if y < 100, y - 380 if y > 380, else 0. With
  s = 5 - speed option: alpha velocity += dx / (s x 1250), beta velocity += dy / (s x 1500);
  if either velocity is non-zero the angles advance by it, the view is set, and both
  velocities are multiplied by 0.8 (per frame).
- **Used by:** spec/china-boot.md Main loop; Q-0501.

### E-0510 — China's still-image lookup order (2026-10-07)
- **Source:** CHINE.EXE 0x402e20, 0x402fb0 (`Images\`, `%s%s%s.%s`), 0x41fdb0 (`Loc\`),
  0x416510 (TGA), 0x416d60 (HNM).
- **Shows:** a still is shown by stem: `<stem>.tga`, then `<stem>.hnm` (both relative to
  the game folder), then `<L>:\Chine\Data\Images\<stem>.hnm`, then `...Images\<stem>.tga`,
  then `<L>:\Chine\Data\Loc\<stem>`; it sets display mode 2. Stems may carry a folder
  (the menu passes `<L>:\Chine\Data\Interf\fondtitr`).
- **Used by:** spec/china-boot.md Start-up, Main menu; Q-0502.

### E-0100 — China's HNM/HNS files are HNM6 as in Mission Sunlight, 764/764 (2026-10-07)
- **Source:** corpus statistic: `python engines/cryomni3d/tools/parsers/hnm.py`
  ("HNM: 764/764 files valid, every byte consumed; chunks IX 13721, AA 44, BB 9423,
  IW 191"); `hnm.ksy` compiled by `tools/ksy_check.py` parses all 764 China files to the end.
- **Shows:** every `.HNM`/`.HNS` under `CHINE/` (WARP 191, IMAGES 127, SYNC 384, INTERF 15,
  LOC 2, HNM 44, `Cd.hnm` 1) has the 64-byte HNM6 header (`unk_04` 0, bpp 16, `unk_14` 0,
  `unk_18` 0, author "Pascal URRO  R&D", copyright "-Copyright CRYO-"), `frame_count`
  superchunks (flag byte 0) of 4-aligned chunks (flags 0), and a zero u32 at the end, as in
  Mission Sunlight (peintre E-0200..E-0203). Per folder: IMAGES, INTERF, LOC and `Cd.hnm` are
  640x480 one-frame IX stills; SYNC 384 files of 7 IX frames each (one key frame), no sound;
  HNM 44 `.HNS` 640x480, 11..3118 frames, 1..38 key frames, all with sound: audio_flags
  0xA1 (37, 22050 Hz stereo), 0x21 (5, 22050 Hz mono), 0xC1 (2, 44100 Hz stereo), each
  agreeing with its AA chunk's CRYO_APC 1.20 header (rate = ((flags & 0x60) >> 4) * 11025,
  stereo = bit 7), every file 15 frames/s of sound (each BB = AA ADPCM / 32). 9 HNS hold
  only the AA chunk (short sound); in the others the sound frames end 10..85 frames before
  the last video frame (31 short in 18 files). `unk_1a` is 2 in every non-warp.
- **Used by:** `docs/formats/hnm.ksy`, README "HNM6".

### E-0101 — China's warps are one-frame 2048x768 HNM6 files with an IW chunk (2026-10-07)
- **Source:** corpus statistic (as E-0100); ScummVM `engines/cryomni3d/image/hnm.cpp`
  (`HNMFileDecoder::loadStream`: the first chunk tag IW selects warp mode, IX normal; the
  header's buffer size "is not reliable on IW") and `image/codecs/hnm.cpp`
  (`DecoderImpl::reset` asserts quality > 0 in warp mode; `decodeIWkf` walks 8x8 blocks).
- **Shows:** all 191 files in `DATA/WARP` are 2048x768, `frame_count` 1, `unk_1a` 1,
  `max_frame_size` 0x300000 (2048*768*2), `file_size` = file length - 4 (the terminator
  is not counted; every other China HNM counts it), and one chunk `IW` whose payload has a
  24-byte header (s32 quality = 85 in all 191, then bit, motion, short-motion, jpeg and end
  offsets, bit = 24, end = payload size) instead of IX's 28 bytes (IX adds unk_18 = end).
  No IW appears outside WARP and no IX inside it.
- **Used by:** `docs/formats/hnm.ksy` (`video_iw`), README "HNM6".

### E-0102 — China's SPR is one 15-bit picture in a TGA container with a 12-byte ID (2026-10-07)
- **Source:** Ghidra `/china/CHINE.EXE!0x41f760` (the loader every game source calls for
  `*.spr`: callers in `Interface.cpp`, `MyMouse.cpp` (`tri270.spr`), `save.cpp`, `load.cpp`,
  `Minutes.cpp`, the puzzles); corpus statistic `python engines/cryomni3d/tools/parsers/spr.py`
  ("SPR: 448/448 files valid, every byte consumed; 27 key colours (most common 0x001f x184,
  0x03e0 x88, 0x037e x33); 304 files contain their key colour; unk_16 0..603, unk_1a 0..458").
- **Shows:** the loader reads 18 header bytes (width at 12, height at 14, depth at 16),
  then three u32 (the first's low u16 kept as the sprite's key colour, the other two kept
  as two s32 fields), accepts only depth 15 or 16, allocates width*height*2 + 20 bytes,
  reads width*height*2 pixel bytes; on a 16-bit (565) screen it converts the pixels and the
  key from 555 to 565. In the corpus every file is: id_length 12, colour map 0, type 2,
  origins 0, depth 15, descriptor 0x20, the 12 ID bytes, then exactly width*height u16
  pixels (bit 15 never set). The two s32 fields lie in 0..603 and 0..458 and often exceed
  the sprite's own size (274 and 269 files), so they look like screen positions, but nothing
  here shows how they are used (Q-0100). Mission Sunlight's SPR (a multi-frame RLE bank with
  a palette) is a different format.
- **Used by:** `docs/formats/spr.ksy`, README "SPR".

### E-0103 — China's TGA: uncompressed true colour, 16-bit or one 24-bit file (2026-10-07)
- **Source:** Ghidra `/china/CHINE.EXE!0x416510` (`MyTga.cpp` loader; error "TGA load
  Failure."); corpus statistic `python engines/cryomni3d/tools/parsers/tga.py` ("TGA: 151/151
  files valid, every byte consumed; 39 x 16-bit footer, 111 x 16-bit no footer, 1 x 24-bit
  footer").
- **Shows:** the loader reads the 18-byte header, skips id_length bytes, reads width*height*2
  bytes when depth is 16 or width*height*3 when depth is 24 (then converts to the screen's
  555 or 565), any other depth fails; it flips the rows when descriptor bit 5 is clear and
  never reads the footer. Corpus: id_length 0, type 2, origins 0, depth 16 (150 files) or 24
  (`DATA/SPRITES/LOAD/FOND.TGA`, 640x480), descriptor 0 (112) or 1 (39), bit 15 never set
  in 16-bit pixels, and nothing after the pixels but, in 40 files, the 26-byte TGA 2.0
  footer with zero offsets. Mission Sunlight's TGA (peintre E-0104) is the 16-bit subset.
- **Used by:** `docs/formats/tga.ksy`, README "TGA".

### E-0104 — China's WAV: plain RIFF PCM, 16-bit mono, 22050 Hz but one (2026-10-07)
- **Source:** corpus statistic `python engines/cryomni3d/tools/parsers/wav.py` ("WAV:
  763/763 files valid, every byte consumed; 762 x tag 1 (PCM), 1 ch, 22050 Hz, 16 bit;
  1 x tag 1 (PCM), 1 ch, 44100 Hz, 16 bit"; chunk orders fmt+data 320, fmt+data+LIST 440,
  fmt+data+LIST+cue+LIST 3).
- **Shows:** every `.WAV` (LOC/VOICES 721, SOUND 25, PUZZLES 16, SPRITES/LOAD 1) is a RIFF
  WAVE whose RIFF size is the file size - 8, chunks padded to even, a 16-byte `fmt ` (or 18
  with cbSize 0) of PCM 16-bit mono, a `data` chunk a whole number of samples long; only
  `DATA/SOUND/BOITE32A.WAV` is 44100 Hz. No APC or other Cryo codec among them.
- **Used by:** `docs/formats/wav.ksy`, README "WAV".

### E-0105 — China's CRF fonts have Versailles' layout, 224 glyphs each (2026-10-07)
- **Source:** Ghidra `/china/CHINE.EXE!0x413300` (`MyFont.cpp`: loads `font01..09.crf`,
  `font10..11.crf`) and `0x413420` (one font: whole file in memory, the header u16 at 0xc
  and 0xe byte-swapped, glyphs indexed from offset 0x30 for characters 0x20 up while the
  offset stays inside the file, each glyph 10 + h*w bytes); ScummVM
  `engines/cryomni3d/fonts/cryofont.cpp` (`CryoFont::load`: magic, three u16, s16 height,
  32-byte comment, then `k8bitCharactersCount` = 223 glyphs of BE u16 h, u16 w, s16 offX,
  s16 offY, u16 advance, w*h bytes); corpus statistic
  `python engines/cryomni3d/tools/parsers/crf.py` ("CRF: 11/11 files valid, every byte
  consumed; 224 glyphs each; unk_08/unk_0a (1, 1) x11; comments 32 '?' x11").
- **Shows:** China's fonts have exactly the layout ScummVM reads for Versailles, with 224
  glyphs (0x20..0xFF) filling each file to its last byte; ScummVM's 223 leaves the 0xFF
  glyph unread (Versailles' `DATAS_V/FONTS/FONT01.CRF` also holds 224). Bitmaps hold only 0
  and 255. The third u16 (`unk_0c`) is 9..24, heights 12..20.
- **Used by:** `docs/formats/crf.ksy`, README "CRF".

### E-0106 — China's two MASK.RAW are 640x480 zone maps read under the mouse (2026-10-07)
- **Source:** strings `mask.raw` next to `Puzzle4\` and `horloge\` in CHINE.EXE; Ghidra
  `/china/CHINE.EXE!0x417e90` (`Puzzle4.cpp`, loads `Puzzle4\mask.raw` whole with
  0x413200) and its loop 0x4189bc; `0x41bd30` (`PuzzleHorloge.cpp`, same load) and
  0x41c1d0; corpus statistic `python engines/cryomni3d/tools/parsers/raw.py`
  ("HORLOGE/MASK.RAW: 55 values 0..54; PUZZLE4/MASK.RAW: 25 values 231..255; RAW: 2/2").
- **Shows:** both files are 307,200 bytes = 640*480, no header; the code reads the byte at
  `mask + y * 640 + x` for the mouse position. Puzzle 4 subtracts 0xE7: 0..23 pick a label
  from a table of 3 rows of 8 names, 24 (byte 0xFF, 203,151 pixels) is no zone. The clock
  puzzle treats 0 as no zone (291,917 pixels) and values below 0x37 as zones (1..54 occur;
  some tests are < 13). Puzzle meaning belongs in `games/china/docs/`.
- **Used by:** `docs/formats/raw.ksy`, README "RAW".
