# Original scalar effects inside timed queues, 9 November 2026

The expanded instruction replay passes **810 controlled cases and 12,150 ticks** against the real native ScriptRunner, aggregate `4cdb607d`. Unlike the earlier queue check, it retains original bit updates, free-bit selection and random ranges in addition to predicates, assignments, additions, template calls and conditional control. The next random draw is checked at every tick using a copy of each state, so the observation itself does not consume the running generator.

The cases retain original delays from P423/P429/P510/P515/P536, initial queue sizes 1/2/3 and clock epochs 100, `0x7ffffff0` and `0xfffffff0`. Original condition widths are checked directly against the unchanged HYP files. Each tick checks all 200 scalar words, executed/pending counts, action order and RNG continuation. The oracle executes 13,991,613 bounded original instruction steps.

Three independent deliberately corrupted expectations are rejected: executed count, one scalar word, and the next random draw. The linked engine archive is also checked member by member: all seven objects exactly match the current fresh engine object and six verified foundation objects, including the actual ScriptRunner. A separate local snapshot reruns the positive comparison and all three negative checks without original assets; it contains binaries and reduced fixtures and is deliberately excluded from GitHub.

The first native attempt exposed a test setup error: loading condition metadata clears the program table. Installing templates after metadata fixes that admission failure. No engine admission check was relaxed. The corrected comparison and negative checks have their own receipts.

Allocation/free/clock APIs are modeled. Non-scalar game effects remain timed trace markers. Exact powers of two and integer conversion results are modeled only for admitted bit indices 0..30; the general floating-point helper bodies are not executed. Controlled scalar states do not establish all natural gameplay histories. This is not the original Windows application running, a human playthrough, or a whole-game percentage.

The installed engine remains the published builder mask revision. This research does not change save layouts, video core, or runtime sources. Fixed acceptance stays 7/10 (70%), with 35/35 documented bounded save profiles; whole-game completion remains unmeasured.
