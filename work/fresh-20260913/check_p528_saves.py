"""P528 full-frame state/continuation checks and a fresh-process slot7."""
from pathlib import Path
import hashlib,json,os,re,subprocess
base=Path('work/fresh-20260913').resolve();cfg=base/'verify-p528-saves.ini'
savepath=base/'p528-save-regression';savepath.mkdir(exist_ok=True)
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_p528_saves=true\nastronomica_verify_save_files=true\nsavepath='+savepath.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
common=[str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--extrapath='+str(base/'fonts'),'--savepath='+str(savepath),'--debuglevel=1']
hashes=[]
for name,extra in [('p528-saves',[]),('p528-saves-startup',['--save-slot=7'])]:
 p=subprocess.run(common+['--logfile='+str(base/(name+'.log'))]+extra+['astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=1800)
 (base/(name+'-console.log')).write_text(p.stdout+p.stderr);log=(base/(name+'.log')).read_text()
 print(name,'exit',p.returncode,flush=True)
 if p.returncode or 'FAIL' in log:print(log[-4500:]+p.stderr[-1000:]);raise AssertionError(name)
 assert 'P528 save verification: PASS' in log and 'Log closed successfully' in log
 hashes.append(re.findall(r'P528 slot fingerprint: ([0-9a-f]+)',log)[-1]);print(log[-800:],flush=True)
assert hashes[0]==hashes[1],hashes
graph_path=base.parent.parent/'outputs/astronomica-cleanroom/evidence/p528-settled-graph.json'
graph=json.loads(graph_path.read_text())
def key(values):
 phase,quadrant,first,second,committed,tall=values
 return f'{phase},{quadrant},{first},{second},{12-phase if committed else 0},{int(tall[4:]) if tall else 0}'
expected={}
for edge in graph['edges']:
 action={'phase':4,'quadrant':5,'answer':6}[edge['action']]
 expected[key(edge['source']),action]=(526,'-') if edge['departure_to'] else (528,key(edge['target']))
for state in graph['states']:expected[key(state['values']),0]=(268,'-')
rows=re.findall(r'P528 save edge: ([0-9,]+) / ([0-9]+) -> P([0-9]+) ([0-9,-]+)',(base/'p528-saves.log').read_text())
actual={(source,int(action)):(int(place),target) for source,action,place,target in rows}
assert len(rows)==len(actual)==len(expected)==640 and actual==expected
p=subprocess.run(common+['--list-saves'],env=env,cwd=base,capture_output=True,text=True,timeout=60)
assert p.returncode==0 and 'P528 continuation regression' in p.stdout
(base/'p528-saves-list.log').write_text(p.stdout+p.stderr)
(base/'p528-save-proof.json').write_text(json.dumps(dict(date='2026-10-18',status='PASS',fresh_process_fingerprint=hashes[1],slot=7,metadata_listed=True,resource_edges_compared=640,original_state_graph_sha256=hashlib.sha256(graph_path.read_bytes()).hexdigest()),indent=2))
print('P528 160 states, 640 round trips, fresh-process partial completion and metadata PASS')
