# P524 save preparation, 16 October 2026

P524 saves remain unsupported. `probe_p524_save.py` freshly reads the original
scene and records hashes in `evidence/p524-save-original.json`.

The nine displayed pictures all replace (0,0), 640x320. The Moon picture is
an initial stage separate from the eight randomized choices. Unlike P505
and P508, one choice starts an ongoing animation: program3 selects Triton
and starts original sprite32 (zero-based index31) with command19 arguments
`32,200,1,0`. It has eight frames; program1 stops it using command30.

A future save must preserve that sprite's frame selection, auto-frame flag,
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

Required tests include the Moon stage, all eight later pictures, correct and
wrong answers, third-error exit, completion count, duplicate solved entry,
mentor return, animation continuity, inactive/active ambient sound, atomic
malformed-load rejection and fresh-process restoration. Reuse the full
compatibility suite for exploration v1/v2 and puzzle formats v3–v5.
