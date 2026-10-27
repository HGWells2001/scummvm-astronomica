# Astronomica: Windows 11 ISO compatibility installer

This is a **source-only compatibility patch** for the 1994 English Windows 3.1 edition of *Astronomica: The Quest for the Edge of the Universe*. It uses the native, experimental Astronomica engine in this repository rather than launching the 16-bit Windows executable.

**Requirements:** Windows 11 x64, PowerShell 5.1 or later, the original English ISO, and a **custom-built** `scummvm.exe` containing the Astronomica engine. Ordinary official ScummVM releases do not automatically include this experimental private engine. The installer does not compile or download the engine.

## Installation

1. Check out this branch of this repository on the Windows 11 PC.
2. Obtain or build the Windows x64 `scummvm.exe` with the project's Astronomica engine. See [BUILDING.md](../../BUILDING.md). On the development machine, the previously validated output was `work/fresh-20260913/build/Releasex64/scummvm.exe`. **It is not shipped in this repository.**
3. Open PowerShell in the repository root and execute:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\patches\windows11\Install-Astronomica.ps1 -IsoPath "C:\Path\To\Astronomica.iso" -ScummVMExe "C:\Path\To\Custom\scummvm.exe"
```

If the validated development build is already in the workspace, omit `-ScummVMExe`.

4. After success, launch the game by double-clicking:

```text
%LOCALAPPDATA%\Astronomica-Win11\Launch-Astronomica.cmd
```

All copied original game files are kept under `Game\`; settings, saves, and logs remain in the separate install root. The source ISO is not modified. If the script mounted the ISO, it also unmounts it. An ISO previously mounted by the user stays mounted.

## Version integrity

The installer recognizes exactly the English game-data revision in `outputs/astronomica-cleanroom/engine/astronomica/detection.cpp`:

| File | Expected bytes | MD5 of first 5,000 bytes |
| --- | ---: | --- |
| `ASTRO.EXE` | 418376 | `14929fa8e52d7e3bc539244413703ecb` |
| `GAMEDATA` | 1604 | `84099c2580e5c71beec97ca3e52a5967` |

The 5,000-byte MD5 convention matches the default ScummVM advanced detector. Do **not** substitute full-file MD5 for `ASTRO.EXE`. The script searches for these two files side-by-side, copies their containing folder including subdirectories, rechecks the copies, verifies `--list-engines`, then runs native `--detect`.

If the ISO contains only installation archives or a different English revision, it reports that limitation without touching the binaries. Such variants need an additional verified extraction/detection path, not blindly changed hashes.

## Important limitations

* This is **not** a patch that makes the 16-bit original `ASTRO.EXE` itself run on Windows 11.
* It depends on the game's original data and the experimental native engine in this repository.
* The archive supplied in chat has not yet been binary inspected or run in a Windows 11 environment. The exact ISO-specific installation path remains to be confirmed against its contents.
* Existing engine validation covers many scenes and tests, but it is not proof of an uninterrupted, complete audiovisual playthrough.
* No original commercial data, Windows 3.1 binaries, or proprietary media is distributed.

If the ISO is a different version, record the installer's error plus the names and hashes found, and add a separate verified detector entry only after checking format and engine compatibility.

### Alternative for original Win16 behavior

DOSBox-X can run a legally obtained Windows 3.1 installation inside emulation. This is a fallback for investigating missing Win16-specific behavior, not a prerequisite for the native patch. See [DOSBox-X's Windows 3.1 guide](https://dosbox-x.com/wiki/Guide%3AInstalling-Windows-3.1x).
