## Verified P521 save support,23 October2026

Version19 is implemented and verified; see P521-SAVE-FORMAT.md and evidence/p521-saves-validation.json. The original inventory below remains research history.

# P521 candidate contract

Status: static original profile; native candidate audit and save verification pending.

Fresh original MEGAFILE.HYP has 27 sprites, zero local declarations, one startup program and 175 commands. The single startup command places sprite13 at15,251/frame2. Opcode24 is an absolute stored/render position followed by frame selection. Clones inherit frame images only.

The proposed boundary is settled script execution with no pending program/action, button pulse, hover, foreground voice, movie or staged image. Sprite12's400ms animation remains active and must retain its phase. Sprite11's stopped hidden animation and fragments14..23 retain selected frames, coordinates, movement/frame parameters and epochs. Repeated choice5 does not reset their coordinates or clocks. The absence of local declarations does not justify zeroing historical values: preserve the full605-word runner state and metadata.

Choice5 displays ROCKS_b during locked queued animation, then EARTH_b before unlocking. Both originals are640×320×8bit. EARTH_B is byte-identical to the embedded background, but the displayed image name remains observable engine state. A settled image identifier distinguishes base(0) and EARTH_B(1); restore starts from the full HYP background and copies EARTH_B at0,0, preserving the lower scene/control. Pending-image state and transient ROCKS_B are excluded.

Proposed v19 stream: ASVM/version8bytes +11header words +27×27sprite words +605persistent words +checksum word =5392bytes. Header preserves place, completed count, clock, previous place, ambient loop fields, comet history and retained image identifier. No additional P521 private callback cache was found; explicitly verify unused orbit/planet fields remain default. Restore must preflight original HYP/assets/profile and all sprite geometry before mutation and import onto the live runner whose bindings loadPlace recreates.

Before claiming support, audit fresh startup, all five original controls, repeated/mixed choices, retained EARTH_B, hidden fragment history and timer edges. Verify full480-row surfaces, byte roundtrip/successor, future outcomes, natural voice completion, ambient restart, dormant variant, full atomic malformed rejection and fresh-process slot18. Native execution is not part of this static report. Dynamic history bounds remain unknown until that audit; no runtime support claim is made here.
