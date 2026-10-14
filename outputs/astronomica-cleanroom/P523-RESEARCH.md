# P523: original research checkpoint, 2 October 2026

P523 is integrated. The original research below precedes the native checkpoint at the end.
No old failed implementation was used for this research.

The original resource has 44 sprites, DANGERS.MOV, six control buttons for
custom 1, two buttons for custom 4, and startup custom 20/custom 5. The inventory,
command locations, disassembled operations and hashes are in p523-inventory.json.

Custom 20 initializes three process-static words DS:0145/0147/0149 to 33 each.
Custom 1 buttons 1-3 subtract 10 from one channel and buttons 4-6 add 10. The
original _spread function at 3:009e redistributes the other two channels using
single-precision temporary stores, caps them to 0..99 and truncates to integers.
The argument permutations matter: the last channel is calculated as a residual.
The original total can therefore be 98 or 99, not necessarily 99 at every step.
The y coordinate is truncated from 414 - value *0.55; x positions are 121,244,362.
Native floating-point equivalence still needs testing before implementation.

probe_p523_spread.py executes the original instructions and models their x87
stack, float32 stores, comparisons and integer truncation. Starting at 33/33/33,
all six buttons produce 5899 reachable states and 35394 transitions. Their graph
hash and representative boundary cases are in p523-spread.json. This is an
instruction-model result, not execution of the complete original Windows game.

Custom 4 sets the left or right response flag (DS:0b40/0b42) without clearing
the other. The original _qt_callme function clears both after each callback.
Both flags may be set simultaneously; evaluation order must be preserved.
Custom 5 sets movie range 0+602 and registers event 1 at 600 on callback slot 0 and
event 13 at 510 on slot 1, all at 30Hz. It hides sprites 5,6,1 and shows 7,11,18.
Two callback slots are essential; the single P510 slot cannot represent P523.

probe_p523_callbacks.py executes events 1..19 against 1728 combinations of channel
levels (0,19,20,29,30,39,40,59,60,74,75,99), four response-flag combinations and both prior success
states:262656 cases,60 distinct outcomes. External movie and visibility calls
are recorded, not executed. This is a boundary grid, not every reachable state.
Event 3 stops the movie and returns to P117 without victory. Event 12 stops it,
sets global 39, calls success only on first completion, and enters P524.
Events 13..19 control response opportunities and visibility while other callbacks
remain pending. Event 18 can schedule event 19 based on the second channel's 60
threshold. Main decision callbacks use thresholds20,30,40 and75 with flag priority.

The helpers at 3:0000-009e set visibility directly. hide_em hides every sprite
from 9 through 37 inclusive; show/hide affect the supplied sprite ID. Their code
hash is preserved in the inventory.

Next: reproduce setup and sprite positions, implement
both decoder-time callback slots, then compare the recorded calls and complete
real click routes. Test simultaneous flags, exact threshold choices, repeated
victory, failure, timing and continuous movie playback before enabling support.


## Integrated P523 checkpoint, 3 October 2026

Native P523 and full regression suite PASS.35 route scenes, not35 distinct
puzzles. Controls:5899 reachable states/35394 transitions. Callback comparison:
262656 cases, with the explicit malformed event8 call repair documented below.
Positions:100 exact x87 cases. Ten click routes include first/repeated victory,
five failures, simultaneous response flags, exit and opening help. A complete
winning movie route passed without seeks and with real input delays.
Manual audiovisual review, help return, saves and whole-game playthrough remain.

Original4:7a87-7a9f passes two WORDs to a two-DWORD movie-range function,
producing start5246601 and an uninitialized duration. The native engine uses
the explicit original WORD values3721/80 for this failure clip. This is a
documented compatibility repair, not literal emulation of undefined stack data.
The original probes now label that duration unknown; normalized native
reference hash:f8ea0405. Control hash:40e80615; position hash:742cfb9d.
P523 also needs the full movie duration before startup custom5 selects a range.


## Mentor help checkpoint, 4 October 2026

P408 mentor buttons now play their original contextual video ranges. Native
comparison passes1900 cases, with explicit no-hint handling for undefined
P524 variant0/9.170 decoded selections,37 source-scene returns, no-hint speech
and natural continuous segment completion pass, together with the full suite.
P523 help return resets modified controls and response flags and reinstalls
the movie callbacks; original input still works after returning.
The Windows help book (custom22), native saves and manual audiovisual review
remain incomplete.35 puzzle-route scenes remain verified, not35 distinct
puzzles; no whole-game completion percentage is asserted.
