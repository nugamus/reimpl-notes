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
