"""Record local P510 validation only after the complete same-main native chain."""
from pathlib import Path
from datetime import datetime
import hashlib,json,shutil,subprocess,sys
root=Path(__file__).resolve().parents[2];w=root/'work/fresh-20260913';r=root/'outputs/astronomica-cleanroom';d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected=d(w/'build/Releasex64/scummvm.exe')
hold=w/'P510-PUBLICATION-HOLD.json'
assert not hold.exists() or json.loads(hold.read_text())['status']=='RELEASED_AFTER_VERIFIED_ORDINARY_ENTRY','P510 ordinary-entry save contract is not yet verified'
from p510_ordinary_gate import validated_ordinary
ordinary_dir=w/'p510-main-ordinary-entry'
ordinary_path=ordinary_dir/'ordinary-entry-gate-proof.json'
validated_ordinary(ordinary_path,ordinary_dir,expected,ordinary_dir/'astro-verify.027')
reg=json.loads((w/'p510-regressions-status.json').read_text());proof=json.loads((w/'p510-save-proof.json').read_text());old=json.loads((w/'p501-v27-previous-slot-proof.json').read_text())
assert reg['status']=='PASS' and reg['full_suite'] and reg['exe_sha256']==expected
assert proof['status']=='PASS' and proof['exe_sha256']==expected and not proof['diagnostic'] and proof['actual_audio_driver']=='wasapi' and proof['metadata_listed'] and proof['fresh_process']
assert proof['scope']=='trusted_p510_ordinary_countdown' and proof['slot']==27 and proof['payload_bytes']==proof['truncations']==proof['corruptions']==4540
assert old['status']=='PASS' and old['exe_sha256']==expected and old['unchanged'] and old['slot_sha256']=='adcc9b9be47d0b7153a94eb3b9883b85a12090fbd64e8793e32e61daeeea81fa'
# Regenerate the complete existing evidence chain on this same executable.
subprocess.run([sys.executable,str(w/'finish_p501_saves.py')],cwd=root,check=True)
for source,target,marker in [('p510-saves.log','p510-saves-runtime.log','P510 ASVM28 malformed atomic: PASS'),('p510-saves-startup.log','p510-saves-startup.log','P510 ASVM28 fresh physical continuation: PASS'),('p501-v27-previous-slot.log','p501-v27-previous-slot.log','P501 startup save: PASS')]:
 text=(w/source).read_text();assert marker in text and 'FAIL' not in text and 'Using SDL Audio Driver "wasapi"' in text and text.rstrip().endswith('--- Log closed successfully.');assert (w/source).stat().st_mtime>(w/'build/Releasex64/scummvm.exe').stat().st_mtime;shutil.copyfile(w/source,r/'evidence'/target)
for name in ['p510-save-proof.json','p501-v27-previous-slot-proof.json']:shutil.copyfile(w/name,r/'evidence'/name)
listed=(w/'p510-saves-list.log').read_text();assert 'P510 native paused continuation' in listed;shutil.copyfile(w/'p510-saves-list.log',r/'evidence/p510-saves-list.log')
validation=dict(proof,date=datetime.now().date().isoformat(),scene=510,full_suite=True,compatibility='Versions1-27 retained; genuine frozen verified v27 slot26 read unchanged',limitations=['Ordinary countdown sole original program1/index6 only; count1..51,width52 literal','Foreground voice,hints,pending images,unrelated work,unsupported media lag/rate excluded','Integer-ms floor audio cursor; physical sample-exact audio not claimed','Full manual audiovisual playthrough remains outstanding'])
ordinary_evidence=r/'evidence/p510-ordinary-entry'
ordinary_evidence.mkdir(exist_ok=True)
for name in ['ordinary-entry-gate-proof.json','initial.log','fresh-true.log','fresh-false.log','listed.log']:
 shutil.copyfile(ordinary_dir/name,ordinary_evidence/name)
validation['ordinary_entry_proof_sha256']=d(ordinary_path)
(r/'evidence/p510-saves-validation.json').write_text(json.dumps(validation,indent=2)+'\n')
format_path=r/'P510-SAVE-FORMAT.md'
format_text=format_path.read_text().replace(
 'Status: candidate awaiting independent file review and main native closure. Canonical support, full-suite coverage and publication require their separate gates.',
 'Status: independent file review and complete same-main native WASAPI validation PASS. Source-only publication requires its separate export/clone/remote gate.')
format_text=format_text.replace(
 'Main same-build compatibility chain, final evidence/export and complete manual audiovisual playthrough remain separate requirements.',
 'The main same-build compatibility chain has passed; final evidence/export/publication and complete manual audiovisual playthrough retain their separate gates.')
format_path.write_text(format_text)
for name in ['record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py']:
 subprocess.run([sys.executable,str(w/name)],cwd=root,check=True)
# Keep the immutable P501 acceptance photograph distinct from the newer local
# validation. This paragraph is written only after every same-build gate above.
progress=r/'PROJECT-PROGRESS.md'
progress_text=progress.read_text()
progress_text=progress_text.replace('La versione verificata corrente è P501/formato27,','La fotografia completa di accettazione qui congelata è P501/formato27,').replace('P510 resta in sviluppo isolato.','Lo stato successivo di P510 è riportato nel prossimo aggiornamento, quando presente.')
heading='## Aggiornamento locale P510 ASVM28'
if heading not in progress_text:
 progress_text+='\n'+heading+'\n\nSuite completa sul medesimo eseguibile `'+expected+'`, audio WASAPI, salvataggio fisico in nuovo processo, metadati, rifiuto atomico e compatibilità v1-v27: PASS. Copertura corrente dei salvataggi: **32/35 (91,4%)**; restano P512, P523 e P525. P510 conserva solo il conto alla rovescia ordinario documentato. Il punteggio dei dieci criteri resta **60% (6/10)**: A07 è ancora parziale. La fotografia P501 sopra resta storica e immutata. La pubblicazione è un passaggio separato: consultare p510-completion-status.json e p510-seal-status.json.\n'
progress.write_text(progress_text)
next_steps=r/'NEXT-STEPS.md'
next_text=next_steps.read_text()
if not next_text.startswith('# P510 ASVM28: suite nativa completa PASS'):
 next_steps.write_text('# P510 ASVM28: suite nativa completa PASS\n\nEseguibile `'+expected+'`. Salvataggi32/35 (91,4%), criteri complessivi6/10 (60%). Restano P512, P523 e P525; consultare P512-RESUME-STAGED.md e P525-RESUME-STAGED.md nel lavoro locale. Verificare separatamente completion/seal per la pubblicazione. Non modificare il motore durante export e sigillo. Le note seguenti sono cronologia.\n\n'+next_text)
(w/'p510-local-validation-status.json').write_text(json.dumps(dict(status='PASS_LOCAL_NATIVE_VALIDATION',exe_sha256=expected,full_suite=True,native_save_scenes=32,publication=False,validation_sha256=d(r/'evidence/p510-saves-validation.json')),indent=2)+'\n')
(r/'RUN-IN-PROGRESS.md').write_text('P510 ASVM28 same-main native validation PASS. Publication/evidence/export finalization remains a separate gate. Do not run older finishers independently.\n')
print('P510 local native validation and conditional coverage/evidence PASS; export/publication remain separately guarded')
