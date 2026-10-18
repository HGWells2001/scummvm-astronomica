"""Record full-frame presentation after the same build passes all regressions."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913');exe=work/'build/Releasex64/scummvm.exe'
names=['presentation.log','p526-previous-slot.log','p526-boundaries.log','runtime.log','help.log','legacy.log','saves.log','saves-startup.log']
for scene in (505,508,519,524,526):names += [f'p{scene}-saves.log',f'p{scene}-saves-startup.log',f'p{scene}-previous-slot.log']
for name in set(names):
 p=work/name;s=p.read_text();assert p.stat().st_mtime>exe.stat().st_mtime,name
 assert 'FAIL' not in s and 'Log closed successfully' in s,name
assert 'full-height presentation: PASS (12 scenes, 855 original P528 pixels, optional strip and recovery)' in (work/'presentation.log').read_text()
assert 'Astronomica script verification: PASS' in (work/'runtime.log').read_text()
assert json.loads((work/'p526-previous-slot-proof.json').read_text())['unchanged']
for name in ('presentation.log','p526-previous-slot.log','p526-previous-slot-proof.json'):
 shutil.copyfile(work/name,root/'evidence'/name)
validation=dict(date='2026-10-18',status='PASS',exe_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),scene_count=12,scenes=[0,1,29,103,425,505,508,519,524,526,528,537],frame_width=640,frame_height=480,
 original_p528_pixels_checked=855,source_nonblack_pixels=204,debug_overlay_default=False,debug_overlay_option='astronomica_debug_overlay',optional_overlay=True,recovery_after_disable=True,
 compatibility='Existing versions1-7 and prior-build v3-v7 slots tested; no save format changes',full_suite=True,
 limitations=['Automated pixel/state/audio verification; no full manual audiovisual playthrough','Legacy screen fingerprints still use the original 456-row region; this presentation test explicitly checks 480 rows'])
(root/'evidence/presentation-validation.json').write_text(json.dumps(validation,indent=2))
old_next=(root/'NEXT-STEPS.md').read_text()
p=subprocess.run([sys.executable,str(work/'finish_p526_saves.py')],capture_output=True,text=True)
if p.returncode:print(p.stdout+p.stderr);p.check_returncode()
print(p.stdout[-400:]);(root/'NEXT-STEPS.md').write_text(old_next)
p=root/'PRESENTATION-RESEARCH.md';s=p.read_text().replace('Status: observed issue; correction not implemented yet.','Status: corrected and verified, 18 October 2026. See evidence/presentation-validation.json.');s+='\n\nImplemented: ordinary presentation preserves all480 rows. Set astronomica_debug_overlay=true only for the diagnostic strip. Twelve complete scenes,855 original GE_S1 pixels, opt-in display and recovery pass. All compatible saves and the WASAPI suite pass on the same build.\n' if 'Implemented: ordinary presentation' not in s else '';p.write_text(s)
note=('\n\n## Full original frame, 18 October 2026\n\n'
 'Ordinary presentation now preserves all 640x480 original pixels. The diagnostic strip is opt-in via astronomica_debug_overlay. '
 'The old strip covered rows 456-479, including five rows of a P528 picture. '
 'Twelve scene comparisons, 855 original picture pixels, optional-strip activation and restoration pass. '
 'All existing v1-v7 saves, prior-build v3-v7 slots, help/import and full WASAPI regressions pass on the same executable. '
 'Existing legacy fingerprints intentionally retain their 456-row scope; the new presentation test checks all 480 rows.\n')
for name in ('README.md','SAVE-RESEARCH.md'):
 p=root/name;s=p.read_text()
 if '## Full original frame, 18 October 2026' not in s:s+=note
 p.write_text(s)
heading=('# Ripresa: fotogramma originale completo, 18 ottobre 2026\n\n'
 'Presentazione 640x480 senza barra diagnostica predefinita: 12 scene e 855 pixel originali P528 PASS; debug opzionale e ripristino PASS.\n'
 'P526: 686 ripristini; compatibilita v1-v7, precedenti slot v3-v7, import, aiuto e suite WASAPI PASS sullo stesso eseguibile.\n'
 'Checkpoint: finish_presentation.py. Test: check_presentation.py e check_presentation_regressions.py.\n'
 'Prossimo: P528-SAVE-PLAN.md, verifica audiovisiva manuale e tipografia aiuto. Non rieseguire finalizzatori storici.\n'
 'P528: conservare la riga della precedente Luna alta; 1728 storie e 48 passi ciclici verificati, salvataggi nativi ancora assenti.\n'
 'Nessuna percentuale globale attendibile. Protocollo: AI_MODEL_CHECKPOINT.md.\n\n')
p=root/'NEXT-STEPS.md';s=p.read_text()
if not s.startswith('# Ripresa: fotogramma originale completo'):s=heading+s
p.write_text(s)
p=Path('AI_MODEL_CHECKPOINT.md');s=p.read_text().replace('Prossimo: PRESENTATION-RESEARCH.md, poi P528-SAVE-PLAN.md','Prossimo: P528-SAVE-PLAN.md')
s+='\nPresentazione completa verificata: 640x480, 12 scene, 855 pixel originali P528, barra diagnostica opzionale. Compatibilita v1-v7 e suite WASAPI PASS. Checkpoint attuale finish_presentation.py; driver check_presentation.py e check_presentation_regressions.py. Variante/livello AI invariati e non verificabili nel client; nessuna richiesta di cambio.\n';p.write_text(s)
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('Full-frame presentation verified 18 October 2026. Twelve scenes,855 original pixels, optional debug/recovery, all v1-v7 saves, prior-build slots, import/help and WASAPI suite PASS on the same executable. No tests running. See NEXT-STEPS.md and AI_MODEL_CHECKPOINT.md.\n')
print('Full-frame presentation checkpoint PASS')
