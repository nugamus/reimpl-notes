"""Random dev_input for crash hunting: a new game, then random clicks, drags and keys.

    python engines/gilbert/tools/fuzz_input.py [seed] [seconds]
prints a dev_input string for run_test.sh (never presses Afslut, x 384..539 y 380..412).
"""

import random
import sys


def main() -> None:
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    rnd = random.Random(seed)
    cmds = ["1500:click 461 120", "3000:key 27"]
    t = 5000
    while t < seconds * 1000:
        t += rnd.randint(150, 1200)
        x, y = rnd.randint(64, 575), rnd.randint(50, 429)
        if 384 <= x <= 539 and 380 <= y <= 412:
            continue  # Afslut ends the run
        r = rnd.random()
        if r < 0.75:
            cmds.append(f"{t}:click {x} {y}")
        elif r < 0.9:
            cmds.append(f"{t}:move {x} {y}")
        elif r < 0.95:
            cmds.append(f"{t}:key 27")
        else:
            cmds.append(f"{t}:area {rnd.randint(1, 30)}")
    cmds.append(f"{t + 1000}:where")
    cmds.append(f"{t + 1500}:quit")
    print(";".join(cmds))


if __name__ == "__main__":
    main()
