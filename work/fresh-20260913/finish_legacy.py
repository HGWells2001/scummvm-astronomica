"""Record legacy import only after a matching build, targeted tests and full suite."""
from pathlib import Path
import json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');exe=work/'build/Releasex64/scummvm.exe'
for name,markers in {
 'legacy.log':['legacy save verification: PASS','legacy original payloads: PASS','legacy parser checks: PASS','legacy state checks: PASS'],
 'saves.log':['save verification: PASS','save file verification: PASS'],
 'saves-startup.log':['startup save verification: PASS'],
 'help.log':['help article rendering: PASS (781 articles)','help UI capture: PASS'],
 'runtime.log':['legacy save verification: PASS','Astronomica script verification: PASS','help verification: PASS']}.items():
 p=work/name;text=p.read_text();assert 'FAIL' not in text and 'Log closed successfully' in text,name
 assert p.stat().st_mtime>exe.stat().st_mtime,name
 for marker in markers:assert marker in text,(name,marker)
for p in (root/'engine/astronomica').glob('*'):
 if p.suffix in ('.cpp','.h','.mk'):
  assert p.stat().st_mtime<exe.stat().st_mtime
  assert p.read_bytes()==(work/'scummvm/engines/astronomica'/p.name).read_bytes()
for name in ('legacy.log','legacy-file-proof.json'):
 shutil.copyfile(work/name,root/'evidence'/('legacy-runtime.log' if name=='legacy.log' else name))
shutil.copyfile(work/'help.log',root/'evidence/help-native-runtime.log')
validation=dict(date='2026-10-13',status='PASS',format='Original text GAMESTAT,102 signed decimal values',
 original_payload_cases=15,truncated_token_cases=102,malformed_numeric_cases=8,extra_token_or_oversize_cases=3,
 signed_int32_limits=True,whitespace_forms=['LF','CRLF','spaces/tabs','vertical tab/form feed'],
 disk_fixture_discovery=True,missing_and_invalid_file_preserve_state=True,fixture_unchanged=True,
 mode1_exploration_import=True,restored_fields=['scene','completion count','100 globals'],native_resave=True,
 original_menu_flow=True,scoped_custom33=True,full_suite=True,
 policy=['Read gamestat/GAMESTAT only from selected game directory. No original files overwritten.',
 'Reject active countdown modes1/2 with nonzero global8; the original file contains no recoverable clock epoch.',
 'Reject unsupported destinations and puzzle/mentor/movie scenes before changing live game state.'],
 limitations=['No binary gamestat import','No arbitrary mid-puzzle restore','Valid decimal-value changes cannot be detected without an original checksum','Manual end-to-end gameplay remains pending'])
(root/'evidence/legacy-validation.json').write_text(json.dumps(validation,indent=2))
note=('\n\n## Original text GAMESTAT import, 13 October 2026\n\n'
 'The native engine reads gamestat/GAMESTAT from the selected game directory '
 'without modifying it. It validates all102 signed decimal values and the '
 'destination before enabling the original P1 saved-game choice. Custom33 '
 'restores the exploration scene, completed count and100 globals. Imported '
 'games can then use ordinary ScummVM saves. Original drive-root/current-'
 'directory fallbacks are not searched. The decoded snapshot stays stable '
 'during the menu interaction. Binary gamestat belongs to another original '
 'routine and is not imported.\n\n'
 'Active countdown modes1/2 with nonzero global8 remain rejected. The original '
 'text writer stores the timestamp, not the current epoch or elapsed time. '
 'Two original countdown executions with the same saved timestamp produce '
 'different results at different current clocks; see legacy-resume-original.json. '
 'No timestamp is guessed from file dates and no countdown is reset. '
 'Only mode1 exploration destinations are admitted; arbitrary puzzle state '
 'cannot be reconstructed from the global-only file.\n\n'
 'Build,15 original payload comparisons,102 token-boundary truncations, '
 'signed bounds, malformed/oversized inputs, file discovery, missing/invalid '
 'files, atomic rejection, original menu clicks, native resave, native slot '
 'startup, all781 help article openings and full WASAPI regression PASS. '
 'The fixture original file is unchanged. Syntactically valid altered numbers '
 'cannot be recognized as corruption because the original format has no '
 'checksum. No manual full-game completion claim.\n')
note += ('\nFuture puzzle saves: probe_puzzle_save_requirements.py inventories the '
 '35 verified route resources, including local conditions, sprite frames/clones, '
 'automatic motion, movie references, script delays and custom handlers. '
 'Uninterpreted resource tails are hashed separately; they are not discarded '
 'or claimed decoded. This is a static inventory, not a save implementation. '
 'A scene reload plus globals cannot restore mutable sprite state, local '
 'conditions, pending work or per-puzzle/random state. Continuation tests '
 'must compare uninterrupted and restored runs at intermediate states. '
 'See evidence/puzzle-save-requirements.json.\n')
for name in ('SAVE-RESEARCH.md','README.md','INTERPRETER.md'):
 p=root/name
 if b'## Original text GAMESTAT import, 13 October 2026' not in p.read_bytes():
  with p.open('ab') as f:f.write(note.encode('ascii'))
p=root/'NEXT-STEPS.md';s=p.read_text();start=s.index('Custom33 usa gamestat TESTUALE');end=s.index('Ricerca:probe_movie_controller.py',start)
s=s[:start]+('Custom33/import GAMESTAT testuale integrato per esplorazione modo1 e\n'
 'conto alla rovescia inattivo. Lettura sola dalla cartella del gioco;\n'
 'menu originale,102 valori,15 confronti,102 troncamenti e native resave PASS.\n'
 'I timer attivi restano rifiutati: il file originale non conserva il clock\n'
 'corrente, quindi il tempo residuo non e ricostruibile dal solo GAMESTAT.\n'
 'Non stimarlo dalla data del file e non azzerare il timer.\n'
 'Restano salvataggi interni ai puzzle e percorso integrale manuale.\n'
 'Inventario preliminare delle35 scene: puzzle-save-requirements.json;\n'
 'include condizioni locali, sprite, script, filmati e code non interpretate.\n'
 'Non dimostra ripristinabilita: servono snapshot e prove di continuazione.\n'
 'Leggere SAVE-RESEARCH.md e legacy-validation.json. Test check_legacy.py.\n'
 'Nessuna percentuale globale attendibile.\n')+s[end:]
s=s.replace('completamento aiuto, resume originale, salvataggi','completamento aiuto, import originali con timer attivo, salvataggi')
s=s.replace('408 byte, scena/contatore/100 globals; import gamestat originale NON implementato.', '408 byte, scena/contatore/100 globals; formato binario distinto dal GAMESTAT\ntestuale ora importabile entro i limiti descritti sopra.')
s=s.replace('Checkpoint:finish_help_media.py','Checkpoint:finish_legacy.py').replace('# Ripresa: lettore aiuto nativo integrato, 12 ottobre 2026','# Ripresa: import GAMESTAT originale integrato, 13 ottobre 2026');p.write_text(s)
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
 subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('Legacy GAMESTAT import checkpoint verified13 October2026. Build, original payloads, parser/rejection, disk discovery, original P1 control, native saves/startup, help and full WASAPI suite PASS. Only mode1 exploration with no active countdown; original inputs unchanged. See NEXT-STEPS.md.\n')
print('Native legacy import checkpoint PASS')
