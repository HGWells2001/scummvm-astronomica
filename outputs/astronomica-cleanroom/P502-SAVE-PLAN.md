# P502 native-save plan,25 October2026

Status:69 fresh native state observations passed; serializer implementation
in progress. No verified P502 save support is claimed yet.
Verified baseline: published P527v23, commit
c87f0ad095a99519462d5de37d472acbd344d74d, executable
d0c181251ab0b4714d344a09134ba4f5aa3c4962314b4892fc82660c17fc8c95.
The genuine frozen v23slot22 is retained unchanged for compatibility testing.

Current original MEGAFILE.HYP is669631bytes, SHA256
880df2452622db2f9377793ef660cbc16ef534d6251394548bbebfacf2e8b020.
It has35sprites,four conditions,two finite startup programs and145commands.
The existing allowed cleanroom engine already executes the comet puzzle;
the next change concerns native saves in useful ordinary nonflight states.
The strict resource parser consumes a586447-byte structured prefix; the83184
remaining original bytes are retained as an opaque tail with independent
identity. This inventory does not establish the interpretation of that tail.

Audit the real engine before defining accepted sprite and private-state
constraints. Cover all four direction controls and16speed levels, prelaunch
states, zero-speed launch, low/high/wrong-direction failures, repeated failures
and a control change after the comet becomes hidden. Preserve coordinates,
motion/frame epochs and retained CometMotion kind/partner/sound/explosion.
Current selection must not be used to invent the previous failed trajectory.
Check inherited dormant variant state and Jupiter collision geometry as well.

The isolated actual-engine audit proved low/wrong-direction failed returns
retain kind2,hidden frame5,render340/190,stored520/310,stopped motion epochs,
and sticky sound3/explosion21. High failures retain kind3,hidden frame0,
render199/10 and sound-1/explosion0. Entry kind0 instead has stored/render
520/270 and no configured standard motion. Changing controls preserves this
history. The complete native records and producer/source identities are in
work/fresh-20260913/p502-audit-stage; this is observation, not save validation.

The proposed scope is script-idle choice and failed-return boundaries with
hidden stopped projectile. Reject active flight, pending transitions, click
locks, foreground audio, hover and uncommitted images. If native observation
does not support this scope, retain the audit and refine the contract before
implementing a serializer. Successful launch queues the original transition;
its eventual first/repeated outcome must still be tested after restoring an
eligible earlier save.

Require an independent source/state review, complete original-resource
preflight, full605 runner state and supported private state preservation,
atomic rejection of every truncation/byte corruption and checksummed invalid
fields, actual natural voice end and ambient restart. Use version24/slot23,
fresh-process continuation and metadata, unchanged genuine frozen v23slot22,
then the complete same-build native WASAPI suite before publishing support.
No measure here represents whole-game completion.
