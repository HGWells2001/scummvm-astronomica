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
