# P529 universe saves, version15

Implemented and verified21 October2026; see evidence/universe-saves-validation.json. Native WASAPI and the complete compatible suite pass on the same executable.

The native payload is3684 bytes: ASVM magic, version15, sixteen32-bit header
words, eleven27-word sprite records,605 runner words and an FNV integrity word.
All payload integers are little-endian; the magic uses the existing format.

| Header word | Meaning |
|---|---|
| 0 | Place529 |
| 1 | Completed-puzzle count |
| 2 | Script clock |
| 3 | Previous place |
| 4 | Ambient sound0 or-1 |
| 5 | Ambient enabled |
| 6 | Last ambient start timestamp |
| 7 | Ambient currently playing |
| 8 | Last presented absolute video sample, or-1 for absence |
| 9–10 | Residual image x/y,160/40 if present, otherwise0/0 |
| 11–12 | Last attempted segment start/end in30Hz ticks;0/0 only before any attempt |
| 13–14 | Cross-puzzle comet phase and previous phase |
| 15 | Reserved zero |

The605-word runner state preserves all global/local values, widths and known
flags, RNG, program timestamp, comparison result and dormant variant round/mask.
Unknown local slots can retain historical values; they are preserved rather
than invented as zero. The four declared locals use their original widths.
Selector0–15 is independent of previous outcome digits and residual movie.
Local2 agrees with outcome-mask bit3; mask15 causes departure and is not a
settled P529 state. Complete prior readout families000,002,005,015 are validated
against the last attempted segment and its historical mask bit. A retained
sample independently requires its own historical group bit, so it can belong
to an older group. No frame may have been committed during an attempt if the
first update arrives after its end; both residual absence with nonzero mask
and a previous group's residual are preserved exactly. All sprite coordinates and flags use
their own original records, including clones10/11; only frames share source9.
Inactive digit frame periods0 and-1 and shared stopped timestamps are retained.

Saving rejects pending commands/actions, blocked clicks, automatic framing or
movement, active video, foreground audio, hover state and uncommitted images.
The test harness may stop foreground audio only after asserting this rejection;
that simulates completed speech and is not evidence of a manual playthrough.

The last-presented index is updated only after successful converted surface
copy in updateMovie and reset with the retained surface. It is never inferred
from the decoder at save time. Preflight checks the original asset profile
(sizes and FNV fingerprints; SHA256 provenance is external evidence), parses
the original scene, validates all state, loads a temporary stopped decoder,
seeks the recorded sample, decodes explicitly and converts to the native screen
format before touching live state. Missing/invalid samples or assets reject.
The original's unique video track has one linear edit, variable frame durations,
and253 samples. The separate audit compares all253 sought frames against
sequential native decoding byte-for-byte. Sample214 lies outside every original
segment and is excluded from settled residual images.

After preflight, the existing loadPlace path checks scene/background inputs
before its normal mutation point. State and the prepared movie surface are then
installed without startup scripts or foreground speech. The movie remains
stopped; a later positive selector playback supplies its own original segment.
Diagnostic decoder cursor/time and frames-drawn counters are not game state.
Ambient music restarts according to the older formats' existing convention.

Malformed payload rejection is tested against complete state/surface fingerprints
and frozen-clock offsets. Host-side file changes between preflight and scene
load remain outside that guarantee. Native WASAPI and official integration pass with the full same-build suite. Natural real-time final-frame save boundaries and broader manual gameplay remain unverified.
