# Running the original's code instead of reading it

When a format's grammar or a table lives in a long function (a `Serialize`, a level
set-up full of calls), run that function under Unicorn rather than decompiling it: feed it
the real file, stub what it calls, and record what it reads, writes or pushes.

- **Grammar from a loader**: Grumpa's `.abi` character records came from running the game's
  own `CFXCharacter::Serialize` under Unicorn (`engines/grumpa/tools/abiemu.py`, E-0401):
  hooks on the stream's read calls log each field's size and order, which becomes the
  parser. `charemu.py` runs an action function for every (action, clip) pair and prints
  the queue it builds, instead of reading a large switch with inlined `std::deque` code.
- **Tables from set-up code**: Ring's zone set-ups ran in Unicorn with their calls stubbed,
  so every loop comes out unrolled as a flat list of calls (E-0094); it replaced a static
  call scanner and checks its lists.

How: map the dumped or decrypted image at its image base; give it a stack and a fake
`this` object with the fields the function touches; stub imports and other functions with
hooks that log arguments and return plausible values; stop at the return. Validate the
result like any parser (rule 2): the whole corpus, every byte.

Only the facts it produces go into specs; the emulator scripts are tools.
