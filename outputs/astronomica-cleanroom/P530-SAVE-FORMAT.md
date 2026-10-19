# P530 native save v9

Implemented and verified19 October2026; evidence/p530-saves-validation.json is PASS.

The payload is5604 bytes: ASVM, little-endian version9,1398 words and the
existing word-wise FNV checksum (seed2166136261, xor each word and multiply
by16777619 modulo2^32). ScummVM metadata follows the payload. Earlier
versions1–8 retain their exact meanings.

The twelve header words contain place530, completion count, clock,
previous place, loop sound ID, loop-enabled flag, last sound epoch, active
ambient flag, committed picture ID0–25, and three zero reserved words.
Picture0 means absence. IDs1–25 follow kP530Images, in the original resource
branch order recorded by p530-save-original.json. Each picture is172x172
at(460,10); the last identity alone suffices to reconstruct its footprint.
It can remain from a previous round after the selection locals reset.

Words12–794 hold29 frozen27-word sprite records, using the v7 layout.
Words795–1397 hold all603 idle-runner words, including globals/locals,
known flags, widths, RNG, program epoch and predicate. Sprite visibility
can change only for original mutation targets. Stored and render positions
are original except the six moving indicators, which may retain their
settled endpoint(466,115), including while hidden. Transient scripted
movement, button pulses and other changed immutable fields are excluded.

Exactly14 locals are known, with original widths1/1/1/1/1/1/1/1/1/5/5/5/1/5.
Their booleans remain bounded; scenario local9 is1–5, detector local10 is0–5,
mask local11 is five bits and round local13 is1–3. Mask population equals
the round and contains the current scenario. The upper/lower component
flags match the original scenario branch. Accepted answers at round3 have
pending completion and cannot be admitted. All100 globals are retained.

The loader preflights checksum, header/state constraints, original scene,
all sprite records and picture dimensions before changing live state. It
rebuilds handlers without entry scripts, restores all runner/RNG and sprite
state, clock/count and the last picture, and restarts an active ambient
loop from its beginning on Music. Saving excludes foreground audio,
queued/blocked work, staged or unrecognized image history, movies and
disabled/missing original audio, animation or sprite input. The three
original mouse rectangles and all sprites have no hover programs; no
entered-hover state can occur in an admitted save.

Verification covers randomized three-round routes, five scenarios in every
round, all six component placement permutations, every detector picture, wrong and repeated
answers, partial placement, prior-round pictures, later RNG continuation,
unsolved exit, malformed atomic rejection and fresh-process slot8.
P530's original completion sets global46 and conditionally plays S12 but
does not increment the completion counter. The matrix tests this exception
both on first completion and on already-completed routes.

This is automated state/pixel/audio verification, not a complete manual
audiovisual playthrough. No global project completion percentage follows
from the supported save-scene count.
