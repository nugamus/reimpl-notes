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

### E-0700 — China's places are 270 procedures in code, chained in one list (2026-10-07)
- **Source:** CHINE.EXE .text 0x421f00..0x436e20 (no function defined there by Ghidra's
  auto-analysis: reached only through function pointers); `0x41f190` (goto),
  `0x41f380` (per-frame tick), `0x41f6a0` (find by name), `0x41f3c0` (debug name);
  `uv run engines/cryomni3d/tools/china_places.py --selftest` ("270 procedures, list
  covers all of them").
- **Shows:** every place (and every close-up, puzzle entry and cut-scene step) is a cdecl
  procedure `int proc(int msg)`, each 16-byte aligned and starting `mov eax,[esp+4]`.
  msg 1 returns the next procedure of a global list (head 0x436db0 "Script_Start"; the
  last returns 0); msg 2 returns the place name; msg 3 is the entry part; any other value
  runs the event part (the entry part falls through into it). The tick 0x41f380 calls the
  current procedure with 3 once after a goto, then with 0 every frame. Goto 0x41f190
  stores the procedure, asks its name (msg 2) and switches music by the name's first
  three letters through the table at 0x45ed10 (PNE/AIE/AIO/CTP/CGC -> Allee; CPC/LGE/SPF
  -> Bureaux1; LGA/BPI/ESP/NWF/BAN/BDA -> Bureaux2; PDC -> Concub; JIX -> Jardins;
  CTH/CHS/SHS -> SalleHS; `.zik` in DATA/MUSIC). Find-by-name 0x41f6a0 walks the list from
  the head with msg 1 comparing msg 2 names (at most 5000 steps): the map and the loader
  use it (callers 0x4013e0, 0x4114b0, 0x4116b0). All 270 procedures are on the list.
- **Used by:** `games/china/docs/places.md`, `engines/cryomni3d/tools/china_places.py`.

### E-0701 — China's zones: 40 rectangles in warp coordinates (2026-10-07)
- **Source:** CHINE.EXE `0x420330` (count at 0x5305a8 = 0), `0x4202e0` (append, refuses
  past 0x28), `0x420460` (record = 0x5305b0 + 40*i), `0x420370`/`0x420340` (hit test),
  `0x4153c0` (mouse -> `0x441b80` -> hit test), `0x4203c0` (debug draw flips y as
  0x2ff - y); rect data e.g. 0x465fc0 = {290,1982,460,2047} and 0x465fd0 = {290,0,460,62}
  for warp jixw111.
- **Shows:** a place's hotspots ("zones") are axis-aligned rectangles of four u32 in .data,
  given as {top, left, bottom, right} in the warp's own picture coordinates (x 0..2047
  around the cylinder, y 0..767; inclusive bounds). The mouse's screen position is turned
  into warp coordinates by the Omni3D library (0x441b80) and the zones are tested in
  creation order; the first hit wins. A zone crossing x = 0 is given twice (one rect
  ending at 2047, one starting at 0). Record (40 bytes): rect[4], disabled (1 = off),
  type, target (procedure or string), arg, alpha (float), beta (float). At most 40 per
  place; procedures reset the list (0x420330) first thing in their entry part and refer to
  zones by creation index.
- **Used by:** `games/china/docs/places.md`.

### E-0702 — China's zone types, cursors and click actions (2026-10-07)
- **Source:** CHINE.EXE zone creators `0x403060` (type 0), `0x4030a0` (2), `0x403290` (4),
  `0x4032f0` (6), `0x403100` (7), `0x403210` (8), `0x4031b0` (9); `0x403590`/`0x4035d0`
  (enable/disable by index); the generic handler `0x41f430`; cursor set `0x4151a0` with
  the sprite list at 0x45d1d0 loaded by `MyMouse.cpp` 0x414d20 (index 8 doigt, 9 voir,
  10 prendre, 12 doigt, 14 util, 15 interrog, 16 bouche); corpus statistic from
  `china_places.py`: 609 type-0, 23 type-2, 84 type-4, 44 type-6, 332 type-7, 325 type-8,
  37 type-9 creations; types 1, 3, 5 never created.
- **Shows:** type 0 "go" (args: disabled, target procedure, an arg always 0, alpha, beta
  as doubles; alpha < 0 = keep the view), cursor 8 (finger; 12 outside a warp); type 2
  "look" (target procedure = a close-up), cursor 9 (eye); type 4 "take" (target procedure
  or 0), cursor 10 (hand) when no object is held; type 6 "use", cursor 14 when no object
  is held; type 7 "label" (a LABELS.TXT key looked up by 0x410600, "ACCES LEGENDE
  INCONNU" if missing): hovering shows the text, no cursor change; type 8 "documentation"
  (a Fichetxt.txt key, "ACCES BASE DOCUMENTAIRE INCONNU" if missing): with empty hands
  hovering shows the title and cursor 15 (question mark), clicking opens that entry
  (0x40c5a0) and re-enters the place (0x41f170); type 9 "talk", cursor 16 (mouth). Over a
  type 4/6 zone while holding an object the cursor is that object's cursor. Visit mode
  (variable 0 MODE_VISITE != 0): types 2, 4, 6, 9 are created disabled; labels (type 7)
  exist only in visit mode (created disabled otherwise); enabling (0x403590) leaves types
  6, 7, 9 off in visit mode. Clicking a type 0/2/4 zone (0x41f430's pressed branch):
  in a warp, turns the view towards the click (0x417500 with the mouse position,
  0x417400 with arg), sets alpha/beta when alpha >= 0, then goes to the target procedure
  when it is not 0. Otherwise the clicked zone's index stays in 0x48f27c (hover clears it
  to -1) and the procedure's own event part reacts to it.
- **Used by:** `games/china/docs/places.md`.

### E-0703 — China's script API used by the place procedures (2026-10-07)
- **Source:** CHINE.EXE callees of the 270 procedures (counts from `china_places.py`):
  `0x402d50` warp (DATA/WARP/<name>.HNM via `warp\` + name, 182 calls), `0x402cf0` video
  (`%s%s.hns` from DATA/HNM, 42), `0x402e20` still image (Images\<name>.tga, 87),
  `0x403380` -> `0x404710` sync dialogue (166), `0x403350` -> `0x404d00` voice-only
  dialogue (9), `0x4033c0`/`0x403580` = `0x4201d0`/`0x4201c0` variable set/get on the table
  at 0x45eec4 ({name, value, id} x 220; 0 MODE_VISITE, 1 CHAPITRE, then
  NWFH401, Venant_de_BOUTON, ...), object state get/set `0x417da0`/`0x417dc0` on the
  table at 0x45d5c0 (48-byte records, name at +4, state at +0x24; states 0 initial,
  1 cursor, 2 inventory, 3 destroyed, per the debug strings at file 0x5b4e4..), wrappers
  `0x4033e0` (==3), `0x403400` (!=0), `0x403420` (==1), `0x403440` (to inventory),
  `0x403480` (to cursor), `0x4034f0` (destroy; drops it from the hand); `0x4035f0` ->
  `0x405ed0` puzzle by number; `0x411d80` add a MINUTES.TXT key to the notebook (60);
  `0x403a10` set view alpha/beta (floats in radians, 46); `0x4037e0`/`0x4039a0`/`0x4039f0`
  sound on channel 3 (queue / play and wait / stop); `0x41f190` goto (170).
- **Shows:** the full verb set a place can use; everything a place does is a sequence of
  these calls guarded by variable and object tests.
- **Used by:** `games/china/docs/places.md`, `china_places.py` (API table).

### E-0704 — China's id conventions: warps, sync videos, dialogue lines (2026-10-07)
- **Source:** `china_places.py` output (e.g. pne140: `sync_video('GICD1011', 'D140gia',
  'D140ANJ')`); `0x404710` formats `%s%s%d.hnm` for 4 slots (0x48f078, stride 32);
  corpus: DATA/SYNC has D140GIA0..3 / E110GIG0..3 style names, DATA/LOC/DIAL.TXT has
  `#GICD1011#` with `GOTO ANGC1011`, DATA/LOC/VOICES has GICD1011.WAV; `var_set(CHAPITRE,
  n)` takes values 1..18 across the procedures.
- **Shows:** a warp name is a 3-letter area code (music table, E-0700) plus an optional
  `w` and three digits (pne140, jixw111, aie600b); its transition videos are `<area>h<nnn>`
  .HNS in DATA/HNM. A sync dialogue names a DIAL.TXT block (also the voice WAV), and two
  video stems: the speaker's and Anjing's (`<letter><3 digits><3-letter speaker>`), each
  played as stem + 0..3 (.HNM in DATA/SYNC). Dialogue ids are two letters of speaker,
  one of listener, a letter, then four digits whose first is the act (Q-0701); game
  variables named after a dialogue id record that it was heard. CHAPITRE is a story step
  (1..18), not the game's chapter.
- **Used by:** `games/china/docs/places.md`.

### E-0705 — China's new game starts in pne140, facing alpha 4.7 (2026-10-07)
- **Source:** CHINE.EXE `0x436db0` (Script_Start): zones reset, CHAPITRE = 1, notebook
  MIN001, view alpha 4.7 / beta 0, goto 0x431050 (pne140); new game `0x406360` and
  `0x41f100` go to 0x436db0; pne140's procedure 0x431050 as dumped by `china_places.py
  pne140` and its disassembly 0x431050..0x43142b.
- **Shows:** the worked example in `games/china/docs/places.md` (zones, conditions, clicks).
- **Used by:** `games/china/docs/places.md`.

### E-0200 — China's LOC text files: loading, encoding, and DIAL.TXT's grammar (2026-10-07)
- **Source:** CHINE.EXE: the six loaders build the path `<data path>Loc\<name>`
  (0x41fdb0 appends "Loc\" 0x45ee60) and read the whole file into one buffer (0x413200:
  open, size, alloc, read); `Dial::load` 0x404080 ("dial.txt"), `Dial::parse` 0x404190,
  `Dial::resolveGotos` 0x404150, `Dial::findBlock` 0x403eb0 ("fin" 0x45bffc, CRT tolower
  0x444050), "goto"/"GOTO" 0x45c048/0x45c040, error "Dialogue init Failure." with Dial.cpp
  lines 0xeb..0x171; corpus `DATA/LOC/*`, `loctext.py`.
- **Shows:** all six files are Windows-1252 text with CR LF line ends and no NUL; bytes
  >= 0x80 are accented Latin-1 letters, except one 0x82 in DIAL.TXT line 1549
  ("Douairi" 0x82 "re": code page 850's é, a slip; Windows-1252 shows a low quote).
  DIAL.TXT: blocks `#id#` `<text>` `GOTO target`, in that order only (any other order or
  byte fails, Dial.cpp line 0x171); between tokens spaces, tabs, CR, LF and comments (`/`
  to the next CR). Id and text may not contain CR/LF (lines 0xf8, 0x128). After `GOTO`
  (case-insensitive) the reader skips one more byte and any spaces; the target runs to
  the line end. At most 700 blocks (lines 0x106, 0x15d). Ids and targets are lowercased;
  after parsing every target is replaced by its block, `fin` meaning "end of dialogue",
  an unknown target failing init (line 0x9b). The 12-byte block record is {id, text,
  next}. Corpus: 694 blocks, 181 end in `fin`, every target resolves, no comments.
- **Used by:** formats/README.md "LOC text files"; `loctext.py`.

### E-0201 — LABELS.TXT: `#id#` `<text>` pairs, comments, 450 at most (2026-10-07)
- **Source:** CHINE.EXE `Label::load` 0x410280 ("labels.txt"), `Label::parse` 0x410300
  (errors "Labels Init Failure." Label.cpp 0x62..0x98), `Label::lowercaseIds` 0x410570;
  corpus LABELS.TXT.
- **Shows:** pairs `#id#` then `<text>`, strictly alternating (two ids or two texts in a
  row fail); whitespace and `/` comments between them; the id may not hold CR/LF, the
  text may span lines (it ends at the first `>`). A pair written with no whitespace
  between `#id#` and `<` also fails: both tokens are taken in one pass and the pass's
  end state is compared with the previous pass's. At most 450 (0x1c2) labels; ids
  lowercased. Corpus: 415 labels, ids unique, 23 comment lines (`/ -----`, `//LÉGENDES`).
- **Used by:** formats/README.md "LOC text files"; `loctext.py`.

### E-0202 — MINUTES.TXT: `#id#` `<text>` entries found by scanning (2026-10-07)
- **Source:** CHINE.EXE `Minutes::load` 0x4119f0 ("Minutes.txt"), `Interface::zeroLineEnds`
  0x40a5b0, `Minutes::parse` 0x411900 (entries {id, text} at 0x500cf8, count 0x500f04);
  corpus MINUTES.TXT.
- **Shows:** 0x40a5b0 first turns every CR outside `<...>`, and the byte after it, into
  NUL (its loop runs to `i <= size`, one byte past the buffer). The parser then repeats:
  scan to `#`, skip the `#` run, the id runs to the next `#`, scan to `<`, the text runs
  to `>` (line breaks allowed). No comments, no error checks; it resumes from the text's
  start, so a `#` inside a text would start an entry. At the buffer end it records one
  more entry past the end before stopping (count = entries + 1). 50 slots
  (0x500cf8..0x500e88), no bound check. Corpus: 45 entries.
- **Used by:** formats/README.md "LOC text files"; `loctext.py`.

### E-0203 — LISTE.TXT: the documentation index, grouped by letter (2026-10-07)
- **Source:** CHINE.EXE `Interface::loadIndex` 0x40b3e0 ("Liste.txt", "-%c-" 0x45c788,
  "%s/%s" 0x45c780, 100-byte rows at 0x48f738, count 0x4ff9a0); disassembly
  0x40b492..0x40b4da (the `%c` is the byte right after the `#` run); corpus LISTE.TXT.
- **Shows:** after 0x40a5b0, a loop: scan to `#`, skip the `#` run, remember the next
  byte C, scan to the next `#`. If that is `##`, nothing is built (a `##name##` line).
  Otherwise a header row `-C-` is written, then entries until the next `##`: `#id#`, scan
  to `<`, text to `>`, row `id/text`. So `##A` makes the group header `-A-`; after a
  `##name##` section line the next group's C is the NUL left by the line end, giving the
  row "-" (the string stops at the NUL); the section's `<title>` is never read. Text
  outside `#id#` pairs is passed over. Corpus: 23 letter lines, 3 sections, 119 entries,
  one orphan `<The Imperial House (Neiwufu)>` (line 195, no id): 140 rows, 21 headers.
- **Used by:** formats/README.md "LOC text files"; `loctext.py`.

### E-0204 — Fichetxt.txt: themes, fiches, captions, links, tables (2026-10-07)
- **Source:** CHINE.EXE `Interface::loadDoc` 0x40a5f0 ("Fichetxt.txt", French error texts
  0x45c4c4..0x45c758 "Label de thème manquant ...", "Doc Init Failure." Interface.cpp
  0x93c..0xaab), `Interface::countDollars` 0x409670, "<>" 0x45c76c; corpus Fichetxt.txt.
- **Shows:** after 0x40a5b0: themes `##label##` `<title>` (exactly two `#`, else error
  0x949), each holding fiches and closed by `###`. A fiche: `#label#` (one `#`),
  `<title>`, then `!tga!` (scan to `!`, error on `<`). With a picture name: `<caption>`
  `<text>`, then up to 10 `$link$` (fiche labels); the count of `$` in the text / 2 must
  equal the number of links (error 0xaab). Without one (`!!`): a table of rows `<a>` `<b>`
  (b exactly `<>` = none), each followed by up to 10 links, kept in a separate store (20
  rows, 0x418-byte records at 0x4ce060). A fiche ends at `##`. Theme records are 0xc8c
  bytes at 0x494558 ({label, title, count, 50 fiches of 0x40 bytes: label, title,
  caption, text, tga, links[10], link count}). The link-count variable is not reset for
  table fiches, so a table fiche right after a picture fiche with links would fail (not
  the case in the corpus). The scans between tokens pass over stray bytes: the corpus has
  a `,` after `$fiche 23$` and a repeated `!089!` line (7 bytes). Corpus: 8 themes, 122
  fiches (120 with a picture, 2 tables, 32 rows, at most 19), 363 links, at most 22
  fiches in a theme.
- **Used by:** formats/README.md "LOC text files"; `loctext.py`.

### E-0205 — CREDITS.TXT: pages of lines, `#` headings, `//` page breaks (2026-10-07)
- **Source:** CHINE.EXE `credits::run` 0x403b10 ("credits.txt" 0x45bff0; colours 0xfb20
  and 0xffff; 30-entry line table; 5000 ms timer test); corpus CREDITS.TXT.
- **Shows:** after 0x40a5b0 (line ends become NUL), one page every 5 s: lines until a
  line whose first or second byte is `/`; a line starting `#` is a heading (drawn in
  RGB565 0xfb20, others 0xffff), each line centred on x = 320, 20 px apart, the block
  centred on y = 240. After the break all `/` and NUL bytes are skipped (blank lines
  after `//` vanish). The `##` line is read as a heading with no text; the end test
  compares the byte after the line scan (always NUL) with `#`, so it never fires and the
  credits end only when the scan passes the buffer end. Up to 30 lines a page. Corpus: 22
  pages, 215 lines (53 headings), at most 25 lines a page.
- **Used by:** formats/README.md "LOC text files"; `loctext.py`.

### E-0206 — ZIK music: headerless 22050 Hz 16-bit stereo PCM, looped whole (2026-10-07)
- **Source:** CHINE.EXE `Music::update` 0x412740 (opens the name set by `Music::setName`
  0x412710, reads the first 0x80000 bytes, calls 0x415dc0 with rate 0x5622, bits 0x10,
  channels 2, loop 1; refills 0x4000-byte pieces of the 512 KiB ring; at the file end
  seeks to 0 (0x438c79) and keeps reading); 0x421990 builds a PCM WAVEFORMATEX (tag 1)
  from those values; `Script::gotoPlace` 0x41f190 picks the file by the place's first
  three letters (table 0x45ed10: PNE AIE AIO CTP CGC Allee; CPC LGE SPF Bureaux1; LGA BPI
  ESP NWF BAN BDA Bureaux2; PDC Concub; JIX Jardins; CTH CHS SHS SalleHS) + ".zik"
  0x45ee0c in `Data\Music\`; volume 0..127 fades by 10 a tick; corpus 6 files.
- **Shows:** no header and no loop points: the whole file is the loop. All 6 sizes are
  multiples of 4; read as LE 16-bit stereo the signal is smooth (mean |delta| 450..1050),
  shifted by one byte it is noise (about 21800). Lengths 55.2..77.3 s; 0..154 leading
  zero bytes. The Cryo APC decoder (0x43750d) is not used for music.
- **Used by:** formats/README.md "ZIK"; `zik.py`, `zik.ksy`.

### E-0207 — chine.cfg field 4 is the save mode: 1 automatic, 0 manual (2026-10-07)
- **Source:** CHINE.EXE options screen 0x40e630 (the fourth button's value names are the
  labels `auto` 0x45c934 / `manu` 0x45c92c indexed by the in-memory flag 0x48f238; the
  second and third use `non`/`oui` 0x45c940/0x45c93c); LABELS.TXT `#save#` "Save : ",
  `#auto#` "Automatic", `#manu#` "Manual"; menu dispatcher 0x406360 (flag 0: the emblem
  chooser 0x410da0; flag 1: the plain screens 0x41e930 "Fondlod" and 0x41e090 "Fondsvg");
  0x41f190 calls the automatic save 0x4115b0 after each place change.
- **Shows:** adds to E-0501: field 4 = 1 means automatic saving (flag 0: one save per
  player emblem, rewritten on every place change), 0 means manual (named) saves. Fields
  2 and 3: 1 = yes. Defaults with no file (0x4056c0): flag 0 (automatic) but field 4 = 0,
  so writing the file without touching that button stores "manual". Corpus file: normal
  speed, subtitles on, music on, manual. Answers Q-0500.
- **Used by:** formats/README.md "chine.cfg"; `cfg.py`, `china_cfg.ksy`.

### E-0208 — China's save file layout, from the code only (2026-10-07)
- **Source:** CHINE.EXE automatic save write 0x4115b0 / read 0x4114b0 ("%s_game%d.sav"
  0x45cd58 with `Data\Saved\` 0x45ee4c and slot + 1, slot 0x48f22c in 0..11), named save
  write 0x4117b0 / read 0x4116b0 ("%s%s.sav" 0x45cd68; the name is typed on 0x41e090
  from A-Z, 0-9 and space, up to 18), slot scan 0x406d20 (`_game1..12`); blocks in order:
  0x420170/0x420120 (u32 at 0x45eec8 + 12k while < 0x45f96c: 227 dwords), 0x417d40/
  0x417ce0 (two u32 at 0x45d5e4 + 0x30k while <= 0x45dca7: 36 pairs), the place name from
  0x41f3c0 (256 bytes of a stack buffer), floats 0x53485c and 0x534844, 0x4125c0/0x412510
  (u32 count 0x500e88, then per minute u32 strlen + the bytes of its 15-byte slot at
  0x51e3c8 + 15k); after a read the game goes to the saved place (0x41f680, 0x41f190).
- **Shows:** the layout in formats/README.md "Save games" and `china_sav.ksy`: 1464 bytes
  + minutes. The variable table holds 220 named entries (MODE_VISITE, CHAPITRE, ...), 5
  with an empty name, an id-0 terminator, and the 227th dword is padding after the table;
  ids run 1..0xe1 except that 191 appears twice and 192 never. The object table has 35
  entries (LISTE_BOITES .. CLE_JARRE); the 36th pair is the 8 bytes after it. The place
  name's bytes after its NUL are stack leftovers. Minute ids are written without NUL and
  read into slots that are not cleared first, and the count is not checked against the
  50 slots. No save exists in the corpus: nothing here is checked against a real file.
- **Used by:** formats/README.md "Save games"; `sav.py`, `china_sav.ksy`.

### E-0800 — China's fonts: eleven CRF files into slots 0..10 (2026-10-08)
- **Source:** CHINE.EXE 0x413300 (MyFont load all: `font0%d.crf` for n = 1..9, then
  `font%d.crf` for n = 10..11, each into slot n-1; any failure is the `Font load Failure.`
  assert, lines 0x76/0x81), 0x413420 (load one: path = data folder + `Fontes\` + name, whole
  file read by 0x4135d0; byte-swaps the BE u16 at file +0x0c and +0x0e (line height), then
  walks glyph records from file +0x30, byte-swapping their five u16 and storing a pointer
  per character 0x20..0xFF until the file ends), table base 0x51eba4, 0xe0 pointers (0x380
  bytes) per slot, pointer for character c of slot s at index s*0xe0 + c; the file pointer
  sits at index 0x1f of the slot.
- **Shows:** slot n-1 = `DATA/FONTES/FONT0n.CRF` (FONT01 = slot 0 .. FONT11 = slot 10).
  Side effect of the stride: slot s's pointer for 0xFF is slot s+1's index 0x1f, which the
  next load overwrites with that file's buffer, so character 0xFF of fonts 0..9 draws
  garbage (original quirk; no use of 0xFF found).
- **Used by:** spec/china-boot.md Text and colours.

### E-0801 — China's glyph drawing, text drawing and measuring (2026-10-08)
- **Source:** CHINE.EXE 0x413750 (draw one glyph), 0x4136d0 (draw string: args dest, y, x,
  text, font slot), 0x4138b0 (glyph advance), 0x413900 (string width), 0x413940 (string
  height; disassembly checked: `mov ecx,[ecx*4+0x51ec24]` = pointer index c+32), global
  0x45cffc = 1 in the EN-ISO exe data and never written, pitch global 0x48f25c, 0x1e0 = 480.
- **Shows:** glyph record = u16 h, u16 w, s16 off_x, s16 off_y, u16 advance, h*w bytes (as
  `crf.ksy`). A character < 0x20 is drawn as '?'; a missing glyph draws nothing and advances
  0. Top-left = (x + off_x, y + off_y + font line height (+0x0e) - 2), each clamped to >= 0
  (the glyph shifts, it is not cut); rows from 480 down are cut; columns are not clipped.
  Every non-zero bitmap byte is written as the current colour (one 16-bit store); zero bytes
  are left alone (mode 0x45cffc = 1; the other mode, never reached, writes 0xffff there). No
  shadow, no outline, no blending. Advance = advance + 1. String: 0x0a returns x to the start
  and adds the height of the space glyph (slot's 0x20 h) to y; 0x0d and other control bytes
  are skipped. Width = sum of (advance + 1) on the last line. Height = max glyph h, but it
  reads glyph c+32 (original bug), so it is only approximate.
- **Used by:** spec/china-boot.md Text and colours.

### E-0802 — China's text colour is given in RGB565 and converted for a 555 screen (2026-10-08)
- **Source:** CHINE.EXE 0x4133f0 (set colour: if pixel-format global 0x48f270 == 15,
  keeps bits 0..4 and puts (c >> 1) & 0x7fe0 above them; stores into 0x45d00c, initial
  value 0xffff in the exe data); callers in 0x407140 pass 0xffff / 0x7020 / 0x9a73; 0x405740
  sets 0xffff then draws `Chargement en cours...` with slot 3 at y 200, x 50; 0x407140 draws
  the menu labels with slot 1 (measures them with slot 0).
- **Shows:** constants are R5G6B5: 0xffff white, 0x7020 = (14, 1, 0) = RGB (115, 4, 0) dark
  red, 0x9a73 = (19, 19, 19) = RGB (156, 77, 156) greyish mauve. Menu labels use
  FONT02.CRF, the loading text FONT04.CRF in white.
- **Used by:** spec/china-boot.md Text and colours, Main menu.

### E-0803 — China's pixels are converted to the display format at load time (2026-10-08)
- **Source:** CHINE.EXE 0x416510 (MyTga load: 16-bit TGA read raw, then if 0x48f270 == 16
  0x4200f0 turns X1R5G5B5 into R5G6B5 (low 5 bits kept, the rest shifted left 1, green low
  bit 0); 24-bit TGA via 0x4169c0 (to 555) or 0x416a10 (to 565), else `TGA load Failure.`);
  0x416ca0 (MyWarp init: 0x48f270 == 15 selects HNM set-up 0x438ffa -> 0x4393d4, else
  0x438ff0 -> 0x439330, which fills the HNM decoder's colour tables with R<<11, G<<5 (6-bit),
  B for 565, or the 555 equivalent), and the warp shading tables 0x442590 / 0x442610.
- **Shows:** the game's canonical pixel format is whatever the screen is (555 or 565); every
  image, video and constant is converted to it once (images when loaded, HNM inside the
  decoder, colours in 0x4133f0). Files: TGA/SPR are X1R5G5B5; constants are R5G6B5. An
  engine on a 565 surface converts 555 file pixels and uses constants as they are.
- **Used by:** spec/china-boot.md Text and colours.

### E-0804 — China's frames are not paced: no timer wait, no vsync (2026-10-08)
- **Source:** CHINE.EXE 0x4064e0 / 0x406530 (no wait call in the loop); 0x415900 (MyScreen
  flip) calls 0x421200 with 0; 0x421200 full-screen with argument 0: retries
  IDirectDrawSurface::BltFast (vtable +0x1c, flags 0) of the back buffer to the primary until
  it succeeds (restoring surfaces on DDERR_SURFACELOST 0x887601c2); only a non-zero argument
  takes GetFlipStatus + Flip(DDFLIP_WAIT); windowed uses Blt with SRCCOPY. 0x406880 reads
  0x416c90 (QueryPerformanceCounter in ms, 0x4419c9) only to compute 1000 / frame time for
  the frame-rate display; 0x4170a0 and 0x417230 use no time. 0x438110 (Cryo timeSetEvent
  timer) has no callers; MyTimer 0x416bb0 only creates the timer object.
- **Shows:** the warp view runs as fast as the machine draws; edge-scroll velocity (E-0509)
  is per frame, so the turning speed depended on the PC. The original has no frame rate to
  copy (Q-0800).
- **Used by:** spec/china-boot.md Main loop.

### E-0007 — China's code map corrected: place procedures fill 0x421f00..0x436e20 (2026-10-08)
- **Source:** E-0700 (the 270 place procedures reached only through function pointers),
  E-0507 (`Script_Start` 0x436db0, `pne140` 0x431050).
- **Shows:** supersedes E-0004's "then a Cryo library block" for 0x422000..0x437000: the
  game's own place procedures occupy 0x421f00..0x436e20 (undefined in the first Ghidra
  analysis); the Cryo library code (APC 0x43750d.., timer, file I/O, DirectInput) follows
  them, and the warp projection is at 0x441b80..0x44205c (E-0601..E-0604).
- **Used by:** CLAUDE.md Ground truth (China code map).

### E-0008 — China editions and their detection files (2026-10-08)
- **Source:** extraction of the DVD (`games/china/discs/dvd-multi/dvd1/`) and the French
  CD (`games/china/discs/fr-cd/cd1/`); md5 of the first 5000 bytes and sizes of
  `CHINE.EXE` and `DATA/LOC/LOAD.HNM` per edition; ScummVM `--detect` on each folder.
- **Shows:** the DVD holds `DVD/<DE FR IT NL SP SW US>/`, each a full CD tree
  (`CHINE/CHINE.EXE` 578,560 B, its own md5 per language); `US` is byte-identical to the
  English CD's data. Per language only `LOC/` (six texts, `LOAD.HNM`, `PINCEAU.HNM`),
  `LOC/VOICES/` (dubbed), eight subtitled `HNM/*.HNS`, `INTERF/FONDTITR.HNM` and `CD.HNM`
  differ. The FR CD's `CHINE.EXE` is 573,952 B (Templier's `8850a946…`, E-0002); its data
  matches the DVD's FR folder in size. `CHINE.EXE` + `LOAD.HNM` tell all nine apart; the
  detection entries in `detection_tables.h` use them, and each language folder of the DVD
  is a game folder of its own.
- **Used by:** detection (GType_CHINA).

### E-0900 — China's generic zone handler 0x41f430: hover branch, click branch, press latch (2026-10-08)
- **Source:** CHINE.EXE `0x41f430`; `0x414fb0` (mouse poll: 0x48f294 = left button down,
  0x48f298 = right down; latch 0x48f29c cleared whenever the left button is up);
  `0x415370` (zone under the hot point into 0x48f27c, -1 when none or disabled);
  `0x406530` call order (0x414fb0, 0x415270, 0x403640, 0x415370, then the scene).
- **Shows:** the handler first clears the hover label. No zone (index -1) or a disabled
  zone: nothing else (the cursor stays as 0x415270 chose it). If the latch is set or the
  left button is up, it is a hover frame: the index is reset to -1 (the place sees no
  click) and the cursor is set by type: 0 sprite 8 in a warp, 12 otherwise; 1 sprite 8;
  2 and 3 sprite 9; 4 sprite 10 with empty hands, else the held object's cursor; 6 sprite
  14 with empty hands, else the held object's cursor; 7 label set (text), cursor
  untouched; 8 with empty hands label set (title) and sprite 15, holding something
  nothing; 9 sprite 16; others (5) the default cursor 0x415230. If the button is down and
  the latch clear, it is the press frame: types 0, 2, 3, 4, 5 set the latch and, in a
  warp, turn to the cursor's top-left (0x417500), zoom by the zone's arg (0x417400), then
  set the view angles to the zone's alpha/beta when alpha >= 0.0 (0x450268); type 6 sets
  the latch only; type 8 with empty hands opens documentation entry <key> (0x40c5a0),
  re-enters the place (0x41f170) and returns; all other types return with nothing done
  and no latch (so the place sees a type 7/9 zone index on every frame the button stays
  down). After types 0..6: a non-zero target is a goto (0x41f190, returns 1); otherwise
  the index stays in 0x48f27c for the place's own code. Zone lookups use the hot point
  (E-0901); the turn uses the cursor's top-left.
- **Used by:** spec/china-zones.md (Hover, Click and transitions).

### E-0901 — China's cursor sprites, hot points and default cursor (2026-10-08)
- **Source:** CHINE.EXE `MyMouse.cpp` init `0x414d20` (loads the 18 names at 0x45d1d0
  through the SPR loader 0x41f760, zeroes each sprite's hot-point fields +0x0c/+0x10, then
  gives sprite 13 the hot point (1, 45)); `0x415440` (hot point = top-left + hot field, or
  + half the sprite size on an axis whose field is 0); `0x4151a0` (set cursor by index),
  `0x4150e0` (set cursor by sprite; in still mode the top-left moves by the size change);
  `0x414fb0` (top-left clamped to 0..640-w, 0..480-h; starts at 320, 240); `0x415270`
  (default cursor per frame), `0x415230` (held object's cursor, or sprite 11); `0x415340`
  (cursor drawn at its top-left); corpus `DATA/SPRITES/CURSEURS/*.SPR`,
  `DATA/SPRITES/OBJETS/*.SPR` headers.
- **Shows:** table: 0 tri270, 1 tri90, 2 tri0, 3 tri180, 4 tri315, 5 tri45, 6 tri135,
  7 tri225, 8 doigt, 9 voir, 10 prendre, 11 ptroug, 12 doigt, 13 inter, 14 util,
  15 interrog, 16 bouche, 17 pointact (`.spr`). The files' own hot fields are discarded,
  so every cursor's hot point is its centre (w/2, h/2), except inter (1, 45). Default
  cursor each frame in a warp, from the top-left (x, y): x < 100: y < 100 sprite 4,
  y > 380 sprite 7, else 0; x > 540: y < 100 sprite 5, y > 380 sprite 6, else 1;
  otherwise y < 100 sprite 2, y > 380 sprite 3, else the held object's cursor (empty
  hands: sprite 11). In a still: the held object's cursor or sprite 11. Object cursors
  keep their file hot fields: all 34 `R_*.SPR` are 30x30 with hot 0, 0 (so centre),
  `C_*.SPR` 36x36 hot 1, 1.
- **Used by:** spec/china-zones.md (Hover).

### E-0902 — China's hover label: position, box and font (2026-10-08)
- **Source:** CHINE.EXE `0x4106e0` (store key and text, capture the cursor top-left),
  `0x4106a0` (offsets 20, 20), `0x4107c0` (place and clip), `0x410880` (draw), `0x4082a0`
  (box blend), `0x410600` (LABELS.TXT lookup, key lower-cased in place; used by both the
  type 7 and type 8 creators); `0x406530` (0x4107c0 runs after the warp render only, not
  in still mode); corpus: 95 label keys used, 4 not in LABELS.TXT (`edicule`, `poesie`,
  `vase`, `vase_spf`); 35 doc keys, all in LABELS.TXT and Fichetxt.txt.
- **Shows:** text = the zone's looked-up string (type 7 label text, type 8 entry title),
  measured with font slot 0. x = cursor x + 20, or 638 - width when x + width + 2 would
  reach 640; y = cursor y + 20; nothing drawn unless y + 20 < 479. A box 15 rows by
  width + 1 at (x - 2, y - 2) is blended halfway towards (10, 10, 10) in 5-bit units (on
  a 565 screen the red and green terms miss their shift, so those channels just halve:
  original quirk), then the text in slot 0, black at (x + 1, y + 1) and white 0xFFFF at
  (x, y). Missing keys show "ACCES LEGENDE INCONNU" (labels) or "ACCES BASE
  DOCUMENTAIRE INCONNU" (docs).
- **Used by:** spec/china-zones.md (Hover).

### E-0903 — China's click transition, goto and cross-fade (2026-10-08)
- **Source:** CHINE.EXE `0x41f430`, `0x41f190` (goto: current = proc, entry pending,
  display mode 0, zone index -1, `0x403640`, music by name), `0x41f170` (goto current),
  `0x402d50` (warp: load, mode 1, cross-fade flag 0x48f284 = 1), `0x406530` (mode 0 draws
  nothing; mode 1 with the flag set and the skip flag 0x48f1ec clear: copy the front
  screen, render the new view into a second buffer, then loop 0x404e80 + flip until it
  returns 0), `0x404e80` (counter 0x48f198 += 16 per call, t = min(counter, 256); returns
  0 and resets at >= 0x130; disassembly 0x405300..0x405317), `0x406880` (0x48f1ec = 1
  after the interface screen), `0x417230` (render clears the flag); corpus
  (`china_places.py`): zone arg 0 in all 608 resolved type-0 and all 23 type-2 creations
  (one type-0 call unresolved by the dumper), type 4 forces 0; 93 of 609 type-0 zones
  carry angles.
- **Shows:** press on a go/look/take zone in a warp: 32-frame turn (E-0606), zoomIn(arg),
  which is zoomIn(0) in all data (no zoom frames, only the hfov reset), alpha/beta from
  the zone when alpha >= 0 (only type 0 can carry them; types 2 and 4 store -1), goto.
  On the next tick the target's entry loads its warp and that frame draws the cross-fade:
  19 frames; frame k (1..19) writes every other column (odd columns on odd k, even on
  even k) as old - (old - new) x min(16k, 256) / 256 per colour channel into the back
  buffer, the other columns keeping the previous frame, so frame 16 finishes the even
  columns and 17 the odd ones; then normal frames. Music is ticked between frames; no
  timer. Skipped once after returning from the interface screen.
- **Used by:** spec/china-zones.md (Click and transitions).

### E-0904 — China's zone creators: argument lists and visit-mode rules (2026-10-08)
- **Source:** CHINE.EXE `0x403060`, `0x4030a0`, `0x403290`, `0x4032f0`, `0x403100`,
  `0x403210`, `0x4031b0`, `0x403590`, `0x4035d0`, `0x4202e0`, `0x420330`; record layout
  rect[4], disabled, type, target, arg, alpha (float), beta (float).
- **Shows:** go(rect, disabled, target proc, arg, alpha double, beta double); look(rect,
  disabled, target, arg); take(rect, disabled, target); use(rect, disabled);
  label(rect, disabled, key); doc(rect, disabled, key); talk(rect, disabled); alpha and
  beta are -1 for all but go. In visit mode (variable 0 != 0) look, take, use and talk
  are created disabled; a label is created disabled outside visit mode and as given in
  it; go and doc ignore the mode. Enable(i) clears the disabled flag unless visit mode is
  on and the zone is use, label or talk (then nothing changes); disable(i) sets it. Add
  copies the rect and zeroes the rest; past 40 zones the add is ignored.
- **Used by:** spec/china-zones.md (Zones, Place API).

### E-0905 — China's object table and object API (2026-10-08)
- **Source:** CHINE.EXE table 0x45d5c0 (36 records of 48 bytes, record 35 empty; read
  from the en-iso CHINE.EXE); `Object.cpp` loader `0x417a30` (c_ and r_ sprites required,
  i_ optional, suffix `.spr` 0x45e1d0; held = 36 at the end), `0x417c90` (free),
  `0x417e70` (reset: state 0, slot -1), `0x417ce0`/`0x417d40` (save/load each object's
  state and slot), `0x417df0` (cursor sprite = +0x14), `0x417e50`/`0x417e60` (held object
  0x45d5b8, 36 = none), `0x417e10`/`0x417e30` (replace the +0x2c / +0x20 strings),
  `0x403440`, `0x403480`, `0x4034f0`, `0x4150e0`.
- **Shows:** record: +0 index, +4 name, +8 `c_` file (loaded to +0x10), +0x0c `r_` file
  (loaded to +0x14: the hand cursor), +0x18 `i_` file (loaded to +0x1c; objects 0..18
  only), +0x20 a document key (`lboites`, `origine`, ...; 0..18 only), +0x24 state,
  +0x28 slot (-1), +0x2c a key (the name again). To inventory: only from state 0, to 2.
  To cursor: unless already 1 or 2: the held object (if any) goes to 2, this one to 1,
  becomes held and its r_ sprite the cursor. Destroy: drops it from the hand if held,
  state 3, clears 0x4ffa24. The zone handler never changes object state: a take zone only
  turns and goes; the place's code moves objects.
- **Used by:** spec/china-zones.md (Objects).

### E-0906 — China's stills, videos and screen fade (2026-10-08)
- **Source:** CHINE.EXE `0x402e20` (still: mode 2), `0x415410` (still hit test: hot point
  in screen coordinates, no projection), `0x406530` (mode 2 draws the still and the
  cursor, no label), `0x402cf0` (pause music 0x412bb0, play `<Hnm dir><name>.hns` with
  the HNS player 0x4146c0, resume 0x412bd0), `0x4146c0` (stops on Escape or the left
  button), `0x403860` (blend the current screen to black with 0x404e80 until done);
  corpus: of 87 procedures that show a still and load no warp, 54 have a go zone across
  the full width at the bottom (left 0, right 639, bottom 479, top 398..460).
- **Shows:** close-ups are places in still mode with zones in screen pixels {top, left,
  bottom, right}; the usual way back is a bottom-strip go zone to the place (finger
  cursor 12), sometimes target 0 with the place's code choosing. Videos block, are
  skippable by Escape or a left click, and pause the music.
- **Used by:** spec/china-zones.md (Place API).

### E-0710 — China's place procedures are loop-free MSVC code of a few shapes (2026-10-08)
- **Source:** CHINE.EXE .text 0x421f00..0x436e20, all 270 procedures disassembled by
  `engines/cryomni3d/tools/china_places.py` (capstone): no backward jump; branches only
  `je/jne/jl/jle/jg/jge` after `cmp eax, n` (1,169), `test eax, eax` (661),
  `cmp dword ptr [0x48f27c], n` (96) or `test al, n` (4, `soupir`); call arguments only
  pushed immediates or `push eax`; other register use: `inc eax` (var + 1, 7), `or al, n`
  (bit set, 4), `sete al` + `mov byte ptr [0x48f2a8], al` (`jixw210`),
  `mov dword ptr [0x48f27c], -1` (clear the clicked zone, `bpiw202`, `jixw121`),
  `push esi`/`mov esi, eax`/`sub esi, [0x530bf8]` (`fight`: a timer from 0x416c90, E-0804),
  `lea eax, [esp+8]` passed to the interface screen 0x40efd0 (`fight`, E-0508). Every
  procedure dispatches msg with `cmp eax, 1/2/3` and enters its entry part right after
  `cmp eax, 3; jne <event>`. The compiler shares code tails between branches (a jump into
  another branch's identical `push ...; call` sequence, e.g. `aie600b` 0x42b795 ->
  0x42babf, `registre` 0x424692 -> 0x4246d9, `pdc170` 0x42f38e) and threads jumps past
  tests it knows fail (`aie600b` 0x42b8a9).
- **Shows:** a procedure is fully described by its calls, the values they test and an
  acyclic branch graph; the dumper executes it symbolically (pushes, eax/esi, flags),
  duplicates shared tails per path, and models every instruction met (0 left unmodelled).
- **Used by:** `china_places.py`, `games/china/docs/places.md`.

### E-0711 — China's place procedures rebuilt as if/else with and/or conditions (2026-10-08)
- **Source:** `uv run engines/cryomni3d/tools/china_places.py --selftest`: chains of
  branches sharing one exit fold into `and`/`or` conditions (MSVC's short-circuit
  layout); if/else is rebuilt from post-dominators, with returns other than the
  procedure's main one (and tails ending in them) treated as early returns. Checked by
  walking the instruction graph and the rebuilt tree side by side with random values for
  every tested expression: identical call sequences in 162,000 runs over all 270
  procedures (both parts); a deliberately broken rebuild fails 26 procedures. pne140
  (0x431050) comes out as the worked example of places.md (E-0705): the zone 1/2 enable
  test `(CHAPITRE == 1 and not XNED1011 and not GICD1011 and not GIDD1011) or (CHAPITRE
  == 9 and ENED3111 == 1 and not GICD3111 and not GIDD3111)` (0x431178..0x4311e9), the
  same test per guard under `on zone 1` / `on zone 2`, and `on zone 3: view 1.58, 0; if
  MODE_VISITE == 1: goto pne210` (0x4313f5..0x431426). Also checked by hand against the
  disassembly: table11 (close-up, use zones), meuble1 (signed range tests), registre and
  aie600b (shared tails, jump threading), fight (timer, unknown calls), soupir (bit
  tests), jixw121 (zone cleared then retested), jixw210 (`sete`), go1/espw101 (puzzle
  result, var + 1), shs240 (ending), bpiw202 (23 zones), victime, Script_Start (entry
  that returns, so its event part never runs on entry).
- **Shows:** the structure printed by the dumper is the procedure's control flow.
  Limits: shared tails are printed once per branch (9 procedures print more calls than
  the code holds: pdc010, pdc170, aie600b, lgaw101, table14, espw102, fight, registre,
  soupir); zones created under a condition print as `zone ?` (jixw120, 2 zones);
  callees with no meaning yet print as `call 0x<addr>`: 0x403520, 0x403540, 0x403560,
  0x405aa0, 0x414c70 (4 procedures); 266 procedures have none.
- **Used by:** `china_places.py`, `games/china/docs/places-logic.md`.

### E-0712 — China's place logic, all 270 procedures (2026-10-08)
- **Source:** `uv run engines/cryomni3d/tools/china_places.py --md >
  games/china/docs/places-logic.md` (from the EN ISO CHINE.EXE; E-0710, E-0711).
- **Shows:** each place's entry and event part as structured pseudo-code; `--json` gives
  the same as statement trees for code generation. Answers Q-0702.
- **Used by:** `games/china/docs/places.md`, `games/china/docs/places-logic.md`.

### E-0950 — China's place sounds: a two-entry queue on sound channel 3 (2026-10-08)
- **Source:** CHINE.EXE 0x4037e0 (queue), 0x403640 (pump, run every frame, E-0508),
  0x4039a0 (play and wait), 0x4039f0 (stop), 0x416020 (channel busy), 0x415f90 (channel
  stop), 0x415f60 (slot loop flag), 0x415d30 (slot -> channel), 0x41fe30 (`<L>:\Chine\Data\`
  + `Loc\` + `Voices\` 0x45ee70), 0x41fc80 (`<L>:\Chine\Data\` + `Sound\` 0x45ee30),
  `%s%s.wav` 0x45bfb8; queue at 0x48ce00 (two entries of 0x104 bytes: name, then state at
  +0x100), index 0x48cdf8, loop marker 0x48cf04; corpus DATA/SOUND 25 WAVs.
- **Shows:** queue(name): pump first; if channel 3 is still playing, the call is dropped;
  else the name goes into entry 0 (index 1 folds back to 0) unless that entry is already
  pending. Pump (only when channel 3 is idle): free the previous sound, play the pending
  entry from `Loc\Voices\<name>.wav`, else `Sound\<name>.wav` (a missing file drops the
  entry silently), on channel 3 through buffer slot 3, once (state 2 would loop, but no
  code stores 2: no place sound loops), then advance the index and clear the entry.
  Volume is the slot's default (not set here). play-wait(name): wait for channel 3 to be
  idle, queue, pump, then busy-wait until channel 3 ends (no frames drawn, no input).
  stop: stop channel 3 and clear the loop marker; Escape in the frame loop calls it (E-0508).
- **Used by:** spec/china-zones.md Sounds; `china_places.py` names.

### E-0951 — China's voice-only line (`dialogue` 0x403350) (2026-10-08)
- **Source:** CHINE.EXE 0x403350, 0x404d00, 0x403eb0 (DIAL.TXT block, E-0200), 0x40e2b0
  (subtitle band), 0x408510 (zero a rectangle), 0x40df40 (word wrap), 0x4136d0, 0x4133f0
  (E-0801/E-0802), 0x412c30/0x412c40 (music state 6/3), 0x412740 (state 6 lowers the music
  volume by 1 per tick down to 20; state 3 raises it by 10 per tick to 127, E-0206).
- **Shows:** waits for channel 3 (place sounds) to end, then finds the DIAL.TXT block;
  redraws the current display once and flips; sets the music to "duck". For each block of
  the GOTO chain: play `Loc\Voices\<id>.wav` (22050 Hz mono 16-bit, corpus) on channel 1;
  draw the warp view and the block's text as a subtitle (no subtitle-option test here);
  flip; busy-wait until the voice ends or Escape (DIK 1) is down (Escape ends only the
  current block; held, it skips the rest); next block until `fin`. Then music back to
  state 3. The music tick does not run inside this loop, so the duck has no audible
  effect until the line is over (quirk). A missing WAV returns 3 (error).
  Subtitle band (0x40e2b0, shared with E-0952 and the endings): text wrapped to 630 px in
  font slot 1 into n lines; a black band of n x 15 + 10 rows across the full width at the
  bottom (top = 480 - band); line i in white 0xFFFF at x 5, y top + 5 + 15 i; a line
  containing `$` is drawn from after the `$`.
- **Used by:** spec/china-zones.md Dialogues.

### E-0952 — China's lip-sync dialogue (`sync_video` 0x403380) (2026-10-08)
- **Source:** CHINE.EXE 0x403380, 0x404710, 0x404c60 (face frame), 0x4046b0 (loads one
  HNM), `%s%s%d.hnm` 0x45c050 under `<L>:\Chine\Data\Sync\` (0x41fdf0); speaker tables
  0x48f078 (A) and 0x48f104 (B), loaded flags 0x48f100/0x48f18c, frame counters 0x48f0fc;
  subtitle option 0x48f228; timer 0x416c90 (E-0804); DirectSound position 0x421cd0;
  corpus `SYNC/<stem>0..3.HNM` are HNM6 640x480.
- **Shows:** call (block, stemA, stemB): wait for channel 3 to end; load the four face
  loops `Sync\<stem><k>.hnm`, k = 0..3, of each named speaker (a failed load marks that
  speaker as "no face": its frames are black). Speaker of a block: A if the block id's
  first 3 letters equal the first block's, else B (A is assumed to speak first). Music to
  "duck" (E-0951), and here the music tick runs. Per block: wait for channel 1 idle, play
  `Loc\Voices\<id>.wav` on channel 1, then until the voice ends or its play position is
  within 22070 bytes (0.5 s) of the end: read the play position, average 5 samples 11025
  bytes (0.25 s) ahead of it; |average| < 1024 picks loop 3 (mouth shut), else loop
  rand()%3 (0..2), re-drawn if the same loop as last time was picked once already (0 ->
  1 or 2, 1 -> 0 or 2, 2 -> 0 or 1; only counters 0 and 1 are reset, so 2 may repeat
  more). Loop 3 is shown only if 88200 bytes (2 s) passed since it was last shown in this
  block; any 0..2 pick plays 7 frames at no less than 51 ms each: per frame the music tick,
  Escape (stop the voice and end the whole dialogue), the next frame of that speaker's
  current loop (one frame counter per speaker, wrapping at 7, decoded as a delta over the
  speaker's previous frame even across loops), copied full screen 640x480 (black if no
  face), subtitle band if the subtitle option is on, flip. No other input; the mouse and
  zones are not handled. Then the next block of the GOTO chain until `fin`; wait for
  channel 1 to end; music to state 3; free the faces. Nothing of the place is drawn: the
  face fills the screen.
- **Used by:** spec/china-zones.md Dialogues; E-0504.

### E-0953 — China's puzzle call (`puzzle(n, m)` 0x4035f0) (2026-10-08)
- **Source:** CHINE.EXE 0x4035f0, 0x405ed0 (switch), 0x406040, 0x4060e0, 0x406160,
  0x4061e0, 0x406260, 0x4062e0; init/run/close triples per source file (`F:\Chine\Sources\
  Puzzle*.cpp` asserts): Penjing 0x41c520/0x41cda0/0x41cd20, Boudha 0x41a3b0/0x41a6e0/
  0x41a660, Sceaux 0x41d020/0x41d630/0x41d540, GO 0x41b5d0, Puzzle4 0x417e90/0x4189bc/
  0x41887e, Horloge 0x41bd30, Boutons 0x41a8f0, Bombe 0x4192c0/0x419830/0x4197d0; exits of
  run checked in 0x4189bc and 0x419830; result 0x48f280, context {done 0x48f1b0, result
  0x48f1b4}, puzzle-mode flag 0x48f2a8, fatal flag 0x48f28c.
- **Shows:** puzzle(n, m): a held object goes back to the inventory (state 2, hands
  empty); puzzle mode set; run puzzle n to completion (blocking, its own loop); puzzle
  mode cleared; returns 0x48f280. n: 1 Penjing (also any n outside 2..8), 2 Bouddha,
  3 Sceaux, 4 Go, 5 Puzzle4, 6 Horloge, 7 Boutons (folder Porte), 8 Bombe. m is used only
  by 3 (Sceaux): passed to its run and preset as its result. A run ends by setting done
  and a result (Puzzle4 and Bombe: 1 solved, 0 left by Escape), after re-entering the
  current place (0x41f170) so the place's entry part runs again. Only when done is set
  is 0x48f280 updated; on an init/run error the old value is returned and the fatal flag
  is set.
- **Used by:** spec/china-zones.md Puzzles.

### E-0954 — China's remaining place callees and raw stores (2026-10-08)
- **Source:** CHINE.EXE 0x403520 (state == 2), 0x403540 -> 0x417e10 (object +0x2c),
  0x403560 -> 0x417e30 (object +0x20), 0x414c70 (DirectInput key state, DIK codes: 1
  Escape, 0x39 Space), 0x405aa0, 0x41f190 (goto: autosave 0x4115b0 unless visit mode or
  0x48f2a4), 0x405e60 (display by 0x48f200: 1 warp, 2 still), 0x4064e0/0x406360 (0x48f1fc
  ends the game loop), 0x414fb0 (0x48f298 = right button down, 0x48f2a0 cleared on
  release), 0x406880; object table values at 0x45d5c0 (object 0: +0x20 `lboites`, +0x2c
  `LISTE_BOITES`; 14: `lvierge`, `LETTRE_VIERGE`); `lvierge` place: the call pair
  (14, `LETTRE_REVELEE` 0x462050) and (14, `rebus` 0x45de8c).
- **Shows:** 0x403520(o) = object o is in the inventory. 0x403540(o, s) sets the object's
  label key (+0x2c, the LABELS.TXT name shown for it); 0x403560(o, s) sets its examine
  place (+0x20, the place procedure name opened for it, e.g. `lvierge`). 0x414c70(k) = key
  k down. 0x405aa0 (end of shs240) = the epilogue: four stills, each with a LABELS.TXT text
  in the subtitle band (E-0951): ANJFR000 + FIN_ANJING, GEN_DAFR + FIN_DAMING, CONCUFR0 +
  FIN_SHOUXIU, JONGFR00 + FIN_PRINCE; each stays 10 s or until Escape (then waits for its
  release); music ticks meanwhile. Stores: [0x48f200] = display mode (0 none, 1 warp,
  2 still); [0x48f1fc] = 1 ends play, then credits (E-0508); [0x48f2a4] = 1 skips the
  autosave of the next goto (fight -> fight2); [0x48f2a8] = puzzle mode (also set by
  jixw210); [0x530bf8] = the fight's start time; in `fight`, "right button pressed with its
  latch clear, or Space" opens the interface screen, as in the frame loop.
- **Used by:** spec/china-zones.md Place API; `china_places.py`.

### E-0955 — China's interface screen entry (0x40efd0), outline (2026-10-08)
- **Source:** CHINE.EXE 0x406880 (Space held: wait for release; or right button with its
  latch clear), 0x40efd0, 0x40f070 (2413 bytes), 0x40ff30, 0x40f9e0, 0x40fb10; 0x4013e0,
  0x410030 (`loc\voices\`), 0x411e60; rects 0x4ffa14, 0x4ffafc, 0x4ffa34, 0x4ff9bc; slot
  row y 0x1b5..0x1db (437..475), slots 0x26 (38) px wide up to x 0x259 (601).
- **Shows:** modal; redraws the current display, keeps a copy of the frame (640x480 16-bit)
  and runs its own loop over it (music ticks, cursor drawn): an inventory row of object
  slots at the bottom (hover shows the object's label text in font 3 at y 415; click takes
  it as the cursor or puts the held one back), plus buttons tested by rects (one disabled
  in puzzle mode). It ends on Space, a right click, or a button; some buttons re-enter the
  current place (0x41f170) or go to the menu (the returned value, E-0508); afterwards the
  next warp draw skips its cross-fade (E-0903). Details not traced: Q-0902, Q-0953.
- **Used by:** spec/china-zones.md Interface screen (summary).

### E-1100 — China's interface bar: open, slide, close, right latch (2026-10-08)
- **Source:** CHINE.EXE 0x40efd0 (frame copy 0x96000 bytes, band buffer 0x14500 = 65
  rows), 0x40f9e0 (copies rows from offset 0x81b00 = row 415, 0xa280 pixels blended
  halfway towards [0x45c9a0] = 0x39ca in 16-bit mode, [0x45c9a4] = 0x1cea in 15-bit),
  0x40f070 (first loop: screen offset 0x95b00 down to > 0x81b00 by 0x1400, sprite shift
  1,5,..,61; close test `local_208 || exit || key 0x39 || (held && y < 400 && was > 400)
  || (!0x48f2a0 && 0x48f298)`; slide-out 0x14000 down by 0x1400 to 0, skipped when the
  map travelled; `*result = 0` on the spiral), 0x414fb0 (the only store to 0x48f2a0 is
  `mov [0x48f2a0], ebx` with ebx 0, at 0x4150a3; byte search finds no other write),
  0x406880 (Space release wait, then `0x48f1ec = 1`), 0x419830 and 0x41d630 (open from
  puzzles; leave when the result is 0; 0x41d630 only while object 0x15 is not owned).
- **Shows:** the interface is a 65-row blended bar at y 415..479 sliding in over 16
  frames and out over 17; its close conditions; the right latch is never set.
- **Used by:** spec/china-interface.md Opening and closing.

### E-1101 — China's bar sprites place themselves (2026-10-08)
- **Source:** CHINE.EXE 0x40ec80 (loads `oeil`, `bouss`, `cadres`, `bnote`, `spirsort`
  `.spr`; rect = sprite +8 (y), +6 (x), height, width), 0x40fb10 (draws each at (x,
  y - shift + 65); compass only if !0x48f2a8 and 0x48f200 == 1; notebook only if
  variable 0 clear; spiral unless 0x48f2a8 and place name != `jixw210` 0x45cac8);
  corpus en-iso `DATA/INVENT/*.SPR` image IDs: oeil 26x26 (72,442), bouss 26x23
  (603,450), cadres 477x36 (111,437), bnote 26x24 (603,426), spirsort 26x26 (11,442).
- **Shows:** SPR `unk_16`/`unk_1a` are the sprite's screen x/y (cadres at x 111 = the
  code's first slot x 0x6f, y 437 = the slot row); the bar layout.
- **Used by:** spec/china-interface.md Layout; formats README (SPR, Q-0100).

### E-1102 — China's inventory row (2026-10-08)
- **Source:** CHINE.EXE 0x40ff30 (10 slots 0x4ffb18, objects 0x4ffa60..0x4ffaec; slot
  rebuild), 0x40f070 slot loop (x 0x6f + 0x31*i < mx < +0x26, 0x1b5 < my < 0x1db; take /
  put / swap; cursor 0x24 = empty and cursor 11), hover loop (centre 0x82 + 0x31*i ±
  0x13; 0x4136d0(screen, 0x19f, 3, label(+0x2c), 0); lines 0x412c50 (y 0x1ac, x 3 to
  centre) and 0x412cb0 (x centre, y 0x1ac..0x1b5), colour 0xf520), 0x40fb10 (c_ sprite
  +0x10 at (0x6f + 0x31*i, 0x1f6 - shift)), eye hover (cursor +0x1c when +0x18 set).
- **Shows:** ten fixed slots, take/put/swap, label with leader line, `i_` = eye cursor.
- **Used by:** spec/china-interface.md Inventory.

### E-1103 — China's document reading (2026-10-08)
- **Source:** CHINE.EXE 0x40f070 (eye click: base path + `Images\` + object +0x20 ->
  0x402e20), 0x410030 (`loc\voices\` + key on channel 10 unless object index 1; loop
  until left press: still copy 0x48f214, text 0x410600(+0x20) via 0x40e120 with box
  0x45c9a8 + 16*held, colour 0, font 1; then restore, 0x415f90(3)), then back in
  0x40f070: object to first free slot, state 2, cursor 11, 0x41f170; table read from the
  en-iso CHINE.EXE: 14 boxes, then the sprite-name strings at 0x45ca88.
- **Shows:** how a document is shown and read; only objects 0..13 have a text box.
- **Used by:** spec/china-interface.md Documents.

### E-1104 — China's notebook (minutes) screen (2026-10-08)
- **Source:** CHINE.EXE `Minutes::0x411ac0` (`Fond` still via 0x402e20; `som_spir`,
  `i_sprinv`, `fl_basr`, `fl_hautr`, `fl_basj`, `fl_hautj` .spr; string refs by
  disassembly), 0x411e60 (keys 0x51e3c8 x15 bytes, count 0x500e88, 0x411cc0 lookup,
  0x412330(text, 400, 0); first line max(0, n-22); 0x411df0(screen, first, 22, 180, 80);
  arrows step when 0x416c90 advanced 10; exit on click in the som_spir rect or key 1);
  corpus positions: som_spir (21,435), fl_hautr (138,54), fl_basr (138,405).
- **Shows:** the notebook layout, content order, scrolling and exit.
- **Used by:** spec/china-interface.md Notebook.

### E-1105 — China's map (2026-10-08)
- **Source:** CHINE.EXE `carte::0x401000` (petiplan 0x3e940 = 267x480x2, granplan
  0x1fb450 = 846x1228x2; cadre, point, ico_bat, spirs .spr), 0x4013e0 (window 0x175 x
  0x1e0 from granplan at offsets 0x48cce4/0x48cbf0; small map 0x10b wide at x 0x175;
  scroll formulas (mx-0x1b3)*0x34e/0x10b and (my-0x4f)*0x4cc/0x187 clamped to 0x1d9 and
  0x2eb; hot spot table 0x45af38..0x45bcf8 step 36 bytes; travel: 0x41f680, 0x403040,
  0x41f190, result 1; type 8: 0x40c5a0 then 0x41f170; label 0x4136d0(screen, 0x1a9,
  0x17c, ...); rects 0x48cc64 exit and 0x48cbfc -> 0x401fb0); corpus ico_bat (587,449),
  spirs (387,449), GRANPLAN 846x1228, PETIPLAN 267x480.
- **Shows:** the map's layout, scrolling and that it travels to places.
- **Used by:** spec/china-interface.md Map.

### E-1106 — China's documentation base entries (2026-10-08)
- **Source:** CHINE.EXE callers of 0x40c5a0: 0x4013e0, 0x4085d0, 0x41f430; 0x4085d0
  called by the main menu 0x407140 and calling 0x407b20 (`fond_som`, `som_*`, `fl_*`,
  `ico_indx`, `i_indinv`, `i_sprinv`); 0x40b7e0 (eight `fond*` backgrounds), 0x40b8e0
  (`fl_*`, `ico_*` sprites); no call from 0x40f070.
- **Shows:** where the documentation base is entered and which images it loads.
- **Used by:** spec/china-interface.md Documentation base.

### E-1200 — China: puzzle frame shared by Penjing, Bouddha, Sceaux, Go (2026-10-08)
- **Source:** CHINE.EXE (EN ISO) init/run/close of the four puzzles (E-1201..E-1204);
  helpers 0x416120 (load a WAV into sound channel 0..19), 0x415d30 (play a channel),
  0x416020 (channel playing), 0x405320 (message pump), 0x41fac0 (key-colour blit at x, y),
  0x414c70 (DirectInput key down), 0x41f170 (re-enter place), 0x420340 (point in rect).
- **Shows:** each init allocates 0x96000 bytes, loads its WAV(s), `setImage`s the TGA and
  copies the screen; sprite records take x = sprite+0xc, y = sprite+0x10 (from the SPR id,
  E-0505), rect y1,x1,y2,x2 from sprite height (+6) and width (+4). Each run: pump, music,
  mouse; one click per press (latch 0x48f29c); copy, draw, cursor, flip; win test after
  the flip; else Escape (DIK 1) leaves; both end with 0x41f170 and {done 1, result}.
  Clicks test rects regardless of visibility.
- **Used by:** games/china/docs/puzzles.md Common frame.

### E-1201 — China: Penjing puzzle (2026-10-08)
- **Source:** 0x41c520 (sprite pushes `Hiro_spr.spr`/`HIRONDELLE` .. `Bich_spr.spr`/
  `BICHE`, alternately into tables 0x52ca80 (flag 1) and 0x52cbd0 (flag 0), stride 0x1c),
  0x41cda0 (click flips flag 0x52ca94+0x1c*i on the first sprite's rect; hover label;
  win test at 0x41cf9b.. on the twelve flags), 0x41cd20 close. Corpus: SPR positions of
  PUZZLES/PENJING.
- **Shows:** 12 slots of two animals; win = the twelve zodiac animals (flags 0,0,1,1,0,0,
  1,0,1,0,1,1 for slots 0..11), which is a consistency check on the reading.
- **Used by:** games/china/docs/puzzles.md 1 Penjing.

### E-1202 — China: Bouddha puzzle (2026-10-08)
- **Source:** 0x41a3b0 (`B1_spr`,`B2_spr` table 0x52bb90, `R1..R3_spr` table 0x52bbd0,
  stride 0x18, flags 1), 0x41a6e0 (toggle on click; flags 0x52bbc0 armed, 0x52bbc4
  cleared computed at 0x41a85c..0x41a8c0), 0x41a660 close.
- **Shows:** armed is sticky (set when B hidden and all R shown, cleared when a B is
  shown); win = armed and all R hidden.
- **Used by:** games/china/docs/puzzles.md 2 Bouddha.

### E-1203 — China: Sceaux puzzle and its m (2026-10-08)
- **Source:** 0x41d020 (tables stride 0x1c: EMPR 0x52cd40, EMPRF 0x52cd94, SCEAU 0x52cde8
  (+0x14 shown 1, +0x18 held 0), DEBRILL 0x52ce3c, DEMAT 0x52ce90, OMBRE 0x52cee8;
  TAMPONS 0x52cd20), 0x41d630 (m: `fond`/`fond2` at 0x41d68b..0x41d6c6, target table
  0x52cd44 + m*0x54; step array on the stack; 1000 ms DEBRILL loop with object 0x15
  set held at 0x4ffa24; clicks only if 0x417e50 returns 36; pairings at 0x41dae7..
  0x41db8b; win at 0x41ddbd (m 0) and the m 1 test; Space 0x39 / right click to 0x40efd0
  only if m = 0 and 0x403520(0x15) false), 0x41d540 close. Callers: places-logic
  `spfw101` puzzle(3, 0), `arbre3` puzzle(3, 1).
- **Shows:** m selects background and target row and the CIRE/interface behaviour;
  solution left<-middle, middle<-right, right<-left; no Escape; m = 1 cannot be left.
- **Used by:** games/china/docs/puzzles.md 3 Sceaux; answers Q-0950.

### E-1204 — China: Go puzzle (2026-10-08)
- **Source:** 0x41b5d0 (`Bout%d` = 5r+5-c into 0x52bff8; `Barre%d` = 4r+4-c into
  0x52be18; `Barre%d` = 37+r-4c into 0x52c258; stride 0x18, flags 0), 0x41b990 (toggle,
  wait while channel 0 plays, bars from point pairs, win at 0x41bc5a.. on all 25 point
  flags), 0x41b920 close. Corpus: BOUT/BARRE positions confirm bars lie between their
  points (BARRE4 186,176 between BOUT5 and BOUT4; BARRE37 183,191 between BOUT5, BOUT10).
- **Shows:** 5x5 board; win = exactly points 2,6,7,8,11,12,13,17,22 (index 5r+c).
- **Used by:** games/china/docs/puzzles.md 4 Go.

### E-1250 — China's Puzzle4: label rings, sprite rings, the four-element order (2026-10-08)
- **Source:** CHINE.EXE (EN ISO) 0x417e90 (init: `puzzle4a/b.wav` slots 0/1, `fond`,
  `mask.raw`, `%s%s%c%s` with '8'-i for `direct`/`animaux`/`couleur`, ciel..lune2, the 24
  LABELS.TXT keys at 0x418665..0x418785), 0x41880e (sound 0, ring of 8 label pointers
  shifted up by one), 0x4189bc (run: mask - 0xe7 hover label; presses; phase test of
  the three entry-7 flags; `Puzzle4\` + `puzenter` at 0x41912e..0x419169; the soleil,
  lune, mer, ciel step chain; Escape 0x414c70(1)), 0x41887e (free); corpus SPR headers
  (`DATA/PUZZLES/PUZZLE4`), MASK.RAW values 231..255.
- **Shows:** everything in games/china/docs/puzzles.md section 5 (start entry 3 per ring,
  solution entry 7 = files 1, the phase 2 order, return 1 without a video).
- **Used by:** games/china/docs/puzzles.md 5 Puzzle4.

### E-1251 — China's clock puzzle: four hands dragged over a mask, solution 6/9/10/8 (2026-10-08)
- **Source:** CHINE.EXE 0x41bd30 (init: `clicaig.wav`, `hrlgfnd`, `mask.raw`,
  `%s%s%s%d%s` "aig" + zero pad + a/b/d for 1..12 and c for 1..30, stored in reverse
  order; initial flags 0x52c78c, 0x52c90c, 0x52ca14, 0x52c574), 0x41c1d0 (run: grab by
  pixel hit while held, drag by mask value with +1 wrap, click sound on change, solved
  flags 0x52c664, 0x52c7bc, 0x52c894, 0x52c99c only when not dragging, video `puzhorlo`
  at 0x41c4f6, Escape), 0x41c140 (free), 0x41fc20 (pixel hit test); corpus SPR
  headers, MASK.RAW values 0..54.
- **Shows:** games/china/docs/puzzles.md section 6.
- **Used by:** games/china/docs/puzzles.md 6 Horloge.

### E-1252 — China's door puzzle: three six-word columns, solution APPOSER x3 (2026-10-08)
- **Source:** CHINE.EXE 0x41a8f0 (init: `bouton1a.wav` twice, `porte`, 18 sprites with
  LABELS.TXT keys, entries of 0x1c bytes, initial flags 0x52bc64, 0x52bd44, 0x52bd7c),
  0x41b0a0 (run: rect hits 0x420340, entry i -> i-1 with 0 -> 5, hover labels, solved
  when the three entry-0 flags are set, video `puzporte` at 0x41b5a2, Escape), 0x41b010
  (free); corpus SPR headers (`DATA/PUZZLES/PORTE`).
- **Shows:** games/china/docs/puzzles.md section 7.
- **Used by:** games/china/docs/puzzles.md 7 Boutons.

### E-1253 — China's bomb: a 17-step click sequence, two game-over videos (2026-10-08)
- **Source:** CHINE.EXE 0x4192c0 (init: sound slots 2..8 coussin, tvis, pese, clang,
  clic, metal, tuyau; `Trone`; 15 SPR click shapes), 0x419830 (run: hover labels
  AIGUILLE/POISON, cursors 10/14 via 0x41a390 (empty hands only) and 11, the step tests
  at 0x419a55..0x41a23b with backgrounds Bombe1..Bombe37, held-object tests 0x14, 0x16,
  0x19 via 0x417e50, videos gamover1 (0x419ebd, 0x419f9f, 0x41a03c, 0x41a0d8, 0x41a174)
  and gamover2 (0x419dfb, 0x419e8e); right click or Space -> interface 0x40efd0; exit
  returns a held object to the inventory 0x417dc0(obj, 2)), 0x4197d0 (free; frees only
  0x52bb50..0x52bb74); corpus `DATA/PUZZLES/BOMBE` (no TUYAU.WAV).
- **Shows:** games/china/docs/puzzles.md section 8.
- **Used by:** games/china/docs/puzzles.md 8 Bombe.
