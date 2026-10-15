# Exploration saves, 4 October 2026

Correction11 October: custom33 uses the TEXT reader9:4275, not the binary
reader described below. See HELP-RESEARCH.md and evidence/menu-services.json.
Both original formats are real; they must not be conflated.

Original ASTRO.EXE routines9:41b3-4275 and9:433e-43d0 write/read gamestat.
probe_save_layout.py executes the successful writer/reader bodies, recording
I/O at the original wrappers. Five roundtrips verify102 DWORDs/408 bytes:
place, completed-puzzle counter DS:0153, and100 global values. Original
P408/P409 saves substitute the previous place. The payload does not contain
local conditions, sprite state, pending scripts, movie time or random state.
The probe leaves original files and player saves untouched.

Native support currently saves only settled exploration screens (mode1),
outside a variant-puzzle sequence. It does not claim arbitrary mid-puzzle
restoration or import original gamestat files. F5 opens ScummVM's standard
menu; slots and launcher/command-line startup loading use the standard APIs.
Detection no longer disables launcher loading; the engine remains experimental.

Native version1:ASVM magic, LE version1, original-style102 DWORD payload,
FNV word checksum, followed by ScummVM's extended metadata/thumbnail.
The native prefix is420 bytes. The loader validates the entire prefix and
destination resource/mode before changing live globals. It rolls back globals
and completion count if scene loading fails. Loading an exploration save
clears an abandoned variant-puzzle sequence. The menu pauses both video and
the script clock; elapsed menu time does not advance puzzle deadlines.

Scoped native checks pass:100-value/counter roundtrip, all420 truncated
lengths,420 single-byte corruptions, valid-checksum unsupported destination,
disabled puzzle saves, video/clock pause, physical ScummVM slot, description
listing, startup state before test setup, and opening/closing the standard
menu. File tests use work/fresh-20260913/save-regression, never player slots.
The menu regression uses the builtin English theme; manual GUI/audio review
and saves inside puzzles remain unverified. Full-suite evidence is recorded
only after record_saves_checkpoint.py passes its guards.


## Exploration saves checkpoint, 4 October 2026

Native saves now preserve exploration location, completed-puzzle counter and
100 globals. F5 opens the standard ScummVM menu. Startup loading, slot listing,
metadata and menu opening/closing pass.840 truncated/corrupted payload checks
pass; unsupported destinations do not change the active game. Video and script
time pause in the menu. The full regression suite passes with these changes.
Saves are currently limited to settled mode1 exploration screens. No original
gamestat import or arbitrary mid-puzzle restoration is claimed. See
SAVE-RESEARCH.md.35 puzzle-route scenes remain verified; whole-game completion
is not measured. Windows help book and manual audiovisual playthrough remain.


## Advice checkpoint, 5 October 2026

P409 custom27/32 and world countdown are integrated and verified against
34800/108/10530 original cases. Native interaction, seven warning sounds,
expiry and continuous advice playback pass. Saves now use version2 (424
byte prefix) with clock epoch; inactive version1 remains readable. See
P409-RESEARCH.md. Four ending routes423/424/435..437 now play five movies and reach credits.
Full suite PASS; no global completion percentage claimed.


## Original text GAMESTAT import, 13 October 2026

The native engine reads gamestat/GAMESTAT from the selected game directory without modifying it. It validates all102 signed decimal values and the destination before enabling the original P1 saved-game choice. Custom33 restores the exploration scene, completed count and100 globals. Imported games can then use ordinary ScummVM saves. Original drive-root/current-directory fallbacks are not searched. The decoded snapshot stays stable during the menu interaction. Binary gamestat belongs to another original routine and is not imported.

Active countdown modes1/2 with nonzero global8 remain rejected. The original text writer stores the timestamp, not the current epoch or elapsed time. Two original countdown executions with the same saved timestamp produce different results at different current clocks; see legacy-resume-original.json. No timestamp is guessed from file dates and no countdown is reset. Only mode1 exploration destinations are admitted; arbitrary puzzle state cannot be reconstructed from the global-only file.

Build,15 original payload comparisons,102 token-boundary truncations, signed bounds, malformed/oversized inputs, file discovery, missing/invalid files, atomic rejection, original menu clicks, native resave, native slot startup, all781 help article openings and full WASAPI regression PASS. The fixture original file is unchanged. Syntactically valid altered numbers cannot be recognized as corruption because the original format has no checksum. No manual full-game completion claim.

Future puzzle saves: probe_puzzle_save_requirements.py inventories the 35 verified route resources, including local conditions, sprite frames/clones, automatic motion, movie references, script delays and custom handlers. Uninterpreted resource tails are hashed separately; they are not discarded or claimed decoded. This is a static inventory, not a save implementation. A scene reload plus globals cannot restore mutable sprite state, local conditions, pending work or per-puzzle/random state. Continuation tests must compare uninterrupted and restored runs at intermediate states. See evidence/puzzle-save-requirements.json.


## P508 settled question saves, 15 October 2026

Native version3 now saves P508 between questions, including six locals, all global/local values and their known/width metadata, full32-bit RNG, program epoch, branch state, previous place, completion count, sprite visibility/frame selection and ambient audio state. Pending actions, foreground speech, staged images, moving sprites and button pulses are excluded. Original data confirms18 opaque508x108 pictures at(67,354); the selected picture reconstructs the background without storing media. Startup scripts and introduction are skipped on load. Ambient music restarts at the beginning, not at the exact saved sample.

Three seeds and correct/wrong/mixed routes cover63 saved boundaries and 291 resumed answer steps, comparing screen pixels, script data, RNG, sound IDs/counts, destination and completion count with uninterrupted runs. Save/load/save data is stable except for the advancing clock. 2464 truncations,2464 byte corruptions and14 invalid checksummed states are rejected without changing the live state. Physical slot2 loads in a fresh process with the identical state/screen fingerprint and completes the seven remaining correct answers. Music/foreground guards and slot metadata pass. Exploration v1/v2 regressions, help and full WASAPI suite pass on the matching executable. Other puzzle saves remain unsupported.


## P505 settled question saves, 15 October 2026

Native v4 saves P505 between questions. It retains all script state, RNG, completion count, sprite visibility/frame selection, ambient state and entered flags for four sprite and ten rectangle hover targets. The original eight opaque 135x86 pictures at (254,362) reconstruct the current question. Loading skips startup and speech; remaining on a highlighted target does not replay its entry event. Foreground speech, queued work, staged pictures and button pulses exclude saving. Music restarts from its beginning.

Two seeds and correct/wrong/mixed routes verify 38 saved boundaries and their 38 successor states against uninterrupted play, including screen, script/RNG, sound count/ID and hover exit. All 38 unchanged-hover checks pass. 2472 truncations, 2472 byte corruptions and 16 checksummed invalid states reject atomically. Physical slot 3 restores in a fresh process with the same fingerprint and finishes six remaining answers. P508 v3 (63 boundaries, 291 resumed steps), exploration v1/v2, original GAMESTAT import, help and full WASAPI regressions pass on the matching build. These are automated tests; manual audiovisual verification and saves in other puzzles remain outstanding.
