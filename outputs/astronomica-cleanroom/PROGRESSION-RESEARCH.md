# Original scene transitions, 4 October 2026

Source: unmodified D:/astro/SETUP/ASTRO.EXE, segment9:0289-066c.
probe_transitions.py executes those instructions, reading switch tables from CS
separately from mutable DS state. It records external sound calls. It does not
read the native implementation. 47,520 original executions produce normalized
FNV03a3e23b. The cases cover every puzzle source501-537, range boundaries, help,
all-zero/all-one/one-hot globals, and both directions of the world gates.

Nine directed pairs require global57 exactly1:307->414,271->298,284->289,
324->329,101->110,120->144,177->182,139->151,160->168. Success consumes global57;
failure redirects to429. Leaving208 or387 clears global57. The comparisons
continue to use the requested destination even after redirecting the live
destination variable.

Entering501-599 from outside that range requires nonzero global29, except513.
Denied entry restores the old destination and starts globalS10.WAV. The
original then reloads that scene. Native loading preserves this foreground
voice; other scene reloads still stop the previous sound.

Leaving an unsolved puzzle starts globalS11.WAV after loading the destination.
Help408/409 bypass that exit check. Continuations502-504,507/508,515->536 and
520/537 have special exceptions. For506/531-535 the original reversed bounds
(destination<=535 OR destination>=531) always suppress the exit voice. This
behavior is retained. Returning from help still passes the global29 gate;
help fixtures now establish that prerequisite explicitly.

Production scripts, movie callbacks, motion exits and navigation use
changePlace. Direct resource loading, initial placement and save restoration
remain separate. Transitions do not synthesize puzzle completion flags.

## Denial movie chain and credit images

Original429 chooses one of five F21G.MOV ranges:30/187,357/365,810/280,
1200/503,1804/342. Its original script then enters427, whose END_BOOM.MOV
plays before425.426/F23B.MOV and428/F23A.MOV use their original timed exits.
All use ordinary per-scene movie paths from_load_place9:25f7-2612; the
redirects for4,409,520 do not apply. Full-range scenes initialize the decoder
end time;429 subsequently applies the range in the original script.

425 has zero sprite layers but seven external credit images CRD2..CRD8 and
an original timed exit to432. Image discovery now includes that scene. Its
independent custom26 bookkeeping script remains unsupported; this is not a
claim of a complete ending or completed game.

## Next necessary work

probe_progression_inventory.py records original custom26 commands in21 scenes
and its dispatch/body4:5a91-6310. This operation transfers game-wide state to
local conditions and back, including global57. It is not implemented yet and
is necessary for exploration progression. Investigate its counters/settings
and the interaction scripts before claiming the gates can be unlocked in a
full playthrough. Inventory found one truncated original resource,P406;
the native resource test already excludes it.

Windows help-book processing, arbitrary mid-puzzle saves and an audiovisual
manual playthrough also remain. OnlyP508 has user-confirmed manual completion.
No whole-game percentage can be inferred from scene counts or these tests.

Independent custom26 execution is now recorded by probe_game_state.py:
2436 command cases, normalized FNVd253e90a, plus42 resume/memory boundaries.
Read keys:1=completed counter;2=global52;3=global53;4=puzzle selector1..27
maps globals20..46;5..11=globals55..61. Write keys2..11 mirror those
transfers; key1 has no write branch. Key12 reads constant1. Key13 reads the
boolean _resume_game word DS:07a0. Key14 compares _avail_bytes DS:0bd0 against2400000, or against
1650000 when _help_running DS:079c is nonzero. The meaning/lifecycle of those resume flag
and available-memory fields still needs verification before native implementation.


## Scene progression checkpoint, 4 October 2026

Original transition rules are integrated: nine directed world gates, consumed
permit, puzzle-entry prerequisite, and global denial/unsolved-exit voices.
47,520 original instruction cases and native comparison pass. P429's five
denial movie segments, P427, P426/P428 timed exits and seven P425 credit images
are tested. The complete native regression suite passes. See
PROGRESSION-RESEARCH.md. This does not establish a complete game route:
custom26 inventory/state transfers remain unimplemented. Independent original
research now covers2436 custom26 cases and42 resume/memory boundaries.
The35 verified puzzle-route scenes and manual confirmation scope are unchanged.


## Game-wide state checkpoint, 4 October 2026

Custom26 is integrated and matches2436 original instruction cases plus42
resume/memory boundaries. Cabinet/item persistence, world-door flag, live
completion count, hub indicators, credit bookkeeping and the P407/P422
keypad sequences pass native checks. Global voices and zero-layer exploration
images now support those original scripts. Full regression passes. See
GAME-STATE-RESEARCH.md for explicit legacy resume/memory adaptations.
P409 custom27 research covers34800 cases; it is not integrated yet. No new
whole-game percentage or manual completion is claimed.
