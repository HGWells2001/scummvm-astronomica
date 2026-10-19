# P513 stopped-photon save format, v11

Implemented and verified19 October2026; see evidence/p513-saves-validation.json.

Original resource observations:32 sprites, six locals, four entry programs,
no movies,33 image commits using17 original BMP pictures. Every picture has
the same313x320 opaque footprint at177,22. All1089 ordered overwrites on a
sentinel canvas agree with restoring the last picture. Intermediate half
steps belong to pending knob programs; settled settings1..9 use cube1..9.
See p513-save-original.json and the independent original answer/motion
probes p513-answers.json and p513-motion.json.

The v11 payload has5928 bytes: ASVM/version11,12 header words,32 frozen
27-word sprite records,603 frozen runner words, and word-wise FNV checksum.
Header: scene513, count, clock, previous place, loop ID, enabled, sound
epoch, ambient active, current full cube ID1..9, three reserved zero words.
The full cube ID must match local0. Other versions retain their layouts.

Locals: setting1..9; scenario1..14;14-bit used mask including the current
scenario; last response0/1; errors0..9; correct0..6. Mask popcount equals
errors+correct+1. A full14-bit mask is a valid last-question boundary:
the original success program checks it on the next answer. Seven correct
answers or all fourteen scenarios win; ten errors exit. First success
increments count and global29 directly, with no common S12 success voice.

A snapshot requires no queued work, button pulse, foreground sound, staged
image or active photon. After stopping, the hidden photon retains its
SpriteWorld endpoint, standardMotion flag, and disabled timer fields.
Digit/result sprites can describe an earlier launch after changing the
knob; preserve their records instead of deriving them from current setting.
Original instruction execution also confirms two mid-flight changes:
launch settings7/9 followed by setting8 keep endpoints444/443 respectively,
but show setting8 digits0,5,0. See p513-cross-setting.json. These are modeled
SpriteWorld setter effects from original instructions, not Windows runtime
observations. Native validation must exercise both cases separately.
Unknown local values remain inert and are retained with unknown flags and
width0. Audio, animation and sprite input must be enabled.

The loader preflights the complete payload, original scene layout, bounded
sprite state, checksum and cube picture before rebuilding the scene without
entry programs. It restores RNG, locals, sprite records, picture, count and
clock. Background music restarts. Wrong-footprint image history disables
saving until a scene reload; another full cube cannot erase outside pixels.

Required tests: first/repeated seven-answer success, all14 scenarios,
ten-error exit and voluntary exit; all nine photon trajectories/results,
lower/upper knob limits, exact reserialization and next-action comparison;
slot10 in a fresh process after two correct answers with an old photon
result; all5928 truncations/corruptions,37 checksummed invalid fields and
flags/motion/history/Music guards; previous-build v10 slot and full native
regressions on the same executable. Manual audiovisual playthrough remains
outstanding; supported save scenes are not global project progress.

Also compare all126 question/setting answer successors using fourteen
question fixtures reached by the native routes. Knob changes use ordinary
input and complete the original half-step programs. This matrix covers all
answer branches in those fixtures, not all possible previous input histories.
