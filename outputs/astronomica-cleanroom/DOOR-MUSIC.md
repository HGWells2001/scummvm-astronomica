# Shared door effects preserve Music

The original P27 opening sound uses shared905; P85's door control uses shared907. Their exact files are referenced by19 original commands. Both are now reviewed effects over the existing Music stream. The first P27 click opens the door and the second enters P32 while retaining the same regional Music owner. Unknown recordings, explicit introductions and blocking/movie sounds retain foreground handling. Narration still suspends Music.

Causal before/after tests use the original hit-tested P27 sprite and P85 rectangle, controlled initial state and WASAPI. Before the fix each effect replaces Music and restarts it. Afterward the same Music handle advances through the effect, with exactly one sound start and guarded transient save/load. Windows checks and existing regional,close-up,ASVM2/pause,narration,P504 and P513 control regressions pass. The exact full general suite and genuine pre-fix ASVM29 continuations pass before integration.

All seven engine units were built freshly against403 verified unchanged core objects. Only astronomica.cpp changes; the engine header,three core files,sixty serialized save/load method bodies and original scene-music selector remain unchanged. Installed native and previous-save checks pass. Source installation and independent-clone validation are required before final publication.

This adds two exact identities to the eleven already reviewed; it is not an automatic classification of every sound. Original assets, executable binaries and physical save fixtures are not published. Personal installation is excluded. All qualification processes finish naturally. Fixed acceptance remains7/10; total project completion is unmeasured.
