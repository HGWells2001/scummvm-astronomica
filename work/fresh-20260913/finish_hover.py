"""Record the completed hover build and regression; do not rerun obsolete finalizers."""
from pathlib import Path
import json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
log=(work/'runtime.log').read_text();target=(work/'hover.log').read_text()
for text in (log,target):
 assert 'FAIL' not in text
 assert 'hover verification: PASS; 32 targets, 4 sounds, 256 dispatch cases' in text
 assert 'Hover original overlap and sound order: PASS' in text
 assert 'Log closed successfully' in text
assert 'Astronomica script verification: PASS' in log
assert (work/'build/Releasex64/scummvm.exe').stat().st_mtime<(work/'hover.log').stat().st_mtime<(work/'runtime.log').stat().st_mtime
for src in (root/'engine/astronomica').glob('*'):
 if src.suffix in ('.h','.cpp'):
  assert src.read_bytes()==(work/'scummvm/engines/astronomica'/src.name).read_bytes()
  assert src.stat().st_mtime<(work/'build/Releasex64/scummvm.exe').stat().st_mtime
shutil.copyfile(work/'hover.log',root/'evidence/hover-runtime.log')
(root/'evidence/hover-validation.json').write_text(json.dumps(dict(status='PASS',places=[1,505,519,526],paired_targets=32,
 original_dispatch_cases=256,native_dispatch_cases=256,sounds=[11,12,13,14],original_overlap_order=True,
 queued_not_immediate=True,hidden_sprite_hits=True,stationary_no_repeat=True,click_lock_independent=True,
 condition_transitions=True,scene_reset=True,full_suite=True,audio_backend='Windows WASAPI',manual_confirmation=False),indent=2))
p=root/'NEXT-STEPS.md';s=p.read_text();start=s.find('Prossimo: integrare hover');start=s.index('Hover integrato in P1/P505') if start<0 else start;end=s.index('Ricerca:probe_movie_controller.py',start)
s=s[:start]+('Hover integrato in P1/P505/P519/P526:32 coppie, quattro suoni,256 casi,\n'
 'sovrapposizione e ordine audio, condizioni, reset e suite completa PASS.\n'
 'Leggere HOVER-RESEARCH.md e HELP-RESEARCH.md.\n'
 'Prossimo: visualizzatore aiuto nativo/custom22. HLP decodificato in ricerca:\n'
 '41 stream,1701 frasi,68 blocchi,2117 record e782 titoli verificati. Mancano\n'
 'formattazione, hyperlink, bitmap e interfaccia; non dichiarare aiuto integrato.\n'
 'Custom33 usa gamestat TESTUALE, non la routine binaria:15 roundtrip e1088\n'
 'casi flag resume PASS. Import originale non implementato; risolvere il clock\n'
 'del countdown prima di importare salvataggi attivi. Restano save nei puzzle\n'
 'e percorso integrale manuale. Nessuna percentuale globale attendibile.\n')+s[end:]
s=s.replace('manuale, hover, aiuto Windows','manuale, aiuto Windows').replace('Checkpoint:finish_world_movies.py','Checkpoint:finish_hover.py')
p.write_text(s)
note=('\n\n## Hover checkpoint, 11 October 2026\n\n'
 'Native hover now handles32 original paired targets in P1/P505/P519/P526. '
 'All targets, four P505 sounds, stationary suppression, original overlap order, '
 'conditional branches, click-lock independence and scene resets pass.256 native '
 'dispatch cases agree with the original dispatch study. Build and full WASAPI '
 'regression PASS. Help file research decodes1701 phrases and2117 records with '
 'exact length checks;782 titles match the independent index. Native help UI '
 'remains unimplemented. Custom33 reads text gamestat, distinct from the binary '
 'routine studied earlier. See HOVER-RESEARCH.md and HELP-RESEARCH.md. '
 'No manual audiovisual or complete-playthrough claim is made.\n')
for name in ('README.md','INTERPRETER.md'):
 p=root/name
 if b'## Hover checkpoint, 11 October 2026' not in p.read_bytes():
  with p.open('ab') as f:f.write(note.encode('ascii'))
for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
 subprocess.run([sys.executable,str(work/name)],check=True)
(root/'RUN-IN-PROGRESS.md').write_text('Hover build,32 targets,4 sounds,256 dispatch cases,overlap and full suite PASS. Checkpoint verified. Original help/resume research saved; native help not implemented. See NEXT-STEPS.md.\n')
print('Hover checkpoint PASS')
