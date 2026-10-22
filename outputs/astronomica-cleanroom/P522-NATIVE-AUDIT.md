# P522 native observation audit, 21 October 2026

PASS on an isolated copy of the current real v15 engine, using original game
resources and SDL dummy audio/video. No serializer, format, integration or save
support was added. Canonical23 source files and the main executable stayed
unchanged during build/run, as recorded in candidate-build/proof.json.

Candidate SHA256: `d80a7795370f3813bbb2b1f526121dd91d2f8ea1614ed8adb6581650bc9f79f7`.
Main baseline SHA256: `dbe43465359fff29a4a1931b850f463251120a71c21039e44106e64a1b6ffe7b`.

| Source | BASE canonical SHA256 | Staged SHA256 |
|---|---|---|
| astronomica.cpp | `c7fde521a4bac174ed8cf4108afd1758f7fbf2e7849ef9e35ed2fd4e2bc0b221` | `bebf6e9e86851a9ea10b3869209e37c6daa167310becc650c36478222d838c26` |
| astronomica.h | `2a875ee5800502b5405e1af029128f9490f13a007d27678bda3444b131ffd5d4` | `a2f55ca6a9cd47d6215d4e5ac8b775470125c9407eb1fcb75975d9b6c9641f1f` |
| script.cpp | `194c4d871bdaef66acf41c1216ef9827a7a5022626c05aecde8e51104d0f205f` | `803daf92af27b6ebdd0b9e66a327d695d6001f1d4f3924b1d73f6430bf05415e` |
| script.h | `9881ac6388de44a38fc260161edf78ca962cea59c9eba2b5bfa871b516b205e0` | `9881ac6388de44a38fc260161edf78ca962cea59c9eba2b5bfa871b516b205e0` |
| sprites.cpp | `f2cd13d02e3b950a6036ecd58afc79ce06ee7b50996d254dc5eec339d00a9ca6` | `f2cd13d02e3b950a6036ecd58afc79ce06ee7b50996d254dc5eec339d00a9ca6` |
| sprites.h | `3f6bc9590b49d3cdf06472456b47adbf38615f09146e328b80381f7a8742864b` | `3f6bc9590b49d3cdf06472456b47adbf38615f09146e328b80381f7a8742864b` |

The diagnostic copies the existing verifyP522Puzzle route logic, adding only
observations. It retains the real original-motion fixture checks, all four
selectors, failed1991 launch/recovery, successful1992 launch, already-completed
1994 launch, year2003 expiry and voluntary exit. No gameplay algorithm changes.

There are126 complete observations, each with ProbeMotion calendar/flags,
geometry, two locals, clock, pending/idle/script-idle/click/audio fields, full480-row
screen/background hashes and eighteen27-word sprite records. The JSON contains
all records and5830 actual recurring-poll checks, including832 executions.
All four after-startup observations have pending work and idle/scriptsIdle=false.
Recorded due ages are[210]ms for the original200ms delay.
The30ms step and queued call pass quantize execution; this is not evidence that
the original request itself uses a different period.

Ordinary no-flight phases still advance Earth/Mars, and hidden inactive probe
movement is observed in105 snapshots. Year/armed
edges and flight-state/special-hit transitions are sampled. Expiry2003 is captured
immediately before scene change, since loadPlace resets ProbeMotion afterward.
This confirms that flight-idle is not sufficient for a static or empty-queue save.

Future work needs an explicit trusted recurring-poll continuation/epoch and all
active motion/frame phases, rather than dropping pending work or rerunning setup.
The static original-resource contract remains in p522-research/P522-SAVE-PLAN.md.
No roundtrip, restored successor, rejection atomicity, physical slot, WASAPI or
manual playthrough is proved by these observations.

Reproduce from the workspace root with the bundled Python interpreter:
`work/fresh-20260913/build_probe_audit.py`, then
`work/fresh-20260913/analyze_probe_audit.py`.
The one-time prepare_probe_audit.py intentionally refuses an existing directory.
Source/object/PDB/library/executable/log output stays in p522-audit/candidate-build.
