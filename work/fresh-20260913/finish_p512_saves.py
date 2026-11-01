"""Finalize ASVM29 evidence only after complete exact-main native closure."""
from pathlib import Path
from datetime import datetime
import hashlib,json,shutil,subprocess,sys
from p512_integration_gate import validated_integration,active_context_path

w=Path(__file__).resolve().parent;root=w.parents[1];r=root/'outputs/astronomica-cleanroom'
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();exe=w/'build/Releasex64/scummvm.exe';expected=d(exe)
integration,_=validated_integration(root,w,expected)
reg=json.loads((w/'p512-regressions-status.json').read_text());p=json.loads((w/'p512-save-proof.json').read_text())
assert reg['status']=='PASS' and reg['full_suite'] and reg['native_save_scenes']==33 and reg['exe_sha256']==expected
assert reg['descendant_context_sha256']==d(active_context_path(w))
assert p['status']=='PASS' and p['exe_sha256']==expected and not p['diagnostic'] and p['format_version']==29
assert p['actual_audio_driver']=='wasapi' and p['payload_bytes']==9932
# During the recursive v1-v27 finalizers the former v28 validation must not
# impersonate a proof of this new executable. Preserve it before removing its
# activation marker. finish_p510_saves reinstates it with fresh evidence.
held=w/('p281-prior-p510-validation.json' if active_context_path(w).name=='p281-integration.json' else 'p512-prior-p510-validation.json');active=r/'evidence/p510-saves-validation.json'
if active.exists():
    old=json.loads(active.read_text())
    if old['exe_sha256']!=expected:
        assert old['exe_sha256']==integration['base_exe']
        if held.exists():assert d(held)==d(active)
        else:shutil.copyfile(active,held)
        active.unlink()
assert not active.exists() or json.loads(active.read_text())['exe_sha256']==expected
subprocess.run([sys.executable,str(w/'finish_p510_saves.py')],cwd=root,check=True)
native=r/'evidence/p512-native';native.mkdir(exist_ok=True)
for name,sha in p['log_sha256'].items():
    source=w/'p512-save-regression'/name;assert d(source)==sha;shutil.copyfile(source,native/name)
compat=w/'p512-main-frozen-v28';target=r/'evidence/p512-frozen-v28';target.mkdir(exist_ok=True)
old=json.loads((compat/'frozen-v28-proof.json').read_text());assert old['status']=='PASS' and old['exe_sha256']==expected
for name in ['frozen-v28-proof.json',*[label+'.log' for label in old['cases']]]:shutil.copyfile(compat/name,target/name)
shutil.copyfile(w/'p512-save-proof.json',r/'evidence/p512-save-proof.json')
for source,target in [(w/'p512-integration.json','p512-source-integration.json'),(w/'p512-sealed28-rebase-stage/root-source-review.json','p512-source-review.json'),(w/'p512-sealed28-rebase-stage/normal-routes-proof.json','p512-isolated-normal-proof.json')]:shutil.copyfile(source,r/'evidence'/target)
v=dict(p,date=datetime.now().date().isoformat(),scene=512,full_suite=True,public_validation=True,
    genuine_v28_proof_sha256=d(compat/'frozen-v28-proof.json'),descendant_context_sha256=d(active_context_path(w)),active_source_context=active_context_path(w).name,
    compatibility='Versions1-28 retained; both genuine sealed v28 literal loop identities (-1 and0) read unchanged,each entrytrue/false',
    limitations=['Stopped-ready question boundaries only; active movies,queued work,foreground voice,pending images and unsupported private histories excluded',
        'Music restarts from its beginning while preserving active/waiting state and recipient volume/mute preferences; sample-exact audio is not claimed',
        'Mixer-channel exhaustion after commit is a fatal internal resource failure,not an atomic recoverable refusal',
        'Automated native checks do not replace the complete manual audiovisual playthrough'])
(r/'evidence/p512-saves-validation.json').write_text(json.dumps(v,indent=2)+'\n')
from p512_evidence_gate import validated_p512
validated_p512(r,w)
format_path=r/'P512-SAVE-FORMAT.md'
format_path.write_text(format_path.read_text().replace('Status: reviewed isolated real-engine implementation; exact-main native closure and publication have separate gates. Source integration alone does not establish public save coverage.','Status: complete exact-main native WASAPI validation PASS. Publication and the frozen checkpoint have separate gates.'))
for name in ['record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py']:
    subprocess.run([sys.executable,str(w/name)],cwd=root,check=True)
heading='# P512 ASVM29: suite nativa completa PASS\n\n'
text=('Salvataggi verificati **33/35 (94,3%)**; restano P523 e P525. '
      'Criteri complessivi **6/10 (60%)**; non è una percentuale delle ore o della giocabilità. '
      'P512 salva le domande pronte con filmato fermo,64sprite,clock/fotogrammi indipendenti e musica originale. '
      'Tutti6scenari in due percorsi normali,pausa del motore,slot28/29/30 in nuovi processi,metadati,9932troncamenti/alterazioni e compatibilità v1-v28 PASS sul medesimo eseguibile `'+expected+'`. '
      'La musica riparte dall’inizio; filmati attivi,voci e code restano esclusi. '
      'Pubblicazione separata; verificare p512-completion-status.json e p512-seal-status.json.\n\n')
next_path=r/'NEXT-STEPS.md';prior=next_path.read_text()
if not prior.startswith(heading):next_path.write_text(heading+text+prior)
progress=r/'PROJECT-PROGRESS.md';prior=progress.read_text();label='## Aggiornamento locale P512 ASVM29'
if label not in prior:progress.write_text(prior+'\n'+label+'\n\n'+text)
(r/'RUN-IN-PROGRESS.md').write_text('ASVM29 exact-main P512/full inherited native suite PASS. Publication and sealed snapshot remain separate gates. Newest finisher: finish_p512_saves.py.\n')
(w/'p512-local-validation-status.json').write_text(json.dumps(dict(status='PASS_LOCAL_NATIVE_VALIDATION',exe_sha256=expected,full_suite=True,native_save_scenes=33,validation_sha256=d(r/'evidence/p512-saves-validation.json'),publication=False),indent=2)+'\n')
print('P512 ASVM29 exact-main native validation and measured33/35 save coverage PASS; publication separate',flush=True)
