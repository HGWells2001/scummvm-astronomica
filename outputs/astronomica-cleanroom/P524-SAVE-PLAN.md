# P524 save preparation, 16 October 2026

P524 v6 saves are implemented; see P524-SAVE-FORMAT.md and dated validation. `probe_p524_save.py` freshly reads the original
scene and records hashes in `evidence/p524-save-original.json`.

The nine displayed pictures all replace (0,0), 640x320. Correction (18 October): the Moon picture follows the eight randomized
choices, after the used mask reaches 255; it is not the initial stage. Unlike P505
and P508, one choice starts an ongoing animation: program3 selects Triton
and starts original sprite32 (zero-based index31) with command19 arguments
`32,200,1,0`. It has eight frames; program1 stops it using command30.

The save must preserve that sprite's frame selection, auto-frame flag,
frame timing parameters/range and last-frame epoch alongside the script
clock. Merely freezing the current frame or restarting its timer changes
the first post-load animation step. Existing `advanceSpriteFrame` advances
at most one frame on an eligible update; tests must cover 199/200ms, long
gaps, frame wrap and uint32 clock wrap. The animation remains active at idle
question boundaries, so a blanket ban on animated sprites is insufficient.

The original scene defines six locals, but startup custom28 mode1 and help
sprite31 custom28 mode0 transfer state through the mentor flow. The current
native handler restores ten local values on help return, including formerly
unknown slots. Do not assume that exactly six locals are known in every
reachable state. Preserve known/width/value metadata and verify saves before
help, after return, during Triton and after leaving Triton.

Required tests include the Moon stage, all eight randomized pictures, correct and
wrong answers, third-error exit, completion count, duplicate solved entry,
mentor return, animation continuity, inactive/active ambient sound, atomic
malformed-load rejection and fresh-process restoration. Reuse the full
compatibility suite for exploration v1/v2 and puzzle formats v3–v5.


## P524 native saves, 18 October 2026

Native v6 saves settled P524 questions with all script/RNG state, previous scene, clock/count, 32 sprite frames/visibility and the continuing Triton animation epoch and parameters. Mentor return preserves the additional known local values. The original committed picture is reconstructed. The Moon follows all eight random choices; the earlier preparation calling it an initial stage was incorrect. Startup and foreground speech are skipped on load; ambient music restarts from the beginning.

Validation: 72 round trips (23 gameplay successors, one post-help identity, 48 animation cases), all eight animation frames at 199/200/2200ms with ordinary and wrapping clocks, two solve routes, third-error exit, voluntary exit, mentor return and fresh-process slot5 completion. 2612 truncations, 2612 byte corruptions and 21 checksummed invalid states reject atomically. Full P505/P508/P519 saves, prior-build v3/v4/v5 slots, exploration v1/v2, import, help and WASAPI suite pass on the same build. These are automated results, not manual audiovisual confirmation.
