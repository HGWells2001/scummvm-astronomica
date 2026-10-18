# P519 native save v5

The engine payload is 2584 bytes, before ScummVM's extended metadata and
thumbnail. It starts with ASCII `ASVM`, little-endian uint32 version 5,
643 uint32 words, then a uint32 checksum. The checksum starts at 2166136261;
for each word it computes `(hash XOR word) * 16777619` modulo 2^32. Magic
and version are excluded. Values use little endian; -1 is 0xffffffff.

| Word | Content |
| --- | --- |
| 0 | Place, exactly 519 |
| 1 | Completed-puzzle count |
| 2 | Script clock |
| 3 | Previous place |
| 4 | Visibility mask, 27 sprites |
| 5 | Ambient sound, 0 or -1 |
| 6 | Ambient enabled, boolean |
| 7 | Last sound epoch |
| 8 | Ambient active, boolean |
| 9 | Large image ID, 1–5 |
| 10 | Small image ID, 0–5; 0 means absent |
| 11 | Reserved sprite-hover mask, must be 0 |
| 12 | Entered rectangle-hover mask, ten bits |
| 13–39 | Selected frame for each sprite, including -1 and retained frame 2 |
| 40–339 | 100 global triples: value, width, known |
| 340–639 | 100 local triples: value, width, known |
| 640 | Full random generator state |
| 641 | Program-loaded epoch |
| 642 | Last conditional result, boolean |

Large IDs in order: BLACK_B, ASUPER, M82VIEW, ASUN, APULSAR. All are 143x108
at (258,356). Small IDs: JUPNO, M82NO, LOSUN, MSUN, LOPULSAR. All are 99x99
at (282,358). Both footprints and original hashes are recorded separately.
A committed large image clears the small ID. Staging does not change either
ID. Loading decodes both images before replacing the scene, then draws the
large followed by the optional small image. No media is embedded in the save.

Eight locals are known, with widths 5,5,1,1,1,1,1,1. The first two values
are bounded by 5, the remaining values by 1; local7 must be 1. All five solved
flags together are rejected because completion is a pending transition.
Other locals must be unknown and all globals known. Frames are checked
against each original sprite's frame count. The first four button sprites
must have finished their pulse (selected frame -1 or 0).

Admission requires idle scripts, known committed images, no staged image or
movie, no foreground sound, unchanged sprite geometry/ranges/control state,
static sprites and configured hover targets. Loading skips startup scripts
and the introduction, preserves RNG and hover-enter flags, and restarts
active ambient music from its beginning. Exact audio sample position and
arbitrary in-flight actions are outside the format.

Native tests cover 74 gameplay boundaries and successors plus 30 separate
resource-composition round trips, malformed payloads and physical slot 4
loaded in a fresh process. `finish_p519_saves.py` records PASS only after
those tests and the compatibility/full regressions pass on the matching
build. P505 v4, P508 v3 and exploration v1/v2 retain their existing layouts.
