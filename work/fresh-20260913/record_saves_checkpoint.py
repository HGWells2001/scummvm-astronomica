"""Record exploration saves only after scoped, startup and full-suite success."""
from pathlib import Path
import json,subprocess,sys,shutil
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
for name in ('runtime.log','saves.log','saves-startup.log'):
 text=(work/name).read_text()
 assert 'save verification: PASS' in text and 'FAIL' not in text,name
 if name=='runtime.log':assert 'Astronomica script verification: PASS' in text
 else:assert 'save menu verification: PASS' in text and 'save file verification: PASS' in text
 if name=='saves-startup.log':assert 'startup save verification: PASS' in text
assert 'Astronomica regression' in (work/'saves-list.log').read_text()
note='''

## Exploration saves checkpoint, 4 October 2026

Native saves now preserve exploration location, completed-puzzle counter and
100 globals. F5 opens the standard ScummVM menu. Startup loading, slot listing,
metadata and menu opening/closing pass.840 truncated/corrupted payload checks
pass; unsupported destinations do not change the active game. Video and script
time pause in the menu. The full regression suite passes with these changes.
Saves are currently limited to settled mode1 exploration screens. No original
gamestat import or arbitrary mid-puzzle restoration is claimed. See
SAVE-RESEARCH.md.35 puzzle-route scenes remain verified; whole-game completion
is not measured. Windows help book and manual audiovisual playthrough remain.
'''
for name in ('README.md','INTERPRETER.md','SAVE-RESEARCH.md'):
 p=root/name
 if b'## Exploration saves checkpoint, 4 October 2026' not in p.read_bytes():
  with p.open('ab') as f:f.write(note.encode('ascii'))
(root/'evidence/saves-validation.json').write_text(json.dumps(dict(status='PASS',
 original_roundtrips=5,global_values=100,native_prefix_bytes=420,truncations=420,
 corruptions=420,destination_guard=True,physical_slot=True,startup=True,
 metadata_list=True,standard_menu=True,pause=True,full_suite=True,
 scope='Settled mode1 exploration scenes; no mid-puzzle saves or gamestat import',manual_confirmation=False),indent=2))
p=root/'NEXT-STEPS.md';s=p.read_text();s=s.replace('# Ripresa: mentori P408 integrati, 4 ottobre 2026','# Ripresa: salvataggi esplorazione integrati, 4 ottobre 2026')
s=s.replace('Proseguire con aiuto Windows (custom22/process_help), salvataggi e percorso\ngenerale.', 'Salvataggi nativi: F5, slot ScummVM, caricamento iniziale; solo schermate\ndi esplorazione modo1 ferme. Leggere SAVE-RESEARCH.md. Test mirati e suite PASS.\nProseguire con aiuto Windows (custom22/process_help), ripresa interna ai puzzle\ne percorso generale.')
s=s.replace('native saves NON implementati.','import gamestat originale NON implementato.')
s=s.replace('Checkpoint:record_mentors_checkpoint.py;', 'Test salvataggi:check_saves.py. Checkpoint:record_saves_checkpoint.py;')
s=s.replace('Automazione di questa chat:primo controllo dopo5 ore dalla modifica richiesta,\npoi la stessa automazione passa a ogni5 minuti. Riprendere dopo il reset quota.', 'Automazione di questa chat:controllo quota ogni5 minuti; prima attesa conclusa.\nRiprendere dopo il reset quota, senza duplicare automazioni.')
p.write_text(s,encoding='utf-8')
p=work/'refresh_research_evidence.py';s=p.read_text()
if "'SAVE-RESEARCH.md'" not in s:s=s.replace('files.update(root/name for name in (', "files.update(root/name for name in ('SAVE-RESEARCH.md','evidence/saves-validation.json',",1)
p.write_text(s)
p=work/'save_development_evidence.py';s=p.read_text()
guard="assert 'save verification: PASS' in log"
if guard not in s:s=s.replace("for name in ['runtime.log'",guard+"\nfor name in ['runtime.log'",1)
p.write_text(s)
for name in ('saves.log','saves-startup.log','saves-list.log'):shutil.copyfile(work/name,root/'evidence'/name)
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
 subprocess.run([sys.executable,str(work/name)],check=True)
print('Exploration saves checkpoint saved and verified')
