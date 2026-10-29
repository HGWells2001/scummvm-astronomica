"""Same-executable P510 native bytes/fresh process/metadata; no coverage claim."""
from pathlib import Path
from datetime import datetime
import argparse,hashlib,json,os,re,shutil,subprocess,time
ap=argparse.ArgumentParser();ap.add_argument('--exe',type=Path);ap.add_argument('--tag',default='');ap.add_argument('--dummy-audio',action='store_true');args=ap.parse_args()
assert not args.tag or re.fullmatch(r'[a-z0-9-]+',args.tag)
assert not(args.exe or args.dummy_audio) or args.tag
w=Path(__file__).resolve().parent;exe=args.exe.resolve() if args.exe else w/'build/Releasex64/scummvm.exe';prefix=args.tag+'-' if args.tag else ''
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected=d(exe);savepath=w/(prefix+'p510-save-regression');savepath.mkdir(exist_ok=True)
immutable_variant=w/'verification-fixtures/variant2/astro-verify.009'
if immutable_variant.exists():assert d(immutable_variant)=='2cb6bf34b1e42c895a9aa4ddddafd931253545d5f59d802b4458946787f8b92a'
fixtures={99:immutable_variant if immutable_variant.exists() else w/'variant-save-regression/astro-verify.009',98:w/'verified-checkpoints/p501-025e82d8bd3b/frozen-slot26/astro-verify.026'};fixture_sha={}
for alias,source in fixtures.items():shutil.copyfile(source,savepath/('astro-verify.%03d'%alias));fixture_sha[str(alias)]=d(source)
cfg=w/(prefix+'verify-p510-saves.ini');cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=false\nastronomica_verify_p510=true\nastronomica_p510_continuous=false\nsavepath='+savepath.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
if args.dummy_audio:env['SDL_AUDIODRIVER']='dummy'
driver='dummy' if args.dummy_audio else 'wasapi';common=[str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--savepath='+str(savepath),'--debuglevel=1']
assets={p.name:d(p) for p in Path('D:/astro/PLACES/P510').iterdir() if p.is_file()};global912=d(Path('D:/astro/SOUNDS/S12.WAV'));logs={};coverage={};physical_slot_sha=None
for name,extra,marker in [('p510-saves',[],'Astronomica P510 interaction verification: PASS'),('p510-saves-startup',['--save-slot=27'],'P510 ASVM28 fresh physical continuation: PASS')]:
 log=w/(prefix+name+'.log');log.write_text('');console=w/(prefix+name+'-console.log')
 with console.open('w') as stream:
  process=subprocess.Popen(common+['--logfile='+str(log)]+extra+['astro-verify'],env=env,cwd=w,stdout=stream,stderr=subprocess.STDOUT);started=time.monotonic()
  try:
   while process.poll() is None and time.monotonic()-started<1200:
    if 'FAIL' in log.read_text():process.terminate();break
    time.sleep(.25)
   if process.poll() is None:process.terminate()
   process.wait(timeout=10)
  finally:
   if process.poll() is None:process.kill();process.wait(timeout=10)
 text=log.read_text();assert process.returncode==0 and 'FAIL' not in text and marker in text,text[-5000:]
 assert text.rstrip().endswith('--- Log closed successfully.') and re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==[driver]
 assert d(exe)==expected
 if not extra:
  points=re.findall(r'P510 ASVM28 byte roundtrip: PASS \(boundary(\d+),4540bytes',text);assert points and int(points[-1])>=30
  assert '4540 truncations,4540 single-byte flips,23 checksummed invalid fields' in text
  assert 'P510 ASVM28 physical slot27: PASS' in text and 'P510 nested Engine pause install: PASS' in text
  assert len(re.findall(r'Astronomica P510 route \d: PASS',text))==8
  rows=re.findall(r'P510 live install: PASS \(accepted(\d+),excluded(\d+),cross(\d+),starts(\d+),commits(\d+)',text);assert rows and int(rows[-1][2])==7 and rows[-1][3]==rows[-1][4]
  assert text.count('P510 ownership release: PASS (empty holder)')==int(rows[-1][4])
  coverage=dict(boundaries=int(points[-1]),cross_destinations=7,commits=int(rows[-1][4]),starts=int(rows[-1][3]),truncations=4540,corruptions=4540,invalid_states=23,original_routes=8)
  physical_slot_sha=d(savepath/'astro-verify.027')
 else:assert d(savepath/'astro-verify.027')==physical_slot_sha
 logs[name]=d(log);print(name+' PASS',flush=True)
listed=subprocess.run(common+['--list-saves'],cwd=w,env=env,capture_output=True,text=True,timeout=60);assert listed.returncode==0 and 'P510 native paused continuation' in listed.stdout
(w/(prefix+'p510-saves-list.log')).write_text(listed.stdout+listed.stderr)
for alias,source in fixtures.items():assert d(source)==d(savepath/('astro-verify.%03d'%alias))==fixture_sha[str(alias)]
assert assets=={p.name:d(p) for p in Path('D:/astro/PLACES/P510').iterdir() if p.is_file()} and global912==d(Path('D:/astro/SOUNDS/S12.WAV')) and d(exe)==expected
proof=dict(date=datetime.now().date().isoformat(),status='PASS',scope='trusted_p510_ordinary_countdown',format_version=28,payload_bytes=4540,slot=27,exe_sha256=expected,diagnostic=bool(args.tag),audio_driver='dummy' if args.dummy_audio else 'native',actual_audio_driver=driver,metadata_listed=True,fresh_process=True,fresh_slot_unchanged=True,paused_source_save=True,paused_recipient_load=True,original_assets_sha256=assets,global_success_wav_sha256=global912,fixture_sha256=fixture_sha,fixtures_unchanged=True,slot_sha256=d(savepath/'astro-verify.027'),log_sha256=logs,**coverage)
(w/(prefix+'p510-save-proof.json')).write_text(json.dumps(proof,indent=2)+'\n');print('P510 actual bytes,physical fresh process,metadata PASS',flush=True)
