# P522 future save research, 21 October 2026

This is fresh static inventory of `D:/astro/PLACES/P522/MEGAFILE.HYP`, with
current post-13-September cleanroom source consulted for observable fields.
Evidence is `evidence/p522-save-original.json`. No engine change, native run,
callback interpreter execution, save format or support claim is included.

The resource consumes all483379 bytes. It declares18 sprites,11 programs,
eight scene sounds, no movies or mouse rectangles, and69 commands. There are
no external-picture/load-background or commit-picture commands. Two local
declarations are `[1,0,8,2,1,4]` and `[1,1,8,0,0,8]`: values initialize from
field index3 to2 and0, not from the metadata8. Controls5–8 explicitly select
local0 values1–4 and the corresponding one-of-four button frames. Control14
launches only while local1==0. Exit2 goes to388; control4 goes to408.

Sprites1–8 have2 frames each, sprite9 has12 month frames, sprite10 has10 digit
frames, and clones11–13 share only sprite10's frames. The digit source is at
(160,404), while clones have their own(168,404),(177,404),(186,404) coordinates,
flags and subsequent selections. Remaining frame counts are2,11,11,1,1 for
sprites14–18. The initial year display is explicitly set to1991 by programs1–4;
program5 selects the second choice. Only sprites15/16 declare automatic framing
at80ms. No serialized sprite initially declares automatic movement.

Startup programs6/8/10 call custom15 setup for15/16/17. The Mars setup operands
include106/53, retained in the evidence; the current callback implementation
configures centers(300,140), orbit radii120/60 or226/113,30ms motion, delta(2,0)
and orbit flags. Actual source image geometry is54x52,40x40,43x25 for these
three sprites, constant across their respective frame sets.

The current engine exposes ProbeMotion.year (initial1991), yearArmed,
specialHit, flying, expired and three width/height pairs. Sprite state includes
stored center and rendered position separately, movement/frame timestamps,
delta, orbit sides, radii in moveData, frame selection/range/period and flags.
Earth updates month display and the year digits; yearArmed distinguishes a
crossing of the year boundary from merely being in January. specialHit is
sticky: launch only sets it for the original special windows and does not
clear an earlier hit. Hidden/failed probe state still retains ordinary movement
when the custom callback is inactive. The engine dispatches15,16,17 in sprite
order and can change probe position from Earth and Mars before the probe's
own step. A restore must preserve that order and timing.

The supplied original-code probe `outputs/astronomica-cleanroom/probe_p522_motion.py`
was consulted as text only. It identifies Earth3:0b2b, Mars3:0d75,
probe3:0e52 and launch4:32c4, preserving the caller-computed point and
precommit collision rectangle. Its existing assertions cover a calendar to2003,
special launch windows, failures and collision/correction matrices; none of
those computations was rerun here. The JSON records exact current source hashes
and anchor line numbers for the structures and handlers used by this research.

The main obstacle to a future idle contract is program0: after checking local1
for2 and scheduling success/departure, it recalls itself with opcode41[0]
after200ms. Consequently a non-flying phase is still an active animated scene
with recurring queued work. A generic requirement of pending-empty, no active
animation and scriptsIdle would exclude ordinary post-startup play. Supporting
this scene needs an explicit trusted poll continuation and its epoch/remaining
delay, or an equivalent verified recurring-job representation. Silently dropping
the queued check or restarting its delay on load changes success timing.

Suggested future checkpoints distinguish startup, ordinary orbit/no flight,
failed return, active launch and the transient success/expiry departure. The
contract must retain both locals/metadata and complete runner/RNG/known flags,
clock/count, dormant variant state, global/comet state and all18 mutable sprite
records. It must preserve calendar and sticky flags independently of current
display. Re-running custom15 setup would reset important state; restore should
rebind trusted callback identities without rerunning setup. Validate or rederive
the three geometry pairs from the original asset before live mutation. Keep
foreground audio and unrelated pending work outside the admitted contract.

Required native evidence remains: reachable poll boundaries and clock phases;
ordinary/failed/in-flight continuation; each choice and all special windows;
month/year rollover, yearArmed and sticky-hit history; expiry versus first/repeat
success; hidden movement; foreground rejection and natural voice end; full480-row
pixel equality; malformed-state atomicity; and a fresh-process physical slot.
No serializer, active-animation save support or completion percentage is proposed
as already verified by this static inventory.


## Separate native observations

P522-NATIVE-AUDIT.md records an isolated observation-only build:126 snapshots across four original routes,5830 poll checks/832 executions, and exact full-height/sprite records. It confirms persistent pending work after startup and hidden ordinary probe movement. This does not implement or validate a save format; the tests use SDL dummy audio/video.


## Narrow first implementation contract to investigate

The current runner stores each delayed job as a copied Script, a command index
and a uint32 since epoch. The pending observation is index6 of original program0,
whose last command is opcode41[0] with delay200. Its actual execution age210 in
this audit comes from the controlled30ms stepping; a save must retain the epoch,
not encode210 as a new gameplay period or restart a fresh200ms delay.

A first implementation can investigate ordinary no-flight and failed-return
boundaries with local1==0, exactly one trusted poll at that original command,
no queued actions or blocked clicks, and no foreground speech. Active flight,
startup queues and success waiting for its poll would remain rejected until
separately validated. This scope still has active Earth/Mars animation and hidden
ordinary probe movement, so all18 sprite records and ProbeMotion fields remain
necessary. The existing no-pending persistent export cannot simply be relaxed.

A future runner API should validate the entire queued script against the parsed
trusted original program0, not accept serialized commands, callback addresses or
an arbitrary index. It can store only the allowed poll epoch with the existing
605 persistent words, then recreate that one pending job from the trusted original
program after preflight. Preserve programLoadedAt separately from the poll epoch.
The pending generation counter and execution counter are implementation bookkeeping;
verify their required restore behavior rather than assuming they are gameplay data.

Before assigning a format, audit eligibility at multiple poll ages and immediately
before/at/after execution, including uint32 clock wrap and long scheduling gaps.
Compare full sprite/screen state and the next poll, calendar and movement update.
Negative tests must reject extra jobs, the wrong program/index/delay, button pulses,
foreground audio and partial startup without changing queue, sound or rendered state.
This is a proposed implementation scope, not tested serialization support.
