"""Publish speech-over-Music ducking, preserving the previous runtime."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,shutil,subprocess,sys,time
w=Path(__file__).resolve().parent;r=w.parents[1];o=r/'outputs/astronomica-cleanroom';pub=r/'publish/scummvm-astronomica';s=w/'speech-duck-candidate-nov19d-stage'
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();git=lambda *a:subprocess.check_output(['git','-C',str(pub),*a],text=True).strip()
run=w/'speech-duck-release-run-nov19';run.mkdir(exist_ok=False)
def state(status,**kw):(run/'status.json').write_text(json.dumps(dict(status=status,at=datetime.now(timezone.utc).isoformat(),**kw),indent=2)+'\n')
try:
 state('WAITING_NATURAL_GENERAL_AND_GENUINE_COMPLETION')
 while not(w/'speech-duck-general-nov19d/proof.json').exists() or not(w/'speech-duck-genuine-nov19d/proof.json').exists():
  for d in ['speech-duck-general-nov19d','speech-duck-genuine-nov19d']:
   p=w/d/'status.json'
   if p.exists():assert read(p)['status']!='FAILED',d+' failed; nothing installed'
  time.sleep(1)
 parent=read(w/'all-effects-seal-nov19.json');build=read(s/'proof.json');pin=build['candidate_exe_sha256'];previous=git('rev-parse','HEAD');assert git('branch','--show-current')=='main'and not git('status','--porcelain')and git('ls-remote','origin','refs/heads/main').split()[0]==previous
 gates={}
 for n in ['speech-duck-source-review-nov19d.json','speech-duck-payload-review-nov19d.json','speech-duck-native-nov19d/proof.json','speech-duck-windows-nov19d/proof.json','speech-duck-catalogue-windows-nov19d/proof.json','speech-duck-doors-nov19d/proof.json','speech-duck-progress-nov19d/proof.json','speech-duck-navigation-nov19d/proof.json','speech-duck-general-nov19d/proof.json','speech-duck-genuine-nov19d/proof.json']:
  p=read(w/n);assert p['status'].endswith('PASS')and p.get('candidate_exe_sha256',p.get('consumer_exe_sha256'))==pin,n;gates[n]=sha(w/n)
 assert sha(w/'build/Releasex64/scummvm.exe')==parent['exe_sha256']and sha(s/'bin/scummvm.exe')==pin
 for d in[o/'engine/astronomica',w/'scummvm/engines/astronomica']:
  assert {p.name:sha(p)for p in d.iterdir()if p.is_file()}==parent['engine_sha256']
 query="Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq '"+str(w/'build/Releasex64/scummvm.exe')+"' } | Select-Object -ExpandProperty ProcessId"
 assert not subprocess.run(['powershell','-NoProfile','-Command',query],capture_output=True,text=True,check=True).stdout.strip(),'Workspace player running; not replaced'
 snapshot=w/'verified-checkpoints'/('speech-duck-'+pin[:12]);shutil.copytree(s/'source/engines/astronomica',snapshot/'engine/astronomica');shutil.copytree(s/'bin',snapshot/'bin')
 spec=read(pub/'framework-patch.json');assert spec['engine_sha256']==parent['engine_sha256'];spec['engine_sha256']=build['candidate_engine_sha256'];(snapshot/'framework-patch.json').write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
 targets={d/n:(s/'source/engines/astronomica'/n).read_bytes()for d in[o/'engine/astronomica',w/'scummvm/engines/astronomica']for n in['astronomica.cpp','astronomica.h']};targets[w/'build/Releasex64/scummvm.exe']=(s/'bin/scummvm.exe').read_bytes();saved={p:p.read_bytes()for p in targets};done=[]
 state('INSTALLING_QUALIFIED_RUNTIME')
 try:
  for p,data in targets.items():
   temp=p.with_name(p.name+'.all-effects.tmp');temp.write_bytes(data);os.replace(temp,p);done.append(p)
  subprocess.run([sys.executable,str(w/'check_speech_duck_installed_nov19d.py')],check=True)
  subprocess.run([sys.executable,str(w/'check_speech_duck_catalogue_nov19d.py'),'--installed','--windows'],check=True)
 except Exception:
  for p in reversed(done):p.write_bytes(saved[p])
  raise
 gates['speech-duck-installed-native-nov19d/proof.json']=sha(w/'speech-duck-installed-native-nov19d/proof.json')
 gates['speech-duck-installed-nov19d/proof.json']=sha(w/'speech-duck-installed-nov19d/proof.json')
 git('switch','-c','codex/speech-music-ducking-nov19');names=[]
 def copy(src,name):
  dst=pub/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);names.append(name)
 for n in build['candidate_engine_sha256']:copy(s/'source/engines/astronomica'/n,'outputs/astronomica-cleanroom/engine/astronomica/'+n)
 copy(snapshot/'framework-patch.json','framework-patch.json');base=read(pub/'SCUMMVM_BASE.json');base.update(validated_executable_sha256=pin,engine_sha256=build['candidate_engine_sha256'],build_scope='Speech keeps the same Music channel at half its previous channel volume,then restores it;global audio preferences unchanged.5track native/Windows matrices,632audio paths,real intro,ended-voice wait ownership,genuineASVM29,progress/navigation and fullgeneral PASS. Two derived header fields;58payloadmethods identical,two admission guards only;packet/core3 unchanged. Seven fresh engine units,403verified core objects.');(pub/'SCUMMVM_BASE.json').write_text(json.dumps(base,indent=2)+'\n',encoding='utf-8')
 doc="# Parlato sopra la musica con volume ridotto\n\nLa musica di sottofondo continua dallo stesso punto durante le voci. Il suo volume di canale viene dimezzato,poi torna esattamente al livello precedente. Le impostazioni globali di volume e mute non vengono modificate. Gli effetti continuano a suonare sopra la musica al volume normale.\n\nIl ripristino copre fine naturale della voce,interruzione con un effetto,stop esplicito e cambio scena. Le voci consecutive non dimezzano il volume piu volte. Anche l'introduzione reale P503 e verificata con musica in avanzamento. I cicli di attesa conservano il proprio riferimento alla voce,cosi un clip breve finito durante il caricamento della musica non lascia il gioco in attesa del brano in loop.\n\nLe pause congelano entrambi i flussi. Due nuovi campi privati del motore conservano solo lo stato temporaneo del volume:non entrano nei salvataggi. Il salvataggio/caricamento pubblico attende che finisca il parlato o l'effetto sovrapposto;il formato dei file resta invariato.58 metodi di serializzazione sono identici;in altri due cambia solo il controllo d'ammissione.\n\nControlli:cinque brani,volume normale personalizzato170/171,pausa,due voci consecutive,file mancante,sostituzione con effetto,stop,cambi di regione,introduzione reale,fine naturale,salvataggio/ripristino e due casi di voce gia terminata. Passano anche632WAV,Windows,vecchiASVM29,indicatore212casi,navigazione306scene/760percorsi e suite generale. Non e un ascolto manuale completo. I filmati mantengono la loro gestione temporale.\n\nSono stati ricompilati tutti i sette file C++ del motore con il nuovo header;403oggetti del framework verificati riutilizzati. I tre file video del core e il catalogo102effetti non cambiano. Questa revisione sostituisce la precedente preferenza di voce esclusiva,su richiesta dell'utente. Percentuale complessiva del progetto non misurata;accettazione fissa7/10 non e una percentuale globale.\n"
 for target in[o/'SPEECH-MUSIC-DUCKING.md',pub/'outputs/astronomica-cleanroom/SPEECH-MUSIC-DUCKING.md']:target.write_text(doc,encoding='utf-8',newline='\n')
 names.append('outputs/astronomica-cleanroom/SPEECH-MUSIC-DUCKING.md')
 items=['speech_duck_source_nov19.py', 'speech_duck_probe_nov19.py', 'speech_duck_expectations_nov19.py', 'speech_duck_probe_nov19b.py', 'speech_duck_probe_nov19c.py', 'speech_duck_probe_nov19d.py', 'build_speech_duck_nov19d.py', 'check_speech_duck_nov19d.py', 'check_speech_duck_windows_nov19d.py', 'check_speech_duck_catalogue_nov19d.py', 'check_speech_duck_installed_nov19d.py', 'check_speech_duck_general_nov19d.py', 'check_speech_duck_genuine_nov19d.py', 'check_speech_duck_progress_nov19d.py', 'check_speech_duck_navigation_nov19d.py', 'check_speech_duck_doors_nov19.py', 'audit_speech_duck_nov19d.py', 'review_speech_duck_payload_nov19d.py', 'check_speech_duck_publication_install_nov19.py', 'update_downloaded_speech_duck_runtime_nov19.py', 'release_speech_duck_nov19.py', 'speech-duck-candidate-nov19d-stage/proof.json']
 for n in sorted(set(items)|set(gates)):copy(w/n,'work/fresh-20260913/'+n)
 intro='# Current update: speech over continuous Music\n\nMusic continues at half its previous channel volume during speech,then returns to that exact level. Global preferences and save packet layouts are preserved. See outputs/astronomica-cleanroom/SPEECH-MUSIC-DUCKING.md.\n\n---\n\n'
 p=pub/'README.md';p.write_text(intro+p.read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
 p=pub/'outputs/astronomica-cleanroom/NEXT-STEPS.md';p.write_text(intro+p.read_text(encoding='utf-8'),encoding='utf-8',newline='\n');shutil.copyfile(p,o/'NEXT-STEPS.md')
 for name in['AUDIO-MIX.md','DOOR-MUSIC.md','ALL-SOUND-EFFECTS.md']:
  p=pub/'outputs/astronomica-cleanroom'/name;p.write_text('Current audio policy: see SPEECH-MUSIC-DUCKING.md. The scope below is historical.\n\n'+p.read_text(encoding='utf-8'),encoding='utf-8',newline='\n');shutil.copyfile(p,o/name)
 def manifest():
  m=read(pub/'SOURCE-MANIFEST.json');files=set(m['sha256'])|set(names);assert set(git('ls-files','--others','--exclude-standard').splitlines())<=files;m['sha256']={n:sha(pub/n)for n in sorted(files)};(pub/'SOURCE-MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8');subprocess.run([sys.executable,str(pub/'tools/verify_export.py')],check=True)
 manifest();subprocess.run([sys.executable,str(w/'check_speech_duck_publication_install_nov19.py')],check=True);copy(w/'speech-duck-install-n19/proof.json','work/fresh-20260913/speech-duck-install-n19/proof.json');manifest()
 git('add','--',*git('diff','--name-only').splitlines(),*git('ls-files','--others','--exclude-standard').splitlines());git('commit','-m','Keep background music playing at half channel volume during speech');git('push','-u','origin','codex/speech-music-ducking-nov19');commit=git('rev-parse','HEAD');clone=r/'publish/verify-speech-duck-nov19';subprocess.run(['git','clone','--single-branch','--branch','codex/speech-music-ducking-nov19',git('remote','get-url','origin'),str(clone)],check=True);subprocess.run([sys.executable,str(clone/'tools/verify_export.py')],check=True);assert git('ls-remote','origin','refs/heads/main').split()[0]==previous;git('switch','main');git('merge','--ff-only','codex/speech-music-ducking-nov19');git('push','origin','main');assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
 seal=dict(status='SPEECH_DUCK_PUBLISHED_WORKSPACE_SEAL_PASS',at=datetime.now(timezone.utc).isoformat(),published_commit=commit,exe_sha256=pin,engine_sha256=build['candidate_engine_sha256'],framework_sha256=parent['framework_sha256'],snapshot=str(snapshot),gates=gates,independent_source_clone_verified=True,whole_game_completion_percent=None,fixed_acceptance=dict(passed=7,total=10,percent=70));(w/'speech-duck-seal-nov19.json').write_text(json.dumps(seal,indent=2)+'\n',encoding='utf-8');current=read(o/'CURRENT-LOCAL-BUILD.json');current.update(status='VERIFIED_PUBLISHED_SPEECH_DUCK',exe_sha256=pin,main_exe_sha256=pin,engine_sha256=seal['engine_sha256'],source_snapshot=str(snapshot),published_commit=commit,last_published_commit=commit,last_published_exe_sha256=pin,seal_context='work/fresh-20260913/speech-duck-seal-nov19.json',source_publication_pending=False,publication_complete=True);(o/'CURRENT-LOCAL-BUILD.json').write_text(json.dumps(current,indent=2)+'\n',encoding='utf-8');state('PASS',commit=commit);print(seal['status'],commit)
except Exception:
 import traceback
 state('FAILED',error=traceback.format_exc());raise
