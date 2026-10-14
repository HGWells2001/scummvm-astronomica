"""Record a completed real-time intro run without changing native coverage."""
from pathlib import Path
import json, hashlib, shutil, subprocess, sys
root = Path('outputs/astronomica-cleanroom')
work = Path('work/fresh-20260913')
result = json.loads((work / 'intro-live-result.json').read_text())
assert result['status'] == 'PASS: real main loop reached exploration'
assert result['path'] == [2, 3, 4, 27] and not result['native_verify_mode']
assert result['wall_seconds'] >= 340
assert result['exe_sha256'] == hashlib.sha256((work / 'build/Releasex64/scummvm.exe').read_bytes()).hexdigest()
for name in ('intro-live-result.json', 'intro-live.log'):
    shutil.copyfile(work / name, root / 'evidence' / name)
p = root / 'evidence/intro-validation.json'
d = json.loads(p.read_text())
d.update(live_main_loop=True, continuous_intro=False, headless=True,
         live_result=result, manual_confirmation=False,
         timing_note='Scene transitions pass, but P2 media advanced only about 156s at the 208s scene deadline. Investigate headless playback clock/performance before claiming audiovisual continuity.')
p.write_text(json.dumps(d, indent=2))
p = root / 'NEXT-STEPS.md'
s = p.read_text().replace('Prossimo:playback continuo introduzione e filmati mondo29/82/222/231.',
    'Percorso introduzione P2->P3->P4->P27: PASS nel normale ciclo del motore.\n'
    'PRIORITA: P2 avanza solo circa156s video in208s reali nel test headless.\n'
    'Verificare clock audio/performance e continuita audiovisiva prima dei filmati mondo.\n'
    'Poi filmati mondo29/82/222/231; vedere evidence/world-interactions.json.\n'
    'Custom29 chiama UpdateGame/SWUpdateSpriteWorld; verificare blit e cursore prima di integrare.')
p.write_text(s, encoding='utf-8')
note = ('\n\nReal-time introduction, 10 October 2026: PASS in the normal native main loop, '
        'with entry scripts and audio enabled, headless. P2 -> P3 -> P4 -> P27 '
        'completed without accelerated time. This verifies scene progression only. '
        'P2 media reached only about156s at the208s scene deadline, closing while '
        'playing. Investigate headless clock/performance; audiovisual continuity '
        'is NOT validated. Manual audiovisual review remains pending.\n')
for name in ('README.md', 'INTERPRETER.md', 'P409-RESEARCH.md'):
    p = root / name
    if b'Real-time introduction, 10 October 2026' not in p.read_bytes():
        with p.open('ab') as f:
            f.write(note.encode('ascii'))
for name in ('refresh_research_evidence.py', 'save_development_evidence.py', 'verify_development_evidence.py'):
    subprocess.run([sys.executable, str(work / name)], check=True)
(root / 'RUN-IN-PROGRESS.md').write_text('Native full suite and intro scene progression PASS. P2 playback timing discrepancy needs investigation; see NEXT-STEPS.md.\n')
print('Real-time introduction checkpoint PASS')
