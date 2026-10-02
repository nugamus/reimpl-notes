"""Scripted play-through of Ring's first world, NI and RH, for the engine's dev_input
(CLAUDE.md, Ring "Test"): from AS's puzzle 80007 (dev_place=p80007) into NI, through the
Mime, Glug and the car, the console, the tiles and Erda's room, the speaker, the console
again (dam and cross), the valves, the door and the water to RH, RH from the tunnels to the
Rhine Gold, back in NI the tear in its casing, the heater, and NI's end to the hub
(games/ring/docs/ni.md, rh.md "Flow"). Prints the dev_input line; on stderr a timeout in
seconds for the run. Snapshots go to C:/tmp/w1-*.png.
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


def drag(x0, y0, x1, y1, n=3):
    at(500, f"down {x0} {y0}")
    for k in range(1, n + 1):
        at(200, f"move {x0 + (x1 - x0) * k // n} {y0 + (y1 - y0) * k // n}")
    at(300, f"up {x1} {y1}")


def glug_brings_car():  # call Glug where the player stands, feed it: the car comes there
    at(500, "obj 10001 3"); at(1500, "where")
    hold(10002); at(200, "obj 10001 2"); at(2000, "where")
    at(500, "obj 10001 4"); at(1500, "where")


# NI: arrival and the Mime.
at(1500, "click 318 277"); at(100, "move 320 240"); at(20000, "where"); esc(20); at(2000, "where")
movs(1)
at(500, "obj 10303 0"); esc(12); at(6000, "where")
hold(10000); at(200, "obj 10300 0"); at(6000, "where"); esc(12); at(6000, "where")
movs(1); at(500, "obj 10302 0"); esc(10); at(6000, "where")
movs(1); at(500, "obj 10305 0"); esc(15); at(6000, "where")
# Glug and the car, the line to the console.
movs(0)
at(500, "obj 10001 3"); at(2000, "where")
hold(10001); at(200, "obj 10001 1"); at(2000, "where")
hold(10002); at(200, "obj 10001 2"); at(2000, "where")
at(500, "obj 10001 4"); at(2000, "where")
movs(0, 1, 1, 1, 0, 0, 0, 0, 0, 0)
# The console: cover 1, the tile, the mosaic, cover 2, the hologram, the cross at 12.
at(500, "obj 10100 1"); at(1000, "where")
at(500, "click 400 285"); at(5000, "where")
hold(10303); at(200, "click 120 250"); at(1500, "where")
for x, y in ((238, 264), (252, 227), (286, 227), (264, 242), (273, 212), (275, 264)):
    at(700, f"click {x} {y}")
at(1500, "where"); at(500, "click 400 285"); at(5000, "click 427 330"); at(5000, "where")
hold(10000); at(200, "click 300 350"); at(15000, "where")
at(500, "click 200 200"); at(2000, "where")
drag(244, 240, 263, 286); at(4000, "varw 10100")
movs(0); at(500, "click 427 330"); at(4000, "move 320 440"); at(1000, "move 320 240"); at(500, "where")
# The tiles and Erda's room.
movs(0, 2, 1)
drag(420, 140, 276, 140, 4)
for _ in range(2):
    drag(415, 330, 271, 330, 4)
at(3000, "where")
at(500, "obj 10505 0"); at(3000, "where")
movs(1, 1); at(300, "click 318 297"); at(4000, "where")
movs(0, 0, 3, 1, 1); esc(12); at(3000, "where")
movs(0, 0, 0, 0, 0)
# The handle: the car back to 10005; the line to the speaker and its dialogues.
at(500, "obj 10100 1"); at(1000, "where"); drag(505, 220, 560, 220, 4); at(3000, "where")
movs(1, 1, 1, 1, 1, 0, 2, 1)
at(500, "click 310 155"); esc(15); at(2000, "where")
drag(360, 230, 360, 265); at(4000, "where"); esc(15); at(3000, "where")
# Back to the console: the dam open and the cross at 0 (byte 10106).
glug_brings_car()
movs(0, 1, 0, 0, 0, 0, 0, 0)
at(500, "obj 10100 1"); at(1000, "where"); at(500, "click 427 330"); at(5000, "click 200 200"); at(2000, "where")
drag(320, 260, 320, 330, 4); at(1000, "varb 10105")
drag(244, 240, 273, 281); at(4000, "varw 10100"); at(100, "varb 10106")
movs(0); at(500, "click 427 330"); at(4000, "move 320 440"); at(1000, "move 320 240"); at(500, "where")
at(500, "obj 10100 1"); at(1000, "where"); drag(505, 220, 560, 220, 4); at(3000, "where")
# The valves, the heater room, the door, the water with Helmet&Frog: on to RH.
movs(1, 1, 1, 1, 1, 1, 2)
drag(315, 237, 315, 282, 4); at(1500, "varb 10420")
movs(0, 3)
drag(324, 239, 324, 285, 4); at(1500, "varb 10421")
movs(0, 1, 1, 2)
at(500, "obj 10440 0"); at(3000, "where")
hold(10504); at(200, "obj 10450 0"); at(4000, "where"); at(100, "snap C:/tmp/w1-a.png")
at(500, "obj 10460 1"); at(4000, "where"); esc(25); at(2000, "where")
# RH: the tunnels, keys, the goldfish, the necklace, the machines, the Daughter, the Rhine Gold.
for b in range(3):
    movs(0); esc(9)
    at(500, f"obj {20001 + b} 1"); esc(9); at(5000, "where")
    at(500, f"obj {20004 + b} 0"); at(2000, "where")
    movs(1)
at(500, "obj 20007 0"); at(2000, "where"); movs(1)
at(500, "obj 20201 1"); at(4000, "where"); at(500, "obj 20202 2"); esc(12); at(4000, "where")
movs(0); hold(20007); at(200, "obj 20204 0"); esc(9); at(5000, "where")
movs(1, 2)
at(500, "obj 20301 1"); esc(9); at(3000, "where"); hold(20203); at(200, "obj 20301 2"); at(4000, "where")
at(500, "obj 20301 0"); at(4000, "where")
at(500, "obj 20302 1"); esc(9); at(5000, "where"); at(500, "obj 20302 0"); at(4000, "where")
hold(10504); at(200, "obj 20303 1"); at(4000, "where"); hold(20203); at(200, "obj 20303 2"); esc(9); at(5000, "where")
at(500, "obj 20303 0"); at(4000, "where")
hold(20005); at(200, "obj 20304 0"); esc(9); at(5000, "where"); movs(1, 2)
hold(10000); at(200, "obj 20401 0"); at(4000, "where"); hold(20203); at(200, "obj 20403 0"); esc(9); at(6000, "where")
hold(20006); at(200, "obj 20404 0"); esc(9); at(5000, "where"); movs(1, 2)
at(500, "obj 20501 0"); esc(15); at(3000, "where"); at(500, "obj 20501 3"); at(4000, "where")
at(500, "obj 20501 2"); esc(9); at(5000, "where"); at(500, "obj 20501 1"); at(4000, "where")
hold(20004); at(200, "obj 20502 0"); esc(9); at(5000, "where"); movs(1, 2)
hold(10504); at(200, "obj 10504 0"); at(5000, "where")
at(500, "obj 20700 0"); at(6000, "where"); esc(9); at(3000, "where"); at(100, "snap C:/tmp/w1-b.png")
# NI again (entry 3): Glug to the Mime's stop, the line to the heater, the tear in its casing.
movs(0)
glug_brings_car()
movs(0, 1, 1, 1, 1, 1, 1, 0)
at(500, "obj 10430 0"); at(5000, "where")
hold(10305); at(200, "obj 10430 1"); at(2000, "where")
at(500, "click 380 350"); at(6000, "varb 10431"); at(100, "where")
at(15000, "where"); at(3000, "snap C:/tmp/w1-c.png"); esc(30); at(5000, "where"); at(100, "snap C:/tmp/w1-d.png")

print(";".join(steps))
print(total[0] // 1000 + 600, file=sys.stderr)
