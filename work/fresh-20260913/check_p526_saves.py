"""P526 native saves and fresh-process continuation, using test-only slot6."""
from pathlib import Path
import os,re,subprocess,sys,json
base=Path('work/fresh-20260913').resolve();cfg=base/'verify-p526-saves.ini'
savepath=base/'p526-save-regression';savepath.mkdir(exist_ok=True)
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_p526_saves=true\nastronomica_verify_save_files=true\nsavepath='+savepath.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
common=[str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--extrapath='+str(base/'fonts'),'--savepath='+str(savepath),'--debuglevel=1']
hashes=[]
for name,extra in [('p526-saves',[]),('p526-saves-startup',['--save-slot=6'])]:
 p=subprocess.run(common+['--logfile='+str(base/(name+'.log'))]+extra+['astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=1800)
 (base/(name+'-console.log')).write_text(p.stdout+p.stderr)
 print(name,'exit',p.returncode,flush=True);log=(base/(name+'.log')).read_text()
 if p.returncode or 'FAIL' in log:
  print('\n'.join(line for line in log.splitlines() if 'P526' in line or 'FAIL' in line)[-5000:]);sys.exit(1)
 assert 'P526 save verification: PASS' in log and 'Log closed successfully' in log
 hashes.append(re.findall(r'P526 slot fingerprint: ([0-9a-f]+)',log)[-1]);print(log[-700:],flush=True)
assert hashes[0]==hashes[1],hashes
p=subprocess.run(common+['--list-saves'],env=env,cwd=base,capture_output=True,text=True,timeout=60)
assert p.returncode==0 and 'P526 continuation regression' in p.stdout
(base/'p526-saves-list.log').write_text(p.stdout+p.stderr)
(base/'p526-save-proof.json').write_text(json.dumps(dict(date='2026-10-18',status='PASS',fresh_process_fingerprint=hashes[1],slot=6,metadata_listed=True),indent=2))
print('P526 continuation, physical slot, fresh-process restore and metadata PASS')
