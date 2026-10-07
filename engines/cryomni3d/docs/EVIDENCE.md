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
