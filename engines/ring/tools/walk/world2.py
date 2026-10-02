"""Scripted play-through of Ring's second world, N2 and RO, for the engine's dev_input
(CLAUDE.md, Ring "Test"; games/ring/docs/n2.md, ro.md "Flow"). Prints the dev_input line;
on stderr a timeout in seconds for the run. Snapshots go to C:/tmp/w2-*.png.

    python world2.py n2                 # N2 from its entry 0 to its end (GoZone(5, 0))
    python world2.py ro                 # RO from entry 0 to the shuffled tiles, logging the grid
    python world2.py ro <cells>         # RO to its end: <cells> = the tile clicks, e.g. 22,21,...
    python world2.py solve <grid>       # the clicks for a grid logged by `ro` (17 values)
    python world2.py ro-end             # from the egg's puzzle 40012 to RO's end: the game
                                        # domain needs dev_place=p40012, dev_bag=40012,40013

RO's tiles are shuffled with the engine's random numbers: run `ro` with the game domain's
`random_seed` fixed, feed the logged grid to `solve`, then run `ro <cells>` with the same seed.
"""

import heapq
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


def drag(x0, y0, x1, y1, n=3):
    at(500, f"down {x0} {y0}")
    for k in range(1, n + 1):
        at(200, f"move {x0 + (x1 - x0) * k // n} {y0 + (y1 - y0) * k // n}")
    at(300, f"up {x1} {y1}")


def n2():
    # Arrival: the message and the Mime's dialogue, at the Mime (70300).
    at(2000, "zone 8 0"); at(2000, "where"); esc(45); at(2000, "where"); at(100, "snap C:/tmp/w2-a.png")
    movs(0, 2)                                             # 70300 -> 70001 -> 70100
    # The console: cover 2 (the first press closes it, the second opens), the hologram.
    at(500, "obj 70100 1"); at(1000, "where")
    at(500, "click 427 330"); at(4000, "click 427 330"); at(4000, "where")
    at(500, "click 200 200"); at(2000, "where")
    drag(244, 240, 263, 286); at(4000, "varw 70016"); at(100, "varb 10104")   # the cross at 12
    drag(410, 275, 410, 330, 4); at(3000, "varb 70012"); esc(12); at(3000, "where")  # the dam
    at(100, "snap C:/tmp/w2-b.png")
    movs(0); at(500, "click 427 330"); at(4000, "move 320 440"); at(1000, "move 320 240"); at(500, "where")
    # The fire place and the creatures' room.
    movs(0, 2)                                             # 70100 -> 70101 -> 70600
    hold(70000); at(200, "obj 70000 0"); at(3000, "where")
    at(500, "obj 70503 0"); at(1000, "where")
    for m in (1, 2, 3):
        movs(m, 1)
        at(300, f"obj {70499 + m} 0"); at(1000, "where")
        movs(0, 0)
    # Back: 70500 -> 70600 -> 70101 -> 70100, the handle to the hall.
    movs(0, 0, 0)
    at(500, "obj 70100 1"); at(1000, "where"); drag(505, 220, 560, 220, 4); at(3000, "where")
    # The Mime takes the Chrysoberyl, gives the Cage.
    movs(1); hold(70503); at(200, "obj 70300 0"); at(3000, "where")
    # The heater: the tear out of its casing.
    movs(0, 3, 1, 0)                                       # 70300 -> 70001 -> 70400 -> 70410 -> 70411
    at(500, "obj 70404 0"); at(5000, "where"); at(500, "obj 70404 1"); at(1000, "where"); at(100, "varb 70001")
    at(500, "click 380 350"); at(5000, "where")             # close the casing: the way out opens
    # To the hall: Alberich's test begins.
    movs(0, 1, 0); esc(30); at(3000, "where"); at(100, "snap C:/tmp/w2-c.png")
    for r, creature in enumerate((70500, 70501, 70502)):
        esc(6); at(2000, "where"); at(100, "varb 70014")
        hold(creature); at(200, f"obj {creature} 1"); at(3000, "where"); esc(6)
    esc(12); at(5000, "where"); at(100, "snap C:/tmp/w2-d.png")


def ro(cells):
    at(2000, "zone 5 0"); at(3000, "where"); esc(6); at(2000, "where")
    movs(1); hold(40000); at(200, "obj 40010 0"); at(3000, "where")
    if not cells:
        for rc in [12] + [10 * r + c for r in range(2, 6) for c in range(1, 5)]:
            at(50, f"varb {40501 + rc}")
        return
    for c in cells:
        at(400, f"obj 40011 {c}")
    at(3000, "where"); at(100, "varb 40701")
    # The dials: 0 and 1 turn by themselves; 2, 3, 4 dragged to 60, 50, 50.
    at(3000, "snap C:/tmp/w2-e.png")
    for x, dy in ((313, 60), (344, 50), (375, 50)):
        drag(x, 210, x, 210 + dy, 4); at(1500, "where")
    for d in range(5):
        at(100, f"varb {40601 + d}")
    at(2000, "where")
    ro_end()


def ro_end():
    # The Ring, then the Crown: the faces' dialogue, the cave changes.
    hold(40012); at(200, "obj 40010 2"); at(1000, "where")
    hold(40013); at(200, "obj 40010 2"); esc(25); at(4000, "where"); at(100, "snap C:/tmp/w2-f.png")
    movs(0, 0, 0, 1)                                       # 40000 -> 40001 -> 40004 -> 40005 -> 40060
    # The switches all on: pipes 1, 3, 4, 6 clicked with the lever at stop 0.
    for p in (1, 3, 4, 6):
        at(500, f"obj 40201 {p}"); at(3500, f"varb {40200 + p}")
    # The pipes 6..0, each with the lever at stop p + 1 (stop k at x = 553 - 62 k).
    x = 553
    drag(x, 123, x - 420, 123, 14); at(1500, "varb 40804"); x -= 420
    for p in range(6, -1, -1):
        at(500, f"obj 40201 {p}"); at(7000, "where")
        if p:
            drag(x, 123, x + 60, 123, 4); at(1500, "varb 40804"); x += 60
    at(8000, "where"); at(100, "varb 40802"); at(100, "snap C:/tmp/w2-g.png")
    # The keyboard: keys 7..14 as digits 0..7, the tune 01276534.
    keyx = {7: 319, 8: 352, 9: 384, 10: 419, 11: 450, 12: 482, 13: 518, 14: 553}
    for d in "01276534":
        at(700, f"click {keyx[7 + int(d)]} 411")
    at(10000, "where"); at(100, "snap C:/tmp/w2-h.png")


def solve(grid):
    """Weighted A* over the tiles: `grid` = cell 12 then cells 21..24, ..., 51..54 (0 the gap)."""
    order = [12] + [10 * r + c for r in range(2, 6) for c in range(1, 5)]
    start = dict(zip(order, grid))
    goal_last = dict((c, c) for c in order[1:])
    goal_last[12], goal_last[22] = 22, 0  # the last click moves 22 down out of cell 12
    cells = set(order)

    def key(s):
        return tuple(s[c] for c in order)

    def h(s):
        d = 0
        for c, t in s.items():
            if t:
                g = next(k for k, v in goal_last.items() if v == t)
                d += abs(g // 10 - c // 10) + abs(g % 10 - c % 10)
        return d

    frontier = [(0, 0, key(start), [])]
    seen = {key(start)}
    while frontier:
        _, g, k, path = heapq.heappop(frontier)
        s = dict(zip(order, k))
        if s == goal_last:
            return path + [12]
        gap = next(c for c, t in s.items() if t == 0)
        for d in (-10, 10, -1, 1):
            c = gap - d  # the tile at c moves into the gap
            if c in cells:
                n = dict(s)
                n[gap], n[c] = n[c], 0
                nk = key(n)
                if nk not in seen:
                    seen.add(nk)
                    heapq.heappush(frontier, (g + 1 + 3 * h(n), g + 1, nk, path + [c]))
    return None


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "n2"
    if mode == "solve":
        print(",".join(map(str, solve([int(v) for v in sys.argv[2].split(",")]))))
        sys.exit(0)
    if mode == "n2":
        n2()
    elif mode == "ro-end":
        at(2000, "where")
        ro_end()
    else:
        ro([int(c) for c in sys.argv[2].split(",")] if len(sys.argv) > 2 else [])
    print(";".join(steps))
    print(total[0] // 1000 + 300, file=sys.stderr)
