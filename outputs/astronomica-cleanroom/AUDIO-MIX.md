Current catalogue: see ALL-SOUND-EFFECTS.md. The scope below is historical.

# Music and puzzle feedback

At the user's request, reviewed feedback effects now overlap continuing music instead of replacing it. An independent Music handle preserves the actual loop and its clock. The primary foreground handle still represents effects or narration for existing readiness checks. Narration stops the music; after narration it resumes under the existing loop policy. Pause freezes the mixer, scene/movie transitions clear the extra handles, and save/load refuse transient effects or a pending handoff without mutating a rejected request.

The catalogue contains eight exact clip identities: four shared feedback clips and four original numeric-control clips. The latter are tied to nine original increment/decrement controls with input lock, arithmetic, clamp, frame update and 200ms release. Clip identity handles different local file numbers. Explicit introductions and blocking clips retain foreground handling. Other clips are not guessed from duration and still use foreground routing. This is an intentional mixing improvement, not original Win16 single-channel parity or a complete speech/effect catalogue.

Native Windows/WASAPI checks cover simultaneous music/feedback, exclusive S1 narration and restart, paused music clock, guarded saves/loads, rejected-load nonmutation, scene cleanup, and real hit-tested P517 plus/minus controls after its original introduction. The exact extended full general suite passes, as do four fresh genuine earlier ASVM29 continuations and installed checks. Independent source comparison finds60 save/load method payloads unchanged after removing only the two new early stream guards. Two additional transient handles change the engine class layout: rebuild all seven engine units. Paired core files remain unchanged.

The workspace engine is qualified. A separate all-engine build against an older GUI framework passed focused audio/help-focus tests but failed a P525 owned-state preparation check in its general suite; it is not installed into the user's portable directory. That failure is retained and must be diagnosed independently. No original media, native fixtures or binaries are distributed.

Fixed acceptance remains7/10; whole-game completion is not measured. Do not forcibly terminate suites. No shutdown is authorized for the current development session.
