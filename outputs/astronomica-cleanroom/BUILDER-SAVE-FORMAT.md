# P515/P536 construction save format

Implemented and verified20 October2026; see evidence/builder-saves-validation.json.

## Evidence and boundaries

Original MEGAFILE.HYP observations are in evidence/builder-save-original.json and BUILDER-SAVE-PLAN.md. The native control audit records a different kind of evidence: observations from this ScummVM engine, not execution of the Windows original. Its190 boundaries cover all five designs, ordinary two-phase routes, early Launch and the absent P515 success handler. Neither observation set establishes a complete manual audiovisual playthrough.

The v13 format permits settled construction boundaries in both scenes. Pending scripts/actions, click blocking, staged pictures, movies, foreground speech, pressed button frames and unrecognized picture history reject saving. Ordinary audio, animation and sprite input must all be explicitly enabled. Choose stages an image; Confirm commits it, so the intermediate staged-image state remains ineligible.

## Packet

The8960-byte payload contains ASVM, little-endian version13, twelve header words,60 complete27-word sprite records,605 persistent runner words and the existing word-wise FNV checksum. Header fields are scene, puzzle count, script clock, previous scene, ambient sample, ambient enabled, last sound epoch, ambient active, picture ID, dormant comet frame/previous frame and one reserved zero. Picture IDs are0 absent,1 drydock and2 pad. Loaded images must be250x330 at0,0. Opaque ordered overwrites in the original resources permit retaining the last image; the initial absence of an image must also round-trip.

The first603 runner words retain the existing values, known flags, widths, RNG, program epoch and condition state. Words603/604 retain the process-global custom17 round/mask, validated with the same constraints as v10. A new scripts-idle export/import admits a dormant custom17 sequence while preserving the older idle API and every layout1–12. The two process-global comet orientation values also survive scene loads (original callback research in COMET-RESEARCH.md). Header9 accepts frame1..12 and header10 previous frame0..12. Six synthetic legal phase fixtures exercise byte retention and successor comparison; the fresh-process slot must retain3/4. These fixtures are test state, not an additional original execution trace. Loading must not reset that saved sequence while rebuilding the scene's original custom-handler context.

All27 sprite fields are retained, including stored/rendered coordinate differences and inactive timer history. In particular, opcode7 with stored coordinates0,0 can leave the last rendered placement visible. Validation accepts the original literal positions and finite construction offsets; it must not infer coordinates solely from the logical construction stage.

Known local widths are5,5,5,6,7,1,1,1,1,1,1,1,1. Accepted domains are mask0..31, design0..5, stage0..5, required size0/4/5/6, size0..6 and boolean flags. Unknown locals13–99 remain unknown with width0 and retain their raw values. Controls can be used outside the successful sequence: fitting a cap before choosing sets its flag while size remains6. P515 can select designs4/5 after early Launch stores mask7; P536 initially has design2. Those valid cases must not be rejected by an overstrict validator.

Validation and resource/picture preflight precede any live scene mutation. The loader restores background, sprites, runner, clock, count, previous scene and ambient state; entry scripts stay suppressed. An active ambient sample restarts from its beginning. No audio-position preservation is claimed.

## Verification

check_builder_saves.py drives the actual native controls through six routes, compares full480-row rendering and successors after restoration, and exercises every primary control at several construction stages. Choose and Confirm are one compound continuation where required; intermediate successor comparisons include the staged image's name, position and pixels.

The dormant-sequence cases load only the verified test fixture slot9 through an isolated test slot99, then enter construction. The original fixture and alias must remain byte-identical. Physical slot12 is prepared in P536 design5 after parts46,47,53, with dormant round2; a new process must finish construction and increment global31/count exactly once while preserving round/mask. Personal saves are not used.

Prepared rejection tests cover every truncation and single-byte corruption, plus checksummed invalid fields, with no mutation of the current state. Positive Music restart and negative foreground/pending-image/button-pulse guards are included. check_builder_regressions.py first reads the frozen v12 slot11, then runs builder verification and all older graphics/audio/help/import/save suites on one executable. All these checks pass on the same build; the archived logs and proof record the measured coverage.

Successor comparisons retain every saved builder byte exactly. After departure to a newly loaded scene, an active frame timer compares elapsed age rather than its new absolute epoch; this avoids treating millisecond differences in foreground WAV duration as changed animation state. Six departure comparisons exercise this rule.
