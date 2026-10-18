"""Record fresh original-research hashes without changing native route coverage."""
from pathlib import Path
import hashlib,json
root=Path('outputs/astronomica-cleanroom')
path=root/'evidence/research-oct01.json'
previous=json.loads(path.read_text())
files=set(root.glob('probe_*.py')) | set((root/'evidence').glob('p5*.json'))
files.add(root/'evidence/puzzle-save-requirements.json')
files.add(root/'P519-SAVE-PLAN.md')
files.add(root/'P505-SAVE-FORMAT.md')
files.add(root/'P519-SAVE-FORMAT.md')
files.add(root/'P524-SAVE-PLAN.md')
files.add(root/'P524-SAVE-FORMAT.md')
files.add(root/'P526-SAVE-PLAN.md')
files.add(root/'evidence/native-save-coverage.json')
files.update(root/'evidence'/name for name in ('p524-saves-validation.json', 'p524-save-proof.json', 'p524-saves-runtime.log', 'p524-saves-startup.log', 'p519-previous-slot.log', 'p519-previous-slot-proof.json'))
files.update(root/'evidence'/name for name in ('p519-saves-validation.json','p519-save-proof.json','p519-saves-runtime.log','p519-saves-startup.log','p505-previous-slot.log','p505-previous-slot-proof.json'))
files.update(root/'evidence'/name for name in ('p508-previous-slot.log','p508-previous-slot-proof.json'))
files.update(root/'evidence'/name for name in ('p505-save-original.json','p505-saves-validation.json','p505-save-proof.json','p505-saves-runtime.log','p505-saves-startup.log'))
files.update(root/'evidence'/name for name in ('p508-save-original.json','p508-saves-validation.json','p508-save-proof.json','p508-saves-runtime.log','p508-saves-startup.log'))
files.update(root/'evidence'/name for name in ('help-inline-original.json','help-inline0.png','help-inline12.png','help-inline19.png'))
files.add(root/'evidence/help-format366.png')
files.update(root/name for name in ('P409-RESEARCH.md','evidence/world-movie-inventory.json','evidence/advice-validation.json','evidence/endings-validation.json','evidence/postcredits-validation.json','evidence/intro-validation.json','evidence/intro-live-real-audio-result.json','evidence/intro-live-real-audio.log','evidence/sdl-dummy-clock.json','evidence/world29-validation.json','evidence/world-movies-validation.json','evidence/world-movies-runtime.log','evidence/world29.log','evidence/intro-live-result.json','evidence/intro-live.log','evidence/intro-logo-original.json','evidence/world-interactions.json','evidence/movie-controller.json','evidence/remaining-features.json','evidence/hover-dispatch.json','evidence/hover-validation.json','evidence/hover-runtime.log','evidence/menu-services.json','evidence/help-directory.json','evidence/help-compression.json','evidence/help-navigation.json','evidence/help-native-reference.json','evidence/legacy-resume-original.json','evidence/legacy-validation.json','evidence/legacy-runtime.log','evidence/legacy-file-proof.json','evidence/help-bitmaps.json','evidence/help-image-articles.json','evidence/help-format.json','evidence/help-image0.png','evidence/help-image12.png','evidence/help-image19.png','evidence/help-format1.png','evidence/help-format38.png','evidence/help-native-validation.json','evidence/help-native-runtime.log','evidence/help-index.png','evidence/help-article.png','HOVER-RESEARCH.md','HELP-RESEARCH.md','evidence/world-countdown.json','GAME-STATE-RESEARCH.md','evidence/game-state-validation.json','evidence/p409-advice.json','evidence/p409-clock.json','evidence/p409-return.json','PROGRESSION-RESEARCH.md','evidence/transitions.json','evidence/transitions-validation.json','evidence/progression-inventory.json','evidence/game-state.json','SAVE-RESEARCH.md','evidence/saves-validation.json','evidence/p408-mentors.json','evidence/mentors-validation.json','evidence/save-layout.json','P408-RESEARCH.md','evidence/builder.json','evidence/remaining-scenes.json',
    'evidence/comet-state.json','evidence/comet-motion.json','evidence/comet-render.json','evidence/comet-validation.json','COMET-RESEARCH.md','P516-RESEARCH.md','P510-RESEARCH.md','P523-RESEARCH.md'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=dict(date='2026-10-18',scope='Original research; P501, comet, P516, P510 and P523 native routes',
    sha256={p.relative_to(root).as_posix():digest(p) for p in sorted(files)},
    original_inputs_sha256={name:digest(Path('D:/astro')/name) for name in sorted(set(previous['original_inputs_sha256']) | {*[f'PLACES/P{n}/{m}' for n,m in [(0,'HQLOGO.MOV'),(2,'FLATOPEN.MOV'),(2,'FLATOPN2.MOV'),(2,'OPEN2_B'),(432,'RMC2.MOV'),(433,'FX.MOV'),(423,'F24.MOV'),(424,'FFATE_1.MOV'),(435,'FFATE_2.MOV'),(436,'FFATE_3.MOV'),(437,'FFATE_4.MOV')]],'PLACES/P82/MOV','PLACES/P222/MOV','PLACES/P231/MOV','PLACES/P82/MEGAFILE.HYP','PLACES/P222/MEGAFILE.HYP','PLACES/P231/MEGAFILE.HYP','HELP/ASTRONOM.HLP','QTW/QCMC.QTC','PLACES/P29/FLAT29.MOV','PLACES/P29/MEGAFILE.HYP','PLACES/P409/MEGAFILE.HYP',*[f'SOUNDS/S{i}.WAV' for i in range(13,20)],'SOUNDS/S10.WAV','SOUNDS/S11.WAV','PLACES/P429/F21G.MOV','PLACES/P427/END_BOOM.MOV','PLACES/P426/F23B.MOV','PLACES/P428/F23A.MOV','PLACES/P510/FLATPLOT.MOV','PLACES/P523/DANGERS.MOV','PLACES/P408/MEGAFILE.HYP','PLACES/P408/MENTORS.MOV'})})
path.write_text(json.dumps(manifest,indent=2))
print('Research evidence recorded:',len(files),'files')
