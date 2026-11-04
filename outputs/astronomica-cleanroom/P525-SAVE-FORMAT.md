# P525 native saves, ASVM30

The verified engine now supports bounded stopped-ready P525 saves. The game payload is 5396 bytes: ASVM/version plus 1347 little-endian words, including its checksum. Framework thumbnail and metadata follow the payload. Script and sprite state, movie current/presented roles and background identity are retained. Original S0 music restarts at sample zero; this does not preserve mixer phase. Active movie playback, foreground speech, pending scripts/images and completion states are refused.

Six proof gates passed on executable b20721ee19d08ec5aa91d31e7de8bb42fe79f2e510004e2815d3f7539934cbc7: native physical saves, eight fresh-process loads, general native suite, genuine v14–26 original entry=false contracts, genuine v27–29 contracts, and the P281 gateway. No new genuine v1–13 fixtures were recovered. The v18 entry=true verifier assumption also fails on the prior sealed engine; it is not reported as a compatibility pass.

Save coverage is now 34/35 route scenes (97.1%); P523 remains. This is not a whole-game completion percentage. The last fixed project acceptance index remains 6/10 (60%); no complete manual audiovisual playthrough is claimed. Previous evidence files are historical snapshots and keep their producing executable hashes.

The engine source is self-contained and needs no new framework patch. Local archived library/PDB inputs from the older build remain historical: the current executable comes from the reviewed P525 candidate build. Rebuild from the current 23 engine files rather than mixing old engine archives.
