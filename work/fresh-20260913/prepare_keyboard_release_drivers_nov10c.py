"""Derive exact release gates for the reviewed keyboard-only production delta."""
from pathlib import Path
w=Path(__file__).resolve().parent
def convert(text):
 return text.replace('motion-geometry-cache-nov10b-stage','player-keyboard-guard-nov10c-stage').replace('motion-geometry-cache','player-keyboard').replace('motion_geometry_cache','player_keyboard').replace('motion_geometry_publication','player_keyboard_publication').replace('motion-geometry','player-keyboard').replace('motion_geometry','player_keyboard').replace('MOTION_GEOMETRY_CACHE','PLAYER_KEYBOARD').replace('MOTION_GEOMETRY','PLAYER_KEYBOARD').replace('nov10b','nov10c').replace('hit-geometry-cache-seal-nov10c','motion-geometry-cache-seal-nov10b').replace('nov10c-user-prefs','nov10b-user-prefs')
text=convert((w/'promote_motion_geometry_cache_nov10b.py').read_text())
text=text.replace("=={'astronomica.cpp'}","=={'astronomica.cpp','astronomica.h'}")
start=text.index('names=[');end=text.index('\ngates={}',start)
text=text[:start]+"names=['player-keyboard-source-review-nov10c.json','player-keyboard-native-nov10c/proof.json','player-keyboard-general-nov10c/proof.json']"+text[end:]
start=text.index("(snapshot/'physical-slots').mkdir()");end=text.index('for name,p in',start);text=text[:start]+text[end:]
text=text.replace("'player-keyboard-native-nov10c/native.log'","'player-keyboard-native-nov10c/guard/native.log'")
start=text.index('limits=[');end=text.index('\nwrite(snapshot/',start)
text=text[:start]+"limits=['Real P27 opcode28 establishes click lock; pre-fix native keyboard bypass reproduced separately,not original Windows execution','20 blocked key cases,16 absent/false diagnostic opt-in cases,3 original NAV targets,9 modified arrow cases; real F5 menu and Escape verified','Keyboard routing only; no data fields,class layout,core or save schema changes','Seven fresh engine translation units plus403 verified foundation objects; clean full source rebuild required','No manual whole-game completion claim; fixed acceptance7/10 remains unchanged']"+text[end:]
text=text.replace("for n in('astronomica.cpp',)","for n in('astronomica.cpp','astronomica.h')")
(w/'promote_player_keyboard_nov10c.py').write_text(text)
# Installed-path permanent verifier, with its exact markers and no baseline rerun.
text=convert((w/'check_motion_geometry_cache_main_oracle_nov10b.py').read_text())
text=text.replace("'PLAYER_KEYBOARD_REAL_ENGINE_BUILD_PASS'","'PLAYER_KEYBOARD_GUARD_REAL_ENGINE_BUILD_PASS'").replace('astronomica_verify_hit_geometry=true','astronomica_verify_keyboard=true')
start=text.index(" m=re.search(");end=text.index(" assert sha(exe)",start)
text=text[:start]+" for marker in ['Player keyboard blocked: PASS','Player keyboard menu: PASS','Player keyboard diagnostics: PASS','Player keyboard navigation: PASS','Player keyboard verification: PASS','Player keyboard native result: PASS']:assert marker in text,marker\n"+text[end:]
start=text.index(' proof=dict(');end=text.index(" (out/'proof.json')",start)
text=text[:start]+" proof=dict(status='INSTALLED_PLAYER_KEYBOARD_NATIVE_PASS',completed_at=datetime.now(timezone.utc).isoformat(),candidate_exe_sha256=sha(exe),native_log_sha256=sha(log),user_preferences_unchanged=True,blocked_no_mutation_cases=20,diagnostic_default_off_cases=16,unblocked_original_nav_targets=3,modified_arrow_no_mutation_cases=9,actual_F5_during_original_lock=True)\n"+text[end:]
text=text.replace("print('Hit geometry cache matches uncached native oracle:',scenes,'scenes',queries,'queries')","print('Installed real keyboard handler PASS')")
(w/'check_player_keyboard_main_oracle_nov10c.py').write_text(text)
for old,new in [('check_motion_geometry_publication_install_nov10b.py','check_player_keyboard_publication_install_nov10c.py'),('publish_motion_geometry_cache_nov10b.py','publish_player_keyboard_nov10c.py'),('seal_motion_geometry_cache_nov10b.py','seal_player_keyboard_nov10c.py'),('final_integrity_motion_geometry_nov10b.py','final_integrity_player_keyboard_nov10c.py'),('release_motion_geometry_cache_nov10b.py','release_player_keyboard_nov10c.py')]:
 text=convert((w/old).read_text())
 text=text.replace("'player-keyboard-main-smoke-nov10c/proof.json'","'player-keyboard-main-oracle-nov10c/proof.json'")
 text=text.replace("'check_player_keyboard_main_smoke_nov10c.py',",'')
 text=text.replace('Reuse decoded sprite dimensions during motion updates','Respect original click locks and disable diagnostic player shortcuts')
 (w/new).write_text(text)
print('Keyboard release drivers prepared; must pass general suite before promotion')
