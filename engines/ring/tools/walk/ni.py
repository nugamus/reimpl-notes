"""Scripted play-through steps for the Ring engine's dev_input:
prints the dev_input line, and on stderr a timeout in seconds for the run."""
# Builds a dev_input line from (time_ms, command) steps; Escape presses every 1.5 s between steps that wait for dialogue.
import sys
steps = []
t = 1500
def at(dt, cmd):
    global t
    t += dt
    steps.append(f"+{dt}:{cmd}")
def esc(seconds):  # skip dialogue lines for a while
    for _ in range(int(seconds / 1.5)):
        at(1500, "key 27 0")
at(0, "click 318 277"); at(100, "move 320 240")
at(25000, "where"); esc(20); at(2000, "where"); at(100, "snap C:/tmp/n1-a.png")
# The Mime: the Tile on his table first (he asks for Brutality), then Brutality on him.
at(500, "mov 1"); at(3000, "where"); at(100, "snap C:/tmp/n1-b.png")
at(500, "obj 10303 0"); esc(12); at(8000, "where")       # 10012 -> PlyCin 1546 -> 10013 -> back to 10301
at(500, "hold 10000"); at(200, "obj 10300 0"); at(8000, "where"); esc(12); at(8000, "where")  # 1512, 10014, 1547 Tile
at(500, "mov 1"); at(3000, "obj 10302 0"); esc(10); at(8000, "where")  # Frog
at(500, "mov 1"); at(3000, "obj 10305 0"); esc(15); at(8000, "where")  # Tear
# Stage 2: Glug brings the car to the Mime's stop, then the rail line to the console.
at(500, "mov 0"); at(12000, "where")                     # 10301 -> 10003
at(500, "obj 10001 3"); at(3000, "where")               # call Glug: puzzle 10001
at(500, "hold 10001"); at(200, "obj 10001 1"); at(12000, "where")   # put Glug down: puzzle 10002
at(500, "hold 10002"); at(200, "obj 10001 2"); at(12000, "where")   # feed the Minerals: the car comes
at(500, "obj 10001 4"); at(3000, "where"); at(100, "snap C:/tmp/n2-a.png")   # back to 10003
for m in (0, 1, 1, 1, 0, 0, 0, 0, 0, 0):
    at(500, f"mov {m}"); at(12000, "where")
at(100, "snap C:/tmp/n2-b.png")
# Stage 3: the console.
at(500, "obj 10100 1"); at(1000, "where"); at(100, "snap C:/tmp/n3-a.png")
at(500, "click 400 285"); at(5000, "snap C:/tmp/n3-b.png")         # cover 1 opens
at(500, "hold 10303"); at(200, "click 120 250"); at(1500, "where")  # the Tile on its holder
for x, y in ((238, 264), (252, 227), (286, 227), (264, 242), (273, 212), (275, 264)):
    at(700, f"click {x} {y}")
at(1500, "snap C:/tmp/n3-c.png"); at(100, "where")
at(500, "click 400 285"); at(5000, "snap C:/tmp/n3-c2.png")   # close cover 1
at(500, "click 427 330"); at(5000, "snap C:/tmp/n3-d.png")   # cover 2
at(500, "hold 10000"); at(200, "click 300 350"); at(15000, "where"); at(100, "snap C:/tmp/n3-e.png")  # Brutality on the hologram
at(500, "click 200 200"); at(2000, "where"); at(100, "snap C:/tmp/n3-f.png")   # the hologram puzzle
at(500, "down 244 240"); at(300, "move 250 250"); at(300, "move 263 286"); at(300, "up 263 286"); at(4000, "snap C:/tmp/n3-g.png")
at(100, "varw 10100"); at(100, "varb 10104")
at(500, "mov 0"); at(1500, "where"); at(500, "click 427 330"); at(4000, "where")     # back to the console, close cover 2
at(500, "move 320 440"); at(1000, "move 320 240"); at(500, "where")
at(500, "mov 0"); at(12000, "where"); at(500, "mov 2"); at(12000, "where"); at(100, "snap C:/tmp/n3-h.png")
# Stage 4: the tiles to 0, 0, 0 open Erda's room.
at(500, "mov 1"); at(2000, "where"); at(100, "varw 10600"); at(100, "varw 10601"); at(100, "varw 10602")
at(500, "down 420 140"); at(200, "move 380 140"); at(200, "move 330 140"); at(200, "move 276 140"); at(300, "up 276 140")
for _ in range(2):
    at(500, "down 415 330"); at(200, "move 380 330"); at(200, "move 320 330"); at(200, "move 271 330"); at(300, "up 271 330")
at(3000, "where"); at(100, "snap C:/tmp/n4-a.png")
# Stage 5: Erda's room.
at(500, "obj 10505 0"); at(3000, "where")
at(500, "mov 1"); at(1000, "mov 1"); at(1000, "where"); at(300, "click 318 297"); at(4000, "where")
at(500, "mov 0"); at(1000, "mov 0"); at(1000, "mov 3"); at(1000, "mov 1"); at(1000, "mov 1"); esc(12); at(3000, "where"); at(100, "snap C:/tmp/n5-a.png")
at(500, "mov 0"); at(1000, "mov 0"); at(1000, "where")
at(500, "mov 0"); at(2000, "mov 0"); at(2000, "mov 0"); at(2000, "where")
# Stage 6: the handle sends the car back to 10005, then the line to the speaker.
at(500, "obj 10100 1"); at(1000, "down 505 220"); at(200, "move 525 220"); at(200, "move 545 220"); at(200, "move 560 220"); at(300, "up 560 220"); at(3000, "where")
for m in (1, 1, 1, 1, 1, 0, 2):
    at(500, f"mov {m}"); at(2000, "where")
at(100, "snap C:/tmp/n6-a.png")
# Stage 7: the speaker.
at(500, "mov 1"); at(2000, "where"); at(500, "click 310 155"); esc(15); at(2000, "where")
at(500, "down 360 230"); at(200, "move 360 245"); at(200, "move 360 265"); at(300, "up 360 265"); at(4000, "where"); esc(15); at(3000, "where")
at(100, "snap C:/tmp/n7-a.png")
# Stage 8: Glug brings the car to the speaker, then the valves.
at(500, "obj 10001 3"); at(2000, "where"); at(500, "hold 10002"); at(200, "obj 10001 2"); at(2000, "where")
at(500, "obj 10001 4"); at(2000, "where")
for m in (0, 1, 1):
    at(500, f"mov {m}"); at(2000, "where")
at(500, "mov 2"); at(2000, "where")
at(500, "down 315 237"); at(200, "move 315 255"); at(200, "move 315 270"); at(200, "move 315 282"); at(300, "up 315 282"); at(1500, "varb 10420")
at(500, "mov 0"); at(2000, "mov 3"); at(2000, "where")
at(500, "down 324 239"); at(200, "move 324 255"); at(200, "move 324 270"); at(200, "move 324 285"); at(300, "up 324 285"); at(1500, "varb 10421")
at(500, "mov 0"); at(2000, "where"); at(100, "snap C:/tmp/n8-v.png")
# Stage 9: the heater room, the door, the water without the hologram: game over 1.
at(500, "mov 1"); at(2000, "where"); at(500, "mov 1"); at(2000, "where"); at(500, "mov 2"); at(2000, "where")
at(500, "obj 10440 0"); at(2000, "where"); at(500, "obj 10450 0"); at(1500, "snap C:/tmp/n9-a.png"); at(6000, "where"); at(100, "snap C:/tmp/n9-b.png")
print(";".join(steps)); print(t // 1000 + 15, file=sys.stderr)
