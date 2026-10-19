"""Native custom17 saves, all six scenes and physical slot9 continuation."""
from pathlib import Path
import json,os,re,subprocess
base=Path('work/fresh-20260913').resolve();cfg=base/'verify-variant-saves.ini'
savepath=base/'variant-save-regression';savepath.mkdir(exist_ok=True)
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_variant_saves=true\nastronomica_verify_save_files=true\nsavepath='+savepath.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
common=[str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--extrapath='+str(base/'fonts'),'--savepath='+str(savepath),'--debuglevel=1']
hashes=[];coverage=None
for name,extra in [('variant-saves',[]),('variant-saves-startup',['--save-slot=9'])]:
 p=subprocess.run(common+['--logfile='+str(base/(name+'.log'))]+extra+['astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=3600)
 (base/(name+'-console.log')).write_text(p.stdout+p.stderr);log=(base/(name+'.log')).read_text()
 print(name,'exit',p.returncode,flush=True)
 if p.returncode or 'FAIL' in log:print(log[-6000:]+p.stderr[-800:]);raise AssertionError(name)
 assert 'variant save verification: PASS' in log and 'Log closed successfully' in log
 hashes.append(re.findall(r'variant slot fingerprint: ([0-9a-f]+)',log)[-1]);print(log[-1100:],flush=True)
 if not extra:
  m=re.search(r'variant saves: PASS \((\d+) boundaries, (\d+) routes, (\d+) transitions, (\d+) initial repeats, six scenes at all four stages, (\d+) truncations, (\d+) corruptions, (\d+) invalid states',log)
  assert m;coverage=dict(zip(('boundaries','routes','transitions','initial_repeats','truncations','corruptions','invalid_states'),map(int,m.groups())))
assert hashes[0]==hashes[1],hashes
assert coverage['routes']>=12 and coverage['initial_repeats']>0 and coverage['transitions']==4*coverage['routes']+1
assert coverage['truncations']==coverage['corruptions']==23736 and coverage['invalid_states']==192
p=subprocess.run(common+['--list-saves'],env=env,cwd=base,capture_output=True,text=True,timeout=60)
assert p.returncode==0 and 'Variant continuation regression' in p.stdout
(base/'variant-saves-list.log').write_text(p.stdout+p.stderr)
(base/'variant-save-proof.json').write_text(json.dumps(dict(date='2026-10-19',status='PASS',fresh_process_fingerprint=hashes[1],slot=9,metadata_listed=True,**coverage),indent=2))
print('Custom17 saves, nonrepeating continuation, fresh-process partial solution and metadata PASS')
