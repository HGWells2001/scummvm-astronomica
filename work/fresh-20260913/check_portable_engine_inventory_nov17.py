"""Confirm the isolated portable build retains the user's complete engine inventory."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,sys
w=Path(__file__).resolve().parent;s=w/'portable-terminal-clock-compat-nov17-stage';old=Path('D:/00/_SCUMMVM_PORTATILE/scummvm.exe');candidate=s/'bin/scummvm.exe';out=w/'portable-terminal-clock-compat-engine-inventory-nov17d';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();build=json.loads((s/'proof.json').read_text());assert sha(old)==build['selected_portable_exe_sha256']and sha(candidate)==build['candidate_exe_sha256']
results={}
for label,exe in [('original',old),('candidate',candidate)]:
 cfg=out/(label+'.ini');cfg.write_text('[scummvm]\nconfirm_exit=false\n',encoding='utf-8')
 with(out/(label+'.json')).open('w',encoding='utf-8')as stdout,(out/(label+'.stderr')).open('w',encoding='utf-8')as stderr:
  # These CLI-only commands can exit before PID/birth registration completes.
  # Wait synchronously and naturally; no timeout, background job or shutdown.
  code=subprocess.run([str(exe),'--config='+str(cfg),'--list-engines-json'],cwd=out,stdout=stdout,stderr=stderr).returncode
 assert code==0
 text=(out/(label+'.json')).read_text(encoding='utf-8')
 prefix='Using configuration file: '+str(cfg)+'\n';assert text.startswith(prefix)
 results[label]=json.loads(text[len(prefix):])
assert results['original']==results['candidate'],'Engine inventory differs; do not install'
assert sha(old)==build['selected_portable_exe_sha256']and sha(candidate)==build['candidate_exe_sha256']
p=dict(status='PORTABLE_FULL_ENGINE_INVENTORY_RETAINED_PASS',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(candidate),selected_portable_exe_sha256=sha(old),inventory=results['candidate'],original_log_sha256=sha(out/'original.json'),candidate_log_sha256=sha(out/'candidate.json'),native_exited_naturally=True,limits=['Exact --list-engines-json comparison; not gameplay certification for unrelated engines','No user configuration or original portable executable changes'])
(out/'proof.json').write_text(json.dumps(p,indent=2)+'\n');print(p['status'])
