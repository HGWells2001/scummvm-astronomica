# Original resource branch inventory, 6 November 2026

The full numeric operand inventory remains local and is regenerated from the user's originals; the source repository contains the generator, verifier and proof summary. The new inventory rereads the original `D:/astro/PLACES/P*/MEGAFILE.HYP` files and checks every file against the September cleanroom input hashes. It contains structural references and numeric operands; it distributes no bitmap, movie, sound or original text body.

| Measured syntax | Count |
| --- | ---: |
| Original scene files checked | 421 |
| Scenes parsed | 420 |
| Script lists | 936 |
| Commands with exact original offsets | 10,316 |
| Condition-test tokens (opcode 31) | 1,392 |
| Alternative tokens (opcode 45) | 915 |
| Condition-end tokens (opcode 42) | 477 |
| Commands with a positive delay | 1,593 |
| Literal script place operands | 364 |
| Positive navigation references | 760 |
| Opaque resource tails retained by hash | 4 |

These are syntax counts. They are not counts of reachable branches, distinct puzzles, executed outcomes or completed gameplay. Each command starts with `execution_verified=false`. Native custom handlers, callback-generated commands, time-dependent failures and dynamically selected routes need their own evidence map.

`PLACES/P406/MEGAFILE.HYP` is an unchanged 24-byte file that the strict reader cannot finish parsing. Its original SHA-256 is `fcd48d6c1f370a53f62870fb81f0532aeacb5dded8d5a81342538883b5f87cd8`. The current literal navigation and place-operand search finds no incoming reference to P406; that bounded result does not establish that native code cannot select it. The four opaque tails belong to P502, P503, P504 and P533. Their purpose is not inferred from their contents.

The inventory preserves literal condition markers without imposing a nested-if model. The current reconstructed runner uses a single last-condition pointer. An initial stack-based draft was rejected and retained locally; its proposed links are not accepted evidence.

The independent byte verifier checks all 10,316 opcode records, numeric operands, hashed text operands, delay fields, command adjacency and nonempty script terminators directly against the original bytes. It also checks the 421 input hashes and four tail hashes. This validates transcription, not original runtime semantics.

```text
python outputs/astronomica-cleanroom/inventory_original_branches_nov6.py D:/astro --out work/fresh-20260913/original-branches-nov6/inventory.json
python outputs/astronomica-cleanroom/verify_original_branches_nov6.py D:/astro work/fresh-20260913/original-branches-nov6/inventory.json --proof work/fresh-20260913/original-branches-nov6/proof.json
```

The historical 114/121 entry-template metric was measured with animation disabled. All seven rejects occur in four scene cohorts: P514 (two), P516 (one), P518 (one), and P522 (three). They must be distinguished from missing game behavior. A separate native startup-admission matrix checks those same cohorts with animation enabled and disabled; its receipt `original-entry-admission-nov6/proof.json` passed: 18/18 admitted with animation enabled, 11/18 with it disabled, in eight bounded native observations. Admission alone does not demonstrate execution of every conditional branch.

Fixed acceptance gate A03 remains open. Its completion requires a versioned behavioral inventory and an evidence mapping for required alternative, failure and timed outcomes, including native behavior outside these resource scripts. Whole-game completion remains unmeasured.
