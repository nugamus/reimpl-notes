# Module map of /MISSION.EXE

Generated from `function-map.csv` (`engines/peintre/tools/funcmap.py`, ranges in its
`MODULES` table). 1,191 functions after Ghidra's auto-analysis, thunks excluded.
Proof in EVIDENCE.md E-0009..E-0012.

```
game/puzzles           78 functions   21373 bytes   0 named
game/shell            182 functions   44004 bytes  19 named
game/sound             24 functions    5406 bytes   7 named
game/users             20 functions    6158 bytes   5 named
game3d/scenes         108 functions   46228 bytes  21 named
game3d/tga              7 functions    2038 bytes   4 named
game3d/world           30 functions   16738 bytes   6 named
game3d/app             27 functions    5439 bytes   8 named
game3d/cinematics       1 functions    1238 bytes   0 named
engine3d              176 functions  108362 bytes   3 named
engine3d/asm            1 functions     119 bytes   0 named
cryo/codec             12 functions    4393 bytes   1 named
cryo/file               9 functions     591 bytes   0 named
cryo/font               8 functions     558 bytes   1 named
cryo/misc              91 functions   19750 bytes   0 named
cryo/memory             9 functions     854 bytes   5 named
cryo/ddraw             18 functions    3584 bytes   1 named
cryo/dinput            16 functions    1676 bytes   1 named
cryo/dsound            26 functions    4544 bytes   1 named
msvcrt                348 functions   76194 bytes   0 named
total 1191, named 83
```

## Order of the code

The linker kept object-file order, and the game's object files come in alphabetical
order of their scene names, so a module is a contiguous range:

| Range | Module | What proves it |
|---|---|---|
| 0x401000–0x4022bf | incremental-link thunks | `jmp` stubs only |
| 0x4022c0–0x408cf0 | 2D puzzles | asset names `A01_03x`, `A03_0xx`, `A13_0xx`, `A14_0xx`, "reussit", `*_clic*` sounds; called through pointers (no direct callers) |
| 0x408cf1–0x41664f | 2D shell | Cryo-library users: sprites (.SPR), fonts (.AWF), movies (.HNM/.CVY), .TGP, cursor, option menu, GAME/GGAME saves, credits, inventory ("Invent", "CapsE%02u"), window procedure |
| 0x416650–0x4180bf | sound | DirectSound buffers, WAV/APC loading, ADPCM streams |
| 0x4180c0–0x419f0d | users | registry, USERS.BIN, player-name window (ACCUEIL_BMP), display flip |
| 0x419f0e–0x41ed12 | 3D scenes auberge, (tga), cafe, chambreb, chambrev, champ | `LoadBox*`, `LoadAnims*::%s manque` |
| 0x41ed13–0x4241ef | 3D world | PEINTRE.INI, scene name tables, `C_Monde::LoadScene`, debug overlay, 3D main loop |
| 0x4241f0–0x42e62f | 3D scenes eglise … terrasse | as above |
| 0x42e630–0x42fbd5 | 3D app | "Vangogh Erreur" box, scene file loading, 3D saves (`GAME%04d.BIN`), 3D timer |
| 0x42fbd6–0x43062f | end cinematics | "cinefin2" |
| 0x430700–0x45546f | 3D engine | heap ("Heap overflow"), 3DM loading, "Type d'entete non valide", "Camera", "Bad_Handle!" |
| 0x455470–0x465bcf | assembly | 64 KB of NOP-aligned code without C prologues; Ghidra made no functions; purpose open (Q-0002) |
| 0x465bd0–0x4746ff | Cryo libraries | APC codec ("CRYO_APC", "1.20", ADPCMERR_*), file, fonts, Mem-Lib (`m__malloc`…), DirectDraw, DirectInput, DirectSound |
| 0x474cc0–end | MSVC debug CRT | CRT source names in asserts |
