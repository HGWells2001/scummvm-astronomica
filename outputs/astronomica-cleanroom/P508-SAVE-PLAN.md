# P508 native save continuation contract, 14 October 2026

The plan below is retained as the pre-implementation contract. P508 settled
question saving is now implemented and verified; see the dated result below.
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


## P508 settled question saves, 15 October 2026

Native version3 now saves P508 between questions, including six locals, all global/local values and their known/width metadata, full32-bit RNG, program epoch, branch state, previous place, completion count, sprite visibility/frame selection and ambient audio state. Pending actions, foreground speech, staged images, moving sprites and button pulses are excluded. Original data confirms18 opaque508x108 pictures at(67,354); the selected picture reconstructs the background without storing media. Startup scripts and introduction are skipped on load. Ambient music restarts at the beginning, not at the exact saved sample.

Three seeds and correct/wrong/mixed routes cover63 saved boundaries and 291 resumed answer steps, comparing screen pixels, script data, RNG, sound IDs/counts, destination and completion count with uninterrupted runs. Save/load/save data is stable except for the advancing clock. 2464 truncations,2464 byte corruptions and14 invalid checksummed states are rejected without changing the live state. Physical slot2 loads in a fresh process with the identical state/screen fingerprint and completes the seven remaining correct answers. Music/foreground guards and slot metadata pass. Exploration v1/v2 regressions, help and full WASAPI suite pass on the matching executable. Other puzzle saves remain unsupported.
