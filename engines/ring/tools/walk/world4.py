"""Scripted play-through of Ring's world 4, WA (Walhalla), for the engine's dev_input
(CLAUDE.md, Ring "Test"): from WA's entry 0 (the first step is `zone 6 0`) through the four
tasks (50300 with the Beam, the golem and its grid, the Conch and the leaf, the tree), the desk
and the letter burnt, the switches aligning the beam, the Rope and the ending back to the hub
(games/ring/docs/wa.md "Flow"). Prints the dev_input line; on stderr a timeout in seconds for
the run. Snapshots go to C:/tmp/w4-*.png.
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


def movs(*indices):
    for m in indices:
        at(500, f"mov {m}")
        at(1500, "where")


def obj(o, v, wait=1500):
    at(500, f"obj {o} {v}")
    at(wait, "where")


# Arrival: the Beam and the Golem, the dialogue at 50001.
at(2000, "zone 6 0"); at(3000, "where"); esc(12); at(2000, "where")
# 50300 with the Beam (progress 1), then the Bark at 50302.
movs(0, 0, 0, 0, 2, 1, 1)
hold(50000); obj(50300, 0, 4000); esc(6)
movs(1)
obj(50302, 0)
# The Conch lit with the Beam (50302 -> 50304 by the ways switched on by the task).
movs(5)
hold(50000); obj(50301, 0, 4000)
# The golem: the Flower, the Golem put down, its parts into their sockets.
movs(0, 3, 2, 0, 2, 1)
obj(50402, 0)
movs(1)
hold(50400); obj(50400, 0)
for part, socket in ((50431, 1), (50432, 20), (50433, 300), (50434, 4000), (50435, 50000), (50436, 600000)):
    obj(part, 0, 500); obj(part, socket, 800)
at(500, "vard 50000")
obj(50437, 0, 500); obj(50437, 7000000, 4000)
at(500, "vard 50000"); at(100, "snap C:/tmp/w4-a.png")
# The grid: the seven pieces in their cells; the Feather (progress 2).
movs(2)
for piece, cell in ((50451, 30), (50452, 61), (50453, 1), (50454, 33), (50455, 26), (50456, 46), (50457, 42)):
    obj(piece, 0, 500); obj(50499, cell, 800)
at(3000, "where"); at(100, "varb 50012"); at(100, "snap C:/tmp/w4-b.png")
# The tree: the Sword and the Apple, the Flower, Apple and Bark on their branches.
movs(0, 0, 0, 2, 1)
obj(50501, 0); obj(50502, 0)
for branch, item in ((0, 50402), (1, 50502), (3, 50302)):
    obj(50503, 10 + branch); hold(item); obj(50503, branch); movs(0)
at(100, "varw 50000")
# The Conch freed with the Sword and taken; the Sword back.
movs(0, 0, 1, 1, 2, 3, 5)
hold(50501); obj(50301, 0, 5000)
obj(50301, 1); obj(50301, 0)
# The leaf: the Sword on 50202, the Conch on 50203 (progress 3).
movs(1, 3, 2, 1, 1, 2, 1)
hold(50501); obj(50202, 0, 4000)
hold(50301); obj(50203, 0, 8000)
at(100, "varb 50001"); at(100, "varb 50012")
# The Leaf on the tree: the Rope (progress 4).
movs(0, 0, 0, 0, 0, 0, 2, 1)
obj(50503, 12); hold(50201); obj(50503, 2, 5000)
at(100, "varw 50000"); at(100, "varb 50012"); at(100, "snap C:/tmp/w4-c.png")
# The desk at 50108: the letter written, the Ashes clicked during its hold.
movs(0, 0, 0, 0)
obj(50100, 0, 4000)
obj(50101, 0, 500); obj(50104, 9, 500)          # Ink on the inkwell
obj(50103, 2, 500); obj(50104, 9, 500)          # the Stylet into it
obj(50102, 1, 500); obj(50103, 8, 500)          # the Paper on its place
obj(50104, 9, 500); obj(50103, 8, 4000)         # Ink & Stylet: the letter
at(100, "varb 50011"); obj(50105, 0, 4000)      # the Ashes during the hold
at(100, "varb 50012"); at(2000, "where"); at(100, "snap C:/tmp/w4-d.png")
# The switches: s1 and s2 align the beam (progress 6).
movs(3)
obj(50600, 1, 800); obj(50600, 2, 8000)
at(100, "varb 50012"); at(100, "snap C:/tmp/w4-e.png")
# The Rope at 50602: the ending, back to the hub.
movs(0, 1)
hold(50504); obj(50601, 0, 8000)
esc(60); at(5000, "where"); at(100, "snap C:/tmp/w4-f.png")

print(";".join(steps))
print(total[0] // 1000 + 900, file=sys.stderr)
