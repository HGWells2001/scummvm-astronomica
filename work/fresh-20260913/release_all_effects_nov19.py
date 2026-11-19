"""Publish the qualified all-effect routing expansion, preserving the previous runtime."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,shutil,subprocess,sys,time
w=Path(__file__).resolve().parent;r=w.parents[1];o=r/'outputs/astronomica-cleanroom';pub=r/'publish/scummvm-astronomica';s=w/'all-effects-candidate-nov19-stage'
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();git=lambda *a:subprocess.check_output(['git','-C',str(pub),*a],text=True).strip()
run=w/'all-effects-release-run-nov19';run.mkdir(exist_ok=False)
def state(status,**kw):(run/'status.json').write_text(json.dumps(dict(status=status,at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 state('WAITING_NATURAL_GENERAL_AND_GENUINE_COMPLETION')
 while not(w/'all-effects-general-nov19/proof.json').exists() or not(w/'all-effects-genuine-nov19/proof.json').exists():
  for d in ['all-effects-general-nov19','all-effects-genuine-nov19']:
   p=w/d/'status.json'
   if p.exists():assert read(p)['status']!='FAILED',d+' failed; nothing installed'
  time.sleep(1)
 parent=read(w/'progress-indicator-seal-nov19.json');build=read(s/'proof.json');pin=build['candidate_exe_sha256'];previous=git('rev-parse','HEAD');assert git('branch','--show-current')=='main'and not git('status','--porcelain')and git('ls-remote','origin','refs/heads/main').split()[0]==previous
 gates={}
 for n in ['all-effects-source-review-nov19.json','all-effects-payload-review-nov19.json','all-effects-native-nov19/proof.json','all-effects-windows-nov19/proof.json','all-effects-doors-nov19/proof.json','all-effects-progress-nov19b/proof.json','all-effects-navigation-nov19/proof.json','all-effects-general-nov19/proof.json','all-effects-genuine-nov19/proof.json']:
  p=read(w/n);assert p['status'].endswith('PASS')and p.get('candidate_exe_sha256',p.get('consumer_exe_sha256'))==pin,n;gates[n]=sha(w/n)
 assert sha(w/'build/Releasex64/scummvm.exe')==parent['exe_sha256']and sha(s/'bin/scummvm.exe')==pin
 for d in[o/'engine/astronomica',w/'scummvm/engines/astronomica']:
  assert {p.name:sha(p)for p in d.iterdir()if p.is_file()}==parent['engine_sha256']
 query="Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq '"+str(w/'build/Releasex64/scummvm.exe')+"' } | Select-Object -ExpandProperty ProcessId"
 assert not subprocess.run(['powershell','-NoProfile','-Command',query],capture_output=True,text=True,check=True).stdout.strip(),'Workspace player running; not replaced'
 snapshot=w/'verified-checkpoints'/('all-effects-'+pin[:12]);shutil.copytree(s/'source/engines/astronomica',snapshot/'engine/astronomica');shutil.copytree(s/'bin',snapshot/'bin')
 spec=read(pub/'framework-patch.json');assert spec['engine_sha256']==parent['engine_sha256'];spec['engine_sha256']=build['candidate_engine_sha256'];(snapshot/'framework-patch.json').write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
 targets={d/'astronomica.cpp':(s/'source/engines/astronomica/astronomica.cpp').read_bytes()for d in[o/'engine/astronomica',w/'scummvm/engines/astronomica']};targets[w/'build/Releasex64/scummvm.exe']=(s/'bin/scummvm.exe').read_bytes();saved={p:p.read_bytes()for p in targets};done=[]
 state('INSTALLING_QUALIFIED_RUNTIME')
 try:
  for p,data in targets.items():
   temp=p.with_name(p.name+'.all-effects.tmp');temp.write_bytes(data);os.replace(temp,p);done.append(p)
  subprocess.run([sys.executable,str(w/'check_all_effects_nov19.py'),'--installed','--windows'],check=True)
 except Exception:
  for p in reversed(done):p.write_bytes(saved[p])
  raise
 gates['all-effects-installed-nov19/proof.json']=sha(w/'all-effects-installed-nov19/proof.json')
 git('switch','-c','codex/all-sound-effects-nov19');names=[]
 def copy(src,name):
  dst=pub/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);names.append(name)
 for n in build['candidate_engine_sha256']:copy(s/'source/engines/astronomica'/n,'outputs/astronomica-cleanroom/engine/astronomica/'+n)
 copy(snapshot/'framework-patch.json','framework-patch.json');base=read(pub/'SCUMMVM_BASE.json');base.update(validated_executable_sha256=pin,engine_sha256=build['candidate_engine_sha256'],build_scope='102 exact effect identities across308 original WAV paths mixed over uninterrupted Music;205 speech/vocal and27 ambient identities retain routing. All632original WAV paths tested on native/Windows WASAPI;full general and genuine ASVM29 continuations PASS. Header,core3,60serialized methods and ambient selector unchanged. Machine-assisted acoustic/resource catalogue;not a full manual audiovisual playthrough.');(pub/'SCUMMVM_BASE.json').write_text(json.dumps(base,indent=2)+'\n',encoding='utf-8')
 doc='''# Musica ed effetti in contemporanea

La precedente correzione copriva13 registrazioni precise. Il catalogo ora copre tutti i632 WAV originali:102 effetti distinti (308 file con le copie),205 registrazioni vocali (277 file),27 sottofondi (47 file).

Gli effetti, comprese le registrazioni condivise S4/S6 e i controlli dei puzzle, mantengono lo stesso canale Music e il suo avanzamento. Le voci e le vocalizzazioni ambigue restano in primo piano senza musica. I file sconosciuti o modificati mantengono il comportamento prudente. Non vengono introdotti riconoscitori automatici nel gioco: il motore confronta le identita dei file originali.

La classificazione deriva da un'analisi acustica assistita da modelli e dal controllo dei comandi/selector originali. Non e un ascolto umano di ogni file. I risultati incerti con caratteristiche vocali restano trattati come voci. I dettagli e gli hash sono in work/fresh-20260913/audio-role-catalogue-nov19.json; audio e trascrizioni private non vengono distribuiti.

Controlli effettivi: tutti632 percorsi audio riprodotti nel mixer nativo e Windows;308 verifiche di sovrapposizione e continuita Music,324 di riproduzione esclusiva. Anche porte P27/P85,212 stati dell'indicatore,306 scene/760 percorsi, suite generale e vecchi salvataggi ASVM29 passano. Sono prove controllate del mixer e dello stato, non una registrazione acustica o una partita manuale completa.

La modifica non cambia formato dei salvataggi, header del motore, tre file del core o60 metodi di serializzazione. I filmati mantengono la propria gestione audio. Accettazione fissa7/10;percentuale complessiva non misurata.
'''
 for target in[o/'ALL-SOUND-EFFECTS.md',pub/'outputs/astronomica-cleanroom/ALL-SOUND-EFFECTS.md']:target.write_text(doc,encoding='utf-8',newline='\n')
 names.append('outputs/astronomica-cleanroom/ALL-SOUND-EFFECTS.md')
 items=['audio-role-catalogue-nov19.json','all_effects_source_nov19.py','build_all_effects_nov19.py','check_all_effects_nov19.py','check_all_effects_general_nov19.py','check_all_effects_genuine_nov19.py','check_all_effects_navigation_nov19.py','check_all_effects_progress_nov19.py','audit_all_effects_nov19.py','review_all_effects_payload_nov19.py','check_all_effects_publication_install_nov19.py','update_downloaded_all_effects_runtime_nov19.py','release_all_effects_nov19.py','all-effects-candidate-nov19-stage/proof.json']
 for n in sorted(set(items)|set(gates)):copy(w/n,'work/fresh-20260913/'+n)
 intro='# Current update: all original WAV effects keep Music\n\n102 exact effect identities across308 original file paths now overlap continuous Music;voices remain foreground. See outputs/astronomica-cleanroom/ALL-SOUND-EFFECTS.md for validation and classification limits.\n\n---\n\n'
 p=pub/'README.md';p.write_text(intro+p.read_text(),encoding='utf-8',newline='\n')
 p=pub/'outputs/astronomica-cleanroom/NEXT-STEPS.md';p.write_text(intro+p.read_text(),encoding='utf-8',newline='\n');shutil.copyfile(p,o/'NEXT-STEPS.md')
 for name in['AUDIO-MIX.md','DOOR-MUSIC.md']:
  p=pub/'outputs/astronomica-cleanroom'/name;p.write_text('Current catalogue: see ALL-SOUND-EFFECTS.md. The scope below is historical.\n\n'+p.read_text(),encoding='utf-8',newline='\n');shutil.copyfile(p,o/name)
 def manifest():
  m=read(pub/'SOURCE-MANIFEST.json');files=set(m['sha256'])|set(names);assert set(git('ls-files','--others','--exclude-standard').splitlines())<=files;m['sha256']={n:sha(pub/n)for n in sorted(files)};(pub/'SOURCE-MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');subprocess.run([sys.executable,str(pub/'tools/verify_export.py')],check=True)
 manifest();subprocess.run([sys.executable,str(w/'check_all_effects_publication_install_nov19.py')],check=True);copy(w/'all-effects-install-n19/proof.json','work/fresh-20260913/all-effects-install-n19/proof.json');manifest()
 git('add','--',*git('diff','--name-only').splitlines(),*git('ls-files','--others','--exclude-standard').splitlines());git('commit','-m','Mix all catalogued original sound effects over continuous exploration and puzzle music');git('push','-u','origin','codex/all-sound-effects-nov19');commit=git('rev-parse','HEAD');clone=r/'publish/verify-all-effects-nov19';subprocess.run(['git','clone','--single-branch','--branch','codex/all-sound-effects-nov19',git('remote','get-url','origin'),str(clone)],check=True);subprocess.run([sys.executable,str(clone/'tools/verify_export.py')],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==previous;git('switch','main');git('merge','--ff-only','codex/all-sound-effects-nov19');git('push','origin','main');assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
 seal=dict(status='ALL_EFFECTS_PUBLISHED_WORKSPACE_SEAL_PASS',at=datetime.now(timezone.utc).isoformat(),published_commit=commit,exe_sha256=pin,engine_sha256=build['candidate_engine_sha256'],framework_sha256=parent['framework_sha256'],snapshot=str(snapshot),gates=gates,independent_source_clone_verified=True,whole_game_completion_percent=None,fixed_acceptance=dict(passed=7,total=10,percent=70));(w/'all-effects-seal-nov19.json').write_text(json.dumps(seal,indent=2)+'\n',encoding='utf-8');current=read(o/'CURRENT-LOCAL-BUILD.json');current.update(status='VERIFIED_PUBLISHED_ALL_EFFECTS',exe_sha256=pin,main_exe_sha256=pin,engine_sha256=seal['engine_sha256'],source_snapshot=str(snapshot),published_commit=commit,last_published_commit=commit,last_published_exe_sha256=pin,seal_context='work/fresh-20260913/all-effects-seal-nov19.json',source_publication_pending=False,publication_complete=True);(o/'CURRENT-LOCAL-BUILD.json').write_text(json.dumps(current,indent=2)+'\n',encoding='utf-8');state('PASS',commit=commit);print(seal['status'],commit)
except Exception:
 import traceback
 state('FAILED',error=traceback.format_exc());raise
