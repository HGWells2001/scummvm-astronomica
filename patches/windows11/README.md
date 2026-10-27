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

The installer recognizes the supported English game-data revision in `outputs/astronomica-cleanroom/engine/astronomica/detection.cpp` using **two layouts**:

1. **Installed folder:** `ASTRO.EXE` and the **file** `GAMEDATA` are present alongside each other, with the original exact ScummVM detector signatures.
2. **Original CD-root resource folders:** `PLACES` (including `PLACES\P1\MEGAFILE.HYP`) contains the actual assets but there is **no** `GAMEDATA` detector file. A genuine original `ASTRO.EXE` with the recognized signature is required, along with three full-file verified `MEGAFILE.HYP` resource fingerprints. If the executable is elsewhere on the CD, the installer copies the validated executable beside the resource folders in the local destination, leaving the ISO untouched.

**Important:** The second detection entry is new in this branch. You **must recompile** the custom ScummVM engine from these branch sources before `--detect` will recognize the CD-root layout. An older build will still reject it.



| File | Expected bytes | MD5 of first 5,000 bytes |
| --- | ---: | --- |
| `ASTRO.EXE` | 418376 | `14929fa8e52d7e3bc539244413703ecb` |
| `GAMEDATA` | 1604 | `84099c2580e5c71beec97ca3e52a5967` |

For the second layout, the game also needs these unchanged verified files beneath the same `PLACES` directory root:

| File | Expected bytes | Full-file FNV-1a 32-bit |
| --- | ---: | ---: |
| `PLACES/P502/MEGAFILE.HYP` | 669631 | 2443827672 |
| `PLACES/P503/MEGAFILE.HYP` | 782595 | 231093171 |
| `PLACES/P527/MEGAFILE.HYP` | 348102 | 3684137004 |

These fingerprints were already used by the project's experimental engine to validate scene assets. A wrong signature produces a diagnostic report rather than a forced install. The new detector uses the known `ASTRO.EXE` signature, while the installer enforces the stronger resource-file fingerprints, so direct ScummVM imports are less guarded than this installer.

The 5,000-byte MD5 convention matches the default ScummVM advanced detector. Do **not** substitute full-file MD5 for `ASTRO.EXE`. In the installed-folder layout the script searches for these files side-by-side. In the CD-root layout it instead verifies the resource fingerprints. In both cases it copies unchanged source files, verifies the local copy and runs the custom engine's `--detect`.

If the ISO contains only installation archives or a different English revision, it reports that limitation without touching the binaries. Such variants need an additional verified extraction/detection path, not blindly changed hashes.


## When the installer says ASTRO.EXE was found but GAMEDATA was not recognized

**Do not edit the accepted MD5 values to bypass this message.** The installer now supports a validated direct-CD `PLACES` folder layout as well. If detection still fails, your disc might require original setup extraction, a supported `ASTRO.EXE` copied from another directory, or additional validation of an unrecognized game revision. The updated engine recognizes the exact known `ASTRO.EXE` fingerprint without needing a separate `GAMEDATA` file for the CD-root variant.

The updated installer now writes a **read-only** report automatically when detection fails. Find it at:

`%TEMP%\Astronomica-ISO-Diagnostic.txt`

Open the report in Notepad. It lists candidate files with sizes and MD5s of their first 5,000 bytes, the main CD directory entries, and common installer/archives. It does not copy or modify original game data when detection fails.

To produce the report independently after mounting the ISO (for example at `E:\`), open PowerShell in the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\patches\windows11\Diagnose-Astronomica.ps1 -SourceRoot "E:\"
```

Share the report to identify whether the data must be extracted by running the original installer in Windows 3.1/DOSBox-X, reorganized safely, or specifically ported to a different English revision. Because the actual ISO contents have not yet been verified on the development machine, no claim is made that this diagnostic alone repairs an unsupported revision.

## Important limitations

* This is **not** a patch that makes the 16-bit original `ASTRO.EXE` itself run on Windows 11.
* It depends on the game's original data and the experimental native engine in this repository.
* The archive supplied in chat has not yet been binary inspected or run in a Windows 11 environment. The exact ISO-specific installation path remains to be confirmed against its contents.
* Existing engine validation covers many scenes and tests, but it is not proof of an uninterrupted, complete audiovisual playthrough.
* No original commercial data, Windows 3.1 binaries, or proprietary media is distributed.

If the ISO is a different version, record the installer's error plus the names and hashes found; support requires checking actual file formats and engine compatibility, not simply changing the detector.

### Alternative for original Win16 behavior

DOSBox-X can run a legally obtained Windows 3.1 installation inside emulation. This is a fallback for investigating missing Win16-specific behavior, not a prerequisite for the native patch. See [DOSBox-X's Windows 3.1 guide](https://dosbox-x.com/wiki/Guide%3AInstalling-Windows-3.1x).
