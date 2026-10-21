# P529 save preparation, 21 October 2026

This is static preparation for future save work. It adds no serializer, native
restoration or support claim. The reproducible probe reads the original
`D:/astro/PLACES/P529/MEGAFILE.HYP` and `FUNIV.MOV` directly; evidence identity
is `p529-save-original-20261021` in `evidence/p529-save-original.json`.
It uses only the cleanroom reader developed from 13 September 2026 onward.

The resource consumes exactly 282102 bytes and declares four locals, eleven
sprites, three programs, fourteen sounds and one movie, with no mouse rectangles.
The local declarations are `[1,0,16,0,0,15]`, `[1,1,1,0,0,1]`,
`[1,2,1,0,0,0]`, `[1,3,4,0,0,15]`. Their third fields are metadata;
the initial values are the fourth fields, all zero. Preserve values, known
flags and metadata independently rather than deriving the state from selector0.

Sprites1–7 have two frames each, sprite8 has sixteen and sprite9 has ten.
Sprites10/11 reference sprite9's frame collection and each resolve ten frames.
Keep their own serialized mutable fields: source9 is at(445,396), clone10 at
(456,396), clone11 at(467,396). Their visibility, layer, click flags and other
fields come from their own records, never from the frame owner. The evidence
records each source offset and own fields explicitly. The original loader
analysis recorded in SPRITES.md (load_place / CloneGameSprite12:012f /
SWCloneSprite7:02d8) supplies the existing clone-frame interpretation; this
probe independently checks the P529 records and does not execute that loader.

Selector local0 is clamped to0–15 by decrement/increment click scripts6/7.
Program0 selects sprite8's corresponding frame through sixteen explicit branches.
Program1 writes the three outcome digits and sets mask-local3 bits2,3,1,0 for
selector groups1–5,6–8,13–15,9–12 respectively. Selector0 is outside these
four outcome groups. Program2 chooses original movie ranges(start,length)
(0,359),(1029,232),(720,226),(360,359) and plays at(160,40).
The original movie header has timescale30 and duration1261 ticks; all segment
ranges fit. Selector6–8 explicitly sets local2 to1 before playback. Program1
checks local3==15 before custom25 and departure to P98; the exit click also
checks local2==1 before custom25. Global success/counter semantics need the
separate executable evidence and are not inferred from custom25's name.

No opcode20 external picture commits or opcode39 random-selection commands
occur in this resource. No sprite declares initial automatic framing or movement.
Nevertheless program2 issues opcode19 for sprites11,10,9 with20ms frame periods,
then stops them using-1, with a4000ms delayed first stop. Movie playback, audio,
these timer phases and delayed/queued actions prevent treating every frame as
a settled save boundary. Opcode41 calls queue programs0/1/2; positive command
delays up to8000ms are recorded with exact source offsets. Any future format
must preserve or explicitly exclude active work using verified native rules.

Next work: audit actual settled boundaries and preserve complete runner state,
clock/count, globals and all eleven independent mutable sprite records. Retain
the previous result digits independently of a changed selector. Determine whether
movie pixels persist after playback and how they are reconstructed; the absence
of external picture commands does not answer that. Preflight everything before
state mutation and reject unsupported work atomically.

Required continuation comparisons include all sixteen selector values, clamping
at both ends, repeated outcomes, all four outcome-mask bits, early success via
local2, completed mask15, selector changes after an outcome, unsolved exit,
fresh-process slots and malformed-state rejection. No such native continuation
or original-runtime execution was performed by this inventory.

## Residual movie-frame design audit, 21 October 2026

Read-only inspection of the current cleanroom engine and its local ScummVM
decoder establishes a separate native-state requirement. Paths below are relative
to `work/fresh-20260913/scummvm`; these line references identify the inspected
source revision and may move in future edits.

* `engines/astronomica/astronomica.cpp:1483` stops playback at segment end but
  retains `_movieFrame`. Lines1485–1490 replace that surface only after a
  non-null decoded frame and successful screen-format conversion.
  `presentScene()` at2016–2020 overlays the retained surface even when playback
  is stopped. The fields at `astronomica.h:129–135` include surface, coordinates,
  segment start and a frames-drawn count, but no last-presented sample identity.
* Opcode37 at `astronomica.cpp:2343–2347` changes the segment and seeks without
  replacing the retained surface. Playback starts at2354–2362. Therefore a
  decoder seek, including a test seek to segment end, does not identify the
  pixels still shown. The draw count is a count of commits, not a sample number.
* `video/video_decoder.cpp:256–263` sums current indices across video tracks.
  `seekToFrame()` at418–444 supports exactly one video track and converts its
  frame number to time before seeking. A successful seek does not display a
  frame: `seek()` at386–415 sets update state, while decode returns a surface
  through207–229.
* `video/qt_decoder.cpp:401–415` can seek beyond the last edit and return before
  assigning a new current sample. Lines463–469 can decode keyframe preroll
  internally without a displayed-surface commit. A later read of getCurFrame()
  consequently cannot recover the engine's last displayed frame reliably.
  `getFrameTime()` at612–625 explicitly carries a TODO about edit lists;
  frame-based seeking must be proved against FUNIV's actual track/edit layout.

Proposed future state: explicit residual-image absence/presence, asset identity,
last successfully presented absolute video sample index and its own x/y. Record
that index at the same successful commit as `_movieFrame.copyFrom`, after decode
and conversion, using validated single-video-track semantics. Never overwrite it
merely on seek, playback end, failed decode or failed conversion. Clear presence
where the surface is cleared (`closeMovie()`1397–1402 and full background
display1883–1886). Preserve absence on first entry. Keep this identity independent
of current selector, outcome locals and the decoder's current time or index:
selector0 can retain an older outcome, and selector changes do not decode frames.
Track stopped segment start/end separately if future playback can depend on them.

For a settled restore, first use a temporary stopped decoder loaded from the
validated original asset. Validate the recorded sample bounds and track/edit
profile, call seekToFrame(sample), then decodeNextFrame directly, without calling
the engine's updateMovie (which is gated by `_moviePlaying` and end-time checks).
Require a non-null frame, expected index and expected geometry, convert using
the same palette and screen format, and stage the resulting surface. Only after
all other save state passes validation should the staged surface, its position
and identity be committed atomically. The decode surface belongs to the decoder,
so retain a copy before disposing of it. No playback/audio start is necessary.
If edit-list seeking cannot reproduce the sample exactly, decode sequentially
from the start in the temporary decoder or retain validated pixel data; do not
substitute segment end minus one or presume the final frame was presented.

This is a design proposal, not implemented support. Required future evidence:
original MOV track/sample/edit inventory; equality of uninterrupted and restored
full-screen pixels at natural stops and after button redraw; explicit absence;
selector changes and repeated outcomes; a deliberately early displayed frame
followed by seek-to-end to prove identity is not inferred from the decoder;
fresh-process restoration; and atomic rejection of invalid sample/asset/geometry
states. No decoder or codec runtime was executed during this source audit.

## Original FUNIV atom/sample inventory, 21 October 2026

The probe now inventories the entire original MOV atom tree with byte offsets,
all stts/stsc/stsz/stss tables, every video sample's byte range and presentation
interval, and audio/video chunk ranges. Every range fits the original mdat.
There are exactly two tracks: one Cinepak(cvid) video track,320x240,24-bit,
253 samples in236 chunks; and one raw PCM audio track, mono8-bit,11025Hz,
463050 one-byte samples in84 chunks. Video has27 sync samples (one-based list
in the JSON). Both track matrices are identity.

Each track has exactly one nonempty edit with media time0 and rate1. Video
edit duration is1261 movie ticks at30Hz; audio duration is1260 ticks, exactly
42 seconds at its11025Hz media clock. The movie/video length is1261/30 seconds.
The mapping is linear and monotonic, with no edit-list discontinuities or offset.
This removes the specific edit-list ambiguity for frame seeking in this asset.

Video frame duration is **not constant**. Its complete stts(count,delta) table is
`(79,3),(1,123),(79,3),(1,123),(53,3),(1,69),(1,81),(37,3),(1,121)`
at30 ticks/second. Regular samples last0.1 seconds; long holds last2.3,2.7,
4.0333 or4.1 seconds. Use the stts prefix sum, never index multiplied by a
constant nominal rate. Segment intervals[start,end) overlap sample indices:

| Original range | Overlapping indices, zero-based | Last sample interval |
|---|---|---|
| 0–359 | 0–79 | [237,360) |
| 1029–1261 | 215–252 | [1140,1261) |
| 720–946 | 160–213 | [879,948) |
| 360–719 | 80–159 | [597,720) |

Every segment starts at a sample boundary. Three segment ends fall inside a
long-held sample; end tick minus one is a time, not a frame number. These are
eligible sample intervals from static tables, not proof of which frame the
engine actually committed under a particular scheduling history. An early
seek-to-end leaves whichever earlier surface was committed. The precise
last-presented index remains necessary.

For this asset's unique video track and simple edit, seekToFrame(recordedIndex)
followed by one explicit decode is a reasonable implementation candidate:
QuickTime seek handles keyframe preroll, and the frame-to-time table has a
strictly increasing prefix sum. It still requires native equality checks for
the resulting pixels/index and palette/format conversion. Sequential temporary
decode is a fallback, not a requirement demonstrated by these static tables.
No decoder, codec, game runtime or save restoration was executed here.
