"""Verify actual quiet P503 saves, original failure history and fresh-process route."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,time
ap=argparse.ArgumentParser();ap.add_argument('--exe',type=Path);ap.add_argument('--tag',default='');ap.add_argument('--dummy-audio',action='store_true');ap.add_argument('--variant-slot',type=Path);args=ap.parse_args()
assert not args.tag or re.fullmatch(r'[a-z0-9-]+',args.tag)
assert not (args.exe or args.dummy_audio or args.variant_slot) or args.tag
base=Path(__file__).resolve().parent;exe=args.exe.resolve() if args.exe else base/'build/Releasex64/scummvm.exe'
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected=d(exe);prefix=args.tag+'-' if args.tag else ''
cfg=base/(prefix+'verify-p503-saves.ini');savepath=base/(prefix+'p503-save-regression');savepath.mkdir(exist_ok=True)
source=args.variant_slot.resolve() if args.variant_slot else base/'variant-save-regression/astro-verify.009';alias=savepath/'astro-verify.099';source_sha=d(source);assert source!=alias;shutil.copyfile(source,alias)
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_p503_saves=true\nastronomica_verify_save_files=true\nsavepath='+savepath.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
if args.dummy_audio:env['SDL_AUDIODRIVER']='dummy'
driver='dummy' if args.dummy_audio else 'wasapi';common=[str(exe),'--config='+str(cfg),'--extrapath='+str(base/'fonts'),'--savepath='+str(savepath),'--debuglevel=1']
assets={p.name:d(p) for p in sorted(Path('D:/astro/PLACES/P503').iterdir()) if p.is_file()};assert all(n in assets for n in ('S0.WAV','S1.WAV','MEGAFILE.HYP'))
fps=[];coverage={}
for name,extra in [('p503-saves',[]),('p503-saves-startup',['--save-slot=24'])]:
 assert d(exe)==expected;log=base/(prefix+name+'.log');console=base/(prefix+name+'-console.log');log.write_text('')
 with console.open('w') as output:
  p=subprocess.Popen(common+['--logfile='+str(log)]+extra+['astro-verify'],env=env,cwd=base,stdout=output,stderr=subprocess.STDOUT,text=True);started=time.monotonic()
  try:
   while p.poll() is None and time.monotonic()-started<1800:
    if 'FAIL' in log.read_text():p.terminate();break
    time.sleep(.25)
   if p.poll() is None:p.terminate()
   p.wait(timeout=10)
  finally:
   if p.poll() is None:p.terminate();p.wait(timeout=10)
 text=log.read_text();print(name,'exit',p.returncode,flush=True)
 if p.returncode or 'FAIL' in text:print(text[-7000:]+console.read_text()[-1200:]);raise AssertionError(name)
 assert 'P503 save verification: PASS' in text and text.rstrip().endswith('--- Log closed successfully.')
 assert re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==[driver] and 'Using SDL Video Driver "dummy"' in text
 found=re.findall(r'P503 slot fingerprint: ([0-9a-f]{8})',text);assert len(found)==1;fps.append(found[0])
 if extra:assert 'P503 startup save: PASS' in text
 else:
  rows=re.findall(r'P503 saves: PASS \((\d+) boundaries, (\d+) history boundaries, (\d+) dormant boundaries, (\d+) ordinary boundaries, (\d+) busy rejections\)',text);assert len(rows)==1
  coverage.update(zip(('boundaries','history_boundaries','dormant_boundaries','ordinary_boundaries','busy_rejections'),map(int,rows[0])))
  rows=re.findall(r'P503 history coverage: PASS \((\d+) prelaunch boundaries, (\d+) low failure boundaries, (\d+) high failure boundaries, (\d+) changed control histories, (\d+) retained explosion boundaries, (\d+) private cache boundaries, (\d+) successor checks, (\d+) future outcome checks\)',text);assert len(rows)==1
  coverage.update(zip(('prelaunch_boundaries','low_failure_boundaries','high_failure_boundaries','changed_control_history','retained_explosion_boundaries','private_cache_boundaries','successor_checks','future_outcome_checks'),map(int,rows[0])))
  rows=re.findall(r'P503 controls coverage: PASS \((\d+) target settings, (\d+) direction settings, (\d+) speed settings, (\d+) failed launch combinations\)',text);assert len(rows)==1
  coverage.update(zip(('target_settings','direction_settings','speed_settings','failed_launch_combinations'),map(int,rows[0])));assert (coverage['direction_settings'],coverage['speed_settings'],coverage['failed_launch_combinations'])==(4,16,312)
  rows=re.findall(r'P503 accepted masks: PASS \((\d+) proper solved masks, (\d+) first kind4 transitions\)',text);assert len(rows)==1;coverage.update(zip(('proper_solved_masks','first_kind4_transitions'),map(int,rows[0])));assert coverage['proper_solved_masks']==30 and coverage['first_kind4_transitions']==5
  rows=re.findall(r'P503 orbit coverage: PASS \((\d+) partial boundaries, (\d+) handoffs, (\d+) excluded solved failure histories\)',text);assert len(rows)==1;coverage.update(zip(('partial_boundaries','handoffs','excluded_solved_failure_histories'),map(int,rows[0])));assert coverage['excluded_solved_failure_histories']==5 and coverage['target_settings']==5
  rows=re.findall(r'P503 timer epochs: PASS \((\d+) independent frame movement and uint32 wrap cases\)',text);assert len(rows)==1;coverage['timer_cases']=int(rows[0])
  rows=re.findall(r'P503 rejection verification: PASS \((\d+) truncations, (\d+) corruptions, (\d+) invalid states, extended atomic state\)',text);assert len(rows)==1;coverage.update(zip(('truncations','corruptions','invalid_states'),map(int,rows[0])))
  assert coverage['truncations']==coverage['corruptions']==8132 and coverage['future_outcome_checks']>=2 and all(n>0 for n in coverage.values())
  assert text.count('P503 natural voice end: PASS')==text.count('P503 Music restart: PASS')==1;coverage.update(extended_atomic_state=True,natural_voice_ends=1,music_restart=True)
 assert d(exe)==expected;print(text[-1800:],flush=True)
assert fps[0]==fps[1],fps
p=subprocess.run(common+['--list-saves'],env=env,cwd=base,capture_output=True,text=True,timeout=60);listed=p.returncode==0 and 'P503 continuation regression' in p.stdout;assert listed,p.stdout+p.stderr
(base/(prefix+'p503-saves-list.log')).write_text(p.stdout+p.stderr)
assert d(source)==d(alias)==source_sha and d(exe)==expected
assert assets=={p.name:d(p) for p in sorted(Path('D:/astro/PLACES/P503').iterdir()) if p.is_file()}
proof=dict(date='2026-10-26',status='PASS',scope='quiet_p503_partial_orbits',payload_bytes=8132,slot=24,audio_driver='dummy' if args.dummy_audio else 'native',actual_audio_driver=driver,diagnostic=bool(args.tag),exe_sha256=expected,metadata_listed=listed,fresh_process_fingerprint=fps[1],original_wav_sha256={'P503/'+k:v for k,v in assets.items() if k.upper().endswith('.WAV')},original_assets_sha256=assets,variant_fixture_sha256=source_sha,variant_fixture_unchanged=True,**coverage)
(base/(prefix+'p503-save-proof.json')).write_text(json.dumps(proof,indent=2));print('P503 measured save coverage, full original route continuation, fresh process and metadata PASS',flush=True)
