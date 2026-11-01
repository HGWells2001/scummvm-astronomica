"""Read all three genuine sealed P512 v29 slots with true/false entry settings."""
from pathlib import Path
import argparse,hashlib,json,os,re,struct,subprocess
ap=argparse.ArgumentParser();ap.add_argument('--exe',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
w=Path(__file__).resolve().parent;exe=a.exe.resolve();out=a.out.resolve();out.mkdir(exist_ok=False)
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected=d(exe);snapshot=w/'verified-checkpoints/p512-932d7f582215'
env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env.pop('SDL_AUDIODRIVER',None)
hashes={28:'593ba739a24a429cf574bdbd1c2e55a9263d4674ce3305184809c7c7adbf6a75',29:'0fe72555055d995b6f4b89de95cf666286ed0227e0a90cf3915e43928ccee4ce',30:'4ce119a412bf51ac99a952e8e2568b6a72bb921317ed1089861a0407a5a5535d'};cases={}
for slot,sha in hashes.items():
    descriptor=json.loads((snapshot/('frozen-slot%d.json'%slot)).read_text());path=snapshot/('frozen-slot%d'%slot)/('astro-verify.%03d'%slot)
    assert descriptor['status']=='FROZEN_VERIFIED_V29' and descriptor['origin_commit']=='5000da749a05de7604fd6dc9f0d9313a4aa901bb'
    assert descriptor['producing_exe_sha256']=='932d7f5822152b41edeaddc6f0bdefdcbad1a334f439507c82497a6471b8932b' and descriptor['slot_sha256']==d(path)==sha
    raw=path.read_bytes();assert raw[:4]==b'ASVM' and struct.unpack_from('<I',raw,4)[0]==29
    words=struct.unpack_from('<2481I',raw,8);h=2166136261
    for v in words[:-1]:h=((h^v)*16777619)&0xffffffff
    assert words[-1]==h and words[0]==512 and words[4]==0 and words[5]==words[7]==1
    if slot!=28:assert words[1]==words[24+28*3]==slot-29 and words[24+309]==127
    for entry in ('true','false'):
        label='slot%d-%s'%(slot,entry);cfg=out/(label+'.ini');log=out/(label+'.log')
        cfg.write_text('[scummvm]\nautosave_period=0\nconfirm_exit=false\nenable_unsupported_game_warning=false\ngui_language=en\ngui_theme=builtin\n[astro-verify]\nengineid=astronomica\ngameid=astronomica\npath=D:/astro\nastronomica_audio=true\nastronomica_animation=true\nastronomica_sprite_input=true\nastronomica_entry_scripts='+entry+'\nastronomica_verify_p512=true\nsavepath='+path.parent.as_posix()+'\n')
        with (out/(label+'-console.log')).open('w') as console:
            result=subprocess.run([str(exe),'--config='+str(cfg),'--extrapath='+str(w/'fonts'),'--savepath='+str(path.parent),'--logfile='+str(log),'--debuglevel=1','--save-slot='+str(slot),'astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT,timeout=600)
        text=log.read_text();assert result.returncode==0 and 'FAIL' not in text and 'P512 ASVM29 fresh physical continuation: PASS' in text,text[-3000:]
        assert 'introduction:' not in text and re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi'] and text.rstrip().endswith('--- Log closed successfully.')
        if slot!=28:assert ('P512 ordinary final continuation: PASS (priorGlobal%d,P157,count1,'%(slot-29)) in text
        assert d(path)==sha and d(exe)==expected
        cases[label]=dict(slot=slot,entry_scripts=entry=='true',slot_sha256=sha,log_sha256=d(log),unchanged=True)
        print(label+' genuine v29 continuation PASS',flush=True)
(out/'frozen-v29-proof.json').write_text(json.dumps(dict(status='PASS',scope='genuine_sealed_v29_active_music_and_final_first_repeated',exe_sha256=expected,origin_commit='5000da749a05de7604fd6dc9f0d9313a4aa901bb',actual_audio_driver='wasapi',cases=cases,public_validation=False),indent=2)+'\n')
