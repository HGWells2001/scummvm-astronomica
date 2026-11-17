"""Prepare exact-candidate qualification without personal installation access."""
from pathlib import Path
w=Path(__file__).resolve().parent
text=(w/'audit_scene_music_nov17.py').read_text().replace('from scene_music_lifecycle_source_nov17 import production','from p504_control_effect_source_nov17b import production').replace('exploration-music-seal-nov17.json','scene-music-seal-nov17.json').replace('SCENE_MUSIC_SOURCE_AND_LIBRARY_CLOSURE_PASS','P504_CONTROL_MUSIC_SOURCE_AND_LIBRARY_CLOSURE_PASS').replace("sha(w/'scene_music_lifecycle_source_nov17.py')","sha(w/'p504_control_effect_source_nov17b.py')").replace('exploration_ambience_added=True','p504_numeric_effect_added=True')
(w/'audit_p504_control_music_nov17.py').write_text(text)
for kind in ('general','genuine','startup'):
 text=(w/f'check_scene_music_{kind}_nov17.py').read_text()
 text=text.replace('scene-music-candidate-nov17-stage','p504-control-music-candidate-nov17b-stage')
 text=text.replace('scene-music-','p504-control-music-').replace('SCENE_MUSIC','P504_CONTROL_MUSIC')
 # The general suite must wait on the actual-click gate and exact B build.
 text=text.replace("codec=w/'p504-control-music-final-native-nov17'","codec=w/'p504-control-music-final-native-nov17b'")
 text=text.replace('P504_CONTROL_MUSIC_CANDIDATE_BUILD_PASS','P504_CONTROL_MUSIC_CANDIDATE_B_BUILD_PASS')
 (w/f'check_p504_control_music_{kind}_nov17.py').write_text(text)
# Replacements above must not recursively rename the already adjusted stage prefix.
for kind in ('general','genuine','startup'):
 p=w/f'check_p504_control_music_{kind}_nov17.py';text=p.read_text().replace('p504-control-music-candidate-nov17b-stage','p504-control-music-candidate-nov17b-stage');assert 'p504-control-music-candidate-nov17b-stage'in text;p.write_text(text)
text=(w/'review_scene_music_payload_nov17.py').read_text();text=text[:text.index('baseline=read(')]
text=text.replace('exploration-music-seal-nov17.json','scene-music-seal-nov17.json').replace('scene-music-candidate-nov17-stage','p504-control-music-candidate-nov17b-stage')
text+='''baseline=read(w/'p504-control-music-baseline-native-nov17b/proof.json');fixed=read(w/'p504-control-music-final-native-nov17b/proof.json')
assert baseline['values']['music']==0 and fixed['values']['music']==1 and fixed['candidate_exe_sha256']==build['candidate_exe_sha256']
assert baseline['values']['setting']==fixed['values']['setting']==1 and baseline['values']['starts']==fixed['values']['starts']==1
signature='static int originalSceneAmbient(int mode,int place,int32 state){'
assert function(before,signature)==function(after,signature)
start=after.index('bool AstronomicaEngine::isFeedbackEffect(int id) const {');end=after.index('void AstronomicaEngine::synchronizeMusicHandle()',start)
assert after[start:end].count('if(universeFileIdentity(')==9
j=dict(status='P504_CONTROL_MUSIC_PAYLOAD_AND_REGRESSION_REVIEW_PASS',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=build['candidate_exe_sha256'],parent_exe_sha256=parent['exe_sha256'],payload_methods=rows,header_byte_identical=True,serialized_methods_byte_identical=60,scene_selector_byte_identical=True,exact_effect_clip_identities=9,user_installation_ignored=True,limits=['Only exact original P504 speed-step clip added; other unclassified roles remain foreground','Actual original control preserves same Music handle; no change to save schemas or scene-music selector'])
(w/'p504-control-music-payload-review-nov17.json').write_text(json.dumps(j,indent=2)+'\\n');print(j['status'])
'''
(w/'review_p504_control_music_payload_nov17.py').write_text(text)
print('P504 control music qualification helpers prepared')
