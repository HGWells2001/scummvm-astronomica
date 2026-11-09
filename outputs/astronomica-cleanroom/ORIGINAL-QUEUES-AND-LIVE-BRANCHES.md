# Original queues and observed native branches, 9 November 2026

The new bounded queue replay executes original command-copy, pending-list, dispatch-wrapper and control instructions, including calls to other script templates. It compares with the real native `ScriptRunner` while preserving the original delays. Non-scalar game effects remain timed trace markers in this particular comparison.

The initial comparison passes 70 cases and 840 ticks. The expanded comparison passes **630 cases and 9,450 ticks**, with initial queue sizes 1/2/3 and clock epochs 100, `0x7ffffff0` and `0xfffffff0`. It checks executed counts, pending counts, trace summaries and all 200 scalar words at every tick. Allocation, freeing and clock API results are modeled; this is not original Windows execution or a complete native-effects replay.

Separately, temporary logging candidates of the actual engine exercised original-asset builder, ending, transition, game-state and P510 startup paths. The logged predicates map back to original HYP offsets and operands. All **1,308 native evaluations** agree with the original predicate instruction body at the observed values. This includes five builder designs, all four original ending choices, five denial segments, real game-state controls and all three randomized P510 starts.

Joining these observations with the accepted scalar matrix gives the following coverage of its 1,392 original condition positions:

| Observed outcomes | Positions |
| --- | ---: |
| Both | 1,215 |
| False only | 164 |
| True only | 12 |
| Unvisited | 1 |

Sixteen of the 17 previously unvisited positions now have native observations. The remaining position is P536 sprite8 click, command16. It is not classified as an engine defect or an unreachable original branch. These counts combine a reduced scalar matrix with controlled engine routes; they are neither complete gameplay coverage nor a whole-project percentage.

The tracing builds were not installed. The installed update is the separate mask-only builder guard, whose `ScriptRunner` and other headers are unchanged. Per-command details, logged values, full reduced fixtures and original assets stay local. The published source helpers refer to recorded Windows build inputs and local evidence; their hash guards are intentional. They are not portable installation commands.
