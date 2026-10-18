# P524 native save format v6

Implemented 18 October 2026. Applies at settled P524 question boundaries;
queued work, foreground audio, staged images and button pulses exclude saving.
The Triton animation may continue while the script runner is idle.

The payload is 2612 bytes: big-endian `ASVM`, little-endian version 6,
650 little-endian uint32 words, then a wordwise FNV checksum. Start at
2166136261; for each payload word apply `(hash ^ word) * 16777619` modulo
2^32. ScummVM metadata follows outside this payload.

| Word | Meaning |
| --- | --- |
| 0 | Scene 524 |
| 1 | Completed puzzle count |
| 2 | Script clock |
| 3 | Previous scene, or 0xffffffff |
| 4 | Visibility mask for 32 sprites |
| 5–8 | Loop sound, loop enabled, last sound epoch, active ambient flag |
| 9–14 | Sprite31 auto-frame flag, last-frame epoch, three frame parameters, first motion parameter |
| 15–46 | Selected frame of each sprite |
| 47–649 | ScriptRunner idle snapshot: all global/local values, widths and known flags, RNG state, program epoch and last predicate |

The six original local widths are 8,8,1,3,1,4. Mentor return defines four
additional zero-valued locals with zero width; their known flags are retained.
The selected scenario identifies one original 640x320 picture at (0,0).
Scenarios 1–8 are randomized; scenario 9 is the Moon, displayed after all
eight mask bits are used. This corrects the 16 October preparatory wording
that called the Moon an initial stage. Original program2 offsets 783055,
783087 and 783107 directly encode mask255, scenario9 and VIEWMOON.

Sprite31 is the only running animation: eight frames at 200ms on Triton.
The last-frame epoch is saved even after the sprite stops, because command19
does not reset it. Immutable frame range and geometry are reconstructed from
the original scene. Command30 leaves the previous frame selected, disables
animation and sets both frame/motion periods to -1. Its remaining frame
parameters may retain the preceding animation's values.

Loading validates payload and image before restoring scene 524, skips startup,
imports the runner and timer, restores sprites, and commits the original image.
The mentor support flag follows the saved previous scene; subsequent mentor
visits use the normal custom28 transfer. Ambient audio restarts from its
beginning; exact audio sample position is not saved.

Validation: `check_p524_saves.py` performs 23 gameplay successor comparisons,
one extra post-help identity round trip and 48 animation round trips (all
eight frames, ordinary/wrapping epochs, 199/200/2200ms). It checks two complete
solve routes, already-solved counting, three errors, voluntary exit, help
during Triton and subsequent questions. All 2612 truncations, 2612 single-byte
corruptions and 21 checksummed invalid states must reject without changing
live state. Slot5 is test-generated and loaded in a fresh process, followed
by mentor return and completion. Foreground handles are stopped by the test
only after proving they exclude saving; this is not manual audio validation.

Versions 1–5 retain their original readers. Compatibility and full-suite
results are recorded separately by `finish_p524_saves.py` after they pass.
