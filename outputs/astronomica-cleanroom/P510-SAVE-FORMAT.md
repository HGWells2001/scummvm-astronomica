# P510 ordinary active-media save format28

Status: independent file review and complete same-main native WASAPI validation PASS. Source-only publication requires its separate export/clone/remote gate.

Scope identifier: `trusted_p510_ordinary_countdown`. P510 ordinary sole original program1/index6 countdown, current count1..51 with original width52 retained. Startup drained; no foreground voice, hints, pending image/unrelated work, unsupported lag or rate. Coherent paired Engine/movie pause is permitted and normalized; receiver Engine pause ownership is retained.

The engine payload is4540bytes: ASCII `ASVM` (4), uint32LE version28 (4), then1133 uint32LE words including final checksum. ScummVM may append standard metadata. Slot27 is the native continuation fixture; it is not part of the format.

Loop identity remains literal: word4 admits -1 or0 only while word5 (enabled) and word7 (active handle) are both0. Normal entry probes S0 and retains id0; original startup opcode25 disables playback without erasing the id. The diagnostic entry-disabled path retains -1. The ordinary-entry gate requires actual S300 completion, exactly four automatically queued original startup programs, paused byte restore and physical fresh-process loads with entry scripts both enabled and disabled on the same main executable. This is a domain correction within format28, not a new packet layout.

| Word range | Meaning |
|---|---|
|0..23|Scene510,completion,script clock,previous place,loop id/enabled,lastSoundAt,ambient0,Comet frame/previous,active media milliseconds,decoder current sample,presented sample,segment start/end30units,plot event/deadline30units,playing1,movieX261/Y33,volume,lastSound,lastBlockingSoundEnd,lastSuccessEnd|
|24..630|607 literal runner words:605persistent plus original pending phase/epoch|
|631..1008|14 independent sprite records×27 literal words|
|1009..1126|Comet scratch and Jupiter widths/heights118words|
|1127..1131|Five dormant Ball state words|
|1132|FNV whole-word checksum|

Checksum starts2166136261, then `(hash XOR word)*16777619` modulo2^32 for words0..1131. Signed fields use their uint32 bit pattern. Displayed sample absence is0xffffffff. Active current sample and separately displayed sample are not interchangeable; presentation can retain an earlier segment or have no sample yet.

Loads validate payload/checksum, all literal domains and original asset identities into independent stopped owned scene/runner/decoder/surfaces. Original sprite widths and each private/dormant record remain literal. Required script sound/callback/success capabilities bind to the recipient before commit. The prepared holder cannot copy/move or be reused. Explicit member swaps commit once, stop destination foreground audio, clear/rederive hover/navigation/history state, replace sound epochs, preserve user preferences and start media once. No startup commands replay. Preparation failure changes neither live state nor output bytes.

Active media uses public integer milliseconds. Raw11025Hz cursor convention is `floor(ms*11025/1000)`. Combined timestamp flooring may exceed1ms; mixer/output buffering adds uncertainty. No physical sample-exact audio claim. Segment lower bound is floor(start30units*1000/30), not ceil.

Measured isolated source proof:46 paused byte-exact roundtrips,4540 truncations,4540 byte flips,23 checksummed invalid fields,7cross destinations and8future routes. Fresh physical process reads slot27 and follows11original callbacks to P136 solved without startup replay. The exact candidate additionally passes WASAPI byte/fresh/metadata validation; frozen pause installation also passes continuous WASAPI. The main same-build compatibility chain has passed; final evidence/export/publication and complete manual audiovisual playthrough retain their separate gates.
