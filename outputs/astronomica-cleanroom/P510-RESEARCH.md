# P510: original movie-controlled puzzle

Reconstructed from D:/astro/SETUP/ASTRO.EXE and the original P510 resource
on 2 October 2026. This work belongs to the current cleanroom engine.

## Original evidence

`probe_p510_plot.py` follows custom 23 at segment 4:5163-528e and records
its three initial positions, movie ranges and QuickTime callback registrations.
`probe_p510_callbacks.py` executes the original callback instructions and
CS dispatch tables, separately from emulated data memory. It checks 27 events
in 432 cases (eight choices, including invalid values, and both success states).
The full traces and original code hashes are saved in evidence/p510-*.json.
The probes model external QuickTime calls as recorded calls; they do not run
QuickTime for Windows or prove original multimedia playback by themselves.

The three starts use movie units 0,1800,900, duration 359, and callbacks 20,21,22
at start+358. The time scale is 30. Events 20-24 and 26-32 sample local condition 4,
the five-button choice, at callback time. Choices 1/2 select one branch,
choices 4/5 the other, and choice 3 usually fails. Original exceptions are kept:
event 31 accepts the middle branch; event 30's middle callback uses end-1.
Callbacks 40-44 and 46-52 start the next node with a callback at start+356.
Event 53 plays the final 540-unit segment; event 54 marks global 26, calls success
only if previously unsolved, and returns to P136. Event 25 returns without success.
Both terminal paths cancel scene-local callbacks through scene loading.

The callback moves sprite 2's visual position, without changing its logical
coordinates or visibility. SWMoveSprite was inspected at 7:0a32-0a92.
The callback's _in_custom call is a no-op at 18:18ba-18c9. Its two reset process
flags concern the shared P523 callback and have no P510 branch dependencies.
Opcode 4 stops the selected movie; it does not erase the displayed frame.
The local-movie branch is reconstructed from 15:02f7-0360.

## Native implementation and validation boundaries

The production engine uses plot.h for the original transition rules,
script.cpp for opcode 4 and custom 23, and astronomica.cpp for decoder timing,
sprite movement and scene changes. FLATPLOT.MOV is loaded only for the expected
P510 resource shape and a valid 30Hz movie. Callback execution is driven by the
decoder's movie time; button state is read at execution, not captured at start.

The native comparison hash of the 432 original cases is 33d6e7a1. Eight accelerated
routes cover all three original random starts, both choice directions, first
and repeated victory, two failures, voluntary exit and countdown expiration.
These route checks seek the real movie decoder and are separate from continuous
playback. check_p510_continuous.py exercises a full winning path without seeks.
The continuous and complete regression results must pass before the checkpoint
is recorded. Manual audiovisual confirmation and help/return remain pending.

This document does not establish a whole-game completion percentage.
