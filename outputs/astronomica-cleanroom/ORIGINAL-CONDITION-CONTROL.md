# Original condition-link control regression, 6 November 2026

The original Win16 command reader uses a single most-recent condition pointer. It does not build a nested condition stack. A new bounded machine-instruction replay was compared with the actual native `ScriptRunner` implementation for all **936 nonempty script sequences**, covering **10,316 original command positions and 1,392 condition tests**, under **5,997 controlled input cases**. The native comparison passed with aggregate `1ee292f2`.

This is a control-flow regression, not a claim that all original game commands, alternative outcomes or scene routes have been played.

## Original evidence and replay boundary

The source is the unchanged `SETUP/ASTRO.EXE`, SHA-256 `c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e`. REA rejected this NE target as unsupported; that rejection is retained. The subsequent analysis uses the existing cleanroom Capstone package, actual version **5.0.7**, in explicit x86 16-bit mode. It is not presented as REA execution evidence or as the original Windows program running.

The reader dispatch comes directly from its original segment-9 table. Opcode 31 selects `9:3289`; opcode 42 selects `9:334e`; opcode 45 selects `9:335d`. The bounded replay executes the relevant flag/pointer writes and common linking epilogue through `9:3521`. The current condition pointer is stored in the reader's local slot; links occupy command field `+0x40`. The alternative marker selects the current command, while a nonterminal end marker selects the newly allocated following command. A later condition replaces the remembered pointer. A terminal marker has no following allocation.

The control epilogue replay uses `15:1636–1799`, with the original alternative/end flag handling at `15:0e81–0e99`. It chooses ordinary following commands, failed-condition links, and the following condition's link when an already-taken alternative is skipped. The replay executed **1,845,464 original instruction steps** across the bounded cases. It fails on an unmodeled instruction, call or selector; no unsupported behavior is silently skipped.

The initial model exposed a Capstone operand-size detail: a 16-bit `LES` destination still loads a four-byte far pointer. That was corrected before any accepted fixture was produced. The independent instruction-derived link arrays match the documented single-pointer source model for all 936 sequences.

## What is modeled

The allocator returns distinct deterministic far pointers. The modeled clock returns zero. Operand-copy calls are omitted after separate exact-byte verification of the original resource operands. The original predicate machine body is outside this replay: comparison results are supplied from controlled uniform values at thresholds and integer limits, using the declared comparison policy.

Command delays are normalized to `-1` for this topology check. Every noncontrol command becomes a numbered trace action. Assignments, random choices, sounds, movies, transitions, timers and native custom callbacks are therefore not executed as original game effects. The reduced fixture is local and is not distributed as original game content.

The native console test links the real `ScriptRunner` from the verified current engine library. It feeds the reduced sequences through the public queue/tick API, then checks executed-command counts, pending work and the exact trace-action order. No replacement script interpreter is substituted for the engine. The helper's test entry point is distinct from the installed full game executable, which remains unchanged.

## Reproduce with the original files and local build

```text
python outputs/astronomica-cleanroom/probe_original_condition_links_nov6.py D:/astro work/fresh-20260913/original-branches-nov6/inventory.json --out work/fresh-20260913/original-condition-control-nov6
python work/fresh-20260913/run_original_condition_control_nov6.py
```

The first command requires the original syntax inventory and local Capstone package. The second requires the recorded Windows compiler, current engine library and verified full-build objects. It is a regression driver, not a portable source-installation command. Output directories are deliberately new; preserve existing evidence rather than overwriting it.

Fixed acceptance A03 remains partial. Required original behavior, dynamic callbacks, timed failures, state-changing branches, reachability in real gameplay and the unparsed P406 resource still require explicit scope and execution evidence. Exact help typography and the human audiovisual playthrough also remain open. There is no measured whole-game completion percentage.
