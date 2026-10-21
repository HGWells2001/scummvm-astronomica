"""Observe real P537 controls independently of any new serializer."""
from pathlib import Path
import subprocess,os,json,hashlib
b=Path('work/fresh-20260913').resolve();cfg=b/'verify-rocket-boundaries.ini';exe=b/'build/Releasex64/scummvm.exe'
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_rocket_boundaries=true\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
log=b/'rocket-boundaries.log'
with (b/'rocket-boundaries-console.log').open('w') as f:
 p=subprocess.run([str(exe),'--config='+str(cfg),'--extrapath='+str(b/'fonts'),'--savepath='+str(b),'--logfile='+str(log),'--debuglevel=1','astro-verify'],env=env,cwd=b,stdout=f,stderr=subprocess.STDOUT,text=True,timeout=1800)
s=log.read_text();assert p.returncode==0 and 'FAIL' not in s and 'rocket boundary verification: PASS' in s and 'Log closed successfully' in s,s[-2500:]
rows=[];current=None
for line in s.splitlines():
 if 'Rocket audit boundary: ' in line:
  v=list(map(int,line.split('Rocket audit boundary: ')[1].split()));current=dict(zip(('route','control','clock','selector','rocket_delta','rocket_since','variant_round','variant_mask','foreground_active'),v));current['sprites']=[];rows.append(current)
 elif 'Rocket audit sprite: ' in line:
  v=list(map(int,line.split('Rocket audit sprite: ')[1].split()));assert len(v)==28 and v[0]==len(current['sprites']);current['sprites'].append(v[1:])
assert len(rows)>300 and all(len(r['sprites'])==48 for r in rows)
assert {r['selector'] for r in rows}==set(range(16)) and {r['route'] for r in rows}==set(range(17))
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=dict(date='2026-10-21',status='PASS',scope='Native settled-script/stopped-motion observations; foreground audio may still bar a save; no P537 save support',exe_sha256=d(exe),source_sha256=d(Path('D:/astro/PLACES/P537/MEGAFILE.HYP')),boundaries=len(rows),rows=rows)
(b/'rocket-boundaries.json').write_text(json.dumps(report,indent=2));print('P537 independent boundary audit PASS:',len(rows),'observations, all16 selectors and14 failed-return routes')
