# P409 advice and world countdown, 5 October 2026

Evidence comes only from the original D:/astro files. Custom27 at4:6313-67d6
matches34800 independently executed instruction cases (FNVbcb8ca85).
Custom32 matches108 cases (FNVbf6ea917). The clock import is timeGetTime,
MMSYSTEM ordinal607. Scene409 has three sprites (two clickable buttons),
one layer and uses P408/MENTORS.MOV via the original path redirect.

Advice priority is global45, first visit from208, completion milestones
9/22/26 with global6 stages, global56 then55, then random advice. Random
branch1 draws a group and a selection separately. The original frame offsets
and padding are preserved. Custom27 stops the movie after setting its range.
The first click plays the selected speaker at343/113 or143/113; repeated
clicks still grant permission57 and consume advice flags but stop playback.
The original local1 branch suppresses a second movie. Return runs custom32
immediately, then returns to the previous scene750ms later. Custom32 starts
only when global45 equals1 and global8 equals0; a zero clock remains zero.

Original _do_game at9:0a09-0cba matches10530 instruction cases, FNV0ae350b7.
Global60 mode1 checks unsigned elapsed time from global8. At strictly greater
than4/60/120/180/240/270/295 seconds, stages0..6 advance once and play global
sounds913..919 (S13..S19.WAV). Only one warning is emitted per update. After
300 seconds it sets mode3 and enters427, unless a stage warning ran first.
Global53==1 changes mode1 to2 but the same update still checks the timer.
Mode2 returns to1 when the item is absent, with checks on the next update.
Elapsed time continues while the item is held, as in the original. Nonzero
global8 is required; unsigned wraparound is preserved.

Native save version2 stores the logical game clock as an extra DWORD,
covered by the checksum. Loading restores its epoch before loading the scene,
including when the F5 menu pauses the clock. This preserves the original
nonzero sentinel and overflow arithmetic and excludes time outside the game.
Version1 inactive saves remain readable; active version1 timer data is rejected
because it has no recorded clock epoch and the prior engine did not run it.
The native menu pause freezes the timer as it freezes the rest of the engine.

Validation: check_advice.py, check_saves.py and runtime_test.py. Consult
advice-validation.json and development-validation.json for the last committed
PASS rather than treating this research note as a test result. No manual
playthrough or global completion percentage is claimed.

## Ending movies

The original P423 entry script plays F24.MOV then chooses424/435/436/437
with the original random command. Each branch plays its own FFATE_1..4.MOV
and enters425 after73000ms; the lead-in changes scene after23000ms. Native
configuration now loads these five original files. check_endings.py exercises
all four branches, decodes frames at several points of each movie, checks
transition boundaries and runs the lead-in continuously to its natural end.
The downstream logo/animated scenes432/433/0 remain a separate pending task.

probe_world_movies.py records20 movie-bearing world scenes from the original
resources, with P406's truncated resource reported explicitly. It confirms
P4's redirect to P2 at9:2612-2630. Opcode50 at15:0721-080e calls ReadBM twice
(the second call follows closing the handle), followed by imported graphics
operations. The three P2 palette BMPs have identical pixel index255 but
different color tables. This is research, not an implemented palette policy.


## Intro and logo checkpoint, 10 October 2026

The new-game click, P2/P4 movies and nine P3 cards now reach exploration27.
P4 reads its movie fromP2 as the original loader specifies. Opcode50's
Win16 display palette is adapted to native RGB rendering: both original
Cinepak video descriptions are24-bit. Its original OPEN2_B must decode,
the movie and screen must be RGB, and other contexts/names fail closed.
Logo0 handles state61=0/2 returning to menu and1 quitting after20000ms.
Quit accepts trailing condition closures only; following effects still fail.
P432/P433 moving text, stops, movie frames and continuous playback pass.
The prior full-suite failure was P423 reaching19.475s of video at the26s
wall deadline. The test now allows50s but still requires natural completion;
new diagnostics record wall/media/end times. Full regression PASS.
Intro continuous playback and manual audiovisual review remain unverified.
Evidence:probe_intro_logo.py, intro-logo-original.json and runtime logs.


Real-time introduction, 10 October 2026: PASS in the normal native main loop, with entry scripts and audio enabled, headless. P2 -> P3 -> P4 -> P27 completed without accelerated time. This verifies scene progression only. P2 media reached only about156s at the208s scene deadline, closing while playing. Investigate headless clock/performance; audiovisual continuity is NOT validated. Manual audiovisual review remains pending.


## P29 and audio clock, 11 October 2026

P29 original FLAT29.MOV integrated with both control orders, repeat-control guards, four decoded positions, redraw at65000ms, cursor release and delayed input unlock. Custom29 rebuilds background/sprites without stopping the movie. Original evidence in probe_world_interactions.py includes final display callback and cursor flag consumer. Native cursor movement is constrained below the movie; manual pointer review remains pending. World scenes82/222/231 remain unsupported.
The Oct10 intro timing discrepancy was reproduced in SDL dummy without game/video: 9.6595 audio seconds in12 wall seconds. On Windows WASAPI, P2 ends naturally before the208s transition and P4 advances69.994s at the70s transition. No production movie clock change was required. Real-audio intro proof retains its exact pre-P29 executable hash; the subsequent full native regression uses WASAPI and passes on the new build. Manual audiovisual review and full-game completion remain unverified.


## Remaining features inventory, 11 October 2026

Fresh original inventory parses420 resources; P406 remains a truncated resource.
Custom22 occurs in P1 and P408; custom33 only in P1. There are32 paired hover
targets across P1/P505/P519/P526, including four P505 sound triggers. Native
hover dispatch is not implemented yet. Original9:0857-0a03 and0cba-0dbd uses
per-target entered flags, queues entry/exit scripts, and does not repeat the
event while staying inside/outside. Pending work runs before pointer checks.
Cursor-bearing sprite early exit needs review before broad native support.
See probe_remaining_features.py and probe_hover_dispatch.py. These inventories
are not whole-game completion metrics.


## World movies82/222/231, 11 October 2026

Original MOV files now play in world panels82,222,231. Controller replay is scoped to supported world movies: completed playback seeks to0 before play; in-range playback preserves position. Original QCMC control-flow research executes762 boundary cases. Native tests cover arm toggles, unarmed rejection, four decoded positions, input/cursor release deadlines, P222 replay and in-range resume, P222 two-second sprite animation and exit407. Continuous native playback passes for29/82/222/231 with WASAPI. Complete native regression PASS. No extra puzzle completion count is claimed. Manual audiovisual/pointer review and a complete game playthrough remain pending.

Original hover transition audit:256 cases PASS, comprising64 state/hit combinations
for three sprites and64 for three rectangles, each repeated with stationary
pointer. Hit predicates are modeled; event-state and dispatch instructions
execute from ASTRO.EXE. Native hover implementation remains pending.
