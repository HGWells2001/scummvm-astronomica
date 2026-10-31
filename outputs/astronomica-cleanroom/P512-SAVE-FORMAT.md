# P512 stopped-ready save format29

Status: complete exact-main native WASAPI validation PASS. Publication and the frozen checkpoint have separate gates.

The scope is an original P512 question ready for input after its movie selection has stopped. Active movie playback, queued work, foreground voices, pending images and unsupported private histories are excluded. All six original scenarios, including the unanswered final mask127, retain their original controls and solution logic.

The payload is9932bytes: four-byte `ASVM`, little-endian version29, then2481little-endian uint32 words including the checksum. ScummVM metadata may follow the payload. The checksum starts at2166136261 and updates `(hash XOR word) *16777619` modulo2^32 for every packet word except its final checksum.

| Packet words | Meaning |
|---|---|
|0–23|Scene512,completion count,logical epoch,previous scene,literal Music loop identity and active/waiting state,comet frames,independent stopped movie clock/current/presented frame,selection endpoints,scenario,draw count,position,volume and sound history|
|24–628|All605runner words,including dormant values,metadata,RNG,program epoch and variant process statics|
|629–2356|64independent sprites ×27words|
|2357–2474|118private Comet/Jupiter words|
|2475–2479|Five private Ball values|
|2480|Checksum|

The loader validates the complete packet and original assets before transferring ownership. It reconstructs the background,panel,sprites and presented movie image independently of the stopped decoder cursor. The stopped media clock is retained separately from that cursor. Original scripts and callbacks are rebound to fresh owners; original startup programs and introduction302 are not replayed on load.

The original S0 Music loop restarts from its beginning when the saved state says it is active. Its waiting/active state,recipient volume and mute settings are preserved. Nested engine pauses retain the caller’s token ownership and do not consume the restored underlying PCM before release. No sample-exact audio continuation is claimed. A mixer channel is allocated during commit; exhaustion at that point is a fatal internal resource failure,not a recoverable atomic refusal.

Dedicated native tests use slot28 for an ordinary active-Music question,slot29 for the unanswered first-completion final question and slot30 for the repeated-completion final question. These are test slots in separate directories,not user save slots. Genuine sealed format28 fixtures with literal disabled loop IDs−1and0 must load unchanged in both entry modes,alongside the full inherited version1–27 native chain.

Automated checks do not replace the complete manual audiovisual playthrough.
