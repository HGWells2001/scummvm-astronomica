## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

## Verified settled save support,21 October2026

Version14 is implemented and verified; see P537-SAVE-FORMAT.md and evidence/rocket-saves-validation.json. The following sections retain the original investigation history.

# P537 rocket saves: original requirements

Updated20 October2026. P537 save support is not implemented. Construction v13 and the P537 callback/readout correction are verified and published; this inventory prepares subsequent settled-boundary save work.

probe_p537_save.py records the original resource's48 sprites, one local selector0..15 and one startup program. Cloned indicators inherit source frame/visibility state. No picture commits, movies, drag/hover or initial automatic motion occur. Original custom14 dispatch/callback evidence remains separately documented by probe_rocket.py and evidence/p537-rocket.json; this new resource inventory is not an additional Windows execution trace.

Launch control33 starts custom14 inside a click-blocked script with delayed commands after the motion begins. The continuation selects failure/success speech, original custom25 and departure to P321. Coordinates and a stopped/moving flag cannot reconstruct that queued continuation. A settled-only format must reject it; actual mid-launch saving would additionally require a separately verified representation of pending scripts and click blocking. Do not present a selector-only save as a mid-flight save.

The real engine also has RocketMotion kind/delta/since outside the sprite records. startRocket intentionally retains the prior movement timestamp, so even stopped history may affect a subsequent launch. Any save proposal must retain or explicitly constrain that state, alongside full sprite records, selector/RNG, clock/count, previous scene, ambient state and dormant cross-puzzle state. No payload version or byte count is assigned before the scope and native boundaries are established.

Next verification should observe actual controls at initial, selected, failed-return and launch boundaries; establish save eligibility independently of the new serializer; compare all16 selector values (0..15), clamping, queued-launch rejection, stopped history, next movement timing, failure/success counts and fresh-process continuation. Existing rocket motion checks and static resource observations do not prove a new save implementation or complete manual playthrough.


## Original callback oracle,20 October2026

probe_p537_motion.py executes the actual three callback instruction ranges over96 explicit fixtures,14592 steps. The combined semantic word hash is292dc3fd. It records rendered rectangles, frame indices, selected timer fields, success-call count and global36; sample rows and complete-row digests are retained. Callback kind and local selector are deliberately independent inputs, so this is not a claim of96 UI-reachable routes. SpriteWorld setters and the success helper are modeled; actual animation scheduling, duplicate internal timer fields/flags and sound duration are outside the model.

Original FrameTime(-1) calls for all21 digits reveal an inactive-timer difference in finishRocketDigits: the engine stopped animation but retained period0. The real-engine correction to period-1 and the original final readout IDs passes the native96-fixture comparison and exact original-image pixel checks on the same verified construction v13 build. RocketMotion.kind/delta/since is a functional adapter for the original move callback/timer, not a byte-identical SpriteWorld structure.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Narrow boundary audit,20 October2026

Direct re-read of D:/astro/PLACES/P537/MEGAFILE.HYP confirms the selector controls are one-based sprites5/6: their click programs begin by blocking clicks, adjust local0 by-1/+1, clamp at0/15, refresh the indicator, then unblock with a200ms delayed command. Their first commands start at resource offsets323319 and326731. A save during that pulse must remain ineligible even when the selector already has its final value.

Launch is sprite33, starting at offset354555. Its custom14 command is at354659; delayed conditional continuation begins at354699. Motion stopping alone therefore cannot establish an eligible boundary. Candidate positive boundaries for a future independent native audit are initial settled entry, each settled selector value, and completed failure-return after all queued commands and foreground sound finish. Successful launches depart to P321 and should use that scene's eligibility. The existing verified native rocket suite samples launch settings0,1,10,11,12,13,15; it does not prove a new serializer or every save-boundary case. Preserve stopped RocketMotion.delta/since and prior readout independently of the current selector, and explicitly exercise selector changes after failure before proposing a format.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.


## Native callback correction verified,20 October2026

The production engine matches all96 controlled original callback fixtures and14592 steps (292dc3fd), including the exact final readout IDs and21 stopped frame periods. Full real-audio regression passes on the same build. See evidence/p537-motion-validation.json. This fixes rocket behavior; P537 save support is still not implemented.
