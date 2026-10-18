"""Inventory reachable P526 native states on existing real engine routes."""
from pathlib import Path
import hashlib,json,os,re,subprocess
base=Path('work/fresh-20260913').resolve();cfg=base/'verify-p526-boundaries.ini'
cfg.write_text('[scummvm]\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_p526=true\nastronomica_verify_p526_boundaries=true\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
exe=base/'build/Releasex64/scummvm.exe';logfile=base/'p526-boundaries.log'
p=subprocess.run([str(exe),'--config='+str(cfg),'--logfile='+str(logfile),'--extrapath='+str(base/'fonts'),'--savepath='+str(base),'--debuglevel=1','astro-verify'],env=env,cwd=base,capture_output=True,text=True,timeout=600)
(base/'p526-boundaries-console.log').write_text(p.stdout+p.stderr)
log=logfile.read_text();assert p.returncode==0 and 'FAIL' not in log and 'P526 interaction verification: PASS' in log
fields=['visible','selected_frame','x','y','render_x','render_y','auto_frame','auto_move','frame_since','move_since','standard_motion','move_dx','move_dy','orbit_motion','orbit_side_x','orbit_side_y','frame_first','frame_last','click_enabled','frame_period','frame_step','frame_mode','move_period','move_a','move_b','move_mode','move_extra']
rows=[];current=None
for line in log.splitlines():
 if 'P526 audit boundary: ' in line:
  parts=line.split('P526 audit boundary: ')[1].split()
  current=dict(route=int(parts[0]),phase=parts[1],clock=int(parts[2]),locals=list(map(int,parts[3:])),sprites=[]);rows.append(current)
 elif 'P526 audit sprite: ' in line:
  values=list(map(int,line.split('P526 audit sprite: ')[1].split()));assert len(values)==len(fields)+1
  assert current is not None and values[0]==len(current['sprites'])
  current['sprites'].append(dict(zip(fields,values[1:])))
 elif 'P526 audit image: ' in line:
  current['image']=line.split('P526 audit image: ')[1]
assert rows and all(len(r['sprites'])==23 and len(r['locals'])==7 for r in rows)
assert {r['locals'][2] for r in rows if r['phase']=='stopped'}==set(range(1,7))
assert all(not any(s['auto_move'] for s in r['sprites']) for r in rows)
assert all(r['sprites'][17]['frame_period']==-1 for r in rows if r['phase']=='stopped')
report=dict(date='2026-10-18',status='PASS',scope='Observed native boundaries; save implementation still absent',exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(Path('D:/astro/PLACES/P526/MEGAFILE.HYP').read_bytes()).hexdigest(),boundaries=len(rows),fields=fields,rows=rows)
(base/'p526-boundaries.json').write_text(json.dumps(report,indent=2))
print('P526 native boundary inventory PASS:',len(rows),'boundaries; six stopped scenarios; real audio routes')
