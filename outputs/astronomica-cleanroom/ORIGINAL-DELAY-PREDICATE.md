# Original pending-delay comparison, 6 November 2026

The unchanged original Win16 scheduler's due/not-due predicate was compared with the real native `ScriptRunner` queue/tick implementation. All **83 distinct original delay values**, representing **1,593 positive-delay command occurrences**, passed **3,290 controlled clock cases**. Native aggregate: `6eaf8f86`.

The reference replays the original instructions at `15:1b7e–1ba1` from `ASTRO.EXE`, SHA-256 `c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e`, using Capstone 5.0.7 in explicit 16-bit mode. It interprets the original zero-delay shortcut, 32-bit subtraction and signed comparison/branch. The clock and command fields are controlled inputs; the original Windows program is not run.

Cases include values immediately around each delay boundary, several starting epochs, wraparound, and the signed half-range. They check the original arithmetic policy, not whether those clocks occur during ordinary gameplay. The native test also verifies that a newly queued zero-delay continuation waits until the next queue pass. Original instructions at `15:1b40` and `15:1c65` independently show that the pending loop uses a captured initial count.

The comparison is a console regression linked with the real current engine library. Its command produces a trace action through the public queue/tick API; no sound handler or original game effect is invoked. The installed executable, original files, core and personal saves remain unchanged. Queue ownership, cancellation, callbacks and complete timed gameplay remain separate requirements. This does not complete acceptance A03 or establish a whole-game completion percentage.

```text
python outputs/astronomica-cleanroom/probe_original_delay_predicate_nov6.py D:/astro work/fresh-20260913/original-branches-nov6/inventory.json --out work/fresh-20260913/original-delay-oracle-nov6
python work/fresh-20260913/run_original_delay_nov6.py
```

These research commands require the original syntax inventory, local Capstone package, recorded Windows compiler and verified local build objects. They are not portable installation commands. Binary fixtures and original disassembly remain local; source code and proof summaries are published.
