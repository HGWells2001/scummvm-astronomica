# Decoded hit-image dimension cache —10 November2026

Input hit testing previously decoded the bitmap of every earlier clickable sprite on each query, just to obtain its dimensions. The engine now retains successfully decoded dimensions keyed by current place and original image offset/size. It owns no pixel buffers or streams. Normal scene reload clears the cache; a different place also invalidates it before lookup. At4096entries further requests use the uncached decoder. Failed decodes are not cached.

The original resource is still opened on every query. A missing file remains an error even when dimensions were already cached. Frame changes look up their own image reference. Invariant-size checks for an unspecified frame remain intact. Original signed16 inclusive rectangular edges, first-sprite precedence and visibility/mask treatment are unchanged. In particular, hidden sprites may still have clickable regions: an early development visibility filter was discarded before use.

Only astronomica.cpp/.h change. The header adds private derived cache fields; all seven engine translation units were freshly compiled and403 pinned foundation objects reused, including the detection object. The paired three video core files and all native save layouts stay unchanged. Sources require a full clean rebuild. The cache and its diagnostic decode counter are not serialized; there is no new ASVM version.

## Verified scope

-41 original scenes,2,953 query comparisons against the frozen pre-cache decoder algorithm;35 hidden controls,227 unspecified-frame cases and264 unsupported geometry states.
-1,312 warmed repeat queries without another image decode, plus same-place reload invalidation, missing-file refusal and invalid-reference failures without cache poisoning.
-Identical P536 settled default-control graph:8nodes/120edges/24 selected-project or scene-exit terminals/1,902 predicate evaluations, using actual original exposed controls and replayed paths without local-value injection. Idle program/frame epochs are normalized. This is a bounded settled-state comparison, not arbitrary timing coverage.
-93 earlier P536 entry-interleaving clicks add651 predicate observations. The original condition at350661 remains unobserved. Neither unreachability nor a defect is claimed.
-The four isolated actual global-menu open/close profiles pass: English/builtin-language and fixed font scaling enabled/disabled, with game pixels preserved and the clock resumed. A font error seen only after a deliberately failed test did not reproduce on the positive path; no GUI configuration/font workaround was applied. This is not a human visual playthrough.
-Full same-executable general native suite, six genuine preceding-main ASVM32 files in12 fresh processes, actual installed-path continuation and installed-path41scene oracle passed. Original media playback uses muted WASAPI during unattended checks.

Two diagnostic builds share the exact shipping production source and differ only in observation code. Their recorded graph spans were269s before and40s after caching. Host load was not controlled, so these are descriptive timings, not an FPS guarantee or a controlled speed benchmark. The direct guarantee is unchanged hit results and elimination of repeated geometry decodes on warmed requests.

Rejected experimental runs remain local and are not reported as passing gates. The initial viewport-wide graph search was stopped as too slow; a visibility filter was rejected; normal navigation exits were then correctly treated as graph terminals. The first compatibility driver was stopped early because an inherited final assertion referenced the producer binary instead of the consumer; the corrected driver reran all12 cases.

Fixed acceptance remains7/10 (70%), with35 documented bounded native save profiles. Whole-game completion remains unmeasured. Complete required behavior, exact help typography and a human audiovisual playthrough remain open. Original media, physical saves, executables, toolchain objects and local frozen binary packages are excluded from this source export.
