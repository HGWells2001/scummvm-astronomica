"""Activate P281 evidence only after the whole successor native chain passes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,shutil,subprocess,sys
from p281_integration_gate import validated_p281_integration
w=Path(__file__).resolve().parent;r=w.parents[1];official=r/'outputs/astronomica-cleanroom';d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();expected=d(w/'build/Releasex64/scummvm.exe')
assert os.environ.get('ASTRONOMICA_REVIEWED_DESCENDANT')=='p281-sealed29'
integration,_=validated_p281_integration(r,w,expected);reg=json.loads((w/'p281-regressions-status.json').read_text())
assert reg['status']=='PASS' and reg['exe_sha256']==expected and reg['full_suite'] and reg['source_context_sha256']==d(w/'p281-integration.json')
assert reg['gateway_proof_sha256']==d(w/'p281-main-gateway/gateway-proof.json') and reg['genuine_v29_proof_sha256']==d(w/'p281-main-frozen-v29/frozen-v29-proof.json')
# Older recursive finishers must not interpret a former main's P512 marker as
# proof of this executable. The sealed old evidence remains immutable.
marker=official/'evidence/p512-saves-validation.json';held=w/'p281-prior-p512-validation.json'
if marker.exists() and json.loads(marker.read_text())['exe_sha256']!=expected:
    assert json.loads(marker.read_text())['exe_sha256']==integration['base_exe']
    if held.exists():assert d(held)==d(marker)
    else:shutil.copyfile(marker,held)
    marker.unlink()
subprocess.run([sys.executable,str(w/'finish_p512_saves.py')],cwd=r,check=True)
subprocess.run([sys.executable,str(w/'finish_local_launcher.py')],cwd=r,check=True)
target=official/'evidence/p281-native';target.mkdir(exist_ok=True)
for name in ['gateway-proof.json','gateway.log']:shutil.copyfile(w/'p281-main-gateway'/name,target/name)
old=official/'evidence/p281-frozen-v29';old.mkdir(exist_ok=True);proof=json.loads((w/'p281-main-frozen-v29/frozen-v29-proof.json').read_text())
for name in ['frozen-v29-proof.json',*[label+'.log' for label in proof['cases']]]:shutil.copyfile(w/'p281-main-frozen-v29'/name,old/name)
for source,name in [(w/'p281-integration.json','p281-source-integration.json'),(w/'p281-sealed29-rebase-v2-stage/root-source-review.json','p281-source-review.json')]:shutil.copyfile(source,official/'evidence'/name)
if 'clock_revision' in integration:
    shutil.copyfile(w/'p281-stopclock-nov1-stage/root-source-review.json',official/'evidence/p281-stopclock-source-review.json')
p=json.loads((target/'gateway-proof.json').read_text());v=dict(p,full_suite=True,public_validation=True,source_context_sha256=d(w/'p281-integration.json'),genuine_v29_proof_sha256=d(old/'frozen-v29-proof.json'),date=datetime.now(timezone.utc).date().isoformat(),save_scene_count=33)
(official/'evidence/p281-gateway-validation.json').write_text(json.dumps(v,indent=2)+'\n')
from p281_evidence_gate import validated_p281
assert validated_p281(official,w) is not None
for name in ['record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py']:subprocess.run([sys.executable,str(w/name)],cwd=r,check=True)
note=('# P281: portale originale e ritorni verificati\n\nIl pulsante originale di P281 avvia la sequenza delle varianti con voce e ritardo originali. Le uscite non risolte conservano turno e maschera; il comportamento originale del terzo turno è preservato. '
      'Salvataggi v2 iniziali e rifiuti senza scrivere durante la sequenza PASS; nessun nuovo formato. Suite completa sul medesimo eseguibile `'+expected+'`, compatibilità dei tre veri slot v29 e intera catena precedente PASS. '
      'Copertura salvataggi invariata 33/35; criteri complessivi6/10. Pubblicazione e sigillo restano separati.\n\n')
path=official/'NEXT-STEPS.md';text=path.read_text()
if not text.startswith('# P281:'):path.write_text(note+text)
(w/'p281-checkpoint-status.json').write_text(json.dumps(dict(status='PASS',full_suite=True,exe_sha256=expected,native_save_scenes=33,source_context_sha256=d(w/'p281-integration.json'),publication=False),indent=2)+'\n')
print('P281 gateway plus complete exact-main native/compatibility closure PASS; publication separate',flush=True)
