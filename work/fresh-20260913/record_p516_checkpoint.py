"""Save integrated P516 only after the complete native verification passes."""
from pathlib import Path
import json,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
log=(work/'runtime.log').read_text()
assert 'FAIL' not in log and 'Astronomica script verification: PASS' in log
assert 'P516 interaction verification: PASS' in log
note='''

## Integrated P516 checkpoint, 1 October 2026

P516 is integrated in the native ScummVM engine. Full regression suite PASS.
Native verification:128 original setup configurations,20 seconds of eight
original orbit trajectories,64 collision fixtures plus four API edge cases,
three independent image compositions and79/80ms frame timing on both layers.
Actual click routes cover victory/repeat, zero-speed and missed launches,
and voluntary exits. Total33 verified route scenes; these are not33 distinct
puzzles. Whole-game completion percentage remains unknown. Manual P516
audiovisual verification and help/return remain pending. No prototype,
package or launcher was created. See P516-RESEARCH.md for proof boundaries.
'''
for name in ('README.md','INTERPRETER.md'):
 p=root/name
 if b'## Integrated P516 checkpoint, 1 October 2026' not in p.read_bytes():
  with p.open('ab') as f:f.write(note.encode('ascii'))
(root/'NEXT-STEPS.md').write_text('''# Ripresa: P516 integrato, 1 ottobre 2026

Compilazione e collaudo generale PASS.33 scene con percorsi automatici,
non33 puzzle indipendenti. Conferma manuale soloP508; percentuale globale
ignota. P501, P502-P504 e P516 integrati nel vero motore.

P516:128 setup,20 secondi/otto sprite,64 collisioni +4 bordi API,3 immagini,
timer79/80ms e4 percorsi click (vittoria/ripetizione/zero/errore con uscita).
La convenzione dei bordi USER e documentata da Microsoft ma non provata
eseguendo USER Win16; vedere P516-RESEARCH.md. Rimane verifica manuale.

Prossimi: P510 custom23+FLATPLOT.MOV/opcode4 e P523 custom1/4/5/20.
Restano inoltre aiuto/ritorno, salvataggi e collaudo integrale del gioco.
Comete: vedere COMET-RESEARCH.md per limiti dei rilanci e prove manuali.
P501 conserva la nota sul campoY non inizializzato nell'opcode20 originale.
Preservare i byte finali dei MEGAFILE: contengono BMP, non sono padding.

Canonical outputs/astronomica-cleanroom/engine/astronomica; mirror
work/fresh-20260913/scummvm/engines/astronomica. Build locale:
work/fresh-20260913/build/Releasex64/scummvm.exe.
Test mirato:check_p516.py; intero:runtime_test.py. Registrare con
record_p516_checkpoint.py e verificare con verify_development_evidence.py.
Non rieseguire i vecchi record_comet_checkpoint.py/finalize_comet_research.py:
descrivono stati ormai superati. Nessun nuovo pacchetto/prototipo/launcher.
''',encoding='utf-8')
(root/'evidence/p516-validation.json').write_text(json.dumps(dict(status='PASS',setup_cases=128,motion_ms=20000,orbit_sprites=8,
 original_collision_fixtures=64,documented_api_edge_cases=4,image_compositions=3,click_routes=4,full_suite=True,manual_confirmation=False),indent=2))
p=work/'save_development_evidence.py';s=p.read_text().replace('514,515,517,','514,515,516,517,');p.write_text(s)
p=work/'refresh_research_evidence.py';s=p.read_text().replace('P501 and comet native routes; P516 research only','P501, comet and P516 native routes');p.write_text(s)
for script in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
 subprocess.run([sys.executable,str(work/script)],check=True)
print('Integrated P516 checkpoint saved and verified')
