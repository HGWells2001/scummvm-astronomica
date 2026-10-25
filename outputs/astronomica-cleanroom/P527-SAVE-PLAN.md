# P527 native-save plan, 25 October 2026

Status: implementation in progress. The verified published baseline is P516 v22,
commit dcc18aed083b3957d6a72c5a3e1c3794814d5b9d, executable
6727874da49ad53d05645971547ff544bc57d58ed3ad665cd4ae6dfce1adef8c.
This plan does not establish P527 save support.

Direct parsing of the nine remaining original resources selects P527 as the
smallest sprite state: nine sprites, eight conditions, one startup program and
82 commands. Original HYP: 348102 bytes, SHA256
03df944bdc8dffc6780ba324c6879b7cd91529e741637dd7c59acde220aad6a4.
Original FLATRING.MOV: 8387803 bytes, SHA256
f33e62405662875f3fd1d85087f19954f4d334a3235d528f53facd404dd3b4f3.
See work/fresh-20260913/remaining-save-review-20261025/report.md and the separate
work/fresh-20260913/p527-independent-review/original-movie-inventory.json for
the original field and sample-table evidence. These are static observations;
the original executable was not run.

The first scope is quiet, stopped-movie, script-idle boundaries. Preserve the
full605 runner words, all sprite fields, independent script clock and ambient
timing, previous place, completion count and supported dormant cross-puzzle
state. Queued work, click locks, foreground sound, hover and pending images
must bar a save. Active playback requires a separate future contract.

The current selection, seen mask, last attempted movie segment and last
presented image are independent. The image must be reconstructed from its
actual committed sample, not inferred from the selector or decoder cursor.
No frame can be committed when the first update reaches the segment end;
both an absent image and a retained earlier image need native witnesses.

| Selection | Segment start/end,30Hz | Eligible retained samples | Seen bit |
|---|---|---|---|
|1|1800/2399|600..799|1|
|2|2568/3527|801..1079|2|
|3|900/1799|300..599|4|
|4|0/899|0..299|8|

The movie has1105 samples at320x240, variable sample duration, and a single
rate-one edit starting at media0. Samples800 and1080..1104 are outside the
original requested segments. Sample801 is not a sync sample. Compare every
sequential native decode with a stopped decoder's seekToFrame reconstruction
before trusting temporary-decoder preflight.

Native acceptance requires all four choices, every non-full seen mask,
repeated viewing, changed selectors with older pictures, independent absent
and retained history, first/repeated success, early solved/unsolved exits,
busy rejection, natural voice end, ambient restart, fresh-process slot22 and
metadata. Reject truncations, byte corruptions and checksummed invalid state
without mutating live state. Preserve the genuine frozen v22 slot21 unchanged.
Only reviewed candidate sources may be integrated; then build the real main
engine and run the complete same-build WASAPI regression chain before
recording support or publishing v23. Keep the existing v22 rollback intact.
