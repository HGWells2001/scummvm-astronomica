# Animation geometry cache —10 November2026

The animation loop now uses the verified decoded-dimension cache instead of allocating/decoding an image just to obtain width and height on every motion update. Current-frame selection, file-opening checks, original physics functions, collision/sound callbacks, event order and final redraw stay in place. Drawing still decodes the original pixels; this change does not cache rendered frames or alter video playback.

Relative to the preceding input cache, only astronomica.cpp changes. The engine header, class layout, three paired video core files and every save packet layout are unchanged. All seven engine units were freshly compiled with403 verified foundation objects reused; this is not a new full410unit rebuild. Source installation still requires a clean complete build.

## Verified scope

Two actual-engine diagnostic builds share the exact respective production sources. Seven existing original-resource interaction verifiers exercise comets (P502-P504), ball (P501), Jupiter (P516), photon (P513), probe (P522), rendezvous (P514) and orbit (P526). Every source-image reference, size, decoded width/height and logical update tick matches exactly between the old and cached animation paths. Existing trajectory/composition/collision/answer/completion assertions also pass. These verifiers include their documented controlled edge cases and are not a manual natural whole-game playthrough.

Across these cases, **226,301** successful motion-geometry requests require **369** cache-miss decodes; **225,932** repeated geometry decodes are avoided. These counts concern this bounded verifier set. Elapsed times are descriptive only; no FPS or controlled wall-clock speed claim is made.

The same shipping executable passes the complete general native suite and the41scene/2,953query frozen uncached input oracle. Four fresh processes consume the two frozen ASVM26/P504 and ASVM27/P501 files from accepted earlier cleanroom engines, with both initial entry settings, unchanged source files and full-future assertions. They are physical historical engine saves, not original Windows saves. Installed-path oracle and frozen-save continuation pass separately.

The preceding input-cache diagnostic's four positive global-menu checks remain historical evidence; they are not relabeled as fresh executions of this new binary. This delta changes no menu code. No GUI font/config workaround or new save version is introduced.

This real rebuild also removes the sole cosmetic trailing space retained in the preceding validated oracle lambda. The current source export passes strict whitespace checks without the earlier exception. No validated source bytes were silently normalized under the old binary hash.

Fixed acceptance remains7/10 (70%),35 documented bounded native save profiles; whole-game completion remains unmeasured. Required-behavior completeness, exact help typography and a human audiovisual playthrough remain open. Original media, physical saves, executables and toolchain objects are not included in the source export.
