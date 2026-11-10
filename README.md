# Current update: respect script locks for keyboard navigation

Verified executable: `dc4fece462ed23df8c6b027935b7961f1dea3806a5325ae52044705694567214`. P27 lock bypass fixed; diagnostic letter/scene cycling shortcuts default off. Complete general suite and installed keyboard checks pass. See [verified scope](outputs/astronomica-cleanroom/PLAYER-KEYBOARD.md). Fixed acceptance7/10 (70%); whole-game completion unmeasured. Original assets and excluded attempts remain excluded.

---

# Current update: reuse dimensions during animation (10 November2026)

The real engine now reuses decoded dimensions in its motion loop as well as input hit testing, preserving original trajectories/collisions and drawing. [Verified scope](outputs/astronomica-cleanroom/MOTION-GEOMETRY-CACHE.md).

Verified executable: `576bbfc9739ac89ecc9c9b92fcaed52579d722e119771463bedaac26c6d6f01f`. Seven old/new puzzle-animation traces match exactly; 226,301 requests need 369 geometry decodes in these cases. Complete general suite, old ASVM26/27 futures and installed-path checks pass. Only astronomica.cpp changes relative to the preceding cache; headers/core/save layouts stay unchanged. Seven fresh engine units plus403 verified foundation objects; clean full source rebuild required.

Fixed acceptance remains **7/10 (70%)**; whole-game completion remains unmeasured. Historical updates follow.

---

# Current update: cache decoded click dimensions (10 November2026)

The real engine now reuses decoded image dimensions during input hit testing, preserving the original rectangles, hidden input regions and frame checks. [Verified scope and limits](outputs/astronomica-cleanroom/HIT-GEOMETRY-CACHE.md).

Verified local executable: `fb8238c96dff7c815039006979f06bf71bfa065c05cf6530109b40553405fdaa`. The41scene/2,953query old/new oracle, unchanged8node/120edge P536 graph, actual menu checks, full general suite, twelve genuine ASVM32 continuations and installed-path checks pass. Seven fresh engine units plus403 verified foundation objects; header layout changed, clean complete rebuild required. No new save version or video-core change.

Fixed acceptance remains **7/10 (70%)**; whole-game completion remains unmeasured. Historical updates follow.

---

# Current update: retained P281 rounds (10 November 2026)

Native saving now works at the idle gateway after leaving an unfinished variant puzzle. It preserves the visited variants and random state across restart. Active gateway actions still require waiting. [Verified scope and remaining limits](outputs/astronomica-cleanroom/P281-RETAINED-SAVES.md).

Exact locally verified executable: `1927d9cd4c09ddc8d125cf8cf2d1bd1873908435bfe659b9e1c9fd7c96e6b255`. Six physical files/twelve fresh continuations, atomic rejection checks, unchanged round0 ASVM2, general native suite and installed-path smoke passed. Seven fresh engine units plus403 verified foundation objects; full source installation needs a clean rebuild.

Fixed acceptance remains **7/10 (70%)**; **whole-game completion remains unmeasured**. Historical updates follow.

---

# Current update: P512 weather voice ordering (10 November 2026)

The weather puzzle now updates its answer result after a synchronous error voice returns, matching the original instructions. Previously the callback saw an already-cleared result. Sound selection, final answer result, video core and save layouts are unchanged. See [the original comparison and verified scope](outputs/astronomica-cleanroom/WEATHER-VOICE-ORDER.md).

The exact installed executable4468c9063a7b8e07c57fb15a29fb9ac186688719e2795cd6ab4f7a529ea1f100 passes the general native suite, genuine old-main ASVM29 continuation and installed-path smoke. Its verified engine library also passes61,648 original-instruction cases/123,296 sound modes and three negative controls. A separate actual-movie/voice comparison confirms the old/new ordering with exact shared ScriptRunner sources. Only script.cpp and the permanent conditions regression change; headers/core remain paired and unchanged. Local build scope is three fresh current units plus407 hash-verified foundation objects. Source installation still requires a full clean rebuild.

[Original completion effects](outputs/astronomica-cleanroom/ORIGINAL-COMPLETION-EFFECTS.md) additionally records600 calls and44 actual voices on the pre-weather-fix real engine, without relabeling that historical receipt as a run of the later binary.

Fixed acceptance remains **7/10 (70%)**, with **35/35 documented bounded save profiles**. Whole-game completion remains unmeasured. Historical versions follow.

---

# Current update: builder selection masks (9 November 2026)

Builder saves now reject component-selection masks that the original P515/P536 scripts cannot produce. Exhaustive public-codec checks cover 49 invalid masks, 49 zero-byte writer refusals and 15 positive component masks. Early Launch, P536 initial project 2 and all existing project ranges are preserved. The general native suite, a genuine previous-main ASVM13 continuation and installed-path smoke pass on executable 51ae19ca62b3b3cdbe24245069c84ae3351c040e19b3217cf28ead99b44f4943. See [the guard and compatibility scope](outputs/astronomica-cleanroom/BUILDER-SELECTION-MASK-GUARD.md).

Only astronomica.cpp changes; headers, paired video core and ASVM layouts are unchanged. Local build scope is one fresh engine unit and 409 hash-verified foundation objects. Source installation still requires the paired core and a full clean build.

[Original queues and live predicates](outputs/astronomica-cleanroom/ORIGINAL-QUEUES-AND-LIVE-BRANCHES.md) adds 630 controlled queue cases/9,450 ticks and 1,308 live native predicate comparisons with original instruction bodies. Effects and timing assumptions are explicit. These checks do not execute the original Windows application or certify every gameplay branch.

Fixed acceptance remains **7/10 (70%)**, with **35/35 documented bounded save profiles**. Whole-game completion remains unmeasured. The notes below retain their historical versions.

Additional source verification: [timed scalar queues](outputs/astronomica-cleanroom/ORIGINAL-SCALAR-QUEUES.md) passes810cases/12,150ticks and3independent negative controls. [General native predicate observations](outputs/astronomica-cleanroom/GENERAL-NATIVE-CONDITIONS.md) conservatively maps completed native traces back to original instructions, explicitly excluding ambiguous signatures. Runtime sources remain unchanged.

---

# Current update: ordinary-launcher opening restored (6 November 2026)

Starting the game from ScummVM's launcher now selects an advertised lossless RGB format instead of inheriting the launcher's first 16-bit format. The original menu, opening movie, credit cards and natural P27arrival were observed in a separate profile. User preferences and personal saves were preserved. The change is limited to output-format selection; ASVM31 packets, gameplay and video-core layout are unchanged.

The exact Windows executable 89fdd9016b3c38e17f12835a65c7516a88ac2918112c415391aa340e1d94ac41 passed all eleven native gates again, including the general suite, six fresh ASVM31 loads, 185 recorded-state replays, 21 recipient cases, 32 genuine prior-save processes v14ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ30, real WASAPI gates and P281. Installed-path smoke also passed. Build scope is one recompiled engine unit plus 409 hash-verified objects from the full 410-unit f286base; no new full rebuild is claimed for this one-file delta. Source installation still requires the paired core and a full clean build.

The fixed acceptance index is **7/10 (70%)**, with **35/35 inventoried route scenes** supporting documented useful save boundaries. These are different measures; whole-game completion remains unmeasured. Original branch inventory, exact help typography and a human audiovisual playthrough remain open. Keyboard delivery in the automated UI checks is still unverified.

[Original branch inventory](outputs/astronomica-cleanroom/ORIGINAL-BRANCH-INVENTORY.md) now records 420 parsed scenes and 10,316 commands from 421 original files. Independent byte checks pass. Eight native startup observations classify the historical seven static rejects: the four affected cohorts admit 18/18 scripts with animation enabled versus 11/18 disabled. Admission is not proof of all branch outcomes. The complete operand inventory remains local and can be regenerated from the user's originals.

Additional source regressions: [original conditional control](outputs/astronomica-cleanroom/ORIGINAL-CONDITION-CONTROL.md) passes 936 reduced sequences in 5,997 controlled cases; [original delay arithmetic](outputs/astronomica-cleanroom/ORIGINAL-DELAY-PREDICATE.md) passes 3,290 cases across all 83 distinct delay values. Both compare original bounded instruction replays with the real native ScriptRunner. Effects/time assumptions remain explicit; A03 is still partial and the fixed index remains 70%. The runtime engine is unchanged from the RGB-opening revision.

Further original-source regression: [scalar state and random choices](outputs/astronomica-cleanroom/ORIGINAL-SCALAR-STATE.md) compares original instruction bodies with the real native ScriptRunner in 14,922 controlled cases: 936 original sequences plus 72 synthetic sequences. All 200 final scalar words, queue counts, trace summaries and the next random draw match; original scene width tables are byte-verified. Three deliberate expectation corruptions are rejected. Runtime engine/core are unchanged, A03 remains partial and fixed acceptance remains 70%.

---

# Current update: P523 ASVM31 (6 November 2026)

Native saves now cover **35/35 inventoried route scenes**, each within its documented useful-boundary scope. P523 retains the active movie timeline and resumes from physical saves in fresh processes. See [the exact ASVM31 contract](outputs/astronomica-cleanroom/P523-SAVE-FORMAT.md). This is not a whole-game completion percentage.

**Build requirement changed:** install the paired three-file video-core overlay with the 23 engine files and perform a full clean rebuild. The current preparation tools apply and verify that pair. Read [BUILDING.md](BUILDING.md); old no-core-change statements below describe earlier versions.

The reviewed Windows executable f286eece070cd192fe90855ff48b0fe9953e63fda89f4592b3a23a1a58d51182 was freshly built from 410 translation units. Eleven same-binary gates passed, including six fresh ASVM31 loads, 185 recorded-state loads/rewrites, 21 active recipient cases, 32 genuine prior-save processes (v14ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ30), the general suite, and real WASAPI movie-clock/audio gates. The 185 packets are newly encoded recorded native states, not historical ASVM31 save files. Original mixer/resampler phase is not recovered. No new genuine v1ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ13 compatibility claim is made.

Source publication is independently checked before and after pushing. Current manual audiovisual playthrough, exhaustive original-branch inventory and exact help typography remain outstanding. Historical reports below retain their producing versions and limitations.

---

# Current update: P525 ASVM30 (4 November 2026)

Native save coverage: **34/35 route scenes (97.1%)**, with P523 outstanding. See [P525 save contract and verified limits](outputs/astronomica-cleanroom/P525-SAVE-FORMAT.md). The historical notes below retain their original scope; whole-game completion remains unmeasured.

# Astronomica for ScummVM

Native experimental ScummVM engine for **Astronomica: The Quest for the Edge of the Universe** (Windows, 1994).

This repository contains the engine, original-file research tools, regression drivers and development reports from the work restarted on 13 September 2026. It is a source overlay for the pinned ScummVM revision in [SCUMMVM_BASE.json](SCUMMVM_BASE.json). No original game files, media, user saves, compiler dependencies or executables are included.

## Verified development state

The local Windows x64 build passed its complete WASAPI regression on 25 October 2026. Publishing this source snapshot does not constitute a new build on another machine.

- P524 v6 saves question boundaries, including the running Triton animation and mentor return. Tests cover 72 round trips, 48 animation boundary cases and fresh-process continuation.
- [Measured save coverage](outputs/astronomica-cleanroom/evidence/native-save-coverage.json) records thirty-three supported puzzle scenes (P501-P506, P508-P519, P521, P522, P524, P526-P537), plus exploration. This is not a whole-game completion percentage.
- P526 v7 saves stopped orbital experiments, retaining animation phases, render positions and hover. 686 round trips include 216 animation cases and 432 synthetic phase/answer comparisons.
- Ordinary presentation preserves all 640x480 original pixels. The diagnostic strip is opt-in; twelve complete-scene checks and 855 original P528 picture pixels pass.
- Looping WAVs follow the Music control; foreground WAVs retain Effects. Six scenes pass with Music muted at volume zero, original controls restored and twelve WAV hashes unchanged.
- P528 v8 retains partial eclipses and original image history; 160 reachable abstract states, 640 continuations, full480-row pixels and fresh-process completion pass.
- The workspace entry point [Avvia-Astronomica.cmd](Avvia-Astronomica.cmd) uses the current local build and keeps personal preferences/saves separate from verification slots. The default template passes normal P1 startup; see [local play](outputs/astronomica-cleanroom/LOCAL-PLAY.md).
- P530 v9 preserves partial component assembly, the prior-round picture, RNG and the original unchanged completion counter; five scenarios per round and all25 pictures pass native continuation tests.
- Six-scene custom17 v10 saves retain partial solutions and original process statics across random rounds and exit/reentry. Every scene passes at all four stages; one family slot resumes in a fresh process.
- Retained unknown locals from earlier scenes no longer block P524/P526/P528/P530 saves. Four original P509 entries, twelve inert-value extremes and eight invalid-metadata rejections pass with v6-v9 layouts unchanged.
- P513 v11 saves settled photon experiments and question progress, retaining hidden photon endpoints, old digits and cube image. Tests cover 728 round trips, 126 answer continuations, two changes during flight, and fresh-process silent completion.
- P517 v12 retains active aurora cycles, stopped phases and timers, original pictures and controls. All14 settings,2240 animation cases, first/repeated completion and slot11 in a fresh process pass.
- Builder v13 retains construction in P515/P536, all five designs and a dormant custom17 sequence. Early Launch, first/repeated completion, P515 no-op and partial P536 slot12 in a fresh process pass.
- Rocket v14 preserves settled P537 selectors, prior failed-launch digits/gauges, stopped motion epoch and dormant custom17 state. All16 selectors, first/repeated success and fresh-process slot13 pass.
- Universe v15 retains P529 selectors, original movie frame and digit history, mask, comet and dormant custom17 state. Original253 movie frames, a fresh-process slot14 and compatibility with older save versions pass.
- Probe v16 preserves ordinary nonflight and failed-return P522 boundaries, active orbit/calendar phases and the trusted200ms poll epoch; active flight remains excluded. Fresh-process continuation and older save compatibility are verified.
- Rendezvous v17 retains live P514 orbit and fuel phases, speed settings and hidden docking-attempt history at settled script boundaries. Fresh-process continuation and frozen v16 save compatibility are verified.
- Planets v18 preserves P518 idle-script boundaries with following and released planets, random selection state and hidden failed-attempt history. Fresh-process continuation and frozen v17 compatibility are verified.
- P521 v19 retains the displayed external image, hidden fragment history, animation/timer phases and inherited state at idle-script boundaries. Fresh-process continuation and frozen v18 compatibility are verified.
- P509 v20 preserves the trusted original pending narrator at index3, ordinary sky identity and hidden bounce state. Other queued work and active foreground audio remain excluded. Fresh-process continuation and genuine frozen v19 compatibility pass.
- P511 v21 preserves retained cloud images, independent selected frame/range history and active animation epochs at idle-script boundaries. Fresh-process continuation and genuine frozen v20 compatibility pass.
- P516 v22 preserves restricted quiet local2=0 boundaries with active orbits and a hidden stopped projectile. Active flight, unproved aborted history, stopped moons, foreground audio and queued/success transitions remain excluded. Fresh-process continuation and unchanged genuine frozen v21 compatibility pass.
- P527 v23 preserves quiet stopped-movie boundaries, independent selected button, seen mask and committed movie sample. All1105original samples compare equal between sequential decoding and seeking. Fresh-process continuation and genuine frozen v22 compatibility pass.
- P502 v24 preserves quiet nonflight choices and hidden stopped failed comet/explosion history, all605runner words and dormant Jupiter geometry. Active flight, foreground audio and queued work remain excluded. Fresh-process continuation and genuine frozen v23 compatibility pass.
- P503 v25 preserves quiet choices, never-solved failures and healthy partial orbit pairs with independent frames and motion epochs. All30 proper partial masks and fresh-process continuation pass. Primary ascent, solved-target failed relaunch histories, full solution transitions and foreground audio remain excluded.
- P504 v26 preserves healthy partial orbits and never-solved stopped failures with literal original pending poll index0/10 and independent partner frames/epochs. Other pending phases/work, ascent, stale solved-target failed relaunch histories and completion remain excluded. Fresh-process continuation and genuine frozen v25 compatibility pass.
- P501 v27 preserves stopped ready-to-pitch states, the original pending poll at index0/7, seven background identities and retained sprite/private ball history. Active pitches, generated cleanup work, foreground audio and completion remain excluded. Fresh-process continuation and genuine frozen v26 compatibility pass.
- P510 v28 preserves the sole original countdown at program1/index6, independent media frames and literal sprites. Native WASAPI, nested pause restoration, 4540 truncations and byte corruptions, fresh physical slot loading, metadata listing and genuine frozen v27 compatibility pass. Foreground voice, hints, unrelated pending work and unsupported media lag remain excluded.
- P512 v29 saves stopped-ready original questions with independent media clock/current/presented frames, all64 sprites and original S0 Music restoration. All six normal scenarios, first/repeated final questions in fresh processes, nested engine pauses, malformed atomic refusal and both genuine v28 loop identities pass on the same WASAPI build. Active movies, foreground voices and pending work remain excluded; Music restarts from its beginning.
- P281 original gateway now admits its original delayed custom17 voice button. Actual solved and unsolved returns preserve the process round/mask, idle v2 saves retain the restored gateway, and pending/nonzero-round saves refuse before writing. The original third-round unsolved-exit completion remains unchanged. Full inherited native checks and all three genuine v29 slots pass.
- Automatically verified routes in 35 puzzle scenes; these include variants, so this is **not** a count of distinct puzzles.
- Navigation, original script execution, puzzle motion, audio, video, mentors, countdown and endings have dedicated checks.
- Native ScummVM saves support settled exploration screens and P505/P508 question boundaries. P519 v5 saves idle selections and partial solutions, with 74 gameplay comparisons, 30 image compositions and fresh-process continuation verified. P505 continuation tests cover 38 boundaries and successor states, hover restoration, corrupt payload rejection and fresh-process slot loading. P508 continuation tests cover 63 boundaries, 291 answer steps and fresh-process slot loading; ambient music restarts from its beginning. Original text `GAMESTAT` import supports exploration with no active countdown.
- The original help file supplies 781 readable articles, 31 pictures in 20 articles, search and tables. Pictures now scroll with their surrounding text. Thirteen original exponent runs use explicit `^(value)` notation.
- PageUp/PageDown/Home/End scroll the native help reader; all 781 articles pass keyboard navigation and boundary checks.
- Help checks cover all articles, image pixels, wheel/drag scrolling and narrow-width/height reflow. Save/import regressions passed on the same executable.

The game is still experimental. Native saves have documented scene-specific boundaries; arbitrary-instant saving, exact help typography/layout and a complete manual audiovisual playthrough remain outstanding. There is **no measured total completion percentage**; the historical 94.2% refers only to 114 of 121 static entry-script templates.

## Build and use

See [BUILDING.md](BUILDING.md). You need your own original game files and a ScummVM build environment.

```text
python tools/verify_export.py
python tools/prepare_scummvm.py
```

The second command retrieves the pinned upstream source and installs this engine. It does not download the game or compiler dependencies.

## Repository layout

- `outputs/astronomica-cleanroom/engine/astronomica/`: canonical native engine sources.
- `outputs/astronomica-cleanroom/`: research tools, format descriptions and development notes.
- `outputs/astronomica-cleanroom/evidence/`: recorded reference comparisons and runtime reports.
- `work/fresh-20260913/*.py`: original local development and test drivers.
- `tools/`: portable source-export verification and installation helpers.

Start with [NEXT-STEPS.md](outputs/astronomica-cleanroom/NEXT-STEPS.md) and [HELP-RESEARCH.md](outputs/astronomica-cleanroom/HELP-RESEARCH.md). Older notes are retained as history. Old `implement_*`, `record_*`, `finish_*` and numbered revision scripts are **not an installation sequence** and may overwrite later work; do not run them indiscriminately. The current engine directory is authoritative, not historical patches embedded in scripts.

[EXPORT-NOTES.json](EXPORT-NOTES.json) lists excluded derived game content. Some historical manifests reference those local-only files; [tools/verify_export.py](tools/verify_export.py) validates this exported snapshot without needing the game.

## License

Engine sources carry `GPL-3.0-or-later` identifiers. See [COPYING](COPYING). Original game content remains the property of its respective rights holders. This is an independent experimental project, not an official ScummVM release.
