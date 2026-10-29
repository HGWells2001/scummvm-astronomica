"""Normal-entry proof on any exact reviewed executable; no general-suite or publication claim."""
from pathlib import Path
import argparse,hashlib,json,re,os,subprocess,struct
a=argparse.ArgumentParser();a.add_argument('--exe',required=True,type=Path);a.add_argument('--out',required=True,type=Path);a.add_argument('--reuse-native-dir',action='store_true');args=a.parse_args()
w=Path(__file__).resolve().parent;exe=args.exe.resolve();out=args.out.resolve();d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected=d(exe)
assets={p.name:d(p) for p in Path('D:/astro/PLACES/P510').iterdir() if p.is_file()}
original=json.loads((w/'p510-file-save-stage/native-audio-run/native-file-proof.json').read_text())['original_assets_sha256'];assert assets==original
global_success=d(Path('D:/astro/SOUNDS/S12.WAV'));frozen_slot=w/'verified-checkpoints/p501-025e82d8bd3b/frozen-slot26/astro-verify.026';assert d(frozen_slot)=='adcc9b9be47d0b7153a94eb3b9883b85a12090fbd64e8793e32e61daeeea81fa'
if not args.reuse_native_dir:
 out.mkdir(exist_ok=False)
 env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
 cfgtext='[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_verify_p510=true\nastronomica_verify_p510_ordinary_entry=true\nastronomica_entry_scripts=ENTRY\nsavepath='+out.as_posix()+'\n'
 slot_sha=None
 for label,entry,extra in [('initial','true',[]),('fresh-true','true',['--save-slot=27']),('fresh-false','false',['--save-slot=27'])]:
  cfg=out/(label+'.ini');cfg.write_text(cfgtext.replace('ENTRY',entry));common=[str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--savepath='+str(out),'--debuglevel=1']
  with (out/(label+'-console.log')).open('w') as console:result=subprocess.run(common+['--logfile='+str(out/(label+'.log'))]+extra+['astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT,timeout=600)
  assert result.returncode==0
  if label=='initial':slot_sha=d(out/'astro-verify.027')
  else:assert d(out/'astro-verify.027')==slot_sha
 listed=subprocess.run(common+['--list-saves'],cwd=w,env=env,capture_output=True,text=True,timeout=60);assert listed.returncode==0;(out/'listed.log').write_text(listed.stdout+listed.stderr)
logs={n:(out/(n+'.log')).read_text() for n in ('initial','fresh-true','fresh-false','listed')}
for n in ('initial','fresh-true','fresh-false'):
 t=logs[n];assert 'FAIL' not in t and t.rstrip().endswith('--- Log closed successfully.') and re.findall(r'Using SDL Audio Driver "([^"]+)"',t)==['wasapi']
 assert 'P510 ASVM28 fresh physical continuation: PASS' in t
for n in ('fresh-true','fresh-false'):assert 'introduction:' not in logs[n]
initial=logs['initial'];assert initial.count('Astronomica P510 introduction: S300.WAV')==1
assert 'P510 entry scripts: 4 queued, 0 skipped' in initial and 'P510 ordinary loaded: loop0 enabled1 lastSound300 active0 starts1 queued4' in initial
counts=re.findall(r'P510 ordinary ready: PASS \(loop0 disabled,inactive,count(\d+),',initial);assert len(counts)==1 and 1<=int(counts[0])<=51
assert 'P510 ordinary paused ASVM28 save: PASS' in initial and 'P510 ASVM28 byte roundtrip: PASS (boundary1,4540bytes,paused source/recipient' in initial
assert 'P510 native paused continuation' in logs['listed']
slot=out/'astro-verify.027';data=slot.read_bytes();assert data[:4]==b'ASVM' and struct.unpack_from('<I',data,4)[0]==28
words=struct.unpack_from('<1133I',data,8);h=2166136261
for word in words[:-1]:h=((h^word)*16777619)&0xffffffff
assert words[-1]==h and words[0]==510 and words[4]==0 and words[5]==0 and words[7]==0
assert d(exe)==expected and assets=={p.name:d(p) for p in Path('D:/astro/PLACES/P510').iterdir() if p.is_file()} and d(Path('D:/astro/SOUNDS/S12.WAV'))==global_success
proof=dict(status='PASS',scope='actual_ordinary_entry_retained_disabled_loop0',exe_sha256=expected,entry_scripts=True,source_loop_id=0,loop_enabled=False,
 intro_id=300,actual_intro_starts=1,intro_drained=True,original_startup_programs_queued=4,manual_startup_enqueue=False,
 actual_audio_driver='wasapi',ordinary_ready_count=int(counts[0]),payload_bytes=4540,format_version=28,slot=27,slot_sha256=d(slot),
 paused_source_byte_roundtrip=True,fresh_entry_true=True,fresh_entry_false=True,no_intro_replay=True,metadata_listed=True,
 fresh_loop_id=0,fresh_loop_identity_basis='Physical slot word4=0; exact reviewed load/commit transfers word4 literally; no separate fresh-process loop print',
 source_assets_sha256=assets,s0_sha256=assets['S0.WAV'],s300_sha256=assets['S300.WAV'],global_success_wav_sha256=global_success,
 frozen_v27_slot_sha256=d(frozen_slot),log_sha256={n+'.log':d(out/(n+'.log')) for n in logs},
 configuration_evidence='Dedicated checker writes immutable per-run configs' if not args.reuse_native_dir else 'Existing verify_p510_ordinary_entry.py loop configured true/false before each process',
 checker_sha256=d(Path(__file__)),implementation_author=True,independent_review=False,production_release_approved=False)
(out/'ordinary-entry-gate-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('Actual ordinary P510 entry,loop0paused bytes,fresh true/false and metadata PASS')
