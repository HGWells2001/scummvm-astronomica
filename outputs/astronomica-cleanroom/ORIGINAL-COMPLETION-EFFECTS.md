# Original completion effects, 10 November 2026

A new bounded replay executes the original custom25 scene dispatcher and completion handlers, including `_puzzle_successful`. It covers all25 scenes with a serialized custom25 call in the accepted HYP inventory. Resource opcodes/operands are checked against the original bytes. The original voice call is an observation boundary rather than original OS playback.

The comparison with a separate real-engine verifier passes300 cases and600 invocations. It checks all100 global values after each call, the puzzle counter, and the global/counter snapshot when each of44 actual muted WASAPI voices begins. Cases include zero/nonzero signed completion flags, repeated calls and counter wraparound. P513's silent increment, P530's voice without increment, P529's additional flag, and original no-op dispatches retain their separate effects.

The tested actual engine uses the pre-weather-fix ScriptRunner. This historical receipt is not relabeled as a new run of the later installed binary. The weather source delta is separately bounded to its mode0 result store and a focused regression test. Completion logic is unchanged by that delta.

The original executable is SHA-256 `c2b02b97afd77d5e0c68d1fc38e67a700e6b397f9b0bcf90ffbf578aec9f5d0e`. The OS voice boundary is modeled, scalar owners are controlled, and command delays are normalized to minus1 for these isolated calls. The verifier's voice itself is actual native playback. This does not certify every complete puzzle route, timing history, original Windows execution or a human full playthrough. Raw fixtures and diagnostic executables stay local.
