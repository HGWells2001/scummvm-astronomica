# ScummVM music control, 18 October 2026

The engine sent every WAV to the Effects category, including the looping
S0.WAV background music. This made ScummVM's separate Music volume and mute
controls ineffective for those loops.

The native playSound() now selects Music for looping playback and Effects
for foreground playback. Both use the existing single SoundHandle: an
incoming foreground recording stops the loop, and resumeLoopAt() retains
its existing conditions and delay. The WAV decoder, resource IDs, timing,
stream ownership and original files are unchanged. Foreground recordings
are not reclassified as Speech without a resource-specific basis.

Evidence and scope:

- Original resources: S0.WAV and S1.WAV exist in P505, P508, P519, P524,
  P526 and P528. Their twelve SHA-256 hashes are recorded by the driver
  before and after playback. No WAV media is copied into the export.
- Native test: force Music muted at volume zero, Effects unmuted at full
  volume; start each original S0 loop and query the real mixer category,
  then replace it with S1 and verify the Effects category and absence of
  the Music channel. Restore and verify both previous controls afterward.
- This is automated channel/control verification with WASAPI. It does not
  measure PCM amplitude or replace manual listening. The assertion of the
  mixer category is evidence that the standard ScummVM Music control is
  applied to the loop; it is not evidence about original Win16 UI sliders.

Run check_audio_channel_regressions.py and finalize with
finish_audio_channels.py only after the same executable passes the
presentation, compatible save, previous-slot, help/import, movie and full
WASAPI suite. The final record is evidence/audio-channels-validation.json.
No save format changes are required.
