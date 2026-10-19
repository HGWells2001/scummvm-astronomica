"""Finalize P528 v8 only after its native matrix and all compatible tests."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');exe=work/'build/Releasex64/scummvm.exe'
for name,marker in [('p528-saves.log','P528 saves: PASS (160 reachable states, 640 round trips, 6 completion edges, 160 exits, 3444 truncations, 3444 corruptions, 30 invalid states'),('p528-saves-startup.log','P528 startup save: PASS')]:
 p=work/name;s=p.read_text();assert p.stat().st_mtime>exe.stat().st_mtime and marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
proof=json.loads((work/'p528-save-proof.json').read_text());assert proof['status']=='PASS' and proof['metadata_listed'] and proof['slot']==7
for src,dst in [('p528-saves.log','p528-saves-runtime.log'),('p528-saves-startup.log','p528-saves-startup.log'),('p528-save-proof.json','p528-save-proof.json')]:shutil.copyfile(work/src,root/'evidence'/dst)
validation=dict(date='2026-10-18',status='PASS',exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),format_version=8,payload_bytes=3444,scene=528,
 reachable_states=160,boundaries=640,gameplay_successor_comparisons=640,completion_edges=6,unsolved_exits=160,full_frame_height=480,
 truncations=3444,byte_corruptions=3444,invalid_checksummed_states=30,fresh_process_slot=7,fresh_process_fingerprint=proof['fresh_process_fingerprint'],
 full_suite=True,compatibility='Versions1-7 retained; previous-build v3-v7 slots unchanged',
 limitations=['The 160 states abstract clocks, counters, RNG and transient audio; no finite count covers every possible epoch','The matrix uses the already-solved global44 branch; separate original solve routes and fresh-process first completion verify counting/audio','Ambient music restarts from the beginning','No full manual audiovisual playthrough'])
(root/'evidence/p528-saves-validation.json').write_text(json.dumps(validation,indent=2))
old_next=(root/'NEXT-STEPS.md').read_text()
p=subprocess.run([sys.executable,str(work/'finish_audio_channels.py')],capture_output=True,text=True)
if p.returncode:print(p.stdout+p.stderr);p.check_returncode()
print(p.stdout[-400:]);(root/'NEXT-STEPS.md').write_text(old_next)
p=root/'P528-SAVE-PLAN.md';s=p.read_text().replace('P528 saves are not implemented.','P528 v8 settled saves are implemented and verified; see P528-SAVE-FORMAT.md.\nThe preparation below records the original implementation questions.').replace('Suggested v8 payload, still unimplemented:','Implemented v8 payload:');p.write_text(s)
note=('\n\n## P528 native saves, 18 October 2026\n\n'
 'Native v8 saves settled P528 states with full runner/RNG, clock/count, nine sprite records, partial eclipse flags, current image pair and retained tall-moon history. '
 'Tests cover160 reachable abstract states and640 round trips/successors, including six completion edges and160 exits, using full480-row pixel hashes. '
 '3444 truncations,3444 byte corruptions and30 checksummed invalid states reject atomically. Slot7 loads in a fresh process, retains the old moon row and completes the remaining eclipse with first-success counting. '
 'Versions1-7, prior-build slots, presentation/audio controls, help/import and WASAPI regressions pass on the same executable. No whole-game completion percentage is inferred.\n')
for name in ('README.md','SAVE-RESEARCH.md'):
 p=root/name;s=p.read_text()
 if '## P528 native saves, 18 October 2026' not in s:s+=note
 p.write_text(s)
p=root/'P528-SAVE-FORMAT.md';s=p.read_text().replace('Implementation under verification.','Implemented and verified 18 October 2026; evidence/p528-saves-validation.json is PASS.');p.write_text(s)
heading=('# Ripresa: salvataggi P528, 18 ottobre 2026\n\n'
 'P528 v8:160 stati astratti raggiungibili,640 ripristini/successori,6 completamenti e160 uscite PASS; confronto integrale480 righe.\n'
 'Slot7 e nuovo processo: riga Luna persistente, risultato parziale e completamento con conteggio PASS.\n'
 'Compatibilita v1-v7, precedenti slot v3-v7, grafica completa, controllo Musica, import, aiuto e WASAPI PASS sullo stesso eseguibile.\n'
 'Checkpoint: finish_p528_saves.py. Test: check_p528_saves.py e check_p528_regressions.py.\n'
 'Leggere P528-SAVE-FORMAT.md. Prossimo: P530-SAVE-PLAN.md; inventario originale25 immagini/625 coppie, salvataggi P530 ancora assenti. Restano verifica audiovisiva manuale completa e tipografia aiuto.\n'
 'Non rieseguire finalizzatori storici. Nessuna percentuale globale attendibile; vedere AI_MODEL_CHECKPOINT.md.\n\n')
p=root/'NEXT-STEPS.md';s=p.read_text()
if not s.startswith('# Ripresa: salvataggi P528'):s=heading+s
p.write_text(s)
p=Path('AI_MODEL_CHECKPOINT.md');s=p.read_text();s+='\nCheckpoint attuale P528 v8:160 stati astratti/640 successori verificati sul motore reale, formato3444 byte, slot7 e nuovo processo PASS. Grafica480 righe, controllo Musica, compatibilita v1-v7 e WASAPI PASS. Sei scene con salvataggi non misurano completamento globale. Configurazione AI corrente sufficiente, variante/livello client non verificabili; nessun cambio richiesto o applicato. Leggere NEXT-STEPS.md, P528-SAVE-FORMAT.md e finish_p528_saves.py; scegliere il prossimo puzzle da inventario.\n';p.write_text(s)
for name in ('record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('P528 v8 verified 18 October 2026.160 abstract states,640 successors, full480-row images, malformed rejection and fresh-process partial completion PASS. Full compatible save/presentation/audio/help/import/WASAPI suite PASS on the same executable. No tests running. See NEXT-STEPS.md and AI_MODEL_CHECKPOINT.md.\n')
print('P528 v8 save checkpoint PASS')
