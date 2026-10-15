# P505 native save v4

Implemented and verified 15 October 2026. This describes the engine payload;
ScummVM appends its own extended slot metadata and thumbnail. Game media is
not embedded. P508 continues writing v3; exploration continues writing v2,
and the inactive v1 exploration format remains readable.

The payload is 2472 bytes. The first four bytes are ASCII `ASVM`, followed by
the little-endian uint32 version 4. Next come 615 little-endian uint32 words
and a final uint32 checksum. The checksum starts at 2166136261, then for each
of those 615 words performs `(hash XOR word) * 16777619`, wrapping to 32 bits.
Magic and version are not included in that checksum.

| Word index | Content |
| --- | --- |
| 0 | Place, exactly 505 |
| 1 | Completed-puzzle count |
| 2 | Script clock in milliseconds |
| 3 | Previous place; 0xffffffff represents -1 |
| 4 | Visibility bitmask for 18 sprites |
| 5 | Frame-zero bitmask; unset means selected frame -1 |
| 6 | Ambient sound, 0 or 0xffffffff (-1) |
| 7 | Ambient loop enabled, boolean |
| 8 | Last sound epoch |
| 9 | Ambient handle active, boolean |
| 10–309 | 100 global triples: value, width, known |
| 310–609 | 100 local triples: value, width, known |
| 610 | Full 32-bit random generator state |
| 611 | Program-loaded epoch |
| 612 | Last conditional branch result, boolean |
| 613 | Entered sprite-hover bits; permitted mask 0x55 |
| 614 | Entered rectangle-hover bits; permitted mask 0x3ff |

The four known locals have widths 8, 8, 4 and 1. They hold the current
question (1–8), used-question bitmask, error count (0–2), and branch flag 1.
The current question must be present in the mask; errors must be fewer than
the number of selected questions. Other locals must be unknown. All globals
must be known. Signed values are stored in their uint32 representation.

Saving requires idle scripts, the displayed original question, unchanged
sprite geometry/control/frame ranges, completed button pulses, no motion,
no staged picture, no movie and no active foreground sound. P505 hover
handlers must be configured. A save is rejected before the first question
or while an answer is executing. This is not an arbitrary execution snapshot.

Loading checks the payload, original scene and selected bitmap before
rebuilding P505 without startup scripts or introduction. It restores the
question at (254,362), script/RNG state, sprites and hover flags. It must not
consume a random draw or replay a hover-enter event. If ambient audio was
active, it restarts from the beginning; sample-accurate music seeking is not
part of this format.

Regression drivers: `check_p505_saves.py` and `check_question_regressions.py`.
Evidence: `p505-saves-validation.json`, `p505-save-proof.json` and native logs.
Coverage is 38 boundaries and successor comparisons, 38 unchanged-hover
checks, 2472 truncations, 2472 one-byte corruptions, 16 checksummed invalid
states, and fresh-process slot 3 continuation. This is automated evidence,
not a claim of a complete manual audiovisual playthrough.
