# P516 custom9: integrated native implementation

The scoped native suite now passes setup128, motion20 seconds, collision64
plus four API boundary cases, three independent image compositions, frame
timing at79/80ms, victory/repeat and two failure/exit routes. The current
development manifest identifies the latest complete regression checkpoint.
Manual audiovisual testing and help/return coverage are still pending.

1 October2026. Setup:128 original instruction executions in p516-setup.json.
Collision:64 executions in p516-collision.json; external PtInRect boundaries
are explicitly excluded. Neither file is a native implementation test.
Motion: probe_p516_motion.py executes all eight original ellipse callbacks
for20 seconds with the original bitmap dimensions. Hash0x7780b563,
34 visibility changes; evidence/p516-motion.json records sizes and events.
Generic frame cycling is excluded from this movement-only comparison.

Local0 selects direction1..4, local1 speed0..15, local2 success0/1.
Custom9 mode0,4:1c67..1f40, configures sprites14..21:
center320,100; AD10; ellipse callback; quadrant flags0; move period10ms;
both deltas0 after the initial setter. For14..17, partner=35-id, hidden,
rx=(18-id)*40+100, ry=(18-id)*12+50. For18..21, partner=id-35, visible,
rx=(id-17)*40+100, ry=(id-17)*12+50, location320,100+ry.
These are four paired orbits sharing the comet ellipse/handoff mechanism.

Custom9 mode1,4:1f43..2038, is a no-op for speed<=0. Otherwise sprite13:
callback _fxm_hit_jup_comet, move period50ms, visible, location320,300;
dx=trunc((2*direction-5)*(speed+3)/3), dy=trunc(-2*(speed+3)/3).
Movement timestamps are not reset by the setters.

Projectile callback3:34d5..364e checks the OLD sprite rectangle against
move bounds. If wholly beyond a bound it hide/stops13 but still performs
the collision loop. Test point is old left+16, old top+16, with16-bit
wrapping. Visible targets14..21 are tested in ascending id order through
_fxm_PtInRect, a wrapper around the imported USER rectangle function.
Any collision hide/stops13. Only targets17 and18 set local2=1; those hits
also stop movement timers14..21, start explosion23 at(pointX-48,pointY-48)
with10 ticks/frame, hide/stop the hit target, and play direct sound9.
The loop continues after a hit: do not silently add an early break.

Original launch button12 locks input, plays serialized sound11 (directS10),
hide/stops13 and calls custom9/1 immediately. After5000ms it tests local2;
success invokes custom25 after2500ms and transitions toP388 after2000ms.
The conditional then ends and input unlocks. These delays are consecutive
script delays, unlike the independent explosion commands.
Sprites14,17,18,21 have80ms automatic frame cycling in the resource;
the20-second motion evidence intentionally does not cycle those frames.
This must be covered separately in the eventual native interaction test.

Implemented: layer guard for37 sprites, startup orbits, projectile callback,
independent explosion commands, custom9 dispatch, real-resource motion and
graphics comparisons, and actual click victory/repeat/failure/exit routes.
The deterministic victory uses direction2 and speed1 with300ms between
button operations after startup. Failed routes use speed0 and direction1/
speed1. No success flags are injected to obtain the victory.

The imported USER PtInRect call is modeled using Microsoft's documented
left/top inclusive and right/bottom exclusive convention:
https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-ptinrect
This is API-contract evidence, not execution of the Win16 USER library.
The64 original callback fixtures deliberately exclude boundaries; four
additional native tests check that documented convention separately.
Sprite13 is42x41; its collision point is still the original fixed+16,+16.
Sprites14/21 have one frame and wrap to0 every80ms;17/18 have three frames.
