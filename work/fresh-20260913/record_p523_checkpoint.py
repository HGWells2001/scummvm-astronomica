"""Record native P523 only after scoped, continuous and full-suite success."""
from pathlib import Path
import json,subprocess,sys,shutil
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
for name in ('runtime.log','p523.log','p523-continuous.log'):
 text=(work/name).read_text()
 assert 'FAIL' not in text and 'P523 interaction verification: PASS' in text,name
 if name=='runtime.log':assert 'Astronomica script verification: PASS' in text
 if name=='p523.log':
  for i in range(10):assert f'P523 route {i}: PASS' in text

note='''

## Integrated P523 checkpoint, 3 October 2026

Native P523 and full regression suite PASS.35 route scenes, not35 distinct
puzzles. Controls:5899 reachable states/35394 transitions. Callback comparison:
262656 cases, with the explicit malformed event8 call repair documented below.
Positions:100 exact x87 cases. Ten click routes include first/repeated victory,
five failures, simultaneous response flags, exit and opening help. A complete
winning movie route passed without seeks and with real input delays.
Manual audiovisual review, help return, saves and whole-game playthrough remain.

Original4:7a87-7a9f passes two WORDs to a two-DWORD movie-range function,
producing start5246601 and an uninitialized duration. The native engine uses
the explicit original WORD values3721/80 for this failure clip. This is a
documented compatibility repair, not literal emulation of undefined stack data.
The original probes now label that duration unknown; normalized native
reference hash:f8ea0405. Control hash:40e80615; position hash:742cfb9d.
P523 also needs the full movie duration before startup custom5 selects a range.
'''
for name in ('README.md','INTERPRETER.md','P523-RESEARCH.md'):
 p=root/name
 if b'## Integrated P523 checkpoint, 3 October 2026' not in p.read_bytes():
  with p.open('ab') as f:f.write(note.encode('ascii'))
p=root/'P523-RESEARCH.md';s=p.read_text().replace('P523 is not enabled. The current production checkpoint includes P510 and P516.','P523 is integrated. The original research below precedes the native checkpoint at the end.');p.write_text(s)
(root/'NEXT-STEPS.md').write_text('''# Ripresa: P523 integrato, 3 ottobre 2026

Build, dieci percorsi P523, filmato continuo e suite completa PASS.
35 scene con percorsi automatici; non35 puzzle distinti. Conferma manuale P508.
Percentuale globale ignota. Leggere P523-RESEARCH.md per la correzione esplicita
del ramo video originale malformato e per la precisione x87 delle posizioni.

Proseguire con verifica del percorso generale, aiuto/ritorno e salvataggi.
P520 ha test del razzo e filmato: controllare cosa manca al percorso completo
prima di includerlo nel conteggio. P507 resta interattiva, non un puzzle risolto.
Non confondere il riconoscimento degli opcode con la giocabilita integrale.

Canonical outputs/astronomica-cleanroom/engine/astronomica; mirror
work/fresh-20260913/scummvm/engines/astronomica; build locale
work/fresh-20260913/build/Releasex64/scummvm.exe.
Test:check_p523.py, check_p523_continuous.py, runtime_test.py.
Checkpoint:record_p523_checkpoint.py; integrita:verify_development_evidence.py.
Non rieseguire i vecchi record_*: ripristinano riepiloghi superati.
Automazione attiva in questa chat: controllo quota ogni5 ore e ripresa dopo reset.
Fermarsi vicino all'1%, lasciando margine per chiusura e verifica; niente reset riscattati.
''',encoding='utf-8')
(root/'evidence/p523-validation.json').write_text(json.dumps(dict(status='PASS',callback_cases=262656,
 compatibility_repair='event8 malformed original movie arguments restored to3721/80',
 control_states=5899,control_transitions=35394,position_cases=100,click_routes=10,
 continuous_winning_route=True,real_input_delays=True,full_suite=True,manual_confirmation=False),indent=2))
p=work/'save_development_evidence.py';s=p.read_text().replace("date='2026-10-02'","date='2026-10-03'").replace('521,522,524,','521,522,523,524,').replace('continuous_video_scenes=[510,512,520,','continuous_video_scenes=[510,512,520,523,')
guard="assert 'P523 interaction verification: PASS' in log"
if guard not in s:s=s.replace("for name in ['runtime.log'",guard+"\nfor name in ['runtime.log'",1)
p.write_text(s)
p=work/'refresh_research_evidence.py';s=p.read_text().replace("date='2026-10-02'","date='2026-10-03'").replace('P516 and P510 native routes','P516, P510 and P523 native routes');p.write_text(s)
for script in ('refresh_research_evidence.py','save_development_evidence.py'):
 subprocess.run([sys.executable,str(work/script)],check=True)
for name in ('p523.log','p523-continuous.log'):shutil.copyfile(work/name,root/'evidence'/name)
subprocess.run([sys.executable,str(work/'verify_development_evidence.py')],check=True)
print('P523 checkpoint saved and verified')
