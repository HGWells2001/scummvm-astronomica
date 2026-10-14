# Game-wide state and exploration, 4 October 2026

Original custom26 is segment4:5a91-6310 of the unchanged ASTRO.EXE.
probe_game_state.py executes the original instructions independently. The
native ScriptRunner matches2436 cases (FNVd253e90a), checking all100 local and
100 global values after each operation, plus42 resume/memory boundaries
(FNV662a3a5a). Bounds and missing runtime context/value are rejected before
execution. The production engine supplies the live completion counter.

Read key1 returns the completed-puzzle counter. Keys2/3 transfer globals52/53.
Key4 selects globals20..46 with selector1..27. Keys5..11 transfer globals55..61.
Mode0 reads into the selected local; mode1 writes back for keys2..11.
Invalid puzzle selectors and writes to read-only keys retain the original
no-op behavior. The unused last command argument must be zero in native input.

Key12 returns1. Key13 reads the original resume-game flag. Native code reports
false because the legacy gamestat loader/custom33 is not implemented: native
ScummVM saves are accessed through F5 and the launcher. Key14 is the old Win16
free-memory test. The port supplies a sufficient-memory result, with no
Windows Help process; it does not display a spurious legacy memory warning.
The original signed threshold arithmetic remains separately tested. These
two host adaptations are explicit, not deductions about the old executable.

Original sound operands are decremented by_read_command_mem9:30b0-30d8.
Direct IDs900..922 resolve to SOUNDS/S0.WAV..S22.WAV (_playSound9:3b38-3b85).
The engine now discovers these23 streams and validates commands against
available files, including serialized905 -> globalS4. External images are
also discovered in mode1 exploration scenes with zero sprite layers.

Native interaction checks cover the original P359 cabinet, P352 item pickup
and revisits, the P35 global59 door flag and P85 entry, the P98 completion
counter gate, eight P388 completion indicators, and P425 credit bookkeeping.
Two additional world keypads are covered by dedicated checks: P407's
seven-key sequence and wrong-key reset, and P422's four-key sequence while
its27-second exit timer is live. These world interactions are not additional
entries in the35 puzzle-route metric and have no manual confirmation yet.

## Next: P409 advice and permits

probe_p409_advice.py independently executes custom27 at4:6313-67d6:
34800 cases, FNVbcb8ca85. It records priority branches and all29 random draw
paths, with exact random-call counts, local0 side, global6 stage and global55/56
consumption. P409 uses P408/MENTORS.MOV: the original path redirect is
9:2630-2651, string DS20:03ce. Advice clips subtract5 from start and add20
to duration, like custom21. This is research only; P409 is not enabled yet.

Its click script first writes global57 through custom26/7, then invokes27.
The return button invokes custom32 before previous-place. Custom32 at
4:69c8-6a01 tests global45==1 and global8==0, sets global60, and stores an
imported clock result in global8. The relocation is MMSYSTEM ordinal607, timeGetTime; p409-clock.json
records it. probe_p409_return.py verifies108 original cases, FNVbf6ea917,
including existing timestamps and clock wrap values. Verify the downstream
lifecycle before integrating the return action. Do not admit the whole
P409 script with either custom operation missing. Windows help-book custom22,
legacy resume custom33, other exploration movies, mid-puzzle saves and a
complete audiovisual playthrough remain outstanding.


## Game-wide state checkpoint, 4 October 2026

Custom26 is integrated and matches2436 original instruction cases plus42
resume/memory boundaries. Cabinet/item persistence, world-door flag, live
completion count, hub indicators, credit bookkeeping and the P407/P422
keypad sequences pass native checks. Global voices and zero-layer exploration
images now support those original scripts. Full regression passes. See
GAME-STATE-RESEARCH.md for explicit legacy resume/memory adaptations.
P409 custom27 research covers34800 cases; it is not integrated yet. No new
whole-game percentage or manual completion is claimed.


## Advice checkpoint, 5 October 2026

P409 custom27/32 and world countdown are integrated and verified against
34800/108/10530 original cases. Native interaction, seven warning sounds,
expiry and continuous advice playback pass. Saves now use version2 (424
byte prefix) with clock epoch; inactive version1 remains readable. See
P409-RESEARCH.md. Four ending routes423/424/435..437 now play five movies and reach credits.
Full suite PASS; no global completion percentage claimed.
