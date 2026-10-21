# P537 settled rocket save format

Implemented and verified21 October2026; see evidence/rocket-saves-validation.json.

ASVM version14 stores7680 bytes before the ScummVM extended metadata. It supports settled entry, selectors0..15 and completed failed-launch returns. Pending commands, the200ms selector pulse, active motion, foreground audio, movies and uncommitted images reject saving. A stopped rocket alone does not establish eligibility.

After the8-byte tag/version,16 little-endian DWORD header words retain scene537, completion count, logical clock, previous scene, ambient sample ID/enabled/last-start/active flags, stopped RocketMotion.delta/since and process-global comet frame/previousFrame. Header12 represents the stopped kind and must be0; words13..15 are reserved0. The header is followed by48 sprite records of27 DWORDs,605 persistent runner words, and an FNV word checksum.

The runner retains all100 globals, known and unknown local values and widths, RNG, program epoch, last conditional result and dormant custom17 round/mask. Only local0 is known in this scene, with width16 and range0..15. Unknown local values inherited from other scenes are preserved.

All sprite positions use each original sprite's own fields, including clones. Only bitmap frames inherit their prototype. Validation checks the complete indicator prefix against the selector. Previous digits, gauges and stopped motion are validated against the original initial/slow/fast families independently of the current selector. The digit pattern must match a complete original readout; arbitrary mixtures reject. Stopped timestamps and the21 inactive digit frame periods are retained.

The loader validates the full payload, checksum, state metadata, original scene and every sprite before replacing the current scene. It suppresses startup narration, restores the logical epoch and renders original resources. Ambient music may restart at its beginning. No save format for queued mid-flight scripts is introduced; versions1..13 remain readable.

check_rocket_boundaries.py observes real control states independently of the serializer. check_rocket_saves.py compares exact serialized bytes, full-frame rendering and gameplay successors for all16 selectors, first/repeated success, prior failed-launch displays, changed selectors, zero relaunch, controls and departure. Slot13 represents a fast failure followed by selector11 with dormant round2. A fresh process must complete exactly once. Corruption, truncation and checksummed invalid states must reject atomically. All these checks pass on the same executable; archived logs and proof record the measured coverage.
