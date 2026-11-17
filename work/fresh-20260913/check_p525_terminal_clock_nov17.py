"""Compare terminal-frame clock cells on real original media without live-clock mutation."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,subprocess,sys
w=Path(__file__).resolve().parent;ap=argparse.ArgumentParser();ap.add_argument('--stage',default='p525-terminal-clock-baseline-nov17-stage');ap.add_argument('--out',default='p525-terminal-clock-baseline-native-nov17');ap.add_argument('--expected',choices=['baseline','fixed'],default='baseline');ap.add_argument('--portable',action='store_true');a=ap.parse_args();s=w/a.stage;exe=s/'bin/scummvm.exe';out=w/a.out;out.mkdir(exist_ok=False);(out/'saves').mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pin=json.loads((s/'proof.json').read_text())['candidate_exe_sha256'];assert sha(exe)==pin
cfg=out/'test.ini';log=out/'native.log';cfg.write_text('[scummvm]\nconfirm_exit=false\nautosave_period=0\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_p525_terminal_clock=true\n',encoding='utf-8')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi')
if a.portable:
 cfg.write_text(cfg.read_text().replace('gui_theme=builtin','gui_theme=RESIDUALVM\nthemepath='+exe.parent.as_posix()))
 env['SDL_VIDEODRIVER']='windows'
with(out/'console.log').open('w')as console:
 child=subprocess.Popen([str(exe),'--config='+str(cfg),'--logfile='+str(log),'--savepath='+str(out/'saves'),'--extrapath='+str(exe.parent if a.portable else w/'fonts'),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=console,stderr=subprocess.STDOUT)
 subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','p525-terminal-clock-'+a.expected,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL);code=child.wait()
text=log.read_text(errors='replace');assert code==0 and 'P525 terminal clock observation complete: 1'in text,text[-2500:]
b=re.search(r'P525 terminal clock bounds: scene(\d+) frame(\d+) retained(\d+) lastStart(\d+) nextStart(\d+) end(\d+)',text);assert b
scene,frame,retained,last,nextframe,end=map(int,b.groups());assert scene==525 and 0<last<end<=nextframe
rows=[dict(zip(('clock','accepted','unchanged','exact'),map(int,m)))for m in re.findall(r'P525 terminal clock cell: clock(\d+) accepted(\d) unchanged(\d) exact(\d)',text)]
assert len(rows)==5 and [r['clock']for r in rows]==[last-1,last,end-1,end,end+1]
assert [r['accepted']for r in rows]==([0,1,1,1,1]if a.expected=='fixed'else[0,0,0,1,1])
assert all(r['unchanged']and r['exact']==r['accepted']for r in rows)
if a.expected=='fixed':
 assert re.findall(r'P525 terminal wrong frame refusal: frame\d+ refused(\d)',text)==['1','1']
 assert 'P525 terminal low-clock memory futures: PASS'in text
assert sha(exe)==pin and not list((out/'saves').iterdir())
j=dict(status='P525_TERMINAL_CLOCK_FIXED_NATIVE_PASS'if a.expected=='fixed'else'P525_TERMINAL_CLOCK_BASELINE_REJECTION_REPRODUCED',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=pin,original_movie_sha256=sha(Path('D:/astro/PLACES/P525/FSUN.MOV')),frame=frame,observed_natural_clock=retained,last_frame_start=last,next_frame_start=nextframe,range_end=end,cells=rows,native_log_sha256=sha(log),native_exited_naturally=True,limits=['One genuine original selector4 route with immutable detached packet clock cells','Detached modified clock cells are not genuine historical save fixtures; original natural log separately records clock22065 below end22066'])
(out/'proof.json').write_text(json.dumps(j,indent=2)+'\n');print(j['status'],last,nextframe,end)
