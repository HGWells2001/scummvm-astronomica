# Astronomica for ScummVM

Native experimental ScummVM engine for **Astronomica: The Quest for the Edge of the Universe** (Windows, 1994).

This repository contains the engine, original-file research tools, regression drivers and development reports from the work restarted on 13 September 2026. It is a source overlay for the pinned ScummVM revision in [SCUMMVM_BASE.json](SCUMMVM_BASE.json). No original game files, media, user saves, compiler dependencies or executables are included.

## Verified development state

The local Windows x64 build passed its complete WASAPI regression on 21 October 2026. Publishing this source snapshot does not constitute a new build on another machine.

- P524 v6 saves question boundaries, including the running Triton animation and mentor return. Tests cover 72 round trips, 48 animation boundary cases and fresh-process continuation.
- [Measured save coverage](outputs/astronomica-cleanroom/evidence/native-save-coverage.json) records nineteen supported puzzle scenes (P505, P506, P508, P513, P515, P517, P519, P524, P526, P528-P537), plus exploration. This is not a whole-game completion percentage.
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
- Automatically verified routes in 35 puzzle scenes; these include variants, so this is **not** a count of distinct puzzles.
- Navigation, original script execution, puzzle motion, audio, video, mentors, countdown and endings have dedicated checks.
- Native ScummVM saves support settled exploration screens and P505/P508 question boundaries. P519 v5 saves idle selections and partial solutions, with 74 gameplay comparisons, 30 image compositions and fresh-process continuation verified. P505 continuation tests cover 38 boundaries and successor states, hover restoration, corrupt payload rejection and fresh-process slot loading. P508 continuation tests cover 63 boundaries, 291 answer steps and fresh-process slot loading; ambient music restarts from its beginning. Original text `GAMESTAT` import supports exploration with no active countdown.
- The original help file supplies 781 readable articles, 31 pictures in 20 articles, search and tables. Pictures now scroll with their surrounding text. Thirteen original exponent runs use explicit `^(value)` notation.
- PageUp/PageDown/Home/End scroll the native help reader; all 781 articles pass keyboard navigation and boundary checks.
- Help checks cover all articles, image pixels, wheel/drag scrolling and narrow-width/height reflow. Save/import regressions passed on the same executable.

The game is still experimental. Saving during the other puzzles, exact help typography/layout and a complete manual audiovisual playthrough remain outstanding. There is **no measured total completion percentage**; the historical 94.2% refers only to 114 of 121 static entry-script templates.

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
