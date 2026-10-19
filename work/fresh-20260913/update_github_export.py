"""Refresh the existing reviewed source-only export after checkpoint validation."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path('publish/scummvm-astronomica')
subprocess.run([sys.executable,'work/fresh-20260913/verify_development_evidence.py'],check=True)
assert subprocess.check_output(['git','-C',str(root),'remote','get-url','origin'],text=True).strip()=='https://github.com/HGWells2001/scummvm-astronomica.git'
manifest=json.loads((root/'SOURCE-MANIFEST.json').read_text())
ignore=root/'.gitignore';rules=ignore.read_text()
for rule in ('!outputs/astronomica-cleanroom/astronomica-play.ini','userdata/'):
    if rule not in rules.splitlines():rules+=rule+'\n'
ignore.write_text(rules)
# Only refresh paths already in the reviewed export. Do not add game media,
# binaries, saves or the full workspace through a recursive wildcard copy.
for name in manifest['sha256']:
    if name.startswith(('outputs/astronomica-cleanroom/','work/fresh-20260913/')):
        src=Path(name); assert src.is_file(),name
        shutil.copyfile(src,root/name)
for name in ('work/fresh-20260913/finish_help_keyboard.py','work/fresh-20260913/update_github_export.py','outputs/astronomica-cleanroom/GITHUB-PUBLISH.md','outputs/astronomica-cleanroom/P508-SAVE-PLAN.md',
 'work/fresh-20260913/check_p508_saves.py','work/fresh-20260913/finish_p508_saves.py','outputs/astronomica-cleanroom/probe_p508_save.py',
 'work/fresh-20260913/check_p505_saves.py','work/fresh-20260913/finish_p505_saves.py','outputs/astronomica-cleanroom/probe_p505_save.py',
 'work/fresh-20260913/check_question_regressions.py',
 'outputs/astronomica-cleanroom/P505-SAVE-FORMAT.md',
 'work/fresh-20260913/record_save_coverage.py','outputs/astronomica-cleanroom/evidence/native-save-coverage.json',
 'AI_MODEL_CHECKPOINT.md',
 'Avvia-Astronomica.cmd','outputs/astronomica-cleanroom/astronomica-play.ini','outputs/astronomica-cleanroom/LOCAL-PLAY.md','outputs/astronomica-cleanroom/bin/Avvia-Astronomica.cmd',
 'outputs/astronomica-cleanroom/evidence/local-launcher-validation.json','outputs/astronomica-cleanroom/evidence/local-launcher-startup.log',
 'work/fresh-20260913/check_local_launcher.py','work/fresh-20260913/finish_local_launcher.py',
 'outputs/astronomica-cleanroom/probe_variant_saves.py','outputs/astronomica-cleanroom/evidence/variant-save-original.json',
 'outputs/astronomica-cleanroom/PRESENTATION-RESEARCH.md',
 'outputs/astronomica-cleanroom/AUDIO-CHANNELS.md',
 'work/fresh-20260913/check_audio_channels.py','work/fresh-20260913/check_audio_channel_regressions.py','work/fresh-20260913/finish_audio_channels.py',
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('audio-channels-validation.json','audio-channels.log','audio-channels-proof.json')],
 'work/fresh-20260913/check_presentation.py','work/fresh-20260913/check_presentation_regressions.py','work/fresh-20260913/finish_presentation.py',
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('presentation-validation.json','presentation.log','p526-previous-slot.log','p526-previous-slot-proof.json')],
 'outputs/astronomica-cleanroom/P528-SAVE-PLAN.md','outputs/astronomica-cleanroom/probe_p528_save.py','outputs/astronomica-cleanroom/evidence/p528-save-original.json',
 'outputs/astronomica-cleanroom/probe_p528_answer_states.py','outputs/astronomica-cleanroom/evidence/p528-answer-states.json',
 'outputs/astronomica-cleanroom/probe_p528_settled_graph.py','outputs/astronomica-cleanroom/evidence/p528-settled-graph.json',
 'outputs/astronomica-cleanroom/P528-SAVE-FORMAT.md','work/fresh-20260913/check_p528_saves.py','work/fresh-20260913/check_p528_regressions.py','work/fresh-20260913/finish_p528_saves.py',
 'outputs/astronomica-cleanroom/P530-SAVE-PLAN.md','outputs/astronomica-cleanroom/probe_p530_save.py','outputs/astronomica-cleanroom/evidence/p530-save-original.json',
 'outputs/astronomica-cleanroom/P530-SAVE-FORMAT.md','outputs/astronomica-cleanroom/probe_p530_orders.py','outputs/astronomica-cleanroom/evidence/p530-orders-original.json',
 'work/fresh-20260913/check_p530_saves.py','work/fresh-20260913/check_p530_regressions.py','work/fresh-20260913/finish_p530_saves.py',
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p530-saves-validation.json','p530-save-proof.json','p530-saves-runtime.log','p530-saves-startup.log','p528-previous-slot.log','p528-previous-slot-proof.json')],
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p528-saves-validation.json','p528-save-proof.json','p528-saves-runtime.log','p528-saves-startup.log')],
 'work/fresh-20260913/check_p526_saves.py','work/fresh-20260913/check_p526_boundaries.py','work/fresh-20260913/check_p526_regressions.py','work/fresh-20260913/finish_p526_saves.py','outputs/astronomica-cleanroom/P526-SAVE-FORMAT.md',
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p526-saves-validation.json','p526-save-proof.json','p526-saves-runtime.log','p526-saves-startup.log','p526-native-save-boundaries.json','p526-native-save-boundaries.log','p524-previous-slot.log','p524-previous-slot-proof.json')],
 'outputs/astronomica-cleanroom/P526-SAVE-PLAN.md','outputs/astronomica-cleanroom/probe_p526_save.py','outputs/astronomica-cleanroom/evidence/p526-save-original.json',
 'outputs/astronomica-cleanroom/P524-SAVE-FORMAT.md','work/fresh-20260913/check_p524_saves.py','work/fresh-20260913/check_p524_regressions.py','work/fresh-20260913/finish_p524_saves.py','outputs/astronomica-cleanroom/evidence/p524-saves-validation.json','outputs/astronomica-cleanroom/evidence/p524-save-proof.json','outputs/astronomica-cleanroom/evidence/p524-saves-runtime.log','outputs/astronomica-cleanroom/evidence/p524-saves-startup.log','outputs/astronomica-cleanroom/evidence/p519-previous-slot.log','outputs/astronomica-cleanroom/evidence/p519-previous-slot-proof.json',
 'outputs/astronomica-cleanroom/P524-SAVE-PLAN.md','outputs/astronomica-cleanroom/probe_p524_save.py','outputs/astronomica-cleanroom/evidence/p524-save-original.json',
 'outputs/astronomica-cleanroom/P519-SAVE-FORMAT.md','work/fresh-20260913/check_p519_saves.py','work/fresh-20260913/check_p519_regressions.py','work/fresh-20260913/finish_p519_saves.py',
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p519-saves-validation.json','p519-save-proof.json','p519-saves-runtime.log','p519-saves-startup.log','p505-previous-slot.log','p505-previous-slot-proof.json')],
 'outputs/astronomica-cleanroom/probe_p519_save.py','outputs/astronomica-cleanroom/P519-SAVE-PLAN.md','outputs/astronomica-cleanroom/evidence/p519-save-original.json',
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p508-previous-slot.log','p508-previous-slot-proof.json')],
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p505-save-original.json','p505-saves-validation.json','p505-save-proof.json','p505-saves-runtime.log','p505-saves-startup.log')],
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p508-save-original.json','p508-saves-validation.json','p508-save-proof.json','p508-saves-runtime.log','p508-saves-startup.log')]):
    (root/name).parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(name,root/name)
m=json.loads(Path('outputs/astronomica-cleanroom/evidence/development-validation.json').read_text())
p=root/'SCUMMVM_BASE.json';j=json.loads(p.read_text())
j.update(engine_sha256=m['engine_sha256'],validated_executable_sha256=m['exe_sha256']);p.write_text(json.dumps(j,indent=2)+'\n')
p=root/'README.md';s=p.read_text().replace('on 13 October 2026','on 15 October 2026').replace('on 14 October 2026','on 15 October 2026')
s=s.replace('Native ScummVM saves support settled exploration screens.','Native ScummVM saves support settled exploration screens and P508 question boundaries. P508 continuation tests cover 63 boundaries, 291 answer steps and fresh-process slot loading; ambient music restarts from its beginning.')
s=s.replace('Arbitrary mid-puzzle saves,','Saving during the other puzzles,')
if 'P505 continuation tests' not in s:
    s=s.replace('and P508 question boundaries.', 'and P505/P508 question boundaries. P505 continuation tests cover 38 boundaries and successor states, hover restoration, corrupt payload rejection and fresh-process slot loading.')
if 'PageUp/PageDown/Home/End' not in s:
    s=s.replace('- Help checks cover', '- PageUp/PageDown/Home/End scroll the native help reader; all 781 articles pass keyboard navigation and boundary checks.\n- Help checks cover')
if 'P519 v5' not in s:
    s=s.replace('and P505/P508 question boundaries.', 'and P505/P508 question boundaries. P519 v5 saves idle selections and partial solutions, with 74 gameplay comparisons, 30 image compositions and fresh-process continuation verified.')
s=s.replace('on 15 October 2026','on 16 October 2026')
p524_note='P524 v6 saves question boundaries, including the running Triton animation and mentor return. Tests cover 72 round trips, 48 animation boundary cases and fresh-process continuation.'
s=s.replace('\n'+p524_note+'\n','\n')
if '- '+p524_note not in s:
    s=s.replace('- Automatically verified routes', '- '+p524_note+'\n- Automatically verified routes')
if 'native-save-coverage.json' not in s:
    s=s.replace('- Automatically verified routes', '- [Measured save coverage](outputs/astronomica-cleanroom/evidence/native-save-coverage.json) records four supported puzzle scenes (P505, P508, P519, P524), plus exploration. This is not a whole-game completion percentage.\n- Automatically verified routes')
s=s.replace('on 16 October 2026','on 18 October 2026')
s=s.replace('on 18 October 2026','on 19 October 2026')
if 'Avvia-Astronomica.cmd' not in s:
    s=s.replace('- Automatically verified routes','- The workspace entry point [Avvia-Astronomica.cmd](Avvia-Astronomica.cmd) uses the current local build and keeps personal preferences/saves separate from verification slots. The default template passes normal P1 startup; see [local play](outputs/astronomica-cleanroom/LOCAL-PLAY.md).\n- Automatically verified routes')
if 'P526 v7' not in s:
    s=s.replace('- Automatically verified routes','- P526 v7 saves stopped orbital experiments, retaining animation phases, render positions and hover. 686 round trips include 216 animation cases and 432 synthetic phase/answer comparisons.\n- Automatically verified routes')
s=s.replace('four supported puzzle scenes (P505, P508, P519, P524)','five supported puzzle scenes (P505, P508, P519, P524, P526)')
s=s.replace('five supported puzzle scenes (P505, P508, P519, P524, P526)','six supported puzzle scenes (P505, P508, P519, P524, P526, P528)')
s=s.replace('six supported puzzle scenes (P505, P508, P519, P524, P526, P528)','seven supported puzzle scenes (P505, P508, P519, P524, P526, P528, P530)')
if 'P530 v9' not in s:
    s=s.replace('- Automatically verified routes','- P530 v9 preserves partial component assembly, the prior-round picture, RNG and the original unchanged completion counter; five scenarios per round and all25 pictures pass native continuation tests.\n- Automatically verified routes')
if 'P528 v8' not in s:
    s=s.replace('- Automatically verified routes','- P528 v8 retains partial eclipses and original image history; 160 reachable abstract states, 640 continuations, full480-row pixels and fresh-process completion pass.\n- Automatically verified routes')
if 'Ordinary presentation preserves all 640x480' not in s:
    s=s.replace('- Automatically verified routes','- Ordinary presentation preserves all 640x480 original pixels. The diagnostic strip is opt-in; twelve complete-scene checks and 855 original P528 picture pixels pass.\n- Automatically verified routes')
p.write_text(s.rstrip()+'\n')
if 'Looping WAVs follow the Music control' not in s:
    s=s.replace('- Automatically verified routes','- Looping WAVs follow the Music control; foreground WAVs retain Effects. Six scenes pass with Music muted at volume zero, original controls restored and twelve WAV hashes unchanged.\n- Automatically verified routes')
    p.write_text(s.rstrip()+'\n')
manifest['date']='2026-10-19'
manifest['sha256']={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(root.rglob('*')) if p.is_file()
                   and not {'.git','__pycache__','userdata'}.intersection(p.parts) and p.name!='SOURCE-MANIFEST.json'}
(root/'SOURCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
subprocess.run([sys.executable,str(root/'tools/verify_export.py')],check=True)
print('Source-only export refreshed; review git diff before commit/push')
