# Original mouse edge navigation —11 November2026

The real engine now follows mode1 room exits with mouse clicks in the original border zones. Previously those exits were reachable through keyboard arrows only. Sprite hits and scripted rectangles keep precedence; even an empty rectangle consumes its hit. Fully disabled sprites leave the hit available,while an eligible unsupported sprite consumes it. Original script input locks remain respected. Scene changes use the existing transition resolver,including denial/permission behavior.

Original SetRect calls and actual import relocations establish the left zone[-20,50)×[50,270),top[50,590)×[-20,50),right[590,660)×[50,270). Original stream order is left,top,right. Current Windows PtInRect supplies an independent307,200point geometry oracle; this is not original Win16execution. See Microsoft's [PtInRect contract](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-ptinrect). Raw original instruction evidence remains local.

## Verified scope

The actual previous native engine reproduces P103's missing left-edge exit. The shipping candidate passes the independent geometry hash,three real directional exits,actual original P27 input lock,documented controlled sprite/rectangle overlaps,disabled-navigation mode,and P101's denied/permitted top exit. The previous keyboard routing verifier also passes unchanged.

A separately audited actual-engine diagnostic adds only the exported test branch to the exact shipping sources. All22other engine files,including the class header,match. It visits306original mode1 scene resources and all760nonzero NAVreferences. For every reference it finds an original unobstructed point,clicks the actual mouse path,and compares destination plus all100globals with the corresponding existing keyboard path under controlled default globals/RNG and disabled entry scripts.760matched,zero untested. This proves the documented bounded input parity; it does not prove naturally reachable whole-game paths,audiovisual futures or completeness of puzzle behavior. Original resources remain unchanged. The optional.inc branch permits repeat after insertion at the documented condition and a clean rebuild;it is not installed.

The complete general native suite and installed-path edge-navigation verifier pass. Every suite process was observed until natural exit. No elapsed-time or failure-marker process termination is used. The first audio-disabled test configuration and a controlled sprite-priority expectation were corrected;those failed receipts remain separate and are not presented as passing.

Only astronomica.cpp/.h change from126dd66. There are no added data fields,class layout changes,core changes or native save schema changes. All7engine units were freshly compiled with403verified foundation objects reused;full clean source rebuild required. Cursor artwork/hover shapes are unchanged by this update.

Fixed acceptance remains7/10(70%),35bounded save profiles;whole-game completion remains unmeasured. Complete required behavior,exact help typography and a human audiovisual playthrough remain open. No original media,disassembly,binaries or physical saves are included in this export.
