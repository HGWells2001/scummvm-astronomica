# P527 version23 saves

Status: complete same-build native WASAPI suite verified25October2026; publication requires the separate export gate. Scope: `quiet_p527`. No active playback or queued work is saved.

The original HYP is348102bytes SHA-256 `03df944bdc8dffc6780ba324c6879b7cd91529e741637dd7c59acde220aad6a4`; original MOV is8387803bytes SHA-256 `f33e62405662875f3fd1d85087f19954f4d334a3235d528f53facd404dd3b4f3`. The selected movie has1105Cinepak samples,320x240,30Hz timebase,duration3618ticks. Candidate tests compare all1105 sequentially decoded pictures to seekToFrame reconstruction, including nonsyncsample801, using converted pixel-row byte comparisons.

Payload3940bytes before ordinary ScummVM metadata/thumbnail: magicASVM, uint32LEversion23;982uint32LE datawords; finaluint32LEchecksum. Checksum starts2166136261 and folds each dataWORD as `(hash ^ word) *16777619` modulo2^32. Magic/version are excluded.

Header16 words: scene527, completedcount, logicalclock, previousplace, loopsound(-1/0), loopenabled1, lastSoundAt, ambientactive0/1, presentedframe(-1whenabsent), imageX(0whenabsent otherwise10), imageY(same), lastattemptedrangestart, rangeend, processglobalCometframe1..12, previousframe0..12, reserved0.

Next243words: nine sprites in existing27-word field order (`p526SpriteWords`). Positions, visibility, selectedframe, motion/animation epochs, flags, frame/move configuration and clickenabled are preserved. All static fields must match the original resource; selectedframes of buttons1..4 exactly reflect local3 (0meansnone), other buttons frame0 at quiet boundaries. Sprite drag/orbit/planet state must remain the P527 default.

Next605words: all100global and100local value/width/known triples, RNG, programLoadedAt,lastTrue,dormantvariantRound,dormantvariantMask. Global values and unknown-local values are retained verbatim. Global metadata follows the existing admitted width0 or inherited first-threewidth6 profile; local known/width fields must match P527's eight original condition declarations. Local0=52,local1=0,local2=0,local3=0..4,local4=1,local5=0..14,local6=0/1,local7=`bool(local5&2)`. A nonzero mask requires a selection andlocal6=1. Fullmask15 enters the original pending success path and is excluded. Startup with selection0 legitimately setslocal6=1 and leaves mask0.

Final118datawords: CometMotionkind[50],partner[50],sound,explosion,Jupiterwidths[8],heights[8]. P527 requires allkind/partner0,sound-1,explosion0. Dormant Jupitergeometry must be allzero or the complete known P516shape (widths50,39,110,60,60,110,39,50 and heights50,100,40,60,60,40,100,50); it is restored exactly. The current BallMotion,ProbeMotion,RocketMotion,plot/danger events and worldmovie cursor must be P527 defaults before saving. Their default reconstruction is guaranteed by loadPlace.

Selection1 uses range[1800,2399),maskbit1,presentedsamples600..799; selection2 uses[2568,3527),bit2,samples801..1079; selection3 uses[900,1799),bit4,samples300..599; selection4 uses[0,899),bit8,samples0..299. Sample800 and1080..1104 are excluded from retained P527 pictures. A displayed sample must belong to a seen maskbit, but need not match either the currentselector or lastattemptedrange. The attemptedrange bit must be present in the mask. Mask0 requires range0/0 and absentpicture. Nonzero masks admit an absent picture if playback ended before its first sample was committed.

Load validates complete checksummed state, original-file identities, original sprite/profile shape, local metadata, dormant state and exact prepared native movie reconstruction before live mutation. It installs the exact retained picture and range; no startup scripts run. The original ordinary audio loop resumes once if active, retaining Music volume; its sample cursor is not retained. Foreground sound, movies in playback, pending image, hover-entered or pending/locked script states are excluded.

Tests use slot22 and metadata title `P527 continuation regression`, then load it in a new process. Candidate evidence remains diagnostic until the complete compatible native WASAPI suite passes on the promoted executable.

Quiet save/restore checks compare all605runnerwords exactly and compare the same1000mslogical successor exactly. A first success plays a real blocking voice whose wall-clock duration can vary between runs. Terminal continuation comparisons therefore compare the full game outcome except destination programLoadedAt601, and separately require departure at520..539ms after the measured success-voice end (original500msdelay plus20mstick). A repeated, already-counted success has no success voice and requires the identical logical terminalclock. This does not claim equal physical speech duration across runs. Host-side resource changes between preflight and final loadPlace I/O remain outside the atomicity guarantee, as in the existing P529 implementation.

## Official same-build verification,25 October2026

Complete same-build native WASAPI suite,fresh-process slot22,metadata and unchanged genuine frozen v22slot21 PASS. All1105original frame reconstructions compare byte-for-byte. Earlier candidate entries remain historical evidence.
