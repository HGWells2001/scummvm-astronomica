"""P530 native saves, random continuation and fresh-process slot8."""
from pathlib import Path
import json,os,re,subprocess
base=Path('work/fresh-20260913').resolve();cfg=base/'verify-p530-saves.ini'
savepath=base/'p530-save-regression';savepath.mkdir(exist_ok=True)
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_p530_saves=true\nastronomica_verify_save_files=true\nsavepath='+savepath.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
common=[str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--extrapath='+str(base/'fonts'),'--savepath='+str(savepath),'--debuglevel=1']
hashes=[];coverage=None
for name,extra in [('p530-saves',[]),('p530-saves-startup',['--save-slot=8'])]:
 p=subprocess.run(common+['--logfile='+str(base/(name+'.log'))]+extra+['astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=1800)
 (base/(name+'-console.log')).write_text(p.stdout+p.stderr);log=(base/(name+'.log')).read_text()
 print(name,'exit',p.returncode,flush=True)
 if p.returncode or 'FAIL' in log:print(log[-6000:]+p.stderr[-800:]);raise AssertionError(name)
 assert 'P530 save verification: PASS' in log and 'Log closed successfully' in log
 hashes.append(re.findall(r'P530 slot fingerprint: ([0-9a-f]+)',log)[-1]);print(log[-1000:],flush=True)
 if not extra:
  match=re.search(r'P530 saves: PASS \((\d+) round trips, (\d+) solve routes, five scenarios at each round, 25 pictures, 5604 truncations, 5604 corruptions, 31 invalid states',log)
  assert match;coverage=dict(round_trips=int(match[1]),solve_routes=int(match[2]))
assert hashes[0]==hashes[1],hashes
assert 8<=coverage['solve_routes']<=32 and coverage['round_trips']==57*coverage['solve_routes']+2
p=subprocess.run(common+['--list-saves'],env=env,cwd=base,capture_output=True,text=True,timeout=60)
assert p.returncode==0 and 'P530 continuation regression' in p.stdout
(base/'p530-saves-list.log').write_text(p.stdout+p.stderr)
(base/'p530-save-proof.json').write_text(json.dumps(dict(date='2026-10-19',status='PASS',fresh_process_fingerprint=hashes[1],slot=8,metadata_listed=True,**coverage),indent=2))
print('P530 continuation, physical slot, fresh-process partial components/RNG and metadata PASS')
