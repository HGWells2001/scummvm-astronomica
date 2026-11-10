from pathlib import Path
w=Path(__file__).resolve().parent
t=(w/'build_builder_mask_guard_nov9.py').read_text()
t=t.replace("s=w/'builder-mask-guard-nov9-stage'","s=w/'success-effects-nov10-stage'").replace("w/'opening-rgb-seal-nov6-status.json'","w/'builder-mask-guard-seal-nov9-status.json'")
t=t.replace('from builder_profile_guard_source_nov9 import harden\nfrom builder_profile_probe_source_nov9 import inject\np=src/\'astronomica.cpp\';p.write_text(inject(harden(p.read_text()),True))',"from success_effects_probe_source_nov10 import inject\np=src/'astronomica.cpp';p.write_text(inject(p.read_text()))")
assert 'harden(' not in t
t=t.replace('BUILDER_PROFILE_GUARD_ENGINE_CANDIDATE_BUILD_PASS','SUCCESS_EFFECTS_REAL_ENGINE_CANDIDATE_BUILD_PASS')
(w/'build_success_effects_nov10.py').write_text(t)
