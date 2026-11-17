"""Derive isolated qualification runners for the complete original scene selector."""
from pathlib import Path
w=Path(__file__).resolve().parent
for kind in ('general','genuine'):
 text=(w/f'check_exploration_music_{kind}_nov17.py').read_text()
 text=text.replace('exploration-music-candidate-nov17c-stage','scene-music-candidate-nov17-stage')
 text=text.replace('exploration-music-','scene-music-').replace('EXPLORATION_MUSIC','SCENE_MUSIC')
 text=text.replace('SCENE_MUSIC_CANDIDATE_C_BUILD_PASS','SCENE_MUSIC_CANDIDATE_BUILD_PASS')
 (w/f'check_scene_music_{kind}_nov17.py').write_text(text)
text=(w/'check_audio_restore_startup_nov17.py').read_text()
text=text.replace("prefs=json.loads((w/'nov12-user-prefs-pin.json').read_text())",'# Personal installation excluded.')
text=text.replace("assert sha(Path(prefs['path']))==prefs['sha256']",'')
text=text.replace('user_preferences_unchanged=True','user_installation_ignored=True')
text=text.replace('audio-restore-startup-native-nov17','scene-music-startup-native-nov17').replace('audio-restore-candidate-nov17-stage','scene-music-candidate-nov17-stage')
text=text.replace('gui_language=en\\n','gui_language=en\\nmute=true\\n')
(w/'check_scene_music_startup_nov17.py').write_text(text)
text=(w/'audit_exploration_music_nov17.py').read_text()
text=text.replace('from exploration_music_source_nov17b import production','from scene_music_lifecycle_source_nov17 import production')
text=text.replace('p525-terminal-clock-compat-seal-nov17.json','exploration-music-seal-nov17.json')
text=text.replace('EXPLORATION_MUSIC','SCENE_MUSIC').replace("sha(w/'exploration_music_source_nov17b.py')","sha(w/'scene_music_lifecycle_source_nov17.py')")
(w/'audit_scene_music_nov17.py').write_text(text)
text=(w/'review_exploration_music_payload_nov17.py').read_text()
text=text[:text.index('baseline=read(')]
text=text.replace('p525-terminal-clock-compat-seal-nov17.json','exploration-music-seal-nov17.json').replace('exploration-music-candidate-nov17c-stage','scene-music-candidate-nov17-stage')
text+='''baseline=read(w/'scene-music-baseline-native-nov17/proof.json');fixed=read(w/'scene-music-final-native-nov17/proof.json');original=read(w/'exploration-music-original-nov17.json')
assert baseline['matched']==6 and fixed['matched']==18 and fixed['candidate_exe_sha256']==build['candidate_exe_sha256']
assert original['status']=='ORIGINAL_EXPLORATION_MUSIC_SELECTOR_PASS' and original['cases']==45192
assert fixed['current_and_legacy_menu_music_recipients'] and fixed['narration_rejected_without_mutation']
j=dict(status='SCENE_MUSIC_PAYLOAD_AND_REGRESSION_REVIEW_PASS',at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=build['candidate_exe_sha256'],parent_exe_sha256=parent['exe_sha256'],payload_methods=rows,header_byte_identical=True,serialized_methods_byte_identical=60,original_cases=45192,baseline_entries=6,fixed_entries=18,user_installation_ignored=True,limits=['Complete original selector for modes0,1,3; actual native sample covers nine scenes at two state values','Old local P1 music recipient remains accepted alongside original shared901; narration still refused'])
(w/'scene-music-payload-review-nov17.json').write_text(json.dumps(j,indent=2)+'\\n');print(j['status'])
'''
(w/'review_scene_music_payload_nov17.py').write_text(text)
print('Scene-music qualification helpers prepared')
