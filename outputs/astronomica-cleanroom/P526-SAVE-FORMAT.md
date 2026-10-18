# P526 native save format v7

Implemented and verified 18 October 2026; p526-saves-validation.json is PASS.

Scope: settled P526 entry, stopped experiment, and answered boundaries.
Queued work, orbital travel, staged bitmaps, foreground audio and button
pulses exclude saving. Idle animations continue, including hidden sprites.
Animation and sprite input must be enabled to use this format.

The payload is 4956 bytes: big-endian ASVM, little-endian version7, 1236
little-endian uint32 words and a checksum. Wordwise FNV starts at 2166136261,
then applies `(hash ^ word) * 16777619` modulo 2^32. ScummVM metadata follows.

| Words | Meaning |
| --- | --- |
| 0–3 | Scene526, completed count, script clock, previous scene |
| 4–7 | Loop sound, loop enabled, last sound epoch, active ambient flag |
| 8 | Committed image identity: 0 absent, 1–6 original S1–S6 |
| 9 | Reserved sprite hover mask, must be zero |
| 10 | Six answer-rectangle hover entered bits |
| 11 | Reserved, must be zero |
| 12–632 | 23 sprite records, 27 words each |
| 633–1235 | Full 603-word idle ScriptRunner snapshot |

Each sprite record contains, in order: visibility, selected frame, center
x/y, render x/y, auto-frame, auto-move, frame epoch, move epoch, standard
motion flag, delta x/y, orbit motion flag, quadrant x/y flags, frame first/last,
click enabled, three frame parameters and five movement parameters. Signed
values use their uint32 bit pattern. Immutable geometry/control data is
reconstructed from the original resource and checked before restoration.
Planet, drag and unsupported motion states are excluded.

The seven local widths are 6,9,6,6,1,4,1. Their values describe used scenarios,
the constant selector, scenario, selected answer, acceptance, errors and
active experiment. A mask of63 can be a valid stopped sixth question; it
must not be rejected merely because the next answer will schedule completion.
The committed image is independent of whether a new scenario has been chosen.
An absent image reconstructs the original untouched background.

Original pictures are all98x94 at (90,361). All payload, resource geometry,
frame counts, sprite ranges and optional bitmap checks occur before changing
the live scene. Loading skips startup, reconstructs programs/handlers, imports
all local/global metadata and RNG, and restores hover and sprite state. Ambient
music restarts at its beginning; no audio sample cursor is serialized.

The original-resource inventory and native audit are separate evidence:
probe_p526_save.py hashes the original files; check_p526_boundaries.py observes
33 actual boundaries across six native scenarios with real audio. The audit
records that stopped sprites retain orbital center/radii/directions while
indices19/21 continue animating. Index17's stopped phase controls acceptance.

Tests: 33 gameplay successor comparisons, five additional identity round trips,
216 animation comparisons (three sprites, twelve frames, ordinary/wrapping
epochs, before/exact/long-gap updates), and432 synthetic phase/answer cases.
The latter vary twelve phase frames and six answers on six route-derived
snapshots using the original already-solved branch. First completion/counting
and victory audio are checked by the separate route tests. The matrix does
not claim all phases occur naturally at each stop. The
existing original x86 answer comparison remains the acceptance oracle.
All4956 truncations,4956 byte corruptions and25 checksummed invalid states must
reject without altering the live state. Slot6 is test-generated, restored in
a new process and completed normally. Foreground handles are stopped only
after testing the save exclusion, so this remains automated audio evidence.

Restore equality compares every serialized word except unavoidable elapsed
wall time in the current script clock. Successor equality compares all script
values/RNG, sprite fields/epochs, hover, pixels, previous scene, completion
count and sound IDs/counts. The successor fingerprint uses the600 metadata
words and RNG, excluding the program epoch and last predicate; both excluded
words are still preserved and checked by exact re-serialization before the
next action. In particular, a new scene's program epoch follows real playback
time after synchronous audio, and two playbacks can differ by milliseconds.

Compatibility v1–v6 and the full WASAPI suite must pass on the final executable
before finish_p526_saves.py records a publishable result.
