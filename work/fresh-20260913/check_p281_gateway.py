"""Actual ordinary P281 gateway and unsolved returns on one reviewed executable."""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess
ap=argparse.ArgumentParser();ap.add_argument('--exe',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
w=Path(__file__).resolve().parent;exe=a.exe.resolve();out=a.out.resolve();out.mkdir(exist_ok=False)
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected=d(exe)
assets={}
for place in [281,506,531,532,533,534,535,519]:
    for f in (Path('D:/astro/PLACES')/('P%d'%place)).iterdir():
        if f.is_file():assets[f'PLACES/P{place}/{f.name}']=d(f)
for name in ('S12.WAV','S22.WAV'):assets['SOUNDS/'+name]=d(Path('D:/astro/SOUNDS')/name)
cfg=out/'gateway.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=true\nastronomica_verify_p512=true\nastronomica_verify_p281_gateway=true\nsavepath='+out.as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
log=out/'gateway.log'
with (out/'console.log').open('w') as console:
    result=subprocess.run([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--savepath='+str(out),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT,timeout=1200)
text=log.read_text();assert result.returncode==0 and 'FAIL' not in text and text.rstrip().endswith('--- Log closed successfully.'),text[-3500:]
assert re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi']
for marker,count in [('P281 full gateway route: PASS',2),('P281 unsolved full route: PASS',2),('P281 unsolved return: PASS',6),('P281 save refusal: PASS',14),('P281 idle v2 roundtrip: PASS',2),('P281 original blocking voice: S912',2),('P281 original blocking voice: S922',4),('Astronomica P519 introduction: S300.WAV',4),('P519 entry scripts: 3 queued, 0 skipped',4)]:assert text.count(marker)==count,(marker,text.count(marker))
assert 'P281 real original gateway verification: PASS' in text and 'P281 return-round verification: PASS' in text
for route in (0,1):
    assert f'P281 full gateway route: PASS (route{route},P519,first/repeated count1,' in text
    assert f'P281 unsolved full route: PASS (route{route},P519,first/repeated count2,' in text
    for round_ in (1,2,3):assert re.search(r'P281 unsolved return: PASS \(route%d,round%d,P(?:506|53[1-5]) -> P281,mask\d+ retained\)'%(route,round_),text)
assert text.count('424 bytes,restored original gateway,custom25 excluded')==2
assert text.count('zero bytes,unchanged runner')==14 and d(exe)==expected
for name,sha in assets.items():assert d(Path('D:/astro')/name)==sha
proof=dict(status='PASS',scope='p281_actual_original_gateway_and_unsolved_returns',exe_sha256=expected,actual_audio_driver='wasapi',ordinary_entry=True,original_delay_ms=5000,solved_routes=2,unsolved_routes=2,unsolved_exits=6,zero_byte_save_refusals=14,idle_v2_roundtrips=2,first_repeated_completion=True,unrelated_custom25_excluded=True,original_round3_exit_completion_preserved=True,manual_startup_enqueue=False,loop_statics_not_manually_reset=True,source_assets_sha256=assets,log_sha256=d(log),config_sha256=d(cfg),new_save_format=False,public_validation=False)
(out/'gateway-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('Exact executable P281 actual gateway,all return rounds,first/repeated outcome and v2 save gate PASS',flush=True)
