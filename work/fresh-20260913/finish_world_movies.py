"""Run native world-movie checks and full regression before recording evidence."""
from pathlib import Path
import json,shutil,subprocess,sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
try:
    subprocess.run([sys.executable,str(root/'probe_world_interactions.py'),'D:/astro','--out',str(root/'evidence/world-interactions.json')],check=True)
    subprocess.run([sys.executable,str(work/'check_world_movies.py')],check=True)
    target=(work/'world-movies.log').read_text()
    assert 'FAIL' not in target and 'world movies verification: PASS' in target
    for n in (29,82,222,231):assert f'P{n} world movie continuous: PASS' in target
    subprocess.run([sys.executable,str(work/'runtime_test.py'),'--real-audio'],check=True)
    log=(work/'runtime.log').read_text()
    assert 'FAIL' not in log and 'Astronomica script verification: PASS' in log
    assert 'world movies verification: PASS' in log
    shutil.copyfile(work/'world-movies.log',root/'evidence/world-movies-runtime.log')
    (root/'evidence/world-movies-validation.json').write_text(json.dumps(dict(status='PASS',
        places=[29,82,222,231],continuous_movies=[29,82,222,231],
        original_controller_boundary_cases=762,completed_movie_replay=True,in_range_resume=True,
        arm_toggle=True,unarmed_rejection=True,decoded_positions=4,timed_input_release=True,
        p222_sprite_animation_and_exit=True,full_suite=True,manual_confirmation=False,
        audio_backend='Windows WASAPI',cursor_note='Cursor state verified; manual pointer review pending'),indent=2))
    p=root/'evidence/world29-validation.json';d=json.loads(p.read_text());d['continuous_movie']=True;p.write_text(json.dumps(d,indent=2))
    note=('\n\n## World movies82/222/231, 11 October 2026\n\n'
        'Original MOV files now play in world panels82,222,231. Controller replay is '
        'scoped to supported world movies: completed playback seeks to0 before play; '
        'in-range playback preserves position. Original QCMC control-flow research '
        'executes762 boundary cases. Native tests cover arm toggles, unarmed rejection, '
        'four decoded positions, input/cursor release deadlines, P222 replay and in-range '
        'resume, P222 two-second sprite animation and exit407. Continuous native playback '
        'passes for29/82/222/231 with WASAPI. Complete native regression PASS. '
        'No extra puzzle completion count is claimed. Manual audiovisual/pointer review '
        'and a complete game playthrough remain pending.\n')
    for name in ('README.md','INTERPRETER.md','P409-RESEARCH.md'):
        p=root/name
        if b'## World movies82/222/231, 11 October 2026' not in p.read_bytes():
            with p.open('ab') as f:f.write(note.encode('ascii'))
    p=root/'NEXT-STEPS.md';s=p.read_text();a=s.index('Prossimo: filmati mondo82/222/231.');b=s.index('Restano filmati esplorazione',a)
    s=s[:a]+('P82/P222/P231: filmati integrati; replay dopo fine e ripresa a meta verificati.\n'
        'P222: animazione sprite per2s e uscita407 PASS. Playback continuo29/82/222/231 PASS.\n'
        'Prossimo: inventario delle lacune effettive, aiuto Windows/custom22 e resume/custom33;\n'
        'restano salvataggi nei puzzle e percorso integrale manuale.\n'
        'Ricerca:probe_movie_controller.py,762 casi del ramo originale QCMC.\n'
        'Test:check_world_movies.py; suite completa runtime_test.py --real-audio.\n')+s[b:]
    s=s.replace('finish_oct11.py','finish_world_movies.py');p.write_text(s,encoding='utf-8')
    for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
        subprocess.run([sys.executable,str(work/name)],check=True)
    (root/'RUN-IN-PROGRESS.md').write_text('World movies29/82/222/231, replay, continuous playback and full suite PASS. Checkpoint verified; see NEXT-STEPS.md.\n')
    print('World movie checkpoint PASS')
except Exception:
    (root/'RUN-IN-PROGRESS.md').write_text('World movie validation/checkpoint failed. Inspect world-movies.log and runtime.log before resuming.\n')
    raise
