"""Actual original P509 -> four puzzle save boundaries, plus inert extremes."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
base=Path('work/fresh-20260913').resolve();cfg=base/'verify-save-entry-history.ini';red='--expect-rejection' in sys.argv
folder=base/'save-entry-history';folder.mkdir(exist_ok=True)
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_save_history=true\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
log=base/('save-entry-history-before.log' if red else 'save-entry-history.log');log.write_text('')
exe=base/'build/Releasex64/scummvm.exe'
console=base/('save-entry-history-before-console.log' if red else 'save-entry-history-console.log')
output=console.open('w')
p=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(base/'fonts'),'--savepath='+str(folder),'--logfile='+str(log),'--debuglevel=1','astro-verify'],env=env,cwd=base,stdout=output,stderr=subprocess.STDOUT,text=True)
try:
 for _ in range(120):
  if p.poll() is not None:break
  if 'save entry history verification: FAIL' in log.read_text():p.terminate();break
  time.sleep(0.25)
 else:p.terminate();raise AssertionError('Save entry check timeout')
 p.wait(timeout=10)
finally:
 if p.poll() is None:p.terminate();p.wait(timeout=10)
 output.close()
s=log.read_text();print(s[-1500:])
if red:
 assert 'save entry history rejected: P509 -> P524 (unknown locals14=1,16=2)' in s and 'verification: FAIL' in s
 print('Pre-fix original scene entry rejection reproduced');sys.exit(0)
assert p.returncode==0 and 'save entry history: PASS (4 original P509 entries, 12 inert-value round trips, 8 metadata rejections' in s and 'FAIL' not in s and 'Log closed successfully' in s
proof=dict(date='2026-10-19',status='PASS',exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),source_scene=509,destinations=[524,526,528,530],original_entries=4,inert_extreme_round_trips=12,metadata_rejections=8,layouts_unchanged=[6,7,8,9])
(base/'save-entry-history-proof.json').write_text(json.dumps(proof,indent=2))
print('Natural cross-puzzle save entry and exact inert-data preservation PASS')
