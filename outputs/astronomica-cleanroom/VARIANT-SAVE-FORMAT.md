# Native custom17 saves, v10

Implemented and verified19 October2026. See evidence/variant-saves-validation.json.

The original sequence spans P506/P531/P532/P533/P534/P535. Its initial
scene is followed by three random scenes without repeats among those three.
The initial scene can recur. Two original process statics retain the round
and six-bit used mask even after a voluntary exit. See variants.json and
variant-save-original.json for original executable/resource observations.

The v10 payload contains ASVM/version, twelve header words,
27 words for each original sprite, the frozen603 runner words, the two
process statics, and an FNV checksum. Payload sizes including magic/version:

| Scene | Sprites | Bytes |
| --- | --- | --- |
| P506/P531 |14|3992|
| P532/P533/P535 |12|3776|
| P534 |18|4424|

Header: place, completed count, clock, previous place, loop ID, loop enabled,
sound epoch, ambient active, four reserved zero words. Sprite records reuse
the v7 layout. Runner words603/604 add round/mask; words0..602 keep the
existing representation. Unknown local values can retain previous-scene
data; they stay inert and must be preserved, with unknown flags and width0.

Restoration rebuilds original callbacks, programs and hit regions without
running entry scripts, repeating the introduction or consuming RNG. It
restores frames, visibility, local partial solutions, process statics,
count, clock and previous place. Background music restarts at its beginning.

Save boundaries require no queued scripts/actions, input block, foreground
audio, button pulse, staged image, movie, automatic movement or animation.
Audio, sprite input and animation must be enabled. The current solved mask
must be partial; the final correct answer queues the next original scene.

The loader preflights size, checksum, destination resource, shape and sprite
fields, known flags, local widths/ranges, and round/mask popcount before
changing state. v1-v9 retain their existing contracts; the old idle-state
API still rejects an active custom17 sequence.

Required validation: every scene at stages0..3; original wrong/repeated
choices and partial solutions; exact pre-action reserialization plus native
successor comparison; first/repeated completion count and original S22;
physical slot9 in a fresh process; exit/reentry with persistent statics;
all truncations and single-byte corruptions for all six layouts; checksummed
semantic errors; flags, pending work, pulse, foreground and Music guards;
previous-build v9 slot and complete compatible native regression suite.

Successor hashes omit newly rebuilt program epochs and departure voice
epochs; exact before-action reserialization still checks saved epochs.
These are automated route checks, not a full manual audiovisual playthrough
or a global completion percentage.

The same checkpoint also corrects a separate save-admission defect in
v6-v9. P509 initializes local14=1 and local16=2. Loading P524/P526/P528/P530
marks these locals unknown and width0 but retains their values, as the
runner has always done. Rejecting nonzero unknown values incorrectly
disabled saving after such an entry. The fix preserves these inert values;
known flags, widths and active-local checks remain enforced. P524's known
mentor-return locals must still be zero. No v6-v9 payload layout changes.
The before-fix P509->P524 rejection is recorded separately; the new suite
requires four natural entries,12 extreme-value round trips and8 metadata
rejections on the current build.
