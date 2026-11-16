# Audio mixing work in progress

Development stopped at the user's request. The installed and accepted engine remains the startup-logo release on main (02ce784). This branch preserves unfinished source changes, not a production audio release.

Requested behavior: shared feedback effects should overlap continuing music; narration may silence it. Candidate D uses an independent Music handle and retains the primary foreground handle for existing save/readiness rules. Four exact shared feedback clip fingerprints are recognized across different scene-local file numbers. An inventory found 153 matching files; blocking sounds and explicit introduction files retain foreground routing. Other clips are not classified as effects merely from their duration.

Native targeted tests pass for feedback overlap with retained music, exclusive narration followed by music restart, pause, rejected-load nonmutation and scene cleanup. Seven engine units were freshly compiled. Candidate D SHA256 e8eb0c621251a742c701a1c562326b574b0a773868d757904b506f037a5a5b25.

The full general suite finished naturally with PASS on 16 November 2026 at 23:52 CET. Its exact candidate-bound receipt is included. Save payloads have not intentionally changed; additional installation, portable-framework and clip-role coverage work remains. No candidate was installed into the project launcher or the user's all-engine portable installation. No game assets or binaries are included. Main remains the accepted production source.

After the existing suites finish, the user requested normal computer shutdown without forcibly terminating suites or programs. This is a one-session request, not a standing future shutdown policy.
