# P515/P536 construction saves: investigation plan

19 October2026. Save support is not implemented or verified for these two scenes.

Original resource observations are recorded by probe_builder_save.py and evidence/builder-save-original.json. Each scene has60 sprites,13 locals,seven programs and no movie, automatic motion, drag or hover programs. The only picture commits are opaque250x330 drydock/pad at0,0. Eight ordered original-image overwrites across the two scenes confirm that the last image is sufficient; absence of a picture is also an initial state.

The original custom25 dispatch has no P515 entry; P536 uses global31 and increments the counter on first success. See probe_builder.py/evidence/builder.json for the executable-byte evidence. A restored scene must rebuild that handler context rather than assume the two scenes share a success implementation.

Do not restrict P515 to designs1–3. Launch starts with a stage<4 branch that stores mask7. Choose then uses that mask through command39. On a fresh P515 this can select designs4/5; the expected direct exit is P510 while P515 success remains a no-op. This conclusion from command order is scheduled for separate native validation in the next build. P536 also starts with scenario2 before a normal choice; its initial state must remain admissible.

Proposed local checks, to compare with native boundaries: known widths5,5,5,6,7,1,1,1,1,1,1,1,1; mask0..31; scenario0..5; stage0..5; required size0/4/5/6; current size0..6; remaining flags boolean. Preserve unknown locals13–99 verbatim with unknown flags and width0. Current size6 is an original initial value. Controls9–14 can be pressed outside the successful construction order, so do not infer cap/part flags from stage or required size.

Retain all27 fields of every sprite. Button frames must settle before saving; the original request for sprite15 frame1 exceeds its one loaded frame and is ignored. Movement setters and offsets require preserving stored and rendered coordinates independently. In particular, an opcode7(0,0) request cannot justify forcing rendered coordinates to zero. Literal mutation lists alone do not establish every reachable combination.

The staged check_builder_boundaries.py uses actual engine controls on four ordinary routes and two early-Launch routes. It records locals, all sprite fields, picture and clock after settled actions. No native boundary report exists yet for this investigation. Before implementing a validator, compare the report against literal setters and finite offset sequences, include initial/cap-removal/partial-part/reset states, and retain any unresolved bounds explicitly.

Pending assembly/launch programs, foreground WAVs, staged images and button pulses must block saving. Unexpected picture footprints must invalidate image history until a scene reload. Preserve clock, previous place, count, runner/RNG and ambient state. Also account for the process-global custom17 round/mask: existing non-family formats require that sequence to be inactive, and a new format must not silently discard a suspended sequence.

Required tests after implementation: all five designs in both scenes when reachable, both normal phases, early Launch, first/repeated success and P515 no-op, undersized cap/removal recovery, partial parts, resets, no-picture boundaries, physical fresh-process continuation, full480-row rendering, corrupt/truncated payload atomic rejection and all older formats. Native route observations do not replace a complete manual audiovisual playthrough.
