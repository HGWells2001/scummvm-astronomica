# Exploration music and workspace launcher — 18 November 2026

The user confirmed hearing background music in the normal interactive exploration player opened at P103: “Sì, ora la sento”. This used the current verified executable, without diagnostic flags, with an isolated configuration. The player exited normally. This confirms this room's audible playback, not every room or a complete audiovisual playthrough.

A separate observer build checked all 306 original mode1 exploration rooms through the actual frame loop. Every room had the expected active, advancing Music stream. The test used controlled direct room loads and muted WASAPI output; it does not prove every navigation route or acoustic playback. The observer is not the deployed game. The production engine and executable remain unchanged.

The workspace launcher now records its executable, exit code and console output in `userdata/astronomica/avvio-console.log`. Missing prerequisites and failed launches keep an error visible. Native startup, paths containing spaces, failure handling and preservation of existing configuration passed. The reported one-second closure did not reproduce during direct invocation; its original cause remains unconfirmed.

The personal ScummVM installation remains outside this work. No original game assets, saves, screenshots or raw player logs are published.

Fixed acceptance remains 7/10. A03 exhaustive behavior coverage, A08 exact help typography and A09 a recorded full manual audiovisual playthrough remain open. Total project completion has no reliable percentage.
