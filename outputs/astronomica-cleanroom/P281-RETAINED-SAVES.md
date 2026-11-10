# P281 retained-round saves — 10 November 2026

Leaving an unfinished variant puzzle returns to P281 while the original variant bag remains partly consumed. Previously native saving at that return was refused. ASVM32 now saves an idle P281 gateway at retained rounds1,2,3, preserving all100 globals,100 local slots/metadata, random state, selected-variant mask, logical clock, completion counter and declared dormant caches. The next actual gateway click continues the remaining selection without repeating a visited variant.

P281 round0 keeps its existing ASVM2 format. An active gateway voice/delayed selection remains unsavable. This does not claim arbitrary scene, version or in-flight save support. No new ScummVM core change or class data field is introduced. Five private method declarations accompany the implementation and permanent tests.

The reader checks the complete native packet, checksum, state metadata, exact original P281 resource identity, static sprite and required voices before committing. Failed loads leave the live recipient unchanged. A successful load retires the previous recipient's pending actions/audio/decoder while preserving caller-owned nested pause tokens. No entry script or foreground voice is replayed on loading.

## Native packet

The native payload is2,652bytes: big-endian ASVM tag, little-endian version32,660 little-endian words, then one FNV word. ScummVM's physical file additionally includes its standard description/thumbnail metadata;2,652 is not the entire physical file size. The checksum starts2166136261 and applies `(hash ^ word) *16777619` modulo2^32 to the660 words.

| Word span | Meaning |
| --- | --- |
| 0..11 | place281, completed count, logical clock, previous place, last-sound epoch, Comet frame, previous Comet frame, last sound ID, last blocking-sound end, last success end, zero, zero |
| 12..38 | Original static gateway sprite, the existing27-word sprite representation; selected frame0 after normal scene initialization |
| 39..643 | Existing605 persistent runner words: values/metadata, RNG word600, program epoch601, last condition602, round603 and mask604 |
| 644..659 | Eight dormant Jupiter widths followed by eight heights |

Unknown local values remain inert but are preserved with width0/known0. Global metadata stays known; only global0..2 may carry the original width6 declarations. Round1..3 and popcount(mask)==round are required. Dimensions must be allzero or the exact known configured set; other Comet arrays and ball scratch must remain dormant. No primary game code reads ASVM32; this is the cleanroom engine's native save contract.

## Verified evidence

- Six physical files from six actual unsolved exits: first/repeated completion, retained rounds1..3. The second route additionally seeds valid dormant Jupiter dimensions/Comet frame caches; this is explicitly controlled coverage.
- Independent selection predictions from each serialized RNG/mask match all twelve fresh-process continuations, using the original custom17/range rules. This is a bounded mathematical model, not original Windows execution.
- Twelve independent fresh-process loads: all six files with the initial entry setting both enabled and disabled, followed by original gateway/unsolved controls to P519. No repeated variant; final completion count1 for both first and repeated routes.
- 2,652 truncated packets and2,652 single-byte changes refused atomically;23 rehashed invalid fields and three disabled configurations refused. Two existing idle ASVM2 roundtrips still pass, and eight pending gateway attempts write zero bytes.
- Two genuine pre-weather-fix ASVM29 P512 final-question files also continue correctly in four fresh processes on this executable, first/repeated completion and both initial entry settings. This is a scoped compatibility check.
- The same exact executable passes the existing general native suite and an installed-path physical-file continuation. WASAPI is used with playback muted for unattended verification. This is not a human audiovisual playthrough.
- Two source files change: astronomica.cpp/.h. All seven engine translation units are rebuilt;403 pinned foundation objects are reused, including the detection library object. The three paired video core files remain unchanged. Installing these sources requires a clean complete rebuild.

The preceding failed development runs remain local evidence: missing original declarations, initial-frame normalization and temporary diagnostic wording caught by the driver's failure detector were corrected before installation. They are not reported as passing gates.

Fixed acceptance remains7/10 (70%), with35/35 bounded scene profiles. Whole-game completion is not measured. Required behavior completeness, exact typography and a human audiovisual playthrough remain open. Original game assets, executables, physical saves and local frozen binary packages are excluded from this source export.
