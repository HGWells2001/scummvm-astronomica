# P516 version22 saves

Status: verified25October2026; complete same-build native WASAPI suite PASS within the explicit restricted scope.

25October2026. Fresh six-source candidate from published P511v21/main1e27c45d9b7f5f3ab780837931cc7a6b07639fac3b95d6b58d6e2bfdcce2e306; BASE23.json/BASE.json/ORIGIN.json bind provenance. Original MEGAFILE.HYP563403bytes SHA256fae86ac8d36038046a9d387f8fbc28d822d2cdcacc2cdb0ab4d941d55b58ced6. Frozen55record audit and separate40record/eightphase flight audit remain unchanged. Only post13September2026 cleanroom and original assets were used.

Supported scope is quiet ordinary P516, local2=0, all8original moon orbits configured and active, and projectile13hidden/stopped in original prelaunch, zero-speed NOOP, or true failed-return history. Reject queued work/actions/click locks, foreground voice, hover entry, movie/surface, pending/displayed image, active projectile, sticky-hit local2=1, stopped moons and explosion history. Stopped nonzero deltas retained by an opcode30abort of an unproved ordinary active-flight history are explicitly outside this contract; they are rejected, never normalized. The bounded flight audit did not observe ordinary active flight and does not prove it impossible.

Payload6944bytes: ASVM big-endian magic and little-endian version22(8bytes),11header words,37x27sprite words,605runner words,118extra words and checksum. All data words are little-endian. Checksum starts2166136261 and folds `(hash ^ word)*16777619` over header/sprites/runner/extra; it is an integrity check, not authentication. Slot21 description: `P516 continuation regression`.

Header: place516,count,logical clock,previousPlace(-1or0..537),loopSound(-1or0),loopEnabled1,lastSoundAt,ambientActive0/1,comet.frame1..12,comet.previousFrame0..12,imageReserved0. Active ambience requires direct sound0. Entry with ordinary audio enables S0; manual startup can retain loop-1. Preserve the original greater-than5000ms restart rule and Music volume; active foreground sound cannot be saved.

27words per sprite: visible/selected/storedXY/renderXY/autoFrame/autoMove/frameSince/moveSince/standardMotion/dxdy/orbitMotion/orbitSides/frameFirst/Last/clickEnabled/frameData3/moveData5. Clones inherit only their frame assets. Private planetMotion/planetPeriod and orbitMotion are guarded at original0/-1/false. All original static fields remain bound to parsed HYP. No snapping, common frame/epoch inference, startup replay or configureJupiter(mode0) runs during restore.

605runner words:100global+100local value/width/known triples; RNG600,programLoadedAt601,lastTrue602,dormant variantRound603/mask604. Original local0direction1..4,width8;local1speed0..15,width16;local2flag0,width0butKNOWNtrue. Unknown local3..99values are preserved while metadata remains unknown. Globals retain the reviewed historical width0/6 for indices0..2 and0 elsewhere, with known bits1. Live original programs/handlers/targets are rebuilt by loadPlace and state is imported on that configured runner; a prepared runner is used only for preflight validation.

Extra118words: kind[50],partner[50],sound,explosion,widths[8],heights[8]. kind4and exact signed partner formula are required for indices13..20, zero elsewhere; sound-1/explosion0. Cache widths50,39,110,60,60,110,39,50 and heights50,100,40,60,60,40,100,50 are validated against immutable decoded original geometry before mutation. Global comet frame/previous remain independent in the header.

Orbit records preserve independent selected frame, visibility, delta, sides and frame/move epochs. Pair handoff copies selected frame and motion but does not copy either epoch. One member of each original pair remains visible; hidden members retain their history. The four auto-frame sprites keep80ms behavior; configured motion period is10ms. Render bounds derive from original ellipse parameters and handoff delta, not sampled extrema. The native harness checks eligibility at every10ms tick across2000ticks, as well as independent10/80ms epochs and wraparound.

Projectile13storedXY remains320,300. A failed callback hides/stops it, zeroes delta, sets both periods-1 and still commits the proposed next rectangle. Historical renderedXY/epoch remain independent of current selectors. Max original dx18/dy-12 plus the final OLDrectangle commit and42x41geometry give conservative boundsX-78..676,Y-65..300. Prelaunch zero-speed opcode30can set periods-1 while standardMotion remainsfalse. No selector-derived velocity or fresh coordinates replace saved history.

Preflight validates the complete stream, checksum, original HYP identity/profile,605metadata and all static/dynamic sprite/extra constraints. Original target geometry is decoded before mutation. Restore uses loadPlace(false,true), live runner import, exact clock freeze,37sprite records and118extra records, then redraw; it does not replay setup. Immutable-resource assumptions exclude concurrent host filesystem replacement after preflight and arbitrary resource corruption outside recorded original identities.

Final measured SDL diagnostics, historical failures, source/executable hashes and limits are in CHECKPOINT.md. Root coordinates independent fresh-process metadata/continuation checks, integration, same-build WASAPI suite and publication. SDLdummy is not manual original play or official audio proof.


## Official same-build verification,25 October2026

Native WASAPI,86 measured boundaries,all6944truncations/all6944byte corruptions,fresh-process slot21 and metadata,and unchanged genuine frozen v21slot20 PASS. The complete compatible native suite passed on the same executable. Earlier SDL investigation remains historical evidence. The coverage measure becomes26/35inventoried puzzle route scenes (74.3% of save-scene coverage); it does not measure whole-game completion.
