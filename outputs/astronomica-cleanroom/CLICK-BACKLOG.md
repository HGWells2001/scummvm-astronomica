# Pending mouse clicks - 12 November 2026

Normal gameplay now handles only the first mouse-down event in each pending input batch. The actual production event loop is shared through one private nonvirtual helper. Keyboard navigation, the ScummVM menu and quit remain available in that same batch.

The original Win16 left-button message calls do_mouse, which drains queued messages before paused/input-disabled checks, the button pulse and the clicked script. The double-click message exits separately. The import resolves USER ordinal109 to PeekMessage. The port adapts the mouse backlog while retaining host controls. These are static original control-flow/import findings, not an original Windows runtime trace.

Primary API references: [Wine Win16 USER exports](https://raw.githubusercontent.com/wine-mirror/wine/master/dlls/user.exe16/user.exe16.spec) and [Microsoft PeekMessage semantics](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-peekmessagea). The public facts receipt excludes all raw original instructions. Direct handler bursts bypass the original queue drain and cannot establish human input equivalence or global P536 reachability.

The actual production poll loop is exercised with native event sources on twelve original P536 click bursts, comparing every case to an independent first-click reference across all100 globals and13 locals. The baseline differs in12/12 cases;the candidate matches12/12 in both dummy and actual Windows video. Actual keyboard navigation, F5 menu/pause and normal quit pass. An initial diagnostic build failed on a forbidden local identifier before any native process started;the observer was corrected and both roles rebuilt.

Four post-introduction physical ASVM2/26/27 roundtrips, four fresh-process genuine earlier accepted-engine ASVM29 continuations, twelve controlled P512 end-minus8 restored futures, a new full general suite on this exact candidate and installed checks pass. Physical fixtures remain local. These are bounded compatibility checks, not every historical save or original Windows saves.

CPP and header change only for input handling and the private helper;no fields,class layout,paired core files or save schemas change. All seven engine objects are freshly compiled against403 verified foundation objects. The clean pinned-source installer,independent clone and export integrity are checked before publication. Original assets,raw executable/disassembly,native fixtures and binaries are excluded. Optional clock and physical observers recover exactly from shipping source. All new native checks exit naturally. The old failed general remains untouched in its debugger. Never forcibly terminate suites. Do not shut down the computer.

Fixed acceptance remains7/10 (70%),with35 bounded native save profiles. Whole-game completion is unmeasured. Complete required behavior,exact help typography and a human audiovisual playthrough remain open.
