"""Finalize mentor support only after its continuous and full native tests pass."""
from pathlib import Path
import json,subprocess,sys,shutil
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
log=(work/'runtime.log').read_text()
for marker in ('Astronomica script verification: PASS','mentors original comparison: PASS',
 'mentors interaction verification: PASS','mentor continuous playback: PASS','P523 help return: PASS'):
 assert marker in log,marker
assert 'FAIL' not in log
note='''

## Mentor help checkpoint, 4 October 2026

P408 mentor buttons now play their original contextual video ranges. Native
comparison passes1900 cases, with explicit no-hint handling for undefined
P524 variant0/9.170 decoded selections,37 source-scene returns, no-hint speech
and natural continuous segment completion pass, together with the full suite.
P523 help return resets modified controls and response flags and reinstalls
the movie callbacks; original input still works after returning.
The Windows help book (custom22), native saves and manual audiovisual review
remain incomplete.35 puzzle-route scenes remain verified, not35 distinct
puzzles; no whole-game completion percentage is asserted.
'''
for name in ('README.md','INTERPRETER.md','P408-RESEARCH.md','P523-RESEARCH.md'):
 p=root/name
 if b'## Mentor help checkpoint, 4 October 2026' not in p.read_bytes():
  with p.open('ab') as f:f.write(note.encode('ascii'))
(root/'evidence/mentors-validation.json').write_text(json.dumps(dict(status='PASS',
 original_cases=1900,undefined_cases=10,undefined_policy='unavailable hint',
 decoded_selections=170,source_scene_returns=37,continuous_completion=True,
 p523_help_return=True,full_suite=True,windows_help_book=False,manual_confirmation=False),indent=2))
(root/'NEXT-STEPS.md').write_text('''# Ripresa: mentori P408 integrati, 4 ottobre 2026

Build e suite completa PASS:35 scene con percorsi verificati, non35 puzzle.
P523:dieci percorsi e filmato continuo; aiuto/ritorno con reset verificato.
P408:1900 confronti originali,170 selezioni video,37 ritorni e filmato continuo.
Leggere P408-RESEARCH.md e P523-RESEARCH.md per le correzioni esplicite ai casi
originali con dati non inizializzati. Conferma manuale solo P508.
Percentuale globale non misurata;94.2% si riferisce solo ai template accettati.

Proseguire con aiuto Windows (custom22/process_help), salvataggi e percorso
generale. probe_save_layout.py verifica il formato originale:102 DWORD,
408 byte, scena/contatore/100 globals; native saves NON implementati.
P520 ha filmato e transizione verificati; non e contato come puzzle aggiuntivo.
P507 e interattiva. Mancano prove manuali audiovisive e un percorso integrale.

Sorgenti:outputs/astronomica-cleanroom/engine/astronomica.
Mirror:work/fresh-20260913/scummvm/engines/astronomica.
Build:work/fresh-20260913/build/Releasex64/scummvm.exe.
build.py NON copia i sorgenti: sincronizzare cpp/h prima di compilare.
Test:check_mentors.py,check_p523.py,check_p523_continuous.py,runtime_test.py.
Checkpoint:record_mentors_checkpoint.py; verify_development_evidence.py.
Non rieseguire vecchi record_*: sovrascrivono lo stato con riepiloghi superati.

Automazione di questa chat:primo controllo dopo5 ore dalla modifica richiesta,
poi la stessa automazione passa a ogni5 minuti. Riprendere dopo il reset quota.
Fermarsi vicino all'1%, lasciando margine per checkpoint e verifiche.
Non riscattare reset e non acquistare crediti.
''',encoding='utf-8')
p=work/'refresh_research_evidence.py';s=p.read_text().replace("date='2026-10-03'","date='2026-10-04'")
s=s.replace("files.update(root/name for name in (", "files.update(root/name for name in ('evidence/p408-mentors.json','evidence/mentors-validation.json','evidence/save-layout.json','P408-RESEARCH.md',")
s=s.replace("'PLACES/P523/DANGERS.MOV'", "'PLACES/P523/DANGERS.MOV','PLACES/P408/MEGAFILE.HYP','PLACES/P408/MENTORS.MOV'")
p.write_text(s)
p=work/'save_development_evidence.py';s=p.read_text().replace("date='2026-10-03'","date='2026-10-04'")
guard="assert 'mentors interaction verification: PASS' in log"
if guard not in s:s=s.replace("for name in ['runtime.log'",guard+"\nassert 'mentor continuous playback: PASS' in log\nassert 'P523 help return: PASS' in log\nfor name in ['runtime.log'",1)
p.write_text(s)
p=root/'survey_puzzles.py';s=p.read_text()
if 'Aggiornamento 4 ottobre' not in s:
 s=s.replace("(args.out/'PUZZLE-SURVEY.md').write_text", "lines += ['', 'Aggiornamento 4 ottobre: P523 integrato,35 scene con percorsi automatici. Aiuto/ritorno P523 e cinque mentori P408 verificati;170 selezioni video e ritorni da37 scene. Libro di aiuto Windows, salvataggi e percorso integrale restano da completare. Conferma manuale solo P508.']\n(args.out/'PUZZLE-SURVEY.md').write_text",1)
p.write_text(s)
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
 subprocess.run([sys.executable,str(work/name)],check=True)
shutil.copyfile(work/'mentors.log',root/'evidence/mentors-scoped.log')
print('Mentors checkpoint saved and verified')
