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
| 9â€“10 | Residual image x/y,160/40 if present, otherwise0/0 |
| 11â€“12 | Last attempted segment start/end in30Hz ticks;0/0 only before any attempt |
| 13â€“14 | Cross-puzzle comet phase and previous phase |
| 15 | Reserved zero |

The605-word runner state preserves all global/local values, widths and known
flags, RNG, program timestamp, comparison result and dormant variant round/mask.
Unknown local slots can retain historical values; they are preserved rather
than invented as zero. The four declared locals use their original widths.
Selector0â€“15 is independent of previous outcome digits and residual movie.
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


## Segment and retained-image invariants

The original script intervals are in30Hz ticks; readouts below are the three
digit sprites. End values are the engine's actual start-plus-length boundary.

| Selectors | Last attempted start/end | Historical mask flag value | Readout | Eligible retained samples from this group |
|---|---|---|---|---|
| 13–15 | 0/359 | 2 | 002 | 0–79 |
| 9–12 | 360/719 | 1 | 005 | 80–159 |
| 6–8 | 720/946 | 8 | 015 | 160–213 |
| 1–5 | 1029/1261 | 4 | 005 | 215–252 |

Before any attempt, the segment pair is0/0 and the readout000. Do not infer
movie identity from the readout:005 belongs to two different groups. Likewise,
the current selector does not identify either the last attempt or last picture.
The last attempted group validates the readout and its mask bit; a retained
picture independently validates its own group's bit. An absent picture is valid
after an attempt when the first movie update arrived after the segment ended.
Header0/359 therefore remains distinct from0/0 even when both have no picture.

The variable-duration samples hold frame79 from tick237, frame159 from597,
frame213 from879 and frame252 from1140. Sample214 begins at948 and ends at1029,
outside the requested movie segments; it cannot be a settled retained picture.
End checks run before decoding, so a delayed update can leave an earlier picture
unchanged. A decoder seek-to-end can also change its cursor without presenting
any new pixels. Only the successful surface-copy commit updates the saved sample.

The253-sample comparison validates native frame reconstruction across the full
asset; ordinary round trips and the two explicit zero-frame histories validate
how that image state combines with script and control history. Most test routes
skip movies after a real presentation and do not establish natural final-frame
save timing for every real-time playback history.
