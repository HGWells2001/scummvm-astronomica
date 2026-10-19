# P528 save preparation, 18 October 2026

P528 v8 settled saves are implemented and verified; see P528-SAVE-FORMAT.md.
The preparation below records the original implementation questions. probe_p528_save.py reads the original
MEGAFILE.HYP and pictures, writing hashes and twelve exact branch mappings
to evidence/p528-save-original.json. The original file contains nine sprites,
five locals (widths13,4,4,1,1), no startup programs, no mouse rectangles, no
movies and no automatic motion. Sprite7 has twelve frames; sprite8 has one.

Each phase button branch moves sprite7 and selects its frame, invokes
custom18/0, and commits two nonoverlapping original pictures at (87,356)
and (401,369). The phase2 branch explicitly pairs GE_S1 with MO_S10.
Do not replace that original filename with a guessed GE_S10. There are
23 distinct picture resources across the twelve pairs.

The initial last-pair-only hypothesis fails32 of144 two-pair comparisons.
Moon pictures are143x80 or143x81: an80px picture preserves the bottom row of
the most recent81px picture. The four81px pictures (MO_S1, MO_S2, MO_S10,
MO_S11) have four different last-row hashes. Preserve that image identity,
or absence, as well as the current pair. Restore the retained tall moon
first, then the current pair. All1728 three-pair histories reproduce the
same pixels using this bounded history. The base is now decoded from the
original embedded640x320 background and640x146 control panel (placed at
y334), matching the native loader's composition. The48 consecutive natural
phase steps also match. Step1 and step13 both have phase0 but different
background hashes: the former retains the original bottom row, the latter
retains MO_S1's row. This is a reachable history distinction, not merely a
counterexample made by ordering arbitrary phases. The proof covers original
RGB background pixels; full native scene/sprite restoration remains to test.

Local phase11 is also the initial state. On first entry neither picture
has been committed, while after a complete cycle the same phase11 has
GE_S1 and MO_S1. Phase alone cannot distinguish these backgrounds. Track
commit identity or absence explicitly and refuse staged-image saves.

In the native implementation, positionEclipseMoon changes only sprite8's
render coordinates. Its stored x/y center and frame stay intact. Opcode24
similarly changes sprite7's position/frame. The existing native eclipse
verification compares48 original coordinate pairs, both eclipse orders,
wrong and repeated alignments, and solved/unsolved exits. A save contract
must retain the two solved flags and verify the same continuations.

Next: derive settled-state invariants from those native routes; preflight
the required bitmaps; snapshot all script metadata/RNG, clock/count, mutable sprite
state, committed image presence and the retained tall-moon image. Exclude foreground sound, queued actions
and button pulses. Test all48 phase/quadrant boundaries, both solve orders,
already-solved entry, repeated alignment, malformed atomic rejection and
a fresh-process slot. Keep native formats v1-v7 compatible.

This is preparation for the actual engine, not a playable prototype or a
claim that static inventory proves restoration.

Original answer-handler audit, 18 October 2026: probe_p528_answer_states.py
steps the fifty instructions at ASTRO.EXE 4:444c–4523 for all192 combinations
of twelve phases, four quadrants and two boolean solved flags. Every
instruction is covered. It records direct sound calls without executing
them. The first flag is set at (phase0,quadrant1) or (6,3), the second at
(0,3) or (6,1); both flags are monotonic. The result is exactly their
conjunction. Among144 inputs with fewer than two flags set, four answer
edges complete the puzzle. Original serialized commands test that result
after400ms and depart to P526 after4500ms.

Admission inference: a settled P528 save must have result local2=0 and
cannot have both solved flags set, because completion has pending departure
work. Preserve either partial flag independently from the current alignment:
moving the phase/quadrant does not erase it. Evidence: p528-answer-states.json.
This static handler audit does not claim native save/load implementation or
manual runtime observation.

probe_p528_settled_graph.py derives a finite abstraction from the original
rotation/wrap command prefixes and that instruction-derived answer table.
Starting at the serialized phase11/quadrant0, it finds160 reachable states,
480 control edges and six completion departures. There are56 distinct
phase/quadrant/image-history combinations. These counts exclude clocks,
RNG, globals, counters and sprite snapshot details and are not a whole-game
or native-restoration completion measure.

The graph sharpens the image-history preflight: absent pictures occur only
in the four initial phase11/quadrant states, with neither partial flag set.
After commits, phase0 retains either no tall moon on its first visit or
MO_S1 later; phase1 retains MO_S11, phases2–9 retain MO_S10, phase10 retains
MO_S2 and phase11 retains MO_S1. The broader1728 image-composition proof
covers arbitrary three-pair histories; it must not be described as1728
naturally reachable puzzle states. Both proofs have separate scopes.

Implemented v8 payload: twelve header words, nine
frozen27-word sprite records and603 runner words, followed by the current
word-wise FNV checksum. With ASVM/version this is3444 bytes. Preserve an
explicit current pair (or absence), retained tall moon and two reserved
words; preflight the resource-derived history constraints before mutation.
Do not change the already published v7 field meanings. The native test must
compare the full480-row background and screen, not the older456-row hashes.
