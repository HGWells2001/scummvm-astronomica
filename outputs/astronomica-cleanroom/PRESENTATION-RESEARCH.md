# Lower-screen presentation, 18 October 2026

Status: corrected and verified, 18 October 2026. See evidence/presentation-validation.json.

The native presentScene() unconditionally fills rows456–479 with black and
draws an EXPERIMENTAL/simple-hotspots diagnostic label. This occurs after
the original scene and sprites have been composed. Consequently the bottom
24 rows of original game content can be overwritten during normal play.

Concrete original resource witness: P528 phase pictures GE_S* are171x105,
committed at (87,356), reaching row460. The overlay intersects five rows,
or855 pixel addresses, of that picture. GE_S1's lower five RGB rows contain
204 nonblack pixels and22 distinct colors. These are original picture data,
not a diagnostic area. Resource identity/dimensions are hashed in
evidence/p528-save-original.json. The native screen is640x480; its source
control panel is composed at the bottom by readImage(...,control=true).

Proposed correction: preserve composed pixels during ordinary presentation;
make the diagnostic strip opt-in through an explicit debug configuration.
Keep movie-frame composition and screen updates. Do not change game input,
the save formats or the original resources as part of this correction.

Required native checks: verify all480 rows survive a normal presentation,
compare the855 affected P528 picture pixels with the original decoded image,
verify the optional overlay still appears when explicitly enabled, and
restore the full original rows after disabling it and recomposing. Run the
existing compatible save, image, movie, help and WASAPI suite on that build.
Existing save thumbnails may show the old label; game state payloads contain
resource/state identities and must remain readable.

This observation is separate from P526 save verification. Finish and publish
that checkpoint before changing presentation, to keep its evidence coherent.


Implemented: ordinary presentation preserves all480 rows. Set astronomica_debug_overlay=true only for the diagnostic strip. Twelve complete scenes,855 original GE_S1 pixels, opt-in display and recovery pass. All compatible saves and the WASAPI suite pass on the same build.
