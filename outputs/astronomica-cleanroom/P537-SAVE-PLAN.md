# P537 rocket saves: original requirements

19 October2026. New save support is not implemented. This inventory prepares later work while the frozen P517 regression runs.

probe_p537_save.py records the original resource's48 sprites, one local selector0..15 and one startup program. Cloned indicators inherit source frame/visibility state. No picture commits, movies, drag/hover or initial automatic motion occur. Original custom14 dispatch/callback evidence remains separately documented by probe_rocket.py and evidence/p537-rocket.json; this new resource inventory is not an additional Windows execution trace.

Launch control33 starts custom14 inside a click-blocked script with delayed commands after the motion begins. The continuation selects failure/success speech, original custom25 and departure to P321. Coordinates and a stopped/moving flag cannot reconstruct that queued continuation. A settled-only format must reject it; actual mid-launch saving would additionally require a separately verified representation of pending scripts and click blocking. Do not present a selector-only save as a mid-flight save.

The real engine also has RocketMotion kind/delta/since outside the sprite records. startRocket intentionally retains the prior movement timestamp, so even stopped history may affect a subsequent launch. Any save proposal must retain or explicitly constrain that state, alongside full sprite records, selector/RNG, clock/count, previous scene, ambient state and dormant cross-puzzle state. No payload version or byte count is assigned before the scope and native boundaries are established.

Next verification should observe actual controls at initial, selected, failed-return and launch boundaries; establish save eligibility independently of the new serializer; compare all15 settings, clamping, queued-launch rejection, stopped history, next movement timing, failure/success counts and fresh-process continuation. Existing rocket motion checks and static resource observations do not prove a new save implementation or complete manual playthrough.


## Original callback oracle,20 October2026

probe_p537_motion.py executes the actual three callback instruction ranges over96 explicit fixtures,14592 steps. The combined semantic word hash is292dc3fd. It records rendered rectangles, frame indices, selected timer fields, success-call count and global36; sample rows and complete-row digests are retained. Callback kind and local selector are deliberately independent inputs, so this is not a claim of96 UI-reachable routes. SpriteWorld setters and the success helper are modeled; actual animation scheduling, duplicate internal timer fields/flags and sound duration are outside the model.

Original FrameTime(-1) calls for all21 digits reveal an inactive-timer difference in finishRocketDigits: the engine stopped animation but retained period0. A real-engine correction to period-1 and a native96-fixture comparison are staged with construction v13; no native pass is claimed until their runtime log is checked. RocketMotion.kind/delta/since is a functional adapter for the original move callback/timer, not a byte-identical SpriteWorld structure.
