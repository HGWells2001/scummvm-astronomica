"""Exercise real builder save boundaries and a fresh-process slot12 continuation."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,subprocess,time
ap=argparse.ArgumentParser();ap.add_argument('--exe',type=Path);ap.add_argument('--tag',default='');ap.add_argument('--dummy-audio',action='store_true');ap.add_argument('--variant-slot',type=Path);args=ap.parse_args()
assert not args.tag or re.fullmatch(r'[a-z0-9-]+',args.tag)
assert not (args.exe or args.dummy_audio or args.variant_slot) or args.tag,'Diagnostic overrides require isolated output names'
base=Path('work/fresh-20260913').resolve();prefix=args.tag+'-' if args.tag else '';cfg=base/(prefix+'verify-builder-saves.ini');savepath=base/(prefix+'builder-save-regression');savepath.mkdir(exist_ok=True)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=args.variant_slot.resolve() if args.variant_slot else base/'variant-save-regression/astro-verify.009';alias=savepath/'astro-verify.099'
source_hash=digest(source);shutil.copyfile(source,alias)
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_builder_saves=true\nastronomica_verify_save_files=true\nsavepath='+savepath.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
if args.dummy_audio:env['SDL_AUDIODRIVER']='dummy'
common=[str(args.exe.resolve() if args.exe else base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--extrapath='+str(base/'fonts'),'--savepath='+str(savepath),'--debuglevel=1']
audio={f'P{scene}/{name}':digest(Path(f'D:/astro/PLACES/P{scene}')/name) for scene in (515,536) for name in ('S0.WAV','S1.WAV')}
hashes=[];coverage=None
for name,extra in [('builder-saves',[]),('builder-saves-startup',['--save-slot=12'])]:
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
 assert 'builder save verification: PASS' in s and 'Log closed successfully' in s
 hashes.append(re.findall(r'builder slot fingerprint: ([0-9a-f]+)',s)[-1]);print(s[-1600:],flush=True)
 if not extra:
  m=re.search(r'builder saves: PASS \((\d+) boundaries, six routes, (\d+) control matrix cases, 8960 truncations, 8960 corruptions, (\d+) invalid states, (\d+) no-picture and (\d+) dormant-sequence boundaries, (\d+) fresh-scene timer comparisons, Music restart, comet phase and P515 no-op\)',s);assert m
  coverage=dict(boundaries=int(m[1]),routes=6,matrix_cases=int(m[2]),truncations=8960,corruptions=8960,invalid_states=int(m[3]),no_picture_boundaries=int(m[4]),dormant_boundaries=int(m[5]),fresh_scene_timer_comparisons=int(m[6]))
assert hashes[0]==hashes[1],hashes
assert coverage['boundaries']>300 and coverage['matrix_cases']>=280 and coverage['invalid_states']>40
assert coverage['fresh_scene_timer_comparisons']>=6
assert coverage['no_picture_boundaries'] and coverage['dormant_boundaries']
p=subprocess.run(common+['--list-saves'],env=env,cwd=base,capture_output=True,text=True,timeout=60)
assert p.returncode==0 and 'Builder continuation regression' in p.stdout
(base/(prefix+'builder-saves-list.log')).write_text(p.stdout+p.stderr)
for name,expected in audio.items():assert digest(Path('D:/astro/PLACES')/name)==expected
assert digest(source)==digest(alias)==source_hash
(base/(prefix+'builder-save-proof.json')).write_text(json.dumps(dict(date='2026-10-20',status='PASS',audio_driver='dummy' if args.dummy_audio else 'native',diagnostic=bool(args.tag),fresh_process_fingerprint=hashes[1],slot=12,metadata_listed=True,music_restart=True,comet_phase_retained=True,original_wav_sha256=audio,variant_fixture_sha256=source_hash,variant_fixture_unchanged=True,**coverage),indent=2))
print('Builder both scenes, original controls, dormant sequence and fresh-process completion PASS')
