"""Update current notes only after both bounded native qualifications pass."""
from pathlib import Path
import json
w=Path(__file__).resolve().parent;o=w.parents[1]/'outputs/astronomica-cleanroom'
assert json.loads((w/'navigation-music-native-nov18b/proof.json').read_text())['status']=='ORIGINAL_NAVIGATION_ACTIVE_MUSIC_PASS'
assert json.loads((w/'navigation-music-requirements-nov18b/proof.json').read_text())['status']=='CURRENT_NAVIGATION_MUSIC_REQUIREMENT_MAP_PASS'
assert json.loads((w/'p419-foreground-native-nov18b/proof.json').read_text())['status']=='ORIGINAL_P419_REPEATED_FOREGROUND_NAVIGATION_PASS'
note='''
## Original navigation with active Music — 18 November 2026

All 760 positive literal NAV references were tested using actual arrow and keypad handlers. Nine additional permitted-gate fixtures make 1,538 native cases. Source rooms are loaded directly with controlled globals, then the unchanged normal frame pump runs with the original Music stream. All destinations and global57 results match the original executable instruction oracle. Same-region transitions retain the stream owner; region changes select the expected loop. Denied gates reach P429 without a room Music stream. P31 has no positive NAV reference and remains covered by the separate 306-room frame sweep.

The versioned catalogue now links this bounded current-source evidence to 760 literal-route candidate requirements. The 364 script-place candidates, natural reachability, sprite-click histories and other global/timing combinations are not inferred. This does not close A03 or measure whole-game completion.

P419's original entry0 explicitly self-calls with delay100 when global52 is1, dispatching local S1 repeatedly. Its role remains unclassified as speech or effect. A native controlled check observes the repeated foreground dispatch, then uses the actual Left handler to reach P358 and verifies advancing Music after cleanup. With global52=0, P419 Music advances without that local dispatch. Earlier one-shot expectations were rejected; no production audio change was made for this case.

All native qualification processes exit naturally. These observer builds are isolated and are not deployed. Receipts export hashes and bounded counts, without original assets or raw logs.
'''
p=o/'EXPLORATION-VERIFICATION-NOV18.md';s=p.read_text();assert '## Original navigation with active Music'not in s;p.write_text(s+note)
p=o/'BEHAVIOR-REQUIREMENTS.md';s=p.read_text();assert '## Current navigation Music boundaries'not in s;p.write_text(s+'''
## Current navigation Music boundaries

The November18 map links all760 literal navigation candidates to1,538 current-source observer cases using real arrow/keypad handlers and active Music through the ordinary frame loop. Original NAV bytes identify each route; original transition instructions determine the destination and global57 result. The per-case source, controlled permit, expected track and native log line stay local. The exported receipt binds all input hashes and records bounded totals.

The305 source rooms with positive NAV routes cover all760 references; mode1 P31 has no such route. Nine permitted-gate fixtures supplement the normal zero-permit cases. This does not establish natural reachability, sprite-click navigation, exhaustive global/timing histories or the364 script-place outcomes. Candidate requirements remain incomplete as full behavior claims. A03 and full project completion remain unmeasured.

```text
python outputs/astronomica-cleanroom/map_navigation_music_requirements_nov18.py --workspace work/fresh-20260913 --out work/fresh-20260913/navigation-music-requirements-nov18b
```
''')
p=o/'NEXT-STEPS.md';s=p.read_text();p.write_text('''# Current checkpoint — 18 November 2026

Exploration Music is audible in the normal P103 player, confirmed by the user. All306 mode1 rooms pass the actual frame-loop stream sweep. All760 literal NAV references pass1,538 actual arrow/keypad handler cases with active Music and an independent original transition oracle. P419 repeated local foreground playback and navigation cleanup pass separately. See EXPLORATION-VERIFICATION-NOV18.md and work/fresh-20260913/SESSION-20261118.md.

Production engine/core/executable are unchanged from the verified P513 release. The workspace launcher now retains launch errors and writes avvio-console.log; its original one-second closure did not reproduce directly. Do not deploy observer executables. Ignore the personal installation.

Next: investigate the364 script-place outcome candidates and natural reachability with primary resource/runtime evidence; do not relabel controlled navigation fixtures as full gameplay coverage. Exact help typography and a recorded full manual audiovisual playthrough remain open. Fixed acceptance7/10 is not a total development percentage.

The latest user request authorizes forced-app shutdown only after the requested quota reserve, GitHub backup and natural completion of every suite. Earlier no-shutdown statements below are historical. Do not reuse the executed November17 shutdown record. Do not forcibly terminate suites or redeem reset credits.

---

# Historical checkpoints follow

'''+s)
p=w/'SESSION-20261118.md';s=p.read_text();p.write_text(s+'''
## Completed navigation qualification

navigation-music-native-nov18b/proof.json:1,538/1,538 current-source handler cases over760 original NAV references,305 source rooms,9 extra permitted gates,two keyboard variants. P31 has no NAV edges. navigation-music-requirements-nov18b/proof.json links760 candidate route cells without reachability/full-behavior claims.

p419-foreground-native-nov18b/proof.json: original global52 states0/1 and actual Left→P358 cleanup pass. Entry0 explicitly self-calls with delay100 and repeatedly dispatches localS1 when global52=1. Do not classify it as narration or force a one-shot policy without further evidence. Earlier entry observer tests had an invalid one-shot hypothesis; their failed outputs are retained. No production engine change.

All new native checks completed naturally. Publish through publish_navigation_music_nov18.py; continuation seal navigation-music-source-extension-seal-nov18.json. Remaining source/script-place reachability and A08/A09 work are open.
''')
print('CURRENT_NAVIGATION_NOTES_UPDATED')
