# P519 save preparation, 15 October 2026

P519 saving is not implemented. This contract comes from a fresh parse of
`D:/astro/PLACES/P519/MEGAFILE.HYP` and its ten original bitmaps, recorded by
`probe_p519_save.py` in `evidence/p519-save-original.json`.

The scene has eight locals, 27 sprites, ten rectangles and no automatic
sprite movement, automatic frames, dragging or movies. Serialized mutations
are visibility and explicit frame selection (including frame 2). There are
15 background-load commands, each immediately followed by display opcode49.

Five images occupy (258,356), 143x108; five occupy (282,358), 99x99. The small
rectangle is entirely inside the large one. Every new large image erases all
previous image contributions. Every small image erases all previous small
ones but leaves the surrounding large image intact. A bounded background
record therefore needs the latest large image and the latest subsequent
small image, or none. The initial large image is BLACK_B.

All 1000 three-image sequences from the ten original RGB-decoded bitmaps
produce identical pixels when reconstructed from the bounded two-image
record. This confirms the geometry/composition contract; these synthetic
image sequences do not establish reachable gameplay states or native saves.

Implementation must track these identities at successful display commit,
not when an image is merely staged. A single `_displayedImageName` is
insufficient. Loading should validate both originals and their dimensions
before changing live state, then restore large followed by optional small.
Do not store original media in the save or export repository.

Preserve all script locals/globals and metadata, RNG/clock, completion and
previous-place state, sprite visibility/frame selection and hover-enter
flags. Exclude transient queued actions, speech, flash and button pulses.
Do not reuse the P505/P508 frame-0-only restriction: P519 retains solved
indicators and visual results in higher frames.

Required native tests: save at initial state, after each detector selection,
after correct and incorrect target selections, after repeated targets and
after several solved pairs. Cover both existing solve orders, unsolved
exit, all large/small image combinations reachable through original scripts,
hover continuity and final completion count. Compare resumed screens,
script/RNG state, sound IDs and destinations against uninterrupted runs.
Check corrupted payload rejection, save/load/save stability and fresh-process
slot restoration. Static geometry alone is not evidence of save support.
