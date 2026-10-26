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


## P519 native saves, 16 October 2026

Native v5 now saves idle P519 selections and partial solutions. It retains all script state and RNG, clock/count, 27 sprite frames and visibility, ten rectangle hover flags and ambient state. Two original image identities reconstruct the full background: the latest large image and optional subsequent small image. Image identities change only when display commits; a new large image clears the small record. Loading skips startup and speech. Foreground audio, queued work, button pulses and staged pictures exclude saving. Ambient music restarts from its beginning.

Tests pass 74 gameplay successor comparisons (all 25 detector/target pairs, both solve orders, repeated target and unsolved exit), plus 30 separate native image-composition round trips. All compare script/RNG, background/screen pixels, sprite frames, hover state and applicable sound IDs/counts. 2584 truncations, 2584 byte corruptions and 18 checksummed invalid states reject without changing live state. Physical slot 4 loads in a fresh process with an identical fingerprint and completes five pairings after the wrong Sun selection. P505/P508 full save tests, previous-build v3/v4 slots, exploration saves, original import, help and full WASAPI suite pass. This remains automated evidence; manual audiovisual playthrough and other puzzle saves are outstanding.


## P524 native saves, 18 October 2026

Native v6 saves settled P524 questions with all script/RNG state, previous scene, clock/count, 32 sprite frames/visibility and the continuing Triton animation epoch and parameters. Mentor return preserves the additional known local values. The original committed picture is reconstructed. The Moon follows all eight random choices; the earlier preparation calling it an initial stage was incorrect. Startup and foreground speech are skipped on load; ambient music restarts from the beginning.

Validation: 72 round trips (23 gameplay successors, one post-help identity, 48 animation cases), all eight animation frames at 199/200/2200ms with ordinary and wrapping clocks, two solve routes, third-error exit, voluntary exit, mentor return and fresh-process slot5 completion. 2612 truncations, 2612 byte corruptions and 21 checksummed invalid states reject atomically. Full P505/P508/P519 saves, prior-build v3/v4/v5 slots, exploration v1/v2, import, help and WASAPI suite pass on the same build. These are automated results, not manual audiovisual confirmation.


## P526 native saves, 18 October 2026

Native v7 saves settled P526 entry, stopped experiments and answered states. It retains the full runner/RNG, clock/count, 23 sprite records with render/center positions, animation and movement epochs, orbital parameters and flags, committed picture and six hover bits. Orbit travel, foreground audio, queued work and staged images exclude saving. Ambient music restarts at its beginning.

Verified on one matching build: 686 round trips (33 gameplay successors, five identities, 216 animation comparisons, 432 synthetic phase/answer cases), 4956 truncations, 4956 byte corruptions and 25 checksummed invalid states. A physical slot6 loads in a fresh process and completes all remaining questions. The separate native audit observes 33 boundaries on real routes. Full v1-v6 compatibility, previous-build v3-v6 slots, exploration, import, help and WASAPI regressions pass. This is automated evidence, not a full manual audiovisual playthrough.


## Full original frame, 18 October 2026

Ordinary presentation now preserves all 640x480 original pixels. The diagnostic strip is opt-in via astronomica_debug_overlay. The old strip covered rows 456-479, including five rows of a P528 picture. Twelve scene comparisons, 855 original picture pixels, optional-strip activation and restoration pass. All existing v1-v7 saves, prior-build v3-v7 slots, help/import and full WASAPI regressions pass on the same executable. Existing legacy fingerprints intentionally retain their 456-row scope; the new presentation test checks all 480 rows.


## Separate music control, 18 October 2026

Looping background WAVs now use the ScummVM Music channel. Foreground recordings retain the Effects channel and replace the active loop as before. Six scenes pass with Music muted and volume zero, Effects audible, and all original controls restored afterward. Twelve original S0/S1 WAV hashes are unchanged. Presentation, compatible v1-v7 saves, prior-build slots, help/import and the full WASAPI suite pass on the same executable. This is automated channel/control verification; manual listening remains outstanding. See AUDIO-CHANNELS.md and evidence/audio-channels-validation.json.


## P528 native saves, 18 October 2026

Native v8 saves settled P528 states with full runner/RNG, clock/count, nine sprite records, partial eclipse flags, current image pair and retained tall-moon history. Tests cover160 reachable abstract states and640 round trips/successors, including six completion edges and160 exits, using full480-row pixel hashes. 3444 truncations,3444 byte corruptions and30 checksummed invalid states reject atomically. Slot7 loads in a fresh process, retains the old moon row and completes the remaining eclipse with first-success counting. Versions1-7, prior-build slots, presentation/audio controls, help/import and WASAPI regressions pass on the same executable. No whole-game completion percentage is inferred.


## P530 native saves,19 October2026

Native v9 retains14 locals and full runner/RNG,29 sprite records including hidden settled indicator positions, clock/count and the last picture or absence. 800 round trips across14 randomized routes cover five scenarios at every round, all25 pictures, all six placement permutations, wrong/repeated answers and unsolved exit. Slot8 loads in a fresh process with a partial component assembly and prior-round picture, then completes the remaining random rounds without increasing the counter, as in the original. 5604 truncations,5604 byte corruptions and31 checksummed invalid states reject atomically. Versions1-8, previous-build slots, full-frame presentation, music controls, help/import and WASAPI pass on the same executable.


## Six-scene custom17 saves,19 October2026

Native v10 saves P506/P531/P532/P533/P534/P535 partial solutions, all runner data and the original round/mask process statics. 1222 round trips and successors across 15 randomized solve routes cover all six scenes at each of four stages, including 4 initial-scene repeats. Slot9 resumes a partial solution at round2 in a fresh process, then finishes the remaining nonrepeating rounds and first completion count. Voluntary exit/reentry retains the original statics. All23736 truncations,23736 single-byte corruptions and192 checksummed invalid payloads reject without changing state. The P509 entry-history regression also passes for P524/P526/P528/P530: previously retained unknown locals blocked saving. Four natural entries and12 inert-value extremes now round-trip, while8 invalid metadata cases still reject. v6-v9 payload layouts remain unchanged. v1-v9 compatibility, prior-build slots, normal P1 launcher startup, full graphics/audio/help/import/WASAPI suite pass on the same executable.


## P513 native saves,19 October2026

Native v11 retains six locals/RNG,32 complete sprite records, stopped hidden photon endpoint and old digit/result state, cube image and clock/count. 728 native round trips/successors cover five solve/exit routes, all14 scenarios, nine photon results, bounds and silent first/repeated success. Slot10 resumes after two correct answers in a fresh process and finishes with the original count. All5928 truncations,5928 byte corruptions and37 checksummed invalid states reject without changing state. Versions1-10, old slots, cross-puzzle entry correction, full graphics/audio/help/import/WASAPI and normal launcher startup pass on the same build.


## P517 aurora saves,19 October2026

Native v12 retains both locals, all eleven sprite records, the active aurora timer and stopped inactive phases, background, gauge and marker. 2278 native round trips/successors cover all14 settings,2240 animation cases, both controls, minimum clamp and first/repeated completion count. Slot11 resumes setting12 with active/stopped phases in a fresh process and completes with the original count. All3660 truncations,3660 byte corruptions and45 checksummed invalid states reject atomically. Versions1-11, old slots, full graphics/audio/help/import/WASAPI and normal launcher startup pass on the same build.


## Unreproduced test-file truncation,20 October2026

During validation of the rebuilt v12 executable, test slot5 was observed at16384 bytes with its ASVM payload and SVMCR header present but the extended metadata footer absent. Native P524 continuation and fresh-process load passed; metadata listing correctly failed. Repeating the exact targeted test produced a complete41085-byte slot and passed listing and fresh-process continuation. The cause is not established and no fix is claimed. Core Engine::saveGameState currently returns the payload result without checking the finalized stream error; this is a possible detection gap, not evidence of the cause. Personal saves were not used. Preserve a failing physical file before rerunning if this recurs.


## Construction saves,20 October2026

Native v13 retains both P515/P536 construction scenes and the dormant custom17 round/mask and comet orientation. 613 round trips/successors and420 control matrix cases cover six routes, all five designs, early Launch, no-picture states, partial parts and cap recovery. Physical slot12 resumes partial P536 design5 in a fresh process, preserves dormant round2 and applies first completion exactly once. P515 success remains the original no-op. All8960 truncations,8960 byte corruptions and52 checksummed invalid states reject atomically. Versions1-12 and the complete WASAPI regression pass on this build.


## P537 rocket saves,21 October2026

Version14 retains all48 sprites, selector, prior digits/gauges, stopped motion epoch and dormant cross-puzzle state. 577 exact round trips/successors and fresh-process slot13 pass; all7680 truncations,7680 corruptions and48 checksummed invalid states reject atomically. Full native WASAPI suite and normal startup pass with versions1-13 retained.


## P529 universe saves,21 October2026

Version15 preserves original movie and readout history independently of selector and attempted segment, plus all eleven sprites, four locals, mask, dormant custom17 and comet phase. 188 exact round trips/successors and physical slot14 in a fresh process pass. All3684 truncations,3684 corruptions and25 checksummed invalid states reject atomically. Original253-frame reconstruction, zero-frame history, natural voice completion, Music restart and the full native WASAPI regression pass on the same build.


## P522 nonflight probe saves,22 October2026

Version16 preserves ordinary P522 state across 31 measured native round trips/successors, with a fresh-process slot15 and unchanged verified v15 slot compatibility. The original recurring200ms poll epoch, active orbit/frame phases and calendar are retained. Flight, expiry, special-hit success and the deferred index0 phase remain excluded. All4472 truncations and4472 byte corruptions reject atomically. The complete compatible native WASAPI suite passes on the same executable.


## P514 rendezvous saves,22 October2026

Version17 preserves settled P514 state across 87 measured native round trips/successors, with a fresh-process slot16 and unchanged verified v16 slot compatibility. Active orbit, frame and fuel timers, all16 speeds and hidden failed-docking history are retained. Queued launch, successful-docking and fuel-exhaustion transitions remain excluded. All4632 truncations and4632 byte corruptions reject atomically. The complete compatible native WASAPI suite passes on the same executable.


## P518 planet saves,22 October2026

Version18 preserves P518 idle-script boundaries across 59 measured native round trips/successors, with a fresh-process slot17 and unchanged verified v17 slot compatibility. Planet motion, random selection, hidden failed-attempt history and timer phases are retained. Queued commands, foreground audio and transitions remain excluded. All6184 truncations and6184 byte corruptions reject atomically. The complete compatible native WASAPI suite passes on the same executable.


## P521 saves,23 October2026

Version19 preserves P521 idle-script boundaries across 32 measured native round trips/successors, with a fresh-process slot18 and unchanged verified v18 slot compatibility. Retained external image, hidden fragment history, animation/timer phases and inherited runner values are preserved. Queued commands, flash, foreground audio and transitions remain excluded. All5392 truncations and5392 byte corruptions reject atomically. The complete compatible native WASAPI suite passes on the same executable.


## P509 saves,24 October2026

Version20 preserves 59 measured ordinary P509 boundaries with the original pending narrator and exact timed continuation. Fresh-process slot19 and unchanged genuine frozen v19 compatibility pass. Retained sky identity, hidden bounce and timer epochs are preserved. Foreground audio, other queued work and phase3 exits remain excluded. All4540 truncations and4540 byte corruptions reject atomically. Complete same-build WASAPI suite PASS.


## P511 saves,25 October2026

Version21 preserves 109 measured ordinary P511 boundaries with retained cloud image, independent frame/range history and exact timed continuation. Fresh-process slot20 and unchanged genuine frozen v20 compatibility pass. Original frame ranges, hidden animations and timer epochs are preserved. Foreground audio, queued work and success transitions remain excluded. All6256 truncations and6256 byte corruptions reject atomically. Complete same-build WASAPI suite PASS.


## P516 saves,25 October2026

Version22 preserves 86 measured quiet local2=0 P516 boundaries with active orbits and a hidden stopped projectile. Handoff frame/epoch history, hidden stopped motion, all605runner values, CometMotion and collision geometry are retained. Active flight, aborted unproved histories, local2=1,stopped moons,pending work,foreground audio and success/explosion transitions remain excluded. Fresh-process slot21,unchanged genuine frozen v21slot20,6944truncations and6944corruptions,and the complete native WASAPI suite PASS.


## P527 saves,25 October2026

Version23 preserves quiet stopped-movie boundaries, selection and seen history, independent retained movie sample and all605runner words. All1105native frame reconstructions,fresh-process slot22,unchanged genuine frozen v22slot21 and the complete WASAPI suite PASS. Active playback,queued work and foreground audio remain excluded.


## P502 saves,26 October2026

Version24 preserves quiet nonflight choices and hidden stopped failed-return history, all605runner words,CometMotion scratch and dormant Jupiter geometry. Fresh-process slot23, all6728truncations/corruptions and genuine frozen v23slot22 compatibility plus complete native WASAPI suite PASS. Active flight,success transitions,pending work and foreground audio remain excluded.
