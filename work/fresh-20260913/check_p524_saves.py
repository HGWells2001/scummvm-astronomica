"""P524 continuation and fresh-process slot restoration using test-only saves."""
from pathlib import Path
import os,re,subprocess,sys,json
base=Path('work/fresh-20260913').resolve();cfg=base/'verify-p524-saves.ini'
savepath=base/'p524-save-regression';savepath.mkdir(exist_ok=True)
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_p524_saves=true\nastronomica_verify_save_files=true\nsavepath='+savepath.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
common=[str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--extrapath='+str(base/'fonts'),'--savepath='+str(savepath),'--debuglevel=1']
hashes=[]
for name,extra in [('p524-saves',[]),('p524-saves-startup',['--save-slot=5'])]:
    p=subprocess.run(common+['--logfile='+str(base/(name+'.log'))]+extra+['astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=1800)
    (base/(name+'-console.log')).write_text(p.stdout+p.stderr)
    print(name,'exit',p.returncode,flush=True)
    log=(base/(name+'.log')).read_text()
    if p.returncode or 'FAIL' in log:
        print("\n".join(line for line in log.splitlines() if "P524 save" in line or "P524 restore" in line or "P524 continuation" in line or "P524 boundary" in line or "FAIL" in line));sys.exit(1)
    assert 'P524 save verification: PASS' in log and 'Log closed successfully' in log
    hashes.append(re.findall(r'P524 slot fingerprint: ([0-9a-f]+)',log)[-1])
    print(log[-700:],flush=True)
assert hashes[0]==hashes[1],hashes
p=subprocess.run(common+['--list-saves'],env=env,cwd=base,capture_output=True,text=True,timeout=60)
assert p.returncode==0 and 'P524 continuation regression' in p.stdout
(base/'p524-saves-list.log').write_text(p.stdout+p.stderr)
(base/'p524-save-proof.json').write_text(json.dumps(dict(date='2026-10-18',status='PASS',fresh_process_fingerprint=hashes[1],slot=5,metadata_listed=True),indent=2))
print('P524 continuation, physical slot, fresh-process restore and metadata PASS')
