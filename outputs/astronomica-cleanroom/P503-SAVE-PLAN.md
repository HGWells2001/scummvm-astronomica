# P503 save research, 26 October 2026

Status: same-build native WASAPI and complete compatibility verification PASS26October2026. Publication requires the separate export gate.

The original P503 resource has 48 sprites in two layers, 9 local values and 237 commands. The whole 782595-byte file is bound by SHA256 `0b6e4b9afa8bafa670b19d8e79cbdb6bab7f675166aabfe27f9d421d9ed3447f`. The structured prefix ends at 617311; the remaining 165284 bytes remain opaque. Full-file identity includes those bytes.

The independently reviewed native audit retains 729 observations, all 320 target/direction/speed combinations and 55 orbit partner handoffs. Those observations describe the allowed cleanroom engine using original resources; they are not observations of the original Windows executable and do not by themselves establish save correctness.

Proposed version 25 uses slot 24 and 8132 bytes: 11 header words, 48 independent 27-word sprite records, all 605 runner words and 118 private Comet/Jupiter words, plus magic, version and checksum. The first useful scope admits quiet prelaunch controls, never-solved stopped failures and healthy partial orbit pairs. Each partner retains its own position, frame, movement and frame epochs, sides and deltas. Shared scratch and dormant Jupiter geometry are preserved literally.

Primary ascent, solved-target failed relaunch histories with stale one-way partner links, a fully solved transition, pending work and foreground audio remain outside this first scope. A failed relaunch must never be reconstructed as a healthy orbit from its historical solved flag.

Required checks include all 30 proper partial masks; first-kind-4 side bits; movement/frame before, at and after their periods and clock wrap; exact successor continuation; all 8132 truncations and corruptions; checksummed-invalid atomic rejection; natural voice and Music handling; first/repeated P503 to P504 to P527 outcomes; and physical slot continuation with metadata in a fresh process. Independent final review must bind the final source, executable and diagnostic proof. Production then requires native WASAPI target verification and the complete prior compatibility chain, including the genuine frozen P502 version 24 slot.
