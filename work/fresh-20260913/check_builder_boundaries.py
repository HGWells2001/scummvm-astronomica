"""Observe settled real-engine construction states; does not implement a save format."""
from pathlib import Path
import hashlib,json,os,subprocess
base=Path('work/fresh-20260913').resolve();cfg=base/'verify-builder-boundaries.ini'
cfg.write_text('[scummvm]\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_builder=true\nastronomica_verify_builder_boundaries=true\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
exe=base/'build/Releasex64/scummvm.exe';logfile=base/'builder-boundaries.log'
with (base/'builder-boundaries-console.log').open('w') as output:
 p=subprocess.run([str(exe),'--config='+str(cfg),'--logfile='+str(logfile),'--extrapath='+str(base/'fonts'),'--savepath='+str(base),'--debuglevel=1','astro-verify'],env=env,cwd=base,stdout=output,stderr=subprocess.STDOUT,text=True,timeout=600)
log=logfile.read_text();assert p.returncode==0 and 'FAIL' not in log and 'Builder audit nonidle' not in log and 'P515/P536 interaction verification: PASS' in log and 'Log closed successfully' in log
fields=['visible','selected_frame','x','y','render_x','render_y','auto_frame','auto_move','frame_since','move_since','standard_motion','move_dx','move_dy','orbit_motion','orbit_side_x','orbit_side_y','frame_first','frame_last','click_enabled','frame_period','frame_step','frame_mode','move_period','move_a','move_b','move_mode','move_extra']
rows=[];current=None
for line in log.splitlines():
 if 'Builder audit boundary: ' in line:
  parts=list(map(int,line.split('Builder audit boundary: ')[1].split()))
  current=dict(route=parts[0],scene=parts[1],control=parts[2],clock=parts[3],locals=parts[4:],sprites=[]);rows.append(current)
 elif 'Builder audit sprite: ' in line:
  values=list(map(int,line.split('Builder audit sprite: ')[1].split()));assert len(values)==28 and current is not None and values[0]==len(current['sprites'])
  current['sprites'].append(dict(zip(fields,values[1:])))
 elif 'Builder audit image: ' in line:
  assert current is not None;current['image']=line.split('Builder audit image: ')[1]
assert len(rows)>100 and all(len(r['sprites'])==60 and len(r['locals'])==13 for r in rows)
assert {r['scene'] for r in rows}=={515,536} and {r['route'] for r in rows}=={0,1,2,3,4,5}
assert {r['locals'][1] for r in rows if r['scene']==515 and r['route']>=4 and r['locals'][1]}=={4,5}
assert {r['locals'][1] for r in rows if r['locals'][1]}=={1,2,3,4,5}
assert all(not any(s['auto_move'] or s['auto_frame'] for s in r['sprites']) for r in rows)
assert all(r['image'].lower() in ('','pad','drydock') for r in rows)
original=Path('outputs/astronomica-cleanroom/evidence/builder-save-original.json')
report=dict(date='2026-10-19',status='PASS',scope='Observed native route boundaries; no builder save support or original Windows execution claim',exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),original_inventory_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
 source_sha256={str(n):hashlib.sha256(Path(f'D:/astro/PLACES/P{n}/MEGAFILE.HYP').read_bytes()).hexdigest() for n in (515,536)},boundaries=len(rows),fields=fields,rows=rows,
 limitations=['Four ordinary routes and two early-Launch routes; all five designs, both phases and cap recovery; not all possible control histories','Only settled boundaries are observed; launch programs are deliberately not saveable'])
(base/'builder-boundaries.json').write_text(json.dumps(report,indent=2))
print('Builder native boundary inventory PASS:',len(rows),'boundaries; five designs; two phases; original controls')
