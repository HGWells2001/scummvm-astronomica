"""Compare accepted baseline and real candidate on fresh/explicit configuration profiles."""
from pathlib import Path
from datetime import datetime,timezone
import configparser,hashlib,json,os,re,subprocess,sys,time,traceback
w=Path(__file__).resolve().parent;out=w/'startup-defaults-native-nov12d';out.mkdir(exist_ok=False);read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
KEYS=('astronomica_audio','astronomica_animation','astronomica_sprite_input','astronomica_entry_scripts')
def state(st,**kw):(out/'status.json').write_text(json.dumps(dict(status=st,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 state('WAITING_BASELINE_AND_CANDIDATE_BUILDS');stages={role:w/('startup-defaults-'+role+'-nov12c-stage')for role in('baseline','candidate')}
 for role,s in stages.items():
  while not(s/'proof.json').exists():
   err=w/('startup-defaults-'+role+'-nov12c-build.err')
   if err.exists()and err.stat().st_size:raise RuntimeError(err.read_text())
   time.sleep(1)
  subprocess.run([sys.executable,str(w/('audit_startup_defaults_'+role+'_nov12c.py')),s.name,'startup-defaults-'+role+'-source-review-nov12c.json'],check=True,stdout=subprocess.DEVNULL)
 pinned=['PLACES/P1/MEGAFILE.HYP','PLACES/P27/MEGAFILE.HYP','PLACES/P27/S0.WAV'];resources={n:sha(Path('D:/astro')/n)for n in pinned};rows=[]
 cases=[('baseline-fresh','baseline',0,0,{}, {},'dummy'),('fresh-defaults','candidate',15,0,{}, {},'dummy')]
 for mask in range(16):cases.append(('explicit-'+str(mask),'candidate',mask,15,{k:bool(mask&(1<<i))for i,k in enumerate(KEYS)}, {},'dummy'))
 for i,k in enumerate(KEYS):cases.append(('application-off-'+str(i),'candidate',15^(1<<i),1<<i,{}, {k:False},'dummy'))
 cases.append(('game-overrides-application','candidate',15,15,{k:True for k in KEYS},{k:False for k in KEYS},'dummy'))
 cases.append(('fresh-windows','candidate',15,0,{}, {},'windows'))
 for label,role,expected,explicit,game,app,video in cases:
  stage=stages[role];b=read(stage/'proof.json');exe=stage/'bin/scummvm.exe';assert sha(exe)==b['candidate_exe_sha256'];case=out/label;case.mkdir();(case/'saves').mkdir()
  config='[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\nfullscreen=false\ngui_language=en\ngui_theme=builtin\nmute=true\n'+''.join(k+'='+str(v).lower()+'\n'for k,v in app.items())+'[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_verify_startup_defaults=true\nastronomica_expected_startup_mask='+str(expected)+'\nastronomica_expected_explicit_mask='+str(explicit)+'\nsavepath='+(case/'saves').as_posix()+'\n'+''.join(k+'='+str(v).lower()+'\n'for k,v in game.items())
  cfg=case/'test.ini';cfg.write_text(config);cfg_hash=sha(cfg);env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER=video,SDL_AUDIODRIVER='wasapi');log=case/'native.log';state('RUNNING_FRESH_CONFIGURATION_PROFILE',profile=label)
  with(case/'console.log').open('w')as console:
   child=subprocess.Popen([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT)
   subprocess.run([sys.executable,str(w/'suite_registry_nov12.py'),'register','--pid',str(child.pid),'--label','startup-defaults-native-'+label,'--proof',str(out/'proof.json')],check=True,stdout=subprocess.DEVNULL);code=child.wait()
  text=log.read_text(errors='replace');assert code==0 and 'FAIL'not in text and 'Startup defaults native result: PASS'in text and 'Log closed successfully'in text,text[-4500:]
  assert 'Using SDL Video Driver "'+video+'"'in text
  found=re.search(r'configuration: PASS \(observed(\d+),expected(\d+),explicit(\d+),expectedExplicit(\d+),P1pending(\d+)\)',text);assert found and tuple(map(int,found.groups()[:4]))==(expected,expected,explicit,explicit)
  parsed=configparser.ConfigParser(interpolation=None);parsed.read(cfg)
  for domain,values in [('scummvm',app),('astro-verify',game)]:
   for key in KEYS:assert parsed.has_option(domain,key)==(key in values) and (key not in values or parsed.getboolean(domain,key)==values[key])
  assert not list((case/'saves').iterdir())
  rows.append(dict(profile=label,role=role,observed_mask=expected,explicit_mask=explicit,initial_original_P1_queue=int(found[5]),video_driver=video,native_log_sha256=sha(log),gameplay_feature_keys_unchanged=True,native_exited_naturally=True))
 assert resources=={n:sha(Path('D:/astro')/n)for n in pinned};prefs=read(w/'nov12-user-prefs-pin.json');assert sha(Path(prefs['path']))==prefs['sha256']
 proof=dict(status='STARTUP_DEFAULTS_CAUSAL_NATIVE_AND_EXPLICIT_PREFERENCES_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(stages['candidate']/'bin/scummvm.exe'),baseline_diagnostic_exe_sha256=sha(stages['baseline']/'bin/scummvm.exe'),original_installed_base_exe_sha256=read(stages['candidate']/'proof.json')['base_exe_sha256'],cases=rows,fresh_baseline_missing_gameplay_reproduced=True,fresh_candidate_original_entry_input_audio_and_animation_pass=True,all16explicit_feature_masks_preserved=True,application_and_game_precedence_preserved=True,windows_backend_fresh_profile_pass=True,original_resource_sha256=resources,all_processes_exited_naturally=True,user_preferences_unchanged=True,limits=['Baseline contains exact same optional verification branch added to the accepted engine;candidate adds actual production defaults/guard fix','Original P1entry queue,P27selected sprite frame,actual original P27click lock and S0mixer submission checked;not a human audio inspection','Explicit false remains a deliberate override. ScummVM may normalize its isolated test INI/core metadata;all four gameplay key presences/values preserved and real user preferences/original resources unchanged','No original Win16execution or global completion percentage claim'])
 (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state('PASS');print(proof['status'],len(rows),'profiles')
except Exception:state('FAILED',error=traceback.format_exc());raise
