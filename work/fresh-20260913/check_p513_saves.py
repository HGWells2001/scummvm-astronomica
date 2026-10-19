"""Stopped photon state, question RNG and physical slot10 continuation."""
from pathlib import Path
import json,os,re,subprocess,time
base=Path('work/fresh-20260913').resolve();cfg=base/'verify-p513-saves.ini';savepath=base/'p513-save-regression';savepath.mkdir(exist_ok=True)
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_p513_saves=true\nastronomica_verify_save_files=true\nsavepath='+savepath.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
common=[str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--extrapath='+str(base/'fonts'),'--savepath='+str(savepath),'--debuglevel=1']
hashes=[];coverage=None
for name,extra in [('p513-saves',[]),('p513-saves-startup',['--save-slot=10'])]:
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
 if p.returncode or 'FAIL' in s:print(s[-6000:]+console.read_text()[-1000:]);raise AssertionError(name)
 assert 'P513 save verification: PASS' in s and 'Log closed successfully' in s
 hashes.append(re.findall(r'P513 slot fingerprint: ([0-9a-f]+)',s)[-1]);print(s[-1000:],flush=True)
 if not extra:
  m=re.search(r'P513 saves: PASS \((\d+) boundaries, five routes, fourteen scenarios, nine stopped photon results, 126 answer continuations, two live-setting changes, 5928 truncations, 5928 corruptions, 37 invalid states',s);assert m
  coverage=dict(boundaries=int(m[1]),routes=5,scenarios=14,photon_results=9,answer_continuations=126,live_setting_changes=2)
assert hashes[0]==hashes[1],hashes
assert coverage['boundaries']>100
p=subprocess.run(common+['--list-saves'],env=env,cwd=base,capture_output=True,text=True,timeout=60)
assert p.returncode==0 and 'P513 continuation regression' in p.stdout
(base/'p513-saves-list.log').write_text(p.stdout+p.stderr)
(base/'p513-save-proof.json').write_text(json.dumps(dict(date='2026-10-19',status='PASS',fresh_process_fingerprint=hashes[1],slot=10,metadata_listed=True,**coverage),indent=2))
print('P513 stopped photon/digits, question continuation and fresh-process silent completion PASS')
