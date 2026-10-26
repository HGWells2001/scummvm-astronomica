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
 'outputs/astronomica-cleanroom/probe_p513_save.py','outputs/astronomica-cleanroom/evidence/p513-save-original.json','outputs/astronomica-cleanroom/P513-SAVE-FORMAT.md',
 'outputs/astronomica-cleanroom/probe_p513_cross_setting.py','outputs/astronomica-cleanroom/evidence/p513-cross-setting.json',
 'outputs/astronomica-cleanroom/probe_p517_save.py','outputs/astronomica-cleanroom/evidence/p517-save-original.json','outputs/astronomica-cleanroom/P517-SAVE-FORMAT.md',
 'outputs/astronomica-cleanroom/probe_p537_motion.py','outputs/astronomica-cleanroom/evidence/p537-motion-original.json',
 'outputs/astronomica-cleanroom/probe_p537_save.py','outputs/astronomica-cleanroom/evidence/p537-save-original.json','outputs/astronomica-cleanroom/P537-SAVE-PLAN.md',
 'outputs/astronomica-cleanroom/probe_builder_save.py','outputs/astronomica-cleanroom/evidence/builder-save-original.json','outputs/astronomica-cleanroom/BUILDER-SAVE-PLAN.md',
 'outputs/astronomica-cleanroom/probe_p529_save.py','outputs/astronomica-cleanroom/evidence/p529-save-original.json','outputs/astronomica-cleanroom/P529-SAVE-PLAN.md',
 'outputs/astronomica-cleanroom/P537-SAVE-FORMAT.md',
 'outputs/astronomica-cleanroom/P529-SAVE-FORMAT.md',
 'work/fresh-20260913/prepare_probe_audit.py','work/fresh-20260913/build_probe_audit.py','work/fresh-20260913/analyze_probe_audit.py',
 'outputs/astronomica-cleanroom/P522-NATIVE-AUDIT.md',
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p522-probe-boundaries.json', 'p522-probe-boundaries.log', 'p522-probe-audit-build-proof.json')],
 'outputs/astronomica-cleanroom/probe_p522_save.py','outputs/astronomica-cleanroom/evidence/p522-save-original.json','outputs/astronomica-cleanroom/P522-SAVE-PLAN.md',
 'work/fresh-20260913/check_universe_saves.py','work/fresh-20260913/check_universe_boundaries.py','work/fresh-20260913/check_universe_regressions.py','work/fresh-20260913/finish_universe_saves.py',
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('universe-saves-validation.json', 'universe-save-proof.json', 'universe-saves-runtime.log', 'universe-saves-startup.log', 'universe-boundaries-proof.json', 'universe-boundaries.log', 'rocket-previous-slot.log', 'rocket-previous-slot-proof.json')],
 'work/fresh-20260913/check_rocket_saves.py','work/fresh-20260913/check_rocket_boundaries.py','work/fresh-20260913/check_rocket_regressions.py','work/fresh-20260913/finish_rocket_saves.py',
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('rocket-saves-validation.json', 'rocket-save-proof.json', 'rocket-saves-runtime.log', 'rocket-saves-startup.log', 'rocket-boundaries.json', 'rocket-boundaries.log', 'builder-previous-slot.log', 'builder-previous-slot-proof.json')],
 'outputs/astronomica-cleanroom/BUILDER-SAVE-FORMAT.md',
 'work/fresh-20260913/check_p537_readout.py','work/fresh-20260913/check_builder_saves.py','work/fresh-20260913/check_builder_regressions.py','work/fresh-20260913/finish_builder_saves.py',
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p537-readout-proof.json', 'p537-readout-runtime.log', 'p537-readout-1.png', 'p537-readout-7.png', 'p537-readout-11.png', 'p537-readout-13.png', 'p537-motion-validation.json', 'builder-saves-validation.json', 'builder-save-proof.json', 'builder-saves-runtime.log', 'builder-saves-startup.log', 'p517-previous-slot.log', 'p517-previous-slot-proof.json')],
 'work/fresh-20260913/check_p517_saves.py','work/fresh-20260913/check_p517_regressions.py','work/fresh-20260913/finish_p517_saves.py','work/fresh-20260913/check_builder_boundaries.py',
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p517-saves-validation.json','p517-save-proof.json','p517-saves-runtime.log','p517-saves-startup.log','p513-previous-slot.log','p513-previous-slot-proof.json','builder-boundaries.json','builder-boundaries.log')],
 'work/fresh-20260913/check_p513_saves.py','work/fresh-20260913/check_p513_regressions.py','work/fresh-20260913/finish_p513_saves.py',
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p513-saves-validation.json','p513-save-proof.json','p513-saves-runtime.log','p513-saves-startup.log','variant-previous-slot.log','variant-previous-slot-proof.json')],
 'outputs/astronomica-cleanroom/VARIANT-SAVE-FORMAT.md',
 'work/fresh-20260913/check_variant_saves.py','work/fresh-20260913/check_variant_regressions.py','work/fresh-20260913/finish_variant_saves.py','work/fresh-20260913/check_save_entry_history.py',
 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('variant-saves-validation.json','variant-save-proof.json','variant-saves-runtime.log','variant-saves-startup.log','p530-previous-slot.log','p530-previous-slot-proof.json','save-entry-history.log','save-entry-history-proof.json','save-entry-history-before.log')],
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
probe_save_present=Path('outputs/astronomica-cleanroom/evidence/probe-saves-validation.json').is_file()
if probe_save_present:
    probe_paths=['outputs/astronomica-cleanroom/P522-SAVE-FORMAT.md',
                 'work/fresh-20260913/check_probe_saves.py','work/fresh-20260913/check_probe_regressions.py','work/fresh-20260913/finish_probe_saves.py',
                 *['outputs/astronomica-cleanroom/evidence/'+name for name in ('probe-saves-validation.json','probe-save-proof.json','probe-saves-runtime.log','probe-saves-startup.log','universe-previous-slot.log','universe-previous-slot-proof.json')]]
    for name in probe_paths:
        (root/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(name,root/name)
rendezvous_save_present=Path('outputs/astronomica-cleanroom/evidence/rendezvous-saves-validation.json').is_file()
p514_research_paths=['outputs/astronomica-cleanroom/'+name for name in ('P514-SAVE-PLAN.md','probe_p514_save.py','evidence/p514-save-original.json')]
if Path('outputs/astronomica-cleanroom/evidence/p514-save-original.json').is_file():
    for name in p514_research_paths:
        (root/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(name,root/name)
if rendezvous_save_present:
    rendezvous_paths=['outputs/astronomica-cleanroom/P514-SAVE-FORMAT.md',
                      *['work/fresh-20260913/'+name for name in ('check_rendezvous_saves.py','check_rendezvous_regressions.py','finish_rendezvous_saves.py')],
                      *['outputs/astronomica-cleanroom/evidence/'+name for name in ('rendezvous-saves-validation.json','rendezvous-save-proof.json','rendezvous-saves-runtime.log','rendezvous-saves-startup.log','probe-previous-slot.log','probe-previous-slot-proof.json')]]
    for name in rendezvous_paths:
        (root/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(name,root/name)
planet_save_present=Path('outputs/astronomica-cleanroom/evidence/planet-saves-validation.json').is_file()
if Path('outputs/astronomica-cleanroom/evidence/p518-save-original.json').is_file():
    for name in ('P518-SAVE-PLAN.md','probe_p518_save.py','evidence/p518-save-original.json'):
        source=Path('outputs/astronomica-cleanroom')/name
        (root/source).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,root/source)
if planet_save_present:
    planet_paths=['outputs/astronomica-cleanroom/P518-SAVE-FORMAT.md',
                  *['work/fresh-20260913/'+name for name in ('check_planet_saves.py','check_planet_regressions.py','finish_planet_saves.py')],
                  *['outputs/astronomica-cleanroom/evidence/'+name for name in ('planet-saves-validation.json','planet-save-proof.json','planet-saves-runtime.log','planet-saves-startup.log','rendezvous-previous-slot.log','rendezvous-previous-slot-proof.json')]]
    for name in planet_paths:
        (root/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(name,root/name)
p521_save_present=Path('outputs/astronomica-cleanroom/evidence/p521-saves-validation.json').is_file()
if Path('outputs/astronomica-cleanroom/evidence/p521-save-original.json').is_file():
    for name in ('P521-SAVE-PLAN.md','probe_p521_save.py','evidence/p521-save-original.json'):
        source=Path('outputs/astronomica-cleanroom')/name
        (root/source).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,root/source)
if p521_save_present:
    p521_paths=['outputs/astronomica-cleanroom/P521-SAVE-FORMAT.md',
                *['work/fresh-20260913/'+name for name in ('check_p521_saves.py','check_p521_regressions.py','finish_p521_saves.py')],
                *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p521-saves-validation.json','p521-save-proof.json','p521-saves-runtime.log','p521-saves-startup.log','planet-previous-slot.log','planet-previous-slot-proof.json')]]
    for name in p521_paths:
        (root/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(name,root/name)
p509_save_present=Path('outputs/astronomica-cleanroom/evidence/p509-saves-validation.json').is_file()
if Path('outputs/astronomica-cleanroom/evidence/p509-save-original.json').is_file():
    for name in ('P509-SAVE-PLAN.md','probe_p509_save.py','evidence/p509-save-original.json'):
        source=Path('outputs/astronomica-cleanroom')/name
        (root/source).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,root/source)
if p509_save_present:
    p509_paths=['outputs/astronomica-cleanroom/P509-SAVE-FORMAT.md',
                *['work/fresh-20260913/'+name for name in ('check_p509_saves.py','check_p509_regressions.py','finish_p509_saves.py')],
                *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p509-saves-validation.json','p509-save-proof.json','p509-saves-runtime.log','p509-saves-startup.log','p521-previous-slot.log','p521-previous-slot-proof.json')]]
    for name in p509_paths:
        (root/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(name,root/name)
p511_save_present=Path('outputs/astronomica-cleanroom/evidence/p511-saves-validation.json').is_file()
if Path('outputs/astronomica-cleanroom/evidence/p511-save-original.json').is_file():
    for name in ('P511-SAVE-PLAN.md','probe_p511_save.py','evidence/p511-save-original.json'):
        source=Path('outputs/astronomica-cleanroom')/name
        (root/source).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,root/source)
if p511_save_present:
    p511_paths=['outputs/astronomica-cleanroom/P511-SAVE-FORMAT.md',
                *['work/fresh-20260913/'+name for name in ('check_p511_saves.py','check_p511_regressions.py','finish_p511_saves.py')],
                *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p511-saves-validation.json','p511-save-proof.json','p511-saves-runtime.log','p511-saves-startup.log','p509-previous-slot.log','p509-previous-slot-proof.json')]]
    for name in p511_paths:
        (root/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(name,root/name)

p516_save_present=Path('outputs/astronomica-cleanroom/evidence/p516-saves-validation.json').is_file()
if Path('outputs/astronomica-cleanroom/evidence/p516-save-original.json').is_file():
    for name in ('P516-SAVE-PLAN.md','probe_p516_save.py','evidence/p516-save-original.json'):
        source=Path('outputs/astronomica-cleanroom')/name
        (root/source).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,root/source)
if p516_save_present:
    p516_paths=['outputs/astronomica-cleanroom/P516-SAVE-FORMAT.md',
                *['work/fresh-20260913/'+name for name in ('check_p516_saves.py','check_p516_regressions.py','finish_p516_saves.py')],
                *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p516-saves-validation.json','p516-save-proof.json','p516-saves-runtime.log','p516-saves-startup.log','p511-previous-slot.log','p511-previous-slot-proof.json')]]
    for name in p516_paths:
        (root/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(name,root/name)

p527_save_present=Path('outputs/astronomica-cleanroom/evidence/p527-saves-validation.json').is_file()
if Path('outputs/astronomica-cleanroom/evidence/p527-save-original.json').is_file():
    for name in ('P527-SAVE-PLAN.md','probe_p527_save.py','evidence/p527-save-original.json'):
        source=Path('outputs/astronomica-cleanroom')/name
        (root/source).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,root/source)
if p527_save_present:
    p527_paths=['outputs/astronomica-cleanroom/P527-SAVE-FORMAT.md',
                *['work/fresh-20260913/'+name for name in ('check_p527_saves.py','check_p527_regressions.py','finish_p527_saves.py')],
                *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p527-saves-validation.json','p527-save-proof.json','p527-saves-runtime.log','p527-saves-startup.log','p516-previous-slot.log','p516-previous-slot-proof.json')]]
    for name in p527_paths:
        (root/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(name,root/name)

p502_save_present=Path('outputs/astronomica-cleanroom/evidence/p502-saves-validation.json').is_file()
if Path('outputs/astronomica-cleanroom/evidence/p502-save-original.json').is_file():
    for name in ('P502-SAVE-PLAN.md','probe_p502_save.py','evidence/p502-save-original.json'):
        source=Path('outputs/astronomica-cleanroom')/name
        (root/source).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,root/source)
if p502_save_present:
    p502_paths=['outputs/astronomica-cleanroom/P502-SAVE-FORMAT.md',
                *['work/fresh-20260913/'+name for name in ('check_p502_saves.py','check_p502_regressions.py','finish_p502_saves.py')],
                *['outputs/astronomica-cleanroom/evidence/'+name for name in ('p502-saves-validation.json','p502-save-proof.json','p502-saves-runtime.log','p502-saves-startup.log','p527-previous-slot.log','p527-previous-slot-proof.json')]]
    for name in p502_paths:
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
s=s.replace('on 19 October 2026','on 21 October 2026').replace('on 20 October 2026','on 21 October 2026')
if 'Avvia-Astronomica.cmd' not in s:
    s=s.replace('- Automatically verified routes','- The workspace entry point [Avvia-Astronomica.cmd](Avvia-Astronomica.cmd) uses the current local build and keeps personal preferences/saves separate from verification slots. The default template passes normal P1 startup; see [local play](outputs/astronomica-cleanroom/LOCAL-PLAY.md).\n- Automatically verified routes')
if 'P526 v7' not in s:
    s=s.replace('- Automatically verified routes','- P526 v7 saves stopped orbital experiments, retaining animation phases, render positions and hover. 686 round trips include 216 animation cases and 432 synthetic phase/answer comparisons.\n- Automatically verified routes')
s=s.replace('four supported puzzle scenes (P505, P508, P519, P524)','five supported puzzle scenes (P505, P508, P519, P524, P526)')
s=s.replace('five supported puzzle scenes (P505, P508, P519, P524, P526)','six supported puzzle scenes (P505, P508, P519, P524, P526, P528)')
s=s.replace('six supported puzzle scenes (P505, P508, P519, P524, P526, P528)','seven supported puzzle scenes (P505, P508, P519, P524, P526, P528, P530)')
s=s.replace('seven supported puzzle scenes (P505, P508, P519, P524, P526, P528, P530)','fourteen supported puzzle scenes (P505, P506, P508, P513, P519, P524, P526, P528, P530-P535)')
s=s.replace('thirteen supported puzzle scenes (P505, P506, P508, P519, P524, P526, P528, P530-P535)','fourteen supported puzzle scenes (P505, P506, P508, P513, P519, P524, P526, P528, P530-P535)')
s=s.replace('fourteen supported puzzle scenes (P505, P506, P508, P513, P519, P524, P526, P528, P530-P535)','fifteen supported puzzle scenes (P505, P506, P508, P513, P517, P519, P524, P526, P528, P530-P535)')
if 'P517 v12' not in s:
    s=s.replace('- Automatically verified routes','- P517 v12 retains active aurora cycles, stopped phases and timers, original pictures and controls. All14 settings,2240 animation cases, first/repeated completion and slot11 in a fresh process pass.\n- Automatically verified routes')
s=s.replace('fifteen supported puzzle scenes (P505, P506, P508, P513, P517, P519, P524, P526, P528, P530-P535)','seventeen supported puzzle scenes (P505, P506, P508, P513, P515, P517, P519, P524, P526, P528, P530-P536)')
if 'Builder v13' not in s:
    s=s.replace('- Automatically verified routes','- Builder v13 retains construction in P515/P536, all five designs and a dormant custom17 sequence. Early Launch, first/repeated completion, P515 no-op and partial P536 slot12 in a fresh process pass.\n- Automatically verified routes')
s=s.replace('seventeen supported puzzle scenes (P505, P506, P508, P513, P515, P517, P519, P524, P526, P528, P530-P536)','eighteen supported puzzle scenes (P505, P506, P508, P513, P515, P517, P519, P524, P526, P528, P530-P537)')
s=s.replace('eighteen supported puzzle scenes (P505, P506, P508, P513, P515, P517, P519, P524, P526, P528, P530-P537)','nineteen supported puzzle scenes (P505, P506, P508, P513, P515, P517, P519, P524, P526, P528-P537)')
if 'Universe v15' not in s:
    s=s.replace('- Automatically verified routes','- Universe v15 retains P529 selectors, original movie frame and digit history, mask, comet and dormant custom17 state. Original253 movie frames, a fresh-process slot14 and compatibility with older save versions pass.\n- Automatically verified routes')
if 'Rocket v14' not in s:
    s=s.replace('- Automatically verified routes','- Rocket v14 preserves settled P537 selectors, prior failed-launch digits/gauges, stopped motion epoch and dormant custom17 state. All16 selectors, first/repeated success and fresh-process slot13 pass.\n- Automatically verified routes')
if 'custom17 v10' not in s:
    s=s.replace('- Automatically verified routes','- Six-scene custom17 v10 saves retain partial solutions and original process statics across random rounds and exit/reentry. Every scene passes at all four stages; one family slot resumes in a fresh process.\n- Retained unknown locals from earlier scenes no longer block P524/P526/P528/P530 saves. Four original P509 entries, twelve inert-value extremes and eight invalid-metadata rejections pass with v6-v9 layouts unchanged.\n- Automatically verified routes')
if 'P530 v9' not in s:
    s=s.replace('- Automatically verified routes','- P530 v9 preserves partial component assembly, the prior-round picture, RNG and the original unchanged completion counter; five scenarios per round and all25 pictures pass native continuation tests.\n- Automatically verified routes')
if 'P513 v11' not in s:
    s=s.replace('- Automatically verified routes','- P513 v11 saves settled photon experiments and question progress, retaining hidden photon endpoints, old digits and cube image. Tests cover 728 round trips, 126 answer continuations, two changes during flight, and fresh-process silent completion.\n- Automatically verified routes')
if 'P528 v8' not in s:
    s=s.replace('- Automatically verified routes','- P528 v8 retains partial eclipses and original image history; 160 reachable abstract states, 640 continuations, full480-row pixels and fresh-process completion pass.\n- Automatically verified routes')
if 'Ordinary presentation preserves all 640x480' not in s:
    s=s.replace('- Automatically verified routes','- Ordinary presentation preserves all 640x480 original pixels. The diagnostic strip is opt-in; twelve complete-scene checks and 855 original P528 picture pixels pass.\n- Automatically verified routes')
if probe_save_present:
    s=s.replace('on 21 October 2026','on 22 October 2026')
    s=s.replace('nineteen supported puzzle scenes (P505, P506, P508, P513, P515, P517, P519, P524, P526, P528-P537)',
                'twenty supported puzzle scenes (P505, P506, P508, P513, P515, P517, P519, P522, P524, P526, P528-P537)')
    if 'Probe v16' not in s:
        s=s.replace('- Automatically verified routes','- Probe v16 preserves ordinary nonflight and failed-return P522 boundaries, active orbit/calendar phases and the trusted200ms poll epoch; active flight remains excluded. Fresh-process continuation and older save compatibility are verified.\n- Automatically verified routes')
if rendezvous_save_present:
    s=s.replace('twenty supported puzzle scenes (P505, P506, P508, P513, P515, P517, P519, P522, P524, P526, P528-P537)',
                'twenty-one supported puzzle scenes (P505, P506, P508, P513, P514, P515, P517, P519, P522, P524, P526, P528-P537)')
    if 'Rendezvous v17' not in s:
        s=s.replace('- Automatically verified routes','- Rendezvous v17 retains live P514 orbit and fuel phases, speed settings and hidden docking-attempt history at settled script boundaries. Fresh-process continuation and frozen v16 save compatibility are verified.\n- Automatically verified routes')
if planet_save_present:
    s=s.replace('twenty-one supported puzzle scenes (P505, P506, P508, P513, P514, P515, P517, P519, P522, P524, P526, P528-P537)',
                'twenty-two supported puzzle scenes (P505, P506, P508, P513, P514, P515, P517, P518, P519, P522, P524, P526, P528-P537)')
    if 'Planets v18' not in s:
        s=s.replace('- Automatically verified routes','- Planets v18 preserves P518 idle-script boundaries with following and released planets, random selection state and hidden failed-attempt history. Fresh-process continuation and frozen v17 compatibility are verified.\n- Automatically verified routes')
if p521_save_present:
    s=s.replace('on 22 October 2026','on 23 October 2026')
    s=s.replace('twenty-two supported puzzle scenes (P505, P506, P508, P513, P514, P515, P517, P518, P519, P522, P524, P526, P528-P537)',
                'twenty-three supported puzzle scenes (P505, P506, P508, P513, P514, P515, P517, P518, P519, P521, P522, P524, P526, P528-P537)')
    if 'P521 v19' not in s:
        s=s.replace('- Automatically verified routes','- P521 v19 retains the displayed external image, hidden fragment history, animation/timer phases and inherited state at idle-script boundaries. Fresh-process continuation and frozen v18 compatibility are verified.\n- Automatically verified routes')
p.write_text(s.rstrip()+'\n')
if 'Looping WAVs follow the Music control' not in s:
    s=s.replace('- Automatically verified routes','- Looping WAVs follow the Music control; foreground WAVs retain Effects. Six scenes pass with Music muted at volume zero, original controls restored and twelve WAV hashes unchanged.\n- Automatically verified routes')
    p.write_text(s.rstrip()+'\n')
if p509_save_present:
    s=s.replace('on 23 October 2026','on 24 October 2026')
    s=s.replace('twenty-three supported puzzle scenes (P505, P506, P508, P513, P514, P515, P517, P518, P519, P521, P522, P524, P526, P528-P537)',
                'twenty-four supported puzzle scenes (P505, P506, P508, P509, P513, P514, P515, P517, P518, P519, P521, P522, P524, P526, P528-P537)')
    if 'P509 v20' not in s:
        s=s.replace('- Automatically verified routes','- P509 v20 preserves the trusted original pending narrator at index3, ordinary sky identity and hidden bounce state. Other queued work and active foreground audio remain excluded. Fresh-process continuation and genuine frozen v19 compatibility pass.\n- Automatically verified routes')
    p.write_text(s.rstrip()+'\n')
if p511_save_present:
    s=s.replace('on 24 October 2026','on 25 October 2026')
    s=s.replace('twenty-four supported puzzle scenes (P505, P506, P508, P509, P513, P514, P515, P517, P518, P519, P521, P522, P524, P526, P528-P537)',
                'twenty-five supported puzzle scenes (P505, P506, P508, P509, P511, P513, P514, P515, P517, P518, P519, P521, P522, P524, P526, P528-P537)')
    if 'P511 v21' not in s:
        s=s.replace('- Automatically verified routes','- P511 v21 preserves retained cloud images, independent selected frame/range history and active animation epochs at idle-script boundaries. Fresh-process continuation and genuine frozen v20 compatibility pass.\n- Automatically verified routes')
    p.write_text(s.rstrip()+'\n')
if p516_save_present:
    s=s.replace('twenty-five supported puzzle scenes (P505, P506, P508, P509, P511, P513, P514, P515, P517, P518, P519, P521, P522, P524, P526, P528-P537)',
                'twenty-six supported puzzle scenes (P505, P506, P508, P509, P511, P513-P519, P521, P522, P524, P526, P528-P537)')
    if 'P516 v22' not in s:
        s=s.replace('- Automatically verified routes','- P516 v22 preserves restricted quiet local2=0 boundaries with active orbits and a hidden stopped projectile. Active flight, unproved aborted history, stopped moons, foreground audio and queued/success transitions remain excluded. Fresh-process continuation and unchanged genuine frozen v21 compatibility pass.\n- Automatically verified routes')
    p.write_text(s.rstrip()+'\n')
if p527_save_present:
    s=s.replace('twenty-six supported puzzle scenes (P505, P506, P508, P509, P511, P513-P519, P521, P522, P524, P526, P528-P537)',
                'twenty-seven supported puzzle scenes (P505, P506, P508, P509, P511, P513-P519, P521, P522, P524, P526-P537)')
    if 'P527 v23' not in s:
        s=s.replace('- Automatically verified routes','- P527 v23 preserves quiet stopped-movie boundaries, independent selected button, seen mask and committed movie sample. All1105original samples compare equal between sequential decoding and seeking. Fresh-process continuation and genuine frozen v22 compatibility pass.\n- Automatically verified routes')
    p.write_text(s.rstrip()+'\n')
if p502_save_present:
    s=s.replace('twenty-seven supported puzzle scenes (P505, P506, P508, P509, P511, P513-P519, P521, P522, P524, P526-P537)',
                'twenty-eight supported puzzle scenes (P502, P505, P506, P508, P509, P511, P513-P519, P521, P522, P524, P526-P537)')
    if 'P502 v24' not in s:
        s=s.replace('- Automatically verified routes','- P502 v24 preserves quiet nonflight choices and hidden stopped failed comet/explosion history, all605runner words and dormant Jupiter geometry. Active flight, foreground audio and queued work remain excluded. Fresh-process continuation and genuine frozen v23 compatibility pass.\n- Automatically verified routes')
    p.write_text(s.rstrip()+'\n')
manifest['date']='2026-10-26' if p502_save_present else '2026-10-25' if p511_save_present else '2026-10-24' if p509_save_present else '2026-10-23' if p521_save_present else '2026-10-22' if probe_save_present else '2026-10-21'
manifest['sha256']={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(root.rglob('*')) if p.is_file()
                   and not {'.git','__pycache__','userdata'}.intersection(p.parts) and p.name!='SOURCE-MANIFEST.json'}
(root/'SOURCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
subprocess.run([sys.executable,str(root/'tools/verify_export.py')],check=True)
print('Source-only export refreshed; review git diff before commit/push')
