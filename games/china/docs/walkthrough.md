# China: the critical path

The shortest sequence of actions that takes a new game of *China: The Forbidden City* to
the epilogue, derived from the generated logic of the 270 place procedures,
[places-logic.md](places-logic.md) (E-0710..E-0712). Every step cites the place whose code
it follows. It is the script for chained play-through scenarios (one scenario per chapter,
chained by saves). Places, zones and the place API: [places.md](places.md) and
`engines/cryomni3d/docs/spec/china-zones.md`; puzzles: [puzzles.md](puzzles.md); the
interface bar: `engines/cryomni3d/docs/spec/china-interface.md`.

## Conventions

- **Zone n** is the zone's index in the place, in creation order (places-logic `zone n:`).
  Types: go, look, take, use, talk, doc. A doc zone clicked with an object in hand gives
  the place's code the zone (the documentation does not open): many steps show an object
  to a character by clicking a doc zone with it (Q-1302).
- **Hold X**: the interface step. Space (or right click) opens the bar, click X's slot,
  move the cursor back above y 400; X is now the cursor (china-interface.md, "Opening and
  closing"). Nothing on the path needs an object in hand that is not already in the
  inventory.
- **Route** `a 1 > b 0* > c`: click zone 1 in a, then zone 0 in b, arriving in c.
  `*` marks a zone that is created disabled or whose target is chosen by the place's
  code: it works only in the state the step describes. Routes come from
  `uv run engines/cryomni3d/tools/china_route.py --any <from> <to>`, which prefers plain
  go zones. The interface's map (compass) can shorten routes; it is not used here.
- **To bpiw201** (the player's office, PPC, CHAPITRE 0..9 and 10 before the second seal
  clue): reach `cpc120`, then `cpc120 5* > bpiw101 2`. **To bpiw202** (the same office
  from CHAPITRE 10 with INDICE_CACHETS2, and later): `cpc120 5* > bpiw102 2`
  ([cpc120](places-logic.md#cpc120)).
- Variables are set to 1 unless a value is given. `note` = notebook entry.
- New game: CHAPITRE = 1, MANDAT1 in the inventory, at `pne140`
  ([Script_Start](places-logic.md#script_start), E-0506).

## Chapter values

CHAPITRE takes the values 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14, 15, 17, 18; no place
procedure stores 3, 7, 11 or 16 (tests such as `>= 16` or `< 11` fall between) (Q-1300).

| CHAPITRE | Set by (step) | Place |
|---:|---|---|
| 1 | new game | Script_Start |
| 2 | 8, talk zone 1/2 | jixw121 |
| 4 | 15, Bouddha puzzle solved | meuble5 |
| 5 | 19, Go puzzle solved | espw101 |
| 6 | 29, after the boxes | pdc179 |
| 8 | 33, the brush on the table | table11 (or table12, table13) |
| 9 | 36, after the door puzzle | bouton21 |
| 10 | 42, go zone 9 | cpc410 |
| 12 | 51, the hiding place opened | cachwen2 (cachwen3 if VAR_Pieces_prises) |
| 13 | 53, on arrival | victime |
| 14 | 59, go zone 1 | cgc110 |
| 15 | 66, the seals shown | bpiw202 |
| 17 | 69, Penjing solved | pdcw522 (and penjing2) |
| 18 | 72, the clock solved | bdaw100 |

## Steps

### CHAPITRE 1

1. In `pne140` go to the library: route `pne140 0 > pne150 2*` (pne150 zone 2 leads to
   `lgaw101` while CHAPITRE <= 8) ([pne150](places-logic.md#pne150)). Optional before
   this: the gate guards, talk zone 1 or 2 -> GICD1011 or GIDD1011 (only before XNED1011)
   ([pne140](places-logic.md#pne140)).
2. In `lgaw101`, talk zone 6 -> dialogue XNED1011 (G101XNE, G101ANJ), XNED1011
   ([lgaw101](places-logic.md#lgaw101)).
3. In `lgaw101`, talk zone 4 (enabled now) -> dialogues ENED1011, ENED1021, ENED1031
   (G101EGC, I201ANJ), ENED1011, note MINPN102 ([lgaw101](places-logic.md#lgaw101)).
4. To `bpiw201`: `lgaw101 0* > pne150 0 > pne140 4 > pne130 1 > pne120 1 > pne110 1 >
   aio100 2 > aio200 3 > cpc110 0 > cpc120 5* > bpiw101 2`. Talk zone 19 -> dialogues
   ANXI1011, XPID1012 (I201XPI), note MINBP101, ANXI1011, MANDAT1 destroyed, MANDAT2 to
   the inventory ([bpiw201](places-logic.md#bpiw201)).
5. To `aie600b`: `bpiw201 0 > bpiw101 0 > cpc120 1 > cpc110 5 > aio200 0 > aio100 0 >
   cgc120 1 > cgc130 1 > cgc140 4 > cgc150 1 > cgc160 0 > aie100 1 > aie200 4 > aie300 1 >
   aie400 1 > aie500 1`. Talk zone 0 (enabled on entry by ENED1011) -> dialogue EGJD1011
   (C600EGJ, C600ANJ), EGJD1011 ([aie600b](places-logic.md#aie600b)).
6. In `aie600b`, hold MANDAT2, use zone 4 (enabled once EGJD1011 is set) -> dialogue
   EGJD1041, EGJD1041, JIXW111_ouvert. (Holding MANDAT1 there instead plays EGJD1021 and
   opens nothing.) ([aie600b](places-logic.md#aie600b))
7. In `aie600b`, go zone 5 -> video jixh007, `jixw111` (JIXW111_ouvert, CHAPITRE < 13);
   go zone 0 -> video jixh111, `jixw121` ([aie600b](places-logic.md#aie600b),
   [jixw111](places-logic.md#jixw111)).
8. In `jixw121`, talk zone 1 (or 2) -> dialogues ANID1011, ANID1121 (M111ANJ, M111IMD),
   VAR_ANID1121, **CHAPITRE = 2**, CLE_WANG and POSTHUME to the inventory, note MINJI109
   ([jixw121](places-logic.md#jixw121)). A second click plays ANID1131 (optional).

### CHAPITRE 2

9. To `lgaw101`: `jixw121 0 > jixw111 2* > aie600b 1 > aie500 0 > aie400 0 > aie300 0 >
   aie200 0 > aie100 0 > cgc160 1 > cgc150 0 > cgc140 3 > cgc130 0 > cgc120 0 > aio100 1 >
   pne110 0 > pne120 0 > pne130 0 > pne140 0 > pne150 2*`. Talk zone 6 twice -> ANXN1111,
   then ANXN1121 ([lgaw101](places-logic.md#lgaw101)).
10. In `lgaw101`, look zone 2 (enabled by VAR_ANID1121) -> `meuble1`; take zone 1 ->
    `meuble2` ([meuble1](places-logic.md#meuble1)).
11. In `meuble2`, take zone 3 -> `meuble30`; take zone 1 -> MARTEAU to the inventory,
    Marteau, `meuble31`; go zone 0 -> `meuble2` ([meuble30](places-logic.md#meuble30)).
12. In `meuble2`, take zone 4 -> `meuble40`; take zone 1 -> BURIN, Burin, `meuble41`;
    take zone 1 -> TOURNEVIS, Tournevis, `meuble43`; go zone 0 -> `meuble2`
    ([meuble40](places-logic.md#meuble40), [meuble41](places-logic.md#meuble41)).
13. In `meuble2`, hold CLE_WANG, use zone 5 (enabled by ANXN1121 and the three tools
    taken) -> Cle_Wang_Utilisee, CLE_WANG destroyed, `meuble5`
    ([meuble2](places-logic.md#meuble2)).
14. In `meuble5`, take zone 1 -> **puzzle 2 (Bouddha)** ([meuble5](places-logic.md#meuble5)).
15. Solved -> **CHAPITRE = 4**, Venant_de_BOUDDHA = 1, POSTHUME destroyed, `bouddha2`;
    take zone 0 -> CONFES1 to the inventory, `confess1`; go zone 0 -> `bouddha3`; take
    zone 0 -> INDIC1, `indice1`; go zone 0 -> Venant_de_BOUDDHA = 2, note MINPN201,
    `lgaw101` ([bouddha2](places-logic.md#bouddha2), [confess1](places-logic.md#confess1),
    [bouddha3](places-logic.md#bouddha3), [indice1](places-logic.md#indice1)).

### CHAPITRE 4

16. Leave `lgaw101` by go zone 0 -> (CHAPITRE 4, first time) dialogue GDCD2011, video
    PNEH202, note MINPN202, PNEH201, `pne150` ([lgaw101](places-logic.md#lgaw101)).
17. To `espw201`: `pne150 0 > pne140 4 > pne130 1 > pne120 1 > pne110 1 > aio100 0 >
    cgc120 1 > cgc130 1 > cgc140 4 > cgc150 1 > cgc160 0 > aie100 1 > aie200 3 > cpc210 1 >
    cpc220 0 > cpc230 5* > espw101 1` (cpc230 zone 5 leads to espw101 while CHAPITRE <=
    14). Optional: talk zone 3 -> ANMW2011 (or ANMW201A) ([espw201](places-logic.md#espw201)).
18. In `espw201`, hold INDIC1, click doc zone 2 -> dialogues ANMW2031, PRND2011, ANMW2031,
    PRND2011 (the test `not PRND1011` reads a variable nothing sets, so it always passes)
    ([espw201](places-logic.md#espw201)).
19. `espw201 0` -> `espw101`; look zone 10 (enabled on entry by ANMW2031) -> **puzzle 4
    (Go)**. Solved -> CONFES1 and INDIC1 destroyed, **CHAPITRE = 5**, `go20`; failed ->
    GO + 1 (hints at espw201 talk zone 3) ([espw101](places-logic.md#espw101)).

### CHAPITRE 5

20. In `go20` take zone 0 -> CONFES2, `confess2`; go zone 0 -> `go21`; take zone 0 ->
    INDIC2, `indice2`; go zone 0 -> note MINES209, `espw101` (Venant_de_GO 1, 2, 3)
    ([go20](places-logic.md#go20), [confess2](places-logic.md#confess2),
    [go21](places-logic.md#go21), [indice2](places-logic.md#indice2)).
21. `espw101 1` -> `espw201`; hold CONFES2, doc zone 2 -> ANMW2111
    ([espw201](places-logic.md#espw201)).
22. To `bpiw201`: `espw201 0 > espw101 0 > cpc230 0 > cpc370 0 > cpc360 0 > cpc350 0 >
    cpc340 3 > cpc330 3 > cpc440 3 > cpc420 3 > cpc120 5* > bpiw101 2`. Hold CONFES2, doc
    zone 17 -> dialogues ANXI2111, XPID2112, note MINBP211, ANXI2111
    ([bpiw201](places-logic.md#bpiw201)).
23. To `banw111`: `bpiw201 0 > bpiw101 0 > cpc120 1 > cpc110 5 > aio200 0 > aio100 0 >
    cgc120 2 > cgc110 1* > nwfw101 2*` (cgc110 zone 1 leads to nwfw101 while CHAPITRE <=
    10; nwfw101 zone 2 to banw111 until RUYI is taken). Optional: take zone 4 -> RUYI,
    Ruyi, `banw112` (RUYI can replace BURIN in step 50 and MARTEAU in step 71)
    ([banw111](places-logic.md#banw111)).
24. In `banw111` (or banw112), look zone 2 (enabled at CHAPITRE 5 by ANXI2111 and
    ANMW2111) -> `registre`; take zone 1 -> note MINNW211, PDC_ouvert, `cahiers`; take
    zone 1 -> `lboites`; go zone 0 -> LISTE_BOITES to the inventory, Liste_Boites, back to
    banw111 ([registre](places-logic.md#registre), [cahiers](places-logic.md#cahiers),
    [lboites](places-logic.md#lboites)).
25. To `bpiw201`: `banw111 0 > nwfw101 0 > cgc110 0 > cgc120 0 > aio100 2 > aio200 3 >
    cpc110 0 > cpc120 5* > bpiw101 2`. Hold LISTE_BOITES, doc zone 17 -> dialogues ANXI2131,
    XPID2132, note MINBP212, ANXI2131, MANDAT2 destroyed, MANDAT3 to the inventory
    ([bpiw201](places-logic.md#bpiw201)).
26. To `pdc010`: route of step 5 to `aie600b`, then `aie600b 2* > pdc005 0` (zones 2/3
    enabled from CHAPITRE 5). Talk zone 1 -> dialogue EGCD2111 (L010EGC, L010ANJ),
    EGCD2111 ([aie600b](places-logic.md#aie600b), [pdc010](places-logic.md#pdc010)).
27. In `pdc010`, hold MANDAT3, use zone 2 (enabled by EGCD2111) -> dialogue ANEC212A,
    video PDCH211, `pdc011`: voice EGCD2131, video PDCH212, dialogue EGCD2141,
    Mandat_Montre_EGC, back to pdc010 ([pdc010](places-logic.md#pdc010),
    [pdc011](places-logic.md#pdc011)).
28. To `pdc170`: `pdc010 3* > pdc110 3 > pdc120 0 > pdc130 0 > pdc140 3`. Talk zone 2 ->
    dialogue XPRD2111 (L170XPR, L170ANJ), XPRD2111; from now until step 29 zone 0 (the
    way out) is disabled ([pdc170](places-logic.md#pdc170)).
29. In `pdc170`, hold LISTE_BOITES, doc zone 1 -> dialogue ANXP215A, video ORGH211,
    `pdc178`: voice XPRD2161, video ORGH212, ORGH211, `pdcw171`; look zone 0 -> `boite31`;
    take zone 1 -> `boite32`; hold TOURNEVIS, use zone 1 -> `boite331`; take zone 0 ->
    ORIGINAUX to the inventory, `origine`; go zone 0 -> dialogue ANJORG21, video ORGH221,
    `pdc179`: voice CPRD2111, video ORGH222, ORGH221, note MINPD219, LISTE_BOITES
    destroyed, dialogue ANXP2211, **CHAPITRE = 6**, `pdc170`
    ([pdc170](places-logic.md#pdc170), [pdc178](places-logic.md#pdc178),
    [boite31](places-logic.md#boite31), [boite32](places-logic.md#boite32),
    [boite331](places-logic.md#boite331), [origine](places-logic.md#origine),
    [pdc179](places-logic.md#pdc179)).

### CHAPITRE 6

30. To `bpiw201`: `pdc170 0* > pdc140 1 > pdc130 3 > pdc110 0 > pdc010 0 > pdc005 1 >
    aie600b 1 > aie500 0 > aie400 0 > aie300 0 > aie200 0 > aie100 0 > cgc160 1 > cgc150 0 >
    cgc140 3 > cgc130 0 > cgc120 0 > aio100 2 > aio200 3 > cpc110 0 > cpc120 5* > bpiw101 2`.
    Hold ORIGINAUX, doc zone 17 -> dialogue ANXI2211, note MINBP221, ANXI2211
    ([bpiw201](places-logic.md#bpiw201)).
31. To `espw201`: `bpiw201 0 > bpiw101 0 > cpc120 2 > cpc420 5 > cpc440 1 > cpc330 0 >
    cpc340 1 > cpc350 2 > cpc360 1 > cpc370 1 > cpc230 5* > espw101 1`. Talk zone 3 ->
    dialogue MWED2131, MWED2131 ([espw201](places-logic.md#espw201)).
32. In `espw201`, hold ORIGINAUX, doc zone 2 -> ORIGINAUX destroyed, var221 = 1, `table`;
    take zone 2 -> PINCEAU_ESP in hand, `table10`; use zone 2 -> Pinceau_mouille (the
    brush is wet); use zone 1 (brush in hand, CHAPITRE 6) -> `table11`
    ([espw201](places-logic.md#espw201), [table](places-logic.md#table),
    [table10](places-logic.md#table10)).
33. In `table11`, use zone 2 with the wet brush -> **CHAPITRE = 8**, ORIGINAUX destroyed,
    note MINES299, video ideo, sound origine, `table14`; go zone 0 -> PINCEAU_ESP and
    CONFES2 destroyed, T14, var221 = 2, `espw201`, whose entry plays dialogue MWED3011
    (var221 = 3) ([table11](places-logic.md#table11), [table14](places-logic.md#table14)).
    ORIGINAUX stays destroyed (to-inventory acts only on state 0, china-zones.md Objects);
    nothing later needs it.

### CHAPITRE 8

34. To `cgc310`: `espw201 0 > espw101 0 > cpc230 2 > cpc220 2 > cpc210 4 > aie200 0 >
    aie100 0 > cgc160 1 > cgc150 2`. Look zone 4 (enabled at CHAPITRE 8) -> `porte`; look
    zone 1 -> `porte1` ([cgc310](places-logic.md#cgc310), [porte](places-logic.md#porte)).
35. In `porte1`, hold BURIN, use zone 1 -> `porte2`; hold MARTEAU, use zone 1 -> `bouton1`;
    take zone 0 -> **puzzle 7 (Boutons)**; failed -> `porte`
    ([porte1](places-logic.md#porte1), [porte2](places-logic.md#porte2),
    [bouton1](places-logic.md#bouton1)).
36. Solved -> INDIC2 and CONFES2 destroyed, `bouton20`; take zone 0 -> CONFES3,
    `confess3`; go zone 0 -> `bouton21`; take zone 0 -> INDIC3, **CHAPITRE = 9**,
    `indice3`; go zone 0 -> note MINGC301, video poch301, dialogue GDCD3011, video poch302,
    note MINGC302, `cgc310` ([bouton20](places-logic.md#bouton20),
    [confess3](places-logic.md#confess3), [bouton21](places-logic.md#bouton21),
    [indice3](places-logic.md#indice3)).

### CHAPITRE 9

37. To `espw201`: `cgc310 11 > cgc150 1 > cgc160 0 > aie100 1 > aie200 3 > cpc210 1 >
    cpc220 0 > cpc230 5* > espw101 1`. Hold CONFES3, doc zone 2 -> ANMW3111
    ([espw201](places-logic.md#espw201)).
38. To `bpiw201`: `espw201 0 > espw101 0 > cpc230 0 > cpc370 0 > cpc360 0 > cpc350 0 >
    cpc340 3 > cpc330 3 > cpc440 3 > cpc420 3 > cpc120 5* > bpiw101 2`. Hold CONFES3, doc
    zone 17 -> dialogues ANXI3111, XPID3112, note MINBP311, ANXI3111
    ([bpiw201](places-logic.md#bpiw201)).
39. To `lgaw102`: `bpiw201 0 > bpiw101 0 > cpc120 1 > cpc110 5 > aio200 0 > aio100 1 >
    pne110 0 > pne120 0 > pne130 0 > pne140 0 > pne150 2*` (pne150 zone 2 leads to lgaw102
    from CHAPITRE 9). Talk zone 4 (enabled by ANXI3111 and ANMW3111) -> dialogue ENED3111
    (G102ENE, G102ANJ), note MINPN311, ENED3111 ([lgaw102](places-logic.md#lgaw102)).
40. To `aio100`: `lgaw102 0 > pne150 0 > pne140 4 > pne130 1 > pne120 1 > pne110 1`. Talk
    zone 6 -> dialogue GIAD3111 (B100gid), GIAD3111 (or zone 7 -> GIBD3111)
    ([aio100](places-logic.md#aio100)). Optional: the pne140 guards (GICD3111) and the
    aio200 guards (GIED3111).
41. To `cpc110`: `aio100 2 > aio200 3`. Talk zone 8 (or 9; both play GIGD3111) ->
    dialogue GIGD3111 (E110GIG), notes MINCP311, MINCP312, GIGD3111
    ([cpc110](places-logic.md#cpc110)).
42. `cpc110 1` -> `cpc410`; go zone 9 (enabled at CHAPITRE 9 by GIGD3111) -> **CHAPITRE =
    10**, INDICE_CACHETS to the inventory, video GRTH301, dialogue ANJGRT34 (R100ANJ),
    note MINCP319, `bpiw201` ([cpc410](places-logic.md#cpc410)).

### CHAPITRE 10

43. In `bpiw201`, hold INDICE_CACHETS, doc zone 17 -> dialogue XPID3122, note MINBP319,
    XPID3122, MANDAT3 destroyed, MANDAT4 to the inventory ([bpiw201](places-logic.md#bpiw201)).
    Do this before step 45: once INDICE_CACHETS2 exists, cpc120 leads to bpiw202 instead.
44. To `aie500`: `bpiw201 0 > bpiw101 0 > cpc120 1 > cpc110 5 > aio200 0 > aio100 0 >
    cgc120 1 > cgc130 1 > cgc140 4 > cgc150 1 > cgc160 0 > aie100 1 > aie200 4 > aie300 1 >
    aie400 1`. Hold MANDAT4, use zone 5 (the guard; or 6) -> dialogue GITD3221 (or
    GISD3221), entree_PPF, zone 7 enabled ([aie500](places-logic.md#aie500)). The same
    works at aio500 zones 5/6 ([aio500](places-logic.md#aio500)).
45. To `spfw101`: `aie500 7* > ctp210 0 > ctp350 0 > ctp340 0 > ctp330 2*` (ctp330 zone 2
    leads to spfw101 at CHAPITRE 9, and at 10 until ANMI3211). Talk zone 5 -> dialogue
    XPFD3211, XPFD3211 ([ctp330](places-logic.md#ctp330), [spfw101](places-logic.md#spfw101)).
46. In `spfw101`, hold INDICE_CACHETS, doc zone 3 (or 4) -> video SPFH320, **puzzle 3
    (Sceaux, m = 0)**; solved -> EPFD3211, INDICE_CACHETS destroyed, INDICE_CACHETS2 to
    the inventory; solved or not, dialogue ANEF3221 ([spfw101](places-logic.md#spfw101)).
    The puzzle also hands the player CIRE (puzzles.md, Sceaux; Q-1200).
47. To `bpiw202`: `spfw101 0 > ctp330 0 > ctp320 0 > ctp310 0 > ctp110 6 > aio500 0 >
    aio400 0 > aio300 0 > aio200 3 > cpc110 0 > cpc120 5* > bpiw102 2`. Hold INDICE_CACHETS2
    (or CIRE), doc zone 18 -> dialogues MPID3211, MPID3221, note MINBP321, CIRE destroyed,
    ANMI3211 ([bpiw202](places-logic.md#bpiw202)).
48. To `spfw102`: `bpiw202 0 > bpiw102 0 > cpc120 1 > cpc110 5 > aio200 5 > aio300 1 >
    aio400 1 > aio500 3 > ctp110 0 > ctp310 1 > ctp320 1 > ctp330 2*` (aio500 zones 3/4
    stay open after entree_PPF; ctp330 zone 2 now leads to spfw102). Talk zone 2 ->
    dialogue ANEF3231, note MINSP326, ANEF3231 ([spfw102](places-logic.md#spfw102)).
49. To `lgew100`: `spfw102 0 > ctp330 1 > ctp340 1 > ctp350 1 > ctp210 6*` (ctp210 zone 6
    enabled at CHAPITRE 10 by ANEF3231) ([ctp210](places-logic.md#ctp210)).
50. In `lgew100`, take zone 2 -> `coffre`; take zone 1 -> `cachwen1`; hold BURIN (or
    RUYI), use zone 1 -> `cachwen2` ([lgew100](places-logic.md#lgew100),
    [coffre](places-logic.md#coffre), [cachwen1](places-logic.md#cachwen1)).
51. In `cachwen2`, go zone 0 -> note MINLG401, VAR_Pieces_prises, **CHAPITRE = 12**,
    `lgew100` ([cachwen2](places-logic.md#cachwen2)).

### CHAPITRE 12

52. Leave `lgew100` by go zone 0: the first click plays video LGEH331 (VAR_LGE_entree,
    note MINLG399) and stays; click zone 0 again -> `ctp210`
    ([lgew100](places-logic.md#lgew100)). Then `ctp210 4 > aie500 1` -> `aie600b`.
    Optional at this chapter: the guards' CHAPITRE 12 lines (cpc110, cpc210, aie200,
    aie500), EGJD4011 at aie600b, MPID3991 and ANMI4021 at bpiw202.
53. In `aie600b`, go zone 5 -> video jixh007, `jixw110` (CHAPITRE >= 12); `jixw110 1` ->
    `jixw120`; go zone 1 (created only while LVICT is 0) -> videos JIXH401, JIXH402,
    JIXH402b, dialogues ANEB4091, ANJIX41, EN1JIX41, note MINJI4090, `victime`: on its
    first frame LVICT, on the next **CHAPITRE = 13**, voice victime, LISTE_VICTIMES to the
    inventory, note MINJI409, `jixw210` ([aie600b](places-logic.md#aie600b),
    [jixw120](places-logic.md#jixw120), [victime](places-logic.md#victime)).

### CHAPITRE 13

54. `jixw210` at CHAPITRE 13 sets puzzle mode until the next step is done (no compass;
    the exit spiral stays, china-interface.md) and only look zone 1 is on. Look zone 1 ->
    `soupir`. Hold TOURNEVIS and use zones 0, 1, 5 and 3 (one per side; crans bits 1, 2,
    4, 8) -> crans = 15, sounds soupira/soupirb, `soupir2`
    ([jixw210](places-logic.md#jixw210), [soupir](places-logic.md#soupir)).
55. In `soupir2`, take zone 0 -> **puzzle 5 (Puzzle4)**; solved -> INDIC3 and CONFES3
    destroyed, VAR_Venant_de_PUZZLE4, video puzzl4, note MINJI411, `puzzle42`; take zone 0 ->
    CONFES4, `confess4`; go zone 0 -> `puzzle43`; take zone 0 -> INDIC4, `indice4`; go
    zone 0 -> VAR_Venant_de_PUZZLE4 = 2, `jixw210` ([soupir2](places-logic.md#soupir2),
    [puzzle42](places-logic.md#puzzle42), [confess4](places-logic.md#confess4),
    [puzzle43](places-logic.md#puzzle43), [indice4](places-logic.md#indice4)).
56. `jixw210 0*` -> `jixw132`, whose event plays dialogue XPRD4101 on arrival (XPRD4101).
    Optional: talk zone 0 -> ANXP4111, talk zone 4 -> ANCP4101. Back to `aie600b`:
    `jixw132 1 > jixw122 0 > jixw112 0*` ([jixw132](places-logic.md#jixw132),
    [jixw112](places-logic.md#jixw112)).
57. `aie600b 2* > pdc005 0` -> `pdc010`; talk zone 1 -> `pdc012`: dialogue EGCD4111,
    video PDCH211, voice EGCD4131, video PDCH212, dialogue EGCD4141, EGCD4111, back to
    pdc010 ([pdc010](places-logic.md#pdc010), [pdc012](places-logic.md#pdc012)).
58. `pdc010 3* > pdc112 4` -> `pdc162` (pdc010 zones 3/4 lead to pdc112 from CHAPITRE 13).
    Talk zone 9 -> dialogue ANEQ4111 (L162ANJ, L162EQR), ANEQ4111, MINXQ411, video PDCH401,
    `pdc175`: voices EQRD4131, DQRD4131, video PDCH402, dialogue EQRD4141, note MINPD411,
    back to pdc162 ([pdc162](places-logic.md#pdc162), [pdc175](places-logic.md#pdc175)).
59. To `cgc110`: `pdc162 1 > pdc112 0 > pdc010 0 > pdc005 1 > aie600b 1 > aie500 0 >
    aie400 0 > aie300 0 > aie200 0 > aie100 0 > cgc160 1 > cgc150 0 > cgc140 3 > cgc130 0 >
    cgc120 2`. Go zone 1 -> (CHAPITRE 13, MINXQ411) video NWFH431, dialogues XQRD4091,
    MPID4191, note MINNW419, NWFH401, **CHAPITRE = 14**, LISTE_VICTIMES destroyed,
    `bpiw202` ([cgc110](places-logic.md#cgc110)).

### CHAPITRE 14

60. To `pdc010`: `bpiw202 0 > bpiw102 0 > cpc120 1 > cpc110 5 > aio200 0 > aio100 0 >
    cgc120 1 > cgc130 1 > cgc140 4 > cgc150 1 > cgc160 0 > aie100 1 > aie200 4 > aie300 1 >
    aie400 1 > aie500 1 > aie600b 2* > pdc005 0`. Talk zone 1 -> dialogue ANEC4211, note
    MINHB421, EGCD4211 ([pdc010](places-logic.md#pdc010)).
61. `pdc010 3* > pdc112 4` -> `pdc162`; talk zone 9 (enabled on entry by EGCD4211) ->
    dialogue EQRD4211, video PDCH401, `pdc176`: voice EQRD4221, video PDCH402, dialogue
    EQRD4231, EQRD4211, C510_ouvert, back to pdc162 ([pdc162](places-logic.md#pdc162),
    [pdc176](places-logic.md#pdc176)).
62. In `pdc162`, go zone 10 (enabled by C510_ouvert) -> `pdcw512`; talk zone 13 ->
    dialogues DQRD4211, DQRD4221, LETTRE_VIERGE in hand, note MINPD422, DQRD4211
    ([pdcw512](places-logic.md#pdcw512)).
63. In `pdcw512`, with LETTRE_VIERGE in hand, use zone 2 -> VAR_LETTRE_REVELEE, the letter
    relabelled LETTRE_REVELEE, `lvierge`: sound jingfind, note MINPD423, `rebus`; go zone
    0 -> `pdcw512` ([pdcw512](places-logic.md#pdcw512), [lvierge](places-logic.md#lvierge),
    [rebus](places-logic.md#rebus)).
64. To `jarre2`: `pdcw512 0* > pdc162 1 > pdc112 3 > pdc122 2*` (pdc122 look zones 2/3
    enabled at CHAPITRE 14). Take zone 1 (enabled by VAR_LETTRE_REVELEE) -> `pierre2`; hold
    BURIN, use zone 2 -> Pierre_ouverte, `pierre21`; take zone 0 -> note MINPD425,
    CLE_JARRE, Cle_jarre_prise, `pierre22`; go zone 0 -> `pdc122`
    ([pdc122](places-logic.md#pdc122), [jarre2](places-logic.md#jarre2),
    [pierre2](places-logic.md#pierre2), [pierre21](places-logic.md#pierre21),
    [pierre22](places-logic.md#pierre22)).
65. To `arbre1`: `pdc122 1 > pdc112 4 > pdc162 6*` (look zones 6/7/8 enabled at CHAPITRE
    14 with C510_ouvert while SCEAUX is untouched). Take zone 1 -> `arbre2`; hold
    CLE_JARRE, use zone 1 -> video arbre, `arbre3`; take zone 0 -> **puzzle 3 (Sceaux,
    m = 1)**; solved -> CLE_JARRE, LETTRE_VIERGE, INDICE_CACHETS2 destroyed, SCEAUX to the
    inventory, note MINPD429, `pdc162` ([pdc162](places-logic.md#pdc162),
    [arbre1](places-logic.md#arbre1), [arbre2](places-logic.md#arbre2),
    [arbre3](places-logic.md#arbre3)). The puzzle cannot be left unsolved (Q-1200).
66. To `bpiw202`: the route of step 59 to `cgc110`, then `cgc110 1*`. Hold SCEAUX, doc
    zone 18 -> dialogues ANMI4311, MPID4312, SCEAUX destroyed, note MINBP431, ANMI4311,
    **CHAPITRE = 15** ([bpiw202](places-logic.md#bpiw202)).

### CHAPITRE 15

67. To `pdc162`: the route of step 60 to `pdc010`, then `pdc010 3* > pdc112 4`. Talk zone
    9 -> C520_ouvert, dialogue EQRD4311, video PDCH401, `pdc177`: voice EQRD4321, video
    PDCH402, dialogue EQRD4331, ANEQ4311, C510_ouvert, back to pdc162
    ([pdc162](places-logic.md#pdc162), [pdc177](places-logic.md#pdc177)).
68. `pdc162 10* > pdcw512 1*` -> `pdcw522`; talk zone 0 -> dialogue CQRD4311, CQRD4311,
    zone 2 enabled ([pdcw512](places-logic.md#pdcw512), [pdcw522](places-logic.md#pdcw522)).
69. In `pdcw522`, take zone 2 -> **puzzle 1 (Penjing)**; solved -> PENJING, **CHAPITRE =
    17**, `penjing2`; failed -> var220 = 1 (enables a hint, ANDQ4321, at pdcw512 talk
    zone 13) ([pdcw522](places-logic.md#pdcw522)).
70. In `penjing2`, take zone 0 -> PROCLA to the inventory, CHAPITRE = 17, `proclam`; go
    zone 0 -> video cqrh501, dialogues ANCQ5011, MPID5011, MPID5015, PDCH501, C520_ouvert,
    C510_ouvert, note MINPD501, `bpiw202` ([penjing2](places-logic.md#penjing2),
    [proclam](places-logic.md#proclam)).

### CHAPITRE 17

71. Hold MARTEAU (or RUYI) before going in. To `nwfw100`: `bpiw202 0 > bpiw102 0 > cpc120 1 >
    cpc110 5 > aio200 0 > aio100 0 > cgc120 2 > cgc110 1*` (cgc110 zone 1 leads to nwfw100
    from CHAPITRE 16). Go zone 3 (enabled from CHAPITRE 17) -> video DAMH501, no autosave,
    `fight2` (FIGHTED = 1), `fight` ([nwfw100](places-logic.md#nwfw100),
    [fight2](places-logic.md#fight2)).
72. In `fight`, within 3 seconds of its entry, use zone 0 with MARTEAU (or RUYI) -> video
    DAMH503 (DAMH504), dialogue ANDA5111, note MINNW501, DAMH501, FIGHTED = 3, videos
    DAMH502a, DAMH502g, dialogue ANJDAM61, `bdaw100`. Too late -> video DAMH505, FIGHTED =
    0, `nwfw100` (try again) ([fight](places-logic.md#fight)). Opening the bar during the
    fight does not stop the clock, so the hammer must be in hand already.
73. In `bdaw100`, take zone 2 (enabled at CHAPITRE 17) -> **puzzle 6 (Horloge)**; solved ->
    Venant_de_HORLOGE, **CHAPITRE = 18**, `horloge2`; take zone 0 -> PLBOMB, `plbombe`;
    go zone 0 -> `horloge3`; take zone 0 -> EDI, `edit`; go zone 0 -> Venant_de_HORLOGE =
    2, note MINNW510, `bdaw100` ([bdaw100](places-logic.md#bdaw100),
    [horloge2](places-logic.md#horloge2), [plbombe](places-logic.md#plbombe),
    [horloge3](places-logic.md#horloge3), [edit](places-logic.md#edit)).

### CHAPITRE 18

74. To `shs240`: `bdaw100 0 > nwfw100 0 > cgc110 0 > cgc120 1 > cgc130 1 > cgc140 0 >
    cgc230 0 > cgc210 0 > cth380 1 > cth360 2 > cth270 5 > cth280 1 > cth290 2 > cth150 5 >
    cth170 2 > chs110 1 > chs120 0 > chs130 0 > chs010 1 > shs140 0`. Take zone 8 (the
    throne; enabled on entry from CHAPITRE 16 with Venant_de_HORLOGE) -> **puzzle 8
    (Bombe)**, which needs TOURNEVIS taken in hand through the bar inside the puzzle
    (puzzles.md, Bombe) ([shs240](places-logic.md#shs240)).
75. Solved -> screen fade, video fin, the epilogue (four stills), end of play, credits
    ([shs240](places-logic.md#shs240)).

## Puzzles on the path

| Step | Place | Puzzle |
|---:|---|---|
| 14 | meuble5 | 2 Bouddha |
| 19 | espw101 | 4 Go |
| 35 | bouton1 | 7 Boutons |
| 46 | spfw101 | 3 Sceaux, m = 0 |
| 54 | soupir | the four screws (place code, no puzzle number) |
| 55 | soupir2 | 5 Puzzle4 |
| 65 | arbre3 | 3 Sceaux, m = 1 |
| 69 | pdcw522 | 1 Penjing |
| 72 | fight | the timed blow (place code, no puzzle number) |
| 73 | bdaw100 | 6 Horloge |
| 74 | shs240 | 8 Bombe |

## Objects taken in hand on the path

MANDAT2 (6), CLE_WANG (13), INDIC1 (18), CONFES2 (21, 22), LISTE_BOITES (25, 29),
MANDAT3 (27), TOURNEVIS (29, 54, and inside puzzle 8), ORIGINAUX (30, 32), BURIN (35, 50,
64), MARTEAU (35, 71), CONFES3 (37, 38), INDICE_CACHETS (43, 46), MANDAT4 (44),
INDICE_CACHETS2 (47), CLE_JARRE (65), SCEAUX (66). PINCEAU_ESP and LETTRE_VIERGE are put
in hand by the place's code.

## Unreachable and dead content

From the same logic, for scenario writers: no procedure goes to `go1`, `trone`,
`bombe1`, `bombe2`, `bougies`, `posthum`, `natte`, `boite33`, `penjing`, `fsceaux`,
`puzzle41`, `banw122`, `lgaw100`, `jixw130`, `jixw131`, `espw200`/`espw100`,
`bpiw200`/`bpiw100` (no place outside each pair leads into it). Branches that test variables
nothing sets never run (Q-1301): the CHAPITRE 9 talks ANXI3151 (bpiw201) and ANMW3151
(espw201); `posthum`'s CHAPITRE = 2. `jixw132`'s CHAPITRE 14 talk (ANXP4211) is out of
reach: at CHAPITRE 14 aie600b leads to jixw110, and jixw120 has no way on once LVICT is
set.
