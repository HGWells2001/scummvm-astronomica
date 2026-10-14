# P502/P503/P504: original comet behavior

Status, 1 October 2026: all three scenes are integrated in the ScummVM
engine. Scoped native tests pass: 30 trajectories, 1920 setup/display states,
nine reference compositions, the complete P502-P503-P504-P527 chain,
repeated success, low/high speed, wrong direction and voluntary exits.
The saved development manifest identifies the latest full-suite checkpoint.
Manual playtesting of these scenes has not yet been performed.

## Reproducible evidence

- `probe_comet_state.py`: executes custom8 at segment4:0ca5..1c33;
  640 display configurations and 1280 launch configurations, including
  initially empty and already-set success flags. verifyCometSetup compares
  all1920 cases against native locals, transition/lock result, sprite fields
  and callback selection. AD10 is implicit in the shared ellipse helper.
- `probe_comet_motion.py`: executes callbacks in segment3:22b3..2732
  and the original ellipse at27a9. Ten targets, each with slow, fast and
  successful settings. It records sounds, explosion requests and visibility.
- `verifyCometMotion()` in sprites.cpp compares native FNV hashes of every
  10ms sample, up to20 seconds. Fields: position, deltas, visibility,
  selected frame, move period and quadrant flags. Both sprite partners
  are included. Synthetic16x16 geometry; generic frame cycling and sound
  playback are not covered by this comparison.
- Native scoped run: `work/fresh-20260913/check_comet.py`, comet.log.
- `probe_comet_render.py`: nine independent compositions from original BMPs
  and masks, compared with native RGB screen hashes in both supported color
  formats. Includes clone overlap, layer order and lower-edge clipping.

## Setup and state

Local0 is direction1..4; local1 is speed index0..15; local2 is target.
P502 uses target10; P503 targets5..9; P504 targets1..4.
Speed display values are0,5010,10080,11520,14400,20880,28080,51840,
64800,75600,102960,120610,140810,162000,181300,200000.
Six decimal digit sprites start at10(P502),14(P503),13(P504).

Correct speed is13 for target10, otherwise11-target. Correct direction
is target for1..4, target-4 for5..8, any direction for9, and1 or4 for10.
Too fast selects escape; all other failures select collision with the sun.
Successful launches use a40ms period, except target10 at10ms.
Target1..4 failures clear their own success flag. Target5..9 failures
do not clear an earlier success flag: preserve this original asymmetry.

P502 success schedules P503 after16667ms and locks input. P503 with all
five flags set plays S2, schedules P504 after16667ms and locks input.
P504 with four flags set stores local7=1 and locks input; its own script
handles the remaining success sequence. The original input lock is DS:6a5.

## Motion and layered handoff

Primary id is20(target10), target+19(target5..9), target+22(target1..4).
Paired id is57-primary(P503) or53-primary(P504). The primary stores a
negative partner id; the partner stores the positive primary id.
Both use center320,160. Radii:200,100 for target10; otherwise25*target,
12*target, adding100,50 for targets1..4. Orbit AD is10.

Approach starts at520,285 (520,310 for target10), dy=-2. At oldY<=160
it switches to ellipse; target10 plays S2. The callback still commits the
proposed point on the switch. Sideways adjustment occurs at y%5==0 or
(y-1)%5==0, except y285: add target-4 for1..4, target-8 for5..9.

Ellipse handoff occurs in its vertical branch BEFORE correcting proposedX.
The partner receives that proposed point, visibility, deltas, quadrants,
move period and frame. Its prior movement timestamp is retained. The
old sprite's deltas are cleared; its timer remains active. The partner
initially has the approach callback, which then switches it to ellipse.
Original SpriteWorld processing order is layer1 then layer2, ordered ids.

Collision: x=520-(310-y)^2/80; x<=340 stops/hides the comet, plays S3,
requests explosion id21/34/31(P502/503/504) at320,160 with10 ticks
per frame. Original frame cycling uses floor(10*1000/60)=166ms and
queues opcode30 after the last frame interval. Escape uses denominator280
and stops/hides at x<=10 or y<=10.

## Integration and remaining checks

Custom8 is registered for the supported scene shapes with animation on.
Prior sprite actions are drained before applying setup. The original
stateful orientation globals persist across scene loads. Both layers are
rendered/processed in order, clone frames are resolved and layer2 frame
cycling is enabled inside the supported-scene guard. All click targets in
these comet scenes are on layer1. Transition and explosion commands use
independent deadlines.

The interaction tests use real assets and actual click handling. They cover
both complete transitions, all success flags, wrong direction, low/high
speed, repeated success, unlocking after failed launches and exits.
Manual audiovisual testing, help/return coverage and exhaustive relaunch
timing remain to be checked. They are not implied by the automatic routes.

The serialized tails contain13/37/32 valid embedded BMPs and must remain
preserved. The original loader ends its regular parsing at9:2c97 before
layer/sprite initialization; the tails' full purpose is not established.
All observed loaded sprites use the standard drawing procedure7:055a;
no special sun-clipping operation has been established. Generic lower-edge
clipping is confirmed at6:06f4-0723: draw rectangle.bottom is temporarily
replaced by min(rectangle.bottom,moveBounds.bottom), then restored.
