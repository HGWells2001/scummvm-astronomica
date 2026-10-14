# Building the engine

Use Python 3 and Git. The engine is pinned to upstream ScummVM commit `2085bcb368c19bc90f0190efcd56b9d58cd7fb5a`; no ScummVM core changes were required in the validated checkout.

## Source preparation

From the repository root:

```text
python tools/verify_export.py
python tools/prepare_scummvm.py
```

The default destination is `work/fresh-20260913/scummvm`. To install into an existing checkout at that revision, use:

```text
python tools/install_engine.py /path/to/scummvm
```

Installation is idempotent when files match. A different existing engine directory is rejected, so local modifications cannot be silently replaced.

## Compile

Follow the build instructions shipped with the pinned ScummVM source to install dependencies for your platform. Enable `astronomica`, which is experimental and disabled by default.

For a supported configure/make environment, from the ScummVM checkout:

```text
./configure --disable-all-engines --enable-engine=astronomica
make -j2
```

This command is build guidance, **not a claim that this snapshot was tested on Linux/macOS**. The recorded build used Windows x64, MSVC v145, the Windows SDK and SDL 2.32.6. On Windows, use ScummVM's `devtools/create_project` with the installed Visual Studio toolchain and enable the same engine. The archived `build.py` and `build_project_tool.py` assume the original machine's compiler paths and are not portable setup scripts.

No game data is required to compile. To run, add your legally obtained original Astronomica directory to the resulting ScummVM launcher. Runtime decoding reads the original resources directly; the research JSON files are not runtime dependencies.

## Validation

`tools/verify_export.py` checks hashes of the exported source snapshot and all native engine files. It does not claim to rerun gameplay tests.

The recorded runtime evidence is in `outputs/astronomica-cleanroom/evidence/`. The latest executable hash is in `SCUMMVM_BASE.json` and `evidence/development-validation.json`; the older `build-provenance.json` is historical.

Original runtime drivers include `check_help.py`, `check_saves.py`, `check_legacy.py` and `runtime_test.py --real-audio`. They expect the original workspace layout, game files at `D:/astro`, a local build in `work/fresh-20260913/build/Releasex64/`, and local font dependencies. Review paths before running elsewhere. Use a real audio backend for timing-sensitive playback: SDL dummy audio was previously shown to produce a clock artifact.

Research tools require Python packages such as Capstone and Pillow; the recorded Capstone version was 5.0.9. Some early tools explicitly add `work/fresh-20260913/deps` to the module search path. These tools inspect local originals, which are not distributed here. Extracted help text/format/image corpora can be regenerated using the corresponding `probe_help_*` tools in dependency order (directory, compression, navigation/format, images).

Do not run historical patch-generation or checkpoint-finalization scripts as setup. They are preserved for provenance and may replace current files or expect excluded local artifacts.
