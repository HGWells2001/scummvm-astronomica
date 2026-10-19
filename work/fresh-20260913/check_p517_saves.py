"""Verify real aurora animation phases and physical slot11 continuation."""
from pathlib import Path
import hashlib,json,os,re,subprocess,time
base=Path('work/fresh-20260913').resolve();cfg=base/'verify-p517-saves.ini';savepath=base/'p517-save-regression';savepath.mkdir(exist_ok=True)
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_p517_saves=true\nastronomica_verify_save_files=true\nsavepath='+savepath.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
common=[str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--extrapath='+str(base/'fonts'),'--savepath='+str(savepath),'--debuglevel=1']
hashes=[];coverage=None
original=json.loads(Path('outputs/astronomica-cleanroom/evidence/p517-save-original.json').read_text())
def verify_audio():
 for name,expected in original['original_wav_sha256'].items():assert hashlib.sha256((Path('D:/astro/PLACES/P517')/name).read_bytes()).hexdigest()==expected,name
verify_audio()
for name,extra in [('p517-saves',[]),('p517-saves-startup',['--save-slot=11'])]:
 log=base/(name+'.log');log.write_text('');console=base/(name+'-console.log')
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
 assert 'P517 save verification: PASS' in s and 'Log closed successfully' in s
 hashes.append(re.findall(r'P517 slot fingerprint: ([0-9a-f]+)',s)[-1]);print(s[-1000:],flush=True)
 if not extra:
  m=re.search(r'P517 saves: PASS \((\d+) boundaries, three routes, fourteen settings, (\d+) animation cases, 3660 truncations, 3660 corruptions, (\d+) invalid states',s);assert m
  coverage=dict(boundaries=int(m[1]),routes=3,settings=14,animation_cases=int(m[2]),truncations=3660,corruptions=3660,invalid_states=int(m[3]))
  assert 'Music restart and guards)' in s
assert hashes[0]==hashes[1],hashes
assert coverage['boundaries']>2000 and coverage['animation_cases']==2240 and coverage['invalid_states']>30
p=subprocess.run(common+['--list-saves'],env=env,cwd=base,capture_output=True,text=True,timeout=60)
assert p.returncode==0 and 'P517 continuation regression' in p.stdout
(base/'p517-saves-list.log').write_text(p.stdout+p.stderr)
verify_audio()
(base/'p517-save-proof.json').write_text(json.dumps(dict(date='2026-10-19',status='PASS',fresh_process_fingerprint=hashes[1],slot=11,metadata_listed=True,music_restart=True,original_wav_sha256=original['original_wav_sha256'],**coverage),indent=2))
print('P517 animation phases, all settings and fresh-process completion PASS')
