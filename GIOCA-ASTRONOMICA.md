# Astronomica: prepare original files and launch (English edition)

This project is an experimental ScummVM engine. The launcher is **not** a substitute for building ScummVM with this engine enabled. The game files are not included in this repository.

## One-command local build and play (no GitHub artifact required)

On Windows 10/11, download this repository branch and open PowerShell in its root directory. You can compile and launch using your original English CD ZIP:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Build-e-Gioca.ps1 -Archivio "C:\Users\YOU\Downloads\ASTROeng(3).zip"
```

The script installs MSYS2 through `winget` if missing, updates the MSYS2 environment, downloads the pinned ScummVM source, builds the native Astronomica engine using MinGW-w64, verifies its registration, safely extracts your original ZIP into ignored `game_data`, and launches the game. The first MSYS2 upgrade can require closing any running MSYS2 windows and running the command again.

To compile without launching or extracting game data, add `-SoloCompila`. This route does not depend on GitHub Actions artifact or release-upload permissions.

## Windows x64 precompiled preview

If GitHub has permission to publish releases, download the ZIP from the [Astronomica Windows preview release](https://github.com/HGWells2001/scummvm-astronomica/releases/tag/astronomica-windows-preview) and extract it into a new directory. That link will not have an asset if the repository's Actions token lacks release-write permission. Use the local-build method above in that case. The ZIP contains the experimental ScummVM binary and the required DLLs but **no original game files**.

With Python 3 installed, open PowerShell in that extracted directory:

```powershell
py -3 tools\game_archive.py "C:\Users\YOU\Downloads\ASTROeng.zip" --output game_data
```

Then double-click `GIOCA.cmd`. Your original `ASTROeng.zip` is not modified. Saves and settings remain in `userdata\astronomica` alongside the player.

The Windows preview is compiled automatically. Successful compilation and engine registration do **not** prove that the whole adventure is playable start-to-finish. The game's original audiovisual content still requires manual testing on Windows.

## 1. Validate the original archive

From the repository root, run with Python 3:

```powershell
py -3 tools\game_archive.py "C:\Users\YOU\Downloads\ASTROeng.zip" --verify-only
```

The tool checks the `PLACES/GAMEDATA` signature, the 5,000-byte executable prefix and original ZIP CRCs. It **does not run any installer**. The tested English archive has 1,607 files, 423,388,486 uncompressed bytes and `SETUP/ASTROeng.EXE` (418,376 bytes).

## 2. Extract safely

```powershell
py -3 tools\game_archive.py "C:\Users\YOU\Downloads\ASTROeng.zip" --output game_data
```

`game_data` must not already exist; existing files are never overwritten. The tool copies `ASTROeng.EXE` to the root of the game data folder to simplify detection; the original in `SETUP/` remains untouched. Do not commit the extracted files, original media or executables.

## 3. Compile the custom engine

See [BUILDING.md](BUILDING.md) for pinning the ScummVM source and installing the engine into the correct checkout. The command `python tools/prepare_scummvm.py` does **not** compile the engine or install compiler dependencies. A standard precompiled ScummVM executable will not know this experimental engine.

The currently documented local Windows x64 executable location is:

```text
work\fresh-20260913\build\Releasex64\scummvm.exe
```

If your custom executable is elsewhere, launch in a terminal using:

```powershell
$env:ASTRO_SCUMMVM = "C:\path\to\your\custom\scummvm.exe"
.\Avvia-Astronomica.cmd
```

## 4. Play

Double-click `Avvia-Astronomica.cmd`. It searches for `game_data` next to the repository first, then `D:\astro` for older installations. To use another original-files directory:

```powershell
$env:ASTRO_GAME_PATH = "E:\Games\Astronomica"
.\Avvia-Astronomica.cmd
```

Save files and personal preferences are kept under `userdata\astronomica\`. The launcher passes `--path` to ScummVM instead of relying on the historical `D:/astro` path in the template. The English CD archive can now be matched by the detector's exact executable prefix and file-size signature.

## What is and is not verified

The supplied archive has been inspected and successfully unpacked without running original programs. This validates installation inputs only. The existing repository records Windows x64 engine builds and many automated puzzle regressions, and the GitHub Windows x64 workflow now compiles and links the patched engine successfully. A full audiovisual completion test has not yet been performed for this patch. The game remains experimental.
