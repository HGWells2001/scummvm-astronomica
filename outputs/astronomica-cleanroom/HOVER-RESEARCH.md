# Hover, 11 October 2026

Original place-loop research: probe_hover_dispatch.py executes sprite and
rectangle dispatch instructions for 256 state/hit combinations, including
stationary repeats. Hit predicates are modeled. Per-target entered flags
queue scripts in sprite-index order, then rectangle-index order. Click lock
does not suppress ordinary hover. Cursor-bearing sprites can intercept the
original scan; the four scenes covered here contain no such sprites or drag.

Native configureHover caches invariant bounds only for original hover sprites
in P1/P505 and validates paired scripts for all32 targets in P1/P505/P519/P526.
hoverAtTime samples every ordinary engine loop after pending scripts run.
Hidden sprites still receive hits. Scripts are queued for the following tick,
with no repeat while the pointer stays inside or outside. Scene loading
clears state and queues. Changed conditions do not synthesize a new entry.

Target tests use all32 original target geometries and scripts, four original
P505 sounds11..14, conditional P1/P526 branches and256 dispatch combinations.
P526 starts in local3=1; positive hover checks explicitly use the settled
selection state local3=0. The initial test failure was a test precondition,
not a production condition change. P505 sprites0/2 genuinely overlap at
105,376: both highlight and play in order, with sound12 replacing sound11.
The single-target checks use centers outside that overlap.

Targeted native checks PASS. Full-suite status is recorded separately in
hover-validation.json only after regression completes. Manual audiovisual
review and an interactive full-game playthrough remain pending.
