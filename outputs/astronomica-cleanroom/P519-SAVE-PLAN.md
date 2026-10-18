# P519 save preparation, 15 October 2026

P519 saving is now implemented and verified; see the dated result below.
The original implementation contract comes from a fresh parse of
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


## P519 native saves, 16 October 2026

Native v5 now saves idle P519 selections and partial solutions. It retains all script state and RNG, clock/count, 27 sprite frames and visibility, ten rectangle hover flags and ambient state. Two original image identities reconstruct the full background: the latest large image and optional subsequent small image. Image identities change only when display commits; a new large image clears the small record. Loading skips startup and speech. Foreground audio, queued work, button pulses and staged pictures exclude saving. Ambient music restarts from its beginning.

Tests pass 74 gameplay successor comparisons (all 25 detector/target pairs, both solve orders, repeated target and unsolved exit), plus 30 separate native image-composition round trips. All compare script/RNG, background/screen pixels, sprite frames, hover state and applicable sound IDs/counts. 2584 truncations, 2584 byte corruptions and 18 checksummed invalid states reject without changing live state. Physical slot 4 loads in a fresh process with an identical fingerprint and completes five pairings after the wrong Sun selection. P505/P508 full save tests, previous-build v3/v4 slots, exploration saves, original import, help and full WASAPI suite pass. This remains automated evidence; manual audiovisual playthrough and other puzzle saves are outstanding.
