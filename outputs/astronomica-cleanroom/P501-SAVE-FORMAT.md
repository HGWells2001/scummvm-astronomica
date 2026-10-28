# P501 ready-state save format27

Status: complete same-build native WASAPI verification PASS; publication requires the separate export gate. Scope `trusted_p501_ready`, diagnostic slot26, base finalized P504 main SHA256 `2a305b13466244f84cfd092bfa20774ea0bcfe2f91dbef77decddb850a3a727c`.

Payload5896bytes: ASVM magic/version27,1471 little-endian data words and checksum. Word sections are12header,729sprite,607runner,118Comet/Jupiter and5BallMotion. Checksum is the existing whole-word FNV fold excluding magic/version. Header contains scene501,count,clock,previous place,ambient id,loop enabled,lastSoundAt,ambient-active flag,Comet frame/previous,reserved0 and background selector.

Background0 preserves empty displayed name and the embedded original background;1 preserves `backorbi`;2..6 preserve `phobos`,`blackdwa`,`jupiter`,`vesta`,`moon`. The six original bitmap filenames have no extension. All six whole files and fully parsed786726-byte HYP are bound; chosen image is decoded and shape640x320 validated before live mutation. Name identity is retained even where embedded/BACKORBI pixels are equal.

The607 runner words preserve605persistent words plus literal original program0 pending index/since. Exact eight-command template, index0or7, no actions/lock, won0,pitch0,strikes0..2 are required. Index0 since equals saved loadedAt;200ms reschedule epochs remain literal. New capability resets on every load. Recipient preflight installs the original program and Ball callback and imports state without ticking callbacks; only then may live loading/install occur, without startup replay. All729 sprite words, five Ball fields and118Comet/Jupiter words remain independent and literal.

Stopped ball can retain nonzero deltas and old stored/render coordinates. Supported dormant Ball profiles are default plus regular Phobos/Moon/Vesta hit center ranges, including Vesta side0/period5000 across another selection. These are bounded regular profiles, not universal claims about arbitrary interleaved clicks. Hidden crush frames and no-world reset history persist. Other private motion must match explicit defaults; dormant Comet phase/cache is retained. Active pitches, won/departure, generated cleanup queues, pending images and foreground sound are excluded.

Additional native audit183 is frozen in `additional-ready-audit`; it proves fifteen hit/selection ready histories but is not save proof. The first serializer test failure was the strict hit fixture: asynchronous button dispatch moved the ball after a requested boundary. Exact four hit and four catch thresholds are now explicitly real-callback fixtures; genuine button-based pitch/hit/catch completion remains a separate future route. The validP501Loop preflight now checks state size/world before indexing, with malformed6/ffffffff rejection tests.

Required proof counters are world_states6,background_identities7,cross_world_histories15,strike_histories3,input_windows8,vesta_pauses1,poll_timer_cases24, plus5896truncations/corruptions and checksummed-invalid atomic rejection including displayed-image identity. Natural voice/Music, first/repeated actual success, voluntary exit and physicalslot26 fresh-process metadata are required. Until exact candidate/fresh proofs and independent review pass, this remains staged development only.

## Official same-build verification,28 October2026

Complete same-build native WASAPI suite,fresh-process slot26,metadata and unchanged genuine frozen v26slot25 PASS. Only the explicit trusted_p501_ready scope is verified; earlier candidate entries remain historical evidence.
