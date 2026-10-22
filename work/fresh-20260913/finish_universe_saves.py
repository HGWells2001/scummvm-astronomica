"""Finalize v15 only after the complete same-build native suite has passed."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
r=Path('outputs/astronomica-cleanroom');w=Path('work/fresh-20260913');exe=w/'build/Releasex64/scummvm.exe'
d=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=next(x for x in Path('AI_MODEL_CHECKPOINT.md').read_text().splitlines() if x.startswith('Modello dichiarato'))
proof=json.loads((w/'universe-save-proof.json').read_text());audit=json.loads((w/'universe-boundaries-proof.json').read_text())
assert proof['status']=='PASS' and proof['exe_sha256']==audit['exe_sha256']==d(exe)
assert proof['metadata_listed'] and proof['slot']==14 and not proof['diagnostic'] and proof['audio_driver']=='native'
assert proof['boundaries']>100 and proof['history_boundaries']>50 and proof['dormant_boundaries']>100 and proof['busy_rejections']>0
assert proof['truncations']==proof['corruptions']==3684 and proof['invalid_states']>=25 and proof['variant_fixture_unchanged']
assert proof['movie_samples']==audit['movie_samples']==253 and audit['boundaries']>=137
assert proof['movie_audit_proof_sha256']==d(w/'universe-boundaries-proof.json') and proof['movie_audit_log_sha256']==d(w/'universe-boundaries.log')
for name,marker in [('universe-saves.log','universe saves: PASS ('),('universe-saves-startup.log','universe startup save: PASS'),('rocket-previous-slot.log','rocket startup save: PASS'),('universe-boundaries.log','universe boundary result: PASS')]:
 p=w/name;s=p.read_text();assert p.stat().st_mtime>exe.stat().st_mtime and marker in s and 'FAIL' not in s and 'Log closed successfully' in s,name
s=(w/'universe-saves.log').read_text()
for marker in ('universe natural voice end: PASS','universe Music restart: PASS','universe extra guards: PASS','universe zero-frame history: PASS'):assert marker in s,marker
for src,dst in [('universe-saves.log','universe-saves-runtime.log'),('universe-saves-startup.log','universe-saves-startup.log'),('universe-save-proof.json','universe-save-proof.json'),('universe-boundaries-proof.json','universe-boundaries-proof.json'),('universe-boundaries.log','universe-boundaries.log'),('rocket-previous-slot.log','rocket-previous-slot.log'),('rocket-previous-slot-proof.json','rocket-previous-slot-proof.json')]:shutil.copyfile(w/src,r/'evidence'/dst)
v=dict(date='2026-10-21',status='PASS',exe_sha256=d(exe),format_version=15,payload_bytes=3684,scene=529,
 boundaries=proof['boundaries'],history_boundaries=proof['history_boundaries'],dormant_boundaries=proof['dormant_boundaries'],busy_rejections=proof['busy_rejections'],
 truncations=3684,byte_corruptions=3684,invalid_checksummed_states=proof['invalid_states'],fresh_process_slot=14,fresh_process_fingerprint=proof['fresh_process_fingerprint'],
 music_restart=True,natural_voice_end=True,ordinary_round_zero=True,zero_frame_history=True,extended_atomic_state=True,movie_samples=253,
 dormant_sequence_retained=True,comet_phase_retained=True,full_frame_height=480,full_suite=True,
 compatibility='Versions1-14 retained; previous-build v3-v14 slots unchanged',
 limitations=['Settled script boundaries only; queued commands, active movies and foreground speech bar saving','Ambient sample restarts from beginning','Most movie routes are test-skipped after a real frame; controlled zero-frame cases also verified','No complete manual audiovisual playthrough'])
(r/'evidence/universe-saves-validation.json').write_text(json.dumps(v,indent=2))
p=subprocess.run([sys.executable,str(w/'finish_rocket_saves.py')],capture_output=True,text=True)
if p.returncode:print(p.stdout+p.stderr);p.check_returncode()
print(p.stdout[-250:])
heading=('# Ripresa: salvataggi universo P529,21 ottobre2026\n\n'
 f'Formato v15:3684 byte,{proof["boundaries"]} ripristini/successori,{proof["history_boundaries"]} confini con immagini/cifre precedenti,{proof["dormant_boundaries"]} con custom17 sospeso PASS.\n'
 'Tutti16 selector,quattro gruppi,primo/ripetuto successo,uscita e slot14 in nuovo processo PASS. Immagine realmente presentata indipendente dal cursore decoder e dall\'ultimo segmento tentato; verificati anche primo filmato senza fotogramma e immagine residua di gruppo precedente.\n'
 'Audit indipendente253 fotogrammi originali e137 confini; fine voce naturale,Music restart,stati ordinari round0 e rifiuto atomico esteso PASS. Compatibilita v1-v14,suite completa WASAPI e avvio normale PASS sullo stesso eseguibile.\n'
 'Checkpoint:finish_universe_saves.py;check_universe_saves.py/check_universe_regressions.py/check_universe_boundaries.py/P529-SAVE-FORMAT.md. Non eseguire finalizzatori precedenti da soli.\n'
 'Prossimo studio:P522-SAVE-PLAN.md/P522-NATIVE-AUDIT.md eprobe_p522_save.py;18sprite,2locali,poll200ms eanimazioni attive;126osservazioni diagnostiche conservate. Serve contrattoesplicito del lavoro ricorrente;nessunsupportoP522salvataggi giaimplementato.\n'
 'Diciannove scene con salvataggi verificati non sono una percentuale globale. Restano altri salvataggi,tipografia aiuto e verifica audiovisiva manuale integrale. Avvio:Avvia-Astronomica.cmd;userdata/astronomica intatti.\n\n')
p=r/'NEXT-STEPS.md';s=p.read_text();p.write_text(heading+s if not s.startswith('# Ripresa: salvataggi universo') else s)
Path('AI_MODEL_CHECKPOINT.md').write_text('# Astronomica: checkpoint AI,21 ottobre2026\n\n'+model+'\n\n'+heading+'Vincoli:originali D:/astro,solo cleanroom dal13settembre2026,niente tentativi esclusi o prototipi. Modello invariato. Controllare entrambe le quote e fermarsi vicino1%limitante;nessun acquisto/riscatto reset.\n')
p=r/'P529-SAVE-FORMAT.md';s=p.read_text();start=s.index('The native payload');s='# P529 universe saves, version15\n\nImplemented and verified21 October2026; see evidence/universe-saves-validation.json. Native WASAPI and the complete compatible suite pass on the same executable.\n\n'+s[start:];s=s.replace('Natural real-time final-frame presentation,\nWASAPI, official integration and broader manual gameplay require separate work.','Native WASAPI and official integration pass with the full same-build suite. Natural real-time final-frame save boundaries and broader manual gameplay remain unverified.');p.write_text(s)
p=r/'P529-SAVE-PLAN.md';s=p.read_text();note='## Verified settled save support,21 October2026\n\nVersion15 is implemented and verified; see P529-SAVE-FORMAT.md and evidence/universe-saves-validation.json. The original inventory below remains research history.\n\n';p.write_text(s if s.startswith(note) else note+s)
note=f'\n\n## P529 universe saves,21 October2026\n\nVersion15 preserves original movie and readout history independently of selector and attempted segment, plus all eleven sprites, four locals, mask, dormant custom17 and comet phase. {proof["boundaries"]} exact round trips/successors and physical slot14 in a fresh process pass. All3684 truncations,3684 corruptions and{proof["invalid_states"]} checksummed invalid states reject atomically. Original253-frame reconstruction, zero-frame history, natural voice completion, Music restart and the full native WASAPI regression pass on the same build.\n'
for name in ('README.md','SAVE-RESEARCH.md'):
 p=r/name;s=p.read_text();p.write_text(s if '## P529 universe saves,21 October2026' in s else s+note)
for name in ('record_save_coverage.py','refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(w/name)],check=True)
(r/'RUN-IN-PROGRESS.md').write_text('P529 v15 verified21October2026. Targeted/fresh-process/independent MOV audit/prior-slot and complete same-build native WASAPI suite plus launcher PASS. No tests running. Follow NEXT-STEPS.md/AI_MODEL_CHECKPOINT.md; newest finisher finish_universe_saves.py.\n')
print('P529 v15 universe save checkpoint PASS')
