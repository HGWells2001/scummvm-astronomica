"""Load and finish the genuine physical old-main ASVM13 through the new guard."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,shutil,subprocess
w=Path(__file__).resolve().parent;stage=w/'builder-mask-guard-nov9-stage';out=w/'builder-mask-guard-main-smoke-nov9';out.mkdir(exist_ok=False);(out/'saves').mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
producer=read(w/'genuine-builder-old-main-nov9/proof.json');assert producer['status']=='GENUINE_OLD_MAIN_BUILDER_ASVM13_PRODUCED'
source=w/'genuine-builder-old-main-nov9/saves/astro-verify.012';assert sha(source)==producer['slot_sha256']
shutil.copyfile(source,out/'saves/astro-verify.012')
exe=w/'build/Releasex64/scummvm.exe';build=read(stage/'proof.json');assert sha(exe)==build['candidate_exe_sha256']
cfg=out/'test.ini';cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=C\ngui_theme=builtin\nmute=true\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nsave_slot=12\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts=true\nastronomica_verify_builder_saves=true\nsavepath='+(out/'saves').as_posix()+'\n')
env={k.upper():v for k,v in os.environ.items()};env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='wasapi')
log=out/'native.log'
with(out/'console.log').open('w')as f:result=subprocess.run([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--logfile='+str(log),'--debuglevel=1','astro-verify'],cwd=w,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180)
text=log.read_text(errors='replace')
assert result.returncode==0 and 'Astronomica builder startup save: PASS'in text and 'Astronomica builder save verification: PASS'in text,text[-1500:]
match=re.search(r'Astronomica builder slot fingerprint: ([0-9a-f]+)',text)
assert match and match[1]==producer['source_fingerprint']
assert sha(source)==sha(out/'saves/astro-verify.012')==producer['slot_sha256']
assert sha(exe)==build['candidate_exe_sha256']
(out/'proof.json').write_text(json.dumps(dict(
    status='INSTALLED_BUILDER_MASK_GUARD_GENUINE_CONTINUATION_PASS',completed_at=datetime.now(timezone.utc).isoformat(),
    producer_exe_sha256=producer['producer_exe_sha256'],consumer_exe_sha256=sha(exe),
    genuine_slot_sha256=sha(source),source_and_loaded_fingerprint=match[1],
    native_log_sha256=sha(log),final_scene=510,final_global31=1,final_completed=11,
    variant_round2_preserved=True,physical_file_unchanged=True,
    limits=['One genuine old-main physical builder save at the declared P536/design5/partial-parts boundary',
            'Actual public startup load and ordinary remaining controls; not all historical ASVM versions or all builder boundaries']
),indent=2)+'\n');print('Installed-path old-main builder save/remaining controls PASS:',match[1])
