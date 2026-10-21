"""Summarize observation-only native P522 diagnostics; no save claims."""
from pathlib import Path
import hashlib,json,collections
work=Path(__file__).resolve().parent;stage=work/'p522-audit'
log=stage/'candidate-build/probe-boundaries.log';text=log.read_text()
fields='id route tag clock place selector state year yearArmed specialHit flying expired width0 height0 width1 height1 width2 height2 pending idle scriptsIdle clicksBlocked foreground completed screen480Hash background480Hash'.split()
rows={};polls=[];departures=[];expiries=[];route=-1
for line in text.splitlines():
 if 'Probe audit boundary: ' in line:
  parts=line.split('Probe audit boundary: ')[1].split();assert len(parts)==len(fields)
  r={k:(v if k=='tag' else int(v,16 if k.endswith('Hash') else 10)) for k,v in zip(fields,parts)}
  r['sprites']={};rows[r['id']]=r;route=r['route']
 elif 'Probe audit sprite: ' in line:
  n,i,count,*words=map(int,line.split('Probe audit sprite: ')[1].split());assert count==len(words)==27
  rows[n]['sprites'][i]=words
 elif 'Probe audit poll: ' in line:
  now,since,delay,due,count,index=map(int,line.split('Probe audit poll: ')[1].split())
  assert delay==200 and due==int(now-since>=delay) and index==6
  polls.append(dict(route=route,clock=now,since=since,delay=delay,due=due,pending_at_tick_entry=count,index=index))
 elif 'Probe audit departure: ' in line:departures.append(list(map(int,line.split('Probe audit departure: ')[1].split())))
 elif 'Probe audit expiry: ' in line:expiries.append(list(map(int,line.split('Probe audit expiry: ')[1].split())))
assert 'Astronomica probe boundary result: PASS' in text and 'FAIL' not in text and 'Log closed successfully' in text
assert set(r['route'] for r in rows.values())==set(range(4))
assert all(set(r['sprites'])==set(range(18)) for r in rows.values())
assert {r['selector'] for r in rows.values()} >= {1,2,3,4}
assert any(r['tag']=='failed-return' and r['state']==0 and not r['flying'] for r in rows.values())
assert any(r['flying'] for r in rows.values()) and any(r['specialHit'] for r in rows.values())
assert expiries and expiries[-1][1:]==[2003,1]
due=[p for p in polls if p['due']]
assert due and all(p['pending_at_tick_entry']>=1 for p in polls)
post=[r for r in rows.values() if r['tag']=='after-startup']
assert len(post)==4 and all(r['pending'] and not r['idle'] and not r['scriptsIdle'] for r in post)
proof=json.loads((stage/'candidate-build/proof.json').read_text())
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert proof['status']=='PASS' and proof['diagnostic_only'] and proof['canonical_files']==23
assert proof['candidate_exe_sha256']==digest(stage/'candidate-build/scummvm.exe')
assert Path(proof['probe_log']).resolve()==log.resolve()
for name,expected in proof['stage_sha256'].items():assert digest(stage/name)==expected
for name,expected in proof['canonical_sha256'].items():assert digest(work.parents[1]/'outputs/astronomica-cleanroom/engine/astronomica'/name)==expected
assert proof['regression_exe_sha256']==digest(work/'build/Releasex64/scummvm.exe')
assert 'Using SDL Audio Driver "dummy"' in text and 'Using SDL Video Driver "dummy"' in text

report=dict(date='2026-10-21',status='PASS',scope='Isolated real-engine observation audit only; original assets; SDL dummy audio/video; no serializer or save format',
 log=str(log),log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),build_proof=proof,
 observations=len(rows),route_counts=dict(collections.Counter(r['route'] for r in rows.values())),
 tags=dict(collections.Counter(r['tag'] for r in rows.values())),
 selectors=sorted({r['selector'] for r in rows.values()}),
 local_states=sorted({r['state'] for r in rows.values()}),
 calendar_years=sorted({r['year'] for r in rows.values()}),
 polling_observations=len(polls),poll_executions=len(due),
 observed_due_ages=sorted({p['clock']-p['since'] for p in due}),
 after_startup_pending_counts=[r['pending'] for r in post],
 ordinary_nonflight_active_motion=sum(r['state']==0 and r['sprites'][14][7] and r['sprites'][15][7] for r in rows.values()),
 hidden_probe_ordinary_motion=sum(not r['sprites'][16][0] and r['sprites'][16][7] and not r['flying'] for r in rows.values()),
 expiries=expiries,departures=departures,records=list(rows.values()),polls=polls,
 limits=['Four existing native representative routes and original motion fixtures; not all launch/calendar histories',
 'Controlled30ms test clock; positive success audio uses existing blocking behavior, other foreground samples may remain active',
 'Record clock is the next30ms tick after a step; poll logs use the actual tick execution clock',
 'No pending-job serialization, callback rebinding, malformed-payload checks, native audio backend, fresh-process restore or save coverage',
 'No original ASTRO.EXE runtime was executed'])
(stage/'probe-boundary-analysis.json').write_text(json.dumps(report,indent=2)+'\n')
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=json.loads((stage/'BASE.json').read_text())
sha='\n'.join(f'| {n} | `{base[n]}` | `{digest(stage/n)}` |' for n in base)
(stage/'AUDIT.md').write_text(f'''# P522 native observation audit, 21 October 2026

PASS on an isolated copy of the current real v15 engine, using original game
resources and SDL dummy audio/video. No serializer, format, integration or save
support was added. Canonical23 source files and the main executable stayed
unchanged during build/run, as recorded in candidate-build/proof.json.

Candidate SHA256: `{proof['candidate_exe_sha256']}`.
Main baseline SHA256: `{proof['regression_exe_sha256']}`.

| Source | BASE canonical SHA256 | Staged SHA256 |
|---|---|---|
{sha}

The diagnostic copies the existing verifyP522Puzzle route logic, adding only
observations. It retains the real original-motion fixture checks, all four
selectors, failed1991 launch/recovery, successful1992 launch, already-completed
1994 launch, year2003 expiry and voluntary exit. No gameplay algorithm changes.

There are{len(rows)} complete observations, each with ProbeMotion calendar/flags,
geometry, two locals, clock, pending/idle/script-idle/click/audio fields, full480-row
screen/background hashes and eighteen27-word sprite records. The JSON contains
all records and{len(polls)} actual recurring-poll checks, including{len(due)} executions.
All four after-startup observations have pending work and idle/scriptsIdle=false.
Recorded due ages are{report['observed_due_ages']}ms for the original200ms delay.
The30ms step and queued call pass quantize execution; this is not evidence that
the original request itself uses a different period.

Ordinary no-flight phases still advance Earth/Mars, and hidden inactive probe
movement is observed in{report['hidden_probe_ordinary_motion']} snapshots. Year/armed
edges and flight-state/special-hit transitions are sampled. Expiry2003 is captured
immediately before scene change, since loadPlace resets ProbeMotion afterward.
This confirms that flight-idle is not sufficient for a static or empty-queue save.

Future work needs an explicit trusted recurring-poll continuation/epoch and all
active motion/frame phases, rather than dropping pending work or rerunning setup.
The static original-resource contract remains in p522-research/P522-SAVE-PLAN.md.
No roundtrip, restored successor, rejection atomicity, physical slot, WASAPI or
manual playthrough is proved by these observations.

Reproduce from the workspace root with the bundled Python interpreter:
`work/fresh-20260913/build_probe_audit.py`, then
`work/fresh-20260913/analyze_probe_audit.py`.
The one-time prepare_probe_audit.py intentionally refuses an existing directory.
Source/object/PDB/library/executable/log output stays in p522-audit/candidate-build.
''')
print(json.dumps({k:report[k] for k in ['status','observations','route_counts','polling_observations','poll_executions','observed_due_ages','after_startup_pending_counts','hidden_probe_ordinary_motion']},indent=2))
