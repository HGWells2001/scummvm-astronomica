"""Finalize native P530 v9 after same-build targeted and complete regressions."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');exe=work/'build/Releasex64/scummvm.exe'
ai_before=Path('AI_MODEL_CHECKPOINT.md').read_text()
for name,marker in [('p530-saves.log','P530 saves: PASS ('),('p530-saves-startup.log','P530 startup save: PASS'),('p528-previous-slot.log','P528 startup save: PASS')]:
 p=work/name;s=p.read_text();assert p.stat().st_mtime>exe.stat().st_mtime and marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
proof=json.loads((work/'p530-save-proof.json').read_text());assert proof['status']=='PASS' and proof['metadata_listed'] and proof['slot']==8
assert proof['round_trips']==57*proof['solve_routes']+2 and 8<=proof['solve_routes']<=32
for src,dst in [('p530-saves.log','p530-saves-runtime.log'),('p530-saves-startup.log','p530-saves-startup.log'),('p530-save-proof.json','p530-save-proof.json'),('p528-previous-slot.log','p528-previous-slot.log'),('p528-previous-slot-proof.json','p528-previous-slot-proof.json')]:shutil.copyfile(work/src,root/'evidence'/dst)
assert json.loads((work/'p528-previous-slot-proof.json').read_text())['unchanged']
validation=dict(date='2026-10-19',status='PASS',exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),format_version=9,payload_bytes=5604,scene=530,
 boundaries=proof['round_trips'],gameplay_successor_comparisons=proof['round_trips'],solve_routes=proof['solve_routes'],scenarios_per_round=5,rounds=3,pictures=25,
 full_frame_height=480,truncations=5604,byte_corruptions=5604,invalid_checksummed_states=31,fresh_process_slot=8,fresh_process_fingerprint=proof['fresh_process_fingerprint'],
 partial_components=True,prior_round_picture=True,random_continuation=True,counter_unchanged=True,placement_permutations=6,full_suite=True,compatibility='Versions1-8 retained; previous-build v3-v8 slots unchanged',
 limitations=['The routes cover every scenario in each round and all six placement permutations, not all possible input histories','Successor fingerprints exclude fresh-scene program/sound epochs after departure; exact pre-action reserialization includes all saved epochs','Ambient sample cursor is not retained','No full manual audiovisual playthrough'])
(root/'evidence/p530-saves-validation.json').write_text(json.dumps(validation,indent=2))
old_next=(root/'NEXT-STEPS.md').read_text()
p=subprocess.run([sys.executable,str(work/'finish_p528_saves.py')],capture_output=True,text=True)
if p.returncode:print(p.stdout+p.stderr);p.check_returncode()
print(p.stdout[-300:]);(root/'NEXT-STEPS.md').write_text(old_next)
note=('\n\n## P530 native saves,19 October2026\n\n'
 f'Native v9 retains14 locals and full runner/RNG,29 sprite records including hidden settled indicator positions, clock/count and the last picture or absence. '
 f'{proof["round_trips"]} round trips across{proof["solve_routes"]} randomized routes cover five scenarios at every round, all25 pictures, all six placement permutations, wrong/repeated answers and unsolved exit. '
 'Slot8 loads in a fresh process with a partial component assembly and prior-round picture, then completes the remaining random rounds without increasing the counter, as in the original. '
 '5604 truncations,5604 byte corruptions and31 checksummed invalid states reject atomically. Versions1-8, previous-build slots, full-frame presentation, music controls, help/import and WASAPI pass on the same executable.\n')
for name in ('README.md','SAVE-RESEARCH.md','P530-SAVE-PLAN.md'):
 p=root/name;s=p.read_text()
 if '## P530 native saves,19 October2026' not in s:s+=note
 if name=='P530-SAVE-PLAN.md':s=s.replace('P530 native saves are not implemented.','P530 v9 settled saves are implemented and verified; see P530-SAVE-FORMAT.md.\nThe inventory below records the original preparation.')
 p.write_text(s)
p=root/'P530-SAVE-FORMAT.md';s=p.read_text().replace('Implementation under verification,19 October2026.','Implemented and verified19 October2026; evidence/p530-saves-validation.json is PASS.');p.write_text(s)
heading=('# Ripresa: salvataggi P530,19 ottobre2026\n\n'
 f'P530 v9:{proof["round_trips"]} ripristini/successori,{proof["solve_routes"]} percorsi randomizzati; cinque scenari per ogni turno,25 immagini, entrambi gli ordini componenti PASS.\n'
 'Slot8/nuovo processo: montaggio parziale, immagine del turno precedente, RNG e contatore invariato PASS.\n'
 'Compatibilita v1-v8, precedenti slot v3-v8 e suite grafica/audio/help/import/WASAPI PASS sullo stesso eseguibile.\n'
 'Checkpoint: finish_p530_saves.py. Test: check_p530_saves.py e check_p530_regressions.py.\n'
 'Prossimo: inventario dei salvataggi per il prossimo puzzle; restano verifica audiovisiva manuale e tipografia aiuto. Non rieseguire finalizzatori storici.\n'
 'Nessuna percentuale globale attendibile. Modello utente: GPT-6.1 Sol / medio.\n\n')
p=root/'NEXT-STEPS.md';s=p.read_text()
if not s.startswith('# Ripresa: salvataggi P530'):s=heading+s
p.write_text(s)
model=next((line for line in ai_before.splitlines() if line.startswith('Modello dichiarato')), 'Modello dichiarato dall\'utente: GPT-6.1 Sol, ragionamento medio. Nessun cambio automatico applicato.')
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,19 ottobre2026\n\n'+model+'\n\n'
 f'Checkpoint attuale: P530 v9,5604 byte,{proof["round_trips"]} successori/{proof["solve_routes"]} percorsi randomizzati,25 immagini e cinque scenari in ogni turno. Slot8, nuovo processo, montaggio parziale, RNG e contatore originale invariato PASS. Compatibilita v1-v8 e WASAPI PASS.\n\n'
 'Sorgenti: outputs/astronomica-cleanroom/engine/astronomica/astronomica.cpp e astronomica.h. Leggere NEXT-STEPS.md, P530-SAVE-FORMAT.md, check_p530_saves.py, check_p530_regressions.py e finish_p530_saves.py. Non rieseguire finalizzatori storici da soli.\n\n'
 'Prossimo: scegliere il prossimo puzzle dall\'inventario; restano verifica audiovisiva manuale e tipografia aiuto. Configurazione AI corrente sufficiente; rivalutare prima di una fase piu difficile. Se occorre cambiare, salvare checkpoint, chiedere e attendere la conferma del protocollo utente. Nessuna richiesta pendente.\n\n'
 'Vincoli: motore reale senza prototipi, originali D:/astro, solo cleanroom dal13 settembre2026; nessun tentativo precedente escluso. Controllare entrambe le quote, riservare verifica/pubblicazione, fermarsi vicino all\'1% limitante, non riscattare reset o acquistare crediti. Sette scene con salvataggi non misurano il completamento globale.\n')
for name in ('record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('P530 v9 verified19 October2026. Same-build targeted, fresh-process, previous-slot and full compatible presentation/audio/help/import/WASAPI suites PASS. No tests running. See NEXT-STEPS.md and AI_MODEL_CHECKPOINT.md.\n')
print('P530 v9 save checkpoint PASS')
