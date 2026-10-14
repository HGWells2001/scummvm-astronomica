# GitHub publication, 14 October 2026

Repository: https://github.com/HGWells2001/scummvm-astronomica

Visibility: private. Default branch: main.

Initial published commit: 0302884389c38c18274d98ba86e18644fbc3177c

Local publication checkout: `publish/scummvm-astronomica` relative to the workspace root. It is separate from the canonical engine and the ScummVM build checkout. The workspace root itself is not a Git repository.

The initial commit contains 514 files: native engine, authored research scripts, development/test drivers, reports, GPL license and portable source installation/verification helpers. The full upstream ScummVM tree is pinned by commit rather than duplicated. Game media, original executables, user saves, local configuration, toolchains and extracted full help corpora are excluded and described by EXPORT-NOTES.json.

Validation: the exported 23 engine files match the verified development manifest. A fresh local Git clone passed the 513-file source manifest check. The remote main commit was read back and matches the local commit. Repository visibility was read back as PRIVATE. The original full development checkpoint verification also passed after publication.

For future updates, first finish and verify canonical development. Then copy only intended source/research/report changes into the publication checkout, update SCUMMVM_BASE.json if engine hashes change, regenerate SOURCE-MANIFEST.json excluding .git, __pycache__ and the manifest itself, and verify a clean clone before pushing. Preserve .gitattributes byte-exact handling so the recorded source hashes remain portable. Do not blindly add the workspace root or copied game assets.

Update workflow: work/fresh-20260913/update_github_export.py refreshes the reviewed allowlist after verifying the canonical checkpoint. It adds only explicitly named new source/document files. Run tools/verify_export.py, review and commit, verify the local clone, then push and compare the remote main SHA. Current development checkpoint is recorded by NEXT-STEPS.md and evidence/development-validation.json; use Git history for the latest publication SHA.
