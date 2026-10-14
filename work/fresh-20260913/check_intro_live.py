"""Run the unmodified native main loop through the complete introduction.
Only this harness's own child process is terminated after reaching P27.
"""
from pathlib import Path
import os,subprocess,time,json,re,hashlib,sys
from intro_timing import timing_valid
real_audio = '--real-audio' in sys.argv
suffix = 'intro-live-real-audio' if real_audio else 'intro-live'
base=Path('work/fresh-20260913').resolve();cfg=base/('verify-'+suffix+'.ini');log=base/(suffix+'.log')
if log.exists(): log.unlink()
cfg.write_text('[scummvm]\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-live]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_start_place=2\nastronomica_entry_scripts=true\nastronomica_sprite_input=true\nastronomica_animation=true\nastronomica_audio=true\n')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
if real_audio: env.pop('SDL_AUDIODRIVER', None)
cmd=[str(base/'build/Releasex64/scummvm.exe'),'--config='+str(cfg),'--logfile='+str(log),'--extrapath='+str(base/'fonts'),'--savepath='+str(base),'--debuglevel=1','astro-live']
start=time.monotonic(); reached=False
with (base/(suffix+'-console.log')).open('w') as output:
 child=subprocess.Popen(cmd,env=env,cwd=base,stdout=output,stderr=subprocess.STDOUT)
 try:
  while child.poll() is None and time.monotonic()-start<420:
   text=log.read_text(errors='replace') if log.exists() else ''
   if 'Astronomica resource explorer: P27;' in text:reached=True;break
   time.sleep(.25)
 finally:
  if child.poll() is None:child.terminate();child.wait(timeout=15)
text=log.read_text(errors='replace')
expected=['Astronomica resource explorer: P2;','Astronomica native RGB palette command: OPEN2_b','Astronomica resource explorer: P3;','Astronomica resource explorer: P4;','Astronomica resource explorer: P27;']
positions=[text.find(x) for x in expected]
assert reached and all(x>=0 for x in positions) and positions==sorted(positions)
assert 'unsupported scripts skipped' not in text and 'FAIL' not in text and 'CRITICAL' not in text
lines=[x for x in text.splitlines() if any(t in x for t in ('movie closed while playing','movie segment finished','resource explorer:','native RGB palette'))]
result=dict(status='PASS: real main loop reached exploration',wall_seconds=round(time.monotonic()-start,2),path=[2,3,4,27],native_verify_mode=False,entry_scripts=True,audio=True,headless=True,natural_ends=sum('movie segment finished' in x for x in lines),timeline=lines,exe_sha256=hashlib.sha256((base/'build/Releasex64/scummvm.exe').read_bytes()).hexdigest(),manual_confirmation=False)
result['audio_backend'] = 'system default' if real_audio else 'SDL dummy'
result['movie_timing_valid'] = timing_valid(text)
if real_audio: assert result['movie_timing_valid'], 'Intro reached exploration but movie clock diverged from real time'
(base/(suffix+'-result.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
