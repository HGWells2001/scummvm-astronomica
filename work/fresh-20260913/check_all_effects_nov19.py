"""Verify every original WAV path in the real mixer with a catalogue-derived fixture."""
from pathlib import Path
import json,hashlib,os,subprocess,sys,re
from datetime import datetime,timezone
w=Path(__file__).resolve().parent;windows='--windows'in sys.argv;installed='--installed'in sys.argv;s=w/'all-effects-candidate-nov19-stage';out=w/('all-effects-installed-nov19'if installed else('all-effects-windows-nov19'if windows else'all-effects-native-nov19'));out.mkdir(exist_ok=False);(out/'saves').mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=json.loads((s/'proof.json').read_text());exe=w/'build/Releasex64/scummvm.exe'if installed else s/'bin/scummvm.exe';assert sha(exe)==build['candidate_exe_sha256'];cfg=out/'test.ini';log=out/'native.log';cfg.write_text('[scummvm]\nconfirm_exit=false\nautosave_period=0\nenable_unsupported_game_warning=false\ngui_theme=builtin\ngui_language=en\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_audio_roles=true\nastronomica_audio_role_fixture='+str(w/'audio-role-fixture-nov19.bin')+'\n')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='windows'if windows else'dummy',SDL_AUDIODRIVER='wasapi')
with(out/'console.log').open('w')as f:
 child=subprocess.Popen([str(exe),'--config='+str(cfg),'--savepath='+str(out/'saves'),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT)
 try:subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','all-original-audio-roles','--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL)
 finally:code=child.wait()
t=log.read_text(errors='replace');rows=[tuple(map(int,m))for m in re.findall(r'Audio catalogue row: (\d+) P(\d+) S(\d+) effect(\d) role(\d) overlap(\d) exclusive(\d) continuous(\d) result(\d)',t)]
assert code==0 and len(rows)==632 and all(r[-1]==1 for r in rows),str([r for r in rows if r[-1]!=1])+t[-1500:]
assert 'Audio catalogue complete: PASS (passed632,total632,effects308,foreground324)'in t and t.rstrip().endswith('--- Log closed successfully.')
p=dict(status='ALL_EFFECTS_NATIVE_PASS',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),catalogue_sha256=sha(w/'audio-role-catalogue-nov19.json'),fixture_sha256=sha(w/'audio-role-fixture-nov19.bin'),native_log_sha256=sha(log),original_wav_paths=632,effect_file_paths=308,exclusive_file_paths=324,distinct_effects=102,windows_backend=windows,native_exited_naturally=True,limits=['Direct native playback per original WAV path,not every naturally reached gameplay event','Actual mixer handles/continuity,not an acoustic loopback recording','Catalogue machine-assisted;ambiguous vocal clips remain exclusive;no runtime ML'])
(out/'proof.json').write_text(json.dumps(p,indent=2)+'\n');print(p['status'])
