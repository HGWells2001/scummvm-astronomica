# P517 aurora save requirements

Implemented and verified19 October2026; see evidence/p517-saves-validation.json.

The original P517 resource has eleven sprites, two locals and two startup programs. Its fourteen control positions select four opaque 640x320 AURBACK images and move the gauge and marker. The original resource probe records all positions and 196 ordered picture overwrites; this is resource evidence, not a Windows execution trace.

The three aurora cycles use four, four and two frames. Their original periods are 100,100 and300ms. Command30 hides and stops an inactive cycle but retains its frame and last timer epoch. Reactivating a cycle preserves that history. A restore must preserve all three phases and the signed stopped timer fields, not just the currently visible frame.

The v12 payload is3660 bytes: ASVM/version, twelve header words, eleven complete27-word sprite records, the frozen603-word runner state and checksum. Header8 identifies AURBACK1..4; the others retain scene, count, script clock, previous scene and ambient state. The locals must match the original level/position table; unknown local values remain inert and are retained.

Saving should remain available during ordinary cyclic animation once foreground scripts and button pulses settle. Pending images, foreground WAVs, incomplete startup, unsupported settings or unexpected picture footprints must prevent saving. Load must preflight every field and picture before changing state.

Required verification: settings1..14, both controls, minimum clamp, animation phase and next-frame timing, inactive phase history, first/repeated completion to P512, unsolved exit to P157, physical slot11/fresh process, positive S0 Music restart, old slots, corrupt/truncated payload atomic rejection and the complete compatible suite. Music may restart from the beginning; full manual audiovisual playthrough remains outstanding.
