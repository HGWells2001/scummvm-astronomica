"""Exercise real universe save boundaries and a fresh-process slot14 continuation."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,time
def frame_audit(proof_path,exe_sha256):
 try:
  proof_bytes=proof_path.read_bytes();proof=json.loads(proof_bytes)
  if proof.get('status')!='PASS':raise ValueError('audit status is not PASS')
  if proof.get('exe_sha256',proof.get('candidate_exe_sha256'))!=exe_sha256:raise ValueError('audit executable SHA256 does not match --exe')
  log_path=Path(proof['universe_log'])
  if not log_path.is_absolute():log_path=proof_path.parent/log_path
  log_bytes=log_path.read_bytes();log=log_bytes.decode('utf-8-sig')
  if 'FAIL' in log or not log.rstrip().endswith('--- Log closed successfully.'):
   raise ValueError('audit log failed or did not close successfully')
  counts=re.findall(r'Astronomica universe original-frame reconstruction: PASS \((\d+) sequential versus seekToFrame native pixel comparisons; stopped decoders\)',log)
  if len(counts)!=1 or int(counts[0])!=253:raise ValueError('audit must contain exactly one 253-frame sequential-versus-seek PASS')
  return dict(movie_samples=int(counts[0]),movie_audit_proof_sha256=hashlib.sha256(proof_bytes).hexdigest(),movie_audit_log_sha256=hashlib.sha256(log_bytes).hexdigest())
 except (OSError,ValueError,KeyError,TypeError) as exc:
  raise ValueError(f'Invalid or missing frame audit {proof_path}: {exc}; provide --frame-audit-proof PATH for the same executable') from exc

ap=argparse.ArgumentParser();ap.add_argument('--exe',type=Path);ap.add_argument('--frame-audit-proof',type=Path);ap.add_argument('--tag',default='');ap.add_argument('--dummy-audio',action='store_true');ap.add_argument('--variant-slot',type=Path);args=ap.parse_args()
assert not args.tag or re.fullmatch(r'[a-z0-9-]+',args.tag)
assert not (args.exe or args.dummy_audio or args.variant_slot) or args.tag,'Diagnostic overrides require isolated output names'
base=Path('work/fresh-20260913').resolve()
exe=args.exe.resolve() if args.exe else base/'build/Releasex64/scummvm.exe'
expected_exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()
try:movie_audit=frame_audit(args.frame_audit_proof.resolve() if args.frame_audit_proof else exe.parent/'proof.json',expected_exe_sha256)
except (OSError,ValueError) as exc:ap.error(str(exc))
prefix=args.tag+'-' if args.tag else '';cfg=base/(prefix+'verify-universe-saves.ini');savepath=base/(prefix+'universe-save-regression');savepath.mkdir(exist_ok=True)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=args.variant_slot.resolve() if args.variant_slot else base/'variant-save-regression/astro-verify.009';alias=savepath/'astro-verify.099'
source_hash=digest(source);shutil.copyfile(source,alias)
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_universe_saves=true\nastronomica_verify_save_files=true\nsavepath='+savepath.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
if args.dummy_audio:env['SDL_AUDIODRIVER']='dummy'
common=[str(args.exe.resolve() if args.exe else base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--extrapath='+str(base/'fonts'),'--savepath='+str(savepath),'--debuglevel=1']
audio={f'P{scene}/{name}':digest(Path(f'D:/astro/PLACES/P{scene}')/name) for scene in (529,) for name in ('S0.WAV','S1.WAV')}
hashes=[];coverage=None;extra_coverage=None;audio_drivers=[]
for name,extra in [('universe-saves',[]),('universe-saves-startup',['--save-slot=14'])]:
 log=base/(prefix+name+'.log');log.write_text('');console=base/(prefix+name+'-console.log')
 with console.open('w') as output:
  p=subprocess.Popen(common+['--logfile='+str(log)]+extra+['astro-verify'],env=env,cwd=base,stdout=output,stderr=subprocess.STDOUT,text=True)
  started=time.monotonic()
  try:
   while p.poll() is None and time.monotonic()-started<1800:
    if 'FAIL' in log.read_text():p.terminate();break
    time.sleep(0.25)
   if p.poll() is None:p.terminate()
   p.wait(timeout=10)
  finally:
   if p.poll() is None:p.terminate();p.wait(timeout=10)
 s=log.read_text();print(name,'exit',p.returncode,flush=True)
 if p.returncode or 'FAIL' in s:print(s[-6500:]+console.read_text()[-1000:]);raise AssertionError(name)
 assert 'universe save verification: PASS' in s and 'Log closed successfully' in s
 audio_driver=re.findall(r'Using SDL Audio Driver "([^"]+)"',s);assert len(audio_driver)==1
 audio_drivers.append(audio_driver[0]);assert audio_driver[0]==('dummy' if args.dummy_audio else 'wasapi')
 assert 'Using SDL Video Driver "dummy"' in s
 hashes.append(re.findall(r'universe slot fingerprint: ([0-9a-f]+)',s)[-1]);print(s[-1600:],flush=True)
 if not extra:
  m=re.search(r'universe saves: PASS \((\d+) boundaries, (\d+) history boundaries, (\d+) dormant boundaries, (\d+) busy rejections, 3684 truncations, 3684 corruptions, (\d+) invalid states, test-skipped movies\)',s);assert m
  coverage=dict(zip(('boundaries','history_boundaries','dormant_boundaries','busy_rejections','invalid_states'),map(int,m.groups())))
  m=re.search(r'universe extra guards: PASS \((\d+) ordinary boundaries, (\d+) natural voice ends, Music restart, foreground rejection, extended atomic state\)',s);assert m
  extra_coverage=dict(zip(('ordinary_boundaries','natural_voice_ends'),map(int,m.groups())))
  assert extra_coverage['ordinary_boundaries']>0 and extra_coverage['natural_voice_ends']==1
  assert 'universe zero-frame history: PASS' in s and 'universe natural voice end: PASS' in s and 'universe Music restart: PASS' in s
assert hashes[0]==hashes[1],hashes
assert audio_drivers[0]==audio_drivers[1]
assert coverage['boundaries']>50 and coverage['history_boundaries']>30 and coverage['dormant_boundaries']>50 and coverage['invalid_states']>=25
p=subprocess.run(common+['--list-saves'],env=env,cwd=base,capture_output=True,text=True,timeout=60)
assert p.returncode==0 and 'Universe continuation regression' in p.stdout
(base/(prefix+'universe-saves-list.log')).write_text(p.stdout+p.stderr)
for name,expected in audio.items():assert digest(Path('D:/astro/PLACES')/name)==expected
assert digest(source)==digest(alias)==source_hash
assert digest(exe)==expected_exe_sha256
(base/(prefix+'universe-save-proof.json')).write_text(json.dumps(dict(date='2026-10-21',status='PASS',audio_driver='dummy' if args.dummy_audio else 'native',actual_audio_driver=audio_drivers[0],diagnostic=bool(args.tag),fresh_process_fingerprint=hashes[1],slot=14,metadata_listed=True,exe_sha256=expected_exe_sha256,**movie_audit,movies_test_skipped=True,music_restart=True,foreground_rejection=True,extended_atomic_state=True,zero_frame_first_absent=True,zero_frame_prior_residual=True,comet_phase_retained=True,truncations=3684,corruptions=3684,original_wav_sha256=audio,variant_fixture_sha256=source_hash,variant_fixture_unchanged=True,**coverage,**extra_coverage),indent=2))
print('Universe controls, original readout history, dormant sequence and fresh-process completion PASS')
