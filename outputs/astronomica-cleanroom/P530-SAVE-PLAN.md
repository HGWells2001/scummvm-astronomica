# P530 save preparation, 18 October 2026

P530 native saves are not implemented. The original resource inventory
records14 locals,29 sprites and11 startup programs. There are581 commands,
including25 external background image commits, and no movies, automatic
animation or movement. Only the first four sprites have two frames; the
remaining25 have one. The raw mutation operands and source offsets are in
evidence/p530-save-original.json.

The random selection uses opcode39 with mask local11, destination local9
and width5. Save the complete runner metadata and RNG, not just the current
scenario. Original startup script0 checks round local13 against3 and
departs to P228 on completion. The separate original executable proof
p530-success.json establishes its exceptional success rule: global46 and
S12 voice, with no puzzle-counter increment.

Next: audit settled native boundaries for partial component placement,
detector selection and between rounds. Retain all14 local values/known
flags/widths, globals, RNG, clock/count, mutable sprite visibility/frames
and mouse rectangle hover. Exclude pending work and foreground audio.
All25 pictures are172x172 at(460,10). Across625 ordered image pairs, opaque
RGB composition on a sentinel canvas confirms that the last picture alone
reconstructs that rectangle. Retain its identity or absence explicitly;
do not infer it from a new round's reset selection. Native scene restoration
is not covered by this image-only proof.
Compare three randomized rounds, both component orders, wrong/repeated
answers, already-completed behavior, unsolved exit, malformed atomic
rejection and a fresh-process physical slot. Preserve formats1–8.

This inventory is static original-resource evidence; it does not demonstrate
native P530 save restoration or add a global completion percentage.
