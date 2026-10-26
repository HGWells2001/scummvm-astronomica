# P502 version24 saves

Status: complete same-build native WASAPI suite verified26October2026; publication requires the separate export gate. Scope `quiet_p502_nonflight`,slot23. Native observation audit69records is retained separately under `work/fresh-20260913/p502-audit-stage`; it implements no save support.

The full669631byte original HYP has SHA-256 `880df2452622db2f9377793ef660cbc16ef534d6251394548bbebfacf2e8b020`. The parser consumes586447bytes(0x8f2cf),SHA-256 `1c5260dc5cd5d13a9cbdee4590cb31ebe3b4d7fa4342ce54ed1af84e2c8d7c49`. The remaining83184bytes,SHA-256 `490792195eb49ebedddac45900bea46b009065ca809b339f0a3807e8341b6cf7`,remain unparsed. The native reader reports this same consumed/trailing shape; save loading binds the entire original HYP identity and never claims that the tail was decoded.

Payload6728bytes before standard ScummVM metadata: magicASVM, uint32LEversion24,1679uint32LEdatawords,checksum. The checksum starts2166136261 and folds every dataWORD with `(hash ^ word)*16777619` modulo2^32, excluding magic/version.

Header11words: scene502,completedcount,logicalclock,previousplace,loopsound(-1/0),loopenabled1,lastSoundAt,ambientactive0/1,Cometframe1..12,Cometpreviousframe0..12,reserved0. Then35x27spritewords,605runnerwords and118extra private words follow. Sprite order is existing `p526SpriteWords`; runner order is100global/100local value-width-known triples,RNG,programLoadedAt,lastTrue,dormantvariantRound/dormantvariantMask. The118extra words areCometkind[50],partner[50],sound,explosion,Jupiterwidths[8],heights[8].

Local0direction1..4(width8),local1speed0..15(width20),local2target10(width20),local3=0(width20). Known/width metadata is validated while unknown-local values remain exact. Global values and inherited metadata follow the existing admitted first-threewidth6or0/global-known profile. All605words are restored exactly; no startup programs replay.

Admitted projectile20 histories are native-observed: initialkind0,hidden at stored/render520,270 with no standardmotion; failedlowkind2,hidden frame5 at stored520,310/render340,190 with standardMotion1,autoMove0,delta0,frameData0/moveData0=-1 and independent retainedmoveSince; failedhighkind3,hiddenframe0/render199,10 with the same stopped fields. Allother sprite fields must match original/static control-derived state. Direction buttons16..19 exactly reflect local0; six-digit speed and cumulative gauge reflect local1. The launchbutton9 is hidden/stopped after a completed launch.

Kind2 retains scratchsound3/explosion21 even after the queued explosion finishes. Kind3 retains scratchsound-1/explosion0. Explosion21 is either the original hidden state or an older hiddenframe9 at render320,160 with stopped configuration. A low failure requires that finished explosion; a high failure may preserve an older low explosion independently of its currentkind. This history is verified by a chained low-high-low route without reloading. It is never normalized to a clean entry.

Other Cometkind/partner entries are0. Jupitergeometry is either allzero or the full observed cache from an actual precedingP516entry: widths50,39,110,60,60,110,39,50 and heights50,100,40,60,60,40,100,50. All118extra words plus frame/previousframe are restored exactly. Current BallMotion,ProbeMotion,RocketMotion,plot/danger callback state and worldmovie cursor must remain P502defaults, which loadPlace reconstructs.

Saving rejects activeflight, nonzero local3, pending script/actions, locked input, hover-entered state, foreground audio, movie/pending/external images and unsupported private histories. Correctspeed13withdirection1or4 queues a16667mslocked transition503and is excluded. It is tested as a future from an admitted stopped state instead. Full native continuation follows the original P502-P503-P504-P527 route through first/repeated global21success and correct completion counting.

Malformed load preflights checksum, fulloriginalidentity, parsedprefixshape, every serialized field and a prepared runner before loadPlace mutates live state. Full truncation/byte-corruption rejection and checksummed invalid-state tests preserve live queue/clock/surfaces/audio/private state. Host I/O changes between preflight and final loadPlace are outside this guarantee, consistent with prior formats. Ambient restarts once with Music volume unchanged; samplecursor is not retained.

Native tests cover all64real direction/speed settings,62failed launches, the two successful settings via future continuations, hidden failure and explosion histories, all605runnerwords including dormant variant state, an actual priorP516cache and nondefault Cometframe/previousframe, inactive timer epochs/uint32wrap, real natural voice end, Music restart and fresh-process slot23/metadata. Quiet restore and1000ms successor comparisons are exact. First-success speech uses host-time duration; terminal downstream comparisons normalize destinationprogramLoadedAt601only and compare allremaining game data/sprites/pixels/private state. This does not claim identical speech wall-clock duration across runs.

## Official same-build verification,26 October2026

Complete same-build native WASAPI suite,fresh-process slot23,metadata and unchanged genuine frozen v23slot22 PASS. Only the explicit quiet nonflight P502 scope is verified. Earlier candidate entries remain historical evidence.
