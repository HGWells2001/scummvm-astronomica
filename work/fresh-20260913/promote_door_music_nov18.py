"""Install only after the physical candidate passes all declared native gates."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,shutil,subprocess,sys
w=Path(__file__).resolve().parent;r=w.parents[1];o=r/'outputs/astronomica-cleanroom';s=w/'door-music-candidate-nov18b-stage';read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=read(w/'p513-control-music-seal-nov17.json');build=read(s/'proof.json');pin=build['candidate_exe_sha256'];exe=w/'build/Releasex64/scummvm.exe'
assert sha(exe)==parent['exe_sha256'] and sha(s/'bin/scummvm.exe')==pin
gates={}
for n in ['door-music-source-review-nov18.json','door-music-payload-review-nov18.json','door-music-final-native-nov18/proof.json','door-music-windows-native-nov18/proof.json','door-music-genuine-nov18/proof.json','door-music-general-nov18/proof.json','door-music-regional-regression-nov18/proof.json','door-music-scene-regression-nov18/proof.json','door-music-p513-regression-nov18/proof.json','door-music-p504-regression-nov18b/proof.json']:
    p=read(w/n);assert p['status'].endswith('PASS') and p.get('candidate_exe_sha256',p.get('consumer_exe_sha256'))==pin,n;gates[n]=sha(w/n)
assert read(w/'door-music-general-nov18/proof.json')['native_exited_naturally']
assert read(w/'door-effects-original-nov18.json')['status']=='ORIGINAL_SHARED_DOOR_EFFECTS_EVIDENCE_PASS';gates['door-effects-original-nov18.json']=sha(w/'door-effects-original-nov18.json')
for folder in(o/'engine/astronomica',w/'scummvm/engines/astronomica'):
    assert {n:sha(folder/n)for n in parent['engine_sha256']}==parent['engine_sha256']
for n,h in parent['framework_sha256'].items():assert sha(w/'scummvm'/n)==h
query="Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq '"+str(exe)+"' } | Select-Object -ExpandProperty ProcessId"
assert not subprocess.run(['powershell','-NoProfile','-Command',query],capture_output=True,text=True,check=True).stdout.strip(),'Workspace game is running; keep it untouched'
snapshot=w/'verified-checkpoints'/('door-music-'+pin[:12]);snapshot.mkdir(exist_ok=False);(snapshot/'engine/astronomica').mkdir(parents=True);(snapshot/'bin').mkdir()
for n,h in build['candidate_engine_sha256'].items():assert sha(s/'source/engines/astronomica'/n)==h;shutil.copyfile(s/'source/engines/astronomica'/n,snapshot/'engine/astronomica'/n)
for n in('scummvm.exe','SDL2.dll'):shutil.copyfile(s/'bin'/n,snapshot/'bin'/n)
spec=read(r/'publish/scummvm-astronomica/framework-patch.json');assert spec['engine_sha256']==parent['engine_sha256'];spec['engine_sha256']=build['candidate_engine_sha256'];(snapshot/'framework-patch.json').write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
receipt=dict(status='DOOR_MUSIC_VERIFIED_LOCAL_INTEGRATION_PASS',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=pin,previous_exe_sha256=parent['exe_sha256'],engine_sha256=build['candidate_engine_sha256'],framework_sha256=parent['framework_sha256'],snapshot=str(snapshot),gates=gates,user_installation_ignored=True,source_publication_pending=True,whole_game_completion_percent=None)
(snapshot/'CONTRACT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
manifest={p.relative_to(snapshot).as_posix():sha(p)for p in snapshot.rglob('*')if p.is_file()};(snapshot/'snapshot-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
targets={folder/'astronomica.cpp':(s/'source/engines/astronomica/astronomica.cpp').read_bytes()for folder in(o/'engine/astronomica',w/'scummvm/engines/astronomica')};targets[exe]=(s/'bin/scummvm.exe').read_bytes();saved={p:p.read_bytes()for p in targets};done=[]
try:
    for p,data in targets.items():temp=p.with_name(p.name+'.door-install.tmp');temp.write_bytes(data);os.replace(temp,p);done.append(p)
    assert sha(exe)==pin
    for folder in(o/'engine/astronomica',w/'scummvm/engines/astronomica'):assert {n:sha(folder/n)for n in build['candidate_engine_sha256']}==build['candidate_engine_sha256']
except Exception:
    for p in reversed(done):p.write_bytes(saved[p])
    raise
(w/'door-music-integration-nov18.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(receipt['status'])
