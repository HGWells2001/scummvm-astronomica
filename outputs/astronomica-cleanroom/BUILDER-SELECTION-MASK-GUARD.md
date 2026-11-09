# Original builder selection pools, 9 November 2026

The native ASVM13 builder parser previously accepted every selection mask from 0 to 31. Original P515/P536 resources permit a smaller, closed set. A checksum-valid edited packet could therefore introduce a project-selection pool that the original scene programs never create.

The real engine now checks that pool for the incoming scene before replacing the receiver. The save writer applies the same check before emitting any bytes. The ASVM13 layout, checksum, sprite data and numeric project ranges are unchanged.

| Scene | Original initialization and updates | Accepted component masks |
| --- | --- | --- |
| P515 | Starts at 24; selection and early-Launch scripts can reset to 7; free-bit selection only adds bits | 7, 15, 23, 24, 25, 26, 27, 28, 29, 30, 31 |
| P536 | Starts and resets at 7; free-bit selection only adds bits | 7, 15, 23, 31 |

These are component invariants, not a complete reachable-state model. In particular, original early Launch can allow later designs while still in P515. P536 also legitimately initializes its current project number to **2**. Both behaviors remain supported; this change deliberately preserves the previous numeric project bounds.

`verify_builder_masks_nov9b.py` checks original file hashes, every serialized scalar writer, initial condition bytes and the original custom25 dispatch. P515 has no custom25 handler; P536 invokes the global31 success path. No original file is repaired, substituted or modified.

## Verification

The public codec comparison first observes the old guard accepting **49 forbidden masks**: 21 for P515 and 28 for P536. With the new guard, all 49 rehashed in-memory packets are refused atomically, and all 49 invalid live-state writes return failure with zero output bytes. Fifteen component masks remain accepted. These are public `loadGameStream`/`saveGameStream` tests, not 49 physical file loads.

The complete existing builder save suite passes, including natural controls, wrong-size recovery, early Launch, default P536 project2, dormant variant round2, truncations, corruptions and valid continuations. A genuine physical ASVM13 produced by the exact previous installed executable `89fdd9016b3c38e17f12835a65c7516a88ac2918112c415391aa340e1d94ac41` loads in a fresh process with identical fingerprint `d6e10777` and completes the remaining controls to P510, global31=1 and completion count11. Its bytes remain unchanged.

The general native verifier and the installed-path genuine-save continuation also pass on executable `51ae19ca62b3b3cdbe24245069c84ae3351c040e19b3217cf28ead99b44f4943`. This one-file engine delta freshly compiled one translation unit and reused 409 hash-verified objects from the clean 410-unit ASVM31 foundation. Headers, ABI and the mandatory three-file video overlay are unchanged. A new fresh 410-unit build is not claimed; source installation still requires the paired overlay and a clean build.

Two preliminary hypotheses were rejected before any production installation: P515 does not permanently retain mask24, and P536 project2 is not invalid. The original bytes and full natural tests exposed those mistakes. The final change constrains only selection masks. Failed diagnostic stages remain local; none was installed.

Fixed acceptance remains **7/10 (70%)**, with 35/35 documented bounded save profiles. This does not establish a whole-game completion percentage or replace the remaining original-branch, help-typography and human-playthrough work. Physical saves, thumbnails, binaries, raw operands and disassembly remain local.
