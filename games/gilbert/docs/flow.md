# Gilbert: the whole game (flow)

The game's progression as `default.dat` defines it: rooms, close-ups, the goal, every
puzzle chain with its preconditions, and a complete walkthrough that
`engines/gilbert/tools/simulate.py` replays against the database to the ending. The data is
the evidence: `python engines/gilbert/tools/parsers/gamedat.py
games/gilbert/discs/cd/Program/Data/game/default.dat` dumps every record cited here; the rules
that run them are `engines/gilbert/docs/spec/logic.md` (events, object lists, anims),
`rooms.md` (areas) and `screens.md` (close-ups, map, dialogues). Claims beyond a data lookup
are E-0600..E-0608, open points Q-0600..Q-0601.

Conventions: an **object code** is `id * 100 + state` (logic.md); "event n" is every CEvent
record with id n; `v<n>` is game variable n; "R<n>" a room (walkmap), "C<n>" a close-up (CUA).
"Take" = drag a pickable close-up object to the inventory (its take event runs), "use A on B"
= drop A (an inventory item or a pickable object of the close-up) on B (GEUseObjectOnObject
with the exact codes), "click" = GEClickObjectInCUA on a not-pickable object, "area n" = walk
into control-map cells of value n + 1 (event room · 100 + n).

## Structure

### Rooms

38 of the 40 walkmaps are rooms with a folder `Data/maps/<id>/` and a control map; 900
("Flygkarta") and 999 (the travel map's walkmap, holding only C999) have neither. Titles are
the database's internal Swedish names. Areas: every control-map value 2..31 present in the
room, n = value − 1, with the type-4 (room) or type-3 (close-up) record of event room·100+n;
the films named by the same event play first. 99 is the "Kort" button (C999, every room).

| Room | Title | Close-ups listed | Areas → destination |
|---|---|---|---|
| 100 | Stranden 100 | 101 102 103 105 107 109 199 | 1 → R554; 11 → C102; 12 → C101; 13 → C103; 14 → C105; 15 → C107; 25..28 → R151 |
| 150 | Stranden/Pir 150 | 104 | 1 → R170; 2 → R270; 11 → C104 |
| 151 | Stranden/Kläckningsplats 151 | 106 108 | 11 → C106; 12 → C108; 21, 22 → R555; 23, 24 → R170; 25..28 → R100 |
| 170 | Stranden mellanlänk 170 | — | 1..4 → R557; 21 → R150; 23, 24 → R151; 26, 27 → R555 |
| 200 | Labbet övre 200 | 201 210 211 214 | 1 → R250; 2 → R254 (film la_down); 11 → C210; 12 → C209 |
| 250 | Labbet nedre 250 | 202 203 204 205 206 207 209 215 | 1 → R200; 11 → C206; 12 → C204; 13 → C203; 14 → C202 |
| 254 | Labbet utanför 254 | 212 216 | 1 → R200 (film la_up); 2 → R270; 11 → C212; 12 → C216 |
| 270 | Labbet utanför 270 mellanlänk | — | 1 → R150; 2 → R254 |
| 300 | Öknen/oljeförädl 300 | 300 | 1..4 → R352; 5..8 → R350; 11 → C300 |
| 350 | Öknen/kamel 350 | 302 | 3, 4 → R351; 5..8 → R300; 11 → C302 |
| 351 | Öknen/Tält 351 | 303 304 308 | 3, 4 → R350; 5..8 → R352; 11 → C303; 12 → C304 |
| 352 | Öknen/Jordgubb 352 | 305 306 307 309 | 1..4 → R300; 5..8 → R351; 11 → C305; 12 → C307; 13 → C306; 23..26 → R370 |
| 370 | Öknen/mellangång 370 | — | 21, 22 → R552; 23..26 → R352 |
| 400 | Gruvingång 400 | 401 402 | 1 → R600; 11 → C402; 12 → C401; 21..23 → R500 |
| 451 | Gruvrum 01 | 403 | 1 → R400; 2 → R452; 3 → R456; 11 → C403 |
| 452 | Gruvrum 02 | 404 | 1 → R451; 2 → R457; 3 → R460; 11 → C404 |
| 453 | Gruvrum 03 | 405 | 1 → R455; 3 → R463; 11 → C405 |
| 454 | Gruvrum 04 | 406 | 1 → R456; 2 → R458; 11 → C406 |
| 455 | Gruvrum 05 | 407 | 1 → R459; 2 → R453; 3 → R458; 11 → C407 |
| 456 | Gruvrum 06 | 408 | 1 → R451; 2 → R460; 3 → R454; 11 → C408 |
| 457 | Gruvrum 07 | 409 417 | 1 → R452; 3 → R459; 11 → C409; 12 → C417 |
| 458 | Gruvrum 08 | 410 | 1 → R454; 2 → R455; 3 → R460; 11 → C410 |
| 459 | Gruvrum 09 | 411 | 1 → R460; 2 → R457; 3 → R455; 11 → C411 |
| 460 | Gruvrum 10 | 414 | 1 → R456; 2 → R459; 3 → R458; 4 → R452; 11 → C414 |
| 461 | Gruvhiss / 461 | 412 | 1 → R463; 11 → C415; 12 → C412 |
| 462 | Gruva Lavaman | 413 416 | 11 → R461; 12 → C413 |
| 463 | Gruva före hiss | 415 | 1 → R453; 2 → R461 |
| 500 | Skog 500 | 501 | 1..4 → R556; 5..8 → R557; 11 → C501; 21..23 → R400 |
| 550 | Barrskog/glänta 550 | 505 506 507 508 510 | 1, 2 → R556; 11 → C505; 12 → C510 (film fo_house); 13 → C507; 14 → C506 |
| 552 | Regnskog/flygplan 552 | 504 | 1..4 → R553; 5..8 → R554; 11 → C504; 21, 22 → R370 |
| 553 | Regnskog/ 553 | — | 1..4 → R552; 5..8 → R555 |
| 554 | Regnskog/ 554 | 509 | 1..4 → R555; 5..8 → R552; 9 → R100; 11 → C509 |
| 555 | Regnskog/ihåligt träd 555 | 503 | 1..4 → R554; 5..8 → R553; 11 → C503; 21, 22 → R151; 26, 27 → R170 |
| 556 | Barrskog/ 556 | 502 | 1..4 → R500; 5..8 → R558; 11 → C502; 21, 22 → R550; 9: no event |
| 557 | Barrskog/ 557 | — | 1..4 → R558; 5..8 → R500; 21..24 → R170 |
| 558 | Barrskog/ 558 | — | 1..4 → R557; 5..8 → R556; 9: no event |
| 600 | Glaciär/glasskiosk 600 | 601 602 603 608 609 611 620 | 1 → R400; 2 → C608; 11 → C601; 12 → C603 (kiosk side); 3 → R650; 13 → C620 (upper side) |
| 650 | Glaciär/utsiktspl 650 | 604 605 606 619 | 1 → R600 (upper side); 11 → C604; 12 → C606; 13 → C605 |

Area events without cells in the control map (never run): 20050, 25050, 25450 (back to a
room "from a CUA"), 35001, 35002 (commented "*Anv inte*", do not use), 35209 (R352 → R552).

**Gates between rooms** (E-0603): three parts of the island are reached only through close-up
events, not areas:

- **The mine** (R451..R460, R463, R461): C401's door 40110 opens with the battery (use
  5040100 on 4011000 → event 4010: film mi_door, door state 1, acid symbol 4010100 to the
  inventory); clicking the broken door 4011001 → event 4011 → R451. R451 area 1 leads out.
- **The lava man's cave** (R462): C412 in R461, elevator button 3010200 on the empty button
  place 4123000 → event 4120 (film mi_down) → R462; later clicks on 4123001 → event 4121.
  The button place shows only after the lemon in C415 (event 4151).
- **The glacier's upper side and the lookout** (R600 areas 3, 13; R650): the frozen
  waterfall C603 splits R600. Before it melts, the far bank 6032500 slides Gilbert down to
  the desert (event 6031, film gl_slip, R351); after event 6033 its state 1 crosses (event
  6032 → R600 at 164,229, where areas 3 and 13 are). R650 area 1 and C620's event 6201 lead
  back to R600.

The flood fill that decides which areas Gilbert can reach from where he enters a room is in
`simulate.py` (`reachable`): 0 cells joined 8-way to his cell, and the area cells beside them.

### Close-ups opened from close-ups

| From | Event | To | Back (end event) |
|---|---|---|---|
| C202 cupboard, open (mops, pictures) | 2022 | C215 | 2153 → C202 |
| C206 lab table, arrows 2067000 / 2067100 | 2068 / 2069 | C207 / C205 | 2050 → C206 |
| C210 stairs, chair in place 2100601 | 2108 (and 2106) | C211 roof hatch | — |
| C211 switch plate with lever 2113001 / 2113002 | 2112 / 2113 | C214 | — |
| C303 water tap 3031000 | 3031 | C308 | 3088 → C303 |
| C307 cactus (magnifier with glass) | 3070 | C309 | 3091 → C307 |
| C510 gingerbread house door 5101000 | 5101 | C508 | 5081 → C510 |
| C608 igloo, bridge down 6081001 | 6080 | C602 | 6020 → C608 |
| C602 melted ice queen 6021001 | 6503 | C611 | 6110 → C602 |
| C605 painting 6051300 | 6052 | C609 | 6091 → C605 |
| C606 binoculars 6061000 | 6061 | C619 | 6199 → C606 |

C209 (egg stand) is listed under R250 but opened from R200 area 12, C415 under R463 but from
R461 area 11, C609 under R600 but from R650: their pictures are in the folder of the room
they are opened from (`Data/maps/200/cua209.wxi`, `461/cua415.wxi`, `650/cua609.wxi`).

### The travel map (C999)

"Kort" in any room: event room·100 + 99 → C999; its nine symbols (objects 99901..99909,
state 0, codes 9990100..9990900) run:

| Event | Symbol text | Room, start point |
|---|---|---|
| 9901 | Til stranden | R100 (1215, 179) |
| 9902 | Til ørkenen | R352 (830, 651) |
| 9903 | Til molen | R150 (574, 480) |
| 9904 | Til skoven | R552 (118, 870) |
| 9905 | Til skoven | R557 (462, 870) |
| 9906 | Til gletsjeren | R600 (812, 767), kiosk side |
| 9907 | Til lysningen | R550 (90, 290) |
| 9908 | Til laboratoriet | R254 (575, 448) |
| 9909 | Til minen | R400 (310, 484), outside the mine |

Each also starts the place's room music (type 6, kind 0). The map is always available and
reaches no gated part.

## The goal

- **New game** (event 1): v60..v64 := 1 (the five gases of the gas tap), the sorter's He
  button lit (2033102), Gilbert in R151 at (400, 300), film intro.mpg, music "standard".
- **Eggs found** = v199 (the panel's egg picture, rooms.md): +1 by events 1060, 3041, 5021,
  4026, 6508, 2141, one per eggshell; event 795 also adds 1 but nothing runs it.
- **Eggs placed** = v1: use an eggshell on the stand 20920 in C209 (any of its states 0..5,
  six CUseObj per egg) → events 2091..2096: stand state + 1, the eggshell removed, v1 += 1,
  and when v1 == 6 → **event 2099: film outro.mpg, v198 := 1**. The EXE reads v198 every
  tick and returns to the main menu with Continue and Save disabled (boot.md). Event 770
  also sets v198 but nothing runs it (E-0600).

| Egg | Object | Found by | Code placed | Placing event |
|---|---|---|---|---|
| 1 | 10601 | take in C106 (event 1060) | 1060102 (after the water, below) | 2091 |
| 2 | 60202 | ice crystal on the window, event 6508 | 6020200 | 2092 |
| 3 | 30403 | take in C304 after event 9503001 (event 3041) | 3040301 | 2093 |
| 4 | 40201 | the third piece of foil on the wok, event 4026 | 4020100 | 2094 |
| 5 | 50210 | soap in the pond, event 5021 | 5021001 | 2095 |
| 6 | 21401 | take in C214 (event 2141) | 2140100 | 2096 |

## Puzzle chains

Each row: the goal, the action, what must hold (else the action does nothing or only
comments), the effect. Dialogue rows name the record that matters; the choices that reach it
are in the walkthrough and the dialogue table below.

### Beach (eggs 1 and 3 begin here)

| Goal | Action | Preconditions | Effect |
|---|---|---|---|
| Egg 1 | take 1060100 in C106 | — | v199 + 1 |
| Volcano | click the sandcastle 1032000 (1031) or the bucket/spade 1030200/1030500 (1032) in C103 | v66 == 0 (once) | film be_girl(2), volcano 1032101 active, girl sad 1032202, v66 := 1 |
| Water in the eggshell | use 1060100 on 1032101 (1034) | volcano active | egg → 1060101, volcano removed |
| Egg ready to place | use 1060101 on the crevice 1081000 in C108 (1081) | — | egg → 1060102, crevice → 1081003 (with bottle) |
| Bottle | click 1081003 (1083) | crevice state 3 | bottle 1080200, crevice → 2, v52 := 1, **v44 := 1** (needed by the kiosk, below) |
| Lifeguard | click 1011000 in C101, dialogue to 9200201 | — | camera 1010100 (pickable), close-up lifeguard 1011600 shown |
| Photo | use 1010100 on 1011600 (1011) | 9200201 done | film be_life; can 1010300, towel 1010200, comb 1010500, sunglasses 1010600 pickable |
| Pacifier | in C104 use the rod 1040200 on Gilbert 1042000 (1041) | — | film pi_fish, pacifier 1040100 shown (pickable) |
| Bucket, spade, paper | use 1040100 on the girl 1032200 or 1032202 (1033) | — | girl with pacifier; paper 1030100, bucket 1030200, spade 1030500 pickable |
| Foil and receipt | use a can on the machine 1022000 in C102: 1010300 (1021), 1070100 (1022), 3060200 (1023), 5090100 (1024) | — | film be_panto2; foil 10201/10202/10203/10208 and receipt 10204/10205/10206/10209 shown, pickable |

### Desert

| Goal | Action | Preconditions | Effect |
|---|---|---|---|
| Camel | toothpaste 1020700 (from C102) on the camel 3021100 in C302 (3021), then sunglasses 1010600 on 3021101 (3022) | — | film de_camel, the refinery's lamp 3012000 shown in C300 |
| Refinery | click the lamp 3012000 (3011), 3012002 (3012), 3012004 (3013) in C300 | stay until each anim ends (3015/3016/3017, ~0.9 s) | elevator button 3010200; petrol can with fire symbol 3010300; ping-pong ball 3010400 |
| Bedouin 1 | click 3041000 in C304 (3050 → 3049) | v8 == 0 | v8 := 1 |
| Gingerbread | take 5070200 in C510 (5102) | — | v7 := 1 |
| Bedouin 2 | click, dialogue to 9502061 | v8 == 1, v7 == 1 (3052 sets v54 := 1) | gingerbread given, v8 := 2 |
| Sand | use the bucket 1030200 on the sand 3031400 in C303 (3032) | v54 == 1 | bucket with quartz sand 1030201 |
| Egg 3 | click, dialogue to 9503001 | v8 == 2, v10 == 1 (lab report) | lab report given, eggshell cup 3040301 pickable, v8 := 3; take it (3041): v199 + 1 |
| Bedouin 4, 5, 6 | click, dialogues to 9504061 / 9506061 / 9508061 | v8 == 3 / 4 with v9 == 1 / 5 with v11 == 1 | v8 := 4 / 5 / 6; at 6 the tent 3040200 is pickable |
| Bedouin 7 | click, dialogue to 9510061 | v8 == 6, v12 == 1 | strawberries 3050300, v8 := 7, v6 := 1 (only the beach seller uses them) |
| Brush | take 3060100 in C306 | — | — |
| Desert artist | use coal 4030100 on the artist 3062100 in C306 (3064), dialogue to 9602001 | — | can 3060200 shown, v55 := 1; leaving C306 (3067 → 3069 → 5096) moves him to C509 |
| Lice | use the magnifier with glass 2151001 on the cactus 3071000 in C307 (3070 → C309); matchbox 2060900 on 3091000 (3090) | — | matchbox with lice 2060901, back in C307 |
| Strawberry bed | ice queen in the bucket 1030203 on the sprinkler 3052200 in C305 (3202) | — | film de_icebl, bed salted 3053001, salt heap 3052300 shown, bucket empty, **v9 := 1, v40 := 0** |
| Manure | compost soil 5072103 on 3053001 (3205) | v48 == 0 (3206: v11 := 1) | bed manured; with v48 == 1 (3207) strawberries grow but v11 stays 0, which cannot happen in play: v48 needs the opened bottle, the bottle the tent, the tent v11 |
| Salt | bucket 1030200 on the salt heap 3052300 (3204) | — | bucket with salt 1030206 |

### Forest

| Goal | Action | Preconditions | Effect |
|---|---|---|---|
| Plane wreck | take the battery 5040100 in C504 | — | (mirror 5040200 and tyre 5040300 only feed the sorter) |
| Mower | petrol 3010300 on the mower 5051100 in C505 (5051) | — | film fo_cut, grass 5050100, fire symbol 3010500, **v15 := 1** |
| Compost | grass 5050100 on 5072100 in C507 (5072) | — | soil 5072103 pickable, pickaxe 5070800 shown |
| Food lady 1 | via C510's door (5101 → C508), click 5081000 (5080 → 5084) | v14 == 0, v15 == 1 | v14 := 1 |
| Pancakes | click 5085000 three times (5502) | v15 == 1 | pancake 5080100 (5505), then (5509, film fo_lady) the rolling pin 5080201 pickable |
| Oil | rod 1040200 on the oil 5081500 in C508 (5510) | — | oil 5070700 shown in C507 (take it there) |
| Mosquito net | take 6010200 in C601 (glacier kiosk) | — | — |
| Pulp | click the logs 5012000 in C501 (5013); net on the pulp 5012100 (5011); rolling pin on 5012101 (5012) | — | film fo_timb; paper 5012102 and tall oil 5010400 |
| Forest artist | paper 5012102 on the artist 5092000 in C509 (5095), dialogue to 9605001 | he is shown (v55 == 1, after leaving C306) | can 5090100 pickable, v55 := 2; leaving C509 (5096 → 1078) moves him to C107 |
| Lemon | take 5070300 in C510 | — | — |
| Bees | magnifier with glass on the hollow tree 5031000 in C503 (5031); towel 1010200 on the queen 5032000 (5032); towel with queen 1010201 on the hive 5061000 in C506 (5061) | — | beeswax 5030100 shown in C503 (take it there) |
| Egg 5 | soap 2061700 on the pond 5021100 in C502 (5021) | — | film fo_bub, eggshell 5021001, v199 + 1 |

### Laboratory

| Goal | Action | Preconditions | Effect |
|---|---|---|---|
| Soda machine | click 2041000 in C204 (2041) | — | film la_lask, v49 := 1 |
| Lab assistant | click 2161000 in C216 twice; second time dialogue to 91101041 | v51: 0 → 1 (first click), then v49 == 1 | cupboard door ajar 2021001, v51 := 2 |
| Lab report, magnifier | click 2021001 in C202 (2021: door open, contents shown), click them (2022 → C215); take 2150200 (2151) and 2151000 (2152) | door ajar | **v10 := 1**; magnifier without glass |
| Tools | take matchbox 2060900, thermometer 2063200, lye 2063300, linseed oil 2063400 in C206; the big crucible 2071000 in C207 | — | — |
| Soap | tall oil on the crucible 2062300 (2271), lye on 2062337 (2273), the soap crucible 2065700 on a big jar 2062200 (2275) or 2064200 (2276); take the jar (2341/2342) | v88 == 0 (once) | soap 2061700 |
| Gas tap | click the gas button 2073000 in C207 (2074): each click steps v58 to the next gas whose v60..v64 is still 1; party balloons 6010300 on the tap | v57 == 0 (no balloon filling) | hydrogen (2771 → 2773 → 2774): explosive symbol 2070400 pickable, v60 := 0; helium (2776 → 2778): balloon 2070300, v61 := 0; neon (2780 → 2783): balloon 2070200, **v42 := 1**, v62 := 0 |
| Glass | diamond 4130300 on the empty glass cutter 2052000 in C205 (2051), glass 4130600 on 2052001 (2057, anim to 2058), magnifier 2151000 on 2052002 (2053) | — | magnifier with glass 2151001 |
| Crushed lice | lice box 2060901 on the saucer 2062400 (2355), saucer on the microwave 2062500 (2356 → 2357), dried lice 2062402 on the mortar 2062600 (2359 → 2360) | stay for the anims (1.4 s, 4.5 s) | mortar 2062601 pickable |
| Lipstick | beeswax on the crucible 2062300 (2203), mortar on 2062332 (2205), oil on 2062334 (2207), mould 2020400 on 2062335 (2208) | v87 == 0 | mould with lipstick 2020402, **v18 := 1** |
| Element sorter | an item on 2032000 in C203 | — | cartridge 4060100 (8303): mould 2020400 and poison symbol 2020500; zinc mineral 4040100 (8311): zinc 2030700; the others only light element buttons |
| Lever | enter C203 (2700) | v99 == 1 (the crystal) | film la_switch, lever 2010100 (2730), v99 := 0 |
| Rust-proof paint | zinc 2030700 on the crucible (2201); linseed on a big jar (2242 or 2253); zinc crucible 2065400 on that jar (2245 / 2256); take it (2345 / 2346) | v85 == 0; only one big jar takes linseed (v89 / v95) | paint 2061800 |
| Mailbox | click 2121100 in C212 (2120 by v3): 0 → 1 (film la_mail1, broken rung shown); step 1 4130200 on 2122000 (2128) → 2; click → 3 (la_mail2); click → 4 (la_mail3, rung rusted 2122002); step 2 4130700 on 2122002 (2129) → 5; paint on 2122003 (2130) → 6; click → 7 (la_mail4) | the steps from the lava man | concert tickets 2120200, **v17 := 1** |
| Hazard boxes | on the boxes in C210: fire symbol 3010500 on 2100200 (2101), explosive 2070400 on 2100100 (2102), acid 4010100 on 2100300 (2103), poison 2020500 on 2100400 (2104) | — | v0 += 1 each |
| Chair | camping chair 6050200 on 2100600 (2105 → 2106) | v0 == 4 | chair placed, C211 opens |
| Egg 6 | lever 2010100 on the switch plate 2113000 in C211 (2111), click 2113001 (2112 → C214), take 2140100 (2141) | — | v199 + 1 |

### Mine

The signs: phosphor on the brush first (brush 3060100 on the crack 4111000 in C411, event
4110 → brush 3060101), then the brush on each dark sign 40x2000 (events 4030, 4040, 4050,
4060, 4070, 4080, 4090, 4100, 4140) lights it and makes its crack usable.

| Goal | Action | Preconditions | Effect |
|---|---|---|---|
| Coal | click the crack 4031001 in C403 (4032), take 4030100 | sign lit | coal |
| Cartridge | ping-pong ball 3010400 on 4061001 in C406 (4061), take 4060100 | sign lit | cartridge |
| Zinc mineral | bucket with salt 1030206 on 4041001 in C404 (4041), take 4040100 | sign lit | zinc mineral; the table place 2072800 in C207 shown |
| Crystal | butter 5080500 on Gilbert 4092100 in C409 (4091: v23 := 1, crystal shown); wash in C417 (click 4171100, 4172: v23 := 0); click the crystal 4090100 (4093 → 4095) | sign lit; v23 == 0 when clicking | crystal 4090100, **v39 := 1, v99 := 1** |
| Elevator | lemon 5070300 on 4151000 in C415 (4150 → anim → 4151, 1 s) | — | solar battery; film mi_start; button place 4123000 in C412 |
| Miner | click 4021000 in C402 (4027): v19 == 0 → dialogue to 9400081 (v19 := 1); then with v20 == 1 → 4502 | the wok (v20) | wok on the stand 4021500 |
| Egg 4 | three pieces of foil (1020100, 1020200, 1020300, 1020800) on the wok 40215 (4020/4022/4023/4024 → 4025) | — | at v21 == 3: event 4026, eggshell 4020100, v199 + 1; 4072: the neon crack becomes a TV tube |

### Lava man (C413, v24) and ice queen (C602, v35)

| Goal | Action | Preconditions | Effect |
|---|---|---|---|
| Meet the lava man | click 4131000 (4130 → 4131) | v24 ≤ 1 | v24 := 1, **v65 := 1** (the igloo's bridge can come down) |
| Thermometer | 2063200 on 4131000 (4132 → 4133) | v24 == 1 | v24 := 2 |
| Sand | 1030201 on 4131000 (4138 → 4139) | v24 == 2 | bucket empty, v24 := 4 |
| Glass | magnifier 2151000 on 4131000 (4135 → 4137) | v24 == 4 | film mi_do_gl, glass 4130600, v24 := 5, **v36 := 1** |
| Meet the queen | via C608 (bridge down: 6081 with v65 == 1, v35 == 0), click 6021000 (6023) | — | v35 := 1 |
| Photo | camera on the queen (6025 → 6026) | v36 == 1 | photo 6020100, v35 := 4, v26 := 1 |
| Photo to the lava man | click (4130 → 4701 → 4703) | v24 == 5, v26 == 1 | v24 := 6 |
| Ladder step 1 | click (4706) | v24 == 6 or 7 | step 4130200, **v37 := 1**, v24 := 8 |
| Queen 3 | click (6021 → 6027 → 6028), dialogue to 91002061 | v35 == 4, v37 == 1 (the bridge is down again) | v35 := 5, **v27 := 1** |
| Diamond | click (4707 → 4709) | v24 == 8, v27 == 1 | diamond 4130300, v24 := 9 |
| — | click (4713) | v24 == 9 | v24 := 10 |
| Lava | big crucible 2071000 on 4131000 (4714 → 4715) | v24 == 10 | crucible with lava 2071001, v38 := 1, v24 := 11 |
| Ladder step 2 | click (4716) | v24 == 11 | step 4130700 |
| Melt the queen | 2071001 on the queen 6021000 (6502) | (v35 == 5, v38 == 1 open the bridge) | film gl_lava, queen melted 6021001, v35 := 6, crucible empty |
| Queen in the bucket | click 6021001 (6503 → C611), bucket 1030200 on 6111000 (6112) | **before leaving C602/C611** (dead end below) | bucket with queen 1030203, v35 := 7, v40 := 1 |
| Egg 2 | crystal 4090100 on the eggshell 6021100 by the window (6506 → 6507 → 6508) | v35 == 7, v40 == 0 (the sprinkler or a later visit to C603, event 792) | eggshell 6020200, ice crystal 6020300, v199 + 1, v35 := 8, queen at the crack 6041300 shown in C604 |
| Camping chair | click the queen 6041300 in C604 (6041), dialogue to 91009121 | the lookout (the waterfall melted) | film gl_grow, chair 6050200 shown in C605 |

The igloo's bridge (C608 runs 6081 on every entry): up (6084) while v65 == 0; then down
for v35 == 0; v35 == 1 with v36 == 1; v35 == 4 with v37 == 1; v35 == 5 with v38 == 1; v35 ==
7 with v39 == 1 and v40 == 0 (6089 also puts the queen back in 6021000). v35 == 1 with v36
== 0 and v35 == 7 with v39 == 1, v40 == 1 leave it as it was; every other case raises it
(6084), v35 == 6 and 8 included.

### Glacier ice-cream seller and kiosk (C601, v41)

| Goal | Action | Preconditions | Effect |
|---|---|---|---|
| Seller 1 | click 6011000 (6011 → 6012), dialogue to 9900081 | v41 == 0 | v41 := 1 |
| Guilbers | receipts 1020400/1020500/1020600/1020900 on 6011000 (6712..6715) | — | a guilber each (6010600..6010900) |
| Party balloons | three guilbers on 6011000 (6716..6719 → 6720) | v45 reaches 3 | balloons 6010300 (6721; the balloons are never used up) |
| Seller 2 | click (6013 → 6015), dialogue to 9902021 | v41 == 1, v42 == 1 (neon balloon) | neon balloon given, sign lit, v41 := 2 |
| Seller 3 | click (6016), dialogue to 9903081 | v41 == 2 | v41 := 3 |
| Tent, helium | tent 3040200 on the kiosk 6010100 (6724); helium balloon 2070300 on 6010101 (6725) | — | **v43 := 1** |
| Corkscrew, the kiosk flies | click (6017 → 6019), dialogue to 9905061 | v41 == 3, v43 == 1; **v44 == 1 (bottle taken)** | corkscrew 6010400, v41 := 4, v92 := 1; with v44 == 1 → 6704: film gl_kiosk, bottle opened 1080300, the seller moves to the beach (C105) |
| Waterfall | opened bottle 1080300 on 6032000 in C603 (6033) | — | film gl_melt, far bank 6032501 crossable, **v48 := 1, v12 := 1** |

### Food lady (C508, v14) and the wok

| Goal | Action | Preconditions | Effect |
|---|---|---|---|
| Food lady 2 | click (5085 → 5087) | v14 == 1, v17 == 1 | tickets given, v14 := 2 |
| Food lady 3 | click (5088 → 5501), dialogue to 9809021 | v14 == 2, v18 == 1 | film fo_lady2; wok 5080400, butter 5080500 and the rolling pin pickable; pancake and oil to the inventory |
| Wok | take 5080400 (5516) | — | **v20 := 1** |

### Order constraints (summary)

Egg 1 and egg 5 stand alone (beach; lab + forest). Egg 3 needs the gingerbread and the lab
report. Everything else hangs on the lava man, and through him on the ice queen: the
lava man needs the thermometer, the sand (bedouin 2), the magnifier, the queen's photo; his
steps and diamond feed the mailbox (tickets → food lady → wok → egg 4) and the glass cutter
(magnifier with glass → lice, beeswax → lipstick → food lady). The melted queen feeds the
strawberry bed (bedouin 5, tent → kiosk → corkscrew → opened bottle → waterfall → the
lookout → the chair → egg 6) and, with the mine's crystal, egg 2. Three receipts (the
lifeguard's can, the desert artist's, the forest artist's) buy the balloons for the gases.

## Walkthrough

A new game (event 1 → R151) to the ending, one action per line, as `simulate.py` reads them
(its docstring has the grammar; `#` starts a comment). `back` leaves a close-up (its end event
may open another: C508 → C510, C611 → C602 → C608, C205/C207 → C206); `map E` is the "Kort"
button and the symbol with click event E; `wait MS` means staying in the close-up while its
anims run. `python engines/gilbert/tools/simulate.py` replays it: 582 actions (161 room
areas, 40 map trips, 83 backs, 211 close-up actions, 77 dialogue choices, 10 waits),
ending with v1 = 6, event 2099 (outro.mpg), v198 = 1 (E-0601). It leaves out the optional
content listed below. Film records play their films
in between; the simulator only notes them.

```
# egg 1: water from the volcano, the water into the crevice, the egg on the stand
room 151 area 11
cua 106 take 1060100
back
room 151 area 25
room 100 area 13
cua 103 click 1032000
cua 103 use 1060100 on 1032101
back
room 100 area 25
room 151 area 12
cua 108 use 1060101 on 1081000
cua 108 click 1081003
back
map 9908
room 254 area 1
room 200 area 12
cua 209 use 1060102 on 2092000
# gingerbread for the bedouin; the soda machine, the lab assistant, the lab report; egg 3
back
map 9907
room 550 area 12
cua 510 take 5070200
back
map 9902
room 352 area 5
room 351 area 12
cua 304 click 3041000
dialog 50000 choice 4
cua 304 click 3041000
dialog 50200 choice 0
dialog 50202 choice 0
dialog 50204 choice 0
dialog 50206 choice 0
dialog 50208 choice 1
back
map 9908
room 254 area 1
room 200 area 1
room 250 area 12
cua 204 click 2041000
back
map 9908
room 254 area 12
cua 216 click 2161000
dialog 110000 choice 3
cua 216 click 2161000
dialog 110100 choice 0
dialog 110102 choice 0
dialog 110104 choice 0
back
room 254 area 1
room 200 area 1
room 250 area 14
cua 202 click 2021001
cua 202 click 2021100
cua 215 take 2150200
cua 215 take 2151000
back
back
map 9902
room 352 area 5
room 351 area 12
cua 304 click 3041000
dialog 50300 choice 0
cua 304 take 3040301
# lifeguard: camera, photo
back
map 9901
room 100 area 12
cua 101 click 1011000
dialog 20000 choice 0
dialog 20002 choice 0
dialog 20004 choice 0
dialog 20006 choice 0
dialog 20008 choice 2
dialog 20014 choice 0
dialog 20016 choice 0
dialog 20018 choice 0
dialog 20020 choice 0
cua 101 take 1010100
cua 101 use 1010100 on 1011600
cua 101 take 1010300
cua 101 take 1010200
cua 101 take 1010600
# pier: fishing brings up the pacifier; the girl's pacifier frees the bucket
back
map 9903
room 150 area 11
cua 104 take 1040200
cua 104 use 1040200 on 1042000
cua 104 take 1040100
back
map 9901
room 100 area 13
cua 103 use 1040100 on 1032202
cua 103 take 1030200
back
room 100 area 11
cua 102 take 1020700
cua 102 use 1010300 on 1022000
cua 102 take 1020400
cua 102 take 1020100
# desert: toothpaste and sunglasses for the camel; the refinery's three products
back
map 9902
room 352 area 1
room 300 area 5
room 350 area 11
cua 302 use 1020700 on 3021100
cua 302 use 1010600 on 3021101
back
room 350 area 5
room 300 area 11
cua 300 click 3012000
wait 2000
cua 300 take 3010200
cua 300 click 3012002
wait 2000
cua 300 take 3010300
cua 300 click 3012004
wait 2000
cua 300 take 3010400
# desert: sand, brush
back
room 300 area 1
room 352 area 5
room 351 area 11
cua 303 use 1030200 on 3031400
back
room 351 area 5
room 352 area 13
cua 306 take 3060100
# forest: plane wreck, mower, compost
back
map 9904
room 552 area 11
cua 504 take 5040100
back
map 9907
room 550 area 11
cua 505 use 3010300 on 5051100
back
room 550 area 13
cua 507 use 5050100 on 5072100
cua 507 take 5072103
# glacier kiosk: mosquito net; forest logs to pulp
back
map 9906
room 600 area 11
cua 601 take 6010200
back
room 600 area 1
room 400 area 21
room 500 area 11
cua 501 click 5012000
cua 501 use 6010200 on 5012100
# food lady: first talk, pancakes, rolling pin
back
map 9907
room 550 area 12
cua 510 click 5101000
cua 508 click 5081000
dialog 80600 choice 2
cua 508 click 5085000
cua 508 click 5085000
cua 508 click 5085000
cua 508 take 5080201
cua 508 use 1040200 on 5081500
back
cua 510 take 5070300
back
room 550 area 13
cua 507 take 5070700
back
room 550 area 1
room 556 area 1
room 500 area 11
cua 501 use 5080201 on 5012101
# lab: tools; soap for the pond (egg 5)
back
map 9908
room 254 area 1
room 200 area 1
room 250 area 11
cua 206 take 2060900
cua 206 take 2063200
cua 206 take 2063300
cua 206 take 2063400
cua 206 use 5010400 on 2062300
cua 206 use 2063300 on 2062337
cua 206 use 2065700 on 2062200
cua 206 take 2062201
cua 206 click 2067000
cua 207 take 2071000
back
back
map 9907
room 550 area 1
room 556 area 11
cua 502 use 2061700 on 5021100
# mine: battery acid on the door, phosphor on the brush, the signs lit; coal, cartridge
back
map 9909
room 400 area 12
cua 401 use 5040100 on 4011000
cua 401 click 4011001
room 451 area 2
room 452 area 2
room 457 area 3
room 459 area 11
cua 411 use 3060100 on 4111000
back
room 459 area 1
room 460 area 1
room 456 area 1
room 451 area 11
cua 403 use 3060101 on 4032000
cua 403 click 4031001
cua 403 take 4030100
back
room 451 area 2
room 452 area 11
cua 404 use 3060101 on 4042000
back
room 452 area 1
room 451 area 3
room 456 area 3
room 454 area 11
cua 406 use 3060101 on 4062000
cua 406 use 3010400 on 4061001
cua 406 take 4060100
back
room 454 area 1
room 456 area 1
room 451 area 2
room 452 area 2
room 457 area 11
cua 409 use 3060101 on 4092000
# elevator to the lava man
back
room 457 area 3
room 459 area 3
room 455 area 2
room 453 area 3
room 463 area 2
room 461 area 11
cua 415 use 5070300 on 4151000
wait 3000
back
room 461 area 12
cua 412 use 3010200 on 4123000
room 462 area 12
cua 413 click 4131000
dialog 30000 choice 4
cua 413 use 2063200 on 4131000
dialog 30100 choice 1
cua 413 use 1030201 on 4131000
cua 413 use 2151000 on 4131000
# ice queen: first talk, photo
back
map 9906
room 600 area 2
cua 608 click 6081001
cua 602 click 6021000
dialog 100000 choice 3
cua 602 use 1010100 on 6021000
# lava man: photo, ladder step 1
back
back
room 600 area 1
room 400 area 12
cua 401 click 4011001
room 451 area 2
room 452 area 2
room 457 area 3
room 459 area 3
room 455 area 2
room 453 area 3
room 463 area 2
room 461 area 12
cua 412 click 4123001
room 462 area 12
cua 413 click 4131000
dialog 30600 choice 1
cua 413 click 4131000
dialog 30800 choice 1
# ice queen: talk after the step
back
map 9906
room 600 area 2
cua 608 click 6081001
cua 602 click 6021000
dialog 100200 choice 0
dialog 100202 choice 0
dialog 100204 choice 0
dialog 100206 choice 0
# lava man: diamond, lava, ladder step 2
back
back
room 600 area 1
room 400 area 12
cua 401 click 4011001
room 451 area 2
room 452 area 2
room 457 area 3
room 459 area 3
room 455 area 2
room 453 area 3
room 463 area 2
room 461 area 12
cua 412 click 4123001
room 462 area 12
cua 413 click 4131000
dialog 31000 choice 1
cua 413 click 4131000
dialog 31200 choice 1
cua 413 use 2071000 on 4131000
cua 413 click 4131000
# melt the ice queen, carry her to the strawberry field
back
map 9906
room 600 area 2
cua 608 click 6081001
cua 602 use 2071001 on 6021000
cua 602 click 6021001
cua 611 use 1030200 on 6111000
back
back
back
map 9902
room 352 area 11
cua 305 use 1030203 on 3052200
cua 305 use 5072103 on 3053001
cua 305 use 1030200 on 3052300
# artists: coal for the desert artist, paper for the forest artist
back
room 352 area 13
cua 306 use 4030100 on 3062100
dialog 60200 choice 0
cua 306 take 3060200
back
map 9901
room 100 area 1
room 554 area 11
cua 509 use 5012102 on 5092000
dialog 60500 choice 0
cua 509 take 5090100
back
# pant machine: two more cans
room 554 area 9
room 100 area 11
cua 102 use 3060200 on 1022000
cua 102 take 1020600
cua 102 take 1020300
cua 102 use 5090100 on 1022000
cua 102 take 1020900
cua 102 take 1020800
# glacier ice-cream seller: receipts for guilbers, guilbers for balloons
back
map 9906
room 600 area 11
cua 601 click 6011000
dialog 90000 choice 0
dialog 90002 choice 0
dialog 90004 choice 0
dialog 90006 choice 0
dialog 90008 choice 0
dialog 90010 choice 1
cua 601 use 1020400 on 6011000
cua 601 use 1020600 on 6011000
cua 601 use 1020900 on 6011000
cua 601 use 6010600 on 6011000
cua 601 use 6010800 on 6011000
cua 601 use 6010900 on 6011000
# lab gas tap: hydrogen (explosive symbol), helium, neon
back
map 9908
room 254 area 1
room 200 area 1
room 250 area 11
cua 206 click 2067000
cua 207 click 2073000
cua 207 use 6010300 on 2072001
wait 15000
cua 207 take 2070400
cua 207 click 2073000
cua 207 use 6010300 on 2072002
wait 7000
cua 207 click 2073000
cua 207 use 6010300 on 2072003
wait 7000
# glacier seller: the neon balloon lights the sign
back
back
map 9906
room 600 area 11
cua 601 click 6011000
dialog 90200 choice 0
dialog 90202 choice 0
cua 601 click 6011000
dialog 90300 choice 0
dialog 90302 choice 0
dialog 90304 choice 0
dialog 90306 choice 0
dialog 90308 choice 0
# bedouin: three more talks, the tent
back
map 9902
room 352 area 5
room 351 area 12
cua 304 click 3041000
dialog 50400 choice 0
dialog 50402 choice 0
dialog 50404 choice 0
dialog 50406 choice 0
cua 304 click 3041000
dialog 50600 choice 0
dialog 50602 choice 0
dialog 50604 choice 0
dialog 50606 choice 0
cua 304 click 3041000
dialog 50800 choice 0
dialog 50802 choice 0
dialog 50804 choice 0
dialog 50806 choice 0
cua 304 take 3040200
# glacier kiosk: tent and helium, the corkscrew; the kiosk flies to the beach
back
map 9906
room 600 area 11
cua 601 use 3040200 on 6010100
cua 601 use 2070300 on 6010101
cua 601 click 6011000
dialog 90500 choice 0
dialog 90502 choice 1
dialog 90506 choice 0
# melt the waterfall with the opened bottle
back
room 600 area 12
cua 603 use 1080300 on 6032000
# glass cutter: the magnifying glass gets its glass
back
map 9908
room 254 area 1
room 200 area 1
room 250 area 11
cua 206 click 2067100
cua 205 use 4130300 on 2052000
cua 205 use 4130600 on 2052001
wait 6000
cua 205 use 2151000 on 2052002
# lice from the cactus
back
back
map 9902
room 352 area 12
cua 307 use 2151001 on 3071000
cua 309 use 2060900 on 3091000
# bees: the queen in the towel, the hive, the beeswax
back
map 9901
room 100 area 1
room 554 area 1
room 555 area 11
cua 503 use 2151001 on 5031000
cua 503 use 1010200 on 5032000
back
map 9907
room 550 area 14
cua 506 use 1010201 on 5061000
back
map 9901
room 100 area 1
room 554 area 1
room 555 area 11
cua 503 take 5030100
# element sorter: the cartridge gives the mould and the poison symbol
back
map 9908
room 254 area 1
room 200 area 1
room 250 area 13
cua 203 use 4060100 on 2032000
# lab table: dried, crushed lice; lipstick in the mould
back
room 250 area 11
cua 206 use 2060901 on 2062400
cua 206 use 2062401 on 2062500
wait 2000
cua 206 use 2062402 on 2062600
wait 6000
cua 206 use 5030100 on 2062300
cua 206 use 2062601 on 2062332
cua 206 use 5070700 on 2062334
cua 206 use 2020400 on 2062335
# zinc: salt in the zinc crack, the sorter, rust-proof paint
back
map 9909
room 400 area 12
cua 401 click 4011001
room 451 area 2
room 452 area 11
cua 404 use 1030206 on 4041001
cua 404 take 4040100
back
map 9908
room 254 area 1
room 200 area 1
room 250 area 13
cua 203 use 4040100 on 2032000
back
room 250 area 11
cua 206 use 2030700 on 2062300
cua 206 use 2063400 on 2064200
cua 206 use 2065400 on 2064204
cua 206 take 2064203
# mailbox: the ladder steps, the paint, the concert tickets
back
map 9908
room 254 area 11
cua 212 click 2121100
cua 212 use 4130200 on 2122000
cua 212 click 2121100
cua 212 click 2121100
cua 212 use 4130700 on 2122002
cua 212 use 2061800 on 2122003
cua 212 click 2121100
# food lady: tickets, lipstick; the wok and the butter
back
map 9907
room 550 area 12
cua 510 click 5101000
cua 508 click 5081000
dialog 80800 choice 2
cua 508 click 5081000
dialog 80900 choice 0
dialog 80902 choice 0
cua 508 take 5080400
cua 508 take 5080500
# mine entrance: the miner, the wok, three pieces of foil (egg 4)
back
back
map 9909
room 400 area 11
cua 402 click 4021000
dialog 40000 choice 0
dialog 40002 choice 0
dialog 40004 choice 0
dialog 40006 choice 0
dialog 40008 choice 0
cua 402 click 4021000
dialog 40200 choice 1
cua 402 use 1020100 on 4021500
cua 402 use 1020300 on 4021501
cua 402 use 1020800 on 4021502
# mine crystal: butter, wash, take
back
room 400 area 12
cua 401 click 4011001
room 451 area 2
room 452 area 2
room 457 area 11
cua 409 use 5080500 on 4092100
back
room 457 area 12
cua 417 click 4171100
back
room 457 area 11
cua 409 click 4090100
# ice queen: the crystal for the eggshell by the window (egg 2)
back
map 9906
room 600 area 2
cua 608 click 6081001
cua 602 use 4090100 on 6021100
dialog 100700 choice 1
# the ice queen at the crack: the camping chair
back
back
room 600 area 12
cua 603 click 6032501
room 600 area 3
room 650 area 11
cua 604 click 6041300
dialog 100900 choice 2
dialog 100906 choice 1
dialog 100908 choice 0
dialog 100910 choice 0
dialog 100912 choice 0
back
room 650 area 13
cua 605 take 6050200
# lab stairs: four hazard symbols on the boxes, the chair; the lever from the sorter; the roof hatch (egg 6)
back
map 9908
room 254 area 1
room 200 area 11
cua 210 use 3010500 on 2100200
cua 210 use 2070400 on 2100100
cua 210 use 4010100 on 2100300
cua 210 use 2020500 on 2100400
cua 210 use 6050200 on 2100600
back
room 200 area 1
room 250 area 13
back
room 250 area 1
room 200 area 11
cua 210 click 2100601
cua 211 use 2010100 on 2113000
cua 211 click 2113001
cua 214 take 2140100
# the egg stand: the other five eggs
back
room 200 area 12
cua 209 use 6020200 on 2092001
cua 209 use 3040301 on 2092002
cua 209 use 4020100 on 2092003
cua 209 use 5021001 on 2092004
cua 209 use 2140100 on 2092005
```

### Dialogue choices the walkthrough needs

A dialogue's effect sits in the event of one choice, usually the last "Fortsæt" of a chain;
"Annuller" anywhere before it closes the box without the effect, and clicking the person again
repeats the dialogue (the variable that selects it has not moved). The choice sequences
(dialogue id : choice index, 0-based) and the record they reach:

| Opened by | Dialogue | Choices | Record with the effect |
|---|---|---|---|
| click 1011000 (C101) | Badvakt 01 | 20000:0 20002:0 20004:0 20006:0 20008:2 ("Hvem er du?") 20014:0 20016:0 20018:0 20020:0 | 9200201 |
| click 3041000 (C304), v8 == 1 | Beduin 03 | 50200:0 50202:0 50204:0 50206:0 | 9502061 |
| click 2161000 (C216), v51 == 1, v49 == 1 | Labbassistent 02 | 110100:0 110102:0 ("Ja, jeg gjorde!") 110104:0 | 91101041 |
| click 3041000, v8 == 2 | Beduin 04 | 50300:0 | 9503001 |
| click 6021000 (C602), v35 == 4 | Isdronning 03 | 100200:0 100202:0 100204:0 100206:0 | 91002061 |
| coal on 3062100 (C306) | Kunstneren 03 | 60200:0 | 9602001 |
| paper on 5092000 (C509) | Kunstneren 06 | 60500:0 | 9605001 |
| click 6011000 (C601), v41 == 0 | Issælgerske 01 | 90000:0 90002:0 90004:0 90006:0 90008:0 ("Med glæde!") | 9900081 |
| the same, v41 == 1 | Issælgerske 03 | 90200:0 90202:0 | 9902021 |
| the same, v41 == 2 | Issælgerske 04 | 90300:0 90302:0 90304:0 90306:0 90308:0 | 9903081 |
| click 3041000, v8 == 3 / 4 / 5 | Beduin 05 / 07 / 09 | 5x400:0 5x402:0 5x404:0 5x406:0 (x = 0, 2, 4 → 50400.., 50600.., 50800..) | 9504061 / 9506061 / 9508061 |
| click 6011000, v41 == 3 | Issælgerske 06 | 90500:0 90502:1 90506:0 | 9905061 |
| click 5081000 (C508), v14 == 2 | Matmora 10 | 80900:0 80902:0 | 9809021 |
| click 4021000 (C402), v19 == 0 | Gruvearbeiderne 01 | 40000:0 40002:0 40004:0 40006:0 40008:0 | 9400081 |
| click 6041300 (C604) | Isdronning 10 | 100900:2 100906:1 100908:0 100910:0 100912:0 | 91009121 |

The other dialogues in the walkthrough carry no effect in their choices (the click that
opened them did the work, e.g. 4131, 4133, 4703, 4706, 4709) and are closed with "Annuller".

### Waiting for anims

Some effects come from anim end events (logic.md "The tick"), which run only while the
close-up that shows the object is open. Leaving restarts them: GotoCUA's ClearAnims resets
every listed state's anim to its first frame (E-0602). The walkthrough's `wait` lines:

| Where | Started by | End event after | Effect |
|---|---|---|---|
| C300 lamp | 3011 / 3012 / 3013 | 0.9 s each (3015 / 3016 / 3017) | the elevator button / petrol can / ping-pong ball shown |
| C415 lemon | 4150 | 1.05 s (4151) | film mi_start, the button place in C412 |
| C207 hydrogen balloon | 2771 | 4.3 s (2773), then the symbol's anim 6.6 s (2774) | explosive symbol pickable |
| C207 helium / neon balloon | 2776 / 2780 | 3.9 s (2778) / 4.7 s (2783) | balloon to the inventory (neon: v42 := 1) |
| C205 glass cutter | 2057 | 4.1 s (2058) | cutter with glass, ready for the magnifier |
| C206 microwave / mortar | 2356 / 2359 | 1.4 s (2357) / 4.5 s (2360) | dried lice / crushed lice |

Durations are the sums of the anim chains' `duration` fields up to the anim with the end event;
each anim in a chain also ends only on the first tick past its duration, so the real wait is a
little longer. The simulator's ticks cycle 15..17 ms: a fixed 16 ms stalls any anim whose
duration is a multiple of 16 (80, 400, …), because `t == duration` wraps to 0 without
ending (logic.md); the original's timer is not that regular.

### Optional content

Not needed for the ending (the walkthrough leaves it out; E-0607): the beach artist (C107,
v29, cans 1070100) and with him the cobalt-blue paint (razor blade 4100100 from C410 → sorter
→ cobalt → crucible → small jar, v31); the beach ice-cream seller after the kiosk moves (C105,
v4: dialogues only; the cold mixture 1030204 and the strawberries 3050300 serve only her);
the glacier artist's own dialogue (6051); the element sorter's lit buttons (all items but the
cartridge, the zinc mineral and, for v99, the crystal); the iron ore and pure iron (v90); the
gold ore (pickaxe 5070800); the can from C408 (pancake on the crack); the neon crack's
dialogue; the pipette and the water drop (C308); the mine's stone 4010200; mirror and tyre
5040200/5040300; the bedouin's seventh talk (strawberries, v6); the ice queen's dialogue
isdia 07 (6505); the paper 1030100 with salt (1082, sorter); the spade with camel dung
(3071, sorter); the small eggshells 5070600 (sorter); the binoculars' zoom (C619, v13).

### Dead ends

States the game cannot leave, both reached by ordinary play (the engine repairs both at
load, always on: Q-0601, E-0609; `simulate.py --repair` applies the same patches):

1. **Leaving the igloo with the queen melted** (E-0604, simulated): after event 6502
   (lava crucible on the queen, v35 := 6), C608's entry event 6081 has no case for v35 == 6
   and falls through to 6084, which raises the bridge (6081000, no click event). v35 leaves 6
   only through event 6112 (bucket on the queen in C611), and C611 opens only from C602
   (6503) and C602 only from the bridge (6080) or C611's end event. So once the player backs
   out of C602 or C611 before putting the melted queen in the bucket, the igloo stays shut:
   no strawberry bed (v9, v11), no tent, no kiosk flight, no opened bottle, no lookout, no
   chair (egg 6), and egg 2 needs v35 == 7. The game cannot be finished.
2. **The corkscrew before the bottle** (E-0605, simulated): the kiosk flies (event 6704,
   which also opens the bottle) only from dialogue record 9905061, and only if v44 == 1, i.e.
   the bottle was already taken from the crevice (1083). 9905061 sets v41 := 4, and event
   6011 has no case for v41 == 4, so the seller never says it again. The only other source of
   the opened bottle 1080300 is event 6704 itself (use 1080300 on 6012500) and the
   unreferenced event 6700; the corkscrew 6010400 has no use at all. So taking the bottle
   after that dialogue leaves the closed bottle 1080200 forever: no waterfall, no lookout, no
   chair, no egg 6. The data has the repair: event 1080 (take the bottle: if v92 == 1, the
   corkscrew already given, it hands out the opened bottle 1080300) exists but no object runs
   it; the crevice's state 3 runs 1083.
3. Not dead ends but closed doors for a while: the igloo stays shut until the lava man is met
   (v65), while v35 == 4 until the first ladder step (v37), while v35 == 5 until the lava
   crucible (v38), and while v35 == 7 until the crystal (v39); the lookout is out of reach
   until the waterfall melts (sliding down to the desert instead).

### Data that looks wrong

- **Events that name deleted objects** (E-0606, Q-0600). ge.dll's FindObj still returns an
  object after events 1 and 8 freed it (logic.md, Q-0401); `simulate.py` lists every such
  reference. The walkthrough makes eight, in six events, and a complete game cannot avoid
  most of them:
  - type 8 after a type 1 on the same object: 2341 and 2346 (taking the soap or paint jar:
    `remove` then `inv-`), 2057 (the glass cutter deletes the diamond that 2051 already
    deleted). Type 8 only searches the inventory list for the pointer (E-0405), so these
    compare a stale pointer and do nothing.
  - type 7: 6704's `inv+ 6010200` gives the mosquito net, which every complete game has
    used up before (5011 deletes it: the balloons need a third receipt, and every third
    receipt needs the paper made with the net). Type 7 reads the freed object's owner.
  - types 15/16: 9809021 hides the oil in the gingerbread house (5081500), deleted by 5510
    (the rod), which the lipstick needs first; C605's end event 6058 hides (v55 ≠ 3) or
    shows (v55 == 3, 6059) the glacier artist's objects 60508, 60512, 60513, which 91009121
    deleted, on every visit to C605 after the chair appears. Types 15/16 read the freed
    object's state and write its `visible`.
  - not in the walkthrough: 9809021's `inv+ 5080100` (the pancake) if it went into the can
    crack (4081), and 4712 → 4706's `inv+ 4130200` (coal after the iron, ladder step 1
    already on the mailbox).
- **The cold mixture's bucket stays invisible**: event 2800 hides the bucket (bucket with
  salt on the lab table), and 2802 (taking the cold mixture) sets it to state 4 and runs
  `inv+ 1030204`, which does nothing to an object already in the inventory (logic.md type 7),
  so the bucket is never shown again. Only the optional beach seller needs it (by v5, not by
  the item).
- Dialogue starts without a dialogue: events 800 (dialogue 0) and 900 (dialogue 900) name
  dialogues that do not exist; nothing runs them.
- Area events that no cell reaches (above); in R556 and R558 value 10 (area 9) has no
  event (logic.md).

### Unused content

(E-0608)

- **Developer set-ups**: events 2, 4, 5, 7 (nothing runs them) hold 84, 8, 15 and 2 `inv+`
  records, set progress variables (event 2: v5, v15, v17, v20, v26, v27, v31, v34,
  v36..v39, v47, v48, v55; events 4, 5, 7: v6, v7, v10, v18, v40, v42, v44, v99), and event
  2 runs 25 GotoWalkmap records in turn (the last, R254, wins); event 3 joins topics. v47 is
  set only by event 2, so C509's 5093 → 5095 branch (the forest artist's dialogue 06 by
  talking) is unreachable; the paper (5095 directly) is the way.
- "Magic" events 770 (v198 := 1), 777..780 (topics), 790..792, 795 (v199 + 1): unreferenced
  (792 is C603's later-visit event).
- Two dedications, reachable: clicking Gilbert at the pier before fishing (10420 state 0, event 1048)
  99 times in one visit opens dialogue 190000 ("Hej Jimpa og Jonathan! Mange kram fra morbror
  Danne!"); clicking Gilbert at the bottle machine (10230, event 1802) 99 times opens 190100
  (to Michael, "9 måneder ved spillets udgivelse", from Cici og Åke). The close-ups' events
  (1047, 1801) reset the counters (v197, v196) on entering and leaving; the comments say
  "Not used for the production".
- Close-ups never opened: C109 ("Länk till Walkmap Labbet", empty), C199 ("Heaven (temp)":
  the store for items that events hand out, e.g. soap, paint, pancake), C201 (the lever's
  compartment, likewise a store), C416 (the lava pool; its first event would play
  mi_rise.mpg).
- Events nothing runs (101 IDs): besides the above, alternative orders of lab recipes
  (2052, 2055, 2061..2063, 2072, 2243, 2247..2249, 2254, 2258..2260, 2314, 2380), the mailbox's
  other script (22121..22128), 1080 (above), 6700 (open the bottle), 6705/6706 (kiosk
  variants), 4021 (wok to the miner), 3062, 6501, and dialogue-chain entries.
- Dialogues never started: 30300, 31100, 31300, 31400, 50100, 80500, 80700, 100504.
- R900 "Flygkarta" (no folder, no close-ups).
