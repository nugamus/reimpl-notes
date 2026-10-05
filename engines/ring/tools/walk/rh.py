"""Scripted play-through steps for the Ring engine's dev_input:
prints the dev_input line, and on stderr a timeout in seconds for the run."""
import sys
steps=[]; T=[0]
def at(dt, cmd): steps.append(f"+{dt}:{cmd}"); T[0]+=dt
def esc(s):
    for _ in range(int(s/1.5)): at(1500, "key 27 0")
at(2000, "zone 3 0"); at(3000, "where"); esc(25); at(2000, "where")
for b in range(3):
    at(500, "mov 0"); at(3000, "where"); esc(9)                          # the guard's first words
    at(500, f"obj {20001 + b} 1"); esc(9); at(5000, "where")            # he leaves his key
    at(500, f"obj {20004 + b} 0"); at(2000, "where")                    # take it: the way on opens
    at(500, "mov 1"); at(3000, "where")
at(100, "snap C:/tmp/rh-a.png")
at(500, "obj 20007 0"); at(2000, "where"); at(500, "mov 1"); at(3000, "where"); at(100, "snap C:/tmp/rh-b.png")
def hold(o): at(300, f"hold {o}")
# The goldfish: take it, give it at the stand: the necklace comes back and the way on opens.
at(500, "obj 20201 1"); at(4000, "where")
at(500, "obj 20202 2"); esc(12); at(4000, "where")
at(500, "mov 0"); at(3000, "where"); hold(20007); at(200, "obj 20204 0"); esc(9); at(5000, "where")
at(500, "mov 1"); at(3000, "where"); at(500, "mov 2"); at(3000, "where")
# 20301..20303: the necklace and Helmet&Frog.
at(500, "obj 20301 1"); esc(9); at(3000, "where"); hold(20203); at(200, "obj 20301 2"); at(4000, "where")
at(500, "obj 20301 0"); at(4000, "where")
at(500, "obj 20302 1"); esc(9); at(5000, "where"); at(500, "obj 20302 0"); at(4000, "where")
hold(10504); at(200, "obj 20303 1"); at(4000, "where"); hold(20203); at(200, "obj 20303 2"); esc(9); at(5000, "where")
at(500, "obj 20303 0"); at(4000, "where")
hold(20005); at(200, "obj 20304 0"); esc(9); at(5000, "where"); at(500, "mov 1"); at(3000, "mov 2"); at(3000, "where")
# 20401: the statue and the cells, Selfishness's machine.
hold(10000); at(200, "obj 20401 0"); at(4000, "where"); hold(20203); at(200, "obj 20403 0"); esc(9); at(6000, "where")
hold(20006); at(200, "obj 20404 0"); esc(9); at(5000, "where"); at(500, "mov 1"); at(3000, "mov 2"); at(3000, "where")
# The Daughter of the Rhine.
at(500, "obj 20501 0"); esc(15); at(3000, "where"); at(500, "obj 20501 3"); at(4000, "where")
at(500, "obj 20501 2"); esc(9); at(5000, "where"); at(500, "obj 20501 1"); at(4000, "where")
hold(20004); at(200, "obj 20502 0"); esc(9); at(5000, "where"); at(500, "mov 1"); at(3000, "mov 2"); at(3000, "where")
# The dive and the Rhine Gold.
hold(10504); at(200, "obj 10504 0"); at(5000, "where"); at(100, "snap C:/tmp/rh-c.png")
at(500, "obj 20700 0"); at(8000, "where"); at(100, "snap C:/tmp/rh-d.png")
print(";".join(steps)); print(T[0]//1000+60, file=sys.stderr)
