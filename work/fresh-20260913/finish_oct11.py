"""Guarded full regression and checkpoint for P29 and intro-clock diagnosis."""
from pathlib import Path
import json, re, shutil, subprocess, sys
root=Path('outputs/astronomica-cleanroom');work=Path('work/fresh-20260913')
try:
    subprocess.run([sys.executable,str(work/'check_world29.py')],check=True)
    target=(work/'world29.log').read_text()
    assert 'P29 movie verification: PASS' in target and 'FAIL' not in target
    intro=json.loads((work/'intro-live-real-audio-result.json').read_text())
    text=(work/'intro-live-real-audio.log').read_text()
    assert intro['path']==[2,3,4,27] and intro['natural_ends']==1
    assert 'Using SDL Audio Driver "wasapi"' in text
    last=re.findall(r'movie closed while playing: \d+ frames, time (\d+), end (\d+)',text)
    assert len(last)==1 and 69500<=int(last[0][0])<=70500 and int(last[0][1])==71100
    subprocess.run([sys.executable,str(work/'runtime_test.py'),'--real-audio'],check=True)
    log=(work/'runtime.log').read_text()
    assert 'FAIL' not in log and 'Astronomica script verification: PASS' in log
    assert 'P29 movie verification: PASS' in log and 'Using SDL Audio Driver "wasapi"' in log
    for name in ('intro-live-real-audio-result.json','intro-live-real-audio.log','sdl-dummy-clock.json','world29.log'):
        shutil.copyfile(work/name,root/'evidence'/name)
    (root/'evidence/world29-validation.json').write_text(json.dumps(dict(status='PASS',place=29,
        both_control_orders=True,duplicate_controls=True,decode_positions=4,redraw=True,
        timed_lock_release=True,no_replay=True,context_guard=True,full_suite=True,
        manual_confirmation=False,continuous_movie=False,
        cursor_note='Native cursor constrained below movie; automated test checks state, no manual pointer review'),indent=2))
    p=root/'evidence/intro-validation.json';d=json.loads(p.read_text())
    d.update(continuous_intro=True,headless=True,manual_confirmation=False,
        audio_clock_diagnosis='SDL dummy independently advances 9.66s in12s; WASAPI P2 ends naturally and P4 reaches69.994s at70s deadline',
        timing_note='Original P4 script changes scene at70s before71.1s movie end',
        real_audio_result=intro)
    p.write_text(json.dumps(d,indent=2))
    note=('\n\n## P29 and audio clock, 11 October 2026\n\n'
        'P29 original FLAT29.MOV integrated with both control orders, repeat-control guards, '
        'four decoded positions, redraw at65000ms, cursor release and delayed input unlock. '
        'Custom29 rebuilds background/sprites without stopping the movie. Original evidence '
        'in probe_world_interactions.py includes final display callback and cursor flag consumer. '
        'Native cursor movement is constrained below the movie; manual pointer review remains pending. '
        'World scenes82/222/231 remain unsupported.\n'
        'The Oct10 intro timing discrepancy was reproduced in SDL dummy without game/video: '
        '9.6595 audio seconds in12 wall seconds. On Windows WASAPI, P2 ends naturally before '
        'the208s transition and P4 advances69.994s at the70s transition. No production movie '
        'clock change was required. Real-audio intro proof retains its exact pre-P29 executable '
        'hash; the subsequent full native regression uses WASAPI and passes on the new build. '
        'Manual audiovisual review and full-game completion remain unverified.\n')
    for name in ('README.md','INTERPRETER.md','P409-RESEARCH.md'):
        p=root/name
        if b'## P29 and audio clock, 11 October 2026' not in p.read_bytes():
            with p.open('ab') as f:f.write(note.encode('ascii'))
    p=root/'NEXT-STEPS.md';s=p.read_text();a=s.index('PRIORITA: P2');b=s.index('Restano filmati esplorazione',a)
    s=s[:a]+('Scarto intro risolto: artefatto SDL dummy, riprodotto senza gioco.\n'
        'WASAPI: P2 termina naturalmente; P4 avanza69.994s in70s. Nessuna modifica al clock.\n'
        'P29 filmato interattivo integrato: due ordini, clic ripetuti, quattro posizioni video,\n'
        'ridisegno, rilascio cursore e sblocco input verificati; suite completa WASAPI PASS.\n'
        'Prossimo: filmati mondo82/222/231; verificare restart del controller originale per222.\n'
        'P29: playback continuo e prova manuale del cursore ancora da verificare.\n'
        'Prove:check_world29.py, check_intro_live.py --real-audio, check_sdl_dummy_clock.py.\n')+s[b:]
    s=s.replace('10 ottobre 2026','11 ottobre 2026').replace('finish_oct10.py','finish_oct11.py');p.write_text(s,encoding='utf-8')
    for name in ('refresh_research_evidence.py','save_development_evidence.py','verify_development_evidence.py'):
        subprocess.run([sys.executable,str(work/name)],check=True)
    (root/'RUN-IN-PROGRESS.md').write_text('Oct11 native full suite and checkpoint PASS. P29 integrated; intro clock discrepancy isolated to SDL dummy. See NEXT-STEPS.md.\n')
    print('October11 checkpoint PASS')
except Exception:
    (root/'RUN-IN-PROGRESS.md').write_text('Oct11 full suite/checkpoint failed; inspect finish_oct11.py and runtime.log before resuming.\n')
    raise
