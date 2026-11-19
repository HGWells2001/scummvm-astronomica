from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,shutil,os
w=Path(__file__).resolve().parent;r=w.parents[1];pub=r/'publish/scummvm-astronomica';o=r/'outputs/astronomica-cleanroom';s=w/'italian-detection-nov19-stage'
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();git=lambda *a:subprocess.check_output(['git','-C',str(pub),*a],text=True).strip()
parent=read(w/'speech-duck-seal-nov19.json');build=read(s/'proof.json');tests=read(w/'italian-detection-tests-nov19/proof.json');pin=build['exe_sha256'];assert tests['status']=='ITALIAN_ENGLISH_ACTUAL_DETECTOR_PASS'and tests['exe_sha256']==pin
previous=git('rev-parse','HEAD');assert git('branch','--show-current')=='main'and not git('status','--porcelain')and git('ls-remote','origin','refs/heads/main').split()[0]==previous
engine=dict(parent['engine_sha256']);engine['detection.cpp']=build['detection_sha256']
for d in [o/'engine/astronomica',w/'scummvm/engines/astronomica',pub/'outputs/astronomica-cleanroom/engine/astronomica']:
 assert {p.name:sha(p)for p in d.iterdir()if p.is_file()}==parent['engine_sha256']
exe=w/'build/Releasex64/scummvm.exe';assert sha(exe)==parent['exe_sha256'];query="Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq '"+str(exe)+"' } | Select-Object -ExpandProperty ProcessId";assert not subprocess.run(['powershell','-NoProfile','-Command',query],capture_output=True,text=True,check=True).stdout.strip(),'Player running; leave untouched'
backup=w/'verified-checkpoints/italian-detection-nov19';backup.mkdir(exist_ok=False);shutil.copyfile(exe,backup/'previous-scummvm.exe');shutil.copyfile(o/'engine/astronomica/detection.cpp',backup/'previous-detection.cpp')
for dst in [o/'engine/astronomica/detection.cpp',w/'scummvm/engines/astronomica/detection.cpp']:
 t=dst.with_suffix('.qualified.tmp');shutil.copyfile(s/'source/engines/astronomica/detection.cpp',t);os.replace(t,dst)
t=exe.with_suffix('.qualified.tmp');shutil.copyfile(s/'bin/scummvm.exe',t);os.replace(t,exe);assert sha(exe)==pin
for root,lang in [('D:/astroita','Italian'),('D:/astro','English')]:
 q=subprocess.run([str(exe),'--path='+root,'--detect','--game=astronomica'],capture_output=True,text=True,check=True);assert lang in q.stdout,q.stdout

git('switch','-c','codex/italian-detection-nov19');shutil.copyfile(o/'engine/astronomica/detection.cpp',pub/'outputs/astronomica-cleanroom/engine/astronomica/detection.cpp')
for name in ['framework-patch.json','SCUMMVM_BASE.json']:
 q=pub/name;j=read(q);assert j['engine_sha256']==parent['engine_sha256'];j['engine_sha256']=engine
 if name=='SCUMMVM_BASE.json':j.update(validated_executable_sha256=pin,build_scope='Detection-only change: distinct English/Italian opening-scene signatures; actual detector tests pass on originals, neutral renamed folders and root-installed ASTRO.EXE. Missing discriminator never silently added as English. Runtime engine library and all speech-duck behavior unchanged from qualified parent.')
 q.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
exports=['build_italian_detection_nov19.py','check_italian_detection_nov19.py','release_italian_detection_nov19.py','italian-detection-nov19-stage/proof.json','italian-detection-tests-nov19/proof.json']
for name in exports:
 dst=pub/'work/fresh-20260913'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(w/name,dst)
doc="""# Riconoscimento della versione italiana

Il rilevatore identifica la lingua tramite la firma dei primi 5000 byte e la dimensione della scena PLACES/P1/MEGAFILE.HYP. GAMEDATA e ASTRO.EXE sono identici nelle due edizioni e non bastano a distinguere la lingua.

Inglese: MD5 dbad37cdf558f7687c98a66f38cc842d, 537831 byte.
Italiano: MD5 aa43748004160b8b2a33c3d21b1e2510, 498661 byte.

Entrambe le firme richiedono anche GAMEDATA (84099c2580e5c71beec97ca3e52a5967, 1604 byte) e ASTRO.EXE (14929fa8e52d7e3bc539244413703ecb, 418376 byte). Si usa il percorso completo della scena per evitare collisioni fra i molti MEGAFILE.HYP; i due file comuni possono trovarsi nelle sottocartelle originali oppure alla radice dell'installazione.

Prove con il rilevatore reale: D:/astroita viene aggiunto con language=it e D:/astro con language=en. Stesso risultato in due cartelle neutre, con ASTRO.EXE alla radice. I soli file comuni senza scena discriminante non vengono aggiunti come inglese. Nessun dato originale modificato. Il criterio non dipende da P503 e resta valido con la sua riparazione.

Cambia solo detection.cpp. Libreria del motore in esecuzione identica alla revisione audio qualificata; musica e parlato invariati. Non e una nuova verifica completa della giocabilita italiana. Per le partite gia aggiunte, rimuovere soltanto la voce dall'elenco e aggiungere di nuovo la cartella, oppure impostare Italiano nelle opzioni della voce esistente. I salvataggi e i file del gioco vanno conservati.
"""
for dst in [o/'ITALIAN-DETECTION.md',pub/'outputs/astronomica-cleanroom/ITALIAN-DETECTION.md']:dst.write_text(doc,encoding='utf-8')
prefix='# Current update: Italian edition recognition\n\nThe original opening-scene signature distinguishes Italian from English. Existing speech-over-Music behavior is preserved. See outputs/astronomica-cleanroom/ITALIAN-DETECTION.md.\n\n---\n\n'
for name in ['README.md','outputs/astronomica-cleanroom/NEXT-STEPS.md']:
 q=pub/name;q.write_text(prefix+q.read_text(encoding='utf-8'),encoding='utf-8')
shutil.copyfile(pub/'outputs/astronomica-cleanroom/NEXT-STEPS.md',o/'NEXT-STEPS.md')
m=pub/'SOURCE-MANIFEST.json';j=read(m);files=set(j['sha256'])|set(git('ls-files','--others','--exclude-standard').splitlines());j['sha256']={n:sha(pub/n)for n in sorted(files)};m.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8');subprocess.run(['python',str(pub/'tools/verify_export.py')],check=True)
git('add','--',*git('diff','--name-only').splitlines(),*git('ls-files','--others','--exclude-standard').splitlines());git('commit','-m','Recognize original Italian Astronomica through localized opening-scene signature');git('push','-u','origin','codex/italian-detection-nov19');commit=git('rev-parse','HEAD');clone=r/'publish/verify-italian-detection-nov19';subprocess.run(['git','clone','--depth','1','--branch','codex/italian-detection-nov19',git('remote','get-url','origin'),str(clone)],check=True);subprocess.run(['python',str(clone/'tools/verify_export.py')],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==previous;git('switch','main');git('merge','--ff-only','codex/italian-detection-nov19');git('push','origin','main');assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
seal=dict(status='ITALIAN_DETECTION_PUBLISHED_PASS',at=datetime.now(timezone.utc).isoformat(),published_commit=commit,exe_sha256=pin,engine_sha256=engine,framework_sha256=parent['framework_sha256'],parent_seal='speech-duck-seal-nov19.json',runtime_engine_unchanged=True,detector_tests=tests)
(w/'italian-detection-seal-nov19.json').write_text(json.dumps(seal,indent=2)+'\n',encoding='utf-8');c=read(o/'CURRENT-LOCAL-BUILD.json');c.update(status='VERIFIED_PUBLISHED_ITALIAN_DETECTION',exe_sha256=pin,main_exe_sha256=pin,engine_sha256=engine,published_commit=commit,last_published_commit=commit,last_published_exe_sha256=pin,seal_context='work/fresh-20260913/italian-detection-seal-nov19.json');(o/'CURRENT-LOCAL-BUILD.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8');print(seal['status'],commit)
