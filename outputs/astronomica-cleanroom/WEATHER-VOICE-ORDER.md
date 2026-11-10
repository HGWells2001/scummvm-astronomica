# P512 result ordering at an error voice, 10 November 2026

The original weather validator plays an error voice before storing zero in local5. The engine previously stored zero before entering the blocking sound callback. The update moves that store after the voice callback. Sound selection, final result, movie handling, headers and save layouts are unchanged.

For example, scenario1 with settings0/0/0 and a preceding result1 selects S10. The original voice boundary still observes result1, followed by final result0. The pre-fix native engine observed zero at that boundary. Both the original UI numeric-domain comparison and an actual original movie/WASAPI voice test reproduce the difference. The corrected implementation observes one and resumes the decoder after the voice.

The preceding result is a controlled input in these focused tests. They are not presented as a complete natural mouse-interaction history or a human audiovisual playthrough.

## Original evidence and verification

The unchanged original executable has SHA-256 `c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e`. The bounded replay executes the original mode0 dispatcher/validator and the empty `_in_custom` body. Original voice calls are observation boundaries recording the selected sound and preceding result; the original Windows application is not run. Original P512 command operands are checked against the HYP bytes.

The expanded original-instruction/native comparison passes61,648 cases and123,296 blocking/asynchronous modes, aggregate `918e40e1`. It includes the full6×16³ original settings domain with both prior result values, signed extremes and invalid scenarios. All200 final scalar words are checked. Three independent corruptions of expected final result, prior result at voice, and selected sound are rejected. A permanent focused test retains the voice-before-result requirement.

Two temporary real-engine builds execute the original HYP movie-entry program and mode0 command with the original clip and S10 WAV. Their ScriptRunner sources exactly match the pre-fix and reviewed fixed versions. Their private diagnostic additions are not installed. The original-instruction replay uses Capstone5.0.7 after the already recorded REA rejection of the NE executable; no provider repair or original Windows execution is claimed.

Compatibility checks use two genuine ASVM29 files produced by the exact pre-fix installed main after twelve natural P512 question boundaries. Four fresh processes load the first/repeated-completion files with entry scripts enabled/disabled and finish through the original controls to P157 without replaying startup. Physical files remain unchanged. This is scoped compatibility evidence, not all historical save versions or every P512 boundary.

The current fixed acceptance scheme remains7/10 (70%), with35/35 documented bounded save profiles. Whole-game completion remains unmeasured. Full behavior scope, exact help typography and human audiovisual review remain open.
