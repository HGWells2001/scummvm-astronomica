# Original scalar state and random choices, 7 November 2026

The Nov6 control regression supplied comparison results mathematically and replaced all other commands with trace markers. This follow-up executes the original predicate instructions, assignments, additions, bit changes, random ranges and free-bit selection, then compares them with the **real current native ScriptRunner**. It remains a bounded regression rather than a full game execution.

The final scene-metadata comparison is recorded in `work/fresh-20260913/original-scene-scalars-native-nov7/proof.json`. Its controlled fixture contains 936 original nonempty script sequences and 72 explicitly synthetic sequences, with 14,922 test cases. There are 10,316 original command positions, plus 656 synthetic positions. Only commands 31/32/33/39/40/42/45/46 retain their original behavior; the others become trace markers. Their original occurrence counts are respectively 1392/781/37/21/3/477/915/90. No percentage of whole-game semantic coverage is inferred from these counts.

For every case, the native test checks all **200 final scalar words individually**, executed-command and pending counts, the count and FNV order summary of trace actions, and the next random draw. Uniform values, different values for each scope/index, integer limits, inclusive and reversed comparison bounds, bit 0/10/20/30, wraparound additions, single-value and wide random ranges, exhausted masks, and identical source/destination variables are included. Synthetic sequences are test inputs, not recovered game scenes.

The original HYP condition tables are checked directly against their final serialized byte ranges and original file hashes. The final test uses their actual width fields for original scripts; only synthetic scripts use width 31. Initial scalar values are still controlled inputs. This does not reconstruct the prior gameplay history, other metadata fields or global metadata carried across scene transitions.

## Original evidence and modeled boundaries

The unchanged original executable has SHA-256 `c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e`. REA does not support its NE format; the retained fallback uses Capstone **5.0.7** in 16-bit x86 mode. Original reader links and the execution epilogue retain the single most-recent condition pointer. No nested condition stack is introduced.

Original instruction bodies are replayed for predicates at `15:0c70`, assignment at `15:0e99`, bit updates at `15:0f08`, free-bit selection at `15:11a8`, random-range assignment at `15:1508`, and addition at `15:159b`. The bounded ranged-random helper, `1:0b6b` generator and its `1:0b3c` multiplication body are also replayed. This includes the extra random draw consumed when a free-bit mask is exhausted.

Twenty-one original relocations independently establish the imported BC40RTL ordinal 632 (`_pow`), internal `FTOL@` and random-generator call targets. The original data-segment radix is exactly 2.0. The floating helpers are **modeled**, restricted to exactly representable powers for admitted integer bits 0..30 and their exact integer conversion. Their bodies, general x87 behavior and original Windows execution are not claimed. Far-pointer allocation, scalar owners and clock APIs also remain modeled. Delays are normalized to -1; game effects, movies, sounds, scene changes and native custom callbacks remain outside this comparison.

Three deliberately corrupted expectation fixtures must fail independently: one final scalar word, the trace summary, and the next random draw. These failures verify the checks; they are not engine regressions. The fixtures, original disassembly, full operand inventory and native binaries stay local.

## Reproduction

With the original files, accepted cleanroom inventory and recorded Windows build inputs:

```text
python outputs/astronomica-cleanroom/verify_original_random_helpers_nov7.py D:/astro --proof work/fresh-20260913/original-random-helper-relocations-nov7.json
python outputs/astronomica-cleanroom/probe_original_scene_scalars_nov7.py D:/astro work/fresh-20260913/original-branches-nov6/inventory.json --out work/fresh-20260913/original-scene-scalars-nov7
python work/fresh-20260913/run_original_scene_scalars_nov7.py
python work/fresh-20260913/check_scene_scalar_negative_controls_nov7.py
```

Output directories must be new; preserve the accepted receipts. The console helper links the current real engine library and does not replace the game executable. The runtime engine and paired video core are unchanged. Prior complete native gameplay/save gates remain historical evidence for the same installed binary; they are not presented as newly rerun here.

Fixed acceptance stays **7/10 (70%)**, with 35/35 documented bounded save profiles. A03 still needs real gameplay effects, custom/timed branches and reachability; exact help typography and a human full audiovisual playthrough also remain open. Whole-game completion is unmeasured.
