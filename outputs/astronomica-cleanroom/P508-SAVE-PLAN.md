# P508 native save continuation contract, 14 October 2026

This is implementation preparation, not newly supported saving. The current
save gate must remain unchanged until restoration and continuation pass.
Sources: the current cleanroom engine, the original resource inventory in
evidence/puzzle-save-requirements.json, and the verified P508 routes in
evidence/runtime.log. No excluded earlier implementation is used.

## Existing executable test boundaries

astronomica.cpp tests both original startup/click programs using seed 1.
Startup enqueues three programs; the test drains pending work before input.
Local 0 selects an image from 1 through 18. Choice > 12 selects the upper
correct-answer control (sprite 4 at 223,188); otherwise the lower control
is sprite 6 at 222,253. The wrong-answer route reverses that choice.
Each click schedules pending work, which is drained while sprites animate.
At intermediate settled boundaries, local 4 records correct answers or
local 3 records errors. Eight correct answers reach P388 with global 24
equal to 1 and increment the completed count; three errors reach P388
without that increment, with global 24 equal to 0.

These existing tests establish candidate capture points: after startup,
after correct answers 1 through 7, and after errors 1 through 2. They do
not establish that any such point is currently serializable. Mixed answer
orders and multiple random seeds still need explicit continuation tests.

## Required implementation investigation

- Preserve globals, completed count and logical clock already in native v2.
- Preserve local values together with known/width metadata, not just scores.
- Preserve the full random state. The current uint16 seed API cannot restore
  an arbitrary internal uint32 random state.
- Identify every mutable sprite field and staged/displayed image needed to
  reconstruct the settled screen. The image variant alone is not yet a
  proven complete screen recipe. Do not serialize raw surfaces or pointers.
- Prove quiescence includes pending scripts, blocked input, image staging,
  automatic motion and active foreground audio; an empty script queue alone
  is insufficient evidence. Either serialize ongoing state or reject it.
- Restore without replaying startup, introducing an extra random draw or
  awarding an answer/completion twice. Validate before mutating live state.
- Introduce a versioned format while retaining v1/v2 exploration reads.

## Acceptance evidence before enabling the save gate

For each admitted boundary, compare an uninterrupted run against a fresh
engine loading a physical ScummVM slot, then feed the same remaining clicks.
Compare selected image, locals/globals, visible sprite frames/positions,
audio/action sequence, destination and completed count. Exercise correct,
wrong and mixed orders with multiple seeds. Verify screenshot equivalence
at restoration, no repeated introduction, and save/load/save stability.
Add truncation, corruption, invalid dimensions/indices and incompatible
scene rejection with unchanged live state. Keep pending work and unsupported
puzzles rejected. Run native slot startup tests and the complete regression
before documenting mid-puzzle save support.
