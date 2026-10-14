# P408 mentor videos, 4 October 2026

Original resource P408 has seven buttons and MENTORS.MOV (160x120,30Hz).
Buttons2..6 execute custom21 with mentor1..5, wait200ms, and either play the
selected segment at400,30 or speak S2.WAV when local0 indicates no hint.
Button1 returns to the previous scene after750ms. These scripts are read from
D:/astro/PLACES/P408/MEGAFILE.HYP, not recreated in native code.

ASTRO.EXE custom21, segment4:4538-50e8, selects by DS:0c94 (previous place).
All five switch tables contain27 scene IDs. P524 selects a further eight
ranges using global10 (the saved local0 question); other sources select one
range per mentor. The native table contains34 source/question rows.

The final original code computes duration=end-start+20 and start=start-5,
sets local0=0, calls SetMovieActiveSegment and StopMovie. If both original
boundaries are zero, it sets local0=1 without changing playback.

probe_p408_mentors.py executes these original branch and arithmetic
instructions, models memory, and records external movie calls. It checks1900
combinations:five mentors,38 source IDs and10 question values. It separates
CS switch-table reads from DS state. The emitted mentors.h contains numeric
clip boundaries only, not original executable code.

P524 question0/9 leaves both stack boundaries uninitialized. Ten such cases
are explicitly marked undefined in the evidence. Native code returns no hint
for them, rather than playing an arbitrary range. The normalized comparison
hash is3fc5282b. This is a compatibility decision, not literal stack emulation.

P523 example start/duration pairs for mentors1..5:
60883/266,48559/1493,20416/371,29911/350,38398/335.
The largest end is67119, below the actual movie duration67222.

The book button is a separate operation:custom22/1 stops sound, blacks the
screen, presents the movie's first frame and invokes process_help(1).
process_help at9:4016-408c calls the Windows help API. It is not implemented
by enabling mentor movies and remains a separate task. Mentor movie tests do
not establish that the external help book works or confirm human audiovisual
quality.

P523 help-return verification now changes channels and response flags before
entering P408, clicks the original return button, reruns the original P523
entry script, and checks reset channels, fresh callback slots, working controls
and unsolved exit. The scoped native check passes.


## Mentor help checkpoint, 4 October 2026

P408 mentor buttons now play their original contextual video ranges. Native
comparison passes1900 cases, with explicit no-hint handling for undefined
P524 variant0/9.170 decoded selections,37 source-scene returns, no-hint speech
and natural continuous segment completion pass, together with the full suite.
P523 help return resets modified controls and response flags and reinstalls
the movie callbacks; original input still works after returning.
The Windows help book (custom22), native saves and manual audiovisual review
remain incomplete.35 puzzle-route scenes remain verified, not35 distinct
puzzles; no whole-game completion percentage is asserted.
