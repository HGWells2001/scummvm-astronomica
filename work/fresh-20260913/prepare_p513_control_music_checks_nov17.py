"""Prepare isolated P513 qualification, preserving the accepted scene and P504 checks."""
from pathlib import Path
w=Path(__file__).resolve().parent
text=(w/'audit_p504_control_music_nov17.py').read_text().replace('from p504_control_effect_source_nov17b import production','from p513_control_effect_source_nov17 import production').replace('scene-music-seal-nov17.json','p504-control-music-seal-nov17.json').replace('P504_CONTROL_MUSIC','P513_CONTROL_MUSIC').replace("sha(w/'p504_control_effect_source_nov17b.py')","sha(w/'p513_control_effect_source_nov17.py')").replace('p504_numeric_effect_added=True','p513_numeric_effects_added=True')
(w/'audit_p513_control_music_nov17.py').write_text(text)
for kind in ('general','genuine','startup'):
 text=(w/f'check_p504_control_music_{kind}_nov17.py').read_text().replace('p504-control-music-candidate-nov17b-stage','p513-control-music-candidate-nov17-stage').replace('p504-control-music-','p513-control-music-').replace('P504_CONTROL_MUSIC','P513_CONTROL_MUSIC')
 text=text.replace('p513-control-music-final-native-nov17b','p513-control-music-final-native-nov17').replace('P513_CONTROL_MUSIC_CANDIDATE_B_BUILD_PASS','P513_CONTROL_MUSIC_CANDIDATE_BUILD_PASS')
 (w/f'check_p513_control_music_{kind}_nov17.py').write_text(text)
text=(w/'review_p504_control_music_payload_nov17.py').read_text();text=text[:text.index('baseline=read(')]
text=text.replace('scene-music-seal-nov17.json','p504-control-music-seal-nov17.json').replace('p504-control-music-candidate-nov17b-stage','p513-control-music-candidate-nov17-stage')
text+='''baseline=read(w/'p513-control-music-baseline-native-nov17/proof.json');fixed=read(w/'p513-control-music-final-native-nov17/proof.json')
assert [r['music']for r in baseline['cases']]==[0,0] and [r['music']for r in fixed['cases']]==[1,1] and fixed['candidate_exe_sha256']==build['candidate_exe_sha256']
assert [r['setting']for r in baseline['cases']]==[r['setting']for r in fixed['cases']]==[6,4]
signature='static int originalSceneAmbient(int mode,int place,int32 state){'
assert function(before,signature)==function(after,signature)
start=after.index('bool AstronomicaEngine::isFeedbackEffect(int id) const {');end=after.index('void AstronomicaEngine::synchronizeMusicHandle()',start)
assert after[start:end].count('if(universeFileIdentity(')==11
j=dict(status='P513_CONTROL_MUSIC_PAYLOAD_AND_REGRESSION_REVIEW_PASS',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=build['candidate_exe_sha256'],parent_exe_sha256=parent['exe_sha256'],payload_methods=rows,header_byte_identical=True,serialized_methods_byte_identical=60,scene_selector_byte_identical=True,exact_effect_clip_identities=11,user_installation_ignored=True,limits=['Two exact original P513 numeric-selector clips added; other unclassified roles remain foreground','Actual original controls retain Music; no save-schema or scene-selector change'])
(w/'p513-control-music-payload-review-nov17.json').write_text(json.dumps(j,indent=2)+'\\n');print(j['status'])
'''
(w/'review_p513_control_music_payload_nov17.py').write_text(text)
print('P513 Music qualification helpers prepared')
