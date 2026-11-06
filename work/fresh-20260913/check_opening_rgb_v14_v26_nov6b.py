"""Author-only plan by default; --run executes the original entry=false v14..26 verifier contract.

Every process receives its own copied historical slot in a new savepath.
Frozen files and original thirteen configs are never written.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,configparser,hashlib,json,os,re,shutil,struct,subprocess,time,traceback

ap=argparse.ArgumentParser();ap.add_argument('--run',action='store_true');a=ap.parse_args()
w=Path(__file__).resolve().parent;s=w/'opening-rgb-nov6-stage'
out=w/'opening-rgb-genuine-v14-v26-nov6b';d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
specs={
 14:('rocket','Rocket',13),15:('universe','Universe',14),16:('probe','Probe',15),
 17:('rendezvous','Rendezvous',16),18:('planet','Planet',17),19:('p521','P521',18),
 20:('p509','P509',19),21:('p511','P511',20),22:('p516','P516',21),
 23:('p527','P527',22),24:('p502','P502',23),25:('p503','P503',24),26:('p504','P504',25)}

def block(source,opening):
    """Return a brace-delimited C++ block, ignoring comments/quoted text."""
    assert source[opening]=='{'
    depth=0;i=opening;quote=None;comment=None
    while i<len(source):
        c=source[i];pair=source[i:i+2]
        if comment=='line':
            if c=='\n':comment=None
        elif comment=='block':
            if pair=='*/':comment=None;i+=1
        elif quote:
            if c=='\\':i+=1
            elif c==quote:quote=None
        elif pair=='//':comment='line';i+=1
        elif pair=='/*':comment='block';i+=1
        elif c in ('"',"'"):quote=c
        elif c=='{':depth+=1
        elif c=='}':
            depth-=1
            if depth==0:return source[opening:i+1]
        i+=1
    raise AssertionError('Unclosed C++ block')

def author_plan():
    source_stage=s if(s/'astronomica.cpp').exists()else w/'p525-physical-nov3b-stage'
    source=(source_stage/'astronomica.cpp').read_text();rows=[]
    for version,(label,method,slot)in specs.items():
        matches=[]
        for manifest in sorted((w/'verified-checkpoints').glob('*/frozen*slot*.json')):
            m=json.loads(manifest.read_text())
            if m.get('status')!='FROZEN_VERIFIED_V%d'%version:continue
            number=m.get('slot',int(manifest.stem.rsplit('slot',1)[1]))
            path=manifest.parent/manifest.stem/('astro-verify.%03d'%number)
            raw=path.read_bytes()
            assert raw[:4]==b'ASVM' and struct.unpack_from('<I',raw,4)[0]==version
            assert number==slot and d(path)==m['slot_sha256']
            assert m.get('origin_commit') and m.get('producing_exe_sha256')
            matches.append((manifest,m,path,raw))
        assert len(matches)==1,(version,len(matches))
        manifest,m,path,raw=matches[0]
        cfg=w/('verify-%s-saves.ini'%label);c=configparser.ConfigParser(interpolation=None);c.read(cfg)
        flag='astronomica_verify_%s_saves'%label
        assert c.getboolean('astro-verify',flag)
        assert not c.getboolean('astro-verify','astronomica_entry_scripts'), 'Original verifier config must use entry=false'
        other=[key for key,value in c['astro-verify'].items()if key.startswith('astronomica_verify')and value.lower()=='true'and key not in(flag,'astronomica_verify_save_files')]
        assert not other,(label,other)
        begin=source.index('bool AstronomicaEngine::verify'+method+'Saves(')
        method_body=block(source,source.index('{',begin))
        guard=re.search(r'if\s*\(\s*ConfMan\.hasKey\("save_slot"\).*?ConfMan\.getInt\("save_slot"\)\s*==\s*'+str(slot)+r'\s*\)\s*\{',method_body,re.S)
        assert guard,(version,method)
        fresh=block(method_body,method_body.index('{',guard.start()))
        marker='Astronomica %s startup save: '%(method if re.fullmatch(r'P\d+',method)else method.lower())
        assert marker in fresh and 'return ok;'in fresh,(version,marker)
        assert 'saveGameState('not in fresh and 'openForSaving('not in fresh
        # The fixture-producing writes must be below the guarded fresh path.
        prefix=method_body[:guard.start()]
        if 'saveGameState('in prefix:
            assert version==14 and prefix.count('saveGameState(')==1
            assert 'if (physical) { fixture = saved; if (saveGameState(13,'in prefix
            assert 'roundTrip('not in fresh
        later=method_body[method_body.index(fresh,guard.start())+len(fresh):]
        assert 'saveGameState('in later or (version==14 and re.search(r'roundTrip\([^\)]*,\s*true\)',later)),(version,'No historical fixture writer found')
        rows.append(dict(version=version,scene=struct.unpack_from('<I',raw,8)[0],slot=slot,label=label,
            method='verify'+method+'Saves',verification_flag=flag,expected_marker=marker+'PASS',
            manifest=str(manifest),manifest_sha256=d(manifest),frozen_path=str(path),slot_sha256=d(path),
            producing_exe_sha256=m['producing_exe_sha256'],origin_commit=m['origin_commit'],
            config_path=str(cfg),config_sha256=d(cfg),fresh_branch_sha256=hashlib.sha256(fresh.encode()).hexdigest(),
            fresh_branch_returns_before_fixture_writer=True,entry_settings=['false']))
    return dict(status='AUTHOR_ONLY_SUPPORTED_ENTRYFALSE_V14_V26_PLAN',authored_at=datetime.now(timezone.utc).isoformat(),
        driver_sha256=d(Path(__file__)),candidate_source_sha256=d(source_stage/'astronomica.cpp'),author_source_stage=str(source_stage),
        genuine_versions=list(specs),artifacts=rows,planned_processes=13,native_run=False,
        frozen_boundary='verified-checkpoints/*/frozen*slot*.json with exact FROZEN_VERIFIED_V14..26 status and recorded origin/executable/hash',
        limits=['13genuine artifacts, original entry=false verifier contract only; not versions1..13 or entry=true',
            'Source review proves guarded early return before fixture-writing blocks; copied inputs and post-process hashes protect originals independently',
            'Native author fixtures are not run intentionally; any unexpected copied-slot write fails the immutable-copy check',
            'No executable mutation, release, original-executable parity or listening claim'])

plan=author_plan()
if not a.run:
    (w/'p523-complete-genuine-v14-v26-author-nov5.json').write_text(json.dumps(plan,indent=2)+'\n')
    print(plan['status'],len(plan['artifacts']),'artifacts',plan['planned_processes'],'processes pending')
    raise SystemExit(0)

review=s/'source-review-proof.json';fresh=w/'opening-rgb-fresh-nov6/proof.json'
r=json.loads(review.read_text());f=json.loads(fresh.read_text());exe=s/'complete-build/bin/scummvm.exe'
assert r['status']=='OPENING_RGB_ONLY_DELTA_REVIEW_PASS' and f['status']=='P523_ASVM31_COMPLETE_SIX_FRESH_PROCESSES_PASS'
assert r['candidate_exe_sha256']==f['candidate_exe_sha256']==d(exe)
assert f['stage_sha256']==f['stage_sha256']=={n:d(s/n)for n in f['stage_sha256']}
assert f['source_physical_proof_sha256']==d(s/'complete-build/native-proof.json')
assert plan['candidate_source_sha256']==f['stage_sha256']['astronomica.cpp']
exe_pin=d(exe);review_pin=d(review);fresh_pin=d(fresh);own=d(Path(__file__))
out.mkdir(exist_ok=False)
def state(value,**fields):
    (out/'status.json').write_text(json.dumps(dict(status=value,driver_pid=os.getpid(),updated_at=datetime.now(timezone.utc).isoformat(),
        candidate_exe_sha256=exe_pin,main_modified=False,public_support=False,**fields),indent=2)+'\n')
def validate():
    assert d(exe)==exe_pin and d(review)==review_pin and d(fresh)==fresh_pin and d(Path(__file__))==own
    assert f['stage_sha256']=={n:d(s/n)for n in f['stage_sha256']}
    for row in plan['artifacts']:
        assert d(Path(row['manifest']))==row['manifest_sha256'] and d(Path(row['frozen_path']))==row['slot_sha256']
        assert d(Path(row['config_path']))==row['config_sha256']
try:
    state('RUNNING_GENUINE_V14_V26');runs=[];logs={};configs={}
    (out/'input-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    env={k.upper():v for k,v in os.environ.items()};env['SDL_VIDEODRIVER']='dummy';env['SDL_AUDIODRIVER']='wasapi'
    for row in plan['artifacts']:
        for entry in row['entry_settings']:
            validate();label='v%d-slot%d-%s'%(row['version'],row['slot'],entry)
            folder=out/label;folder.mkdir();slots=folder/'slots';slots.mkdir()
            incoming=slots/Path(row['frozen_path']).name;shutil.copyfile(row['frozen_path'],incoming)
            assert d(incoming)==row['slot_sha256']
            cfg=configparser.ConfigParser(interpolation=None);cfg.read(row['config_path'])
            cfg['scummvm']['mute']='true';cfg['scummvm']['autosave_period']='0';cfg['scummvm']['confirm_exit']='false'
            cfg['scummvm']['sfx_volume']='0';cfg['scummvm']['music_volume']='0';cfg['scummvm']['speech_volume']='0'
            cfg['astro-verify']['savepath']=slots.as_posix();cfg['astro-verify']['astronomica_entry_scripts']=entry
            config=folder/'verify.ini'
            with config.open('w')as stream:cfg.write(stream)
            log=folder/'native.log';state('RUNNING_GENUINE_V14_V26',case=label,completed=len(runs),total=13)
            with(folder/'console.log').open('w')as console:
                child=subprocess.Popen([str(exe),'--config='+str(config),'--extrapath='+str(w/'fonts'),'--savepath='+str(slots),
                    '--logfile='+str(log),'--debuglevel=1','--save-slot='+str(row['slot']),'astro-verify'],cwd=w,env=env,stdout=console,stderr=subprocess.STDOUT)
                try:
                    deadline=time.monotonic()+600
                    while child.poll()is None:
                        observed=log.read_text(errors='replace')if log.exists()else''
                        if 'FAIL'in observed or time.monotonic()>=deadline:
                            child.terminate();break
                        time.sleep(.25)
                    code=child.wait(timeout=15)
                finally:
                    if child.poll()is None:
                        child.terminate()
                        try:child.wait(timeout=15)
                        except subprocess.TimeoutExpired:child.kill();child.wait(timeout=15)
            text=log.read_text();assert code==0 and 'FAIL'not in text and text.rstrip().endswith('--- Log closed successfully.'),text[-3000:]
            assert row['expected_marker']in text
            assert re.findall(r'Using SDL Audio Driver "([^"]+)"',text)==['wasapi']
            assert d(incoming)==row['slot_sha256'],'Fresh branch wrote its copied input: '+label
            assert sorted(p.name for p in slots.iterdir())==[incoming.name],'Unexpected fixture save files: '+label
            validate();logs[label]=d(log);configs[label]=d(config)
            runs.append(dict(label=label,version=row['version'],slot=row['slot'],entry_scripts=entry,pid=child.pid,
                frozen_slot_sha256=row['slot_sha256'],copied_slot_sha256=d(incoming),expected_marker=row['expected_marker']))
            print(label+' PASS',flush=True)
    assert len(runs)==13
    result=dict(status='P523_COMPLETE_GENUINE_V14_V26_ENTRYFALSE_WASAPI_PASS',completed_at=datetime.now(timezone.utc).isoformat(),
        driver_sha256=own,candidate_exe_sha256=exe_pin,stage_sha256=f['stage_sha256'],
        source_physical_review_sha256=review_pin,source_physical_fresh_sha256=fresh_pin,
        versions=list(specs),genuine_artifacts=13,fresh_processes=13,entry_true_false=False,entry_scripts=False,scope='original_false_entry_verifier_contract',
        original_configs_unchanged=True,frozen_inputs_unchanged=True,copied_inputs_unchanged=True,
        no_fixture_save_files_created=True,actual_audio_driver='wasapi',muted=True,
        runs=runs,log_sha256=logs,config_sha256=configs,main_modified=False,public_support=False,
        limits=['Original supported existing verifier entry=false only; exploratory entry=true attempt remains preserved separately with9PASS and knownv18failure, never a26casePASS',
            'Genuine versions14..26 only; versions27..29 have a separate matrix, versions1..13 not covered here',
            'Existing native original-control continuation checks; no original-executable runtime/listening or whole-game claim'])
    (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n');state('PASS',proof_sha256=d(out/'proof.json'))
except Exception:state('FAILED',error=traceback.format_exc());raise
