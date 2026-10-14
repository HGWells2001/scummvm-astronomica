"""Record an integrated comet checkpoint only after the full native suite passes."""
from pathlib import Path
import json,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
log=(work/'runtime.log').read_text()
assert 'FAIL' not in log and 'Astronomica script verification: PASS' in log
for test in ('motion','setup','composition'):
 assert 'comet original '+test+' comparison: PASS' in log
assert 'comet interaction verification: PASS' in log
note='''

## Integrated comet puzzles, 1 October 2026

P502/P503/P504 are integrated in the ScummVM engine. Full suite PASS.
Native checks:30 original trajectories,1920 setup/display states,9 independent
layer/clone/clipping compositions, complete P502-P503-P504-P527 chain,
repeated victory, low/high speed, wrong direction and voluntary exits.
The checkpoint now includes32 route scenes, not32 independent puzzles.
Manual confirmation remains limited toP508. Whole-game percentage is unknown.
P516 research covers128 setup and64 collision cases; P516 is not enabled.
See COMET-RESEARCH.md, P516-RESEARCH.md and NEXT-STEPS.md for limitations.
No prototype, package or launcher was created.
'''
for name in ('README.md','INTERPRETER.md'):
 p=root/name
 if b'## Integrated comet puzzles, 1 October 2026' not in p.read_bytes():
  with p.open('ab') as f:f.write(note.encode('ascii'))
(root/'NEXT-STEPS.md').write_text('''# Ripresa: comete integrate, 1 ottobre 2026

P501 e P502/P503/P504 integrati nel vero motore ScummVM.
Compilazione e collaudo completo PASS;32 scene con percorsi automatici.
Comete:30 traiettorie,1920 stati,9 composizioni grafiche, due percorsi
completi con vittoria/ripetizione, tre percorsi errori/uscita.
Le32 scene NON sono32 puzzle indipendenti. Conferma manuale soloP508.
Percentuale globale ignota: resta da verificare il gioco completo.

Ricerca originale per P516:128 setup e64 collisioni, senza abilitazione.
Leggere P516-RESEARCH.md per custom9 e _fxm_hit_jup_comet.
Riutilizzare soltanto il meccanismo di ellisse/handoff ora provato; servono
ancora confronto delle traiettorie reali, implementazione, click e bordi
del test USER PtInRect. P510 custom23+filmato e P523 custom1/4/5/20 restano.

COMET-RESEARCH.md descrive i test e i limiti: mancano verifica manuale
audiovisiva, copertura aiuto/ritorno e rilanci a tutte le fasi possibili.
P501 conserva la nota sul campoY non inizializzato dell'opcode20 originale.
Preservare i dati finali dei MEGAFILE: contengono BMP, non sono padding.

Canonical: outputs/astronomica-cleanroom/engine/astronomica.
Mirror: work/fresh-20260913/scummvm/engines/astronomica.
Eseguibile: work/fresh-20260913/build/Releasex64/scummvm.exe.
Controllo comete: check_comet.py; collaudo intero: runtime_test.py.
Checkpoint: record_comet_checkpoint.py, con guardie che richiedono PASS.
Non rieseguire finalize_comet_research.py: conserva il vecchio stato parziale.
Nessun pacchetto, prototipo o launcher nuovo.
''',encoding='utf-8')
(root/'evidence/comet-validation.json').write_text(json.dumps(dict(status='PASS',scope='Integrated native comet routes; manual playtesting pending',
 native_trajectories=30,native_setup_cases=1920,native_compositions=9,complete_routes=2,failure_exit_routes=3,
 transition_chain=[502,503,504,527],full_suite=True,manual_confirmation=False),indent=2))
p=work/'save_development_evidence.py';s=p.read_text();s=s.replace('complete_route_scenes=[501,505,','complete_route_scenes=[501,502,503,504,505,');p.write_text(s)
for script in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
 subprocess.run([sys.executable,str(work/script)],check=True)
print('Integrated comet checkpoint saved and verified')
