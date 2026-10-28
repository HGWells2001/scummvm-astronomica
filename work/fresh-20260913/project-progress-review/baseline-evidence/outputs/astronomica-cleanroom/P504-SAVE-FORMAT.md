# P504 save format26

Status: same-build native WASAPI and complete compatibility verification PASS27October2026; publication requires the separate export gate. Scope is `trusted_p504_partial_orbits`, diagnostic slot25. All23 baseline files and the six staged source hashes are bound in BASE23/BASE/CHECKPOINT.

Payload7816bytes: big-endian ASVM magic, little-endian version26,1951 little-endian words and one checksum word. Whole-word checksum starts2166136261, folds `(hash XOR word)*16777619` modulo2^32, and excludes magic/version.

|Data-word offset|Count|Meaning|
|---|---|---|
|0|11|Scene504, completed count, logical clock, previous place, ambient sound, loop enabled, lastSoundAt, ambient active, Comet frame, previous Comet frame, reserved0|
|11|1215|45sprites,27words each|
|1226|607|605persistent runner words plus original pending index/since|
|1833|118|50Comet kinds,50signed links,sound/explosion scratch,8Jupiter widths,8heights|

The sprite layout is the existing literal27-word representation: visibility/frame, stored and rendered positions, animation/motion flags and independent epochs, signed deltas, orbit sides, range/click metadata, frameData[3],moveData[5]. Every field outside the proved mutable profile is compared with the exact original resource. Global Comet frame/previous are in the header, so the complete104-word Comet state is preserved across both sections. Jupiter cache is retained independently.

Whole HYP805459bytes SHA256 `dde86ef89aa520e16d006b41ddefece537f81901ad3e8db13c5a3bbe5e6009ba` is bound. Parsed prefix656595 SHA256 `bf4723e44a32953ab5858fddcc7fd22760cab86aec08c75522a1b3f5726cff7b`; opaque tail148864 SHA256 `3c129f7eb2f5e335d0c451db0a0df36be13f0a642fe41776f86cb5f38ebbc0de`. All three original startup programs are matched command by command, including opcode, delay, arguments and text. Tail decoding is not claimed.

The pending kernel accepts exactly one unchanged original program0 at index0or10, with no actions/input lock. Index0 retains since==loadedAt; index10 retains its own timer epoch even when due. Observed index3 is explicitly rejected for snapshots and is retained in ordinary future execution after restoring an accepted phase. There is no clearing or reconstruction of the queue. Local7/local8 must be0, direction1..4, speed0..15, target1..4 and solved mask0..14. Capability is explicitly reset/bound on every load.

Healthy incomplete pairs preserve primary23..26/back30..27, center320,160, original radii and opposite signed links. Primary kind4 with inactive hidden backkind1 or moving backkind4 is accepted. Side bits1/1 with zero deltas are an original transition, not normalized. Never-solved stopped failures with unlinked kind0 backs are also accepted. Solved-then-failed stale kind4 backs, primary ascent, full mask15 and completion/other queued work are excluded. Scratch(-1,0)or(3,31), selected frames, prior completed explosion, both epochs and dormant cache are retained literally rather than inferred from current controls.

Load preflight validates length/checksum/header/assets/scene/programs/sprites/private values and imports all607words into a separate original-program runner with a Comet callback. It never ticks that prepared runner. Only then does the live scene load and validated state install, without startup replay. Failed preflight must leave live queue/audio/pixels/clock/private state untouched. Host filesystem changes between preflight and actual reopen remain outside the same atomicity guarantee used by earlier formats.

Required final proof includes256 real UI combinations/252 failed launches,14 proper masks plus0, four actual first-kind4 transitions, partner handoffs, literal poll index0/10 continuation through index3,24 poll timing cases and18 independent frame/move/wrap cases, explicit index3 rejection,7816truncations/corruptions, checksummed invalid poll/state values, natural S1 completion, Music-volume-preserving ambient restart, first/repeated real completion, and physical slot25 loading in a new process with metadata. The prior728-observation audit and separate native poll kernel are preparatory inputs, not substitutes for these full-engine tests.

## Official same-build verification,27 October2026

Complete same-build native WASAPI suite,fresh-process slot25,metadata and unchanged genuine frozen v25slot24 PASS. Only the explicit trusted-poll partial-orbit P504 scope is verified. Earlier candidate entries remain historical evidence.
