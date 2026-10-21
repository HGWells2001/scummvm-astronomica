# Astronomica v14: completion branch checkpoint (21 October 2026)

Base: main commit 20aa22b8459e443f05a2b9e5fd078a6843933351
Branch: dev/completion-route-audit-20261021

This is a separate development branch. Nothing is merged into main. The v14 puzzle/save code from main is preserved.

## Changes

- Recognize the original English edition (SETUP/ASTROeng.EXE), using the verified 5000-byte executable MD5 14929fa8e52d7e3bc539244413703ecb and original PLACES/GAMEDATA signature. Existing ASTRO.EXE detection remains.
- Correct C++11/MINGW64 initialization ambiguity in DangerAction/ScriptRunner::Action without changing the v14 save payload or intentional puzzle behavior.
- Support locally extracted game_data, custom ASTRO_GAME_PATH and custom ASTRO_SCUMMVM executable without changing the user's existing saves.
- Verify user's own CD ZIP without sharing it. Static audit of 421 scene resources, including P501-P537 and the ending, identifies missing assets and unresolved literal navigation targets; it does not prove routes are traversable.
- Automated Windows x64 compilation and optional prerelease upload, confined to this branch.

## Original ZIP and preview

Release tag (only when a CI build succeeds): https://github.com/HGWells2001/scummvm-astronomica/releases/tag/astronomica-v14-completion-preview

Unpack the preview (or compile this branch with pinned ScummVM). With Python 3 in the same folder and the user's own ASTROeng(3).zip, run:

    py -3 tools\game_archive.py "C:\path\ASTROeng(3).zip" --output game_data
    py -3 tools\completion_audit.py "C:\path\ASTROeng(3).zip" --out completion-audit.json

Then run GIOCA.cmd from the preview, or Avvia-Astronomica.cmd from a source checkout with ASTRO_SCUMMVM set to the actual custom executable.

## Pending acceptance criteria

1. Reproduce P1 startup, audio/video controls, navigation and original interactive state with this exact v14 build and original English CD game data.
2. Solve every mandatory puzzle using the player's own controls, transition through story gates, and see all original ending and postcredits scenes without test-only shortcuts.
3. Verify help/return, save/load and first/repeated-completion counters through real interaction, including remaining unsupported save boundaries.
4. Preserve reproducible scene/transition logs and explicit failures with saved evidence. The historical 114/121 accepted entry-script templates is not a gameplay completion percentage.

No complete real interactive playthrough is claimed. Original copyrighted game media and personal saves remain outside GitHub. Avoid rerunning historical finalizer scripts from main.

## Development checkpoint: native regression harness and normal-play protections

The ScummVM engine now gates developer-only scene skipping (PageUp/PageDown)
and demonstration keys (V/M/R/C/F) behind
`astronomica_debug_controls=true`. The default is off. Original on-screen
click interactions and normal F5 menu / Escape / arrow navigation are unchanged.

The Windows preview now includes `VERIFICA.cmd` and
`tools/verify_gameplay.py`. With your own original English game assets in
`game_data`, double-click `VERIFICA.cmd` to execute five independent
native-core regressions, including story transitions and endings. This uses a
new per-run `astronomica-diagnostics-YYYYMMDD-HHMMSS` directory with separate
configuration, log and save areas. Personal `userdata/astronomica` is never
selected by the test runner.

For more coverage, run:

    py -3 tools/verify_gameplay.py --exe scummvm.exe --game-dir game_data --suite saves
    py -3 tools/verify_gameplay.py --exe scummvm.exe --game-dir game_data --suite av
    py -3 tools/verify_gameplay.py --exe scummvm.exe --game-dir game_data --suite all

The script requires both a zero process exit and a matching PASS marker from
each native test. It stops at the first failure or timeout, retains diagnostic
logs in its private test directory and emits summary.json. No logs, save
files, screenshots or original assets are uploaded automatically. Do not
publish the entire generated diagnostic directory: some native tests can
create image dumps containing original artwork. The operator may share
summary.json and sanitized text logs for bug reproduction.

These checks are **not** a substitute for a real full playthrough. In
particular, test-only scene injection does not prove that a player can
naturally reach every puzzle or cross every story gate. The next phase is
manual P1-to-credits acceptance with failures recorded scene by scene, followed
by implementation of observed blockers. Never infer a global game-completion
percentage from static template acceptance.


## Optional real-play route tracing

To identify the *first actual* blocker during an ordinary playthrough, edit
`userdata/astronomica/astronomica.ini` inside the **player's own extracted
directory** and add under `[astronomica]`:

    astronomica_trace_route=true

Launch `Avvia-Astronomica.cmd` with `ASTRO_TRACE=1` set in the environment,
for example from PowerShell:

    $env:ASTRO_TRACE = "1"
    .\Avvia-Astronomica.cmd

The diagnostic log is `userdata/astronomica/astronomica.log`. Opt-in trace
lines identify startup scene, click coordinates, blocked input, requested
transitions, transitions denied or redirected by original game gates, and
actual loaded destinations. There is **no forced jump** or developer
shortcut in this mode. Keep personal save files private; share sanitized log
lines from the first failure. Turn tracing off by removing the INI key
or setting it to false. (The `ASTRO_TRACE` environment variable alone
only raises debug logging and does not enable route instrumentation.)

## Original mouse cursor integration (21 October 2026)

The branch now contains `original_cursors.h/.cpp`, a runtime loader for the
**actual original Win16 executable's** `RT_CURSOR` and `RT_GROUP_CURSOR`
resources. It uses ScummVM's pinned native `WinResources` and
`Graphics::WinCursorGroup` decoders, so the original bitmap, transparency,
palette, and hot-spot coordinates are retained rather than approximated.
It reads the player's original `SETUP/ASTROeng.EXE` (or `ASTRO.EXE` layout)
locally and **does not package the artwork in GitHub**.

When hovering a static sprite with a serialized original `Sprite.cursor`
identifier, the native cursor is selected by that exact resource ID.
Unsupported/missing IDs revert safely to the classic Windows pointer.
Generic rectangle hotspots are not artificially assigned a cursor ID;
moving sprites and complex interaction regions need further oracle tests.
Scene loads and return from the F5 menu reset the cursor lookup so the
pointer is not stuck with a previous screen's appearance.

The option `astronomica_original_cursors=true` is enabled by default when
the executable's original cursor resources are parseable. To disable it,
add under the user's `[astronomica]` INI section:

    astronomica_original_cursors=false

The native loader logs the count of resource images found, at debug level1:
`Astronomica original cursor resources: N images from original executable`.

**Verification limits:** the unit tests and cross-compiler build only prove
implementation integration. Until the actual original EXE has been examined
and the cursor group IDs and hotspots compared in real interactive play,
do not claim that every original mouse pointer, dynamic context or scene
is fully reproduced.
