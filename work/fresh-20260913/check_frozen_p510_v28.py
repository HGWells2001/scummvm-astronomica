"""Read both genuine sealed v28 identities with one candidate executable.

All generated configs/logs are in --out; genuine inputs are never rewritten.
This proves compatibility only, not a complete native/public closure.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,struct,subprocess

ap=argparse.ArgumentParser();ap.add_argument('--exe',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
w=Path(__file__).resolve().parent;exe=a.exe.resolve();out=a.out.resolve();out.mkdir(exist_ok=False)
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected=d(exe)
snapshot=w/'verified-checkpoints/p510-6dd09d6494b2'
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
cases={}
for kind,loop,sha in [('frozen-slot27',0xffffffff,'3af0c600dba212763a1c8fd26856604f9fab84e72deeafa52904733e8176d6d2'),('frozen-ordinary-slot27',0,'4866b333e816f36ec6ce6e80d640d2b2260ec0d52a1a984d31c8f2f35dacbb5f')]:
    descriptor=json.loads((snapshot/(kind+'.json')).read_text());slot=snapshot/kind/'astro-verify.027'
    assert descriptor['origin_commit']=='a56d2fd646ac440cf01139db32edc3483f0f25f7'
    assert descriptor['producing_exe_sha256']=='6dd09d6494b2c115579f46718b6c924b6f37c13307343e045e5bb38c87ba0f81'
    assert descriptor['slot_sha256']==d(slot)==sha
    raw=slot.read_bytes();assert raw[:4]==b'ASVM' and struct.unpack_from('<I',raw,4)[0]==28
    words=struct.unpack_from('<1133I',raw,8);h=2166136261
    for v in words[:-1]:h=((h^v)*16777619)&0xffffffff
    assert words[-1]==h and words[0]==510 and words[4]==loop and words[5]==words[7]==0
    for entry in ('true','false'):
        label=kind+'-'+entry;cfg=out/(label+'.ini');log=out/(label+'.log')
        cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts='+entry+'\nastronomica_verify_p510=true\nsavepath='+slot.parent.as_posix()+'\n')
        with (out/(label+'-console.log')).open('w') as console:
            result=subprocess.run([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--savepath='+str(slot.parent),'--logfile='+str(log),'--debuglevel=1','--save-slot=27','astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT,timeout=600)
        text=log.read_text()
        assert result.returncode==0 and 'FAIL' not in text and 'P510 ASVM28 fresh physical continuation: PASS' in text,text[-3000:]
        assert re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi'] and text.rstrip().endswith('--- Log closed successfully.')
        assert 'introduction:' not in text and d(slot)==sha and d(exe)==expected
        cases[label]=dict(loop_id=-1 if loop==0xffffffff else 0,entry_scripts=entry=='true',slot_sha256=sha,log_sha256=d(log),config_sha256=d(cfg),unchanged=True)
        print(label+' original frozen v28 continuation PASS',flush=True)
(out/'frozen-v28-proof.json').write_text(json.dumps(dict(status='PASS',scope='genuine_sealed_v28_two_literal_disabled_loop_ids',exe_sha256=expected,origin_commit=descriptor['origin_commit'],producing_exe_sha256=descriptor['producing_exe_sha256'],cases=cases,actual_audio_driver='wasapi',public_validation=False),indent=2)+'\n')
