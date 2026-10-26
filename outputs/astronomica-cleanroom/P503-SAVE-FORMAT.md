# P503 save format25

Status: complete same-build native WASAPI suite verified26October2026; publication requires the separate export gate. Baseline is the published P502 executable SHA256 `5245e9d449b34ae81cf463db644016e5d1081cfaa64ae1aaf1f3bb52065e0ccd`. Six source hashes and all23 canonical hashes are retained in BASE/BASE23/CHECKPOINT. Slot24 is used by diagnostics.

Scope name: `quiet_p503_partial_orbits`. Healthy partial solutions with one to four moving orbit pairs are supported, together with prelaunch controls and stopped failures on targets that have never been solved. A completed five-bit mask, active primary ascent, pending programs/actions, input locks, foreground speech, movies, image transitions, hover/drag and unrelated plot/world/private motion are rejected. Solved-then-failed one-way stale partner histories are explicitly excluded; their native audit remains preserved rather than normalized into healthy pairs.

The payload is8132bytes: big-endian `ASVM` magic, little-endian version25,2030 little-endian data words, then one checksum word. The checksum starts2166136261 and folds each data word as `(hash XOR word)*16777619` modulo2^32. It excludes magic/version. Data layout:

| Word offset | Count | Content |
| --- | --- | --- |
|0|11|Header|
|11|1296|48sprites,27words each|
|1307|605|Full ScriptRunner persistent state|
|1912|118|Private Comet/Jupiter data|

Header words: scene503, completed-puzzle count, logical clock, previous place, ambient sound id(-1or0), ambient enabled1, lastSoundAt, active ambient flag, global Comet frame1..12, previous Comet frame0..12, reserved0.

Each sprite stores visibility, selected frame, storedx/y, renderx/y, autoFrame, autoMove, frameSince, moveSince, standardMotion, moveDX/DY, orbitMotion, orbitSideX/Y, frameFirst/Last, clickEnabled, frameData[3], moveData[5]. Signed values retain their exact32-bit representations. Both side bits may be1 in the actual first-kind4 transition. Every sprite's frame and movement epochs remain independent; partner handoff does not copy epochs. Dimensions, clone owners, layers and all fields outside the proved mutable profile are bound to the exact original resource.

The605 runner words retain100 global and100local value/width/known triples, RNG, loadedAt, lastTrue and dormant variant sequence data. Local0direction1..4, local1speed0..15, local2target5..9, locals3..7 solved bits, local8zero. All30 proper nonempty masks are native diagnostic cases; mask31 owns the original queued P504 transition. Current controls are independent of the retained orbit/failure history.

Private words are50kind entries,50signed partner entries, sound/explosion scratch,8Jupiter widths and8heights. Global Comet frame/previous are in the header, so all104 Comet words including those two are retained. Healthy pairs use primarykind4 with negative partnerid and hidden/visible partnerkind1or4 with a positive backlink. An inactive kind1 partner preserves its original render position and zero move epoch; it already has the configured ellipse center/radii and30ms animation. Never-solved stopped primarykind2/3 has no links and a kind0 back partner; the launch still changed that back partner's frame period to30ms. Every private entry outside the five original pairs remains zero. Scratch may be(-1,0) or(3,34), retained literally rather than reconstructed from the current selection or kind. Dormant Jupiter geometry is either allzero or the complete known P516 cache.

Whole original HYP782595bytes SHA256 `0b6e4b9afa8bafa670b19d8e79cbdb6bab7f675166aabfe27f9d421d9ed3447f` remains part of asset identity. Only617311bytes are parsed; the165284-byte tail remains opaque. The loader validates the complete payload, checksum, header, original asset identity, parsed profile, sprites/private data and prepared runner before its first live scene mutation. Host filesystem changes between preflight and actual scene opening are outside this atomicity claim, consistently with earlier formats.

Required proof includes320 actual UI launches,312 stopped failures, all30 proper masks, five first-kind4 boundaries using a200ms native event cadence, partner handoffs, first/repeated P503->P504->P527 outcomes, ordinary and wrap-aware30/40ms timer edges, exact save/restore plus logical successors,18 timer cases, dormant variant/Comet/cache state, natural S1 completion and Music-volume-preserving ambient restart. Malformed-load checks cover8132truncations,8132single-byte corruptions and checksummed invalid states against the unchanged live state. A second process must load physicalslot24, match its fingerprint, continue the full puzzle family and list its metadata. Candidate-only and second-process proofs must bind identical source/executable hashes before review or promotion.

## Official same-build verification,26 October2026

Complete same-build native WASAPI suite,fresh-process slot24,metadata and unchanged genuine frozen v24slot23 PASS. Only the explicit quiet partial-orbit P503 scope is verified. Earlier candidate entries remain historical evidence.
