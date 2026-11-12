# Normal gameplay defaults — 12 November 2026

Adding Astronomica through the standard ScummVMlauncher now enables reconstructed audio,animation,sprite input and scene entry scripts without manually supplying four engine-specific options. Previously an absent option silently disabled these systems. Registration alone would not fix this:stock ConfigManager::hasKey deliberately excludes the defaults domain. The engine now registers true defaults and reads their values consistently,removing67presence guards that bypassed them.

Explicit false remains respected. Application/game setting precedence remains unchanged. No gameplay keys are created in the target INIby registering defaults. ScummVM itself may normalize INIordering and add ordinary core metadata on exit;the tests check gameplay key presence/values and preserve the actual user preferences file.

## Verified scope

The exact accepted prior source,with the same optional verifier branch, reproduces the fresh-target problem:initial P1queue empty,original sprite frame unset,original P27button input inactive,and script audio admission inactive. The corrected real engine starts the original P1entry program,initializes the original frame,accepts the original P27button with its lock/pending continuation,and dispatches its actual original S0file through the configured ScriptRunner/mixer.

Twenty-four native profiles pass:prior baseline,fresh defaults,all16explicit feature masks,four application-level false settings,game overrides of application settings,and a fresh actual SDLWindows backend run. Seven freshly compiled engine units and403verified foundation objects are audited against the actual linked archive.

Four additional native processes use all four feature keys absent to load,resave and reload physical earlier accepted-engine ASVM2/P103,ASVM27/P501and ASVM26/P504files,including actual Windows P501. Scene,all100globals and completion count roundtrip;original fixture files and aliases remain unchanged. These are earlier engine saves,not original Windows saves or all-history full-future evidence. The optional exact observer fragment is not installed.

The full general regression suite passes with its original intended initial test conditions now stated explicitly(four features false). Its later sections enable the systems required by each test. A separately started fresh-default version of that old verifier naturally plays original introductions during its parser traversal;its receipt remains separate and is never relabeled. Every native process is allowed to end naturally,including failed harness attempts. No shutdown is authorized.

Early harness assumptions were corrected separately:one prelaunch check named a nonexistent local S1file;another called low-level playSound instead of the configured script audio path;another incorrectly required the isolated test INIto remain byte-identical despite ordinary ScummVMmetadata updates. Failed receipts remain local and distinct. The final native receipt checks the relevant behavior and all explicit feature choices.

ASTRO.cpp is the only changed engine file. Class layout,core3and every save schema remain unchanged. All7engine units were freshly compiled with403verified foundation objects reused;clean source rebuild required. Original game media,raw executable bytes/disassembly,pixels,native save fixtures and binaries are excluded from this source export.

Fixed acceptance remains7/10(70%)with35bounded native save profiles. Whole-game completion remains unmeasured. Complete required behavior,exact help typography and human audiovisual playthrough remain open. Automated admission/UI/file checks do not replace a human complete playthrough.
