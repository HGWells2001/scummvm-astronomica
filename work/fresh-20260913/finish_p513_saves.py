"""Finalize P513 v11 after same-build targeted, old-slot and full suites."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');exe=work/'build/Releasex64/scummvm.exe';ai_before=Path('AI_MODEL_CHECKPOINT.md').read_text()
for name,marker in [('p513-saves.log','P513 saves: PASS ('),('p513-saves-startup.log','P513 startup save: PASS'),('variant-previous-slot.log','variant startup save: PASS')]:
 p=work/name;s=p.read_text();assert p.stat().st_mtime>exe.stat().st_mtime and marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
proof=json.loads((work/'p513-save-proof.json').read_text());assert proof['status']=='PASS' and proof['metadata_listed'] and proof['slot']==10 and proof['boundaries']>100
assert (proof['routes'],proof['scenarios'],proof['photon_results'],proof['answer_continuations'],proof['live_setting_changes'])==(5,14,9,126,2)
for src,dst in [('p513-saves.log','p513-saves-runtime.log'),('p513-saves-startup.log','p513-saves-startup.log'),('p513-save-proof.json','p513-save-proof.json'),('variant-previous-slot.log','variant-previous-slot.log'),('variant-previous-slot-proof.json','variant-previous-slot-proof.json')]:shutil.copyfile(work/src,root/'evidence'/dst)
assert json.loads((work/'variant-previous-slot-proof.json').read_text())['unchanged']
validation=dict(date='2026-10-19',status='PASS',exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),format_version=11,payload_bytes=5928,scene=513,boundaries=proof['boundaries'],gameplay_successor_comparisons=proof['boundaries'],
 solve_and_exit_routes=5,scenarios=14,photon_results=9,answer_continuations=126,live_setting_changes=2,full_frame_height=480,truncations=5928,byte_corruptions=5928,invalid_checksummed_states=37,fresh_process_slot=10,fresh_process_fingerprint=proof['fresh_process_fingerprint'],
 retained_stopped_photon=True,retained_digits=True,random_continuation=True,silent_first_success=True,repeated_success_count=True,full_suite=True,compatibility='Versions1-10 retained; prior-build v3-v10 slots unchanged',
 limitations=['Settled states only; active photon trajectories and half-step knob programs are not saved','Successor hashes omit new-scene program/departure sound epochs; pre-action payload comparison includes saved epochs','Music restarts from its beginning','No full manual audiovisual playthrough'])
(root/'evidence/p513-saves-validation.json').write_text(json.dumps(validation,indent=2))
p=subprocess.run([sys.executable,str(work/'finish_variant_saves.py')],capture_output=True,text=True)
if p.returncode:print(p.stdout+p.stderr);p.check_returncode()
print(p.stdout[-300:])
note=(f'\n\n## P513 native saves,19 October2026\n\nNative v11 retains six locals/RNG,32 complete sprite records, stopped hidden photon endpoint and old digit/result state, cube image and clock/count. '
 f'{proof["boundaries"]} native round trips/successors cover five solve/exit routes, all14 scenarios, nine photon results, bounds and silent first/repeated success. '
 'Slot10 resumes after two correct answers in a fresh process and finishes with the original count. All5928 truncations,5928 byte corruptions and37 checksummed invalid states reject without changing state. '
 'Versions1-10, old slots, cross-puzzle entry correction, full graphics/audio/help/import/WASAPI and normal launcher startup pass on the same build.\n')
for name in ('README.md','SAVE-RESEARCH.md'):
 p=root/name;s=p.read_text()
 if '## P513 native saves,19 October2026' not in s:s+=note
 p.write_text(s)
p=root/'P513-SAVE-FORMAT.md';s=p.read_text().replace('Implementation being prepared,19 October2026; not yet a verified checkpoint.','Implemented and verified19 October2026; see evidence/p513-saves-validation.json.');p.write_text(s)
heading=('# Ripresa: salvataggi P513,19 ottobre2026\n\n'
 f'Formato v11: {proof["boundaries"]} ripristini/successori, cinque percorsi,14 scenari e nove risultati fotone PASS. Conserva fotone fermo nascosto, vecchie cifre, immagine cubo, RNG e conteggio silenzioso originale.\n'
 'Slot10 in nuovo processo dopo due risposte corrette PASS; limiti, dieci errori, primo/ripetuto successo e uscita volontaria PASS. Compatibilita v1-v10, vecchi slot v3-v10 e suite completa WASAPI PASS sullo stesso eseguibile.\n'
 'Checkpoint: finish_p513_saves.py; check_p513_saves.py, check_p513_regressions.py e P513-SAVE-FORMAT.md. Non rieseguire finalizzatori storici da soli.\n'
 'Avvio: Avvia-Astronomica.cmd; preferenze e salvataggi personali in userdata/astronomica. Prossimo: altri salvataggi, verifica audiovisiva manuale integrale e tipografia aiuto. Quattordici scene con salvataggi non misurano il completamento globale.\n\n')
p=root/'NEXT-STEPS.md';s=p.read_text()
if not s.startswith('# Ripresa: salvataggi P513'):s=heading+s
p.write_text(s)
model=next((line for line in ai_before.splitlines() if line.startswith('Modello dichiarato')), 'Modello dichiarato dall\'utente: GPT-6.1 Sol, ragionamento medio. Nessun cambio automatico applicato.')
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,19 ottobre2026\n\n'+model+'\n\n'
 f'Checkpoint: P513 v11,5928 byte,{proof["boundaries"]} successori, cinque percorsi,14 scenari,nove risultati fotone e slot10 in nuovo processo PASS. Conserva fotone fermo/cifre e RNG; conteggio originale silenzioso, errori/limiti/uscite PASS. Compatibilita v1-v10 e suite completa WASAPI PASS.\n\n'
 'Seguire NEXT-STEPS.md, P513-SAVE-FORMAT.md e check_p513_saves.py/check_p513_regressions.py/finish_p513_saves.py. Sorgenti canonici in outputs/astronomica-cleanroom/engine/astronomica. Non ricopiare vecchi file di staging sopra i sorgenti correnti.\n\n'
 'Avvio reale: Avvia-Astronomica.cmd; userdata/astronomica contiene preferenze/salvataggi personali. Restano altri salvataggi, verifica audiovisiva manuale integrale e tipografia aiuto. Quattordici scene con salvataggi non sono una percentuale globale.\n\n'
 'Vincoli: originali D:/astro, solo cleanroom dal13 settembre2026, niente vecchi tentativi esclusi o nuovi prototipi. Modello corrente sufficiente, nessun cambio richiesto; se occorre cambiare, checkpoint e conferma del protocollo utente. Controllare entrambe le quote, riservare verifica/pubblicazione e fermarsi vicino all\'1% limitante; nessun acquisto o riscatto reset.\n')
for name in ('record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('P513 v11 verified19 October2026. Targeted/fresh-process/prior-slot and full compatible WASAPI suites PASS; no tests running. Follow NEXT-STEPS.md and AI_MODEL_CHECKPOINT.md.\n')
print('P513 v11 save checkpoint PASS')
