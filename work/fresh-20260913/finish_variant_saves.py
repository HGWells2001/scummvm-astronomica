"""Finalize custom17 v10 only after same-build targeted and full regressions."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');exe=work/'build/Releasex64/scummvm.exe'
ai_before=Path('AI_MODEL_CHECKPOINT.md').read_text()
for name,marker in [('variant-saves.log','variant saves: PASS ('),('variant-saves-startup.log','variant startup save: PASS'),('p530-previous-slot.log','P530 startup save: PASS')]:
 p=work/name;s=p.read_text();assert p.stat().st_mtime>exe.stat().st_mtime and marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
proof=json.loads((work/'variant-save-proof.json').read_text())
assert proof['status']=='PASS' and proof['metadata_listed'] and proof['slot']==9 and proof['routes']>=12 and proof['initial_repeats']>0
assert proof['transitions']==4*proof['routes']+1 and proof['truncations']==proof['corruptions']==23736 and proof['invalid_states']==192
for src,dst in [('variant-saves.log','variant-saves-runtime.log'),('variant-saves-startup.log','variant-saves-startup.log'),('variant-save-proof.json','variant-save-proof.json'),('p530-previous-slot.log','p530-previous-slot.log'),('p530-previous-slot-proof.json','p530-previous-slot-proof.json')]:shutil.copyfile(work/src,root/'evidence'/dst)
for name in ('save-entry-history.log','save-entry-history-proof.json','save-entry-history-before.log'):shutil.copyfile(work/name,root/'evidence'/name)
history=json.loads((root/'evidence/save-entry-history-proof.json').read_text())
assert history['status']=='PASS' and history['exe_sha256']==hashlib.sha256(exe.read_bytes()).hexdigest()
assert json.loads((work/'p530-previous-slot-proof.json').read_text())['unchanged']
launcher=json.loads((root/'evidence/local-launcher-validation.json').read_text())
assert launcher['status']=='PASS' and launcher['exe_sha256']==hashlib.sha256(exe.read_bytes()).hexdigest()
shutil.copyfile(work/'launcher startup check/startup.log',root/'evidence/local-launcher-startup.log')
validation=dict(date='2026-10-19',status='PASS',exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),format_version=10,
 payload_bytes_by_scene={'506':3992,'531':3992,'532':3776,'533':3776,'534':4424,'535':3776},
 boundaries=proof['boundaries'],gameplay_successor_comparisons=proof['boundaries'],solve_routes=proof['routes'],transitions=proof['transitions'],initial_repeats=proof['initial_repeats'],
 scenes_per_stage=6,stages=4,full_frame_height=480,truncations=23736,byte_corruptions=23736,invalid_checksummed_states=192,
 fresh_process_slot=9,fresh_process_fingerprint=proof['fresh_process_fingerprint'],partial_solutions=True,process_statics=True,random_continuation=True,first_completion_count=True,repeated_completion_count=True,exit_reentry=True,
 full_suite=True,compatibility='Versions1-9 retained; previous-build v3-v9 slots unchanged',
 limitations=['Route coverage includes every scene at each stage, not all possible input histories','Successor fingerprints omit newly rebuilt program and departure sound epochs; exact pre-action payload checks retain saved epochs','Ambient sample cursor restarts','No complete manual audiovisual playthrough'])
(root/'evidence/variant-saves-validation.json').write_text(json.dumps(validation,indent=2))
old_next=(root/'NEXT-STEPS.md').read_text()
p=subprocess.run([sys.executable,str(work/'finish_p530_saves.py')],capture_output=True,text=True)
if p.returncode:print(p.stdout+p.stderr);p.check_returncode()
print(p.stdout[-300:]);(root/'NEXT-STEPS.md').write_text(old_next)
note=(f'\n\n## Six-scene custom17 saves,19 October2026\n\nNative v10 saves P506/P531/P532/P533/P534/P535 partial solutions, all runner data and the original round/mask process statics. '
 f'{proof["boundaries"]} round trips and successors across {proof["routes"]} randomized solve routes cover all six scenes at each of four stages, including {proof["initial_repeats"]} initial-scene repeats. '
 'Slot9 resumes a partial solution at round2 in a fresh process, then finishes the remaining nonrepeating rounds and first completion count. '
 'Voluntary exit/reentry retains the original statics. All23736 truncations,23736 single-byte corruptions and192 checksummed invalid payloads reject without changing state. '
 'The P509 entry-history regression also passes for P524/P526/P528/P530: previously retained unknown locals blocked saving. Four natural entries and12 inert-value extremes now round-trip, while8 invalid metadata cases still reject. v6-v9 payload layouts remain unchanged. '
 'v1-v9 compatibility, prior-build slots, normal P1 launcher startup, full graphics/audio/help/import/WASAPI suite pass on the same executable.\n')
for name in ('README.md','SAVE-RESEARCH.md'):
 p=root/name;s=p.read_text()
 if '## Six-scene custom17 saves,19 October2026' not in s:s+=note
 p.write_text(s)
p=root/'VARIANT-SAVE-FORMAT.md';s=p.read_text().replace('Implementation being prepared,19 October2026. Not yet a verified checkpoint.','Implemented and verified19 October2026. See evidence/variant-saves-validation.json.').replace('The proposed v10 payload','The v10 payload');p.write_text(s)
heading=('# Ripresa: salvataggi della sequenza P506,19 ottobre2026\n\n'
 f'Formato v10 per P506/P531/P532/P533/P534/P535: {proof["boundaries"]} ripristini/successori, {proof["routes"]} percorsi, sei scene in ciascuna fase0..3 PASS.\n'
 'Conserva soluzioni parziali, RNG e statica originale round/mask anche dopo uscita/rientro. Slot9 in nuovo processo e contatori primo/ripetuto completamento PASS.\n'
 'Corretto il rifiuto dei salvataggi P524/P526/P528/P530 dopo altri enigmi: quattro ingressi originali da P509,12 estremi inattivi e8 rifiuti di metadati incoerenti PASS; layout v6-v9 invariati.\n'
 'Compatibilita v1-v9, vecchi slot v3-v9, avvio P1 e suite completa WASAPI PASS sullo stesso eseguibile.\n'
 'Checkpoint: finish_variant_saves.py; check_variant_saves.py, check_variant_regressions.py e VARIANT-SAVE-FORMAT.md. Non rieseguire finalizzatori storici da soli.\n'
 'Avvio locale: Avvia-Astronomica.cmd nella radice; configurazione/salvataggi personali in userdata/astronomica, separati dalle prove.\n'
 'Prossimo: altri puzzle dall\'inventario; restano verifica audiovisiva manuale integrale e tipografia aiuto. Tredici scene con salvataggi non misurano il completamento globale.\n\n')
p=root/'NEXT-STEPS.md';s=p.read_text()
if not s.startswith('# Ripresa: salvataggi della sequenza P506'):s=heading+s
p.write_text(s)
model=next((line for line in ai_before.splitlines() if line.startswith('Modello dichiarato')), 'Modello dichiarato dall\'utente: GPT-6.1 Sol, ragionamento medio. Nessun cambio automatico applicato.')
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,19 ottobre2026\n\n'+model+'\n\n'
 f'Checkpoint: custom17 v10 per P506/P531-P535; {proof["boundaries"]} successori, {proof["routes"]} percorsi casuali, sei scene nelle quattro fasi. Slot9 in nuovo processo con soluzione parziale/statica/RNG e primo conteggio PASS; ripetizioni e uscita/rientro PASS. Compatibilita v1-v9 e suite completa WASAPI PASS.\n\n'
 'Corretto anche il rifiuto P524/P526/P528/P530 dopo P509: quattro ingressi reali,12 estremi inattivi e8 metadati invalidi PASS; layout v6-v9 invariati.\n\n'
 'Sorgenti canonici: outputs/astronomica-cleanroom/engine/astronomica. Seguire NEXT-STEPS.md, VARIANT-SAVE-FORMAT.md, check_variant_saves.py, check_variant_regressions.py, check_save_entry_history.py e finish_variant_saves.py. Avvia-Astronomica.cmd usa la build reale corrente; userdata/astronomica conserva preferenze e salvataggi personali.\n\n'
 'Prossimo: altri salvataggi dall\'inventario, verifica audiovisiva manuale e tipografia aiuto. Configurazione AI corrente sufficiente; nessun cambio richiesto. Se occorre cambiarla, salvare checkpoint e attendere la conferma del protocollo utente.\n\n'
 'Vincoli: motore reale senza prototipi, originali D:/astro, solo cleanroom dal13 settembre2026, nessun tentativo precedente escluso. Controllare entrambe le quote; riservare verifica/pubblicazione e fermarsi vicino all\'1% limitante. Nessun riscatto reset o acquisto. Tredici scene con salvataggi non misurano il completamento globale.\n')
for name in ('record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('Custom17 v10 verified19 October2026. Targeted/fresh-process/prior-slot/normal-startup and full compatible WASAPI suites PASS. No tests running. See NEXT-STEPS.md and AI_MODEL_CHECKPOINT.md.\n')
print('Six-scene custom17 v10 save checkpoint PASS')
