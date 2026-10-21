"""Audit original P529 movie reconstruction and controls on the official build."""
from pathlib import Path
import hashlib,json,os,re,subprocess
b=Path('work/fresh-20260913').resolve();exe=b/'build/Releasex64/scummvm.exe'
cfg=b/'verify-universe-boundaries.ini';log=b/'universe-boundaries.log'
exe_before=hashlib.sha256(exe.read_bytes()).hexdigest()
cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_universe_boundaries=true\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
with (b/'universe-boundaries-console.log').open('w') as out:
 p=subprocess.run([str(exe),'--config='+str(cfg),'--extrapath='+str(b/'fonts'),'--savepath='+str(b),'--logfile='+str(log),'--debuglevel=1','astro-verify'],env=env,cwd=b,stdout=out,stderr=subprocess.STDOUT,timeout=1800)
s=log.read_text();assert p.returncode==0 and 'FAIL' not in s and s.rstrip().endswith('--- Log closed successfully.'),s[-2500:]
assert re.findall(r'Using SDL Audio Driver "([^"]+)"',s)==['wasapi']
assert hashlib.sha256(exe.read_bytes()).hexdigest()==exe_before
counts=re.findall(r'universe boundary verification: PASS \((\d+) boundaries, (\d+) test-skipped movies, (\d+) decoder-index changes, (\d+) foreground boundaries, (\d+) repeated outcomes, all16 selectors, all7 controls, three routes; independent boundary/frame audit\)',s)
assert len(counts)==1
samples=re.findall(r'universe original-frame reconstruction: PASS \((\d+) sequential versus seekToFrame native pixel comparisons; stopped decoders\)',s)
assert samples==['253']
n=list(map(int,counts[0]));assert n[0]>=137 and n[1]>=11 and n[2]>=7
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=dict(date='2026-10-21',status='PASS',audio_driver='native',actual_audio_driver='wasapi',exe_sha256=d(exe),universe_log=str(log),log_sha256=d(log),
 source_sha256=d(Path('D:/astro/PLACES/P529/MEGAFILE.HYP')),movie_sha256=d(Path('D:/astro/PLACES/P529/FUNIV.MOV')),
 movie_samples=253,**dict(zip(('boundaries','test_skipped_movies','decoder_index_changes','foreground_boundaries','repeated_outcomes'),n)),
 scope='Independent original-frame and settled-script observations; active foreground audio can still bar a save')
(b/'universe-boundaries-proof.json').write_text(json.dumps(report,indent=2));print('P529 independent original MOV and boundary audit PASS:',n,flush=True)
