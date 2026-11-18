"""Clarify that GitHub source ZIPs do not contain compiled runtimes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
w=Path(__file__).resolve().parent;r=w.parents[1];pub=r/'publish/scummvm-astronomica';o=r/'outputs/astronomica-cleanroom'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'));git=lambda *a:subprocess.check_output(['git','-C',str(pub),*a],text=True).strip()
parent=read(w/'confirmation-encoding-source-extension-seal-nov18.json');engine=read(w/'p513-control-music-seal-nov17.json')
assert git('branch','--show-current')=='main' and not git('status','--porcelain') and git('rev-parse','HEAD')==git('ls-remote','origin','refs/heads/main').split()[0]==parent['published_commit']
assert sha(w/'build/Releasex64/scummvm.exe')==engine['exe_sha256']
assert read(w/'downloaded-runtime-native-nov18/proof.json')['status']=='REPAIRED_DOWNLOAD_NATIVE_STARTUP_PASS'
git('switch','-c','codex/source-download-launch-help-nov18')
intro=b'''# Avvio su Windows: ZIP dei sorgenti

**Code > Download ZIP scarica i sorgenti, senza scummvm.exe o SDL2.dll.** Non e' un pacchetto pronto da giocare.

`Avvia-Astronomica.cmd` funziona quando una compilazione verificata e' presente in `work/fresh-20260913/build/Releasex64/`, insieme a `SDL2.dll`. Usa i file originali del gioco in `D:/astro` e conserva impostazioni e salvataggi in `userdata/astronomica/`.

Per compilare, seguire [BUILDING.md](BUILDING.md). Se la compilazione produce l'eseguibile in un'altra cartella, avviare quello ScummVM e aggiungere la cartella del gioco dal suo menu. Scaricare nuovamente lo ZIP dei sorgenti non aggiunge l'eseguibile mancante.

---

'''
assert b'# Avvio su Windows: ZIP dei sorgenti'not in(pub/'README.md').read_bytes()
(pub/'README.md').write_bytes(intro+(pub/'README.md').read_bytes())
shutil.copyfile(r/'Avvia-Astronomica.cmd',pub/'Avvia-Astronomica.cmd')
helpers=['publish_source_download_help_nov18.py','repair_downloaded_source_launch_nov18.py','check_downloaded_runtime_nov18.py','downloaded-runtime-native-nov18/proof.json']
names=['README.md','Avvia-Astronomica.cmd']+['work/fresh-20260913/'+n for n in helpers]
for name in helpers:
    dest=pub/'work/fresh-20260913'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(w/name,dest)
m=read(pub/'SOURCE-MANIFEST.json');files=set(m['sha256'])|set(names);m['sha256']={n:sha(pub/n)for n in sorted(files)};(pub/'SOURCE-MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
subprocess.run(['python',str(pub/'tools/verify_export.py')],check=True);git('-c','core.whitespace=cr-at-eol','diff','--check')
changed=git('diff','--name-only').splitlines()+git('ls-files','--others','--exclude-standard').splitlines();assert set(changed)==set(names)|{'SOURCE-MANIFEST.json'}
assert not git('diff','--','outputs/astronomica-cleanroom/engine','framework-overlay','SCUMMVM_BASE.json','framework-patch.json','tools','ports')
git('add','--',*changed);git('commit','-m','Explain source-only ZIP downloads and missing executable startup');git('push','-u','origin','codex/source-download-launch-help-nov18');commit=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==parent['published_commit'];git('switch','main');git('merge','--ff-only','codex/source-download-launch-help-nov18');git('push','origin','main')
assert git('ls-remote','origin','refs/heads/main').split()[0]==commit and not git('status','--porcelain')
receipt=dict(status='VERIFIED_SOURCE_DOWNLOAD_LAUNCH_HELP_PASS',at=datetime.now(timezone.utc).isoformat(),published_commit=commit,parent_published_commit=parent['published_commit'],parent_extension_sha256=sha(w/'confirmation-encoding-source-extension-seal-nov18.json'),exe_sha256=engine['exe_sha256'],engine_unchanged=True,framework_unchanged=True,runtime_repair_native_proof_sha256=sha(w/'downloaded-runtime-native-nov18/proof.json'),binary_published=False,whole_game_completion_percent=None)
(w/'source-download-launcher-seal-nov18.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
current=read(o/'CURRENT-LOCAL-BUILD.json');current.update(published_commit=commit,last_published_commit=commit,publication_extension_context='work/fresh-20260913/source-download-launcher-seal-nov18.json',parent_publication_extension_context='work/fresh-20260913/confirmation-encoding-source-extension-seal-nov18.json',source_publication_pending=False,publication_complete=True);(o/'CURRENT-LOCAL-BUILD.json').write_text(json.dumps(current,indent=2)+'\n',encoding='utf-8');print(receipt['status'],commit)
