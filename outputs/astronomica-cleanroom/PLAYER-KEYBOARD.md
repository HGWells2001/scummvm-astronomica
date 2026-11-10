# Player keyboard routing — 10 November 2026

The real player now respects the script click lock for keyboard navigation. A serialized original P27 click establishes opcode28(-1), leaving a pending script and clicks blocked. The previous native ScummVM handler nevertheless followed the right NAV target to P30. Its preserved baseline reproduces this bug; this is not a claim about original Windows execution. The guarded shipping handler preserves the blocked live state.

F5 still opens the real global menu while blocked, and Escape exits. Unblocked arrows retain their original NAV targets. Control/Alt/Meta-modified game keys are ignored. Letter demos and PageUp/PageDown scene cycling require the explicit developer option `astronomica_debug_controls=true`; absent and false both keep them inactive. No player-facing diagnostic UI was added.

Permanent checks cover20 blocked key cases,16 absent/false diagnostic cases,3 original NAV targets and9 modified-arrow cases. They compare live state with a caller-owned pause, exercise an actual F5 menu dialog and verify explicit diagnostic opt-in and Escape. The complete general native suite and the separately installed-path keyboard verifier pass on the exact exported source/executable pair.

Only astronomica.cpp/.h change from the published animation cache. Private nonvirtual methods and an include are added; no data fields,class layout,core files or save schemas change. All seven engine units were freshly compiled with403 verified foundation objects reused. Source installation requires a clean full build. Earlier geometry,animation and frozen-save receipts remain historical evidence under their own hashes, not fresh checks of this binary.

Acceptance remains7/10 fixed criteria (70%); this is not whole-game completion. Whole-game completion is unmeasured. Complete required behavior mapping,original help typography and a human audiovisual playthrough remain open. No original media,binaries or physical saves are exported.
