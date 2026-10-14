"""Finalize P510 only after scoped, continuous and full regression passes."""
from pathlib import Path
import json,subprocess,sys,shutil
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
for name in ('runtime.log','p510.log','p510-continuous.log'):
 text=(work/name).read_text()
 assert 'FAIL' not in text,name
 assert 'P510 interaction verification: PASS' in text,name
 if name=='runtime.log':assert 'Astronomica script verification: PASS' in text
 if name=='p510.log':
  for route in range(8):assert f'P510 route {route}: PASS' in text
 if name=='p510-continuous.log':assert 'P510 route 0: PASS' in text

note='''

## Integrated P510 checkpoint, 2 October 2026

P510 now runs the original movie-controlled puzzle in the native engine.
Full regression suite PASS;34 route scenes, not34 independent puzzles.
Original callback comparison432 cases; eight click routes cover three starts,
both directions, first/repeated victory, failure, voluntary exit and timeout.
A complete winning movie route also passed continuous playback without seeks.
P516 remains integrated and verified. Manual confirmation remains limited to
P508; whole-game completion percentage is unknown. See P510-RESEARCH.md.
No prototype, package or launcher was created.
'''
for name in ('README.md','INTERPRETER.md'):
 p=root/name
 if b'## Integrated P510 checkpoint, 2 October 2026' not in p.read_bytes():
  with p.open('ab') as f:f.write(note.encode('ascii'))
(root/'NEXT-STEPS.md').write_text('''# Ripresa: P510 integrato, 2 ottobre 2026

Compilazione, test mirati, filmato continuo P510 e collaudo generale PASS.
34 scene con percorsi automatici, oltre P507 interattiva. Non34 puzzle distinti.
Conferma manuale solo P508; percentuale globale ancora ignota.

P510:27 eventi originali/432 casi, otto percorsi con pulsanti, tre avvii casuali,
entrambi i rami, vittoria/ripetizione, errore, uscita e scadenza. Filmato continuo
fino alla vittoria verificato senza seek. Rimane verifica audiovisiva manuale.
Dettagli e limiti: P510-RESEARCH.md. P516: P516-RESEARCH.md.

Prossimo puzzle: P523, custom1/4/5/20 e callback QuickTime condiviso con P510.
Non usare automaticamente i rami P510 per P523: il dispatch e comune ma i
rami1..19 dipendono da altri stati. Restano aiuto/ritorno, salvataggi e prova
integrale del gioco. Conservare la nota P501 sul campoY originale non inizializzato.
Preservare i byte finali dei MEGAFILE: contengono BMP, non sono padding.

Canonical outputs/astronomica-cleanroom/engine/astronomica; mirror
work/fresh-20260913/scummvm/engines/astronomica; eseguibile locale
work/fresh-20260913/build/Releasex64/scummvm.exe.
Test:check_p510.py, check_p510_continuous.py, runtime_test.py.
Registrazione:record_p510_checkpoint.py; integrita:verify_development_evidence.py.
Non rieseguire i vecchi record_* checkpoint: ripristinano riepiloghi superati.
''',encoding='utf-8')
(root/'evidence/p510-validation.json').write_text(json.dumps(dict(status='PASS',original_callback_cases=432,
 original_events=27,click_routes=8,random_starts=3,continuous_winning_route=True,
 full_suite=True,manual_confirmation=False),indent=2))
p=work/'save_development_evidence.py';s=p.read_text()
s=s.replace("date='2026-10-01'","date='2026-10-02'").replace('508,509,511,','508,509,510,511,')
s=s.replace('continuous_video_scenes=[512,','continuous_video_scenes=[510,512,')
guard="assert 'P510 interaction verification: PASS' in log"
if guard not in s:s=s.replace("for name in ['runtime.log'",guard+"\nfor name in ['runtime.log'",1)
p.write_text(s)
p=work/'refresh_research_evidence.py';s=p.read_text().replace("date='2026-10-01'","date='2026-10-02'")
s=s.replace('P501, comet and P516 native routes','P501, comet, P516 and P510 native routes')
s=s.replace("'P516-RESEARCH.md'))","'P516-RESEARCH.md','P510-RESEARCH.md'))")
p.write_text(s)
p=root/'survey_puzzles.py';s=p.read_text().replace('known={1,2,3,5,','known={1,2,3,4,5,')
line="lines += ['', 'Aggiornamento 2 ottobre: P516 e P510 integrati,34 scene con percorsi automatici. P510 verificato in432 casi originali e otto percorsi; anche un percorso vincente con filmato continuo. Conferma manuale solo P508. Non e una percentuale di completamento del gioco.']\n"
if line not in s:s=s.replace("(args.out/'PUZZLE-SURVEY.md').write_text",line+"(args.out/'PUZZLE-SURVEY.md').write_text")
p.write_text(s)
for script in ('refresh_research_evidence.py','save_development_evidence.py'):
 subprocess.run([sys.executable,str(work/script)],check=True)
for name in ('p510.log','p510-continuous.log'):shutil.copyfile(work/name,root/'evidence'/name)
subprocess.run([sys.executable,str(work/'verify_development_evidence.py')],check=True)
print('Integrated P510 checkpoint saved and verified')
