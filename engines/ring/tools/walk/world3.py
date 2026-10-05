"""Scripted play-through of Ring's third world, FO (the Forest), for the engine's dev_input: FO entered by `zone 4 0`, the wolves' hall scrolls and the dial,
the smithy (hunter's wall, mine, furnace, mold), the poison berries, the tree, the press and
the golem's panel, the fire arrow, worms and fishing, the hare, the wolf statue, Sieglinde's
door, story, cup and medallion, the sword Notung and the ending back to the hub
(games/ring/docs/fo.md "Flow"). The Wolf Vision goes through the bag (`wv`). Prints the
dev_input line; on stderr a timeout in seconds for the run. Snapshots go to C:/tmp/w3-*.png.
"""

import sys

steps = []
total = [0]


def at(dt, cmd):
    steps.append(f"+{dt}:{cmd}")
    total[0] += dt


def esc(seconds):  # Escape every 1.5 s ends the dialogue lines
    for _ in range(int(seconds / 1.5)):
        at(1500, "key 27 0")


def hold(o):
    at(300, f"hold {o}")


def obj(o, v, wait=1500):
    at(300, f"obj {o} {v}")
    at(wait, "where")


def movs(*indices):
    for m in indices:
        at(500, f"mov {m}")
        at(1500, "where")


def wv(index):  # the Wolf Vision clicked in the bag, `index` objects from the front
    at(500, "where")
    at(300, "rclick 320 240")
    for _ in range(max(0, index - 5)):  # scroll right, mouse away at once (tracking repeats)
        at(400, "click 625 200")
        at(0, "move 320 300")
    at(500, f"click {18 + 100 * min(index, 5) + 50} 60")
    at(1000, "varb 30017")


# Arrival (entry 0).
at(2000, "zone 4 0"); at(8000, "where")
# The wolves' hall: scrolls 1 and 2 swapped -> 30302; the Wolf Vision -> 30303; the dial to 0.
movs(2, 3, 1, 1, 1)
obj(30002, 0, 3000); obj(30003, 0, 3000)
hold(30009); obj(30002, 0, 3000); hold(30010); obj(30003, 0, 6000)
wv(0); at(500, "where")
movs(0)
at(500, "down 460 180")
for k in range(1, 25):
    at(120, f"move {460 + k} {180 + k}")
at(300, "up 484 204"); at(500, "varb 30016")
obj(30027, 0, 6000); at(100, "snap C:/tmp/w3-a.png")
# The smithy: the hunter's wall, the mine, the furnace, the mold.
movs(1, 3)
obj(30026, 0); obj(30026, 1); obj(30026, 5)
movs(0, 7)
obj(30040, 0); obj(30040, 4); obj(30040, 2); obj(30040, 1); obj(30040, 5)
movs(0, 5)
obj(30028, 0, 4000); hold(30030); obj(30028, 1, 4000); hold(30029); obj(30028, 1, 2000)
hold(30041); obj(30028, 1, 5000); obj(30028, 0, 4000)
movs(0, 8)
obj(30042, 0, 4000)
for k in range(7):
    hold(30033 + k); obj(30042, k + 1, 1000)
at(4000, "where")
# The poison berries with the Wolf Vision (index from the bag order, see `where`).
movs(2, 0, 0, 1, 1, 2, 2)
wv(5)
obj(30017, 0, 4000); obj(30017, 1)
movs(0, 1, 2)
obj(30050, 0, 5000); at(100, "varb 30036")  # the tree after arriving from 30402
# The press: juice and poison juice; the golem and the poison juice: a Panel.
movs(1, 6)
hold(30017); obj(30017, 5); obj(30017, 5, 3000); obj(30017, 5)
hold(30018); obj(30017, 5); obj(30017, 5, 3000); obj(30017, 5)
movs(0, 9)
hold(30043); obj(30044, 0, 3000); hold(30032); obj(30044, 1, 4000)
movs(0)
# The fire arrow at 30011.
movs(2, 0, 0, 1)
hold(30026); obj(30051, 1); hold(30053); obj(30051, 0, 4000); at(100, "varb 30034")
# Worms (Wolf Vision at 35020) and fishing.
movs(0, 2, 1, 1, 0, 1, 0, 2, 1)
wv(9)
hold(30043); obj(30049, 0, 4000); at(100, "varb 30038")
movs(0, 0, 0, 1)
obj(30046, 0); obj(30046, 1)
movs(0)
hold(30047); obj(30046, 3, 4000)
# The hare at 30003, then the wolf statue.
movs(0, 1, 1, 0, 2, 0, 0, 0, 0, 2)
hold(30020); obj(30025, 0, 6000)
movs(2, 3, 1, 1, 1, 1)
hold(30054); obj(30001, 0)
for k in range(3):
    hold(30021 + k); obj(30001, k + 1, 2000)
at(4000, "where"); obj(30001, 4)
# Sieglinde's door, her story, the cup, her medallion.
movs(0, 0, 0, 0, 0, 2)
obj(30025, 1, 2000)
obj(30100, 0, 4000); obj(30100, 1, 2000); esc(15); at(4000, "where")
obj(30102, 1, 2000); esc(45); at(30000, "where"); at(100, "pres 30109")
obj(30109, 0); at(15000, "pres 30109"); obj(30109, 0); hold(30032); obj(30108, 0, 5000)
hold(30055); obj(30102, 1, 2000); esc(12); at(5000, "where")
# The sword Notung: both medallions, the ending.
movs(0, 2, 5)
wv(10)
hold(30055); obj(30058, 0, 4000); hold(30056); obj(30058, 0, 4000)
at(100, "snap C:/tmp/w3-b.png"); esc(60); at(10000, "where"); at(100, "snap C:/tmp/w3-c.png")

print(";".join(steps))
print(total[0] // 1000 + 900, file=sys.stderr)
