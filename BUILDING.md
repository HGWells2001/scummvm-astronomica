# Building the ASVM31 engine

Use Python 3 and Git. Upstream ScummVM is pinned to commit `2085bcb368c19bc90f0190efcd56b9d58cd7fb5a`. **ASVM31 requires the reviewed three-file video-core overlay together with all 23 engine files.** Earlier no-core-change instructions describe older versions.

## Prepare the paired sources

From this source repository:

```text
python tools/verify_export.py
python tools/prepare_scummvm.py
```

The second command retrieves the pinned upstream source into `work/fresh-20260913/scummvm`, copies the engine, checks the exact original video-core hashes, and applies the reviewed patch with original-core backups. It downloads no game files or compiler dependencies.

For an existing checkout at the pinned revision, use:

```text
python tools/install_engine.py /path/to/scummvm
```

An already matching engine/core pair is accepted without replacing files. An incompatible core, partial patch, different revision or different existing engine is refused. For upgrading an older engine checkout, use a separate fresh checkout; the installer deliberately does not overwrite local engine changes. Core backups are kept under `.astronomica-core-backups/` in the checkout.

The lower-level `tools/apply_framework_patch.py --root /path/to/scummvm` performs read-only pairing checks. Its `--apply` option requires the complete matching engine to be present first.

## Compile from clean output directories

The changed `VideoDecoder` class layout makes **a full clean rebuild of every ScummVM project mandatory**. Do not reuse old framework objects, static libraries, precompiled headers, engine archives or incremental outputs. Use new build/output directories and regenerate project files from the paired source tree.

Install the dependencies described by the pinned ScummVM build documentation and enable the experimental `astronomica` engine. A supported configure/make environment can use:

```text
./configure --disable-all-engines --enable-engine=astronomica
make -j2
```

This is build guidance, not a claim of Linux/macOS validation. The recorded Windows x64 build used MSVC v145, the Windows SDK and SDL 2.32.6; 410 translation units were compiled freshly (402 framework, seven engine and one detection). On Windows, generate fresh Visual Studio projects with ScummVM's `devtools/create_project` and build all required projects. The recorded local builder has machine-specific dependency paths and is not a portable installation command.

No game data is needed to compile. To play, add your original Astronomica directory in the resulting ScummVM launcher. Runtime resources come directly from those original files.

## Validation and limitations

`tools/verify_export.py` checks the exported source hashes and mandatory source pairing. It does not rerun gameplay tests. `SCUMMVM_BASE.json` identifies the reviewed executable and source hashes; recorded ASVM31 proof JSONs are under `work/fresh-20260913/`. Their local paths and fixture references are provenance, not distributed input files or portable tests.

The Windows executable passed eleven same-binary gates, including the general native suite, six genuine fresh ASVM31 loads, 185 newly serialized recorded-state loads/rewrites, 21 recipient cases, 32 genuine old-save processes v14–30, and real WASAPI audio/timeline checks. The declared PCM restart mapping does not recover the original backend/resampler phase. No new genuine v1–13 fixtures or manual whole-game completion are claimed. See `outputs/astronomica-cleanroom/P523-SAVE-FORMAT.md` for supported boundaries and exact packet semantics.

Earlier research drivers require original game files, local fixtures and machine-specific dependencies. Do not run historical patch-generation/checkpoint scripts as setup; they can replace current sources. The paired canonical engine and core overlay are authoritative. No original game media, compiler dependencies, executables or user saves are distributed in this source repository.
