"""Build original-selector extensions from the frozen accepted exploration release."""
from pathlib import Path
w=Path(__file__).resolve().parent
template=(w/'build_exploration_music_candidate_nov17c.py').read_text().replace('p525-terminal-clock-compat-seal-nov17.json','exploration-music-seal-nov17.json')
for label,fn in [('baseline','observe'),('candidate','production')]:
 p=template.replace('exploration-music-candidate-nov17c-stage','scene-music-'+label+'-nov17-stage').replace('from exploration_music_source_nov17b import production','from scene_music_lifecycle_source_nov17 import '+fn+' as production').replace('EXPLORATION_MUSIC_CANDIDATE_C_BUILD_PASS','SCENE_MUSIC_'+label.upper()+'_BUILD_PASS')
 (w/('build_scene_music_'+label+'_nov17.py')).write_text(p)
print('SCENE_MUSIC_BUILD_HELPERS_PREPARED')
