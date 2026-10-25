## Verified restricted P516 saves,25 October2026

Version22 is verified within the explicit stopped-projectile scope. See P516-SAVE-FORMAT.md and evidence/p516-saves-validation.json. Earlier investigation remains history.

# P516 save investigation,25 October2026

Status: investigation and restricted save candidate; no new verified save support yet.

Original: D:/astro/PLACES/P516/MEGAFILE.HYP,563403bytes,SHA256 fae86ac8d36038046a9d387f8fbc28d822d2cdcacc2cdb0ab4d941d55b58ced6. Fresh reader inventory:37sprites,3conditions,2startup programs,133commands. See probe_p516_save.py and evidence/p516-save-original.json. This parses original resources; it does not execute the original executable.

## Evidence and boundary

The cleanroom real-engine audit measured55records (52inP516 and3in388). A separate bounded flight audit measured40records in8cases: directions2/3,speed1 and launch-phase waits0/500/1000/1500ms. Those missiles all stopped before the original5000ms condition; the first two waits hit the correct target and the later two hit a wrong target. This does not establish that every launch phase stops before the condition. Idle active flight and late collision remain unobserved.

The original click program has custom9/1 at344531, local2==1 condition with5000ms delay at344563, custom25/0 with2500ms delay at344595, and destination388 with2000ms delay at344627. It does not reset local2 on launch. If the UI can unlock during flight, later selector changes may differ from the earlier launch velocity. No save eligibility may be inferred from scriptsIdle alone.

Candidate scope: quiet boundaries with local2=0, all8configured orbit sprites still moving, and missile13hidden/stopped, either before launch or after a demonstrated failed return. Pending work, foreground audio, startup, active missiles, aborted unproved histories, local2=1, stopped moons and success/explosion transitions remain excluded explicitly. The scope is a subset of ordinary P516 states.

## State contract

Preserve37x27sprite fields,605runner words,100CometMotion kind/partner entries,4tail fields and16cached collision dimensions. Frame/previousFrame are process history. Epochs, selected frames and range fields remain independent; a layer handoff copies a frame and velocity but retains the recipient's own epochs. Validate planetMotion0/planetPeriod-1 separately. Preserve dormant and unknown runner state, including the known width0 local2.

Original target dimensions are invariant across all frame owners/clones: widths50,39,110,60,60,110,39,50; heights50,100,40,60,60,40,100,50. They are used by collision checks. Recomputing these dimensions after complete preflight is possible; replaying configureJupiter(mode0) resets orbit state and cannot restore it. A reentry can retain the previous dimension cache before setup, so its presence alone does not prove orbit configuration.

Proposed real-engine candidate:v22,slot21,6944bytes. Common11header words include frame/previousFrame and reserved image0; then37x27sprite words,605runner words,100kind/partner words,2scratch words,16cache words and checksum. Header8plus1734uint32words equals6944bytes. Assignment remains candidate until implementation and complete same-build native verification pass.

## Required proof

Exercise all4directions and16speed values through original UI, genuine stopped failed-return history, orbit/frame10/80ms deadlines and wrap, independent handoff epochs, exact successor pixels across640x480, first/repeated outcome counts, natural voice completion, original entry ambient deadline and Music volume. Reject every6944payload truncation and byte corruption, plus invalid checksum-correct states, atomically across runner/sprite/audio/pixel state. Verify slot21 and metadata in a fresh process and retain unchanged genuine frozen v21 slot20 compatibility. Finish with the complete native WASAPI suite on the exact promoted engine.

No whole-game completion percentage follows from this investigation or from counting supported save scenes. Source/evidence is restricted to the post13September2026 cleanroom work and original resources.
