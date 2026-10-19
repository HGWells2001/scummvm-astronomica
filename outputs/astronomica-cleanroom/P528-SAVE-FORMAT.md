# P528 native save v8

Implemented and verified 18 October 2026; evidence/p528-saves-validation.json is PASS.

The payload is3444 bytes: ASVM, a little-endian version8,858 words and a
word-wise FNV checksum. ScummVM adds its standard save metadata separately.
The checksum starts at2166136261 and folds each word with
`hash = (hash ^ word) * 16777619` modulo2^32. Versions1–7 keep their meanings.

The first twelve words are:

| Index | Value |
| --- | --- |
|0|Place528|
|1|Completion count|
|2|Script clock|
|3|Previous place or0xffffffff|
|4|Ambient sound ID:0 or0xffffffff|
|5|Loop enabled, boolean|
|6|Last foreground sound epoch|
|7|Ambient handle active, boolean|
|8|Last committed Moon pair ID:0 absent, otherwise1–12|
|9|Retained81-row Moon ID:0 absent, otherwise1/2/10/11|
|10–11|Reserved, must be zero|

Words12–254 contain nine frozen27-word sprite records, with the exact
layout used by v7 (see P526-SAVE-FORMAT.md). Words255–857 contain all603
idle-runner words, including global/local known flags and widths, RNG,
program epoch and predicate. The position and frame of sprite7 derive from
the original phase command; sprite8 keeps its stored center and uses the
original phase/quadrant render position. Other sprite state must match the
original scene, excluding inactive frame/movement epochs.

Local0 is phase0–11, local1 quadrant0–3, local2 must be zero, and locals3/4
are partial-eclipse flags. Both flags cannot be set in an admitted idle
state: original completion enqueues departure. Exactly five locals are
known with widths13/4/4/1/1; all100 globals are known.

The pair ID is12 minus phase. For pair10, the Earth image is GE_S1, as in
the original branch; other pairs use GE_Sn and MO_Sn. Pair absence is
allowed only at initial phase11, with neither partial flag set. Retained
tall Moon history follows the original forward-only phase cycle:
phase0 has none on the first visit or MO_S1 later; phase1 has MO_S11,
phases2–9 MO_S10, phase10 MO_S2, phase11 MO_S1. These rules are supported by
the160-state resource-derived graph, separate from native round-trip tests.

Before changing live state, loading verifies checksum, all header/state
constraints, original scene geometry, all sprite words and required image
decoding/dimensions. It restores the retained tall Moon first, then the
current Earth/Moon pair. This preserves the bottom row left behind by a
shorter Moon picture. It rebuilds original handlers without entry scripts
or introduction audio, imports runner state, restores clock/count and
restarts any active ambient loop from its beginning on the Music channel.

Saving excludes queued or blocked work, button pulses, staged images,
movies and foreground audio. Original audio targets, animation and sprite
input must be enabled. The ordinary ScummVM Music mute/volume controls do
not disable those resource targets and remain usable. No sample cursor is
retained; arbitrary transient states and other puzzle saves remain outside
this format.

Verification plan:160 reachable abstract states,640 continuations including
the phase/quadrant/answer controls and unsolved exits, full480-row pixels,
all payload truncations and single-byte damage, checksummed invalid fields,
configuration/pending-image/foreground guards, a physical slot7 and a fresh
process completing a partial solution with the retained old Moon row.
The matrix uses the already-completed global44 branch; original first
completion/count/audio is tested separately. This does not replace a full
manual audiovisual playthrough.
