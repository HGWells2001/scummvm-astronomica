# P526 save preparation, 18 October 2026

Saving P526 is not implemented. The original-resource inventory is produced
by `probe_p526_save.py` from D:/astro, with hashes recorded in
`evidence/p526-save-original.json`. This does not reuse excluded attempts.

Observed in the original scene: 23 sprites, six answer rectangles, seven
locals with widths 6,9,6,6,1,4,1, two startup programs and no movies. Three
sprites animate on entry: index17 has twelve frames at 100ms, indices19/21
have twelve at 30ms. Six committed pictures S1–S6 replace the same rectangle
at (90,361). The experiment button invokes custom13 for original sprite IDs
20,22,23; the last has an offset of (13,-50). Answer rectangles have hover
scripts which must not replay spuriously after a restore.

Observed in the current native implementation: `advanceOrbit` changes render
positions separately from center x/y, front/back visibility, orbital radii,
direction deltas and quadrant flags. At the stop position it disables the
phase sprite's animation and some motion flags, but does not clear all
runtime motion state. The other animated sprites continue updating. Therefore
an idle script runner alone is insufficient to identify a frozen state.
The selected phase frame is also an input to answer acceptance; restoring
only the visible background would alter puzzle behavior.

Proposed first scope: settled selection and answer boundaries, excluding
active orbital travel and queued speech/actions. Even this scope needs all
three animation epochs, moved render coordinates, retained orbital data,
all local metadata/RNG and hover state. Track whether an experiment picture
has ever been committed instead of inferring that from a future scenario.
Do not assume all sprite centers equal their render coordinates after stop.

Before enabling saves, derive reachable invariant ranges from the existing
native six-scenario routes, then compare complete continuations with and
without save/load: launch, stop, correct/wrong answer, next experiment,
repeat completion, fourth-error exit and voluntary exit. Include every
accepted phase/answer combination, timer wrap, hidden sprite animation,
hover exit/re-entry, foreground exclusions, atomic corrupt-payload rejection
and fresh-process slot loading. Existing v1–v6 must continue to work.

Unknown until those tests exist: whether settled-only snapshots can omit any
retained motion fields safely. Do not generalize P524's single animated
sprite format to P526 by changing just the sprite count.
